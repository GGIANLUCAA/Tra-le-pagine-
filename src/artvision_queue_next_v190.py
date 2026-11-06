#!/usr/bin/env python3
"""ArtVision deterministic next-action planner. Never renders or approves media."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SLOTS = ("critico_standard", "critico_museum", "cinema_standard", "cinema_museum")
MUSEUM = ("critico_museum", "cinema_museum")

def plan(queue, state):
    verified = state.get("verified_slots", {})
    blocked = state.get("blocked", {})
    if not isinstance(verified, dict) or not isinstance(blocked, dict):
        raise ValueError("Invalid state: verified_slots and blocked must be objects")
    actions, pending, suspended = [], [], []
    for work in queue["works"]:
        wid = work["id"]
        if wid.startswith("dali_"):
            suspended.append(wid)
            continue
        # The queue's count is a cross-check, never a substitute for verified slot IDs.
        done = set(verified.get(wid, []))
        if not done.issubset(SLOTS):
            raise ValueError("Unknown verified slot for " + wid)
        expected = work.get("slots_delivered_this_selection")
        if expected is not None and len(done) != expected:
            pending.append({"work_id": wid, "kind": "reconcile_verified_slots",
                            "expected": expected, "explicit_verified": len(done)})
            continue
        for slot in SLOTS:
            if slot in done:
                continue
            key = wid + ":" + slot
            if key in blocked:
                pending.append({"work_id": wid, "slot": slot,
                                "kind": "blocked", "reason": blocked[key]})
                continue
            if slot in MUSEUM and not work.get("museum_approved", False):
                # Do not silently discard the remaining Museum slots.
                pending.append({"work_id": wid, "slot": slot,
                                "kind": "source_gate_required"})
                continue
            actions.append({"work_id": wid, "slot": slot,
                            "kind": "render_candidate_needs_preflight"})
    return {"schema": "artvision-queue-plan-v191",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "next": actions[0] if actions else None,
            "render_candidates": actions, "pending": pending,
            "suspended": suspended,
            "new_mp4_verified_by_planner": 0,
            "note": "Planner never renders, approves, or counts new MP4."}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--queue", default="queue/artvision_owner_selected_ten_20261102.json")
    p.add_argument("--state", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    q = json.loads(Path(a.queue).read_text(encoding="utf-8"))
    s = json.loads(Path(a.state).read_text(encoding="utf-8"))
    result = plan(q, s)
    Path(a.out).write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"next": result["next"], "render_candidates": len(result["render_candidates"]),
                      "pending": len(result["pending"])}))

if __name__ == "__main__":
    main()
