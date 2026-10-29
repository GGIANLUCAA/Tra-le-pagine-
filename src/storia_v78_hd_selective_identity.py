#!/usr/bin/env python3
"""V78: restore V76 photographic detail, selectively protecting uncertain source objects.
Video -> exact same B/W source-frame freeze -> high-detail AI photo; no V77 global wash.
No paid AI calls. Identity protection is a curated region mask, NOT automated semantic proof.
"""
from pathlib import Path
import cv2
import numpy as np
import hashlib
import json
import shutil
import subprocess
import importlib.util
import zipfile

ROOT=Path(__file__).resolve().parents[1]
ORIG=Path("output/storia_v76_paris")
OUT=Path("output/storia_v78_paris")
OUT.mkdir(parents=True,exist_ok=True)
MOVIE=OUT/"LA_STORIA_RIVIVE_PARIGI_V78_HD_DETTAGLI_FEDeli.mp4"
KIT=OUT/"LA_STORIA_RIVIVE_V78_HD_COMPLETO.zip"
# Fixed-source manually chosen mechanical object areas for this demonstration.
# Coordinates are in the 720x1280 generated frame; never reuse these masks
# on a different shot. Faces and key human subjects are intentionally excluded.
PROTECTED={
 1:[dict(name="right-edge vehicle wheel/frame, uncertain",box=[612,650,720,1000],weight=.70),
    dict(name="right background vehicle hardware, uncertain",box=[532,660,626,883],weight=.58)],
 2:[dict(name="left rails",box=[0,730,128,1190],weight=.60),
    dict(name="right lower rails",box=[596,1020,720,1254],weight=.62)],
 3:[dict(name="small carriage wheel and cart",box=[29,952,185,1142],weight=.60)]
}
SUBJECT_ROIS={
 1:[315,490,595,850],
 2:[344,480,595,860],
 3:[220,225,548,755]
}

def file_sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for chunk in iter(lambda:f.read(1<<20),b""): h.update(chunk)
 return h.hexdigest()

def edge_detail(a):
 return float(cv2.Laplacian(cv2.cvtColor(a,cv2.COLOR_BGR2GRAY),cv2.CV_32F).var())

def validate_source_metadata():
 for n in ["PELICOLA_PARIGI_ORIGINALE.webm","PHOTO_QA.json"]:
  if not (ORIG/n).is_file():raise RuntimeError("MISSING_ALREADY_VERIFIED_SOURCE "+n)
 records=json.loads((ORIG/"PHOTO_QA.json").read_text(encoding="utf8"))
 for r in records["photos"]:
  i=int(r["i"])
  src=ORIG/f"ORIGINAL_{i:02}.png"
  pic=ORIG/f"FOTO_AI_{i:02}.png"
  if file_sha(src)!=r["source_sha"] or file_sha(pic)!=r["photo_sha"]:
   raise RuntimeError(f"IMAGES_NOT_SOURCE_LOCKED_{i}")
 return records

def reconstruct_with_local_masks(records):
 # Keep the original movie in one place. In GitHub Actions, the artifact
 # copied into ORIG is read-only in this pipeline.
 path=OUT/"PELICOLA_PARIGI_ORIGINALE.webm"
 if not path.exists():path.symlink_to((ORIG/"PELICOLA_PARIGI_ORIGINALE.webm").resolve())
 for s in ORIG.glob("ORIGINAL_*.png"):shutil.copy2(s,OUT/s.name)
 guard_spec=importlib.util.spec_from_file_location("v77_guard",ROOT/"src/storia_rivive_v77_identity_guard.py")
 v77=importlib.util.module_from_spec(guard_spec)
 guard_spec.loader.exec_module(v77)
 results=[]
 for i in (1,2,3):
  candidate_file=ORIG/f"FOTO_AI_{i:02}.png"
  candidate=cv2.imread(str(candidate_file))
  src=cv2.imread(str(ORIG/f"ORIGINAL_{i:02}.png"))
  if candidate is None or src is None:raise RuntimeError("MISSING_FRAME")
  hh,ww=candidate.shape[:2]
  if (hh,ww)!=(1280,720):raise RuntimeError("NOT_EXPECTED_PHOTOGRAPH_CROP")
  ref=cv2.resize(src,(ww,hh),interpolation=cv2.INTER_CUBIC)
  # Same full candidate, unchanged except restricted masks on actual object areas.
  genlab=cv2.cvtColor(candidate.astype(np.float32)/255,cv2.COLOR_BGR2LAB)
  srclab=cv2.cvtColor(ref.astype(np.float32)/255,cv2.COLOR_BGR2LAB)
  source_weight=np.zeros((hh,ww),np.float32)
  for roi in PROTECTED[i]:
   p=np.zeros((hh,ww),np.float32)
   x0,y0,x1,y1=roi["box"]
   p[y0:y1,x0:x1]=1
   p=cv2.GaussianBlur(p,(0,0),18)
   source_weight=np.maximum(source_weight,p*roi["weight"])
  mixed=genlab.copy()
  mixed[:,:,0]=genlab[:,:,0]*(1-source_weight)+srclab[:,:,0]*source_weight
  result=np.clip(cv2.cvtColor(mixed,cv2.COLOR_LAB2BGR)*255,0,255).astype(np.uint8)
  pic_path=OUT/f"FOTO_AI_{i:02}.png"
  cv2.imwrite(str(pic_path),result,[cv2.IMWRITE_PNG_COMPRESSION,2])
  r=next(x for x in records["photos"] if int(x["i"])==i)
  r["photo_sha"]=file_sha(pic_path)
  r["source_protection"]="V78 selected mechanical regions; photographic candidate preserved elsewhere"
  x0,y0,x1,y1=SUBJECT_ROIS[i]
  roi_original=candidate[y0:y1,x0:x1]
  roi_result=result[y0:y1,x0:x1]
  old_tex=edge_detail(roi_original);new_tex=edge_detail(roi_result)
  if new_tex<.9*old_tex:raise RuntimeError(f"HD_SUBJECT_DETAIL_REGRESSION_{i}")
  summary, _=v77.inspect(src,result)
  results.append({
   "scene_id":i,
   "candidate_hd_sha":file_sha(candidate_file),
   "v78_photo_sha":file_sha(pic_path),
   "candidate_subject_texture_laplacian":round(old_tex,2),
   "v78_subject_texture_laplacian":round(new_tex,2),
   "fraction_pixels_repaired_over_20pct":round(float((source_weight>.20).mean()),3),
   "source_locked_regions":PROTECTED[i],
   "v77_structural_guard_report":summary,
   "semantic_identity_human_review":"PENDING",
   "notice":"Laplacian and tile warnings are diagnostic, NOT proof of identities."
  })
  print("V78_KEEP_PHOTO_HD",i,old_tex,new_tex,flush=True)
 (OUT/"PHOTO_QA.json").write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding="utf8")
 (OUT/"V78_REGION_QA.json").write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding="utf8")
 # Three-row photo comparisons for art review
 from PIL import Image,ImageDraw
 board=Image.new("RGB",(920,1760),(22,24,29));draw=ImageDraw.Draw(board)
 labels=["FOTOGRAMMA B/N","V76 ALTA DEFINIZIONE","V78 HD + OGGETTI"]
 for idx,i in enumerate((1,2,3)):
  for col,pic in enumerate((ORIG/f"ORIGINAL_{i:02}.png",ORIG/f"FOTO_AI_{i:02}.png",OUT/f"FOTO_AI_{i:02}.png")):
   frame=Image.open(pic).convert("RGB").resize((295,530))
   board.paste(frame,(5+col*305,30+idx*580))
   draw.text((7+col*305,8+idx*580),labels[col],fill="white")
 board.save(OUT/"PRIMA_V76_DOPO_V78.jpg",quality=92)
 return results

def render_existing_reference_effect():
 spec=importlib.util.spec_from_file_location("v76",ROOT/"src/storia_v76_paris_social_museum.py")
 v76=importlib.util.module_from_spec(spec);spec.loader.exec_module(v76)
 v76.OUT=OUT
 v76.SOURCE=OUT/"PELICOLA_PARIGI_ORIGINALE.webm"
 v76.VIDEO=OUT/"LA_STORIA_RIVIVE_SOCIAL_MUSEUM_V76.mp4"
 v76.make()
 old=OUT/"LA_STORIA_RIVIVE_SOCIAL_MUSEUM_V76.mp4"
 if not old.is_file():raise RuntimeError("RENDER_MISSING")
 shutil.move(str(old),str(MOVIE))
 # Actual metadata and ZIP must reflect V78 and real artifact SHA/flags.
 qa_file=OUT/"FONTI_E_QA.json"
 qa=json.loads(qa_file.read_text(encoding="utf8"))
 qa.update({
  "version":"V78",
  "video":MOVIE.name,
  "video_sha256":file_sha(MOVIE),
  "reconstruction_method":"V76 HD candidate kept intact except local V78 manually chosen structure patches",
  "real_HD_recovery":True,
  "semantic_identity_human_review":"PENDING",
  "V77_global_78percent_original_blend":"REJECTED_AS_BLURRY",
  "human_artistic_review":"PENDING",
  "published_to_social":False,
  "published_to_private_site":False
 })
 qa_file.write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding="utf8")
 names=[MOVIE,"COPERTINA.jpg","PRIMA_V76_DOPO_V78.jpg","V78_REGION_QA.json","FONTI_E_QA.json","POST_FACEBOOK.txt","POST_INSTAGRAM.txt","POST_TIKTOK.txt","POST_YOUTUBE.txt"]
 with zipfile.ZipFile(KIT,"w",compression=zipfile.ZIP_DEFLATED) as z:
  for item in names:
   p=OUT/item if isinstance(item,str) else item
   if p.is_file():z.write(p,p.name)
 with zipfile.ZipFile(KIT) as z:
  if z.testzip() is not None:raise RuntimeError("CORRUPT_ZIP")
 check=subprocess.run(["ffmpeg","-v","error","-xerror","-i",str(MOVIE),"-f","null","-"],capture_output=True,text=True)
 if check.returncode:raise RuntimeError("UNDECODABLE_MP4 "+check.stderr[-500:])
 print("V78_COMPLETED_HIGH_DETAIL",MOVIE,str(MOVIE.stat().st_size),"zip",KIT,flush=True)
if __name__=="__main__":
 records=validate_source_metadata()
 reconstruct_with_local_masks(records)
 render_existing_reference_effect()
