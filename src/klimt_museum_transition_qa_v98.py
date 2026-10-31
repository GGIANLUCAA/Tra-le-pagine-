#!/usr/bin/env python3
"""Read-only, source-locked QA for the two Klimt Cinema Museum transitions.

Designed after a measured defect in the existing V97: the 41.30 -> 41.45 s
exit loses fine detail. This is a diagnostic, NOT a general artistic Gold gate,
and does not edit, render, import, upload or publish video.

Usage:
    python src/klimt_museum_transition_qa_v98.py --video PATH.mp4 \
        --expected-sha256 SHA256

Requires cv2 and numpy (existing ArtVision renderer dependencies).
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import cv2
import numpy as np

SAMPLES = {
    "entry_end": (11.25, 11.30),
    "exit_start": (41.30, 41.45),
}
# Diagnostic threshold for this visually inspected anomaly, NOT a universal
# human-perception model. It never automatically certifies artistic approval.
MAX_ABRUPT_SHARPNESS_RATIO = 8.0


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_gray_roi(cap: cv2.VideoCapture, time_s: float, fps: float) -> np.ndarray:
    idx = round(time_s * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ok, frame = cap.read()
    if not ok or frame is None:
        raise RuntimeError(f"Cannot read frame {idx} ({time_s:.2f}s)")
    h, w = frame.shape[:2]
    x0, x1 = round(w * 100 / 720), round(w * 620 / 720)
    y0, y1 = round(h * 240 / 1280), round(h * 1040 / 1280)
    return cv2.cvtColor(frame[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY)


def metrics(gray: np.ndarray) -> dict:
    lap = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    sx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    return {
        "laplacian_variance": round(lap, 3),
        "tenengrad_energy": round(float(np.mean(sx * sx + sy * sy)), 3),
    }


def run(path: Path, expected_sha256: str | None, threshold: float) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    actual_sha = sha256(path)
    if expected_sha256 and actual_sha.lower() != expected_sha256.lower():
        raise ValueError(f"SHA mismatch: {actual_sha} != {expected_sha256}")
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError("Video cannot be opened")
    try:
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if abs(fps - 20) > .001 or frames != 1040:
            raise ValueError(
                f"Unexpected asset: fps={fps}, frames={frames}; expected 20, 1040"
            )
        samples = {}
        for name, (t0, t1) in SAMPLES.items():
            a = metrics(read_gray_roi(cap, t0, fps))
            b = metrics(read_gray_roi(cap, t1, fps))
            la, lb = a["laplacian_variance"], b["laplacian_variance"]
            ratio = max(la, lb) / max(min(la, lb), 1e-9)
            samples[name] = {
                "from_s": t0,
                "to_s": t1,
                "before": a,
                "after": b,
                "laplacian_ratio": round(ratio, 3),
                "sharpness_collapse": bool(lb < la),
                "suspect_abrupt_change": bool(ratio > threshold),
            }
    finally:
        cap.release()
    return {
        "asset": path.name,
        "sha256": actual_sha,
        "bytes": path.stat().st_size,
        "fps": fps,
        "frame_count": frames,
        "roi_reference_px_at_720x1280": [100, 240, 620, 1040],
        "warning_ratio_threshold": threshold,
        "transitions": samples,
        "needs_targeted_visual_review": any(
            s["suspect_abrupt_change"] for s in samples.values()
        ),
        "V25_gold_approved": False,
        "note": (
            "Technical sharpness screen only; camera scale/content changes "
            "affect metrics. No automatic render or Gold approval."
        ),
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--video", type=Path, required=True)
    p.add_argument("--expected-sha256", default=None)
    p.add_argument("--max-ratio", type=float, default=MAX_ABRUPT_SHARPNESS_RATIO)
    p.add_argument("--output", type=Path, default=None)
    args = p.parse_args()
    try:
        result = run(args.video, args.expected_sha256, args.max_ratio)
    except Exception as exc:
        print(f"QA_ERROR: {exc}", file=sys.stderr)
        return 1
    payload = json.dumps(result, indent=2, ensure_ascii=False)
    print(payload)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    return 2 if result["needs_targeted_visual_review"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
