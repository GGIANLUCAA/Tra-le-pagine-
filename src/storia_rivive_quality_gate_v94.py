#!/usr/bin/env python3
"""V94 binding QA for NEW La Storia Rivive video episodes.
No image synthesis, no Vidu POST, no spending, no credentials or fake human approvals.
Checks immutable evidence required to authorize the one paid generation and
a final reel containing the ACTUAL generated motion. Legacy masters are not rewritten.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
POLICY=ROOT/"config/storia_rivive_quality_v94.json"
HEX64=re.compile(r"^[0-9a-f]{64}$")
TASK=re.compile(r"^[a-zA-Z0-9_-]{8,}$")

def _sha_ok(v):return isinstance(v,str) and bool(HEX64.fullmatch(v))
def _txt_ok(v):return isinstance(v,str) and bool(v.strip())
def _bool(v):return v is True
def _number(v):return type(v) in (int,float) and v>=0
def _need(err,predicate,msg):
    if not predicate:err.append(msg)

def is_new_storia(manifest):
    kind=str(manifest.get("format",manifest.get("format_name",""))).lower().strip()
    if not (kind=="storia_rivive" or "storia rivive" in kind):return False
    # A new reel cannot bypass the policy by merely calling itself 'legacy'.
    version=manifest.get("quality_policy_version")
    date=str(manifest.get("production_date",""))
    legacy=manifest.get("legacy_historical_master_readonly") is True
    if legacy and date and date<"2026-10-30" and version!="V94":
        return False
    # Missing dates must fail closed for any explicitly marked historical format.
    return version=="V94" or not date or date>="2026-10-30"

def inspect(manifest,phase="delivery",policy=None):
    """Return list of errors. Fail-closed for new V94 manifests; other formats untouched."""
    if not is_new_storia(manifest):return []
    policy=policy or json.loads(POLICY.read_text(encoding="utf8"))
    errors=[]
    require=lambda ok,msg:_need(errors,ok,msg)
    require(manifest.get("quality_policy_version")=="V94","V94_POLICY_VERSION_MISSING")
    require(_txt_ok(manifest.get("episode_id")),"EPISODE_ID_MISSING")
    require(_bool(manifest.get("authentic_source_reviewed")),"AUTHENTIC_SOURCE_NOT_REVIEWED")
    require(_bool(manifest.get("copyright_and_territories_checked")),"SOURCE_RIGHTS_NOT_CHECKED")
    require(_bool(manifest.get("visual_reference_reviewed")),"REFERENCE_EXAMPLES_NOT_VISUALLY_COMPARED")
    scenes=manifest.get("scenes",[])
    require(isinstance(scenes,list) and len(scenes)>=4,"INSUFFICIENT_DISTINCT_SCENES")
    if not isinstance(scenes,list):scenes=[]
    ids=set()
    faces=0
    for i,s in enumerate(scenes):
        if not isinstance(s,dict):
            errors.append(f"SCENE_{i+1}_INVALID");continue
        label=f"SCENE_{i+1}"
        event=s.get("event_id")
        require(_txt_ok(event) and event not in ids,f"{label}_REPEATED_OR_MISSING_EVENT")
        if _txt_ok(event):ids.add(event)
        require(_bool(s.get("original_source_frame_checked")),f"{label}_ORIGINAL_NOT_CHECKED")
        require(_sha_ok(s.get("original_frame_sha256")),f"{label}_SOURCE_HASH_MISSING")
        require(_bool(s.get("objects_and_people_preserved")),f"{label}_SEMANTIC_FIDELITY_NOT_REVIEWED")
        if s.get("faces_visible") is True:
            faces+=1
            require(_bool(s.get("actual_photo_image2image_generated")),f"{label}_DDCOLOR_ONLY_NOT_PHOTOREAL_FACE_RECONSTRUCTION")
            require(_bool(s.get("face_against_adjacent_original_frames_reviewed")),f"{label}_FACE_SOURCE_IDENTITY_NOT_APPROVED")
            require(_bool(s.get("eyes_skin_hair_expression_reviewed")),f"{label}_FACE_DETAILS_NOT_REVIEWED")
            require(_bool(s.get("no_face_swap_or_person_object_hallucinations")),f"{label}_FACE_OR_OBJECT_CHANGED")
            width=s.get("source_face_native_width_px")
            threshold=policy["visual_quality"]["minimum_useful_source_face_width_px"]
            readable=_number(width) and width>=threshold
            override=s.get("manually_verified_exception_better_native_source_unavailable") is True
            require(readable or override,f"{label}_FACE_HAS_TOO_FEW_NATIVE_SOURCE_PIXELS")
            require(_sha_ok(s.get("restored_face_still_sha256")),f"{label}_RESTORED_IMAGE_MISSING")
    subj=manifest.get("editorial_subject_type","")
    if subj=="people_focused":
        require(faces>=policy["visual_quality"]["minimum_recommended_face_closeups"],
                "NOT_ENOUGH_REAL_FACE_SHOTS_FOR_PEOPLE_STORY")
    vidu=manifest.get("vidu")
    if not isinstance(vidu,dict):
        errors.append("MANDATORY_VIDU_SCENE_MISSING");return errors
    vp=policy["mandatory_vidu"]
    require(_bool(vidu.get("source_crop_complete_subject_checked")),"VIDU_ANCHOR_CROPS_SUBJECT")
    require(_bool(vidu.get("start_photo_source_fidelity_checked")),"VIDU_SOURCE_ANCHOR_NOT_APPROVED")
    require(_sha_ok(vidu.get("original_frame_sha256")),"VIDU_SOURCE_HASH_MISSING")
    require(_sha_ok(vidu.get("color_anchor_sha256")),"VIDU_RESTORED_ANCHOR_HASH_MISSING")
    require(vidu.get("model")==vp["preferred_model"],"VIDU_WRONG_MODEL_REQUIRES_NEW_AUTHORIZATION")
    require(vidu.get("resolution")==vp["resolution"],"VIDU_WRONG_RESOLUTION_REQUIRES_NEW_AUTHORIZATION")
    require(vidu.get("duration_s")==vp["preferred_real_video_s"],"VIDU_WRONG_DURATION_REQUIRES_NEW_AUTHORIZATION")
    require(_sha_ok(vidu.get("prompt_sha256")),"VIDU_PROMPT_FINGERPRINT_MISSING")
    if phase=="pre_spend":
        req=policy["spending_authorization"]
        require(_bool(vidu.get("prepaid_credits_only")),"NOT_PREPAID_CREDITS")
        require(_bool(vidu.get("no_purchase_or_recharge")),"PURCHASE_OR_RECHARGE_NOT_PROHIBITED")
        require(_bool(vidu.get("immutable_ledger_reserved_before_POST")),"NO_PREPAID_LEDGER_RESERVATION")
        require(_bool(vidu.get("fresh_live_provider_balance_checked")),"LIVE_BALANCE_NOT_CHECKED")
        require(_bool(vidu.get("fresh_live_cost_quote_checked")),"LIVE_COST_NOT_CHECKED")
        amount=vidu.get("quoted_credits")
        require(_number(amount) and 0<amount<=req["maximum_credits_per_episode"],
                "VIDU_CREDITS_OVER_16_CAP_OR_UNQUOTED")
        require(_number(vidu.get("current_balance_credits")) and _number(amount) and vidu["current_balance_credits"]>=amount,
                "VIDU_INSUFFICIENT_AVAILABLE_CREDITS")
        require(vidu.get("attempts_previously_submitted")==0,"DUPLICATE_PAID_TASK_NOT_ALLOWED")
        require(_bool(vidu.get("single_post_no_retry_enforced")),"SINGLE_POST_NO_RETRY_NOT_ENFORCED")
        return errors
    if phase!="delivery":raise ValueError("Unsupported validation phase")
    require(vidu.get("provider_state")=="success","VIDU_REAL_GENERATION_NOT_SUCCESSFUL")
    require(_txt_ok(vidu.get("provider_task_id")) and bool(TASK.fullmatch(str(vidu.get("provider_task_id","")))),
            "VIDU_REAL_TASK_ID_MISSING")
    require(_sha_ok(vidu.get("actual_vidu_mp4_sha256")),"VIDU_PROVIDER_MP4_MISSING")
    require(_bool(vidu.get("provider_clip_in_final_master")),"VIDU_GENERATION_NOT_IN_FINAL_VIDEO")
    require(_number(vidu.get("real_clip_duration_s")) and vidu.get("real_clip_duration_s",0)>=vp["min_real_video_s"],
            "VIDU_MOVING_INSERT_TOO_SHORT")
    require(_bool(vidu.get("actual_motion_after_color_verified")),"VIDU_NO_LIVE_COLOR_MOTION")
    require(_bool(vidu.get("same_faces_people_objects_and_camera_approved")),"VIDU_CHANGED_PERSON_OR_OBJECT")
    require(_bool(vidu.get("no_morphs_or_extra_limbs_approved")),"VIDU_MORPHING_OR_ANATOMY_NOT_APPROVED")
    require(_bool(vidu.get("full_scene_reviewed_in_motion")),"VIDU_NOT_VISUALLY_REVIEWED")
    require(_number(vidu.get("actual_spent_credits")) and 0<vidu.get("actual_spent_credits",0)<=16,
            "VIDU_CREDIT_SPEND_UNVERIFIED_OR_OUTSIDE_CAP")
    require(vidu.get("paid_submission_count")==1,"VIDU_NOT_EXACTLY_ONE_GENERATION")
    require(_bool(manifest.get("full_video_watched_with_audio")),"FINAL_VIDEO_NOT_WATCHED")
    require(_bool(manifest.get("full_video_artistically_approved")),"FINAL_ARTISTIC_APPROVAL_MISSING")
    return errors

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",required=True)
    ap.add_argument("--phase",choices=["pre_spend","delivery"],default="delivery")
    a=ap.parse_args()
    try:
        manifest=json.loads(Path(a.manifest).read_text(encoding="utf8"))
        errors=inspect(manifest,a.phase)
    except (ValueError,KeyError,OSError,TypeError) as exc:
        errors=[type(exc).__name__ + ": " + str(exc)]
    print(json.dumps({"policy":"V94","phase":a.phase,"pass":not errors,"errors":errors},ensure_ascii=False,indent=2))
    return 0 if not errors else 2

if __name__=="__main__":raise SystemExit(main())
