#!/usr/bin/env python3
"""V231: one authentic 28.5s editorial SOURCE rough cut, never final 4+1."""
from __future__ import annotations
import argparse, bisect, hashlib, json, math, subprocess, wave, zipfile
from pathlib import Path
from PIL import Image
import numpy as np
from storia_rivive_v230_curated_portrait import validate, digest
from storia_rivive_v209_shot_boundary_review import detect_boundaries

SHOT=5.2
OUTRO=2.5
DURATION=5*SHOT+OUTRO  # 28.5s

def command(args, timeout=180):
    p=subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    if p.returncode: raise RuntimeError("MEDIA_COMMAND_FAILED: "+p.stderr[-900:])
    return p.stdout

def safe_start(t, cuts, duration):
    if not math.isfinite(t) or not 1.2 <= t < duration:
        raise ValueError("INVALID_ARCHIVAL_TIMECODE")
    n=bisect.bisect_right(cuts,t)
    left=0 if n==0 else cuts[n-1]
    right=duration if n==len(cuts) else cuts[n]
    lower=left+.35
    upper=right-.35-SHOT
    if lower>upper: raise ValueError("SOURCE_SHOT_TOO_SHORT_NO_PADDING")
    start=min(max(t-2.55,lower),upper)
    if not start<=t<=start+SHOT: raise ValueError("SOURCE_ANCHOR_OUTSIDE_CLIP")
    return round(start,3)

def score(path):
    sr=44100
    t=np.arange(round(DURATION*sr),dtype=np.float64)/sr
    out=np.zeros_like(t)
    groups=((130.81,155.56,196.0),(116.54,146.83,174.61),
            (103.83,130.81,155.56),(130.81,164.81,196.0))
    span=DURATION/4
    for k,tones in enumerate(groups):
        a=round(k*span*sr)
        z=min(len(t),round((k+1)*span*sr))
        local=t[a:z]-k*span
        env=np.minimum(1,local/.8)*np.minimum(1,(span-local)/1.2)
        out[a:z]+=sum((.44/(j+1))*np.sin(2*np.pi*f*local) for j,f in enumerate(tones))*env
    out*=.30*np.minimum(1,t/1.2)*np.minimum(1,(DURATION-t)/1.4)
    pcm=(np.clip(out,-.95,.95)*32767).astype(np.int16)
    with wave.open(str(path),"wb") as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr)
        w.writeframes(np.repeat(pcm[:,None],2,axis=1).tobytes())

def render(config, selection, scout, cache, episode, out):
    entry=validate(config,selection,scout,cache,episode)
    if entry is None: raise ValueError("NO_SOURCE_CONFIG")
    out.mkdir(parents=True,exist_ok=True)
    film=cache/"ORIGINAL_ARCHIVE.webm"
    cuts=detect_boundaries(film,min(float(scout["duration_s"]),420))
    times=selection["candidate_segment_times_s"]
    windows=[safe_start(float(t),cuts,float(scout["duration_s"])) for t in times]
    clips=[]
    for i,(row,start) in enumerate(zip(entry["frames"],windows),1):
        w,h=entry["crop_width_px"],entry["raster_px"][1]
        x=row["left_px"]
        path=out/f"SOURCE_ONLY_{i:02d}.mp4"
        vf=f"crop={w}:{h}:{x}:0,scale=720:1280:flags=lanczos,format=gray,fps=30,format=yuv420p"
        if i==1:
            vf+=(",drawtext=text='EARLY CINEMA - 1910':fontcolor=white:fontsize=34:"
                 "x=(w-text_w)/2:y=70:enable='between(t,0.15,1.95)',"
                 "drawtext=text='FICTIONAL SILENT FILM':fontcolor=white:fontsize=21:"
                 "x=(w-text_w)/2:y=118:enable='between(t,0.15,1.95)'")
        command(["ffmpeg","-nostdin","-hide_banner","-v","error","-y",
                 "-ss",f"{start:.3f}","-i",str(film),"-t",str(SHOT),"-an",
                 "-vf",vf,"-c:v","libx264","-preset","veryfast","-crf","22",
                 "-pix_fmt","yuv420p",str(path)],180)
        clips.append(path)
    outro=out/"CLOSING_TITLE.mp4"
    vf=("drawtext=text='THE END':fontcolor=white:fontsize=54:"
        "x=(w-text_w)/2:y=(h-text_h)/2-50,"
        "drawtext=text='EARLY CINEMA - 1910':fontcolor=gray:fontsize=25:"
        "x=(w-text_w)/2:y=(h-text_h)/2+45,fade=t=in:st=0:d=0.4")
    command(["ffmpeg","-nostdin","-hide_banner","-v","error","-y",
             "-f","lavfi","-i",f"color=c=black:s=720x1280:r=30:d={OUTRO}",
             "-vf",vf,"-c:v","libx264","-preset","veryfast","-crf","22",
             "-pix_fmt","yuv420p",str(outro)],90)
    tracks=out/"CONCAT.txt"
    tracks.write_text("".join("file '%s'\n"%p.name for p in clips+[outro]))
    audio=out/"ORIGINAL_DEMO_SCORE.wav"
    score(audio)
    video=out/"EARLY_CINEMA_1910_V231_28S_REVIEW_NOT_FINAL.mp4"
    command(["ffmpeg","-nostdin","-hide_banner","-v","error","-y",
             "-f","concat","-safe","0","-i",str(tracks.resolve()),
             "-i",str(audio.resolve()),"-map","0:v:0","-map","1:a:0",
             "-c:v","libx264","-preset","veryfast","-crf","22",
             "-c:a","aac","-b:a","160k","-ar","44100","-ac","2",
             "-pix_fmt","yuv420p","-t",str(DURATION),"-movflags","+faststart",
             str(video.resolve())],180)
    info=json.loads(command(["ffprobe","-v","error","-show_streams","-show_format",
                              "-of","json",str(video)],30))
    v=[s for s in info["streams"] if s.get("codec_type")=="video"]
    a=[s for s in info["streams"] if s.get("codec_type")=="audio"]
    seconds=float(info["format"]["duration"])
    if not v or not a or v[0]["codec_name"]!="h264" or a[0]["codec_name"]!="aac":
        raise ValueError("NOT_ANDROID_H264_AAC")
    if (v[0]["width"],v[0]["height"])!=(720,1280) or not 27.9<=seconds<=29.1:
        raise ValueError("BAD_RENDER_DURATION_OR_GEOMETRY")
    command(["ffmpeg","-nostdin","-hide_banner","-v","error","-xerror",
             "-i",str(video),"-f","null","-"],120)
    with Image.open(cache/"original_frames"/entry["frames"][0]["filename"]) as im:
        x=entry["frames"][0]["left_px"]
        cover=out/"COVER_REVIEW.jpg"
        im.convert("RGB").crop((x,0,x+entry["crop_width_px"],entry["raster_px"][1])).resize(
            (720,1280),Image.Resampling.LANCZOS).save(cover,quality=90)
    posts=out/"FOUR_SOCIAL_DRAFTS_NOT_APPROVED.txt"
    posts.write_text(
        "Instagram: A 1910 staged silent drama — archival source-edit review only.\n"
        "Facebook: Five original moving shots from a 1910 silent fiction film. Restoration pending.\n"
        "TikTok: EARLY CINEMA · 1910. Source footage preview; not AI restored or publishable.\n"
        "YouTube: The Sorrows of the Unfaithful (1910) — 28.5s archival review cut.\n",
        encoding="utf-8")
    report={"version":"V231_28S_SOURCE_ONLY_EDITORIAL_PREVIEW",
            "status":"REVIEW_ONLY_NOT_COMPLETE_4I2I_1VIDU",
            "episode_id":episode,"duration_seconds":seconds,"five_authentic_source_motion_clips":5,
            "clip_seconds":SHOT,"closing_title_seconds":OUTRO,"source_starts_s":windows,
            "film_sha256":digest(film),"video_sha256":digest(video),
            "real_i2i_photos":0,"vidu_clips":0,
            "technical_h264_aac_decoded":True,"rights_italy_verified":False,
            "artistic_approved":False,"publish_allowed":False,
            "finished_mp4":False,"finished_zip":False,
            "real_finished_episodes_delivered":0,
            "warning":"Only the editorial black-and-white 28.5s assembly is complete. Not a final La Storia Rivive episode: 4 real I2I photos, 1 source-locked animated Vidu clip and V91/V94/V96/V99 still missing."}
    doc=out/"V231_QA_RESEARCH_ONLY.json"
    doc.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    kit=out/"V231_ANDROID_SOURCE_REVIEW_ONLY.zip"
    with zipfile.ZipFile(kit,"w",compression=zipfile.ZIP_DEFLATED) as z:
        for file in (video,cover,posts,doc):z.write(file,file.name)
    print("V231_REAL_SOURCE_REVIEW_28_5_S_NOT_FINAL",seconds,digest(video))
    return report

def main():
    ap=argparse.ArgumentParser()
    for name in ("config","selection","scout","cache","out"):
        ap.add_argument("--"+name,required=True,type=Path)
    ap.add_argument("--episode",required=True)
    args=ap.parse_args()
    render(json.loads(args.config.read_text()),json.loads(args.selection.read_text()),
           json.loads(args.scout.read_text()),args.cache,args.episode,args.out)

if __name__=="__main__":
    main()
