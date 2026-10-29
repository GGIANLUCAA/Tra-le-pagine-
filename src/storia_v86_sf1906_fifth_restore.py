#!/usr/bin/env python3
"""V86 San Francisco 1906 fifth real archival image restoration.
No paid API: genuine Miles source at 43.00s cropped x=600 -> faithful
natural color source-guided AI photograph, only one distinct fifth shot.
Writes evidence and fail-closed image quality metadata BEFORE any Vidu POST.
"""
import importlib.util,hashlib,json,sys,os
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageEnhance,ImageFilter

OUT=Path("output/storia_v86_sf1906")
OUT.mkdir(parents=True,exist_ok=True)
SOURCE=Path("output/storia_v70_sf1906/SAN_FRANCISCO_1906_HD_ORIGINALE.webm")
SOURCE_HASH="c8b30802c0fbeb5f9ec3dc9af3e4f71ef627a863d4abba5550b63998cb46725a"
TIME=43.0
X=600
N=603
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
 return h.hexdigest()
def correlation(a,b):
 def small(x):
  g=cv2.cvtColor(x,cv2.COLOR_BGR2GRAY)
  return cv2.GaussianBlur(cv2.resize(g,(72,128)),(9,9),0).astype("float32").ravel()
 return float(np.corrcoef(small(a),small(b))[0,1])
def sat(b):
 return float(np.median(cv2.cvtColor(b,cv2.COLOR_BGR2HSV)[:,:,1]))
def read():
 if not SOURCE.is_file() or sha(SOURCE)!=SOURCE_HASH:raise RuntimeError("CANNOT_VERIFY_PRE1906_FILM")
 cap=cv2.VideoCapture(str(SOURCE))
 if int(cap.get(3))!=1440 or int(cap.get(4))!=1072:raise RuntimeError("HISTORICAL_FILM_GEOMETRY_MISMATCH")
 cap.set(cv2.CAP_PROP_POS_MSEC,TIME*1000)
 ok,frame=cap.read()
 cap.release()
 if not ok:raise RuntimeError("MISSING_FIFTH_HISTORICAL_FRAME")
 crop=frame[:,X:X+N].copy()
 if crop.shape[:2]!=(1072,N):raise RuntimeError("BAD_CROP")
 original=cv2.resize(crop,(720,1280))
 target=OUT/"SOURCE_BW_05.png"
 cv2.imwrite(str(target),original)
 return original
def colorize(original):
 spec=importlib.util.spec_from_file_location("ddcolor_v60",Path("src/storia_rivive_real_ai_v60.py"))
 dd=importlib.util.module_from_spec(spec);spec.loader.exec_module(dd)
 session,model_meta=dd.download_model()
 # Native 720x1280 source, preserve source L luminance (face/vehicle geometry);
 # infer chroma from historic shot without hallucinated modern objects.
 reduced=cv2.resize(original,(720,576))
 ab=dd.infer_ab(session,reduced)
 ab=cv2.resize(ab,(720,1280),interpolation=cv2.INTER_CUBIC)
 lum=dd.l_channel(original)
 lab=np.dstack([lum,np.clip(ab*1.12,-110,110)]).astype("float32")
 rgb=np.clip(cv2.cvtColor(lab,cv2.COLOR_LAB2RGB)*255,0,255).astype("uint8")
 image=ImageEnhance.Color(Image.fromarray(rgb)).enhance(1.03)
 image=image.filter(ImageFilter.UnsharpMask(radius=1.0,percent=90,threshold=4))
 first=OUT/"SOURCE_COLOR_DDCOLOR_05.jpg"
 image.save(first,quality=96,subsampling=0)
 return first,model_meta
def finegrain(reference,original):
 """One free candidate, zero paid retries; model failure creates conservative fallback."""
 from gradio_client import Client,handle_file
 client=Client("finegrain/finegrain-image-enhancer",verbose=False)
 prompt=("Photorealistic FULL COLOR restoration of this EXACT ORIGINAL April 14 1906 San Francisco "
 "Market Street film frame: real horse-drawn carriages, horses, early period automobiles and period-clothed "
 "pedestrians, all in the SAME locations, sizes, poses, costumes, rail tracks and building details as the "
 "input. Camera on a cable car looking forward; restore natural clear photographic light, subdued blue sky, "
 "vivid but believable brown horse leather and carriage canvas, period materials, lifelike soft human skin and "
 "fine wool clothing. No face swap, no invented people, no objects becoming people, no added or removed horses, "
 "wheels remain mechanical circles, true photorealistic fine-detail focus without fantasy scenes. "
 "ALL OBJECTS MUST STAY SOURCE-LOCKED and keep original camera perspective.")
 negative=("extra people, fake faces, extra carriage, added vehicles, altered body pose, missing hands, "
 "wheel becoming a head, horses morphing into humans, giant synthetic street cars, neon color, "
 "modern signs, smooth plastic skin, cartoon, painting, CGI, different city, camera pan, fake text")
 try:
  result=client.predict(handle_file(str(reference)),prompt,negative,
     19060414,2,1.18,.97,6,112,144,.47,18,"DDIM",api_name="/process")
  item=result[1] if isinstance(result,(tuple,list)) and len(result)>1 else result
  if isinstance(item,dict):item=item.get("path")
  if not item or not Path(str(item)).is_file():raise RuntimeError("FREE_IMAGE_MODEL_OUTPUT_MISSING")
  pic=cv2.imread(str(item))
  if pic is None:raise RuntimeError("FREE_MODEL_OUTPUT_INVALID")
  pic=cv2.resize(pic,(720,1280),interpolation=cv2.INTER_AREA)
  c=correlation(original,pic);s=sat(pic)
  if c<.82 or s<13 or s>165:raise RuntimeError(f"AI_DIFFERS_FROM_TRUE_HISTORICAL_FRAME ({c:.3f}, {s:.1f})")
  target=OUT/"FIFTH_VIDU_COLOR_ANCHOR_1906.jpg"
  cv2.imwrite(str(target),pic,[cv2.IMWRITE_JPEG_QUALITY,96])
  return target,"finegrain/free_image_to_image",c,s,None
 except Exception as exc:
  # Mandatory conservative fallback: NOT generative photoreal, flagged to require human review.
  # Better one real source-locked DDColor frame than fictional unsupervised scenery.
  pic=cv2.imread(str(reference))
  c=correlation(original,pic);s=sat(pic)
  if c<.82 or s<12:raise RuntimeError("FREE_MODEL_FAILED_AND_LOCAL_FALLBACK_TOO_WEAK") from exc
  target=OUT/"FIFTH_VIDU_COLOR_ANCHOR_1906.jpg"
  cv2.imwrite(str(target),pic,[cv2.IMWRITE_JPEG_QUALITY,96])
  return target,"DDColor faithful-local-fallback",c,s,{"type":type(exc).__name__,"msg":str(exc)[:400]}
def board(original,anchor):
 pict=Image.new("RGB",(1200,1100),(16,19,23))
 dr=ImageDraw.Draw(pict)
 titles=["FRAME ORIGINALE 1906","CANDIDATO COLORE VINCOLATO"]
 for idx,im in enumerate([cv2.cvtColor(original,cv2.COLOR_BGR2RGB),cv2.cvtColor(cv2.imread(str(anchor)),cv2.COLOR_BGR2RGB)]):
  view=Image.fromarray(im).resize((590,1049))
  pict.paste(view,(idx*600+4,42))
  dr.text((idx*600+12,12),titles[idx],fill=(255,255,244))
 pict.save(OUT/"SCENA_05_PRIMA_DOPO.jpg",quality=93)
def main():
 original=read()
 first,model=colorize(original)
 photo,method,c,s,failure=finegrain(first,original)
 board(original,photo)
 report={"scene":5,"subject":"horse carriages passing pedestrians on Market Street, San Francisco",
         "source":"https://www.loc.gov/item/00694408/","source_timestamp_seconds":TIME,
         "source_crop_x":X,"source_sha256":SOURCE_HASH,"source_frame_sha256":sha(OUT/"SOURCE_BW_05.png"),
         "restored_photo_sha256":sha(photo),"restoration_method":method,"geometry_corr":round(c,3),
         "median_saturation":round(s,1),"model_metadata":model,"free_model_failure":failure,
         "historical_facial_details_not_verified":True,"no_paid_video_calls":True,
         "photo_quality_gate_passed":c>=.82 and s>=12,"human_semantic_review":"PENDING",
         "rights_italy_final_review":"PENDING"}
 (OUT/"FIFTH_SCENE_RESTORATION_QA.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 print("V86_FIFTH_COLOR_ANCHOR_READY",method,round(c,3),round(s,1),sha(photo),flush=True)
if __name__=="__main__":main()
