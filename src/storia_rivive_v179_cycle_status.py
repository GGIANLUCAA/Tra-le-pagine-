#!/usr/bin/env python3
"""V179: honest V101 cycle outcome when a source is rejected or temporarily unavailable.

No provider calls, publication, or invented review. The research workflow must
still produce CYCLE_STATUS.json if the original film has no usable frames.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

READY = "REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW"
HARD_REJECT = {
    "SOURCE_NO_VIDEO_STREAM",
    "SOURCE_MISSING_ENCODED_RASTER",
    "SOURCE_INVALID_ENCODED_RASTER",
    "MANUAL_ACQUISITION_REQUIRED_SIZE_LIMIT",
}


def build_status(order, scout, selection=None, i2i=None):
    if order.get("contract") != "LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT":
        raise ValueError("Invalid V101 work order")
    if order.get("paid_api_call_permitted") is not False or order.get("publish_permitted") is not False:
        raise ValueError("Unsafe V101 permissions")
    scout = scout if isinstance(scout, dict) else {}
    selection = selection if isinstance(selection, dict) else {}
    i2i = i2i if isinstance(i2i, dict) else {}
    source = scout.get("status", "SOURCE_SCOUT_NOT_AVAILABLE")
    preselection_rejected = (source == READY and selection.get("status") in {
        "SOURCE_TOO_FEW_DISTINCT_CANDIDATE_FRAMES",
        "SOURCE_TOO_FEW_VISUALLY_DIVERSE_CANDIDATE_FRAMES",
        "SOURCE_FRAME_SELECTION_BLOCKED",
    })
    rejected = (isinstance(source, str) and
                (source.startswith("REJECT_") or source in HARD_REJECT)) or preselection_rejected
    prepared = source == READY and i2i.get("status") == "I2I_INPUTS_PREPARED_NO_AI_GENERATION"
    selected = source == READY and selection.get("status") == "FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW"
    if preselection_rejected:
        next_step = "Source frame preselection rejected by heuristic; review five real moving shots or choose another source; no I2I or Vidu"
    elif rejected:
        next_step = "Find a higher-quality authentic source and verify Italian rights; no I2I or Vidu"
    elif source != READY:
        next_step = "Recover or retry original archival source safely; no paid API or production"
    else:
        next_step = "Visually verify five DISTINCT moving shots and Italian rights, then obtain four real I2I photos and one source-locked Vidu clip"
    return {
        "cycle_id": order["cycle_id"],
        "candidate": order["episode_id"],
        "source_scout": source,
        "frame_preselection_status": selection.get("status", "NOT_RUN"),
        "source_raster_quality_gate_v176": scout.get("source_raster_quality_gate_v176"),
        "source_frames_preselected_not_shots_verified": 5 if selected else 0,
        "source_locked_i2i_jobs_prepared_not_generated": 5 if prepared else 0,
        "five_distinct_moving_shots_verified": False,
        "italian_rights_verified": False,
        "restored_i2i_photos_approved": 0,
        "real_vidu_clips_approved": 0,
        "finished_mp4": False,
        "human_approved": False,
        "published": False,
        "charged_api_requests": 0,
        "status": "SOURCE_REJECTED" if rejected else "ASSETS_PENDING",
        "next_required": next_step,
    }


def read_optional(path):
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def main():
    parser = argparse.ArgumentParser()
    for name in ("order", "scout", "selection", "i2i", "out"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    result = build_status(read_optional(args.order), read_optional(args.scout),
                          read_optional(args.selection), read_optional(args.i2i))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("V179_CYCLE_STATUS", json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
