#!/usr/bin/env python3
"""V247: inspect real moving shots, not just selected freeze endpoints, for title cards.

A valid photographic endpoint can hide a title card earlier in its 4.8s window.
This is a source-only QA signal, not rights or artistic approval.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from PIL import Image
from storia_rivive_v210_shot_aware_selection import likely_intertitle

def check(video: Path, manifest: Path, output: Path) -> dict:
    if video.is_symlink() or not video.is_file():
        raise ValueError("SOURCE_REVIEW_VIDEO_MISSING")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    shots = data.get("shots")
    if data.get("version") != "V243_ARCHIVAL_FREEZE_ENDPOINT_REVIEW" or not isinstance(shots, list) or len(shots) != 5:
        raise ValueError("INVALID_SOURCE_REVIEW_MANIFEST")
    probe = subprocess.run(["ffprobe","-v","error","-select_streams","v:0",
        "-count_frames","-show_entries","stream=nb_read_frames,width,height,r_frame_rate",
        "-of","json",str(video)],check=True,capture_output=True,text=True,timeout=30)
    streams=json.loads(probe.stdout).get("streams",[])
    if len(streams)!=1 or streams[0].get("width")!=720 or streams[0].get("height")!=1280:
        raise ValueError("UNEXPECTED_SOURCE_REVIEW_GEOMETRY")
    count=int(streams[0].get("nb_read_frames") or 0)
    if count!=575 or streams[0].get("r_frame_rate")!="24/1":
        raise ValueError("SOURCE_REVIEW_FRAMECOUNT_MISMATCH")
    # Sample beginning, middle and pre-freeze of EACH actual encoded motion segment.
    offsets=(5,38,77)
    samples=[]
    with tempfile.TemporaryDirectory(prefix="storia-v247-") as tmp:
        folder=Path(tmp)
        for shot_index,shot in enumerate(shots):
            if not isinstance(shot,dict) or not isinstance(shot.get("sha256"),str):
                raise ValueError("INVALID_SHOT_EVIDENCE")
            row={"shot":shot_index+1,"source_frame":shot.get("source_frame"),
                 "samples":[],"title_intrusion":False}
            for frame_offset in offsets:
                frame_index=shot_index*115+frame_offset
                out=folder/f"sample_{frame_index:03}.png"
                subprocess.run(["ffmpeg","-nostdin","-v","error","-y","-i",str(video),
                    "-vf",f"select=eq(n\\,{frame_index})","-vsync","0",
                    "-frames:v","1",str(out)],check=True,timeout=30)
                if not out.is_file() or out.stat().st_size<1000:
                    raise ValueError("SAMPLED_FRAME_MISSING")
                with Image.open(out) as im:
                    if im.format!="PNG" or im.size!=(720,1280):
                        raise ValueError("INVALID_DECODED_FRAME")
                flagged=bool(likely_intertitle(out))
                row["samples"].append({"decoded_frame_index":frame_index,
                    "sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
                    "likely_intertitle":flagged})
                row["title_intrusion"] |= flagged
            samples.append(row)
    flagged_shots=[row["shot"] for row in samples if row["title_intrusion"]]
    report={"version":"V247_DECODED_MOTION_INTERTITLE_REVIEW",
        "status":"REJECT_MOTION_WINDOW_FOR_EDITORIAL_REVIEW" if flagged_shots else "NO_INTERTITLE_HEURISTIC_FLAGS_NOT_ARTISTIC_APPROVAL",
        "source_video_sha256":hashlib.sha256(video.read_bytes()).hexdigest(),
        "sampled_decoded_frames":15,"flagged_shots":flagged_shots,"shots":samples,
        "false_positive_review_required":True,"i2i_approved":False,
        "rights_approved":False,"vidu_approved":False,"final_video":False,
        "new_final_episodes_delivered":0}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    return report

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    for name in ("video","manifest","out"):
        parser.add_argument("--"+name,required=True,type=Path)
    args=parser.parse_args()
    result=check(args.video,args.manifest,args.out)
    print(result["status"],result["flagged_shots"],"NEW_FINAL_0_OF_4")
