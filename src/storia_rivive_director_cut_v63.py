#!/usr/bin/env python3
"""V63: Director-selected CC0 moving footage -> photographic color restoration (DDColor + RealESRGAN).
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

OUT=Path("output/storia_rivive_v63_director_cut")
OUT.mkdir(parents=True,exist_ok=True)
VIDEO=OUT/"LA_STORIA_RIVIVE_BEIRUT_1919_REGIA_V63.mp4"
W,H,FPS=1080,1920,30
MOTION=1.45;REVEAL=.34;HOLD=2.3
# V63 deliberately hand-reviewed against 62 distinct source frames + 6x5 vertical crops.
# Score emphasizes an expressive subject, meaningful action and readable crop; NOT even shot counts.
SHOTS=[
 {"id":"01","name":"La carovana","end":146.5,"x":195,"motion_s":1.40,"reveal_s":.35,"hold_s":2.50,"subject":"camel_and_rider","priority":5,"why":"Hook: cammello e cavaliere occupano il fotogramma; il movimento avvicina il soggetto"},
 {"id":"02","name":"I volti","end":162.5,"x":190,"motion_s":1.55,"reveal_s":.36,"hold_s":2.75,"subject":"family_and_child","priority":5,"why":"Uomini, bambino e cane chiaramente presenti; il tempo si ferma sul gruppo"},
 {"id":"03","name":"Il mercato","end":128.95,"x":105,"motion_s":1.35,"reveal_s":.35,"hold_s":2.20,"subject":"fruit_sellers","priority":4,"why":"Focalizzare il banco con la frutta e la folla, non il panorama"},
 {"id":"04","name":"Il caffè","end":183.5,"x":290,"motion_s":1.45,"reveal_s":.32,"hold_s":2.35,"subject":"cafe_men","priority":5,"why":"Il gruppo di uomini si raduna, fermo sulla conversazione"},
 {"id":"05","name":"Il porto","end":72.5,"x":95,"motion_s":1.25,"reveal_s":.33,"hold_s":1.82,"subject":"dock_workers","priority":3,"why":"Pausa spaziale dopo quattro ritratti: uomini in primo piano con navi"},
 {"id":"06","name":"La piazza","end":103.0,"x":258,"motion_s":1.48,"reveal_s":.35,"hold_s":2.35,"subject":"town_crowd","priority":4,"why":"Finale corale con gruppi e gesti leggibili, prima che il tempo si spenga"}
]
assert len({s["subject"] for s in SHOTS})==len(SHOTS)
assert len({s["end"] for s in SHOTS})==len(SHOTS)

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
 # This ONNX release exposes a FIXED input of 1x3x64x64: tile exactly 64px.
 # Core 48px + 8px context each side; reflection-pad the final edge tiles.
 core,pad=48,8
 framed=cv2.copyMakeBorder(rgb,pad,pad,pad,pad,cv2.BORDER_REFLECT_101)
 result=np.zeros((h*4,w*4,3),dtype=np.uint8)
 input_name=session.get_inputs()[0].name
 shape=session.get_inputs()[0].shape
 if list(shape[2:])!=[64,64]:
  raise ValueError("Unexpected RealESRGAN fixed input shape: "+str(shape))
 for y in range(0,h,core):
  for x in range(0,w,core):
   ch=min(core,h-y);cw=min(core,w-x)
   tile=framed[y:y+core+2*pad,x:x+core+2*pad]
   if tile.shape[0] < 64 or tile.shape[1] < 64:
    tile=cv2.copyMakeBorder(tile,0,64-tile.shape[0],0,64-tile.shape[1],cv2.BORDER_REFLECT_101)
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

def archival_clean(frame):
 # Clean film grain conservatively: better AI detail and less noise amplification.
 gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
 den=cv2.fastNlMeansDenoising(gray,None,h=3.1,templateWindowSize=7,searchWindowSize=17)
 return cv2.cvtColor(den,cv2.COLOR_GRAY2BGR)

def historical_frame(frame,x):
 bw=cv2.cvtColor(archival_clean(frame),cv2.COLOR_BGR2GRAY)
 image=crop9(cv2.cvtColor(bw,cv2.COLOR_GRAY2BGR),x)
 image=cv2.resize(image,(W,H),interpolation=cv2.INTER_CUBIC)
 return image

def color_photo(frame,x,ddcolor,esrgan):
 # IMPORTANT V63: V62 DOWNSCALED the only original 324x576 crop to 240x427
 # before AI. Never throw away original information before neural restoration.
 clean=archival_clean(frame)
 ab=v60.infer_ab(ddcolor,clean)
 colored=v60.image_at(clean,ab)
 crop=crop9(colored,x)  # original 324x576 real pixels, never fake 4K scan
 assert crop.shape[0]>=560 and crop.shape[1]>=310
 learned=esrgan_4x(esrgan,crop) # reconstructed 1296x2304, actual ONNX inference
 restored=cv2.resize(learned,(W,H),interpolation=cv2.INTER_AREA)
 # Blend only a little conservative original to suppress GAN grain and edge halos.
 baseline=cv2.resize(crop,(W,H),interpolation=cv2.INTER_CUBIC)
 restored=cv2.addWeighted(restored,.88,baseline,.12,0)
 lab=cv2.cvtColor(restored,cv2.COLOR_BGR2LAB)
 L,A,B=cv2.split(lab)
 L=cv2.createCLAHE(clipLimit=1.12,tileGridSize=(8,8)).apply(L)
 restored=cv2.cvtColor(cv2.merge((L,A,B)),cv2.COLOR_LAB2BGR)
 # No detailEnhance(), which accentuates 1919 grain into ugly artificial texture.
 return restored

def word_image(frame,caption,number,photo=False):
 if number>1:
  # Preserve the 4K-like photorealistic image rather than stacking repeated black boxes.
  return frame
 img=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
 d=ImageDraw.Draw(img,"RGBA")
 try:
  big=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",48)
  small=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",28)
 except OSError:
  big=ImageFont.load_default();small=ImageFont.load_default()
 d.rounded_rectangle((40,45,490,166),radius=12,fill=(9,9,12,100))
 d.text((62,57),"BEIRUT  ·  1919",font=big,fill=(255,248,237,248))
 d.text((64,115),"LA STORIA RIVIVE",font=small,fill=(233,222,207,242))
 return cv2.cvtColor(np.asarray(img.convert("RGB")),cv2.COLOR_RGB2BGR)

def audio(total,path,beats,reveal_times):
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
  for at in [reveal_times[i],reveal_times[i]+REVEAL]:
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
 pre=OUT/"V63_VIDEO_SENZA_AUDIO.mp4"
 proc=subprocess.Popen(["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error",
                        "-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),
                        "-i","-","-c:v","libx264","-preset","veryfast","-crf","18",
                        "-pix_fmt","yuv420p",str(pre)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 if not proc.stdin:raise RuntimeError("No video encoder stdin")
 count=0;scene_meta=[];beats=[];reveal_times=[]
 photos=[]
 for i,s in enumerate(SHOTS):
  scene_motion=s["motion_s"];scene_reveal=s["reveal_s"];scene_hold=s["hold_s"]
  start=max(0,s["end"]-scene_motion);beats.append(count/FPS)
  reveal_times.append(count/FPS+scene_motion)
  end_frame=extract_frame(cap,s["end"])
  # ONE accurate original frame for each new AI-restored photograph.
  photo=color_photo(end_frame,s["x"],ddcolor,esrgan)
  path=OUT/(f"FOTO_AI_{i+1:02d}.jpg")
  cv2.imwrite(str(path),photo,[cv2.IMWRITE_JPEG_QUALITY,93])
  photos.append(photo)
  still=word_image(photo,s["name"],i+1,True)
  raw_moving=[]
  for k in range(round(scene_motion*FPS)):
   frame=extract_frame(cap,start+k/FPS)
   moving=historical_frame(frame,s["x"])
   raw_moving.append(moving)
  # last moving image is frozen exactly (approximately within one source-frame).
  freeze=historical_frame(end_frame,s["x"])
  for fi,m in enumerate(raw_moving):
   im=word_image(m,s["name"],i+1,False)
   proc.stdin.write(im.tobytes());count+=1
  ntrans=round(scene_reveal*FPS)
  for k in range(ntrans):
   a=(k+1)/ntrans
   smooth=a*a*(3-2*a)
   blended=cv2.addWeighted(freeze,1-smooth,photo,smooth,0)
   # short white shimmer at halfway, without hiding frame continuity
   glare=max(0,1-abs(a-.55)/.24)*.13
   if glare:blended=cv2.addWeighted(blended,1-glare,np.full_like(blended,235),glare,0)
   proc.stdin.write(word_image(blended,s["name"],i+1,k==ntrans-1).tobytes());count+=1
  for k in range(round(scene_hold*FPS)):
   proc.stdin.write(still.tobytes());count+=1
  scene_meta.append({"source_timecode_seconds":s["end"],"source_starts":round(start,3),
                     "why":s["why"],"source_shot_id":"AI13347", "ai_photo":path.name,"photo_sha256":sha(path),
                     "moving_frames":len(raw_moving),"morph_frames":ntrans,
                     "still_frames":round(scene_hold*FPS),"true_frozen_photo":True,
                     "director_priority":s["priority"],"director_subject":s["subject"],
                     "crop_x_original_px":s["x"],"restoration_input_px":[324,576],
                     "ai_restoration_scale":4,"native_4k":False})
  print("REAL_PHOTO_COMPLETED",i+1,s["name"],path.stat().st_size,"frames",count,flush=True)
 proc.stdin.close();error=proc.stderr.read()
 cap.release()
 if proc.wait()!=0:raise RuntimeError("FFmpeg encoding failed "+error.decode(errors="ignore")[-1200:])
 length=count/FPS;wav=OUT/"MUSICA_ORIGINALE.wav";audio(length,wav,beats,reveal_times)
 command(["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error",
          "-i",str(pre),"-i",str(wav),"-map","0:v","-map","1:a:0","-c:v","copy",
          "-c:a","aac","-b:a","128k","-shortest","-movflags","+faststart",str(VIDEO)],150)
 command(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(VIDEO),"-f","null","-"],150)
 # Cover is actual reconstructed photo, not a fabricated unrelated AI scene.
 cv2.imwrite(str(OUT/"COVER.jpg"),word_image(photos[0],"IL TEMPO SI FERMA",1,True),[cv2.IMWRITE_JPEG_QUALITY,94])
 info={"title":"Beirut 1919 | I volti del tempo","version":"V63",
       "status":"rendered_pending_human_artistic_and_rights_review",
       "source":rights,"actual_source_sha256":sha(original),
       "description":"Archivio CC0 vero in B/N in movimento; la stessa scena diventa una fotografia AI restaurata che resta ferma.",
       "ai_color":ddmeta,"ai_restoration":esmeta,
       "disclosure":"Riprese reali del 1919. Colori e microdettagli delle fotografie sono ricostruzioni IA, non fatti storici accertati.",
       "music":"Composizione originale procedurale; senza registrazioni di terzi",
       "frame_geometry_preserved":True,
       "source_modified_by_image_generation":False,
       "timings":{"per_scene":True,"range_motion_s":[1.25,1.55],
                  "range_hold_s":[1.82,2.75],"total_video_s":round(length,2)},
       "actual_delivery_resolution":[W,H],"source_native_resolution":[720,576],
       "true_4k":False,"scene_selection":"manually reviewed whole 188 second movie and 6 multi-crop sheets",
       "target":"4k-like perceived detail, never claiming original 4k data",
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
    "La Storia Rivive V63. 1080x1920 H264/AAC, 6 tagli selezionati editorialmente da 188s di archivio autentico CC0. Riprese originali B/N in movimento, freeze, fotografia AI colorizzata con DDColor + Real-ESRGAN sui pixel ORIGINALI di crop 324x576 senza riduzione preliminare, hold adattato all'importanza del soggetto. Non è una ripresa 4K né garantisce il realismo di diffusion image-to-image. Nessuna pubblicazione social automatica.\n",encoding="utf8")
 pack=OUT/"BEIRUT_1919_REGIA_V63_KIT.zip"
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
