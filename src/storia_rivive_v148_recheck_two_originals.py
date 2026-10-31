#!/usr/bin/env python3
"""V148: only two ORIGINAL films from V146, with unchanged SHA and native PTS.

One-time free source research; never writes to I2I, Vidu, social or releases.
Unlike V115's whole-frame 64px mean, V148 can detect small local motion while
mean-centering exposure changes within each 8x8 tile. Manual artistic QA
remains required even if an original source passes.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

try:
    from src.storia_rivive_scout_v101 import metadata,native_raster_preflight
    from src.storia_rivive_v146_multi_reel_audit import download_source,probe_real_video
    from src.storia_rivive_v148_local_motion import inspect_local_original_window
    from src.storia_rivive_motion_window_v115 import check_source_window
except ModuleNotFoundError:
    from storia_rivive_scout_v101 import metadata,native_raster_preflight
    from storia_rivive_v146_multi_reel_audit import download_source,probe_real_video
    from storia_rivive_v148_local_motion import inspect_local_original_window
    from storia_rivive_motion_window_v115 import check_source_window

SHA1=re.compile(r"[0-9a-f]{40}\Z")
SHA256=re.compile(r"[0-9a-f]{64}\Z")


def validate(m):
    if (not isinstance(m,dict) or m.get("version")!="V148_TWO_AUTHENTIC_SHA_BOUND_RECHECKS"
            or m.get("research_only") is not True
            or any(m.get(k) is not False for k in (
                "rights_italy_verified","artistically_approved",
                "vidu_permitted","photo_i2i_permitted","publish_permitted"))):
        raise ValueError("V148_CONTRACT_INVALID")
    prev=m.get("original_checks_from",{})
    if prev.get("V146_run")!=41221612482 or prev.get("V146_artifact")!=13050560931:
        raise ValueError("V148_PREVIOUS_REAL_SOURCE_EVIDENCE_MISSING")
    sources=m.get("sources")
    if not isinstance(sources,list) or len(sources)!=2 or {r.get("id") for r in sources}!={
            "perrache_train_arrival_1896","workers_sidewalk_1898"}:
        raise ValueError("V148_TWO_SOURCE_IDS_REQUIRED")
    seen=set()
    for item in sources:
        p=item.get("page")
        uri=urlparse(p) if isinstance(p,str) else None
        if (not uri or uri.scheme!="https" or uri.netloc!="commons.wikimedia.org"
                or not uri.path.startswith("/wiki/File:") or p in seen
                or item.get("prior_v115_status")!="V146_NO_PHOTOGRAPHIC_MOVEMENT_REEL_REJECTED"
                or not isinstance(item.get("original_sha256"),str)
                or SHA256.fullmatch(item["original_sha256"]) is None
                or not isinstance(item.get("original_sha1"),str)
                or SHA1.fullmatch(item["original_sha1"]) is None
                or item.get("original_w")!=1920 or item.get("original_h")!=1080):
            raise ValueError("V148_SOURCE_SHA_OR_IDENTITY_INVALID")
        seen.add(p)
        windows=item.get("verified_windows")
        if not isinstance(windows,list) or len(windows)!=3:
            raise ValueError("V148_PREVIOUS_PTS_EVIDENCE_MISSING")
        for entry in windows:
            if (not isinstance(entry,dict)
                    or not isinstance(entry.get("original_frame_sha256"),str)
                    or SHA256.fullmatch(entry["original_frame_sha256"]) is None
                    or entry.get("time_base")!="1/1000"):
                raise ValueError("V148_ORIGINAL_FRAME_SHA_OR_TIMEBASE_INVALID")
            ok,reason=check_source_window(entry.get("start_pts"),entry.get("freeze_pts"),
                                          entry.get("time_base"))
            if not ok:
                raise ValueError("V148_BAD_ORIGINAL_FRAME_WINDOW_"+reason)
    return sources


def audit(manifest,outdir,*,lookup=metadata,download=download_source,
          probe=probe_real_video,check=inspect_local_original_window):
    config=json.loads(Path(manifest).read_text(encoding="utf-8"))
    files=validate(config)
    folder=Path(outdir);folder.mkdir(parents=True,exist_ok=True)
    source_reports=[]
    for item in files:
        row={"id":item["id"],"source_page":item["page"],
             "expected_original_sha256":item["original_sha256"],
             "motion_windows":[],"status":"V148_NOT_STARTED",
             "human_artistic_review":False,"rights_italy_verified":False}
        source_reports.append(row)
        try:
            live=lookup(item["page"])
            if (live.get("source_page")!=item["page"]
                    or live.get("original_sha1")!=item["original_sha1"]):
                raise ValueError("V148_ARCHIVAL_CONTENT_FINGERPRINT_CHANGED")
            if not native_raster_preflight(live)["native_raster_eligible"]:
                raise ValueError("V148_ORIGINAL_RASTER_NO_LONGER_ELIGIBLE")
            film=folder/"original_files"/(item["id"]+".webm")
            actual=download(live,film,75_000_000)
            if actual!=item["original_sha256"]:
                raise ValueError("V148_PREVIOUS_ORIGINAL_SHA256_CHANGED")
            _,actual_probe=probe(film,live)
            row["verified_original_sha256"]=actual
            row["decoded_video"]=actual_probe
            passes=0
            for window in item["verified_windows"]:
                event=check(film,actual,
                            window["start_pts"],window["freeze_pts"],window["time_base"])
                record={**window,**event}
                row["motion_windows"].append(record)
                if event.get("status")=="V148_LOCAL_MOTION_PASS_REVIEW_ONLY" and event.get("motion_verified") is True:
                    passes+=1
            row["verified_local_motion_windows"]=passes
            row["status"]=("V148_ORIGINAL_MOVING_SUBJECT_REVIEW_ONLY" if passes else
                            "V148_NO_PERSISTENT_LOCAL_SOURCE_MOTION")
        except (OSError,ValueError,TypeError,KeyError,TimeoutError) as exc:
            row["status"]="V148_SOURCE_RECHECK_BLOCKED_NOT_APPROVED"
            row["reason"]=str(exc)[:240]
        print("V148_SOURCE",row["id"],row["status"],
              row.get("verified_local_motion_windows",0),flush=True)
    count=sum(x["status"]=="V148_ORIGINAL_MOVING_SUBJECT_REVIEW_ONLY" for x in source_reports)
    report={
        "version":"V148_TWO_EXACT_SOURCE_LOCAL_MOTION_RECHECK",
        "status":("V148_TWO_ADDITIONAL_MOVING_REELS_NEED_ARTISTIC_REVIEW" if count==2
                  else "V148_NOT_ENOUGH_LOCAL_MOTION_NEW_FILMS"),
        "sources":source_reports,
        "additional_local_moving_reels":count,
        "original_baseline_v146_run":41221612482,
        "existing_v147_moving_reels":3,
        "possible_total_distinct_moving_original_reels":count+3,
        "five_genuine_camera_shots_artistic_review":False,
        "rights_italy_verified":False,"modern_restoration_rights_verified":False,
        "real_i2i_photos_generated":0,"vidu_clips_generated":0,"paid_calls":0,
        "video_finished":False,"published":False}
    (folder/"V148_TWO_ORIGINALS_RECHECK.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",default="config/storia_rivive_v148_two_source_local_motion_recheck.json")
    p.add_argument("--out",default="output/storia_v148_two_recheck")
    args=p.parse_args()
    result=audit(args.manifest,args.out)
    print("V148_STRICT_LOCAL_SOURCE_RESULT",result["status"],"passes",
          result["additional_local_moving_reels"],"paid",0)
