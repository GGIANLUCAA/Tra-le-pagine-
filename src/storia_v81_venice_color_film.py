#!/usr/bin/env python3
"""VENICE 1896 V81: authentic film, conservatively AI-colorized restored photo freezes.
No invented face generation. This is AI color restoration, NOT generative face reconstruction.
"""
import sys,json,hashlib,importlib.util
from pathlib import Path
import cv2
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location("v80film",ROOT/"src/storia_v80_new_york_venice.py")
v80=importlib.util.module_from_spec(sp);sp.loader.exec_module(v80)

def restore_palace_photo(source,dd,session):
 bgr=cv2.imread(str(source))
 base=v80.natural_color(dd,session,source)
 lab=cv2.cvtColor(base.astype(np.float32)/255,cv2.COLOR_BGR2LAB)
 L=lab[:,:,0]
 hh,ww=L.shape
 # Preserve source structure; AI DDColor predicts color, controlled grading.
 # Improved Venice architecture photographed in luminous warm morning light.
 # Moderate increase of sky-blue and palace stone warmth to avoid sepia monotony.
 ys,xs=np.ogrid[:hh,:ww]
 sky=np.clip((460-ys)/240,0,1).astype(np.float32)
 water=np.clip((ys-935)/260,0,1).astype(np.float32)
 # Simple semantic priors by spatial position only; deliberately not repainting objects.
 # High source luminance maintains original facial/architectural contours.
 chroma=np.maximum(0,1-np.abs(L-61)/95)
 lab[:,:,1]=np.clip(lab[:,:,1]*1.2+2.0*(1-sky)-2.0*sky-4.0*water,-110,110)
 lab[:,:,2]=np.clip(lab[:,:,2]*1.2+3.5*(1-sky)-2.8*sky-6.5*water,-110,110)
 rgb=cv2.cvtColor(lab.astype(np.float32),cv2.COLOR_LAB2BGR)
 col=np.uint8(np.clip(rgb*255,0,255))
 # Modern photographic contrast while preserving authentic source luminance.
 tone=cv2.cvtColor(col,cv2.COLOR_BGR2LAB)
 cl=cv2.createCLAHE(clipLimit=1.55,tileGridSize=(12,12))
 gray=tone[:,:,0];tone[:,:,0]=cv2.addWeighted(gray,.88,cl.apply(gray),.12,0)
 col=cv2.cvtColor(tone,cv2.COLOR_LAB2BGR)
 blur=cv2.GaussianBlur(col,(0,0),.85)
 col=cv2.addWeighted(col,1.38,blur,-.38,0)
 return col

def main():
 meta=v80.FILMS["VENICE_1896"]
 path=v80.OUT/"VENICE_1896";path.mkdir(parents=True,exist_ok=True)
 source,provenance=v80.acquire(meta,path)
 records=v80.grab_stills(source,meta,path)
 dd,sess,m=v80.load_dd()
 photo_records=[]
 for r in records:
  i=int(r["scene"])
  src=path/r["source_frame"]
  out=restore_palace_photo(src,dd,sess)
  target=path/f"PHOTO_AI_{i:02d}.png"
  cv2.imwrite(str(target),out,[cv2.IMWRITE_PNG_COMPRESSION,2])
  original=cv2.imread(str(src))
  corr=v80.similarity(original,out)
  sat=float(cv2.cvtColor(out,cv2.COLOR_BGR2HSV)[:,:,1].mean())
  if corr<.88 or sat<10:raise RuntimeError(f"VENICE_PHOTO_TOO_DIFFERENT_OR_MONO_{i}:{corr:.3f}/{sat:.1f}")
  photo_records.append({**r,
    "photo_file":target.name,"photo_sha256":v80.sha(target),
    "geom_corr":round(corr,4),"sat":round(sat,2),
    "model":"DDColor neural ONNX chroma + gentle local contrast + source preserved",
    "new_detail_generation":False,"interpretative_color":True,
    "source_locked_semantic_review":"PENDING_HUMAN"
  })
  print("VENICE_CINEMATIC_PHOTO_RECONSTRUCTION",i,round(corr,3),round(sat,1),flush=True)
 (path/"PHOTO_QA.json").write_text(json.dumps(photo_records,indent=2,ensure_ascii=False))
 v80.render(meta,source,photo_records,path,provenance)
 qa_path=path/"QA.json"
 qa=json.loads(qa_path.read_text())
 qa.update({"version":"V81","photo_restoration_method":"source-locked DDColor ONNX AI recolor and conservative sharpness; no generative objects or faces","limitation":"NOT a photorealistic face re-generation / no new face details","safe_video_preview":True,"human_review":"PENDING"})
 qa_path.write_text(json.dumps(qa,indent=2,ensure_ascii=False))
 # Refresh ZIP with corrected exact content and English social posts.
 for social in path.glob("POST_*.txt"):
  txt=social.read_text()
  txt=txt.replace("Faces and colors restored with AI are interpretations","Colors restored with AI are interpretations; no face identities were invented")
  txt=txt.replace("AI reconstructed photographic stills","AI-colored, carefully enhanced photographic stills")
  social.write_text(txt)
 zipfile_path=path/"LA_STORIA_RIVIVE_VENICE_1896_KIT.zip"
 import zipfile
 with zipfile.ZipFile(zipfile_path,"w",compression=zipfile.ZIP_DEFLATED) as z:
  for file in [path/"LA_STORIA_RIVIVE_VENICE_1896_V80.mp4",path/"COVER.jpg",path/"BEFORE_AFTER_ACTUAL_GENERATED.jpg",
   path/"QA.json",path/"SOURCE_QA.json",path/"PHOTO_QA.json",*path.glob("POST_*.txt")]:
   z.write(file,file.name)
 with zipfile.ZipFile(zipfile_path) as z:
  if z.testzip():raise RuntimeError("BROKEN_ZIP")
 print("VENICE_V81_COMPLETE",path,flush=True)
if __name__=="__main__":main()
