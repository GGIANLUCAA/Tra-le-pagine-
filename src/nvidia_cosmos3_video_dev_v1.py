#!/usr/bin/env python3
"""Experimental NVIDIA Cosmos3 Nano video preview, for development only.

The hosted API may carry watermarking and service-side safety checks. Never
remove either. User must explicitly enable a single zero-spend trial; the output
is a synthetic test clip, NOT original historic footage and NOT an approved MP4.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import json
import os
from pathlib import Path
from urllib import error, request

URL = "https://ai.api.nvidia.com/v1/cosmos/nvidia/cosmos3-nano"
MAX_RESPONSE_BYTES = 32_000_000
MAX_PROMPT_CHARS = 900
MAX_IMAGE_BYTES = 2_000_000

class CosmosDevError(RuntimeError):
    pass


def _license_and_key(env):
    if env.get("NVIDIA_COSMOS_DEV_ENABLED") != "1":
        raise CosmosDevError("Disabled; explicit NVIDIA_COSMOS_DEV_ENABLED=1 required")
    if env.get("NVIDIA_NIM_NONCOMMERCIAL_ACK") != "1":
        raise CosmosDevError("Developer/trial terms acknowledgment is required")
    if env.get("NVIDIA_NIM_ZERO_SPEND_CONFIRMED") != "1":
        raise CosmosDevError("Verify account is permitted to make a no-charge test")
    key = env.get("NVIDIA_API_KEY", "").strip()
    if len(key) < 8 or any(ch.isspace() for ch in key):
        raise CosmosDevError("NVIDIA_API_KEY not supplied as a secret")
    return key


def _source_image(path):
    p = Path(path)
    if not p.is_file():
        raise CosmosDevError("Reference source image missing")
    if p.stat().st_size > MAX_IMAGE_BYTES or p.stat().st_size < 64:
        raise CosmosDevError("Image size outside allowed test range")
    raw = p.read_bytes()
    if raw.startswith(b"\x89PNG\r\n\x1a\n"):
        mime = "image/png"
    elif raw.startswith(b"\xff\xd8\xff"):
        mime = "image/jpeg"
    elif raw.startswith(b"RIFF") and raw[8:12] == b"WEBP":
        mime = "image/webp"
    else:
        raise CosmosDevError("Only PNG/JPEG/WebP real image file supported")
    return "data:" + mime + ";base64," + base64.b64encode(raw).decode("ascii")


def preview_clip(prompt, *, source_image=None, environ=None, opener=None):
    """Generate 25 frames (~1.04s at 24 fps) only, no automatic publication."""
    env = os.environ if environ is None else environ
    key = _license_and_key(env)
    if not isinstance(prompt, str) or not 5 <= len(prompt.strip()) <= MAX_PROMPT_CHARS:
        raise CosmosDevError("Prompt must contain 5..900 characters")
    body = {
        "model_mode": "text2video",
        "prompt": prompt.strip(),
        "resolution": "480_9_16",
        "num_frames": 25,
        "num_inference_steps": 35,
        "fps": 24,
        "seed": 42,
    }
    if source_image is not None:
        body["model_mode"] = "image2video"
        body["input_reference"] = _source_image(source_image)
    req = request.Request(URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "TraLePagine-CosmosDevClip/1.0",
        }, method="POST")
    transport = opener or request.urlopen
    try:
        with transport(req, timeout=120) as resp:
            raw = resp.read(MAX_RESPONSE_BYTES+1)
    except error.HTTPError as exc:
        raise CosmosDevError("Cosmos API returned HTTP " + str(exc.code) + "; no retry") from None
    except (error.URLError, TimeoutError, OSError):
        raise CosmosDevError("Cosmos API unreachable or timed out; no retry") from None
    if len(raw) > MAX_RESPONSE_BYTES:
        raise CosmosDevError("Cosmos response exceeded preview size limit")
    try:
        parsed = json.loads(raw)
        encoded = parsed["b64_video"]
        if not isinstance(encoded, str):
            raise ValueError("Video field not a string")
        video = base64.b64decode(encoded, validate=True)
    except (KeyError, ValueError, TypeError, binascii.Error):
        raise CosmosDevError("Cosmos returned no valid base64 MP4") from None
    if not 256 <= len(video) <= 24_000_000 or video[4:8] != b"ftyp":
        raise CosmosDevError("Returned bytes are not a plausible MP4")
    return {
        "video_bytes": video,
        "metadata": {
            "schema": "nvidia-cosmos3-dev-preview-v1",
            "status": "experimental_unreviewed",
            "model": "nvidia/cosmos3-nano",
            "mode": body["model_mode"],
            "frames_requested": 25,
            "fps_requested": 24,
            "video_duration_estimate_seconds": round(25/24, 3),
            "resolution_requested": "480_9_16",
            "source_is_historical_footage": False,
            "watermark_preserved": True,
            "commercial_use_authorized": False,
            "publication_authorized": False,
            "cost_guaranteed": False,
            "human_visual_review_completed": False,
        },
    }


def main():
    p = argparse.ArgumentParser(description="Explicit single NVIDIA Cosmos preview clip")
    p.add_argument("--prompt-file", type=Path, required=True)
    p.add_argument("--image-file", type=Path)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--execute", action="store_true")
    args = p.parse_args()
    if not args.execute:
        print("COSMOS_DRY_RUN_ONLY: no API requests or new files")
        return 0
    prompt = args.prompt_file.read_text(encoding="utf-8")
    output = preview_clip(prompt, source_image=args.image_file)
    path = args.output
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(output["video_bytes"])
    path.with_suffix(".json").write_text(
        json.dumps(output["metadata"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("COSMOS_PREVIEW_UNREVIEWED:", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
