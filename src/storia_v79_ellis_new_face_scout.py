#!/usr/bin/env python3
"""V79 scout new authentic 1903 Ellis Island historical film source with human-face legibility checks."""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode
import json,hashlib,subprocess,sys
import cv2
from PIL import Image,ImageDraw,ImageFont
import numpy as np

OUT=Path("output/storia_v79_ellis");OUT.mkdir(parents=True,exist_ok=True)
TITLE="File:Emigrants (i.e. immigrants) landing at Ellis Island -.webm"
SOURCE_PAGE="https://commons.wikimedia.org/wiki/File:Emigrants_(i.e._immigrants)_landing_at_Ellis_Island_-.webm"
LOC="https://www.loc.gov/item/00694367/"
def get_source():
 p=OUT/"ELLIS_ISLAND_1903_ORIGINAL.webm"
 if p.exists() and p.stat().st_size>50_000_000:return p
 params=urlencode({"action":"query","format":"json","formatversion":"2","prop":"imageinfo","titles":TITLE,"iiprop":"url|size|mime|extmetadata"})
 query="https://commons.wikimedia.org/w/api.php?"+params
 req=Request(query,headers={"User-Agent":"TraLePagine-ArtVision/1.0 (educational archive research)","Accept":"application/json"})
 with urlopen(req,timeout=55) as r:data=json.load(r)
 pg=data["query"]["pages"][0]
 if "imageinfo" not in pg:raise RuntimeError("Commons source API unavailable or title mismatch "+str(pg))
 info=pg["imageinfo"][0]
 url=info["url"];size=info["size"];mime=info["mime"]
 if mime!="video/webm" or size<50_000_000 or size>100_000_000:raise RuntimeError("Wrong source metadata: "+str(info))
 request=Request(url,headers={"User-Agent":"TraLePagine-ArtVision/1.0 (educational archive research)"})
 with urlopen(request,timeout=140) as r,p.open("wb") as f:
  while block:=r.read(1<<20):f.write(block)
 if p.stat().st_size!=size:raise RuntimeError("Incomplete primary archival video")
 return p

def scout():
 p=get_source()
 cap=cv2.VideoCapture(str(p));fps=cap.get(cv2.CAP_PROP_FPS);w=cap.get(3);h=cap.get(4);dur=cap.get(7)/fps
 if w<1200 or h<900 or dur<120:raise RuntimeError("Wrong source frame size/film duration")
 face_cascade=None
 if hasattr(cv2,"CascadeClassifier") and hasattr(cv2,"data"):
  face_cascade=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
 rows=[]
 for sec in [5,15,25,35,45,55,65,75,85,95,105,115,125,135,143]:
  cap.set(cv2.CAP_PROP_POS_MSEC,sec*1000)
  ok,fr=cap.read()
  if not ok:continue
  mono=cv2.cvtColor(fr,cv2.COLOR_BGR2GRAY)
  # Source has tiny figures: look for 24+ px human faces; detection is a heuristic only, not factual count.
  faces=face_cascade.detectMultiScale(mono,scaleFactor=1.08,minNeighbors=4,minSize=(24,24)) if face_cascade is not None else []
  body=np.mean(cv2.Laplacian(mono,cv2.CV_32F)**2)
  sharp=float(cv2.Laplacian(mono,cv2.CV_32F).var())
  rows.append(dict(second=sec,face_boxes=faces.tolist() if hasattr(faces,"tolist") else [],
                   max_face_px=int(max([ww for xx,yy,ww,hh in faces],default=0)),
                   sharpness=round(sharp,2)))
  cv2.imwrite(str(OUT/f"FRAME_{sec:03d}.png"),fr)
 cap.release()
 if not rows:raise RuntimeError("No true historical movie frames")
 font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",21)
 canvas=Image.new("RGB",(3*450,5*360),(13,15,17));dr=ImageDraw.Draw(canvas)
 for j,s in enumerate(rows):
  rgb=Image.open(OUT/f"FRAME_{s['second']:03d}.png").convert("RGB")
  im=rgb.resize((445,330),Image.Resampling.LANCZOS)
  x=j%3*450+3;y=j//3*360+26
  canvas.paste(im,(x,y))
  dr.text((x+7,y-25),f"{s['second']}s | {len(s['face_boxes'])} faces | max {s['max_face_px']} px",font=font,fill="white")
 canvas.save(OUT/"SCENE_SCOUT_BOARD.jpg",quality=90)
 print("FILM",p,str(p.stat().st_size),w,h,fps,dur,flush=True)
 print("FRAMES",json.dumps(rows),flush=True)
 (OUT/"SCOUT.json").write_text(json.dumps({"page":SOURCE_PAGE,"loc":LOC,"source_sha":hashlib.sha256(p.read_bytes()).hexdigest(),
    "source_size":p.stat().st_size,"fps":fps,"width":w,"height":h,"duration":dur,
    "frame_heuristics":rows,"note":"Human face detections may be false or missed. Only human visual review can confirm."},indent=2,ensure_ascii=False))
if __name__=="__main__":scout()
