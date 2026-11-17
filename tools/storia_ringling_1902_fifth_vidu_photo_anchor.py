#!/usr/bin/env python3
"""Ringling 1902 scene 5, verified original 212s frame -> one FREE genuine
photographic source-locked Finegrain image-to-image anchor for Vidu only.
Zero video API calls; does not self-authorize paid video.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,inspect
import cv2,numpy as np
from PIL import Image,ImageDraw
OUT=Path("output/storia_ringling_1902_v1")
ROOT=Path(__file__).resolve().parents[1]
SRC=OUT/"FRAME_05_SOURCE.png"
ANCHOR=OUT/"RINGLING_1902_SCENE05_VIDU_ANCHOR.jpg"
SHA_SOURCE_EXPECTED=None
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for x in iter(lambda:f.read(1<<20),b""):h.update(x)
 return h.hexdigest()
def corr(x,y):
 def reduction(v):
  z=cv2.cvtColor(cv2.resize(v,(120,216)),cv2.COLOR_BGR2GRAY)
  return cv2.GaussianBlur(z,(7,7),0).astype("float32").flatten()
 a,b=reduction(x),reduction(y)
 return float(np.corrcoef(a,b)[0,1])
def main():
 q=json.loads((OUT/"PHOTO_QA.json").read_text())
 if len(q)!=4 or [x["scene"] for x in q]!=[1,2,3,4]:raise RuntimeError("FOUR_REAL_FINEGRAIN_I2I_SHOTS_NOT_YET_VERIFIED")
 for x in q:
  if x.get("model")!="DDColor+free Finegrain image enhancer":raise RuntimeError("DDCOLOR_ONLY_NOT_ACCEPTED")
  if sha(OUT/x["photo_file"])!=x["photo_sha256"]:raise RuntimeError("PREVIOUS_GOOD_PHOTO_MISSING")
 source=cv2.imread(str(SRC))
 if source is None or source.shape[:2]!=(1280,720):raise RuntimeError("FIFTH_ORIGINAL_SOURCE_NOT_VERIFIED")
 # Generate one free image-to-image from source-locked neutral neural base.
 spec=importlib.util.spec_from_file_location("v80_photo",ROOT/"src/storia_v80_new_york_venice.py")
 v80=importlib.util.module_from_spec(spec);spec.loader.exec_module(v80)
 d,session,_=v80.load_dd()
 cond=v80.natural_color(d,session,SRC)
 conditioning=OUT/"RINGLING_1902_SCENE05_NEURAL_COLOR_CONDITIONING.jpg"
 cv2.imwrite(str(conditioning),cv2.resize(cond,(576,1024)),[cv2.IMWRITE_JPEG_QUALITY,96])
 from gradio_client import Client,handle_file
 kw={"verbose":False}
 parms=inspect.signature(Client).parameters
 token=os.environ.get("HF_TOKEN","")
 if token:
  if "hf_token" in parms:kw["hf_token"]=token
  elif "token" in parms:kw["token"]=token
 client=Client("finegrain/finegrain-image-enhancer",**kw)
 prompt=("Extremely realistic source-faithful color documentary photograph restoring the EXACT original 1902 "
  "Ringling Brothers circus parade movie frame: one real mounted uniformed circus horse rider with original "
  "ornamental embroidered jacket, formal headgear, reins and black horse in the foreground; the second original "
  "horse and crowd and period masonry buildings remain exactly where shown. All original horse heads and bodies "
  "are fully anatomical and SAME shapes and numbers as source; muzzle/ears/tack, eyes, rider hands and expression "
  "must preserve actual 1902 cinema source geometry. Visually believable skin, fabric and black horse coat with "
  "natural noon daylight, muted photographic colors, subtle historical coloring not cartoon. The same street sign "
  "exists in precisely the same place; do not invent its text or replace architecture. "
  "DO NOT add or remove any people or animals, eyes, legs or hats, no objects become people.")
 neg=("extra animals, extra horse heads, horses turning into humans, morphing faces, missing horse legs, "
   "second rider on same horse, duplicate faces, fake signs, fabricated text, neon orange, plastic people, "
   "shiny fake coats, paintings, illustration, cartoon, modern cars, change of camera angle, extra hands")
 raw=client.predict(handle_file(str(conditioning)),prompt,neg,1902,2,1.08,.96,6,112,144,.38,18,"DDIM",api_name="/process")
 item=raw[1] if isinstance(raw,(list,tuple)) and len(raw)>1 else raw
 if isinstance(item,dict):item=item.get("path")
 if not item or not Path(str(item)).is_file():raise RuntimeError("FREE_IMAGE_TO_IMAGE_PROVIDER_GAVE_NO_REAL_IMAGE")
 pic=cv2.imread(str(item))
 if pic is None:raise RuntimeError("FREE_PROVIDER_IMAGE_NOT_DECODABLE")
 pic=cv2.resize(pic,(720,1280),interpolation=cv2.INTER_CUBIC)
 geom=corr(source,pic)
 hsv=cv2.cvtColor(pic,cv2.COLOR_BGR2HSV);mean=float(hsv[:,:,1].mean())
 if mean>115:
  hsv[:,:,1]=np.uint8(np.clip(hsv[:,:,1].astype("float32")*(115/mean),0,225))
  pic=cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
 sat=float(cv2.cvtColor(pic,cv2.COLOR_BGR2HSV)[:,:,1].mean())
 if geom<.85 or not 13<sat<136:
  raise RuntimeError("FIFTH_TRUE_I2I_PHOTO_TOO_DIFFERENT_OR_NEON_COLOR_"+str((round(geom,3),round(sat,2))))
 cv2.imwrite(str(ANCHOR),pic,[cv2.IMWRITE_JPEG_QUALITY,96])
 compare=Image.new("RGB",(2*430,770),(16,20,26));d=ImageDraw.Draw(compare)
 for j,(picture,label) in enumerate([(source,"AUTHENTIC 1902 FRAME"),(pic,"REAL FINEGRAIN I2I COLOR")]):
  picture=Image.fromarray(cv2.cvtColor(picture,cv2.COLOR_BGR2RGB)).resize((424,752))
  compare.paste(picture,(j*430+3,18));d.text((j*430+6,3),label,fill=(253,241,216))
 compare.save(OUT/"RINGLING_1902_FIFTH_TRUE_SOURCE_VS_VIDU_START.jpg",quality=93)
 report={"status":"FIFTH_REAL_FINEGRAIN_COLOR_ANCHOR_FREE_NO_VIDEO_POST",
  "source":"Ringling Brothers Parade 1902 original 212s historical actual B/W frame",
  "source_page":"https://commons.wikimedia.org/wiki/File:Ringling_Brothers_Parade_Film_(1902).webm",
  "scene_5_exact_frame_file":SRC.name,"source_frame_sha256":sha(SRC),
  "fifth_actual_photographic_image_to_image":True,
  "photo_file":ANCHOR.name,"photo_sha256":sha(ANCHOR),
  "geometry_corr":round(geom,4),"saturation_mean":round(sat,2),
  "semantic_artistic_human_review":"PENDING",
  "vidu_paid_post_count":0,"vidu_task":None,
  "italy_source_rights":"PENDING_VERIFICATION","video_final":False,
  "next":"Do not spend before single-clip budget and semantic review; generate only one Vidu clip from EXACT anchor and source film shot"}
 (OUT/"FIFTH_VIDU_ANCHOR_PRESPEND_QA.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("RINGLING_1902_FREE_FIFTH_I2I_ANCHOR_READY",sha(ANCHOR),"corr",round(geom,3),"sat",round(sat,2),flush=True)
if __name__=="__main__":main()
