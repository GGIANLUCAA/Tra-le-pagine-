#!/usr/bin/env python3
"""V126: fail-closed visual near-duplicate audit of V125's five ORIGINAL PNGs.

Research-only. Similar-looking archival frames can be different camera shots,
and different-looking frames can still belong to one continuous shot. Neither
outcome is a camera-shot certification, Italian-rights clearance or AI approval.
No network, Vidu, I2I, purchases or publication.
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import math
import re
from pathlib import Path

from PIL import Image, ImageOps

try:
    from src.storia_rivive_frame_rank_v101 import pre_freeze_window_evidence
except ModuleNotFoundError:
    from storia_rivive_frame_rank_v101 import pre_freeze_window_evidence

FRAME_RE = re.compile(r"frame_\d{2}\.png\Z")
SHA_RE = re.compile(r"[0-9a-f]{64}\Z")
MIN_CONTRAST = 7.0
DUPLICATE_CORRELATION = 0.985


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def signature(path):
    """Normalize only for comparison, never replace a source PNG."""
    with Image.open(path) as image:
        if image.format != "PNG" or min(image.size) < 64:
            raise ValueError("V126_INVALID_OR_TINY_SOURCE_PNG")
        image.verify()
    with Image.open(path) as image:
        gray = ImageOps.grayscale(image).resize((96, 54), Image.Resampling.LANCZOS)
        values = list(gray.tobytes())
    avg = sum(values) / len(values)
    centered = [v - avg for v in values]
    energy = sum(v * v for v in centered)
    contrast = math.sqrt(energy / len(values))
    return centered, energy, round(contrast, 3)


def correlation(a, b):
    av, ae, _ = a
    bv, be, _ = b
    if ae <= 0 or be <= 0:
        return 0.0
    return sum(x*y for x, y in zip(av, bv)) / math.sqrt(ae*be)



def check_source_pts_provenance(v125_report, scout_path):
    """Reconcile every selected V125 row with V124's original FFmpeg PTS ledger.

    A fifth of the film is not a camera shot: these checks prevent accidental
    mismatch or metadata substitutions, NOT certify edits, identity or rights.
    """
    scout = json.loads(Path(scout_path).read_text(encoding="utf-8"))
    digest = v125_report["source_video_sha256"]
    if (scout.get("status") != "REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW"
            or scout.get("adaptive_research_version")
               != "V124_UNAPPROVED_LONG_SEGMENT_TARGET_SAMPLING"
            or scout.get("original_sha256") != digest
            or scout.get("frame_provenance_source_sha256") != digest
            or scout.get("historical_camera_shots_verified") is not False):
        raise ValueError("V126_SCOUT_SOURCE_SHA_OR_REVIEW_STATE_INVALID")
    analysis = scout.get("shot_boundary_analysis")
    duration = scout.get("duration_s")
    if (not isinstance(analysis, dict)
            or analysis.get("version") != "V113_FFMPEG_SCENE_CANDIDATES"
            or analysis.get("source_sha256") != digest
            or analysis.get("status") != "FIVE_SEGMENTS_POSSIBLE_REVIEW_REQUIRED"
            or type(duration) not in (int, float) or not math.isfinite(duration)
            or duration <= 0):
        raise ValueError("V126_SCOUT_CUT_PROVENANCE_INVALID")
    cuts = analysis.get("cut_candidate_times_s")
    if (not isinstance(cuts, list) or len(cuts) < 4
            or any(type(x) not in (int, float) or not math.isfinite(x)
                   or x <= 0 or x >= duration for x in cuts)
            or any(a >= b for a, b in zip(cuts, cuts[1:]))):
        raise ValueError("V126_SCOUT_CUT_TIMESTAMPS_INVALID")
    provenance = scout.get("frame_provenance")
    if not isinstance(provenance, list) or not 5 <= len(provenance) <= 48:
        raise ValueError("V126_SCOUT_PTS_PROVENANCE_MISSING")
    by_name = {}
    for original in provenance:
        if not isinstance(original, dict):
            raise ValueError("V126_SCOUT_PTS_ROW_INVALID")
        name = original.get("filename")
        if not isinstance(name, str) or not FRAME_RE.fullmatch(name) or name in by_name:
            raise ValueError("V126_SCOUT_FRAME_NAME_DUPLICATED")
        by_name[name] = original
    seen_segments = set()
    for row in v125_report["five_review_shots"]:
        original = by_name.get(row["filename"])
        if (original is None
                or original.get("source_pts_logged_from_decode") is not True
                or original.get("sha256") != row["frame_sha256"]
                or original.get("source_pts") != row.get("source_pts")
                or original.get("source_pts_time_s") != row.get("source_time_s")
                or original.get("source_time_base") != row.get("time_base")
                or original.get("shot_candidate_segment_index")
                   != row.get("candidate_segment_index")):
            raise ValueError("V126_V125_SOURCE_PTS_OR_FRAME_SHA_MISMATCH")
        seconds = original.get("source_pts_time_s")
        segment = original.get("shot_candidate_segment_index")
        if (type(seconds) not in (int, float) or not math.isfinite(seconds)
                or not 0 <= seconds < duration
                or type(segment) is not int
                or segment != bisect.bisect_right(cuts, seconds)
                or segment in seen_segments
                or row["timeline_region"] != min(4, int(seconds*5/duration))):
            raise ValueError("V126_FAKE_TIMELINE_REGION_OR_SEGMENT")
        seen_segments.add(segment)
        window = pre_freeze_window_evidence(original, cuts)
        embedded = row.get("pre_freeze_window_pts")
        if (window.get("eligible") is not True
                or not isinstance(embedded, dict)
                or any(embedded.get(key) != window.get(key)
                       for key in ("start_pts", "freeze_pts", "time_base"))):
            raise ValueError("V126_SOURCE_FREEZE_PTS_WINDOW_MISMATCH")
    return True


def audit(v125_path, frames_folder, out_path, scout_path):
    """Inspect exact five source-locked V125 selections, without clearing QA."""
    report = json.loads(Path(v125_path).read_text(encoding="utf-8"))
    if (report.get("version") != "V125_REAL_BW_DECODED_SPATIAL_MOTION_UNAPPROVED"
            or report.get("status") != "V125_FIVE_MOVING_PHOTO_REGIONS_REVIEW_REQUIRED"
            or report.get("five_genuine_camera_shots_approved") is not False
            or report.get("italian_rights_verified") is not False):
        raise ValueError("V126_V125_NOT_IN_REVIEW_STATE")
    rows = report.get("five_review_shots")
    if not isinstance(rows, list) or len(rows) != 5:
        raise ValueError("V126_NEED_FIVE_SOURCE_FRAMES")
    film_sha = report.get("source_video_sha256")
    if not isinstance(film_sha, str) or not SHA_RE.fullmatch(film_sha):
        raise ValueError("V126_FILM_SHA_MISSING")
    check_source_pts_provenance(report, scout_path)
    root = Path(frames_folder)
    names, hashes, regions, sigs = set(), set(), set(), []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("V126_SOURCE_ROW_INVALID")
        name, digest = row.get("filename"), row.get("frame_sha256")
        if (not isinstance(name, str) or not FRAME_RE.fullmatch(name)
                or name in names or not isinstance(digest, str)
                or not SHA_RE.fullmatch(digest) or digest in hashes
                or row.get("source_film_sha256") != film_sha
                or row.get("human_camera_shot_approval") is not False):
            raise ValueError("V126_SOURCE_IDENTITY_OR_APPROVAL_INVALID")
        region = row.get("timeline_region")
        if type(region) is not int or not 0 <= region <= 4 or region in regions:
            raise ValueError("V126_DUPLICATE_OR_INVALID_TIME_REGION")
        path = root / name
        if not path.is_file() or path.is_symlink() or sha256_file(path) != digest:
            raise ValueError("V126_SOURCE_PNG_BYTES_MISSING_OR_TAMPERED")
        names.add(name)
        hashes.add(digest)
        regions.add(region)
        sigs.append((name, signature(path)))
    weak = [{"filename": name, "grayscale_contrast": sig[2]}
            for name, sig in sigs if sig[2] < MIN_CONTRAST]
    near = []
    for i in range(5):
        for j in range(i+1, 5):
            sim = correlation(sigs[i][1], sigs[j][1])
            if sim >= DUPLICATE_CORRELATION:
                near.append({"first": sigs[i][0], "second": sigs[j][0],
                             "grayscale_correlation": round(sim, 5)})
    if weak:
        status = "V126_LOW_DETAIL_SOURCE_FRAMES_BLOCKED"
    elif near:
        status = "V126_NEAR_DUPLICATE_FRAMES_BLOCKED_FOR_REVIEW"
    else:
        status = "V126_VISUALLY_DIVERSE_FRAMES_REVIEW_REQUIRED"
    result = {
        "version": "V126_FIVE_SOURCE_FRAMES_VISUAL_DUPLICATE_REVIEW",
        "status": status,
        "source_video_sha256": film_sha,
        "source_frame_count": 5,
        "original_pts_provenance_crosschecked": True,
        "near_duplicate_pairs": near,
        "low_contrast_frames": weak,
        "five_genuine_camera_shots_approved": False,
        "italian_rights_verified": False,
        "human_review_required": True,
        "i2i_calls": 0, "vidu_calls": 0, "published": False,
        "note": "Appearance similarity is a conservative warning, not proof of camera cuts."
    }
    output = Path(out_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--v125", required=True)
    parser.add_argument("--frames", required=True)
    parser.add_argument("--scout", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    try:
        result = audit(args.v125, args.frames, args.out, args.scout)
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        result = {"version": "V126_FIVE_SOURCE_FRAMES_VISUAL_DUPLICATE_REVIEW",
                  "status": "V126_SOURCE_FRAME_AUDIT_BLOCKED",
                  "reason": str(exc)[:200], "near_duplicate_pairs": [],
                  "original_pts_provenance_crosschecked": False,
                  "five_genuine_camera_shots_approved": False,
                  "italian_rights_verified": False, "human_review_required": True,
                  "i2i_calls": 0, "vidu_calls": 0, "published": False}
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print("V126_VISUAL_SOURCE_AUDIT", result["status"])


if __name__ == "__main__":
    main()
