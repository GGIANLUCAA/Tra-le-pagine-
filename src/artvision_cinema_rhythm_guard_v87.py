#!/usr/bin/env python3
"""Read-only Cinema Standard visual rhythm review on REAL MP4 bytes.

Advisory quality gate, NOT V25 approval. Museum V57 continuity thresholds
must not be applied to intentional Cinema Standard hard cuts.
"""
from __future__ import annotations
import argparse
import json
import statistics
from pathlib import Path
import cv2
import numpy as np


def inspect(path: str, cut_mad: float = 20.0) -> dict:
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise ValueError(f"Unable to open MP4: {path}")
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    if fps <= 0:
        cap.release()
        raise ValueError("Invalid FPS")
    frames, previous, cuts, end_dark = 0, None, [], []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        gray = cv2.cvtColor(cv2.resize(frame, (135, 240)), cv2.COLOR_BGR2GRAY)
        if previous is not None:
            mad = float(np.mean(cv2.absdiff(gray, previous)))
            if mad > cut_mad and (not cuts or (frames / fps) - cuts[-1] > 0.5):
                cuts.append(round(frames / fps, 3))
        previous = gray
        end_dark.append((frames / fps, float(np.mean(gray < 12))))
        if len(end_dark) > int(fps * 12) + 1:
            end_dark.pop(0)
        frames += 1
    cap.release()
    if frames == 0:
        raise ValueError("Video has no decodable frames")
    gaps = [b - a for a, b in zip(cuts, cuts[1:])]
    cv = (statistics.pstdev(gaps) / statistics.mean(gaps)) if len(gaps) >= 2 and statistics.mean(gaps) else None
    trailing_dark_frames = 0
    for _, fraction in reversed(end_dark):
        if fraction >= 0.5:
            trailing_dark_frames += 1
        else:
            break
    dark_tail = trailing_dark_frames / fps
    findings = []
    if len(gaps) >= 6 and cv is not None and cv < 0.04:
        findings.append("NEEDS_ARTISTIC_REVIEW: almost periodic Cinema Standard cuts")
    if dark_tail >= 5.0:
        findings.append("NEEDS_ARTISTIC_REVIEW: long mostly-dark closing composition")
    return {
        "file": Path(path).name,
        "decoded_frames": frames,
        "fps": round(fps, 3),
        "duration_video_seconds": round(frames / fps, 3),
        "hard_cut_candidates_seconds": cuts,
        "internal_cut_interval_mean_seconds": round(statistics.mean(gaps), 3) if gaps else None,
        "internal_cut_interval_cv": round(cv, 4) if cv is not None else None,
        "trailing_majority_black_seconds": round(dark_tail, 3),
        "advisories": findings,
        "v25_approved": False,
        "scope": "cinema_standard_read_only_advisory",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mp4", help="existing real MP4; never renders")
    parser.add_argument("--cut-mad", type=float, default=20.0)
    args = parser.parse_args()
    print(json.dumps(inspect(args.mp4, args.cut_mad), indent=2))


if __name__ == "__main__":
    main()
