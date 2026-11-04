#!/usr/bin/env python3
"""V283 — one real source-locked fifth photo for authentic Delhi 1910 Vidu anchor.

Output is only a PHOTO candidate for visual approval; NEVER a Vidu video,
never permission to spend credits or publish. Works with existing V278 open
DDColor+Finegrain method. No new billed API, one free inference attempt only.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps,ImageEnhance
import storia_rivive_v278_delhi_four_ddcolor_finegrain as v278

FRAME="frame_12.png"
FRAME_SHA="28a71dff0d65a4529a946fbe1d531626c70dca389d344e4d17f7646022fc8ca2"
X=750
BBOX=(X,0,X+608,1080)
TIME=218.176
PROMPT=(
    "Natural modern documentary COLOR photograph faithfully restored from the "
    "exact original Delhi India 1910 historical film image. "
    "The two real men in traditional turbans and white period cotton clothes stand "
    "beside a small herd of real horned bovine cattle on a dusty country path. "
    "Keep the exact number, placement, bodies, horns, heads, limbs, garments, "
    "people, historic stone arch and foliage visible in the source. "
    "Photographically realistic subtle dark and light cowhide, natural brown skin, "
    "white cotton, green shrubs and warm neutral earth. "
    "No extra cattle, no additional people, no modern objects, no artistic "
    "recomposition, no text or watermark, no sepia tint."
)

def sha(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def source_check(src:Path)->None:
    if not src.is_file() or src.is_symlink() or src.name!=FRAME or sha(src)!=FRAME_SHA:
        raise ValueError("V283_DELHI_SOURCE_FIFTH_FRAME_SHA_INVALID")
    with Image.open(src) as im:
        if im.format!="PNG" or im.size!=(1920,1080):
            raise ValueError("V283_DELHI_BAD_SOURCE_SIZE")
        im.verify()

def crop_source(src:Path,target:Path)->None:
    source_check(src)
    with Image.open(src) as im:
        image=im.convert("RGB").crop(BBOX).resize((720,1280),Image.Resampling.LANCZOS)
        image.save(target,quality=95)
    with Image.open(target) as im:
        if im.size!=(720,1280):raise ValueError("V283_CROP_SIZE")

def ddcolor(src:Path,dest:Path,dd,session)->None:
    import cv2,numpy as np
    img=cv2.imread(str(src))
    if img is None or img.shape[:2]!=(1080,1920):
        raise ValueError("V283_BAD_ORIGINAL")
    reduced=cv2.resize(img,(720,576),interpolation=cv2.INTER_AREA)
    ab_small=dd.infer_ab(session,reduced)
    lab_l=dd.l_channel(img)
    ab=cv2.resize(ab_small,(1920,1080),interpolation=cv2.INTER_CUBIC)
    rgb=np.clip(cv2.cvtColor(np.dstack((lab_l,np.clip(ab*1.09,-110,110))).astype(np.float32),cv2.COLOR_LAB2RGB)*255,0,255).astype(np.uint8)
    photo=Image.fromarray(rgb[:,X:X+608]).resize((540,960),Image.Resampling.LANCZOS)
    photo=ImageEnhance.Color(photo).enhance(.90)
    photo.save(dest)

def comparison(source,base,color,output):
    board=Image.new("RGB",(3*270,525),(21,23,27));draw=ImageDraw.Draw(board)
    for i,(p,label) in enumerate(((source,"DELHI 1910 EXACT ORIGINAL"),(base,"DDCOLOR BASE ONLY"),(color,"TRUE FINEGRAIN I2I / REVIEW"))):
        with Image.open(p) as im:
            a=ImageOps.fit(im.convert("RGB"),(266,476))
            board.paste(a,(i*270+2,35))
        draw.text((i*270+4,13),label,fill="white")
    board.save(output,quality=92)

def run(source:Path,out:Path,offline=False,predict=None,make_base=None)->dict:
    source_check(source)
    out.mkdir(parents=True,exist_ok=True)
    bw=out/"DELHI_1910_SHOT05_EXACT_SOURCE_BW_FOR_VIDU_REVIEW.jpg"
    base=out/"DELHI_1910_SHOT05_DDCOLOR_ONLY_BASE.png"
    color=out/"DELHI_1910_SHOT05_FINEGRAIN_PHOTO_REVIEW_NOT_APPROVED.jpg"
    crop_source(source,bw)
    manifest={
        "episode":"delhi_ruins_1910_v217",
        "version":"V283_REAL_FIFTH_PHOTO_SOURCE_ANCHOR_NO_VIDU_YET",
        "original_source_frame_sha256":FRAME_SHA,
        "frame_filename":FRAME,"original_time_s":TIME,
        "original_crop_bbox_px":list(BBOX),
        "exact_bw_anchor_sha256":sha(bw),
        "source_page":v278.PAGE,
        "source_subject":"two people and several bovine cattle on path near ruins",
        "prompt_sha256":hashlib.sha256(PROMPT.encode()).hexdigest(),
        "model":v278.MODEL,
        "five_second_vidu_clip_generated":False,
        "vidu_credits_spent":0,
        "credit_balance_approved":False,
        "subject_reviewed_by_user":False,
        "scene5_photo_artistically_approved":False,
        "italian_rights_approved":False,
        "publication_allowed":False,
        "master_videos_finished":0,
        "status":"EXACT_ORIGINAL_FIFTH_SHOT_READY_NO_GENERATION"
    }
    report=out/"DELHI_V283_SHOT05_SOURCE_LOCKED_QA_NOT_FINAL.json"
    report.write_text(json.dumps(manifest,indent=2)+"\n")
    if offline:return manifest
    try:
        if make_base is None:
            import storia_rivive_real_ai_v60 as dd
            session,_=dd.download_model()
            ddcolor(source,base,dd,session)
        else:make_base(source,base)
        with Image.open(base) as im:
            if im.size!=(540,960):raise ValueError("V283_DDCOLOR_RASTER_CHANGED")
        generated=(predict or v278.genuine_finegrain)(base,PROMPT,218176)
        with Image.open(generated) as im:
            image=ImageOps.fit(im.convert("RGB"),(720,1280),Image.Resampling.LANCZOS)
            image.save(color,quality=95,subsampling=0)
        if color.stat().st_size<18000:raise ValueError("V283_INVALID_PHOTO_BYTES")
        stats=v278.photo_stats(bw,color)
        manifest.update(stats)
        manifest["generated_photo_sha256"]=sha(color)
        manifest["generated_photo_filename"]=color.name
        manifest["scene5_photo_generated"]=True
        manifest["status"]="ONE_REAL_PHOTO_SOURCE_LOCKED_NEEDS_ACTUAL_ARTISTIC_REVIEW_NO_VIDU"
        comparison(bw,base,color,out/"DELHI_V283_ACTUAL_ORIGINAL_VS_NEW_PHOTO_QA.jpg")
    except Exception as exc:
        manifest["status"]="V283_PHOTO_FAILED_NO_VIDU_NO_FINAL"
        manifest["error_type"]=type(exc).__name__
        raise
    finally:
        report.write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--offline",action="store_true")
    a=p.parse_args()
    r=run(a.source,a.out,offline=a.offline)
    print(r["status"],"NEW_FINAL_VIDEOS",r["master_videos_finished"])
