#!/usr/bin/env python3
"""Complete only two missing real I2I images for Bombay V98 on a fresh runner.
Reuse and SHA-verify existing three successful real I2I outputs. Never ask Vidu
or rerun previously successful free image jobs. Fail closed.
"""
import os,json,cv2,numpy as np,hashlib
from pathlib import Path
from gradio_client import Client,handle_file
from PIL import Image,ImageDraw
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import storia_v98_bombay_five_photos as p
R=Path("output/storia_bombay_v98")
def main():
 qa=json.loads((R/"V95_FREE_SOURCE_QA.json").read_text())
 byscene={r["scene"]:r for r in qa["selected_scenes"]}
 prev=json.loads((R/"V98_FREE_I2I_QA.json").read_text())
 accepted={r["scene"]:r for r in prev["scene_photos"] if r.get("status","").startswith("I2I_GENERATED")}
 for k in [2,4,5]:
  r=accepted.get(k);f=R/f"RESTORATION_FINAL_{k:02d}.jpg"
  if not r or not f.is_file() or p.sha(f)!=r["new_i2i_photo_sha256"]:
   raise RuntimeError("PREVIOUS_REAL_I2I_PHOTO_NOT_FOUND "+str(k))
 token=os.getenv("HF_TOKEN","").strip()
 if token:
  try:client=Client("finegrain/finegrain-image-enhancer",hf_token=token,verbose=False)
  except TypeError:client=Client("finegrain/finegrain-image-enhancer",token=token,verbose=False)
 else:client=Client("finegrain/finegrain-image-enhancer",verbose=False)
 records=[accepted[k] for k in [2,4,5]]
 for k in [7,8]:
  src=R/f"SOURCE_BW_{k:02d}.png";old=R/f"RESTORED_PHOTO_{k:02d}.jpg"
  row=byscene[k]
  if not src.is_file() or not old.is_file() or p.sha(src)!=row["original_BW_frame_sha256"] or p.sha(old)!=row["existing_AI_color_photo_sha256"]:
   raise RuntimeError("SOURCE_RESTORATION_SUBJECT_MISMATCH_"+str(k))
  orig=cv2.imread(str(src));ref=cv2.imread(str(old))
  try:
   result=client.predict(handle_file(str(old)),p.SCENES[k],p.NEG,
       1929+k,2,1.14,.97,6,112,144,.45,18,"DDIM",api_name="/process")
   file=result[1] if isinstance(result,(list,tuple)) and len(result)>1 else result
   if isinstance(file,dict):file=file.get("path")
   out=cv2.imread(str(file)) if file else None
   if out is None:raise RuntimeError("I2I_UNREADABLE_OUTPUT")
   out=cv2.resize(out,(720,1280))
   c=p.corr(orig,out);s=p.sat(out);sh=p.sharp(out)
   if c<.93 or s<18 or s>175:raise RuntimeError(f"NOT_SOURCE_LOCKED c={c:.3f} sat={s:.1f}")
   dest=R/f"RESTORATION_FINAL_{k:02d}.jpg"
   cv2.imwrite(str(dest),out,[cv2.IMWRITE_JPEG_QUALITY,96])
   records.append({"scene":k,"status":"I2I_GENERATED_TECHNICALLY_SOURCE_LOCKED_REQUIRES_ARTISTIC_QA",
                   "original_sha256":p.sha(src),"new_i2i_photo_sha256":p.sha(dest),
                   "method":"real_image_to_image_photographic_restoration",
                   "auto_frame_correlation_pass":True,"source_to_output_corr":round(c,4),
                   "sharp_i2i":round(sh,2),"saturation":round(s,2),
                   "human_facial_fidelity":"PENDING","human_scene_identity":"PENDING"})
   print("V98_REMAINING_I2I_SUCCESS",k,round(c,4),round(sh,1),p.sha(dest),flush=True)
  except Exception as e:
   print("V98_REMAINING_I2I_FAILED",k,type(e).__name__,str(e)[:290],flush=True)
   raise
 manifest={"version":"V98_FIVE_REAL_I2I_COMPLETE_PRE_VIDU","photographic_images":records,
           "all_five_generated_image_to_image":True,"all_have_exact_source_hash":True,
           "artistic_human_review":"PENDING","source_rights_italy":"PENDING",
           "no_vidu_credits_spent":True}
 (R/"V98_FIVE_REAL_PHOTOS_QA.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
 pic=Image.new("RGB",(5*234,3*437),(14,18,23));d=ImageDraw.Draw(pic)
 for i,k in enumerate([2,4,5,7,8]):
  for j,f in enumerate([R/f"SOURCE_BW_{k:02d}.png",R/f"RESTORED_PHOTO_{k:02d}.jpg",R/f"RESTORATION_FINAL_{k:02d}.jpg"]):
   im=Image.open(f).convert("RGB").resize((230,409))
   pic.paste(im,(i*234+2,j*437+24))
   d.text((i*234+5,j*437+5),f"#{k} "+["SOURCE B/W","OLD DDCOLOR","NEW REAL I2I"][j],fill="white")
 pic.save(R/"V98_FIVE_SCENES_REAL_I2I_COMPARE.jpg",quality=91)
 print("V98_ALL_FIVE_SOURCE_LOCKED_REAL_I2I_AVAILABLE_ZERO_VIDU_CREDITS",flush=True)
if __name__=="__main__":main()
