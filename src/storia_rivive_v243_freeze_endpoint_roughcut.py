#!/usr/bin/env python3
"""V243: source-locked archival roughcut; every shot ENDS on its selected frame.
Review-only: no I2I, Vidu, rights approval or finished-video claim.
"""
from __future__ import annotations
import argparse,hashlib,json,math,re,subprocess,tempfile
from pathlib import Path
from PIL import Image,ImageChops,ImageOps,ImageStat

FRAME=re.compile(r"frame_(0[1-9]|1[0-2])\.png\Z")
def load_plan(selection:Path,alignment:Path,frames:Path,seconds:float=4.8)->list[dict]:
    sel=json.loads(selection.read_text())
    evidence=json.loads(alignment.read_text())
    rows=sel.get("preselected")
    times=sel.get("candidate_segment_times_s")
    checks=evidence.get("checks")
    if sel.get("status")!="FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW":
        raise ValueError("SOURCE_SELECTION_NOT_READY")
    if not all(isinstance(x,list) and len(x)==5 for x in (rows,times,checks)):
        raise ValueError("FIVE_VERIFIED_FRAMES_REQUIRED")
    if not 3<=seconds<=6:raise ValueError("INVALID_SEGMENT_LENGTH")
    plan=[]
    for i,(row,t,check) in enumerate(zip(rows,times,checks)):
        name=row.get("filename") if isinstance(row,dict) else None
        if not isinstance(name,str) or not FRAME.fullmatch(name) or not isinstance(check,dict):
            raise ValueError("INVALID_SOURCE_FRAME")
        if isinstance(t,bool) or not isinstance(t,(int,float)) or not math.isfinite(t) or t<seconds:
            raise ValueError("INSUFFICIENT_MOTION_BEFORE_FREEZE")
        path=frames/name
        if path.is_symlink() or not path.is_file():raise ValueError("SOURCE_FRAME_MISSING")
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if (check.get("source_frame")!=name or check.get("source_frame_sha256")!=digest
            or check.get("endpoint_visually_aligned") is not True
            or abs(float(check.get("selected_timecode_s",-100))-t)>.002):
            raise ValueError("SOURCE_ALIGNMENT_NOT_VERIFIED")
        plan.append({"source_frame":name,"sha256":digest,"start_s":round(t-seconds,3),
                     "freeze_timecode_s":round(t,3)})
    if len({x["source_frame"] for x in plan})!=5:
        raise ValueError("DUPLICATE_FRAMES")
    # A 4.8s motion segment must not overlap the next; otherwise the cut is invalid.
    ordered=sorted(plan,key=lambda x:x["start_s"])
    if any(b["start_s"]<a["freeze_timecode_s"] for a,b in zip(ordered,ordered[1:])):
        raise ValueError("OVERLAPPING_SHOTS")
    return plan

def build(film:Path,plan:list[dict],out:Path,seconds:float=4.8)->dict:
    if film.is_symlink() or not film.is_file() or len(plan)!=5:raise ValueError("INVALID_FILM_OR_PLAN")
    out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="storia-v243-") as tmp:
        folder=Path(tmp);segments=[]
        for i,shot in enumerate(plan):
            segment=folder/f"shot_{i:02d}.mp4"
            subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
                "-ss",str(shot["start_s"]),"-i",str(film),"-t",str(seconds),"-an",
                "-vf","scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,format=gray,format=yuv420p,fps=24",
                "-c:v","libx264","-preset","veryfast","-crf","24",str(segment)],
                check=True,timeout=120)
            if segment.stat().st_size<1000:raise ValueError("EMPTY_SOURCE_SHOT")
            segments.append(segment)
        concat=folder/"concat.txt"
        concat.write_text("".join(f"file '{s.name}'\n" for s in segments))
        subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
            "-f","concat","-safe","0","-i",str(concat),"-c:v","copy",
            "-movflags","+faststart",str(out.resolve())],cwd=folder,check=True,timeout=90)
    probe=subprocess.run(["ffprobe","-v","error","-show_entries",
        "format=duration:stream=codec_name,width,height","-of","json",str(out)],
        capture_output=True,text=True,check=True,timeout=30)
    data=json.loads(probe.stdout)
    duration=float(data["format"]["duration"])
    if not 20<=duration<=30 or not any(s.get("codec_name")=="h264" and s.get("width")==720
          and s.get("height")==1280 for s in data["streams"]):
        raise ValueError("DECODED_ROUGHCUT_QA_FAILED")
    result={"version":"V243_ARCHIVAL_FREEZE_ENDPOINT_REVIEW","status":"NOT_FINAL",
        "duration_s":round(duration,3),"shots":plan,"i2i_generated":False,
        "vidu_generated":False,"italian_rights_verified":False,
        "artistic_approved":False,"final_mp4":False,"final_zip":False,
        "new_final_episodes_delivered":0,"publish_allowed":False}
    out.with_suffix(".json").write_text(json.dumps(result,indent=2)+"\n")
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for name in ("film","selection","alignment","frames","out"):
        p.add_argument("--"+name,required=True,type=Path)
    a=p.parse_args()
    plan=load_plan(a.selection,a.alignment,a.frames)
    print(build(a.film,plan,a.out)["status"])
