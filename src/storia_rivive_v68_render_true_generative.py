#!/usr/bin/env python3
"""V68 FINAL: authentic CC0 Paris movie B/W motion to SAME-FRAME FREE ZeroGPU diffusion still.
No fallback DDColor/ESRGAN for the final stills. Three verified actual diffusion photos.
"""
import hashlib, importlib.util, io, json, math, os, subprocess, wave, zipfile
from pathlib import Path
import cv2, numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("v65source",ROOT/"src/storia_rivive_v65_paris_source_contact.py")
v65=importlib.util.module_from_spec(spec);spec.loader.exec_module(v65)

OUT=Path("output/storia_rivive_v68_parigi_generativa");OUT.mkdir(parents=True,exist_ok=True)
GEN=Path(os.environ.get("V68_GENERATIVE_PHOTO_DIR","output/storia_rivive_v68_generativa_sei"))
VIDEO=OUT/"PARIGI_1918_RESTAURATA_GENERATIVA_V68.mp4"
W,H,FPS=1080,1920,30
SHOTS=[
  {"name":"La venditrice","end":265.0,"x":240,"motion":2.50,"reveal":.36,"hold":3.20,
   "description":"La venditrice di giornali e la sua clientela; la mano si ferma fra i fogli"},
  {"name":"I viaggiatori","end":32.0,"x":166,"motion":2.65,"reveal":.36,"hold":3.35,
   "description":"Un viaggiatore in cappotto, persone presso la Gare de Lyon"},
  {"name":"Il cinema","end":91.0,"x":275,"motion":2.45,"reveal":.39,"hold":3.65,
   "description":"La folla di Parigi davanti alle insegne del cinema Parisiana"},
]
OUTRO=.60

def sha(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for b in iter(lambda:f.read(2**20),b""):h.update(b)
 return h.hexdigest()

def cmd(args,timeout=200):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError((p.stderr or p.stdout)[-1200:])
 return p

def read_exact(cap,sec):
 cap.set(cv2.CAP_PROP_POS_MSEC,sec*1000)
 ok,f=cap.read()
 if not ok:raise RuntimeError("Missing authentic original frame at "+str(sec))
 if f.shape[:2]!=(576,720):raise RuntimeError("Unexpected original film dimensions "+str(f.shape))
 return f

def bw_frame(frame,x):
 bw=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
 bw=cv2.createCLAHE(clipLimit=1.35,tileGridSize=(8,8)).apply(bw)
 cropped=cv2.cvtColor(bw,cv2.COLOR_GRAY2BGR)[:,x:x+324]
 if cropped.shape[:2]!=(576,324):raise RuntimeError("Original source crop invalid")
 return cv2.resize(cropped,(W,H),interpolation=cv2.INTER_CUBIC)

def load_restored(i):
 p=GEN/f"GENERATIVA_{i:02d}.png"
 if not p.is_file():raise FileNotFoundError("NO ACTUAL DIFFUSION PHOTO; video blocked: "+str(p))
 im=cv2.imread(str(p),cv2.IMREAD_COLOR)
 if im is None or im.shape[0]<1700 or im.shape[1]<950:raise RuntimeError("Diffusion photo invalid")
 return cv2.resize(im,(W,H),interpolation=cv2.INTER_CUBIC),p

def title_overlay(img,t):
 if t>1.5:return img
 im=Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
 d=ImageDraw.Draw(im,"RGBA")
 a=min(1,t/.3)*min(1,(1.5-t)/.35)
 if a<=0:return img
 try:
  headline=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",55)
  subt=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",24)
 except OSError:headline=ImageFont.load_default();subt=ImageFont.load_default()
 d.rounded_rectangle((52,70,794,227),radius=15,fill=(7,9,12,int(148*a)))
 d.text((75,77),"PARIGI · 1918",font=headline,fill=(246,237,220,int(254*a)))
 d.line((82,165,553,165),fill=(217,176,116,int(240*a)),width=3)
 d.text((80,183),"QUANDO IL TEMPO SI FERMA",font=subt,fill=(237,236,232,int(246*a)))
 return cv2.cvtColor(np.asarray(im.convert("RGB")),cv2.COLOR_RGB2BGR)

def original_sound(duration,shots,filename):
 sr=32000
 t=np.arange(int(sr*duration),dtype=np.float32)/sr
 audio=np.zeros_like(t)
 chords=[[110,146.832,174.614,220],[98,130.813,164.814,196],[87.31,130.813,174.614,261.626]]
 onsets=[0.]
 for shot in shots[:-1]:onsets.append(onsets[-1]+shot["motion"]+shot["reveal"]+shot["hold"])
 for i,begin in enumerate(onsets):
  stop=onsets[i+1] if i+1<len(onsets) else duration
  s=(t>=begin)&(t<stop);u=t[s]-begin
  val=np.zeros_like(u)
  for k,f in enumerate(chords[i]):
   vibrato=.06*np.sin(2*np.pi*(.2+.013*k)*u)
   val+=.035*np.sin(2*np.pi*f*u+vibrato+k*.3)*(1-np.exp(-3*u))
   val+=.009*np.sin(2*np.pi*(f*2.001)*u+1.4)
  val+=.014*np.sin(2*np.pi*55*u)*np.exp(-5*u)
  audio[s]+=val
  # Original soft mallet motif throughout the actual movie rather than loud repeating beats.
  for tick in np.arange(begin+.45,stop,.72):
   v=t-tick;ss=(v>=0)&(v<.78)
   freq=chords[i][int((tick-begin)/.72)%4]*2
   audio[ss]+=.033*np.sin(2*np.pi*freq*v[ss])*np.exp(-4.5*v[ss])
  marker=begin+shots[i]["motion"]
  v=t-marker;ss=(v>=0)&(v<.7)
  audio[ss]+=.11*np.sin(2*np.pi*(86*v[ss]+38*v[ss]**2))*np.exp(-7*v[ss])
 # Gentle original dynamic foley texture, low in mix.
 np.random.seed(1918)
 noise=np.random.randn(len(t)).astype(np.float32)
 smoothed=np.convolve(noise,np.ones(200,dtype=np.float32)/200,mode="same")
 audio+=.007*smoothed
 audio*=np.minimum(1,t/.85)*np.minimum(1,np.maximum(0,(duration-t)/.95))
 audio=np.tanh(audio*2.6)
 stereo=np.stack((audio,np.roll(audio,193)*.96),axis=1)
 data=(np.clip(stereo,-1,1)*18500).astype("<i2")
 with wave.open(str(filename),"wb") as f:
  f.setframerate(sr);f.setnchannels(2);f.setsampwidth(2);f.writeframes(data.tobytes())

def build():
 source,rights=v65.original()
 cap=cv2.VideoCapture(str(source))
 if not cap.isOpened():raise RuntimeError("Original archive unreadable")
 photo_list=[load_restored(i)[0] for i in range(1,4)]
 pipeline=OUT/"RENDER_VIDEO_ONLY.mp4"
 enc=subprocess.Popen(["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error",
   "-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
   "-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p",
   "-movflags","+faststart",str(pipeline)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 if enc.stdin is None:raise RuntimeError("Encoder stdin missing")
 totalframes=0;stats=[];qa_source=[]
 try:
  for i,s in enumerate(SHOTS):
   photo=photo_list[i]
   start=s["end"]-s["motion"]
   nmove=round(s["motion"]*FPS)
   for k in range(nmove):
    frame=bw_frame(read_exact(cap,start+k/FPS),s["x"])
    if i==0:frame=title_overlay(frame,totalframes/FPS)
    enc.stdin.write(frame.tobytes())
    totalframes+=1
   same_keyframe=bw_frame(read_exact(cap,s["end"]),s["x"])
   qa_source.append(same_keyframe.copy())
   nrev=round(s["reveal"]*FPS)
   for k in range(nrev):
    v=(k+1)/nrev; alpha=v*v*(3-2*v)
    blended=cv2.addWeighted(same_keyframe,1-alpha,photo,alpha,0)
    enc.stdin.write(blended.tobytes());totalframes+=1
   nstill=round(s["hold"]*FPS)
   for k in range(nstill):
    # Actual frozen high-detail reconstructed photograph — NO moving archive under it.
    enc.stdin.write(photo.tobytes());totalframes+=1
   stats.append({"scene":i+1,"archival_end_sec":s["end"],"source_name":v65.TITLE,
    "source_frame_really_from_archive":True,"photo_generated_using_diffusion":True,
    "photo_file":f"GENERATIVA_{i+1:02d}.png","photo_sha256":sha(GEN/f"GENERATIVA_{i+1:02d}.png"),
    "motion_frames":nmove,"transition_frames":nrev,"still_frames":nstill,
    "subject":s["name"],"reason":s["description"]})
   print("V68_REEL_SCENE_DONE",i+1,s["name"],flush=True)
  # Short gentle fade-out on last restored frame, without adding a new/fake shot.
  last=photo_list[-1]
  for k in range(round(OUTRO*FPS)):
   v=1-k/max(1,OUTRO*FPS-1)
   faded=(last.astype(np.float32)*v).astype(np.uint8)
   enc.stdin.write(faded.tobytes());totalframes+=1
 finally:
  cap.release();enc.stdin.close()
 stderr=enc.stderr.read()
 if enc.wait()!=0:raise RuntimeError("Video encoder failed "+stderr.decode(errors="ignore")[-850:])
 duration=totalframes/FPS
 audio=OUT/"MUSICA_CINEMATOGRAFICA_ORIGINALE.wav"
 original_sound(duration,SHOTS,audio)
 cmd(["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error",
  "-i",str(pipeline),"-i",str(audio),"-map","0:v","-map","1:a","-c:v","copy",
  "-c:a","aac","-b:a","150k","-shortest","-movflags","+faststart",str(VIDEO)])
 cmd(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(VIDEO),"-f","null","-"])
 # Assert true stillness during each generated photo and real motion in black/white segments.
 cap=cv2.VideoCapture(str(VIDEO));cursor=0
 for i,s in enumerate(SHOTS):
  move=round(s["motion"]*FPS);rev=round(s["reveal"]*FPS);hold=round(s["hold"]*FPS)
  def at(n):
   cap.set(cv2.CAP_PROP_POS_FRAMES,n)
   ok,f=cap.read()
   if not ok:raise RuntimeError("QA missing output frame "+str(n))
   return cv2.resize(f,(120,213))
  a=at(cursor+move+rev+max(3,round(hold*.22)))
  b=at(cursor+move+rev+max(4,round(hold*.77)))
  diff=float(np.abs(a.astype("float32")-b.astype("float32")).mean())
  if diff>1.4:raise RuntimeError("Photo not frozen: "+str(diff))
  stats[i]["still_frame_difference"]=round(diff,4)
  cursor+=move+rev+hold
 cap.release()
 # Two-row documentary contact sheet to expose any face/pose hallucinations.
 board=Image.new("RGB",(3*346,2*650),(17,17,20))
 for i,s in enumerate(SHOTS):
  bw=cv2.cvtColor(qa_source[i],cv2.COLOR_BGR2RGB)
  co=cv2.cvtColor(photo_list[i],cv2.COLOR_BGR2RGB)
  for row,im in enumerate((bw,co)):
   tile=Image.fromarray(im).resize((336,597),Image.Resampling.LANCZOS)
   board.paste(tile,(i*346+5,row*650+30))
  ImageDraw.Draw(board).text((i*346+8,6),s["name"],fill=(246,241,230))
  ImageDraw.Draw(board).text((i*346+8,655),"Fotografia AI ricostruita",fill=(246,241,230))
 board.save(OUT/"V68_TRE_SCENE_ORIGINALE_VS_DIFFUSIONE.jpg",quality=94)
 # Elegant cover uses genuinely generated photo, not imagegen's unrelated Rome render.
 first=Image.fromarray(cv2.cvtColor(photo_list[0],cv2.COLOR_BGR2RGB))
 d=ImageDraw.Draw(first,"RGBA")
 d.rounded_rectangle((40,60,960,279),radius=15,fill=(4,5,8,153))
 try:
  f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",64)
  g=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",25)
 except OSError:f=ImageFont.load_default();g=ImageFont.load_default()
 d.text((70,70),"PARIGI · 1918",fill=(251,241,220,255),font=f)
 d.text((73,170),"IL TEMPO SI FERMA",fill=(240,239,236,255),font=g)
 d.text((73,217),"Riprese autentiche · fotografie ricostruite",fill=(219,221,222,250),font=g)
 first.save(OUT/"COPERTINA.jpg",quality=93)
 metadata={
  "video_title":"Parigi 1918 — Il tempo si ferma | Restaurata con IA generativa",
  "output_status":"REAL_DIFFUSION_RENDERED_TECHNICAL_QA_PASSED_ARTISTIC_REVIEW_REQUIRED",
  "source_license":rights,"source_sha256":sha(source),"source_rights":"Exact Wikimedia CC0 file; verify other residual legal/privacy rights",
  "source_episodes_are_not_all_same_day":True,
  "new_model":"finegrain/finegrain-image-enhancer, public free ZeroGPU, Stable Diffusion 1.5 / ControlNet tile + restoration",
  "not_used_for_stills":"DDColor + ESRGAN alone as V65 final stills",
  "disclosure":"Historical movements are genuine. Photorealistic colors, skin and invented microdetails are AI reconstruction, not recorded facts.",
  "generated_photo_source":"V65 DDColor color photo from same source original keyframe, then real diffusion enhancement",
  "model_fidelity":"Reference/ControlNet constraint; faces may be inferred differently from historical reality",
  "dimensions_px":[W,H],"native_4k":False,"fps":FPS,
  "duration_s":round(duration,3),"mp4_sha256":sha(VIDEO),"mp4_bytes":VIDEO.stat().st_size,
  "full_decode":True,"no_paid_services_or_vidu":True,
  "no_social_auto_publish":True,"video_library_site_uploaded":False,
  "qa_human_reviewer":"Needs user comparison against reference videos",
  "shots":stats}
 (OUT/"FONTI_DIRITTI_RICOSTRUZIONE_QA.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 posts={
 "FACEBOOK":"Parigi, 1918. Una donna vende giornali, i viaggiatori affollano la stazione e fuori dal cinema la città continua a vivere. Poi, per un istante, il tempo si ferma: il vero filmato in bianco e nero diventa una fotografia ricostruita con intelligenza artificiale. Volti, stoffe e insegne acquistano nuove texture: sono interpretazioni digitali, non particolari storicamente accertati. Riprese autentiche Musée Albert-Kahn / Wikimedia Commons CC0. #Parigi1918 #LaStoriaRivive #RestauroFotografico",
 "INSTAGRAM":"PARIGI 1918 🎞️ Tre istanti di vita reale: la venditrice di giornali, i viaggiatori, il cinema. La pellicola si muove; l'immagine si ferma e diventa una fotografia ricostruita nei dettagli con IA generativa. Fonte storica CC0: Musée Albert-Kahn / Wikimedia Commons. Colori e dettagli nuovi sono interpretazioni, non fotografie originali a colori. #HistoryReels #Paris1918 #LaStoriaRivive",
 "TIKTOK":"Parigi nel 1918… e se il tempo si fermasse? 👀 Filmati autentici in bianco e nero diventano fotografie realistiche ricostruite con IA. I movimenti sono originali, i dettagli e i colori sono ipotesi digitali. Archivio Musée Albert-Kahn, CC0. #storia #parigi #restauro #AI",
 "YOUTUBE":"PARIGI 1918 | IL TEMPO SI FERMA — VERE RIPRESE, RESTAURO FOTOGRAFICO GENERATIVO\n\nUn breve viaggio nel 1918: una venditrice di giornali, persone alla Gare de Lyon e la folla davanti a un cinema di Parigi. Le riprese in bianco e nero sono autentiche e provengono dal Musée départemental Albert-Kahn, file CC0 su Wikimedia Commons. Ogni scena viene fermata su un fotogramma originale; i colori e microdettagli sono restaurati con DDColor e una successiva ricostruzione fotografica di diffusione tramite Finegrain/ControlNet. Questi particolari possono differire dall'aspetto storico reale, specialmente i volti. La pellicola originale non è in 4K e i momenti non sono necessariamente filmati nella stessa data. Musica originale creata per l'episodio.\nFonte: "+v65.PAGE}
 for social,body in posts.items(): (OUT/f"POST_{social}.txt").write_text(body+"\n",encoding="utf8")
 (OUT/"LEGGIMI.txt").write_text("Parigi 1918. Video 1080x1920/H264/AAC, TRE riprese autentiche diverse e TRE fotografie IA generative. Non sono fotogrammi in vero colore storico né riprese 4K native. Nessun credito Vidu e nessuna chiamata a GPU a pagamento. Archiviazione sito privato non ancora effettuata.\n",encoding="utf8")
 kit=OUT/"PARIGI_1918_V68_RESTAURO_GENERATIVO_COMPLETO.zip"
 files=[VIDEO,OUT/"COPERTINA.jpg",OUT/"V68_TRE_SCENE_ORIGINALE_VS_DIFFUSIONE.jpg",OUT/"FONTI_DIRITTI_RICOSTRUZIONE_QA.json",OUT/"LEGGIMI.txt",*[OUT/f"POST_{x}.txt" for x in posts],*[GEN/f"GENERATIVA_{i:02d}.png" for i in range(1,4)]]
 with zipfile.ZipFile(kit,"w",compression=zipfile.ZIP_DEFLATED) as z:
  for f in files:z.write(f,f.name)
 with zipfile.ZipFile(kit) as z:
  if z.testzip():raise RuntimeError("Kit CRC fails")
 print("V68_REAL_DIFFUSION_VIDEO_COMPLETE",json.dumps({"mp4":str(VIDEO),"size":VIDEO.stat().st_size,"duration_s":duration,"zip":str(kit),"sha256":sha(VIDEO)},ensure_ascii=False),flush=True)
if __name__=="__main__":
 build()
