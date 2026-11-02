#!/usr/bin/env python3
"""ArtVision V126: conservative offline QA of claimed 3D museum camera movement.

A single homography fitting most feature tracks means real 3D parallax has NOT
been demonstrated. It does not prove the video was made from a single photo;
a real 3D scene dominated by a planar wall can also fit a homography.
A negative result does NOT certify 3D, realism, physical scale, or authenticity.
Human review remains mandatory. No API calls or master modifications.
Requires: numpy, opencv-python(-headless), ffprobe.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
import cv2
import numpy as np


def probe(path: Path) -> dict:
    raw = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,size:stream=codec_name,width,height,nb_frames",
        "-of", "json", str(path)
    ], text=True)
    return json.loads(raw)


def read_at(cap: cv2.VideoCapture, sec: float):
    cap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
    ok, frame = cap.read()
    if not ok or frame is None:
        raise ValueError(f"Cannot decode frame at {sec:.3f}s")
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def compare(a: np.ndarray, b: np.ndarray) -> dict:
    sift = cv2.SIFT_create(nfeatures=2600)
    ka, da = sift.detectAndCompute(a, None)
    kb, db = sift.detectAndCompute(b, None)
    if da is None or db is None or len(da) < 5 or len(db) < 5:
        return {"status": "insufficient_features"}
    pairs = cv2.FlannBasedMatcher(dict(algorithm=1, trees=5),
                                  dict(checks=55)).knnMatch(da, db, k=2)
    good = [m for pair in pairs if len(pair) == 2
            for m, n in [pair] if m.distance < 0.72 * n.distance]
    if len(good) < 12:
        return {"status": "insufficient_matches", "matches": len(good)}
    src = np.float32([ka[m.queryIdx].pt for m in good])
    dst = np.float32([kb[m.trainIdx].pt for m in good])
    h, mask = cv2.findHomography(src, dst, cv2.RANSAC, 2.5)
    if h is None or mask is None:
        return {"status": "homography_fit_failed", "matches": len(good)}
    pred = cv2.perspectiveTransform(src[:, None, :], h)[:, 0, :]
    residuals = np.linalg.norm(pred - dst, axis=1)
    inliers = mask[:, 0].astype(bool)
    inlier_pts = src[inliers]
    height, width = a.shape
    zones = set((min(2, int(y * 3 / height)), min(2, int(x * 3 / width)))
                for x, y in inlier_pts)
    return {
        "status": "measured",
        "good_matches": len(good),
        "inliers": int(inliers.sum()),
        "inlier_fraction": round(float(inliers.mean()), 4),
        "inlier_median_reprojection_error_px": round(float(np.median(residuals[inliers])), 3),
        "inlier_3x3_spatial_zones": len(zones),
        "homography": np.round(h / h[2, 2], 6).tolist(),
    }


def analyze(path: Path, sample_pairs: list[tuple[float, float]]) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    info = probe(path)
    duration = float(info["format"]["duration"])
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError("Could not open MP4")
    checks = []
    try:
        for start, end in sample_pairs:
            if start < 0 or end >= duration or start >= end:
                raise ValueError(f"Invalid sample pair {start} {end} for {duration}s video")
            res = compare(read_at(cap, start), read_at(cap, end))
            checks.append({"start_s": start, "end_s": end, **res})
    finally:
        cap.release()
    strong = [c for c in checks if c.get("status") == "measured"
              and c["inliers"] >= 80 and c["inlier_fraction"] >= 0.80
              and c["inlier_median_reprojection_error_px"] <= 1.0
              and c["inlier_3x3_spatial_zones"] >= 3]
    planar = len(strong) == len(checks)
    return {
        "schema": "artvision-museum-parallax-qa-v126",
        "video_file": path.name,
        "bytes": path.stat().st_size,
        "sha256": digest.hexdigest(),
        "duration_seconds": duration,
        "video_streams": [s for s in info["streams"] if s.get("codec_name") != "aac"],
        "sample_pairs": checks,
        "classification": ("strong_single_homography_explanation"
                           if planar else "not_conclusively_planar_or_insufficient_data"),
        "real_3d_parallax_verified": False,
        "museum_artistic_approval": False,
        "interpretation": ("A single 2D projective transform consistently explains the "
                           "observed movement. Do not market as verified 3D camera or "
                           "physically reconstructed room. A negative result does not "
                           "establish 3D, room authenticity, scale or realism."),
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mp4", type=Path)
    p.add_argument("--pair", action="append", default=[], metavar="START:END")
    p.add_argument("--output", type=Path, default=None)
    args = p.parse_args()
    pairs = [(float(x), float(y)) for x, y in
             (s.split(":", 1) for s in args.pair)]
    if not pairs:
        pairs = [(0.5, 4.0), (1.5, 5.5)]
    result = analyze(args.mp4, pairs)
    txt = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(txt, encoding="utf-8")
    print(txt)


if __name__ == "__main__":
    main()
