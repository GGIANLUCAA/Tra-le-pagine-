#!/usr/bin/env python3
"""ArtVision V119 fail-closed museum approval gate. No rendering or paid calls.

This program deliberately cannot judge whether a scene looks photorealistic:
an actual human review of a real MP4 is still mandatory. It blocks missing
evidence, non-metric staging, unapproved presets and bitmap-zoom fallbacks.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

CATALOG_SCHEMA = "artvision-museum-library-v119"
VALID_FRAMES = {"authentic_documented", "faithful_reconstruction_documented", "unverified"}
REAL_SHA256 = re.compile(r"^[0-9a-f]{64}$")
DISALLOWED_RENDERERS = {
    "artvision_four_original_v116.py",
    "artvision_four_new_original_v114.py",
    "artvision_missing_critico_v117.py",
}


def number(value):
    return type(value) in (int, float) and math.isfinite(value) and value > 0


def sha256(value):
    return isinstance(value, str) and bool(REAL_SHA256.fullmatch(value))


def check_catalog(data):
    problems = []
    if data.get("schema") != CATALOG_SCHEMA:
        problems.append("catalog_schema_invalid")
    if data.get("status") != "design_candidates_only_no_assets_or_approval" and data.get("status") != "assets_in_review":
        if data.get("status") != "production_ready":
            problems.append("catalog_status_unknown")
    for kind, prefix in (("rooms", "GAL"), ("frames", "FRA")):
        items = data.get(kind)
        if not isinstance(items, list) or len(items) < 5:
            problems.append(kind + "_minimum_five")
            continue
        ids = [p.get("id") for p in items if isinstance(p, dict)]
        if len(set(ids)) != len(items) or any(not isinstance(v, str) or not v.startswith(prefix) for v in ids):
            problems.append(kind + "_invalid_or_duplicate_ids")
        for p in items:
            if not isinstance(p, dict):
                problems.append(kind + "_invalid_entry")
                continue
            if p.get("status") == "approved":
                asset_hash = p.get("real_3d_or_photographic_asset_sha256") if kind == "rooms" else p.get("asset_sha256")
                if not sha256(asset_hash) or not sha256(p.get("preview_mp4_sha256")):
                    problems.append(p["id"] + "_approved_without_real_asset_and_mp4")
                if p.get("artistic_approval") is not True:
                    problems.append(p["id"] + "_approved_without_artistic_approval")
                if kind == "rooms" and (not p.get("asset_source_url") or not p.get("license")):
                    problems.append(p["id"] + "_approved_without_source_rights")
                if kind == "frames" and not p.get("source_or_model_rights"):
                    problems.append(p["id"] + "_approved_without_rights")
            elif p.get("status") not in ("candidate_unbuilt", "rendered_needs_review"):
                problems.append(str(p.get("id")) + "_unknown_status")
    return problems


def by_id(catalog, kind, ident):
    return next((v for v in catalog.get(kind, []) if v.get("id") == ident), None)


def check_real_render(renderer_path):
    if not renderer_path:
        return ["renderer_path_required"]
    path = Path(renderer_path)
    if path.name in DISALLOWED_RENDERERS:
        return ["legacy_bitmap_museum_renderer_forbidden"]
    if not path.is_file():
        return ["renderer_source_not_found"]
    code = path.read_text(encoding="utf8")
    # A standalone panorama/card followed by zoompan is not a 3D gallery.
    if "def room_card(" in code:
        return ["raster_room_card_renderer_forbidden"]
    if "zoompan" in code and not any(s in code for s in ("bpy", "pyrender", "render_3d_scene", "real_camera_track")):
        return ["zoompan_only_renderer_not_a_museum_camera"]
    return []


def check_work(catalog, work, renderer_path=None):
    problems = check_catalog(catalog)
    if not isinstance(work, dict):
        return problems + ["work_dossier_missing"]
    need = lambda key: work.get(key) not in (None, "", "unverified", "unknown")
    for key in ("artwork_id", "accession", "source_url", "dimensions_source",
                "room_preset_id", "frame_status", "frame_preset_or_bespoke_id"):
        if not need(key):
            problems.append(key + "_missing")
    if not sha256(work.get("image_sha256")):
        problems.append("artwork_image_sha256_missing")
    for key in ("width_cm", "height_cm"):
        if not number(work.get(key)):
            problems.append(key + "_invalid")
    if work.get("frame_status") not in VALID_FRAMES:
        problems.append("frame_status_invalid")
    if work.get("frame_status") == "unverified":
        if work.get("frame_owner_exception_approval") is not True:
            problems.append("unverified_frame_needs_specific_owner_approval")
    elif not work.get("frame_source_url"):
        problems.append("documented_frame_source_missing")
    room = by_id(catalog, "rooms", work.get("room_preset_id"))
    if room is None:
        problems.append("room_preset_not_in_catalog")
    else:
        if room.get("status") != "approved" or room.get("artistic_approval") is not True:
            problems.append("room_not_yet_approved")
        if work.get("room_asset_sha256") != room.get("real_3d_or_photographic_asset_sha256") or not sha256(work.get("room_asset_sha256")):
            problems.append("room_asset_hash_not_verified")
        if work.get("room_license") != room.get("license") or not work.get("room_license"):
            problems.append("room_license_not_verified")
    frame = by_id(catalog, "frames", work.get("frame_preset_or_bespoke_id"))
    if frame is None:
        # An individually documented bespoke frame is valid with explicit provenance.
        if not work.get("bespoke_frame_documentation"):
            problems.append("frame_not_catalogued_or_documented_bespoke")
    elif frame.get("status") != "approved" or frame.get("artistic_approval") is not True:
        problems.append("frame_preset_not_yet_approved")
    if not number(work.get("camera_world_scale_m")) or not number(work.get("reference_scale_object_m")):
        problems.append("room_camera_and_scale_reference_must_be_metric")
    if work.get("artwork_scale_constant_across_shots") is not True:
        problems.append("artwork_scale_must_remain_constant")
    if work.get("same_room_and_frame_on_exit") is not True:
        problems.append("museum_intro_outro_continuity_missing")
    if not sha256(work.get("intro_outro_mp4_sha256")):
        problems.append("real_video_preview_hash_missing")
    # V331 (12/11/2026): no oblique/skewed painting on a museum wall.
    # This is a necessary gate, never sufficient for Gold or room authenticity.
    # A real V331 JSON geometry result is required in the production dossier.
    if work.get("frontal_geometry_v331_status") != "READY_FOR_ARTISTIC_REVIEW":
        problems.append("museum_frontal_geometry_v331_not_passed")
    if not sha256(work.get("frontal_geometry_v331_report_sha256")):
        problems.append("museum_frontal_gate_report_sha256_missing")
    if work.get("frontal_pose_fullspeed_review_passed") is not True:
        problems.append("museum_frontal_pose_human_review_missing")
    if work.get("visual_review_status") != "approved" or work.get("user_or_authorized_reviewer_approval") is not True:
        problems.append("human_visual_approval_missing")
    problems.extend(check_real_render(renderer_path))
    return list(dict.fromkeys(problems))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=Path("config/artvision_museum_library_v119.json"))
    parser.add_argument("--dossier", type=Path)
    parser.add_argument("--renderer", type=str)
    args = parser.parse_args()
    catalog = json.loads(args.catalog.read_text(encoding="utf8"))
    errors = check_catalog(catalog) if args.dossier is None else check_work(
        catalog, json.loads(args.dossier.read_text(encoding="utf8")), args.renderer
    )
    data = {
        "schema": "artvision-museum-v119-validation",
        "passed": not errors,
        "errors": errors,
        "rooms_ready": sum(v.get("status") == "approved" for v in catalog.get("rooms", [])),
        "frames_ready": sum(v.get("status") == "approved" for v in catalog.get("frames", [])),
        "artistic_quality_certified_by_software": False,
        "final_video_approved": False if args.dossier is None else not errors,
    }
    print(json.dumps(data, indent=2))
    if errors:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
