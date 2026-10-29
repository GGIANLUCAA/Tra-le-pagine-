#!/usr/bin/env python3
"""La Storia Rivive V83: 4 authentic-film-to-AI-photo scenes + 1 real Vidu video.
A technical montage uses existing paid output only; no Vidu API calls in this file.
For production, enforce the V83 color/motion gates and obtain approval per paid clip.
"""
from __future__ import annotations
import hashlib,json,math,os,subprocess,sys,wave,zipfile
from pathlib import Path
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path("output/storia_ibrida_v83")
ASSETS=ROOT/"assets"
OUT=ROOT/"delivery"
OUT.mkdir(parents=True,exist_ok=True)
FPS,W,H=30,720,1280
V65=ASSETS/"PARIGI_1918_IL_TEMPO_SI_FERMA_V65.mp4"
V76=ASSETS/"LA_STORIA_RIVIVE_SOCIAL_MUSEUM_V76.mp4"
VIDU=ASSETS/"VIDU_TRANSIZIONE_ORIGINALE.mp4"
V68_NAMES=[f"FOTO_AI_RICOSTRUITA_{n:02d}.png" for n in range(1,5)]
SCENES=[
 {"name":"newspaper vendor","offset":0.00,"motion":1.56,"photo":V68_NAMES[0]},
 {"name":"railway station","offset":4.55,"motion":1.58,"photo":V68_NAMES[1]},
 {"name":"cinema street crowd","offset":8.77,"motion":1.35,"photo":V68_NAMES[2]},
 {"name":"Paris tram","offset":12.56,"motion":1.48,"photo":V68_NAMES[3]}]
POLICY={
 "version":"V83","mix":"4 classical V82 + 1 Vidu real moving video",
 "demo_era_range":"PARIS 1900–1918","single_era_production":True,
 "format":"vertical 9:16","fps":FPS,"size":[W,H],
 "bw_real_motion_first":True,"photo_true_ai_reconstruction":True,
 "vidu_color_reveal_within_s":1.15,"vidu_color_motion_after_s":1.15,
 "vidu_recommended_seconds":5,"no_new_vidu_calls":True,
 "no_duplicate_footage":True,"seamless_audio":True,
 "zero_automatic_publication":True,"artistic_review_required":True
}
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
 return h.hexdigest()
def run(argv,timeout=200):
 p=subprocess.run(argv,capture_output=True,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError("Command failed: "+" ".join(map(str,argv[:6]))+" "+p.stderr[-1300:])
 return p.stdout
def info(path):
 if not path.is_file() or path.stat().st_size<10000:raise RuntimeError("MISSING_SOURCE "+str(path))
 d=json.loads(run(["ffprobe","-v","error","-show_entries","format=duration,size:stream=codec_name,width,height,r_frame_rate","-of","json",str(path)]))
 vids=[x for x in d["streams"] if x.get("codec_name") not in ("aac","mp3") and x.get("width")]
 if not vids:raise RuntimeError("VIDEO_STREAM_MISSING "+str(path))
 return d,vids[0]
def norm(frame):
 return cv2.resize(frame,(W,H),interpolation=cv2.INTER_AREA)
def gray(im):
 return cv2.cvtColor(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR)
def statsat(im):
 h=cv2.cvtColor(cv2.resize(im,(180,320)),cv2.COLOR_BGR2HSV)
 return float(np.median(h[:,:,1]))
def corr(a,b):
 def v(im):
  g=cv2.cvtColor(cv2.resize(im,(72,128)),cv2.COLOR_BGR2GRAY)
  return cv2.GaussianBlur(g,(9,9),0).astype("float32").ravel()
 x=v(a);y=v(b)
 return float(np.corrcoef(x,y)[0,1])
def at(path,second):
 c=cv2.VideoCapture(str(path));c.set(cv2.CAP_PROP_POS_MSEC,second*1000);ok,f=c.read();c.release()
 if not ok:raise RuntimeError("NO_FRAME "+str(path)+" "+str(second))
 return norm(f)
def frames(path,start,length,outfps=FPS):
 cap=cv2.VideoCapture(str(path))
 native=cap.get(cv2.CAP_PROP_FPS)
 if not 10<native<100:raise RuntimeError("INVALID_NATIVE_FPS")
 cap.set(cv2.CAP_PROP_POS_MSEC,max(0,start)*1000)
 results=[]
 prev_idx=-1;cached=None
 count=round(length*outfps)
 for k in range(count):
  idx=round(k*native/outfps)
  if idx!=prev_idx:
   for _ in range(idx-prev_idx):
    ok,cached=cap.read()
    if not ok:raise RuntimeError("TRUNCATED_REAL_MOTION "+str(path))
   prev_idx=idx
  results.append(norm(cached))
 cap.release()
 return results
def validate_inputs():
 d65,s65=info(V65);d76,s76=info(V76);dv,sv=info(VIDU)
 if (s65["width"],s65["height"])!=(1080,1920):raise RuntimeError("V65_RASTER_MISMATCH")
 if (s76["width"],s76["height"])!=(W,H) or (sv["width"],sv["height"])!=(W,H):raise RuntimeError("R2_RASTER_MISMATCH")
 if not 4.95<float(dv["format"]["duration"])<6.2:raise RuntimeError("VIDU_NOT_5S")
 if len(set(V68_NAMES))!=4:raise RuntimeError("DUPLICATE_PHOTOS")
 imgs=[]
 for i,n in enumerate(V68_NAMES):
  p=ASSETS/n
  if not p.exists() or p.stat().st_size<100000:raise RuntimeError("MISSING_REAL_GENERATIVE_PHOTO "+n)
  pic=cv2.imread(str(p))
  if pic is None or pic.shape[:2]!=(1920,1080):raise RuntimeError("WRONG_PHOTO_DIMENSIONS")
  imgs.append(norm(pic))
 if len({sha(ASSETS/n) for n in V68_NAMES})!=4:raise RuntimeError("PHOTO_SHA_DUPLICATED")
 return imgs,dv
def analyze_vidu(vdur):
 # Probe true colored moving frames, rather than judging a single still.
 metrics=[]
 previous=None
 for t in np.arange(.2,min(vdur-.1,5),.4):
  f=at(VIDU,float(t))
  g=cv2.cvtColor(cv2.resize(f,(180,320)),cv2.COLOR_BGR2GRAY)
  d=None if previous is None else round(float(np.mean(np.abs(g.astype("float32")-previous.astype("float32")))),3)
  metrics.append({"t":round(float(t),2),"median_saturation":round(statsat(f),2),"frame_change":d})
  previous=g
 samples=[m for m in metrics if 1.15<=m["t"]<=4.5]
 changed=[m["frame_change"] for m in samples if m["frame_change"] is not None]
 # Color should become evident by ~1 s, remain vivid, and movement continue after reveal.
 early=[m["median_saturation"] for m in metrics if 1<=m["t"]<=1.6]
 full=[m["median_saturation"] for m in metrics if 2.0<=m["t"]<=4.5]
 early_ok=bool(early) and max(early)>=19
 sustained=bool(full) and min(full)>=17
 movement=bool(changed) and sum(z>=.9 for z in changed)>=max(3,len(changed)//2)
 return {"samples":metrics,"first_second_color_pass":early_ok,
  "sustained_color_pass":sustained,"sustained_motion_pass":movement,
  "production_gate_pass":early_ok and sustained and movement}
def textframe(frame,t):
 if t>1.55:return frame
 from PIL import Image
 rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
 out=Image.fromarray(rgb).convert("RGBA");mask=Image.new("RGBA",(W,H),(0,0,0,0))
 d=ImageDraw.Draw(mask)
 fade=max(0,min(1,t/.27,(1.55-t)/.30))
 d.rectangle((0,100,W,330),fill=(8,12,17,round(110*fade)))
 try:
  big=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",62)
  small=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",31)
 except OSError:
  big=ImageFont.load_default();small=big
 d.text((105,151),"PARIS",font=big,fill=(255,250,240,round(252*fade)))
 d.text((114,239),"1900–1918",font=small,fill=(245,210,166,round(240*fade)))
 return cv2.cvtColor(np.array(Image.alpha_composite(out,mask).convert("RGB")),cv2.COLOR_RGB2BGR)
def soundtrack(seconds,beats,path):
 sr=32000
 t=np.arange(int(seconds*sr),dtype="float32")/sr
 sound=np.zeros_like(t)
 base=[130.81,164.81,196.,261.63]
 for k,hz in enumerate(base):
  sound+=(0.020-0.002*k)*np.sin(2*np.pi*hz*t+k*.31)*(0.88+0.12*np.sin(.6*t+k))
  sound+=.002*np.sin(2*np.pi*(hz*2.002)*t)
 # One continuous musical phrase; low-volume accents emphasize the photographic reveals.
 for beat in beats:
  u=t-float(beat)
  mask=(u>=0)&(u<.55)
  sound[mask]+=.024*np.sin(2*np.pi*(100*u[mask]+80*u[mask]**2))*np.exp(-8*u[mask])
 env=np.minimum(1,t/.6)*np.minimum(1,np.maximum(0,(seconds-t)/1.1))
 sound=np.tanh(sound*2)*env
 pair=np.column_stack([sound,np.roll(sound,int(.013*sr))*.94])
 with wave.open(str(path),"wb") as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr)
  w.writeframes((np.clip(pair,-1,1)*18000).astype("<i2").tobytes())
def make_preview(preview=True):
 photos,vmeta=validate_inputs()
 quality=analyze_vidu(float(vmeta["format"]["duration"]))
 if not preview and not quality["production_gate_pass"]:
  raise RuntimeError("VIDU_PREMIUM_MOTION_REJECTED: old clip remains a slow photo morph; do not label it the new moving-color preset")
 # A sample montage is deliberately marked as not approved: Vidu = 1900; classic photos = 1918.
 original=at(V76,16.08)
 first=at(VIDU,.0)
 first_match=corr(original,first)
 if first_match<.90:raise RuntimeError("VIDU_START_FRAME_DOES_NOT_MATCH_HISTORIC_FRAME "+str(first_match))
 silent=OUT/"TEMP_V83.mp4"
 command=["ffmpeg","-nostdin","-y","-v","error","-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
 "-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p","-movflags","+faststart",str(silent)]
 pipe=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 count=0;scenes=[];beats=[]
 def emit(frame):
  nonlocal count
  if frame.shape[:2]!=(H,W):raise RuntimeError("FRAME_GEOMETRY_INVALID")
  pipe.stdin.write(frame.tobytes());count+=1
 try:
  # Actual monochrome moving source leads directly to the exact first Vidu image.
  begin=count/FPS
  lead=frames(V76,15.16,.92)
  for f in lead:
   emit(textframe(gray(f),count/FPS))
  vdur=float(vmeta["format"]["duration"])
  vidu_frames=frames(VIDU,0,vdur)
  for f in vidu_frames:emit(textframe(f,count/FPS))
  scenes.append({"name":"1900 moving walkway / color-motion Vidu","mode":"vidu",
     "start_s":round(begin,3),"end_s":round(count/FPS,3),
     "vidu_original_sha256":sha(VIDU),"start_match_corr":round(first_match,4),
     "source_video":"V76 documentary archival source frame","color_motion_QA":quality})
  # Historical chapters from the SAME 1918 source (four different authentic shots).
  for index,(s,pic) in enumerate(zip(SCENES,photos),1):
   begin=count/FPS
   motion=frames(V65,s["offset"],s["motion"])
   monochrome=[gray(f) for f in motion]
   if statsat(monochrome[-1])>9:raise RuntimeError("SOURCE_SHOT_NOT_BW")
   if float(np.mean(np.abs(monochrome[0].astype("float32")-monochrome[-1].astype("float32"))))<1.0:
    raise RuntimeError("NO_AUTHENTIC_FILM_MOTION_"+str(index))
   for f in monochrome:emit(f)
   freeze=monochrome[-1]
   source_corr=corr(freeze,pic)
   if source_corr<.61:raise RuntimeError(f"PHOTO_NOT_SOURCE_MATCHED_SCENE_{index}_CORR_{source_corr:.3f}")
   for _ in range(2):emit(freeze)
   nfade=8
   for k in range(nfade):
    a=(k+1)/nfade;a=a*a*(3-2*a)
    emit(cv2.addWeighted(freeze,1-a,pic,a,0))
   beats.append(count/FPS)
   for _ in range(round(2.1*FPS)):emit(pic)
   scenes.append({"name":s["name"],"mode":"classic_free_AI_photo",
       "start_s":round(begin,3),"end_s":round(count/FPS,3),
       "bw_archive_motion_s":s["motion"],"source_start_in_V65_s":s["offset"],
       "actual_still_sha256":sha(ASSETS/s["photo"]),"source_photo_frame_match_corr":round(source_corr,3)})
   print("V83_CLASSIC_SHOT",index,s["name"],"photo_match",round(source_corr,3),flush=True)
 finally:
  pipe.stdin.close();err=pipe.stderr.read().decode(errors="replace")
  if pipe.wait()!=0:raise RuntimeError("V83_ENCODER_FAILED "+err[-1300:])
 duration=count/FPS
 audio=OUT/"ORIGINAL_SCORE.wav"
 soundtrack(duration,beats,audio)
 video=OUT/"PARIS_1900_1918_HYBRID_4PLUS1_V83_TECHNICAL_PREVIEW.mp4"
 run(["ffmpeg","-nostdin","-y","-v","error","-i",str(silent),"-i",str(audio),
      "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","160k",
      "-shortest","-movflags","+faststart",str(video)],100)
 run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(video),"-f","null","-"],130)
 if len(scenes)!=5 or sum(s["mode"]=="vidu" for s in scenes)!=1:raise RuntimeError("NOT_FIVE_SCENES_4PLUS1")
 if not 17<duration<28:raise RuntimeError("UNEXPECTED_PACING "+str(duration))
 cover=OUT/"COPERTINA.jpg"
 im=Image.open(ASSETS/V68_NAMES[0]).convert("RGB").resize((W,H))
 d=ImageDraw.Draw(im,"RGBA");d.rounded_rectangle((28,35,690,204),radius=14,fill=(8,10,17,165))
 try:font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",50)
 except:font=ImageFont.load_default()
 d.text((60,60),"PARIS 1900–1918",font=font,fill=(252,240,218,255));im.save(cover,quality=95)
 posts={
 "FACEBOOK":"Parigi, 1900–1918. Un momento prende vita a colori, altri quattro veri spezzoni d’epoca si fermano per diventare fotografie moderne ricostruite. Un esperimento ibrido fra pellicola autentica e AI. Colori, volti e movimento Vidu sono interpretazioni digitali, non documenti originali.",
 "INSTAGRAM":"PARIS · 1900–1918 🎞️ Quattro restauri fotografici e un unico istante che si anima con Vidu. Riprese d’epoca, dettagli interpretativi AI. #LaStoriaRivive",
 "TIKTOK":"Un vecchio film diventa una scena viva a colori. Poi quattro fotografie restaurate della Parigi storica. #History #Paris",
 "YOUTUBE":"PARIS 1900–1918 | La Storia Rivive · 4+1 Hybrid preview\n\nPilota tecnico: 4 scene tratte dal film del 1918 e una ricostruzione Vidu del 1900. Film d'archivio da fonti dichiarate PD/CC0 nel progetto, originali storici in movimento, quattro fotografie AI e un video sintetico. Le due epoche sono diverse: non è un unico piano sequenza reale né colori originali.\nRevisione artistica e diritti per la pubblicazione social ancora necessari."}
 for k,v in posts.items():(OUT/f"POST_{k}.txt").write_text(v+"\n",encoding="utf8")
 qa={"version":"V83","status":"TECHNICAL_PREVIEW_NOT_ARTISTICALLY_APPROVED",
     "provenance_historic_1918":"https://github.com/GGIANLUCAA/Tra-le-pagine-/releases/tag/storia-rivive-parigi-1918-photo-freeze-v65",
     "provenance_historic_1900":"https://commons.wikimedia.org/wiki/File:A_Trip_Through_Paris,_France,_Late_1890s.webm",
     "source_era_warning":"1900 and 1918 mixed intentionally only for integration demo; future production requires coherent date and location",
     "source_vidu":"existing approved single generation on 2026-10-29; no new credits",
     "vidu_job_id":"1013429649004335104","vidu_motion_result":quality,
     "warning":"Old Vidu clip does not necessarily satisfy 1-second color-reveal and sustained motion; production gate is strict",
     "source_validated_sha256":{"V65":sha(V65),"V76":sha(V76),"VIDU":sha(VIDU),**{n:sha(ASSETS/n) for n in V68_NAMES}},
     "duration_s":round(duration,3),"frames":count,"resolution":[W,H],"fps":FPS,
     "video_sha256":sha(video),"video_bytes":video.stat().st_size,
     "sources_exact_film_scenes":True,"five_chapters":scenes,"no_duplicate_generated_credit":True,
     "4_classic_photos_used":True,"1_real_vidu_mp4_used":True,
     "rights_italy_final_review":"PENDING","identity_review":"PENDING_HUMAN",
     "artistic_review":"PENDING","social_published":False,"website_published":False}
 (OUT/"QA_V83.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 zfile=OUT/"PARIS_V83_HYBRID_ANDROID.zip"
 with zipfile.ZipFile(zfile,"w",zipfile.ZIP_DEFLATED) as z:
  for path in [video,cover,OUT/"QA_V83.json",*[OUT/f"POST_{k}.txt" for k in posts]]:
   z.write(path,path.name)
 with zipfile.ZipFile(zfile) as z:
  if z.testzip():raise RuntimeError("CORRUPT_DELIVERY_ZIP")
 print("V83_FIVE_SCENE_TECHNICAL_PREVIEW",video,video.stat().st_size,"length",duration,"strict_quality",quality["production_gate_pass"],flush=True)
if __name__=="__main__":
 try:make_preview(preview=os.environ.get("V83_MODE","preview")=="preview")
 except Exception as e:
  print("V83_HYBRID_FAILED",type(e).__name__,str(e),file=sys.stderr,flush=True)
  raise
