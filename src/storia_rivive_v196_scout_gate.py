#!/usr/bin/env python3
"""V196: verify genuine V101 cached film and frames before downstream research.

Fail closed and skip costly/redundant steps; this is not a rights or artistic gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from PIL import Image

MAX_SOURCE_BYTES = 160 * 1024 * 1024
READY_STATUS = "REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_cache(order: dict, cache_dir: Path) -> dict:
    """Return a research-only readiness result; never assert approval or payment."""
    result = {
        "status": "SOURCE_SCOUT_BLOCKED_NO_PRODUCTION",
        "ready": False,
        "reason": "UNKNOWN",
        "verified_original_frames": 0,
        "distinct_source_frame_pixels": 0,
        "restored_photos": 0,
        "vidu_clips": 0,
        "paid_calls": 0,
        "publish_permitted": False,
    }

    def block(reason: str) -> dict:
        result["reason"] = reason
        return result

    if order.get("contract") != "LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT":
        return block("INVALID_WORK_ORDER")
    if order.get("paid_api_call_permitted") is not False or order.get("publish_permitted") is not False:
        return block("UNSAFE_WORK_ORDER_PERMISSIONS")
    if not isinstance(order.get("source_page"), str) or not order["source_page"]:
        return block("MISSING_SOURCE_PAGE")

    report_file = cache_dir / "SCOUT_REPORT.json"
    try:
        report = json.loads(report_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return block("MISSING_OR_INVALID_SCOUT_REPORT")
    if not isinstance(report, dict) or report.get("status") != READY_STATUS:
        return block("SCOUT_NOT_READY")
    if report.get("source_page") != order["source_page"]:
        return block("CACHE_SOURCE_MISMATCH")

    source = cache_dir / "ORIGINAL_ARCHIVE.webm"
    try:
        size = source.stat().st_size
    except OSError:
        return block("MISSING_ORIGINAL_FILM")
    if not 0 < size <= MAX_SOURCE_BYTES or source.is_symlink():
        return block("INVALID_ORIGINAL_FILM_SIZE_OR_PATH")
    expected_sha = report.get("original_sha256")
    if not isinstance(expected_sha, str) or len(expected_sha) != 64:
        return block("MISSING_ORIGINAL_FILM_SHA256")
    if sha256_file(source) != expected_sha.lower():
        return block("ORIGINAL_FILM_SHA256_MISMATCH")

    frames_dir = cache_dir / "original_frames"
    frames = sorted(frames_dir.glob("frame_*.png"))
    if len(frames) < 5 or report.get("source_frames_extracted") != len(frames):
        return block("INSUFFICIENT_OR_INCONSISTENT_FRAMES")
    # A valid PNG filename/hash does not mean a distinct source image. Compare
    # decoded RGB pixels, not compressed PNG bytes (metadata/compression differ).
    # This is a research-cache sanity check, NOT proof of five different shots.
    unique_pixels = set()
    native_size = None
    for frame in frames:
        if frame.is_symlink():
            return block("FRAME_PATH_NOT_REGULAR")
        try:
            with Image.open(frame) as image:
                if image.format != "PNG" or min(image.size) < 32:
                    return block("FRAME_NOT_VALID_NATIVE_PNG")
                image.load()
                if native_size is None:
                    native_size = image.size
                elif image.size != native_size:
                    return block("MIXED_SOURCE_FRAME_GEOMETRY")
                unique_pixels.add(hashlib.sha256(image.convert("RGB").tobytes()).digest())
        except (OSError, ValueError):
            return block("FRAME_PNG_DECODE_FAILED")
    if len(unique_pixels) < 5:
        return block("INSUFFICIENT_DISTINCT_SOURCE_FRAME_PIXELS")

    result.update({
        "status": "REAL_BW_FILM_FRAMES_VERIFIED_FOR_RESEARCH_ONLY",
        "ready": True,
        "reason": "SOURCE_BYTES_AND_FRAMES_VERIFIED_NOT_ARTISTICALLY_APPROVED",
        "verified_original_frames": len(frames),
        "distinct_source_frame_pixels": len(unique_pixels),
        "original_film_sha256": expected_sha.lower(),
    })
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--order", required=True)
    parser.add_argument("--cache", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    order = json.loads(Path(args.order).read_text(encoding="utf-8"))
    result = inspect_cache(order, Path(args.cache))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if os.environ.get("GITHUB_OUTPUT"):
        with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as handle:
            handle.write("ready=" + ("true" if result["ready"] else "false") + "\n")
    print(json.dumps({"status": result["status"], "reason": result["reason"],
                      "frames": result["verified_original_frames"], "paid_calls": 0}))


if __name__ == "__main__":
    main()
