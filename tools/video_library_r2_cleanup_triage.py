#!/usr/bin/env python3
"""Read-only R2 cleanup triage. No API calls and no deletion action."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

DEFAULT = Path(__file__).resolve().parents[1] / "reports/video_library_r2_storage_audit_20261116.json"


def triage(audit: dict) -> dict:
    assert audit["schema"] == "vls-r2-storage-review-v1"
    assert audit["complete"] is True and audit["pages"] > 0
    assert audit["totals"]["deleted_bytes"] == 0
    assert audit["mp4"]["count"] >= 1
    assert sum(x[1] for x in audit["numbered_variant_rows"]) == audit["totals"]["numbered_bytes"]
    groups = []
    for group in audit["same_etag_size_groups"]:
        keys = group["keys"]
        assert len(keys) > 1 and len(set(keys)) == len(keys)
        candidate = {
            "keys": keys,
            "possible_bytes": group["wasted_candidate_bytes"],
            "fingerprint": group["etag"],
            "ready_keys": group.get("ready", []),
            "action": "DO_NOT_DELETE",
            "reason": "ETag does not replace full source SHA256, reference audit or rollback",
        }
        verified = audit.get("confirmed_sha_duplicate") or {}
        if set(keys) == set(verified.get("keys", [])):
            candidate["sha256"] = verified["sha256"]
            candidate["reason"] = (
                "Same bytes verified; still requires external link compatibility "
                "and independently verified keeper before any deletion"
            )
        if candidate["ready_keys"]:
            candidate["reason"] += "; preserve curated ready key(s)"
        groups.append(candidate)
    return {
        "schema": "vls-safe-r2-cleanup-triage-v1",
        "recorded_objects": audit["objects"]["count"],
        "recorded_bytes": audit["objects"]["bytes"],
        "numbered_variants_not_duplicates": len(audit["numbered_variant_rows"]),
        "fingerprint_groups": groups,
        "possible_fingerprint_bytes": sum(g["possible_bytes"] for g in groups),
        "eligible_to_delete_now": [],
        "actually_deleted_bytes": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, default=DEFAULT)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = triage(json.loads(args.audit.read_text(encoding="utf-8")))
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
