#!/usr/bin/env python3
"""V147: join two no-credit Commons batches and previously verified V146 bytes.

Never re-download the three original films audited in Actions #41221612482.
A five-film source review PASS is NOT photo I2I, a Vidu clip, rights clearance,
five different genuine camera shots, or a video master.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

try:
    from src.storia_rivive_v146_multi_reel_audit import select_five_film_sources
    from src.storia_rivive_v147_archival_rate_limit_batches import validate_config
except ModuleNotFoundError:
    from storia_rivive_v146_multi_reel_audit import select_five_film_sources
    from storia_rivive_v147_archival_rate_limit_batches import validate_config

SHA=re.compile(r"[0-9a-f]{64}\Z")


def aggregate(config_path,baseline_path,batch_dir,outfile):
    config=json.loads(Path(config_path).read_text(encoding="utf-8"))
    batches=validate_config(config)
    baseline=json.loads(Path(baseline_path).read_text(encoding="utf-8"))
    if (baseline.get("version")!="V147_ORIGINAL_PREVIOUS_RUN_EVIDENCE_REVIEW_ONLY"
            or baseline.get("source_run")!=config["baseline_evidence"]["run"]
            or baseline.get("source_artifact")!=config["baseline_evidence"]["artifact_id"]
            or baseline.get("verified_original_sha_count")!=3
            or baseline.get("unapproved") is not True
            or baseline.get("italy_rights_verified") is not False
            or baseline.get("paid_api_calls")!=0):
        raise ValueError("V147_PREVIOUS_SHA_BOUND_AUDIT_INVALID")
    first=baseline.get("first_three_originals")
    if not isinstance(first,list) or len(first)!=3:
        raise ValueError("V147_PREVIOUS_THREE_REELS_INCOMPLETE")
    desired={r["id"]:r["page"] for group in batches.values() for r in group}
    baseline_names={"perrache_train_arrival_1896",
                    "lyon_perrache_train_panorama_1896","workers_sidewalk_1898"}
    if {x.get("reel_id") for x in first}!=baseline_names:
        raise ValueError("V147_PREVIOUS_SOURCE_IDS_CHANGED")
    dirs=list(Path(batch_dir).rglob("V147_BATCH_REPORT.json"))
    if len(dirs)!=2:
        raise ValueError("V147_TWO_INDEPENDENT_BATCH_REPORTS_REQUIRED")
    chunks=[json.loads(p.read_text(encoding="utf-8")) for p in dirs]
    if {r.get("batch") for r in chunks}!={"a","b"}:
        raise ValueError("V147_BATCH_IDS_OR_DOWNLOADS_MISSING")
    results=list(first)
    for part in chunks:
        key=part["batch"]
        if (part.get("version")!="V147_TWO_BATCH_NO_REDOWNLOAD_ARCHIVAL_RESEARCH"
                or part.get("status")!="V147_SOURCE_REVIEW_ONLY"
                or part.get("api_paid_calls")!=0 or part.get("video_completed") is not False
                or part.get("publish_permitted") is not False
                or part.get("rights_italy_verified") is not False
                or part.get("previous_v146_originals_reused_not_redownloaded")!=3):
            raise ValueError("V147_PAID_OR_FAKE_BATCH_STATUS")
        rows=part.get("source_reels")
        if not isinstance(rows,list) or len(rows)!=len(batches[key]):
            raise ValueError("V147_BATCH_REEL_COUNT_INVALID")
        for item,expected in zip(rows,batches[key]):
            if item.get("reel_id")!=expected["id"] or item.get("source_page")!=expected["page"]:
                raise ValueError("V147_SOURCE_BINDING_CHANGED")
            if item.get("rights_italy_verified") is not False or item.get("artistically_approved") is not False:
                raise ValueError("V147_FORGED_APPROVAL")
            results.append(item)
    names=[r.get("reel_id") for r in results]
    pages=[r.get("source_page") for r in results]
    if len(results)!=8 or len(set(names))!=8 or len(set(pages))!=8:
        raise ValueError("V147_EIGHT_SOURCE_IDS_OR_PAGES_NOT_UNIQUE")
    for r in results:
        if r.get("original_sha256") is not None and not SHA.fullmatch(r["original_sha256"]):
            raise ValueError("V147_ORIGINAL_VIDEO_SHA_INVALID")
        if r.get("status")=="V146_ONE_MOVING_ORIGINAL_SOURCE_REVIEW_ONLY":
            best=r.get("best_moving_freeze")
            if (not isinstance(best,dict)
                    or best.get("motion_verified") is not True
                    or best.get("original_picture_content") is not True
                    or best.get("original_native_detail") is not True
                    or not isinstance(best.get("frame_sha256"),str)
                    or SHA.fullmatch(best["frame_sha256"]) is None):
                raise ValueError("V147_MOTION_OR_PHOTO_EVIDENCE_FORGED")
    # Stable editorial order: train, then four different types, boat as fallback.
    editorial_order=["lyon_perrache_train_panorama_1896",
                     "rough_port_1899","girl_cat_1900","children_marbles_1896",
                     "martinique_market_1902","moving_whaleboat_1897",
                     "perrache_train_arrival_1896","workers_sidewalk_1898"]
    lookup={row["reel_id"]:row for row in results}
    chosen=select_five_film_sources([lookup[key] for key in editorial_order])
    state=("V147_FIVE_DIFFERENT_ORIGINAL_FILMS_HAVE_MOVEMENT_REVIEW_REQUIRED"
           if len(chosen)==5 else "V147_INSUFFICIENT_DIFFERENT_MOVING_ORIGINAL_FILMS")
    report={
        "version":"V147_BATCHED_ORIGINAL_ARCHIVE_AGGREGATE",
        "status":state,
        "baseline_v146_run":baseline["source_run"],
        "original_reels_examined":8,
        "original_reels_reused_from_v146_without_redownload":3,
        "downloaded_in_two_small_independent_jobs":5,
        "moving_original_reel_count":sum(r.get("status")=="V146_ONE_MOVING_ORIGINAL_SOURCE_REVIEW_ONLY"
                                         for r in results),
        "five_review_reels":chosen,
        "all_reels":results,
        "five_real_camera_shots_artistic_review":False,
        "rights_italy_verified":False,
        "modern_restoration_rights_verified":False,
        "new_real_i2i_photos":0,
        "new_real_vidu_clips":0,
        "paid_calls":0,"published":False,"video_finished":False}
    target=Path(outfile);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--manifest",default="config/storia_rivive_v147_remaining_five_reels.json")
    parser.add_argument("--baseline",default="docs/evidence/STORIA_V146_FIRST_3_REAL_FILMS_41221612482.json")
    parser.add_argument("--batch-dir",required=True)
    parser.add_argument("--out",required=True)
    a=parser.parse_args()
    s=aggregate(a.manifest,a.baseline,a.batch_dir,a.out)
    print("V147_EIGHT_DISTINCT_ORIGINAL_FILMS",s["status"],"moving",s["moving_original_reel_count"],
          "five",len(s["five_review_reels"]),"paid_calls",0)
