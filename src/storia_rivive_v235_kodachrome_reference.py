#!/usr/bin/env python3
"""Source-real 1926 Kodachrome reference. NEVER a 4+1 final, never publish."""
import argparse,hashlib,json,math,subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageStat,ImageChops

PAGE="https://commons.wikimedia.org/wiki/File:Colourful_Fashions_From_Paris_(1926).webm"
SHA1="1021632bf541dd543f735b2092be37a76b06282b"

def cmd(argv,timeout=180):
    p=subprocess.run(argv,capture_output=True,text=True,timeout=timeout)
    if p.returncode: raise RuntimeError("VIDEO_ERROR "+p.stderr[-500:])
    return p.stdout

def sha(path,kind="sha256"):
    h=hashlib.new(kind)
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()

def download(path):
    import requests
    s=requests.Session()
    s.headers.update({"User-Agent":"LaStoriaRiviveSourceQA/1.0 (archival research, no redistribution)"})
    q=s.get("https://commons.wikimedia.org/w/api.php",params={
        "action":"query","titles":"File:Colourful Fashions From Paris (1926).webm",
        "prop":"imageinfo","iiprop":"url|size|sha1","format":"json"},timeout=40)
    q.raise_for_status()
    info=next(iter(q.json()["query"]["pages"].values()))["imageinfo"][0]
    if info["sha1"]!=SHA1 or not 120_000_000<int(info["size"])<140_000_000:
        raise ValueError("COMMONS_METADATA_CHANGED")
    url=info["url"]
    if not url.startswith("https://upload.wikimedia.org/"):raise ValueError("UNTRUSTED_HOST")
    path.parent.mkdir(parents=True,exist_ok=True)
    with s.get(url,stream=True,timeout=180) as r:
        r.raise_for_status()
        with path.open("wb") as f:
            for chunk in r.iter_content(1024*1024):
                if chunk:f.write(chunk)
                if f.tell()>140_000_000:raise ValueError("SOURCE_TOO_LARGE")
    if sha(path,"sha1")!=SHA1:raise ValueError("SOURCE_SHA1_MISMATCH")

def color_score(im):
    r,g,b=im.convert("RGB").resize((240,135)).split()
    return round(sum(ImageStat.Stat(ImageChops.difference(x,y)).mean[0]
        for x,y in ((r,g),(g,b),(b,r)))/3,2)

def inspect(source,out,samples=30,strict=True):
    if strict and sha(source,"sha1")!=SHA1:raise ValueError("SOURCE_SHA1_MISMATCH")
    meta=json.loads(cmd(["ffprobe","-v","error","-show_format","-show_streams","-of","json",str(source)],30))
    v=next(x for x in meta["streams"] if x.get("codec_type")=="video")
    duration=float(meta["format"]["duration"])
    if duration<40 or int(v["width"])<900 or int(v["height"])<600:
        raise ValueError("SOURCE_NATIVE_RASTER_TOO_SMALL")
    frames=out/"real_frames";frames.mkdir(parents=True,exist_ok=True)
    rows=[];board=Image.new("RGB",(1600,math.ceil(samples/5)*215),(18,20,24));d=ImageDraw.Draw(board)
    for i in range(samples):
        t=round((i+.5)*duration/samples,3)
        p=frames/f"frame_{i+1:02d}.jpg"
        cmd(["ffmpeg","-nostdin","-v","error","-y","-ss",str(t),"-i",str(source),"-frames:v","1","-q:v","3",str(p)],60)
        with Image.open(p) as im:
            score=color_score(im)
            im.thumbnail((308,180))
            board.paste(im,((i%5)*320+(320-im.width)//2,(i//5)*215+5))
        d.text(((i%5)*320+8,(i//5)*215+189),f"{i+1:02d}  t={t:.1f}s  color={score:.1f}",fill="white")
        rows.append({"frame":p.name,"time_s":t,"color_difference_mean":score})
    if sum(x["color_difference_mean"]>=5 for x in rows)<samples//3:
        raise ValueError("NOT_AUTHENTIC_COLOR_REFERENCE")
    board.save(out/"V235_REAL_1926_COLOR_CONTACT.jpg",quality=87)
    report={"version":"V235_AUTHENTIC_KODACHROME_REFERENCE","source_page":PAGE,
        "source_sha1":sha(source,"sha1"),"source_sha256":sha(source),
        "source_size_bytes":source.stat().st_size,"duration_s":duration,
        "width":int(v["width"]),"height":int(v["height"]),
        "real_source_color_not_black_white":True,"frames":rows,
        "italian_rights_verified":False,"publish_allowed":False,
        "four_real_i2i_photos":0,"real_vidu_clips":0,"final_episodes":0,
        "not_a_4_plus_1_episode":True,"credit_spent":0}
    (out/"V235_REFERENCE_QA.json").write_text(json.dumps(report,indent=2)+"\n")
    return report

def motion(source,out,report):
    # 9 distinct sampled temporal windows, each 2.8s of REAL moving film.
    # The B/W start is an explicit artistic desaturation of authentic COLOR film.
    times=[report["frames"][i]["time_s"] for i in (2,5,8,11,14,17,20,23,26)]
    clips=[]
    for i,t in enumerate(times):
        clip=out/f"real_motion_{i+1:02d}.mp4"
        vf="scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,hue=s='clip((t-0.65)/0.55,0,1)',fps=30,format=yuv420p"
        cmd(["ffmpeg","-nostdin","-v","error","-y","-ss",str(t),"-i",str(source),
            "-t","2.8","-an","-vf",vf,"-c:v","libx264","-preset","veryfast",
            "-crf","22",str(clip)],180)
        clips.append(clip)
    listing=out/"concat.txt"
    listing.write_text("".join("file '"+p.name+"'\n" for p in clips))
    dest=out/"V235_25S_AUTHENTIC_COLOR_MOTION_REFERENCE_NOT_FINAL.mp4"
    cmd(["ffmpeg","-nostdin","-v","error","-y","-f","concat","-safe","0",
         "-i",str(listing),"-c","copy","-movflags","+faststart",str(dest)],180)
    probe=json.loads(cmd(["ffprobe","-v","error","-show_format","-of","json",str(dest)],30))
    dur=float(probe["format"]["duration"])
    if not 24.8<=dur<=25.6:raise ValueError("MOTION_DURATION_INVALID")
    cmd(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(dest),"-f","null","-"],180)
    report.update({"motion_reference_duration_s":dur,"motion_reference_sha256":sha(dest),
        "motion_reference_is_original_color_not_i2i":True,
        "motion_reference_is_final":False,"motion_reference_has_audio":False,
        "motion_source_times_s":times})
    (out/"V235_REFERENCE_QA.json").write_text(json.dumps(report,indent=2)+"\n")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path)
    ap.add_argument("--download-to",type=Path)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    source=args.source or args.download_to
    if args.download_to:download(source)
    report=inspect(source,args.out)
    motion(source,args.out,report)
    print("V235_REFERENCE_ONLY_NOT_FINAL",report["source_sha256"])
