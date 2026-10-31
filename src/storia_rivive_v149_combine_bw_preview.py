#!/usr/bin/env python3
"""V149: concat ONLY five SHA-verified authentic source-only B/W previews.

Not a finished 4-I2I/1-Vidu historical restoration. No color restoration,
I2I, Vidu, inferred camera-shot identity, music, Italian rights or publishing.
Must not mark any technical preflight as an artistic endorsement.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
from pathlib import Path

try:
    from src.storia_rivive_v149_authentic_bw_proxy import validate, probe_clip, sha256_file
except ModuleNotFoundError:
    from storia_rivive_v149_authentic_bw_proxy import validate, probe_clip, sha256_file


def assemble(manifest, artifacts, output):
    m=json.loads(Path(manifest).read_text(encoding="utf-8"))
    sources=validate(m)
    root=Path(artifacts)
    reports=sorted(root.rglob("BW_PREVIEW_SOURCE_REPORT_V149.json"))
    if len(reports)!=2:
        raise ValueError("V149_TWO_INDEPENDENT_SOURCE_BATCH_REPORTS_REQUIRED")
    payload=[json.loads(path.read_text(encoding="utf-8")) for path in reports]
    if {x.get("batch") for x in payload}!={"a","b"}:
        raise ValueError("V149_DUPLICATED_OR_MISSING_SOURCE_BATCH")
    indexed={}
    for batch in payload:
        name=batch["batch"]
        if (batch.get("version")!=m["version"]
                or batch.get("status")!="V149_ORIGINAL_BW_CLIPS_READY_FOR_PRIVATE_QA"
                or batch.get("clips_verified")!=(3 if name=="a" else 2)
                or batch.get("paid_api_calls")!=0
                or batch.get("is_finished_video") is not False
                or batch.get("publish_permitted") is not False
                or batch.get("rights_italy_verified") is not False
                or batch.get("artistic_approved") is not False
                or batch.get("new_true_i2i_photos")!=0
                or batch.get("new_vidu_clips")!=0):
            raise ValueError("V149_FAILED_OR_UNAPPROVED_SOURCE_BATCH")
        for row in batch.get("source_clips",[]):
            index=row.get("scene")
            if type(index) is not int or index in indexed or index not in range(1,6):
                raise ValueError("V149_DUPLICATED_OR_UNKNOWN_SOURCE_SCENE")
            indexed[index]=(row,name)
    if set(indexed)!={1,2,3,4,5}:
        raise ValueError("V149_NOT_FIVE_SOURCE_SCENES")
    selected=[];seen_hashes=set()
    for source in sources:
        i=source["scene"]
        row,batch=indexed[i]
        expected=f"scene_{i:02d}_BW_SOURCE_PREVIEW.mp4"
        if (source["batch"]!=batch or row.get("id")!=source["id"]
                or row.get("source_page")!=source["source_page"]
                or row.get("source_sha256")!=source["original_sha256"]
                or row.get("verified_freeze_frame_sha256")!=source["frame_sha256"]
                or row.get("start_pts")!=source["start_pts"]
                or row.get("freeze_pts")!=source["freeze_pts"]
                or row.get("time_base")!=source["time_base"]
                or row.get("status")!="V149_TRUE_SOURCE_BW_MOVING_MP4_REVIEW_ONLY"
                or row.get("clip_filename")!=expected
                or row.get("original_source_timecodes_verified") is not True):
            raise ValueError("V149_SOURCE_PROVENANCE_SHA_PTS_MISMATCH")
        if row["source_sha256"] in seen_hashes:
            raise ValueError("V149_REPEATED_ARCHIVAL_SOURCE_FILM")
        seen_hashes.add(row["source_sha256"])
        candidate=reports[0].parent/expected
        # Artifacts are uploaded with batch names, not simply at root.
        found=list(root.rglob(expected))
        if len(found)!=1 or not found[0].is_file() or found[0].is_symlink():
            raise ValueError("V149_MISSING_OR_DUPLICATED_VIDEO_CLIP_ARTIFACT")
        candidate=found[0]
        if sha256_file(candidate)!=row.get("clip_sha256"):
            raise ValueError("V149_NORMALIZED_VIDEO_CLIP_SHA_MISMATCH")
        seconds=probe_clip(candidate)
        if abs(seconds-row["proxy_seconds"])>0.034:
            raise ValueError("V149_REPORTED_PROXY_DURATION_CHANGED")
        selected.append({"scene":i,"clip_file":str(candidate.resolve()),"source_sha256":row["source_sha256"],
                         "freeze_sha256":row["verified_freeze_frame_sha256"],
                         "native_pts":[source["start_pts"],source["freeze_pts"]],
                         "proxy_seconds":seconds})
    final=Path(output);final.parent.mkdir(parents=True,exist_ok=True)
    playlist=final.parent/"CONCAT_FIVE_AUTHENTIC_BW_CLIPS_V149.txt"
    lines=["file '"+r["clip_file"].replace("'","'\\''")+"'" for r in selected]
    playlist.write_text("\n".join(lines)+"\n",encoding="utf-8")
    cmd=["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error",
         "-f","concat","-safe","0","-i",str(playlist),"-an",
         "-c:v","copy","-movflags","+faststart",str(final)]
    subprocess.run(cmd,capture_output=True,text=True,check=True,timeout=100)
    duration=probe_final(final)
    if not 6.25<=duration<=7.38:
        raise ValueError("V149_FIVE_CLIP_COMBINED_DURATION_WRONG")
    report={
        "version":"V149_SOURCE_ONLY_FIVE_BW_FILMS_NO_RESTORATION",
        "status":"V149_GENUINE_ORIGINAL_BW_MOTION_TECHNICAL_EDITOR_PREVIEW",
        "is_technical_preview_not_final":True,
        "original_film_count":5,"scenes":selected,
        "master_filename":final.name,
        "master_sha256":sha256_file(final),"duration_seconds":duration,
        "raster_px":[720,1280],"video_codec":"h264",
        "audio_included":False,"color_restoration":False,
        "original_source_motion_only":True,"frame_rate_conversion_duplicates_only_no_optical_flow":True,
        "source_motion_evidenced_by_v146_v147_v148":True,
        "five_distinct_true_camera_angles_artistically_verified":False,
        "rights_italy_verified":False,"modern_restoration_rights_verified":False,
        "human_artistic_approval":False,
        "real_i2i_generated":0,"real_vidu_generated":0,"paid_api_calls":0,
        "user_4i2i_1vidu_pilot_finished":False,"publication_permitted":False}
    report_file=final.parent/"BW_TECHNICAL_MASTER_REPORT_V149.json"
    report_file.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report


def probe_final(path):
    p=subprocess.run(["ffprobe","-v","error","-show_entries",
        "format=duration:stream=codec_type,codec_name,width,height",
        "-of","json",str(path)],capture_output=True,text=True,check=True,timeout=25)
    obj=json.loads(p.stdout)
    films=[s for s in obj.get("streams",[]) if s.get("codec_type")=="video"]
    if (len(films)!=1 or films[0].get("codec_name")!="h264"
            or films[0].get("width")!=720 or films[0].get("height")!=1280
            or any(s.get("codec_type")=="audio" for s in obj.get("streams",[]))):
        raise ValueError("V149_COMBINED_VIDEO_NOT_SILENT_H264_PORTRAIT")
    duration=float(obj["format"]["duration"])
    if not math.isfinite(duration):
        raise ValueError("V149_FINAL_DURATION_NONFINITE")
    return duration


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--manifest",default="config/storia_rivive_v149_five_original_motion_preview.json")
    parser.add_argument("--artifacts",required=True)
    parser.add_argument("--out",required=True)
    a=parser.parse_args()
    state=assemble(a.manifest,a.artifacts,a.out)
    print("V149_REAL_FIVE_MOVING_SOURCES_SILENT_EDITOR_PREVIEW",state["status"],
          "duration",state["duration_seconds"],"MP4_SHA",state["master_sha256"],
          "rights",False,"paid",0,"finished",False)
