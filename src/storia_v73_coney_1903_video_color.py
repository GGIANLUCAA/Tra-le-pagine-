#!/usr/bin/env python3
"""V73 Coney Island 1903: genuine LOC original motion -> semantic AI chroma, splash-anchored progressive reveal.
Free CPU inference, 0 Vidu; no AI-created people or synthetic historical motion.
"""
from pathlib import Path
import os, sys, json, math, hashlib, subprocess, wave, zipfile, urllib.request, importlib.util
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=Path("output/storia_v73_coney"); OUT.mkdir(parents=True,exist_ok=True)
PAGE="https://www.loc.gov/item/00563608/"
MOV="https://tile.loc.gov/storage-services/service/mbrs/ntscrm/01831478/01831478.mov"
MP4="https://tile.loc.gov/storage-services/service/mbrs/ntscrm/01831478/01831478.mp4"
T0,T1=34.0,51.6
FPS=24; W,H=720,1280
SOURCE_SHA_MOV="f3458277cb1bb86964fd5effa1f621dfa2c3676fd489939017ccbee190a18408"
SOURCE_SHA_MP4=""

def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()

def cmd(args,timeout=240):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError(str(args[:4])+"\n"+p.stderr[-1400:])
 return p.stdout

def acquire():
 for ext,url in [(".mov",MOV),(".mp4",MP4)]:
  p=OUT/("SOURCE_LOC_ORIGINAL"+ext)
  try:
   if not p.exists() or p.stat().st_size<1000000:
    cmd(["curl","-fL","--show-error","--connect-timeout","25","--max-time","180","--retry","1","-A","Tra-le-Pagine-Historical/1.0","-o",str(p),url],195)
   if p.stat().st_size<1_000_000:raise RuntimeError("No original file")
   probe=json.loads(cmd(["ffprobe","-v","error","-show_entries","stream=codec_name,width,height,r_frame_rate:format=duration,size","-of","json",str(p)],35))
   vs=[s for s in probe["streams"] if s.get("width")]
   if not vs or vs[0]["width"]<1200 or vs[0]["height"]<900 or float(probe["format"]["duration"])<100:
    raise RuntimeError("Poor or wrong original source")
   if ext==".mov" and (p.stat().st_size!=303848375 or sha(p)!=SOURCE_SHA_MOV):
    raise RuntimeError("Original ProRes does not match previous verified provenance")
   info={"archive":"Library of Congress","page":PAGE,"download":url,"sha256":sha(p),"bytes":p.stat().st_size,
         "stream_info":probe,"license_note":"LOC early historical film, US public domain indicated; distribution/Italy must be checked",
         "historical_movement":"original real camera footage","audio_from_source":"EXCLUDED; modern archive accompaniment not used"}
   (OUT/"SOURCE_QA.json").write_text(json.dumps(info,indent=2))
   print("ACQUIRED_LOC_FILM",p,p.stat().st_size,vs[0]["codec_name"],flush=True)
   return p,info
  except Exception as e:
   print("SOURCE_ATTEMPT_FAILED",ext,type(e).__name__,str(e)[:500],flush=True)
   if p.exists():p.unlink()
 raise RuntimeError("Official archival source inaccessible; no invented substitute")

def load_model():
 spec=importlib.util.spec_from_file_location("ddcolor",ROOT/"src/storia_rivive_real_ai_v60.py")
 dd=importlib.util.module_from_spec(spec);spec.loader.exec_module(dd)
 session,meta=dd.download_model()
 print("FREE_AI_MODEL_LOADED",meta["model_id"],flush=True)
 return dd,session,meta

def read_frames(source):
 cap=cv2.VideoCapture(str(source))
 fps=cap.get(cv2.CAP_PROP_FPS)
 cap.set(cv2.CAP_PROP_POS_MSEC,T0*1000)
 n=round((T1-T0)*FPS)
 frames=[]
 for i in range(n):
  # Original is 24fps; use exact sequential native frames.
  ok,fr=cap.read()
  if not ok:raise RuntimeError("Truncated historical action at "+str(i))
  if i==0 and (fr.shape[1]<1200 or fr.shape[0]<900):raise RuntimeError("Wrong source geometry")
  # Work with 720x540 native landscape, avoid upsampling before AI.
  frames.append(cv2.resize(fr,(720,540),interpolation=cv2.INTER_AREA))
 cap.release()
 if abs(fps-FPS)>1:raise RuntimeError("Source native fps mismatch")
 print("REAL_MOVEMENT_FRAMES",len(frames),"original_fps",fps,flush=True)
 return frames

def alpha_map(t,shape):
 # Spatially motivated reveal: splash becomes a radial expansion of the colors.
 hh,ww=shape[:2]
 if t<39.05:return None
 if t>44.4:return np.ones((hh,ww),dtype=np.float32)
 y,x=np.ogrid[:hh,:ww]
 radius=(t-39.05)/(44.4-39.05)
 radius=35+radius*1590
 dist=np.sqrt(((x-480)*1.02)**2+((y-990)*.94)**2)
 softness=85
 return np.clip((radius+softness-dist)/(2*softness),0,1).astype(np.float32)

def render(source,dd,session):
 frames=read_frames(source)
 # Cache semantic color anchor forecasts every 12 frames, then optical-flow align.
 every=12
 keys=list(range(0,len(frames),every))
 if keys[-1]!=len(frames)-1:keys.append(len(frames)-1)
 anch={}
 for j,i in enumerate(keys):
  anch[i]=dd.infer_ab(session,frames[i])
  if j%8==0:print("CHROMA_ANCHOR",j+1,len(keys),flush=True)
 # Source and colorization need stay exactly time/position aligned.
 output=OUT/"MUTO.mp4"
 proc=subprocess.Popen(["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error",
  "-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
  "-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",
  "-movflags","+faststart",str(output)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 if not proc.stdin:raise RuntimeError("Encoder pipe missing")
 font_regular="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
 try:f1=ImageFont.truetype(font_regular,38);f2=ImageFont.truetype(font_regular,19)
 except:f1=ImageFont.load_default();f2=ImageFont.load_default()
 yy=xx=None
 sample_times=[0,3.4,5.8,7.5,9.6,12.6,16.5]
 sample_frames=[]
 colormetrics=[]
 try:
  for i,frame in enumerate(frames):
   t=T0+i/FPS
   prev=keys[min(i//every,len(keys)-1)]
   nxt=keys[min(i//every+1,len(keys)-1)]
   if prev==nxt or i==prev:ab=anch[prev]
   else:
    p=dd.warp_ab(frame,frames[prev],anch[prev])
    q=dd.warp_ab(frame,frames[nxt],anch[nxt])
    mix=(i-prev)/(nxt-prev)
    ab=(1-mix)*p+mix*q
   # Same real frame, its genuine luminance and geometry, only model-generated chroma.
   color=dd.image_at(frame,ab)
   # Dynamic pan following real boat and splash (not a synthetic camera movement).
   progress=np.clip((t-34.0)/(51.6-34.0),0,1)
   x0=int(205+135*progress)
   cw=round(540*9/16)
   original=cv2.resize(frame[:,x0:x0+cw],(W,H),interpolation=cv2.INTER_CUBIC)
   colored=cv2.resize(color[:,x0:x0+cw],(W,H),interpolation=cv2.INTER_CUBIC)
   mask=alpha_map(t,original.shape)
   if mask is None:out=original
   else:out=np.clip(original.astype(np.float32)*(1-mask[...,None])+colored.astype(np.float32)*mask[...,None],0,255).astype(np.uint8)
   # Bare city/year + archive, avoid extraneous commentary and before/after.
   if i<round(2.65*FPS):
    pil=Image.fromarray(cv2.cvtColor(out,cv2.COLOR_BGR2RGB));d=ImageDraw.Draw(pil,"RGBA")
    d.rounded_rectangle((24,43,574,151),radius=12,fill=(10,12,16,115))
    d.text((42,57),"CONEY ISLAND · 1903",font=f1,fill=(251,248,236,248))
    d.text((44,110),"Library of Congress",font=f2,fill=(240,233,222,230))
    out=cv2.cvtColor(np.asarray(pil),cv2.COLOR_RGB2BGR)
   if any(abs(i/FPS-v)<(0.5/FPS) for v in sample_times):
    sample_frames.append((round(i/FPS,2),out.copy()))
   if i%24==0:
    s=float(cv2.cvtColor(cv2.resize(out,(180,320)),cv2.COLOR_BGR2HSV)[:,:,1].mean())
    colormetrics.append({"second":round(i/FPS,2),"saturation":round(s,1)})
   proc.stdin.write(out.tobytes())
 finally:
  proc.stdin.close()
  err=proc.stderr.read().decode(errors="replace")
  if proc.wait():raise RuntimeError("Encoding error "+err[-1700:])
 print("COLOR_VIDEO_RENDERED",output,output.stat().st_size,flush=True)
 # Contact for human inspection.
 if sample_frames:
  board=Image.new("RGB",(4*230,2*470),(14,15,18));d=ImageDraw.Draw(board)
  for j,(t,img) in enumerate(sample_frames):
   x=(j%4)*230;y=(j//4)*470
   board.paste(Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB)).resize((225,420)),(x+2,y+22))
   d.text((x+9,y+3),f"{t:.2f} s",fill="white")
  board.save(OUT/"CONFRONTO_VIDEO_MOVIMENTO.jpg",quality=90)
 if max(s["saturation"] for s in colormetrics[8:])<17:
  raise RuntimeError("AI actual-color gate failed: video remains monochromatic")
 return output,colormetrics,sample_frames

def make_audio(seconds,path):
 # Original instrumental soundtrack with a controlled recreated splash at approx source 41 sec.
 sr=32000;t=np.arange(int(seconds*sr),dtype=np.float32)/sr
 v=np.zeros_like(t)
 chord=[110,164.81,196,261.63]
 for j,f in enumerate(chord):
  # modest documentary cinematic progression
  v+=(0.028-.004*j)*np.sin(2*np.pi*f*t+j*.6)*(0.60+0.4*np.sin(np.pi*t/seconds))
  v+=0.007*np.sin(2*np.pi*f*2.002*t+j*.31)
 # progressive tension approaching real splash
 sweep=np.maximum(0,1-np.abs(t-6.9)/2.5)
 v+=0.027*sweep*np.sin(2*np.pi*(78*t+6*t*t))
 # Historic film is silent; these are newly synthesized sound-design textures.
 rng=np.random.default_rng(1903)
 noise=rng.standard_normal(len(t)).astype(np.float32)
 # High-passed diffuse water texture, no copyrighted samples.
 n2=noise-np.convolve(noise,np.ones(50)/50,mode="same").astype(np.float32)
 splash_t=6.7;dt=t-splash_t
 burst=(dt>=0)&(dt<1.8)
 v[burst]+=.08*n2[burst]*np.exp(-3*dt[burst])
 v*=np.minimum(1,t/.8)*np.minimum(1,(seconds-t)/1.2)
 v=np.tanh(v*2.3)
 stereo=np.stack((v,np.roll(v,int(sr*.013))*.94),axis=1)
 with wave.open(str(path),"wb") as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr)
  w.writeframes((np.clip(stereo,-1,1)*18000).astype("<i2").tobytes())

def finish(silent,srcmeta,modelmeta,metrics,samples):
 video=OUT/"CONEY_ISLAND_1903_LA_STORIA_RIVIVE_V73.mp4"
 music=OUT/"MUSICA_ORIGINALE.wav";seconds=(T1-T0)
 make_audio(seconds,music)
 cmd(["ffmpeg","-nostdin","-y","-v","error","-i",str(silent),"-i",str(music),"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","160k","-movflags","+faststart","-t",f"{seconds:.3f}",str(video)],120)
 cmd(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(video),"-f","null","-"],180)
 probe=json.loads(cmd(["ffprobe","-v","error","-show_entries","stream=codec_name,width,height,r_frame_rate:format=duration,size","-of","json",str(video)],30))
 if len(probe.get("streams",[]))<2 or float(probe["format"]["duration"])<17:raise RuntimeError("Incomplete output")
 frame=samples[-1][1] if samples else None
 if frame is None:raise RuntimeError("Cover frame missing")
 # Cover from actual fully colorized frame, no invented illustration.
 cv2.imwrite(str(OUT/"COPERTINA.jpg"),frame,[cv2.IMWRITE_JPEG_QUALITY,94])
 posts={
 "FACEBOOK":"Coney Island, 1903. Una discesa vertiginosa, un tuffo nell’acqua e la folla che assiste. È una vera pellicola d'epoca: il movimento appartiene al film originale, mentre i colori sono stati ricostruiti con intelligenza artificiale. Fonte: Library of Congress. #Storia #ConeyIsland #1903",
 "INSTAGRAM":"CONEY ISLAND · 1903 🎞️ Una giostra acquatica oltre un secolo fa. Il movimento è autentico; i colori sono ricostruiti con AI. Fonte: Library of Congress. #HistoryReels #OldNewYork #ConeyIsland",
 "TIKTOK":"Nel 1903 si lanciavano già così nell’acqua. 🌊 Film autentico di Coney Island, restaurato e colorizzato con AI. Fonte: Library of Congress. #history #coneyisland #1903",
 "YOUTUBE":"CONEY ISLAND 1903 | La Storia Rivive\n\nScena storica autentica di Shooting the Chutes, Luna Park (1903). Il movimento proviene dal film della Library of Congress, i colori sono una ricostruzione digitale interpretativa, non una testimonianza a colori del 1903. Musica e splash sound design composti per questa edizione; non provengono dalla pellicola. Fonte: "+PAGE
 }
 for k,v in posts.items():(OUT/("POST_"+k+".txt")).write_text(v+"\n",encoding="utf8")
 qa={
 "version":"V73","title":"Coney Island · 1903","original_record":PAGE,
 "original_file":srcmeta,"source_timecode":{"start":T0,"end":T1},
 "video":video.name,"video_sha256":sha(video),"video_size":video.stat().st_size,
 "video_probe":probe,"render":{"resolution":[W,H],"fps":FPS,"real_source_motion":True,
 "colorization":"DDColor ONNX semantic chroma anchored by optical flow; same original frame movement",
 "transition":"spatial splash-anchored progressive color","color_metrics":metrics,"not_original_4k":True},
 "color_model":modelmeta,"original_sound":"none; soundtrack created originally","rights_italy_clearance":"PENDING",
 "artistic_human_review":"PENDING","technical_full_decode":True,"zero_eur":True,"vidu_credits":0,
 "archive_upload_verified":False,"social_published":False,
 "disclosure":"Colors are modern AI hypotheses; underlying moving people/objects are original, not regenerated."
 }
 (OUT/"FONTI_E_QA.json").write_text(json.dumps(qa,indent=2,ensure_ascii=False))
 zpath=OUT/"CONEY_ISLAND_1903_KIT.zip"
 with zipfile.ZipFile(zpath,"w",compression=zipfile.ZIP_DEFLATED) as z:
  for p in [video,OUT/"COPERTINA.jpg",OUT/"FONTI_E_QA.json",OUT/"CONFRONTO_VIDEO_MOVIMENTO.jpg",*[OUT/("POST_"+k+".txt") for k in posts]]:z.write(p,p.name)
 with zipfile.ZipFile(zpath) as z:
  if z.testzip():raise RuntimeError("ZIP CRC broken")
 print("DONE_REAL_ARCHIVAL_MP4",video,video.stat().st_size,"ZIP",zpath,zpath.stat().st_size,flush=True)
if __name__=="__main__":
 source,srcmeta=acquire()
 dd,session,modelmeta=load_model()
 silent,metrics,samples=render(source,dd,session)
 finish(silent,srcmeta,modelmeta,metrics,samples)
