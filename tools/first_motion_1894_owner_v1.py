#!/usr/bin/env python3
"""FIRST MOTION 1893-1894: one-off real 5-source archival short, source-locked I2I + single Vidu. Review only."""
import base64, hashlib, json, math, os, pathlib, random, subprocess, sys, time, urllib.parse, urllib.request, wave, zipfile
import cv2
import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont
from gradio_client import Client, handle_file
sys.path.insert(0,"src")
import storia_rivive_real_ai_v60 as dd

REPO="GGIANLUCAA/Tra-le-pagine-"
ROOT=pathlib.Path("output/first_motion_1894_v1")
ROOT.mkdir(parents=True,exist_ok=True)
W,H,FPS=720,1280,24
MAX_CREDITS=16
LEDGER="queue/vidu_api_attempts/FIRST_MOTION_1894_V1_SINGLE_POST.json"
SRC=[
 ("barber01","The Barbershop (1894).webm",1894,2.0,0.90,1.85,"A customer waits at a Victorian barber shop; preserve all visible customers, hats and furnishings."),
 ("barber02","The Barbershop (1894).webm",1894,4.3,1.50,2.05,"A barber handles a customer at an 1894 barbershop, preserve true head and hand positions, the mirror and counter."),
 ("barber03","The Barbershop (1894).webm",1894,6.6,1.30,1.90,"Men in 1894 barbershop react naturally; exact face and body counts, no invented expressions."),
 ("barber04","The Barbershop (1894).webm",1894,8.7,1.40,2.00,"The barber and customers seen from fixed original 1894 camera; accurate silhouettes, fabric and period interior."),
 ("barber05","The Barbershop (1894).webm",1894,10.5,1.30,5.00,"Barber and waiting customers in 1894 Edison barbershop; real person positions and authentic details.")
]
PAGE="https://commons.wikimedia.org/wiki/File:"
OUTVIDEO=ROOT/"FIRST_MOTION_1893_1894_VIDU_REVIEW.mp4"
def say(*xs):print(*xs,flush=True)
def out(name,v):(ROOT/name).write_text(json.dumps(v,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
def cmd(xs,timeout=160):
 p=subprocess.run(xs,capture_output=True,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError("CMD_FAIL "+str(xs[:4])+" "+p.stderr[-350:])
 return p.stdout
def wiki_source(name):
 s=requests.Session();s.headers.update({"User-Agent":"LaStoriaRivive/1.0 (educational restoration; Wikimedia attribution)","Accept":"application/json"})
 j=s.get("https://commons.wikimedia.org/w/api.php",params={"action":"query","titles":"File:"+name,"prop":"imageinfo","iiprop":"url|size|sha1","format":"json"},timeout=35)
 j.raise_for_status()
 pages=j.json().get("query",{}).get("pages",{})
 row=next(iter(pages.values())).get("imageinfo",[None])[0]
 if not isinstance(row,dict) or not str(row.get("url","")).startswith("https://upload.wikimedia.org/"):
  raise RuntimeError("COMMONS_FILE_NOT_RESOLVED "+name)
 return row
def source_download(spec):
 id,name,year,t,bw,hold,prompt=spec
 stored=ROOT/"BARBERSHOP_VERIFIED_ARCHIVAL_SOURCE.mp4"
 if not stored.exists():
  # Existing verified genuine original moving B/W extract, copied from the Nov 9 scout.
  cmd(["gh","release","download","storia-barbershop-1894-source-scout-42649779508",
       "--repo",REPO,"-p","ARCHIVAL_MOVING_SCOUT_NOT_RESTORED.mp4","-D",str(ROOT)],timeout=100)
  acquired=ROOT/"ARCHIVAL_MOVING_SCOUT_NOT_RESTORED.mp4"
  if not acquired.exists():raise RuntimeError("VERIFIED_ARCHIVAL_SOURCE_UNAVAILABLE")
  acquired.rename(stored)
 if stored.stat().st_size<500000:raise RuntimeError("ARCHIVAL_SOURCE_TOO_SMALL")
 cap=cv2.VideoCapture(str(stored))
 fps=cap.get(cv2.CAP_PROP_FPS)
 duration=cap.get(cv2.CAP_PROP_FRAME_COUNT)/max(1,fps)
 sw=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));sh=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
 if not (t>0.7 and t<duration-0.25):
  raise RuntimeError("TIMECODE_OUT_OF_RANGE "+id+" "+str(duration))
 # Select only real nonblack source frames, not black leader, fade or blank gaps.
 scene_times=ROOT/"SOURCE_VALID_SCENE_TIMES.json"
 if scene_times.exists():
  chosen=json.loads(scene_times.read_text())["times"]
 else:
  choices=[]
  usable_duration=min(duration-0.35,11.5)
  tt=1.55
  while tt<usable_duration:
   cap.set(cv2.CAP_PROP_POS_MSEC,tt*1000)
   good,frame=cap.read()
   if good:
    g=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    mean=float(g.mean());std=float(g.std())
    if 25<mean<226 and std>19:
     choices.append((round(tt,3),round(mean,2),round(std,2)))
   tt+=.2
  if len(choices)<13:raise RuntimeError("TOO_FEW_NONBLACK_SOURCE_FRAMES_NO_SPEND")
  chosen=[choices[round(i*(len(choices)-1)/4)][0] for i in range(5)]
  if any(chosen[k+1]-chosen[k]<.55 for k in range(4)):
   raise RuntimeError("SOURCE_NOT_ENOUGH_DISTINCT_MOTION_MOMENTS_NO_SPEND")
  scene_times.write_text(json.dumps({"times":chosen,"usable_samples":len(choices),"analysis":"Real source luminance and contrast scan; black frames excluded"},indent=2))
  say("SOURCE_SCENE_TIMECODES_VERIFIED",chosen)
 t=chosen[[z[0] for z in SRC].index(id)]
 cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,img=cap.read();cap.release()
 if not ok:raise RuntimeError("NO_EXACT_FRAME "+id)
 img=cv2.resize(img,(960,720),interpolation=cv2.INTER_AREA)
 cv2.imwrite(str(ROOT/(id+"_exact_bw.png")),img)
 return {"id":id,"name":name,"year":year,"second":t,"path":str(stored),
         "sha256":sha(stored),
         "source_page":"https://commons.wikimedia.org/wiki/File:The_Barbershop_(1894).webm",
         "verified_release":"https://github.com/"+REPO+"/releases/tag/storia-barbershop-1894-source-scout-42649779508",
         "image_sha256":sha(ROOT/(id+"_exact_bw.png")),"seconds":duration,
         "native_width":sw,"native_height":sh}

def gray_corr(a,b):
 x=cv2.cvtColor(cv2.resize(a,(144,108)),cv2.COLOR_BGR2GRAY).astype(np.float32).ravel()
 y=cv2.cvtColor(cv2.resize(b,(144,108)),cv2.COLOR_BGR2GRAY).astype(np.float32).ravel()
 return float(np.corrcoef(x,y)[0,1])
def natural_color(bw,ab):
 lab=cv2.cvtColor(bw.astype(np.float32)/255,cv2.COLOR_BGR2LAB)
 lab[:,:,1:]=np.clip(cv2.resize(ab,(bw.shape[1],bw.shape[0]))*.83,-92,92)
 return np.uint8(np.clip(cv2.cvtColor(lab,cv2.COLOR_LAB2BGR)*255,0,255))
def restore(meta,model,client):
 id=meta["id"]
 bw=cv2.imread(str(ROOT/(id+"_exact_bw.png")))
 base=natural_color(bw,dd.infer_ab(model,bw))
 basefile=ROOT/(id+"_color_base_not_final.png")
 cv2.imwrite(str(basefile),base)
 desc=next(z[6] for z in SRC if z[0]==id)
 prompt=("Ultra realistic documentary photography, source-locked restoration of the ORIGINAL "+str(meta["year"])+
 " motion picture frame. "+desc+" Preserve identical camera viewpoint, exact silhouettes, faces, number of people, objects, backgrounds, fabric folds and hairstyles. Natural European-American late Victorian era colors, high photographic microtexture and clear but historically plausible face details. No modern objects. Full color looks like a well-exposed contemporary analogue photograph, not a painting or color filter.")
 neg="invented faces, extra people, extra fingers, changing expressions, plastic skin, fake teeth, merged hands, changed pose, modern objects, false background, illustration, cartoon, watercolor, over-sharp halos, saturated orange, cyan shadows"
 raw=client.predict(handle_file(str(basefile)),prompt,neg,1894,2,1.14,.97,6,112,144,.45,18,"DDIM",api_name="/process")
 result=raw[1] if isinstance(raw,(list,tuple)) and len(raw)>1 else raw
 if isinstance(result,dict):result=result.get("path")
 img=cv2.imread(str(result))
 if img is None:raise RuntimeError("NO_FINEGRAIN_PHOTO "+id)
 img=cv2.resize(img,(960,720),interpolation=cv2.INTER_AREA)
 c=gray_corr(bw,img);sat=float(cv2.cvtColor(img,cv2.COLOR_BGR2HSV)[:,:,1].mean())
 diff=float(cv2.absdiff(img,base).mean())
 report={"source":id,"source_exact_frame_sha":meta["image_sha256"],
         "grayscale_geometry_correlation":round(c,4),"saturation":round(sat,2),
         "different_from_neural_color_base":round(diff,2),"method":"Finegrain real image-to-image after DDColor (NOT DDColor-only)",
         "human_anatomy_review":"PENDING"}
 if c<0.72 or sat<15 or sat>165 or diff<1.7:
  out(id+"_PHOTO_QA.json",report)
  raise RuntimeError("PHOTO_FAIL_SOURCE_LOCK "+id+" "+json.dumps(report))
 p=ROOT/(id+"_I2I_RESTORED.png")
 cv2.imwrite(str(p),img);report["photo_sha"]=sha(p)
 out(id+"_PHOTO_QA.json",report)
 say("REAL_I2I_SOURCE_LOCKED",id,"corr",c,"sat",sat)
 return img
def canvas(img, label=None):
 # Full width historical source is never cropped into false close-ups.
 tiny=cv2.resize(img,(180,135))
 blur=cv2.GaussianBlur(tiny,(0,0),12)
 back=cv2.resize(blur,(W,H))
 back=np.uint8(np.clip(back.astype(np.float32)*.24,0,255))
 center=cv2.resize(img,(720,540),interpolation=cv2.INTER_AREA)
 top=360
 back[top:top+540,:]=center
 if label:
  im=Image.fromarray(cv2.cvtColor(back,cv2.COLOR_BGR2RGB))
  d=ImageDraw.Draw(im)
  fpath="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
  f=ImageFont.truetype(fpath,21)
  d.text((22,1116),label,font=f,fill=(233,221,197),stroke_width=1,stroke_fill=(10,10,10))
  back=cv2.cvtColor(np.array(im),cv2.COLOR_RGB2BGR)
 return back
def video_frame(p,t):
 c=cv2.VideoCapture(str(p));c.set(cv2.CAP_PROP_POS_MSEC,t*1000)
 ok,f=c.read();c.release()
 if not ok:raise RuntimeError("FILM_FRAME_UNAVAILABLE "+str(t))
 return cv2.resize(f,(960,720))
def debit_guard():
 key=os.environ.get("VIDU_API_KEY","")
 if not key:raise RuntimeError("VIDU_KEY_NOT_AVAILABLE")
 req=urllib.request.Request("https://api.vidu.com/ent/v2/credits",headers={"Authorization":"Token "+key,"Accept":"application/json"})
 with urllib.request.urlopen(req,timeout=25) as r: j=json.loads(r.read(200000))
 rows=j.get("remains",j.get("remaining_credits",[]))
 if not any(isinstance(z,dict) and type(z.get("credit_remain")) in (int,float) and z["credit_remain"]>=MAX_CREDITS for z in rows):raise RuntimeError("NO_SUFFICIENT_VIDU_CREDITS")
 return key
def reserve_once(meta,photo):
 payload={"scene":"The Barbershop 1894 at "+str(meta["second"])+"s",
  "source_sha256":meta["sha256"],"restored_photo_sha256":sha(photo),
  "model":"viduq2-pro-fast","duration":5,"resolution":"720p","max_credits":16,
  "user_instruction":"User expressly requested a new high-quality historical video and authorized using Vidu credits in the current conversation.",
  "status":"reserved_before_single_POST","paid_posts":0}
 b=base64.b64encode((json.dumps(payload,sort_keys=True)+"\n").encode()).decode()
 cmd(["gh","api","-X","PUT","repos/"+REPO+"/contents/"+LEDGER,"-f","branch=main",
      "-f","message=Reserve single authorized Vidu 1894 source-locked video request",
      "-f","content="+b],timeout=60)
 out("VIDU_RESERVATION.json",{"status":"reserved_before_paid_post","cost_ceiling":MAX_CREDITS,"source":meta["id"]})
def vidu_clip(photo,meta):
 key=debit_guard()
 p=ROOT/"barbershop_vidu_source.png"
 cv2.imwrite(str(p),canvas(photo))
 # Reserve original image and prompt before POST; duplicate run fails closed.
 reserve_once(meta,p)
 image_data=base64.b64encode(p.read_bytes()).decode()
 prompt=("1894 Edison barbershop reconstructed from THIS EXACT historical original frame. "
 "Same barber and same seated customers move gently and plausibly in the same room, "
 "subtle human expressions, natural shaving motions, realistic hands and eyes, "
 "realistic historic fabrics, no new people and no camera change. "
 "Keep the same camera perspective and same person positions throughout, "
 "continuous five second naturally moving photorealistic scene. "
 "No modern objects, no morphing, no cuts, no zooming, no title, no text.")
 body={"model":"viduq2-pro-fast","resolution":"720p","images":["data:image/png;base64,"+image_data],
  "prompt":prompt,"duration":5,"off_peak":False,"audio":False,"is_rec":False,
  "payload":"owner-first-motion-1894-onepost"}
 req=urllib.request.Request("https://api.vidu.com/ent/v2/img2video",
       data=json.dumps(body).encode(),headers={"Authorization":"Token "+key,"Content-Type":"application/json","Accept":"application/json"},method="POST")
 try:
  with urllib.request.urlopen(req,timeout=75) as response: accepted=json.loads(response.read(150000))
 except Exception:
  out("VIDU_STATUS.json",{"status":"PAID_POST_UNKNOWN_DO_NOT_RETRY","single_attempt":True})
  raise RuntimeError("PAID_SUBMISSION_UNKNOWN_CHECK_PROVIDER_NEVER_RETRY")
 taskid=str(accepted.get("task_id",""))
 credits=accepted.get("credits")
 out("VIDU_STATUS.json",{"status":"submitted","task_id":taskid,"reported_credits":credits,"single_attempt":True})
 if not taskid or type(credits) not in (int,float) or credits>MAX_CREDITS:raise RuntimeError("VIDU_COST_OR_ID_INVALID_NO_RETRY")
 say("VIDU_SINGLE_SUBMITTED",taskid,"reported",credits)
 result=None
 for i in range(54):
  time.sleep(10)
  try:
   get=urllib.request.Request("https://api.vidu.com/ent/v2/tasks/"+taskid+"/creations",headers={"Authorization":"Token "+key})
   with urllib.request.urlopen(get,timeout=35) as r:resp=json.loads(r.read(300000))
  except Exception:continue
  if resp.get("state") in ("failed","cancelled"):raise RuntimeError("VIDU_PROVIDER_FAILED_NO_RETRY")
  if resp.get("state")=="success":
   result=resp;break
 if result is None:raise RuntimeError("VIDU_PENDING_GET_COLLECT_NEEDED_NO_RETRY")
 creations=result.get("creations") or []
 url=creations[0].get("url") if creations else ""
 if not isinstance(url,str) or not url.startswith("https://"):raise RuntimeError("VIDU_NO_VALID_VIDEO")
 p=ROOT/"VIDU_BARBERSHOP_REAL_MOTION.mp4"
 with requests.get(url,stream=True,timeout=(25,130)) as r:
  r.raise_for_status()
  with p.open("wb") as f:
   for ch in r.iter_content(1048576):
    f.write(ch)
    if f.tell()>90000000:raise RuntimeError("VIDU_VIDEO_OVERSIZE")
 cmd(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(p),"-f","null","-"],timeout=180)
 out("VIDU_STATUS.json",{"status":"real_video_collected","task_id":taskid,"reported_credits":credits,"sha256":sha(p),"single_attempt":True})
 return p
def create_original_sound(seconds):
 sr=32000;n=int(seconds*sr)
 t=np.arange(n,dtype=np.float64)/sr
 rng=np.random.default_rng(1894)
 # Original restrained cinematic score; no sampled copyrighted music.
 audio=np.zeros(n,dtype=np.float64)
 chords=[(146.83,174.61,220.0),(130.81,164.81,196.0),(146.83,185.0,220.0),(123.47,164.81,196.0)]
 for beat in range(math.ceil(seconds*2.0)):
  onset=beat*.5;ind0=int(onset*sr)
  if ind0>=n:break
  L=min(n-ind0,int(2.0*sr));local=np.arange(L)/sr
  c=chords[(beat//4)%4]
  f=c[beat%3]* (2.0 if beat%2 else 1.0)
  # Clavichord-like soft percussive envelopes layered over bowed string pad.
  sig=np.sin(2*np.pi*f*local)*np.exp(-4*local)+.24*np.sin(2*np.pi*2*f*local)*np.exp(-6*local)
  audio[ind0:ind0+L]+=.07*sig
 for i,c in enumerate(chords):
  start=i*seconds/4;ind0=int(start*sr);L=min(n-ind0,int((seconds/4+1)*sr))
  local=np.arange(L)/sr
  if L>0:
   env=np.minimum(1,local/.5)*np.minimum(1,(L/sr-local)/.6)
   pad=sum(np.sin(2*np.pi*f*local) for f in c)/3
   audio[ind0:ind0+L]+=.018*pad*env
 audio+=.0025*rng.standard_normal(n)
 # Clear soft reveal emphasis on source photo transitions.
 for idx,s in enumerate([SRC[0][4],SRC[0][4]+SRC[0][5]+SRC[1][4],
 SRC[0][4]+SRC[0][5]+SRC[1][4]+SRC[1][5]+SRC[2][4],
 sum(z[4]+z[5] for z in SRC[:3])+SRC[3][4]]):
  o=int(s*sr);L=min(n-o,int(.36*sr))
  if L>0:
   x=np.arange(L)/sr;audio[o:o+L]+=.025*np.sin(2*np.pi*390*x)*np.exp(-10*x)
 audio/=max(1,np.max(np.abs(audio))/.60)
 p=ROOT/"ORIGINAL_SCORE.wav"
 with wave.open(str(p),"wb") as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes(np.int16(audio*32767).tobytes())
 return p
def make_cover(photo):
 image=Image.fromarray(cv2.cvtColor(canvas(photo),cv2.COLOR_BGR2RGB))
 d=ImageDraw.Draw(image)
 fpath="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
 titlef=ImageFont.truetype(fpath,34)
 d.text((36,130),"THE BARBERSHOP",font=titlef,fill=(245,231,206),stroke_width=1,stroke_fill=(5,5,5))
 d.text((40,184),"1894",font=ImageFont.truetype(fpath,23),fill=(225,207,172))
 image.save(ROOT/"SOCIAL_COVER.jpg",quality=94)
def assemble(metas,photos,clip):
 partial=ROOT/"TEMP_VISUAL.mp4"
 writer=cv2.VideoWriter(str(partial),cv2.VideoWriter_fourcc(*"mp4v"),FPS,(W,H))
 if not writer.isOpened():raise RuntimeError("VIDEO_WRITER_NOT_OPEN")
 timeline=[]
 for i,(spec,meta,photo) in enumerate(zip(SRC,metas,photos)):
  if i>=4:break
  id,_,year,t,bw,hold,_=spec
  t=meta["second"]
  fcount=int(round(bw*FPS));start=t-bw
  for n in range(fcount):
   frame=canvas(video_frame(meta["path"],max(.05,start+n/FPS)),
                "BARBERSHOP  ·  1894" if i==0 and n<19 else None)
   writer.write(frame)
  # Freeze on exact original frame, then reveal reconstructed color.
  anchor=canvas(cv2.imread(str(ROOT/(id+"_exact_bw.png"))))
  full=canvas(photo)
  ramp=5
  for n in range(ramp):
   a=((n+1)/ramp)
   a=a*a*(3-2*a)
   writer.write(cv2.addWeighted(anchor,1-a,full,a,0))
  for _ in range(max(1,int(round(hold*FPS))-ramp)):writer.write(full)
  timeline.append({"name":id,"bw_motion_s":bw,"color_photo_s":hold,"source_timecode":t,"source_original_sha256":meta["sha256"]})
 # final sequence: authentic Barbershop B/W leading into REAL moving Vidu.
 spec=SRC[4];meta=metas[4];id,_,year,t,bw,hold,_=spec
 for n in range(int(round(bw*FPS))):
  writer.write(canvas(video_frame(meta["path"],max(.05,t-bw+n/FPS))))
 c=cv2.VideoCapture(str(clip))
 vidu_count=0;last=None
 while vidu_count<int(round(5.0*FPS)):
  ok,frame=c.read()
  if not ok:break
  frame=cv2.resize(frame,(W,H))
  tclip=vidu_count/FPS
  if tclip<.95:
   gray=cv2.cvtColor(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR)
   a=max(0,min(1,(tclip-.07)/.88));a=a*a*(3-2*a)
   frame=cv2.addWeighted(gray,1-a,frame,a,0)
  writer.write(frame);vidu_count+=1;last=frame
 c.release();writer.release()
 if vidu_count<96:raise RuntimeError("VIDU_TOO_SHORT_TO_VERIFY")
 timeline.append({"name":"barbershop","bw_motion_s":bw,"vidu_color_motion_s":vidu_count/FPS,"source_timecode":t,"source_original_sha256":meta["sha256"]})
 duration=sum(z["bw_motion_s"]+z.get("color_photo_s",z.get("vidu_color_motion_s",0)) for z in timeline)
 music=create_original_sound(duration)
 cmd(["ffmpeg","-nostdin","-y","-v","error","-i",str(partial),"-i",str(music),"-shortest",
     "-c:v","libx264","-preset","fast","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-movflags","+faststart",str(OUTVIDEO)],timeout=360)
 cmd(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(OUTVIDEO),"-f","null","-"],timeout=240)
 stats=json.loads(cmd(["ffprobe","-v","error","-show_entries","format=duration:stream=codec_name,width,height,r_frame_rate","-of","json",str(OUTVIDEO)]))
 out("TECHNICAL_QA.json",{"genuine_new_composition":True,"full_4plus1_distinct_films_gate":"NOT_APPLICABLE_REVIEW_ONLY","source_film_count":1,"different_moments_same_original_film":5,
    "new_finegrain_restorations":5,"real_vidu_clip_produced":True,
    "timeline":timeline,"video_sha256":sha(OUTVIDEO),"ffprobe":stats,
    "source_locked_photo_qa":"AUTOMATED_ONLY","human_identity_review":"PENDING",
    "artistic_approval":False,"social_published":False,
    "disclosure":"AI color/photos and Vidu motion are interpretations, not documentary color"})
 make_cover(photos[4])
 for platform in ("FACEBOOK","INSTAGRAM","TIKTOK","YOUTUBE"):
  (ROOT/("POST_"+platform+".txt")).write_text("FIRST MOTION · 1893–1894\nFive distinct moments from the authentic Edison 1894 Barbershop film. Authentic archival B/W footage meets source-matched photographic AI reconstruction, ending with one openly AI-animated sequence. Historic sources from Wikimedia Commons. Technical preview — not a documentary color recording.\n",encoding="utf8")
 (ROOT/"README.txt").write_text("OWNER REVIEW ONLY - NOT APPROVED OR PUBLISHED. One authentic historical Barbershop film, five time-distinct original moving moments, 5 I2I source-locked photos and one single Vidu scene. Source scans and photo interpretations are not claims of exact historical skin/fabric colors. Inspect hand/face continuity before approving.\n")
 Z=ROOT/"FIRST_MOTION_1893_1894_ANDROID_KIT.zip"
 with zipfile.ZipFile(Z,"w",zipfile.ZIP_DEFLATED,compresslevel=3) as z:
  for p in [OUTVIDEO,ROOT/"SOCIAL_COVER.jpg",ROOT/"TECHNICAL_QA.json",ROOT/"SOURCES_AND_RIGHTS.json",ROOT/"VIDU_STATUS.json",ROOT/"README.txt",*[ROOT/("POST_"+s+".txt") for s in ("FACEBOOK","INSTAGRAM","TIKTOK","YOUTUBE")]]:
   z.write(p,arcname=p.name)
 with zipfile.ZipFile(Z) as z:assert z.testzip() is None
 say("REAL_NEW_MP4_ZIP_COMPLETED",sha(OUTVIDEO),stats.get("format",{}).get("duration"))
def main():
 say("START_FIRST_MOTION_FIVE_AUTHENTIC_SOURCES")
 metas=[source_download(spec) for spec in SRC]
 out("SOURCES_AND_RIGHTS.json",{"sources":metas,"licensing":"Wikimedia Commons public domain US; verify specific derivative and Italian reuse rights before publication","all_source_film_original_video":True,"unique_original_films":1,"not_5_independent_scenes":True})
 model,_=dd.download_model()
 client=Client("finegrain/finegrain-image-enhancer",verbose=False)
 photos=[restore(meta,model,client) for meta in metas]
 say("FIVE_PHOTOS_READY_SAME_EXACT_SOURCE_FRAMES")
 vidu=vidu_clip(photos[4],metas[4])
 assemble(metas,photos,vidu)
if __name__=="__main__":
 try:main()
 except Exception as e:
  out("FAILURE.json",{"error_type":type(e).__name__,"reason":str(e)[:400],
    "finished_video":False,"never_retry_paid_post":True,"artistic_approval":False})
  say("FIRST_MOTION_BLOCKED",type(e).__name__,str(e)[:250])
  raise
