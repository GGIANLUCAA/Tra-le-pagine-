#!/usr/bin/env python3
"""V64: fail-closed PHOTO REALISM + ARCHIVAL FIDELITY editorial gate.

This is NOT a face-recognition model, and it does NOT certify that generated
facial details are historically accurate. It prevents misleading '4K-like final'
declarations when restoration evidence is absent or people change.
Usage: python src/storia_rivive_quality_policy_v64.py episode.json
"""
import argparse,json,hashlib,os
from pathlib import Path

MIN_FACE_SHORT_EDGE=72  # Editorial heuristic, NOT a scientific biometrics threshold.
PREFERRED_FACE_SHORT_EDGE=100
MIN_CROP_PIXELS=700_000  # Acquiring better source rather than inventing detail.
ALLOWED_RIGHTS={"CC0","CC0 1.0","PUBLIC_DOMAIN","PDM"}
GENERATION_MODES={"reference_constrained_img2img","multi_frame_reference_constrained_img2img"}

def validate(episode):
    failures=[];warnings=[]
    def need(ok, reason):
        if not ok:failures.append(reason)
    need(episode.get("format")=="storia_rivive","Only 'storia_rivive' eligible")
    need(not episode.get("auto_publish"),"No unapproved publication")
    need(not episode.get("paid_credits_consumed"),"No unauthorized paid generation")
    need(episode.get("release_preset")=="reference_photo_freeze","Wrong preset")
    need(episode.get("rights",{}).get("original_license") in ALLOWED_RIGHTS,
         "Original film must be verified PD or CC0")
    shots=episode.get("shots",[])
    need(isinstance(shots,list) and 1<=len(shots)<=12,"Need individually reviewed shots")
    if not isinstance(shots,list):shots=[]
    for i,shot in enumerate(shots,1):
        prefix=f"SCENE_{i}: "
        size=shot.get("native_crop_size_px",[])
        if isinstance(size,list) and len(size)==2 and all(isinstance(x,(int,float)) and x>0 for x in size):
            w,h=size
            if w*h<MIN_CROP_PIXELS:
                need(False,prefix+f"source crop {w}x{h} too small for reference-grade faithful photo; seek better scan")
            if w<h and w<600:
                warnings.append(prefix+"vertical crop width under 600px: facial microdetail likely sparse")
        else:
            need(False,prefix+"source crop dimensions missing")
        need(shot.get("keyframe_provenance_verified") is True,prefix+"missing exact historic frame/timecode hash")
        need(shot.get("moving_archive_scene") is True,prefix+"no genuine moving original")
        need(shot.get("frame_source_license_verified") is True,prefix+"archive source not verified")
        need(shot.get("masks_preserve_original_people_objects") is True,
             prefix+"no original object/person geometry comparison")
        faces=shot.get("faces",[])
        need(isinstance(faces,list) and len(faces)>=1,prefix+"must document at least one readable face")
        for j,face in enumerate(faces if isinstance(faces,list) else [],1):
            short=face.get("source_short_edge_px",0)
            need(isinstance(short,(int,float)) and short>=MIN_FACE_SHORT_EDGE,
                 prefix+f"face_{j} is too small in archival source for faithful lifelike detail")
            if isinstance(short,(int,float)) and short < PREFERRED_FACE_SHORT_EDGE:
                warnings.append(prefix+f"face_{j} below preferred {PREFERRED_FACE_SHORT_EDGE}px")
            need(face.get("same_person_shape_reviewed") is True,
                 prefix+f"face_{j} identity/geometry not reviewed")
            need(face.get("no_age_or_ethnicity_changed") is True,
                 prefix+f"face_{j} demographic appearance altered/unreviewed")
        r=shot.get("restoration",{})
        need(r.get("method") in GENERATION_MODES,
             prefix+"DDColor + ESRGAN is not true image-to-image photographic reconstruction")
        need(r.get("visual_face_reconstruction") is True,
             prefix+"missing face restoration/reconstruction stage")
        need(r.get("source_guidance_strength_reviewed") is True,
             prefix+"no source-identity conditioning evidence")
        need(r.get("model_weights_license_checked") is True,
             prefix+"model/weight publication license unchecked")
        need(r.get("native_4k_claim") is not True,
             prefix+"do not mislabel outputs as original 4K")
        need(r.get("photo_historically_hypothetical_disclosed") is True,
             prefix+"photo generated details must be disclosed as conjectural")
        quality=shot.get("quality_review",{})
        need(quality.get("original_v_restored_side_by_side") is True,
             prefix+"original/photo side-by-side not checked")
        need(quality.get("natural_skin_colors") is True,
             prefix+"skin palette insufficient or unchecked")
        need(quality.get("lifelike_eyes_skin_hair") is True,
             prefix+"face is not sharp and photographic or unchecked")
        need(quality.get("same_people_count") is True,
             prefix+"invented or missing people/unreviewed")
        need(quality.get("same_pose_clothes_background") is True,
             prefix+"changed pose, clothes or buildings/unreviewed")
        need(quality.get("no_synthetic_face_or_hand_artifacts") is True,
             prefix+"AI facial/hands artifacts")
        need(quality.get("actual_100_percent_mobile_crop_approved") is True,
             prefix+"not checked at phone viewing crop")
        need(quality.get("art_director_approved") is True,
             prefix+"human artistic approval not supplied")
    return {"eligible_for_reference_grade":len(failures)==0,
            "status":"REFERENCE_GRADE_REVIEWED" if not failures else "REJECT_PHOTO_FIDELITY",
            "failures":failures,"warnings":warnings,
            "important_limitation":"Unobserved historical facial microdetails can never be proven true from a degraded input."}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--output")
    args=ap.parse_args()
    plan=json.loads(Path(args.plan).read_text(encoding="utf8"))
    result=validate(plan)
    printed=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if args.output:Path(args.output).write_text(printed,encoding="utf8")
    print(printed,end="")
    raise SystemExit(0 if result["eligible_for_reference_grade"] else 2)

if __name__=="__main__":main()
