#!/usr/bin/env python3
"""V131: fail-closed editorial hold on SHA-bound source audit results.

A veto, never an approval engine: no I2I, Vidu or publication permission.
"""
from __future__ import annotations
import argparse
import json
import math
import re
from fractions import Fraction
from pathlib import Path

SHA = re.compile(r"[0-9a-f]{64}\Z")
FRAME = re.compile(r"frame_\d{2}\.png\Z")

def finite_source_seconds(value):
    """Reject NaN/Infinity and unbounded integers without float overflow."""
    return (type(value) in (int, float) and 0 <= value <= 1_000_000_000
            and math.isfinite(value))

def valid_prefreeze_pts(strip, stamp):
    """Match V129's exact native freeze PTS to V128's audited frame time."""
    start, freeze, clock = (strip.get("pre_freeze_start_pts"),
                            strip.get("freeze_pts"), strip.get("source_time_base"))
    if (type(start) is not int or type(freeze) is not int
            or start < 0 or freeze <= start or not isinstance(clock, str)):
        return False
    try:
        period = Fraction(clock)
        duration = (freeze - start) * period
        return (period > 0 and 0 < duration <= Fraction(5, 2)
                and abs(float(freeze * period) - stamp) <= 0.0001)
    except (ValueError, ZeroDivisionError, OverflowError):
        return False

def evaluate(visual, motion, registry):
    film = visual.get("source_film_sha256")
    if not isinstance(film, str) or not SHA.fullmatch(film):
        raise ValueError("V131_SOURCE_SHA_INVALID")
    if (visual.get("version") != "V128_BALANCED_REAL_ORIGINAL_FRAME_REVIEW_ONLY"
            or visual.get("status") != "V128_FIVE_BALANCED_FRAMES_VISUAL_REVIEW_REQUIRED"
            or visual.get("original_pts_sha_motion_evidence_crosschecked") is not True
            or visual.get("genuine_camera_shots_verified") is not False
            or visual.get("italian_rights_verified") is not False
            or visual.get("human_artistic_approved") is not False
            or visual.get("video_finished") is not False):
        raise ValueError("V131_V128_NOT_SOURCE_LOCKED_OR_NOT_REVIEW_ONLY")
    if (motion.get("version") != "V129_REAL_PREFREEZE_MOTION_STRIPS_UNAPPROVED"
            or motion.get("status") != "V129_FIVE_SOURCE_LOCKED_MOTION_STRIPS_REVIEW_ONLY"
            or motion.get("original_film_sha256") != film
            or motion.get("proxy_sampling_is_not_exact_freeze_pts") is not True
            or motion.get("five_genuine_camera_shots_verified") is not False
            or motion.get("italian_rights_verified") is not False
            or motion.get("human_artistic_approved") is not False
            or motion.get("video_finished") is not False):
        raise ValueError("V131_V129_FILM_OR_REVIEW_STATUS_INVALID")
    frames, strips = visual.get("five_review_frames"), motion.get("five_prefreeze_proxy_strips")
    if not isinstance(frames, list) or len(frames) != 5 or not isinstance(strips, list) or len(strips) != 5:
        raise ValueError("V131_FIVE_SOURCE_WINDOWS_REQUIRED")
    indexed = {}
    for frame, strip in zip(frames, strips):
        if not isinstance(frame, dict) or not isinstance(strip, dict):
            raise ValueError("V131_FRAME_STRIP_INVALID")
        name, stamp, digest = frame.get("filename"), frame.get("source_pts_time_s"), frame.get("frame_sha256")
        if (not isinstance(name, str) or not FRAME.fullmatch(name) or name in indexed
                or not isinstance(digest, str) or not SHA.fullmatch(digest)
                or frame.get("source_film_sha256") != film
                or not finite_source_seconds(stamp)
                or strip.get("source_frame") != name
                or strip.get("freeze_source_pts_time_s") != stamp
                or not isinstance(strip.get("proxy_rgb_sha256"), str)
                or not SHA.fullmatch(strip["proxy_rgb_sha256"])
                or type(strip.get("proxy_decoded_frame_count")) is not int
                or not 3 <= strip["proxy_decoded_frame_count"] <= 10
                or not valid_prefreeze_pts(strip, stamp)):
            raise ValueError("V131_FRAME_STRIP_SHA_PTS_MISMATCH")
        indexed[name] = {"freeze_s": stamp, "frame_sha256": digest}
    if (registry.get("version") != "V131_REVIEWED_SOURCE_VETOES"
            or not isinstance(registry.get("source_vetoes"), list)):
        raise ValueError("V131_VETO_REGISTRY_INVALID")
    holds, seen = [], set()
    for veto in registry["source_vetoes"]:
        if not isinstance(veto, dict) or not isinstance(veto.get("film_sha256"), str) or not SHA.fullmatch(veto["film_sha256"]):
            raise ValueError("V131_VETO_FILM_SHA_INVALID")
        if veto["film_sha256"] != film:
            continue
        name, reason = veto.get("frame"), veto.get("reason")
        if (name not in indexed or name in seen or not finite_source_seconds(veto.get("freeze_s"))
                or abs(indexed[name]["freeze_s"] - veto["freeze_s"]) > .02
                or not isinstance(reason, str) or not 8 <= len(reason) <= 220):
            raise ValueError("V131_STALE_OR_MALFORMED_VETO_REQUIRES_REVIEW")
        seen.add(name)
        holds.append({"frame": name, "freeze_s": indexed[name]["freeze_s"],
                      "source_frame_sha256": indexed[name]["frame_sha256"], "reason": reason})
    return {
        "version": "V131_SOURCE_EDITORIAL_HOLD_NO_AUTOMATIC_APPROVAL",
        "status": "SOURCE_ARTISTIC_REVIEW_HOLD" if holds else "SOURCE_ARTISTIC_REVIEW_REQUIRED",
        "source_film_sha256": film, "source_review_vetoes": holds,
        "five_original_windows_crosschecked": True,
        "exact_native_freeze_pts_crosschecked": True,
        "prefreeze_proxy_frame_counts_crosschecked": True,
        "italian_rights_verified": False, "five_genuine_camera_shots_approved": False,
        "human_artistic_approved": False, "i2i_permitted": False,
        "vidu_permitted": False, "paid_api_call_permitted": False,
        "publish_permitted": False, "video_finished": False,
        "note": "A diagnostic veto is not human approval. New selections require full visual and rights review."
    }

def run(visual_path, motion_path, veto_path, output_path):
    output = Path(output_path)
    try:
        visual = json.loads(Path(visual_path).read_text(encoding="utf-8"))
        motion = json.loads(Path(motion_path).read_text(encoding="utf-8"))
        registry = json.loads(Path(veto_path).read_text(encoding="utf-8"))
        result = evaluate(visual, motion, registry)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        result = {"version": "V131_SOURCE_EDITORIAL_HOLD_NO_AUTOMATIC_APPROVAL",
                  "status": "SOURCE_AUDIT_INVALID", "reason": str(exc)[:200],
                  "italian_rights_verified": False, "human_artistic_approved": False,
                  "i2i_permitted": False, "vidu_permitted": False,
                  "paid_api_call_permitted": False, "publish_permitted": False,
                  "video_finished": False}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("visual", "motion", "vetoes", "out"):
        p.add_argument("--" + name, required=True)
    args = p.parse_args()
    result = run(args.visual, args.motion, args.vetoes, args.out)
    print("V131_SOURCE_EDITORIAL_GATE", result["status"])

if __name__ == "__main__":
    main()
