#!/usr/bin/env python3
"""V84: up to FIVE user-authorized real Vidu img2video trials, one at a time.
5 x Q2 Pro Fast 5s 720p, <=16 credits per accepted task, <=80 credits expected.
No paid retries, no parallel generations, never post secrets/balances to public repo.
Every paid POST is preceded by a permanent unique ledger reservation on GitHub.
Technical draft previews only. Human semantic QA is necessary before publication.
"""
from __future__ import annotations
import base64,hashlib,json,os,pathlib,subprocess,sys,time,urllib.request,urllib.error,zipfile
import cv2
import numpy as np
from PIL import Image

REPO=os.getenv("GITHUB_REPOSITORY","GGIANLUCAA/Tra-le-pagine-")
KEY=os.getenv("VIDU_API_KEY","")
OUT=pathlib.Path("output/storia_vidu_v84_five_tests")
MEDIA=OUT/"inputs"
OUT.mkdir(parents=True,exist_ok=True)
MODEL="viduq2-pro-fast"
DURATION=5
RESOLUTION="720p"
MAX_CREDITS_PER_CLIP=16
MAX_TOTAL=80
FP="20261029_V84_5_TESTS"
SEED=190018

SPECS=[
 {"id":"01_TRAM_CAMERA_FISSA","image":"FOTO_AI_RICOSTRUITA_04.png","kind":"1918 tram/people", "motion":"locked",
  "prompt":"One continuous documentary shot from this exact color-restored archival Paris street photograph. The vintage electric tram slowly rolls forward along its original rails and the pedestrians walk at natural human speed; tram wheels stay wheels, tram remains one rigid mechanical vehicle, buildings remain fixed. Tripod camera fully locked off; eye-level framing stays identical. Realistic coordinated locomotion, small wind movement in clothing, subtle depth motion, crisp natural details. Preserve exact number and identities of visible people. DO NOT change historical signs, clothes or geometry; no zoom, no pan, no morphs, no extra humans or limbs, no freeze-frame or slideshow. Every second contains real object movement."},
 {"id":"02_NEWSSTAND_HANDS","image":"FOTO_AI_RICOSTRUITA_01.png","kind":"1918 street newspaper stand","motion":"human gesture",
  "prompt":"The same Paris newsstand from the input archival color photograph comes alive as uninterrupted realistic live footage. Camera is fixed at the exact source viewpoint, a customer reaches for one newspaper while the newspaper seller adjusts a single paper, natural tiny head motion, real cloth fabric reacting gently, neighboring customers move subtly in place. No changes to the identities, faces, hats, newspaper count, storefront architecture, or camera lens. Human hands with correct fingers and grip; no disintegrating papers or letters, no object-person morph, no new people, no rubber limbs, no camera zoom, no artificial freeze. Full-color continuous live-action movement throughout all five seconds."},
 {"id":"03_STATION_PEDESTRIANS","image":"FOTO_AI_RICOSTRUITA_02.png","kind":"1918 station arrival","motion":"walking crowd",
  "prompt":"Animate the exact same early-20th-century Paris station entrance color-restored photograph into a credible 5-second continuous historical documentary shot. The nearest adult subtly shifts weight then walks one deliberate step, other people pass naturally behind at their existing depth and positions, fabric and luggage respond to real gravity. Camera on stationary tripod, no cut, no reframing, no dolly, no zoom. Keep same people, ages, clothes, hats, luggage, architecture and storefront details. Hands, shoes and faces anatomically stable, no new characters, no multiplied body parts, no object becoming human. Real continuous natural color motion throughout."},
 {"id":"04_CINEMA_CROWD","image":"FOTO_AI_RICOSTRUITA_03.png","kind":"1918 cinema exterior","motion":"moving crowd",
  "prompt":"The EXACT color-restored still of the historic Paris cinema and the crowd begins naturally moving in the same camera composition. Vintage moviegoers walk slowly past the entrance, a woman turns her head slightly, hats and coat fabric respond naturally, passers-by keep their identities and plausible physical trajectories. The cinema signage, marquee, buildings, lamps and rails stay architecture and lettering remains stable. Camera completely fixed without zoom, pan, or shake. One uninterrupted 5-second color documentary shot, no still image pans, no extra faces, no deforming letters, no people morphing into objects or each other, anatomically correct feet, hands, realistic light."},
 {"id":"05_1900_WALKWAY_COLOR_MOTION","image":"END_MODERN.jpg","kind":"1900 moving walkway benchmark","motion":"moving walkway",
  "prompt":"Bring this exact restored full-color archival Paris 1900 moving walkway scene to life as genuine continuous realistic video. The old electric moving sidewalk belt slowly transports the existing passengers in their exact historical hats and outfits; railings and supporting columns remain rigid, natural slight head and arm movement, correct mechanical motion, physically consistent shifting shadows. Preserve number and identity of all people, details of machinery, frame geometry and viewpoint. Stationary documentary camera, no push-in, no zoom, no cut and no camera shake. Rich but natural photographic color and coherent real movement for the FULL five seconds. No static frame, no surreal transformations, no false people, no invented architectural elements."}
]
IMAGE_SUBJECTS_HUMAN_VERIFIED={
 "FOTO_AI_RICOSTRUITA_01.png":"NEWSSTAND",
 "FOTO_AI_RICOSTRUITA_02.png":"STATION",
 "FOTO_AI_RICOSTRUITA_03.png":"CINEMA",
 "FOTO_AI_RICOSTRUITA_04.png":"TRAM",
 "END_MODERN.jpg":"MOVING_WALKWAY"
}
EXPECTED_SUBJECTS={"01_TRAM_CAMERA_FISSA":"TRAM","02_NEWSSTAND_HANDS":"NEWSSTAND",
"03_STATION_PEDESTRIANS":"STATION","04_CINEMA_CROWD":"CINEMA",
"05_1900_WALKWAY_COLOR_MOTION":"MOVING_WALKWAY"}
# Subject labels were manually checked against all FIVE source images. Strict mapping
# protects future paid runs from the prompt/image mismatch discovered during V84 QA.

KNOWN_SHA={"FOTO_AI_RICOSTRUITA_01.png":"25070cfd5aa0e38585c6b582b7cdade10a7aeb8154c4983f94b058da9b128e71",
"FOTO_AI_RICOSTRUITA_02.png":"328af7951bb4b443166143eded5b149aae4f6982713a47420428f79ae291dedf",
"FOTO_AI_RICOSTRUITA_03.png":"8d36d33fec39d6051b2dbed9bc0d5349438522ef1f2756e8bbf91416aeaa6211",
"FOTO_AI_RICOSTRUITA_04.png":"5abf828d87465ad90201da0bb7e0ea3dad1554cd1436aa3f953a36c26f4b9688",
"END_MODERN.jpg":"f9c83984489830b938a90857cf6ea5afe63cc4ab7f16e795f0a0c9c297d90772"}

def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def run(args,timeout=150):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError("LOCAL_COMMAND_FAILED "+str(args[:4])+" "+p.stderr[-750:])
 return p.stdout
def store(path,data):
 pathlib.Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
def api(route,body=None,method="GET",timeout=55):
 if not KEY:raise RuntimeError("VIDU_API_KEY_MISSING")
 req=urllib.request.Request("https://api.vidu.com"+route,
  headers={"Authorization":"Token "+KEY,"Content-Type":"application/json","Accept":"application/json"},
  data=json.dumps(body).encode() if body is not None else None,method=method)
 with urllib.request.urlopen(req,timeout=timeout) as r:return json.loads(r.read(2000000))
def credit_rows(data):
 r=data.get("remains",data.get("remaining_credits"))
 if not isinstance(r,list):raise RuntimeError("VIDU_BALANCE_SCHEMA_CHANGED")
 rows=[{"type":str(x.get("type","credit")),"remaining":x.get("credit_remain")} for x in r if isinstance(x,dict)]
 if not rows or any(type(x["remaining"]) not in (int,float) or x["remaining"]<0 for x in rows):
  raise RuntimeError("INVALID_CREDIT_POOL")
 return rows
def reserve(spec):
 """Permanent ledger BEFORE the paid POST: second execution cannot spend twice."""
 filename=f"queue/vidu_api_attempts/{FP}_{spec['id']}.json"
 dat={"status":"reserved_before_paid_call","test_id":spec["id"],"model":MODEL,"resolution":RESOLUTION,
 "duration_s":DURATION,"max_credits":MAX_CREDITS_PER_CLIP,"user_authorized_5_tests":True,
 "source_photo_sha256":KNOWN_SHA[spec["image"]],
 "prompt_sha256":hashlib.sha256(spec["prompt"].encode()).hexdigest(),
 "created_at_utc":int(time.time()),"paid_post_count":0}
 endpoint=f"repos/{REPO}/contents/{filename}"
 args=["gh","api","-X","PUT",endpoint,"-f",f"message=Reserve one V84 authorized Vidu test {spec['id']}",
       "-f","branch=main","-f","content="+base64.b64encode((json.dumps(dat,sort_keys=True)+"\n").encode()).decode()]
 try:run(args,60)
 except Exception as exc:raise RuntimeError("LEDGER_ALREADY_PRESENT_OR_INACCESSIBLE_DO_NOT_RESUBMIT "+spec["id"]) from exc
 return filename,dat
def update_ledger(filename,dat):
 endpoint=f"repos/{REPO}/contents/{filename}"
 old=json.loads(run(["gh","api",endpoint+"?ref=main"],45))
 payload=base64.b64encode((json.dumps(dat,sort_keys=True)+"\n").encode()).decode()
 run(["gh","api","-X","PUT",endpoint,"-f","message=Update V84 test state",
      "-f","branch=main","-f","sha="+old["sha"],"-f","content="+payload],60)
def input_photo(spec):
 p=MEDIA/spec["image"]
 if not p.exists() or sha(p)!=KNOWN_SHA[spec["image"]]:raise RuntimeError("SOURCE_IMAGE_CHANGED "+spec["image"])
 im=Image.open(p).convert("RGB")
 if im.width<650 or im.height<1000:raise RuntimeError("SOURCE_TOO_LOW_RES")
 im=im.resize((720,1280),Image.Resampling.LANCZOS)
 target=OUT/("INPUT_"+spec["id"]+".jpg");im.save(target,format="JPEG",quality=94,subsampling=0)
 if target.stat().st_size>=9_000_000:raise RuntimeError("BASE64_IMAGE_TOO_LARGE")
 return target
def post_one(spec,balance_before,attempt_index):
 photo=input_photo(spec)
 filename,receipt=reserve(spec)
 request={"model":MODEL,"images":["data:image/jpeg;base64,"+base64.b64encode(photo.read_bytes()).decode()],
          "prompt":spec["prompt"],"duration":DURATION,"resolution":RESOLUTION,"off_peak":False,
          "audio":False,"is_rec":False,"seed":SEED+attempt_index,"payload":FP+"_"+spec["id"]}
 # Exactly ONE POST per paid ledger. Any HTTP or network error stops entire batch,
 # as submission may have succeeded at provider even without response.
 try:submission=api("/ent/v2/img2video",request,"POST",75)
 except Exception as e:
  receipt.update(status="submission_unknown_NEVER_RETRY",paid_post_count=1,error_type=type(e).__name__)
  update_ledger(filename,receipt)
  raise RuntimeError("VIDU_SUBMISSION_AMBIGUOUS_STOP_ALL") from e
 tid=str(submission.get("task_id",""))
 charged=submission.get("credits")
 if not tid:
  receipt.update(status="provider_returned_no_task_id_DO_NOT_RETRY",paid_post_count=1)
  update_ledger(filename,receipt)
  raise RuntimeError("NO_TASK_ID_DO_NOT_RETRY")
 receipt.update(status="accepted",task_id=tid,credits_reported=charged,paid_post_count=1)
 update_ledger(filename,receipt)
 print("V84_ACCEPTED",spec["id"],"TASK",tid,"CREDITS",charged,flush=True)
 if type(charged) not in (int,float) or charged>MAX_CREDITS_PER_CLIP:
  raise RuntimeError("VIDER_BILLING_ABOVE_AUTHORIZED_PER_CLIP_STOP_ALL")
 # Poll GET only: never paid POST twice
 for poll in range(45):
  time.sleep(10)
  try:state=api(f"/ent/v2/tasks/{tid}/creations",timeout=35)
  except Exception as e:
   print("V84_POLL_RECOVERABLE",spec["id"],type(e).__name__,flush=True);continue
  status=state.get("state")
  if poll%3==0:print("V84_POLL",spec["id"],poll,status,flush=True)
  if status in ("failed","cancelled"):
   receipt.update(status=status,provider_credits=state.get("credits"))
   update_ledger(filename,receipt)
   raise RuntimeError("VIDU_TASK_FAILED_NO_RETRY_"+spec["id"])
  if status!="success":continue
  items=state.get("creations") or []
  url=items[0].get("url") if items else None
  if not isinstance(url,str) or not url.startswith("https://"):
   receipt.update(status="completed_without_video_link")
   update_ledger(filename,receipt)
   raise RuntimeError("VIDU_RETURNED_NO_MP4")
  dest=OUT/(spec["id"]+"_VIDU_ORIGINAL.mp4")
  req=urllib.request.Request(url,headers={"User-Agent":"TraLePagine-V84/1.0"})
  with urllib.request.urlopen(req,timeout=130) as f,open(dest,"wb") as o:
   while block:=f.read(1<<20):
    o.write(block)
    if o.tell()>75_000_000:raise RuntimeError("VIDU_VIDEO_OVERSIZED")
  if dest.stat().st_size<10000:raise RuntimeError("VIDU_VIDEO_EMPTY")
  run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(dest),"-f","null","-"],130)
  receipt.update(status="video_verified",provider_credits=state.get("credits"),original_mp4_sha256=sha(dest),
      bytes=dest.stat().st_size)
  update_ledger(filename,receipt)
  return dest,receipt
 receipt.update(status="pending_poll_timeout_NO_NEW_POST")
 update_ledger(filename,receipt)
 raise RuntimeError("VIDU_POLL_TIMED_OUT_STOP_BATCH_NO_RETRY_"+spec["id"])
def style_bw_to_fullcolor(original,export,fade_seconds=1.0):
 cap=cv2.VideoCapture(str(original))
 fps=float(cap.get(cv2.CAP_PROP_FPS));n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
 w=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));h=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
 if not (20<=fps<=60 and 4.7<=n/fps<=5.4 and w>=500 and h>=850):
  raise RuntimeError("VIDU_OUTPUT_GEOMETRY_OR_TIMING_INVALID")
 p=subprocess.Popen(["ffmpeg","-nostdin","-y","-v","error","-f","rawvideo","-pix_fmt","bgr24","-s","720x1280",
   "-r",str(fps),"-i","-","-an","-c:v","libx264","-preset","veryfast","-crf","18",
   "-pix_fmt","yuv420p","-movflags","+faststart",str(export)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 prev_gray=None;changes=[];sats=[];orig_sats=[];first=None;last=None
 try:
  for k in range(n):
   ok,raw=cap.read()
   if not ok:raise RuntimeError("BAD_VIDU_FRAME_STREAM")
   frame=cv2.resize(raw,(720,1280),interpolation=cv2.INTER_AREA)
   if first is None:first=frame
   last=frame
   gray=cv2.cvtColor(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR)
   t=k/fps
   a=np.clip((t-.05)/max(.01,fade_seconds-.05),0,1)
   a=a*a*(3-2*a)
   out=cv2.addWeighted(gray,1-float(a),frame,float(a),0)
   p.stdin.write(out.tobytes())
   if k%max(1,round(fps*.5))==0:
    g=cv2.resize(cv2.cvtColor(out,cv2.COLOR_BGR2GRAY),(180,320),interpolation=cv2.INTER_AREA)
    mot=float(np.mean(np.abs(g.astype("float32")-prev_gray.astype("float32")))) if prev_gray is not None else None
    if mot is not None:changes.append({"second":round(t,2),"mean_luma_delta":round(mot,3)})
    prev_gray=g
    sat=float(np.median(cv2.cvtColor(out,cv2.COLOR_BGR2HSV)[:,:,1]))
    sats.append({"second":round(t,2),"median_sat":round(sat,2)})
    orig_sats.append({"second":round(t,2),"median_sat":round(float(np.median(cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)[:,:,1])),2)})
 finally:
  cap.release()
  p.stdin.close()
  err=p.stderr.read().decode(errors="replace")
  if p.wait():raise RuntimeError("COLOR_REVEAL_ENCODING_FAILED "+err[-900:])
 run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(export),"-f","null","-"],125)
 color=[x["median_sat"] for x in sats if 1.1<=x["second"]<=4.5]
 move=[x["mean_luma_delta"] for x in changes if x["second"]>=1.0]
 firstgray=cv2.resize(cv2.cvtColor(first,cv2.COLOR_BGR2GRAY),(120,214)).astype("float32").ravel()
 lastgray=cv2.resize(cv2.cvtColor(last,cv2.COLOR_BGR2GRAY),(120,214)).astype("float32").ravel()
 drift=float(np.corrcoef(firstgray,lastgray)[0,1])
 return {"color_reveal":"source-preserving per-frame grayscale to full-color at t <=1.00sec, NO optical-flow color transfer",
         "frames":n,"fps":fps,"duration_s":n/fps,"first_last_gray_corr":round(drift,4),
         "color_after_1s":min(color)>17 if color else False,
         "moving_after_1s":sum(x>=1 for x in move)>=max(3,len(move)//2),
         "motion_luma_delta_samples":changes,"saturation_samples":sats,
         "source_saturation_samples":orig_sats,"original_mp4_sha256":sha(original),
         "reveal_mp4_sha256":sha(export),"human_semantic_review":"PENDING",
         "technical_pass":len(move)>=4 and min(color)>17 if color else False}
def main():
 if not KEY:raise RuntimeError("Vidu API secret absent")
 if len(SPECS)!=5 or len({x["id"] for x in SPECS})!=5:raise RuntimeError("NOT_FIVE_UNIQUE_EXPERIMENTS")
 for spec in SPECS:
  if IMAGE_SUBJECTS_HUMAN_VERIFIED[spec["image"]]!=EXPECTED_SUBJECTS[spec["id"]]:
   raise RuntimeError("SOURCE_SEMANTIC_MISMATCH_STOP_BEFORE_BILLING "+spec["id"])
 for s in SPECS:
  if not (MEDIA/s["image"]).exists() or sha(MEDIA/s["image"])!=KNOWN_SHA[s["image"]]:
   raise RuntimeError("PRECHECK_IMAGES_MISSING_OR_CHANGED "+s["image"])
 starting=credit_rows(api("/ent/v2/credits"))
 if not any(x["remaining"]>=MAX_TOTAL for x in starting):
  raise RuntimeError("NOT_ENOUGH_IN_ONE_CREDIT_POOL_FOR_FIVE_TESTS")
 manifest={"schema":"V84-5-clips-test","user_preapproved":True,
           "planned_credits_max":MAX_TOTAL,"model":MODEL,"duration_each_s":DURATION,
           "source_material":"existing genuine historical film frame reconstructions; AI restoral interpretive",
           "before":starting,"after":None,"completed":[],"paid_post_count":0,
           "never_parallel":True,"no_paid_retry":True,"public_github_release_preview_only":True,
           "website_uploaded":False,"social_published":False,"human_artistic_review":"PENDING"}
 full=OUT/"CREDIT_REPORT_PRIVATE.json"
 store(full,manifest)
 for i,spec in enumerate(SPECS,1):
  print("V84_BEGIN",i,spec["id"],flush=True)
  before=credit_rows(api("/ent/v2/credits"))
  if not any(x["remaining"]>=MAX_CREDITS_PER_CLIP for x in before):
   raise RuntimeError("BALANCE_BELOW_SINGLE_CLIP_BUDGET")
  original,receipt=post_one(spec,before,i)
  final=OUT/(spec["id"]+"_BW_TO_COLOR_1S_AND_MOVING.mp4")
  qa=style_bw_to_fullcolor(original,final)
  after=credit_rows(api("/ent/v2/credits"))
  report={"id":spec["id"],"source":spec["kind"],"motion_mode":spec["motion"],"image":spec["image"],
          "task_id":receipt["task_id"],"provider_reported_credits":receipt.get("provider_credits",receipt.get("credits_reported")),
          "balance_before":before,"balance_after":after,"qa":qa,
          "original_vidu_filename":original.name,"final_processed_filename":final.name,
          "semantic_review":"PENDING_HUMAN","no_social_publication":True}
  store(OUT/(spec["id"]+"_QA_PRIVATE.json"),report)
  manifest["completed"].append(report)
  manifest["paid_post_count"]=len(manifest["completed"])
  manifest["after"]=after
  store(full,manifest)
  print("V84_FINISHED",spec["id"],"actual_credits",receipt.get("provider_credits"),"technical_pass",qa["technical_pass"],flush=True)
  if not qa["technical_pass"]:
   print("V84_FAIL_CLOSED_TEST_REVIEW_CONTINUES: new image is usable only if manual QA approves",flush=True)
 # Export public-safe QC with NO private credits balance.
 public={"schema":"V84-5-clips-test","total_clips":len(manifest["completed"]),
         "spend_reported_total":sum(float(x["provider_reported_credits"] or 0) for x in manifest["completed"]),
         "status":"TECHNICAL_PREVIEW_ARTISTIC_QA_REQUIRED",
         "historical_periods":["Paris ~1900","Paris ~1918"],"social_published":False,
         "new_videos":[{"id":r["id"],"task_id":r["task_id"],"motion_mode":r["motion_mode"],
                         "mp4":r["final_processed_filename"],"qa":r["qa"],
                         "source_photo":r["image"]} for r in manifest["completed"]]}
 store(OUT/"TEST_REPORT_FOR_REVIEW.json",public)
 with zipfile.ZipFile(OUT/"FIVE_VIDU_TESTS_ANDROID.zip","w",zipfile.ZIP_DEFLATED) as z:
  for r in manifest["completed"]:
   for n in (r["final_processed_filename"],r["original_vidu_filename"]):z.write(OUT/n,n)
  z.write(OUT/"TEST_REPORT_FOR_REVIEW.json","TEST_REPORT_FOR_REVIEW.json")
 with zipfile.ZipFile(OUT/"FIVE_VIDU_TESTS_ANDROID.zip") as z:
  if z.testzip():raise RuntimeError("TEST_ZIP_CORRUPTED")
 print("V84_ALL_FIVE_TESTS_COMPLETED",len(manifest["completed"]),"SPEND_REPORTED",public["spend_reported_total"],flush=True)

if __name__=="__main__":main()
