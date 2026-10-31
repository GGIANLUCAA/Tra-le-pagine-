#!/usr/bin/env python3
"""V124: source-locked supplemental sampling in real archival shot candidates.

Offline/free research ONLY. Does not replace V101's 12 original frames, request
I2I, call Vidu, certify camera shots, clear Italian rights or publish video.
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

try:
    from src.storia_rivive_frame_rank_v101 import rank
except ModuleNotFoundError:
    from storia_rivive_frame_rank_v101 import rank

MIN_SEGMENT_S = 1.85
MAX_TARGETS = 48
SHOWINFO = re.compile(
    r"\[Parsed_showinfo_\d+\s+@[^\]]+\]\s+n:\s*(\d+)\s+pts:\s*(-?\d+)"
    r"\s+pts_time:\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))"
)
TIME_BASE = re.compile(
    r"\[Parsed_showinfo_\d+\s+@[^\]]+\]\s+config in time_base:\s*(\d+/\d+)"
)


def sha256_file(path):
    hasher = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for piece in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(piece)
    return hasher.hexdigest()


def choose_targets(analysis, duration, *, limit=MAX_TARGETS):
    """Find spaced, long-enough V113 segments, one target per candidate cut.

    A V113 scene boundary is a *candidate*, not a genuine different shot.
    Targets stay >=1.45s after their proposed start for B/W lead-in room.
    """
    if (not isinstance(analysis, dict)
            or analysis.get("version") != "V113_FFMPEG_SCENE_CANDIDATES"
            or analysis.get("status") != "FIVE_SEGMENTS_POSSIBLE_REVIEW_REQUIRED"):
        raise ValueError("V124_SHOT_ANALYSIS_UNAVAILABLE")
    if not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration <= 3:
        raise ValueError("V124_SOURCE_DURATION_INVALID")
    cuts = analysis.get("cut_candidate_times_s")
    if (not isinstance(cuts, list) or len(cuts) < 4
            or any(type(t) not in (int, float) or not math.isfinite(t) or t <= 0 or t >= duration for t in cuts)
            or any(a >= b for a, b in zip(cuts, cuts[1:]))):
        raise ValueError("V124_CUT_TIMES_INVALID")
    if type(limit) is not int or not 5 <= limit <= MAX_TARGETS:
        raise ValueError("V124_TARGET_LIMIT_INVALID")
    eligible = []
    bounds = [0.0] + cuts + [float(duration)]
    for segment, (start, end) in enumerate(zip(bounds, bounds[1:])):
        if end - start < MIN_SEGMENT_S:
            continue
        # A source-PTS frame >=1.5s after cut permits 1.35s B/W + 0.05s buffer.
        freeze_at = start + min(2.35, max(1.5, 0.55 * (end - start)))
        if freeze_at >= end - 0.20:
            continue
        eligible.append({
            "candidate_segment_index": segment,
            "target_time_s": round(freeze_at, 5),
            "proposed_segment_start_s": start,
            "proposed_segment_end_s": end,
        })
    if len(eligible) < 5:
        raise ValueError("V124_NOT_ENOUGH_LONG_SOURCE_SEGMENTS")
    if len(eligible) > limit:
        idx = [round(i * (len(eligible) - 1) / (limit - 1)) for i in range(limit)]
        eligible = [eligible[i] for i in idx]
    if len({row["candidate_segment_index"] for row in eligible}) != len(eligible):
        raise ValueError("V124_DUPLICATE_SHOT_CANDIDATES")
    return eligible


def extract_target_frames(film, folder, targets, *, max_runtime_s=230):
    """One original-film FFmpeg decode, no CFR conversion, exact showinfo PTS.

    FFmpeg selected_n counts prior selected frames; each gte selects exactly the
    earliest decoded ORIGINAL frame at/after its targeted scene timestamp.
    """
    if not 5 <= len(targets) <= MAX_TARGETS:
        raise ValueError("V124_TARGET_COUNT_INVALID")
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    if list(folder.glob("frame_*.png")):
        raise ValueError("V124_OUTPUT_FRAMES_ALREADY_EXIST")
    expression = "+".join(
        f"eq(selected_n,{i})*gte(t,{t['target_time_s']:.5f})"
        for i, t in enumerate(targets)
    )
    args = [
        "ffmpeg", "-nostdin", "-y", "-hide_banner", "-loglevel", "info",
        "-i", str(film), "-an", "-sn", "-vf", f"select='{expression}',showinfo",
        "-fps_mode", "vfr", "-frames:v", str(len(targets)),
        str(folder / "frame_%02d.png")
    ]
    try:
        result = subprocess.run(
            args, capture_output=True, text=True, check=True, timeout=max_runtime_s)
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as exc:
        raise ValueError("V124_ORIGINAL_FRAME_DECODE_FAILED_OR_TIMEOUT") from exc
    pts_rows = SHOWINFO.findall(result.stderr)
    bases = TIME_BASE.findall(result.stderr)
    files = sorted(folder.glob("frame_*.png"))
    if (len(pts_rows) != len(targets) or len(files) != len(targets)
            or len(bases) != 1 or not re.fullmatch(r"[1-9]\d*/[1-9]\d*", bases[0])):
        raise ValueError("V124_NATIVE_PTS_OUTPUT_COUNT_OR_TIMEBASE_INVALID")
    records = []
    last = -1.0
    n, d = map(int, bases[0].split("/"))
    for i, (show_n, pts, pts_time) in enumerate(pts_rows):
        frame = files[i]
        seconds = float(pts_time)
        ticks = int(pts)
        if (int(show_n) != i or not math.isfinite(seconds)
                or seconds <= last
                or abs(ticks * n / d - seconds) > 0.0001
                or seconds + 0.0001 < targets[i]["target_time_s"]):
            raise ValueError("V124_SOURCE_PTS_NOT_GENUINE_OR_MONOTONIC")
        last = seconds
        row = {
            "filename": frame.name,
            "sha256": sha256_file(frame),
            "extraction_index": i,
            "source_pts": ticks,
            "source_pts_time_s": seconds,
            "source_time_base": bases[0],
            "source_pts_logged_from_decode": True,
            "shot_candidate_segment_index": targets[i]["candidate_segment_index"],
            "target_time_s": targets[i]["target_time_s"],
            "historical_camera_shot_verified": False,
            "exact_source_timecode_verified": False,
        }
        if seconds >= targets[i]["proposed_segment_end_s"] - 0.05:
            # This frame may be a valid original, but not a safe candidate cut.
            row["shot_candidate_segment_index"] = -1
        records.append(row)
    return records


def spread_review_shortlist(selection, provenance, duration_s):
    """Prefer one actual source frame per fifth of the film for editorial review.

    Does NOT authenticate shots or human subjects. Never mark a source approved.
    If one film region has no safe photographic sample, fail closed rather than
    presenting a visually repetitive shortlist as five distinct historical shots.
    """
    rows = selection.get("all_candidates", [])
    if not isinstance(rows, list) or not rows:
        return {"status": "V124_NO_PHOTOGRAPHIC_FRAMES", "preselected": []}
    by_name = {p.get("filename"): p for p in provenance if isinstance(p, dict)}
    candidates = []
    for row in rows:
        if (row.get("source_picture_content_eligible") is not True
                or row.get("source_native_detail_sufficient") is not True
                or row.get("pre_freeze_window_viable") is not True):
            continue
        source = by_name.get(row.get("filename"))
        if not source or type(source.get("shot_candidate_segment_index")) is not int:
            continue
        seconds = source.get("source_pts_time_s")
        if type(seconds) not in (int, float) or not math.isfinite(seconds) or not 0 <= seconds < duration_s:
            continue
        bucket = min(4, int(seconds * 5 / duration_s))
        candidates.append({**row, "source_pts_time_s": seconds, "review_time_bucket": bucket,
                           "candidate_segment_index": source["shot_candidate_segment_index"]})
    five = []
    used_segments = set()
    for bucket in range(5):
        ranked = sorted(
            (x for x in candidates
             if x["review_time_bucket"] == bucket and x["candidate_segment_index"] not in used_segments),
            key=lambda x: (-x["source_visual_quality_score"], x["source_pts_time_s"]))
        if not ranked:
            return {"status": "V124_NOT_FIVE_SPREAD_REGIONS", "preselected": [],
                    "regions_with_eligible_photo": sorted({x["review_time_bucket"] for x in candidates}),
                    "photographic_candidates_not_approved": len(candidates)}
        chosen = ranked[0]
        used_segments.add(chosen["candidate_segment_index"])
        five.append(chosen)
    return {"status": "V124_FIVE_TIME_SPREAD_SOURCE_CANDIDATES_REVIEW_ONLY",
            "preselected": five,
            "region_count": 5,
            "photographic_candidates_not_approved": len(candidates),
            "historical_camera_shots_verified": False,
            "artistic_approved": False}


def contact_sheet(frames, provenance, output, *, columns=6, rows=None):
    paths = sorted(Path(frames).glob("frame_*.png"))
    if len(paths) != len(provenance):
        raise ValueError("V124_CONTACT_SHEET_PTS_MISMATCH")
    rows = rows or math.ceil(len(paths) / columns)
    width, height = 300, 192
    board = Image.new("RGB", (columns * width, rows * height), (16, 16, 16))
    draw = ImageDraw.Draw(board)
    for i, path in enumerate(paths):
        with Image.open(path) as source:
            frame = source.convert("RGB")
            frame.thumbnail((width - 12, height - 26))
        x, y = (i % columns) * width, (i // columns) * height
        board.paste(frame, (x + (width-frame.width)//2, y+24))
        info = provenance[i]
        draw.text((x+5, y+5), f"{path.stem}  {info['source_pts_time_s']:.2f}s  "
                  f"seg#{info['shot_candidate_segment_index']}", fill=(245, 245, 245))
    board.save(output, quality=90)


def inspect(film_path, original_scout_path, output_root, *, limit=MAX_TARGETS):
    """Produce only source-locked research files and an unapproved shortlist."""
    film_path = Path(film_path)
    scout = json.loads(Path(original_scout_path).read_text(encoding="utf-8"))
    if scout.get("status") != "REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW":
        raise ValueError("V124_ORIGINAL_SOURCE_NOT_READY")
    source_sha = scout.get("original_sha256")
    if not isinstance(source_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", source_sha):
        raise ValueError("V124_ORIGINAL_SOURCE_SHA_MISSING")
    if sha256_file(film_path) != source_sha:
        raise ValueError("V124_SOURCE_BYTES_SHA_MISMATCH")
    analysis = scout.get("shot_boundary_analysis")
    if not isinstance(analysis, dict) or analysis.get("source_sha256") != source_sha:
        raise ValueError("V124_CUT_SOURCE_SHA_MISMATCH")
    targets = choose_targets(analysis, scout.get("duration_s"), limit=limit)
    root = Path(output_root)
    frames = root / "original_frames"
    provenance = extract_target_frames(film_path, frames, targets)
    derived = dict(scout)
    derived["frame_provenance"] = provenance
    derived["frame_provenance_source_sha256"] = source_sha
    derived["frame_provenance_version"] = "V112_SOURCE_PTS_FROM_FFMPEG_SHOWINFO"
    derived["source_frames_extracted"] = len(provenance)
    derived["status"] = "REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW"
    derived["adaptive_research_version"] = "V124_UNAPPROVED_LONG_SEGMENT_TARGET_SAMPLING"
    derived["historical_camera_shots_verified"] = False
    root.mkdir(parents=True, exist_ok=True)
    (root / "SCOUT_REPORT.json").write_text(
        json.dumps(derived, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    contact_sheet(frames, provenance, root / "ADAPTIVE_CONTACT_SHEET_V124.jpg")
    selection = rank(frames)
    original_score_shortlist = [r["filename"] for r in selection.get("preselected", [])]
    spread = spread_review_shortlist(selection, provenance, scout["duration_s"])
    selection["original_score_only_preselected_files"] = original_score_shortlist
    selection["adaptive_temporal_spread_review"] = spread
    selection["preselected"] = spread["preselected"]
    if spread["status"] != "V124_FIVE_TIME_SPREAD_SOURCE_CANDIDATES_REVIEW_ONLY":
        selection["status"] = "INSUFFICIENT_TEMPORALLY_DIVERSE_PHOTOGRAPHIC_SOURCE_CANDIDATES"
    selection["adaptive_frame_source_sha256"] = source_sha
    selection["adaptive_review_only_not_camera_approval"] = True
    selection["sampled_candidate_segment_count"] = len(targets)
    (root / "ADAPTIVE_RANK_V124.json").write_text(
        json.dumps(selection, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    # Keep full-res source PNG samples only inside the private runner. A contact
    # sheet plus SHA-locked provenance/report is archived for human review.
    return {
        "status": "V124_SOURCE_RESEARCH_COMPLETE_NOT_APPROVED",
        "source_sha256": source_sha,
        "sampled": len(targets),
        "photographic_candidates": selection.get("eligible_photographic_scene_candidates", 0),
        "preselected": [z["filename"] for z in selection.get("preselected", [])],
        "selection_status": selection.get("status"),
        "temporal_spread_status": spread.get("status"),
        "italy_rights_verified": False,
        "artistic_approved": False,
        "paid_calls": 0,
        "video_finished": False
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--film", required=True)
    p.add_argument("--scout", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--limit", type=int, default=MAX_TARGETS)
    a = p.parse_args()
    root = Path(a.out)
    try:
        outcome = inspect(a.film, a.scout, root, limit=a.limit)
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        outcome = {"status": "V124_ADAPTIVE_SOURCE_RESEARCH_BLOCKED",
                   "reason": str(exc)[:240], "paid_calls": 0,
                   "video_finished": False}
    root.mkdir(parents=True, exist_ok=True)
    (root / "ADAPTIVE_STATUS_V124.json").write_text(
        json.dumps(outcome, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("V124_SOURCE_ONLY", outcome["status"],
          "samples", outcome.get("sampled",0),
          "photographic_candidates", outcome.get("photographic_candidates",0))


if __name__ == "__main__":
    main()
