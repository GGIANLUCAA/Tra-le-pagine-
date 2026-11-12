#!/usr/bin/env python3
"""Fail-closed join of real GitHub read-only status with a REVIEWED queue manifest.

Preview only. No GitHub write, render, dispatch, purchase or publication code.
"""
import json
import re
from src.artvision_chain_selector_v1 import select_next
from src.artvision_chain_live_snapshot_v1 import ACTIVE_STATUSES, REPO

WORKFLOW_RE = re.compile(r"\.github/workflows/[A-Za-z0-9][A-Za-z0-9_.-]*\.ya?ml\Z")


def preview(snapshot, queue):
    base = {
        "schema": "artvision-chain-preview-v1",
        "repo": REPO,
        "dispatch_authorized": False,
        "publication_authorized": False,
        "render_started": False,
        "status": "blocked",
    }
    if not isinstance(snapshot, dict) or snapshot.get("repo") != REPO:
        return dict(base, reason="live GitHub snapshot missing or wrong repository")
    if snapshot.get("inventory_status") != "complete_read_only_non_atomic" or (
        snapshot.get("active_run_statuses_checked") != list(ACTIVE_STATUSES)
    ) or type(snapshot.get("active_heavy_render")) is not bool:
        return dict(base, reason="live GitHub inventory incomplete or unverified")
    if snapshot.get("dispatch_authorized") is not False:
        return dict(base, reason="unsafe live inventory authorization")
    if not isinstance(queue, dict) or queue.get("schema") != "artvision-chain-candidates-v1":
        return dict(base, reason="candidate manifest schema not verified")
    allowed = queue.get("reviewed_workflow_paths")
    if not isinstance(allowed, list) or not allowed or any(
        not isinstance(path, str) or not WORKFLOW_RE.fullmatch(path) for path in allowed
    ):
        return dict(base, reason="no explicit safe reviewed workflow allowlist")
    # The caller cannot override real GitHub 'busy' using a claim in the queue.
    guarded = dict(queue)
    guarded["active_heavy_render"] = snapshot["active_heavy_render"]
    chosen = select_next(guarded)
    if chosen.get("status") == "candidate":
        if chosen["workflow_path"] not in allowed:
            return dict(base, reason="candidate workflow not independently allowlisted",
                        candidate_id=chosen["id"])
        return dict(base, status="candidate_manual_review_only",
                    candidate_id=chosen["id"],
                    workflow_path=chosen["workflow_path"],
                    reason="missing atomic dispatch lock, evidence and QA checks")
    return dict(base, status="preparing",
                reason=chosen.get("reason", "candidate not ready"),
                selector=chosen)


def main():
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    try:
        snap = json.loads(args.snapshot.read_text(encoding="utf-8"))
        proposed = json.loads(args.manifest.read_text(encoding="utf-8"))
        result = preview(snap, proposed)
    except (OSError, ValueError):
        result = {"schema": "artvision-chain-preview-v1", "status": "blocked",
                  "dispatch_authorized": False, "publication_authorized": False,
                  "render_started": False,
                  "reason": "missing or invalid input"}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("ArtVision safety preview:", result["status"])


if __name__ == "__main__":
    main()
