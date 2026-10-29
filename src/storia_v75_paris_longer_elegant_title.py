#!/usr/bin/env python3
"""V75 correction: true original film motion -> exact source-frame freeze -> genuine AI photo."""
import json,hashlib,subprocess,wave,zipfile,importlib.util
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont

OUT=Path("output/storia_v75_paris");OUT.mkdir(parents=True,exist_ok=True)
SOURCE=OUT/"PELICOLA_PARIGI_ORIGINALE.webm"
VIDEO=OUT/"LA_STORIA_RIVIVE_PARIGI_1896_1900_V75.mp4"
SHOTS=[
 {"id":1,"sec":218.0,"center_x":620,"motion":3.22,"hold":3.58,"name":"Pompieri a cavallo"},
 {"id":2,"sec":300.0,"center_x":640,"motion":3.12,"hold":3.72,"name":"Esposizione Universale"},
 {"id":3,"sec":31.0,"center_x":600,"motion":3.14,"hold":3.68,"name":"Notre-Dame"}]
FPS,W,H=30,720,1280

def sha(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()

def run(cmd,timeout=180):
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError(str(cmd[:4])+" "+p.stderr[-1100:])
 return p.stdout

def crop(frame,center):
 h,w=frame.shape[:2];cw=round(h*9/16);x=max(0,min(w-cw,round(center-cw/2)))
 return frame[:,x:x+cw]

def grayscale(frame):
 return cv2.cvtColor(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR)


def cinematic_title(frame,t):
 # Elegant museum opening over the authentic moving B/W footage. Cities and years only.
 opacity=min(1.0,t/.48,max(0.0,(2.52-t)/.62))
 if opacity<=0:return frame
 pil=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)).convert("RGBA")
 layer=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(layer,"RGBA")
 try:
  serif=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",68)
  year=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",50)
  sans=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",22)
  small=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",19)
 except OSError:
  serif=ImageFont.load_default();year=serif;sans=serif;small=serif
 for yy in range(0,520,4):
  d.rectangle((0,yy,W,yy+4),fill=(5,8,13,int(125*opacity*max(0,1-(yy/530)**1.5))))
 def centered(text,font,y,col):
  box=d.textbbox((0,0),text,font=font);x=(W-(box[2]-box[0]))//2
  d.text((x,y),text,font=font,fill=col)
 gold=(235,213,169,int(244*opacity))
 white=(252,247,238,int(254*opacity))
 d.line((136,110,584,110),fill=(231,204,154,int(160*opacity)),width=2)
 centered("LA STORIA RIVIVE",sans,131,(236,229,213,int(246*opacity)))
 centered("PARIGI",serif,187,white)
 centered("1896 — 1900",year,292,gold)
 d.line((207,374,513,374),fill=(231,204,154,int(140*opacity)),width=2)
 centered("FILMATI D'EPOCA",small,401,(235,230,217,int(225*opacity)))
 return cv2.cvtColor(np.asarray(Image.alpha_composite(pil,layer).convert("RGB")),cv2.COLOR_RGB2BGR)

def make():
 records=json.loads((OUT/"PHOTO_QA.json").read_text())["photos"]
 for rec in records:
  i=rec["i"]
  if sha(OUT/("ORIGINAL_%02d.png"%i))!=rec["source_sha"]:raise RuntimeError("Original frame SHA mismatch")
  if sha(OUT/("FOTO_AI_%02d.png"%i))!=rec["photo_sha"]:raise RuntimeError("Original AI photo SHA mismatch")
 cap=cv2.VideoCapture(str(SOURCE))
 if not cap.isOpened() or cap.get(cv2.CAP_PROP_FRAME_COUNT)/cap.get(cv2.CAP_PROP_FPS)<350:raise RuntimeError("Wrong original archive film")
 silent=OUT/"VIDEO_MUTO.mp4"
 proc=subprocess.Popen(["ffmpeg","-nostdin","-y","-v","error","-f","rawvideo","-pix_fmt","bgr24","-s","720x1280",
 "-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p",str(silent)],
 stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 frames=0;cues=[];scenes=[]
 try:
  font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",41)
  small=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",20)
 except OSError:font=ImageFont.load_default();small=ImageFont.load_default()
 try:
  for shot_index,s in enumerate(SHOTS):
   i=s["id"];cues.append(frames/FPS)
   orig=cv2.imread(str(OUT/("ORIGINAL_%02d.png"%i)))
   photo=cv2.imread(str(OUT/("FOTO_AI_%02d.png"%i)))
   if orig is None or photo is None:raise RuntimeError("Missing actual photo")
   orig=grayscale(cv2.resize(orig,(W,H),interpolation=cv2.INTER_CUBIC))
   photo=cv2.resize(photo,(W,H))
   if i==3:
    hsv=cv2.cvtColor(photo,cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:,:,1]*=.88
    photo=cv2.cvtColor(np.clip(hsv,0,255).astype(np.uint8),cv2.COLOR_HSV2BGR)
   cap.set(cv2.CAP_PROP_POS_MSEC,(s["sec"]-s["motion"])*1000)
   motion_count=round(s["motion"]*FPS)
   for k in range(motion_count):
    ok,fr=cap.read()
    if not ok:raise RuntimeError("Missing actual film motion")
    im=grayscale(cv2.resize(crop(fr,s["center_x"]),(W,H),interpolation=cv2.INTER_CUBIC))
    if k>=motion_count-5:
     blend=(k-(motion_count-5)+1)/6
     im=cv2.addWeighted(im,1-blend,orig,blend,0)
    if shot_index==0 and k<round(2.52*FPS):
     im=cinematic_title(im,k/FPS)
    proc.stdin.write(im.tobytes());frames+=1
   # Freeze the EXACT source-image, not a similar or invented replacement.
   for _ in range(5):proc.stdin.write(orig.tobytes());frames+=1
   reveal=9
   for k in range(reveal):
    a=(k+1)/reveal;a=a*a*(3-2*a)
    proc.stdin.write(cv2.addWeighted(orig,1-a,photo,a,0).tobytes());frames+=1
   hold=round(s["hold"]*FPS)
   for k in range(hold):
    frame=photo
    if shot_index==len(SHOTS)-1 and k>=hold-12:
     fade=(k-(hold-12)+1)/12
     frame=cv2.addWeighted(photo,1-fade,np.zeros_like(photo),fade,0)
    proc.stdin.write(frame.tobytes());frames+=1
   scenes.append({"scene":s["name"],"original_time":s["sec"],"real_BW_motion_frames":motion_count,
                  "AI_reveal_frames":reveal,"freeze_photo_frames":hold,
                  "source_sha":sha(OUT/("ORIGINAL_%02d.png"%i)),
                  "actual_AI_photo_sha":sha(OUT/("FOTO_AI_%02d.png"%i))})
   print("V75_REAL_VIDEO_SCENE",s["name"],frames,flush=True)
 finally:
  cap.release();proc.stdin.close();err=proc.stderr.read().decode(errors="replace")
  if proc.wait():raise RuntimeError("ffmpeg pipe error "+err[-1200:])
 dur=frames/FPS
 # Original synthetic score from warm, restrained strings/piano tones. No soundtrack samples.
 sr=32000;t=np.arange(round(sr*dur),dtype=np.float32)/sr;v=np.zeros_like(t)
 chords=[[130.81,164.81,196,261.63],[146.83,174.61,220,293.66],[130.81,196,246.94,329.63]]
 for j,start in enumerate(cues):
  end=cues[j+1] if j+1<len(cues) else dur
  m=(t>=start)&(t<end);q=t[m]-start;z=np.zeros_like(q)
  for k,f in enumerate(chords[j]):
   z+=(0.010+.0015*k)*(np.sin(2*np.pi*f*q+k*.23)+.14*np.sin(2*np.pi*2.002*f*q+k*.3))
   for at in (.12,1.12,2.2,3.42):
    dt=q-at;on=(dt>=0)&(dt<1.6)
    z[on]+=.010*np.sin(2*np.pi*f*2*dt[on]+k*.25)*np.exp(-3.5*dt[on])
  tt=q-SHOTS[j]["motion"];gate=(tt>=0)&(tt<.75)
  z[gate]+=.038*np.sin(2*np.pi*(180*tt[gate]+70*tt[gate]**2))*np.exp(-7*tt[gate])
  v[m]+=z
 v*=np.minimum(1,t/.7)*np.minimum(1,(dur-t)/1.0)
 v=np.tanh(v*2.5)
 audio=OUT/"MUSICA_ORIGINALE.wav"
 with wave.open(str(audio),"wb") as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr)
  stereo=np.column_stack((v,np.roll(v,int(sr*.014))*.93))
  w.writeframes((np.clip(stereo,-1,1)*18000).astype("<i2").tobytes())
 run(["ffmpeg","-nostdin","-y","-v","error","-i",str(silent),"-i",str(audio),
 "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","160k",
 "-t",str(dur),"-movflags","+faststart",str(VIDEO)],100)
 run(["ffmpeg","-v","error","-xerror","-i",str(VIDEO),"-f","null","-"],100)
 spec=importlib.util.spec_from_file_location("gate","src/storia_rivive_v74_effect_gate.py")
 gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
 review=gate.inspect_video(VIDEO)
 if review["approved_pattern_cycles"]<3:raise RuntimeError("V75 reference artistic pattern FAILS: "+str(review))
 cover=OUT/"COPERTINA.jpg"
 Image.open(OUT/"FOTO_AI_02.png").convert("RGB").save(cover,quality=94)
 posts={
 "FACEBOOK":"Parigi, oltre 120 anni fa. Tre veri istanti d'epoca si fermano per diventare fotografie a colori ricostruite digitalmente. Riprese autentiche, dettagli e colori interpretati dall'AI. #LaStoriaRivive",
 "INSTAGRAM":"PARIGI 1896–1900 · Il tempo si ferma. Film autentico e fotografie AI. #HistoryReels #Paris1900",
 "TIKTOK":"Parigi oltre un secolo fa, in movimento. Poi per un attimo il passato diventa una fotografia a colori. #storia #parigi",
 "YOUTUBE":"PARIGI 1896–1900 | La Storia Rivive\nLe riprese storiche autentiche si congelano sugli stessi fotogrammi, ricostruiti come fotografie AI a colori. Colori e dettagli sono interpretazioni. Fonte: Wikimedia Commons / Lumière."
 }
 for k,body in posts.items():(OUT/("POST_"+k+".txt")).write_text(body+"\n",encoding="utf8")
 qa={"version":"V75","source":"https://commons.wikimedia.org/wiki/File:A_Trip_Through_Paris,_France,_Late_1890s.webm",
     "source_sha256":sha(SOURCE),"video":VIDEO.name,"video_sha256":sha(VIDEO),
     "duration_s":round(dur,2),"opening_title":"PARIGI 1896—1900 for first 2.52s of real moving B/W footage","scenes":scenes,"reference_effect_gate":review,
     "real_moving_source":True,"true_freeze_AI_photos":3,"human_artistic_review":"REQUIRED",
     "zero_paid_credits":True,"published_to_social":False,"published_to_private_site":False}
 (OUT/"FONTI_E_QA.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2))
 kit=OUT/"PARIGI_1896_1900_VIDEO_COMPLETO_V75.zip"
 with zipfile.ZipFile(kit,"w",compression=zipfile.ZIP_DEFLATED) as z:
  for p in [VIDEO,cover,OUT/"FONTI_E_QA.json",*[OUT/("POST_"+k+".txt") for k in posts]]:z.write(p,p.name)
 with zipfile.ZipFile(kit) as z:
  if z.testzip():raise RuntimeError("Corrupt ZIP")
 print("V75_LONGER_ELEGANT_OPENING_MP4_VERIFIED",VIDEO,VIDEO.stat().st_size,"zip",kit,flush=True)

if __name__=="__main__":make()
