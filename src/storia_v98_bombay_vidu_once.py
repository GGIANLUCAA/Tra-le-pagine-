#!/usr/bin/env python3
"""One user-authorized Vidu Q2 Pro Fast clip for V98 BOMBAY 1929.
SCENE 08 from a SHA-verified restored historical frame (full realistic heads).
Reserve a unique paid ledger before ONE POST; GET-only polling, NO paid retry.
"""
import base64,hashlib,json,os,pathlib,subprocess,time,urllib.request
import numpy as np, cv2
ROOT=pathlib.Path("output/storia_bombay_v98")
PHOTO=ROOT/"RESTORATION_FINAL_08.jpg"
SOURCE=ROOT/"SOURCE_BW_08.png"
ORIG=ROOT/"VIDU_BOMBAY_1929_08_ORIGINAL.mp4"
COLOR=ROOT/"VIDU_BOMBAY_1929_08_BW_COLOR_MOVING.mp4"
REPORT=ROOT/"V98_VIDU_QA_PRIVATE.json"
LEDGER="queue/vidu_api_attempts/20261030_V98_BOMBAY_1929_PEOPLE_08_SINGLE.json"
REPO=os.environ.get("GITHUB_REPOSITORY","GGIANLUCAA/Tra-le-pagine-")
KEY=os.environ.get("VIDU_API_KEY","")
PROMPT=(
 "An authentic continuous documentary-style close-up of the EXACT same group of real adult men shown "
 "in this faithfully reconstructed full-color historical Bombay 1929 photograph. "
 "The man at right-front in blue waistcoat turns his eyes toward the camera and makes a very subtle real smile; "
 "the moustached man in pale shirt and white cap at center naturally blinks and nods almost imperceptibly; "
 "the man on left shifts his shoulder slightly and another man behind breathes naturally. "
 "Physical micro-expressions, realistic blinking, fine facial skin texture, cloth reacting to natural gravity, "
 "very subtle human movements THROUGHOUT ALL FIVE SECONDS without freeze or slideshow. "
 "Locked eye-level camera, NO CAMERA MOVEMENT and no zoom. "
 "PRESERVE EXACTLY ALL existing faces, moustaches, caps, ages, ethnic features, clothing colors, hands, "
 "body count, body positions, held circular object, buildings and historical background. "
 "NO new face, NO invented hand or extra fingers, NO smile stretching, NO object turning into person, "
 "NO plastic wax skin, NO clothes changing, NO scene or lighting cut, NO added modern objects, "
 "NO artificial sepia tint. Natural clean full-color live-action motion, genuine human-scale physics."
)
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for x in iter(lambda:f.read(1<<20),b""):h.update(x)
 return h.hexdigest()
def cmd(a,timeout=90):
 x=subprocess.run(a,capture_output=True,text=True,timeout=timeout)
 if x.returncode:raise RuntimeError("CMD_FAIL "+str(a[:5])+" "+x.stderr[-700:])
 return x.stdout
def api(path,payload=None,method="GET",timeout=65):
 if not KEY:raise RuntimeError("VIDU_SECRET_NOT_BOUND")
 r=urllib.request.Request("https://api.vidu.com"+path,method=method,
  data=json.dumps(payload).encode() if payload is not None else None,
  headers={"Authorization":"Token "+KEY,"Content-Type":"application/json","Accept":"application/json"})
 with urllib.request.urlopen(r,timeout=timeout) as resp:return json.loads(resp.read(1200000))
def balance():
 r=api("/ent/v2/credits").get("remains")
 if not isinstance(r,list):raise RuntimeError("NO_TRUSTED_CREDIT_BALANCE_SCHEMA")
 vals=[v.get("credit_remain") for v in r if isinstance(v,dict)]
 if not vals or any(type(v) not in (float,int) for v in vals):raise RuntimeError("BAD_CREDIT_BALANCE")
 return vals
def ledger_create(data):
 payload=base64.b64encode((json.dumps(data,sort_keys=True)+"\n").encode()).decode()
 try:
  cmd(["gh","api","-X","PUT",f"repos/{REPO}/contents/{LEDGER}","-f","branch=main",
      "-f","message=Reserve ONE user-authorized V98 Bombay 1929 Vidu clip",
      "-f","content="+payload],60)
 except Exception as e:raise RuntimeError("LEDGER_ALREADY_EXISTS_OR_UNAVAILABLE_NO_PAID_POST") from e
def ledger_update(data):
 route=f"repos/{REPO}/contents/{LEDGER}"
 old=json.loads(cmd(["gh","api",route+"?ref=main"],45))
 payload=base64.b64encode((json.dumps(data,sort_keys=True)+"\n").encode()).decode()
 cmd(["gh","api","-X","PUT",route,"-f","branch=main","-f","sha="+old["sha"],
   "-f","message=Update existing Bombay Vidu task without another POST",
   "-f","content="+payload],60)
def metadata_check():
 m=json.loads((ROOT/"V98_FIVE_REAL_PHOTOS_QA.json").read_text())
 if m.get("all_five_generated_image_to_image") is not True:raise RuntimeError("FOUR_PHOTOS_NOT_REAL_IMAGE_TO_IMAGE")
 if {p["scene"] for p in m["photographic_images"]}!={2,4,5,7,8}:raise RuntimeError("WRONG_SOURCE_SHOT_SET")
 for rec in m["photographic_images"]:
  file=ROOT/f"RESTORATION_FINAL_{rec['scene']:02d}.jpg"
  if not file.exists() or sha(file)!=rec["new_i2i_photo_sha256"]:
   raise RuntimeError("PHOTO_SOURCE_IDENTITY_SHA_MISMATCH "+str(rec["scene"]))
 a=next(p for p in m["photographic_images"] if p["scene"]==8)
 if a.get("source_to_output_corr",0)<.97:raise RuntimeError("VIDU_ANCHOR_NOT_FAITHFUL")
 if not SOURCE.is_file() or sha(SOURCE)!=a["original_sha256"]:raise RuntimeError("ORIGINAL_REAL_FILM_FREEZE_FRAME_CHANGED")
 if cv2.imread(str(PHOTO)).shape[:2]!=(1280,720):raise RuntimeError("VIDU_BAD_ANCHOR_DIMENSIONS")
 return m
def gray(frame):
 return cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
def motion_video():
 cap=cv2.VideoCapture(str(ORIG))
 fps=float(cap.get(cv2.CAP_PROP_FPS));n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
 size=(int(cap.get(3)),int(cap.get(4)))
 if size!=(720,1280) or not 20<=fps<=60 or not 4.75<n/fps<5.4:
  raise RuntimeError("VIDU_GENERATED_VIDEO_NOT_REAL_FIVE_SECONDS_VERTICAL")
 source_g=cv2.resize(gray(cv2.imread(str(SOURCE))),(120,214)).astype(np.float32).ravel()
 outp=subprocess.Popen(["ffmpeg","-nostdin","-y","-v","error","-f","rawvideo","-pix_fmt","bgr24",
   "-s","720x1280","-r",str(fps),"-i","-","-an","-c:v","libx264","-crf","18","-preset","veryfast",
   "-pix_fmt","yuv420p","-movflags","+faststart",str(COLOR)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 firstcorr=0;prev=None;sample=[]
 try:
  for idx in range(n):
   ok,f=cap.read()
   if not ok:raise RuntimeError("TRUNCATED_VIDU_FRAMES")
   if idx==0:
    anchor=cv2.resize(gray(f),(120,214)).astype(np.float32).ravel()
    firstcorr=float(np.corrcoef(source_g,anchor)[0,1])
    if firstcorr<.80:raise RuntimeError(f"FIRST_GENERATED_FRAME_LOSES_REAL_SOURCE_FIDELITY:{firstcorr:.3f}")
   t=idx/fps
   # Vidu produced a FULL COLOR live-motion movie; perform an early single-shot
   # desaturation reveal, not an optical-flow color propagation/ghost.
   hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
   hsv[:,:,1]=np.clip(hsv[:,:,1].astype(np.float32)*.88,0,255).astype("uint8")
   graded=cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
   mono=cv2.cvtColor(gray(graded),cv2.COLOR_GRAY2BGR)
   alpha=max(0,min(1,(t-.03)/.99));alpha=alpha*alpha*(3-2*alpha)
   frame=cv2.addWeighted(mono,1-alpha,graded,alpha,0)
   outp.stdin.write(frame.tobytes())
   if idx%max(1,round(.4*fps))==0:
    small=cv2.resize(gray(frame),(180,320))
    change=0 if prev is None else float(np.mean(np.abs(small.astype(np.float32)-prev.astype(np.float32))))
    s=float(np.median(cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)[:,:,1]))
    sample.append({"time_s":round(t,2),"motion_luma_change":round(change,2),"median_saturation":round(s,2)})
    prev=small
 finally:
  cap.release();outp.stdin.close()
  err=outp.stderr.read().decode(errors="replace")
  if outp.wait():raise RuntimeError("VIDU_REVEAL_ENCODER_ERROR "+err[-700:])
 cmd(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(COLOR),"-f","null","-"],150)
 active=[s for s in sample if s["time_s"]>1.1]
 moving=sum(s["motion_luma_change"]>=.8 for s in active)
 vivid=sum(s["median_saturation"]>=13 for s in active)
 return {"first_frame_corr_with_exact_original_bw":round(firstcorr,3),
         "moving_color_after_1s":moving>=max(3,len(active)//2),
         "color_after_1s":vivid>=max(3,len(active)//2),
         "sample":sample,"motion_examples":moving,
         "colored_frames_reused_from_real_Vidu_video":True,
         "photo_animation_ken_burns":False,
         "full_semantic_human_review":"PENDING"}
def main():
 m=metadata_check()
 before=balance()
 if not any(v>=16 for v in before):raise RuntimeError("NOT_ENOUGH_PREPAID_VIDU_CREDITS_16")
 ledger={"scene":"Bombay 1929 #8 original 399.2s","status":"reserved_pre_POST",
   "source_photo_sha256":sha(PHOTO),"source_original_bw_sha256":sha(SOURCE),
   "source_photo_model":"Finegrain real image-to-image","prompt_sha256":hashlib.sha256(PROMPT.encode()).hexdigest(),
   "model":"viduq2-pro-fast","resolution":"720p","duration_s":5,
   "single_clip_user_authorized_under_V94":True,"maximum_prepaid_credits":16,
   "paid_post_count":0,"created_unix":int(time.time())}
 ledger_create(ledger)
 post={"model":"viduq2-pro-fast",
       "images":["data:image/jpeg;base64,"+base64.b64encode(PHOTO.read_bytes()).decode()],
       "prompt":PROMPT,"duration":5,"resolution":"720p","off_peak":False,"audio":False,
       "is_rec":False,"seed":192908,"payload":"V98_BOMBAY_1929_ONE_FACE_GROUP_SHOT_08"}
 try:res=api("/ent/v2/img2video",post,method="POST",timeout=75)
 except Exception as exc:
  ledger.update(status="unknown_billed_call_DO_NOT_RETRY",paid_post_count=1,error_type=type(exc).__name__)
  ledger_update(ledger);raise RuntimeError("PAID_CALL_AMBIGUOUS_STOP_NO_RETRY") from exc
 task=str(res.get("task_id") or "");credits=res.get("credits")
 ledger.update(status="accepted" if task else "no_task_id_NO_RETRY",paid_post_count=1,
               task_id=task,credits_reported=credits)
 ledger_update(ledger)
 print("V98_BOMBAY_VIDU_TASK_ACCEPTED",task,"credits",credits,flush=True)
 if not task or type(credits) not in (int,float) or credits>16:
  raise RuntimeError("PROVIDER_BILLING_OUTSIDE_USER_V94_CAP_DO_NOT_RETRY")
 result=None
 for k in range(60):
  time.sleep(10)
  try:state=api("/ent/v2/tasks/"+task+"/creations",timeout=35)
  except Exception as e:
   if k%8==0:print("VIDU_FREE_GET_POLL_EXCEPTION",type(e).__name__,flush=True)
   continue
  if k%5==0:print("VIDU_FREE_GET_TASK",k,state.get("state"),flush=True)
  if state.get("state")=="success":result=state;break
  if state.get("state") in ("failed","cancelled"):
   ledger.update(status=state.get("state"));ledger_update(ledger)
   raise RuntimeError("VIDU_PROVIDER_FAILED_NO_RETRY")
 if result is None:
  ledger.update(status="pending_recover_later_by_GET_ONLY");ledger_update(ledger)
  raise RuntimeError("TASK_STILL_PENDING_NO_SECOND_PAID_POST")
 url=(result.get("creations") or [{}])[0].get("url")
 if not isinstance(url,str) or not url.startswith("https://"):raise RuntimeError("VIDU_TASK_SUCCESS_BUT_NO_REAL_VIDEO_URL")
 req=urllib.request.Request(url,headers={"User-Agent":"LaStoriaRivive-V98/1"})
 with urllib.request.urlopen(req,timeout=140) as obj,open(ORIG,"wb") as f:
  while chunk:=obj.read(1<<20):
   f.write(chunk)
   if f.tell()>80_000_000:raise RuntimeError("VIDU_VIDEO_OVER_SIZE_LIMIT")
 if ORIG.stat().st_size<10_000:raise RuntimeError("VIDU_EMPTY_MP4")
 cmd(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(ORIG),"-f","null","-"],150)
 quality=motion_video()
 after=balance()
 report={"provider_state":"success","task_id":task,"credits_paid":result.get("credits",credits),
    "paid_post_count":1,"model":"viduq2-pro-fast","duration_s":5,
    "input_photo_sha256":sha(PHOTO),"original_historical_frame_sha256":sha(SOURCE),
    "original_generated_MP4_sha256":sha(ORIG),"processed_color_video_sha256":sha(COLOR),
    "motion_QA":quality,"before_credit_pools":before,"after_credit_pools":after,
    "human_visual_review":"PENDING","source":"Bombay historical 1929, scene 8",
    "not_claimed_genuine_color_history":True}
 REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 ledger.update(status="real_video_downloaded",provider_credits=report["credits_paid"],
               original_MP4_sha256=sha(ORIG),color_MP4_sha256=sha(COLOR),
               motion_verified=quality["moving_color_after_1s"])
 ledger_update(ledger)
 print("V98_BOMBAY_VIDU_REAL_MP4",task,"motion",quality["moving_color_after_1s"],
       "color",quality["color_after_1s"],"original_sha",sha(ORIG),flush=True)
 if not quality["moving_color_after_1s"] or not quality["color_after_1s"]:
  raise RuntimeError("V98_REAL_VIDU_QUALITY_GATE_FAILED_AFTER_ONE_GENERATION_NO_PAID_RETRY")
if __name__=="__main__":main()
