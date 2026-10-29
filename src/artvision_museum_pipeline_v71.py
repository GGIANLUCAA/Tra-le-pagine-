#!/usr/bin/env python3
"""ArtVision V71: V68 recipe + V69 evidence + V70 scale + V64 continuous camera.

Safe offline planning adapter. Does not download assets, render or approve videos,
contact paid APIs, change existing masters, or release the V58 pilot lock.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

from artvision_museum_director_v69 import evaluate
from artvision_museum_stage_v70 import plan_stage
from artvision_museum_camera_v64 import camera_at
from artvision_museum_frame_focus_v73 import focus_storyboard
from artvision_recipe_v68 import build_recipe, inspect, VARIANTS

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "config/artvision_pilot_lock_v58.json"
BASELINE = ROOT / "docs/productions/2026-10-29-socrates-pilot-v68/BASELINE_CREATIVE_MANIFEST_V68.json"

class PlanningBlocked(ValueError):
    pass

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def validate_provenance(d):
    errors = []
    image_sha = d.get("artwork", {}).get("image_sha256", "")
    if not isinstance(image_sha, str) or not re.fullmatch(r"[a-f0-9]{64}", image_sha):
        errors.append("Exact 64-character source image SHA256 required")
    for kind in ("frame", "gallery"):
        obj = d.get(kind, {})
        if obj.get("status") == "actual_documented" and kind == "gallery":
            if not obj.get("photo_rights"):
                errors.append("Actual gallery photograph rights required")
        if kind == "frame" and obj.get("status") in (
            "original_documented", "current_documented", "historic_documented"
        ):
            if not obj.get("photo_source", "").startswith("https://"):
                errors.append("Exact frame photo must have HTTPS source URL")
    return errors

def beats_for_duration(seconds, center_x, center_y):
    """V64 timed camera positions: start and end at same normalized room pose."""
    seconds = float(seconds)
    if not math.isfinite(seconds) or seconds < 12:
        raise PlanningBlocked("Museum sequence must last at least 12 seconds")
    starts = [round(seconds * p, 6) for p in (0, .12, .27, .44, .70, .86)]
    poses = [
        (center_x, center_y, 1.00),
        (center_x, center_y, 1.22),
        (center_x, center_y, 1.95),
        (min(.8, center_x + .08), min(.8, center_y + .04), 2.75),
        (center_x, center_y, 2.05),
        (center_x, center_y, 1.00),
    ]
    samples = sorted(set([0, 1, 3, 5, 7, seconds, seconds*.7,
                          max(0, seconds*.7-.001), min(seconds, seconds*.7+.001)]))
    keyframes = []
    for t in samples:
        x,y,z = camera_at(t, seconds, starts, poses)
        keyframes.append({"t_seconds":round(t,4), "x":round(x,6),
                          "y":round(y,6),"zoom":round(z,6)})
    if abs(camera_at(0,seconds,starts,poses)[2]-
           camera_at(seconds,seconds,starts,poses)[2])>1e-8:
        raise PlanningBlocked("Camera does not return to gallery")
    return {"module":"artvision_museum_camera_v64.camera_at",
            "frame_visibility_v73":focus_storyboard(seconds,starts,poses),
            "duration_seconds":seconds,"beat_starts_seconds":starts,
            "poses":[list(p) for p in poses],
            "sampled_keyframes":keyframes,
            "method":"normalized continuous POV; illustrative artwork entry",
            "spoken_content_alignment":"not_checked_without_real_WAV_ASR"}

def build(dossier, pilot_lock=None, baseline=None):
    lock = pilot_lock if pilot_lock is not None else load_json(LOCK)
    existing = baseline if baseline is not None else load_json(BASELINE)
    work_id = dossier.get("artwork_id","")
    if lock.get("active") and work_id != lock.get("allowed_group_id"):
        raise PlanningBlocked("V58 PILOT LOCK: only existing Socrates pilot allowed")
    if work_id != existing.get("artwork_id"):
        raise PlanningBlocked("Baseline not matched to artwork; no new work")
    if lock.get("active") and not lock.get("no_paid_video_calls",True):
        raise PlanningBlocked("V58 pilot safety flags unexpected")
    evidence = evaluate(dossier)
    problems = evidence["errors"] + validate_provenance(dossier)
    if problems:
        raise PlanningBlocked("Museum evidence blocked: " + "; ".join(problems))
    physical = plan_stage(dossier)
    if physical["status"] != "stage_plan_ready":
        raise PlanningBlocked("Museum physical planning failed")
    a = dossier["artwork"]
    recipe = build_recipe(work_id, a["title"], a["artist"], a["source_url"])
    recipe_errors = inspect(recipe)
    if recipe_errors:
        raise PlanningBlocked("V68 recipe contract: " + "; ".join(recipe_errors))
    existing_slots=existing.get("four_slots",{})
    if set(existing_slots)!=set(VARIANTS):
        raise PlanningBlocked("Four existing V68 slots required")
    if existing.get("formal_v25_approvals",existing.get("artistic_user_feedback",{}).get("formal_v25_approvals")) not in (None,0):
        raise PlanningBlocked("Baseline approval state changed: review manually")
    # Reuse the same safe physical viewing distance calculated in V72.
    # A small panel must not be zoomed to fill the opening frame.
    field_of_view_deg=physical["gallery"]["horizontal_fov_degrees"]
    start_distance_m=round(physical["gallery"]["camera_start_distance_cm"]/100.,3)
    center_x = dossier["camera"]["painting_center_x"]
    center_y = dossier["camera"]["painting_center_y"]
    durations = {
        "critico_museum": existing_slots["critico_museum"]["duration_seconds"],
        "cinema_museum": existing_slots["cinema_museum"]["duration_seconds"]
    }
    camera = {k:beats_for_duration(v,center_x,center_y) for k,v in durations.items()}
    critic1=existing_slots["critico_standard"].get("voice_sha256")
    critic2=existing_slots["critico_museum"].get("voice_sha256")
    if not critic1 or critic1!=critic2:
        raise PlanningBlocked("V68 critic pair must share identical source WAV")
    if any(existing_slots[k].get("approval_v25") for k in VARIANTS):
        raise PlanningBlocked("Existing pilot approvals require manual reconciliation")
    return {
      "schema":"artvision-museum-integration-plan-v71",
      "artwork_id":work_id,
      "primary_source":a["source_url"],
      "evidence":{"frame_status":dossier["frame"]["status"],
                  "frame_source":dossier["frame"].get("photo_source"),
                  "frame_photo_rights":dossier["frame"].get("photo_rights"),
                  "gallery_status":dossier["gallery"]["status"],
                  "gallery_disclosure":dossier["gallery"].get("disclosure"),
                  "real_gallery_claim":False,
                  "painting_image_sha256":a["image_sha256"],
                  "dimensions_source":a["dimensions_source"]},
      "physical_stage":physical,
      "physical_camera":{"horizontal_fov_degrees":field_of_view_deg,
                         "starting_view_distance_m_estimate":start_distance_m,
                         "distance_kind":"creative_fov_staging_estimate_not_measured"},
      "museum_camera":camera,
      "four_slots":{k:{"existing_status":existing_slots[k]["status"],
                       "existing_sha256":existing_slots[k]["sha256"],
                       "v25_approved":False,
                       "has_new_render":False,
                       "museum_plan":k in camera}
                    for k in VARIANTS},
      "voice":{"critico_exact_shared_wav_sha256":critic1,
               "re_synthesis_authorized":False},
      "controls":{"pilot_lock_active":bool(lock.get("active")),
                  "owner_automation_id":lock.get("owner_automation_id"),
                  "new_artwork_selection":False,
                  "social_autopublish":False,
                  "paid_video_calls":False,
                  "archive_claimed_verified":False,
                  "render_authorized":False,
                  "human_full_speed_review_pending":True},
      "next_step":"Use on Socrates existing artwork/approved assets; production needs renderer adapter and real QA."
    }

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dossier",required=True)
    parser.add_argument("--out")
    args=parser.parse_args()
    plan=build(load_json(args.dossier))
    output=json.dumps(plan,ensure_ascii=False,indent=2)+"\n"
    if args.out:
        target=Path(args.out)
        target.parent.mkdir(parents=True,exist_ok=True)
        with target.open("x",encoding="utf-8") as f:f.write(output)
        print("MUSEUM_V71_PLAN_WRITTEN: "+str(target)+" (NO RENDER)")
    else:print(output,end="")

if __name__=="__main__":
    main()
