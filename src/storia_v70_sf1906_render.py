#!/usr/bin/env python3
"""V70 finish real archival motion -> exact frame freeze -> ACTUAL generated photo, no fake upscales.
Requires actual previously generated V70 photos, original film + their SHA provenance.
Creates 1080x1920 H264/AAC reel, original music, QA, cover + four captions + ZIP.
"""
import importlib.util,hashlib,io,json,os,subprocess,zipfile,wave,math
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=Path("output/storia_v70_sf1906");OUT.mkdir(parents=True,exist_ok=True)
M=importlib.util.spec_from_file_location("source_v70",ROOT/"src/storia_v70_sf1906_source_scout.py")
src=importlib.util.module_from_spec(M);M.loader.exec_module(src)
S=importlib.util.spec_from_file_location("photos_v70",ROOT/"src/storia_v70_sf1906_photo_ai.py")
photo_module=importlib.util.module_from_spec(S);S.loader.exec_module(photo_module)
W,H,FPS=1080,1920,30
MASTER=OUT/"SAN_FRANCISCO_1906_WOW_FOTO_GENERATIVE_V70.mp4"

def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()

def command(args,timeout=160):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError("Cmd failed "+str(args[:2])+p.stderr[-1100:])
 return p

def getphotos():
 manifest=json.loads((OUT/"RESTORATION_QA.json").read_text(encoding="utf8"))
 if manifest.get("original_video_sha256")!="c8b30802c0fbeb5f9ec3dc9af3e4f71ef627a863d4abba5550b63998cb46725a":
  raise RuntimeError("Original historical movie hash mismatch")
 if manifest.get("no_paid_credits") is not True:raise RuntimeError("Unexpected paid service")
 s=manifest.get("results",[])
 if len(s)<3:raise RuntimeError("Need at least 3 REAL generatively restored photos")
 checked=[]
 for i,a in enumerate(s):
  if i>=len(photo_module.SHOTS) or a["scene"]!=i+1:raise RuntimeError("Photo/scene indices do not match")
  f=OUT/a["photo"];orig=OUT/a["source_frame"]
  if not f.is_file() or sha(f)!=a["photo_sha256"] or not orig.is_file() or sha(orig)!=a["source_frame_sha256"]:
   raise RuntimeError("Generated photo/source SHA not verifiable")
  image=cv2.imread(str(f))
  if image is None or image.shape[:2]!=(1920,1080):raise RuntimeError("photo missing or wrong size")
  if a["coarse_layout_corr"]<.73:raise RuntimeError("AI changed source scene geometry")
  checked.append((a,image))
 return manifest,checked

def title(frame,show=False):
 if not show:return frame
 img=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
 d=ImageDraw.Draw(img,"RGBA")
 try:
  one=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",57)
  two=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",24)
 except OSError:
  one=ImageFont.load_default();two=ImageFont.load_default()
 d.rounded_rectangle((32,38,735,183),radius=14,fill=(5,5,9,104))
 d.text((58,45),"SAN FRANCISCO · 1906",font=one,fill=(250,242,228,248))
 d.text((62,133),"PRIMA DEL TERREMOTO",font=two,fill=(236,235,231,246))
 return cv2.cvtColor(np.asarray(img.convert("RGB")),cv2.COLOR_RGB2BGR)

def motion_frames(original,s):
 # Timestamp-based source clip starting before exact AI photo keyframe.
 cap=cv2.VideoCapture(str(original))
 fps=cap.get(cv2.CAP_PROP_FPS)
 if abs(fps-24)>1:raise RuntimeError("Expected 24fps genuine 1906 source")
 start=s["sec"]-s["motion"]
 cap.set(cv2.CAP_PROP_POS_MSEC,start*1000)
 frames=[];source_index=-1;last=None
 n=round(s["motion"]*FPS)
 for k in range(n):
  needed=min(int(k*fps/FPS),round(s["motion"]*fps)-1)
  while source_index<needed:
   ok,last=cap.read()
   if not ok:raise RuntimeError("Actual 1906 footage missing at "+str(start))
   source_index+=1
  crop=last[:,s["x"]:s["x"]+603]
  gray=cv2.cvtColor(crop,cv2.COLOR_BGR2GRAY)
  bw=cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)
  output=cv2.resize(bw,(W,H),interpolation=cv2.INTER_CUBIC)
  frames.append(output)
 cap.release()
 if len(frames)!=n:raise RuntimeError("Incomplete motion")
 return frames

def music(total,cues,file):
 # Original spectral ambient piano and strings, no samples or copyrighted recordings.
 sr=32000
 t=np.arange(round(total*sr),dtype=np.float32)/sr
 signal=np.zeros_like(t)
 chord=[[110,164.81,220],[130.81,164.81,261.63],[98,146.83,196],[110,174.61,220]]
 for j,at in enumerate(cues):
  end=cues[j+1] if j+1<len(cues) else total
  mask=(t>=at)&(t<end);q=t[mask]-at
  v=np.zeros_like(q)
  for k,f in enumerate(chord[j%len(chord)]):
   vibr=.0004*np.sin(2*np.pi*(.08+.02*k)*q)
   v+=.028*np.sin(2*np.pi*(f*q+vibr)+k*.5)
   v+=.006*np.sin(2*np.pi*f*2.001*q+k*.3)
  v*=np.minimum(1,q/.47)
  v+=.07*np.exp(-6*q)*np.sin(2*np.pi*66*q)
  signal[mask]+=v
  # Single restrained shimmer emphasizes color change (no camera flash).
  tt=t-(at+photo_module.SHOTS[j]["motion"])
  gate=(tt>=0)&(tt<.7)
  signal[gate]+=.075*np.sin(2*np.pi*(140*tt[gate]+70*tt[gate]**2))*np.exp(-8*tt[gate])
  for b in np.arange(.1,end-at,.64):
   tt=t-(at+b);gate=(tt>=0)&(tt<.46)
   freq=chord[j%len(chord)][int(b/.64)%3]*4
   signal[gate]+=.032*np.sin(2*np.pi*freq*tt[gate])*np.exp(-9*tt[gate])
 signal*=np.minimum(1,t/.75)*np.minimum(1,(total-t)/.85)
 signal=np.tanh(signal*3)
 stereo=np.column_stack((signal,np.roll(signal,int(.01*sr))*.94))
 pcm=(np.clip(stereo,-1,1)*19000).astype("<i2")
 with wave.open(str(file),"wb") as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes(pcm.tobytes())

def render():
 rights=src.original()
 srcfile=src.SOURCE
 manifest,checked=getphotos()
 if srcfile.stat().st_size!=127835024 or sha(srcfile)!=manifest["original_video_sha256"]:
  raise RuntimeError("Unverified original 1906 film")
 silent=OUT/"V70_SENZA_AUDIO.mp4"
 proc=subprocess.Popen(["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error",
  "-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),
  "-i","-","-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p",str(silent)],
  stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 frame_count=0;scene_info=[];start_cues=[]
 try:
  for i,(a,color) in enumerate(checked):
   s=photo_module.SHOTS[i];start_cues.append(frame_count/FPS)
   frames=motion_frames(srcfile,s)
   # Keyframe used for actual AI photo, not just arbitrarily adjacent motion.
   original=cv2.imread(str(OUT/a["source_frame"]))
   bgr=cv2.cvtColor(cv2.cvtColor(original,cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR)
   bw=cv2.resize(bgr,(W,H),interpolation=cv2.INTER_CUBIC)
   for k,frame in enumerate(frames):
    # Opening 0.8 seconds only; don't hide the photo or repeat on other scenes.
    proc.stdin.write(title(frame,show=(i==0 and k<round(.75*FPS))).tobytes())
    frame_count+=1
   n=round(s["reveal"]*FPS)
   for k in range(n):
    alpha=(k+1)/n;alpha=alpha*alpha*(3-2*alpha)
    out=cv2.addWeighted(bw,1-alpha,color,alpha,0)
    proc.stdin.write(out.tobytes());frame_count+=1
   hold=round(s["hold"]*FPS)
   for k in range(hold):
    proc.stdin.write(color.tobytes());frame_count+=1
   scene_info.append({"name":s["name"],"subject":s["subject"],"exact_original_time_s":s["sec"],
    "same_original_frame_sha256":sha(OUT/a["source_frame"]),
    "true_AI_generated_photo_sha256":sha(OUT/a["photo"]),
    "moving_frame_count":len(frames),"reveal_frame_count":n,"frozen_photo_frame_count":hold,
    "coarse_geometry_similarity":a["coarse_layout_corr"],"Vidu_spend":0})
   print("V70_SCENE_ENCODED",i+1,s["name"],"frames_total",frame_count,flush=True)
 finally:
  proc.stdin.close()
 err=proc.stderr.read().decode(errors="ignore")
 if proc.wait()!=0:raise RuntimeError("H264 encoder failure "+err[-900:])
 duration=frame_count/FPS
 if duration<15 or duration>30:raise RuntimeError("Montage duration invalid "+str(duration))
 wav=OUT/"AUDIO_ORIGINALE_V70.wav";music(duration,start_cues,wav)
 command(["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error",
  "-i",str(silent),"-i",str(wav),"-map","0:v:0","-map","1:a:0",
  "-c:v","copy","-c:a","aac","-b:a","160k","-metadata",
  "comment=Filmati storici autentici 1906, fotografie a colori ricostruite con IA; dettagli non documentati.",
  "-t",str(duration),"-movflags","+faststart",str(MASTER)])
 command(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(MASTER),"-f","null","-"],180)
 # Verify exact actual stills do not move after transformation.
 video=cv2.VideoCapture(str(MASTER))
 idx=0;quality=[]
 for j,si in enumerate(scene_info):
  idx+=si["moving_frame_count"]+si["reveal_frame_count"]
  t1=(idx+round(.3*FPS))/FPS;t2=(idx+round(.7*FPS))/FPS
  def read(t):
   video.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,f=video.read()
   if not ok:raise RuntimeError("Output video frame cannot decode")
   return cv2.resize(f,(120,213))
  a,b=read(t1),read(t2)
  diff=float(np.mean(np.abs(a.astype(np.float32)-b.astype(np.float32))))
  if diff>1.5:raise RuntimeError(f"Photo {j+1} not frozen in final MP4: {diff:.2f}")
  quality.append({"shot":si["name"],"photo_hold_mean_abs_difference":round(diff,3)})
  idx+=si["frozen_photo_frame_count"]
 video.release()
 cover=cv2.imread(str(OUT/checked[0][0]["photo"]))
 cv2.imwrite(str(OUT/"COPERTINA.jpg"),title(cover,show=True),[cv2.IMWRITE_JPEG_QUALITY,93])
 posts={
 "FACEBOOK":"San Francisco, 1906. Un passante, un'automobile, un tram e le persone al porto. Tutto filmato realmente, poco prima del terremoto che cambiò la città. Ogni ripresa si ferma e diventa una fotografia a colori ricostruita con AI. I colori e i dettagli dei volti sono interpretazioni digitali e non dati storici certi. Pellicola originale Miles Brothers, archivio di pubblico dominio su Wikimedia Commons. #SanFrancisco1906 #Storia #LaStoriaRivive",
 "INSTAGRAM":"SAN FRANCISCO, 1906 🎞️ Il passato si muove. Un istante dopo, tutto si ferma: occhi, tram, automobili, cappelli e pietre tornano a vivere in una fotografia a colori ricostruita con AI. Riprese autentiche Miles Brothers, pubblico dominio; dettagli e colori non sono fatti documentati. #HistoryReels #1906 #LaStoriaRivive",
 "TIKTOK":"Come sembrava San Francisco prima del terremoto del 1906? 👀 La pellicola è vera: si ferma e il fotogramma diventa una fotografia ricostruita a colori con AI! I dettagli aggiunti sono interpretazioni, non colori originali. #1906 #history #aiart #storia",
 "YOUTUBE":"SAN FRANCISCO 1906 | Prima del terremoto, il tempo si ferma\n\nQuattro momenti autentici del film A Trip down Market Street (1906), ripresa d'epoca dei Miles Brothers: passante, automobile, tram e gruppo davanti al Ferry Building. Ogni scena in bianco e nero si muove davvero, poi resta ferma su una fotografia in cui colore e texture sono ricostruiti digitalmente con DDColor e un modello image-to-image Finegrain. I dettagli dei volti e i colori sono ipotesi, non testimonianza fotografica autentica. Fonte: "+src.PAGE+". Film originale indicato public domain su Wikimedia Commons. Musica originale per questo video."
 }
 for k,v in posts.items():(OUT/("POST_"+k+".txt")).write_text(v+"\n",encoding="utf8")
 report={"version":"V70","title":"San Francisco 1906 — La Storia Rivive","duration_s":round(duration,3),
  "resolution":[W,H],"true_4k_native":False,"input_source_raster":[1440,1072],
  "source_original_sha256":rights["file_sha256"],"source_page":src.PAGE,"PD_declaration":rights["license_marked"],
  "video_sha256":sha(MASTER),"video_bytes":MASTER.stat().st_size,
  "source_and_model_provenance_SHA_checked":True,"real_AI_generated_photographs":len(checked),
  "full_ffmpeg_video_decode_passed":True,"frame_stillness_QA":quality,
  "scenes":scene_info,"historical_disclosure":"Colors, faces, text and textures generated by AI may not reflect the actual historical details",
  "human_identity_historical_certainty":False,"site_upload_verified":False,
  "rights_Italy_review":"US public domain mark; territorial editorial review required before commercial use",
  "any_paid_video_generation":False,"artistic_reviewer_pass":False,
  "status":"PREVIEW_TO_BE_VISUALLY_REVIEWED"}
 (OUT/"V70_QA_REPORT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 kit=OUT/"SAN_FRANCISCO_1906_FOTOGRAFIE_GENERATIVE_KIT.zip"
 with zipfile.ZipFile(kit,"w",compression=zipfile.ZIP_DEFLATED) as z:
  for f in [MASTER,OUT/"COPERTINA.jpg",OUT/"CONTATTI_PRIMA_DOPO_AI_V70.jpg",
   OUT/"RESTORATION_QA.json",OUT/"V70_QA_REPORT.json",
   *[OUT/("POST_"+k+".txt") for k in posts],
   *[OUT/a["photo"] for a,_ in checked]]:
   z.write(f,f.name)
 with zipfile.ZipFile(kit) as z:
  if z.testzip():raise RuntimeError("Pack corrupted")
 print("V70_FINAL_ACTUAL_MP4_READY",json.dumps({"video":str(MASTER),"duration_s":duration,
  "size":MASTER.stat().st_size,"kit":str(kit),"sha256":sha(MASTER)}),flush=True)

if __name__=="__main__":render()
