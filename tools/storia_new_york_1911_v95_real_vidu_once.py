#!/usr/bin/env python3
"""V95 NEW YORK 1911: actual new historical MP4, one paid source-anchored Vidu 5s insert.
Only ONE POST per immutable ledger, max 16 prepaid credits, no retries. Other scenes
are independently rendered from source-locked neural color stills by V83.
If continuity fails keep output as QA-only, never pretend final.
"""
import base64,hashlib,json,os,pathlib,subprocess,urllib.request,time,zipfile,math,shutil
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
P=pathlib.Path("output/storia_v83_new_york_1911")
OUT=pathlib.Path("output/storia_new_york_1911_v95");OUT.mkdir(parents=True,exist_ok=True)
SRC=P/"AUTHENTIC_1911_FILM_ORIGINAL.webm"
REPO=os.getenv("GITHUB_REPOSITORY","GGIANLUCAA/Tra-le-pagine-")
LEDGER="queue/vidu_api_attempts/NEW_YORK_1911_V95_ONCE_20261030.json"
KEY=os.getenv("VIDU_API_KEY","")
W,H,FPS=720,1280,30
ANCHOR_TIME=325.0;X=960
CLIP=OUT/"VIDU_NEW_YORK_1911_REAL_5S.mp4"
PROMPT=("ONE authentic-looking documentary LIVE ACTION five-second scene showing NEW YORK STREET LIFE IN 1911, "
 "using this exact supplied color-restored source historical movie frame as starting point. "
 "Preserve exactly the same people, number, costumes, vehicles, storefronts, perspective, tram rails, "
 "buildings and camera position. Natural period-appropriate movement from every visible real "
 "person and vehicle, no face morphing, no substitutions, no floating limbs, no new people. "
 "No modern details, no signs or added lettering, no soundtrack, no edit cuts, no stationary zoom, "
 "one camera with gentle realistic movement. Realistic skin texture, photographic clarity, "
 "colors richly vivid but plausible and faithful to the scene.")
def sh(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def call(args,limit=190):
 r=subprocess.run(args,capture_output=True,text=True,timeout=limit)
 if r.returncode:raise RuntimeError("command failed "+r.stderr[-1000:])
 return r.stdout
def write(p,j):p.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
def api(path,body=None,method="GET",timeout=45):
 if not KEY:raise RuntimeError("VIDUOK_MISSING")
 req=urllib.request.Request("https://api.vidu.com"+path,
  data=json.dumps(body).encode() if body is not None else None,
  method=method,headers={"Authorization":"Token "+KEY,"Content-Type":"application/json"})
 with urllib.request.urlopen(req,timeout=timeout) as r:return json.loads(r.read(1500000))
def reserve(doc):
 endpoint=f"repos/{REPO}/contents/{LEDGER}"
 v=base64.b64encode((json.dumps(doc,sort_keys=True)+"\n").encode()).decode()
 try:
  call(["gh","api","-X","PUT",endpoint,"-f","branch=main",
   "-f","message=Reserve ONE prepaid New York 1911 V95 Vidu request max 16",
   "-f","content="+v],70)
 except Exception as e:
  raise RuntimeError("LEDGER_EXISTS_OR_CANNOT_RESERVE_NO_NEW_PAID_REQUEST") from e
def update(doc):
 endpoint=f"repos/{REPO}/contents/{LEDGER}"
 old=json.loads(call(["gh","api",endpoint+"?ref=main"],60))
 v=base64.b64encode((json.dumps(doc,sort_keys=True)+"\n").encode()).decode()
 call(["gh","api","-X","PUT",endpoint,"-f","branch=main","-f","sha="+old["sha"],
  "-f","message=Record actual V95 Vidu state; never retry billable request","-f","content="+v],70)
def photo():
 # Native documentary source 1920x1080, 607px wide portrait crop -> 720x1280.
 cap=cv2.VideoCapture(str(SRC))
 cap.set(cv2.CAP_PROP_POS_MSEC,ANCHOR_TIME*1000)
 ok,fr=cap.read();cap.release()
 if not ok:raise RuntimeError("NO_ANCHOR_SOURCE")
 h,w=fr.shape[:2];cw=round(h*9/16);left=int(max(0,min(w-cw,X-cw/2)))
 crop=fr[:,left:left+cw]
 if cw<560 or len(crop)!=h:raise RuntimeError("ANCHOR_GEOMETRY_BAD")
 orig=cv2.resize(crop,(W,H))
 cv2.imwrite(str(OUT/"AUTHENTIC_VIDU_SOURCE_FRAME.jpg"),orig)
 # Use the SAME DDColor neural semantic model already used for prior 4 scenes.
 import importlib.util
 sp=importlib.util.spec_from_file_location("base","src/storia_v80_new_york_venice.py")
 base=importlib.util.module_from_spec(sp);sp.loader.exec_module(base)
 dd,session,meta=base.load_dd()
 tmp=OUT/"SOURCE_CROP.png";cv2.imwrite(str(tmp),orig)
 colored=base.natural_color(dd,session,tmp)
 hsv=cv2.cvtColor(colored,cv2.COLOR_BGR2HSV)
 hsv[:,:,1]=np.clip(hsv[:,:,1].astype(np.float32)*1.25,0,170).astype(np.uint8)
 color=cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
 target=OUT/"VIDU_SOURCE_LOCKED_NEURAL_COLOR.jpg"
 cv2.imwrite(str(target),color,[cv2.IMWRITE_JPEG_QUALITY,95])
 def g(f):return cv2.resize(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY),(80,140)).ravel()
 corr=float(np.corrcoef(g(orig),g(color))[0,1])
 if not np.isfinite(corr) or corr<.93:raise RuntimeError("SOURCE_COLOR_GEOMETRY_UNSAFE")
 return target,corr
def generate(anchor,corr):
 before=api("/ent/v2/credits")
 remains=before.get("remains",before.get("remaining_credits"))
 values=[v.get("credit_remain") for v in remains] if isinstance(remains,list) else []
 if not any(isinstance(n,(int,float)) and n>=16 for n in values):raise RuntimeError("NOT_ENOUGH_PREPAID_API_CREDITS_FOR_16")
 doc={"episode":"NEW_YORK_1911_V95","status":"reserved_prebill",
  "source_video_sha256":sh(SRC),"anchor_sha256":sh(anchor),
  "anchor_time_s":ANCHOR_TIME,"geometry_correlation":corr,
  "prompt_sha256":hashlib.sha256(PROMPT.encode()).hexdigest(),
  "model":"viduq2-pro-fast","duration_s":5,"resolution":"720p",
  "maximum_credits":16,"prepaid_only":True,"paid_post_count":0,
  "authorization":"User 2026-10-30 expressly authorizes using Vidu credits in La Storia Rivive",
  "before_balance_types":[str(v.get("type","credit")) for v in remains if isinstance(v,dict)]}
 reserve(doc)
 payload={"model":"viduq2-pro-fast",
  "images":["data:image/jpeg;base64,"+base64.b64encode(anchor.read_bytes()).decode()],
  "prompt":PROMPT,"duration":5,"resolution":"720p",
  "off_peak":False,"audio":False,"is_rec":False,
  "seed":1911,"payload":"NYC1911_V95_SINGLE_CREDITED_TASK"}
 try:res=api("/ent/v2/img2video",payload,method="POST",timeout=75)
 except Exception as e:
  doc.update(status="POST_OUTCOME_UNKNOWN_NO_RETRY",paid_post_count=1,error=type(e).__name__)
  update(doc);raise RuntimeError("VIDU_POST_AMBIGUOUS_NO_DUPLICATE") from e
 task=str(res.get("task_id") or "")
 doc.update(status="submitted",paid_post_count=1,task_id=task,reported_credits=res.get("credits"))
 update(doc)
 if not task:raise RuntimeError("VIDU_TASK_WITHOUT_ID_NO_RETRY")
 print("ONE_REAL_VIDU_TASK",task,"credits",res.get("credits"),flush=True)
 if not isinstance(res.get("credits"),(int,float)) or res.get("credits")>16:
  raise RuntimeError("VIDU_PROVIDER_CHARGE_UNVERIFIED_OR_EXCEEDS_CAP")
 finished=None
 for i in range(55):
  time.sleep(10)
  try:j=api("/ent/v2/tasks/"+task+"/creations",timeout=40)
  except Exception as e:
   print("VIDU_FREE_POLL_ERROR",type(e).__name__,flush=True);continue
  if i%5==0:print("VIDU_STATUS",j.get("state"),flush=True)
  if j.get("state") in ("failed","cancelled"):
   doc.update(status=j["state"]);update(doc);raise RuntimeError("GENERATION_FAILED_NO_RETRY")
  if j.get("state")=="success":finished=j;break
 if not finished:
  doc.update(status="PENDING_NO_RETRY");update(doc);raise RuntimeError("VIDU_PENDING_CHECK_EXISTING_TASK_LATER")
 cre=finished.get("creations") or []
 url=cre[0].get("url") if cre else ""
 if not url.startswith("https://"):raise RuntimeError("PROVIDER_NO_VIDEO_URL")
 with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"LaStoriaRiviveV95/1"}),timeout=120) as r,CLIP.open("wb") as f:
  while z:=r.read(1048576):
   f.write(z)
   if f.tell()>90000000:raise RuntimeError("VIDU_CLIP_OVERSIZE")
 call(["ffmpeg","-v","error","-xerror","-i",str(CLIP),"-f","null","-"],100)
 cap=cv2.VideoCapture(str(CLIP))
 nf=cap.get(cv2.CAP_PROP_FRAME_COUNT);fps=cap.get(cv2.CAP_PROP_FPS)
 ok,first=cap.read()
 cap.set(cv2.CAP_PROP_POS_MSEC,2400);ok2,middle=cap.read();cap.release()
 if not(ok and ok2) or not 4.65<=nf/fps<=5.6:raise RuntimeError("VIDU_BAD_CLIP")
 original=cv2.imread(str(anchor))
 def gray(f):
  return cv2.GaussianBlur(cv2.resize(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY),(80,140)),(9,9),0).ravel()
 corr=float(np.corrcoef(gray(first),gray(original))[0,1])
 motion=float(np.mean(np.abs(cv2.resize(first,(90,160)).astype("float32")-cv2.resize(middle,(90,160)).astype("float32"))))
 status="received_needs_artistic_review" if corr>=.68 and motion>=2 else "rejected_visual_mismatch"
 doc.update(status=status,vidu_sha256=sh(CLIP),frame_correlation=round(corr,3),motion_delta=round(motion,2))
 update(doc)
 write(OUT/"VIDU_REAL_RECEIPT.json",doc)
 print("VIDU_CLIP_VISUAL_QA",status,corr,motion,flush=True)
 if status!="received_needs_artistic_review":raise RuntimeError("VIDU_MISMATCH_RETAIN_FOR_REVIEW_NO_FAKE_MASTER")
 return doc
def splice(claim):
 source=P/"LA_STORIA_RIVIVE_NEW_YORK_1911_V83.mp4"
 if not source.is_file():raise RuntimeError("NYC_ARCHIVAL_REEL_NOT_RENDERED")
 # Genuine full-motion Vidu insert at the *scene boundary*, no fabricated zoom.
 # Re-encode once for hard frame-accurate joins and consistent soundtrack.
 old=OUT/"nyc_original.mp4";shutil.copy2(source,old)
 clipfull=OUT/"vidu_normalized.mp4"
 call(["ffmpeg","-y","-v","error","-i",str(CLIP),"-vf",f"scale={W}:{H},fps=30,format=yuv420p",
  "-an","-c:v","libx264","-crf","20","-preset","fast",str(clipfull)],200)
 prefix=OUT/"prefix.mp4";suffix=OUT/"suffix.mp4"
 cut=12.0
 for dst,ss,to in [(prefix,None,cut),(suffix,cut,None)]:
  cmd=["ffmpeg","-y","-v","error"]
  if ss is not None:cmd+=["-ss",str(ss)]
  cmd+=["-i",str(old)]
  if to is not None:cmd+=["-t",str(to)]
  cmd+=["-an","-vf",f"scale={W}:{H},fps=30","-c:v","libx264","-preset","veryfast","-crf","20",str(dst)]
  call(cmd,180)
 playlist=OUT/"video_parts.txt"
 playlist.write_text("\n".join("file '"+p.name+"'" for p in (prefix,clipfull,suffix))+"\n")
 concatenated=OUT/"concatenated.mp4"
 call(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",str(playlist),
   "-c","copy",str(concatenated)],100)
 final=OUT/"NEW_YORK_1911_V95_REAL_VIDU.mp4"
 # Reuse original music, pad full final with same soundtrack using film's previous musical palette.
 call(["ffmpeg","-y","-v","error","-i",str(concatenated),
  "-stream_loop","-1","-i",str(old),"-map","0:v:0","-map","1:a:0",
  "-c:v","copy","-af","loudnorm=I=-18:TP=-2:LRA=7","-c:a","aac","-b:a","160k",
  "-shortest","-movflags","+faststart",str(final)],200)
 call(["ffmpeg","-v","error","-xerror","-i",str(final),"-f","null","-"],180)
 dur=float(json.loads(call(["ffprobe","-v","error","-show_entries","format=duration","-of","json",str(final)]))["format"]["duration"])
 if not 22<=dur<=35:raise RuntimeError("V95_LENGTH_INVALID "+str(dur))
 cover=P/"COVER.jpg"
 if cover.is_file():shutil.copy2(cover,OUT/"COVER.jpg")
 else:shutil.copy2(OUT/"VIDU_SOURCE_LOCKED_NEURAL_COLOR.jpg",OUT/"COVER.jpg")
 posts={"FACEBOOK":"NEW YORK · 1911. Vere immagini d'archivio e un breve momento di movimento ricostruito con Vidu. I colori e i particolari IA sono interpretazioni, non prove storiche. Fonte: Wikimedia Commons / Svenska Biografteatern.",
 "INSTAGRAM":"NEW YORK · 1911 — The city comes alive. Real documentary film, neural color and one AI-animated scene. #HistoryReels",
 "TIKTOK":"New York 1911: authentic moving film, restored color, and one Vidu animated historical moment. #history",
 "YOUTUBE":"NEW YORK · 1911 | La Storia Rivive. Authentic film: https://commons.wikimedia.org/wiki/File:New_York_1911.webm. AI color and one Vidu generated scene are interpretations of the real historic footage."}
 for k,v in posts.items():(OUT/("POST_"+k+".txt")).write_text(v+"\n")
 report={"production":"New York 1911 V95","format":"storia_rivive","status":"TECHNICAL_RENDER_VISUAL_REVIEW_PENDING",
  "source":"https://commons.wikimedia.org/wiki/File:New_York_1911.webm",
  "duration_s":dur,"vidu_task_id":claim["task_id"],"vidu_credits":claim["reported_credits"],
  "vidu_actual_clip_sha256":sh(CLIP),"final_mp4_sha256":sh(final),
  "source_visual_fidelity_ai":"automated similarity passed, human review not done",
  "photo_reconstruction_level":"DDColor neural color original 4 historical shots, does NOT qualify as full photoreal face restoration",
  "rights_italy":"PENDING_REVIEW","full_V94_artistically_approved":False,
  "publisher":"not uploaded to private site or social platforms"}
 write(OUT/"V95_QA.json",report)
 zipfile_=OUT/"NEW_YORK_1911_V95_PACKAGE.zip"
 with zipfile.ZipFile(zipfile_,"w",zipfile.ZIP_DEFLATED) as z:
  for p in [final,OUT/"COVER.jpg",OUT/"V95_QA.json",OUT/"VIDU_REAL_RECEIPT.json",*OUT.glob("POST_*.txt")]:
   z.write(p,p.name)
 with zipfile.ZipFile(zipfile_) as z:assert z.testzip() is None
 print("NEW_V95_VIDEO_RENDERED",final.name,dur,final.stat().st_size,zipfile_.stat().st_size,flush=True)
def main():
 if not SRC.is_file():raise RuntimeError("V83 must render source first")
 anchor,corr=photo()
 claim=generate(anchor,corr)
 splice(claim)
if __name__=="__main__":main()
