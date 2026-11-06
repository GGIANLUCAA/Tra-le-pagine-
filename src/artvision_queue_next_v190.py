#!/usr/bin/env python3
"""Fail-closed ArtVision queue planner. Never renders or marks a video complete."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SLOTS = ("critico_standard", "critico_museum", "cinema_standard", "cinema_museum")

def plan(queue, state):
    works = queue.get("works", [])
    blocked = state.get("blocked", {})
    candidates = []
    for work in works:
        wid = work["id"]
        if "dali" in wid.lower() or "dalí" in work.get("artist", "").lower():
            continue  # Explicit owner suspension, not an automatic rights bypass.
        completed = set(state.get("verified_slots", {}).get(wid, []))
        # Do not infer individual completed slots from the aggregate count.
        for slot in SLOTS:
            if slot in completed:
                continue
            key = wid + ":" + slot
            if key in blocked:
                continue
            if "museum" in slot and not work.get("museum_approved", False):
                continue
            candidates.append({"work_id": wid, "slot": slot, "status": "candidate_needs_source_and_QA"})
    return {"schema": "artvision-queue-plan-v190", "generated_at": datetime.now(timezone.utc).isoformat(),
            "candidates": candidates, "next": candidates[0] if candidates else None,
            "blocked_count": len(blocked),
            "note": "No candidate is an approved render; no existing MP4 is counted."}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--queue", default="queue/artvision_owner_selected_ten_20261102.json")
    p.add_argument("--state", required=True, help="JSON with verified_slots and blocked; missing state is an error")
    p.add_argument("--out", required=True)
    args = p.parse_args()
    q = json.loads(Path(args.queue).read_text(encoding="utf-8"))
    s = json.loads(Path(args.state).read_text(encoding="utf-8"))
    result = plan(q, s)
    Path(args.out).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"next": result["next"], "candidate_count": len(result["candidates"])}))

if __name__ == "__main__":
    main()
