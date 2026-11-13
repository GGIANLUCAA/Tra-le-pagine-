#!/usr/bin/env python3
"""One-and-only-one authorized 1905 film Vidu Q3 Pro 5s scene from verified photoreal Finegrain anchor.
No social publishing; no POST retries; source-locked first-frame, color/motion gates and Android-safe evidence."""
import os,json,base64,pathlib,hashlib,subprocess,urllib.request,urllib.error,time,cv2,numpy as np,sys
R=pathlib.Path("output/storia_subway_1905_vidu_q3")
R.mkdir(parents=True,exist_ok=True)
I=pathlib.Path("output/storia_subway_1905_prev_photo")
REPO="GGIANLUCAA/Tra-le-pagine-"
LEDGER="queue/vidu_api_attempts/SUBWAY_1905_Q3_PRO_FIVE_SECONDS_SINGLE_20261113.json"
MAX_CREDITS=120
def say(*a):print(*a,flush=True)
def save(n,o):(R/n).write_text(json.dumps(o,indent=2,ensure_ascii=False,allow_nan=False)+"\n")
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def cmd(a,timeout=120):
 p=subprocess.run(a,text=True,capture_output=True,timeout=timeout)
 if p.returncode:raise RuntimeError(str(a[:6])+" "+p.stderr[-430:])
 return p.stdout
def gh(a):return json.loads(cmd(["gh","api"]+a))
def provider(key,path,body=None,timeout=70):
 r=urllib.request.Request("https://api.vidu.com"+path,data=json.dumps(body).encode() if body is not None else None,
  headers={"Authorization":"Token "+key,"Accept":"application/json","Content-Type":"application/json"},
  method="POST" if body is not None else "GET")
 with urllib.request.urlopen(r,timeout=timeout) as res:return json.loads(res.read(300000))
def source_photo():
 first=I/"FINEGRAIN_NEW_REAL_I2I_PHOTO.jpg"
 dd=I/"DDCOLOR_BASE_ONLY_NOT_A_PHOTOREAL_PHOTO.png"
 info=json.loads((I/"ONE_PHOTO_MODEL_AUDIT.json").read_text())
 if sha(first)!="7a6e05fd8fc28197d1d9e8c3d132817831f6945b3f71123bc9f5876a32eac5f4":
  raise RuntimeError("UNVERIFIED_FIRST_GENUINE_I2I_PHOTO_NO_VIDU")
 if info["historic_film_sha"]!="9bc7bc7a0a35f7a3fabde683f98b76f4d4dc287adc53cef2e468a04eb2c46428":
  raise RuntimeError("WRONG_SOURCE_FILM_NO_VIDU")
 image=cv2.imread(str(first));color=cv2.imread(str(dd))
 if image is None or color is None or image.shape!=(1280,720,3):raise RuntimeError("I2I_PHOTO_NOT_FULL_VERTICAL")
 lab1=cv2.cvtColor(image,cv2.COLOR_BGR2LAB).astype(np.float32)
 lab2=cv2.cvtColor(color,cv2.COLOR_BGR2LAB).astype(np.float32)
 lab1[:,:,1:]=.6*lab1[:,:,1:]+.4*lab2[:,:,1:]
 out=cv2.cvtColor(np.uint8(np.clip(lab1,0,255)),cv2.COLOR_LAB2BGR)
 out=np.uint8(np.clip(out.astype(np.float32)*np.array([1.045,1.018,.976])[None,None,:],0,255))
 path=R/"PHOTO_EXACT_VIDU_START_720x1280.jpg"
 cv2.imwrite(str(path),out,[cv2.IMWRITE_JPEG_QUALITY,96])
 full=cv2.resize(out,(1080,1920),interpolation=cv2.INTER_CUBIC)
 sent=R/"PHOTO_SENT_VIDU_1080x1920.jpg"
 cv2.imwrite(str(sent),full,[cv2.IMWRITE_JPEG_QUALITY,95])
 return path,sent,info
def first_corr(a,b):
 def g(img):
  gray=cv2.cvtColor(cv2.resize(img,(128,228)),cv2.COLOR_BGR2GRAY).astype("float32")
  return cv2.GaussianBlur(gray,(5,5),0).ravel()
 x,y=g(a),g(b)
 if x.std()<.5 or y.std()<.5:return -1
 return float(np.corrcoef(x,y)[0,1])
def ledger_new(data):
 blob=base64.b64encode((json.dumps(data,sort_keys=True)+"\n").encode()).decode()
 gh(["-X","PUT","repos/"+REPO+"/contents/"+LEDGER,"-f","branch=main",
  "-f","message=Reserve single authorized 1905 subway Q3 Pro scene from audited real I2I",
  "-f","content="+blob])
def ledger_update(data):
 previous=gh(["repos/"+REPO+"/contents/"+LEDGER+"?ref=main"])
 blob=base64.b64encode((json.dumps(data,sort_keys=True)+"\n").encode()).decode()
 gh(["-X","PUT","repos/"+REPO+"/contents/"+LEDGER,"-f","branch=main",
  "-f","sha="+previous["sha"],"-f","message=Record actual 1905 Vidu task and no-retry result",
  "-f","content="+blob])
def main():
 key=os.environ.get("VIDU_API_KEY","").strip()
 if not key:raise RuntimeError("NO_VIDU_KEY")
 # No duplicate requests, even if GH reruns the same workflow.
 try:
  gh(["repos/"+REPO+"/contents/"+LEDGER+"?ref=main"])
 except Exception as e:
  if "404" not in str(e) and "Not Found" not in str(e):
   raise RuntimeError("CANNOT_VERIFY_NO_PRIOR_CHARGE_DO_NOT_POST")
 else:raise RuntimeError("LEDGER_ALREADY_EXISTS_DO_NOT_CHARGE_TWICE")
 path,sent,src=source_photo()
 credits=provider(key,"/ent/v2/credits")
 remains=credits.get("remains")
 if not isinstance(remains,list) or not any(isinstance(x,dict) and type(x.get("credit_remain")) in (int,float) and x["credit_remain"]>=MAX_CREDITS for x in remains):
  raise RuntimeError("VIDU_PREPAID_CREDITS_NO_VERIFIABLE_120_BLOCK")
 receipt={"status":"reserved_before_post","paid_posts":0,"spend_cap":MAX_CREDITS,
  "source_film_sha":src["historic_film_sha"],"photo_i2i_sha":sha(path),"photo_sent_sha":sha(sent),
  "model":"viduq3-pro","resolution":"1080p","duration":5,
  "one_post_only":True,"authorization":"Owner authorized new Vidu credit use for new La Storia Rivive videos; no new purchases",
  "release":"owner_review_only"}
 ledger_new(receipt);save("VIDU_RECEIPT.json",receipt)
 prompt=("ONE CONTINUOUS FIVE SECOND PHOTO-REALISTIC COLOR CINEMATIC SHOT, same original "
  "fictional cast of Biograph's '2 A.M. in the Subway' (filmed 1905), starting from the exact "
  "input high-resolution photograph. The young woman at center smiles and gently waves with realistic "
  "natural arm and hand movements; the man to her right smiles and turns his head a little, "
  "while the uniformed policeman at her left stays near the stairs. "
  "Real gentle breathing, genuine human eye blinks and gestures, restrained natural period acting. "
  "Exactly preserve ALL source actors, positions, Edwardian dresses and coats, hats and train set, "
  "hands, faces and hairstyle in the same 1905 staged film. No modern objects, no new people, no face changes, "
  "no painted or plastic skin, no morphing, no fake extra arms. "
  "Camera locked, no zoom, no cuts, no pan, no music or dialogue, live-action natural realistic documentary-grade "
  "photography in believable full color from the FIRST FRAME, no monochrome, no sepia.")
 body={"model":"viduq3-pro","images":["data:image/jpeg;base64,"+base64.b64encode(sent.read_bytes()).decode()],
       "prompt":prompt,"duration":5,"resolution":"1080p","audio":False,
       "is_rec":False,"off_peak":False,"payload":"owner-new-1905-subway-one-q3-photo-locked"}
 try:
  post=provider(key,"/ent/v2/img2video",body,timeout=80)
 except Exception as e:
  receipt.update(status="ambiguous_paid_submission_NEVER_RETRY",paid_posts=1,error_class=type(e).__name__)
  ledger_update(receipt);save("VIDU_RECEIPT.json",receipt)
  raise RuntimeError("VIDU_POST_UNKNOWN_NEVER_RETRY")
 task=str(post.get("task_id") or "")
 cost=post.get("credits")
 receipt.update(status="submitted",paid_posts=1,task_id=task,reported_credits=cost)
 ledger_update(receipt);save("VIDU_RECEIPT.json",receipt)
 if not task or type(cost) not in (float,int) or cost>MAX_CREDITS:
  raise RuntimeError("PROVIDER_REPORTED_COST_NOT_WITHIN_LIMIT_NEVER_RETRY")
 say("VIDU_Q3_NEW_SUBWAY_ONCE_ACCEPTED",task,"CREDITS",cost)
 state=None
 for i in range(66):
  time.sleep(10)
  try:status=provider(key,"/ent/v2/tasks/"+task+"/creations",timeout=40)
  except Exception:continue
  if status.get("state") in ("failed","cancelled"):
   receipt.update(status="failed_no_retry");ledger_update(receipt)
   raise RuntimeError("VIDU_PROVIDER_FAILED_NO_RETRY")
  if status.get("state")=="success":
   state=status;break
 if state is None:
  receipt.update(status="pending_GET_ONLY_NO_NEW_POST");ledger_update(receipt)
  raise RuntimeError("VIDU_PENDING_CONTINUE_POLL_ONLY")
 clips=state.get("creations") or []
 url=clips[0].get("url") if clips else None
 if not isinstance(url,str) or not url.startswith("https://"):raise RuntimeError("NO_REAL_RESULT_VIDEO_URL")
 import requests
 clip=R/"VIDU_REAL_Q3_PRO_SUBWAY_MOVING_5_SECONDS.mp4"
 with requests.get(url,stream=True,timeout=(25,160)) as resp:
  resp.raise_for_status()
  with clip.open("wb") as f:
   for c in resp.iter_content(1<<20):
    f.write(c)
    if f.tell()>120000000:raise RuntimeError("VIDEO_BYTES_OVER_LIMIT")
 cmd(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(clip),"-f","null","-"],190)
 cap=cv2.VideoCapture(str(clip))
 fps=cap.get(cv2.CAP_PROP_FPS);n=cap.get(cv2.CAP_PROP_FRAME_COUNT)
 frames=[]
 for t in [0,.5,2.5,4.3]:
  cap.set(cv2.CAP_PROP_POS_MSEC,t*1000)
  ok,im=cap.read()
  if not ok:raise RuntimeError("NO_TRUE_VIDU_FRAMES")
  frames.append(cv2.resize(im,(720,1280)))
 cap.release()
 origin=cv2.imread(str(path))
 co=first_corr(origin,frames[0])
 chroma=[float(cv2.cvtColor(f,cv2.COLOR_BGR2HSV)[:,:,1].mean()) for f in frames]
 movement=float(np.abs(frames[3].astype("float32")-frames[1].astype("float32")).mean())
 qa={"model":"viduq3-pro","task_id":task,"credits_provider_reported":cost,
     "video_sha256":sha(clip),"bytes":clip.stat().st_size,
     "actual_video_duration_sec":round(n/max(1,fps),3),
     "photo_match_correlation":co,"mean_saturation_at_seconds_0_05_25_43":chroma,
     "motion_change_metric":movement,"no_artist_approval":True,
     "technical_pass":bool(co>=.76 and min(chroma)>18 and movement>1.4 and n/max(1,fps)>4.65)}
 for i,f in enumerate(frames):
  cv2.imwrite(str(R/f"VIDU_FRAME_{i:02d}_REVIEW.jpg"),f,[cv2.IMWRITE_JPEG_QUALITY,91])
 save("VIDU_REAL_CLIP_QA.json",qa)
 receipt.update(status="video_collected_technical_QA_"+("PASS" if qa["technical_pass"] else "FAIL"),video_sha=sha(clip),qa=qa)
 ledger_update(receipt)
 say("VIDU_SINGLE_VIDEO_COLLECTED",qa)
 if not qa["technical_pass"]:
  raise RuntimeError("VIDU_REAL_CLIP_DID_NOT_MATCH_PHOTO_QA_NO_RETRY")
if __name__=="__main__":
 try:main()
 except Exception as e:
  save("FAILURE.json",{"type":type(e).__name__,"error":str(e)[:400],"never_retry_post":True})
  say("VIDU_WORKFLOW_STOPPED",str(e)[:220]);sys.exit(1)
