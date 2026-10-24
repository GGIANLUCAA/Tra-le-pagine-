#!/usr/bin/env python3
"""ArtVision permanent NO GHOSTING gate (24 Oct 2026).

Reject scene-to-scene image blending. Audio fades are permitted; fade-through-black
is permitted only when no frame contains two simultaneous pictures.
This is a *recipe/source-code* preflight, not a substitute for inspecting real frames.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

ALLOWED={"hard_cut","hard_cut_only","match_cut_no_overlap","geometric_match_cut_no_overlap","fade_through_black_no_overlap","locked_hold"}
BANNED={"crossfade","xfade","dissolve","dissolve_overlap","image_blend","double_exposure","alpha_overlay","ghost_background","overlay_alpha"}
BAD_SOURCE=(r"Image\.blend\s*\(",r"cv2\.addWeighted\s*\(",r"\bxfade\s*=",r"blend=all_expr=",r"\balpha\s*=\s*0\.")
def check_recipe(obj:dict)->list[str]:
    errors=[]
    p=obj.get("visual_transition_policy",{})
    if p.get("image_opacity")!=1.0:errors.append("Image opacity must be 1.0")
    if p.get("max_simultaneous_source_images")!=1:errors.append("Maximum simultaneous source images must be 1")
    if p.get("frames_with_two_visuals")!=0:errors.append("Even a single overlapped frame is forbidden")
    if float(obj.get("crossfade_seconds",0) or 0)>0:errors.append("Crossfade duration must be zero")
    if float(obj.get("overlap_frames",0) or 0)>0:errors.append("Scene overlap must be zero frames")
    trans=obj.get("transition_style")
    if trans and trans.lower() not in ALLOWED:errors.append("Forbidden transition_style: "+str(trans))
    for x in obj.get("transitions",[]):
        kind=str(x.get("type","")).lower()
        if kind not in ALLOWED:errors.append("Forbidden transition "+kind)
        if float(x.get("overlap_frames",0) or 0)>0:errors.append("Overlapping transition at "+str(x.get("at","?")))
    if obj.get("transition_style","").lower() in BANNED:errors.append("No image crossfades")
    return errors

def check_source(source:str)->list[str]:
    return ["Unsafe visual blending expression: "+pattern for pattern in BAD_SOURCE if re.search(pattern,source,flags=re.I)]

def main():
    ap=argparse.ArgumentParser(description="Block ghosting/overlapping images in ArtVision scene transitions")
    ap.add_argument("--manifest",required=True,type=Path)
    ap.add_argument("--source-file",type=Path,action="append")
    args=ap.parse_args()
    errors=check_recipe(json.loads(args.manifest.read_text(encoding="utf-8")))
    for path in args.source_file or []:
        errors.extend(f"{path}: {problem}" for problem in check_source(path.read_text(encoding="utf-8")))
    if errors:
        print("BLOCKED: ArtVision no-ghosting gate")
        for e in errors:print(" -",e)
        raise SystemExit(2)
    print("PASSED: each frame belongs to one opaque visual; no scene overlap declared.")
    print("Review 0/1/3/5/7 seconds and ALL transition boundaries in the final MP4.")
if __name__=="__main__":main()
