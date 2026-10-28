#!/usr/bin/env python3
"""ArtVision 4x1: offline storyboard gate. Never renders or spends credits."""
import argparse
import json
from pathlib import Path

VARIANTS = {
    "critico_standard": ("critico", "standard"),
    "critico_museum": ("critico", "museum"),
    "cinema_standard": ("cinema", "standard"),
    "cinema_museum": ("cinema", "museum"),
}

def validate(plan):
    errors = []
    def need(ok, msg):
        if not ok: errors.append(msg)
    need(isinstance(plan, dict), "Plan must be an object")
    if not isinstance(plan, dict): return errors
    d = plan.get("emotional_direction") or {}
    need(bool(str(d.get("central_tension") or "").strip()), "Missing central_tension")
    feelings = d.get("intended_feeling")
    need(isinstance(feelings, list) and 1 <= len(feelings) <= 2 and all(isinstance(x, str) and x.strip() for x in feelings), "Specify 1-2 intended feelings")
    details = d.get("evidence_details")
    details = details if isinstance(details, list) else []
    need(len(details) >= 3, "At least three meaningful artwork details required")
    ids = set()
    for i, item in enumerate(details):
        item = item if isinstance(item, dict) else {}
        for field in ("id", "location", "observation", "significance", "image_source"):
            need(bool(str(item.get(field) or "").strip()), f"detail {i}: missing {field}")
        if item.get("id"): ids.add(item["id"])
        need(item.get("claim_type") in ("documented", "interpretation"), f"detail {i}: distinguish fact and interpretation")
    order = d.get("reveal_order")
    need(isinstance(order, list) and len(order) >= 3 and all(x in ids for x in order), "reveal_order must reference 3+ valid details")
    need(bool(str(d.get("wow_justification") or "").strip()), "Missing meaningful reveal")
    variants = plan.get("variants") or {}
    need(isinstance(variants, dict), "variants must be an object")
    if not isinstance(variants, dict): return errors
    for name, (fmt, mode) in VARIANTS.items():
        v = variants.get(name)
        need(isinstance(v, dict), f"Missing {name}")
        if not isinstance(v, dict): continue
        need(v.get("format") == fmt and v.get("mode") == mode, f"{name}: wrong format/mode")
        scenes = v.get("scenes")
        need(isinstance(scenes, list) and len(scenes) >= 2, f"{name}: need >=2 planned scenes")
        for j, scene in enumerate(scenes if isinstance(scenes, list) else []):
            scene = scene if isinstance(scene, dict) else {}
            need(scene.get("detail_id") in ids, f"{name} scene {j}: unknown detail")
            for field in ("purpose", "movement", "emotional_effect"):
                need(bool(str(scene.get(field) or "").strip()), f"{name} scene {j}: missing {field}")
            if fmt == "critico":
                need(bool(str(scene.get("spoken_line") or "").strip()), f"{name} scene {j}: missing spoken line")
        if mode == "museum":
            m = v.get("museum") or {}
            for field in ("dimensions_source", "frame_status", "entrance_plan", "exit_same_gallery_plan"):
                need(bool(str(m.get(field) or "").strip()), f"{name}: missing museum {field}")
            need(isinstance(m.get("width_cm"), (int, float)) and m["width_cm"] > 0 and isinstance(m.get("height_cm"), (int, float)) and m["height_cm"] > 0, f"{name}: missing verified dimensions")
    for a,b in (("critico_standard","critico_museum"),):
        va,vb=variants.get(a),variants.get(b)
        if isinstance(va,dict) and isinstance(vb,dict):
            sa=[x.get("spoken_line") for x in va.get("scenes",[]) if isinstance(x,dict)]
            sb=[x.get("spoken_line") for x in vb.get("scenes",[]) if isinstance(x,dict)]
            need(sa == sb, "Critico pair must preserve the exact same narration")
    return errors

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("plan",type=Path)
    args=parser.parse_args()
    errors=validate(json.loads(args.plan.read_text(encoding="utf-8")))
    print(json.dumps({"passed":not errors,"errors":errors},ensure_ascii=False,indent=2))
    raise SystemExit(1 if errors else 0)

if __name__=="__main__": main()
