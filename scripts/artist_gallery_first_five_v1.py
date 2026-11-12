#!/usr/bin/env python3
"""Five isolated authentic-artist gallery reels, no paid APIs, no publication.

The user approved the Evelyn De Morgan aesthetic; this is a DIFFERENT
format from ArtVision owner 4x1. Each artwork is an independently verified
Commons image. Source/rights/technical/artistic statuses are distinct.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import io
import json
import math
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
CONF = ROOT / "config/artist_gallery_first_five_20261113.json"
USER_AGENT = "ArtVision-Curated-Artists/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-)"
W,H,FPS=720,1280,25

# Curated seeds confirmed from Commons pages; other candidates are only accepted
# when license + artist + painting key + pixels pass source validation.
SEEDS = {
 "waterhouse":["John William Waterhouse The Lady of Shalott.jpg"],
 "redon":[],
 "khnopff":["Fernand Khnopff - Caresses - Google Art Project.jpg",
            "I lock my door upon myself Fernand Khnopff 1891.jpg"],
 "moreau":["The Apparition, Gustave Moreau 1876.jpg"],
 "stokes":["Marianne Stokes - The Queen and the Page (1896).jpg",
           "Marianne Stokes - Primavera.jpg",
           "Marianne Stokes Madonna and Child.jpg",
           "Marianne Stokes Sweet Dreams.jpg",
           "Marianne Stokes Im Gebet.jpg",
           "Marianne Stokes - On the Way to the Fields.jpg",
           "Marianne Stokes St Elizabeth of Hungary Spinning for the Poor.jpg",
           "Marianne Stokes A Woman of Desze.jpg",
           "Marianne Stokes Schneewittchen.jpg"]
}
COMMONS="https://commons.wikimedia.org/w/api.php"
LICENSE="https://creativecommons.org/licenses/by/4.0/"

def sha(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for piece in iter(lambda:f.read(1<<20),b""):h.update(piece)
 return h.hexdigest()

def run(cmd,timeout=420):
 r=subprocess.run([str(x) for x in cmd],text=True,capture_output=True,timeout=timeout)
 if r.returncode:raise RuntimeError("COMMAND_FAILED "+str(cmd[:6])+" "+r.stderr[-1200:])
 return r.stdout

def fetch(url,size=24000000,tries=3):
 last=None
 for n in range(tries):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT,
                "Accept":"application/json,image/jpeg,image/png,image/webp,*/*;q=.8"})
   with urllib.request.urlopen(req,timeout=28) as resp:
    data=resp.read(size+1)
   if len(data)>size:raise ValueError("asset too large")
   if len(data)<100:raise ValueError("asset too small")
   return data
  except (OSError,ValueError) as e:
   last=e
   if n<tries-1:time.sleep(1.0*(n+1))
 raise RuntimeError(f"{type(last).__name__}: {str(last)[:95]}")

def api(params):
 q={"action":"query","format":"json","formatversion":"2",**params}
 url=COMMONS+"?"+urllib.parse.urlencode(q)
 return json.loads(fetch(url,size=9000000,tries=2))

def file_info(filename):
 q=api({"titles":"File:"+filename,"prop":"imageinfo",
    "iiprop":"url|size|extmetadata","iiurlwidth":"1900"})
 pages=q.get("query",{}).get("pages",[])
 if not pages or not pages[0].get("imageinfo"):raise ValueError("source metadata unavailable")
 return pages[0]["imageinfo"][0]

def clean(value):
 if isinstance(value,dict):value=value.get("value","")
 return re.sub("<[^>]+>"," ",html.unescape(str(value))).strip()

def license_ok(info):
 ext=info.get("extmetadata") or {}
 l=clean(ext.get("LicenseShortName")).lower()
 allowed=("public domain","pd-art","pdm","cc0","cc by ","cc-by","cc by-sa","cc-by-sa")
 return any(x in l for x in allowed) and "noncommercial" not in l

def norm(s):
 return re.sub(r"[^a-z0-9]+"," ",html.unescape(str(s)).casefold()).strip()

def match_work(filename,works):
 label=norm(filename.replace("_"," ").rsplit(".",1)[0])
 best=None
 for i,work in enumerate(works):
  tokens=norm(work).split()
  # Match whole term/phrase; do not infer source identity from similar style.
  candidate=" ".join(tokens)
  if candidate in label:
   score=100+len(tokens)*3-i*.1
   if best is None or score>best[0]:best=(score,i,work)
  elif len(tokens)>2 and all(x in label for x in tokens if len(x)>3):
   score=45+len(tokens)
   if best is None or score>best[0]:best=(score,i,work)
 return best

def candidate_page(filename):
 return "https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(filename.replace(" ","_"))

def fallback_url(filename):
 name=filename.replace(" ","_")
 key=hashlib.md5(name.encode("utf8")).hexdigest()
 return "https://upload.wikimedia.org/wikipedia/commons/"+key[0]+"/"+key[:2]+"/"+urllib.parse.quote(name,safe="._-")

def discover(profile):
 found={}
 for name in SEEDS.get(profile["slug"],[]):
  found[name]=None
 for phrase in profile["search_queries"][:2]:
  try:
   result=api({"generator":"search","gsrsearch":phrase,
     "gsrnamespace":"6","gsrlimit":"50","prop":"imageinfo",
     "iiprop":"url|size|extmetadata","iiurlwidth":"1900"})
   for item in result.get("query",{}).get("pages",[]):
    title=item.get("title","")
    if title.startswith("File:") and item.get("imageinfo"):
     found[title[5:]]=item["imageinfo"][0]
   print("SEARCH_OK",profile["slug"],phrase,len(found),flush=True)
  except Exception as e:
   print("SEARCH_UNAVAILABLE",profile["slug"],phrase,str(e)[:120],flush=True)
 result=[]
 for filename,info in found.items():
  if not filename.lower().endswith((".jpg",".jpeg",".png",".webp")):continue
  match=match_work(filename,profile["works"])
  if not match:continue
  rank,work_id,work=match
  if "detail" in norm(filename) or "crop" in norm(filename):rank-=25
  if "google art project" in norm(filename):rank+=4
  if filename in SEEDS.get(profile["slug"],[]):rank+=15
  result.append((rank,work_id,work,filename,info))
 return sorted(result,key=lambda a:-a[0])[:70]

def collect(profile,root):
 assets=root/"SOURCE_PAINTINGS"
 assets.mkdir(parents=True,exist_ok=True)
 works=[];errors=[];picked=set();source_sha=set()
 candidates=discover(profile)
 artist_surname=norm(profile["artist"]).split()[-1]
 for rank,work_idx,work,filename,info in candidates:
  if len(works)>=min(10,len(profile["works"])):break
  if work_idx in picked:continue
  try:
   if not info:info=file_info(filename)
   if not license_ok(info):raise ValueError("source image license not documented as free")
   ext=info.get("extmetadata") or {}
   author=clean(ext.get("Artist"))
   # Commons creator record may be a complex template; if it gives another
   # named painter, exclude rather than claim authenticity.
   if author and artist_surname not in norm(author):
    if "unknown" not in norm(author):raise ValueError("artist metadata conflict "+author[:85])
   uri=info.get("thumburl") or info.get("url") or fallback_url(filename)
   raw=fetch(uri,size=26000000,tries=2)
   with Image.open(io.BytesIO(raw)) as original:
    original.load()
    if original.format not in ("JPEG","PNG","WEBP"):raise ValueError("not an image")
    im=ImageOps.exif_transpose(original).convert("RGB")
   if min(im.size)<550:raise ValueError("image dimensions too small")
   if max(im.size)>2800:im.thumbnail((2800,2800),Image.Resampling.LANCZOS)
   identity=hashlib.sha256(im.tobytes()).hexdigest()
   if identity in source_sha:raise ValueError("duplicate image")
   target=assets/("WORK_%02d.jpg"%(len(works)+1))
   im.save(target,quality=91,optimize=True)
   source_sha.add(identity)
   record={"work":work,"artist":profile["artist"],"original_file":filename,
    "image_source":candidate_page(filename),"download_uri":uri,
    "license":clean(ext.get("LicenseShortName")),
    "license_url":clean(ext.get("LicenseUrl")),"attribution":clean(ext.get("Attribution"))[:1300],
    "artist_metadata":author[:350],"pixels":[im.width,im.height],"bytes":target.stat().st_size,
    "sha256":sha(target),"file":str(target)}
   works.append(record);picked.add(work_idx)
   print("VERIFIED_ARTWORK",profile["slug"],len(works),work,im.size,flush=True)
  except Exception as e:
   errors.append({"file":filename,"reason":str(e)[:180]})
   print("SOURCE_REJECTED",profile["slug"],work,str(e)[:110],flush=True)
  time.sleep(.3)
 if len(works)<6:
  raise RuntimeError(f"BLOCKED_SOURCE {profile['slug']}: only {len(works)} verified works of 6; {errors[:4]}")
 return works,errors

def font(sz,serif=False):
 file="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf" if serif else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
 try:return ImageFont.truetype(file,sz)
 except OSError:return ImageFont.load_default()

def full_frame(filename):
 im=Image.open(filename).convert("RGB")
 bg=ImageOps.fit(im,(W,H),method=Image.Resampling.LANCZOS)
 bg=bg.filter(ImageFilter.GaussianBlur(46)).point(lambda z:int(z*.24))
 raw=ImageOps.contain(im,(W-26,H-145),method=Image.Resampling.LANCZOS)
 bg.paste(raw,((W-raw.width)//2,(H-raw.height)//2))
 return bg

def detail_frame(filename,position):
 im=Image.open(filename).convert("RGB")
 return ImageOps.fit(im,(W,H),method=Image.Resampling.LANCZOS,centering=position)

def caption_frame(im,label="",intro=None):
 result=im.copy();d=ImageDraw.Draw(result)
 if intro:
  d.rectangle((0,20,W,157),fill=(12,16,20))
  d.text((W//2,35),intro["artist"].upper(),anchor="mt",
         font=font(29,True),fill=(238,228,211))
  d.text((W//2,103),intro["public_title"].upper(),anchor="mt",
         font=font(17),fill=(209,201,192))
 elif label:
  d.rounded_rectangle((55,H-128,W-55,H-67),radius=10,fill=(16,18,23))
  d.text((W//2,H-111),label[:39],anchor="mt",
        font=font(20,True),fill=(235,225,205))
 return result

def make_beats(profile,works):
 # Time only flows from the genuine, selected works, not from a generic
 # slideshow of fixed 3-second shots. Every selected work appears COMPLETE.
 target=float(profile["target_seconds"]);n=len(works)
 each=target/n
 beats=[]
 for i,p in enumerate(works):
  full=max(3.0,min(5.2,each*(.74 if i%4 in (1,2) else .93)))
  more=each-full
  # Certain complex paintings deserve a full uninterrupted hold.
  if i in (0,n-1):full=each;more=0
  if i%4==0 and i>0:full=each;more=0
  if more<1.3:full=each;more=0
  beats.append((i,"full",round(full,3)))
  if more:
   beats.append((i,"detail",round(more,3)))
 # ensure two compositions at least 4 seconds and 65% total time is full
 assert sum(b[2] for b in beats if b[1]=="full")/sum(b[2] for b in beats)>.65
 return beats

def make_gallery(profile,assets,errors,out):
 beats=make_beats(profile,assets);files=[];story=[];pos=0
 for k,(i,kind,seconds) in enumerate(beats):
  work=assets[i]
  if kind=="full":
   frame=full_frame(work["file"])
  else:
   frame=detail_frame(work["file"],(.50,.44 if i%2==0 else .54))
  frame=caption_frame(frame,work["work"] if kind=="full" and k>0 else "",
                      intro=profile if k==0 else None)
  img=out/("SCENE_%02d.jpg"%(k+1))
  frame.save(img,quality=92,optimize=True)
  files.append((img,seconds))
  story.append({"source_sha256":work["sha256"],"painting":work["work"],
                "kind":kind,"start_s":round(pos,3),"seconds":seconds,
                "camera_reason":"show actual full composition" if kind=="full" else "brief look at an original detail"})
  pos+=seconds
 real_duration=round(pos,3)
 script=out/"SCENES.ffconcat";lines=["ffconcat version 1.0"]
 for image,length in files:
  lines+=["file '"+image.resolve().as_posix()+"'","duration "+str(length)]
 lines.append("file '"+files[-1][0].resolve().as_posix()+"'")
 script.write_text("\n".join(lines)+"\n",encoding="utf8")
 source_song=out/"SOUNDTRACK_ORIGINAL.mp3"
 audio_data=fetch(profile["music"]["url"],size=24000000)
 if len(audio_data)<100000:raise ValueError("music download too small")
 source_song.write_bytes(audio_data)
 song=json.loads(run(["ffprobe","-v","error","-show_format","-show_streams",
                      "-of","json",source_song],timeout=45))
 if not any(x.get("codec_type")=="audio" for x in song["streams"]):raise ValueError("music has no audio")
 if float(song["format"]["duration"])<real_duration+8:raise ValueError("music shorter than video")
 video=out/(profile["slug"].upper()+"_GALLERY_REVIEW.mp4")
 run(["ffmpeg","-y","-hide_banner","-loglevel","error",
       "-safe","0","-f","concat","-i",script,"-ss","7","-i",source_song,
       "-filter_complex",f"[0:v]fps={FPS},scale={W}:{H},format=yuv420p[v];"
          f"[1:a]afade=t=in:st=0:d=0.75,"
          f"afade=t=out:st={max(1,real_duration-1.8):.2f}:d=1.7,"
          "loudnorm=I=-18:TP=-2:LRA=8[a]",
       "-map","[v]","-map","[a]","-t",str(real_duration),
       "-c:v","libx264","-preset","veryfast","-crf","19",
       "-c:a","aac","-b:a","160k","-movflags","+faststart",video],timeout=420)
 probe=json.loads(run(["ffprobe","-v","error","-show_streams","-show_format","-of","json",video],timeout=50))
 v=next((s for s in probe["streams"] if s.get("codec_type")=="video"),{})
 a=next((s for s in probe["streams"] if s.get("codec_type")=="audio"),{})
 duration=float(probe["format"]["duration"])
 if v.get("codec_name")!="h264" or a.get("codec_name")!="aac":raise RuntimeError("QA_BAD_CODECS")
 if [v.get("width"),v.get("height")]!=[W,H]:raise RuntimeError("QA_BAD_SIZE")
 if abs(duration-real_duration)>.35:raise RuntimeError("QA_BAD_DURATION")
 run(["ffmpeg","-v","error","-xerror","-i",video,"-f","null","-"],timeout=420)
 last=out/"FINAL_FRAME.jpg"
 run(["ffmpeg","-y","-v","error","-ss",str(max(0,duration-.3)),"-i",video,
      "-frames:v","1",last],timeout=35)
 with Image.open(last) as im:
  pixels=im.convert("L").resize((64,64)).getdata()
  if sum(x<8 for x in pixels)>3500:raise RuntimeError("QA_BLACK_ENDING")
 cover=out/"COVER.jpg";Image.open(files[0][0]).save(cover,quality=93)
 thumbs=[]
 for i,work in enumerate(assets):
  slot=next(s for s in story if s["painting"]==work["work"] and s["kind"]=="full")
  second=min(duration-.3,slot["start_s"]+min(1.0,slot["seconds"]/2))
  frame=out/("QA_%02d.jpg"%(i+1))
  run(["ffmpeg","-v","error","-y","-ss",str(second),"-i",video,
       "-frames:v","1","-vf","scale=240:426",frame],timeout=40)
  thumbs.append(frame)
 sheet=Image.new("RGB",(4*240,math.ceil(len(thumbs)/4)*464),(15,17,20))
 d=ImageDraw.Draw(sheet)
 for i,p in enumerate(thumbs):
  x=(i%4)*240;y=(i//4)*464
  sheet.paste(Image.open(p),(x,y))
  d.text((x+8,y+433),assets[i]["work"][:27],font=font(14),fill=(237,227,212))
 sheet.save(out/"CONTACT_SHEET.jpg",quality=90)
 license_text="\""+profile["music"]["title"]+"\" Kevin MacLeod (incompetech.com). Licensed under CC BY 4.0 https://creativecommons.org/licenses/by/4.0/ . Edited excerpt, gain and fades."
 social=(profile["artist"]+" | "+profile["public_title"]+"\n\n"+
    profile["visual_promise"]+". Genuine works by "+profile["artist"]+
    ", shown as both whole paintings and selected original details.\n\n"+
    "Music: "+license_text+"\n"+
    "Artworks: see SOURCE_MANIFEST.json for each source's credit and license. "+
    "Rights and image reuse must be checked separately before publishing.\n\n"+
    "#ArtHistory #Symbolism #Paintings\n")
 (out/"SOCIAL_CAPTION.txt").write_text(social,encoding="utf8")
 manifest={"schema":"curated-artist-gallery-review-v1","status":"TECHNICAL_PASS_ARTISTIC_PENDING",
           "artist":profile["artist"],"public_title":profile["public_title"],
           "artistic_approval":False,"rights_clearance":"PENDING",
           "publishing_permitted":False,"is_four_by_one":False,
           "rendered":{"path":str(video),"bytes":video.stat().st_size,"sha256":sha(video),
                       "duration_seconds":duration,"resolution":[W,H],"fps":FPS,
                       "video_codec":"h264","audio_codec":"aac","complete_decode":"PASS"},
           "artworks":assets,"shots":story,"failed_source_candidates":errors,
           "music":{"title":profile["music"]["title"],"isrc":profile["music"]["isrc"],
                    "composer":"Kevin MacLeod","license":"CC BY 4.0",
                    "license_page":LICENSE,"source_page":profile["music"]["page"],
                    "recording_sha256":sha(source_song)}}
 (out/"SOURCE_MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 pack=out/(profile["slug"].upper()+"_COMPLETE.zip")
 # Root-level MP4, NO NESTED ZIP: addresses repeated Android complaints.
 with zipfile.ZipFile(pack,"w",zipfile.ZIP_DEFLATED,compresslevel=4) as z:
  for file in [video,cover,out/"CONTACT_SHEET.jpg",out/"SOURCE_MANIFEST.json",out/"SOCIAL_CAPTION.txt"]:
   z.write(file,arcname=file.name)
 with zipfile.ZipFile(pack) as z:
  if z.testzip():raise RuntimeError("QA_BAD_ZIP_CRC")
  members=z.namelist()
  if len([x for x in members if x.endswith(".mp4")])!=1:
   raise RuntimeError("QA_ZIP_MISSING_SINGLE_MP4")
  if z.read(video.name)!=video.read_bytes():
   raise RuntimeError("QA_ZIP_MP4_NOT_INTACT")
 print("GALLERY_COMPLETE",profile["slug"],len(assets),len(story),duration,sha(video),flush=True)
 return {"artist":profile["artist"],"status":manifest["status"],
         "mp4":video.name,"zip":pack.name,"sha256":sha(video),
         "seconds":duration,"artworks":len(assets),"shots":len(story)}

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--artist",choices=["waterhouse","redon","khnopff","moreau","stokes","all"],default="all")
 parser.add_argument("--out",default="output/artist-gallery-first-five")
 args=parser.parse_args()
 config=json.loads(CONF.read_text(encoding="utf8"))
 profiles=config["profiles"]
 targets=profiles if args.artist=="all" else [next(p for p in profiles if p["slug"]==args.artist)]
 out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
 results=[]
 for i,p in enumerate(targets):
  folder=out/p["slug"];folder.mkdir(parents=True,exist_ok=True)
  try:
   works,errors=collect(p,folder)
   result=make_gallery(p,works,errors,folder)
  except Exception as e:
   result={"artist":p["artist"],"status":"BLOCKED_NOT_RENDERED","reason":str(e)[:600]}
   print("GALLERY_BLOCKED",p["slug"],result["reason"],flush=True)
  results.append(result)
  (out/"SERIES_STATUS.json").write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
  # Avoid Commons 429 cascade.
  if i<len(targets)-1:time.sleep(1.2)
 print("SERIES_SUMMARY",json.dumps(results,ensure_ascii=False),flush=True)
 # Deliver unaffected successes, but signal to user which are blocked.
 if not any(x["status"].startswith("TECHNICAL_PASS") for x in results):return 2
 return 0
if __name__=="__main__":raise SystemExit(main())
