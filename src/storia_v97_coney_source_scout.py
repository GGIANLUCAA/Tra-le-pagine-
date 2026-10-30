#!/usr/bin/env python3
"""Coney Island 1903: one-pass original LOC camera scout; zero billable providers.
No zoom crops presented as distinct scenes. 22 original frames from widely
different timecodes, plus source-geometry/scene diversity metrics.
"""
from pathlib import Path
import json,subprocess,hashlib,cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path("output/storia_coney_v97");R.mkdir(parents=True,exist_ok=True)
PAGE="https://www.loc.gov/item/00563608/"
MOV=R/"SOURCE_ORIGINAL.mov"
MP4=R/"SOURCE_ORIGINAL.mp4"
MOV_SHA="f3458277cb1bb86964fd5effa1f621dfa2c3676fd489939017ccbee190a18408"
def run(a,timeout=240):
 p=subprocess.run(a,capture_output=True,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError("CMD_FAIL "+str(a[:4])+" "+p.stderr[-600:])
 return p.stdout
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for q in iter(lambda:f.read(1<<20),b""):h.update(q)
 return h.hexdigest()
def main():
 if MOV.exists() and sha(MOV)==MOV_SHA:source=MOV
 elif MP4.exists() and MP4.stat().st_size>1000000:source=MP4
 else:raise RuntimeError("PROVENANCE_SOURCE_MISSING")
 meta=json.loads(run(["ffprobe","-v","error","-show_entries","format=duration,size:stream=codec_name,width,height,r_frame_rate","-of","json",str(source)]))
 duration=float(meta["format"]["duration"]);v=next(x for x in meta["streams"] if x.get("width"))
 if duration<55 or v["width"]<1000 or v["height"]<750:raise RuntimeError("LOW_QUALITY_SOURCE_OR_TOO_SHORT")
 cap=cv2.VideoCapture(str(source))
 if not cap.isOpened():raise RuntimeError("SOURCE_DECODER_FAILED")
 # Entire movie sampled at 5-second increments; allow 15 distinct labels.
 times=sorted(set([round(x,1) for x in np.linspace(7,duration-7,min(28,max(14,int(duration/5))))]))
 cards=[];items=[]
 for i,t in enumerate(times):
  cap.set(cv2.CAP_PROP_POS_MSEC,t*1000)
  ok,f=cap.read()
  if not ok:continue
  h,w=f.shape[:2]
  # A stable 9:16 center crop preserves one real source camera viewpoint per shot.
  cw=round(h*9/16)
  if w<cw:raise RuntimeError("SOURCE_ASPECT_NOT_COMPATIBLE")
  x0=(w-cw)//2
  crop=f[:,x0:x0+cw]
  scaled=cv2.resize(crop,(720,1280),interpolation=cv2.INTER_CUBIC)
  p=R/f"ORIGINAL_{i:02d}_{t:05.1f}.jpg"
  cv2.imwrite(str(p),scaled,[cv2.IMWRITE_JPEG_QUALITY,94])
  small=cv2.resize(cv2.cvtColor(scaled,cv2.COLOR_BGR2GRAY),(90,160))
  sharp=float(cv2.Laplacian(small,cv2.CV_32F).var())
  contrast=float(np.percentile(small,95)-np.percentile(small,5))
  diff=float(np.mean(abs(small.astype("float32")-cards[-1][1].astype("float32")))) if cards else None
  cards.append((p,small))
  items.append({"time_s":t,"source_image":p.name,"sha256":sha(p),"native_crop_w":cw,"native_h":h,"sharpness":round(sharp,2),"contrast":round(contrast,2),"diff_previous":round(diff,2) if diff is not None else None})
 cap.release()
 if len(cards)<12:raise RuntimeError("INSUFFICIENT_REAL_SOURCE_VISUAL_CANDIDATES")
 cols=7;rows=(len(cards)+cols-1)//cols;pw,ph=184,354
 sheet=Image.new("RGB",(cols*pw,rows*ph),(16,20,26));draw=ImageDraw.Draw(sheet)
 for i,((p,small),rec) in enumerate(zip(cards,items)):
  x=i%cols*pw;y=i//cols*ph
  image=Image.open(p).convert("RGB").resize((180,320))
  sheet.paste(image,(x+2,y+27))
  draw.text((x+6,y+5),f"{rec['time_s']:05.1f}s  sharp {rec['sharpness']:.0f}",fill="white")
 sheet.save(R/"FULL_FILM_TIMECODE_SCOUT.jpg",quality=89)
 report={"source":PAGE,"film_file":source.name,"film_sha256":sha(source),"duration_s":duration,
         "native_resolution":[v["width"],v["height"]],"candidate_count":len(items),
         "frames":items,"scene_selection":"PENDING_ACTUAL_VISUAL_DIVERSITY_REVIEW",
         "paid_vidu_credits":0,"no_automatic_same_shot_repetition":True}
 (R/"SCOUT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 print("CONEY_V97_SOURCE_SCOUT_OK",len(items),"duration",duration,
      "native",v["width"],v["height"],"MOV_sha",sha(source),flush=True)
if __name__=="__main__":main()
