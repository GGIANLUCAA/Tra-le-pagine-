#!/usr/bin/env python3
"""ArtVision dry-run queue selector. Never dispatches or spends credits."""
import argparse
import json
import re
from pathlib import Path

REQUIRED = ("source_verified", "rights_verified", "storyboard_ready", "qa_plan_ready")
WORKFLOW_RE = re.compile(r"\.github/workflows/[A-Za-z0-9][A-Za-z0-9_.-]*\.ya?ml\Z")


def _id_set(value):
    """Require a complete and unambiguous snapshot before choosing a render."""
    if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value):
        return None
    return set(value)


def select_next(manifest):
    if not isinstance(manifest, dict) or not isinstance(manifest.get("candidates", []), list):
        return {"status": "preparing", "reason": "invalid queue snapshot",
                "next_action": "repair manifest and recheck live state; no dispatch"}
    completed = _id_set(manifest.get("completed_ids", []))
    running = _id_set(manifest.get("running_ids", []))
    quarantined = _id_set(manifest.get("quarantined_ids", []))
    if completed is None or running is None or quarantined is None:
        return {"status": "preparing", "reason": "invalid deduplication snapshot",
                "next_action": "repair manifest and recheck live state; no dispatch"}

    # Missing, unknown or unverified live state may never be interpreted as idle.
    busy = manifest.get("active_heavy_render") is not False
    seen = set()
    preparation = None
    for item in manifest.get("candidates", []):
        if not isinstance(item, dict):
            continue
        key = item.get("id")
        if not isinstance(key, str) or not key.strip() or key in seen:
            continue
        seen.add(key)
        if key in completed or key in running or key in quarantined:
            continue
        # Do not waste the entire cycle retrying the same blocked artwork.
        # Its recovery is handled separately, after a verified change of evidence.
        if item.get("status") in ("blocked", "quarantined"):
            continue
        if preparation is None and item.get("status") in ("ready", "preparing"):
            missing = [field for field in REQUIRED if item.get(field) is not True]
            if missing:
                preparation = {"status": "preparing", "id": key,
                               "missing_gates": missing,
                               "next_action": "verify source, rights, storyboard and QA evidence"}
        if busy or item.get("status") != "ready":
            continue
        if not all(item.get(field) is True for field in REQUIRED):
            continue
        workflow = item.get("workflow_path")
        if not isinstance(workflow, str) or WORKFLOW_RE.fullmatch(workflow) is None:
            continue
        return {"status": "candidate", "id": key, "workflow_path": workflow,
                "note": "dry-run only; manual/authorized dispatch and independent checks required"}
    if preparation is not None:
        return preparation
    return {"status": "preparing", "reason": "heavy render busy or unverified" if busy else "no eligible render candidate",
            "next_action": "research and validate the next independent candidate"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    print(json.dumps(select_next(json.loads(args.manifest.read_text(encoding="utf-8"))), indent=2))


if __name__ == "__main__":
    main()
