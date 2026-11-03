#!/usr/bin/env python3
"""V235: verify real Coney Island 1903 1080p source pixels before ANY generation.

Editorial research only: 20 time-separated, full film frames plus 9:16 crops.
Refuse unverified provenance, source changes, synthetic 1080p confidence, or false final.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps, ImageStat

EXPECTED_SHA1 = "94801a18ec42b2b312fae88d5ba1dc1c47ab2306"
EXPECTED_SIZE = 198831577
EXPECTED_WH = (1920,1080)
FRAME_TIMES = [14,32,51,69,86,107,130,152,174,196,219,242,
               267,293,319,348,378,410,448,488]
RESEARCH_ONLY = "SOURCE_RESEARCH_IMAGES_ONLY_NO_I2I_OR_VIDU"


def sha(path: Path, algorithm: str = "sha256") -> str:
    h=hashlib.new(algorithm)
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def verify_film(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size != EXPECTED_SIZE:
        raise ValueError("SOURCE_MISSING_OR_SIZE_CHANGED")
    actual=sha(path,"sha1")
    if actual != EXPECTED_SHA1:
        raise ValueError("SOURCE_SHA1_MISMATCH")
    proc=subprocess.run(["ffprobe","-v","error","-show_entries",
         "stream=codec_name,width,height:format=duration","-of","json",str(path)],
         check=True,capture_output=True,text=True,timeout=30)
    data=json.loads(proc.stdout)
    tracks=data.get("streams",[])
    if not any((r.get("width"),r.get("height"))==EXPECTED_WH for r in tracks):
        raise ValueError("SOURCE_DECODED_GEOMETRY_CHANGED")
    duration=float(data.get("format",{}).get("duration",0))
    if not 595 <= duration <= 606:
        raise ValueError("SOURCE_DURATION_CHANGED")
    return {"original_archive_sha1":actual,"original_archive_sha256":sha(path),
            "original_source_bytes":EXPECTED_SIZE,"duration_s":duration,
            "raster_px":list(EXPECTED_WH)}


def frame_at(film: Path, second: int, dest: Path):
    subprocess.run(["ffmpeg","-nostdin","-hide_banner","-v","error","-y",
      "-ss",str(second),"-i",str(film),"-frames:v","1",str(dest)],
      check=True,capture_output=True,timeout=60)
    with Image.open(dest) as im:
        if im.format != "PNG" or im.size != EXPECTED_WH:
            raise ValueError("SOURCE_FRAME_MISSING_OR_GEOMETRY_CHANGED")
        im.verify()


def assess_frame(path: Path) -> dict:
    with Image.open(path) as original:
        rgb=original.convert("RGB")
        # Natural 1920px raster is not proof of 1920px optical detail.
        sampled=rgb.resize((160,90),Image.Resampling.LANCZOS)
        values=list(sampled.getdata())
        mean_chroma=sum(max(p)-min(p) for p in values)/len(values)
        if mean_chroma>15:
            raise ValueError("SOURCE_IS_NOT_MONOCHROME")
        # Local contrast, measured on originals: editorial ranking only, NOT quality certification.
        luminance=ImageOps.grayscale(rgb).resize((480,270),Image.Resampling.BICUBIC)
        contrast=ImageStat.Stat(luminance).stddev[0]
        sharp=ImageOps.grayscale(rgb).filter(__import__("PIL.ImageFilter",fromlist=["FIND_EDGES"]).FIND_EDGES)
        texture=ImageStat.Stat(sharp.resize((320,180))).mean[0]
        return {"mean_channel_spread":round(mean_chroma,2),
                "grayscale_stddev":round(contrast,2),
                "edge_energy_proxy":round(texture,2),
                "face_fidelity_assessed":False,"optical_resolution_certified":False}


def contact_sheet(rows: list, out: Path):
    card_w,card_h=500,325
    sheet=Image.new("RGB",(4*card_w,5*card_h),(28,28,28))
    draw=ImageDraw.Draw(sheet)
    for i,row in enumerate(rows):
        original=Image.open(row["full_frame"])
        base=original.convert("RGB")
        full=ImageOps.contain(base,(318,250))
        x0=(i%4)*card_w+10
        y0=(i//4)*card_h+27
        sheet.paste(full,(x0,y0))
        cw=608
        for j,left in enumerate((0,656,1312)):
            crop=base.crop((left,0,left+cw,1080))
            thumb=ImageOps.contain(crop,(50,125))
            sheet.paste(thumb,(x0+326+j*54,y0+24))
        draw.text((x0,y0-19),f"Film t={row['second']:>3}s  CH={row['quality']['mean_channel_spread']:.1f}  CT={row['quality']['grayscale_stddev']:.1f}",fill="white")
        original.close()
    sheet.save(out,quality=88)


def scout(film: Path,out: Path) -> dict:
    verified=verify_film(film)
    out.mkdir(parents=True,exist_ok=True)
    images=out/"FRAMES_ORIGINAL"
    images.mkdir(exist_ok=True)
    rows=[]
    for second in FRAME_TIMES:
        frame=images/f"frame_t{second:03}.png"
        frame_at(film,second,frame)
        quality=assess_frame(frame)
        rows.append({"second":second,"original_frame_sha256":sha(frame),
                     "full_frame":str(frame),"quality":quality})
    sheet=out/"CONTACT_20_SOURCE_FRAMES_9x16_QA.jpg"
    contact_sheet(rows,sheet)
    report={
        "version":"V235_CONEY_1903_REAL_FILM_OPTICAL_SCREEN",
        "status":RESEARCH_ONLY,
        "source_page":"https://commons.wikimedia.org/wiki/File:Coney_Island%2C_New_York%2C_August_13%2C_1903.webm",
        "is_1903_film_not_newly_generated":True,
        "comedy_actors_are_staged":"Rube and Mandy actors are staged; film depicts a real historical amusement park, avoid claiming candid documentary faces",
        "source_original_is_speed_adjusted_upload":True,
        "five_distinct_camera_shots_verified":False,
        "italian_rights_verified":False,
        "real_i2i_photos":0,"vidu_animated_clips":0,"credits_spent":0,
        "artistic_approved":False,"publish_allowed":False,
        "new_final_episodes_delivered":0,
        "technical_source":verified,
        "samples":rows,
        "visual_sheet":sheet.name,
        "next":"Visually compare 20 ORIGINAL full-frame/crops; reject poor facial visibility, staged-actor-dominated shots or repeated angles. Never generate AI on an uninspected sample."
    }
    (out/"SOURCE_REAL_MEDIA_AUDIT_V235.json").write_text(json.dumps(report,indent=2)+"\n")
    print("V235_REAL_ORIGINAL_PIXELS_INSPECTED",len(rows),"RESEARCH_ONLY_NO_FINAL")
    return report


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--film",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    scout(args.film,args.out)

if __name__=="__main__":
    main()
