#!/usr/bin/env python3
"""V147: resume genuine Commons source audits in two small rate-limit-safe batches.

Three previously verified archive originals MUST NOT be re-downloaded.
This module validates the whole five-source recovery manifest, downloads
only one named group (3 or 2 files), and reuses V146 SHA1/FFprobe/PTS/motion
without weakening source gates or making any paid call.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image,ImageDraw

try:
    from src.storia_rivive_scout_v101 import metadata, native_raster_preflight
    from src.storia_rivive_v146_multi_reel_audit import (
        download_source,probe_real_video,extract_source_freezes,check_candidate)
except ModuleNotFoundError:
    from storia_rivive_scout_v101 import metadata, native_raster_preflight
    from storia_rivive_v146_multi_reel_audit import (
        download_source,probe_real_video,extract_source_freezes,check_candidate)


def validate_config(config):
    if (not isinstance(config,dict)
        or config.get("version")!="V147_ARCHIVE_RECOVERY_TWO_THROTTLE_SAFE_BATCHES"
        or any(config.get(k) is not False for k in (
            "rights_italy_verified","modern_derivative_rights_verified",
            "human_artist_approved","paid_api_permitted","publish_permitted"))
        or config.get("max_original_source_bytes_each")!=75_000_000
        or config.get("max_batch_original_source_bytes")!=120_000_000):
        raise ValueError("V147_BATCH_CONTRACT_INVALID")
    batches=config.get("source_batches")
    if not isinstance(batches,list) or len(batches)!=2:
        raise ValueError("V147_EXACT_TWO_BATCHES_REQUIRED")
    seen_ids=set();seen_pages=set()
    for b in batches:
        if (not isinstance(b,dict) or b.get("id") not in ("a","b")
            or not isinstance(b.get("reels"),list)
            or len(b["reels"])!=(3 if b["id"]=="a" else 2)):
            raise ValueError("V147_INVALID_BATCH_CONTENT")
        for row in b["reels"]:
            if not isinstance(row,dict):
                raise ValueError("V147_REEL_INVALID")
            key,page=row.get("id"),row.get("page")
            u=urlparse(page) if isinstance(page,str) else None
            if (not isinstance(key,str) or not re.fullmatch(r"[a-z][a-z0-9_]{6,65}",key)
                    or key in seen_ids or page in seen_pages
                    or not u or u.scheme!="https" or u.netloc!="commons.wikimedia.org"
                    or not u.path.startswith("/wiki/File:")
                    or type(row.get("year")) is not int or not 1880<=row["year"]<=1930):
                raise ValueError("V147_UNTRUSTED_OR_DUPLICATED_REEL")
            seen_ids.add(key);seen_pages.add(page)
    if {b["id"] for b in batches}!={"a","b"} or len(seen_ids)!=5:
        raise ValueError("V147_DUPLICATE_BATCH_ID_OR_REEL")
    baseline=config.get("baseline_evidence")
    if (not isinstance(baseline,dict) or baseline.get("run")!=41221612482
            or baseline.get("artifact_id")!=13050560931
            or baseline.get("verified_originals")!=3
            or baseline.get("moving_reels")!=1):
        raise ValueError("V147_PREVIOUS_REAL_AUDIT_REFERENCE_INVALID")
    return {b["id"]:b["reels"] for b in batches}


def audit_batch(manifest,outdir,batch,*,lookup=metadata,download=download_source,
                probe=probe_real_video,extract=extract_source_freezes,judge=check_candidate):
    config=json.loads(Path(manifest).read_text(encoding="utf-8"))
    batches=validate_config(config)
    if batch not in batches:
        raise ValueError("V147_UNSUPPORTED_BATCH_ID")
    root=Path(outdir);root.mkdir(parents=True,exist_ok=True)
    results=[];download_planned=0
    for item in batches[batch]:
        row={
            "reel_id":item["id"],"source_page":item["page"],"year":item["year"],
            "place_label":item["place_label"],"subject_group":item["subject_group"],
            "status":"V147_SOURCE_NOT_PROCESSED",
            "candidate_frames":[],"best_moving_freeze":None,
            "rights_italy_verified":False,"modern_derivative_rights_verified":False,
            "artistically_approved":False,"original_sha256":None}
        results.append(row)
        try:
            info=lookup(item["page"])
            if info.get("source_page")!=item["page"]:
                raise ValueError("V147_ARCHIVE_SOURCE_PAGE_MISMATCH")
            if not native_raster_preflight(info)["native_raster_eligible"]:
                raise ValueError("V147_NATIVE_ORIGINAL_RASTER_TOO_LOW")
            size=info.get("size_bytes")
            if type(size) is not int or size<=0 or size>config["max_original_source_bytes_each"]:
                raise ValueError("V147_REEL_EXCEEDS_75MB_BOUND")
            download_planned+=size
            if download_planned>config["max_batch_original_source_bytes"]:
                raise ValueError("V147_BATCH_120MB_BOUND")
            directory=root/"original_files"/item["id"]
            film=directory/"ORIGINAL_ARCHIVE.webm"
            row["commons_license_claim"]=info.get("license_metadata")
            row["original_sha1"]=info.get("original_sha1")
            row["original_sha256"]=download(info,film,config["max_original_source_bytes_each"])
            duration,probed=probe(film,info)
            row["verified_decoded_stream"]=probed
            candidates=extract(film,directory/"frames",duration)
            scored=[judge(film,row["original_sha256"],directory/"frames",candidate)
                    for candidate in candidates]
            row["candidate_frames"]=scored
            moving=[r for r in scored if r.get("motion_verified") is True and
                    r.get("original_picture_content") is True and r.get("original_native_detail") is True]
            if moving:
                row["best_moving_freeze"]=max(moving,key=lambda r:(r["visual_quality_advisory"],r["motion_spatial_delta"]))
                row["status"]="V146_ONE_MOVING_ORIGINAL_SOURCE_REVIEW_ONLY"
            else:
                row["status"]="V147_NO_SAFE_MOVEMENT"
        except (OSError,ValueError,TypeError,KeyError,TimeoutError) as exc:
            row["status"]="V147_RESEARCH_BLOCKED_NOT_SOURCE_REJECTED"
            row["reason"]=str(exc)[:250]
        print("V147_REAL_REEL",batch,row["reel_id"],row["status"],
              "moving",sum(x.get("motion_verified") is True for x in row["candidate_frames"]),flush=True)
    result={
        "version":"V147_TWO_BATCH_NO_REDOWNLOAD_ARCHIVAL_RESEARCH",
        "batch":batch,"status":"V147_SOURCE_REVIEW_ONLY",
        "source_reels":results,
        "sources_checked":len(results),
        "original_source_bytes_budget":download_planned,
        "previous_v146_originals_reused_not_redownloaded":3,
        "rights_italy_verified":False,"modern_restoration_rights_verified":False,
        "human_artistic_approved":False,"photo_i2i_generated":0,
        "vidu_clips_generated":0,"api_paid_calls":0,"publish_permitted":False,
        "video_completed":False}
    (root/"V147_BATCH_REPORT.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    sheet=Image.new("RGB",(1350,530),(19,20,22));draw=ImageDraw.Draw(sheet)
    for i,row in enumerate(results):
        x=i*450
        draw.text((x+8,12),row["reel_id"][:46],fill="white")
        shot=row.get("best_moving_freeze") or (row["candidate_frames"][0] if row["candidate_frames"] else None)
        frame=(root/"original_files"/row["reel_id"]/"frames"/shot["filename"]) if shot else None
        if frame and frame.is_file():
            with Image.open(frame) as im:
                im=im.convert("RGB");im.thumbnail((426,420))
                sheet.paste(im,(x+8,45))
        draw.text((x+8,488),row["status"][:56],fill="white")
    sheet.save(root/"V147_BATCH_CONTACT_SHEET.jpg",quality=87,optimize=True)
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",default="config/storia_rivive_v147_remaining_five_reels.json")
    p.add_argument("--batch",required=True,choices=["a","b"])
    p.add_argument("--out",required=True)
    args=p.parse_args()
    result=audit_batch(args.manifest,args.out,args.batch)
    print("V147_BATCH_DONE",args.batch,len(result["source_reels"]),"paid_calls",0)
