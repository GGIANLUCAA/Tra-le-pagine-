#!/usr/bin/env python3
"""V143: fail-closed handoff from free V124 film sampling to V125–V129.

A V124 research block must not be treated as a successful rank file, nor
should a missing rank cause a downstream FileNotFoundError masquerading as
source QA. No spend, publication or human approval can be granted here.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SHA = re.compile(r"[0-9a-f]{64}\Z")
INSUFFICIENT_SHOTS = {
    "V124_SHOT_ANALYSIS_UNAVAILABLE",
    "V124_NOT_ENOUGH_LONG_SOURCE_SEGMENTS",
}


def decide(adaptive, rank, scout, readiness):
    """Classify only *observed* V124 evidence, not hypothetical five shots."""
    blocked = {"ready": False, "status": "SOURCE_AUDIT_INCOMPLETE",
               "reason": "V124_EVIDENCE_MISSING_OR_INVALID"}
    if not all(isinstance(x, dict) for x in (adaptive, rank, scout, readiness)):
        return blocked
    if readiness.get("ready") is not True:
        return {**blocked, "reason": "V134_SOURCE_BYTES_NOT_VERIFIED"}
    film_sha = scout.get("original_sha256")
    if not isinstance(film_sha, str) or not SHA.fullmatch(film_sha):
        return {**blocked, "reason": "SOURCE_SHA_MISSING"}
    status = adaptive.get("status")
    if status == "V124_ADAPTIVE_SOURCE_RESEARCH_BLOCKED":
        reason = adaptive.get("reason")
        if reason in INSUFFICIENT_SHOTS:
            return {"ready": False,
                    "status": "SOURCE_REJECTED_V143_INSUFFICIENT_DETECTED_SHOTS",
                    "reason": reason}
        return {**blocked, "reason": str(reason or "V124_BLOCKED_UNKNOWN")[:240]}
    if status != "V124_SOURCE_RESEARCH_COMPLETE_NOT_APPROVED":
        return {**blocked, "reason": "V124_NOT_COMPLETED"}
    if (type(adaptive.get("sampled")) is not int
            or not 5 <= adaptive["sampled"] <= 48
            or adaptive.get("source_sha256") != film_sha
            or rank.get("adaptive_frame_source_sha256") != film_sha
            or scout.get("adaptive_research_version")
               != "V124_UNAPPROVED_LONG_SEGMENT_TARGET_SAMPLING"
            or not isinstance(rank.get("all_candidates"), list)
            or len(rank["all_candidates"]) != adaptive["sampled"]):
        return {**blocked, "reason": "V124_SHA_OR_FRAME_COUNT_INCONSISTENT"}
    return {"ready": True, "status": "V143_ADAPTIVE_REVIEW_EVIDENCE_READY",
            "reason": None}


def read_json(path):
    if not Path(path).is_file():
        return {}
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--adaptive", required=True)
    p.add_argument("--rank", required=True)
    p.add_argument("--scout", required=True)
    p.add_argument("--readiness", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    result = decide(*(read_json(x) for x in (
        args.adaptive, args.rank, args.scout, args.readiness)))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    print("V143_ADAPTIVE_HANDOFF", result["status"], result["reason"],
          "ready", result["ready"])


if __name__ == "__main__":
    main()
