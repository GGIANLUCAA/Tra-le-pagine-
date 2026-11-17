#!/usr/bin/env python3
"""New 1905 NYC Subway film scout — original PD Bitzer, QA only, no AI API or spend.
File provenance from Wikimedia Commons page; intentionally detects that one film
might not actually contain five visually DISTINCT moments before video generation.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,subprocess,urllib.request,cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path("output/storia_subway_1905_v1");R.mkdir(parents=True,exist_ok=True)
SOURCE=R/"NY_SUBWAY_1905_GW_BITZER_ORIGINAL.webm"
URL="https://upload.wikimedia.org/wikipedia/commons/c/c4/New_York_Subway_%281905%29_-_G.W._Bitzer_-_Interior_NYC_From_14th_to_42nd_Street.webm"
PAGE="https://commons.wikimedia.org/wiki/File:New_York_Subway_(1905)_-_G.W._Bitzer_-_Interior_NYC_From_14th_to_42nd_Street.webm"
TIMES=[18,42,66,90,114,138,162,186,210,234,258,282,300]
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def fetch():
 if SOURCE.exists() and SOURCE.stat().st_size>40_000_000:return
 req=urllib.request.Request(URL,headers={"User-Agent":"LaStoriaRiviveArchivalScout/1.0 (historical preservation; https://github.com/GGIANLUCAA/Tra-le-pagine-)","Accept":"video/webm"})
 with urllib.request.urlopen(req,timeout=150) as resp,SOURCE.open("wb") as f:
  while data:=resp.read(1<<20):
   f.write(data)
   if f.tell()>105_000_000:raise RuntimeError("FILE_TOO_LARGE")
 if not 60_000_000<SOURCE.stat().st_size<105_000_000:raise RuntimeError("INCOMPLETE_HISTORICAL_SOURCE")
def prep(x):
 g=cv2.cvtColor(cv2.resize(x,(160,120)),cv2.COLOR_BGR2GRAY)
 return g
def contrast(x):
 return float(cv2.Laplacian(prep(x),cv2.CV_64F).var())
def at(cap,t):
 cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,f=cap.read()
 if not ok:raise RuntimeError("FILM_FRAME_UNAVAILABLE_"+str(t))
 return f
def main():
 fetch()
 cap=cv2.VideoCapture(str(SOURCE))
 if not cap.isOpened():raise RuntimeError("COULD_NOT_DECODE_SOURCE")
 fps=float(cap.get(5));count=int(cap.get(7));w,h=int(cap.get(3)),int(cap.get(4))
 duration=count/fps if fps else 0
 if not (w>=950 and h>=700 and 280<duration<350 and 15<fps<45):
  raise RuntimeError("SOURCE_IDENTITY_MISMATCH "+str((w,h,fps,duration)))
 items=[]
 thumbs=[]
 for t in TIMES:
  if t>duration-3:continue
  p=at(cap,float(t));a=at(cap,t-.9);b=at(cap,t+.4)
  pg=prep(p);ag=prep(a);bg=prep(b)
  change=float(np.abs(bg.astype("float32")-ag.astype("float32")).mean())
  exposure=float(pg.mean());sharp=contrast(p)
  item={"t":t,"exposure":round(exposure,1),"motion_change":round(change,1),"sharpness":round(sharp,1)}
  if w>h:
   # 9:16 crop anchored in visible track zone, not invented extra field of view.
   crop_width=int(h*9/16);x=(w-crop_width)//2
   thumb=p[:,x:x+crop_width]
  else:thumb=p
  tall=cv2.resize(thumb,(216,384))
  cv2.imwrite(str(R/f"FRAME_ORIGINAL_{t:03d}.jpg"),tall,[cv2.IMWRITE_JPEG_QUALITY,93])
  item["frame_preview_file"]=f"FRAME_ORIGINAL_{t:03d}.jpg"
  item["frame_sha256"]=sha(R/item["frame_preview_file"])
  item["crop_x"]=x if w>h else 0
  items.append(item);thumbs.append(tall)
 cap.release()
 cols=7;rows=(len(thumbs)+cols-1)//cols
 board=Image.new("RGB",(cols*222,rows*430),(14,18,23));d=ImageDraw.Draw(board)
 for idx,(x,y) in enumerate(zip(items,thumbs)):
  row,col=divmod(idx,cols)
  board.paste(Image.fromarray(cv2.cvtColor(y,cv2.COLOR_BGR2RGB)),(col*222+3,row*430+31))
  d.text((col*222+6,row*430+8),f"{x['t']}s  M{x['motion_change']}  S{x['sharpness']}",fill=(237,232,219))
 board.save(R/"NY_SUBWAY_1905_ORIGINAL_13_MOMENTS_CONTACT.jpg",quality=90)
 output={"source_title":"New York Subway, 1905 — G.W. Bitzer, 14th Street to 42nd Street",
   "source_page":PAGE,"source_sha256":sha(SOURCE),"file_bytes":SOURCE.stat().st_size,
   "width":w,"height":h,"fps":fps,"duration_seconds":duration,
   "source_rights_claim":"Wikimedia Commons lists Public Domain (PDM); Italy publicity review pending",
   "new_paid_vidu_posts":0,"ai_generated_photos":0,
   "original_source_preexisting_repo_episode":False,
   "frames":items,"actual_distinct_shots_human_review":"PENDING",
   "status":"SCOUT_NOT_VIDEO"}
 (R/"SCOUT_QA.json").write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n")
 print("NEW_1905_SUBWAY_REAL_FILM_SCOUT",len(items),"SOURCE",sha(SOURCE),"SIZE",SOURCE.stat().st_size,flush=True)
 print("MOTION",[(x["t"],x["motion_change"],x["exposure"]) for x in items],flush=True)
if __name__=="__main__":main()
