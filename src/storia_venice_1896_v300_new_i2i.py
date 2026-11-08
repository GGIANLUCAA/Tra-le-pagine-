#!/usr/bin/env python3
"""La Storia Rivive V300 — Venice 1896, source-locked Finegrain A/B and four-shot trial.

Original Wikimedia film at native 1364x1022, entirely different archival freeze moments
from existing V81 shot schedule. One free I2I call per scene, NO PAID API, NO VIDU.
This project is NOT final without a real same-scene Vidu clip and artistic approval.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import pathlib
import sys
import time

import cv2
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import storia_v80_new_york_venice as v80
import storia_rivive_v295_photo_identity_gate as gate

OUT = v80.OUT / "VENICE_1896"
OUT.mkdir(parents=True, exist_ok=True)
TRIAL = OUT / "V300_PHOTO_TRIAL.json"
RESULT = OUT / "V300_STATUS.json"

# Different source moments, same actual original 1896 moving film. 4 different scenes
# within a single continuous camera movement; DO NOT claim four camera setups.
meta = dict(v80.FILMS["VENICE_1896"])
meta["shots"] = [
    {"t":6.3, "center":632, "length":1.65, "tag":"Venice Grand Canal facade and real boat movement"},
    {"t":14.1, "center":678, "length":1.65, "tag":"Boat-level Venice architecture and canal reflections"},
    {"t":25.0, "center":705, "length":1.65, "tag":"Nineteenth century Venice water, boats and palaces"},
    {"t":36.5, "center":680, "length":1.65, "tag":"Venetian stone facades reflected in canal water"},
]

def digest(path):
    d=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):d.update(b)
    return d.hexdigest()

def measure(a):
    g=cv2.cvtColor(cv2.resize(a,(260,463)),cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(g,cv2.CV_32F).var())

def genuine_i2i(source, frames):
    from gradio_client import Client, handle_file
    dd, session, model = v80.load_dd()
    cli=Client("finegrain/finegrain-image-enhancer", verbose=False)
    good=[]
    results=[]
    for rec in frames:
        i=rec["scene"]
        bw=OUT/rec["source_frame"]
        original=cv2.imread(str(bw))
        if original is None or digest(bw)!=rec["sha256"]:
            raise RuntimeError("ARCHIVE_SOURCE_CHANGED")
        base=v80.natural_color(dd,session,bw)
        color=OUT/f"V300_SOURCE_COLOR_GUIDE_{i:02d}.png"
        cv2.imwrite(str(color),base,[cv2.IMWRITE_PNG_COMPRESSION,3])
        description=meta["shots"][i-1]["tag"]
        prompt=("Photorealistic detailed documentary COLOR image-to-image restoration of THIS EXACT "
                "1896 original Venice Grand Canal movie frame, filmed on a moving boat. "
                +description+". Keep ALL palaces, windows, boats, canals and stonework in precisely "
                "their existing positions and perspective. Natural stone, cool-blue water, sky and "
                "soft afternoon light, realistic camera-photo texture, subtle color, sharp real detail. "
                "Do not add any people, boats, buildings, animals, text or objects. "
                "Keep architectural lines exact and water geometry continuous. "
                "This remains an interpretation, not historical evidence of original colors.")
        negative=("painting, illustration, unrealistic saturated blue, neon, sepia, "
                  "invented people, invented boats, invented architecture, distorted windows, "
                  "blurred facades, changed perspective, extra limbs, synthetic lettering, "
                  "wrong geometry, grotesque faces, cartoon, monochrome")
        row={"scene":i,"source_sha256":rec["sha256"],"color_guide_sha256":digest(color),
             "color_guide":color.name,"generated_photo":False,"human_approved":False,
             "paid_calls":0,"public_release":False}
        try:
            raw=cli.predict(handle_file(str(color)),prompt,negative,
                            1896+i*3,2,1.12,.96,6,112,144,.41,18,"DDIM",
                            api_name="/process")
            item=raw[1] if isinstance(raw,(tuple,list)) and len(raw)>1 else raw
            if isinstance(item,dict):item=item.get("path")
            if not item or not pathlib.Path(str(item)).is_file():
                raise RuntimeError("PROVIDER_DID_NOT_RETURN_PHOTOGRAPH")
            candidate=cv2.imread(str(item))
            if candidate is None: raise RuntimeError("PROVIDER_FILE_NOT_IMAGE")
            candidate=cv2.resize(candidate,(720,1280),interpolation=cv2.INTER_LANCZOS4)
            fname=OUT/f"V300_TRUE_I2I_PHOTO_{i:02d}.png"
            cv2.imwrite(str(fname),candidate,[cv2.IMWRITE_PNG_COMPRESSION,3])
            q=gate.evaluate(bw,fname)
            q["model"]="finegrain/finegrain-image-enhancer"
            q["source_movie"]=meta["page"]
            contrast=measure(candidate)/max(measure(base),1)
            pixel_delta=float(np.mean(cv2.absdiff(
                cv2.resize(base,(240,427)),cv2.resize(candidate,(240,427)))))
            actual_ok=(q["ready_for_artistic_review"] and
                       q["metrics"]["structure_correlation"]>=.85 and
                       1.12<=contrast<=8.5 and pixel_delta>=3.5 and
                       q["metrics"]["mean_saturation_0_255"]<=153.0)
            q["new_detail_ratio"]=round(contrast,4)
            q["pixel_delta_vs_color_guide"]=round(pixel_delta,4)
            q["technical_new_photo_quality_pass"]=bool(actual_ok)
            (OUT/f"V300_PHOTO_QA_{i:02d}.json").write_text(
                json.dumps(q,ensure_ascii=False,indent=2)+"\n")
            row.update({"generated_photo":True,"photo_sha256":digest(fname),
                        "structure":q["metrics"]["structure_correlation"],
                        "detail_ratio":round(contrast,3),"sat":q["metrics"]["mean_saturation_0_255"],
                        "technical_gate_pass":bool(actual_ok)})
            if not actual_ok:
                row["status"]="REJECTED_NOT_USER_STANDARD"
            else:
                good.append({**rec,"photo_file":fname.name,"photo_sha256":digest(fname),
                             "geom_corr":round(q["metrics"]["structure_correlation"],3),
                             "sat":round(q["metrics"]["mean_saturation_0_255"],2),
                             "model":"REAL_FREE_FINEGRAIN_IMAGE_TO_IMAGE",
                             "new_detail_generation":True,
                             "source_locked_semantic_review":"PENDING_HUMAN"})
                row["status"]="GENUINE_I2I_TECHNICAL_QA_PASS_ARTISTIC_REVIEW_PENDING"
        except Exception as exc:
            row["status"]="PROVIDER_OR_IMAGE_REJECTED"
            row["error_type"]=type(exc).__name__
            row["error_summary"]=str(exc)[:220]
        results.append(row)
        TRIAL.write_text(json.dumps({"photos":results,"status":"IN_PROGRESS",
                   "free_provider":True,"paid_spend":0},indent=2)+"\n")
        print("VENICE_V300_SOURCE_LOCKED_PHOTO",i,row["status"],flush=True)
        if row["status"]!="GENUINE_I2I_TECHNICAL_QA_PASS_ARTISTIC_REVIEW_PENDING":
            # No retries or wasted future calls if first controlled sample fails.
            break
    TRIAL.write_text(json.dumps({"photos":results,"status":"PASS_FOUR_I2I" if len(good)==4 else "STOP_QUALITY_OR_QUOTA",
                    "free_provider":True,"paid_spend":0},indent=2)+"\n")
    return good

def main():
    state={"project":"LA_STORIA_RIVIVE","subject":"VENICE Grand Canal 1896 alternate 4 moments",
           "version":"V300","status":"STARTED","real_new_video_count":0,
           "new_generative_photo_count":0,"real_Vidu_clip_count":0,"paid_spend":0,
           "site_published":False,"social_published":False,
           "approved_final_video":False}
    try:
        source,info=v80.acquire(meta,OUT)
        state.update({"real_archival_source":True,"archive_sha256":digest(source),
                      "archive_original_raster":[info["width"],info["height"]],
                      "source_rights_italy":"PENDING"})
        records=v80.grab_stills(source,meta,OUT)
        state["actual_original_frame_count"]=len(records)
        good=genuine_i2i(source,records)
        state["new_generative_photo_count"]=len(good)
        if len(good)!=4:
            state["status"]="BLOCKED_PHOTOGRAPHIC_QUALITY_OR_FREE_QUOTA"
            return
        # Four source-frame-locked photographic restorations; the fifth Vidu is
        # not fabricated from unrelated footage. This may be a technical preview.
        v80.render(meta,source,good,OUT,info)
        movie=OUT/"LA_STORIA_RIVIVE_VENICE_1896_V80.mp4"
        if not movie.is_file():raise RuntimeError("NO_VIDEO_RENDERED")
        new=OUT/"VENICE_1896_V300_FOUR_TRUE_I2I_NO_VIDU_PREVIEW.mp4"
        movie.rename(new)
        state.update({"status":"REAL_FOUR_PHOTO_VIDEO_RENDERED_VIDU_MISSING",
                      "real_new_video_count":1,"mp4_name":new.name,
                      "mp4_bytes":new.stat().st_size,"mp4_sha256":digest(new),
                      "approved_final_video":False})
        # The previous V80 zip created by the helper refers to the old name;
        # do not declare it as the user's complete V300 delivery.
    except Exception as exc:
        state.update({"status":"SOURCE_OR_RENDER_BLOCKED","error_type":type(exc).__name__,
                      "error_summary":str(exc)[:400]})
        print("VENICE_V300_BLOCKED",type(exc).__name__,str(exc)[:250],flush=True)
    finally:
        RESULT.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n")
        print("VENICE_V300_REPORT",json.dumps(state,ensure_ascii=False),flush=True)

if __name__=="__main__":
    main()
