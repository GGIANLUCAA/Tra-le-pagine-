#!/usr/bin/env python3
"""V118: fail-closed decoded-motion gate between V102 source preparation and I2I.

Only rewrites a locally generated draft request manifest; never invokes AI,
Vidu, publishing or paid APIs. Camera-shot authenticity still needs review.
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import math
import re
from fractions import Fraction
from pathlib import Path
from PIL import Image

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



def verify_five_source_pngs(manifest, scout, film_path):
    """V119: recheck actual source PNG bytes after V102, before any provider.

    V102 already SHA-locks its files at creation time, but cached or modified
    PNGs could change between that check and the next stage. The independent
    scout provenance and the five local PNGs must still agree. This does NOT
    certify the original camera shot or reconstruct a photo.
    """
    film_sha = manifest["source_video_sha256"]
    if (scout.get("frame_provenance_source_sha256") != film_sha
            or scout.get("frame_provenance_version") != "V112_SOURCE_PTS_FROM_FFMPEG_SHOWINFO"):
        raise ValueError("SOURCE_PNG_PROVENANCE_FILM_MISMATCH")
    rows = scout.get("frame_provenance")
    if not isinstance(rows, list) or not rows:
        raise ValueError("SOURCE_PNG_PROVENANCE_MISSING")
    provenance = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("filename"), str):
            raise ValueError("SOURCE_PNG_PROVENANCE_INVALID")
        name = row["filename"]
        if not re.fullmatch(r"frame_\\d{2}\\.png", name) or name in provenance:
            raise ValueError("SOURCE_PNG_PROVENANCE_INVALID")
        provenance[name] = row
    root = Path(film_path).parent / "original_frames"
    seen_names, seen_hashes = set(), set()
    for job in manifest["original_frame_jobs"]:
        raw = job.get("source_file")
        if not isinstance(raw, str) or not raw:
            raise ValueError("SOURCE_PNG_PATH_MISSING")
        path = Path(raw)
        name = path.name
        expected = root / name
        if (not re.fullmatch(r"frame_\\d{2}\\.png", name)
                or name in seen_names or path.is_symlink() or expected.is_symlink()
                or path.resolve() != expected.resolve() or not path.is_file()):
            raise ValueError("SOURCE_PNG_PATH_INVALID_OR_MISSING")
        seen_names.add(name)
        row = provenance.get(name)
        if row is None:
            raise ValueError("SOURCE_PNG_NOT_IN_SCOUT")
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        digest = digest.hexdigest()
        if (digest != job.get("source_sha256") or digest != row.get("sha256")
                or digest in seen_hashes):
            raise ValueError("SOURCE_PNG_SHA_MISMATCH_OR_DUPLICATE")
        seen_hashes.add(digest)
        with Image.open(path) as im:
            if im.format != "PNG" or list(im.size) != job.get("source_raster_px"):
                raise ValueError("SOURCE_PNG_RASTER_MISMATCH")
            im.verify()
        for field in ("source_pts", "source_pts_time_s", "source_time_base",
                      "shot_candidate_segment_index", "extraction_index"):
            if job.get(field) != row.get(field):
                raise ValueError("SOURCE_PNG_SCOUT_METADATA_MISMATCH: " + field)
        if (job.get("source_pts_logged_from_decode") is not True
                or row.get("source_pts_logged_from_decode") is not True):
            raise ValueError("SOURCE_PNG_PTS_PROVENANCE_MISSING")
    if len(seen_names) != 5:
        raise ValueError("NEED_FIVE_VERIFIED_SOURCE_PNGS")
    return {"status": "V119_FIVE_SOURCE_PNG_BYTES_VERIFIED",
            "count": 5, "source_film_sha256": film_sha}


def run(manifest_path, scout_path, film_path, report_path, *, inspector=inspect_five_source_windows):
    """Persist JSON evidence; return only a draft gate decision."""
    manifest_path = Path(manifest_path)
    report_path = Path(report_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    try:
        scout = json.loads(Path(scout_path).read_text(encoding="utf-8"))
        windows = plan_windows(manifest, scout)
        png_evidence = verify_five_source_pngs(manifest, scout, film_path)
        evidence = inspector(film_path, manifest["source_video_sha256"], windows)
        if evidence.get("status") != "FIVE_MOTION_WINDOWS_EVIDENCED_REVIEW_REQUIRED":
            raise ValueError("DECODED_MOTION_REJECTED: " + str(evidence.get("reason", "UNKNOWN")))
        manifest["source_png_integrity_gate"] = "V119_FIVE_SOURCE_PNG_BYTES_VERIFIED"
        manifest["source_bw_motion_gate"] = "V118_FIVE_DECODED_WINDOWS_PASS_REVIEW_REQUIRED"
        for job, window in zip(manifest["original_frame_jobs"], windows):
            job["source_bw_motion_window"] = window
            job["source_bw_motion_review"] = "DECODED_PIXELS_CHANGED_NOT_CAMERA_QA"
        result = {"status": "MOTION_EVIDENCE_PASS_REVIEW_PENDING",
                  "reason": "DECODED_MOTION_ONLY_HUMAN_REVIEW_AND_RIGHTS_STILL_REQUIRED",
                  "evidence": evidence, "source_png_integrity": png_evidence}
    except (ValueError, TypeError, KeyError, OSError, json.JSONDecodeError) as exc:
        # A failed gate MUST NOT leave a provider-consumable request list.
        manifest["status"] = "I2I_INPUTS_BLOCKED"
        manifest["source_bw_motion_gate"] = "V118_BLOCKED"
        manifest["source_png_integrity_gate"] = "V119_BLOCKED"
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
