#!/usr/bin/env python3
"""ArtVision Critico: deterministic speech-to-visible-subject gate.

Offline and additive. It does not synthesize voice, change a renderer, approve
an artwork, buy API calls, or publish video. Numeric checks are NOT visual AI:
a real frame still needs inspection and a human-verified review record.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path

SLOTS = ("critico_standard", "critico_museum")
SHA = re.compile(r"^[a-f0-9]{64}$")
SCHEMA = "artvision-narrative-focus-v1"


def _issue(code, slot=None, segment=None, suggestion=None):
    return {"code": code, "slot": slot, "segment": segment,
            "suggestion": suggestion}


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _box(value):
    return (isinstance(value, list) and len(value) == 4
            and all(_number(v) for v in value)
            and 0 <= value[0] < value[2] <= 1
            and 0 <= value[1] < value[3] <= 1)


def _coverage(crop, subject):
    x0 = max(crop[0], subject[0])
    y0 = max(crop[1], subject[1])
    x1 = min(crop[2], subject[2])
    y1 = min(crop[3], subject[3])
    intersection = max(0., x1 - x0) * max(0., y1 - y0)
    area = (subject[2] - subject[0]) * (subject[3] - subject[1])
    subject_x = (subject[0] + subject[2]) / 2
    subject_y = (subject[1] + subject[3]) / 2
    center_x = (subject_x - crop[0]) / (crop[2] - crop[0])
    center_y = (subject_y - crop[1]) / (crop[3] - crop[1])
    return intersection / area, center_x, center_y


def _sha_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _frame_from_video(video, t, target):
    """Render a real review frame, not a fabricated proof of image semantics."""
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
        "-ss", str(round(t, 3)), "-i", str(video),
        "-frames:v", "1", "-q:v", "3", str(target)
    ], check=True, timeout=120)
    if not target.is_file() or target.stat().st_size == 0:
        raise RuntimeError("frame extraction created no image")
    return _sha_file(target)


def analyze(data, *, phase="plan", manifest_dir=None, frames_dir=None, reviews=None):
    """Produce a report and suggestions; do not mutate the input or masters."""
    if phase not in ("plan", "final"):
        raise ValueError("phase must be plan or final")
    errors, pending, frames = [], [], []
    if data.get("schema") != SCHEMA:
        return {"status": "blocked", "errors": [_issue("INVALID_SCHEMA")],
                "pending": [], "frames": [], "repair_proposals": [],
                "certifies_visual_semantics": False, "v25_approved": False}

    voice = data.get("shared_voice", {})
    digest = voice.get("wav_sha256")
    duration = voice.get("duration_s")
    alignment = voice.get("timing_method")
    if not isinstance(digest, str) or not SHA.fullmatch(digest):
        errors.append(_issue("INVALID_SHARED_WAV_SHA"))
    if not _number(duration) or duration <= 0:
        errors.append(_issue("INVALID_VOICE_DURATION"))
    if alignment not in ("verified_asr", "asr_with_interpolation_reviewed", "forced_alignment_reviewed"):
        errors.append(_issue("VOICE_TIMING_UNVERIFIED", suggestion="Verify phrase timings against the actual Gacrux WAV"))
    segments = data.get("segments", [])
    variants = data.get("variants", {})
    if not isinstance(segments, list) or not segments:
        errors.append(_issue("MISSING_SPOKEN_SEGMENTS"))
        segments = []
    if not isinstance(variants, dict) or set(variants) != set(SLOTS):
        errors.append(_issue("REQUIRE_BOTH_CRITICO_VARIANTS"))
        variants = {}

    ids = set()
    last_start = -1.
    for seg in segments:
        if not isinstance(seg, dict):
            errors.append(_issue("INVALID_SEGMENT"))
            continue
        ident = seg.get("id")
        begin, end = seg.get("start_s"), seg.get("end_s")
        if not isinstance(ident, str) or not ident.strip() or ident in ids:
            errors.append(_issue("INVALID_OR_DUPLICATE_SEGMENT_ID", segment=ident))
            continue
        ids.add(ident)
        if not (isinstance(seg.get("speech"), str) and seg["speech"].strip()
                and isinstance(seg.get("subject_id"), str) and seg["subject_id"].strip()):
            errors.append(_issue("MISSING_SPEECH_OR_SUBJECT", segment=ident))
        if not (_number(begin) and _number(end) and 0 <= begin < end
                and _number(duration) and end <= duration + 0.05 and begin >= last_start):
            errors.append(_issue("INVALID_SPOKEN_TIMES", segment=ident))
        else:
            last_start = begin
        if not _box(seg.get("subject_bbox_xyxy")):
            errors.append(_issue("MISSING_SOURCE_SUBJECT_BOX", segment=ident))

    manifest_dir = Path(manifest_dir or ".").resolve()
    frames_dir = Path(frames_dir or manifest_dir / "artvision-review-frames")
    reviews = reviews or {}
    if not isinstance(reviews, dict):
        reviews = {}
        errors.append(_issue("INVALID_REVIEWS"))

    for slot in SLOTS:
        variant = variants.get(slot)
        if not isinstance(variant, dict):
            errors.append(_issue("MISSING_VARIANT", slot=slot))
            continue
        if variant.get("wav_sha256") != digest:
            errors.append(_issue("CRITICO_WAV_MISMATCH", slot=slot))
        offset = variant.get("voice_offset_s")
        length = variant.get("video_duration_s")
        if not (_number(offset) and offset >= 0 and _number(length) and length > 0
                and _number(duration) and offset + duration <= length + .2):
            errors.append(_issue("INVALID_VARIANT_VOICE_OFFSET_OR_DURATION", slot=slot))
            continue
        shots = variant.get("shots", [])
        if not isinstance(shots, list):
            errors.append(_issue("INVALID_SHOTS", slot=slot))
            continue
        shot_map = {}
        for shot in shots:
            if not isinstance(shot, dict) or not isinstance(shot.get("segment_id"), str):
                errors.append(_issue("INVALID_SHOT", slot=slot))
                continue
            if shot["segment_id"] in shot_map:
                errors.append(_issue("DUPLICATE_SHOT", slot=slot, segment=shot["segment_id"]))
            shot_map[shot["segment_id"]] = shot
        for unknown in set(shot_map) - ids:
            errors.append(_issue("SHOT_WITHOUT_SPOKEN_SEGMENT", slot=slot, segment=unknown))

        video = None
        if phase == "final":
            relative = variant.get("video_path")
            if not isinstance(relative, str) or not relative.strip():
                errors.append(_issue("MISSING_RENDERED_MP4_PATH", slot=slot))
            else:
                # Avoid escaping the working project via unchecked manifest paths.
                video = (manifest_dir / relative).resolve()
                if not video.is_relative_to(manifest_dir) or not video.is_file() or video.suffix.lower() != ".mp4":
                    errors.append(_issue("RENDERED_MP4_NOT_ACCESSIBLE", slot=slot))
                    video = None
                elif variant.get("video_sha256") != _sha_file(video):
                    errors.append(_issue("RENDERED_MP4_SHA_MISMATCH", slot=slot))
                    video = None

        for seg in segments:
            if not isinstance(seg, dict):
                continue
            ident = seg.get("id")
            shot = shot_map.get(ident)
            if not shot:
                errors.append(_issue("MISSING_SHOT_FOR_PHRASE", slot=slot, segment=ident,
                                     suggestion="Add a real painting detail matching this phrase"))
                continue
            start, end = shot.get("start_s"), shot.get("end_s")
            a, b = seg.get("start_s"), seg.get("end_s")
            if not (_number(start) and _number(end) and 0 <= start < end <= length + .05):
                errors.append(_issue("INVALID_SHOT_TIMES", slot=slot, segment=ident))
                continue
            if not (_number(a) and _number(b) and a < b):
                continue
            speech_start, speech_end = offset + a, offset + b
            overlap = max(0, min(end, speech_end) - max(start, speech_start))
            if start > speech_start + .15 or end < speech_end - .12 or overlap / (b - a) < .92:
                errors.append(_issue(
                    "PHRASE_NOT_VISIBLE_FOR_FULL_MEANING", slot=slot, segment=ident,
                    suggestion={"start_s": round(max(0, speech_start - .2), 3),
                                "end_s": round(min(length, speech_end + .2), 3),
                                "note": "Proposal only; check neighboring shots and continuous Museum camera"}))
            crop, subject = shot.get("camera_crop_xyxy"), seg.get("subject_bbox_xyxy")
            if not (_box(crop) and _box(subject)):
                errors.append(_issue("INVALID_OR_MISSING_CAMERA_CROP", slot=slot, segment=ident))
                continue
            ratio, x, y = _coverage(crop, subject)
            if ratio < .90:
                errors.append(_issue("SPOKEN_SUBJECT_CROPPED", slot=slot, segment=ident,
                                     suggestion="Reframe within the REAL painting; preserve all relevant limbs and objects"))
            if not (.22 <= x <= .78 and .22 <= y <= .78):
                errors.append(_issue("SPOKEN_SUBJECT_OFF_CENTER", slot=slot, segment=ident,
                                     suggestion="Move camera toward subject with smooth timing; no fake pixels"))
            if phase == "final" and video is not None:
                t = min(length - .1, max(.0, (max(start, speech_start) + min(end, speech_end)) / 2))
                target = frames_dir / f"{slot}__{re.sub(r'[^a-zA-Z0-9_-]', '_', ident)}.jpg"
                try:
                    fingerprint = _frame_from_video(video, t, target)
                    frames.append({"slot": slot, "segment": ident, "time_s": round(t, 3),
                                   "file": str(target), "sha256": fingerprint})
                    review = (reviews.get(slot) or {}).get(ident) or {}
                    if (review.get("frame_sha256") != fingerprint
                            or review.get("status") != "pass"
                            or not review.get("subject_matches_speech")
                            or not isinstance(review.get("reviewer"), str)
                            or not review["reviewer"].strip()):
                        pending.append(_issue("REAL_FRAME_SEMANTIC_REVIEW_REQUIRED",
                                              slot=slot, segment=ident))
                except (OSError, RuntimeError, subprocess.CalledProcessError,
                        subprocess.TimeoutExpired):
                    errors.append(_issue("REAL_FRAME_EXTRACTION_FAILED", slot=slot, segment=ident))

    status = ("blocked" if errors else
              "needs_visual_review" if phase == "final" and pending else
              "ready_for_existing_v25_review" if phase == "final" else "plan_checks_passed")
    return {"schema": "artvision-narrative-focus-report-v1",
            "status": status, "phase": phase, "errors": errors, "pending": pending,
            "frames": frames,
            "repair_proposals": [x for x in errors if x.get("suggestion") is not None],
            "certifies_visual_semantics": False,
            "v25_approved": False, "published": False,
            "note": "Technical checks and real-frame hashes do not replace human review or V25."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--phase", choices=("plan", "final"), default="plan")
    parser.add_argument("--reviews", type=Path)
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    reviews = json.loads(args.reviews.read_text(encoding="utf-8")) if args.reviews else {}
    result = analyze(data, phase=args.phase,
                     manifest_dir=args.manifest.parent,
                     frames_dir=args.out.parent / "REVIEW_FRAMES", reviews=reviews)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "errors": len(result["errors"]),
                      "pending": len(result["pending"])}, ensure_ascii=False))
    return 0 if result["status"] in ("plan_checks_passed", "ready_for_existing_v25_review") else 2


if __name__ == "__main__":
    raise SystemExit(main())
