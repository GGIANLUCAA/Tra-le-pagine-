#!/usr/bin/env python3
"""V146: genuine five-reel archive scouting for La Storia Rivive, NO paid calls.

Unlike a multi-shot single-film selector, each scene comes from a separately
SHA-bound Commons *original uploaded video*. One original freeze PTS and its
preceding 1.35 s must exhibit decoded spatial motion. FIVE REELS are a
candidate, NOT an artistic claim of five different real camera compositions.

Never invokes image generation, Vidu, social or the final 4+1 renderer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
from fractions import Fraction
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen, Request

from PIL import Image, ImageDraw

try:
    from src.storia_rivive_scout_v101 import metadata, native_raster_preflight, verify_decoded_original_raster, USER_AGENT
    from src.storia_rivive_adaptive_sampling_v124 import SHOWINFO, TIME_BASE, exact_pts_time_from_showinfo, sha256_file
    from src.storia_rivive_frame_rank_v101 import measure
    from src.storia_rivive_motion_window_v115 import inspect_source_motion, check_source_window
except ModuleNotFoundError:
    from storia_rivive_scout_v101 import metadata, native_raster_preflight, verify_decoded_original_raster, USER_AGENT
    from storia_rivive_adaptive_sampling_v124 import SHOWINFO, TIME_BASE, exact_pts_time_from_showinfo, sha256_file
    from storia_rivive_frame_rank_v101 import measure
    from storia_rivive_motion_window_v115 import inspect_source_motion, check_source_window

ID = re.compile(r"[a-z][a-z0-9_]{6,65}\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")
ALLOWED_YEAR_RANGE = range(1880, 1930)
MIN_MOVING_REELS = 5


def validate_manifest(m):
    if (not isinstance(m,dict) or m.get("version")!="V146_MULTI_ARCHIVE_FIVE_REAL_REELS_RESEARCH_ONLY"
            or m.get("research_qa_only") is not True
            or any(m.get(k) is not False for k in (
                "rights_italy_verified","modern_restoration_rights_verified",
                "visual_artist_approval","i2i_permitted","vidu_post_permitted","publish_permitted"))
            or m.get("minimum_distinct_moving_original_films") != MIN_MOVING_REELS
            or m.get("max_download_count") != 6
            or m.get("max_original_source_bytes_each") != 75_000_000
            or m.get("max_combined_original_source_bytes") != 190_000_000):
        raise ValueError("V146_CONTRACT_OR_PAID_GATE_INVALID")
    films=m.get("sources")
    if not isinstance(films,list) or len(films)!=6:
        raise ValueError("V146_REQUIRE_SIX_ARCHIVE_CANDIDATES")
    ids=set();pages=set();ordinals=set()
    for item in films:
        if not isinstance(item,dict):
            raise ValueError("V146_REEL_ROW_INVALID")
        key,url,year,index=item.get("id"),item.get("page"),item.get("year"),item.get("ordinal")
        parsed=urlparse(url) if isinstance(url,str) else None
        if (not isinstance(key,str) or ID.fullmatch(key) is None
                or key in ids or url in pages or type(index) is not int
                or index not in range(1,7) or index in ordinals
                or type(year) is not int or year not in ALLOWED_YEAR_RANGE
                or parsed is None or parsed.scheme!="https"
                or parsed.netloc!="commons.wikimedia.org"
                or not parsed.path.startswith("/wiki/File:")):
            raise ValueError("V146_DUPLICATE_OR_NON_COMMONS_SOURCE")
        ids.add(key);pages.add(url);ordinals.add(index)
    return sorted(films,key=lambda x:x["ordinal"])


def download_source(meta,path,byte_limit,open_url=urlopen):
    """Only exact HTTPS upload.wikimedia.org original, bounded, SHA1 checked."""
    url=meta.get("download_url")
    size=meta.get("size_bytes")
    sha1=meta.get("original_sha1")
    u=urlparse(url) if isinstance(url,str) else None
    if (not u or u.scheme!="https" or u.netloc!="upload.wikimedia.org"
            or not u.path.lower().endswith((".webm",".ogg",".ogv",".mp4"))
            or type(size) is not int or not 0<size<=byte_limit
            or not isinstance(sha1,str) or re.fullmatch(r"[0-9a-f]{40}",sha1) is None):
        raise ValueError("V146_COMMONS_ORIGINAL_SIZE_SHA1_OR_HOST_INVALID")
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(".part")
    h1=hashlib.sha1();h256=hashlib.sha256();n=0
    try:
        with open_url(Request(url,headers={"User-Agent":USER_AGENT}),timeout=65) as upstream, temp.open("wb") as target:
            resolved=upstream.geturl() if hasattr(upstream,"geturl") else url
            resolved_host=urlparse(resolved)
            if resolved_host.scheme!="https" or resolved_host.netloc!="upload.wikimedia.org":
                raise ValueError("V146_DOWNLOAD_REDIRECT_LEFT_TRUSTED_ARCHIVE")
            while True:
                chunk=upstream.read(1_048_576)
                if not chunk:
                    break
                n+=len(chunk)
                if n>byte_limit or n>size:
                    raise ValueError("V146_DOWNLOAD_BYTE_CAP_BREACHED")
                target.write(chunk);h1.update(chunk);h256.update(chunk)
        if n!=size or h1.hexdigest()!=sha1:
            raise ValueError("V146_ORIGINAL_BYTES_SIZE_OR_COMMONS_SHA1_MISMATCH")
        temp.replace(path)
        return h256.hexdigest()
    finally:
        if temp.exists():
            temp.unlink()


def probe_real_video(path,meta):
    cmd=["ffprobe","-v","error","-show_entries",
         "format=duration:stream=codec_type,codec_name,width,height,avg_frame_rate",
         "-of","json",str(path)]
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=40,check=True)
    info=json.loads(p.stdout)
    verify_decoded_original_raster(info,meta)
    duration=float(info.get("format",{}).get("duration",0))
    if not math.isfinite(duration) or not 14<=duration<=900:
        raise ValueError("V146_ORIGINAL_DURATION_INVALID")
    stream=next(x for x in info["streams"] if x.get("codec_type")=="video")
    return duration,{"width":stream["width"],"height":stream["height"],
                     "codec_name":stream.get("codec_name"),"duration_s":duration}


def extract_source_freezes(video,folder,duration):
    """One FFmpeg native-PTS decode for 3 candidate freeze moments, not 5 cuts."""
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    # Avoid intro cards. Sample middle positions and keep at least 2s before end.
    chosen=[round(duration*f,5) for f in (0.21,0.48,0.74)]
    expression="+".join(f"eq(selected_n,{i})*gte(t,{t:.5f})" for i,t in enumerate(chosen))
    cmd=["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","info",
         "-i",str(video),"-an","-sn","-vf",f"select='{expression}',showinfo",
         "-fps_mode","vfr","-frames:v","3",str(folder/"freeze_%02d.png")]
    p=subprocess.run(cmd,capture_output=True,text=True,check=True,timeout=160)
    rows=SHOWINFO.findall(p.stderr);bases=TIME_BASE.findall(p.stderr)
    files=sorted(folder.glob("freeze_*.png"))
    if len(rows)!=3 or len(files)!=3 or len(bases)!=1:
        raise ValueError("V146_ORIGINAL_FRAME_PTS_DECODE_INCOMPLETE")
    entries=[];last=-1
    for i,(n,pts,printed) in enumerate(rows):
        ticks=int(pts);sec=exact_pts_time_from_showinfo(ticks,bases[0],printed)
        if int(n)!=i or sec<=last or sec+0.0001<chosen[i]:
            raise ValueError("V146_ORIGINAL_FREEZE_PTS_INVALID")
        last=sec
        frame=files[i]
        evidence={"filename":frame.name,"source_pts":ticks,"source_pts_time_s":sec,
                  "source_time_base":bases[0],"source_pts_logged_from_decode":True,
                  "frame_sha256":sha256_file(frame),"target_time_s":chosen[i]}
        entries.append(evidence)
    return entries


def check_candidate(video,sha,folder,pts,check_motion=inspect_source_motion):
    frame=Path(folder)/pts["filename"]
    if not frame.is_file() or sha256_file(frame)!=pts["frame_sha256"]:
        raise ValueError("V146_SOURCE_FRAME_SHA_MISMATCH")
    score=measure(frame)
    base=pts["source_time_base"]
    numerator,denominator=(int(x) for x in base.split("/"))
    if numerator<=0 or denominator<=0:
        raise ValueError("V146_INVALID_TIME_BASE")
    period=Fraction(numerator,denominator)
    freeze=pts["source_pts"]
    start=math.ceil(Fraction(str(max(0,pts["source_pts_time_s"]-1.35)))/period)
    ok,reason=check_source_window(start,freeze,base)
    row={**pts,"original_picture_content":score["source_picture_content_eligible"],
         "original_native_detail":score["source_native_detail_sufficient"],
         "visual_quality_advisory":score["source_visual_quality_score"],
         "source_picture_guard":score["source_picture_content_rejection"],
         "start_pts":start,"freeze_pts":freeze,"time_base":base,
         "pre_freeze_length_s":round(float((freeze-start)*period),4),
         "motion_verified":False,
         "rights_italy_verified":False,"artistically_approved":False}
    if not ok or not row["original_picture_content"] or not row["original_native_detail"]:
        return {**row,"status":"BLOCKED","reason":(reason if not ok else
                     "SOURCE_INTERTITLE_OR_NATIVE_DETAIL_BLOCKED")}
    movement=check_motion(video,sha,start,freeze,base)
    return {**row,"status":("MOTION_EVIDENCE_PASS_REVIEW_REQUIRED" if
                movement.get("status")=="MOTION_EVIDENCE_PASS" and
                movement.get("motion_verified") is True else "BLOCKED"),
            "reason":movement.get("reason"),"motion_verified":movement.get("motion_verified") is True
                          and movement.get("status")=="MOTION_EVIDENCE_PASS",
            "motion_sample_count":movement.get("sample_count",0),
            "motion_changed_pairs":movement.get("changed_pairs",0),
            "motion_spatial_delta":movement.get("max_spatial_pixel_delta",0)}


def select_five_film_sources(reels):
    """Each selected scene MUST belong to a different original verified SHA."""
    if not isinstance(reels,list):
        raise ValueError("V146_INVALID_REELS")
    selected=[];used_sha=set();used_pages=set()
    for row in reels:
        if not isinstance(row,dict):
            continue
        best=row.get("best_moving_freeze")
        digest=row.get("original_sha256")
        page=row.get("source_page")
        if (row.get("status")!="V146_ONE_MOVING_ORIGINAL_SOURCE_REVIEW_ONLY"
                or not isinstance(best,dict)
                or best.get("motion_verified") is not True
                or best.get("original_picture_content") is not True
                or best.get("original_native_detail") is not True
                or not isinstance(digest,str) or SHA.fullmatch(digest) is None
                or not isinstance(page,str) or not page.startswith("https://commons.wikimedia.org/wiki/File:")
                or digest in used_sha or page in used_pages):
            continue
        used_sha.add(digest);used_pages.add(page)
        selected.append({
            "reel_id":row["reel_id"],"source_page":page,"source_sha256":digest,
            "source_original_sha1":row.get("original_sha1"),"year":row["year"],
            "place_label":row["place_label"],"freeze":best,
            "true_physical_camera_shot_approved":False,
            "modern_photo_i2i_approved":False,"vidu_clip_approved":False})
        if len(selected)==MIN_MOVING_REELS:
            break
    return selected if len(selected)==MIN_MOVING_REELS else []


def contact_sheet(reels,root):
    board=Image.new("RGB",(1500,980),(20,20,22))
    d=ImageDraw.Draw(board)
    for i,row in enumerate(reels):
        x=20+(i%3)*500;y=20+(i//3)*480
        d.text((x+8,y+4),f"{i+1}  {row['reel_id']}",fill="white")
        pick=row.get("best_moving_freeze") or next(iter(row.get("candidate_frames",[])),None)
        frame=root/"original_files"/row["reel_id"]/"frames"/(pick["filename"] if pick else "missing.png")
        if frame.is_file():
            with Image.open(frame) as im:
                im=im.convert("RGB");im.thumbnail((475,390))
                board.paste(im,(x+8,y+36))
        d.text((x+8,y+438),str(row.get("status","ERROR"))[:75],fill="#DDDDDD")
    output=root/"SIX_ARCHIVAL_REELS_CONTACT_SHEET_V146.jpg"
    board.save(output,quality=87,optimize=True)


def audit(manifest_file, outdir, *, lookup=metadata, motion=inspect_source_motion,
          download=download_source):
    m=json.loads(Path(manifest_file).read_text(encoding="utf-8"))
    films=validate_manifest(m)
    root=Path(outdir);root.mkdir(parents=True,exist_ok=True)
    results=[];planned_total=0
    for film in films:
        row={
            "reel_id":film["id"],"source_page":film["page"],
            "year":film["year"],"place_label":film["place_label"],
            "status":"V146_REEL_NOT_PROCESSED","candidate_frames":[],
            "best_moving_freeze":None,"original_sha256":None,
            "rights_italy_verified":False,"artistically_approved":False,
            "image_to_image_generated":False,"vidu_generated":False}
        results.append(row)
        try:
            meta=lookup(film["page"])
            if meta.get("source_page") != film["page"]:
                raise ValueError("V146_COMMONS_METADATA_SOURCE_PAGE_DIFFERENT")
            native=native_raster_preflight(meta)
            if not native["native_raster_eligible"]:
                raise ValueError("V146_COMMONS_ORIGINAL_NATIVE_DETAIL_TOO_LOW")
            size=meta.get("size_bytes")
            if type(size) is not int or size>m["max_original_source_bytes_each"] or size<=0:
                raise ValueError("V146_REEL_TOO_LARGE_OR_UNKNOWN")
            planned_total+=size
            if planned_total>m["max_combined_original_source_bytes"]:
                raise ValueError("V146_TOTAL_ARCHIVAL_DOWNLOAD_LIMIT")
            reelroot=root/"original_files"/film["id"]
            path=reelroot/"ORIGINAL_ARCHIVE.webm"
            row["commons_license_claim"]=meta.get("license_metadata","UNKNOWN")
            row["original_sha1"]=meta.get("original_sha1")
            row["original_sha256"]=download(meta,path,m["max_original_source_bytes_each"])
            duration,probe=probe_real_video(path,meta)
            row["verified_decoded_stream"]=probe
            pics=extract_source_freezes(path,reelroot/"frames",duration)
            candidates=[check_candidate(path,row["original_sha256"],reelroot/"frames",p,motion) for p in pics]
            row["candidate_frames"]=candidates
            moving=[c for c in candidates if c["motion_verified"]]
            if not moving:
                row["status"]="V146_NO_PHOTOGRAPHIC_MOVEMENT_REEL_REJECTED"
            else:
                row["best_moving_freeze"]=max(moving,key=lambda c:(c["visual_quality_advisory"],c["motion_spatial_delta"]))
                row["status"]="V146_ONE_MOVING_ORIGINAL_SOURCE_REVIEW_ONLY"
        except (OSError,ValueError,TypeError,KeyError,subprocess.CalledProcessError,
                subprocess.TimeoutExpired,json.JSONDecodeError) as exc:
            row["status"]="V146_SOURCE_RESEARCH_BLOCKED"
            row["reason"]=str(exc)[:250]
        print("V146_REEL",row["reel_id"],row["status"],"moving",
              sum(c["motion_verified"] for c in row["candidate_frames"]),flush=True)
    chosen=select_five_film_sources(results)
    status=("V146_FIVE_DISTINCT_ORIGINAL_MOVING_REELS_REVIEW_REQUIRED" if chosen
            else "V146_INSUFFICIENT_DISTINCT_MOVING_ARCHIVAL_REELS")
    report={
        "version":"V146_MULTI_REEL_AUTHENTIC_MOVEMENT_AUDIT",
        "status":status,"episode_id":m["episode"],
        "attempted_original_reels":len(results),
        "distinct_moving_original_reels":sum(r["status"]=="V146_ONE_MOVING_ORIGINAL_SOURCE_REVIEW_ONLY" for r in results),
        "real_reels":results,"five_review_candidates":chosen,
        "original_source_shas_verified_for_selected":len({x["source_sha256"] for x in chosen})==5,
        "five_genuine_different_camera_shots_artistically_verified":False,
        "italian_rights_verified":False,"modern_restoration_rights_verified":False,
        "photo_i2i_generated":0,"vidu_clips_generated":0,"api_paid_calls":0,
        "video_completed":False,"publish_permitted":False}
    (root/"MULTI_REEL_AUDIT_V146.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    contact_sheet(results,root)
    print("V146_MULTI_ARCHIVE_RESULT",status,"moving_reels",report["distinct_moving_original_reels"],
          "selected",len(chosen),flush=True)
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",default="config/storia_rivive_v146_five_lumiere_reels.json")
    p.add_argument("--out",default="output/storia_v146_five_original_reels")
    a=p.parse_args()
    try:
        audit(a.manifest,a.out)
    except (ValueError,KeyError,TypeError,JSONDecodeError) as exc:
        raise SystemExit("V146_MANIFEST_FAILURE_NO_SOURCE_APPROVAL: "+str(exc)[:180])
