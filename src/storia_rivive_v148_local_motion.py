#!/usr/bin/env python3
"""V148: spatially local motion evidence for historic 1.35s source windows.

V115's 64x64 whole-frame mean can miss people moving in a small region.
Here each grayscale original-film proxy is gently blurred, split into 8x8
spatial tiles, and exposure-shift centered *within each tile*.
A pass requires persistent adjacent spatial regions; global brightness flicker
and isolated grain must fail. Still NOT camera-shot artistic approval, rights,
faithful I2I photography, Vidu permission or publication.
"""
from __future__ import annotations

import hashlib
import json
import math
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path

from PIL import Image, ImageFilter

try:
    from src.storia_rivive_motion_window_v115 import check_source_window
except ModuleNotFoundError:
    from storia_rivive_motion_window_v115 import check_source_window

GRID=8
PROXY=128
FRAME_BYTES=PROXY*PROXY


def local_motion_in_gray_frames(frames, *, tile_raw_min=6.5,
                                tile_spatial_min=4.5, min_pairs=3):
    """Pure byte-level classifier, fail closed on invalid dimensions or count."""
    blocked={"status":"BLOCKED","reason":"LOCAL_MOTION_NOT_EVIDENCED",
             "motion_verified":False,"frames_checked":len(frames),
             "qualifying_pairs":0,"changed_tile_regions":0,
             "max_adjacent_pairs":0,"min_pairs_required":min_pairs,
             "method":"8x8_TILED_BLURRED_GRAY_EXPOSURE_CENTERED_V148"}
    if not isinstance(frames,list) or not 5<=len(frames)<=30 or any(
            not isinstance(x,bytes) or len(x)!=FRAME_BYTES for x in frames):
        return {**blocked,"reason":"V148_INVALID_PROXY_FRAME_BYTES"}
    # Blurring each proxy suppresses frame-grain and compression block flicker.
    blurred=[Image.frombytes("L",(PROXY,PROXY),buf).filter(
            ImageFilter.GaussianBlur(1.25)).tobytes() for buf in frames]
    perpair=[];any_tiles=set()
    for prev,curr in zip(blurred,blurred[1:]):
        active=set();tile=PROXY//GRID
        for cy in range(GRID):
            for cx in range(GRID):
                signed=[]
                for y in range(cy*tile,(cy+1)*tile):
                    start=y*PROXY+cx*tile
                    signed.extend(b-a for a,b in zip(
                        prev[start:start+tile],curr[start:start+tile]))
                mean=sum(signed)/len(signed)
                raw=sum(abs(v) for v in signed)/len(signed)
                centered=sum(abs(v-mean) for v in signed)/len(signed)
                if raw>=tile_raw_min and centered>=tile_spatial_min:
                    active.add((cx,cy))
        adjacent=sum(1 for x,y in active if (x+1,y) in active or (x,y+1) in active)
        perpair.append({"active_regions":len(active),"adjacent_regions":adjacent})
        if adjacent>=1 and len(active)>=2:
            any_tiles.update(active)
    qualifying=sum(p["adjacent_regions"]>=1 and p["active_regions"]>=2 for p in perpair)
    largest=max((p["adjacent_regions"] for p in perpair),default=0)
    result={**blocked,"frames_checked":len(frames),"qualifying_pairs":qualifying,
            "changed_tile_regions":len(any_tiles),"max_adjacent_pairs":largest,
            "tile_raw_threshold":tile_raw_min,"tile_spatial_threshold":tile_spatial_min}
    if qualifying>=min_pairs and len(any_tiles)>=3:
        return {**result,"status":"V148_LOCAL_MOTION_PASS_REVIEW_ONLY",
                "reason":"MULTIPLE_ADJACENT_SPATIAL_MOVEMENT_REGIONS_IN_ORIGINAL_BW",
                "motion_verified":True}
    return {**result,"reason":"SOURCE_LOCAL_STATIC_OR_FLICKER_OR_GRAIN"}


def inspect_local_original_window(film,expected_sha,start_pts,freeze_pts,time_base,
                                  *,ffmpeg="ffmpeg"):
    ok,why=check_source_window(start_pts,freeze_pts,time_base)
    if not ok:
        return {"status":"BLOCKED","reason":why,"motion_verified":False}
    p=Path(film)
    if (not isinstance(expected_sha,str) or len(expected_sha)!=64
            or any(x not in "0123456789abcdef" for x in expected_sha)
            or not p.is_file() or p.is_symlink()):
        return {"status":"BLOCKED","reason":"V148_ORIGINAL_SHA_OR_FILE_MISSING","motion_verified":False}
    digest=hashlib.sha256()
    with p.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""):
            digest.update(chunk)
    if digest.hexdigest()!=expected_sha:
        return {"status":"BLOCKED","reason":"V148_ORIGINAL_SOURCE_BYTES_SHA_MISMATCH","motion_verified":False}
    if not shutil.which(ffmpeg):
        return {"status":"BLOCKED","reason":"V148_FFMPEG_MISSING","motion_verified":False}
    n,d=map(int,time_base.split("/"))
    start=float(Fraction(start_pts*n,d))
    duration=float(Fraction((freeze_pts-start_pts)*n,d))
    cmd=[ffmpeg,"-nostdin","-hide_banner","-loglevel","error",
         "-ss",f"{start:.9f}","-i",str(p),"-t",f"{duration:.9f}",
         "-an","-sn","-dn",
         "-vf","fps=8,scale=128:128:flags=area,format=gray",
         "-f","rawvideo","-pix_fmt","gray","pipe:1"]
    try:
        process=subprocess.run(cmd,capture_output=True,timeout=35,check=False)
    except (OSError,subprocess.TimeoutExpired):
        return {"status":"BLOCKED","reason":"V148_REAL_SOURCE_DECODE_FAILED","motion_verified":False}
    if process.returncode or len(process.stdout)%FRAME_BYTES:
        return {"status":"BLOCKED","reason":"V148_INVALID_SOURCE_PROXY_BYTES","motion_verified":False}
    frames=[process.stdout[i:i+FRAME_BYTES] for i in range(0,len(process.stdout),FRAME_BYTES)]
    return local_motion_in_gray_frames(frames)
