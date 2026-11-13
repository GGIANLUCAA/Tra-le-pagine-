#!/usr/bin/env python3
"""One anonymous no-money image-to-image trial on an authentic public 1901 source photo.
No Vidu, no social posting, no commercial approval. Reject hallucination and keep comparison."""
import base64,hashlib,io,json,os,pathlib,sys,time,requests,cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=pathlib.Path("output/storia_1901_horde_photo")
ROOT.mkdir(parents=True,exist_ok=True)
SRC=pathlib.Path("output/storia_1901_photo_first_probe/ORIGINAL_REAL_1901_FRAME.png")
API="https://aihorde.net/api/v2"
USERAGENT="LaStoriaRivive/0.1 (educational source faithful test; GitHub GGIANLUCAA/Tra-le-pagine-)"
MODEL="ICBINP - I Can't Believe It's Not Photography"
def save(name,v):(ROOT/name).write_text(json.dumps(v,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for x in iter(lambda:f.read(1<<20),b""):h.update(x)
 return h.hexdigest()
def request(method,path,**kwargs):
 r=requests.request(method,API+path,headers={"User-Agent":USERAGENT,
  "apikey":"0000000000","Client-Agent":"LaStoriaRivive:0.1:public-archive-research",
  "Content-Type":"application/json"},timeout=(18,55),**kwargs)
 if r.status_code>=400:raise RuntimeError("HORDE_HTTP_"+str(r.status_code)+" "+r.text[:350])
 return r.json()
def corr(a,b):
 def prep(img):
  g=cv2.cvtColor(cv2.resize(img,(108,176)),cv2.COLOR_BGR2GRAY)
  return cv2.GaussianBlur(g,(7,7),0).astype(np.float32).ravel()
 x,y=prep(a),prep(b)
 return float(np.corrcoef(x,y)[0,1]) if x.std()>.1 and y.std()>.1 else -1.0
def main():
 if not SRC.is_file():raise RuntimeError("ORIGINAL_ARCHIVAL_FRAME_MISSING")
 original=cv2.imread(str(SRC))
 if original is None:raise RuntimeError("ARCHIVAL_FRAME_BAD")
 # Separate semantic color recovery from human photographic detail.
 # The historical source remains the ground truth for the final shape comparison.
 import storia_rivive_real_ai_v60 as dd
 ddmodel,_=dd.download_model()
 sample=cv2.resize(original,(720,576),interpolation=cv2.INTER_AREA)
 ab=dd.infer_ab(ddmodel,sample)
 lab=cv2.cvtColor(original.astype(np.float32)/255.,cv2.COLOR_BGR2LAB)
 lab[:,:,1:]=np.clip(cv2.resize(ab,(original.shape[1],original.shape[0]))*1.08,-92,92)
 naturally_colored=np.uint8(np.clip(cv2.cvtColor(lab,cv2.COLOR_LAB2BGR)*255,0,255))
 baseline_color=float(np.mean(cv2.cvtColor(naturally_colored,cv2.COLOR_BGR2HSV)[:,:,1]))
 if baseline_color<12:raise RuntimeError("NEURAL_COLOR_BASE_TOO_GRAY_NO_IMG2IMG")
 cv2.imwrite(str(ROOT/"NEURAL_COLOR_CONDITIONING_NOT_FINAL.jpg"),naturally_colored,[cv2.IMWRITE_JPEG_QUALITY,96])
 scaled=cv2.resize(naturally_colored,(512,896),interpolation=cv2.INTER_AREA)
 im=Image.fromarray(cv2.cvtColor(scaled,cv2.COLOR_BGR2RGB))
 out=io.BytesIO();im.save(out,format="WEBP",quality=88)
 b64=base64.b64encode(out.getvalue()).decode("ascii")
 models=request("GET","/status/models")
 matching=next((m for m in models if m.get("name")==MODEL),None)
 if not matching or matching.get("count",0)<1:raise RuntimeError("EXACT_PHOTOGRAPHIC_MODEL_NOT_AVAILABLE")
 prompt=("STRICT photographic restoration of exactly this original 1901 archival motion film frame, now already neutrally colorized by DDColor of factory workers, "
 "preserve the chromatic palette of the colored reference, same authentic historical people faces and face count, identical eyes, heads, hats, clothes and positions, "
 "same architecture and authentic group, detailed modern documentary COLOR photography, authentic natural light, life-like skin texture and subtle colors, "
 "everything source-locked, genuine British industrial history, realistic hair and textile texture ### "
 "new people, altered faces, fake clothing, different background, fantasy, invented objects, deformed hands, painting, cartoon, wax skin, "
 "stock photo models, modern cars, orange saturation, sepia, monochrome, oil painting")
 body={"prompt":prompt,"params":{"sampler_name":"k_euler","cfg_scale":5.5,"steps":22,"width":512,"height":896,
  "denoising_strength":0.36,"n":1,"seed":"1901"},
  "source_image":b64,"source_processing":"img2img","models":[MODEL],
  "nsfw":False,"censor_nsfw":True,"r2":False,"shared":False,
  "slow_workers":True}
 save("PRE_SUBMISSION.json",{"model":MODEL,"source_sha256":sha(SRC),
  "source_processing":"img2img","input":"actual frame DDColor chroma conditioned","denoising_strength":0.36,"mode":"anonymous free public-archive research",
  "paid_api_calls":0,"vidu_calls":0,"external_worker_input":"authentic public historical footage frame",
  "shared_policy":"anonymous AI Horde may share image with LAION; no private user photo","human_QA_pending":True})
 job=request("POST","/generate/async",json=body)
 uid=str(job.get("id") or "")
 if not uid:raise RuntimeError("HORDE_NO_JOB_ID "+str(job)[:180])
 save("JOB_STATUS.json",{"job_id":uid,"state":"submitted","credits_purchased":0,
  "vidu_calls":0,"requires_owner_visual_QA":True})
 print("HORDE_SOURCE_LOCKED_IMG2IMG_SUBMITTED",uid,flush=True)
 result=None
 for attempt in range(42):
  time.sleep(8)
  status=request("GET","/generate/check/"+uid)
  if status.get("faulted"):raise RuntimeError("HORDE_JOB_FAULTED")
  if status.get("done"):
   result=request("GET","/generate/status/"+uid)
   break
 if result is None:
  save("JOB_STATUS.json",{"job_id":uid,"state":"pending_no_repeat","cost":0,"no_repost":True})
  raise RuntimeError("HORDE_QUEUED_NO_REPOST")
 gens=result.get("generations") or []
 if not gens:raise RuntimeError("HORDE_COMPLETED_WITHOUT_IMAGE")
 item=gens[0].get("img")
 if not item:raise RuntimeError("HORDE_IMAGE_MISSING")
 if item.startswith("http"):
  response=requests.get(item,timeout=(15,45))
  response.raise_for_status();data=response.content
 else:data=base64.b64decode(item.split(",")[-1])
 if len(data)>14000000:raise RuntimeError("REMOTE_IMAGE_OVERSIZE")
 p=ROOT/"AI_HORDE_PHOTOGRAPH_CANDIDATE.webp";p.write_bytes(data)
 try:edited=Image.open(io.BytesIO(data)).convert("RGB")
 except Exception as e:raise RuntimeError("MODEL_IMAGE_NOT_DECODABLE") from e
 processed=cv2.cvtColor(np.array(edited.resize((720,1280))),cv2.COLOR_RGB2BGR)
 geom=corr(original,processed)
 hsv=cv2.cvtColor(processed,cv2.COLOR_BGR2HSV)
 sat=float(hsv[:,:,1].mean())
 spread=float(np.mean(hsv[:,:,1]>35))
 sharp=float(cv2.Laplacian(cv2.cvtColor(processed,cv2.COLOR_BGR2GRAY),cv2.CV_32F).var())
 qualified=geom>=.83 and 18<=sat<=145 and spread>=.18 and sharp>=8
 metrics={"model":MODEL,"source_sha256":sha(SRC),"ai_photo_sha256":sha(p),
  "geometry_corr":round(geom,4),"mean_saturation":round(sat,2),
  "color_area_fraction":round(spread,4),"sharpness":round(sharp,1),
  "technical_photo_candidate":qualified,"human_face_identity_review":"PENDING",
  "public_archival_source":True,"source_processing":"img2img","DDColor_input_base_saturation":round(baseline_color,2),
  "final_video_ready":False,"vidu_paid_calls":0,"commercial_license_approval":False}
 save("PHOTO_QUALITY_REPORT.json",metrics)
 sheet=Image.new("RGB",(960,900),(15,18,23))
 d=ImageDraw.Draw(sheet)
 for i,image in enumerate([Image.fromarray(cv2.cvtColor(original,cv2.COLOR_BGR2RGB)),Image.fromarray(cv2.cvtColor(processed,cv2.COLOR_BGR2RGB))]):
  image.thumbnail((442,810))
  sheet.paste(image,(22+i*477+(442-image.width)//2,42+(810-image.height)//2))
 d.text((25,17),"REAL ARCHIVAL B/W · 1901",fill="white")
 d.text((500,17),"NEW PHOTOGRAPHIC IMG2IMG · REVIEW ONLY",fill="white")
 sheet.save(ROOT/"NEW_AI_PHOTO_VS_REAL_1901_SOURCE.jpg",quality=95)
 print("HORDE_TRUE_NEW_IMAGE_RECEIVED",json.dumps(metrics),flush=True)
 if not qualified:raise RuntimeError("PHOTOGRAPHIC_QA_REJECTED_NO_VIDEO_PRODUCTION")
if __name__=="__main__":
 try:main()
 except Exception as e:
  save("BLOCKER.json",{"status":"NO_APPROVED_NEW_PHOTO","cause":type(e).__name__+": "+str(e)[:400],
    "vidu_credits_spent":0,"do_not_generate_video_without_photographic_approval":True})
  print("HORDE_PHOTO_TEST_NOT_ACCEPTED",type(e).__name__,str(e)[:330],flush=True)
  sys.exit(1)
