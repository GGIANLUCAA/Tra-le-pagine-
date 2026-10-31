#!/usr/bin/env python3
"""V150: reuse FOUR genuine V149 MP4s + validate ONE recovered workers source.

Do not trust similarly named clips: require real original source SHA1/SHA256,
frame freeze PNG SHA, source PTS and normalized video SHA before V149 concat.
No image enhancement, Vidu, cost, publication or artistic signoff.
"""
from __future__ import annotations
import argparse
import json
import shutil
from pathlib import Path

try:
    from src.storia_rivive_v149_authentic_bw_proxy import validate,sha256_file,probe_clip
    from src.storia_rivive_v149_combine_bw_preview import assemble
except ModuleNotFoundError:
    from storia_rivive_v149_authentic_bw_proxy import validate,sha256_file,probe_clip
    from storia_rivive_v149_combine_bw_preview import assemble


def merge(prior_a,prior_b,latest,manifest,out):
    sources=validate(json.loads(Path(manifest).read_text(encoding="utf-8")))
    folder_a=Path(prior_a);folder_b=Path(prior_b);new=Path(latest)
    a=folder_a/"BW_PREVIEW_SOURCE_REPORT_V149.json"
    b=folder_b/"BW_PREVIEW_SOURCE_REPORT_V149.json"
    recovery=new/"V150_WORKERS_RECOVERY_REPORT.json"
    for file in (a,b,recovery):
        if not file.is_file() or file.is_symlink():
            raise ValueError("V150_EXPECTED_REAL_PRIOR_ARTIFACT_MISSING")
    old_a=json.loads(a.read_text(encoding="utf-8"))
    old_b=json.loads(b.read_text(encoding="utf-8"))
    record=json.loads(recovery.read_text(encoding="utf-8"))
    if (old_a.get("batch")!="a" or old_b.get("batch")!="b"
            or old_a.get("status")!="V149_ORIGINAL_BW_PREVIEW_INCOMPLETE"
            or old_a.get("clips_verified")!=2 or len(old_a.get("source_clips",[]))!=3
            or old_b.get("status")!="V149_ORIGINAL_BW_CLIPS_READY_FOR_PRIVATE_QA"
            or old_b.get("clips_verified")!=2 or len(old_b.get("source_clips",[]))!=2
            or record.get("version")!="V150_ONE_MISSING_REAL_FILM_RECOVERY"
            or record.get("status")!="V150_WORKERS_REAL_BW_SOURCE_MP4_RECOVERED"
            or record.get("prior_run")!=41223340544
            or record.get("prior_original_artifacts")!=[13050324762,13050802833]
            or record.get("original_source_reused_not_redownloaded_count")!=4
            or record.get("paid_calls")!=0 or record.get("video_finished") is not False
            or record.get("rights_italy_verified") is not False
            or record.get("publish_permitted") is not False):
        raise ValueError("V150_PRIOR_RESEARCH_OR_RECOVERY_STATUS_INVALID")
    row=record.get("clip")
    expected=sources[2]
    if (not isinstance(row,dict) or row.get("status")!="V149_TRUE_SOURCE_BW_MOVING_MP4_REVIEW_ONLY"
            or row.get("scene")!=3 or row.get("id")!=expected["id"]
            or row.get("source_page")!=expected["source_page"]
            or row.get("source_sha256")!=expected["original_sha256"]
            or row.get("verified_freeze_frame_sha256")!=expected["frame_sha256"]
            or row.get("start_pts")!=expected["start_pts"]
            or row.get("freeze_pts")!=expected["freeze_pts"]
            or row.get("time_base")!=expected["time_base"]
            or row.get("clip_filename")!="scene_03_BW_SOURCE_PREVIEW.mp4"):
        raise ValueError("V150_RECOVERED_ORIGINAL_SOURCE_SHA_PTS_CHANGED")
    original_failed=old_a["source_clips"][2]
    if (original_failed.get("scene")!=3 or original_failed.get("id")!=row["id"]
            or original_failed.get("status")!="V149_ARCHIVE_OR_PREVIEW_BLOCKED_NOT_APPROVED"
            or "429" not in original_failed.get("reason","")):
        raise ValueError("V150_NOT_PREVIOUSLY_MISSING_SAME_SOURCE_429")
    file=new/"preview_clips"/row["clip_filename"]
    if (not file.is_file() or file.is_symlink()
            or sha256_file(file)!=row.get("clip_sha256")):
        raise ValueError("V150_RECOVERED_MP4_BYTES_MISMATCH")
    probe_clip(file)
    # Reconstitute only a small working copy of the four prior clip artifact
    # files plus the one genuinely new worker clip. The source films stay out.
    root=Path(out)
    aout=root/"batch_a";bout=root/"batch_b"
    for source,dest in ((folder_a,aout),(folder_b,bout)):
        dest.mkdir(parents=True,exist_ok=True)
        for entry in source.rglob("*"):
            if not entry.is_file() or entry.is_symlink():
                continue
            rel=entry.relative_to(source)
            if rel.name!="BW_PREVIEW_SOURCE_REPORT_V149.json" and (
                    not rel.name.endswith("_BW_SOURCE_PREVIEW.mp4")):
                continue
            dst=dest/rel;dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(entry,dst)
    moved=aout/"preview_clips"/row["clip_filename"]
    moved.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(file,moved)
    if sha256_file(moved)!=row["clip_sha256"]:
        raise ValueError("V150_COPIED_MP4_CHANGED")
    old_a["source_clips"][2]=row
    old_a["clips_verified"]=3
    old_a["status"]="V149_ORIGINAL_BW_CLIPS_READY_FOR_PRIVATE_QA"
    (aout/"BW_PREVIEW_SOURCE_REPORT_V149.json").write_text(
        json.dumps(old_a,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return root


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--old-a",required=True)
    parser.add_argument("--old-b",required=True)
    parser.add_argument("--recovery",required=True)
    parser.add_argument("--manifest",default="config/storia_rivive_v149_five_original_motion_preview.json")
    parser.add_argument("--workdir",required=True)
    parser.add_argument("--out",required=True)
    a=parser.parse_args()
    dst=merge(a.old_a,a.old_b,a.recovery,a.manifest,a.workdir)
    status=assemble(a.manifest,dst,a.out)
    print("V150_FIRST_FIVE_REAL_BW_MOVING_REELS",status["status"],
          "runtime",status["duration_seconds"],
          "source_count",status["original_film_count"],
          "paid_calls",0,"real_i2i",0,"real_vidu",0,"finished",False)
