#!/usr/bin/env python3
"""China 1920s V105: image reconstruction with genuine open-source neural models.

Uses exact real 1920s footage original frames (SHA locked) and neural DDColor +
Real-ESRGAN 4x. Optionally fuses pre-existing Finegrain actual I2I photographic
enhancement luminance with predicted historic color for scenes 1-3. NEVER invents
people in source or claims 4K original raster / verified facial identity.
NO Vidu, NO paid provider, NO model upload.
"""
from __future__ import annotations
import hashlib, importlib.util, json, math, time
from pathlib import Path
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path("output/storia_china_v105")
ROOT.mkdir(parents=True,exist_ok=True)
REFERENCE_SHA="fbdf513bd01171c51c431d79510f93a92b44ccdf44bdfdf03d28f6357c1d43d5"

def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for x in iter(lambda:f.read(1<<20),b""):h.update(x)
 return h.hexdigest()

def load_module(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 return m

def resize_wide(im,w=720,h=1280):
 return cv2.resize(im,(w,h),interpolation=cv2.INTER_AREA if im.shape[1]>=w and im.shape[0]>=h else cv2.INTER_CUBIC)

def geometry(a,b):
 def small(v):
  gray=cv2.cvtColor(cv2.resize(v,(72,128)),cv2.COLOR_BGR2GRAY)
  return cv2.GaussianBlur(gray,(9,9),0).astype(np.float32).ravel()
 u=small(a);v=small(b)
 if u.std()<.1 or v.std()<.1:return 0
 return float(np.corrcoef(u,v)[0,1])

def color_with_ddcolor(source,model,dd):
 # NN semantic colorization is not the final photograph. Neural I2I restoration follows.
 base=cv2.resize(source,(720,576),interpolation=cv2.INTER_AREA)
 ab=dd.infer_ab(model,base)
 # Maintain actual source grayscale geometry, only infer chromatic channels.
 L=dd.l_channel(source)
 ab=cv2.resize(ab,(source.shape[1],source.shape[0]),interpolation=cv2.INTER_LINEAR)
 lab=np.dstack((L,np.clip(ab*1.24,-110,110))).astype(np.float32)
 rgb=cv2.cvtColor(lab,cv2.COLOR_LAB2RGB)
 color=cv2.cvtColor(np.clip(rgb*255,0,255).astype(np.uint8),cv2.COLOR_RGB2BGR)
 return color

def enhance(esrgan,base,restorer):
 # Known preverified 4x ONNX model, tile at 64 input with surrounding context.
 small=cv2.resize(base,(240,427),interpolation=cv2.INTER_AREA)
 out=restorer.esrgan_4x(esrgan,small)
 if out.shape[:2]!=(1708,960):raise RuntimeError("ESRGAN_WRONG_SHAPE")
 return cv2.resize(out,(720,1280),interpolation=cv2.INTER_AREA)

def merge_finegrain_luma(photo,photographic_neural):
 # Genuine pre-generated Finegrain output carries high-frequency reconstructed details.
 # Transfer only luminance, while the actual DDColor model supplies faithful chroma.
 # Blend conservatively to reduce hallucinated texture.
 p=cv2.cvtColor(photo,cv2.COLOR_BGR2LAB).astype(np.float32)
 q=cv2.cvtColor(resize_wide(photographic_neural),cv2.COLOR_BGR2LAB).astype(np.float32)
 p[:,:,0]=np.clip(.60*q[:,:,0]+.40*p[:,:,0],0,255)
 return cv2.cvtColor(p.astype(np.uint8),cv2.COLOR_LAB2BGR)

def contact_table(rows):
 c=Image.new("RGB",(5*225,3*414),(14,18,22));d=ImageDraw.Draw(c)
 for idx,(source,base,photo,status) in enumerate(rows):
  for j,im in enumerate([source,base,photo]):
   x=idx*225+2;y=j*414+28
   c.paste(Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB)).resize((221,380)),(x,y))
   d.text((x,y-20),f"SCENE {idx+1} "+["SOURCE B/W","AI SEMANTIC COLOR","NEURAL RESTORED"][j],fill=(241,233,214))
  d.text((idx*225+5,3),status,fill=(220,205,180))
 p=ROOT/"V105_TRUE_SOURCE_COLOR_NEURAL_PHOTO_COMPARE.jpg";c.save(p,quality=92)
 return p

def main():
 source_dir=ROOT/"sources"
 manifest=json.loads((source_dir/"SOURCE_MANIFEST.json").read_text())
 if manifest.get("original_film_sha256")!=REFERENCE_SHA:
  raise RuntimeError("WRONG_ORIGINAL_1920S_SOURCE_NO_PROCESSING")
 assert len(manifest["scenes"])==5
 dd=load_module("v60_ddcolor","src/storia_rivive_real_ai_v60.py")
 photo_restore=load_module("v62_esrgan","src/storia_rivive_real_photo_ai_v62.py")
 model,ddmeta=dd.download_model()
 sr, srmeta=photo_restore.setup_upscaler()
 out={"version":"V105_REAL_NEURAL_SOURCE_RESTORATION","original_source_sha256":REFERENCE_SHA,
   "models":{"semantic_color":ddmeta,"photo_reconstruction":srmeta},
   "new_paid_api_requests":0,"vidu_requests":0,"rendered_master":False,
   "rights_italy":"PENDING","artistic_approval":False,
   "source_original_native_4k":False,"scenes":[]}
 review=[]
 for scene in manifest["scenes"]:
  n=scene["scene"];key=source_dir/scene["source_exact_frame_file"]
  if sha(key)!=scene["source_exact_frame_sha256"]:raise RuntimeError("ORIGINAL_FRAME_SHA_MISMATCH_"+str(n))
  raw=cv2.imread(str(key))
  if raw is None or raw.shape[:2]!=(1280,720):raise RuntimeError("MISSING_VERTICAL_SOURCE_FRAME")
  started=time.monotonic()
  initial=color_with_ddcolor(raw,model,dd)
  base_path=ROOT/f"PHOTO_{n:02d}_AI_COLOR_BASE_NOT_FINAL.jpg"
  cv2.imwrite(str(base_path),initial,[cv2.IMWRITE_JPEG_QUALITY,96])
  neural=enhance(sr,initial,photo_restore)
  finegrain=source_dir/f"SCENE_{n:02d}_I2I_CANDIDATE.jpg"
  used_finegrain=False
  if finegrain.is_file() and n<=3:
   extra=cv2.imread(str(finegrain))
   if extra is not None and geometry(raw,extra)>.90:
    neural=merge_finegrain_luma(neural,extra)
    used_finegrain=True
  # Natural documentary grading: guard overcooked orange and compensate over-muted AI.
  hsv=cv2.cvtColor(neural,cv2.COLOR_BGR2HSV)
  sat=float(np.mean(hsv[:,:,1]))
  if sat<11:
   # Model provides color but too weak: do not fake strong bright colors with arbitrary palette.
   print("WARN_LOW_MODEL_COLOR_SAT",n,sat,flush=True)
  chroma_gain=1.11 if sat>12 else 1.18
  hsv[:,:,1]=np.clip(hsv[:,:,1].astype(np.float32)*chroma_gain,0,205).astype("uint8")
  neural=cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
  corr=geometry(raw,neural)
  sat=float(np.mean(cv2.cvtColor(neural,cv2.COLOR_BGR2HSV)[:,:,1]))
  passed=corr>=.82 and sat>=9
  path=ROOT/f"PHOTO_{n:02d}_REAL_AI_RESTORED.jpg"
  cv2.imwrite(str(path),neural,[cv2.IMWRITE_JPEG_QUALITY,97])
  row={"scene":n,"original_frame_sha256":sha(key),"color_model":"DDColor tiny FP16",
    "neural_i2i_model":"RealESRGAN x4 ONNX",
    "existing_finegrain_i2i_photo_fusion":used_finegrain,
    "color_base_sha256":sha(base_path),"actual_photo_sha256":sha(path),
    "actual_photo_filename":path.name,"source_similarity":round(corr,4),
    "mean_saturation":round(sat,2),"technical_identity_gate_pass":passed,
    "human_identity_approved":False,
    "original_subject_time_s":scene["source_time_s"],
    "runtime_s":round(time.monotonic()-started,2)}
  out["scenes"].append(row)
  (ROOT/"PHOTO_QA_V105.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
  review.append((raw,initial,neural,"TECH QA" if passed else "REJECT"))
  print("NEURAL_AI_PHOTO",n,row["technical_identity_gate_pass"],
    "corr",row["source_similarity"],"sat",row["mean_saturation"],
    "Finegrain",used_finegrain,"time",row["runtime_s"],flush=True)
 contact_table(review)
 out["technical_photos_passed"]=sum(bool(s["technical_identity_gate_pass"]) for s in out["scenes"])
 out["status"]="FIVE_RESTORED_AI_PHOTOS_FOR_ARTISTIC_QA" if out["technical_photos_passed"]==5 else "PHOTOS_NEED_SELECTIVE_REVIEW_OR_REJECTION"
 (ROOT/"PHOTO_QA_V105.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
 print("V105_RECONSTRUCTION_STATUS",out["status"],out["technical_photos_passed"],flush=True)
if __name__=="__main__":main()
