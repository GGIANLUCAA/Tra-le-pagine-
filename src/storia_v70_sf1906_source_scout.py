#!/usr/bin/env python3
"""V70 scout actual high-res 1906 San Francisco footage, no paid inference."""
import hashlib, json, urllib.parse, urllib.request, subprocess, os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import cv2,numpy as np
OUT=Path("output/storia_v70_sf1906");OUT.mkdir(parents=True,exist_ok=True)
TITLE="File:A Trip down market street (1906).webm"
PAGE="https://commons.wikimedia.org/wiki/File:A_Trip_down_market_street_(1906).webm"
SOURCE=OUT/"SAN_FRANCISCO_1906_HD_ORIGINALE.webm"
UA="TraLePagineLaStoriaRivive/0.70 (noncommercial historical research; https://github.com/GGIANLUCAA/Tra-le-pagine-)"
def file_sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def original():
 params=urllib.parse.urlencode({"action":"query","format":"json","formatversion":2,"prop":"imageinfo",
 "titles":TITLE,"iiprop":"url|size|mime|extmetadata"})
 req=urllib.request.Request("https://commons.wikimedia.org/w/api.php?"+params,headers={"User-Agent":UA})
 with urllib.request.urlopen(req,timeout=50) as r:q=json.load(r)
 page=q["query"]["pages"][0]
 if "imageinfo" not in page:raise RuntimeError("Commons file missing")
 meta=page["imageinfo"][0]
 lic=meta.get("extmetadata",{}).get("LicenseShortName",{}).get("value","")
 licenseurl=meta.get("extmetadata",{}).get("LicenseUrl",{}).get("value","")
 print("CC_LICENSE",lic,licenseurl,"file_bytes",meta["size"],flush=True)
 if not any(x in lic.lower() for x in ("public domain","cc0","pd")):
  raise RuntimeError("Source license is NOT marked public domain/CC0")
 if not meta["mime"].startswith("video/") or meta["size"]>165_000_000:
  raise RuntimeError("Unexpected original file")
 if not SOURCE.is_file() or SOURCE.stat().st_size!=meta["size"]:
  with urllib.request.urlopen(urllib.request.Request(meta["url"],headers={"User-Agent":UA}),timeout=160) as s, open(SOURCE,"wb") as f:
   for part in iter(lambda:s.read(1<<20),b""):f.write(part)
 if SOURCE.stat().st_size!=meta["size"]:raise RuntimeError("Truncated source")
 info={"title":TITLE,"page":PAGE,"publisher":"Wikimedia Commons","license_marked":lic,
  "license_url":licenseurl,"file_bytes":meta["size"],"file_sha256":file_sha(SOURCE),
  "source_of_work":"Miles Brothers; 1906 film; original US film; 35mm provenance given on 4k related edition",
  "important":"US public domain tag is not automatically the final territorial clearance or permission to copy later restoration additions"}
 (OUT/"PROVENANCE.json").write_text(json.dumps(info,ensure_ascii=False,indent=2))
 return info
def select():
 cap=cv2.VideoCapture(str(SOURCE))
 fps=cap.get(cv2.CAP_PROP_FPS);w=int(cap.get(3));h=int(cap.get(4));duration=cap.get(cv2.CAP_PROP_FRAME_COUNT)/fps
 if w<1000 or h<700 or not 1<fps<100:raise RuntimeError("Raster/fps too low: "+repr((w,h,fps)))
 print("SCANNED_SOURCE",w,h,fps,duration,flush=True)
 try:font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",18)
 except:font=ImageFont.load_default()
 starts=[8]+list(np.arange(20,min(duration-4,502),12))
 payload=[]
 frames=[]
 for n,t in enumerate(starts):
  cap.set(cv2.CAP_PROP_POS_MSEC,float(t)*1000);ok,frame=cap.read()
  if not ok:continue
  thumb=cv2.resize(frame,(280,210),interpolation=cv2.INTER_AREA)
  gray=cv2.cvtColor(thumb,cv2.COLOR_BGR2GRAY)
  sharp=float(cv2.Laplacian(gray,cv2.CV_32F).var())
  obj={"time_s":round(float(t),2),"sharpness_laplacian":round(sharp,2),"thumbnail_index":len(frames)}
  payload.append(obj);frames.append((t,thumb))
 cap.release()
 for part in range(0,len(frames),24):
  sheet=Image.new("RGB",(6*290,4*250),"#17191c");d=ImageDraw.Draw(sheet)
  for i,(t,frame) in enumerate(frames[part:part+24]):
   x=(i%6)*290+5;y=(i//6)*250+7
   sheet.paste(Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)),(x,y))
   d.text((x,y+212),f"{t:.1f}s • {payload[part+i]['sharpness_laplacian']:.0f}",font=font,fill="#f1f1ee")
  path=OUT/f"TIMELINE_{part//24+1:02d}.jpg"
  sheet.save(path,quality=86)
  print("SHEET_COMPLETE",path,flush=True)
 (OUT/"FILM_SCOUT_INDEX.json").write_text(json.dumps({"fps":fps,"raster":[w,h],"duration_s":duration,
 "sampling":"every 12s, scout only; final freeze frame chosen by reviewing surrounding motion",
 "frames":payload},indent=2))
 print("SCOUT_READY",len(frames),flush=True)
if __name__=="__main__":original();select()
