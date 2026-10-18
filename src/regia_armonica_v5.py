#!/usr/bin/env python3
"""Tra le Pagine V5: restrained shot grading and editorial edit guardrails.
No network calls, downloads or AI models. Uses Pillow, numpy and OpenCV.
Color continuity is OPTIONAL: gentle CIELAB adaptation limited to 4/3/3
Lab units and only between scenes sharing an explicit mood.
Inspired by Reinhard color transfer; deliberately avoids aggressive matching.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageOps

STRONG={"sketch_paint","brush_reveal"}
MOODS={"neutral","warm","cool","dusk"}

def read_plan(config_path):
    if config_path is not None and Path(config_path).exists():
        return json.loads(Path(config_path).read_text(encoding="utf-8"))
    return {}

def check_plan(config, count):
    seen=set(); strong=[]; extras=[]
    for shot in config.get("scenes",[]):
        cue=shot.get("cue")
        if type(cue) is not int or cue<0 or cue>=count or cue in seen:
            raise ValueError(f"Invalid/duplicated scene cue: {cue}")
        seen.add(cue)
        if shot.get("mood","neutral") not in MOODS:
            raise ValueError("Unknown color mood")
        if shot.get("effect") in STRONG and shot.get("postfx") not in (None,"off"):
            raise ValueError(f"Do not stack a painting reveal with another filter in cue {cue}")
        if shot.get("effect") in STRONG or shot.get("postfx") not in (None,"off"):
            if not str(shot.get("reason","")).strip():
                raise ValueError(f"Missing storytelling reason for strong effect in cue {cue}")
        if shot.get("effect") in STRONG:strong.append(cue)
        if shot.get("postfx") not in (None,"off"):extras.append(cue)
    if len(strong)>3 or len(extras)>4:
        raise ValueError("Effects overused: maximum 3 paint reveals and 4 filters")
    if any(b==a+1 for a,b in zip(sorted(strong),sorted(strong)[1:])):
        raise ValueError("Back-to-back painting reveals are repetitive")
    if any(b==a+1 for a,b in zip(sorted(extras),sorted(extras)[1:])):
        raise ValueError("Back-to-back postprocessing filters are distracting")
    return {"painting_reveals":len(strong),"additional_filters":len(extras)}

def lab_mean(img):
    import cv2
    reduced=np.asarray(img.resize((160,284),Image.Resampling.BILINEAR).convert("RGB"))
    lab=cv2.cvtColor(reduced,cv2.COLOR_RGB2LAB).astype(np.float32)
    return lab.reshape(-1,3).mean(axis=0)

def match_gently(image,original_mean,target_mean):
    """Minimal Lab shift; no change to contrast, contours, anatomy or exposure."""
    import cv2
    rgb=np.asarray(image.convert("RGB"))
    shift=np.clip((target_mean-original_mean)*0.15,[-4,-3,-3],[4,3,3]).round().astype(np.int16)
    if not np.any(shift):
        return image.copy(),shift.tolist()
    lab=cv2.cvtColor(rgb,cv2.COLOR_RGB2LAB).astype(np.int16)
    lab=np.clip(lab+shift[None,None,:],0,255).astype(np.uint8)
    return Image.fromarray(cv2.cvtColor(lab,cv2.COLOR_LAB2RGB),"RGB"),shift.tolist()

def contact_sheet(paths,moods,dest):
    w,h=160,284;cols=min(4,len(paths));rows=(len(paths)+cols-1)//cols
    out=Image.new("RGB",(cols*w,rows*(h+28)),(13,38,43))
    d=ImageDraw.Draw(out)
    for i,path in enumerate(paths):
        im=ImageOps.fit(Image.open(path).convert("RGB"),(w,h),method=Image.Resampling.LANCZOS)
        x,y=(i%cols)*w,(i//cols)*(h+28)
        out.paste(im,(x,y));d.text((x+7,y+h+5),f"{i+1:02} · {moods[i]}",fill=(238,219,187))
    dest=Path(dest);dest.parent.mkdir(parents=True,exist_ok=True)
    out.save(dest,quality=89)

def prepare(images,tmp,config_path=None,report_path=None,contact_path=None):
    """Review all shots; grade only clear color outliers within the SAME mood.
    Returns list of ORIGINAL paths unless optional grading is explicitly enabled.
    """
    images=[Path(p) for p in images]
    if not images:raise ValueError("Missing image sequence")
    config=read_plan(config_path)
    budget=check_plan(config,len(images))
    grade=config.get("quality",{}).get("color_cohesion")=="gentle"
    moods=["neutral"]*len(images)
    for item in config.get("scenes",[]):
        moods[item["cue"]]=item.get("mood","neutral")
    originals=[Image.open(p).convert("RGB") for p in images]
    means=np.asarray([lab_mean(p) for p in originals])
    targets={}
    for mood in MOODS:
        indices=[i for i,m in enumerate(moods) if m==mood]
        if len(indices)>=2:
            targets[mood]=np.median(means[indices],axis=0)
    tmp=Path(tmp);tmp.mkdir(parents=True,exist_ok=True)
    adjusted=[]; rows=[]
    for i,im in enumerate(originals):
        delta=float(np.linalg.norm(means[i]-targets[moods[i]])) if moods[i] in targets else 0.
        changed=False; shift=[0,0,0]
        out=images[i]
        if grade and moods[i] in targets and delta>14.0:
            colored,shift=match_gently(im,means[i],targets[moods[i]])
            if any(shift):
                out=tmp/f"graded_{i:02}.jpg"
                colored.save(out,quality=94,subsampling=0)
                changed=True
        adjusted.append(out)
        rows.append({"cue":i,"mood":moods[i],"color_distance":round(delta,1),
                     "light_grade_applied":changed,"Lab_shift":shift})
    summary={"version":"V5","effect_budget":budget,
             "grading":"gentle" if grade else "off",
             "rule":"Retain original faces/textures. Lab shift bounded (4,3,3). Different moods never matched.",
             "scenes":rows,
             "human_review_required":True}
    if report_path:
        Path(report_path).write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    if contact_path:contact_sheet(adjusted,moods,contact_path)
    return adjusted,summary
