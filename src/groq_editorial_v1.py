#!/usr/bin/env python3
"""Direct Groq editorial adapter: no persistent FreeLLMAPI server required.

Disabled unless explicitly executed and an account-specific verified-free
policy entry exists. A Groq API key in GitHub Secrets alone never starts calls.
All outputs are drafts; cannot approve visual QA, rights or publication.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib import error, request

from ecc_public_editorial_guard_v1 import public_copy_violations
from free_llm_zero_cost_v1 import ZeroCostPolicyError, admit, load_policy
from freellmapi_editorial_v1 import TASK_GUIDANCE, SYSTEM

API_URL = "https://api.groq.com/openai/v1/chat/completions"
MAX_PROMPT_CHARS = 12000
MAX_RESPONSE_BYTES = 524288


class GroqError(RuntimeError):
    pass


def generate_groq_draft(
    task: str,
    prompt: str,
    *,
    environ: dict[str, str] | None = None,
    opener=None,
) -> dict:
    env = os.environ if environ is None else environ
    if env.get("GROQ_EDITORIAL_ENABLED") != "1":
        raise GroqError("Disabled: set GROQ_EDITORIAL_ENABLED=1 only after free account review")
    if task not in TASK_GUIDANCE:
        raise GroqError("Unsupported editorial task")
    if not isinstance(prompt, str) or not 1 <= len(prompt.strip()) <= MAX_PROMPT_CHARS:
        raise GroqError("Prompt must have 1..12000 characters")

    model = env.get("GROQ_MODEL", "").strip()
    policy_file = env.get("GROQ_ZERO_COST_POLICY", "").strip()
    try:
        route = admit(model, load_policy(policy_file) if policy_file else load_policy())
        if route["provider"] != "groq":
            raise ZeroCostPolicyError("Only approved Groq routes are accepted here")
    except (ZeroCostPolicyError, OSError, ValueError) as exc:
        raise GroqError("Groq zero-cost route denied: " + str(exc)) from exc

    key = env.get("GROQ_API_KEY", "").strip()
    if not key or any(char in key for char in ("\r", "\n", " ", "\t")):
        raise GroqError("GROQ_API_KEY is missing or invalid")

    body = {
        "model": model,
        "temperature": 0.25,
        "stream": False,
        "max_tokens": 600,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": TASK_GUIDANCE[task] + "\n\n" + prompt},
        ],
    }
    req = request.Request(
        API_URL,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": "Bearer " + key,
                 "Content-Type": "application/json",
                 "User-Agent": "StudioVideoGroqEditorial/1.0"},
        method="POST",
    )
    transport = opener or request.urlopen
    try:
        with transport(req, timeout=30) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except error.HTTPError as exc:
        raise GroqError("Groq returned HTTP " + str(exc.code)) from None
    except (error.URLError, TimeoutError, OSError) as exc:
        raise GroqError("Groq API unreachable or timed out") from None
    if len(raw) > MAX_RESPONSE_BYTES:
        raise GroqError("Groq response exceeded size limit")
    try:
        parsed = json.loads(raw)
        returned_model = parsed["model"]
        message = parsed["choices"][0]["message"]["content"]
        if returned_model != model:
            raise GroqError("Unexpected model in response; reject draft")
        if not isinstance(message, str) or not message.strip():
            raise GroqError("Groq returned no usable text")
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise GroqError("Groq response invalid") from exc
    if task == "social" and public_copy_violations(message):
        raise GroqError("Groq social draft violates public naming rule V134")
    return {
        "schema": "groq-editorial-draft-v1",
        "status": "draft_unreviewed",
        "task": task,
        "model": model,
        "text": message,
        "source": "Groq direct API",
        "sources_verified": False,
        "rights_verified": False,
        "artistic_approval": False,
        "publication_authorized": False,
        "cost_guaranteed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Manual, opt-in Groq editorial draft")
    parser.add_argument("--task", choices=sorted(TASK_GUIDANCE), required=True)
    parser.add_argument("--prompt-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--execute", action="store_true",
                        help="Actually contact the verified-free Groq endpoint")
    args = parser.parse_args()
    if not args.execute:
        print("DRY_RUN_ONLY: no Groq request, no credits, no files written")
        return 0
    prompt = args.prompt_file.read_text(encoding="utf-8")
    draft = generate_groq_draft(args.task, prompt)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(draft, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print("GROQ_DRAFT_UNREVIEWED:", args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
