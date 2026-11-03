#!/usr/bin/env python3
"""Produce a 24-second archival-only five-shot motion rough cut; NOT a final episode."""
import argparse,json,subprocess,tempfile
from pathlib import Path

def build(source,times,output,seconds=4.8):
    if not source.is_file() or source.is_symlink(): raise ValueError("ORIGINAL_ARCHIVE_MISSING")
    if len(times)!=5 or any(not isinstance(t,(float,int)) or t<0 for t in times):
        raise ValueError("FIVE_VALID_TIMECODES_REQUIRED")
    if len(set(times))!=5 or not 3<=seconds<=6: raise ValueError("DUPLICATE_TIMES_OR_UNSAFE_DURATION")
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="storia-v241-") as td:
        folder=Path(td);segments=[]
        for i,t in enumerate(times):
            segment=folder/f"shot_{i:02d}.mp4"
            subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
                "-ss",str(t),"-i",str(source),"-t",str(seconds),"-an",
                "-vf","scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,format=gray,format=yuv420p,fps=24",
                "-c:v","libx264","-preset","veryfast","-crf","24",str(segment)],
                check=True,timeout=120)
            if not segment.is_file() or segment.stat().st_size<1000:
                raise ValueError("EMPTY_ARCHIVAL_SHOT")
            segments.append(segment)
        playlist=folder/"concat.txt"
        playlist.write_text("".join(f"file '{s.name}'\n" for s in segments))
        subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
            "-f","concat","-safe","0","-i",str(playlist),"-c:v","copy",
            "-movflags","+faststart",str(output.resolve())],cwd=folder,check=True,timeout=60)
    p=subprocess.run(["ffprobe","-v","error","-show_entries",
        "format=duration:stream=codec_name,width,height","-of","json",str(output)],
        check=True,capture_output=True,text=True,timeout=30)
    data=json.loads(p.stdout);duration=float(data["format"]["duration"])
    if not 20<=duration<=30 or not any(s.get("codec_name")=="h264" and
        s.get("width")==720 and s.get("height")==1280 for s in data["streams"]):
        raise ValueError("ROUGH_CUT_MEDIA_QA_FAILED")
    return {"status":"SOURCE_ONLY_ROUGHCUT_NOT_FINAL","duration_s":round(duration,3),
        "shots":5,"has_i2i":False,"has_vidu":False,"rights_approved":False,
        "publication_permitted":False,"mp4":str(output)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--selection",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    times=json.loads(a.selection.read_text())["candidate_segment_times_s"]
    result=build(a.source,times,a.out)
    a.out.with_suffix(".json").write_text(json.dumps(result,indent=2)+"\n")
    print(result)
if __name__=="__main__":main()
