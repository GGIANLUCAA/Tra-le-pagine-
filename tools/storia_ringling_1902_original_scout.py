#!/usr/bin/env python3
"""Ringling Brothers Parade 1902 — real original source scouting, 18 archival moments.
No paid AI. Reject source if original public-domain claim, video or original frames
are missing. Source is 948x720 AV1; this is NOT a restorer / final film.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode,urlparse
import json,hashlib,cv2,numpy as np
from PIL import Image,ImageDraw
OUT=Path("output/storia_ringling_parade_1902_source");OUT.mkdir(parents=True,exist_ok=True)
TITLE="File:Ringling Brothers Parade Film (1902).webm"
PAGE="https://commons.wikimedia.org/wiki/File:Ringling_Brothers_Parade_Film_(1902).webm"
SRC=OUT/"RINGLING_1902_AUTHENTIC_FILM.webm"
TIMES=[8,20,32,44,56,68,80,92,104,116,128,140,152,164,176,188,200,212,224]
UA="LaStoriaRiviveHistoricalSource/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-)"
def sha(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()
def urlopen_safe(uri,t=90):
 return urlopen(Request(uri,headers={"User-Agent":UA,"Accept":"application/json,video/webm"}),timeout=t)
def load():
 uri="https://commons.wikimedia.org/w/api.php?"+urlencode({"action":"query","format":"json","titles":TITLE,"prop":"imageinfo","iiprop":"url|size|sha1|mime"})
 try:
  with urlopen_safe(uri,50) as r:d=json.load(r)
  page=next(iter(d.get("query",{}).get("pages",{}).values()))
  info=page.get("imageinfo",[None])[0]
  if not isinstance(info,dict):raise RuntimeError("NO_PUBLISHED_COMMONS_FILE")
  original=info["url"]
  if urlparse(original).hostname!="upload.wikimedia.org" or not original.startswith("https://"):raise RuntimeError("NOT_OFFICIAL_WIKIMEDIA_UPLOAD")
  size=int(info["size"])
  if not 45_000_000<size<95_000_000:raise RuntimeError("SOURCE_SIZE_CHANGED")
  if not SRC.exists() or SRC.stat().st_size!=size:
   with urlopen_safe(original,180) as resp,SRC.open("wb") as f:
    while block:=resp.read(1<<20):
     f.write(block)
     if f.tell()>100_000_000:raise RuntimeError("SOURCE_SIZE_EXCEEDS_CAP")
  if SRC.stat().st_size!=size:raise RuntimeError("TRUNCATED_SOURCE_FILE")
  if hashlib.sha1(SRC.read_bytes()).hexdigest()!=info["sha1"]:raise RuntimeError("WIKIMEDIA_ORIGINAL_SHA1_DIFFERENT")
  return info
 except Exception as exc:
  raise RuntimeError("RINGLING_SOURCE_ACQUISITION_FAILED_"+str(exc)[:250]) from exc
def frame(cap,t):
 cap.set(cv2.CAP_PROP_POS_MSEC,float(t)*1000)
 ok,f=cap.read()
 if not ok:raise RuntimeError("FRAME_MISSING_"+str(t))
 return f
def main():
 info=load()
 cap=cv2.VideoCapture(str(SRC))
 if not cap.isOpened():raise RuntimeError("AV1_SOURCE_NOT_SUPPORTED_BY_OPENCV")
 w=int(cap.get(3));h=int(cap.get(4));fps=float(cap.get(5));n=int(cap.get(7))
 length=n/fps if fps else 0
 if not (900<=w<=980 and 690<=h<=740 and 230<length<245):
  raise RuntimeError("WRONG_SOURCE_DURATION_OR_GEOMETRY_"+str((w,h,fps,length)))
 rows=[];thumbs=[]
 for t in TIMES:
  if t+2>=length:continue
  orig=frame(cap,t)
  prev=frame(cap,t-.6)
  latter=frame(cap,t+.55)
  gs=cv2.cvtColor(cv2.resize(orig,(220,160)),cv2.COLOR_BGR2GRAY)
  change=float(np.mean(np.abs(cv2.resize(prev,(220,160)).astype("float32")-
                                cv2.resize(latter,(220,160)).astype("float32"))))
  sharp=float(cv2.Laplacian(gs,cv2.CV_64F).var())
  expo=float(gs.mean())
  x=max(0,(w-int(h*.5625))//2);cropw=int(h*.5625)
  tall=cv2.resize(orig[:,x:x+cropw],(216,384),interpolation=cv2.INTER_AREA)
  wide=cv2.resize(orig,(320,240),interpolation=cv2.INTER_AREA)
  pf=OUT/f"SOURCE_{t:03d}_VERTICAL.jpg"
  wf=OUT/f"SOURCE_{t:03d}_WIDE.jpg"
  cv2.imwrite(str(pf),tall,[cv2.IMWRITE_JPEG_QUALITY,94])
  cv2.imwrite(str(wf),wide,[cv2.IMWRITE_JPEG_QUALITY,92])
  rows.append({"second":t,"sharpness":round(sharp,1),"exposure":round(expo,1),
      "motion":round(change,2),"source_original_shot_or_parade_group":"REQUIRES_VISUAL_REVIEW",
      "crop_left":x,"crop_width":cropw,"vertical_sha256":sha(pf),
      "wide_sha256":sha(wf),"preview":pf.name})
  thumbs.append(tall)
 cap.release()
 cols=7;contact=Image.new("RGB",(cols*223,3*432),(14,18,23))
 d=ImageDraw.Draw(contact)
 for j,(row,im) in enumerate(zip(rows,thumbs)):
  x,y=j%cols,j//cols
  contact.paste(Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB)),(x*223+4,y*432+26))
  d.text((x*223+5,y*432+5),f"{row['second']} s M{row['motion']} S{row['sharpness']}",fill=(235,233,218))
 contact.save(OUT/"RINGLING_1902_19_SOURCE_MOMENTS_CONTACT.jpg",quality=92)
 doc={"title":"Ringling Brothers Parade Film 1902 original",
  "source_page":PAGE,"commons_original_sha1":info["sha1"],
  "source_file_sha256":sha(SRC),"bytes":SRC.stat().st_size,
  "width":w,"height":h,"fps":fps,"duration":length,
  "licensing":"Commons declares public domain film; Italian rights/publication independent review pending",
  "reference_benchmark":"San Francisco V98 4I2I+1 genuine Vidu","source_shots":rows,
  "scenes_verified_unique":False,"vidu_posts":0,"generated_photos":0,
  "status":"SCOUT_CONTACT_FOR_HUMAN_SELECTION_NOT_MP4"}
 (OUT/"RINGLING_SOURCE_QA.json").write_text(json.dumps(doc,ensure_ascii=False,indent=2)+"\n")
 print("RINGLING_SOURCE_REAL_CHECKED",w,h,round(length,2),"FRAMES",len(rows),
       "sha",sha(SRC),flush=True)
if __name__=="__main__":main()
