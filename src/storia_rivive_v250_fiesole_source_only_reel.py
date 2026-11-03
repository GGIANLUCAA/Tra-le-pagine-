#!/usr/bin/env python3
"""V250: assemble the five verified V249 original-film entrances, source-only.
This 7-second proof is NOT an episode. No paid services or publication.
"""
from __future__ import annotations
import argparse, hashlib, json, subprocess, tempfile
from pathlib import Path

def run(film:Path, selection:Path, alignment:Path, frames:Path, out:Path)->dict:
    from storia_rivive_v249_fiesole_short_motion_selection import FILM_SHA, sha
    if film.is_symlink() or sha(film)!=FILM_SHA: raise ValueError("ORIGINAL_FILM_HASH_MISMATCH")
    selected=json.loads(selection.read_text())
    checks=json.loads(alignment.read_text()).get("checks")
    rows=selected.get("preselected")
    times=selected.get("candidate_segment_times_s")
    if selected.get("status")!="FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW" or not all(isinstance(x,list) and len(x)==5 for x in (checks,rows,times)):
        raise ValueError("V249_FIVE_VERIFIED_SELECTION_REQUIRED")
    shots=[]
    for row,t,check in zip(rows,times,checks):
        name=row.get("filename")
        path=frames/name
        if path.is_symlink() or not path.is_file() or sha(path)!=check.get("source_frame_sha256"):
            raise ValueError("SOURCE_FRAME_HASH_MISMATCH")
        if name!=check.get("source_frame") or abs(float(t)-float(check.get("selected_timecode_s",-1)))>.002 or check.get("endpoint_visually_aligned") is not True:
            raise ValueError("SOURCE_ALIGNMENT_MISMATCH")
        if not 1.4<float(t): raise ValueError("INVALID_WINDOW")
        shots.append({"frame":name,"sha256":sha(path),"start_s":round(float(t)-1.4,3),"end_s":float(t)})
    if len({s["frame"] for s in shots})!=5:raise ValueError("DUPLICATE_SOURCE")
    out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="storia-v250-") as td:
        directory=Path(td);segments=[]
        for i,shot in enumerate(shots):
            seg=directory/f"segment_{i:02d}.mp4"
            subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
                "-ss",str(shot["start_s"]),"-i",str(film),"-an",
                "-vf","scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,format=gray,fps=24,format=yuv420p",
                "-frames:v","34","-c:v","libx264","-preset","veryfast","-crf","22",str(seg)],
                check=True,timeout=100)
            probe=json.loads(subprocess.run(["ffprobe","-v","error","-count_frames","-select_streams","v:0",
                "-show_entries","stream=nb_read_frames","-of","json",str(seg)],
                check=True,capture_output=True,text=True,timeout=30).stdout)
            if int(probe["streams"][0]["nb_read_frames"])!=34:raise ValueError("INVALID_SEGMENT_FRAME_COUNT")
            segments.append(seg)
        concat=directory/"files.txt"
        concat.write_text("".join(f"file '{p.name}'\n" for p in segments))
        subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
            "-f","concat","-safe","0","-i",str(concat),"-c","copy","-movflags","+faststart",
            str(out.resolve())],cwd=directory,check=True,timeout=90)
    probe=json.loads(subprocess.run(["ffprobe","-v","error","-count_frames","-select_streams","v:0",
        "-show_entries","stream=nb_read_frames,codec_name,width,height:format=duration",
        "-of","json",str(out)],check=True,capture_output=True,text=True,timeout=30).stdout)
    stream=probe["streams"][0]
    if (int(stream["nb_read_frames"])!=170 or stream["codec_name"]!="h264"
        or (stream["width"],stream["height"])!=(720,1280)
        or not 7<=float(probe["format"]["duration"])<=7.2):
        raise ValueError("V250_REAL_DECODE_QA_FAILED")
    result={"version":"V250_FIESOLE_FIVE_REAL_SHORT_ENTRANCES",
        "status":"SOURCE_ONLY_REVIEW_NOT_FINAL","source_sha256":FILM_SHA,
        "source_frames":shots,"decoded_frames":170,"duration_s":float(probe["format"]["duration"]),
        "i2i_count":0,"vidu_count":0,"italian_rights_verified":False,
        "human_artistic_approval":False,"final_mp4":False,"final_zip":False,
        "publish_allowed":False,"new_final_episodes_delivered":0}
    out.with_suffix(".json").write_text(json.dumps(result,indent=2)+"\n")
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for name in ("film","selection","alignment","frames","out"):
        p.add_argument("--"+name,required=True,type=Path)
    a=p.parse_args()
    print(run(a.film,a.selection,a.alignment,a.frames,a.out)["status"])
