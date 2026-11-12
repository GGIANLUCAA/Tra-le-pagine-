#!/usr/bin/env python3
"""Giuliano Antikythera: non-commercial-research source scouting, actual bytes+licenses.

Fetch only explicitly listed authentic museum photographs (Wikimedia Commons)
and MIT-repo CC BY 4.0 silent 3D render clips. Never scrape unauthorized
archival dive footage; no TTS, AI image generation or publication.
"""
from __future__ import annotations
import argparse, hashlib, json, subprocess, time, urllib.parse
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image, ImageOps, ImageDraw, ImageFont

PHOTOS = [
 "The Antikythera Mechanism (3471161471).jpg",
 "The Antikythera Mechanism (3471171927).jpg",
 "The Antikythera Mechanism (3471976134).jpg",
 "The Antikythera Mechanism (3471987204).jpg",
 "Antikythera Mechanism - National Archaeological Museum, Athens by Joy of Museum.jpg",
 "Frammenti del meccanismo di antikythera, usato come calcolatore e calendatio astronomico, 150-100 ac ca. 01.jpg",
 "Frammenti del meccanismo di antikythera, usato come calcolatore e calendatio astronomico, 150-100 ac ca. 02.jpg",
 "Frammenti del meccanismo di antikythera, usato come calcolatore e calendatio astronomico, 150-100 ac ca. 06.jpg",
 "Frammenti del meccanismo di antikythera, usato come calcolatore e calendatio astronomico, 150-100 ac ca. 08.jpg",
]
MOTION = [
 ("antikythera_gears_20s.mp4",
  "https://raw.githubusercontent.com/taciclei/antikythera-mechanism/main/build/out/renders/antikythera.mp4",
  "Modern hypothesis: 2021-modelled astronomical gears, NOT genuine antiquity"),
 ("antikythera_exploded_15s.mp4",
  "https://raw.githubusercontent.com/taciclei/antikythera-mechanism/main/build/out/renders/antikythera_eclate.mp4",
  "Modern exploded reconstruction; some parts hypothetical"),
]
USER_AGENT = "GiulianoAntikytheraEditorial/1.0 (public education media verification; see github.com/GGIANLUCAA/Tra-le-pagine-)"
MAX_BYTES=25_000_000

def fetch(url, timeout=60):
 req=Request(url,headers={"User-Agent":USER_AGENT,"Accept":"*/*"})
 with urlopen(req,timeout=timeout) as r:
  body=r.read(MAX_BYTES+1)
  if len(body)>MAX_BYTES:
   raise RuntimeError("Source exceeds restricted 25MB scout limit")
  return body

def sha(data):
 return hashlib.sha256(data).hexdigest()

def duration(path):
 cmd=["ffprobe","-v","error","-show_entries","format=duration","-of","default=nokey=1:noprint_wrappers=1",str(path)]
 return round(float(subprocess.check_output(cmd,text=True,timeout=20).strip()),3)

def commons_info():
 q={"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata|size",
    "iiurlwidth":"1600","titles":"|".join("File:"+x for x in PHOTOS)}
 url="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(q)
 data=json.loads(fetch(url,timeout=70))
 records={}
 for p in data["query"]["pages"].values():
  if not p.get("imageinfo"):continue
  inf=p["imageinfo"][0]
  ext=inf.get("extmetadata",{})
  lic=ext.get("LicenseShortName",{}).get("value","")
  title=p.get("title","").removeprefix("File:")
  if ("cc by" not in lic.lower() and "cc-by" not in lic.lower()) or "-nc" in lic.lower() or "-nd" in lic.lower():
   print("SOURCE_LICENSE_BLOCKED",title,lic,flush=True)
   continue
  records[title]=dict(metadata=inf,title=title,license=lic,
    rights_url=ext.get("LicenseUrl",{}).get("value",""),
    credit_url="https://commons.wikimedia.org/wiki/"+urllib.parse.quote("File:"+title.replace(" ","_")))
 return records

def make_contact(items,path):
 pics=[]
 for item in items:
  if item.get("type")=="photo":
   try:
    im=Image.open(item["local_path"]).convert("RGB")
    img=ImageOps.fit(im,(270,310),Image.Resampling.LANCZOS)
    pics.append((item["name"][:34],img))
   except Exception:pass
 cols=3;cellw=300;cellh=375
 out=Image.new("RGB",(cols*cellw,((len(pics)+cols-1)//cols)*cellh),(16,23,29))
 d=ImageDraw.Draw(out)
 for i,(name,img) in enumerate(pics):
  x=(i%cols)*cellw;y=(i//cols)*cellh
  out.paste(img,(x+15,y+15))
  d.text((x+15,y+330),name,fill=(241,225,196))
 out.save(path,quality=91)

def main(argv=None):
 p=argparse.ArgumentParser()
 p.add_argument("--out-dir",required=True)
 opts=p.parse_args(argv)
 out=Path(opts.out_dir)
 out.mkdir(parents=True,exist_ok=True)
 images=out/"museum_photos"; images.mkdir(exist_ok=True)
 items=[]; errors=[]
 try:
  rec=commons_info()
 except Exception as exc:
  rec={}
  errors.append("Wikimedia license API unavailable: "+type(exc).__name__)
 for i,name in enumerate(PHOTOS):
  item=rec.get(name)
  if not item:
   errors.append("No open licensed metadata: "+name)
   continue
  info=item["metadata"]
  url=info.get("thumburl") or info["url"]
  try:
   data=fetch(url,timeout=90)
   fn=images/("authentic_%02d.jpg"%(i+1))
   fn.write_bytes(data)
   with Image.open(fn) as im:im.verify()
   if len(data)<10000:raise RuntimeError("image suspiciously small")
   authenticity=("modern_reconstruction" if i in (0,2) else "original_fragment_candidate")
   items.append({"type":"photo","name":name,"depicts":authenticity,"local_path":str(fn),"bytes":len(data),
       "sha256":sha(data),"license":item["license"],"credit_url":item["credit_url"],
       "rights_url":item["rights_url"],"source_url":url,"source_status":"binary_downloaded_checksum_verified"})
   print("VERIFIED_MUSEUM_SOURCE",name,len(data),flush=True)
  except Exception as exc:
   errors.append(name+": "+type(exc).__name__)
  time.sleep(.15)
 for name,url,note in MOTION:
  try:
   data=fetch(url,timeout=90)
   f=out/name;f.write_bytes(data)
   if len(data)<10000:raise RuntimeError("very small MP4")
   seconds=duration(f)
   if seconds < 8 or seconds > 35:raise RuntimeError("unexpected video duration")
   items.append({"type":"reconstruction_video","name":name,"local_path":str(f),
      "bytes":len(data),"sha256":sha(data),"duration_s":seconds,
      "license":"CC BY 4.0","credit":"Antikythera Mechanism reconstruction by taciclei",
      "rights_url":"https://github.com/taciclei/antikythera-mechanism/blob/main/LICENSE-MEDIA.md",
      "source_url":url,"scientific_warning":note,"status":"candidate_video_verified_not_historical_record"})
   print("VERIFIED_MODERN_MOTION",name,seconds,len(data),flush=True)
  except Exception as exc:
   errors.append(name+": "+type(exc).__name__+" "+str(exc)[:140])
 make_contact(items,out/"CONTATTO_REPERTI_AUTENTICI.jpg")
 report={"schema":"giuliano-antikythera-media-scout-v1",
   "status":"candidate_sources_downloaded_preproduction" if sum(i["type"]=="photo" for i in items)>=3 and sum(i["type"]=="reconstruction_video" for i in items)==2 else "incomplete_do_not_render",
   "museum_photos_verified":sum(i["type"]=="photo" for i in items),
   "modern_reconstruction_photos":sum(i.get("depicts")=="modern_reconstruction" for i in items),
   "original_fragment_candidate_photos":sum(i.get("depicts")=="original_fragment_candidate" for i in items),
   "modern_motion_videos_verified":sum(i["type"]=="reconstruction_video" for i in items),
   "authentic_1900_diving_footage_found":False,
   "ready_for_film":False,"narration_synced":False,"artistic_approval":False,
   "credit_and_license_notes":"Original photos and 3D CC BY sources cited individually. Hypothetical planetary gears must be labeled. No blanket rights to museum/expedition footage.",
   "errors":errors,"items":items}
 (out/"FONTI_VIDEO_QA.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("ANTIKYTHERA_REAL_MEDIA_SCOUT",report["status"],len(items),"issues",len(errors),flush=True)
 return 0 if report["status"]=="candidate_sources_downloaded_preproduction" else 2

if __name__=="__main__":
 import sys
 sys.exit(main())
