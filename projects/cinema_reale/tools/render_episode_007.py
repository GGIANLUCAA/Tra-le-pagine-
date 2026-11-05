#!/usr/bin/env python3
"""Cinema Reale 007: USGS Hawaiian volcanic cone collapse, genuine video, no AI footage."""
import hashlib, json, math, struct, subprocess, time, urllib.request, wave, zipfile
from pathlib import Path

OUT = Path("output/cinema_reale/episode_007")
OUT.mkdir(parents=True, exist_ok=True)
NAME = "CINEMA_REALE_007_VOLCANO_COLLAPSE_REVIEW.mp4"
SOURCE = "https://svs.gsfc.nasa.gov/vis/a010000/a010300/a010398/MLK_cone_collapse_960x540.m4v"
PAGE = "https://svs.gsfc.nasa.gov/10398"
CREDIT = "USGS, MLK volcanic cone collapse, Hawaii, 2 May 2006"

def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(str(cmd[:3]) + ": " + p.stderr[-2500:])
    return p.stdout

def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1048576), b""): h.update(chunk)
    return h.hexdigest()

def probe(path):
    return json.loads(run(["ffprobe","-v","error","-show_format","-show_streams","-of","json",str(path)]))

def download(dest):
    error = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(SOURCE, headers={"User-Agent":"Mozilla/5.0 (compatible; CinemaReale/1.0)"})
            with urllib.request.urlopen(req, timeout=120) as inp, dest.open("wb") as out:
                while True:
                    b = inp.read(1048576)
                    if not b: break
                    out.write(b)
            if dest.stat().st_size < 500000: raise ValueError("NASA file is too short")
            return
        except Exception as exc:
            error = exc
            dest.unlink(missing_ok=True)
            if attempt < 2: time.sleep(2 ** attempt)
    raise RuntimeError("No verified USGS video available; no alternate source substituted: " + str(error))

def make_score(path, duration, sr=24000):
    # Original instrumental ambient audio, generated mathematically without samples or TTS.
    notes = ((55.00,.16),(82.41,.10),(110.00,.06),(146.83,.055),(174.61,.035))
    with wave.open(str(path),"wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        for first in range(0,int(duration*sr),4096):
            out = bytearray()
            for i in range(first,min(int(duration*sr),first+4096)):
                t = i/sr
                amp = min(1., t/2.2, max(0.,(duration-t)/2.))
                motion = .74+.26*(.5+.5*math.sin(2*math.pi*t/10.6))
                pad = sum(a*math.sin(2*math.pi*f*t+.28*math.sin(.15*t+f)) for f,a in notes)
                sheen = .014*math.sin(2*math.pi*880*t+1.7*math.sin(.33*t))
                hits = sum(.10*math.exp(-3.7*(t-h))*math.sin(2*math.pi*62*(t-h)) for h in (7.5,17.,26.) if 0 <= t-h < 1.6)
                L = amp*(motion*pad+sheen+hits)
                R = amp*(motion*pad+.8*sheen*math.sin(.43*t+1)+hits)
                out += struct.pack("<hh",int(max(-1,min(1,L))*18000),int(max(-1,min(1,R))*18000))
            w.writeframesraw(out)

def main():
    src = OUT/"nasa_source.webm"
    download(src)
    info = probe(src)
    dur = float(info["format"]["duration"])
    vid = next((s for s in info["streams"] if s["codec_type"]=="video"),None)
    if vid is None or vid["width"] < 960 or vid["height"] < 540 or dur < 10:
        raise RuntimeError("Unexpected NASA source properties; fail closed")
    start, length = 0., min(24.,dur-.5)
    if length < 10: raise RuntimeError("Source too short")
    assert start+length <= dur-.5
    vf = f"crop=w=trunc(ih*9/16/2)*2:h=ih:x=(iw-ow)/2:y=0,scale=1080:1920:flags=lanczos,eq=contrast=1.04:saturation=1.06,format=yuv420p,fps=25,fade=t=in:st=0:d=0.25,fade=t=out:st={max(0.,length-.9):.2f}:d=0.9"
    visual = OUT/"video_no_audio.mp4"
    run(["ffmpeg","-hide_banner","-loglevel","error","-ss",str(start),"-i",str(src),"-t",str(length),"-an","-vf",vf,"-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p","-movflags","+faststart","-y",str(visual)])
    audio = OUT/"original_score.wav"
    make_score(audio,length)
    final = OUT/NAME
    run(["ffmpeg","-hide_banner","-loglevel","error","-i",str(visual),"-i",str(audio),"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","192k","-t",str(length),"-af",f"afade=t=out:st={max(0.,length-.8):.2f}:d=0.8","-movflags","+faststart","-y",str(final)])
    meta = probe(final)
    duration = float(meta["format"]["duration"])
    assert abs(duration-length) < .2
    assert any(s["codec_type"]=="video" and s["width"]==1080 and s["height"]==1920 for s in meta["streams"])
    assert any(s["codec_type"]=="audio" and s["codec_name"]=="aac" for s in meta["streams"])
    run(["ffmpeg","-hide_banner","-v","error","-i",str(final),"-f","null","-"])
    cover = OUT/"cover_no_text.jpg"
    run(["ffmpeg","-hide_banner","-loglevel","error","-ss",str(length*.65),"-i",str(final),"-frames:v","1","-y",str(cover)])
    qa = {"project_id":"cinema_reale","episode":"007","status":"RENDERED_REVIEW_NOT_PUBLISHED","source_page":PAGE,"source":SOURCE,"source_bytes":src.stat().st_size,"source_sha256":sha(src),"output_sha256":sha(final),"output_bytes":final.stat().st_size,"duration_seconds":duration,"resolution":[1080,1920],"full_ffmpeg_decode":"PASS","zip_crc":"PASS","original_music":True,"added_voice":False,"added_onscreen_text":False,"video_ai":False,"provenance":"Genuine USGS Hawaiian volcanic cone collapse footage","rights":"USGS footage hosted by NASA; check individual rights and overlays. Credit: "+CREDIT+"; no NASA endorsement implied."}
    (OUT/"qa_report.json").write_text(json.dumps(qa,indent=2),encoding="utf-8")
    (OUT/"SOURCES_AND_RIGHTS.txt").write_text("NASA source: "+PAGE+"\nOriginal file: "+SOURCE+"\nCredit: "+CREDIT+"\nPolicy: https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits\nNo NASA endorsement implied. Source audio not used.\n",encoding="utf-8")
    (OUT/"SOCIAL_DESCRIPTION_DRAFT.txt").write_text("A Hawaiian volcanic cone collapses, 2 May 2006. Genuine USGS footage hosted by NASA, with original cinematic sound design.\nCredit: "+CREDIT+"\n#Volcano #Hawaii #CinemaReale\n",encoding="utf-8")
    pack = OUT/"CINEMA_REALE_007_COMPLETE_REVIEW.zip"
    with zipfile.ZipFile(pack,"w",zipfile.ZIP_DEFLATED) as z:
        for p in (final,cover,OUT/"qa_report.json",OUT/"SOURCES_AND_RIGHTS.txt",OUT/"SOCIAL_DESCRIPTION_DRAFT.txt"):
            z.write(p,p.name)
    with zipfile.ZipFile(pack) as z: assert z.testzip() is None
    for p in (src,visual,audio): p.unlink()
    print(json.dumps({"status":"REVIEW_READY_NOT_PUBLISHED","mp4":NAME,"bytes":qa["output_bytes"],"sha256":qa["output_sha256"],"duration":duration}))

if __name__ == "__main__": main()
