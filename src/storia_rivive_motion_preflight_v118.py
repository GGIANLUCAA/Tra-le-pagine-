#!/usr/bin/env python3
"""V118: fail-closed decoded-motion gate between V102 source preparation and I2I.

Only rewrites a locally generated draft request manifest; never invokes AI,
Vidu, publishing or paid APIs. Camera-shot authenticity still needs review.
"""
from __future__ import annotations

import argparse
import bisect
import json
import math
from fractions import Fraction
from pathlib import Path

try:
    from src.storia_rivive_motion_window_v115 import inspect_five_source_windows, check_source_window
except ModuleNotFoundError:
    from storia_rivive_motion_window_v115 import inspect_five_source_windows, check_source_window


def plan_windows(manifest, scout):
    """Select 1.35s preceding each original freeze within its detected shot."""
    if manifest.get("status") != "I2I_INPUTS_PREPARED_NO_AI_GENERATION":
        raise ValueError("V102_INPUTS_NOT_PREPARED")
    jobs = manifest.get("original_frame_jobs")
    if not isinstance(jobs, list) or len(jobs) != 5:
        raise ValueError("NEED_FIVE_SOURCE_LOCKED_JOBS")
    film_sha = manifest.get("source_video_sha256")
    if not isinstance(film_sha, str) or len(film_sha) != 64 or any(c not in "0123456789abcdef" for c in film_sha):
        raise ValueError("INVALID_SOURCE_SHA256")
    shots = scout.get("shot_boundary_analysis")
    if not isinstance(shots, dict) or shots.get("version") != "V113_FFMPEG_SCENE_CANDIDATES" or shots.get("source_sha256") != film_sha:
        raise ValueError("SHOT_CUT_SOURCE_MISMATCH")
    cuts = shots.get("cut_candidate_times_s")
    if (not isinstance(cuts, list) or len(cuts) < 4
            or any(type(x) not in (int, float) or not math.isfinite(x) or x <= 0 for x in cuts)
            or any(a >= b for a, b in zip(cuts, cuts[1:]))):
        raise ValueError("INVALID_SHOT_CUT_BOUNDARIES")
    if scout.get("original_sha256") != film_sha:
        raise ValueError("SCOUT_FILM_SHA_MISMATCH")
    windows = []
    segments = []
    for job in jobs:
        if not isinstance(job, dict) or job.get("source_film_sha256") != film_sha:
            raise ValueError("JOB_FILM_SHA_MISMATCH")
        pts, second, base = job.get("source_pts"), job.get("source_pts_time_s"), job.get("source_time_base")
        if type(pts) is not int or type(second) not in (int, float) or not math.isfinite(second):
            raise ValueError("INVALID_OR_MISSING_NATIVE_PTS")
        if not isinstance(base, str) or not base.count("/") == 1:
            raise ValueError("INVALID_TIME_BASE")
        try:
            n, d = map(int, base.split("/"))
            if n <= 0 or d <= 0:
                raise ValueError("invalid time base")
            period = Fraction(n, d)
        except (ValueError, OverflowError) as exc:
            raise ValueError("INVALID_TIME_BASE") from exc
        if abs(float(pts * period) - second) > 0.0001:
            raise ValueError("PTS_CLOCK_MISMATCH")
        segment = bisect.bisect_right(cuts, second)
        if job.get("shot_candidate_segment_index") != segment:
            raise ValueError("SELECTED_SHOT_SEGMENT_MISMATCH")
        segment_start = cuts[segment-1] if segment else 0.0
        if pts <= 0 or second <= segment_start:
            raise ValueError("FREEZE_BEFORE_SHOT_START")
        target_start = max(0.0, segment_start + 0.05, second - 1.35)
        start_pts = math.ceil(Fraction(str(target_start)) / period)
        window = {"start_pts": start_pts, "freeze_pts": pts, "time_base": base}
        valid, reason = check_source_window(start_pts, pts, base)
        if not valid:
            raise ValueError("INVALID_PRE_FREEZE_WINDOW: " + reason)
        windows.append(window)
        segments.append(segment)
    if len(set(segments)) != 5:
        raise ValueError("NOT_FIVE_DISTINCT_CANDIDATE_SHOTS")
    return windows


def run(manifest_path, scout_path, film_path, report_path, *, inspector=inspect_five_source_windows):
    """Persist JSON evidence; return only a draft gate decision."""
    manifest_path = Path(manifest_path)
    report_path = Path(report_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    try:
        scout = json.loads(Path(scout_path).read_text(encoding="utf-8"))
        windows = plan_windows(manifest, scout)
        evidence = inspector(film_path, manifest["source_video_sha256"], windows)
        if evidence.get("status") != "FIVE_MOTION_WINDOWS_EVIDENCED_REVIEW_REQUIRED":
            raise ValueError("DECODED_MOTION_REJECTED: " + str(evidence.get("reason", "UNKNOWN")))
        manifest["source_bw_motion_gate"] = "V118_FIVE_DECODED_WINDOWS_PASS_REVIEW_REQUIRED"
        for job, window in zip(manifest["original_frame_jobs"], windows):
            job["source_bw_motion_window"] = window
            job["source_bw_motion_review"] = "DECODED_PIXELS_CHANGED_NOT_CAMERA_QA"
        result = {"status": "MOTION_EVIDENCE_PASS_REVIEW_PENDING",
                  "reason": "DECODED_MOTION_ONLY_HUMAN_REVIEW_AND_RIGHTS_STILL_REQUIRED",
                  "evidence": evidence}
    except (ValueError, TypeError, KeyError, OSError, json.JSONDecodeError) as exc:
        # A failed gate MUST NOT leave a provider-consumable request list.
        manifest["status"] = "I2I_INPUTS_BLOCKED"
        manifest["source_bw_motion_gate"] = "V118_BLOCKED"
        manifest["original_frame_jobs"] = []
        manifest["photos_requested"] = 0
        manifest["reason"] = "V118_MOTION_PREFLIGHT_BLOCKED: " + str(exc)[:180]
        result = {"status": "BLOCKED", "reason": str(exc)[:250]}
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--scout", required=True)
    parser.add_argument("--film", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = run(args.manifest, args.scout, args.film, args.out)
    print("V118_OFFLINE_MOTION_PREFLIGHT", result["status"], result["reason"])


if __name__ == "__main__":
    main()
