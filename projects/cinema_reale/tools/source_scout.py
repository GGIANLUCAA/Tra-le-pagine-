#!/usr/bin/env python3
"""Unpaid source-only inspection for the isolated cinema_reale project.
Downloads authentic NOAA footage, creates source-only contact sheets; NO generation,
NO publish, NO footage labels. Contact-sheet labels are internal QA, not in videos.
"""
import hashlib, json, os, subprocess, sys, time, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw

BASE = Path("output/cinema_reale/source_scout_002")
SOURCES = {
    "cucumber_flight_2026": {
        "url": "https://oceanexplorer.noaa.gov/wp-content/uploads/2026/09/ex2606-dive03-seacuke-640x360-1.mp4",
        "page": "https://oceanexplorer.noaa.gov/multimedia/sea-cucumber-swimming/",
        "credit": "NOAA Ocean Exploration, 2026 American Samoa ROV + Mapping Exploration",
    },
    "isopod_swim_walk_2026": {
        "url": "https://oceanexplorer.noaa.gov/wp-content/uploads/2026/10/ex2606-dive11-isopod_SD.mp4",
        "page": "https://oceanexplorer.noaa.gov/multimedia/unknown-isopod/",
        "credit": "NOAA Ocean Exploration, 2026 American Samoa ROV + Mapping Exploration",
    },
}

def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode: raise RuntimeError(f"{cmd[0]} failure: {p.stderr[-1500:]}")
    return p.stdout

def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "CinemaReale/1.0 (source-inspection; NOAA credit kept)"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as response, dest.open("wb") as out:
                while True:
                    b = response.read(1024*1024)
                    if not b: break
                    out.write(b)
            if dest.stat().st_size < 100000: raise RuntimeError("short download")
            return
        except Exception:
            dest.unlink(missing_ok=True)
            if attempt == 2: raise
            time.sleep(4*(attempt+1))

def inspect(key, source):
    folder = BASE/key
    folder.mkdir(parents=True, exist_ok=True)
    original = folder/"source_original.mp4"
    download(source["url"], original)
    sha = hashlib.sha256(original.read_bytes()).hexdigest()
    probe = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(original)]))
    duration = float(probe["format"].get("duration") or 0)
    video = next((s for s in probe["streams"] if s.get("codec_type") == "video"), None)
    if not video or duration < 3: raise RuntimeError(f"Bad NOAA video: {key}")
    frames = []
    step = duration/13
    for i in range(1,13):
        ts=min(duration-0.15, i*step)
        imagefile=folder/f"frame_{i:02d}.jpg"
        run(["ffmpeg","-hide_banner","-loglevel","error","-ss",f"{ts:.3f}","-i",str(original),"-frames:v","1","-vf","scale=384:-2", "-y", str(imagefile)])
        if imagefile.exists():
            frames.append((ts, imagefile))
    w,h=384,245
    sheet=Image.new("RGB",(3*w,4*h),(12,16,22))
    draw=ImageDraw.Draw(sheet)
    for n,(ts,p) in enumerate(frames):
        im=Image.open(p).convert("RGB")
        im.thumbnail((w,h-24))
        xx=(n%3)*w+(w-im.width)//2
        yy=(n//3)*h
        sheet.paste(im,(xx,yy))
        draw.text(((n%3)*w+6,yy+h-20),f"Source {key} / {ts:.1f}s",fill=(235,235,235))
    sheet.save(folder/"timecode_contact_sheet.jpg",quality=87)
    summary={
        "project_id":"cinema_reale",
        "purpose":"source_only_not_publishable",
        "subject":key, "source_page":source["page"],"download_url":source["url"],
        "credit":source["credit"],"original_sha256":sha,"bytes":original.stat().st_size,
        "duration_s":duration, "width":video.get("width"),"height":video.get("height"),
        "fps":video.get("avg_frame_rate"),"codec":video.get("codec_name"),
        "sample_times_s":[round(ts,2) for ts,_ in frames],
        "visual_editorial_qa":"PENDING; machine contact sheet is not artistic approval",
        "published":"NO","cost":"none",
    }
    (folder/"source_report.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    # SOURCE ONLY: do not include original MP4 in artifact without finishing manual QA.
    original.unlink()
    return summary

def main():
    BASE.mkdir(parents=True,exist_ok=True)
    records,errors=[],{}
    for key,src in SOURCES.items():
        try:
            record=inspect(key,src);records.append(record);print("SCOUT_OK",key,record["duration_s"],flush=True)
        except Exception as ex:
            errors[key]=str(ex)
            print("SCOUT_FAILED",key,str(ex),file=sys.stderr,flush=True)
    (BASE/"summary.json").write_text(json.dumps({"project_id":"cinema_reale","records":records,"errors":errors},indent=2))
    if len(records)!=len(SOURCES):sys.exit(1)

if __name__=="__main__":main()
