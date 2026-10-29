#!/usr/bin/env python3
"""Fail-closed ArtVision 4x1 scheduler bridge. No rendering, downloads or paid calls.

Use before invoking production_adapter_v16.py. Emits a job ONLY when a
prepared V13 project and its local inputs are present and preflight passes.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "queue/artvision_four_variants_s01_20261028.json"
PRODUCTION = ROOT / "queue/production_v15.json"
VARIANTS = ("cinema_standard", "cinema_museum", "critico_standard", "critico_museum")


def choose(root=ROOT):
    queue = json.loads((root / "queue/artvision_four_variants_s01_20261028.json").read_text())
    production = json.loads((root / "queue/production_v15.json").read_text())
    if production.get("items"):
        return {"status": "existing_jobs_take_priority", "count": len(production["items"])}
    blocked = []
    for group in queue["groups"]:
        for variant in VARIANTS:
            state = group["variants"][variant]["status"]
            if state in ("rendered_needs_review", "approved_for_final_delivery"):
                continue
            if variant.startswith("critico"):
                blocked.append({"work": group["group_id"], "variant": variant,
                                "reason": "verified_gacrux_cache_required"})
                continue
            if variant == "cinema_museum":
                blocked.append({"work": group["group_id"], "variant": variant,
                                "reason": "no_verified_generic_museum_renderer"})
                continue
            blocked.append({"work": group["group_id"], "variant": variant,
                            "reason": "prepared_v13_project_and_rights_review_required"})
    return {"status": "new_artwork_preparation_required" if not blocked else "blocked",
            "blockers": blocked,
            "next_action": "Select a new V32-reviewed artwork and prepare authentic local assets, music rights, four-variant dossier and V13 project; do not enqueue a fake render."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = choose()
    print(json.dumps(result, ensure_ascii=False, indent=2))
