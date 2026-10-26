#!/usr/bin/env python3
"""Editorial fail-closed gate for optional scene reveals. Never publishes media."""
import json,math
from pathlib import Path
VALID={"none","blueprint_to_color","detail_color","light_path","object_reveal"}
def evaluate(plan):
    errors=[];warnings=[]
    if plan.get("status")!="experiment":errors.append("Experimental scope required")
    if plan.get("source_is_master"):errors.append("Approved master cannot be overwritten")
    if not plan.get("source_image_reviewed"):errors.append("Original illustration/source requires review first")
    scenes=plan.get("scenes")
    if not isinstance(scenes,list) or not scenes:errors.append("No scene plan")
    for i,scene in enumerate(scenes or [],1):
        name=f"Scene {i}"
        effect=scene.get("effect")
        if effect not in VALID:
            errors.append(name+": unknown effect")
            continue
        if effect=="none":continue
        if plan.get("format","").startswith("artvision"):
            errors.append(name+": ArtVision must preserve authentic original artworks")
        if not str(scene.get("story_reason","")).strip():errors.append(name+": missing narrative reason")
        if not str(scene.get("narration_anchor","")).strip():errors.append(name+": missing spoken anchor")
        times=[scene.get(k) for k in ("effect_start_relative_seconds","effect_duration_seconds","shot_duration_seconds")]
        if any(type(t) not in (float,int) or not math.isfinite(t) for t in times):
            errors.append(name+": timing missing")
        elif times[0]<0 or times[1]<=0 or times[2]<=0 or times[0]+times[1]>times[2] or times[2]>30:
            errors.append(name+": effect exceeds its shot")
        if scene.get("effect_target") not in ("whole_subject","specific_object","detail","background"):
            errors.append(name+": unreviewed target")
        if not scene.get("source_image_stays_opaque"):
            errors.append(name+": do not blend unrelated artworks or shots")
    aligned=plan.get("voice_alignment",{}).get("method") in ("asr_checked","manual_checked")
    if not aligned:warnings.append("Timing still estimated: do not claim word-level synchronization")
    return {"structural_pass":not errors,"errors":errors,"warnings":warnings,
            "private_preview_allowed":not errors,"voice_alignment_verified":aligned,
            "ready_for_publication":False,"requires_human_artistic_review":True,
            "permanent_effect_rule":False}
if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("json_plan");a=p.parse_args()
    print(json.dumps(evaluate(json.loads(Path(a.json_plan).read_text(encoding="utf-8"))),ensure_ascii=False,indent=2))
