#!/usr/bin/env python3
"""V136/V137: classify genuine film scouting evidence, never workflow-green as video-ready.

V137 fixes a fail-open path: five dummy candidates plus arbitrary non-BLOCKED
status strings previously yielded SOURCE_RESEARCH_REVIEW_REQUIRED. This module
never grants I2I/Vidu spend, Italian-rights clearance, or artistic approval.
"""
from __future__ import annotations

import re

SHA = re.compile(r"[0-9a-f]{64}\Z")
FRAME = re.compile(r"frame_\d{2}\.png\Z")

PASS_STATUSES = {
    "motion": "V125_FIVE_MOVING_PHOTO_REGIONS_REVIEW_REQUIRED",
    "balanced": "V126_FIVE_DIFFERENT_MOVING_SOURCE_CANDIDATES_REVIEW_ONLY",
    "visual": "V128_FIVE_BALANCED_FRAMES_VISUAL_REVIEW_REQUIRED",
    "strips": "V129_FIVE_SOURCE_LOCKED_MOTION_STRIPS_REVIEW_ONLY",
}
PASS_VERSIONS = {
    "motion": "V125_REAL_BW_DECODED_SPATIAL_MOTION_UNAPPROVED",
    "balanced": "V126_FIVE_DIVERSE_MOVING_SHOTS_NOT_APPROVED",
    "visual": "V128_BALANCED_REAL_ORIGINAL_FRAME_REVIEW_ONLY",
    "strips": "V129_REAL_PREFREEZE_MOTION_STRIPS_UNAPPROVED",
}


def source_state(readiness, motion, balanced, visual, strips):
    """Return review-only state only for a coherent, source-locked five-shot audit.

    This is a summary of independently executed V125–V129 guards, NOT a
    replacement for their byte-level validation or human shot/rights review.
    """
    reports = (readiness, motion, balanced, visual, strips)
    if any(not isinstance(x, dict) for x in reports):
        return "SOURCE_AUDIT_INCOMPLETE"
    if readiness.get("ready") is not True:
        return "SOURCE_REJECTED_OR_UNVERIFIED"

    moving = motion.get("source_motion_candidates_pass")
    candidates = balanced.get("five_review_candidates")
    if type(moving) is not int or moving < 0 or not isinstance(candidates, list):
        return "SOURCE_AUDIT_INCOMPLETE"
    if (moving < 5 or len(candidates) < 5
            or motion.get("status") == "V125_MOTION_SOURCE_SELECTION_BLOCKED"
            or balanced.get("status") == "V126_INSUFFICIENT_MOTION_SCENE_VARIETY"):
        return "SOURCE_REJECTED_V136_INSUFFICIENT_MOTION_VARIETY"

    for name, report in (("motion", motion), ("balanced", balanced),
                         ("visual", visual), ("strips", strips)):
        if (report.get("status") != PASS_STATUSES[name]
                or report.get("version") != PASS_VERSIONS[name]):
            return "SOURCE_AUDIT_INCOMPLETE"
    if len(candidates) != 5:
        return "SOURCE_AUDIT_INCOMPLETE"

    film_sha = motion.get("source_video_sha256")
    if (not isinstance(film_sha, str) or not SHA.fullmatch(film_sha)
            or balanced.get("source_film_sha256") != film_sha
            or visual.get("source_film_sha256") != film_sha
            or strips.get("original_film_sha256") != film_sha):
        return "SOURCE_AUDIT_INCOMPLETE"

    # The same five actual source frames must appear in all three downstream
    # reports. A five-item list of placeholders is not a completed audit.
    expected = {}
    for row in candidates:
        if not isinstance(row, dict):
            return "SOURCE_AUDIT_INCOMPLETE"
        filename, digest = row.get("filename"), row.get("source_frame_sha256")
        if (not isinstance(filename, str) or not FRAME.fullmatch(filename)
                or filename in expected or not isinstance(digest, str)
                or not SHA.fullmatch(digest)
                or row.get("source_film_sha256") != film_sha):
            return "SOURCE_AUDIT_INCOMPLETE"
        expected[filename] = digest

    visual_rows = visual.get("five_review_frames")
    strip_rows = strips.get("five_prefreeze_proxy_strips")
    if (not isinstance(visual_rows, list) or len(visual_rows) != 5
            or not isinstance(strip_rows, list) or len(strip_rows) != 5):
        return "SOURCE_AUDIT_INCOMPLETE"
    visual_seen, strip_seen = set(), set()
    for row in visual_rows:
        if (not isinstance(row, dict) or row.get("filename") not in expected
                or row["filename"] in visual_seen
                or row.get("frame_sha256") != expected[row["filename"]]
                or row.get("source_film_sha256") != film_sha):
            return "SOURCE_AUDIT_INCOMPLETE"
        visual_seen.add(row["filename"])
    for row in strip_rows:
        if (not isinstance(row, dict) or row.get("source_frame") not in expected
                or row["source_frame"] in strip_seen):
            return "SOURCE_AUDIT_INCOMPLETE"
        strip_seen.add(row["source_frame"])
    if visual_seen != set(expected) or strip_seen != set(expected):
        return "SOURCE_AUDIT_INCOMPLETE"
    return "SOURCE_RESEARCH_REVIEW_REQUIRED"
