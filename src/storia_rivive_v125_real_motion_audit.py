#!/usr/bin/env python3
"""V125: free decoded-motion review of real V124 photographic film candidates.

Use *only* the SHA-bound original film, actual FFmpeg PTS and unaltered PNGs.
Audit every photo-like candidate, then propose up to five different timeline
regions with verified pixel movement. Never authorize I2I, Vidu or publishing.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

try:
    from src.storia_rivive_adaptive_sampling_v124 import sha256_file, spread_review_shortlist
    from src.storia_rivive_frame_rank_v101 import pre_freeze_window_evidence
    from src.storia_rivive_motion_window_v115 import inspect_source_motion
except ModuleNotFoundError:
    from storia_rivive_adaptive_sampling_v124 import sha256_file, spread_review_shortlist
    from storia_rivive_frame_rank_v101 import pre_freeze_window_evidence
    from storia_rivive_motion_window_v115 import inspect_source_motion


SHA = re.compile(r"[0-9a-f]{64}\Z")
FRAME = re.compile(r"frame_\d{2}\.png\Z")
MAX_CANDIDATES = 48


def validate_source(film, scout, selection, source_folder):
    """Raise BEFORE opening any moving scene if source metadata is inconsistent."""
    digest = scout.get("original_sha256")
    if (scout.get("status") != "REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW"
            or scout.get("adaptive_research_version")
               != "V124_UNAPPROVED_LONG_SEGMENT_TARGET_SAMPLING"
            or not isinstance(digest, str) or SHA.fullmatch(digest) is None):
        raise ValueError("V125_SOURCE_SHA_OR_SCOUT_STATE_INVALID")
    if sha256_file(film) != digest:
        raise ValueError("V125_ORIGINAL_SOURCE_SHA256_MISMATCH")
    if (selection.get("adaptive_frame_source_sha256") != digest
            or selection.get("adaptive_review_only_not_camera_approval") is not True):
        raise ValueError("V125_RANK_SOURCE_SHA_OR_UNAPPROVED_STATE_INVALID")
    shots = scout.get("shot_boundary_analysis")
    if (not isinstance(shots, dict)
            or shots.get("version") != "V113_FFMPEG_SCENE_CANDIDATES"
            or shots.get("source_sha256") != digest
            or shots.get("status") != "FIVE_SEGMENTS_POSSIBLE_REVIEW_REQUIRED"):
        raise ValueError("V125_CUTS_NOT_SOURCE_LOCKED")
    cuts = shots.get("cut_candidate_times_s")
    if (not isinstance(cuts, list) or len(cuts) < 4
            or any(type(n) not in (int, float) or not math.isfinite(n) or n <= 0 for n in cuts)
            or any(x >= y for x, y in zip(cuts, cuts[1:]))):
        raise ValueError("V125_INVALID_SOURCE_CUT_TIMES")
    duration = scout.get("duration_s")
    if (type(duration) not in (int, float) or not math.isfinite(duration)
            or duration <= 0 or cuts[-1] >= duration):
        raise ValueError("V125_INVALID_SOURCE_DURATION")
    provenance = scout.get("frame_provenance")
    if (not isinstance(provenance, list)
            or not 5 <= len(provenance) <= MAX_CANDIDATES
            or scout.get("frame_provenance_source_sha256") != digest):
        raise ValueError("V125_SOURCE_PROVENANCE_INCOMPLETE")
    file_map = {}
    for row in provenance:
        if not isinstance(row, dict):
            raise ValueError("V125_PROVENANCE_ROW_INVALID")
        name = row.get("filename")
        if not isinstance(name, str) or FRAME.fullmatch(name) is None or name in file_map:
            raise ValueError("V125_FRAME_NAME_INVALID_DUPLICATE_OR_PATH_ESCAPE")
        png_sha = row.get("sha256")
        if (not isinstance(png_sha, str) or SHA.fullmatch(png_sha) is None
                or row.get("source_pts_logged_from_decode") is not True):
            raise ValueError("V125_SOURCE_FRAME_SHA_OR_PTS_MISSING")
        path = source_folder / name
        if not path.is_file() or path.is_symlink() or sha256_file(path) != png_sha:
            raise ValueError("V125_ORIGINAL_FRAME_BYTES_CHANGED")
        file_map[name] = row
    candidates = selection.get("all_candidates")
    if not isinstance(candidates, list) or len(candidates) != len(file_map):
        raise ValueError("V125_RANKED_SOURCE_FRAME_COUNT_MISMATCH")
    if (len({r.get("filename") for r in candidates if isinstance(r, dict)})
            != len(file_map) or any(r.get("filename") not in file_map for r in candidates
                                    if isinstance(r, dict))):
        raise ValueError("V125_SOURCE_FRAME_RANK_MISMATCH")
    return digest, cuts, file_map, candidates, duration


def audit(film_path, scout_path, selection_path, output_path, *, inspector=None):
    """Record all photo-like motion outcomes and propose no more than five shots.

    The evidence flags mean measurable *spatial pixel differences*, not camera
    changes, subjects walking, reconstructed historical fidelity or rights.
    """
    film = Path(film_path)
    scout = json.loads(Path(scout_path).read_text(encoding="utf-8"))
    ranked = json.loads(Path(selection_path).read_text(encoding="utf-8"))
    digest, cuts, file_map, candidates, duration = validate_source(
        film, scout, ranked, Path(scout_path).parent/"original_frames")
    inspect_motion = inspector if inspector is not None else inspect_source_motion
    checked = []
    passing = []
    for row in candidates:
        original = file_map[row["filename"]]
        # Prefer hard failure over silent fallback when ranking source mismatch:
        if (row.get("shot_candidate_segment_index")
                != original.get("shot_candidate_segment_index")):
            raise ValueError("V125_SELECTED_FRAME_SEGMENT_TAMPERED")
        if (not row.get("source_native_detail_sufficient")
                or not row.get("source_picture_content_eligible")
                or not row.get("pre_freeze_window_viable")):
            continue
        window = pre_freeze_window_evidence(original, cuts)
        if not window["eligible"]:
            checked.append({"filename":row["filename"],"status":"BLOCKED",
                            "reason":window["reason"],"motion_verified":False})
            continue
        embedded = row.get("pre_freeze_window_pts")
        if (not isinstance(embedded, dict)
                or any(embedded.get(k) != window.get(k)
                       for k in ("start_pts", "freeze_pts", "time_base"))):
            raise ValueError("V125_RANKED_SOURCE_PTS_WINDOW_TAMPERED")
        evidence = inspect_motion(film, digest, window["start_pts"],
                                  window["freeze_pts"], window["time_base"])
        pass_motion = (evidence.get("status") == "MOTION_EVIDENCE_PASS"
                       and evidence.get("motion_verified") is True)
        checked.append({
            "filename": row["filename"],
            "source_time_s": original["source_pts_time_s"],
            "source_pts": original["source_pts"],
            "candidate_segment_index": original["shot_candidate_segment_index"],
            "start_pts": window["start_pts"],
            "freeze_pts": window["freeze_pts"],
            "time_base": window["time_base"],
            "motion_verified": pass_motion,
            "status": "MOTION_EVIDENCE_PASS" if pass_motion else "BLOCKED",
            "reason": evidence.get("reason", "UNSPECIFIED"),
            "sample_count": evidence.get("sample_count", 0),
            "changed_pairs": evidence.get("changed_pairs", 0),
            "max_spatial_pixel_delta": evidence.get("max_spatial_pixel_delta", 0.0)
        })
        if pass_motion:
            passing.append(row)
    spread = spread_review_shortlist({"all_candidates":passing},
                                     list(file_map.values()), duration)
    successful = spread["status"] == "V124_FIVE_TIME_SPREAD_SOURCE_CANDIDATES_REVIEW_ONLY"
    selected = []
    if successful:
        selected = [{
            "filename":row["filename"],
            "source_time_s":file_map[row["filename"]]["source_pts_time_s"],
            "source_pts":file_map[row["filename"]]["source_pts"],
            "time_base":file_map[row["filename"]]["source_time_base"],
            "frame_sha256":file_map[row["filename"]]["sha256"],
            "source_film_sha256":digest,
            "candidate_segment_index":row["candidate_segment_index"],
            "timeline_region":row["review_time_bucket"],
            "pre_freeze_window_pts":row["pre_freeze_window_pts"],
            "human_camera_shot_approval":False
        } for row in spread["preselected"]]
    result = {
        "version": "V125_REAL_BW_DECODED_SPATIAL_MOTION_UNAPPROVED",
        "status":("V125_FIVE_MOVING_PHOTO_REGIONS_REVIEW_REQUIRED" if successful
                  else "V125_MOTION_SOURCE_SELECTION_BLOCKED"),
        "source_video_sha256":digest,
        "source_duration_s":duration,
        "source_frames_checked":len(file_map),
        "source_photo_candidates_tested":len(checked),
        "source_motion_candidates_pass":len(passing),
        "five_review_shots":selected,
        "motion_audit":checked,
        "spatial_motion_is_not_proof_of_camera_shots":True,
        "human_review_required":True,
        "five_genuine_camera_shots_approved":False,
        "italian_rights_verified":False,
        "photos_i2i_generated":0,
        "vidu_generated":0,
        "paid_api_calls":0,
        "new_video_finished":False,
        "published":False
    }
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--film",required=True)
    p.add_argument("--scout",required=True)
    p.add_argument("--rank",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    try:
        report=audit(args.film,args.scout,args.rank,args.out)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        report={
            "version":"V125_REAL_BW_DECODED_SPATIAL_MOTION_UNAPPROVED",
            "status":"V125_MOTION_SOURCE_SELECTION_BLOCKED",
            "reason":str(exc)[:260],
            "five_review_shots":[],
            "human_review_required":True,
            "italian_rights_verified":False,
            "paid_api_calls":0,
            "new_video_finished":False,"published":False}
        out=Path(args.out)
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("V125_ORIGINAL_BW_MOTION",report["status"],
          "verified_photo_windows",report.get("source_motion_candidates_pass",0),
          "five_review_shots",len(report["five_review_shots"]))


if __name__=="__main__":
    main()
