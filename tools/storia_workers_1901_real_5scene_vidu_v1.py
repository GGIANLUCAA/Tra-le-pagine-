#!/usr/bin/env python3
"""La Storia Rivive: NEW English workers c.1901, authentic 5 shots, real I2I photos, one quality-capped Q3 Vidu.
Source-first only; no social publication, artistic review pending, no repeat paid posts."""
import base64,hashlib,io,json,math,os,pathlib,subprocess,sys,time,urllib.request,urllib.error,wave,zipfile
import cv2,numpy as np,requests
from PIL import Image,ImageDraw,ImageFont
from gradio_client import Client,handle_file
sys.path.insert(0,"src")
import storia_rivive_real_ai_v60 as dd

REPO="GGIANLUCAA/Tra-le-pagine-"
RUN_SOURCE=42954852591
SRC_ROOT=pathlib.Path("output/storia_workers_1901_source")
R=pathlib.Path("output/storia_workers_1901_v1")
R.mkdir(parents=True,exist_ok=True)
W,H,FPS=720,1280,24
TITLE="ENGLAND · c.1901"
MODEL="viduq3-pro"
DURATION=5
RESOLUTION="1080p"
MAX_CREDITS=120
LEDGER="queue/vidu_api_attempts/STORIA_WORKERS_1901_Q3PRO_V1_ONCE.json"
OUT=R/"ENGLAND_1901_FACES_OF_THE_PAST_OWNER_REVIEW.mp4"
SOURCE_INFO=SRC_ROOT/"SCOUT_REPORT.json"
ONE_VIDEO=SRC_ROOT/"SOURCE_1901_REAL_MOVING.webm"
DOWNLOADS=[SRC_ROOT/"SOURCE_1901_REAL_MOVING.mp4",SRC_ROOT/"SOURCE_1901_REAL_MOVING.mkv"]
SOURCE_PAGE="https://commons.wikimedia.org/wiki/File:Victorian-Edwardian_workers_caught_on_film_(1901).webm"

def say(*x):print(*x,flush=True)
def write(name,data): (R/name).write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf8")
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for ch in iter(lambda:f.read(1<<20),b""):h.update(ch)
 return h.hexdigest()
def cmd(args,timeout=200):
 p=subprocess.run(args,text=True,capture_output=True,timeout=timeout)
 if p.returncode:raise RuntimeError("CMD_FAILED "+str(args[:6])+" "+p.stderr[-550:])
 return p.stdout
def read_frame(cap,t):
 cap.set(cv2.CAP_PROP_POS_MSEC,max(0,t)*1000)
 ok,f=cap.read()
 if not ok:raise RuntimeError("SOURCE_FRAME_UNREADABLE_TIME_"+str(t))
 return f
def score_crop(frame):
 h,w=frame.shape[:2]
 assert h>=500 and w>h
 crop_w=int(h*9/16)
 gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
 cascade=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
 faces=cascade.detectMultiScale(cv2.equalizeHist(gray),scaleFactor=1.08,minNeighbors=4,minSize=(22,22))
 best=(-1,0)
 for x0 in range(0,max(1,w-crop_w)+1,24):
  xend=x0+crop_w
  good=[(x,y,a,b) for x,y,a,b in faces if x>=x0+5 and x+a<xend-5]
  p=gray[:,x0:xend]
  contrast=float(p.std())
  total=sum(math.sqrt(a*b) for x,y,a,b in good)
  center_bias=abs(x0+crop_w/2-w/2)
  score=2.2*total+len(good)*15+contrast*.55-.028*center_bias
  if score>best[0]:best=(score,x0)
 x0=min(max(0,best[1]),w-crop_w)
 return {"x":int(x0),"width":int(crop_w),"source_width":w,"source_height":h,
         "source_frontal_faces_auto_total":int(len(faces)),
         "source_crop_faces_auto":int(sum(1 for x,y,a,b in faces if x>=x0+5 and x+a<x0+crop_w-5))}
def crop_frame(f,crop):
 return cv2.resize(f[:,crop["x"]:crop["x"]+crop["width"]],(W,H),interpolation=cv2.INTER_CUBIC)
def natural_base(frame,ab):
 lab=cv2.cvtColor(frame.astype(np.float32)/255.,cv2.COLOR_BGR2LAB)
 lab[:,:,1:]=np.clip(cv2.resize(ab,(frame.shape[1],frame.shape[0]))*.83,-92,92)
 return np.uint8(np.clip(cv2.cvtColor(lab,cv2.COLOR_LAB2BGR)*255,0,255))
def corr(a,b):
 def prep(x):
  g=cv2.cvtColor(cv2.resize(x,(132,230)),cv2.COLOR_BGR2GRAY)
  return cv2.GaussianBlur(g,(5,5),0).astype(np.float32).ravel()
 a,b=prep(a),prep(b)
 return float(np.corrcoef(a,b)[0,1]) if a.std()>.1 and b.std()>.1 else -1.0
def inspect_source():
 if not SOURCE_INFO.is_file():raise RuntimeError("GITHUB_SOURCE_SCOUT_REPORT_MISSING")
 report=json.loads(SOURCE_INFO.read_text())
 if report.get("status")!="FIVE_ACTUAL_ORIGINAL_FRAMES_SOURCE_SCOUT_ONLY":raise RuntimeError("SOURCE_REPORT_NOT_VERIFIED")
 src=ONE_VIDEO if ONE_VIDEO.is_file() else next((p for p in DOWNLOADS if p.is_file()),None)
 if src is None:raise RuntimeError("REAL_1901_HISTORIC_MOTION_MISSING")
 if sha(src)!=report["source_metadata"]["sha256"]:raise RuntimeError("SOURCE_SHA256_CHANGED")
 scenes=report.get("selected",[])
 if len(scenes)!=5:raise RuntimeError("NEED_FIVE_DISTINCT_MOVING_SHOTS")
 if any(b["time"]-a["time"]<15 for a,b in zip(scenes,scenes[1:])):raise RuntimeError("SHOTS_NOT_DISTINCT_IN_TIME")
 cap=cv2.VideoCapture(str(src))
 if not cap.isOpened():raise RuntimeError("FILM_CANT_DECODE")
 out=[]
 for i,s in enumerate(scenes,1):
  anchor=float(s["time"])
  orig=read_frame(cap,anchor)
  crop=score_crop(orig)
  processed=crop_frame(orig,crop)
  png=R/f"SHOT_{i:02d}_ACTUAL_BW_SOURCE.png"
  cv2.imwrite(str(png),processed)
  # actual historical motion in exact locked frame crop
  p1=crop_frame(read_frame(cap,anchor-1.1),crop)
  p2=crop_frame(read_frame(cap,anchor-.2),crop)
  delta=float(np.abs(p1.astype(np.float32)-p2.astype(np.float32)).mean())
  mean=float(cv2.cvtColor(processed,cv2.COLOR_BGR2GRAY).mean())
  if delta<1.20 or not 28<mean<220:raise RuntimeError(f"SHOT_{i}_MOTION_OR_EXPOSURE_UNSUITABLE {delta:.2f} {mean:.2f}")
  out.append({"scene":i,"time_s":anchor,"crop":crop,
   "original_exact_bw_file":png.name,"bw_sha256":sha(png),"motion_delta":round(delta,2),
   "source_quality_score":s["score"],"source_original_sha256":sha(src)})
 cap.release()
 write("FIVE_ACTUAL_SOURCES.json",{"original_source":SOURCE_PAGE,
  "source_file_sha256":sha(src),"source_file_path":str(src),"distinct_scene_anchors":out,
  "true_historical_film":True,"source_single_edit_compilation":True,"publicly_posted":False})
 say("FIVE_DISTINCT_HISTORICAL_MOTION_SHOTS_VERIFIED",[(x["scene"],x["time_s"],x["motion_delta"],x["crop"]["source_crop_faces_auto"]) for x in out])
 return src,out
def photo_restore(s,ddmodel,client):
 i=s["scene"];orig=cv2.imread(str(R/s["original_exact_bw_file"]))
 base=natural_base(orig,dd.infer_ab(ddmodel,orig))
 basefile=R/f"SHOT_{i:02d}_NEURAL_COLOR_BASE_NOT_FINAL.png"
 cv2.imwrite(str(basefile),base)
 prompt=("High fidelity documentary image-to-image restoration of a VERIFIED REAL black-and-white frame "+
  "filmed in northern England around 1901. People leaving factories look naturally into a real motion-picture camera. "+
  "Exactly preserve the true original people count, real facial expressions, positions, poses, hats, coats, cloth, street and factory facade; no invented humans or objects. "+
  "Photoreal 2026 quality scanner reconstruction, Victorian era wool caps and working-class garments; lifelike skin but never fake modern makeup, natural cloudy British daylight, muted historic palette, full color clearly reveals photographic surfaces. "+
  "Same exact camera angle, source face outlines and silhouettes. Absolutely no painting or aggressive sharpening.")
 neg=("added people, cloned faces, fabricated eye contact, deformed hands, synthetic wax face, glossy fashion models, "+
 "cartoon, painting, altered architecture, exaggerated cosmetics, orange skin, glowing highlights, bloom, "+
 "fake modern vehicles, text, watermarks, artificial crowd patterns, blurry oil painting")
 raw=client.predict(handle_file(str(basefile)),prompt,neg,1901,2,1.14,.97,6,112,144,.43,18,"DDIM",api_name="/process")
 res=raw[1] if isinstance(raw,(list,tuple)) and len(raw)>1 else raw
 if isinstance(res,dict):res=res.get("path")
 candidate=cv2.imread(str(res))
 if candidate is None:raise RuntimeError("I2I_PROVIDER_EMPTY_IMAGE_SCENE_"+str(i))
 candidate=cv2.resize(candidate,(W,H),interpolation=cv2.INTER_AREA)
 geom=corr(orig,candidate)
 diff=float(cv2.absdiff(base,candidate).mean())
 hsv=cv2.cvtColor(candidate,cv2.COLOR_BGR2HSV)
 avg=float(hsv[:,:,1].mean())
 if avg>115:
  hsv[:,:,1]=np.uint8(np.clip(hsv[:,:,1].astype(np.float32)*115/avg,0,215))
  candidate=cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
 sat=float(cv2.cvtColor(candidate,cv2.COLOR_BGR2HSV)[:,:,1].mean())
 # Do not accept mere neural coloring as real reconstructed photographic detail.
 if geom<.83 or diff<1.9 or sat<15 or sat>135:
  write(f"SHOT_{i:02d}_FAIL_GATE.json",{"geometry":geom,"difference_from_ddcolor":diff,"saturation":sat})
  raise RuntimeError("PHOTOGRAPHIC_SOURCE_IDENTITY_GATE_REJECTED_"+str(i))
 path=R/f"SHOT_{i:02d}_MODERN_PHOTO_I2I.jpg"
 cv2.imwrite(str(path),candidate,[cv2.IMWRITE_JPEG_QUALITY,96])
 return {"scene":i,"restored_photo_file":path.name,"photo_sha256":sha(path),
   "bw_sha256":s["bw_sha256"],"geometry_corr":round(geom,4),
   "color_saturation":round(sat,2),"photographic_I2I_real":True,
   "human_face_review":"PENDING","historic_person_exact_identity":"NOT_CLAIMED"}
def make_contact(scenes,photos):
 contact=Image.new("RGB",(5*330,2*625),(15,18,25))
 d=ImageDraw.Draw(contact);font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",20)
 for j,(sc,ph) in enumerate(zip(scenes,photos)):
  for row,p in enumerate([R/sc["original_exact_bw_file"],R/ph["restored_photo_file"]]):
   im=Image.open(p).convert("RGB");im.thumbnail((320,568))
   x=j*330+(330-im.width)//2;y=row*625+24
   contact.paste(im,(x,y))
   d.text((j*330+7,row*625+2),f"SHOT {j+1} "+("REAL B/W" if row==0 else "NEW AI PHOTO"),font=font,fill="white")
 contact.save(R/"SOURCE_VS_RESTORED_FIVE_SCENES_QA.jpg",quality=91)
def api(key,path,body=None,timeout=60):
 req=urllib.request.Request("https://api.vidu.com"+path,
  data=json.dumps(body).encode() if body is not None else None,
  headers={"Authorization":"Token "+key,"Accept":"application/json","Content-Type":"application/json"},
  method="POST" if body is not None else "GET")
 with urllib.request.urlopen(req,timeout=timeout) as res:return json.loads(res.read(250000))
def gh(args,timeout=65):
 return json.loads(cmd(["gh","api"]+args,timeout))
def before_post():
 key=os.environ.get("VIDU_API_KEY","")
 if not key:raise RuntimeError("VIDU_ACCOUNT_KEY_NOT_BOUND")
 data=api(key,"/ent/v2/credits")
 rows=data.get("remains",[])
 if not isinstance(rows,list):raise RuntimeError("VIDU_BALANCE_UNREADABLE")
 nums=[x.get("credit_remain") for x in rows if isinstance(x,dict)]
 if not nums or not any(type(v) in (int,float) and v>=MAX_CREDITS for v in nums):
  raise RuntimeError("NO_PREPAID_120_CREDITS_AVAILABLE")
 try:
  gh(["repos/"+REPO+"/contents/"+LEDGER+"?ref=main"])
 except Exception as e:
  if "404" not in str(e) and "Not Found" not in str(e):raise RuntimeError("CANNOT_VERIFY_NO_PRIOR_POST")
 else:raise RuntimeError("VIDU_PAID_LEDGER_ALREADY_EXISTS_DO_NOT_POST_AGAIN")
 return key
def reserve(key,sc,ph,image_path):
 receipt={"status":"reserved_before_paid_post","scene":"England workers c1901 scene 5",
   "source_film_sha256":sc["source_original_sha256"],
   "source_exact_bw_sha256":sc["bw_sha256"],"i2i_restored_photo_sha256":ph["photo_sha256"],
   "vidu_image_payload_sha256":sha(image_path),"model":MODEL,"resolution":RESOLUTION,
   "duration_s":DURATION,"max_existing_credits":MAX_CREDITS,"paid_post_count":0,
   "authorization":"User authorized use of Vidu credits for another entirely new historical video in this chat; capped one new high-quality 5-second scene",
   "no_paid_retries":True}
 blob=base64.b64encode((json.dumps(receipt,sort_keys=True)+"\n").encode()).decode()
 # Reservation is atomically persisted on GitHub main before the sole billable POST.
 gh(["-X","PUT","repos/"+REPO+"/contents/"+LEDGER,
     "-f","branch=main","-f","message=Reserve one authorized c1901 worker Q3 Pro 5s clip",
     "-f","content="+blob])
 write("VIDU_RESERVATION.json",receipt)
 return receipt
def update_receipt(receipt):
 info=gh(["repos/"+REPO+"/contents/"+LEDGER+"?ref=main"])
 blob=base64.b64encode((json.dumps(receipt,sort_keys=True)+"\n").encode()).decode()
 gh(["-X","PUT","repos/"+REPO+"/contents/"+LEDGER,
     "-f","branch=main","-f","sha="+info["sha"],"-f",
     "message=Record result of single workers 1901 Vidu generation",
     "-f","content="+blob])
def new_vidu_clip(s,ph):
 key=before_post()
 # The Vidu start frame is EXACTLY the fifth photo shown in the montage.
 photo=cv2.imread(str(R/ph["restored_photo_file"]))
 first=R/"EXACT_VIDU_ANCHOR_1080x1920.jpg"
 cv2.imwrite(str(first),cv2.resize(photo,(1080,1920)),[cv2.IMWRITE_JPEG_QUALITY,92])
 receipt=reserve(key,s,ph,first)
 content="data:image/jpeg;base64,"+base64.b64encode(first.read_bytes()).decode()
 prompt=("ONE CONTINUOUS FIVE-SECOND PHOTOREAL DOCUMENTARY SHOT of the EXACT 1901 factory workers in the reference image. "+
 "The workers in their genuine caps, coats and aprons naturally move, turn their heads slightly and walk past the motion-picture camera, authentic unaffected human expressions. "+
 "Keep the precise same individual people, faces, head positions, body count, garments, architecture and viewpoint as in the input; no extra people, no costume changes, no face morphing, no replacement of foreground people. "+
 "Cinematography: period-correct handheld-like tiny natural film movement but stationary viewpoint, overcast daylight, true-to-life human skin and realistic textures. "+
 "No cuts, no camera flying, no surrealism, no synthetic artificial facial motion, no camera zoom, no titles, no new objects, no dialogue. "+
 "The opening frame MUST align visually to the input photograph, and real motion must evolve from that same historical pose.")
 req={"model":MODEL,"images":[content],"prompt":prompt,"duration":DURATION,
      "resolution":RESOLUTION,"audio":False,"is_rec":False,"off_peak":False,
      "payload":"storia-workers-1901-one-shot-5second-q3pro"}
 # Exactly ONE paid POST. Network ambiguity means manual GET only; NEVER repeat POST.
 try:result=api(key,"/ent/v2/img2video",req,timeout=90)
 except Exception as ex:
  receipt.update(status="ambiguous_post_do_not_retry",paid_post_count=1,error_type=type(ex).__name__)
  update_receipt(receipt)
  raise RuntimeError("VIDU_POST_AMBIGUOUS_NO_RETRY")
 taskid=str(result.get("task_id") or "")
 credits=result.get("credits")
 receipt.update(status="submitted",paid_post_count=1,task_id=taskid,reported_credits=credits)
 update_receipt(receipt)
 write("VIDU_SUBMISSION_STATUS.json",{k:receipt.get(k) for k in ("status","model","resolution","duration_s","task_id","reported_credits","paid_post_count")})
 if not taskid or type(credits) not in (int,float) or credits>MAX_CREDITS:
  raise RuntimeError("PROVIDER_COST_EXCEEDS_120_OR_NO_TASKID_NEVER_RETRY")
 say("VIDU_Q3_PRO_SUBMITTED_ONE_POST",taskid,"reported_credits",credits)
 state={}
 for i in range(70):
  time.sleep(10)
  try:state=api(key,"/ent/v2/tasks/"+taskid+"/creations",timeout=40)
  except Exception:continue
  if state.get("state")=="failed":raise RuntimeError("Q3_PROVIDER_FAILED_NO_RETRY")
  if state.get("state")=="success":break
 if state.get("state")!="success":raise RuntimeError("VIDU_TASK_PENDING_COLLECTION_GET_ONLY_NO_RETRY")
 creations=state.get("creations",[])
 url=creations[0].get("url") if creations else None
 if not isinstance(url,str) or not url.startswith("https://"):raise RuntimeError("NO_REAL_Q3_VIDEO_URL")
 out=R/"VIDU_Q3_PRO_TRUE_COLOR_MOTION_5S.mp4"
 with requests.get(url,stream=True,timeout=(30,150)) as res:
  res.raise_for_status()
  with out.open("wb") as f:
   for ch in res.iter_content(1<<20):
    f.write(ch)
    if f.tell()>120000000:raise RuntimeError("VIDEO_PROVIDER_OVERSIZE")
 cmd(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(out),"-f","null","-"],220)
 receipt.update(status="actual_video_collected",sha256_mp4=sha(out),video_bytes=out.stat().st_size)
 update_receipt(receipt)
 write("VIDU_SUBMISSION_STATUS.json",{"state":"real_video_collected","credits_reported":credits,"task_id":taskid,"model":MODEL,"sha256":sha(out)})
 return out
def make_sound(seconds):
 sr=32000;n=round(seconds*sr);t=np.arange(n)/sr
 rng=np.random.default_rng(1901)
 # An understated original cinematic texture (no spoken narration), no borrowed track.
 audio=np.zeros(n,dtype=np.float64)
 chords=[(174.6,220.,261.6),(164.8,196.,246.9),(146.8,185.,220.),(164.8,220.,261.6)]
 for b in range(math.ceil(seconds*2)):
  start=int((b*.5)*sr);N=min(round(2.0*sr),n-start)
  if N<=0:break
  tt=np.arange(N)/sr;freq=chords[(b//8)%4][b%3]
  v=(np.sin(2*np.pi*freq*tt)+.16*np.sin(2*np.pi*2*freq*tt))*.018*np.exp(-2.7*tt)
  audio[start:start+N]+=v
 for j,chord in enumerate(chords):
  start=round(j*seconds/4*sr);N=min(round((seconds/4+1)*sr),n-start)
  if N<=0:continue
  tt=np.arange(N)/sr;env=np.minimum(1,tt/.5)*np.minimum(1,(N/sr-tt)/.8)
  audio[start:start+N]+=.012*sum(np.sin(2*np.pi*f*tt) for f in chord)/3*env
 # Very quiet breath of old crowd ambience, not canned voices.
 noise=rng.standard_normal(n)
 low=np.convolve(noise,np.ones(200)/200,mode="same")
 audio+=.0025*low
 for sec in [1.2,5.1,9.2,13.3,17.4]:
  o=int(sec*sr);N=min(int(.5*sr),n-o)
  if N>0:
   tt=np.arange(N)/sr;audio[o:o+N]+=.014*np.sin(2*np.pi*160*tt)*np.exp(-12*tt)
 audio*=min(1,.6/max(.01,float(np.abs(audio).max())))
 path=R/"ORIGINAL_DISCREET_SCORE.wav"
 with wave.open(str(path),"wb") as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes(np.int16(audio*32767).tobytes())
 return path
def overlay_title(frame):
 # Tiny English city/era in safe lower margin, not a wide intrusive banner.
 im=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
 d=ImageDraw.Draw(im)
 ft=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",25)
 d.text((32,1193),TITLE,fill=(241,231,214),font=ft,stroke_width=1,stroke_fill=(12,12,15))
 return cv2.cvtColor(np.array(im),cv2.COLOR_RGB2BGR)
def video_frame(cap,t,crop):
 return crop_frame(read_frame(cap,t),crop)
def produce(scenes,photos,real_vidu=None):
 source=SRC_ROOT/"SOURCE_1901_REAL_MOVING.webm"
 if not source.is_file():source=next(p for p in DOWNLOADS if p.is_file())
 cap=cv2.VideoCapture(str(source))
 temp=R/"VISUAL_TIMELINE_TEMP.mp4"
 writer=cv2.VideoWriter(str(temp),cv2.VideoWriter_fourcc(*"mp4v"),FPS,(W,H))
 if not writer.isOpened():raise RuntimeError("VIDEO_WRITER_START_FAILED")
 timeline=[];elapsed=0
 # Designed rhythm, 5 genuine moving source shots selected >15 seconds apart.
 for idx,(sc,ph) in enumerate(zip(scenes,photos)):
  crop=sc["crop"];bw_s=[1.20,1.35,1.30,1.25,1.40][idx]
  hold_s=[2.35,2.15,2.25,2.15,1.55][idx]
  anchor=sc["time_s"]
  if idx==4 and real_vidu is None:hold_s=2.6
  t0=elapsed/FPS
  n_bw=round(bw_s*FPS)
  for j in range(n_bw):
   f=video_frame(cap,anchor-bw_s+j/FPS,crop)
   if idx==0 and j<35:f=overlay_title(f)
   writer.write(f);elapsed+=1
  # Align last original frame of motion with identical cropped black-and-white anchor.
  exact=cv2.imread(str(R/sc["original_exact_bw_file"]))
  photo=cv2.imread(str(R/ph["restored_photo_file"]))
  # The color reveal is 0.25 seconds, followed by actual hold sufficient to enjoy the photo.
  fade=6
  for j in range(fade):
   a=(j+1)/fade;a=a*a*(3-2*a)
   writer.write(cv2.addWeighted(exact,1-a,photo,a,0));elapsed+=1
  for j in range(max(0,round(hold_s*FPS)-fade)):
   writer.write(photo);elapsed+=1
  timeline.append({"scene":idx+1,"anchor_source_time_s":anchor,"start_s":round(t0,3),
                   "bw_original_motion_s":n_bw/FPS,"modern_photo_s":round(hold_s,3),
                   "source_crop":crop,"bw_file":sc["original_exact_bw_file"],
                   "modern_photo":ph["restored_photo_file"]})
 cap.release()
 # Only scene five may transition to source-matched Vidu motion, after photo hold.
 counted=0
 if real_vidu is not None:
  # fps-normalize with original framing to 9:16. New movement is not a fake Ken Burns pan.
  norm=R/"VIDU_FINAL_24FPS_720PX.mp4"
  cmd(["ffmpeg","-nostdin","-y","-v","error","-i",str(real_vidu),
       "-t","5","-vf","fps=24,scale=720:1280","-an","-c:v","libx264","-crf","19",
       "-preset","veryfast","-pix_fmt","yuv420p",str(norm)],210)
  vc=cv2.VideoCapture(str(norm))
  photoframe=cv2.imread(str(R/photos[-1]["restored_photo_file"]))
  ok,vfirst=vc.read()
  if not ok:raise RuntimeError("VIDU_NO_FRAMES")
  overlap=corr(photoframe,vfirst)
  # Strict exact photo-to-animated first-frame match gate; no bad sudden image swap.
  if overlap<.78:
   vc.release()
   write("VIDU_MOTION_IDENTITY_GATE_REJECT.json",{"correlation":overlap,"threshold":.78,
       "status":"VIDEO_WILL_NOT_BE_CALLED_FINAL","charged_video_not_reused":True})
   raise RuntimeError("VIDU_FIRST_FRAME_DOES_NOT_MATCH_HISTORICAL_PHOTO")
  writer.write(vfirst);counted=1;elapsed+=1
  while counted<120:
   ok,frame=vc.read()
   if not ok:break
   writer.write(frame);counted+=1;elapsed+=1
  vc.release()
  if counted<114:raise RuntimeError("VIDU_SOURCE_MATCHED_COLOR_MOTION_TOO_SHORT")
  timeline.append({"scene":"5-motion-Vidu","type":"Q3-pro-photo-locked-animation",
                   "duration_s":counted/FPS,"photographic_frame_overlap_corr":round(overlap,3)})
 writer.release()
 duration=elapsed/FPS
 if not 17<duration<26:raise RuntimeError("DURATION_OUTSIDE_EDITORIAL_RANGE")
 if real_vidu is not None and counted<114:raise RuntimeError("REAL_VIDU_MOTION_MISSING")
 music=make_sound(duration)
 cmd(["ffmpeg","-nostdin","-y","-v","error","-i",str(temp),"-i",str(music),"-shortest",
      "-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p",
      "-c:a","aac","-b:a","160k","-movflags","+faststart",str(OUT)],420)
 cmd(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(OUT),"-f","null","-"],250)
 p=json.loads(cmd(["ffprobe","-v","error","-show_entries",
                   "format=duration:stream=codec_name,width,height,r_frame_rate","-of","json",str(OUT)]))
 if not any(k.get("codec_name")=="h264" and k.get("width")==720 and k.get("height")==1280 for k in p["streams"]):
  raise RuntimeError("INVALID_SOCIAL_FORMAT")
 if not any(k.get("codec_name")=="aac" for k in p["streams"]):raise RuntimeError("MISSING_ORIGINAL_MUSIC")
 d={ "subject":"1901 northern English workers leaving factories","source_count":1,"distinct_historical_original_moving_shots":5,
      "photographic_real_i2i_stills":5,"genuine_new_vidu_clip":bool(real_vidu),"vidu_model":MODEL if real_vidu is not None else None,
      "timeline":timeline,"duration_s":round(duration,3),"resolution":[720,1280],
      "format_note":"1080p Vidu scene downscaled to 720x1280 social master. Source film native 1280x720; no false 4K claim.",
      "video_sha256":sha(OUT),"artistic_approval":False,"manual_full_reel_review":"PENDING",
      "historic_rights_italy":"PENDING","social_published":False,"video_status":"OWNER_REVIEW_ONLY_NOT_APPROVED"}
 write("FINAL_TECH_QA.json",d)
 cover=Image.fromarray(cv2.cvtColor(cv2.imread(str(R/photos[4]["restored_photo_file"])),cv2.COLOR_BGR2RGB))
 draw=ImageDraw.Draw(cover);ft=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",32)
 draw.text((28,58),"FACES OF THE PAST",fill="white",font=ft,stroke_width=2,stroke_fill="#242424")
 draw.text((29,103),TITLE,fill="#f7e6be",font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",24),stroke_width=1,stroke_fill="black")
 cover.save(R/"SOCIAL_COVER.jpg",quality=94)
 for site in ("FACEBOOK","INSTAGRAM","TIKTOK","YOUTUBE"):
  (R/f"POST_{site}.txt").write_text(
   "ENGLAND · c.1901 | FACES OF THE PAST\nMen and women caught on original early cinema film outside northern English factories. Authentic historical black-and-white motion, source-locked photographic AI color reconstructions, and one interpretative AI-motion continuation. AI details and colors are interpretative, not a contemporary color recording. Owner review preview; not published.\nSource: "+SOURCE_PAGE+"\n",encoding="utf8")
 (R/"README_ARTISTIC_REVIEW_REQUIRED.txt").write_text(
  "NEW FILM/NEW SUBJECT. Five distant source timecodes from the original verified moving 1901 factory-worker film, five newly generated I2I photos, and one Q3 Pro source-matched scene if permitted by the geometry gate. Technical decode success is NOT human artistic approval. Verify faces, anatomy, colors, content and rights in Italy before publishing. No re-use of owner rejected Barbershop 1894. No fake 4K.\n",encoding="utf8")
 Z=R/"ENGLAND_1901_FACES_OF_THE_PAST_ANDROID_KIT.zip"
 with zipfile.ZipFile(Z,"w",zipfile.ZIP_DEFLATED,compresslevel=3) as z:
  names=[OUT,R/"SOCIAL_COVER.jpg",R/"FINAL_TECH_QA.json",R/"SOURCE_VS_RESTORED_FIVE_SCENES_QA.jpg",
         R/"FIVE_ACTUAL_SOURCES.json",R/"FIVE_AI_PHOTOS_QA.json",R/"README_ARTISTIC_REVIEW_REQUIRED.txt",
         *[R/f"POST_{x}.txt" for x in ("FACEBOOK","INSTAGRAM","TIKTOK","YOUTUBE")]]
  for file in names:
   if not file.exists():raise RuntimeError("MISSING_DELIVERY_FILE "+str(file))
   z.write(file,arcname=file.name)
 with zipfile.ZipFile(Z) as z:assert z.testzip() is None
 say("WORKERS_1901_REAL_MP4_AND_ZIP_COMPLETE",d["video_sha256"],d["duration_s"],"VIDU_INCLUDED",bool(real_vidu))
 return d
def main():
 source,shots=inspect_source()
 model,_=dd.download_model()
 client=Client("finegrain/finegrain-image-enhancer",verbose=False)
 photos=[photo_restore(z,model,client) for z in shots]
 write("FIVE_AI_PHOTOS_QA.json",{"photos":photos,"source_only_original_frames":True,
   "five_new_real_image2image":True,"automatic_gates_passed":True,"human_artistic_review":False})
 make_contact(shots,photos)
 say("FIVE_HIGH_FIDELITY_PHOTO_RESTORATIONS_COMPLETE_NO_VIDU_POST_YET")
 # Safety: paid post is submitted exactly once, only after every photo and source frame has passed.
 vidu=new_vidu_clip(shots[4],photos[4])
 produce(shots,photos,vidu)
if __name__=="__main__":
 try:main()
 except Exception as e:
  write("FAILURE.json",{"error_type":type(e).__name__,"message":str(e)[:460],
    "charged_or_attempted_vidu":"inspect VIDU_RESERVATION and ledger; never repeat POST blindly",
    "final_video":OUT.is_file(),"artistic_approved":False,"social_posted":False})
  say("STORIA_WORKERS_1901_FAILED_OR_BLOCKED",type(e).__name__,str(e)[:400])
  raise
