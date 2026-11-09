#!/usr/bin/env python3
"""Read-only ArtVision owner 30-works preflight. Never render, spend or publish."""
import argparse
import hashlib
import json
import re
from pathlib import Path

QUEUE = "queue/artvision_owner_30_fast_quality_lane_20261109.json"
SOURCES = "research/artvision_owner_selected_30_future_20261109.json"
CHECKPOINTS = (
    "queue/artvision_owner_30_render_checkpoint_20261109_alchemist.json",
    "queue/artvision_owner_30_render_checkpoint_20261109_moreau_apparition.json",
)
GATES = (
    "official_object_verified", "original_file_downloaded",
    "source_pixels_verified", "sha256_verified",
    "exact_file_license_verified", "territorial_commercial_reuse_cleared",
    "ready_for_production",
)


def read_json(path):
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def key(record):
    return (record["selection_order"], record["title_as_chosen"], record["artist_as_chosen"])


def plan(queue, sources, checkpoints):
    priority = queue["selected_works"]
    registry = sources["works"]
    if len(priority) != 30 or len(registry) != 30:
        raise ValueError("Expected exactly the 30 owner-selected works")
    qm, sm = {key(w): w for w in priority}, {key(w): w for w in registry}
    if len(qm) != 30 or len(sm) != 30 or set(qm) != set(sm):
        raise ValueError("Selection identity mismatch or duplicate; fail closed")
    rendered = set()
    for cp in checkpoints:
        w = cp["secondary_work"]
        if not cp.get("mp4", {}).get("sha256") or not cp.get("github_workflow_run_id"):
            raise ValueError("Checkpoint lacking verified video evidence")
        sha = cp["mp4"]["sha256"]
        if re.fullmatch(r"[a-f0-9]{64}", sha) is None:
            raise ValueError("Invalid checkpoint MP4 SHA256")
        rendered.add((w["selection_order"], w["selected_title"], w["artist"], w["variant"]))
    rows = []
    ordered = sorted(qm, key=lambda k: (qm[k].get("provisional_production_priority", 999), k[0]))
    for ident in ordered:
        q, src = qm[ident], sm[ident]
        reasons = []
        for gate in GATES:
            if src.get(gate) is not True:
                reasons.append("source_gate:" + gate)
        if q.get("production_ready") is not True:
            reasons.append("queue_not_production_ready")
        if q.get("rights_and_source_gate") != "cleared":
            reasons.append("queue_rights_not_cleared")
        if q.get("render_status") != "not_started":
            reasons.append("queue_render_status_needs_review")
        for slot in ("cinema_standard",):
            if (*ident, slot) in rendered:
                reasons.append("existing_verified_mp4_" + slot)
        hash_value = src.get("source_sha256") or src.get("verified_source_sha256")
        if not isinstance(hash_value, str) or re.fullmatch(r"[a-f0-9]{64}", hash_value) is None:
            reasons.append("original_image_sha256_missing")
        if ident[1] == "The Temptation of St. Anthony" and "Dalí" in ident[2]:
            reasons.append("owner_excluded_dali")
        rows.append({"selection_order": ident[0], "title": ident[1],
                     "artist": ident[2], "eligible_preflight": not reasons,
                     "reasons": reasons})
    eligible = [r for r in rows if r["eligible_preflight"]]
    return {
        "schema": "artvision-owner-nonstop-preflight-v1",
        "status": "candidate_preflight_only" if eligible else "no_source_cleared_work",
        "first_preflight_candidate": eligible[0] if eligible else None,
        "selected_count": len(rows),
        "blocked_count": len(rows) - len(eligible),
        "checks": rows,
        "auto_render": False,
        "auto_publish": False,
        "paid_api_calls": 0,
        "note": "A positive result is NOT render authorization: require a versioned per-work 4x1 recipe, reviewed rights, actual renderer and owner single-heavy-render lock. This preflight never starts a job.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", default=QUEUE)
    parser.add_argument("--sources", default=SOURCES)
    parser.add_argument("--checkpoint", action="append")
    parser.add_argument("--out", default="output/artvision_owner_nonstop/PREFLIGHT.json")
    args = parser.parse_args()
    paths = args.checkpoint if args.checkpoint is not None else CHECKPOINTS
    result = plan(read_json(args.queue), read_json(args.sources),
                  [read_json(p) for p in paths])
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(result["status"], "blocked=", result["blocked_count"],
          "ready_preflight=", 30 - result["blocked_count"], "rendered=0")


if __name__ == "__main__":
    main()
