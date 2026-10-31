"""Fail-closed offline pre-freeze motion evidence for La Storia Rivive.

A pass proves only that decoded source pixels show spatial changes in the pre-freeze window; uniform exposure flicker alone is rejected.
It does NOT certify five shots, rights, fidelity, or artistic approval.
"""
from __future__ import annotations
import hashlib
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path


def check_source_window(start_pts, freeze_pts, time_base, *, min_seconds=0.9, max_seconds=2.5):
    """Validate the source PTS window with exact rational clock arithmetic."""
    if type(start_pts) is not int or type(freeze_pts) is not int:
        return False, "INVALID_PTS_TYPE"
    if start_pts < 0 or freeze_pts <= start_pts:
        return False, "NO_PRE_FREEZE_SOURCE_WINDOW"
    if not isinstance(time_base, str) or '/' not in time_base:
        return False, "INVALID_TIME_BASE"
    try:
        numerator, denominator = time_base.split('/')
        if not numerator.isdigit() or not denominator.isdigit():
            return False, "INVALID_TIME_BASE"
        num, den = int(numerator), int(denominator)
        if num <= 0 or den <= 0:
            return False, "INVALID_TIME_BASE"
        duration = (freeze_pts - start_pts) * Fraction(num, den)
    except (ValueError, ZeroDivisionError):
        return False, "INVALID_TIME_BASE"
    if duration < Fraction(str(min_seconds)):
        return False, "PRE_FREEZE_WINDOW_TOO_SHORT"
    if duration > Fraction(str(max_seconds)):
        return False, "PRE_FREEZE_WINDOW_TOO_LONG"
    return True, "TEMPORAL_WINDOW_METADATA_PASS_MOTION_UNVERIFIED"


def inspect_source_motion(video_path, expected_sha256, start_pts, freeze_pts, time_base,
                          *, ffmpeg="ffmpeg", min_mean_pixel_delta=8.0,
                          min_spatial_pixel_delta=6.0, min_changed_pairs=2):
    """Decode SHA-bound film and reject static holds AND exposure-only flicker.

    Mean-centering each interframe pixel difference removes a uniform global
    brightness shift (common in aged film). Spatial residuals must also change.
    This is an advisory proxy: grain, local flicker and camera motion can still
    mimic subject motion, so five genuine camera shots require visual review.
    The 8fps 64x64 proxy is never used for exact freeze source-locking.
    """
    ok, reason = check_source_window(start_pts, freeze_pts, time_base)
    result = {"status": "BLOCKED", "reason": reason, "motion_verified": False,
              "sample_count": 0, "changed_pairs": 0, "max_mean_pixel_delta": 0.0,
              "max_spatial_pixel_delta": 0.0, "exposure_only_pairs": 0}
    if not ok:
        return result
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64 or any(c not in '0123456789abcdef' for c in expected_sha256):
        result["reason"] = "INVALID_EXPECTED_SOURCE_SHA256"
        return result
    source = Path(video_path)
    if not source.is_file():
        result["reason"] = "SOURCE_VIDEO_MISSING"
        return result
    h = hashlib.sha256()
    with source.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    if h.hexdigest() != expected_sha256:
        result["reason"] = "SOURCE_VIDEO_SHA256_MISMATCH"
        return result
    if not shutil.which(ffmpeg):
        result["reason"] = "FFMPEG_UNAVAILABLE"
        return result
    num, den = (int(v) for v in time_base.split('/'))
    start = Fraction(start_pts * num, den)
    duration = Fraction((freeze_pts - start_pts) * num, den)
    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin",
           "-ss", f"{float(start):.9f}", "-i", str(source),
           "-t", f"{float(duration):.9f}", "-an", "-sn", "-dn",
           "-vf", "fps=8,scale=64:64:flags=area,format=gray",
           "-f", "rawvideo", "-pix_fmt", "gray", "pipe:1"]
    try:
        decoded = subprocess.run(cmd, capture_output=True, timeout=30, check=False)
    except (OSError, subprocess.TimeoutExpired):
        result["reason"] = "SOURCE_WINDOW_DECODE_FAILED"
        return result
    if decoded.returncode or len(decoded.stdout) % 4096:
        result["reason"] = "SOURCE_WINDOW_DECODE_FAILED"
        return result
    samples = [decoded.stdout[i:i+4096] for i in range(0, len(decoded.stdout), 4096)]
    result["sample_count"] = len(samples)
    if len(samples) < 5:
        result["reason"] = "SOURCE_WINDOW_INSUFFICIENT_DECODED_FRAMES"
        return result
    raw_deltas, spatial_deltas = [], []
    for prev, curr in zip(samples, samples[1:]):
        signed = [int(b) - int(a) for a, b in zip(prev, curr)]
        exposure_shift = sum(signed) / len(signed)
        raw_deltas.append(sum(abs(v) for v in signed) / len(signed))
        spatial_deltas.append(sum(abs(v - exposure_shift) for v in signed) / len(signed))
    result["max_mean_pixel_delta"] = round(max(raw_deltas), 3)
    result["max_spatial_pixel_delta"] = round(max(spatial_deltas), 3)
    result["changed_pairs"] = sum(
        raw >= min_mean_pixel_delta and spatial >= min_spatial_pixel_delta
        for raw, spatial in zip(raw_deltas, spatial_deltas))
    result["exposure_only_pairs"] = sum(
        raw >= min_mean_pixel_delta and spatial < min_spatial_pixel_delta
        for raw, spatial in zip(raw_deltas, spatial_deltas))
    if result["changed_pairs"] < min_changed_pairs:
        result["reason"] = (
            "SOURCE_WINDOW_EXPOSURE_FLICKER_NOT_MOTION"
            if result["exposure_only_pairs"] >= min_changed_pairs
            else "SOURCE_WINDOW_STATIC_OR_TOO_LITTLE_MOTION")
        return result
    result.update({"status": "MOTION_EVIDENCE_PASS",
                   "reason": "DECODED_SOURCE_PIXEL_MOTION_PRESENT_NOT_ARTISTIC_QA",
                   "motion_verified": True})
    return result


def inspect_five_source_windows(video_path, expected_sha256, windows):
    """Fail closed unless all five original shots have measurable pre-freeze motion.

    `windows` must contain exactly five dicts with start_pts, freeze_pts and
    time_base. Does not assert camera cuts, rights or artistic approval.
    """
    if not isinstance(windows, list) or len(windows) != 5:
        return {"status": "BLOCKED", "reason": "NEED_FIVE_SOURCE_WINDOWS", "results": []}
    # Validate all five metadata records BEFORE touching or decoding the film.
    required = ("start_pts", "freeze_pts", "time_base")
    if any(not isinstance(w, dict) or any(key not in w for key in required) for w in windows):
        return {"status": "BLOCKED", "reason": "INVALID_WINDOW_METADATA", "results": []}
    results = []
    for index, window in enumerate(windows):
        evidence = inspect_source_motion(video_path, expected_sha256,
            window.get("start_pts"), window.get("freeze_pts"), window.get("time_base"))
        results.append({"scene": index + 1, **evidence})
        if not evidence["motion_verified"]:
            return {"status": "BLOCKED", "reason": "SCENE_MOTION_REJECTED", "results": results}
    return {"status": "FIVE_MOTION_WINDOWS_EVIDENCED_REVIEW_REQUIRED",
            "reason": "MOTION_ONLY_NOT_HISTORICAL_CAMERA_SHOT_QA", "results": results}
