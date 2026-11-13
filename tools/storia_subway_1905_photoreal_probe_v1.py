#!/usr/bin/env python3
"""NEW 1905 subway film: source-locked photoreal image-to-image trial; zero paid Vidu.
Do not label neural DDColor/ESRGAN photo-real. Save comparative evidence and stop if photo QA fails."""
import os,sys,json,math,pathlib,hashlib,traceback,subprocess
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
from gradio_client import Client,handle_file
sys.path.insert(0,"src")
import storia_rivive_real_ai_v60 as dd
S=pathlib.Path("output/storia_subway_1905_source")
R=pathlib.Path("output/storia_subway_1905_photo_trial")
R.mkdir(parents=True,exist_ok=True)
def log(*x):print(*x,flush=True)
def sha(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for piece in iter(lambda:f.read(1<<20),b""):h.update(piece)
 return h.hexdigest()
def save(name,obj):
 (R/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+"\n")
def graycorr(a,b):
 def norm(im):
  g=cv2.cvtColor(cv2.resize(im,(120,180)),cv2.COLOR_BGR2GRAY)
  return cv2.GaussianBlur(g,(7,7),0).astype("float32").ravel()
 a,b=norm(a),norm(b)
 return float(np.corrcoef(a,b)[0,1]) if a.std()>.5 and b.std()>.5 else -1
def crop_roi(frame):
 h,w=frame.shape[:2]
 crop_w=round(h*.5625)
 g=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
 cascade=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
 faces=cascade.detectMultiScale(cv2.equalizeHist(g),1.1,4,minSize=(22,22))
 poss=[]
 for x in range(0,max(1,w-crop_w)+1,20):
  good=[(a,b) for fx,fy,a,b in faces if fx>=x+8 and fx+a<x+crop_w-8]
  cnt=len(good);sizes=sum(math.sqrt(a*b) for a,b in good)
  poss.append((cnt*30+sizes*.4-.06*abs(x+crop_w/2-w/2),x,cnt))
 if not poss:raise RuntimeError("NO_CROP")
 _,x,n=max(poss)
 roi=cv2.resize(frame[:,x:x+crop_w],(720,1280),interpolation=cv2.INTER_CUBIC)
 return roi,{"crop_x_original":x,"crop_width_original":crop_w,"face_count_in_crop_automatic":n,"input_resolution":[w,h]}
def candidate_qa(source,conditioning,candidate,model):
 c=cv2.resize(candidate,(720,1280))
 corr=graycorr(source,c)
 sat=float(cv2.cvtColor(c,cv2.COLOR_BGR2HSV)[:,:,1].mean())
 delta=float(cv2.absdiff(conditioning,c).mean())
 lap=float(cv2.Laplacian(cv2.cvtColor(c,cv2.COLOR_BGR2GRAY),cv2.CV_32F).var())
 # Correlation is only an automated gross composition check, not a face identity review.
 pass_auto=bool(corr>=.80 and 20<=sat<=137 and delta>=2.4 and lap>9)
 return c,{"model":model,"geometry_corr":round(corr,4),"mean_saturation":round(sat,2),
           "delta_vs_DDColor_base":round(delta,2),"texture_metric":round(lap,2),
           "automatic_source_and_color_gate":pass_auto,
           "face_identity_human_review_required":True}
def photo_trial():
 report=json.loads((S/"SCOUT_REPORT.json").read_text())
 if report.get("status")!="FIVE_ACTUAL_ORIGINAL_FRAMES_SOURCE_SCOUT_ONLY":raise RuntimeError("UNVERIFIED_ORIGINAL_FILM")
 if report.get("reality_status")!="FICTIONAL_REENACTMENT_NOT_ACTUAL_SUBWAY_PASSENGERS":raise RuntimeError("FICTION_MISREPRESENTED")
 film=S/"SOURCE_1905_REAL_MOVING.webm"
 if not film.is_file() or sha(film)!=report["source_metadata"]["sha256"]:raise RuntimeError("MISSING_OR_HASH_CHANGED_ORIGINAL")
 if report["original_resolution"][0]<1200 or report["original_resolution"][1]<900:raise RuntimeError("SOURCE_SCANNER_BELOW_ORIGINAL_RES")
 # Select the scene with most visible frontal faces, not an arbitrary timestamp.
 scored=sorted(report["selected"],key=lambda x:(x["faces_auto"]*12+x["sharp"]/13+x["contrast"]/10),reverse=True)
 clip=cv2.VideoCapture(str(film))
 frame=None;selected=None
 for row in scored:
  clip.set(cv2.CAP_PROP_POS_MSEC,row["time"]*1000)
  ok,f=clip.read()
  if ok and float(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).std())>23:
   frame=f;selected=row;break
 clip.release()
 if frame is None:raise RuntimeError("NO_SOURCE_FRAME_WITH_DETAILS")
 bw,roi=crop_roi(frame)
 # No false original colors.
 gray=cv2.cvtColor(bw,cv2.COLOR_BGR2GRAY)
 bw=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)
 bwfile=R/"ORIGINAL_REAL_1905_EXACT_CROPPED.png"
 cv2.imwrite(str(bwfile),bw)
 model,_=dd.download_model()
 lab=cv2.cvtColor(bw.astype(np.float32)/255,cv2.COLOR_BGR2LAB)
 ab=dd.infer_ab(model,bw)
 lab[:,:,1:]=np.clip(cv2.resize(ab,(720,1280))*.85,-95,95)
 conditioned=np.uint8(np.clip(cv2.cvtColor(lab,cv2.COLOR_LAB2BGR)*255,0,255))
 basefile=R/"DDCOLOR_BASE_ONLY_NOT_A_PHOTOREAL_PHOTO.png"
 cv2.imwrite(str(basefile),conditioned)
 qa={"historic_film_sha":sha(film),"source_anchor_s":selected["time"],
     "source_original_bw_sha":sha(bwfile),"crop":roi,
     "original_source":"https://www.loc.gov/item/2025126022/",
     "camera":"G.W. Bitzer","filmed":"1905-06-05","dramatized_not_candid":True,
     "free_paid_vidu_posts":0,"i2i_trials":[],"zero_gpu_quota_errors":[],
     "photos_ready_for_final":False,"artistic_approval":False}
 prompt=("Source-locked photographic RESTORATION of the EXACT same 1905 Biograph movie still from "
   "the short film Two A.M. in the Subway, a staged comedy set on the New York subway. "
   "Highly realistic present-day full color OPTICAL PHOTOGRAPH of exactly the same actors, "
   "same hats, same bodies, faces, clothes and train scenery from this precise film frame. "
   "Keep each actor exactly where the person is, historically plausible fabrics and complex textures; "
   "preserve source eye spacing, nose, mouth and expressions without creating new eyes, teeth or faces. "
   "Natural warm skin and muted real daylight/tungsten studio hues, real photographic detail not painting, "
   "no magic smoothing, no plastic skin, no saturation filter. Respect source composition and camera angle, "
   "even if film has limited genuine recoverable fine detail. Vertical 9:16.")
 neg=("synthetic faces, beautified actors, extra limbs, extra people, modern clothes, changed hat, "
      "overly saturated, fake eyes, glamour makeup, distorted hands, overpainted skin, illustration, cartoon, "
      "sticker, painting, blurry face, colorless, monochrome, sepia, text, caption, watermark")
 def attempt(provider,fn):
  try:
   pic=fn()
   if isinstance(pic,dict):pic=pic.get("path")
   if not isinstance(pic,str):raise RuntimeError("PROVIDER_RETURN_NOT_IMAGE_PATH")
   raw=cv2.imread(pic)
   if raw is None:raise RuntimeError("NO_REAL_IMAGE_RETURNED")
   image,metrics=candidate_qa(bw,conditioned,raw,provider)
   target=R/(provider.upper()+"_NEW_REAL_I2I_PHOTO.jpg")
   cv2.imwrite(str(target),image,[cv2.IMWRITE_JPEG_QUALITY,95])
   metrics["photo_sha256"]=sha(target);metrics["photo_filename"]=target.name
   qa["i2i_trials"].append(metrics);log("IMAGE_PROVIDER_RESULT",provider,metrics)
  except Exception as e:
   qa["i2i_trials"].append({"model":provider,"actual_image":False,
       "error_class":type(e).__name__,"error":str(e)[:370]})
   log("IMAGE_PROVIDER_FAILED",provider,type(e).__name__,str(e)[:200])
  save("ONE_PHOTO_MODEL_AUDIT.json",qa)
 def fine():
  client=Client("finegrain/finegrain-image-enhancer",verbose=False)
  result=client.predict(handle_file(str(basefile)),prompt,neg,1905,2,1.14,.97,6,112,144,.45,18,"DDIM",api_name="/process")
  if isinstance(result,(tuple,list)) and len(result)>1:
   result=result[1]
  return result
 def qwen():
  # Single publicly hosted free Qwen edit test, zero Vidu credits.
  client=Client("Qwen/Qwen-Image-Edit-2509",verbose=False)
  out=client.predict([[handle_file(str(basefile)),None]],prompt,42,False,4.0,22,1024,576,False,api_name="/infer")
  gallery=out[0] if isinstance(out,(list,tuple)) else out
  if isinstance(gallery,list):gallery=gallery[0]
  if isinstance(gallery,(tuple,list)):gallery=gallery[0]
  if isinstance(gallery,dict):
   gallery=gallery.get("image",gallery)
   if isinstance(gallery,dict):gallery=gallery.get("path",gallery.get("name"))
  return gallery
 attempt("finegrain",fine)
 if not any(r.get("automatic_source_and_color_gate") for r in qa["i2i_trials"]):
  attempt("qwen",qwen)
 # Both generative and non-generative reference: avoid delivering old bad neural images as new photos.
 sources=[("REAL 1905 MOVING FILM",bw),("DDCOLOR NOT APPROVED",conditioned)]
 for v in qa["i2i_trials"]:
  if v.get("photo_filename"):
   sources.append((v["model"].upper()+" PHOTO CANDIDATE",cv2.imread(str(R/v["photo_filename"]))))
 thumb=Image.new("RGB",(len(sources)*350,720),(19,21,26))
 d=ImageDraw.Draw(thumb)
 font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",18)
 for i,(label,im) in enumerate(sources):
  rgb=Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB)).resize((350,622))
  thumb.paste(rgb,(i*350,60))
  d.text((i*350+6,17),label,font=font,fill=(248,239,218))
 thumb.save(R/"TRUE_SOURCE_VS_NEW_PHOTO_CANDIDATES.jpg",quality=94)
 qa["automatic_photo_candidates"]=[v["model"] for v in qa["i2i_trials"] if v.get("automatic_source_and_color_gate")]
 qa["photos_ready_for_final"]=False # Human review required, one image is not a five-scene master.
 qa["next_step"]="Full five scene generation only if genuinely source-locked photoreal photos; NO Vidu until visual QA."
 save("ONE_PHOTO_MODEL_AUDIT.json",qa)
 log("ONE_SCENE_PHOTO_TRIAL_DONE_NO_PAID_VIDU",json.dumps(qa["automatic_photo_candidates"]))
if __name__=="__main__":
 try:photo_trial()
 except Exception as e:
  save("FAILED_WITHOUT_VIDU_SPEND.json",{"error_type":type(e).__name__,"reason":str(e)[:400],"vidu_posts":0})
  log("PREVIEW_FAILED",type(e).__name__,str(e)[:400]);raise
