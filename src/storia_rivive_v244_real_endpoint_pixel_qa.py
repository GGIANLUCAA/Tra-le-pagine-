#!/usr/bin/env python3
"""V244: inspect decoded V243 shot endpoints against SHA-locked archival frames.
This is an artistic/temporal preflight, never final certification or permission to publish.
"""
from __future__ import annotations
import argparse, hashlib, json, math, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageOps, ImageChops, ImageStat

def endpoint_error(reference:Path, decoded:Path)->float:
    with Image.open(reference) as a, Image.open(decoded) as b:
        if min(a.size)<240 or min(b.size)<240: raise ValueError("INVALID_IMAGE_GEOMETRY")
        a=ImageOps.fit(a.convert("L"),(144,256),method=Image.Resampling.LANCZOS)
        b=ImageOps.fit(b.convert("L"),(144,256),method=Image.Resampling.LANCZOS)
        return round(ImageStat.Stat(ImageChops.difference(a,b)).mean[0],3)

def inspect(video:Path,manifest:Path,frames:Path,out:Path,threshold:float=38.0)->dict:
    if not 0<threshold<=60: raise ValueError("UNSAFE_THRESHOLD")
    if video.is_symlink() or not video.is_file() or video.stat().st_size<1000:
        raise ValueError("VIDEO_MISSING")
    plan=json.loads(manifest.read_text())
    shots=plan.get("shots")
    if plan.get("status")!="NOT_FINAL" or len(shots or [])!=5:
        raise ValueError("INVALID_V243_MANIFEST")
    probe=json.loads(subprocess.run(["ffprobe","-v","error","-select_streams","v:0",
        "-show_entries","stream=nb_frames,avg_frame_rate,width,height","-of","json",str(video)],
        capture_output=True,text=True,check=True,timeout=30).stdout)
    stream=probe["streams"][0]
    num=int(stream.get("nb_frames") or 0)
    rate=stream["avg_frame_rate"].split("/")
    fps=float(rate[0])/float(rate[1])
    if not 23.9<=fps<=24.1 or not 20<=num/fps<=30:
        raise ValueError("INVALID_ROUGHCUT_TIMELINE")
    if num%5!=0: raise ValueError("UNEVEN_SHOT_FRAME_COUNT")
    per=num//5
    checks=[]
    with tempfile.TemporaryDirectory(prefix="storia-v244-") as td:
        for i,shot in enumerate(shots):
            frame=frames/shot["source_frame"]
            if frame.is_symlink() or not frame.is_file() or hashlib.sha256(frame.read_bytes()).hexdigest()!=shot["sha256"]:
                raise ValueError("ORIGINAL_FRAME_HASH_MISMATCH")
            image=Path(td)/f"endpoint_{i}.png"
            # Decode the actual last frame of each 4.8s shot from the concatenated MP4.
            index=(i+1)*per-1
            subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
                "-i",str(video),"-vf",f"select=eq(n\\,{index})","-vsync","0",
                "-frames:v","1",str(image)],check=True,timeout=90)
            if not image.is_file():raise ValueError("DECODED_ENDPOINT_MISSING")
            error=endpoint_error(frame,image)
            checks.append({"shot":i+1,"frame":shot["source_frame"],
                "original_sha256":shot["sha256"],"decoded_frame_index":index,
                "grayscale_mean_absolute_error":error,
                "pass_candidate":error<=threshold})
    result={"version":"V244_REAL_DECODED_ENDPOINT_COMPARISON",
        "status":"REVIEW_ENDPOINTS_PASS" if all(x["pass_candidate"] for x in checks)
                 else "REVIEW_ENDPOINTS_REJECTED",
        "frame_count":num,"fps":fps,"threshold_mae":threshold,
        "checks":checks,"exact_frame_certified":False,
        "i2i_generated":False,"vidu_generated":False,"final_mp4":False,
        "final_zip":False,"new_final_episodes_delivered":0,"publish_allowed":False}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n")
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for arg in ("video","manifest","frames","out"):
        p.add_argument("--"+arg,required=True,type=Path)
    a=p.parse_args()
    r=inspect(a.video,a.manifest,a.frames,a.out)
    print("V244",r["status"],"MAE",[x["grayscale_mean_absolute_error"] for x in r["checks"]],"FINAL_0_OF_4")
    if r["status"]!="REVIEW_ENDPOINTS_PASS":raise SystemExit(2)
