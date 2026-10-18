#!/usr/bin/env python3
"""FFmpeg-based, read-only quality check for MP4/audio/subtitles (0 API credits).
Volume and time metrics cannot judge artistic quality, so warnings remain
reviewable and no narration is normalized, filtered or re-synthesized.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

def command(*args, timeout=125):
    return subprocess.run([str(a) for a in args],capture_output=True,
                          text=True,timeout=timeout,check=True)

def check_subtitles(srt, duration):
    if not srt:return {"status":"NOT_PROVIDED"}
    path=Path(srt)
    if not path.exists():return {"status":"MISSING"}
    content=path.read_text(encoding="utf-8-sig")
    cues=re.findall(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})",content)
    def sec(ts):
        h,m,s=ts.replace(",",".").split(":")
        return 3600*int(h)+60*int(m)+float(s)
    if not cues:return {"status":"WARN","why":"No subtitles detected"}
    first=sec(cues[0][0]);last=sec(cues[-1][1])
    if last>duration+1:return {"status":"WARN","why":"Subtitles exceed duration"}
    return {"status":"OK" if last>=duration-8 else "WARN",
            "number":len(cues),"first_second":round(first,2),"last_second":round(last,2)}

def inspect(video,srt=None):
    video=Path(video)
    info=json.loads(command("ffprobe","-v","error","-of","json","-show_entries",
                    "format=duration:stream=codec_type,width,height",video).stdout)
    duration=float(info["format"]["duration"])
    video_stream=next((x for x in info["streams"] if x["codec_type"]=="video"),None)
    audio_stream=next((x for x in info["streams"] if x["codec_type"]=="audio"),None)
    if not video_stream or not audio_stream:raise RuntimeError("MP4 missing video/audio")
    reading=command("ffmpeg","-hide_banner","-nostats","-i",video,"-vn",
         "-af","loudnorm=I=-16:TP=-1.5:LRA=10:print_format=json",
         "-f","null","-").stderr
    measurements=re.findall(r'\{\s*"input_i"\s*:.*?\}',reading,re.S)
    loud=json.loads(measurements[-1]) if measurements else {}
    integrated=float(loud["input_i"]) if "input_i" in loud else None
    peak=float(loud["input_tp"]) if "input_tp" in loud else None
    subtitles=check_subtitles(srt,duration)
    warnings=[]
    if not 100<=duration<=250:warnings.append("Duration outside typical 2–4 minute book video")
    if abs(video_stream.get("width",0)/max(1,video_stream.get("height",1))-9/16)>.018:
        warnings.append("Not vertical 9:16")
    if integrated is None:warnings.append("Unable to measure loudness")
    elif integrated < -22 or integrated > -11:warnings.append("Check average listening loudness")
    if peak is not None and peak > -.4:warnings.append("True peak close to 0 dBTP")
    if subtitles["status"]=="WARN":warnings.append("Subtitle timing needs review")
    return {
        "version":"V5", "duration_seconds":round(duration,2),
        "resolution":[video_stream["width"],video_stream["height"]],
        "loudness_lufs":integrated,"true_peak_dbtp":peak,
        "subtitle_check":subtitles,"warnings":warnings,
        "technical_check":"PASS_WITH_WARNINGS" if warnings else "PASS",
        "human_review_required":True,
        "human_review":"Check every scene, actor identity, narration, image cuts, factual accuracy, and music yourself."
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--video",required=True);p.add_argument("--srt")
    p.add_argument("--out",default="CONTROLLO_AUDIO_VIDEO_V5.json")
    a=p.parse_args()
    report=inspect(a.video,a.srt)
    Path(a.out).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("V5 QA:",report["technical_check"],
          "LUFS:",report["loudness_lufs"],
          "peak:",report["true_peak_dbtp"],
          "duration:",report["duration_seconds"])
