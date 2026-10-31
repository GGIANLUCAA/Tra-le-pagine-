#!/usr/bin/env python3
"""V149: REAL B/W moving-source private editor preview; NOT a finished video.

Five genuine archival Commons sources, their exact source SHA1/SHA256,
previously measured source PTS windows and source-frame PNG SHA are immutable.
Re-decode original frame PTS and generate a 1.35s silent portrait B/W
normalization for human inspection. No I2I, Vidu, paid API, rights clearance,
color reconstruction, social posting or automatic release. The 30fps preview
may duplicate original low-fps frames, NEVER optical-flow interpolate them.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
import subprocess
import time
from pathlib import Path
from urllib.parse import urlparse

try:
    from src.storia_rivive_scout_v101 import metadata,native_raster_preflight
    from src.storia_rivive_v146_multi_reel_audit import (
        download_source,probe_real_video,sha256_file)
    from src.storia_rivive_motion_window_v115 import check_source_window
except ModuleNotFoundError:
    from storia_rivive_scout_v101 import metadata,native_raster_preflight
    from storia_rivive_v146_multi_reel_audit import (
        download_source,probe_real_video,sha256_file)
    from storia_rivive_motion_window_v115 import check_source_window

SHA1=re.compile(r"[0-9a-f]{40}\Z")
SHA256=re.compile(r"[0-9a-f]{64}\Z")
EXPECTED_VERSION="V149_FIVE_REAL_ORIGINAL_PTS_BW_VIDEO_PROOF_ONLY"


def validate(m):
    if (not isinstance(m,dict) or m.get("version")!=EXPECTED_VERSION
            or m.get("status")!="SOURCE_BW_TECHNICAL_PREVIEW_NOT_FINAL"
            or m.get("max_source_file_size_bytes")!=75_000_000
            or any(m.get(k) is not False for k in ("rights_italy_verified",
                "modern_restoration_rights_verified","artistic_approved",
                "vidu_allowed","photo_i2i_allowed","publish_allowed"))
            or m.get("credits_spent")!=0):
        raise ValueError("V149_PREVIEW_CONTRACT_APPROVAL_OR_SPEND_INVALID")
    proxy=m.get("target_proxy")
    if (not isinstance(proxy,dict) or proxy.get("codec")!="H264"
            or proxy.get("raster")!=[720,1280] or proxy.get("fps")!=30
            or proxy.get("audio") is not False
            or proxy.get("duration_each_s")!=1.35
            or any(proxy.get(k) is not False for k in
                   ("is_final","allow_color_generation","allow_interpolated_footage"))):
        raise ValueError("V149_MOTION_PROXY_PRESET_INVALID")
    rows=m.get("sources")
    if not isinstance(rows,list) or len(rows)!=5:
        raise ValueError("V149_EXACT_FIVE_ORIGINAL_SOURCE_WINDOWS_REQUIRED")
    if ([x.get("scene") for x in rows] != [1,2,3,4,5]
            or [x.get("batch") for x in rows]!=["a","a","a","b","b"]):
        raise ValueError("V149_WRONG_SHOT_ORDER_OR_BATCH_ALLOCATION")
    if ([x.get("role") for x in rows]!=["i2i_later_only"]*4+["vidu_later_only"]):
        raise ValueError("V149_FUTURE_SCENE_ROLE_MISMATCH")
    digests=set();pages=set()
    for item in rows:
        if not isinstance(item,dict):
            raise ValueError("V149_SOURCE_ROW_INVALID")
        page=item.get("source_page")
        u=urlparse(page) if isinstance(page,str) else None
        sha=item.get("original_sha256")
        sha1=item.get("original_sha1")
        frame=item.get("frame_sha256")
        if (u is None or u.scheme!="https" or u.netloc!="commons.wikimedia.org"
                or not u.path.startswith("/wiki/File:") or page in pages
                or not isinstance(sha,str) or SHA256.fullmatch(sha) is None
                or sha in digests or not isinstance(sha1,str)
                or SHA1.fullmatch(sha1) is None or not isinstance(frame,str)
                or SHA256.fullmatch(frame) is None
                or not isinstance(item.get("id"),str)
                or not re.fullmatch(r"[a-z][a-z0-9_]{5,70}",item["id"])
                or item.get("time_base")!="1/1000"):
            raise ValueError("V149_SOURCE_SHA_PAGE_OR_TIME_BASE_INVALID")
        pages.add(page);digests.add(sha)
        ok,reason=check_source_window(item.get("start_pts"),item.get("freeze_pts"),item["time_base"])
        if not ok:
            raise ValueError("V149_PRE_FREEZE_PTS_INVALID_"+reason)
        if (item["freeze_pts"]-item["start_pts"])!=1350:
            # Scene 4 has a 1349ms original source period: handle it explicitly.
            if not (item["scene"]==4 and item["freeze_pts"]-item["start_pts"]==1349):
                raise ValueError("V149_UNEXPECTED_SOURCE_PRE_FREEZE_LENGTH")
    return rows


def probe_clip(path):
    p=subprocess.run(["ffprobe","-v","error","-show_entries",
        "format=duration:stream=codec_type,codec_name,width,height,avg_frame_rate",
        "-of","json",str(path)],capture_output=True,text=True,timeout=25,check=True)
    data=json.loads(p.stdout)
    video=[x for x in data["streams"] if x.get("codec_type")=="video"]
    if len(video)!=1 or video[0].get("codec_name")!="h264":
        raise ValueError("V149_MISSING_H264_VIDEO_STREAM")
    if video[0].get("width")!=720 or video[0].get("height")!=1280:
        raise ValueError("V149_CLIP_RASTER_IS_NOT_PORTRAIT")
    if any(x.get("codec_type")=="audio" for x in data["streams"]):
        raise ValueError("V149_SOURCE_PREVIEW_MUST_BE_SILENT")
    secs=float(data["format"]["duration"])
    if not math.isfinite(secs) or not 1.25<=secs<=1.48:
        raise ValueError("V149_CLIP_PREVIEW_DURATION_OUT_OF_RANGE")
    return secs


def render_clip(source,item,destination,*,ffmpeg="ffmpeg"):
    """Cropping/scaling and simple frame duplication only; NO AI or optical flow."""
    start=item["start_pts"]/1000
    duration=(item["freeze_pts"]-item["start_pts"])/1000
    dest=Path(destination);dest.parent.mkdir(parents=True,exist_ok=True)
    video_filter=("crop=trunc(ih*9/16/2)*2:ih:(iw-ow)/2:0,"
                  "scale=720:1280:flags=lanczos,format=gray,fps=30,format=yuv420p")
    command=[ffmpeg,"-nostdin","-y","-hide_banner","-loglevel","error",
             "-ss",f"{start:.6f}","-i",str(source),"-t",f"{duration:.6f}",
             "-an","-sn","-dn","-vf",video_filter,
             "-c:v","libx264","-preset","veryfast","-crf","19",
             "-pix_fmt","yuv420p","-movflags","+faststart",str(dest)]
    subprocess.run(command,capture_output=True,check=True,timeout=115)
    return probe_clip(dest)


def exact_frame_png_from_pts(source,item,destination,*,ffmpeg="ffmpeg"):
    """Verify the V146 archive PNG SHA again, not just the source-film SHA.

    Never extract by global image query or generate a representative fake
    frame; use original video PTS (1/1000) and no fps resampling.
    """
    ticks=item["freeze_pts"]
    path=Path(destination);path.parent.mkdir(parents=True,exist_ok=True)
    filter_expr=f"select='eq(pts,{ticks})',showinfo"
    cmd=[ffmpeg,"-nostdin","-y","-hide_banner","-loglevel","error",
         "-i",str(source),"-an","-sn","-dn",
         "-vf",filter_expr,"-fps_mode","vfr","-frames:v","1",str(path)]
    subprocess.run(cmd,capture_output=True,check=True,timeout=115)
    if not path.is_file():
        raise ValueError("V149_FREEZE_FRAME_NOT_FOUND_AT_NATIVE_PTS")
    sha=sha256_file(path)
    if sha!=item["frame_sha256"]:
        raise ValueError("V149_FREEZE_FRAME_PNG_SHA_DIFFERS_FROM_REAL_AUDIT")
    return sha


def process_one(item,root,*,lookup=metadata,download=download_source,
                probe=probe_real_video,render=render_clip,freeze=exact_frame_png_from_pts):
    report={"scene":item["scene"],"id":item["id"],"source_page":item["source_page"],
            "year":item["year"],"place_label":item["place_label"],
            "source_sha256_expected":item["original_sha256"],
            "start_pts":item["start_pts"],"freeze_pts":item["freeze_pts"],
            "time_base":item["time_base"],
            "original_source_motion_evidence":item["original_motion_evidence"],
            "status":"V149_PREVIEW_NOT_PROCESSED","rights_italy_verified":False,
            "artistic_approved":False,"paid_api_calls":0,"video_finished":False}
    try:
        info=lookup(item["source_page"])
        if (info.get("source_page")!=item["source_page"]
                or info.get("original_sha1")!=item["original_sha1"]):
            raise ValueError("V149_COMMONS_ORIGINAL_SHA1_OR_PAGE_CHANGED")
        if not native_raster_preflight(info)["native_raster_eligible"]:
            raise ValueError("V149_CURRENT_ORIGINAL_RASTER_TOO_LOW")
        frame_root=root/"originals"/item["id"]
        original=frame_root/"ORIGINAL_ARCHIVE.webm"
        sha=download(info,original,75_000_000)
        if sha!=item["original_sha256"]:
            raise ValueError("V149_FILM_SHA256_CHANGED_FROM_REAL_AUDIT")
        duration,video=probe(original,info)
        if duration<item["freeze_pts"]/1000+0.01:
            raise ValueError("V149_VERIFIED_FREEZE_EXCEEDS_REAL_SOURCE_DURATION")
        verified_frame=freeze(original,item,frame_root/"VERIFIED_EXACT_SOURCE_FREEZE.png")
        mp4=root/"preview_clips"/f"scene_{item['scene']:02d}_BW_SOURCE_PREVIEW.mp4"
        seconds=render(original,item,mp4)
        report.update({"status":"V149_TRUE_SOURCE_BW_MOVING_MP4_REVIEW_ONLY",
                       "source_sha256":sha,"verified_freeze_frame_sha256":verified_frame,
                       "original_source_raster":[video["width"],video["height"]],
                       "clip_filename":mp4.name,
                       "clip_sha256":sha256_file(mp4),
                       "proxy_seconds":seconds,
                       "portrait_video_h264":True,
                       "original_source_timecodes_verified":True})
    except (OSError,ValueError,TypeError,KeyError,subprocess.CalledProcessError,
            subprocess.TimeoutExpired) as exc:
        report["status"]="V149_ARCHIVE_OR_PREVIEW_BLOCKED_NOT_APPROVED"
        report["reason"]=str(exc)[:230]
    print("V149_CLIP_SOURCE",report["scene"],report["status"],report.get("reason",""),flush=True)
    return report


def process_with_rate_limit_policy(item, root, *, worker=process_one, sleep=time.sleep):
    """Retry at most once after a Commons HTTP 429, never after a SHA/rights failure.

    This is GET-only archive research. A failed second attempt remains blocked;
    never mark a missing original film as a verified clip.
    """
    first=worker(item,root)
    if (first.get("status")!="V149_ARCHIVE_OR_PREVIEW_BLOCKED_NOT_APPROVED"
            or re.search(r"\\bHTTP Error 429\\b",first.get("reason","")) is None):
        return first
    sleep(60)
    second=worker(item,root)
    second["commons_429_backoff_seconds"]=60
    second["commons_429_retry_count"]=1
    return second


def run(manifest,outdir,batch,*,worker=process_one,sleep=time.sleep):
    m=json.loads(Path(manifest).read_text(encoding="utf-8"))
    shots=validate(m)
    if batch not in ("a","b"):
        raise ValueError("V149_BATCH_NOT_RECOGNIZED")
    root=Path(outdir);root.mkdir(parents=True,exist_ok=True)
    chosen=[x for x in shots if x["batch"]==batch]
    result=[]
    for index,item in enumerate(chosen):
        # Avoid a rapid third Commons download that triggered HTTP 429 in V149.
        if index:
            sleep(12)
        result.append(process_with_rate_limit_policy(item,root,worker=worker,sleep=sleep))
    report={
        "version":EXPECTED_VERSION,"batch":batch,
        "status":("V149_ORIGINAL_BW_CLIPS_READY_FOR_PRIVATE_QA" if
                  all(x["status"]=="V149_TRUE_SOURCE_BW_MOVING_MP4_REVIEW_ONLY" for x in result)
                  else "V149_ORIGINAL_BW_PREVIEW_INCOMPLETE"),
        "source_clips":result,"requested_clips":len(chosen),
        "clips_verified":sum(x["status"]=="V149_TRUE_SOURCE_BW_MOVING_MP4_REVIEW_ONLY" for x in result),
        "not_a_restored_4_i2i_1_vidu_video":True,
        "rights_italy_verified":False,
        "modern_restoration_rights_verified":False,
        "artistic_approved":False,"paid_api_calls":0,
        "new_true_i2i_photos":0,"new_vidu_clips":0,
        "is_finished_video":False,"publish_permitted":False}
    (root/"BW_PREVIEW_SOURCE_REPORT_V149.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("V149_SOURCE_BATCH",batch,report["status"],
          "clips",report["clips_verified"],"paid",0,flush=True)
    return report


if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--manifest",default="config/storia_rivive_v149_five_original_motion_preview.json")
    cli.add_argument("--batch",required=True,choices=["a","b"])
    cli.add_argument("--out",required=True)
    a=cli.parse_args()
    run(a.manifest,a.out,a.batch)
