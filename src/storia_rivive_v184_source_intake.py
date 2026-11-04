#!/usr/bin/env python3
"""V184: read-only intake for a locally acquired archival film. No network or providers.

Metadata alone never establishes native scan quality, territorial rights, five
distinct shots, I2I, Vidu, or artistic approval. Fail closed.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

MIN_WIDTH = 1280
MIN_HEIGHT = 720
MAX_LOCAL_BYTES = 3 * 1024**3


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def probe_video(path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format",
         "-of", "json", str(path)],
        capture_output=True, text=True, check=True, timeout=90,
    )
    parsed = json.loads(result.stdout)
    video = next((s for s in parsed.get("streams", [])
                  if s.get("codec_type") == "video"), None)
    if not video:
        raise ValueError("NO_VIDEO_STREAM")
    return {
        "width": int(video["width"]),
        "height": int(video["height"]),
        "duration_seconds": float(parsed.get("format", {}).get("duration", 0)),
        "codec": video.get("codec_name"),
    }


def inspect_local(path, expected_sha256=None):
    path = Path(path)
    report = {
        "source_path": str(path),
        "source_sha256": None,
        "status": "SOURCE_REJECTED",
        "blocking_issues": [],
        "rights_italy_verified": False,
        "five_distinct_shots_verified": False,
        "human_visual_qa_approved": False,
        "provider_jobs_may_start": False,
        "publish_permitted": False,
    }
    issues = report["blocking_issues"]
    if path.is_symlink() or not path.is_file():
        issues.append("LOCAL_SOURCE_MISSING_OR_SYMLINK")
        return report
    size = path.stat().st_size
    report["size_bytes"] = size
    if size <= 0 or size > MAX_LOCAL_BYTES:
        issues.append("LOCAL_SOURCE_SIZE_INVALID")
        return report
    digest = sha256_file(path)
    report["source_sha256"] = digest
    if expected_sha256 is None:
        issues.append("SHA_LOCK_NOT_PROVIDED")
    elif not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        issues.append("INVALID_EXPECTED_SHA256")
    elif digest != expected_sha256:
        issues.append("SOURCE_SHA256_MISMATCH")
    try:
        media = probe_video(path)
        report["media"] = media
        if media["width"] < MIN_WIDTH or media["height"] < MIN_HEIGHT:
            issues.append("INSUFFICIENT_VIDEO_RESOLUTION")
        if not (30 <= media["duration_seconds"] <= 7200):
            issues.append("VIDEO_DURATION_OUT_OF_RANGE")
    except (OSError, ValueError, KeyError, subprocess.SubprocessError, json.JSONDecodeError):
        issues.append("FFPROBE_FAILED")
    issues.extend([
        "NATIVE_SCAN_AND_FIVE_SHOTS_VISUAL_REVIEW_PENDING",
        "ITALIAN_TERRITORIAL_RIGHTS_REVIEW_PENDING",
    ])
    report["status"] = (
        "SOURCE_REJECTED"
        if any(x in issues for x in (
            "SOURCE_SHA256_MISMATCH", "INVALID_EXPECTED_SHA256",
            "INSUFFICIENT_VIDEO_RESOLUTION", "VIDEO_DURATION_OUT_OF_RANGE",
            "FFPROBE_FAILED"))
        else "ASSETS_PENDING"
    )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    report = inspect_local(args.file, args.expected_sha256)
    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(report["status"], ",".join(report["blocking_issues"]))
    return 0 if report["status"] == "ASSETS_PENDING" else 2


if __name__ == "__main__":
    raise SystemExit(main())
