#!/usr/bin/env python3
"""Evidence-only MP4 editing diagnostics using FFmpeg, no network or inference.

Detects probable blink frames between close scene cuts, brief black intervals,
and obvious codec/duration problems. Results are *technical clues*, not an
artistic rating or proof of visual/voice synchronization.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

MAX_BYTES = 3_000_000_000
MAX_SCAN_SECONDS = 240
SCENE_RE = re.compile(r"\bpts_time:(\d+(?:\.\d+)?)")
BLACK_RE = re.compile(
    r"black_start:(\d+(?:\.\d+)?)\s+black_end:(\d+(?:\.\d+)?)\s+black_duration:(\d+(?:\.\d+)?)"
)


def issue(code, severity, message, at_s=None):
    row = {"code": code, "severity": severity, "message": message}
    if at_s is not None:
        row["at_s"] = round(float(at_s), 3)
    return row


def probe(path):
    if not shutil.which("ffprobe") or not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg and ffprobe must be installed")
    p = Path(path).resolve()
    if not p.is_file() or p.suffix.lower() not in (".mp4", ".mov"):
        raise ValueError("Only real local MP4/MOV files are supported")
    if not 100 <= p.stat().st_size <= MAX_BYTES:
        raise ValueError("Video file is empty, implausible or exceeds 3GB")
    try:
        run = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration:stream=codec_type,codec_name,width,height",
             "-of", "json", str(p)],
            capture_output=True, text=True, timeout=30, check=True,
        )
        payload = json.loads(run.stdout)
        duration = float(payload.get("format", {}).get("duration", 0))
        if not math.isfinite(duration) or duration <= 0:
            raise ValueError("Missing or invalid duration")
        streams = payload.get("streams") or []
        visual = next((s for s in streams if s.get("codec_type") == "video"), None)
        if not visual:
            raise ValueError("No video stream")
    except (subprocess.SubprocessError, OSError, json.JSONDecodeError, TypeError) as exc:
        raise RuntimeError("Cannot verify real video metadata") from exc
    return p, duration, streams


def _run_ffmpeg(path, seconds, filter_graph):
    cmd = [
        "ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "info", "-i", str(path),
        "-t", f"{seconds:.3f}", "-an", "-vf", filter_graph, "-f", "null", "-"
    ]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True,
                             timeout=150, check=False)
    except (subprocess.TimeoutExpired, OSError) as exc:
        raise RuntimeError("FFmpeg diagnostic unavailable or timed out") from exc
    if out.returncode != 0:
        raise RuntimeError("FFmpeg diagnostic failed")
    return out.stderr


def inspect(path):
    """Never changes the source MP4; no publication, provider calls or video generation."""
    p, duration, streams = probe(path)
    cap = min(duration, MAX_SCAN_SECONDS)
    report = {
        "schema": "ai-director-visual-qa-v1",
        "status": "technical_review_only",
        "duration_s": round(duration, 3),
        "analyzed_seconds": round(cap, 3),
        "partial_scan": duration > MAX_SCAN_SECONDS,
        "cut_detector": "ffmpeg scene difference; threshold 0.33 on 12 fps thumbnail",
        "frame_rate_sample": 12,
        "visual_rating": None,
        "narration_alignment_verified": False,
        "human_artistic_approval": False,
        "publication_authorized": False,
        "issues": [],
        "cut_times_s": [],
        "black_intervals": [],
    }
    video = next(x for x in streams if x.get("codec_type") == "video")
    audio = next((x for x in streams if x.get("codec_type") == "audio"), None)
    if video.get("codec_name") != "h264":
        report["issues"].append(issue("VIDEO_CODEC_REVIEW", "warning",
                                      "Video codec is not H264"))
    if not audio or audio.get("codec_name") != "aac":
        report["issues"].append(issue("AUDIO_CODEC_REVIEW", "warning",
                                      "AAC audio track absent/unverified"))
    if report["partial_scan"]:
        report["issues"].append(issue("PARTIAL_SCAN", "info",
                                      "Only first 240 seconds were scanned"))

    try:
        cuts_log = _run_ffmpeg(p, cap, "fps=12,scale=240:-1,select='gt(scene,0.33)',showinfo")
        # showinfo is downstream from select and emits pts_time for retained cuts.
        times = sorted({round(float(x), 3) for x in SCENE_RE.findall(cuts_log)})
        report["cut_times_s"] = times[:500]
        for a, b in zip(times, times[1:]):
            d = b - a
            if 0.08 <= d < 0.95:
                report["issues"].append(issue(
                    "POSSIBLE_BLINK_FRAME", "warning",
                    "Two detected cuts are only %.2fs apart: inspect exact frames" % d,
                    a
                ))
            elif 0.95 <= d < 1.4:
                report["issues"].append(issue(
                    "FAST_CUT_REVIEW", "info",
                    "Two cuts are %.2fs apart; check perceptual readability" % d,
                    a
                ))
    except RuntimeError:
        report["issues"].append(issue("CUT_SCAN_UNAVAILABLE", "warning",
                                      "Cannot verify cut timing on actual MP4"))

    try:
        black_log = _run_ffmpeg(
            p, cap, "scale=240:-1,blackdetect=d=0.12:pix_th=0.10:pic_th=0.98")
        found = []
        for a, b, d in BLACK_RE.findall(black_log):
            row = {"start_s": round(float(a), 3),
                   "end_s": round(float(b), 3), "duration_s": round(float(d), 3)}
            found.append(row)
            report["issues"].append(issue("BLACK_FRAME_REVIEW", "warning",
                                          "Black interval of %.2fs detected" % float(d),
                                          a))
        report["black_intervals"] = found[:250]
    except RuntimeError:
        report["issues"].append(issue("BLACK_SCAN_UNAVAILABLE", "warning",
                                      "Cannot verify black-frame intervals on actual MP4"))
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = inspect(args.video)
    except (ValueError, RuntimeError, OSError) as exc:
        result = {"schema": "ai-director-visual-qa-v1",
                  "status": "unverified", "message": str(exc),
                  "human_artistic_approval": False,
                  "publication_authorized": False, "issues": []}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("AI_DIRECTOR_REAL_MP4_QA", result["status"], "issues", len(result["issues"]),
          "artistic_approval=FALSE")
    return 0 if result["status"] == "technical_review_only" else 2


if __name__ == "__main__":
    raise SystemExit(main())
