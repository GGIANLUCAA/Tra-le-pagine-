#!/usr/bin/env python3
"""V210: choose five candidate source frames in different likely camera shots.

Unlike V101's score-only selection, this runs BEFORE I2I manifest creation and
uses real source-film cut candidates to prevent predictable V209 rejections.
A candidate segment is never an editorially approved shot. No provider calls.
"""
from __future__ import annotations
import argparse
import bisect
import hashlib
import json
import math
import re
from pathlib import Path

from storia_rivive_v209_shot_boundary_review import detect_boundaries, MAX_BYTES, MAX_SECONDS, LEAD_SECONDS

FRAME = re.compile(r"frame_(0[1-9]|1[0-2])\.png\Z")
READY = "FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW"


def select(ranking: dict, scout: dict, cache: Path, detector=detect_boundaries) -> dict:
    result = {"version": "V210_SHOT_AWARE_PRESELECTION",
              "status": "SHOT_AWARE_SELECTION_BLOCKED", "reason": "UNKNOWN",
              "preselected": [], "approved_restored_photos": 0,
              "five_distinct_shots_approved": False,
              "provider_calls_permitted": False, "publish_permitted": False,
              "credits_spent": 0}

    def block(reason):
        result["reason"] = reason
        return result

    if not isinstance(ranking, dict) or not isinstance(scout, dict):
        return block("INVALID_INPUT")
    if ranking.get("status") != READY:
        return block("V101_RANKING_NOT_READY")
    frames = ranking.get("all_candidates")
    if not isinstance(frames, list) or len(frames) != scout.get("source_frames_extracted"):
        return block("INVALID_FRAME_COUNT")
    duration = scout.get("duration_s")
    if isinstance(duration, bool) or not isinstance(duration, (float, int)) or not math.isfinite(duration) or duration < 5:
        return block("INVALID_DURATION")
    period = max(1.0, duration / 12)
    if duration > MAX_SECONDS:
        return block("SOURCE_TOO_LONG_FOR_BOUNDED_SCENE_SCAN")
    film = cache / "ORIGINAL_ARCHIVE.webm"
    expected = scout.get("original_sha256")
    if (film.is_symlink() or not film.is_file() or not 0 < film.stat().st_size <= MAX_BYTES
            or not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected)):
        return block("INVALID_SOURCE_FILM")
    if hashlib.sha256(film.read_bytes()).hexdigest() != expected:
        return block("SOURCE_HASH_CHANGED")
    if len(frames) < 6:
        return block("TOO_FEW_SCOUT_FRAMES")
    try:
        boundaries = detector(film, float(duration))
    except Exception:
        return block("CUT_DETECTION_FAILED")
    if not isinstance(boundaries, list) or any(not isinstance(x, (int, float)) or not math.isfinite(x) for x in boundaries):
        return block("INVALID_DETECTOR_OUTPUT")
    boundaries = sorted(set(float(x) for x in boundaries if 0 < x < duration))
    candidates = {}
    for row in frames:
        if not isinstance(row, dict):
            return block("INVALID_FRAME_ROW")
        name = row.get("filename")
        if not isinstance(name, str) or not FRAME.fullmatch(name):
            return block("INVALID_FRAME_NAME")
        index = int(name[6:8])
        t = (index - 1) * period
        score = row.get("source_visual_quality_score")
        if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score):
            return block("INVALID_SCORE")
        if t < LEAD_SECONDS + 0.1 or t >= duration:
            continue
        start_segment = bisect.bisect_right(boundaries, t - LEAD_SECONDS)
        end_segment = bisect.bisect_right(boundaries, t)
        if start_segment != end_segment:
            continue
        item = (float(score), -index, row, t)
        if end_segment not in candidates or item[:2] > candidates[end_segment][:2]:
            candidates[end_segment] = item
    if len(candidates) < 5:
        result["candidate_segments_available"] = len(candidates)
        result["detected_cut_count"] = len(boundaries)
        return block("FIVE_SHOT_SEGMENTS_WITH_VALID_LEADIN_UNAVAILABLE")
    # Prefer quality, then preserve chronological ordering for the 4+1 story.
    chosen = sorted(candidates.values(), key=lambda item: (-item[0], -item[1]))[:5]
    chosen.sort(key=lambda item: item[3])
    result.update({"status": READY, "reason": "FIVE_CANDIDATE_SHOTS_NOT_APPROVED",
                   "preselected": [item[2] for item in chosen],
                   "candidate_segment_times_s": [round(item[3], 3) for item in chosen],
                   "detected_cut_count": len(boundaries),
                   "selection_is_not_verified_distinct_film_shots": True,
                   "manual_source_and_rights_review_required": True})
    return result


def main():
    parser = argparse.ArgumentParser()
    for name in ("ranking", "scout", "cache", "out"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    try:
        result = select(json.loads(Path(args.ranking).read_text()),
                        json.loads(Path(args.scout).read_text()), Path(args.cache))
    except (OSError, ValueError, TypeError):
        result = {"version": "V210_SHOT_AWARE_PRESELECTION",
                  "status": "SHOT_AWARE_SELECTION_BLOCKED",
                  "reason": "INVALID_OR_MISSING_INPUT", "preselected": [],
                  "provider_calls_permitted": False, "publish_permitted": False}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(result["status"], result["reason"])


if __name__ == "__main__":
    main()
