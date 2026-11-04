#!/usr/bin/env python3
"""V277 — one genuine Finegrain photo-restoration trial on Delhi 1910 source.

The model and /process parameters reproduce the V98 Bombay technique.
Source lock: original 1910 frame and one real earlier I2I base, exact SHA.
This is an artistic candidate, NOT an approved photo, video or publication.
No Vidu POST, spending, retries or public release.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps, ImageStat

EPISODE="delhi_ruins_1910_v217"
FILM_SHA="0a0de7b032cdb19e34d4dac5a6efca02dfa4b00260411aa82290c54b2899f278"
ORIGINAL_FRAME_SHA="d6a6f21789093f971cff0adfa4259511a24875eb73753b8c7f177b882762f16e"
SOURCE_CROP_SHA="816e1555d547e5df8170b242d6ce0ec59c9e8518f2402588d3da902875320add"
V273_BASE_SHA="ff6190681d97d306e27c7d77ad5716dc0a5854382c0b96f965ea7c9bb2a5aca3"
MODEL="finegrain/finegrain-image-enhancer"
MODEL_API="/process"
VERSION="V277_DELHI_REAL_FINEGRAIN_V98_METHOD_NOT_FINAL"
SEED=277
PROMPT=(
  "Authentic 1910 Delhi India ruins: improve the photographic details of the "
  "EXACT reference image while preserving all existing stone columns, ancient "
  "architecture, actual people, their clothing and postures, silhouettes and "
  "original camera geometry. Real modern documentary photography, beautifully "
  "detailed carved sandstone, believable warm beige stone, greenery and trees, "
  "pale natural daylight, realistic muted textile and skin colors. No new "
  "humans, faces, hands, monuments, machines or lettering."
)
NEGATIVE=(
  "new person, extra faces, distorted faces, invented hands, missing legs, "
  "modern building, new architecture, fake objects, cartoon, painting, "
  "plastic skin, excessive orange, sepia filter, oversharpening, watermark"
)
TARGET_SIZE=(720,1280)
PHOTO_NAME="DELHI_1910_V277_FINEGRAIN_V98_METHOD_REAL_I2I_NOT_APPROVED.jpg"
QA_NAME="V277_FINEGRAIN_REAL_I2I_QA_NOT_FINAL.json"

def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""): h.update(chunk)
    return h.hexdigest()

def verified_sources(source:Path,base:Path,manifest:Path)->dict:
    m=json.loads(manifest.read_text(encoding="utf-8"))
    if (m.get("version")!="V273_DELHI_REAL_CPU_I2I_REVIEW_ONLY"
        or m.get("episode")!=EPISODE
        or m.get("source_metadata",{}).get("film_sha256")!=FILM_SHA
        or m.get("source_metadata",{}).get("original_frame_sha256")!=ORIGINAL_FRAME_SHA
        or m.get("source_metadata",{}).get("source_shot")!=3
        or m.get("source_crop_sha256")!=SOURCE_CROP_SHA
        or m.get("generated_sha256")!=V273_BASE_SHA
        or m.get("generated_photos")!=1
        or m.get("artistic_approval") is not False
        or m.get("publish_allowed") is not False):
        raise ValueError("V277_UNVERIFIED_PRIOR_GENERATION")
    for f,expected in ((source,SOURCE_CROP_SHA),(base,V273_BASE_SHA)):
        if not f.is_file() or f.is_symlink() or sha(f)!=expected:
            raise ValueError("V277_INPUT_SOURCE_SHA_CHANGED")
        with Image.open(f) as pic:
            if pic.format!="PNG":
                raise ValueError("V277_SOURCE_NOT_PNG")
            pic.verify()
    with Image.open(source) as src,Image.open(base) as b:
        if src.size!=(608,1080) or b.size!=(448,800):
            raise ValueError("V277_SOURCE_DIMENSIONS_CHANGED")
    return {"original_frame_sha256":ORIGINAL_FRAME_SHA,
            "source_crop_sha256":SOURCE_CROP_SHA,
            "real_base_i2i_sha256":V273_BASE_SHA,
            "original_film_sha256":FILM_SHA}

def genuine_finegrain_call(base:Path)->Path:
    # The exact V98 successful provider; ONE request, no retry on exhausted
    # ZeroGPU or transient errors. Never submit to a paid inference endpoint.
    from gradio_client import Client, handle_file
    client=Client(MODEL,verbose=False)
    result=client.predict(
        handle_file(str(base)),PROMPT,NEGATIVE,SEED,
        2,1.14,0.97,6,112,144,0.45,18,"DDIM",api_name=MODEL_API)
    candidate=result[1] if isinstance(result,(tuple,list)) and len(result)>1 else result
    if isinstance(candidate,dict):candidate=candidate.get("path")
    if not isinstance(candidate,str) or not Path(candidate).is_file():
        raise ValueError("V277_FINEGRAIN_NO_REAL_OUTPUT_PATH")
    return Path(candidate)

def assess(source:Path,new_photo:Path)->dict:
    if not new_photo.is_file() or new_photo.is_symlink() or new_photo.stat().st_size<20000:
        raise ValueError("V277_NO_ACTUAL_PHOTO_BYTES")
    with Image.open(source) as src,Image.open(new_photo) as o:
        if o.size!=TARGET_SIZE or o.mode not in ("RGB","RGBA"):
            raise ValueError("V277_OUTPUT_DIMENSIONS_OR_MODE")
        src_g=ImageOps.grayscale(src.resize((90,160)))
        new_g=ImageOps.grayscale(o.resize((90,160)))
        from PIL import ImageChops
        p=list(src_g.getdata());q=list(new_g.getdata())
        import math
        mp=sum(p)/len(p);mq=sum(q)/len(q)
        co=sum((a-mp)*(b-mq) for a,b in zip(p,q))
        denom=math.sqrt(sum((a-mp)**2 for a in p)*sum((b-mq)**2 for b in q))
        similarity=co/max(denom,1.0)
        saturation=ImageStat.Stat(o.convert("HSV")).mean[1]
    return {"real_photo_sha256":sha(new_photo),
            "photo_pixel_size":list(TARGET_SIZE),
            "source_greyscale_correlation":round(similarity,4),
            "mean_hsv_saturation":round(saturation,2),
            "geometric_preflight_passed":similarity>=0.90,
            "non_monochrome_preflight_passed":18<saturation<175}

def run(source:Path,base:Path,manifest:Path,out:Path,offline:bool=False,predict=None)->dict:
    identity=verified_sources(source,base,manifest)
    out.mkdir(parents=True,exist_ok=True)
    report={"version":VERSION,"episode":EPISODE,"provider":MODEL,
            "source_identity":identity,"prompt_sha256":hashlib.sha256(PROMPT.encode()).hexdigest(),
            "seed":SEED,"provider_calls_attempted":0,"photo_generated":False,
            "approved_photo_count":0,"vidu_count":0,"vidu_credits_spent":0,
            "italian_rights_verified":False,"artistic_approval":False,
            "final_video_created":False,"published":False,"new_final_episodes_delivered":0,
            "status":"REAL_ARCHIVAL_SOURCE_LOCKED_NO_PROVIDER_CALL"}
    report_path=out/QA_NAME
    report_path.write_text(json.dumps(report,indent=2)+"\n")
    if offline:return report
    try:
        report["provider_calls_attempted"]=1
        report["status"]="ONE_FREE_FINEGRAIN_INFERENCE_ATTEMPTED"
        report_path.write_text(json.dumps(report,indent=2)+"\n")
        actual=(predict or genuine_finegrain_call)(base)
        if not actual.is_file() or actual.is_symlink():
            raise ValueError("V277_NO_PROVIDER_IMAGE")
        destination=out/PHOTO_NAME
        with Image.open(actual) as image:
            converted=ImageOps.fit(image.convert("RGB"),TARGET_SIZE,Image.Resampling.LANCZOS)
            converted.save(destination,format="JPEG",quality=96,subsampling=0)
        report.update(assess(source,destination))
        with Image.open(source) as src,Image.open(base) as prev,Image.open(destination) as fin:
            sheet=Image.new("RGB",(3*390,730),(17,20,26))
            draw=ImageDraw.Draw(sheet)
            for i,(pic,title) in enumerate((
                (src,"1910 ACTUAL ARCHIVAL BW FRAME"),
                (prev,"V273 BASE: REJECTED COLOR"),
                (fin,"V277 TRUE FINEGRAIN I2I - QA"))):
                sheet.paste(ImageOps.fit(pic.convert("RGB"),(382,680)),(i*390+4,38))
                draw.text((i*390+5,11),title,fill="white")
            sheet.save(out/"V277_DELHI_SOURCE_V273_V98_FINEGRAIN_COMPARISON.jpg",quality=92)
        report["photo_generated"]=True
        report["status"]=("REAL_FINEGRAIN_I2I_NEEDS_HUMAN_ARTISTIC_QA_NOT_FINAL"
                          if report["geometric_preflight_passed"] and report["non_monochrome_preflight_passed"]
                          else "REAL_FINEGRAIN_I2I_PRECHECK_REJECTED_NOT_FINAL")
    except Exception as err:
        report["status"]="FREE_FINEGRAIN_FAILED_NO_NEW_APPROVED_I2I"
        report["error_class"]=type(err).__name__
        raise
    finally:
        report_path.write_text(json.dumps(report,indent=2)+"\n")
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-crop",type=Path,required=True)
    p.add_argument("--base",type=Path,required=True)
    p.add_argument("--prior-manifest",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--offline",action="store_true")
    a=p.parse_args()
    r=run(a.source_crop,a.base,a.prior_manifest,a.out,a.offline)
    print(r["status"],"FINAL_VIDEO_0_OF_4")

if __name__=="__main__":
    main()
