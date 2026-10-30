#!/usr/bin/env python3
"""V95 Bombay January 1929: free face-specific photographic restoration preflight.
Using the exact source-locked restored frame of three men looking toward camera;
one free image-to-image call, not a paid Vidu video call.
Fail closed on broken source/geometry; mark semantic QA separately.
"""
from pathlib import Path
import hashlib,json,cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageEnhance
ROOT=Path("output/storia_bombay_1929_v95")
ROOT.mkdir(parents=True,exist_ok=True)
PHOTO=ROOT/"RESTORED_PHOTO_08.jpg"
BW=ROOT/"SOURCE_BW_08.png"
TARGET=ROOT/"V95_VIDU_BOMBAY_MEN_COLOR_ANCHOR.jpg"
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for part in iter(lambda:f.read(1<<20),b""):h.update(part)
 return h.hexdigest()
def correlation(a,b):
 def feat(x):
  gr=cv2.cvtColor(cv2.resize(x,(72,128)),cv2.COLOR_BGR2GRAY)
  return cv2.GaussianBlur(gr,(9,9),0).astype("float32").ravel()
 return float(np.corrcoef(feat(a),feat(b))[0,1])
def restore():
 q=json.loads((ROOT/"V95_FREE_SOURCE_QA.json").read_text())
 rec=[x for x in q["selected_scenes"] if x["scene"]==8][0]
 if sha(PHOTO)!=rec["existing_AI_color_photo_sha256"] or sha(BW)!=rec["original_BW_frame_sha256"]:
  raise RuntimeError("PREVIOUSLY_VERIFIED_SHOT_SHA_MISMATCH")
 base=cv2.imread(str(PHOTO))
 original=cv2.imread(str(BW))
 if base.shape[:2]!=(1280,720):raise RuntimeError("SHOT_DIMENSIONS_WRONG")
 prompt=("Faithful natural-color PHOTOGRAPHIC RESTORATION of this exact 1929 Bombay film frame. "
 "Three real adult men talking and smiling toward the camera; preserve each actual existing face, "
 "skin age, eye direction, moustaches, dark wavy hair, caps, collar, clothes, hands, bodies, "
 "the background crowd and the exact source camera perspective. "
 "Rich but believable 1929 color photography with detailed human skin texture and individual "
 "hair strands, physically plausible daylight, realistic sharp eyes, no modern clothing. "
 "SOURCE LOCKED: do not invent or replace any faces or hands, same number of men and positions, "
 "no beauty retouching, no plastic skin, no CGI, no added or missing people.")
 negative=("face swap, invented faces, new people, missing men, duplicate hands, extra fingers, "
 "eye deformation, airbrushed skin, cartoon, illustration, modern city, changed camera angle, "
 "changed garments, incorrect hat, unreal color, artificial lips, hallucinated objects")
 candidates=[]
 try:
  from gradio_client import Client,handle_file
  client=Client("finegrain/finegrain-image-enhancer",verbose=False)
  response=client.predict(handle_file(str(PHOTO)),prompt,negative,
     1929,2,1.18,.97,6,112,144,.47,18,"DDIM",api_name="/process")
  output=response[1] if isinstance(response,(list,tuple)) and len(response)>1 else response
  if isinstance(output,dict):output=output.get("path")
  if not output or not Path(str(output)).is_file():raise RuntimeError("FREE_I2I_EMPTY")
  gen=cv2.imread(str(output))
  if gen is None:raise RuntimeError("FREE_I2I_NOT_IMAGE")
  gen=cv2.resize(gen,(720,1280),interpolation=cv2.INTER_AREA)
  corr=correlation(original,gen)
  hsv=cv2.cvtColor(gen,cv2.COLOR_BGR2HSV)
  sat=float(np.mean(hsv[:,:,1]))
  # Conservative image identity test; AI cannot pass human semantic quality itself.
  if corr<.82 or not 18<sat<175:
   raise RuntimeError("FREE_I2I_ALTERED_IDENTITY_OR_COLOR (corr=%.3f sat=%.2f)"%(corr,sat))
  cv2.imwrite(str(TARGET),gen,[cv2.IMWRITE_JPEG_QUALITY,96])
  method="finegrain-free-image-to-image"
  failure=None
 except Exception as exc:
  # Disclose any downgrade. Never fabricate restoration success.
  method="V92 source-locked DDColor fallback — image-to-image unverified"
  failure={"type":type(exc).__name__,"message":str(exc)[:300]}
  cv2.imwrite(str(TARGET),base,[cv2.IMWRITE_JPEG_QUALITY,96])
  corr=correlation(original,base)
  sat=float(np.mean(cv2.cvtColor(base,cv2.COLOR_BGR2HSV)[:,:,1]))
 # Compare all 3 for visual reviewer, not a substitute for seeing actual film.
 strip=Image.new("RGB",(3*400,750),(15,19,23))
 d=ImageDraw.Draw(strip)
 items=[original,base,cv2.imread(str(TARGET))]
 labels=["REAL FILM B/W","V92 COLOR PHOTO","NEW IMAGE2IMAGE / FALLBACK"]
 for i,(im,label) in enumerate(zip(items,labels)):
  thumb=Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB)).resize((396,704))
  strip.paste(thumb,(400*i+2,32))
  d.text((400*i+7,8),label,fill=(255,244,221))
 strip.save(ROOT/"V95_FACE_FIDELITY_PREPAY_REVIEW.jpg",quality=92)
 q={"scene":8,"subject_verified":"Smiling and speaking men, Bombay 1929, source t=399.2s",
    "source_original":"https://commons.wikimedia.org/wiki/File:Street_Scenes_in_Bombay,_India_(real_sound),_Jan_1929.webm",
    "original_BW_source_sha256":sha(BW),"previous_photo_sha256":sha(PHOTO),
    "new_color_anchor_sha256":sha(TARGET),"restoration_method":method,
    "image2image_call_succeeded":failure is None,
    "free_service_problem":failure,
    "gray_correlation_original_to_anchor":round(corr,3),
    "mean_saturation":round(sat,2),
    "first_image_matches_1929_scene":corr>=.82,
    "source_crop_has_complete_visible_focal_faces":True,
    "manual_anatomy_review":"PENDING","new_vidu_credits_used":0}
 (ROOT/"V95_FACE_RESTORATION_QA.json").write_text(json.dumps(q,ensure_ascii=False,indent=2)+"\n")
 print("V95_FREE_RESTORATION_REVIEW_READY",method,round(corr,3),round(sat,2),sha(TARGET),flush=True)
if __name__=="__main__":restore()
