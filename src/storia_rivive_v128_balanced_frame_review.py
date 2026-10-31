#!/usr/bin/env python3
"""V128: offline source-locked contact sheet of V126's five balanced film frames.

Review only: different source regions/PTS and pixel appearance do NOT certify
five genuine camera shots, Italian rights, I2I, Vidu or artistic quality.
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import math
import re
from collections import Counter
from fractions import Fraction
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

SHA = re.compile(r"[0-9a-f]{64}\Z")
FRAME = re.compile(r"frame_\d{2}\.png\Z")
MIN_CONTRAST = 7.0
DUPLICATE_CORRELATION = 0.985
MIN_SPACING_S = 12.0


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def visual_signature(path):
    with Image.open(path) as frame:
        if frame.format != "PNG" or min(frame.size) < 64:
            raise ValueError("V128_SOURCE_PNG_INVALID_OR_TINY")
        frame.verify()
    with Image.open(path) as frame:
        values = list(ImageOps.grayscale(frame).resize((96, 54), Image.Resampling.LANCZOS).tobytes())
    center = sum(values) / len(values)
    vector = [x - center for x in values]
    energy = sum(x*x for x in vector)
    return vector, energy, round(math.sqrt(energy/len(vector)), 3)


def correlation(a, b):
    if a[1] <= 0 or b[1] <= 0:
        return 0.0
    return sum(x*y for x, y in zip(a[0], b[0])) / math.sqrt(a[1]*b[1])


def verified_source_rows(balanced, motion, scout, frames):
    """Fail closed before opening pixels when any provenance field disagrees."""
    film_sha = motion.get("source_video_sha256")
    if (not isinstance(film_sha, str) or SHA.fullmatch(film_sha) is None
            or motion.get("version") != "V125_REAL_BW_DECODED_SPATIAL_MOTION_UNAPPROVED"
            or motion.get("status") not in ("V125_MOTION_SOURCE_SELECTION_BLOCKED",
                                            "V125_FIVE_MOVING_PHOTO_REGIONS_REVIEW_REQUIRED")
            or motion.get("five_genuine_camera_shots_approved") is not False
            or motion.get("italian_rights_verified") is not False):
        raise ValueError("V128_V125_SOURCE_REPORT_INVALID")
    if (balanced.get("version") != "V126_FIVE_DIVERSE_MOVING_SHOTS_NOT_APPROVED"
            or balanced.get("status") != "V126_FIVE_DIFFERENT_MOVING_SOURCE_CANDIDATES_REVIEW_ONLY"
            or balanced.get("source_film_sha256") != film_sha
            or balanced.get("five_real_camera_shots_verified") is not False
            or balanced.get("human_artistic_approved") is not False
            or balanced.get("italian_rights_verified") is not False
            or balanced.get("video_finished") is not False):
        raise ValueError("V128_BALANCED_SOURCE_OR_UNAPPROVED_STATE_INVALID")
    if (scout.get("original_sha256") != film_sha
            or scout.get("frame_provenance_source_sha256") != film_sha
            or scout.get("status") != "REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW"
            or scout.get("adaptive_research_version") != "V124_UNAPPROVED_LONG_SEGMENT_TARGET_SAMPLING"
            or scout.get("historical_camera_shots_verified") is not False):
        raise ValueError("V128_SCOUT_FILM_PROVENANCE_INVALID")
    cuts_data = scout.get("shot_boundary_analysis")
    duration = scout.get("duration_s")
    if (not isinstance(cuts_data, dict)
            or cuts_data.get("version") != "V113_FFMPEG_SCENE_CANDIDATES"
            or cuts_data.get("source_sha256") != film_sha
            or cuts_data.get("status") != "FIVE_SEGMENTS_POSSIBLE_REVIEW_REQUIRED"
            or type(duration) not in (int, float) or not math.isfinite(duration) or duration <= 0
            or motion.get("source_duration_s") != duration
            or balanced.get("source_duration_s") != duration):
        raise ValueError("V128_SOURCE_TIMELINE_INVALID")
    cuts = cuts_data.get("cut_candidate_times_s")
    if (not isinstance(cuts, list) or len(cuts) < 4
            or any(type(t) not in (int, float) or not math.isfinite(t)
                   or t <= 0 or t >= duration for t in cuts)
            or any(x >= y for x, y in zip(cuts, cuts[1:]))):
        raise ValueError("V128_SOURCE_CUTS_INVALID")
    original = scout.get("frame_provenance")
    audited = motion.get("motion_audit")
    selected = balanced.get("five_review_candidates")
    if (not isinstance(original, list) or not 5 <= len(original) <= 48
            or not isinstance(audited, list) or not isinstance(selected, list) or len(selected) != 5
            or len(audited) > len(original)):
        raise ValueError("V128_FIVE_REVIEW_CANDIDATES_OR_EVIDENCE_MISSING")
    originals = {r.get("filename"): r for r in original if isinstance(r, dict)}
    motions = {r.get("filename"): r for r in audited if isinstance(r, dict)}
    if len(originals) != len(original) or len(motions) != len(audited):
        raise ValueError("V128_DUPLICATE_SOURCE_EVIDENCE")
    used_files, used_segments, used_sha, regions, rows = set(), set(), set(), [], []
    for selected_row in selected:
        if not isinstance(selected_row, dict):
            raise ValueError("V128_SELECTED_ROW_INVALID")
        name = selected_row.get("filename")
        if (not isinstance(name, str) or FRAME.fullmatch(name) is None
                or name in used_files or name not in originals or name not in motions):
            raise ValueError("V128_SELECTED_FRAME_MISSING_OR_DUPLICATED")
        src, evidence = originals[name], motions[name]
        digest = src.get("sha256")
        if (not isinstance(digest, str) or SHA.fullmatch(digest) is None
                or digest in used_sha or selected_row.get("source_frame_sha256") != digest
                or selected_row.get("source_film_sha256") != film_sha
                or src.get("source_pts_logged_from_decode") is not True):
            raise ValueError("V128_SOURCE_FRAME_SHA_OR_PTS_LEDGER_INVALID")
        ticks, seconds, clock = (src.get("source_pts"), src.get("source_pts_time_s"),
                                 src.get("source_time_base"))
        try:
            n, d = (int(v) for v in clock.split("/"))
            period = Fraction(n, d)
            valid_clock = (type(ticks) is int and ticks >= 0 and n > 0 and d > 0
                           and type(seconds) in (int, float) and math.isfinite(seconds)
                           and 0 <= seconds < duration
                           and abs(float(ticks*period)-seconds) <= .0001)
        except (AttributeError, TypeError, ValueError, ZeroDivisionError):
            valid_clock = False
        if not valid_clock:
            raise ValueError("V128_NATIVE_SOURCE_PTS_CLOCK_INVALID")
        segment = bisect.bisect_right(cuts, seconds)
        region = min(4, int(seconds*5/duration))
        if (segment in used_segments or src.get("shot_candidate_segment_index") != segment
                or selected_row.get("candidate_segment_index") != segment
                or selected_row.get("timeline_region") != region
                or selected_row.get("source_pts") != ticks
                or selected_row.get("source_pts_time_s") != seconds
                or selected_row.get("source_time_base") != clock
                or selected_row.get("motion_verified_for_review") is not True
                or selected_row.get("genuine_camera_shot_verified") is not False
                or selected_row.get("human_artistic_approved") is not False):
            raise ValueError("V128_SELECTED_FRAME_TIMELINE_OR_APPROVAL_FORGED")
        start_s = max(0.0, (cuts[segment-1] if segment else 0.0)+0.05, seconds-1.35)
        expected_window = {"start_pts": math.ceil(Fraction(str(start_s))/period),
                           "freeze_pts": ticks, "time_base": clock}
        selected_window = selected_row.get("pre_freeze_window_pts")
        if (not isinstance(selected_window, dict)
                or any(selected_window.get(k) != v for k, v in expected_window.items())
                or expected_window["start_pts"] >= ticks):
            raise ValueError("V128_ORIGINAL_FREEZE_WINDOW_PTS_MISMATCH")
        if (evidence.get("status") != "MOTION_EVIDENCE_PASS"
                or evidence.get("motion_verified") is not True
                or type(evidence.get("changed_pairs")) is not int or evidence["changed_pairs"] < 2
                or type(evidence.get("sample_count")) is not int or evidence["sample_count"] < 5
                or type(evidence.get("max_spatial_pixel_delta")) not in (int, float)
                or not math.isfinite(evidence["max_spatial_pixel_delta"])
                or evidence["max_spatial_pixel_delta"] < 6
                or evidence.get("source_pts") != ticks
                or evidence.get("source_time_s") != seconds
                or evidence.get("candidate_segment_index") != segment
                or any(evidence.get(k) != v for k, v in expected_window.items())):
            raise ValueError("V128_MOTION_EVIDENCE_MISSING_OR_SOURCE_MISMATCH")
        used_files.add(name); used_segments.add(segment); used_sha.add(digest)
        regions.append(region)
        rows.append({"filename": name, "source_pts_time_s": seconds,
                     "candidate_segment_index": segment, "timeline_region": region,
                     "frame_sha256": digest, "source_film_sha256": film_sha})
    times = [r["source_pts_time_s"] for r in rows]
    counts = Counter(regions)
    if (len(counts) < 3 or max(counts.values()) > 2
            or any(b-a < MIN_SPACING_S for a,b in zip(sorted(times),sorted(times)[1:]))
            or balanced.get("selected_timeline_regions") != sorted(counts)
            or balanced.get("minimum_seconds_between_freezes") != MIN_SPACING_S):
        raise ValueError("V128_BALANCED_REVIEW_SHOT_DIVERSITY_INSUFFICIENT")
    # Avoid even decoding arbitrary paths before all V124/V125/V126 evidence is coherent.
    root = Path(frames)
    for row in rows:
        path = root / row["filename"]
        if not path.is_file() or path.is_symlink() or sha256_file(path) != row["frame_sha256"]:
            raise ValueError("V128_ORIGINAL_PNG_BYTES_MISSING_OR_CHANGED")
    return rows


def inspect(balanced_file, motion_file, scout_file, frames_folder, out_file, contact_file):
    balanced = json.loads(Path(balanced_file).read_text(encoding="utf-8"))
    motion = json.loads(Path(motion_file).read_text(encoding="utf-8"))
    scout = json.loads(Path(scout_file).read_text(encoding="utf-8"))
    rows = verified_source_rows(balanced, motion, scout, frames_folder)
    image_signatures = [(r["filename"], visual_signature(Path(frames_folder)/r["filename"]))
                        for r in rows]
    low = [{"filename": name, "contrast": sig[2]} for name,sig in image_signatures
           if sig[2] < MIN_CONTRAST]
    repeats = []
    for i in range(5):
        for j in range(i+1,5):
            score = correlation(image_signatures[i][1], image_signatures[j][1])
            if score >= DUPLICATE_CORRELATION:
                repeats.append({"first": image_signatures[i][0], "second": image_signatures[j][0],
                                "grayscale_correlation": round(score,5)})
    status = ("V128_LOW_CONTRAST_FRAMES_BLOCKED" if low else
              "V128_NEAR_DUPLICATE_FRAMES_BLOCKED" if repeats else
              "V128_FIVE_BALANCED_FRAMES_VISUAL_REVIEW_REQUIRED")
    result = {
        "version": "V128_BALANCED_REAL_ORIGINAL_FRAME_REVIEW_ONLY",
        "status": status, "source_film_sha256": motion["source_video_sha256"],
        "five_review_frames": rows,
        "original_pts_sha_motion_evidence_crosschecked": True,
        "near_duplicate_pairs": repeats, "low_contrast_frames": low,
        "genuine_camera_shots_verified": False, "historical_year_verified": False,
        "italian_rights_verified": False, "human_artistic_approved": False,
        "four_i2i_approved": False, "vidu_clip_approved": False,
        "paid_api_calls": 0, "video_finished": False, "published": False,
        "note": "Pixel difference and time separation cannot certify five camera shots."
    }
    Path(out_file).parent.mkdir(parents=True, exist_ok=True)
    Path(out_file).write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n",encoding="utf-8")
    # Candidate contact sheet is diagnostic; never marks a shot approved.
    board = Image.new("RGB", (5*250, 220), (20,20,20))
    draw = ImageDraw.Draw(board)
    for i,row in enumerate(rows):
        with Image.open(Path(frames_folder)/row["filename"]) as image:
            preview = image.convert("RGB")
            preview.thumbnail((238, 180))
        x = i*250+(250-preview.width)//2
        board.paste(preview,(x,35+(180-preview.height)//2))
        draw.text((i*250+5,7),f"{row['filename']}  {row['source_pts_time_s']:.2f}s",fill=(245,245,245))
    Path(contact_file).parent.mkdir(parents=True, exist_ok=True)
    board.save(contact_file, quality=90)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("balanced", "motion", "scout", "frames", "out", "contact"):
        p.add_argument("--"+name, required=True)
    args = p.parse_args()
    try:
        report = inspect(args.balanced, args.motion, args.scout, args.frames,
                         args.out, args.contact)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        report = {"version": "V128_BALANCED_REAL_ORIGINAL_FRAME_REVIEW_ONLY",
                  "status": "V128_SOURCE_AUDIT_BLOCKED", "reason": str(exc)[:210],
                  "five_review_frames": [], "original_pts_sha_motion_evidence_crosschecked": False,
                  "genuine_camera_shots_verified": False, "italian_rights_verified": False,
                  "paid_api_calls": 0, "video_finished": False, "published": False}
        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n",encoding="utf-8")
    print("V128_BALANCED_VISUAL_REVIEW", report["status"])

if __name__ == "__main__":
    main()
