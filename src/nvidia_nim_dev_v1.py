#!/usr/bin/env python3
"""NVIDIA API Catalog / NIM development-only editorial adapter.

API-key presence is not access authorization. Disabled by default; needs manual
developer-terms/zero-spend attestation before ONE test request. No production
pipeline connection, no automatic billing, no MP4/image/video generation.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from urllib import error, request

from ecc_public_editorial_guard_v1 import public_copy_violations
from freellmapi_editorial_v1 import SYSTEM, TASK_GUIDANCE

API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{1,80}/[a-zA-Z0-9][a-zA-Z0-9._+-]{1,100}$")
MAX_PROMPT_CHARS = 12000
MAX_RESPONSE_BYTES = 524288


class NvidiaNimError(RuntimeError):
    """Safe errors without credential or prompt leakage."""


def generate_dev_draft(task: str, prompt: str, *, environ=None, opener=None) -> dict:
    """Make at most one test chat request; outputs remain drafts, not publishable assets."""
    env = os.environ if environ is None else environ
    if env.get("NVIDIA_NIM_DEV_ENABLED") != "1":
        raise NvidiaNimError("Disabled: NVIDIA_NIM_DEV_ENABLED must be 1 for an explicit test")
    if env.get("NVIDIA_NIM_NONCOMMERCIAL_ACK") != "1":
        raise NvidiaNimError("NVIDIA free developer access is only for R&D/testing; terms acknowledgment required")
    if env.get("NVIDIA_NIM_ZERO_SPEND_CONFIRMED") != "1":
        raise NvidiaNimError("Verify account limits, balance and disabled paid billing before testing")
    if task not in TASK_GUIDANCE:
        raise NvidiaNimError("Unsupported editorial test task")
    if not isinstance(prompt, str) or not 1 <= len(prompt.strip()) <= MAX_PROMPT_CHARS:
        raise NvidiaNimError("Prompt must contain 1..12000 characters")
    model = env.get("NVIDIA_NIM_MODEL", "").strip()
    if not MODEL_PATTERN.fullmatch(model):
        raise NvidiaNimError("Explicit official catalog model required; no default/auto fallback")
    key = env.get("NVIDIA_API_KEY", "").strip()
    if len(key) < 8 or any(ch.isspace() for ch in key):
        raise NvidiaNimError("NVIDIA_API_KEY secret is missing or invalid")
    body = {
        "model": model,
        "max_tokens": 512,
        "temperature": 0.25,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": TASK_GUIDANCE[task] + "\n\n" + prompt},
        ],
    }
    req = request.Request(
        API_URL,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "StudioVideoNvidiaNimResearch/1.0",
        },
        method="POST",
    )
    transport = opener or request.urlopen
    try:
        with transport(req, timeout=30) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except error.HTTPError as exc:
        raise NvidiaNimError("NVIDIA API returned HTTP " + str(exc.code) + " (no automatic retries)") from None
    except (error.URLError, TimeoutError, OSError):
        raise NvidiaNimError("NVIDIA API unreachable or timed out (no retries)") from None
    if len(raw) > MAX_RESPONSE_BYTES:
        raise NvidiaNimError("NVIDIA API response exceeded size cap")

    try:
        data = json.loads(raw)
        response_model = data.get("model")
        content = data["choices"][0]["message"]["content"]
        if response_model != model:
            raise NvidiaNimError("Unexpected returned model: no implicit fallback accepted")
        if not isinstance(content, str) or not content.strip():
            raise NvidiaNimError("NVIDIA NIM returned no usable text")
    except (KeyError, IndexError, ValueError, TypeError):
        raise NvidiaNimError("NVIDIA API returned an invalid chat response") from None
    if task == "social" and public_copy_violations(content):
        raise NvidiaNimError("NVIDIA draft violates public naming rule V134")

    return {
        "schema": "nvidia-nim-dev-draft-v1",
        "status": "draft_unreviewed",
        "task": task,
        "model": model,
        "source": "NVIDIA API Catalog / developer test",
        "text": content,
        "sources_verified": False,
        "rights_verified": False,
        "artistic_approval": False,
        "commercial_use_authorized": False,
        "publication_authorized": False,
        "cost_guaranteed": False,
        "video_generated": False,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Optional NVIDIA NIM developer-only text evaluation")
    p.add_argument("--task", choices=sorted(TASK_GUIDANCE), required=True)
    p.add_argument("--prompt-file", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--execute", action="store_true", help="One explicit account-verified developer test")
    a = p.parse_args()
    if not a.execute:
        print("NVIDIA_NIM_DRY_RUN_ONLY: no API requests, no credits used, no files written")
        return 0
    prompt = a.prompt_file.read_text(encoding="utf-8")
    result = generate_dev_draft(a.task, prompt)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("NVIDIA_NIM_DEV_DRAFT_UNREVIEWED:", a.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
