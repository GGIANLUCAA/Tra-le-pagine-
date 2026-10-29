#!/usr/bin/env python3
"""V83.2 selection gate for 4 restored archival photo scenes + ONE moving-color Vidu shot.
Editorial scoring only. NEVER calls video providers, never authorizes spending.
All candidate ratings must be supplied as explicit editorial observations, not invented.
"""
from __future__ import annotations
import argparse,json,hashlib,sys
from pathlib import Path

FIELDS=("hook","movement","source_quality","photo_fidelity","identity_risk","story_value","continuity")
WEIGHTS={"hook":.23,"movement":.22,"source_quality":.16,"photo_fidelity":.13,"story_value":.16,"continuity":.10}
ROLE_MULTIPLIER={"opening":1.0,"middle":1.0,"ending":1.0}
class PlanningError(ValueError):pass

def validate(data):
 if not isinstance(data,dict):raise PlanningError("Input must be an object")
 items=data.get("scenes")
 if not isinstance(items,list) or len(items)<5:raise PlanningError("At least 5 candidate scenes are required")
 ids=set();keys=set()
 for i,s in enumerate(items):
  if not isinstance(s,dict):raise PlanningError("Scene must be an object")
  for f in ["id","place","period","source_page","source_frame_hash","source_footage_id","description","rights","editorial"]:
   if f not in s:raise PlanningError(f"Scene {i}: missing {f}")
  if not isinstance(s["id"],str) or not s["id"]:raise PlanningError("Empty scene ID")
  if s["id"] in ids:raise PlanningError("Duplicate scene id")
  ids.add(s["id"])
  key=(s["source_footage_id"],s.get("source_timecode"))
  if key in keys:raise PlanningError("Repeated original shot presented as a different scene")
  keys.add(key)
  if not isinstance(s["source_frame_hash"],str) or len(s["source_frame_hash"])!=64:
   raise PlanningError("Source frame SHA-256 required")
  e=s["editorial"]
  if not isinstance(e,dict) or any(k not in e or type(e[k]) not in (int,float) or not 0<=e[k]<=5 for k in FIELDS):
   raise PlanningError("All editorial ratings 0..5 must be explicitly supplied: "+",".join(FIELDS))
  r=s["rights"]
  if not isinstance(r,dict) or r.get("license") not in ("PUBLIC_DOMAIN","CC0","PDM"):
   raise PlanningError("This project accepts only original footage declared PD/CC0/PDM for preflight")
  if not isinstance(s["source_page"],str) or not s["source_page"].startswith("https://"):
   raise PlanningError("Source record with https URL required")
 return items

def rank_vidu(scene):
 e=scene["editorial"]
 raw=sum(WEIGHTS[k]*e[k] for k in WEIGHTS)
 risk=e["identity_risk"]*.25
 if scene.get("camera_moves_large"):risk+=.35
 if scene.get("object_morph_risk_high"):risk+=.5
 return round(raw-risk,4)

def rank_classic(scene):
 e=scene["editorial"]
 return round(.28*e["photo_fidelity"]+.23*e["source_quality"]+.20*e["story_value"]+.16*e["hook"]+.13*e["continuity"]-.14*e["identity_risk"],4)

def choose_position(clip):
 # Candidate editorially rates which role makes its movement most effective.
 roles=clip.get("narrative_roles")
 if not isinstance(roles,dict) or any(x not in roles or type(roles[x]) not in (int,float) or not 0<=roles[x]<=5 for x in ("opening","middle","ending")):
  raise PlanningError("A Vidu candidate must score opening/middle/ending role on 0..5")
 best=sorted(("opening","middle","ending"),key=lambda x:(-roles[x],{"opening":0,"middle":1,"ending":2}[x]))[0]
 return {"opening":0,"middle":2,"ending":4}[best],best

def build_plan(data):
 scenes=validate(data)
 # Eligibility is a separate gate: do not rate unauthorised footage as production ready.
 candidates=[s for s in scenes if s.get("vidu_possible") is True]
 if not candidates:raise PlanningError("No moving-color Vidu candidate available")
 chosen=max(candidates,key=lambda s:(rank_vidu(s),s["id"]))
 other=sorted((s for s in scenes if s["id"]!=chosen["id"] and s.get("restored_photo_available") is True),
              key=lambda s:(-rank_classic(s),s["id"]))
 if len(other)<4:raise PlanningError("Need 4 already available source-matched generative photos distinct from Vidu")
 chosen_classics=other[:4]
 # If source footage has uncertain time, it is not suitable for unlabelled continuity.
 periods={s["period"] for s in [chosen,*chosen_classics]}
 places={s["place"] for s in [chosen,*chosen_classics]}
 same_time=len(periods)==1;same_place=len(places)==1
 slot,role=choose_position(chosen)
 # Stable order: high narrative continuity plus original chronological ordering.
 chosen_classics.sort(key=lambda s:(s.get("story_order",999),s["id"]))
 order=[dict(id=s["id"],type="CLASSICAL_REAL_FILM_TO_AI_PHOTO",
             source=s["source_page"],period=s["period"],place=s["place"],
             source_frame_hash=s["source_frame_hash"],photo=s.get("restored_photo_path"),
             editorial_classic_score=rank_classic(s)) for s in chosen_classics]
 order.insert(slot,dict(id=chosen["id"],type="VIDU_MOVING_COLOR_5S",
      source=chosen["source_page"],period=chosen["period"],place=chosen["place"],
      source_frame_hash=chosen["source_frame_hash"],
      existing_vidu_mp4=chosen.get("vidu_clip_path"),
      editorial_vidu_score=rank_vidu(chosen),position_role=role))
 rights_approved=all(s["rights"].get("jurisdiction_reviewed") is True for s in [chosen,*chosen_classics])
 all_assets=all(s.get("restored_photo_path") for s in chosen_classics)
 video_existing=bool(chosen.get("vidu_clip_path"))
 status="CAN_RENDER_PREVIEW_WITH_REVIEW" if video_existing and all_assets else "PREFLIGHT_NEEDS_VIDEO_OR_PHOTO"
 # Provenance and visual gate are always required; no score or generated AI image can approve itself.
 plan={"version":"V83.2-4PLUS1","total_chapters":5,"classic_count":4,"vidu_count":1,
  "target_duration_s":[19,26],"recommended_vidu_position":slot+1,
  "recommended_vidu_role":role,"chapters":order,"same_place":same_place,"same_historical_period":same_time,
  "warn_mixed_eras":not same_time,"warn_mixed_locations":not same_place,
  "production_may_proceed_without_period_label":bool(same_time and same_place),
  "historical_rights_jurisdiction_preflight":rights_approved,
  "technical_input_status":status,
  "video_cost":"NOT_QUOTED_BY_PROVIDER; obtain new exact API quote if no clip exists",
  "user_approval_required_before_single_Vidu_POST":not video_existing,
  "max_paid_retries":0,"new_video_generated":False,"new_credits_spent":0,
  "creative_requirements":["Vidu first ~1s B/W→color","~4s continuous color motion",
    "exact first frame and clean geometry","one music bed across all five chapters",
    "no 2 unrelated faces cross-dissolved","5 genuine distinct shots"],
  "manual_review_pending":True,"social_publish_authorized":False,
  "visual_artistic_approval":False,"pipeline_reference":"docs/LA_STORIA_RIVIVE_HYBRID_4PLUS1_V83.md"}
 if not same_time:plan["mandatory_title_period"]="Label all historical periods, or choose same-period assets"
 return plan

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--candidates",required=True);p.add_argument("--out",required=True)
 a=p.parse_args();data=json.loads(Path(a.candidates).read_text())
 result=build_plan(data);out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print("V83_EDITORIAL_PLAN_ONLY_NO_PAID_CALL",out,result["technical_input_status"],
       "vidu_slot",result["recommended_vidu_position"],flush=True)
if __name__=="__main__":main()
