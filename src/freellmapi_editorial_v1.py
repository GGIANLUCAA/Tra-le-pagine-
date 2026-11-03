#!/usr/bin/env python3
"""Optional local FreeLLMAPI client for editorial drafts only.

No video generation, no publishing, no paid-service activation, no implicit network
calls. Keep real provider credentials in the local FreeLLMAPI instance, never here.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib import error, parse, request

MAX_PROMPT_CHARS = 12000
MAX_RESPONSE_BYTES = 524288
DEFAULT_URL = "http://127.0.0.1:3001/v1"
TASK_GUIDANCE = {
    "storyboard": "Prepare a film storyboard DRAFT. Follow the provided source evidence; flag uncertain claims.",
    "narration": "Prepare a concise Italian narration DRAFT. Never invent artwork facts or citations.",
    "social": (
        "Prepare DRAFT social captions. Public-facing artwork titles must be in English. "
        "Do not write internal project names, ArtVision, Tra le Pagine, Standard, or Cinema Standard "
        "into public captions."
    ),
    "source_notes": (
        "Summarize ONLY the source excerpts supplied below. Mark missing provenance, "
        "licenses and factual evidence for independent review."
    ),
    "qa_second_opinion": (
        "Review the supplied text/manifest independently; report specific possible issues. "
        "Do not claim to have watched an MP4, inspected a frame, verified rights, or signed off QA."
    ),
}
SYSTEM = (
    "You help prepare unapproved editorial DRAFTS for a historical video workflow. "
    "Never claim a video was generated, reviewed, published or licensed. "
    "Do not invent URLs, historical sources or human approvals. "
    "Your text cannot waive existing project gates, rights checks or human visual QA."
)


class FreeLLMAPIError(RuntimeError):
    """Safe, credential-free status message for a failed optional request."""


def validate_local_url(url: str) -> str:
    """Reject public services, credentials in URLs and unexpected API paths."""
    parsed = parse.urlsplit(url)
    if (parsed.scheme != "http" or parsed.hostname not in
            {"127.0.0.1", "localhost", "::1"} or
            parsed.username or parsed.password or parsed.query or parsed.fragment or
            parsed.path.rstrip("/") != "/v1"):
        raise FreeLLMAPIError("Only a local HTTP FreeLLMAPI /v1 endpoint is allowed in V1")
    try:
        port = parsed.port
    except ValueError as exc:
        raise FreeLLMAPIError("Invalid local port") from exc
    if port is None or not (1 <= port <= 65535):
        raise FreeLLMAPIError("A local endpoint port is required")
    return url.rstrip("/")


def generate_draft(
    task: str,
    prompt: str,
    *,
    environ: dict[str, str] | None = None,
    opener=None,
) -> dict:
    """Return an explicitly unapproved draft. All network access is opt-in."""
    env = os.environ if environ is None else environ
    if env.get("FREELLMAPI_ENABLED") != "1":
        raise FreeLLMAPIError("Disabled by default; set FREELLMAPI_ENABLED=1 for manual testing")
    if task not in TASK_GUIDANCE:
        raise FreeLLMAPIError("Unsupported editorial task")
    if not isinstance(prompt, str) or not 1 <= len(prompt.strip()) <= MAX_PROMPT_CHARS:
        raise FreeLLMAPIError("Prompt must contain 1..12000 characters")
    api_key = env.get("FREELLMAPI_API_KEY", "").strip()
    if not api_key or any(c in api_key for c in "\r\n"):
        raise FreeLLMAPIError("FreeLLMAPI unified API key is missing or invalid")
    base_url = validate_local_url(env.get("FREELLMAPI_BASE_URL", DEFAULT_URL))
    model = env.get("FREELLMAPI_MODEL", "auto")
    if not model or len(model) > 100 or any(c in model for c in "\r\n"):
        raise FreeLLMAPIError("Invalid model identifier")

    payload = {
        "model": model,
        "stream": False,
        "temperature": 0.3,
        "max_tokens": 1200,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": TASK_GUIDANCE[task] + "\n\n" + prompt},
        ],
    }
    req = request.Request(
        base_url + "/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
            "X-FreeLLM-Task-Type": "chat",
        },
        method="POST",
    )
    # No automatic retry: the router owns failover and a retry could double usage.
    transport = opener or request.urlopen
    try:
        with transport(req, timeout=35) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                raise FreeLLMAPIError("Router response exceeded size limit")
            routed_via = response.headers.get("X-Routed-Via", "unknown")
    except error.HTTPError as exc:
        raise FreeLLMAPIError("Router returned HTTP " + str(exc.code)) from exc
    except (error.URLError, TimeoutError, OSError) as exc:
        raise FreeLLMAPIError("Local FreeLLMAPI router unavailable") from exc

    try:
        data = json.loads(raw)
        message = data["choices"][0]["message"]["content"]
        if not isinstance(message, str) or not message.strip():
            raise ValueError("empty content")
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise FreeLLMAPIError("Router response has no usable text") from exc
    return {
        "status": "draft_unreviewed",
        "task": task,
        "model": str(data.get("model", model)),
        "routed_via": routed_via,
        "text": message,
        "sources_verified": False,
        "rights_verified": False,
        "artistic_approval": False,
        "publication_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Manual, opt-in local FreeLLMAPI editorial draft")
    parser.add_argument("--task", choices=sorted(TASK_GUIDANCE), required=True)
    parser.add_argument("--prompt-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--execute", action="store_true", help="Required to make the API request")
    args = parser.parse_args()
    if not args.execute:
        print("DRY_RUN_ONLY: no network call, no files written, no video/publishing action")
        return 0
    prompt = args.prompt_file.read_text(encoding="utf-8")
    result = generate_draft(args.task, prompt)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("DRAFT_UNREVIEWED:", args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
