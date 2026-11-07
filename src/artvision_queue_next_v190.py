#!/usr/bin/env python3
"""ArtVision deterministic next-action planner. Never renders or approves media."""
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SLOTS = ("critico_standard", "critico_museum", "cinema_standard", "cinema_museum")
MUSEUM = ("critico_museum", "cinema_museum")

def plan(queue, state, trial_sources=None):
    verified = state.get("verified_slots", {})
    blocked = state.get("blocked", {})
    if not isinstance(verified, dict) or not isinstance(blocked, dict):
        raise ValueError("Invalid state: verified_slots and blocked must be objects")
    trial_sources = trial_sources or {}
    if not isinstance(trial_sources, dict):
        raise ValueError('Invalid trial source manifest')
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
                # Owner-approved neutral scenography may be trial-rendered, never
                # treated as artistically approved or as a verified delivery.
                # A source manifest can persist the earlier licensed photo readback.
                # It is never artwork/room approval and never a command to render.
                state_evidence = state.get("museum_trial_evidence") or {}
                if not isinstance(state_evidence, dict):
                    raise ValueError("Invalid museum_trial_evidence state")
                evidence = state_evidence.get(wid) or trial_sources.get(wid, {})
                required = ("source_url", "source_sha256", "source_license",
                            "painting_dimensions_verified", "scene_kind",
                            "rights_reviewed", "asset_readback_verified")
                valid = (isinstance(evidence, dict)
                         and all(evidence.get(k) for k in required)
                         and evidence.get("scene_kind") in
                         ("authentic_documented", "neutral_scenography")
                         and isinstance(evidence.get("source_url"), str)
                         and evidence["source_url"].startswith("https://")
                         and isinstance(evidence.get("source_sha256"), str)
                         and re.fullmatch(r"[a-f0-9]{64}", evidence["source_sha256"]) is not None
                         and evidence.get("trial_render_only", True) is True
                         and evidence.get("gold", False) is False
                         and evidence.get("publication_authorized", False) is False
                         and (evidence.get("scene_kind") != "neutral_scenography"
                              or bool(evidence.get("scenography_disclosure"))))
                if not valid:
                    pending.append({"work_id": wid, "slot": slot,
                                    "kind": "source_gate_required",
                                    "reason": "Missing licensed source/readback, valid SHA, metric dimensions or scenographic disclosure"})
                    continue
                actions.append({"work_id": wid, "slot": slot,
                                "kind": "museum_trial_render_candidate_needs_preflight",
                                "artistic_review": "PENDING",
                                "gold": False, "publication_authorized": False,
                                "scene_kind": evidence["scene_kind"],
                                "source_manifest_is_not_render_approval": True})
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
    p.add_argument("--trial-sources", default="config/artvision_museum_trial_sources_v208.json")
    p.add_argument("--out", required=True)
    a = p.parse_args()
    q = json.loads(Path(a.queue).read_text(encoding="utf-8"))
    s = json.loads(Path(a.state).read_text(encoding="utf-8"))
    manifest_path = Path(a.trial_sources)
    trial_sources = {}
    if manifest_path.is_file():
        doc = json.loads(manifest_path.read_text(encoding="utf-8"))
        if doc.get("schema") != "artvision-museum-trial-source-v208":
            raise ValueError("Unknown trial source manifest schema")
        trial_sources = doc.get("museum_trial_evidence", {})
    result = plan(q, s, trial_sources)
    Path(a.out).write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"next": result["next"], "render_candidates": len(result["render_candidates"]),
                      "pending": len(result["pending"])}))

if __name__ == "__main__":
    main()
