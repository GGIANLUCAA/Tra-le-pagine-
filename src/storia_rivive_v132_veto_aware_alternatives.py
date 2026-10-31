#!/usr/bin/env python3
"""V132: re-evaluate genuine B/W motion candidates after SHA-bound editorial vetoes.

Research-only. A different PTS/segment is NOT proof of a different camera shot.
Never starts I2I, Vidu, paid APIs, rendering or publication.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

from src.storia_rivive_v126_balanced_motion_review import (
    _validate_and_candidates, choose_balanced_review, MIN_REGION_COVERAGE,
)

SHA = re.compile(r"[0-9a-f]{64}\Z")
FRAME = re.compile(r"frame_\d{2}\.png\Z")


def evaluate(motion, rank, scout, registry):
    # Revalidate the complete original V125 audit before filtering. Never
    # manufacture a motion PASS or rewrite source PTS, SHA or camera segments.
    film_sha, _, eligible = _validate_and_candidates(motion, rank, scout)
    if (registry.get("version") != "V131_REVIEWED_SOURCE_VETOES"
            or not isinstance(registry.get("source_vetoes"), list)):
        raise ValueError("V132_VETO_REGISTRY_INVALID")
    by_name = {row["filename"]: row for row in eligible}
    vetoed = set()
    for veto in registry["source_vetoes"]:
        if (not isinstance(veto, dict)
                or not isinstance(veto.get("film_sha256"), str)
                or not SHA.fullmatch(veto["film_sha256"])):
            raise ValueError("V132_VETO_SOURCE_SHA_INVALID")
        if veto["film_sha256"] != film_sha:
            continue
        name, stamp, reason = veto.get("frame"), veto.get("freeze_s"), veto.get("reason")
        if (not isinstance(name, str) or not FRAME.fullmatch(name)
                or name not in by_name or name in vetoed
                or type(stamp) not in (int, float) or not math.isfinite(stamp)
                or abs(stamp - by_name[name]["source_pts_time_s"]) > 0.02
                or not isinstance(reason, str) or not 8 <= len(reason) <= 220):
            raise ValueError("V132_STALE_OR_UNVERIFIED_EDITORIAL_VETO")
        vetoed.add(name)

    # A filtered *copy* is only a selection input. The original V125 evidence
    # remains intact in its report/artifact for independent inspection.
    filtered = dict(motion)
    filtered["motion_audit"] = [
        row for row in motion["motion_audit"] if row["filename"] not in vetoed
    ]
    proposed = choose_balanced_review(filtered, rank, scout)
    survivors = [row for row in eligible if row["filename"] not in vetoed]
    regions = sorted({row["timeline_region"] for row in survivors})
    enough = proposed["status"] == "V126_FIVE_DIFFERENT_MOVING_SOURCE_CANDIDATES_REVIEW_ONLY"
    status = ("SOURCE_ALTERNATIVE_FRAMES_REVIEW_REQUIRED" if enough else
              "SOURCE_REJECTED_V132_INSUFFICIENT_DIVERSITY_AFTER_VETO")
    return {
        "version": "V132_EDITORIAL_VETO_AWARE_ALTERNATIVE_RESEARCH_ONLY",
        "status": status,
        "source_film_sha256": film_sha,
        "original_verified_motion_candidates": len(eligible),
        "editorial_veto_frames": sorted(vetoed),
        "verified_motion_candidates_after_veto": len(survivors),
        "timeline_regions_after_veto": regions,
        "minimum_regions_required": MIN_REGION_COVERAGE,
        "alternative_five_frame_names": [
            row["filename"] for row in proposed["five_review_candidates"]
        ] if enough else [],
        "five_genuine_camera_shots_verified": False,
        "italian_rights_verified": False,
        "human_artistic_approved": False,
        "i2i_permitted": False,
        "vidu_permitted": False,
        "paid_api_call_permitted": False,
        "publish_permitted": False,
        "video_finished": False,
        "note": ("No usable 5-shot proposal after the reviewed exclusions."
                 if not enough else
                 "Only metadata candidates; physical film, rights and artistic QA remain mandatory."),
    }


def run(motion_path, rank_path, scout_path, veto_path, output_path):
    try:
        motion = json.loads(Path(motion_path).read_text(encoding="utf-8"))
        rank = json.loads(Path(rank_path).read_text(encoding="utf-8"))
        scout = json.loads(Path(scout_path).read_text(encoding="utf-8"))
        vetoes = json.loads(Path(veto_path).read_text(encoding="utf-8"))
        result = evaluate(motion, rank, scout, vetoes)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        result = {
            "version": "V132_EDITORIAL_VETO_AWARE_ALTERNATIVE_RESEARCH_ONLY",
            "status": "SOURCE_AUDIT_INVALID",
            "reason": str(exc)[:200],
            "alternative_five_frame_names": [],
            "italian_rights_verified": False,
            "human_artistic_approved": False,
            "i2i_permitted": False,
            "vidu_permitted": False,
            "paid_api_call_permitted": False,
            "publish_permitted": False,
            "video_finished": False,
        }
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("motion", "rank", "scout", "vetoes", "out"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    result = run(args.motion, args.rank, args.scout, args.vetoes, args.out)
    print("V132_ALTERNATIVE_SOURCE_AUDIT", result["status"],
          "motion_candidates_after_veto", result.get("verified_motion_candidates_after_veto", 0))


if __name__ == "__main__":
    main()
