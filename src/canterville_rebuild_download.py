#!/usr/bin/env python3
"""Rebuild an Android-downloadable Canterville episode from existing GitHub artifacts.

Independent of ChatGPT Library attachments. Not the original editor's exact MP4
bytes; reuses the approved Gacrux narration and 1906 edition illustrations.
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import json, subprocess, os, math

SHOTS=[
 (12,3.5,"cover"),(12,5.5,"full"),(2,9.4,"full"),
 (3,11.5,"full"),(3,10.2,"detail"),(3,6.9,"full"),
 (12,4.0,"full"),(4,11.2,"full"),(4,10.4,"detail"),
 (9,11.1,"full"),(5,5.1,"full"),(6,7.1,"full"),
 (7,3.5,"full"),(9,9.2,"full"),(11,7.8,"full"),
 (11,3.6,"detail"),(1,7.4,"full"),(11,8.4,"full"),
 (1,4.3,"full"),(11,3.2,"detail"),(12,7.6,"full"),
 (13,3.6,"full"),(14,4.7,"full"),(15,8.0,"full"),
 (16,5.2,"full"),(17,7.1,"full"),(1,4.0,"full"),
 (17,2.996,"ending"),
]
W,H=540,960
BASE=Path("input")
DEST=Path("output")
DEST.mkdir(exist_ok=True)
FRAMES=DEST/"frames"
FRAMES.mkdir(exist_ok=True)

def font(size):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
              "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf"]:
        if Path(p).exists(): return ImageFont.truetype(p,size)
    return ImageFont.load_default()

def framed(src, treatment, number):
    original=Image.open(src).convert("RGB")
    backdrop=ImageOps.fit(original,(W,H),method=Image.Resampling.LANCZOS)
    backdrop=backdrop.filter(ImageFilter.GaussianBlur(24))
    backdrop=ImageEnhance.Brightness(backdrop).enhance(.22)
    art=original.copy()
    if treatment=="detail":
        w,h=art.size
        inset=.10
        art=art.crop((int(w*inset),int(h*inset),int(w*(1-inset)),int(h*(1-inset))))
    avail=(W-54,H-170)
    art.thumbnail(avail,Image.Resampling.LANCZOS)
    x=(W-art.width)//2; y=(H-art.height)//2
    draw=ImageDraw.Draw(backdrop)
    draw.rectangle((x-8,y-8,x+art.width+8,y+art.height+8),fill=(214,205,188))
    backdrop.paste(art,(x,y))
    draw=ImageDraw.Draw(backdrop)
    if treatment in ("cover","ending"):
        dark=Image.new("RGBA",(W,160),(5,12,23,222))
        backdrop.paste(dark,(0,0),dark)
        dark2=Image.new("RGBA",(W,160),(5,12,23,222))
        backdrop.paste(dark2,(0,H-160),dark2)
        draw=ImageDraw.Draw(backdrop)
        draw.text((W/2,30),"TRA LE PAGINE",anchor="mt",font=font(22),fill=(235,207,151))
        draw.text((W/2,H-112),"IL FANTASMA DI",anchor="mt",font=font(29),fill=(255,242,215))
        draw.text((W/2,H-72),"CANTERVILLE",anchor="mt",font=font(31),fill=(255,242,215))
    else:
        draw.line((60,H-42,W-60,H-42),fill=(184,150,105),width=2)
    return backdrop

source_dir=BASE/"illustrations"
assets=sorted(source_dir.glob("illustrazione_*.jpg"))
if len(assets)<17:raise RuntimeError(f"Expected original 17 illustrations, got {len(assets)}")
voice_files=list((BASE/"voice").rglob("VOCE_NATURALE.mp3"))
if not voice_files:raise RuntimeError("Gacrux narration unavailable in artifact")
voice=voice_files[0]
timeline=[]
for i,(artid, duration, mode) in enumerate(SHOTS):
    out=FRAMES/f"shot_{i:03}.jpg"
    framed(source_dir/f"illustrazione_{artid:02}.jpg",mode,i).save(out,quality=90,subsampling=0)
    timeline.append({"shot":i,"image":artid,"duration":duration,"treatment":mode})
concat=DEST/"timeline.ffconcat"
with concat.open("w") as fp:
    fp.write("ffconcat version 1.0\n")
    for row in timeline:
        fp.write(f"file 'frames/shot_{row['shot']:03}.jpg'\n")
        fp.write(f"duration {row['duration']:.3f}\n")
    fp.write(f"file 'frames/shot_{len(SHOTS)-1:03}.jpg'\n")
out=DEST/"CANTERVILLE_GITHUB_DOWNLOAD.mp4"
subprocess.run([
    "ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
    "-safe","0","-f","concat","-i",str(concat),
    "-i",str(voice),"-map","0:v:0","-map","1:a:0",
    "-vf","fps=20,format=yuv420p","-c:v","libx264","-preset","veryfast",
    "-crf","26","-c:a","aac","-b:a","112k","-ar","44100",
    "-t","186.496","-movflags","+faststart",str(out)
],check=True,timeout=900)
probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries",
                  "format=duration,size:stream=codec_type,codec_name",
                  "-of","json",str(out)]))
if set(x["codec_type"] for x in probe["streams"])!={"video","audio"}:
    raise RuntimeError("Output lacks video or audio")
if float(probe["format"]["duration"])<184:raise RuntimeError("Video truncated")
subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-i",
                str(out),"-f","null","-"],check=True,timeout=900)
(DEST/"README_DOWNLOAD.txt").write_text(
  "Tra le Pagine — Il fantasma di Canterville\n"+
  "BACKUP VIDEO DISTRIBUTION GENERATED INSIDE GITHUB ACTIONS\n"+
  "This is an alternate reconstruction, not byte-identical to the ChatGPT deliverable.\n"+
  "Natural voice: Gemini Gacrux, original illustration set: Wallace Goldsmith, 1906.\n"+
  "Original source: https://www.gutenberg.org/cache/epub/14522/pg14522-images.html\n"+
  f"Duration: {probe['format']['duration']} seconds, bytes: {probe['format']['size']}\n"+
  "No publication on any social network; author should review before publication.\n",
  encoding="utf-8")
(DEST/"SHOT_LIST.json").write_text(json.dumps(timeline,indent=2))
print("OK:",out,"size:",out.stat().st_size,"duration:",probe["format"]["duration"])
