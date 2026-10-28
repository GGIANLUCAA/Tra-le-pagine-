#!/usr/bin/env python3
"""V67 Austria 1920: authentic Vienna market and rural movements become frozen AI-restored photographs.
No paid GPU, Vidu, or invented historical footage. 1080x1920 24-26s vertical MP4 with original score.
Prior V64 discussion notes this CPU restoration is NOT HYPIR diffusion reference quality.
"""
import hashlib, importlib.util, json, math, subprocess, sys, wave, zipfile
from pathlib import Path
import cv2, numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]

def module(name,path):
 spec=importlib.util.spec_from_file_location(name,ROOT/path)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 return m
v67=module("vienna_v67_source","src/storia_rivive_v67_vienna_source_contact.py")
v63=module("beirut_v63_modules","src/storia_rivive_director_cut_v63.py")
v60=v63.v60
OUT=Path("output/storia_rivive_v67_vienna_1920")
OUT.mkdir(parents=True,exist_ok=True)
W,H,FPS=1080,1920,30
VIDEO=OUT/"AUSTRIA_1920_IL_TEMPO_SI_FERMA_V67.mp4"
# Times chosen AFTER viewing every five-second representative frame across whole 283s film
# and 12 frames with four vertical-crop choices. Clips are intentionally from DIFFERENT events.
SHOTS=[
 {"name":"La legna","end":331.70,"x":70,"motion":1.38,"reveal":.32,"hold":2.35,"theme":"wood_carrier","note":"A worker carries an enormous bundle of brushwood, foreground emotional hook"},
 {"name":"Il mercato","end":158.0,"x":195,"motion":1.32,"reveal":.34,"hold":2.30,"theme":"vienna_market_people","note":"Market women and men close to frame, their gestures are clear"},
 {"name":"Il tram","end":271.0,"x":155,"motion":1.27,"reveal":.31,"hold":2.12,"theme":"tram_city_life","note":"People boarding an overloaded tram, transport and city bustle"},
 {"name":"Il mercato coperto","end":56.80,"x":190,"motion":1.32,"reveal":.31,"hold":1.95,"theme":"vienna_market_entrance","note":"Vienna market architecture and passers-by"},
 {"name":"Le donne","end":187.1,"x":65,"motion":1.43,"reveal":.33,"hold":2.54,"theme":"market_women","note":"Women conversing amid marketplace crowds, freeze when expressive"},
 {"name":"La campagna","end":324.50,"x":330,"motion":1.29,"reveal":.33,"hold":2.15,"theme":"rural_road","note":"Workers carrying brushwood along a country road"},
 {"name":"Il ritorno","end":344.80,"x":300,"motion":1.43,"reveal":.35,"hold":2.50,"theme":"rural_workers","note":"Villagers returning with heavy bundles, final emotional tableau"}
]
assert 24<sum(s["motion"]+s["reveal"]+s["hold"] for s in SHOTS)<28

def sha(path):
 h=hashlib.sha256()
 with open(path,"rb") as fp:
  for chunk in iter(lambda:fp.read(2**20),b""):h.update(chunk)
 return h.hexdigest()

def exec_cmd(args,timeout=130):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError("FFmpeg error: "+p.stderr[-1000:])
 return p

def raw_frame(cap,sec):
 cap.set(cv2.CAP_PROP_POS_MSEC,sec*1000)
 ok,img=cap.read()
 if not ok:raise ValueError("Archive frame unavailable "+str(sec))
 if img.shape[:2]!=(576,720):raise ValueError("Encoded source raster mismatch "+str(img.shape))
 return img

def crop(frame,x):
 cropw=round(frame.shape[0]*9/16)
 x=max(0,min(int(x),frame.shape[1]-cropw))
 c=frame[:,x:x+cropw]
 if c.shape[:2]!=(576,324):raise ValueError("Expected 324x576 source crop")
 return c

def historic_bnw(frame,x):
 bw=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
 bw=cv2.createCLAHE(clipLimit=1.25,tileGridSize=(8,8)).apply(bw)
 return cv2.resize(cv2.cvtColor(crop(cv2.cvtColor(bw,cv2.COLOR_GRAY2BGR),x),cv2.COLOR_BGR2RGB),(W,H),interpolation=cv2.INTER_CUBIC)[:,:,::-1].copy()

def temporal_denoise(cap,center):
 """Robust alignment of five nearby REAL film frames to reduce scratches/grain before restoring.
    Median + conservative blend avoids manufacturing unrelated facial details.
 """
 base=raw_frame(cap,center)
 gray=cv2.cvtColor(base,cv2.COLOR_BGR2GRAY)
 neighbors=[base]
 h,w=gray.shape
 yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
 for delta in (-.08,-.04,.04,.08):
  nearby=raw_frame(cap,center+delta)
  ng=cv2.cvtColor(nearby,cv2.COLOR_BGR2GRAY)
  flow=cv2.calcOpticalFlowFarneback(gray,ng,None,.5,3,13,3,5,1.1,0)
  warped=cv2.remap(nearby,xx+flow[:,:,0],yy+flow[:,:,1],cv2.INTER_LINEAR,
                   borderMode=cv2.BORDER_REFLECT_101)
  aligned=cv2.cvtColor(warped,cv2.COLOR_BGR2GRAY)
  delta_abs=float(np.mean(np.abs(aligned.astype(np.float32)-gray.astype(np.float32))))
  if delta_abs<14:
   neighbors.append(warped)
 med=np.median(np.stack(neighbors),axis=0).astype(np.uint8)
 # Keep much of source frame to protect identity, gesture and facial geometry
 merged=cv2.addWeighted(base,.37,med,.63,0) if len(neighbors)>=3 else base
 return merged,len(neighbors)

def photo_ai(cap,s,ddcolor,esrgan):
 merged,n=temporal_denoise(cap,s["end"])
 mild=cv2.fastNlMeansDenoisingColored(merged,None,2.2,2.2,7,15)
 ab=v60.infer_ab(ddcolor,mild)
 L=v60.l_channel(mild)
 resized=cv2.resize(ab,(mild.shape[1],mild.shape[0]),interpolation=cv2.INTER_LINEAR)
 lab=np.dstack([L,np.clip(resized*1.15,-111,111)]).astype(np.float32)
 rgb=np.clip(cv2.cvtColor(lab,cv2.COLOR_LAB2RGB)*255,0,255).astype(np.uint8)
 colored=cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR)
 c=crop(colored,s["x"])
 # No downsampling to 240x427 before AI: ESRGAN uses original 324x576 information.
 learned=v63.esrgan_4x(esrgan,c)
 restored=cv2.resize(learned,(W,H),interpolation=cv2.INTER_AREA)
 baseline=cv2.resize(c,(W,H),interpolation=cv2.INTER_CUBIC)
 restored=cv2.addWeighted(restored,.91,baseline,.09,0)
 # No detailEnhance / destructive denoise of AI photo.
 luma=cv2.cvtColor(restored,cv2.COLOR_BGR2LAB)
 l,a,b=cv2.split(luma)
 l=cv2.createCLAHE(clipLimit=1.12,tileGridSize=(9,9)).apply(l)
 restored=cv2.cvtColor(cv2.merge([l,a,b]),cv2.COLOR_LAB2BGR)
 # Stage passes if true color, but is not thereby judged equal to generative reference films.
 saturation=cv2.cvtColor(restored,cv2.COLOR_BGR2HSV)[:,:,1].mean()
 if saturation<12:raise ValueError("AI photo insufficient chroma "+s["name"])
 return restored,n,float(saturation)

def title_text(frame,sec,scene_index):
 # Only the opening has a transparent title panel. Never cover every photo repeatedly.
 if scene_index!=0 or sec>.85:return frame
 im=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
 d=ImageDraw.Draw(im,"RGBA")
 try:
  title=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",64)
  sub=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",24)
 except OSError:
  title=ImageFont.load_default();sub=ImageFont.load_default()
 d.rounded_rectangle((52,64,720,206),radius=12,fill=(4,8,12,118))
 d.text((72,75),"AUSTRIA · 1920",font=title,fill=(250,242,228,251))
 d.text((78,167),"IL TEMPO SI FERMA",font=sub,fill=(228,229,233,239))
 return cv2.cvtColor(np.asarray(im.convert("RGB")),cv2.COLOR_RGB2BGR)

def score(duration,path,scene_onsets,reveals):
 """Original gentle instrumental composition; no third-party samples or copyrighted song."""
 sr=32000
 t=np.arange(int(duration*sr),dtype=np.float32)/sr
 out=np.zeros_like(t)
 chords=[[146.83,174.61,220],[130.81,164.81,196],[174.61,220,261.63],
         [164.81,196,246.94],[146.83,220,293.66],[130.81,196,261.63]]
 for i,begin in enumerate(scene_onsets):
  stop=scene_onsets[i+1] if i+1<len(scene_onsets) else duration
  sel=(t>=begin)&(t<stop);u=t[sel]-begin
  tones=chords[i%len(chords)]
  a=np.zeros_like(u)
  for j,f in enumerate(tones):
   a+=.025*np.sin(2*np.pi*f*u+j*1.4)*np.minimum(1,u/.5)
   a+=.012*np.sin(2*np.pi*2.002*f*u+j*.7)
  a+=.016*np.sin(2*np.pi*55*u)*np.exp(-5*u)
  out[sel]=a
  # Plucked notes: human-like attack and quick resonance, original melody
  for beat in np.arange(0,stop-begin,.49):
   phase=t-begin-beat
   ss=(phase>=0)&(phase<.57)
   freq=tones[int((beat/.49+i)%len(tones))]*2
   out[ss]+=.048*np.sin(2*np.pi*freq*phase[ss])*np.exp(-6*phase[ss])
  for cue in [reveals[i]]:
   tt=t-cue;ss=(tt>=0)&(tt<.7)
   out[ss]+=.095*np.sin(2*np.pi*(97*tt[ss]+30*tt[ss]**2))*np.exp(-9*tt[ss])
 out*=np.minimum(1,t/.7)*np.minimum(1,(duration-t)/1.4)
 out=np.tanh(out*3)
 stere=np.column_stack((out,np.roll(out,190)*.92))
 samples=(np.clip(stere,-1,1)*18000).astype("<i2")
 with wave.open(str(path),"wb") as f:
  f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr);f.writeframes(samples.tobytes())

def build():
 source,rights=v67.original()
 dd,ddmeta=v60.download_model()
 upscale,upmeta=v63.setup_upscaler()
 cap=cv2.VideoCapture(str(source))
 if not cap.isOpened():raise RuntimeError("Original film cannot be decoded")
 tempfile=OUT/"VIENNA_V67_VIDEO_MUTO.mp4"
 p=subprocess.Popen(["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error",
    "-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),
    "-i","-","-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",
    str(tempfile)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 count=0;onsets=[];reveals=[];meta=[];stills=[]
 try:
  for i,s in enumerate(SHOTS):
   sec0=s["end"]-s["motion"]
   onsets.append(count/FPS)
   reveals.append((count+round(s["motion"]*FPS))/FPS)
   original=raw_frame(cap,s["end"])
   photo,used_frames,sat=photo_ai(cap,s,dd,upscale)
   name=f"FOTO_RESTAURATA_{i+1:02d}.jpg"
   saved=OUT/name
   cv2.imwrite(str(saved),photo,[cv2.IMWRITE_JPEG_QUALITY,94])
   stills.append(photo)
   motion=[]
   for k in range(round(s["motion"]*FPS)):
    motion.append(historic_bnw(raw_frame(cap,sec0+k/FPS),s["x"]))
   freeze=historic_bnw(original,s["x"])
   for k,frame in enumerate(motion):
    output=title_text(frame,(count+k)/FPS,i)
    p.stdin.write(output.tobytes())
   count+=len(motion)
   ntrans=round(s["reveal"]*FPS)
   for k in range(ntrans):
    t=(k+1)/ntrans
    alpha=t*t*(3-2*t)
    intermediate=cv2.addWeighted(freeze,1-alpha,photo,alpha,0)
    p.stdin.write(title_text(intermediate,count/FPS+k/FPS,i).tobytes())
   count+=ntrans
   nhold=round(s["hold"]*FPS)
   for k in range(nhold):
    p.stdin.write(title_text(photo,(count+k)/FPS,i).tobytes())
   count+=nhold
   meta.append({"scene":i+1,"subject":s["theme"],"source_timecode_s":s["end"],
    "moving_s":s["motion"],"transition_s":s["reveal"],"photo_hold_s":s["hold"],
    "crop_origin_px":s["x"],"real_photo_from_same_source_frame":True,
    "temporal_align_frames_used":used_frames,"ai_color_saturation_mean":round(sat,1),
    "original_source_crop_px":[324,576],"ai_photo_resolution_px":[W,H],
    "ai_photo_file":name,"ai_photo_sha256":sha(saved),"editorial_reason":s["note"]})
   print("VIENNA_V67_SCENE_READY",i+1,s["name"],"photos",used_frames,"frames",count,flush=True)
 finally:
  p.stdin.close()
 stderr=p.stderr.read()
 if p.wait()!=0:raise RuntimeError("FFmpeg render failed: "+stderr.decode(errors="ignore")[-1200:])
 cap.release()
 duration=count/FPS
 music=OUT/"MUSICA_ORIGINALE.wav"
 score(duration,music,onsets,reveals)
 exec_cmd(["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error",
  "-i",str(tempfile),"-i",str(music),"-map","0:v","-map","1:a","-c:v","copy",
  "-c:a","aac","-b:a","140k","-shortest","-movflags","+faststart",str(VIDEO)],160)
 exec_cmd(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(VIDEO),"-f","null","-"],160)
 cover=stills[0].copy()
 # Source-aligned restored photo is the cover, not fabricated generative cityscape.
 cv2.imwrite(str(OUT/"COPERTINA.jpg"),title_text(cover,0,0),[cv2.IMWRITE_JPEG_QUALITY,94])
 metadata={"title":"Austria 1920 — Il tempo si ferma",
  "format":"La Storia Rivive V67","source":rights,
  "source_sha256_verified":sha(source)==rights["source_file_sha256"],
  "rights":"CC0 asserted for the precise Commons film; extra rights need editorial review",
  "historical_scope":"March 1920 Austria compilation showing Vienna covered market and rural firewood carriers; rural location unconfirmed",
  "scenes":meta,"runtime_s":round(duration,2),
  "output_resolution_px":[W,H],"is_native_4k":False,"native_source_px":[720,576],"display_aspect_ratio":"4:3; square-pixel display width 768, encoded raster width 720",
  "source_crop_px":[324,576],"colorization":ddmeta,"ai_photo_detail_recovery":upmeta,
  "IMPORTANT_ARTISTIC_NOTE":"These are AI-colorized/ESRGAN-restored authentic frames, NOT HYPIR diffusion. Visually review image fidelity; DO NOT claim original face detail recovered with certainty.",
  "ai_disclosure":"Riprese autentiche d'archivio del 1920. Colori e microdettagli sono ricostruiti con AI, non documentazione cromatica certa.",
  "music":"Original score synthesized for this episode; not archive audio",
  "no_paid_provider_or_vidu_credits":True,
  "mp4_sha256":sha(VIDEO),"mp4_bytes":VIDEO.stat().st_size,
  "mp4_ffmpeg_full_decode_passed":True,
  "user_android_download_test_pending":True,
  "video_library_site_uploaded":False,
  "human_artistic_reference_grade_approved":False,
  "no_social_auto_publication":True}
 (OUT/"FONTI_E_QA.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 posts={
  "FACEBOOK":"Austria, 1920. Al mercato di Vienna la folla si accalca, il tram si riempie. Lontano dalla città, uomini e donne portano pesanti fascine di legna. Ogni vecchio filmato si ferma e diventa una fotografia restaurata a colori. Sono riprese autentiche, ma colori e microdettagli sono ricostruzioni AI, non testimonianze cromatiche certe. Archivio Musée Albert-Kahn / Wikimedia Commons CC0. #Austria1920 #Storia #Archivio",
  "INSTAGRAM":"AUSTRIA, 1920 🎞️ Una folla, un tram, il peso della legna sulle spalle. Il filmato si muove, poi il tempo si ferma e si trasforma in una fotografia AI a colori. Riprese originali CC0 Musée Albert-Kahn; colori ricostruiti. #LaStoriaRivive #Austria #Storia",
  "TIKTOK":"Austria 1920: il filmato si ferma e diventa una fotografia a colori! 🎞️ Mercati, tram e portatori di legna. Riprese originali Musée Albert-Kahn, CC0; colori e dettagli ricostruiti con AI. #history #1920 #storia #restauro",
  "YOUTUBE":"AUSTRIA 1920 | Il tempo si ferma — Mercato di Vienna e vita rurale\n\nSette scene dal filmato autentico girato nel marzo 1920: il mercato coperto di Vienna, le persone in attesa, un tram e le scene rurali di persone con fasci di legna. Fonte Musée Albert-Kahn, operatore Lucien Le Saint. Archivio CC0 su Wikimedia Commons. Movimento originale in bianco e nero e fotografie colorizzate con DDColor, dettagli migliorati con Real-ESRGAN. Colori e microdettagli non sono documentati storicamente; gli ambienti urbani e rurali non sono dichiarati la stessa località. Musica originale del video.\nFonte: "+v67.PAGE
 }
 for social,text in posts.items():
  (OUT/f"POST_{social}.txt").write_text(text+"\n",encoding="utf8")
 (OUT/"LEGGIMI.txt").write_text("Austria 1920 — Il tempo si ferma. Video verticale 1080x1920 H264/AAC autentico: mercato di Vienna, tram e scene rurali. Fonte CC0 Musée Albert-Kahn, operatore Lucien Le Saint. Colori con DDColor e dettagli con Real-ESRGAN; NON diffusion HYPIR né scansione 4K. Le fotografie AI sono ricostruzioni plausibili, non prove dei colori storici. Zero crediti Vidu, niente autopubblicazione social.\n",encoding="utf8")
 kit=OUT/"AUSTRIA_1920_VIDEO_E_FOTO_V67.zip"
 files=[VIDEO,OUT/"COPERTINA.jpg",OUT/"FONTI_E_QA.json",OUT/"LEGGIMI.txt",
        *[OUT/f"POST_{k}.txt" for k in posts],*[OUT/f"FOTO_RESTAURATA_{i+1:02d}.jpg" for i in range(len(SHOTS))]]
 with zipfile.ZipFile(kit,"w",compression=zipfile.ZIP_DEFLATED) as z:
  for f in files:z.write(f,f.name)
 with zipfile.ZipFile(kit) as z:
  if z.testzip():raise RuntimeError("ZIP corruption")
 print("VIENNA_1920_MP4_COMPLETE",json.dumps({"path":str(VIDEO),"sha256":sha(VIDEO),
  "size":VIDEO.stat().st_size,"duration_s":duration,"kit":str(kit)},ensure_ascii=False),flush=True)
if __name__=="__main__":
 build()
