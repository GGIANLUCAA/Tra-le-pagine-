#!/usr/bin/env python3
"""V152: conservative editorial coherence preflight for the V151 source handoff.

Only compares authenticated archive metadata and the V151 SHA-bound handoff.
It never grants source/rights/artistic approval or permits provider requests.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

try:
    from src.storia_rivive_v149_authentic_bw_proxy import validate
except ModuleNotFoundError:
    from storia_rivive_v149_authentic_bw_proxy import validate

V151_STATUS = "V151_FIVE_EXACT_SOURCE_FRAMES_PREPARED_AWAITING_HUMAN_SOURCE_AND_RIGHTS_REVIEW"
STATUS = "V152_EDITORIAL_SOURCE_COHERENCE_BLOCKED"
PLACE_YEAR = re.compile(r"([A-ZÀ-ÖØ-Ý][A-ZÀ-ÖØ-Ý '\-]{1,80})\s*·\s*(\d{4})\Z")


def audit(manifest: dict, handoff: dict) -> dict:
    """Fail closed on source/role/approval tampering; flag mixed or unknown subjects.

    Same place/year is a *candidate grouping*, not evidence that shots, historical
    subjects, Italian rights or AI reconstruction are appropriate for one episode.
    """
    sources = validate(manifest)
    if (not isinstance(handoff, dict) or handoff.get("status") != V151_STATUS
            or handoff.get("real_source_frames_sha_verified") != 5
            or handoff.get("candidate_i2i_jobs") != 4
            or handoff.get("vidu_frame_anchors") != 1
            or any(handoff.get(k) != 0 for k in (
                "real_restored_photos_generated", "real_vidu_clips_generated",
                "provider_requests_sent", "paid_api_calls"))
            or any(handoff.get(k) is not False for k in (
                "source_subjects_are_a_coherent_single_episode_verified",
                "five_different_camera_shots_artistically_verified",
                "rights_italy_verified", "artistic_approved",
                "gateway_scene_permission_granted", "publish_permitted"))):
        raise ValueError("V152_UNVERIFIED_OR_PREAPPROVED_HANDOFF")
    rows = handoff.get("freeze_frames")
    if not isinstance(rows, list) or len(rows) != 5:
        raise ValueError("V152_EXACT_FIVE_SOURCE_HANDOFF_ROWS_REQUIRED")
    groups = defaultdict(list)
    missing_place = []
    years = set()
    for source, row in zip(sources, rows):
        role = "I2I_PHOTO_CANDIDATE_NOT_GENERATED" if source["scene"] <= 4 else "VIDU_ANCHOR_NOT_SUBMITTED"
        if (not isinstance(row, dict) or row.get("scene") != source["scene"]
                or row.get("role") != role or row.get("source_id") != source["id"]
                or row.get("source_page") != source["source_page"]
                or row.get("source_film_sha256") != source["original_sha256"]
                or row.get("native_original_frame_sha256") != source["frame_sha256"]
                or row.get("native_original_frame_pts") != source["freeze_pts"]
                or row.get("native_time_base") != source["time_base"]
                or any(row.get(k) is not False for k in (
                    "image_to_image_sent", "vidu_request_sent",
                    "source_subject_artistically_reviewed", "face_and_object_fidelity_verified",
                    "rights_italy_verified", "provider_credit_budget_approved"))):
            raise ValueError("V152_HANDOFF_SCENE_SHA_ROLE_OR_PERMISSION_MISMATCH")
        year = source.get("year")
        if type(year) is not int or not 1850 <= year <= 2026:
            raise ValueError("V152_INVALID_HISTORICAL_YEAR")
        years.add(year)
        label = source.get("place_label")
        matched = PLACE_YEAR.fullmatch(label.strip()) if isinstance(label, str) else None
        if matched:
            place, labeled_year = matched.groups()
            if int(labeled_year) != year:
                raise ValueError("V152_PLACE_LABEL_YEAR_CONTRADICTS_SOURCE")
            groups[(place.strip(), year)].append(source["scene"])
        else:
            missing_place.append(source["scene"])
    reasons = ["HUMAN_SHOT_AND_EPISODE_REVIEW_PENDING", "ITALIAN_TERRITORIAL_RIGHTS_NOT_VERIFIED"]
    if len(years) != 1:
        reasons.append("MIXED_HISTORICAL_YEARS")
    if missing_place:
        reasons.append("PLACE_NOT_DOCUMENTED_FOR_ALL_SCENES")
    if len({place for place, _ in groups}) > 1:
        reasons.append("MULTIPLE_DOCUMENTED_PLACES")
    return {
        "version": "V152", "status": STATUS,
        "source_count": 5, "source_years": sorted(years),
        "scenes_without_documented_place": missing_place,
        "same_place_year_candidate_groups": [
            {"place": place, "year": year, "scenes": scenes, "count": len(scenes)}
            for (place, year), scenes in sorted(groups.items()) if len(scenes) >= 2
        ],
        "blocking_reasons": reasons,
        "coherent_single_episode_verified": False,
        "five_camera_shots_artistically_verified": False,
        "rights_italy_verified": False,
        "provider_jobs_may_start": False,
        "paid_api_calls": 0,
        "published": False,
        "note": "Grouping by documented place/year is metadata-only; it cannot approve a film, restoration, Vidu charge or distribution."
    }


def write_report(manifest_path, handoff_path, output_path):
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    handoff = json.loads(Path(handoff_path).read_text(encoding="utf-8"))
    result = audit(manifest, handoff)
    Path(output_path).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True)
    p.add_argument("--handoff", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    r = write_report(args.manifest, args.handoff, args.out)
    print("V152", r["status"], "years", r["source_years"], "unknown_place_scenes", r["scenes_without_documented_place"], "paid", 0)
