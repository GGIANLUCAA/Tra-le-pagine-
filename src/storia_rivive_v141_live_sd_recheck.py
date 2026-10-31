#!/usr/bin/env python3
"""V141: free live recheck of V140 Commons SD snapshots; never unlock production.

A Commons file may be replaced at the SAME page URL. The V140 snapshot is
research evidence, not a permanent verdict about future uploaded originals.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

from storia_rivive_scout_v101 import metadata


def recheck_low_raster_snapshots(registry, lookup=metadata):
    """Return research-only evidence. Network failures never approve a source."""
    if not isinstance(registry, dict) or registry.get("version") != "V140_COMMONS_ORIGINAL_RASTER_RESEARCH_SKIPS":
        raise ValueError("V141_INVALID_REGISTRY")
    rows = registry.get("excluded")
    if not isinstance(rows, list) or not rows:
        raise ValueError("V141_EMPTY_REGISTRY")
    seen = set()
    checked = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("V141_INVALID_ROW")
        ident, page, raster = row.get("candidate_id"), row.get("source_page"), row.get("commons_original_raster_px")
        if (not isinstance(ident, str) or not ident or ident in seen
                or not isinstance(page, str) or not page.startswith("https://commons.wikimedia.org/wiki/File:")
                or not isinstance(raster, list) or len(raster) != 2
                or any(type(n) is not int or n <= 0 for n in raster)):
            raise ValueError("V141_INVALID_SNAPSHOT")
        baseline = row.get("commons_original_sha1")
        if baseline is not None and (not isinstance(baseline, str)
                or re.fullmatch(r"[0-9a-f]{40}", baseline) is None):
            raise ValueError("V145_INVALID_ORIGINAL_SHA1_BASELINE")
        seen.add(ident)
        live_sha1 = None
        content_identity = "BASELINE_NOT_RECORDED" if baseline is None else "LIVE_FINGERPRINT_UNAVAILABLE"
        try:
            live = lookup(page)
            width, height = live.get("original_width_px"), live.get("original_height_px")
            fingerprint = live.get("original_sha1")
            if isinstance(fingerprint, str) and re.fullmatch(r"[0-9a-f]{40}", fingerprint):
                live_sha1 = fingerprint
            if baseline is not None and live_sha1 is not None:
                content_identity = "MATCH" if baseline == live_sha1 else "CHANGED"
            if type(width) is not int or type(height) is not int or width <= 0 or height <= 0:
                state = "LIVE_RASTER_METADATA_UNAVAILABLE"
                measured = None
            else:
                measured = [width, height]
                if measured != raster:
                    state = "RASTER_CHANGED_REQUIRES_NEW_SOURCE_REVIEW"
                elif content_identity == "CHANGED":
                    state = "ORIGINAL_CONTENT_CHANGED_REQUIRES_NEW_SOURCE_REVIEW"
                elif baseline is not None and content_identity != "MATCH":
                    state = "LIVE_FINGERPRINT_UNAVAILABLE"
                else:
                    state = "SNAPSHOT_UNCHANGED"
        except Exception:
            # No API exception details or provider URLs in public logs.
            state, measured = "RECHECK_PENDING_NETWORK_ERROR", None
        checked.append({"candidate_id": ident, "snapshot_raster_px": raster,
                        "live_raster_px": measured,
                        "snapshot_original_sha1": baseline,
                        "live_original_sha1": live_sha1,
                        "original_content_identity": content_identity,
                        "status": state})
    statuses = {r["status"] for r in checked}
    if statuses & {"RASTER_CHANGED_REQUIRES_NEW_SOURCE_REVIEW",
                   "ORIGINAL_CONTENT_CHANGED_REQUIRES_NEW_SOURCE_REVIEW"}:
        overall = "SOURCE_SNAPSHOT_REVIEW_REQUIRED"
    elif statuses != {"SNAPSHOT_UNCHANGED"}:
        overall = "SOURCE_SNAPSHOT_CHECK_UNAVAILABLE"
    else:
        overall = "ALL_LOW_RASTER_SNAPSHOTS_CURRENT"
    return {"contract": "V141_COMMONS_SD_LIVE_RECHECK_RESEARCH_ONLY",
            "status": overall, "checked_count": len(checked), "sources": checked,
            "v145_content_fingerprint_inventory": True,
            "same_raster_original_bytes_verified": all(
                r["original_content_identity"] == "MATCH" and r["status"] == "SNAPSHOT_UNCHANGED" for r in checked),
            "source_acquisition_permitted": False, "i2i_permitted": False,
            "vidu_post_permitted": False, "publication_permitted": False,
            "note": "V145: Commons original SHA1 is public research evidence only. Without a stored baseline, same-raster replacement remains UNVERIFIED; no rights, quality or production clearance."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default="config/storia_rivive_v140_low_raster_sources.json")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    report = recheck_low_raster_snapshots(json.loads(Path(args.registry).read_text(encoding="utf-8")))
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("V141_RECHECK", report["status"], "sources", report["checked_count"], "paid_calls", 0)


if __name__ == "__main__":
    main()
