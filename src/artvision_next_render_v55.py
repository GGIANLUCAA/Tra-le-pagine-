#!/usr/bin/env python3
"""Fail-closed ArtVision 4x1 scheduler bridge. No rendering, downloads or paid calls.

Use before invoking production_adapter_v16.py. Diagnoses eligible work only.
It never emits a job or bypasses V13 material/rights preflight.
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
    missing_standard = 0
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
            missing_standard += 1
            blocked.append({"work": group["group_id"], "variant": variant,
                            "reason": "prepared_v13_project_and_rights_review_required"})
    # A planned Museum without a compatible real renderer is not an executable
    # video job. Do not let it monopolize the only ArtVision rendering owner;
    # instead prepare a new authentic Standard subject, preserving Museum block.
    return {"status": "new_artwork_preparation_required" if not missing_standard else "missing_standard_preparation",
            "blockers": blocked,
            "new_artwork_required": missing_standard == 0,
            "next_action": "Select a new V32-reviewed artwork and prepare authentic local assets, music rights, four-variant dossier and V13 project; do not enqueue a fake render."
               if missing_standard == 0 else "Prepare the listed missing Cinema Standard with source/rights-reviewed V13 project; do not manufacture a V15 job."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = choose()
    print(json.dumps(result, ensure_ascii=False, indent=2))
