#!/usr/bin/env python3
"""ArtVision 4×1 V68: reusable, versioned planning recipes from the Socrates pilot.

This is a planning/preflight tool, NOT a renderer and NOT a V25 approval service.
Never overwrites the global preset, existing masters, or a destination file.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PRESET=ROOT/"config/artvision_four_variants_presets_v68.json"
VARIANTS=("critico_standard","critico_museum","cinema_standard","cinema_museum")

def digest_bytes(data: bytes)->str:
    return hashlib.sha256(data).hexdigest()

def load_preset(preset_path=PRESET):
    p=Path(preset_path)
    value=json.loads(p.read_text(encoding="utf-8"))
    if value.get("schema")!="artvision-4x1-reusable-preset-v68":
        raise ValueError("Unknown ArtVision preset version")
    if value.get("invariants",{}).get("required_variant_ids")!=list(VARIANTS):
        raise ValueError("Exactly FOUR independent ArtVision slots required")
    if set(value.get("defaults",{}).get("slots",{}))!=set(VARIANTS):
        raise ValueError("Preset has missing or duplicate variant definitions")
    return value

def build_recipe(artwork_id, title, artist, source_url="", preset_path=PRESET):
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{4,100}",artwork_id):
        raise ValueError("Artwork ID must be stable lower-case slug")
    if not title.strip() or not artist.strip():
        raise ValueError("Exact artwork title and artist are required")
    preset=load_preset(preset_path)
    return {
      "schema":"artvision-artwork-recipe-v68",
      "artwork":{"id":artwork_id,"title":title.strip(),"artist":artist.strip(),
                 "primary_source":source_url.strip()},
      "creative_baseline":{"preset_id":preset["preset_id"],
                           "preset_version":preset["version"],
                           "preset_sha256":digest_bytes(Path(preset_path).read_bytes()),
                           "reference_feedback_scope":preset["feedback"]["scope"]},
      "invariants":copy.deepcopy(preset["invariants"]),
      "creative":copy.deepcopy(preset["defaults"]),
      "required_evidence":{k:{"status":"pending","sources":[]} for k in preset["per_work_evidence_required"]},
      "storyboards":{v:{"status":"draft","shots":[],"direction_notes":""} for v in VARIANTS},
      "variants":{v:{"status":"not_rendered","mp4_sha256":None,"mp4_bytes":None,
                     "source_voice_sha256":None,"voice_script_sha256":None,
                     "full_speed_human_review":"pending","V25_approved":False,
                     "private_archive_import_verified":False} for v in VARIANTS},
      "production":{"status":"planning_only","render_eligible":False,
                    "social_publishing_authorized":False,"paid_video_ai_authorized":False,
                    "single_owner_required":True,"source_code_commit":"PIN_ON_ACTUAL_RENDER"},
      "change_log":[]
    }

def coerce(value,spec):
    t=spec["type"]
    if t=="enum":
        if value not in spec["values"]:
            raise ValueError("Unsupported choice: "+repr(value)+", valid: "+", ".join(spec["values"]))
        return value
    if t=="int":
        if isinstance(value,bool) or not re.fullmatch(r"-?\\d+",str(value)):
            raise ValueError("Expected integer")
        x=int(value)
    elif t=="float":
        try:x=float(value)
        except (ValueError,TypeError):raise ValueError("Expected numeric")
        if not (float("-inf")<x<float("inf")):raise ValueError("Non-finite number")
    else:raise ValueError("Unknown rule type")
    if not spec["min"]<=x<=spec["max"]:
        raise ValueError("Value outside safe range: "+str(spec["min"])+" .. "+str(spec["max"]))
    return x

def change_creative(recipe,field,value,reason,preset_path=PRESET):
    if recipe.get("schema")!="artvision-artwork-recipe-v68":
        raise ValueError("Not an ArtVision V68 artwork recipe")
    if len(reason.strip())<8:
        raise ValueError("Provide reason for every production setting change")
    preset=load_preset(preset_path)
    spec=preset["adjustable_fields"].get(field)
    if not spec:raise ValueError("Immutable or unknown ArtVision setting: "+field)
    x=coerce(value,spec)
    changed=copy.deepcopy(recipe)
    path=field.split(".")
    target=changed["creative"]
    for segment in path[:-1]:
        target=target[segment]
    before=target[path[-1]]
    target[path[-1]]=x
    # Source-accurate frames cannot be silently recolored into fictional frames.
    museum=changed["creative"]["museum"]
    if museum["frame_finish"]!="match_source" and museum["frame_mode"]!="declared_creative_alternative":
        raise ValueError("A non-original frame finish requires frame_mode=declared_creative_alternative")
    changed["change_log"].append({
        "number":len(changed["change_log"])+1,
        "field":field,"previous":before,"new":x,"reason":reason.strip(),
        "requested_scope":"THIS_ARTWORK_ONLY",
        "source_preset_unchanged":True
    })
    changed["production"]["status"]="planning_only"
    changed["production"]["render_eligible"]=False
    return changed

def inspect(recipe,preset_path=PRESET,root=ROOT,require_render=False):
    preset=load_preset(preset_path)
    errors=[]
    if recipe.get("schema")!="artvision-artwork-recipe-v68":
        errors.append("recipe schema mismatch")
        return errors
    if list(recipe.get("variants",{}))!=list(VARIANTS):
        errors.append("four slot identities/order missing")
    if set(recipe.get("storyboards",{}))!=set(VARIANTS):
        errors.append("four separate storyboards missing")
    if recipe.get("invariants")!=preset["invariants"]:
        errors.append("immutable ArtVision rules have been changed")
    museum=recipe.get("creative",{}).get("museum",{})
    if museum.get("frame_finish")!="match_source" and museum.get("frame_mode")!="declared_creative_alternative":
        errors.append("creative frame must declare reconstruction")
    for key,rule in preset["adjustable_fields"].items():
        obj=recipe.get("creative",{})
        try:
            for k in key.split("."):obj=obj[k]
            coerce(obj,rule)
        except (KeyError,ValueError,TypeError) as exc:
            errors.append("invalid override/default "+key+": "+str(exc))
    hashes=[]
    for v in VARIANTS:
        state=recipe.get("variants",{}).get(v,{})
        if state.get("status")=="rendered_needs_review" or state.get("status")=="approved_for_final_delivery":
            h=state.get("mp4_sha256")
            if not isinstance(h,str) or not re.fullmatch("[a-f0-9]{64}",h) or not isinstance(state.get("mp4_bytes"),int) or state["mp4_bytes"]<=0:
                errors.append(v+": rendered status without real MP4 SHA/bytes")
            else: hashes.append(h)
        if state.get("V25_approved") is True and state.get("full_speed_human_review")!="passed":
            errors.append(v+": human approval cannot replace full-speed QA")
    if len(set(hashes))!=len(hashes):
        errors.append("Two different variants reuse the SAME MP4 hash")
    critico=recipe.get("variants",{})
    a,b=(critico.get("critico_standard",{}),critico.get("critico_museum",{}))
    if a.get("status")!="not_rendered" or b.get("status")!="not_rendered":
        wav1,wav2=a.get("source_voice_sha256"),b.get("source_voice_sha256")
        script1,script2=a.get("voice_script_sha256"),b.get("voice_script_sha256")
        if a.get("status") in ("rendered_needs_review","approved_for_final_delivery") and b.get("status") in ("rendered_needs_review","approved_for_final_delivery"):
            if not wav1 or wav1!=wav2 or not script1 or script1!=script2:
                errors.append("Both Critico must share the exact same verified voice WAV/script hash")
    if require_render:
        # Legacy pilot freeze also applies to scripts generated by this new preset system.
        sys.path.insert(0,str(Path(root)/"src"))
        from artvision_pilot_guard_v58 import enforce_pilot_project
        for variant in VARIANTS:
            try:enforce_pilot_project({"serial_mode":"artvision_4x1",
                       "topic":recipe["artwork"]["title"],
                       "artvision_4x1_variant":variant},root)
            except ValueError as exc:errors.append(str(exc));break
        missing=[k for k,e in recipe.get("required_evidence",{}).items()
                 if e.get("status")!="verified" or not e.get("sources")]
        if missing:errors.append("Missing verified source/rights/QA evidence: "+", ".join(missing))
        if any(v.get("status")=="draft" or not v.get("shots") for v in recipe["storyboards"].values()):
            errors.append("All four actual storyboards required before rendering")
        if recipe["production"].get("source_code_commit")=="PIN_ON_ACTUAL_RENDER":
            errors.append("Pin exact source-code commit before rendering")
    return errors

def write_new(path,data):
    p=Path(path)
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("x",encoding="utf-8") as f:
        f.write(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
    return p

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    actions=ap.add_subparsers(dest="cmd",required=True)
    new=actions.add_parser("init",help="Create a new planning-only four-video artwork recipe")
    for name in ("id","title","artist","out"):new.add_argument("--"+name,required=True)
    new.add_argument("--source-url",default="")
    tune=actions.add_parser("set",help="Create a revised per-artwork recipe; never edit source")
    for name in ("recipe","field","value","reason","out"):tune.add_argument("--"+name,required=True)
    check=actions.add_parser("validate",help="Check recipe structure; optional render eligibility")
    check.add_argument("--recipe",required=True)
    check.add_argument("--for-render",action="store_true")
    args=ap.parse_args()
    if args.cmd=="init":
        r=build_recipe(args.id,args.title,args.artist,args.source_url)
        write_new(args.out,r)
        print("RECIPE_DRAFT_CREATED: "+args.out+" (NO VIDEO RENDERED)")
    elif args.cmd=="set":
        r=json.loads(Path(args.recipe).read_text(encoding="utf-8"))
        result=change_creative(r,args.field,args.value,args.reason)
        write_new(args.out,result)
        print("PER_WORK_OVERRIDE_SAVED: "+args.out+" (BASELINE UNCHANGED)")
    else:
        r=json.loads(Path(args.recipe).read_text(encoding="utf-8"))
        errors=inspect(r,require_render=args.for_render)
        print(json.dumps({"status":"blocked" if errors else "planning_structure_valid",
               "render_claim":False,"errors":errors},ensure_ascii=False,indent=2))
        if errors:raise SystemExit(2)

if __name__=="__main__":
    main()
