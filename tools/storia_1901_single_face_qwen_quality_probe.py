#!/usr/bin/env python3
"""One genuine photo-edit attempt on archived 1901 workers. Zero Vidu calls. Fail-closed photo-first experiment."""
import hashlib,io,json,os,pathlib,subprocess,sys,time,zipfile
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
from gradio_client import Client,handle_file
R=pathlib.Path("output/storia_1901_photo_first_probe")
R.mkdir(parents=True,exist_ok=True)
S=pathlib.Path("output/storia_workers_1901_source")
SOURCE=S/"SOURCE_1901_REAL_MOVING.webm"
REPORT=S/"SCOUT_REPORT.json"
def save(name,data):(R/name).write_text(json.dumps(data,indent=2,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf8")
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
 return h.hexdigest()
def centered_crop(img):
 h,w=img.shape[:2];cropw=round(h*9/16)
 gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
 face=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
 faces=face.detectMultiScale(cv2.equalizeHist(gray),scaleFactor=1.1,minNeighbors=4,minSize=(22,22))
 best=(-1,0)
 for x in range(0,w-cropw+1,12):
  contained=[(a,b,fw,fh) for a,b,fw,fh in faces if x+5<a and a+fw<x+cropw-5]
  score=sum(fw*fh for a,b,fw,fh in contained)+300*len(contained)-.1*abs((x+cropw/2)-w/2)
  if score>best[0]:best=(score,x)
 x=best[1]
 return cv2.resize(img[:,x:x+cropw],(720,1280),interpolation=cv2.INTER_CUBIC),{"source_faces":len(faces),"crop_x":x,"crop_width":cropw,"total_crop_face_area":best[0]}
def prep():
 report=json.loads(REPORT.read_text())
 if sha(SOURCE)!=report["source_metadata"]["sha256"]:raise RuntimeError("ARCHIVAL_SOURCE_CHANGED")
 frame_time=152.0 # independently selected source scout frame with 10 automatically detected faces.
 cap=cv2.VideoCapture(str(SOURCE));cap.set(cv2.CAP_PROP_POS_MSEC,frame_time*1000)
 ok,frame=cap.read();cap.release()
 if not ok:raise RuntimeError("HISTORIC_FRAME_UNREADABLE")
 bw,crop=centered_crop(frame)
 if crop["total_crop_face_area"]<500:raise RuntimeError("NO_FACE_AREA_WORTH_RESTORING")
 original=R/"ORIGINAL_REAL_1901_FRAME.png"
 cv2.imwrite(str(original),bw)
 return original,crop
def gradio_result(raw):
 candidates=[]
 def visit(obj):
  if isinstance(obj,str) and pathlib.Path(obj).is_file():candidates.append(pathlib.Path(obj))
  elif isinstance(obj,dict):
   for k in ("path","name","url","image"): 
    if k in obj:visit(obj[k])
  elif isinstance(obj,(list,tuple)):
   for item in obj:visit(item)
 visit(raw)
 for p in candidates:
  try:
   im=cv2.imread(str(p))
   if im is not None and im.size>0:return im
  except Exception:pass
 raise RuntimeError("QWEN_NO_DECODEABLE_PHOTO_FILE")
def similarity(a,b):
 def gray(im):
  x=cv2.cvtColor(cv2.resize(im,(100,180)),cv2.COLOR_BGR2GRAY)
  return cv2.GaussianBlur(x,(7,7),0).astype(np.float32).ravel()
 x=gray(a);y=gray(b)
 return float(np.corrcoef(x,y)[0,1]) if x.std()>.1 and y.std()>.1 else -1
def generate(original):
 base=cv2.imread(str(original))
 prompt=("Restore and colorize THIS EXACT original real 1901 Edwardian factory worker historical motion-picture frame into an ultra-realistic clear modern photographic still. "
 "This is strict image editing, NOT text-to-image creation. Preserve exactly every existing person and their facial structure, eye direction, body proportions, hats, garments, authentic factory architecture, camera angle, background and crowd density. "
 "Natural British cloudy daylight, realistic human skin microtexture, hair, wool, textiles, old stone and historical atmosphere. Do not beautify, invent, clone, remove or reposition anyone. "
 "Attractive and emotionally powerful documentary photography, not a painting, and NOT sepia or monochrome. Distinct naturally plausible color across skin, clothes and environment. "
 "No subtitles, text, fake watermarks, digital plastic skin, modern cosmetics, fantasy colors, artifact doubling, extra heads, invented eyes, smooth mannequins, or changed clothing.")
 client=Client("Qwen/Qwen-Image-Edit-2509",verbose=False)
 # Configuration confirmed in existing repository test: image, prompt, seed, random seed, cfg, steps, width, height, prompt extend.
 raw=client.predict([[handle_file(str(original)),None]],prompt,1901,False,3.0,24,576,720,False,api_name="/infer")
 image=gradio_result(raw)
 image=cv2.resize(image,(720,1280),interpolation=cv2.INTER_AREA)
 geometry=similarity(base,image)
 sat=float(np.mean(cv2.cvtColor(image,cv2.COLOR_BGR2HSV)[:,:,1]))
 source_sat=float(np.mean(cv2.cvtColor(base,cv2.COLOR_BGR2HSV)[:,:,1]))
 color_fraction=float(np.mean(cv2.cvtColor(image,cv2.COLOR_BGR2HSV)[:,:,1]>35))
 detail=float(cv2.Laplacian(cv2.cvtColor(image,cv2.COLOR_BGR2GRAY),cv2.CV_32F).var())
 metrics={"provider":"Qwen/Qwen-Image-Edit-2509","source_frame_sha256":sha(original),
  "source_to_photo_geometry_correlation":round(geometry,4),
  "color_saturation_avg":round(sat,2),"color_coverage_fraction":round(color_fraction,4),
  "source_gray_saturation":round(source_sat,2),"laplacian_detail":round(detail,2),
  "human_face_fidelity":"NOT_HUMAN_VERIFIED","social_or_site_published":False,
  "vidu_post_count":0,"vidu_credits_spent":0,"photorealism_approved":False}
 out=R/"QWEN_PHOTO_1901_CANDIDATE.jpg"
 cv2.imwrite(str(out),image,[cv2.IMWRITE_JPEG_QUALITY,96])
 metrics["candidate_sha256"]=sha(out)
 # Numerical pass alone only qualifies for review, never certification.
 metrics["technical_review_candidate"]=bool(geometry>=.76 and sat>=22 and color_fraction>=.23 and detail>10)
 save("QWEN_PHOTO_METRICS.json",metrics)
 image_before=Image.fromarray(cv2.cvtColor(base,cv2.COLOR_BGR2RGB))
 image_after=Image.fromarray(cv2.cvtColor(image,cv2.COLOR_BGR2RGB))
 sheet=Image.new("RGB",(1040,980),(16,19,22))
 draw=ImageDraw.Draw(sheet)
 for idx,img in enumerate((image_before,image_after)):
  img.thumbnail((490,870))
  x=15+idx*520+(490-img.width)//2
  sheet.paste(img,(x,44))
 draw.text((20,15),"ORIGINAL 1901 FILM FRAME",fill="white")
 draw.text((541,15),"NEW AI IMAGE EDIT  ·  ARTISTIC REVIEW PENDING",fill="white")
 draw.text((20,940),f"Exact source locked, geometry correlation {geometry:.3f}. Colors are modern interpretations.",fill="#e1dbd2")
 sheet.save(R/"1901_REAL_SOURCE_VS_NEW_PHOTOGRAPH.jpg",quality=93)
 print("QWEN_TRUE_IMAGE_EDIT_RETURNED",json.dumps(metrics),flush=True)
 if not metrics["technical_review_candidate"]:raise RuntimeError("PHOTO_REJECTED_BY_TECHNICAL_GATES_DO_NOT_VIDEO")
 return metrics
def main():
 original,crop=prep()
 save("HISTORIC_SOURCE_PROVENANCE.json",{"source":"Wikimedia Commons original, 1901 workers film","original_sha256":sha(SOURCE),
  "source_url":"https://commons.wikimedia.org/wiki/File:Victorian-Edwardian_workers_caught_on_film_(1901).webm",
  "source_time_s":152.0,"vertical_crop":crop,"no_existing_2026_video_reuse":True})
 report=generate(original)
 print("PHOTO_ONLY_QWEN_SUCCESS_REAL_FRAME_WAITING_HUMAN_REVIEW_NO_VIDU",flush=True)
if __name__=="__main__":
 try:main()
 except Exception as exc:
  save("PHOTO_PROBE_FAILURE.json",{"status":"BLOCKED_NO_NEW_VIDEO","error":type(exc).__name__+": "+str(exc)[:350],
   "no_paid_video_attempt":True,"human_quality_approved":False})
  print("PHOTO_FIRST_TEST_BLOCKED_NO_PAID_VIDEO",type(exc).__name__,str(exc)[:300],flush=True)
  sys.exit(1)
