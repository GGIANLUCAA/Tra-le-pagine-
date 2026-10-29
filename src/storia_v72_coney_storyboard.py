#!/usr/bin/env python3
"""Coney Island source storyboard from the genuine LOC ProRes master."""
import importlib.util
from pathlib import Path
import cv2
from PIL import Image,ImageDraw,ImageFont

root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("source",root/"src/storia_v72_coney_primary_scout.py")
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
# source scout actually runs at import, downloads the ProRes
p=Path("output/storia_v72_coney/SOURCE_ORIGINAL.mov")
out=p.parent
if not p.is_file():raise SystemExit("No master")
cap=cv2.VideoCapture(str(p))
if not cap.isOpened():raise SystemExit("Cannot decode ProRes")
fps=cap.get(cv2.CAP_PROP_FPS);total=cap.get(cv2.CAP_PROP_FRAME_COUNT)/fps
print("LOC_MASTER_REAL",fps,total,flush=True)
try:f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",18)
except:f=ImageFont.load_default()
for start in (0,36,72):
 board=Image.new("RGB",(4*320,6*263),(15,17,18));draw=ImageDraw.Draw(board)
 for i,t in enumerate(range(start,min(start+36,int(total)),2)):
  cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,fr=cap.read()
  if not ok:continue
  rgb=cv2.cvtColor(fr,cv2.COLOR_BGR2RGB)
  small=Image.fromarray(rgb).resize((310,232))
  x=i%4*320+5;y=i//4*263+5
  board.paste(small,(x,y));draw.text((x+5,y+232),f"{t:03d} sec",font=f,fill=(240,240,230))
 target=out/f"CONTI_{start:03d}_{start+36:03d}.jpg";board.save(target,quality=87)
 print("STORYBOARD",target,target.stat().st_size,flush=True)
cap.release()
