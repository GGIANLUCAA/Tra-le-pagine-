#!/usr/bin/env python3
"""V273 Delhi 1910: one real source-locked CPU I2I on genuine V272 frame_06.

Use 1 no-cost local diffusers InstructPix2Pix call; preserve source objects.
Not a completed episode, no Vidu credits, rights or artistic approval.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
from PIL import Image
import storia_rivive_v257_fiesole_third_source_i2i as engine

EPISODE="delhi_ruins_1910_v217"
FILM_SHA="0a0de7b032cdb19e34d4dac5a6efca02dfa4b00260411aa82290c54b2899f278"
SHOT=3
FRAME="frame_06.png"
FRAME_SHA="d6a6f21789093f971cff0adfa4259511a24875eb73753b8c7f177b882762f16e"
FRAME_TIME=104.345
FRAME_ORDER=["frame_01.png","frame_04.png","frame_06.png","frame_11.png","frame_12.png"]
MODEL="timbrooks/instruct-pix2pix"
PROMPT=(
    "Realistic full-color documentary photograph of Delhi India, 1910. "
    "Preserve exactly the stone temple pillars, existing people, clothing and "
    "camera view of the input. Sunlit warm beige sandstone, green trees, natural "
    "earth tones and pale blue sky, realistic skin and white cotton garments. "
    "Natural photographic detail. No extra people, monuments or objects."
)
SEED=273
OUTPUT_NAME="DELHI_1910_SHOT03_ONE_TRUE_I2I_CANDIDATE_NOT_FINAL.png"
REPORT_NAME="DELHI_V273_REAL_I2I_TRIAL_NOT_FINAL.json"

def sha(data: bytes)->str:
    return hashlib.sha256(data).hexdigest()

def verify_input(scout:Path,selection:Path,original:Path)->dict:
    s=json.loads(scout.read_text(encoding="utf-8"))
    m=json.loads(selection.read_text(encoding="utf-8"))
    if (s.get("source_page")!="https://commons.wikimedia.org/wiki/File:Ruins_of_Delhi_(1910).webm"
        or s.get("original_sha256")!=FILM_SHA
        or s.get("status")!="REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW"):
        raise ValueError("V273_FILM_SOURCE_NOT_VERIFIED")
    if (m.get("status")!="FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW"
        or [v.get("filename") for v in m.get("preselected",[])]!=FRAME_ORDER
        or len(set(FRAME_ORDER))!=5
        or len(m.get("candidate_segment_times_s",[]))!=5
        or abs(m["candidate_segment_times_s"][SHOT-1]-FRAME_TIME)>0.005
        or m.get("approved_restored_photos")!=0
        or m.get("publish_permitted") is not False):
        raise ValueError("V273_FIVE_SOURCE_SHOTS_CHANGED_OR_NOT_APPROVED")
    if (not original.is_file() or original.is_symlink() or original.name!=FRAME
        or engine.sha(original)!=FRAME_SHA):
        raise ValueError("V273_ORIGINAL_FRAME_SHA_CHANGED")
    with Image.open(original) as im:
        if im.format!="PNG" or im.size!=(1920,1080):
            raise ValueError("V273_ORIGINAL_DIMENSIONS_OR_TYPE")
        im.verify()
    return {"film_sha256":FILM_SHA,"original_frame_sha256":FRAME_SHA,
            "source_time_s":FRAME_TIME,"source_shot":SHOT}

def generate(src:Path,out:Path)->None:
    import torch
    from diffusers import StableDiffusionInstructPix2PixPipeline
    torch.set_num_threads(min(4,os.cpu_count() or 2))
    pipeline=StableDiffusionInstructPix2PixPipeline.from_pretrained(
        MODEL,torch_dtype=torch.float32,use_safetensors=True)
    pipeline.to("cpu")
    pipeline.enable_attention_slicing()
    with Image.open(src) as im:
        picture=im.convert("RGB").resize(engine.MODEL_DIMS)
    g=torch.Generator(device="cpu").manual_seed(SEED)
    with torch.inference_mode():
        photo=pipeline(prompt=PROMPT,image=picture,generator=g,
                       num_inference_steps=20,guidance_scale=9.0,
                       image_guidance_scale=2.2).images[0]
    if not isinstance(photo,Image.Image) or photo.size!=engine.MODEL_DIMS:
        raise ValueError("V273_INFERENCE_NO_REAL_PHOTO")
    photo.save(out)

def run(scout:Path,selection:Path,original:Path,out:Path,offline=False,fn=None)->dict:
    info=verify_input(scout,selection,original)
    out.mkdir(parents=True,exist_ok=True)
    source_crop=out/"V273_ACTUAL_DELHI_ORIGINAL_CROP.png"
    engine.SOURCE_SHA=FRAME_SHA
    engine.crop_source(original,source_crop)
    report={"version":"V273_DELHI_REAL_CPU_I2I_REVIEW_ONLY",
            "source_page":"https://commons.wikimedia.org/wiki/File:Ruins_of_Delhi_(1910).webm",
            "episode":EPISODE,"source_metadata":info,"model":MODEL,
            "seed":SEED,"prompt_sha256":sha(PROMPT.encode()),
            "source_crop_sha256":engine.sha(source_crop),
            "source_crop_pixel_dimensions":[608,1080],
            "generated_photos":0,"vidu_clips":0,"paid_credit_spend":0,
            "artistically_approved":False,"italian_rights_verified":False,
            "publish_allowed":False,"new_finished_mp4_zip":0,
            "status":"SOURCE_LOCKED_ONLY_NO_GENERATION"}
    rp=out/REPORT_NAME
    rp.write_text(json.dumps(report,indent=2)+"\n")
    if offline:return report
    image=out/OUTPUT_NAME
    try:
        (fn or generate)(source_crop,image)
        details=engine.inspect_candidate(source_crop,image)
        report.update(details)
        report["generated_photos"]=1
        engine.make_comparison(source_crop,image,out/"V273_REAL_DELHI_BEFORE_AFTER_QA_ONLY.jpg")
        report["status"]="ONE_TRUE_SOURCE_LOCKED_I2I_NEEDS_ARTISTIC_QA_NOT_FINAL"
    except Exception as exc:
        report["status"]="NO_VALID_I2I_GENERATED_NOT_FINAL"
        report["error_type"]=type(exc).__name__
        raise
    finally:
        rp.write_text(json.dumps(report,indent=2)+"\n")
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--scout",required=True,type=Path)
    p.add_argument("--selection",required=True,type=Path)
    p.add_argument("--original",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--offline",action="store_true")
    a=p.parse_args()
    result=run(a.scout,a.selection,a.original,a.out,a.offline)
    print(result["status"],"FINAL_0_OF_4")
