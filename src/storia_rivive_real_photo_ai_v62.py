#!/usr/bin/env python3
"""V62: Real CC0 1919 moving footage -> frozen *AI-restored photo* (DDColor + RealESRGAN).
Costs 0 Vidu/API. This script produces full H264/AAC reel, 6 photos, cover, 4 posts, and ZIP.
Photos preserve the source frame's layout; their reconstructed colors and microdetail are hypotheses.
"""
import cv2, hashlib, importlib.util, json, math, os, subprocess, sys, wave, zipfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from huggingface_hub import hf_hub_download
import onnxruntime as ort

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("historical_v60",ROOT/"src/storia_rivive_real_ai_v60.py")
v60=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(v60)

OUT=Path("output/storia_rivive_v62_photo_freeze")
OUT.mkdir(parents=True,exist_ok=True)
VIDEO=OUT/"LA_STORIA_RIVIVE_BEIRUT_1919_FOTO_AI_V62.mp4"
W,H,FPS=720,1280,30
MOTION=1.24;REVEAL=.36;HOLD=1.43
# Each end time is the exact frame used to generate the restored photograph.
SHOTS=[
 {"id":"01","name":"Il cammello","end":147.95,"x":270,"why":"Il volto del cammello emerge all'improvviso fra la gente"},
 {"id":"02","name":"Il mercato","end":122.15,"x":247,"why":"La folla e le merci di un mercato pieno di vita"},
 {"id":"03","name":"Il porto","end":22.85,"x":181,"why":"Le persone lungo la banchina e le imbarcazioni"},
 {"id":"04","name":"La famiglia","end":166.50,"x":238,"why":"Vite e volti in una strada di pietra"},
 {"id":"05","name":"Il lavoro","end":47.75,"x":269,"why":"Le figure fra le barche e le strutture del porto"},
 {"id":"06","name":"La città","end":90.80,"x":246,"why":"La folla attraversa la città nel 1919"}
]

def sha(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as fp:
  for data in iter(lambda:fp.read(2**20),b""):h.update(data)
 return h.hexdigest()

def command(args,timeout=120):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError(" ".join(args[:2])+": "+p.stderr[-1200:])
 return p

def setup_upscaler():
 repo="lxfater/inpaint-web";file="realesrgan-x4.onnx"
 model=Path(hf_hub_download(repo_id=repo,filename=file))
 expected="fa18ce70de3a55f3149d0cc898d335d2d69fca29edc0692cb362c856b2942c3f"
 actual=sha(model)
 if actual!=expected:raise ValueError("RealESRGAN exact model SHA mismatch: "+actual)
 so=ort.SessionOptions()
 so.intra_op_num_threads=4;so.inter_op_num_threads=1
 so.graph_optimization_level=ort.GraphOptimizationLevel.ORT_ENABLE_ALL
 session=ort.InferenceSession(str(model),sess_options=so,providers=["CPUExecutionProvider"])
 print("ESRGAN_READY",session.get_inputs()[0].shape,session.get_outputs()[0].shape,flush=True)
 return session,{"repo":repo,"file":file,"sha256":actual,
                 "upstream":"https://github.com/xinntao/Real-ESRGAN","license":"model file GPL-3.0; upstream architecture BSD-3-Clause"}

def esrgan_4x(session,bgr):
 # Tiled CPU ONNX restoration, never replace source geometry.
 rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
 h,w=rgb.shape[:2]
 core,pad=96,12
 framed=cv2.copyMakeBorder(rgb,pad,pad,pad,pad,cv2.BORDER_REFLECT_101)
 result=np.zeros((h*4,w*4,3),dtype=np.uint8)
 input_name=session.get_inputs()[0].name
 for y in range(0,h,core):
  for x in range(0,w,core):
   ch=min(core,h-y);cw=min(core,w-x)
   tile=framed[y:y+ch+2*pad,x:x+cw+2*pad]
   n=np.transpose(tile.astype(np.float32)/255,(2,0,1))[None]
   pred=session.run(None,{input_name:n})[0]
   if pred.ndim!=4 or pred.shape[1]!=3 or pred.shape[2]!=tile.shape[0]*4 or pred.shape[3]!=tile.shape[1]*4:
    raise ValueError("Unexpected ESRGAN output "+str(pred.shape))
   crop=pred[0,:,pad*4:(pad+ch)*4,pad*4:(pad+cw)*4].transpose(1,2,0)
   result[y*4:(y+ch)*4,x*4:(x+cw)*4]=np.clip(crop*255,0,255).astype("uint8")
 return cv2.cvtColor(result,cv2.COLOR_RGB2BGR)

def extract_frame(capture,when):
 capture.set(cv2.CAP_PROP_POS_MSEC,when*1000)
 ok,frame=capture.read()
 if not ok:raise RuntimeError("Missing original archival frame at "+str(when))
 return frame

def crop9(frame,x):
 h,w=frame.shape[:2];width=round(h*9/16);x=int(max(0,min(x,w-width)))
 return frame[:,x:x+width].copy()

def historical_frame(frame,x):
 bw=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
 # Gentle photographic cleaning but retains grain, motion and physical structure.
 bw=cv2.createCLAHE(clipLimit=1.45,tileGridSize=(8,8)).apply(bw)
 image=crop9(cv2.cvtColor(bw,cv2.COLOR_GRAY2BGR),x)
 image=cv2.resize(image,(W,H),interpolation=cv2.INTER_CUBIC)
 return image

def color_photo(frame,x,ddcolor,esrgan):
 # DDColor is genuinely semantic color AI; Real-ESRGAN is a genuine learned photo-detail restoration.
 ab=v60.infer_ab(ddcolor,frame)
 colored=v60.image_at(frame,ab)
 crop=crop9(colored,x)
 resized=cv2.resize(crop,(240,427),interpolation=cv2.INTER_AREA)
 enhanced=esrgan_4x(esrgan,resized)
 # restrained film-restore finishing: preserve original identities, no inpainting or face replacement
 yuv=cv2.cvtColor(enhanced,cv2.COLOR_BGR2LAB)
 l,a,b=cv2.split(yuv)
 l=cv2.createCLAHE(clipLimit=1.38,tileGridSize=(8,8)).apply(l)
 enhanced=cv2.cvtColor(cv2.merge((l,a,b)),cv2.COLOR_LAB2BGR)
 # true 960x1708 learned upscaling pixels; 720x1280 delivery retains original framing.
 photo=cv2.resize(enhanced,(W,H),interpolation=cv2.INTER_AREA)
 photo=cv2.detailEnhance(photo,sigma_s=9,sigma_r=.14)
 return photo

def word_image(frame,caption,number,photo=False):
 img=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
 d=ImageDraw.Draw(img,"RGBA")
 try:
  big=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",31)
  small=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",19)
 except OSError:
  big=ImageFont.load_default();small=ImageFont.load_default()
 # Text reserved for first part + final; no graphics obscuring historical faces.
 d.rounded_rectangle((37,44,360,124),radius=8,fill=(10,10,14,112))
 d.text((50,52),"BEIRUT  ·  1919",font=big,fill=(255,248,232,246))
 d.text((52,97),caption.upper(),font=small,fill=(235,227,203,236))
 if photo:
  d.rounded_rectangle((35,H-91,380,H-44),radius=7,fill=(0,0,0,115))
  d.text((46,H-77),"FOTOGRAFIA RICOSTRUITA CON IA",font=small,fill=(238,233,225,246))
 return cv2.cvtColor(np.asarray(img.convert("RGB")),cv2.COLOR_RGB2BGR)

def audio(total,path,beats):
 # Original pulsing cinematic ambient orchestration, not copyrighted audio.
 sr=32000
 t=np.arange(int(total*sr),dtype=np.float32)/sr
 signal=np.zeros_like(t)
 chords=[[110,164.81,220],[98,146.83,196],[130.81,164.81,261.63],
         [110,174.61,220],[98,146.83,246.94],[110,164.81,220]]
 for i,onset in enumerate(beats):
  end=min(total,beats[i+1] if i+1<len(beats) else total)
  seg=(t>=onset)&(t<end);u=t[seg]-onset
  if len(u)==0:continue
  vals=np.zeros_like(u)
  for k,f in enumerate(chords[i%len(chords)]):
   vibrato=.0007*np.sin(2*np.pi*(.09+k*.02)*u)
   vals+=.032*np.sin(2*np.pi*(f*u+vibrato))*np.minimum(1,u/.5)
   vals+=.013*np.sin(2*np.pi*f*2.002*u+1.3)
  vals+=.018*np.sin(2*np.pi*55*u)*np.exp(-4*u)
  signal[seg]+=vals
  for at in [onset+MOTION,onset+MOTION+REVEAL]:
   tt=t-at;sel=(tt>=0)&(tt<.66)
   signal[sel]+=.11*np.sin(2*np.pi*(85*tt[sel]-24*tt[sel]**2))*np.exp(-8*tt[sel])
  # subtle low impacts precisely on cuts
  tt=t-onset;sel=(tt>=0)&(tt<.32)
  signal[sel]+=.12*np.sin(2*np.pi*(70-25*tt[sel])*tt[sel])*np.exp(-10*tt[sel])
 signal*=np.minimum(1,t/.8)*np.minimum(1,(total-t)/.7)
 signal=np.tanh(signal*3.8)
 # Stereo pseudo widening with 10ms decorrelation, tasteful not extreme
 stereo=np.column_stack([signal,np.roll(signal,int(.007*sr))*.92])
 samples=(np.clip(stereo,-1,1)*16000).astype("<i2")
 with wave.open(str(path),"wb") as wav:
  wav.setnchannels(2);wav.setsampwidth(2);wav.setframerate(sr);wav.writeframes(samples.tobytes())

def produce():
 original,rights=v60.get_source()
 ddcolor,ddmeta=v60.download_model()
 esrgan,esmeta=setup_upscaler()
 cap=cv2.VideoCapture(str(original))
 if not cap.isOpened():raise RuntimeError("Archive film could not be opened")
 pre=OUT/"V62_VIDEO_SENZA_AUDIO.mp4"
 proc=subprocess.Popen(["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error",
                        "-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),
                        "-i","-","-c:v","libx264","-preset","veryfast","-crf","18",
                        "-pix_fmt","yuv420p",str(pre)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 if not proc.stdin:raise RuntimeError("No video encoder stdin")
 count=0;scene_meta=[];beats=[]
 photos=[]
 for i,s in enumerate(SHOTS):
  start=max(0,s["end"]-MOTION);beats.append(count/FPS)
  end_frame=extract_frame(cap,s["end"])
  # ONE accurate original frame for each new AI-restored photograph.
  photo=color_photo(end_frame,s["x"],ddcolor,esrgan)
  path=OUT/(f"FOTO_AI_{i+1:02d}.jpg")
  cv2.imwrite(str(path),photo,[cv2.IMWRITE_JPEG_QUALITY,93])
  photos.append(photo)
  still=word_image(photo,s["name"],i+1,True)
  raw_moving=[]
  for k in range(round(MOTION*FPS)):
   frame=extract_frame(cap,start+k/FPS)
   moving=historical_frame(frame,s["x"])
   raw_moving.append(moving)
  # last moving image is frozen exactly (approximately within one source-frame).
  freeze=historical_frame(end_frame,s["x"])
  for fi,m in enumerate(raw_moving):
   im=word_image(m,s["name"],i+1,False)
   proc.stdin.write(im.tobytes());count+=1
  ntrans=round(REVEAL*FPS)
  for k in range(ntrans):
   a=(k+1)/ntrans
   smooth=a*a*(3-2*a)
   blended=cv2.addWeighted(freeze,1-smooth,photo,smooth,0)
   # short white shimmer at halfway, without hiding frame continuity
   glare=max(0,1-abs(a-.55)/.24)*.13
   if glare:blended=cv2.addWeighted(blended,1-glare,np.full_like(blended,235),glare,0)
   proc.stdin.write(word_image(blended,s["name"],i+1,k==ntrans-1).tobytes());count+=1
  for k in range(round(HOLD*FPS)):
   proc.stdin.write(still.tobytes());count+=1
  scene_meta.append({"source_timecode_seconds":s["end"],"source_starts":round(start,3),
                     "why":s["why"],"source_shot_id":"AI13347", "ai_photo":path.name,"photo_sha256":sha(path),
                     "moving_frames":len(raw_moving),"morph_frames":ntrans,
                     "still_frames":round(HOLD*FPS),"true_frozen_photo":True})
  print("REAL_PHOTO_COMPLETED",i+1,s["name"],path.stat().st_size,"frames",count,flush=True)
 proc.stdin.close();error=proc.stderr.read()
 cap.release()
 if proc.wait()!=0:raise RuntimeError("FFmpeg encoding failed "+error.decode(errors="ignore")[-1200:])
 length=count/FPS;wav=OUT/"MUSICA_ORIGINALE.wav";audio(length,wav,beats)
 command(["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error",
          "-i",str(pre),"-i",str(wav),"-map","0:v","-map","1:a:0","-c:v","copy",
          "-c:a","aac","-b:a","128k","-shortest","-movflags","+faststart",str(VIDEO)],150)
 command(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(VIDEO),"-f","null","-"],150)
 # Cover is actual reconstructed photo, not a fabricated unrelated AI scene.
 cv2.imwrite(str(OUT/"COVER.jpg"),word_image(photos[0],"IL TEMPO SI FERMA",1,True),[cv2.IMWRITE_JPEG_QUALITY,94])
 info={"title":"Beirut 1919 | Il tempo si ferma","version":"V62",
       "status":"rendered_pending_visual_and_source_rights_review",
       "source":rights,"actual_source_sha256":sha(original),
       "description":"Archivio CC0 vero in B/N in movimento; la stessa scena diventa una fotografia AI restaurata che resta ferma.",
       "ai_color":ddmeta,"ai_restoration":esmeta,
       "disclosure":"Riprese reali del 1919. Colori e microdettagli delle fotografie sono ricostruzioni IA, non fatti storici accertati.",
       "music":"Composizione originale procedurale; senza registrazioni di terzi",
       "frame_geometry_preserved":True,
       "source_modified_by_image_generation":False,
       "timings":{"motion_s":MOTION,"color_reveal_s":REVEAL,"still_hold_s":HOLD,
                  "total_video_s":round(length,2)},
       "shots":scene_meta,
       "mp4_sha256":sha(VIDEO),"mp4_size":VIDEO.stat().st_size,
       "mp4_decode_test_passed":True,
       "vidu_used":False,
       "source_direct_publishing_not_monetized":True,
       "no_social_autopublish":True,
       "video_library_import_verified":False,
       "android_download_verified":False,
       "human_artistic_review_completed":False}
 (OUT/"FONTI_RICETTA_QA.json").write_text(json.dumps(info,ensure_ascii=False,indent=2)+"\n")
 social={
 "FACEBOOK":"Beirut, 1919. Per un istante la vecchia pellicola si ferma e il passato diventa una fotografia a colori. Questi gesti e queste persone furono filmati davvero: la fotografia è stata restaurata e colorizzata con intelligenza artificiale. Le tinte e i dettagli ricostruiti sono un'interpretazione, non una testimonianza cromatica certa. Archivio Musée Albert-Kahn, filmato CC0 su Wikimedia Commons. #Beirut #Storia #Archivio",
 "INSTAGRAM":"BEIRUT, 1919 🎞️ Dal movimento reale in bianco e nero a una fotografia a colori, immobile, come se il tempo si fermasse. ✨ I fotogrammi sono storici; colori e dettagli sono ricostruzioni IA. Fonte: Musée Albert-Kahn / Wikimedia Commons (CC0). #StoriaRivive #Beirut1919 #ArchiveFilm",
 "TIKTOK":"Hai mai visto il tempo fermarsi? 👀 Beirut 1919: il filmato in bianco e nero si blocca e si trasforma in una fotografia restaurata a colori. Riprese autentiche CC0, colori ricostruiti con IA. #history #beirut #restauro #storia",
 "YOUTUBE":"BEIRUT 1919 — IL TEMPO SI FERMA | Filmati autentici e fotografie AI a colori\n\nSei brevi movimenti ripresi a Beirut nel 1919 dal fondo del Musée Albert-Kahn. Ogni ripresa in bianco e nero si ferma sul suo fotogramma originale, poi diventa una fotografia restaurata: colore con DDColor e recupero dettagli con Real-ESRGAN. Colori e microdettagli sono interpretazioni digitali, non colori storicamente verificati. Filmato d'archivio CC0: https://commons.wikimedia.org/wiki/File:Sc%C3%A8nes_de_rue_-_AI13347.webm. Musica originale creata per questa clip."
 }
 for k,txt in social.items():(OUT/f"POST_{k}.txt").write_text(txt+"\n",encoding="utf8")
 (OUT/"README.txt").write_text(
    "La Storia Rivive V62. Video H264/AAC: archivio autentico in B/N in movimento, freeze su un frame reale, foto colorizzata con DDColor e restaurata con Real-ESRGAN, fotografia FERMA. Sei riprese NON simultanee. La foto riproduce la geometria originale e migliora i dettagli con AI; i colori non sono storicamente documentati. Pubblicazione social non monetizzata. Scaricabilita' Android e Video Library Studio da verificare.\n",encoding="utf8")
 pack=OUT/"BEIRUT_1919_FOTO_AI_V62_KIT.zip"
 with zipfile.ZipFile(pack,"w",compression=zipfile.ZIP_DEFLATED) as z:
  for p in [VIDEO,OUT/"COVER.jpg",OUT/"FONTI_RICETTA_QA.json",OUT/"README.txt",
            *[OUT/f"POST_{k}.txt" for k in social],*[OUT/f"FOTO_AI_{i+1:02d}.jpg" for i in range(len(SHOTS))]]:
   z.write(p,p.name)
 with zipfile.ZipFile(pack) as z:
  if z.testzip():raise ValueError("ZIP checksum fails")
 print("FINISHED",json.dumps({"video":VIDEO.name,"bytes":VIDEO.stat().st_size,
                            "duration":length,"sha":sha(VIDEO),"zip":pack.name},ensure_ascii=False),flush=True)

if __name__=="__main__":
 produce()
