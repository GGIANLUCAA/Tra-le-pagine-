#!/usr/bin/env python3
"""V86 ONE new Vidu image-to-video of San Francisco 1906 original historic footage.
User asked for one (and only one) moving-video insert in a fresh 4+1 episode.
No repeat charges: permanent GitHub reservation BEFORE any billable POST;
max 16 API credits on success, no retry if ambiguous or provider fails.
"""
from __future__ import annotations
import base64,hashlib,json,os,time,pathlib,subprocess,urllib.request
import cv2,numpy as np
from PIL import Image

REPO=os.environ.get("GITHUB_REPOSITORY","GGIANLUCAA/Tra-le-pagine-")
KEY=os.environ.get("VIDU_API_KEY","")
R=pathlib.Path("output/storia_v86_sf1906")
PHOTO=R/"FIFTH_VIDU_COLOR_ANCHOR_1906.jpg"
QA=R/"FIFTH_SCENE_RESTORATION_QA.json"
MASTER=R/"VIDU_SF1906_05_ORIGINAL.mp4"
COLOR=R/"VIDU_SF1906_05_COLOR_MOTION.mp4"
LEDGER="queue/vidu_api_attempts/20261029_V86_SF1906_43S_SINGLE.json"
PROMPT=(
 "A meticulously source-faithful five-second LIVE-ACTION COLOR documentary shot, at exactly the same "
 "San Francisco Market Street 1906 location and camera perspective shown in this restored photograph. "
 "FILM MOTION: A cable-car-front camera moves very slowly forward in ONE SINGLE UNBROKEN SHOT; "
 "the existing horse-drawn carriages roll steadily ahead on original street rails, horses walk with "
 "realistic alternating leg motions and physically attached harnesses, wheels rotate as rigid circular "
 "mechanical objects, distant people walk and shift naturally without changing appearances, "
 "colorful woven fabric and leather textures maintain their exact material properties. "
 "PRESERVE EXACTLY the same number of carriages, horses, people, storefronts, rails, windows, "
 "street perspective, clothing and buildings that actually exist in the supplied image. "
 "Architecture remains rigid and still while the moving camera travels slowly with natural documentary pace. "
 "Every second must show genuine continuous physical object and human motion, no still photo push-in or "
 "Ken Burns zoom, no freeze-frame or morph-dissolve, no flicker, no optical flow streaks. "
 "Do not add or remove people, horses, wheels or vehicles; no rubber buildings, no false signs, "
 "no object/person swaps, no camera cuts, no modern cars, no on-screen title or soundtrack. "
 "Authentic period details, rich but restrained believable full-color photographic appearance."
)
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for part in iter(lambda:f.read(1<<20),b""):h.update(part)
 return h.hexdigest()
def cmd(args,limit=100):
 p=subprocess.run(args,capture_output=True,text=True,timeout=limit)
 if p.returncode:raise RuntimeError("LOCAL_COMMAND_FAILED "+str(args[:4])+" "+p.stderr[-1100:])
 return p.stdout
def writej(file,data):
 pathlib.Path(file).write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
def api(path,body=None,method="GET",timeout=65):
 if not KEY:raise RuntimeError("VIDU_SECRET_MISSING")
 data=json.dumps(body).encode() if body is not None else None
 req=urllib.request.Request("https://api.vidu.com"+path,data=data,method=method,headers={
 "Authorization":"Token "+KEY,"Content-Type":"application/json","Accept":"application/json"})
 with urllib.request.urlopen(req,timeout=timeout) as r:return json.loads(r.read(1500000))
def balance():
 response=api("/ent/v2/credits")
 remain=response.get("remains",response.get("remaining_credits"))
 if not isinstance(remain,list):raise RuntimeError("VIDU_BALANCE_SCHEMA_INVALID")
 values=[{"type":str(x.get("type","credits")),"remaining":x.get("credit_remain")} for x in remain if isinstance(x,dict)]
 if not values or any(type(x["remaining"]) not in (int,float) or x["remaining"]<0 for x in values):
  raise RuntimeError("VIDU_BALANCE_INVALID")
 return values
def reserve(doc):
 payload=base64.b64encode((json.dumps(doc,sort_keys=True)+"\n").encode()).decode()
 endpoint=f"repos/{REPO}/contents/{LEDGER}"
 try:
  cmd(["gh","api","-X","PUT",endpoint,"-f","branch=main",
      "-f","message=Reserve one approved V86 San Francisco real-motion Vidu generation (16 credit cap)",
      "-f","content="+payload],75)
 except Exception as e:
  raise RuntimeError("EXISTING_LEDGER_OR_GITHUB_WRITE_UNAVAILABLE_NO_NEW_POST") from e
def update(doc):
 endpoint=f"repos/{REPO}/contents/{LEDGER}"
 old=json.loads(cmd(["gh","api",endpoint+"?ref=main"],45))
 value=base64.b64encode((json.dumps(doc,sort_keys=True)+"\n").encode()).decode()
 cmd(["gh","api","-X","PUT",endpoint,"-f","branch=main","-f","sha="+old["sha"],
      "-f","message=Update single V86 paid Vidu task no duplicate requests","-f","content="+value],60)
def valid_input():
 if not PHOTO.exists() or not QA.exists():raise RuntimeError("UNREVIEWED_FIFTH_PHOTO_NOT_PRESENT")
 d=json.loads(QA.read_text())
 if not d.get("photo_quality_gate_passed") or d.get("source_timestamp_seconds")!=43.0:raise RuntimeError("PHOTO_QA_FAILED")
 if sha(PHOTO)!=d["restored_photo_sha256"]:raise RuntimeError("IMAGE_SHA_MISMATCH")
 src=Image.open(PHOTO)
 if src.size!=(720,1280):raise RuntimeError("VIDU_IMAGE_GEOMETRY_MISMATCH")
 if d.get("geometry_corr",0)<.82:raise RuntimeError("INPUT_NOT_MATCHED_TO_REAL_FRAME")
 return d
def colored_motion():
 cap=cv2.VideoCapture(str(MASTER))
 fps=float(cap.get(cv2.CAP_PROP_FPS));n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
 w=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));h=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
 if not 20<=fps<=60 or not 4.75<n/fps<5.5 or (w,h)!=(720,1280):
  raise RuntimeError("BAD_VIDU_MOVING_OUTPUT_LENGTH_OR_FORMAT")
 raw_input=cv2.imread(str(PHOTO))
 original_gray=cv2.resize(cv2.cvtColor(raw_input,cv2.COLOR_BGR2GRAY),(72,128)).astype("float32")
 writer=subprocess.Popen(["ffmpeg","-nostdin","-y","-v","error","-f","rawvideo","-pix_fmt","bgr24",
  "-s","720x1280","-r",str(fps),"-i","-","-an","-c:v","libx264","-crf","18",
  "-preset","veryfast","-pix_fmt","yuv420p","-movflags","+faststart",str(COLOR)],
  stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 stats=[];first_corr=None;prev=None
 try:
  for i in range(n):
   ok,frame=cap.read()
   if not ok:raise RuntimeError("TRUNCATED_VIDU_GENERATED_FILM")
   if i==0:
    curr=cv2.resize(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),(72,128)).astype("float32")
    first_corr=float(np.corrcoef(curr.ravel(),original_gray.ravel())[0,1])
    if not np.isfinite(first_corr) or first_corr<.65:
     raise RuntimeError("GENERATED_FIRST_FRAME_DEPARTS_FROM_ACTUAL_HISTORICAL_PHOTO")
   t=i/fps
   # Original AI VIDEO is fully colored for ALL five seconds, so this
   # desaturates only its first second and DOES NOT create or warp any motion.
   g=cv2.cvtColor(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR)
   a=max(0,min(1,(t-.04)/.96));a=a*a*(3-2*a)
   out=cv2.addWeighted(g,1-a,frame,a,0)
   writer.stdin.write(out.tobytes())
   if i%max(1,round(.45*fps))==0:
    small=cv2.resize(cv2.cvtColor(out,cv2.COLOR_BGR2GRAY),(160,284))
    delta=None if prev is None else float(np.mean(np.abs(small.astype("float32")-prev.astype("float32"))))
    stats.append({"second":round(t,2),"median_saturation":round(float(np.median(cv2.cvtColor(out,cv2.COLOR_BGR2HSV)[:,:,1])),2),
    "motion_grayscale_change":None if delta is None else round(delta,3)})
    prev=small
 finally:
  cap.release();writer.stdin.close()
  err=writer.stderr.read().decode(errors="replace")
  if writer.wait()!=0:raise RuntimeError("VIDU_COLOR_REVEAL_ENCODER_FAILED "+err[-700:])
 cmd(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(COLOR),"-f","null","-"],150)
 after=[s for s in stats if 1.25<=s["second"]<=4.5]
 vivid=bool(after) and sum(x["median_saturation"]>=13 for x in after)>=max(3,len(after)*.7)
 motion=sum((x["motion_grayscale_change"] or 0)>=.9 for x in after)
 return {"first_frame_corr_to_real_restoration":round(first_corr,3),"color_after_1s":vivid,
         "motion_after_1s":motion>=max(3,len(after)//2),
         "motion_intervals_above_threshold":motion,
         "samples":stats,"source_original_video_sha256":sha(MASTER),
         "full_decode":True,"original_motion_preserved":True}
def main():
 R.mkdir(parents=True,exist_ok=True)
 valid_input()
 before=balance()
 if not any(x["remaining"]>=16 for x in before):raise RuntimeError("NOT_ENOUGH_API_CREDITS_FOR_AUTHORIZED_SINGLE_CLIP")
 doc={"status":"reserved_prebill","paid_post_count":0,"source_photo_sha256":sha(PHOTO),
  "prompt_sha256":hashlib.sha256(PROMPT.encode()).hexdigest(),
  "user_authorization":"new 4+1 San Francisco historical video with one Vidu insert",
  "max_credits":16,"model":"viduq2-pro-fast","duration":5,"resolution":"720p",
  "source":"Miles Brothers real 1906 film at t=43s", "created_at_utc":int(time.time())}
 # Only this reservation allows the single paid call.
 reserve(doc)
 req={"model":"viduq2-pro-fast",
    "images":["data:image/jpeg;base64,"+base64.b64encode(PHOTO.read_bytes()).decode()],
    "prompt":PROMPT,"duration":5,"resolution":"720p","off_peak":False,"audio":False,"is_rec":False,
    "seed":1906,"payload":"V86_SF1906_SOURCE_43S_SINGLE_PAID_ONE"}
 try:submitted=api("/ent/v2/img2video",req,method="POST",timeout=75)
 except Exception as e:
  doc.update(status="submission_unknown_DO_NOT_RETRY",paid_post_count=1,error_type=type(e).__name__)
  update(doc)
  raise RuntimeError("BILLABLE_POST_AMBIGUOUS_DO_NOT_RETRY") from e
 task=str(submitted.get("task_id") or "")
 charge=submitted.get("credits")
 if not task:
  doc.update(status="submitted_missing_id_DO_NOT_RETRY",paid_post_count=1)
  update(doc);raise RuntimeError("VIDU_ACCEPTED_BUT_NO_TASK_ID")
 doc.update(status="accepted",task_id=task,credits_reported=charge,paid_post_count=1)
 update(doc)
 print("V86_ONE_NEW_VIDU_TASK_ACCEPTED",task,"REPORT_CREDITS",charge,flush=True)
 if type(charge) not in (float,int) or charge>16:raise RuntimeError("VIDEO_CREDIT_COST_EXCEEDS_16_STOP")
 response=None
 for k in range(55):
  time.sleep(12)
  try:res=api(f"/ent/v2/tasks/{task}/creations",timeout=35)
  except Exception as exc:
   print("V86_FREE_POLL_ERROR",type(exc).__name__,flush=True);continue
  state=res.get("state")
  if k%4==0:print("V86_VIDU_POLL",k,state,flush=True)
  if state in ("failed","cancelled"):
   doc.update(status=state);update(doc);raise RuntimeError("VIDER_TASK_FAILED_NO_RETRY")
  if state=="success":
   response=res;break
 if response is None:
  doc.update(status="pending_poll_timeout_no_second_post");update(doc)
  raise RuntimeError("VIDU_PENDING_AFTER_POLL_NO_SECOND_PAID_REQUEST")
 rows=response.get("creations") or []
 url=rows[0].get("url") if rows else None
 if not isinstance(url,str) or not url.startswith("https://"):raise RuntimeError("COMPLETED_TASK_HAS_NO_MP4_URL")
 req=urllib.request.Request(url,headers={"User-Agent":"LaStoriaRivive-V86/1"})
 with urllib.request.urlopen(req,timeout=135) as web,open(MASTER,"wb") as fd:
  while ch:=web.read(1<<20):
   fd.write(ch)
   if fd.tell()>80000000:raise RuntimeError("VIDU_VIDEO_TOO_LARGE")
 if MASTER.stat().st_size<10000:raise RuntimeError("VIDER_ORIGINAL_EMPTY")
 cmd(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(MASTER),"-f","null","-"],140)
 doc.update(status="video_retrieved",vidu_original_sha256=sha(MASTER),provider_reported_credits=response.get("credits",charge))
 update(doc)
 post=colored_motion()
 after=balance()
 private={"provider_state":"success","task_id":task,"paid_post_count":1,
   "provider_credits":response.get("credits",charge),"balance_before":before,"balance_after":after,
   "source_photo_sha256":sha(PHOTO),"vidu_original_sha256":sha(MASTER),
   "processed_mp4_sha256":sha(COLOR),"color_transition_per_frame":True,
   "motion_qa":post,"artistic_review":"PENDING_HUMAN",
   "source_provenance":"Miles Brothers, A Trip Down Market Street Before the Fire, April 14 1906",
   "source_public_domain":"https://www.loc.gov/item/00694408/"}
 writej(R/"SF1906_VIDU_SINGLE_TASK_QA_PRIVATE.json",private)
 # Store only safe technical proof in public repo ledger, never account balance or secret.
 doc.update(status="video_downloaded_and_qa",vidu_original_sha256=sha(MASTER),processed_sha256=sha(COLOR),
   validated_motion=post["motion_after_1s"],validated_color=post["color_after_1s"])
 update(doc)
 print("V86_ONE_REAL_VIDU_VIDEO_FINISHED",task,"color_after_1s",post["color_after_1s"],
       "moving_after_1s",post["motion_after_1s"],"sha256",sha(COLOR),flush=True)
if __name__=="__main__":main()
