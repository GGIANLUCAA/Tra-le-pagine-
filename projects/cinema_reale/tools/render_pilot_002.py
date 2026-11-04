#!/usr/bin/env python3
"""Isolated Cinema Reale visual pilot. Genuine NOAA images, original procedural score.
Not a claim of platform originality or artistic Gold approval. No text/voice/AI scenes.
"""
import hashlib,json,math,random,subprocess,urllib.request,wave,struct,zipfile
from pathlib import Path

OUT=Path("output/cinema_reale/pilot_002"); OUT.mkdir(parents=True,exist_ok=True)
SOURCE="https://oceanexplorer.noaa.gov/wp-content/uploads/2026/09/ex2606-dive03-seacuke.mp4"
CREDIT="NOAA Ocean Exploration, 2026 American Samoa ROV + Mapping Exploration"
def run(args):
    p=subprocess.run(args,capture_output=True,text=True)
    if p.returncode:raise RuntimeError(f"{args[0]}: {p.stderr[-2500:]}")
    return p.stdout
def fetch():
    path=OUT/"noaa_original_hd.mp4"
    req=urllib.request.Request(SOURCE,headers={"User-Agent":"CinemaReale/1.0 original-footage-pilot"})
    with urllib.request.urlopen(req,timeout=150) as r,path.open("wb") as f:
        while True:
            b=r.read(1048576)
            if not b:break
            f.write(b)
    if path.stat().st_size<20000000:raise RuntimeError("HD source unexpectedly small")
    probe=json.loads(run(["ffprobe","-v","error","-show_format","-show_streams","-of","json",str(path)]))
    v=next(s for s in probe["streams"] if s["codec_type"]=="video")
    if v["width"]<1280 or v["height"]<720:raise RuntimeError("HD source too small for vertical crop")
    if float(probe["format"]["duration"])<81:raise RuntimeError("Source shorter than storyboard")
    return path,v,probe

def score(seconds=30.0):
    # Original, deterministic, wordless ambient soundscape synthesized from math; no copyrighted samples.
    sr=24000; rng=random.Random(2606); path=OUT/"original_ambient_score.wav"
    n=int(seconds*sr);chunk=4096; low=0.0
    with wave.open(str(path),"wb") as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr)
        for off in range(0,n,chunk):
            buf=bytearray()
            for i in range(off,min(off+chunk,n)):
                t=i/sr
                env=min(1,t/1.8,max(0,(seconds-t)/2.4))
                tension=0.38+0.62*min(1,t/20)
                # 3 dark harmonic drones with slow amplitude movement
                pad=(math.sin(2*math.pi*55*t)+0.4*math.sin(2*math.pi*82.4*t)+0.23*math.sin(2*math.pi*110.1*t))*0.17
                pad*=0.65+0.35*math.sin(2*math.pi*0.11*t)**2
                low=low*0.997+(rng.random()*2-1)*0.003
                waveval=env*(pad*tension+low*0.8)
                # sparse low pulses during the reveal
                for hit in (7.5,14.5,21.5):
                    d=t-hit
                    if 0<d<2.5:waveval+=0.12*math.exp(-2*d)*math.sin(2*math.pi*63*d)
                sample=int(max(-1,min(1,waveval))*18000)
                buf.extend(struct.pack("<hh",sample,sample))
            w.writeframesraw(buf)
    return path

def main():
    original,v,probe=fetch()
    # All source timecodes are from the SAME genuine recorded animal.
    # Excludes the source's initial text and its end slate.
    shots=[(33.0,5.0),(43.0,4.5),(51.0,5.0),(61.0,5.0),(71.0,7.0)]
    # Use source HD dimensions, center crop preserving animal and no in-video labels.
    w,h=int(v["width"]),int(v["height"]); cw=int(h*9/16)//2*2
    if cw>w:raise RuntimeError("No portrait crop possible")
    clips=[]
    for j,(start,duration) in enumerate(shots):
        dst=OUT/f"shot_{j+1:02d}.mp4"
        vf=f"crop={cw}:{h}:(iw-{cw})/2:0,scale=720:1280:flags=lanczos,fps=30,format=yuv420p"
        run(["ffmpeg","-hide_banner","-loglevel","error","-ss",str(start),"-i",str(original),"-t",str(duration),"-an","-vf",vf,"-c:v","libx264","-preset","veryfast","-crf","19","-movflags","+faststart","-y",str(dst)])
        clips.append(dst)
    concat=OUT/"concat.txt";concat.write_text("".join("file '"+p.name+"'\n" for p in clips))
    silent=OUT/"silent_edit.mp4"
    run(["ffmpeg","-hide_banner","-loglevel","error","-f","concat","-safe","0","-i",str(concat),"-c","copy","-y",str(silent)])
    duration=sum(d for _,d in shots)
    audio=score(duration)
    final=OUT/"CINEMA_REALE_002_FUGA_DAL_FONDALE_PILOT.mp4"
    run(["ffmpeg","-hide_banner","-loglevel","error","-i",str(silent),"-i",str(audio),"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","160k","-af",f"afade=t=in:st=0:d=1.0,afade=t=out:st={duration-1.6}:d=1.6","-shortest","-movflags","+faststart","-y",str(final)])
    probeout=json.loads(run(["ffprobe","-v","error","-show_format","-show_streams","-of","json",str(final)]))
    streams=probeout["streams"];video=next(s for s in streams if s["codec_type"]=="video")
    audio_stream=next(s for s in streams if s["codec_type"]=="audio")
    if video["width"]!=720 or video["height"]!=1280 or audio_stream["codec_name"]!="aac":raise RuntimeError("QA codec/layout failed")
    if not 25<float(probeout["format"]["duration"])<30:raise RuntimeError("QA duration failed")
    # Full video decode and scene checks, not an artistic approval.
    run(["ffmpeg","-hide_banner","-v","error","-i",str(final),"-f","null","-"])
    cover=OUT/"cover_no_text.jpg"
    run(["ffmpeg","-hide_banner","-loglevel","error","-ss","1.8","-i",str(final),"-frames:v","1","-y",str(cover)])
    report={"project_id":"cinema_reale","status":"RENDERED_PILOT_NEEDS_ARTISTIC_REVIEW_NOT_PUBLISHED",
      "source":SOURCE,"source_page":"https://oceanexplorer.noaa.gov/multimedia/sea-cucumber-swimming/",
      "source_sha256":hashlib.sha256(original.read_bytes()).hexdigest(),
      "credit":CREDIT,"license_note":"NOAA Media Kit says credit NOAA; check individual clip for copyright exceptions",
      "video_sha256":hashlib.sha256(final.read_bytes()).hexdigest(),
      "shots_seconds":shots,"source_hd":{"width":w,"height":h},"duration_s":float(probeout["format"]["duration"]),
      "output":{"width":video["width"],"height":video["height"],"video_codec":video["codec_name"],"audio_codec":audio_stream["codec_name"]},
      "audio":"original procedural synthesized ambient soundtrack, no sampled music, no voices",
      "no_added_text":True,"no_generated_video":True,"platform_originality_guaranteed":False,
      "artistic_qa":"PENDING: inspect full vertical MP4 and assess originality, subject visibility and narrative",
      "publication":"NOT AUTHORIZED"}
    (OUT/"qa_report.json").write_text(json.dumps(report,indent=2))
    (OUT/"SOCIAL_DESCRIPTION_DRAFT.txt").write_text("A creature from the deep, moving like nothing on land. Real footage from NOAA Ocean Exploration.\n\nFootage: "+CREDIT+"\n#DeepSea #OceanExploration #Nature\n")
    (OUT/"SOURCES_AND_RIGHTS.txt").write_text("Video source: "+SOURCE+"\nNOAA Media Kit: https://oceanexplorer.noaa.gov/about/media-kit/\nCredit: "+CREDIT+"\nNo narration, no in-video text. Original synthesized audio. Not yet cleared for publication; assess editorial originality.\n")
    archive=OUT/"CINEMA_REALE_002_PILOT_PACKAGE.zip"
    with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED,compresslevel=5) as z:
        for p in (final,cover,OUT/"qa_report.json",OUT/"SOCIAL_DESCRIPTION_DRAFT.txt",OUT/"SOURCES_AND_RIGHTS.txt"):
            z.write(p,p.name)
    print(json.dumps({"result":"RENDERED_PILOT_NEEDS_ARTISTIC_REVIEW","duration":duration,"bytes":final.stat().st_size,"zip_bytes":archive.stat().st_size}))
    # Never upload source HD, internal working clips, or unaudited footage as finished assets.
    original.unlink()
if __name__=="__main__":main()
