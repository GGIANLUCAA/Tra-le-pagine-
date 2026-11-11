#!/usr/bin/env python3
"""Read-only owner preflight. Never renders, spends or publishes."""
import argparse
import json
import re
from pathlib import Path

QUEUE = "queue/artvision_owner_30_fast_quality_lane_20261109.json"
SOURCES = "research/artvision_owner_selected_30_future_20261109.json"
CHECKPOINT_GLOB = "artvision_owner_30_render_checkpoint_20*.json"
GATES = (
    "official_object_verified", "original_file_downloaded",
    "source_pixels_verified", "sha256_verified",
    "exact_file_license_verified", "territorial_commercial_reuse_cleared",
    "ready_for_production",
)
SHA256 = re.compile(r"[a-f0-9]{64}")


def read_json(path):
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def key(record):
    return (record["selection_order"], record["title_as_chosen"],
            record["artist_as_chosen"])


def checkpoint_record(cp):
    """Support both historical and current checkpoint schemas; fail closed."""
    work = cp.get("secondary_work") or cp.get("work")
    if not isinstance(work, dict):
        raise ValueError("Unrecognized secondary checkpoint: missing work")
    ident = (work["selection_order"], work.get("selected_title") or work["title"],
             work["artist"], work["variant"])
    run_id = (cp.get("github_workflow_run_id") or cp.get("github_run_id")
              or cp.get("run_id") or cp.get("github", {}).get("run_id"))
    if not isinstance(run_id, int) or run_id <= 0:
        raise ValueError("Checkpoint missing GitHub run ID")
    mp4_sha = ((cp.get("mp4") or {}).get("sha256")
               or (cp.get("qa") or {}).get("mp4_sha256")
               or (cp.get("qa") or {}).get("sha256_mp4")
               or (cp.get("qa") or {}).get("SHA256"))
    if mp4_sha is not None and (not isinstance(mp4_sha, str)
                                or SHA256.fullmatch(mp4_sha) is None):
        raise ValueError("Invalid checkpoint MP4 SHA256")
    # Absent SHA must never be considered a verified MP4; the run still blocks duplicates.
    status = "verified_mp4_checkpoint" if mp4_sha else "run_exists_needs_reconciliation"
    return ident, {"status": status, "github_run_id": run_id,
                   "mp4_sha256": mp4_sha}


def plan(queue, sources, checkpoints):
    priority, registry = queue["selected_works"], sources["works"]
    if len(priority) != 30 or len(registry) != 30:
        raise ValueError("Expected exactly the 30 owner-selected works")
    qm, sm = {key(w): w for w in priority}, {key(w): w for w in registry}
    if len(qm) != 30 or len(sm) != 30 or set(qm) != set(sm):
        raise ValueError("Selection mismatch or duplicate; fail closed")
    executions = {}
    for cp in checkpoints:
        ident, record = checkpoint_record(cp)
        if ident[:3] not in qm:
            raise ValueError("Checkpoint work not in selected owner shortlist")
        if ident in executions:
            raise ValueError("Two checkpoint records for same variant; reconcile first")
        executions[ident] = record

    rows = []
    ordered = sorted(qm, key=lambda k: (
        qm[k].get("provisional_production_priority", 999), k[0]))
    for ident in ordered:
        q, src = qm[ident], sm[ident]
        reasons = ["source_gate:" + gate for gate in GATES
                   if src.get(gate) is not True]
        if q.get("production_ready") is not True:
            reasons.append("queue_not_production_ready")
        if q.get("rights_and_source_gate") != "cleared":
            reasons.append("queue_rights_not_cleared")
        if q.get("render_status") != "not_started":
            reasons.append("queue_render_status_needs_review")
        # This selector preflights Cinema Standard only. Critico/Museum need
        # independent voice, camera, scale and semantic QA gates.
        existing = executions.get((*ident, "cinema_standard"))
        if existing:
            reasons.append("existing_cinema_standard_" + existing["status"])
        digest = src.get("source_sha256") or src.get("verified_source_sha256")
        if not isinstance(digest, str) or SHA256.fullmatch(digest) is None:
            reasons.append("original_image_sha256_missing")
        rows.append({"selection_order": ident[0], "title": ident[1],
                     "artist": ident[2], "eligible_preflight": not reasons,
                     "existing_cinema_standard": existing, "reasons": reasons})

    eligible = [r for r in rows if r["eligible_preflight"]]
    return {
        "schema": "artvision-owner-nonstop-preflight-v2",
        "status": ("candidate_preflight_only" if eligible
                   else "no_source_cleared_work"),
        "first_preflight_candidate": eligible[0] if eligible else None,
        "selected_count": len(rows),
        "blocked_count": len(rows) - len(eligible),
        "existing_cinema_standard_checkpoints": len(executions),
        "sha_documented_checkpoints": sum(
            item["status"] == "verified_mp4_checkpoint"
            for item in executions.values()),
        "runs_needing_checkpoint_reconciliation": sum(
            item["status"] == "run_exists_needs_reconciliation"
            for item in executions.values()),
        "checks": rows,
        "auto_render": False,
        "auto_publish": False,
        "paid_api_calls": 0,
        "note": ("Check GitHub's live job status before rendering. "
                 "A preflight candidate is not authorization or artistic approval. "
                 "Existing run IDs without MP4 SHA block duplicates but are NOT counted "
                 "as verified videos. No 4x1 production is initiated here."),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", default=QUEUE)
    parser.add_argument("--sources", default=SOURCES)
    parser.add_argument("--checkpoint", action="append")
    parser.add_argument("--checkpoint-dir", default="queue")
    parser.add_argument("--out", default="output/artvision_owner_nonstop/PREFLIGHT.json")
    args = parser.parse_args()
    if args.checkpoint is not None:
        paths = [Path(p) for p in args.checkpoint]
    else:
        paths = sorted(Path(args.checkpoint_dir).glob(CHECKPOINT_GLOB))
        if not paths:
            raise ValueError("No owner checkpoint files discovered; fail closed")
    result = plan(read_json(args.queue), read_json(args.sources),
                  [read_json(p) for p in paths])
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")
    print(result["status"], "blocked=", result["blocked_count"],
          "checkpoints=", result["existing_cinema_standard_checkpoints"],
          "need_reconciliation=", result["runs_needing_checkpoint_reconciliation"],
          "new_rendered_by_this_command=0")


if __name__ == "__main__":
    main()
