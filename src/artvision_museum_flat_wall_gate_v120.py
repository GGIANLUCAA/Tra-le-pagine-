#!/usr/bin/env python3
"""V120: real-MP4 guard for flat-wall Museum intros/outros.

Flags large uniform regions in BOTH ends of a video. This is a conservative
regression warning, NOT a photorealism, scale, rights, or V25 Gold certificate.
No external APIs or rendering; requires ffmpeg, ffprobe and numpy.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

WIDTH, HEIGHT = 180, 320
SAMPLE_START = 0.20
SAMPLE_END_OFFSET = 1.00
QUANT = 8
THRESHOLD = 0.45


def run(command):
    p = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if p.returncode:
        raise RuntimeError(
            f"Command failed: {command[0]}: {p.stderr.decode(errors='replace')[-500:]}"
        )
    return p.stdout


def duration(path):
    raw = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "json", str(path)])
    return float(json.loads(raw)["format"]["duration"])


def sample(path, second):
    raw = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss",
               f"{second:.3f}", "-i", str(path), "-frames:v", "1",
               "-vf", f"scale={WIDTH}:{HEIGHT}", "-pix_fmt", "rgb24",
               "-f", "rawvideo", "-"])
    expected = WIDTH * HEIGHT * 3
    if len(raw) != expected:
        raise ValueError(f"Expected one frame ({expected} bytes), got {len(raw)}")
    rgb = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
    quantized = rgb // QUANT
    _, counts = np.unique(quantized, axis=0, return_counts=True)
    return round(float(counts.max() / len(rgb)), 6)


def inspect(path):
    d = duration(path)
    if d < 3.0:
        raise ValueError("Too short to inspect both Museum ends")
    start, end = SAMPLE_START, d - SAMPLE_END_OFFSET
    a, b = sample(path, start), sample(path, end)
    flagged = a >= THRESHOLD and b >= THRESHOLD
    return {
        "file": path.name,
        "duration_seconds": round(d, 3),
        "sample_seconds": [round(start, 3), round(end, 3)],
        "largest_8_level_RGB_bin_fraction": [a, b],
        "threshold": THRESHOLD,
        "flat_wall_suspected_both_ends": flagged,
        "interpretation": (
            "flat-wall fallback likely; mandatory Museum visual review"
            if flagged else
            "no flat-wall signature; Museum artistic review still required"
        ),
        "V25_Gold": False,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("mp4", type=Path)
    p.add_argument("--json", type=Path, default=None)
    args = p.parse_args()
    result = inspect(args.mp4)
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.json:
        args.json.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 2 if result["flat_wall_suspected_both_ends"] else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, ValueError, FileNotFoundError) as exc:
        print(json.dumps({"error": str(exc), "status": "QA_INCOMPLETE"}), file=sys.stderr)
        sys.exit(3)
