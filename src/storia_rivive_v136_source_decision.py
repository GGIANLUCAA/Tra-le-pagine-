#!/usr/bin/env python3
"""V136: classify genuine film scouting evidence, never workflow-green as video-ready.

Only a *verified* source with five motion-capable and balanced candidate windows
can enter artistic/source-rights review. No path grants paid API or publication.
"""


def source_state(readiness, motion, balanced, visual, strips):
    if readiness.get("ready") is not True:
        return "SOURCE_REJECTED_OR_UNVERIFIED"
    motion_status = motion.get("status")
    balanced_status = balanced.get("status")
    if not motion_status or not balanced_status:
        return "SOURCE_AUDIT_INCOMPLETE"
    moving = motion.get("source_motion_candidates_pass")
    candidates = balanced.get("five_review_candidates")
    if (type(moving) is not int or moving < 0 or not isinstance(candidates, list)):
        return "SOURCE_AUDIT_INCOMPLETE"
    if moving < 5 or len(candidates) < 5 or "BLOCKED" in motion_status or (
            "INSUFFICIENT" in balanced_status or "BLOCKED" in balanced_status):
        return "SOURCE_REJECTED_V136_INSUFFICIENT_MOTION_VARIETY"
    if (not visual.get("status") or not strips.get("status")
            or "BLOCKED" in visual["status"] or "BLOCKED" in strips["status"]):
        return "SOURCE_AUDIT_INCOMPLETE"
    return "SOURCE_RESEARCH_REVIEW_REQUIRED"
