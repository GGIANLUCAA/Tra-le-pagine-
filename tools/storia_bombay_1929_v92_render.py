#!/usr/bin/env python3
"""La Storia Rivive V92.1: Bombay January 1929 (8 authentic shots + 8 ONNX neural AI photo stills).
Fails closed if source missing, source frame mismatch, color missing, duplicate scenes, or bad video.
NO billable Vidu, no HF quota, no fabricated faces, no auto-publication.
"""
import os,sys,math,json,hashlib,subprocess,pathlib,zipfile,urllib.request,wave,io,importlib.util
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageEnhance
ROOT=pathlib.Path("output/storia_bombay_1929_v92")
ROOT.mkdir(parents=True,exist_ok=True)
SRC=ROOT/"BOMBAY_1929_ORIGINAL.webm"
URL="https://commons.wikimedia.org/wiki/Special:Redirect/file/Street_Scenes_in_Bombay%2C_India_%28real_sound%29%2C_Jan_1929.webm"
SOURCE_PAGE="https://commons.wikimedia.org/wiki/File:Street_Scenes_in_Bombay,_India_(real_sound),_Jan_1929.webm"
KNOWN_SHA="04f87708e8029c85cbf62baa42db5b825b3d0d6613c4f2e452129526e35430d4"
W,H,FPS=720,1280,24
# Subject-first edits selected from 64 *actual* source frames. No duplicate cropped source shot.
SHOTS=[
 {"t":84.5,"x":630,"kind":"face","label":"Fruit-seller and first human face","motion":.72,"transition":.27,"hold":1.88},
 {"t":537.7,"x":643,"kind":"wide","label":"Crowd in front of landmark corner building","motion":1.12,"transition":.38,"hold":1.79},
 {"t":285.9,"x":675,"kind":"action","label":"Man carrying immense woven load through market","motion":.92,"transition":.34,"hold":1.94},
 {"t":512.5,"x":637,"kind":"detail","label":"Harbor workers handling bundles and goods","motion":.94,"transition":.32,"hold":1.68},
 {"t":613.2,"x":620,"kind":"wide","label":"Street traders under building balconies","motion":1.10,"transition":.41,"hold":1.93},
 {"t":751.7,"x":652,"kind":"action","label":"Horse cart outside monumental stone entrance","motion":1.17,"transition":.36,"hold":1.90},
 {"t":223.0,"x":640,"kind":"action","label":"Merchants walking through the crowded market","motion":.84,"transition":.31,"hold":2.12},
 {"t":399.2,"x":645,"kind":"climax","label":"Smiling men speaking together facing the camera","motion":1.08,"transition":.48,"hold":2.35},
]
def run(args,timeout=250):
 r=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
 if r.returncode:raise RuntimeError("Command failed "+str(args[:5])+" "+r.stderr[-1400:])
 return r.stdout
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()
def writej(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf8")
def check_source():
 if not SRC.exists() or SRC.stat().st_size<120000000:
  req=urllib.request.Request(URL,headers={"User-Agent":"TraLePagine/HistoryV92"})
  with urllib.request.urlopen(req,timeout=180) as r,open(SRC,"wb") as f:
   while data:=r.read(1024*1024):
    f.write(data)
    if f.tell()>160000000:raise RuntimeError("source oversized")
 if sha(SRC)!=KNOWN_SHA:raise RuntimeError("REAL SOURCE HASH CHANGED: do not use a different film")
 cap=cv2.VideoCapture(str(SRC))
 width,height,framerate=cap.get(3),cap.get(4),cap.get(5)
 duration=cap.get(7)/framerate
 cap.release()
 if int(width)!=1280 or int(height)!=720 or duration<800:raise RuntimeError("source mismatch")
 return {"file":SRC.name,"sha256":KNOWN_SHA,"width":int(width),"height":int(height),"fps":framerate,
         "duration_s":round(duration,3),"page":SOURCE_PAGE,
         "commons_license_declaration":"PD-India + PD-1996 (US), verification of rights for Italy remains pending",
         "declared_date":"January 11–14, 1929"}
def anchor_image(cap,t,x):
 cap.set(cv2.CAP_PROP_POS_MSEC,t*1000)
 ok,f=cap.read()
 if not ok:raise RuntimeError("missing source anchor "+str(t))
 h,w=f.shape[:2];cw=int(h*9/16);left=max(0,min(w-cw,int(x-cw/2)))
 crop=f[:,left:left+cw]
 if crop.shape[1]!=cw:raise RuntimeError("source crop not complete")
 return crop
def quality_photo(frame,dd,session,index):
 # Preserve original facial positions and body silhouette EXACTLY.
 # Neural DDColor produces learned chroma (not hand tint/LUT), original grayscale produces brightness.
 source=cv2.resize(frame,(W,H),interpolation=cv2.INTER_CUBIC)
 src=cv2.cvtColor(source,cv2.COLOR_BGR2GRAY)
 src=cv2.fastNlMeansDenoising(src,None,h=3,templateWindowSize=7,searchWindowSize=17)
 base=cv2.cvtColor(src,cv2.COLOR_GRAY2BGR)
 # DDColor expects grayscale RGB as model input; learn semantic color.
 ab=dd.infer_ab(session,base)
 lab_l=dd.l_channel(base)
 ab=cv2.resize(ab,(W,H),interpolation=cv2.INTER_LINEAR)
 lab=np.dstack((lab_l,np.clip(ab*1.32,-105,105))).astype(np.float32)
 rgb=cv2.cvtColor(lab,cv2.COLOR_LAB2RGB)
 image=cv2.cvtColor((np.clip(rgb,0,1)*255).astype("uint8"),cv2.COLOR_RGB2BGR)
 # Adjust local light/dark photographic contrast, not geometry or hair/faces invented.
 lab=cv2.cvtColor(image,cv2.COLOR_BGR2LAB)
 l,a,b=cv2.split(lab)
 clahe=cv2.createCLAHE(clipLimit=1.52,tileGridSize=(10,10))
 l=cv2.addWeighted(l,.78,clahe.apply(l),.22,0)
 image=cv2.cvtColor(cv2.merge((l,a,b)),cv2.COLOR_LAB2BGR)
 # Modest sharpening prevents the cartoon crisp look, does not create true lost detail.
 soft=cv2.GaussianBlur(image,(0,0),.65)
 image=cv2.addWeighted(image,1.14,soft,-.14,0)
 image=np.clip(image,0,255).astype(np.uint8)
 # Scene-aware photograph-grade correction applied only to new AI colors.
 # Prevent model's bright scarlet from turning naturally woven straw baskets into neon.
 factors=[.78,.84,.59,.81,.88,.60,.75,.84]
 hsv=cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
 h,s,v=cv2.split(hsv)
 if index==3:
  yy=np.arange(H,dtype=np.int32)[:,None]
  basket=(np.logical_or(h<12,h>171) & (s>85) & (yy<800))
  h[basket]=17
  s[basket]=np.minimum(s[basket],97)
 s=np.clip(s.astype(np.float32)*factors[index-1],0,255).astype(np.uint8)
 image=cv2.cvtColor(cv2.merge([h,s,v]),cv2.COLOR_HSV2BGR)
 if index==6:
  # Historic stone and wooden cart: neutralize excessive generated orange cast.
  f=image.astype(np.float32)
  f[:,:,0]=np.clip(f[:,:,0]*1.08,0,255)
  f[:,:,2]=np.clip(f[:,:,2]*.90,0,255)
  image=f.astype(np.uint8)
 g1=cv2.resize(cv2.cvtColor(source,cv2.COLOR_BGR2GRAY),(90,160)).astype(np.float32)
 g2=cv2.resize(cv2.cvtColor(image,cv2.COLOR_BGR2GRAY),(90,160)).astype(np.float32)
 corr=float(np.corrcoef(g1.ravel(),g2.ravel())[0,1])
 hsv=cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
 mean_s=float(np.mean(hsv[:,:,1]))
 fraction=float(np.mean(hsv[:,:,1]>22))
 if not np.isfinite(corr) or corr<.82 or (mean_s<12 and fraction<.13):
  raise RuntimeError(f"source photo rejected {index}: geometry {corr:.3f}, saturation {mean_s:.2f}")
 target=ROOT/f"COLOR_PHOTO_{index:02}.jpg"
 cv2.imwrite(str(target),image,[cv2.IMWRITE_JPEG_QUALITY,95])
 return {"file":target.name,"sha256":sha(target),"correlation":round(corr,3),
         "mean_hsv_saturation":round(mean_s,1),"fraction_visibly_colored":round(fraction,3),
         "method":"Source-faithful neural DDColor chroma, conservative local contrast; colors hypothetical",
         "generative_face_replacement":False}
def make_photo_qa(source_info):
 spec=importlib.util.spec_from_file_location("dd_v60","src/storia_rivive_real_ai_v60.py")
 dd=importlib.util.module_from_spec(spec);spec.loader.exec_module(dd)
 model,meta=dd.download_model()
 cap=cv2.VideoCapture(str(SRC))
 info=[];imgs=[]
 for i,shot in enumerate(SHOTS,1):
  crop=anchor_image(cap,shot["t"],shot["x"])
  file=ROOT/f"SOURCE_FRAME_{i:02}.png"
  cv2.imwrite(str(file),cv2.resize(crop,(W,H),interpolation=cv2.INTER_CUBIC))
  color=quality_photo(crop,dd,model,i)
  rec={**shot,"number":i,"historical_anchor":file.name,"historical_frame_sha256":sha(file),**color}
  info.append(rec)
  origin=cv2.imread(str(file));p=cv2.imread(str(ROOT/color["file"]))
  imgs.append((origin,p))
  print("ACTUAL_NEURAL_AI_PHOTO",i,"t",shot["t"],"geometry",color["correlation"],
        "color",color["mean_hsv_saturation"],"file",color["file"],flush=True)
 cap.release()
 if len({round(z["t"],2) for z in info})!=len(info):raise RuntimeError("duplicate timecodes")
 # Full image inspection board: NOT a guarantee of scene identity; shows the real assets.
 bw=170;bh=302;gap=8
 board=Image.new("RGB",(len(imgs)*(bw+gap),2*(bh+38)),(11,16,20))
 dr=ImageDraw.Draw(board)
 for i,(original,photo) in enumerate(imgs):
  for r,frame in enumerate((original,photo)):
   im=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)).resize((bw,bh))
   x=i*(bw+gap)+3;y=r*(bh+38)+6
   board.paste(im,(x,y))
   dr.text((x,y+bh+4),f"{i+1}  {'SOURCE' if r==0 else 'AI COLOR'}  {SHOTS[i]['t']}s",fill=(234,227,209))
 board.save(ROOT/"CONTACT_REAL_FILM_VS_AI_PHOTOS.jpg",quality=89)
 writej(ROOT/"PHOTO_QA.json",info)
 return info
def frames_motion(cap,shot):
 t=shot["t"];length=shot["motion"];x=shot["x"]
 # Only REAL source cinema motion ending on EXACT frame at t.
 desired=int(round(length*FPS));native=[]
 for i in range(desired-1):
  v=t-length+(i/FPS)
  orig=anchor_image(cap,v,x)
  native.append(cv2.resize(orig,(W,H),interpolation=cv2.INTER_LINEAR))
 # Ensure source frame exactly matches AI still reference anchor by identity, not inferred interpolation.
 anchor=cv2.imread(str(ROOT/f"SOURCE_FRAME_{SHOTS.index(shot)+1:02}.png"))
 native.append(anchor)
 return [cv2.cvtColor(cv2.cvtColor(x,cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR) for x in native]
def overlay_title(img,t):
 if t>1.95:return img
 fade=min(1,t/.17,max(0,(1.95-t)/.28))
 if fade<=0:return img
 rgba=Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB)).convert("RGBA")
 layer=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(layer)
 d.rounded_rectangle((45,1020,675,1160),radius=20,fill=(6,12,17,int(fade*166)))
 font="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
 ft=ImageFont.truetype(font,51);tiny=ImageFont.truetype(font,25)
 d.text((76,1040),"BOMBAY · 1929",font=ft,fill=(246,233,209,int(255*fade)))
 d.text((79,1110),"A CITY BEFORE OUR TIME",font=tiny,fill=(236,215,187,int(243*fade)))
 return cv2.cvtColor(np.asarray(Image.alpha_composite(rgba,layer).convert("RGB")),cv2.COLOR_RGB2BGR)
def make_audio(seconds,scenes):
 import array
 sr=32000
 samples=array.array("h")
 # Distinct warm melody / bowed strings + delicate pulses, completely original synthesized composition.
 notes=[196.00,246.94,293.66,329.63,293.66,261.63,220.00,196,174.61,220,261.63,293.66]
 starts=[s["output_start"] for s in scenes]
 for i in range(int(seconds*sr)):
  t=i/sr
  ph=t*1.42;at=int(ph);frac=ph-at
  freq=notes[at%len(notes)]
  env=min(1,t/.65,max(0,(seconds-t)/.95))
  melody=(.5*math.sin(2*math.pi*freq*t)+.23*math.sin(2*math.pi*2*freq*t)
          +.10*math.sin(2*math.pi*3*freq*t))*math.exp(-3.3*frac)
  longtones=.27*math.sin(2*math.pi*98*t)+.22*math.sin(2*math.pi*146.83*t)+.17*math.sin(2*math.pi*196*t)
  # soft low pulse marking city-life cuts
  k=(t*1.42)%1
  beat=.08*math.sin(2*math.pi*85*t)*math.exp(-10*k)
  hits=0
  for s in scenes:
   dt=t-s["reveal_at"]
   if 0<=dt<.18:hits+=.12*math.sin(2*math.pi*(490*dt-120*dt**2))*math.exp(-23*dt)
  val=int(max(-28000,min(28000,2900*env*(melody+longtones+beat+hits))))
  samples.extend((val,int(val*.93)))
 path=ROOT/"ORIGINAL_MUSIC.wav"
 with wave.open(str(path),"wb") as wav:
  wav.setnchannels(2);wav.setsampwidth(2);wav.setframerate(sr);wav.writeframes(samples.tobytes())
 return path
def render(source_info,photos):
 out=ROOT/"BOMBAY_1929_LA_STORIA_RIVIVE_V92.mp4";tmp=ROOT/"silent.mp4"
 p=subprocess.Popen(["ffmpeg","-nostdin","-y","-v","error","-f","rawvideo","-pix_fmt","bgr24",
    "-s",f"{W}x{H}","-r",str(FPS),"-i","-",
    "-an","-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p","-movflags","+faststart",str(tmp)],
    stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 cap=cv2.VideoCapture(str(SRC))
 framecount=0;timeline=[]
 try:
  for i,(shot,photo) in enumerate(zip(SHOTS,photos),1):
   assert photo["historical_frame_sha256"]==sha(ROOT/photo["historical_anchor"])
   assert photo["sha256"]==sha(ROOT/photo["file"])
   t0=framecount/FPS
   motion=frames_motion(cap,shot)
   image=cv2.imread(str(ROOT/photo["file"]))
   original=cv2.imread(str(ROOT/photo["historical_anchor"]))
   bgr=cv2.cvtColor(cv2.cvtColor(original,cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR)
   for frame in motion:
    if i==1:frame=overlay_title(frame,framecount/FPS)
    p.stdin.write(frame.tobytes());framecount+=1
   # Source's EXACT frame stops, then transitions with geometric coordinates unchanged.
   n=round(shot["transition"]*FPS)
   for k in range(n):
    a=(k+1)/n;a=a*a*(3-2*a)
    frame=cv2.addWeighted(bgr,1-a,image,a,0)
    if i==1:frame=overlay_title(frame,framecount/FPS)
    p.stdin.write(frame.tobytes());framecount+=1
   for k in range(round(shot["hold"]*FPS)):
    frame=image
    if i==1:frame=overlay_title(frame,framecount/FPS)
    p.stdin.write(frame.tobytes());framecount+=1
   timeline.append({"scene":i,"event_id":f"bombay-1929-original-{shot['t']}",
     "source_timecode_s":shot["t"],"subject":shot["label"],"output_start":round(t0,3),
     "reveal_at":round(t0+len(motion)/FPS,3),
     "photo_seconds":round(round(shot["hold"]*FPS)/FPS,3),
     "output_end":round(framecount/FPS,3)})
   print("RENDERED_DISTINCT_SCENE",i,"elapsed",framecount/FPS,flush=True)
 finally:
  cap.release();p.stdin.close()
 e=p.stderr.read().decode(errors="replace")
 if p.wait():raise RuntimeError("ffmpeg stream failed "+e[-1000:])
 duration=framecount/FPS
 if not 22<=duration<=29:raise RuntimeError(f"V91 refuses unexpectedly short/long result {duration:.2f}")
 music=make_audio(duration,timeline)
 run(["ffmpeg","-y","-nostdin","-v","error","-i",str(tmp),"-i",str(music),
   "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","128k",
   "-movflags","+faststart","-shortest",str(out)],200)
 run(["ffmpeg","-v","error","-xerror","-i",str(out),"-f","null","-"],180)
 probe=json.loads(run(["ffprobe","-v","error","-show_entries",
   "format=duration,size:stream=codec_name,width,height","-of","json",str(out)],45))
 streams={s["codec_name"] for s in probe["streams"]}
 if "h264" not in streams or "aac" not in streams:raise RuntimeError("missing media tracks")
 if abs(float(probe["format"]["duration"])-duration)>.13:raise RuntimeError("duration changed during mux")
 return out,timeline,probe
def packaging(out,timeline,probe,source_info,photos):
 # Cover from a real source-anchored neural-colored close human shot, not an invented portrait.
 cover=Image.open(ROOT/"COLOR_PHOTO_01.jpg").convert("RGB")
 d=ImageDraw.Draw(cover)
 # Put cover text where it doesn't obscure the upper face.
 d.rounded_rectangle((35,1005,685,1163),radius=21,fill=(9,16,23))
 f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",51)
 small=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",24)
 d.text((72,1030),"BOMBAY · 1929",font=f,fill=(243,225,183))
 d.text((75,1100),"THE CITY COMES TO LIFE",font=small,fill=(230,218,202))
 cover.save(ROOT/"COVER.jpg",quality=94)
 common="Riprese vere, gennaio 1929. I colori sono una ricostruzione IA, non colori storicamente verificati."
 posts={
 "FACEBOOK":"BOMBAY, 1929. Un venditore ci guarda. La folla attraversa il mercato. Carri, ceste, sorrisi: per un attimo il passato sembra vicinissimo. "+common+"\nFonte: "+SOURCE_PAGE,
 "INSTAGRAM":"BOMBAY · 1929 🎞️ Una città intera, otto istanti di vita vera. Dal bianco e nero al colore ricostruito con IA. Le persone e il movimento sono originali. #HistoryReels #Bombay1929",
 "TIKTOK":"Queste persone erano davvero davanti a una cinepresa nel 1929. Guarda il momento in cui l'immagine si ferma e riprende colore. "+common+" #storia #Bombay",
 "YOUTUBE":"BOMBAY 1929 | La Storia Rivive\n\nOtto momenti diversi tratti dalla pellicola originale Street Scenes in Bombay, India, January 1929 (Wikimedia Commons), colorizzati con il modello neurale DDColor. Film storico autentico in movimento; colori ricostruiti digitalmente, non testimonianza cromatica certa. Musica originale composta per il montaggio.\n"+SOURCE_PAGE}
 for site,txt in posts.items():(ROOT/f"POST_{site}.txt").write_text(txt+"\n",encoding="utf8")
 report={"status":"RENDERED_FOR_ARTISTIC_REVIEW_NOT_AUTOPUBLISHED",
    "title":"Bombay · 1929 — The City Comes to Life","format":"La Storia Rivive V70/V91",
    "duration_s":round(float(probe["format"]["duration"]),3),"source":source_info,
    "shot_count":len(timeline),"shots":timeline,
    "photo_records":photos,"video_sha256":sha(out),
    "video_bytes":out.stat().st_size,"video_streams":probe["streams"],
    "restoration_method":"8 separate neural AI DDColor true photographic still frames from exact source timecodes; moderate detail processing, no invented faces",
    "vadu_credits_used":0,"vidu_credits_used":0,"new_api_cost_eur":0,
    "source_original_is_authentic":True,"colors_hypothetical":True,
    "automatic_technical_qa_passed":True,
    "human_semantic_and_artistic_qa":"PENDING_VIEWER_REVIEW",
    "private_site_import_verified":False,"social_published":False,
    "license_for_italy":"check international territorial terms; Commons declares PD India & US"}
 writej(ROOT/"FINAL_QA_SOURCES.json",report)
 pack=ROOT/"BOMBAY_1929_V92_ANDROID_COMPLETO.zip"
 with zipfile.ZipFile(pack,"w",zipfile.ZIP_DEFLATED) as z:
  for p in [out,ROOT/"COVER.jpg",ROOT/"CONTACT_REAL_FILM_VS_AI_PHOTOS.jpg",
       ROOT/"FINAL_QA_SOURCES.json",ROOT/"PHOTO_QA.json",
       *[ROOT/f"POST_{x}.txt" for x in posts]]:
   z.write(p,p.name)
 with zipfile.ZipFile(pack) as z:
  if z.testzip():raise RuntimeError("ZIP integrity failure")
 print("V92_NEW_BOMBAY_REAL_VIDEO_RENDER_READY",out.name,"DURATION",report["duration_s"],
       "VIDEO_BYTES",out.stat().st_size,"ZIP",pack.name,pack.stat().st_size,flush=True)
def main():
 source=check_source()
 print("SOURCE_HASH_VERIFIED",source["sha256"],flush=True)
 photos=make_photo_qa(source)
 out,timeline,probe=render(source,photos)
 packaging(out,timeline,probe,source,photos)
if __name__=="__main__":main()
