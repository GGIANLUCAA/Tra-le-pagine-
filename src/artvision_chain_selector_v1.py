#!/usr/bin/env python3
"""ArtVision dry-run queue selector. Never dispatches or spends credits."""
import argparse
import json
from pathlib import Path

REQUIRED = ("source_verified", "rights_verified", "storyboard_ready", "qa_plan_ready")

def select_next(manifest):
    if manifest.get("active_heavy_render", True):
        return {"status": "preparing", "reason": "heavy render busy or unverified",
                "next_action": "prepare sources, rights and storyboards; retry live run check before dispatch"}
    completed = set(manifest.get("completed_ids", []))
    running = set(manifest.get("running_ids", []))
    seen = set()
    for item in manifest.get("candidates", []):
        key = item.get("id")
        if not isinstance(key, str) or not key or key in seen:
            continue
        seen.add(key)
        if key in completed or key in running:
            continue
        if item.get("status") != "ready":
            continue
        if not all(item.get(field) is True for field in REQUIRED):
            continue
        if not item.get("workflow_path", "").startswith(".github/workflows/"):
            continue
        return {"status": "candidate", "id": key, "workflow_path": item["workflow_path"],
                "note": "dry-run only; manual/authorized dispatch and independent checks required"}
    return {"status": "preparing", "reason": "no eligible render candidate",
            "next_action": "research and validate the next independent candidate"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    print(json.dumps(select_next(json.loads(args.manifest.read_text(encoding="utf-8"))), indent=2))

if __name__ == "__main__":
    main()
