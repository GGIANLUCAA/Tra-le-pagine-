#!/usr/bin/env python3
"""Barbershop 1894 compact genuine archival short: two source-locked I2I plus one Vidu motion continuation; owner review only."""
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
 ("barber01","The Barbershop (1894).webm",1894,2.0,1.5,3.0,"1894 Edison barbershop customer, preserve face, hat, barber and all furnishings without invention."),
 ("barber02","The Barbershop (1894).webm",1894,4.3,1.5,3.0,"1894 Edison barber and customer, authentic hand positions, shaving gesture, period environment and human faces.")
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
 p=ROOT/"BARBERSHOP_VERIFIED_ARCHIVAL_SOURCE.mp4"
 if not p.exists():
  cmd(["gh","release","download","storia-barbershop-1894-source-scout-42649779508",
       "--repo",REPO,"-p","ARCHIVAL_MOVING_SCOUT_NOT_RESTORED.mp4","-D",str(ROOT)],timeout=100)
  orig=ROOT/"ARCHIVAL_MOVING_SCOUT_NOT_RESTORED.mp4"
  if not orig.is_file():raise RuntimeError("REAL_SOURCE_UNAVAILABLE")
  orig.rename(p)
 if p.stat().st_size<500000:raise RuntimeError("ORIGINAL_FILM_FILE_TOO_SMALL")
 cap=cv2.VideoCapture(str(p))
 fps=cap.get(cv2.CAP_PROP_FPS)
 duration=cap.get(cv2.CAP_PROP_FRAME_COUNT)/max(1,fps)
 if not (t>bw and t<duration-.4):raise RuntimeError("SOURCE_ANCHOR_OUTSIDE_FILM")
 cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,frame=cap.read()
 # Verify no black leader at source anchor and at the starting moving moment.
 if not ok:raise RuntimeError("SOURCE_ANCHOR_NOT_READABLE")
 g=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
 if g.mean()<23 or g.std()<13:raise RuntimeError("SOURCE_ANCHOR_BLACK_OR_LOW_DETAIL_NO_VIDU")
 cap.set(cv2.CAP_PROP_POS_MSEC,(t-bw+.15)*1000)
 ok,early=cap.read()
 if not ok:raise RuntimeError("SOURCE_BW_MOTION_MISSING")
 early_g=cv2.cvtColor(early,cv2.COLOR_BGR2GRAY)
 # A dark early frame is a diagnostic, not permission to reconstruct nonexistent footage.
 if early_g.mean()<12 or early_g.std()<8:raise RuntimeError("SOURCE_BW_OPENING_BLACK_NO_VIDU")
 w=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));h=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
 cap.release()
 frame=cv2.resize(frame,(960,720),interpolation=cv2.INTER_AREA)
 jpg=ROOT/(id+"_exact_bw.png")
 cv2.imwrite(str(jpg),frame)
 return {"id":id,"name":name,"year":year,"second":t,
  "path":str(p),"sha256":sha(p),"image_sha256":sha(jpg),
  "source_page":"https://commons.wikimedia.org/wiki/File:The_Barbershop_(1894).webm",
  "verified_release":"https://github.com/"+REPO+"/releases/tag/storia-barbershop-1894-source-scout-42649779508",
  "seconds":duration,"native_width":w,"native_height":h}

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
 # Gentle emphasis at each exact frame-to-photo reveal.
 for sec in [SRC[0][4],SRC[0][4]+SRC[0][5]+SRC[1][4]]:
  o=int(sec*sr);L=min(n-o,int(.36*sr))
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
  id,_,year,t,bw,hold,_=spec
  t=meta["second"]
  for n in range(round(bw*FPS)):
   f=canvas(video_frame(meta["path"],max(.05,t-bw+n/FPS)),
            "THE BARBERSHOP  ·  1894" if i==0 and n<20 else None)
   writer.write(f)
  bwframe=canvas(cv2.imread(str(ROOT/(id+"_exact_bw.png"))))
  colorframe=canvas(photo)
  ramp=5
  for n in range(ramp):
   a=(n+1)/ramp;a=a*a*(3-2*a)
   writer.write(cv2.addWeighted(bwframe,1-a,colorframe,a,0))
  for _ in range(round(hold*FPS)-ramp):
   writer.write(colorframe)
  timeline.append({"name":id,"bw_motion_s":bw,"photo_color_hold_s":hold,
   "source_timecode_s":t,"original_film_sha256":meta["sha256"],
   "I2I_real_photo_sha256":sha(ROOT/(id+"_I2I_RESTORED.png"))})
 # Continue directly from the second reconstructed historical frame into a 5s Vidu motion.
 normalized=ROOT/"VIDU_FULL_FIVE_SECONDS_24FPS.mp4"
 cmd(["ffmpeg","-nostdin","-y","-v","error","-i",str(clip),"-t","5","-vf","fps=24,scale=720:1280",
      "-an","-c:v","libx264","-preset","fast","-crf","18","-pix_fmt","yuv420p",str(normalized)],timeout=200)
 c=cv2.VideoCapture(str(normalized))
 vidu_count=0
 while vidu_count<int(5.0*FPS):
  ok,frame=c.read()
  if not ok:break
  if frame.shape[:2]!=(H,W):frame=cv2.resize(frame,(W,H))
  # Preserve the already displayed color; no reset to black-and-white at scene continuity.
  writer.write(frame);vidu_count+=1
 c.release();writer.release()
 if vidu_count<115:raise RuntimeError("VIDU_FULL_MOTION_5SEC_NOT_RECOVERED")
 timeline.append({"name":"barber02_vidu_continuation","color_motion_s":vidu_count/FPS,
                  "source_timecode_s":metas[1]["second"],
                  "source_photo_sha256":sha(ROOT/"barber02_I2I_RESTORED.png")})
 video_duration=sum(v.get("bw_motion_s",0)+v.get("photo_color_hold_s",0)+v.get("color_motion_s",0) for v in timeline)
 if not 13.8<=video_duration<=25:raise RuntimeError("VIDEO_RHYTHM_OR_DURATION_UNEXPECTED")
 music=create_original_sound(video_duration)
 cmd(["ffmpeg","-nostdin","-y","-v","error","-i",str(partial),"-i",str(music),"-shortest",
     "-c:v","libx264","-preset","fast","-crf","19","-pix_fmt","yuv420p",
     "-c:a","aac","-b:a","160k","-movflags","+faststart",str(OUTVIDEO)],timeout=320)
 cmd(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(OUTVIDEO),"-f","null","-"],timeout=250)
 stats=json.loads(cmd(["ffprobe","-v","error","-show_entries","format=duration:stream=codec_name,width,height,r_frame_rate","-of","json",str(OUTVIDEO)]))
 report={"genuine_new_composition":True,"new_historical_original_films":1,
  "different_real_film_moments":2,"new_finegrain_restorations":2,
  "real_vidu_clip_produced":True,"project_format":"ONE_SOURCE_TWO_I2I_ONE_VIDU_SHORT_PREVIEW_NOT_4PLUS1",
  "timeline":timeline,"video_sha256":sha(OUTVIDEO),"ffprobe":stats,
  "source_locked_photo_qa":"AUTOMATED_ONLY","human_identity_review":"PENDING",
  "artistic_approval":False,"social_published":False,
  "disclosure":"AI colors, photo detail and Vidu movement are modern interpretation; NOT original recorded color"}
 out("TECHNICAL_QA.json",report)
 make_cover(photos[1])
 for platform in ("FACEBOOK","INSTAGRAM","TIKTOK","YOUTUBE"):
  (ROOT/("POST_"+platform+".txt")).write_text("THE BARBERSHOP · 1894\nA moment from the dawn of cinema. Original moving film by Edison and Dickson, restored through source-matched color photographs and a short AI-animated continuation. Experimental review, not original historical color footage.\n",encoding="utf8")
 (ROOT/"README.txt").write_text("OWNER REVIEW ONLY; NOT APPROVED OR PUBLISHED. Two genuine source film moments, two new source-locked Finegrain photos and one Vidu animated continuation from EXACT PHOTO 2. Rights and artistic face fidelity review pending. No claim of five independent scenes.\n",encoding="utf8")
 zfile=ROOT/"FIRST_MOTION_1893_1894_ANDROID_KIT.zip"
 with zipfile.ZipFile(zfile,"w",zipfile.ZIP_DEFLATED,compresslevel=3) as z:
  for p in [OUTVIDEO,ROOT/"SOCIAL_COVER.jpg",ROOT/"TECHNICAL_QA.json",
            ROOT/"SOURCES_AND_RIGHTS.json",ROOT/"VIDU_STATUS.json",ROOT/"README.txt",
            *[ROOT/("POST_"+k+".txt") for k in ("FACEBOOK","INSTAGRAM","TIKTOK","YOUTUBE")]]:
   z.write(p,arcname=p.name)
 with zipfile.ZipFile(zfile) as z:assert z.testzip() is None
 say("BARBERSHOP_NEW_REVIEW_MP4_ZIP_COMPLETED",sha(OUTVIDEO),stats.get("format",{}).get("duration"))

def main():
 say("START_THE_BARBERSHOP_1894_SOURCE_AUTHENTIC_COMPACT_REEL")
 metas=[source_download(spec) for spec in SRC]
 out("SOURCES_AND_RIGHTS.json",{"sources":metas,
  "licensing":"Wikimedia public-domain source; verify Italy and any derivative rights before publication",
  "original_film_count":1,"new_moving_footage_preserved":True,"historical_identity_approval":False})
 model,_=dd.download_model()
 client=Client("finegrain/finegrain-image-enhancer",verbose=False)
 photos=[restore(meta,model,client) for meta in metas]
 say("TWO_FRESH_SOURCE_LOCKED_PHOTOS_READY_NO_SPENDING_YET")
 # The second photo is used as the exact initial condition of the final moving Vidu scene.
 clip=vidu_clip(photos[1],metas[1])
 assemble(metas,photos,clip)
if __name__=="__main__":
 try:main()
 except Exception as e:
  out("FAILURE.json",{"error_type":type(e).__name__,"reason":str(e)[:400],
    "finished_video":False,"never_retry_paid_post":True,"artistic_approval":False})
  say("FIRST_MOTION_BLOCKED",type(e).__name__,str(e)[:250])
  raise
