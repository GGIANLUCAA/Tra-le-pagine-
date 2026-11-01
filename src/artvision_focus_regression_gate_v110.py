#!/usr/bin/env python3
"""Read-only ArtVision focus regression gate for existing MP4 revisions.

Detects lost detail and long static holds. Review flags are not V25 approval.
Never renders video, calls AI/TTS, or changes the input masters.
"""
import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def inspect(path, start, end, static_threshold, min_static_seconds):
    cap = cv2.VideoCapture(str(path))
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if fps <= 0 or count < 2 or width <= 0 or height <= 0:
        raise ValueError(f"Unreadable video: {path}")
    if not 0 <= start < end <= count / fps + 0.05:
        raise ValueError(f"Invalid focus interval: {path}")
    previous = None
    mads, sharpness = [], []
    decoded = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        gray = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (180, 320))
        sharpness.append(float(cv2.Laplacian(gray, cv2.CV_64F).var()))
        if previous is not None:
            mads.append(float(np.abs(gray.astype(np.int16) - previous.astype(np.int16)).mean()))
        previous = gray
        decoded += 1
    cap.release()
    if decoded != count:
        raise ValueError(f"Truncated MP4: {decoded}/{count} frames")
    a, b = max(0, round(start * fps)), min(decoded, round(end * fps))
    if b <= a:
        raise ValueError("Empty focus interval")
    runs, run_start = [], None
    for j, mad in enumerate(mads):
        if mad < static_threshold and run_start is None:
            run_start = j
        if run_start is not None and (mad >= static_threshold or j == len(mads) - 1):
            stop = j if mad >= static_threshold else j + 1
            if (stop - run_start) / fps >= min_static_seconds:
                runs.append({"start": round(run_start / fps, 2),
                             "end": round(stop / fps, 2),
                             "seconds": round((stop - run_start) / fps, 2)})
            run_start = None
    return {
        "sha256": sha256(path), "bytes": path.stat().st_size,
        "frames_decoded": decoded, "fps": fps,
        "width": width, "height": height,
        "focus_sharpness_mean": round(float(np.mean(sharpness[a:b])), 3),
        "peak_consecutive_frame_mad": round(max(mads), 3),
        "long_static_intervals": runs,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--baseline", required=True, type=Path)
    p.add_argument("--candidate", required=True, type=Path)
    p.add_argument("--start", required=True, type=float)
    p.add_argument("--end", required=True, type=float)
    p.add_argument("--max-sharpness-loss", type=float, default=0.25)
    p.add_argument("--static-threshold", type=float, default=0.16)
    p.add_argument("--min-static-seconds", type=float, default=5.0)
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    base = inspect(a.baseline, a.start, a.end,
                   a.static_threshold, a.min_static_seconds)
    cand = inspect(a.candidate, a.start, a.end,
                   a.static_threshold, a.min_static_seconds)
    dims = ("frames_decoded", "fps", "width", "height")
    if tuple(base[k] for k in dims) != tuple(cand[k] for k in dims):
        raise ValueError("Frame count, rate, or resolution changed")
    ratio = cand["focus_sharpness_mean"] / max(base["focus_sharpness_mean"], 1e-9)
    loss = 1 - ratio
    flags = []
    if loss > a.max_sharpness_loss:
        flags.append("FOCUS_SHARPNESS_REGRESSION_REVIEW_REQUIRED")
    if cand["long_static_intervals"]:
        flags.append("LONG_STATIC_HOLDS_REVIEW_REQUIRED")
    if cand["peak_consecutive_frame_mad"] > 35:
        flags.append("CAMERA_JUMP_REVIEW_REQUIRED")
    result = {
        "method": "decoded grayscale 180x320 Laplacian variance / frame MAD",
        "focus_interval_seconds": [a.start, a.end],
        "baseline": base, "candidate": cand,
        "focus_sharpness_ratio": round(ratio, 4),
        "focus_sharpness_loss_percent": round(100 * loss, 2),
        "flags": flags, "manual_visual_audio_review_required": True,
        "V25_Gold_automatically_approved": False,
        "source_files_modified": False,
    }
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
