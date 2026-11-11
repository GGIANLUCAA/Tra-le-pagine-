#!/usr/bin/env python3
"""V121: verify real V120 room photographs and preliminary review, not video quality.

Read-only: no APIs, edits, rendering, credits or publication. A passing result
certifies file provenance for research only, NEVER a museum preset or MP4.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

SCHEMA = "artvision-v121-photo-source-visual-audit"
CANDIDATE_STATUS = {
    "reference_only", "priority_for_3d_reconstruction_study",
    "reject_for_painting_wall",
}


def audit(archive: Path, review: dict) -> list[str]:
    errors: list[str] = []
    if review.get("schema") != SCHEMA:
        errors.append("review_schema_invalid")
    entries = review.get("entries")
    if not isinstance(entries, list) or len(entries) != 5:
        return errors + ["exactly_five_review_entries_required"]
    ids = [x.get("id") for x in entries if isinstance(x, dict)]
    if len(ids) != 5 or len(set(ids)) != 5 or set(ids) != {
        "GAL01", "GAL02", "GAL03", "GAL04", "GAL05"
    }:
        errors.append("photo_review_ids_invalid")
    for field in ("accepted_room_preset_count", "approved_museum_video_count"):
        if type(review.get(field)) is not int or review[field] != 0:
            errors.append(field + "_must_stay_zero_in_candidate_study")
    if not archive.is_file():
        return errors + ["real_photo_archive_missing"]
    try:
        with zipfile.ZipFile(archive) as z:
            files = set(z.namelist())
            if "PROVENANCE_AND_RIGHTS.json" not in files:
                return errors + ["source_provenance_manifest_missing"]
            manifest = json.loads(z.read("PROVENANCE_AND_RIGHTS.json"))
            sources = manifest.get("items", [])
            by_id = {row["id"]: row for row in sources if isinstance(row, dict) and "id" in row}
            if len(sources) != 5 or len(by_id) != 5 or set(by_id) != set(ids):
                errors.append("manifest_review_five_ids_mismatch")
            if manifest.get("asset_count") != 5:
                errors.append("manifest_does_not_report_five_photos")
            for entry in entries:
                if not isinstance(entry, dict):
                    errors.append("review_entry_not_object")
                    continue
                ident = entry.get("id")
                src = by_id.get(ident)
                if not src:
                    errors.append(str(ident) + "_manifest_missing")
                    continue
                name = src.get("local_basename")
                if name != ident + "_PHOTOGRAPH.jpg" or name not in files:
                    errors.append(ident + "_file_missing_or_renamed")
                    continue
                raw_sha = hashlib.sha256(z.read(name)).hexdigest()
                if (raw_sha != src.get("sha256")
                    or raw_sha != entry.get("photo_jpg_sha256")):
                    errors.append(ident + "_byte_sha_mismatch")
                if (entry.get("dimensions_px") != src.get("dimensions")
                    or entry.get("source_page") != src.get("source_page")
                    or entry.get("license_declared_by_source_manifest") != src.get("license")
                    or entry.get("photographer") != src.get("author")):
                    errors.append(ident + "_provenance_review_mismatch")
                if src.get("status") != "photo_downloaded_unreviewed":
                    errors.append(ident + "_photograph_not_downloaded")
                if entry.get("assistant_visual_triage") not in CANDIDATE_STATUS:
                    errors.append(ident + "_unknown_triage")
                for field in ("metric_room_reconstruction_exists",
                              "tracked_camera_mp4_exists",
                              "artwork_specific_frame_verified",
                              "artistic_approval", "owner_approval",
                              "eligible_for_museum_final"):
                    if entry.get(field) is not False:
                        errors.append(ident + "_" + field + "_false_claim")
    except (OSError, zipfile.BadZipFile, ValueError, KeyError, TypeError) as exc:
        errors.append("photo_archive_invalid:" + type(exc).__name__)
    return errors


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", type=Path, required=True)
    ap.add_argument("--review", type=Path, default=Path(
        "config/artvision_v121_photo_source_visual_audit.json"))
    args = ap.parse_args()
    review = json.loads(args.review.read_text(encoding="utf8"))
    errors = audit(args.archive, review)
    print(json.dumps({
        "schema": "artvision-v121-photo-source-integrity-result",
        "passed": not errors, "errors": errors,
        "verified_museum_video_count": 0,
        "artistically_approved_room_count": 0,
        "nature": "photo source audit only; never a video approval",
    }, indent=2))
    if errors:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
