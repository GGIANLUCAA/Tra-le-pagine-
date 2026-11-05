#!/usr/bin/env python3
"""Zero-credit audio remaster of existing La Storia Rivive video masters.

This creates a *new audio-polished review candidate*, not a new episode or an
artistically approved release. It never calls generative APIs or publishes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=True)


def probe(path: Path) -> dict:
    return json.loads(run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,size:stream=codec_type,codec_name,width,height",
        "-of", "json", str(path)
    ]).stdout)


def measure(path: Path) -> dict:
    result = run([
        "ffmpeg", "-nostdin", "-hide_banner", "-i", str(path),
        "-vn", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
        "-f", "null", "-"
    ])
    matches = re.findall(r'\{\s*"input_i"\s*:.*?\}', result.stderr, re.S)
    if not matches:
        raise RuntimeError("FFmpeg loudnorm measurement missing")
    data = json.loads(matches[-1])
    for k in ["input_i", "input_tp", "input_lra", "input_thresh", "target_offset"]:
        if not math.isfinite(float(data[k])):
            raise RuntimeError(f"Non-finite loudness field: {k}")
    return data


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--report", required=True, type=Path)
    p.add_argument("--candidate", required=True)
    args = p.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)

    src_probe = probe(args.source)
    kinds = [s.get("codec_type") for s in src_probe["streams"]]
    if "video" not in kinds or "audio" not in kinds:
        raise RuntimeError("Existing master must contain both video and audio")

    src_audio = measure(args.source)
    filt = (
        "loudnorm=I=-16:TP=-1.5:LRA=11:"
        f"measured_I={src_audio['input_i']}:"
        f"measured_TP={src_audio['input_tp']}:"
        f"measured_LRA={src_audio['input_lra']}:"
        f"measured_thresh={src_audio['input_thresh']}:"
        f"offset={src_audio['target_offset']}:linear=true"
    )
    run([
        "ffmpeg", "-nostdin", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(args.source), "-map", "0:v:0", "-map", "0:a:0",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-af", filt, "-movflags", "+faststart", str(args.output)
    ])
    run(["ffmpeg", "-nostdin", "-v", "error", "-xerror",
         "-i", str(args.output), "-f", "null", "-"])
    dest_probe = probe(args.output)
    dest_audio = measure(args.output)
    duration_delta = abs(float(src_probe["format"]["duration"]) -
                         float(dest_probe["format"]["duration"]))
    loudness = float(dest_audio["input_i"])
    peak = float(dest_audio["input_tp"])
    checks = {
        "complete_decode": True,
        "source_and_output_different": sha256(args.source) != sha256(args.output),
        "duration_within_0_3_seconds": duration_delta <= 0.3,
        "loudness_within_3_LU_of_minus_16": abs(loudness + 16) <= 3.0,
        "true_peak_at_most_minus_1_dBTP": peak <= -1.0,
        "original_video_codec_retained": (
            next(s["codec_name"] for s in src_probe["streams"] if s["codec_type"] == "video")
            == next(s["codec_name"] for s in dest_probe["streams"] if s["codec_type"] == "video")
        ),
    }
    report = {
        "project": "LA_STORIA_RIVIVE",
        "candidate": args.candidate,
        "stage": "AUDIO_REMASTER_ONLY",
        "status": "RENDERED_AUDIO_POLISHED_REVIEW_REQUIRED" if all(checks.values()) else "QA_FAILED",
        "checks": checks,
        "original_sha256": sha256(args.source),
        "review_video_sha256": sha256(args.output),
        "original_loudness_LUFS": float(src_audio["input_i"]),
        "remaster_loudness_LUFS": loudness,
        "original_true_peak_dBTP": float(src_audio["input_tp"]),
        "remaster_true_peak_dBTP": peak,
        "source_duration_seconds": float(src_probe["format"]["duration"]),
        "remaster_duration_seconds": float(dest_probe["format"]["duration"]),
        "artistic_review": "PENDING",
        "source_rights_italy": "PENDING",
        "release_approved": False,
        "new_episode_created": False,
        "social_published": False,
        "paid_ai_api_calls": 0,
        "notice": "This is an audio-normalized legacy video for review only; not a final or new episode.",
    }
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"candidate": args.candidate, "status": report["status"],
                      "loudness": loudness, "checks": checks}, ensure_ascii=False))
    return 0 if all(checks.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
