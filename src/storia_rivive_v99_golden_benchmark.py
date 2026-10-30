#!/usr/bin/env python3
"""La Storia Rivive V99: empirical regression QA against the ACTUAL user-accepted V98 MP4.

This verifies media bytes, not self-attested success flags. It DOES NOT judge
face beauty, identity, artistic merit or rights. Those remain V91/V94/V96/human.
Only for 4 genuine original-film-to-I2I-photo + 1 source-matched moving Vidu.
Zero paid AI calls, no social publication.
"""
from __future__ import annotations
import argparse, hashlib, json, math, re, subprocess
from pathlib import Path
import cv2
import numpy as np

GOLDEN_SHA="b20726893e067bbae493859ae1c51379c4abab8c2c8768d5c6f2d4ab324b47a8"
GOLDEN_TAG="storia-rivive-san-francisco-1906-v98-4-real-i2i-1-real-vidu"
VERSION="V99_GOLDEN_V98_REGRESSION_GATE"

def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()

def probe(path):
 result=subprocess.run(["ffprobe","-v","error","-show_entries","stream=codec_name,width,height,r_frame_rate:format=duration",
  "-of","json",str(path)],capture_output=True,text=True,timeout=40,check=True)
 d=json.loads(result.stdout)
 streams=d.get("streams",[])
 h264=next((x for x in streams if x.get("codec_name")=="h264"),{})
 frac=h264.get("r_frame_rate","0/1").split("/")
 fps=float(frac[0])/max(1.0,float(frac[-1]))
 return {"duration_s":float(d["format"]["duration"]),"fps":fps,
  "resolution":[h264.get("width"),h264.get("height")],
  "codecs":sorted({x.get("codec_name") for x in streams if x.get("codec_name")})}

def grab(cap,t):
 cap.set(cv2.CAP_PROP_POS_MSEC,max(0,t)*1000)
 ok,f=cap.read()
 return cv2.resize(f,(180,320)) if ok else None

def sat(frame):
 return float(np.mean(cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)[:,:,1]))

def fraction(frame):
 return float(np.mean(cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)[:,:,1]>35))

def movement(a,b):
 if a is None or b is None:return 0.0
 x=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY).astype("float32")
 y=cv2.cvtColor(b,cv2.COLOR_BGR2GRAY).astype("float32")
 return float(np.abs(x-y).mean())

def geometry(a,b):
 if a is None or b is None:return -1.0
 def f(x):
  g=cv2.cvtColor(cv2.resize(x,(100,178)),cv2.COLOR_BGR2GRAY)
  return cv2.GaussianBlur(g,(7,7),0).ravel().astype("float32")
 x,y=f(a),f(b)
 return float(np.corrcoef(x,y)[0,1]) if x.std()>.1 and y.std()>.1 else -1.0

def golden_timeline():
 out=[];t=0.0
 for m in [1.35,1.3,1.4,1.35]:
  bw=round(m*30)/30
  dur=bw+(11+round(1.65*30))/30
  out.append({"kind":"classic_photo","start_s":t,"duration_s":dur,"bw_motion_s":bw})
  t+=dur
 out.append({"kind":"vidu_motion","start_s":t,"duration_s":6.08,"bw_motion_s":1.08})
 return out

def scores(path,scenes):
 cap=cv2.VideoCapture(str(path))
 if not cap.isOpened():raise RuntimeError("VIDEO_NOT_DECODABLE")
 result=[]
 try:
  for i,s in enumerate(scenes):
   t=s["start_s"];bw=s["bw_motion_s"];end=t+s["duration_s"]
   orig=grab(cap,t+min(.20,.3*bw))
   moving=grab(cap,t+min(.70,bw-.15))
   if orig is None or moving is None:raise RuntimeError("ORIGINAL_MOVING_SOURCE_MISSING")
   row={"scene":i+1,"kind":s["kind"],"black_white_saturation":round(sat(orig),2),
    "original_motion_delta":round(movement(orig,moving),2)}
   if s["kind"]=="classic_photo":
    photo=grab(cap,end-.28)
    earlier=grab(cap,end-.68)
    if photo is None or earlier is None:raise RuntimeError("RESTORED_PHOTO_MISSING")
    row.update(color_gain=round(sat(photo)-sat(orig),2),
     colored_area_fraction=round(fraction(photo),4),
     still_motion=round(movement(photo,earlier),2))
   else:
    frames=[grab(cap,t+bw+n) for n in [1.4,2.0,2.6,3.2,3.8,4.4]]
    if any(f is None for f in frames):raise RuntimeError("VIDU_FIVE_SECONDS_NOT_PRESENT")
    deltas=[movement(frames[k-1],frames[k]) for k in range(1,len(frames))]
    row.update(color_gain=round(float(np.median([sat(f) for f in frames]))-sat(orig),2),
     colored_area_fraction=round(float(np.median([fraction(f) for f in frames])),4),
     moving_intervals=sum(d>1.2 for d in deltas),
     motion_deltas=[round(d,2) for d in deltas])
   result.append(row)
 finally:cap.release()
 return result

def approved_reference(path):
 if sha(path)!=GOLDEN_SHA:raise RuntimeError("USER_ACCEPTED_V98_REFERENCE_FILE_HASH_MISMATCH")
 p=probe(path)
 if p["resolution"]!=[720,1280] or abs(p["fps"]-30)>.07 or not {"aac","h264"}.issubset(p["codecs"]):
  raise RuntimeError("GOLDEN_REFERENCE_MEDIA_CORRUPT")
 if abs(p["duration_s"]-19.567)>.12:raise RuntimeError("GOLDEN_REFERENCE_DURATION_CHANGED")
 sc=scores(path,golden_timeline())
 return {"version":VERSION,"reference_sha256":GOLDEN_SHA,"reference_release":GOLDEN_TAG,
  "reference_actual_mp4_scanned":True,"technical_video":p,"per_scene":sc,
  "mean_reference_four_photo_color_fraction":round(float(np.mean([x["colored_area_fraction"] for x in sc[:4]])),4),
  "meaning":"User-accepted artistic baseline, NOT automatic verification of real historical faces or legal rights."}

def structural_checks(manifest):
 fails=[]
 if manifest.get("format")!="storia_rivive" or manifest.get("project_format")!="4classic_1vidu":
  fails.append("WRONG_HISTORICAL_FORMAT")
 shots=manifest.get("scenes")
 if not isinstance(shots,list) or len(shots)!=5:return fails+["FIVE_REAL_SCENES_NOT_PRESENT"]
 if [x.get("kind") for x in shots]!=["classic_photo"]*4+["vidu_motion"]:
  fails.append("FOUR_PHOTOGRAPHS_PLUS_ONE_VIDU_WRONG_ORDER")
 times=set();end=0.0
 for i,x in enumerate(shots,1):
  prefix=f"SCENE_{i}_"
  t=x.get("start_s");bw=x.get("bw_motion_s");duration=x.get("duration_s")
  if any(type(v) not in (float,int) for v in (t,bw,duration)):
   fails.append(prefix+"TIMING_MISSING");continue
  if abs(t-end)>.12:fails.append(prefix+"TIMELINE_GAP_OR_OVERLAP")
  end=t+duration
  if not .45<=bw<=2.5:fails.append(prefix+"ORIGINAL_MOVEMENT_OUT_OF_RANGE")
  identity=(x.get("source_film_sha256"),x.get("source_timecode_s"))
  if identity in times:fails.append(prefix+"ORIGINAL_SOURCE_REPEATED")
  times.add(identity)
  if not isinstance(identity[0],str) or not re.fullmatch(r"[0-9a-f]{64}",identity[0]):
   fails.append(prefix+"SOURCE_FILM_HASH_NOT_VERIFIED")
  if type(identity[1]) not in (float,int):fails.append(prefix+"SOURCE_TIME_NOT_VERIFIED")
  if i<5:
   fade=x.get("reveal_s");hold=x.get("color_photo_hold_s")
   if type(fade) not in (float,int) or type(hold) not in (float,int):
    fails.append(prefix+"FREEZE_REVEAL_OR_HOLD_MISSING")
   elif not (.12<=fade<=.95 and .9<=hold<=3.05 and abs(bw+fade+hold-duration)<.15):
    fails.append(prefix+"PHOTO_DURATION_OR_REVEAL_WRONG")
   if x.get("restoration_model") not in ("Finegrain+DDColor","verified_photographic_image_to_image"):
    fails.append(prefix+"DDCOLOR_ONLY_IS_NOT_A_REAL_PHOTO_RESTORATION")
  elif not 4.5<=duration-bw<=5.5:fails.append(prefix+"VIDU_NOT_FIVE_SECONDS")
 if not 14<=end<=35:fails.append("TOTAL_VIDEO_DURATION_WRONG")
 return fails

def file(folder,x,name,key,errors,tag):
 filename=x.get(name)
 if not isinstance(filename,str) or not filename or filename!=Path(filename).name:
  errors.append(tag+"_MISSING_FILENAME");return None
 p=Path(folder)/filename
 if not p.is_file():errors.append(tag+"_MISSING_FILE");return None
 if sha(p)!=x.get(key):errors.append(tag+"_SHA256_MISMATCH");return None
 return p

def evaluate(video,manifest,asset_folder,reference):
 errors=structural_checks(manifest)
 warnings=[]
 p=probe(video);fingerprint=sha(video)
 if p["resolution"]!=[720,1280] or abs(p["fps"]-30)>.07 or not {"aac","h264"}.issubset(p["codecs"]):
  errors.append("VIDEO_NOT_720X1280_H264_AAC_30FPS")
 if manifest.get("final_video_sha256")!=fingerprint:
  errors.append("FINAL_MP4_ACTUAL_SHA256_NOT_VERIFIED")
 film=file(asset_folder,manifest,"historical_film_file","historical_film_sha256",errors,"REAL_ARCHIVAL_FILM")
 timeline=manifest.get("scenes",[])
 if len(timeline)==5:
  if abs(sum(x.get("duration_s",0) for x in timeline)-p["duration_s"])>.18:
   errors.append("FIVE_SCENE_TIMELINE_DIFFERS_FROM_ACTUAL_MP4")
  source=cv2.VideoCapture(str(film)) if film is not None else None
  output=cv2.VideoCapture(str(video))
  for j,x in enumerate(timeline):
   tag=f"SCENE_{j+1}_"
   if x.get("source_film_sha256")!=manifest.get("historical_film_sha256"):
    errors.append(tag+"NOT_FROM_SAME_VERIFIED_FILM")
   original=file(asset_folder,x,"source_frame_file","source_frame_sha256",errors,tag+"SOURCE_FRAME")
   if original is None:continue
   im=cv2.imread(str(original))
   if im is None:errors.append(tag+"ORIGINAL_PICTURE_DECODE_FAILED");continue
   if source is not None:
    crop=x.get("source_crop",{});left=crop.get("left");width=crop.get("width")
    fw=int(source.get(cv2.CAP_PROP_FRAME_WIDTH));fh=int(source.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if type(left) is not int or type(width) is not int or left<0 or width<80 or left+width>fw or abs(fh/width-16/9)>.05:
     errors.append(tag+"ARCHIVAL_CROP_NOT_VERIFIABLE")
    else:
     source.set(cv2.CAP_PROP_POS_MSEC,x["source_timecode_s"]*1000)
     ok,film_frame=source.read()
     if not ok or geometry(im,film_frame[:,left:left+width])<.85:
      errors.append(tag+"ORIGINAL_ARCHIVE_FRAME_DIFFERS_FROM_PHOTO_SOURCE")
   bw_last=grab(output,x["start_s"]+x["bw_motion_s"]-.035)
   if bw_last is None or geometry(im,bw_last)<.73:
    errors.append(tag+"MOVING_BW_TO_PHOTO_IS_NOT_SAME_ORIGINAL_FRAME")
   if j<4:
    photo=file(asset_folder,x,"restored_photo_file","restored_photo_sha256",errors,tag+"I2I_PHOTO")
    if photo:
     pic=cv2.imread(str(photo))
     if pic is None or geometry(im,pic)<.70:
      errors.append(tag+"RECONSTRUCTION_ALTERS_SOURCE_GEOMETRY")
     elif geometry(pic,grab(output,x["start_s"]+x["duration_s"]-.28))<.83:
      errors.append(tag+"ACTUAL_VIDEO_PHOTO_DIFFERS_FROM_VERIFIED_RESTORATION")
   else:
    clip=file(asset_folder,x,"vidu_clip_file","vidu_clip_sha256",errors,tag+"REAL_VIDU")
    if clip:
     v=cv2.VideoCapture(str(clip))
     vfirst=grab(v,.035);v.release()
     if vfirst is None or geometry(im,vfirst)<.74:
      errors.append(tag+"VIDU_FIRST_FRAME_NOT_FROM_EXACT_HISTORIC_SHOT")
  output.release()
  if source is not None:source.release()
 measured=[]
 if not errors:
  measured=scores(video,timeline)
  for j,x in enumerate(measured[:4],1):
   if x["color_gain"]<=3:errors.append(f"SCENE_{j}_PHOTO_COLOR_NOT_REVEALED")
   if x["still_motion"]>5:warnings.append(f"SCENE_{j}_PHOTO_UNEXPECTEDLY_MOVING")
  avg=float(np.mean([x["colored_area_fraction"] for x in measured[:4]]))
  accepted=reference["mean_reference_four_photo_color_fraction"]
  if avg < accepted*.7:errors.append("FOUR_PHOTOS_FALL_BELOW_V98_COLOR_VISIBILITY_FLOOR")
  if measured[4]["moving_intervals"]<3:errors.append("VIDU_STOPPED_MOVING_AFTER_COLOR_REVEAL")
  if measured[4]["color_gain"]<=12:errors.append("VIDU_BW_TO_COLOR_NOT_VISIBLE")
 if manifest.get("visual_review_completed") is not True:
  warnings.append("REAL_HUMAN_VISUAL_COMPARISON_WITH_V98_PENDING")
 if manifest.get("rights_verified_for_publication") is not True:
  warnings.append("ITALIAN_PUBLICATION_RIGHTS_PENDING")
 return {"version":VERSION,"passed":not errors,"status":"TECHNICAL_PASS_REVIEW_PENDING" if not errors else "BLOCKED",
  "reference_sha256":GOLDEN_SHA,"actual_video_sha256":fingerprint,
  "errors":errors,"warnings":warnings,"scenes":measured,"media":p,
  "human_artistic_approval":False,
  "note":"This mechanical check cannot confirm face identity, creative quality or territorial rights."}

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--mode",choices=["reference","candidate"],required=True)
 ap.add_argument("--video",required=True)
 ap.add_argument("--reference")
 ap.add_argument("--manifest")
 ap.add_argument("--assets")
 ap.add_argument("--output",required=True)
 a=ap.parse_args()
 if a.mode=="reference":d=approved_reference(a.video)
 else:
  if not (a.reference and a.manifest and a.assets):
   ap.error("candidate mode requires reference, manifest and assets")
  r=approved_reference(a.reference)
  d=evaluate(a.video,json.loads(Path(a.manifest).read_text()),a.assets,r)
 o=Path(a.output);o.parent.mkdir(parents=True,exist_ok=True)
 o.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
 print(json.dumps({"v99_reference_verified":True,"status":d.get("status","REFERENCE_VERIFIED"),
  "errors":d.get("errors",[])},ensure_ascii=False),flush=True)
 return 0 if d.get("passed",True) else 2

if __name__=="__main__":raise SystemExit(main())
