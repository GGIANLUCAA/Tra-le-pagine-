#!/usr/bin/env python3
"""Fail-closed, offline preflight for V185/V186 Commons candidate metadata.

Metadata alone NEVER proves that a photo shows the exact painting, its frame
or the real museum room. This gate cannot approve a Museum render.
"""
import argparse
import json
from pathlib import Path

WORKS = ("rebel_angels", "garden_of_death", "triumph_of_death",
         "magic_circle", "ghost_of_a_flea")
PERMISSIVE_LICENSES = ("CC0", "Public domain", "CC BY 3.0", "CC BY 4.0",
                       "CC BY-SA 3.0", "CC BY-SA 4.0")

def evaluate(data):
    report = {"status": "SOURCE_DISCOVERY_ONLY_NO_RENDER_AUTHORIZATION",
              "works": {}, "errors": data.get("errors", [])}
    for work in WORKS:
        candidates = []
        for item in data.get("works", {}).get(work, []):
            license_name = item.get("license_label_unverified") or ""
            width, height = item.get("width") or 0, item.get("height") or 0
            reasons = []
            if not item.get("commons_page") or not item.get("original_url"):
                reasons.append("missing_original_or_source_page")
            if not item.get("sha1_commons"):
                reasons.append("missing_original_hash")
            if min(width, height) < 1200:
                reasons.append("insufficient_source_resolution")
            if license_name not in PERMISSIVE_LICENSES:
                reasons.append("license_not_precleared_for_commercial_review")
            # Never infer photo subject or authentic frame from file title.
            reasons.extend(("exact_work_and_frame_not_visually_verified",
                            "actual_room_and_scale_not_visually_verified",
                            "rights_and_attribution_not_independently_verified",
                            "original_bytes_sha256_not_verified"))
            candidates.append({"source_page": item.get("commons_page"),
                               "original_url": item.get("original_url"),
                               "commons_sha1": item.get("sha1_commons"),
                               "license_claim": license_name,
                               "dimensions": [width, height],
                               "metadata_preflight": "NEEDS_REVIEW",
                               "render_allowed": False,
                               "reasons": reasons})
        report["works"][work] = {"candidate_count": len(candidates),
                                  "museum_render_allowed": False,
                                  "candidates": candidates}
    return report

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    result = evaluate(json.loads(Path(args.input).read_text(encoding="utf-8")))
    Path(args.out).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Museum source gate: review required; no automatic approval")
    for name, work in result["works"].items():
        print(name, work["candidate_count"], "candidates")

if __name__ == "__main__":
    main()
