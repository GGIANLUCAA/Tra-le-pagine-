#!/usr/bin/env python3
"""Select a fifth genuinely different source shot from the verified Miles 1906 film.
Read-only: no image generation provider and no paid video generation.
Produce an inspection board of real original black-and-white frames, not fake stills.
"""
import hashlib,os,json,cv2,numpy as np,importlib.util
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path("output/storia_v86_sf1906");ROOT.mkdir(parents=True,exist_ok=True)
PATH=Path("output/storia_v70_sf1906/SAN_FRANCISCO_1906_HD_ORIGINALE.webm")
EXPECTED="c8b30802c0fbeb5f9ec3dc9af3e4f71ef627a863d4abba5550b63998cb46725a"
# Exclude timestamps near previously used archival V70 scenes: 128,164,236,476.
TIMES=[43,75,94,193,269,293,317,347,379,406,442]
def digest(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def main():
 if not PATH.is_file() or digest(PATH)!=EXPECTED:raise RuntimeError("ORIGINAL_SOURCE_1906_HASH_MISMATCH")
 cap=cv2.VideoCapture(str(PATH))
 if int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))!=1440 or int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))!=1072:raise RuntimeError("SOURCE_RASTER_MISMATCH")
 cards=[];catalog=[]
 for t in TIMES:
  cap.set(cv2.CAP_PROP_POS_MSEC,float(t)*1000)
  ok,src=cap.read()
  if not ok:raise RuntimeError(f"MISSING_REAL_SOURCE_FRAME_{t}")
  # centered on people/vehicles in front of the tram's lens
  x=600 if t in (43,75,193,379) else 670
  crop=src[:,x:x+603]
  if crop.shape[:2]!=(1072,603):raise RuntimeError("INVALID_9X16_FRAME")
  full=cv2.resize(crop,(720,1280))
  cv2.imwrite(str(ROOT/f"ORIGINAL_BW_{t:03d}.jpg"),full,[cv2.IMWRITE_JPEG_QUALITY,95])
  gray=cv2.cvtColor(full,cv2.COLOR_BGR2GRAY)
  sharp=float(cv2.Laplacian(cv2.resize(gray,(240,427)),cv2.CV_32F).var())
  delta=float(np.percentile(gray,97)-np.percentile(gray,3))
  catalog.append({"t":t,"x":x,"sha256":digest(ROOT/f"ORIGINAL_BW_{t:03d}.jpg"),"sharpness":round(sharp,2),"contrast_3to97":round(delta,1)})
  cards.append(Image.fromarray(cv2.cvtColor(full,cv2.COLOR_BGR2RGB)).resize((240,427)))
 cap.release()
 w=5*252;h=3*474
 sheet=Image.new("RGB",(w,h),(19,21,24));d=ImageDraw.Draw(sheet)
 try:font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",20)
 except:font=ImageFont.load_default()
 for i,(im,r) in enumerate(zip(cards,catalog)):
  xx=(i%5)*252+4;yy=(i//5)*474+6
  sheet.paste(im,(xx,yy+34))
  d.text((xx,yy+4),f"{r['t']}s · sharp {r['sharpness']:.0f}",font=font,fill="white")
 sheet.save(ROOT/"SCELTA_QUINTA_SCENA_BN.jpg",quality=91)
 (ROOT/"CANDIDATE_FRAMES.json").write_text(json.dumps({"title":"San Francisco, 14 April 1906","source":"https://www.loc.gov/item/00694408/","source_sha256":EXPECTED,"candidates":catalog,"not_the_four_v70_photo_timecodes":[128,164,236,476],"no_paid_calls":True},indent=2)+"\n")
 print("V86_FIFTH_SHOT_CANDIDATES_READY",len(catalog),flush=True)
if __name__=="__main__":main()
