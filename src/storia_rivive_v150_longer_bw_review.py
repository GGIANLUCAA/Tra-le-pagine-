#!/usr/bin/env python3
"""V150: optional 2.4s authentic B/W review per V149 source, no AI or paid calls.

This is NOT a 4+1 restored master. Extra footage is decoded from the SAME
SHA-verified original immediately before the authenticated V149 window.
No frame-hold, artificial slow motion or invented archival images.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path

from src.storia_rivive_v149_authentic_bw_proxy import (
    validate, exact_frame_png_from_pts, probe_clip, sha256_file,
    process_with_rate_limit_policy,
)
from src.storia_rivive_scout_v101 import metadata, native_raster_preflight
from src.storia_rivive_v146_multi_reel_audit import download_source, probe_real_video

EXTRA_MS = 1050
EXTENDED_SECONDS = 2.40
STATUS = "V150_LONGER_AUTHENTIC_BW_REVIEW_ONLY"


def extended_window(item):
    """Keep exact original freeze PTS; look 1.05s further BACK, never forward."""
    start = item["start_pts"] - EXTRA_MS
    end = item["freeze_pts"]
    if (type(start) is not int or type(end) is not int
            or start < 0 or end - start not in (2399, 2400)
            or item["time_base"] != "1/1000"):
        raise ValueError("V150_INVALID_EXTENDED_NATIVE_SOURCE_WINDOW")
    return start, end


def changed_frames_in_added_window(film, start_ms, *, ffmpeg="ffmpeg"):
    """Report true decoded temporal variation, not proof of camera movement.

    Fail closed for identical decoded frames. Human inspection is still needed
    for motion, authenticity, faces and editorial uniqueness.
    """
    cmd = [ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error",
           "-ss", f"{start_ms/1000:.6f}", "-i", str(film),
           "-t", f"{EXTRA_MS/1000:.6f}", "-an", "-sn", "-dn",
           "-vf", "fps=8,scale=160:90,format=gray",
           "-f", "rawvideo", "-pix_fmt", "gray", "pipe:1"]
    res = subprocess.run(cmd, capture_output=True, check=True, timeout=55)
    size = 160*90
    raw = res.stdout
    if len(raw) % size:
        raise ValueError("V150_EXTRA_WINDOW_RAW_FRAMES_CORRUPTED")
    frames = [raw[i:i+size] for i in range(0,len(raw),size)]
    if len(frames) < 5:
        raise ValueError("V150_TOO_FEW_EXTRA_NATIVE_SOURCE_FRAMES")
    changes = []
    for previous, current in zip(frames,frames[1:]):
        score = sum(abs(a-b) for a,b in zip(previous,current)) / size
        changes.append(round(score,3))
    if sum(score >= 1.5 for score in changes) < 2:
        raise ValueError("V150_ADDED_WINDOW_STATIC_OR_UNREADABLE")
    return {"sampled_frames":len(frames),"luma_mean_abs_differences":changes,
            "visual_motion_artistic_review_required":True}


def render_longer(film, item, out, *, ffmpeg="ffmpeg"):
    start, end = extended_window(item)
    dest=Path(out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    vf=("crop=trunc(ih*9/16/2)*2:ih:(iw-ow)/2:0,"
        "scale=720:1280:flags=lanczos,format=gray,fps=30,format=yuv420p")
    cmd=[ffmpeg,"-nostdin","-y","-hide_banner","-loglevel","error",
         "-ss",f"{start/1000:.6f}","-i",str(film),
         "-t",f"{(end-start)/1000:.6f}","-an","-sn","-dn",
         "-vf",vf,"-c:v","libx264","-preset","veryfast","-crf","19",
         "-pix_fmt","yuv420p","-movflags","+faststart",str(dest)]
    subprocess.run(cmd,capture_output=True,check=True,timeout=120)
    probe=subprocess.run(["ffprobe","-v","error","-show_entries",
                           "format=duration:stream=codec_type,codec_name,width,height",
                           "-of","json",str(dest)],capture_output=True,text=True,check=True,timeout=25)
    info=json.loads(probe.stdout)
    videos=[s for s in info["streams"] if s.get("codec_type")=="video"]
    seconds=float(info["format"]["duration"])
    if (len(videos)!=1 or videos[0].get("codec_name")!="h264"
            or (videos[0].get("width"),videos[0].get("height"))!=(720,1280)
            or any(s.get("codec_type")=="audio" for s in info["streams"])
            or not 2.28 <= seconds <= 2.53):
        raise ValueError("V150_EXTENDED_CLIP_CODEC_RASTER_OR_DURATION_INVALID")
    return seconds


def process_one(item, root, *, lookup=metadata, download=download_source,
                probe=probe_real_video, freeze=exact_frame_png_from_pts,
                changes=changed_frames_in_added_window, render=render_longer):
    start,end=extended_window(item)
    row={"scene":item["scene"],"id":item["id"],"source_page":item["source_page"],
         "original_sha256":item["original_sha256"],"freeze_frame_sha256":item["frame_sha256"],
         "start_pts":start,"freeze_pts":end,"time_base":"1/1000",
         "status":"V150_BLOCKED","rights_italy_verified":False,
         "artistic_approved":False,"paid_api_calls":0,"finished":False}
    try:
        meta=lookup(item["source_page"])
        if (meta.get("source_page")!=item["source_page"] or
                meta.get("original_sha1")!=item["original_sha1"]):
            raise ValueError("V150_COMMONS_SHA1_OR_PAGE_CHANGED")
        if not native_raster_preflight(meta)["native_raster_eligible"]:
            raise ValueError("V150_NATIVE_RASTER_BELOW_REQUIREMENT")
        original=Path(root)/"originals"/item["id"]/"ARCHIVE.webm"
        original.parent.mkdir(parents=True,exist_ok=True)
        digest=download(meta,original,75_000_000)
        if digest!=item["original_sha256"]:
            raise ValueError("V150_SOURCE_SHA256_MISMATCH")
        film_duration,_=probe(original,meta)
        if film_duration <= end/1000:
            raise ValueError("V150_FREEZE_OUTSIDE_SOURCE")
        actual=freeze(original,item,original.parent/"EXACT_FREEZE.png")
        if actual!=item["frame_sha256"]:
            raise ValueError("V150_NATIVE_FREEZE_SHA_CHANGED")
        motion=changes(original,start)
        clip=Path(root)/"preview"/f"scene_{item['scene']:02d}_V150_BW_LONGER.mp4"
        seconds=render(original,item,clip)
        row.update(status=STATUS,clip_filename=clip.name,
                   clip_sha256=sha256_file(clip),seconds=seconds,
                   added_source_variation=motion,freeze_frame_sha256=actual)
    except (OSError,ValueError,KeyError,TypeError,subprocess.CalledProcessError,
            subprocess.TimeoutExpired) as error:
        row["reason"]=str(error)[:240]
    return row


def process_batch(manifest, out, batch, *, worker=process_one, sleep=time.sleep):
    data=json.loads(Path(manifest).read_text(encoding="utf-8"))
    shots=validate(data)
    if batch not in ("a","b"):
        raise ValueError("V150_INVALID_BATCH")
    root=Path(out)
    root.mkdir(parents=True,exist_ok=True)
    selected=[s for s in shots if s["batch"]==batch]
    rows=[]
    for index,shot in enumerate(selected):
        if index:
            sleep(12)
        rows.append(process_with_rate_limit_policy(shot,root,worker=worker,sleep=sleep))
    report={"version":"V150","batch":batch,"status":(
        "V150_EXTENDED_BW_SOURCE_BATCH_READY" if all(x["status"]==STATUS for x in rows)
        else "V150_EXTENDED_BW_SOURCE_BATCH_BLOCKED"),"sources":rows,
        "paid_api_calls":0,"rights_italy_verified":False,"artistic_approved":False,
        "is_finished_video":False,"publish_permitted":False,
        "real_i2i_generated":0,"real_vidu_generated":0}
    (root/"V150_BATCH_REPORT.json").write_text(
        json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return report


def combine(manifest, artifacts, output):
    data=json.loads(Path(manifest).read_text(encoding="utf-8"))
    shots=validate(data)
    root=Path(artifacts)
    reports=sorted(root.rglob("V150_BATCH_REPORT.json"))
    if len(reports)!=2:
        raise ValueError("V150_TWO_SOURCE_BATCHES_REQUIRED")
    found={}
    for path in reports:
        batch=json.loads(path.read_text(encoding="utf-8"))
        if (batch.get("batch") not in ("a","b") or batch["batch"] in found
                or batch.get("status")!="V150_EXTENDED_BW_SOURCE_BATCH_READY"
                or batch.get("is_finished_video") is not False
                or batch.get("paid_api_calls")!=0
                or batch.get("publish_permitted") is not False):
            raise ValueError("V150_INVALID_BATCH_REPORT")
        found[batch["batch"]]=batch
    files=[]
    for shot in shots:
        batch=found[shot["batch"]]
        rows=[x for x in batch["sources"] if x.get("scene")==shot["scene"]]
        if len(rows)!=1:
            raise ValueError("V150_MISSING_OR_DUPLICATE_SCENE")
        row=rows[0]
        name=f"scene_{shot['scene']:02d}_V150_BW_LONGER.mp4"
        if (row.get("status")!=STATUS or row.get("id")!=shot["id"]
                or row.get("original_sha256")!=shot["original_sha256"]
                or row.get("freeze_frame_sha256")!=shot["frame_sha256"]
                or row.get("start_pts")!=shot["start_pts"]-EXTRA_MS
                or row.get("freeze_pts")!=shot["freeze_pts"]
                or row.get("clip_filename")!=name
                or row.get("artistic_approved") is not False):
            raise ValueError("V150_SOURCE_PROVENANCE_CHANGED")
        matches=list(root.rglob(name))
        if len(matches)!=1 or matches[0].is_symlink():
            raise ValueError("V150_CLIP_FILE_NOT_UNIQUE")
        clip=matches[0]
        if sha256_file(clip)!=row.get("clip_sha256"):
            raise ValueError("V150_VIDEO_BYTES_SHA_MISMATCH")
        files.append(clip.resolve())
    target=Path(output)
    target.parent.mkdir(parents=True,exist_ok=True)
    playlist=target.parent/"V150_SAFE_PLAYLIST.txt"
    playlist.write_text("\n".join("file '"+str(f).replace("'","'\\''")+"'" for f in files)+"\n",encoding="utf-8")
    subprocess.run(["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error",
                    "-f","concat","-safe","0","-i",str(playlist),"-an",
                    "-c:v","copy","-movflags","+faststart",str(target)],
                   check=True,capture_output=True,timeout=120)
    p=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                      "-of","default=noprint_wrappers=1:nokey=1",str(target)],
                     check=True,capture_output=True,text=True,timeout=25)
    duration=float(p.stdout.strip())
    if not 11.4<=duration<=13.0:
        raise ValueError("V150_COMBINED_DURATION_WRONG")
    report={"version":"V150","status":"LONGER_AUTHENTIC_BW_ONLY_NOT_FINAL",
            "duration_s":duration,"source_count":5,"sha256":sha256_file(target),
            "original_frame_sha_verified":True,"added_motion_is_artistically_verified":False,
            "has_restorations":False,"has_vidu":False,"has_audio":False,
            "rights_italy_verified":False,"artistic_approved":False,
            "paid_api_calls":0,"publish_permitted":False}
    (target.parent/"V150_REVIEW_ONLY_REPORT.json").write_text(
        json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return report


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",default="config/storia_rivive_v149_five_original_motion_preview.json")
    ap.add_argument("--out",required=True)
    ap.add_argument("--batch",choices=["a","b"])
    ap.add_argument("--artifacts")
    args=ap.parse_args()
    if args.batch:
        report=process_batch(args.manifest,args.out,args.batch)
    elif args.artifacts:
        report=combine(args.manifest,args.artifacts,args.out)
    else:
        ap.error("Specify --batch or --artifacts")
    print("V150",report["status"],"paid",0,"final",False)
