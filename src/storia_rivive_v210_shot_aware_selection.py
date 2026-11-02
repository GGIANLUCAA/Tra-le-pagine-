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
import itertools
import json
import math
import re
from pathlib import Path

from PIL import Image, ImageChops, ImageOps, ImageStat
from storia_rivive_v205_visual_novelty import fingerprint

from storia_rivive_v209_shot_boundary_review import detect_boundaries, MAX_BYTES, MAX_SECONDS, LEAD_SECONDS

FRAME = re.compile(r"frame_(0[1-9]|1[0-2])\.png\Z")
READY = "FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW"


def portraits_are_distinct(a, b) -> bool:
    """Reuse exactly V205's portrait-crop novelty thresholds before I2I preparation."""
    _, gray_a, norm_a, hash_a = a
    _, gray_b, norm_b, hash_b = b
    raw = ImageStat.Stat(ImageChops.difference(gray_a, gray_b)).mean[0]
    normalized = ImageStat.Stat(ImageChops.difference(norm_a, norm_b)).mean[0]
    distance = (hash_a ^ hash_b).bit_count()
    return not (min(raw, normalized) < 8 or (distance <= 5 and normalized < 20))


def likely_intertitle(path: Path) -> bool:
    """V216 conservative text-card prefilter, not a scene/rights certificate.

    Real 1920 cotton-film pilot had 10/12 samples dominated by bright
    subtitles on black backgrounds; raw edge score incorrectly ranked them
    as the best five 'restoration' sources.
    """
    with Image.open(path) as source:
        gray = ImageOps.grayscale(source).resize((160, 90))
        hist = gray.histogram()
    total = 160 * 90
    dark = sum(hist[:40]) / total
    bright = sum(hist[160:]) / total
    mean_luma = sum(level * count for level, count in enumerate(hist)) / total
    # V219: real Paramountown cards at 70/140s have grey text (<0.1%
    # pixels >=160). V216 also falsely rejected the actual 175s car shot:
    # dark background + large, connected bright vehicle != a title card.
    # Keep dark but genuinely structured photographic regions for review.
    if dark < 0.70:
        return False
    if dark >= 0.88 and mean_luma <= 26:
        return True  # unreadably dark or faint text; never feed I2I
    pixels = gray.tobytes()  # 160x90 grayscale, no OCR or new dependency
    visited = bytearray(total)
    largest = 0
    for i, value in enumerate(pixels):
        if value < 100 or visited[i]:
            continue
        visited[i] = 1
        pending = [i]
        area = 0
        while pending:
            k = pending.pop()
            area += 1
            x = k % 160
            neighbors = (k - 160 if k >= 160 else -1,
                         k + 160 if k < total - 160 else -1,
                         k - 1 if x else -1,
                         k + 1 if x < 159 else -1)
            for n in neighbors:
                if n >= 0 and not visited[n] and pixels[n] >= 100:
                    visited[n] = 1
                    pending.append(n)
        largest = max(largest, area)
        if largest >= 250:
            break
    if largest < 250:
        return True  # isolated lettering or irrecoverably dark source
    # V216's synthetic high-contrast cards are long repeated horizontal
    # lines; reject them without treating the actual bright car as text.
    broad_rows = [sum(pixels[y * 160 + x] >= 100 for x in range(160)) >= 90
                  for y in range(90)]
    separated_text_lines = sum(flag and (y == 0 or not broad_rows[y - 1])
                               for y, flag in enumerate(broad_rows))
    return bright >= 0.02 and separated_text_lines >= 3


def sha256_stream(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
    period = scout.get("sampling_period_s", max(1.0, duration / 12))
    if isinstance(period, bool) or not isinstance(period, (float, int)) or not math.isfinite(period):
        return block("INVALID_SCOUT_SAMPLING_PERIOD")
    if period < 1 or period > max(1.0, duration / 12) + 0.001:
        return block("SCOUT_SAMPLING_PERIOD_OUT_OF_BOUNDS")
    # V214: a long authentic reel is not automatically unusable. Inspect only
    # its first bounded window, and accept frames sampled within that window.
    # Never claim that later scenes were examined. No change to source SHA.
    scan_seconds = min(float(duration), float(MAX_SECONDS))
    result["film_duration_s"] = round(float(duration), 3)
    result["cut_scan_seconds"] = round(scan_seconds, 3)
    result["cut_scan_is_partial"] = duration > MAX_SECONDS
    film = cache / "ORIGINAL_ARCHIVE.webm"
    expected = scout.get("original_sha256")
    if (film.is_symlink() or not film.is_file() or not 0 < film.stat().st_size <= MAX_BYTES
            or not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected)):
        return block("INVALID_SOURCE_FILM")
    if sha256_stream(film) != expected:
        return block("SOURCE_HASH_CHANGED")
    if len(frames) < 6:
        return block("TOO_FEW_SCOUT_FRAMES")
    # V212: reject weak native portrait detail BEFORE cut detection or I2I.
    # 720p landscape and 720p 4:3 leave ~405px of real source in 9:16;
    # 480p archives leave ~270px and cannot support V98-like facial detail.
    # These are SOURCE pixels, never AI-upscaled output dimensions.
    min_crop_width, min_native_height = 400, 720
    dimensions = set()
    for row in frames:
        if not isinstance(row, dict):
            return block("INVALID_FRAME_ROW")
        name = row.get("filename")
        if not isinstance(name, str) or not FRAME.fullmatch(name):
            return block("INVALID_FRAME_NAME")
        source = cache / "original_frames" / name
        if source.is_symlink() or not source.is_file():
            return block("SOURCE_FRAME_MISSING_OR_UNSAFE")
        try:
            with Image.open(source) as image:
                if image.format != "PNG":
                    return block("INVALID_SOURCE_FRAME_FORMAT")
                width, height = image.size
                image.verify()
        except (OSError, ValueError):
            return block("SOURCE_FRAME_DECODE_FAILED")
        crop_width = min(width, round(height * 9 / 16))
        if row.get("raster_px") != [width, height] or row.get("native_portrait_crop_px") != [crop_width, height]:
            return block("RANKING_NATIVE_GEOMETRY_MISMATCH")
        dimensions.add((width, height))
        if crop_width < min_crop_width or height < min_native_height:
            result["native_portrait_crop_px"] = [crop_width, height]
            result["minimum_native_portrait_crop_px"] = [min_crop_width, min_native_height]
            return block("INSUFFICIENT_NATIVE_PORTRAIT_DETAIL")
    if len(dimensions) != 1:
        return block("MIXED_NATIVE_SOURCE_GEOMETRY")
    result["native_portrait_crop_px"] = [crop_width, height]
    result["minimum_native_portrait_crop_px"] = [min_crop_width, min_native_height]
    result["native_detail_preflight"] = "V212_ACTUAL_DECODED_SOURCE_PIXELS"
    try:
        boundaries = detector(film, scan_seconds)
    except Exception:
        return block("CUT_DETECTION_FAILED")
    if not isinstance(boundaries, list) or any(not isinstance(x, (int, float)) or not math.isfinite(x) for x in boundaries):
        return block("INVALID_DETECTOR_OUTPUT")
    boundaries = sorted(set(float(x) for x in boundaries if 0 < x < scan_seconds))
    candidates = []
    intertitles = []
    seen_names = set()
    for row in frames:
        if not isinstance(row, dict):
            return block("INVALID_FRAME_ROW")
        name = row.get("filename")
        if not isinstance(name, str) or not FRAME.fullmatch(name) or name in seen_names:
            return block("INVALID_OR_DUPLICATED_FRAME_NAME")
        seen_names.add(name)
        index = int(name[6:8])
        t = (index - 1) * period
        score = row.get("source_visual_quality_score")
        if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score):
            return block("INVALID_SCORE")
        if t < LEAD_SECONDS + 0.1 or t >= scan_seconds:
            continue
        segment = bisect.bisect_right(boundaries, t)
        if segment != bisect.bisect_right(boundaries, t - LEAD_SECONDS):
            continue
        source = cache / "original_frames" / name
        if source.is_symlink() or not source.is_file():
            return block("SOURCE_FRAME_MISSING_OR_UNSAFE")
        try:
            if likely_intertitle(source):
                intertitles.append(name)
                continue
            pixels = fingerprint(source)
        except (OSError, ValueError):
            return block("SOURCE_PORTRAIT_DECODE_FAILED")
        candidates.append((index, segment, float(score), row, t, pixels))
    segments = {item[1] for item in candidates}
    result["candidate_segments_available"] = len(segments)
    result["likely_intertitle_frames_filtered"] = intertitles
    result["likely_intertitle_count"] = len(intertitles)
    result["detected_cut_count"] = len(boundaries)
    result["portrait_candidates_checked"] = len(candidates)
    result["unscanned_late_frames"] = sum(1 for row in frames if (int(row["filename"][6:8]) - 1) * period >= scan_seconds)
    if len(segments) < 5:
        return block("FIVE_PHOTOGRAPHIC_CANDIDATE_SEGMENTS_UNAVAILABLE" if intertitles
                     else "FIVE_SHOT_SEGMENTS_WITH_VALID_LEADIN_UNAVAILABLE")

    # Check the actual visible 9:16 image, not just the camera-cut heuristic.
    # Enumerate <= 12 choose 5 (792) combinations, deterministic and cheap.
    # Greedy best-per-segment can fail when a lower-scoring alternative is
    # visually distinct, so optimize across all candidates.
    distinct = {}
    for i, j in itertools.combinations(range(len(candidates)), 2):
        distinct[i, j] = portraits_are_distinct(candidates[i][5], candidates[j][5])
    best = None
    best_key = None
    for ids in itertools.combinations(range(len(candidates)), 5):
        group = [candidates[i] for i in ids]
        if len({item[1] for item in group}) != 5:
            continue
        if any(not distinct[i, j] for i, j in itertools.combinations(ids, 2)):
            continue
        # Highest aggregate source quality; stable earlier-frame tie break.
        key = (round(sum(item[2] for item in group), 6),
               tuple(-item[0] for item in group))
        if best_key is None or key > best_key:
            best, best_key = group, key
    if best is None:
        return block("FIVE_VISUALLY_DISTINCT_SHOT_CANDIDATES_UNAVAILABLE")
    best.sort(key=lambda item: item[4])
    result.update({"status": READY, "reason": "FIVE_NONREDUNDANT_CANDIDATES_NOT_HUMAN_APPROVED",
                   "preselected": [item[3] for item in best],
                   "candidate_segment_times_s": [round(item[4], 3) for item in best],
                   "detected_cut_count": len(boundaries),
                   "visible_portrait_novelty_preflight": "V205_THRESHOLDS_REUSED_ON_SOURCE_PNG",
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
