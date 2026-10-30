#!/usr/bin/env python3
"""V98 Bombay 1929: four TRUE modern image-to-image freeze restorations and one
source-anchored REAL Vidu moving-color scene. All five from verified distinct
original moving archive footage. 30fps, one original music score, short title.
Requires actual 5s Vidu video already created by single paid ledger.
"""
from pathlib import Path
import cv2,numpy as np,json,hashlib,wave,zipfile,math,subprocess
from PIL import Image,ImageDraw,ImageFont
R=Path("output/storia_bombay_v98"); R.mkdir(parents=True,exist_ok=True)
MASTER=R/"BOMBAY_1929_LA_STORIA_RIVIVE_V92.mp4"
VIDU=R/"VIDU_BOMBAY_1929_08_BW_COLOR_MOVING.mp4"
FIN=R/"BOMBAY_1929_V98_4PHOTO_1VIDU.mp4"
ORIG_SHA="3520595c7eb2d9be30d0fc33292726f0ab277d276b838f4d1d213a83c74a3890"
FPS=30;SIZE=(720,1280)
SCENES=[
 (2,"A CITY AWAKENS",1.13,.33,1.95),
 (7,"THE MARKET",.83,.27,2.10),
 (4,"A DAY'S WORK",.96,.30,1.90),
 (5,"THE STREETS",1.08,.31,1.95),
 (8,"A MOMENT IN TIME",1.08,0,5.0)]
MASTER_TIMINGS={1: (.72,.27,1.88),2:(1.12,.38,1.79),3:(.92,.34,1.94),
                4:(.94,.32,1.68),5:(1.10,.41,1.93),6:(1.17,.36,1.90),
                7:(.84,.31,2.12),8:(1.08,.48,2.35)}
def sha(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for q in iter(lambda:f.read(1<<20),b""):h.update(q)
 return h.hexdigest()
def sh(cmd,timeout=170):
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError("VIDEO_COMMAND_FAIL "+str(cmd[:6])+" "+p.stderr[-850:])
 return p.stdout
def video_frame(cap,idx):
 cap.set(cv2.CAP_PROP_POS_FRAMES,int(idx))
 ok,f=cap.read()
 if not ok:raise RuntimeError("SOURCE_VIDEO_MISSING_FRAME "+str(idx))
 if f.shape[:2]!=(1280,720):raise RuntimeError("UNEXPECTED_FRAME_GEOMETRY")
 return f
def similarity(a,b):
 def f(x):
  y=cv2.resize(cv2.cvtColor(x,cv2.COLOR_BGR2GRAY),(90,160))
  return cv2.GaussianBlur(y,(9,9),0).astype("float32").ravel()
 return float(np.corrcoef(f(a),f(b))[0,1])
def read_data():
 if not MASTER.is_file() or sha(MASTER)!=ORIG_SHA:raise RuntimeError("V92_MOVIE_SOURCE_HASH_MISMATCH")
 if not VIDU.is_file():raise RuntimeError("REAL_VIDU_MOTION_MP4_MISSING")
 q=json.loads((R/"V95_FREE_SOURCE_QA.json").read_text())
 p=json.loads((R/"V98_FIVE_REAL_PHOTOS_QA.json").read_text())
 v=json.loads((R/"V98_VIDU_QA_PRIVATE.json").read_text())
 if v.get("provider_state")!="success" or v.get("paid_post_count")!=1 or not v.get("task_id"):
  raise RuntimeError("NO_ACTUAL_SINGLE_PAID_VIDU_TASK")
 if not v["motion_QA"]["moving_color_after_1s"] or not v["motion_QA"]["color_after_1s"]:
  raise RuntimeError("VIDU_REAL_COLOR_MOTION_FAILED")
 if sha(VIDU)!=v["processed_color_video_sha256"]:raise RuntimeError("NEW_VIDU_VIDEO_SHA_CHANGED")
 m={s["scene"]:s for s in q["selected_scenes"]}
 phot={s["scene"]:s for s in p["photographic_images"]}
 for k,*_ in SCENES:
  if k not in m or k not in phot:raise RuntimeError("SELECTED_1929_FRAME_MISSING")
  orig=R/f"SOURCE_BW_{k:02d}.png";col=R/f"RESTORATION_FINAL_{k:02d}.jpg"
  if not orig.is_file() or not col.is_file() or sha(orig)!=m[k]["original_BW_frame_sha256"] or sha(col)!=phot[k]["new_i2i_photo_sha256"]:
   raise RuntimeError("IMAGE_NOT_THE_TRUE_1929_SOURCE_FRAME_"+str(k))
 return m,phot,v
def music(sec,scene_starts):
 sr=32000;t=np.arange(round(sec*sr),dtype=np.float32)/sr
 audio=np.zeros_like(t)
 # Original unobtrusive cinematic harmonic underscore, no copyrighted samples.
 chords=[[130.81,196.00,261.63],[146.83,220.00,293.66],[123.47,164.81,246.94],[130.81,174.61,261.63],[146.83,196.00,293.66]]
 for i,start in enumerate(scene_starts):
  stop=scene_starts[i+1] if i+1<len(scene_starts) else sec
  b=(t>=start)&(t<stop);z=t[b]-start
  for j,f in enumerate(chords[i]):
   amp=(.020-.003*j)
   audio[b]+=amp*np.sin(2*np.pi*f*z+j*.3)*(0.85+.15*np.cos(z*.35))
   audio[b]+=.002*np.sin(2*np.pi*(f*2.003)*z+j*.5)
 for mark in scene_starts:
  d=t-mark;k=(d>=0)&(d<.62)
  audio[k]+=.028*np.sin(2*np.pi*(85*d[k]+55*d[k]**2))*np.exp(-11*d[k])
 audio=np.tanh(audio*2.2)
 env=np.minimum(1,t/.6)*np.minimum(1,np.maximum(0,(sec-t)/1.0))
 audio*=env
 path=R/"MUSICA_ORIGINALE_V98.wav"
 with wave.open(str(path),"wb") as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr)
  w.writeframes((np.column_stack([audio,np.roll(audio,int(sr*.012))*.94])*18000).astype("<i2").tobytes())
 return path
def render():
 metas,photos,task=read_data()
 cap=cv2.VideoCapture(str(MASTER));vid=cv2.VideoCapture(str(VIDU))
 vfps=float(vid.get(cv2.CAP_PROP_FPS));vn=int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
 if not 20<=vfps<=60 or not 4.7<=vn/vfps<=5.3:raise RuntimeError("NOT_THE_USER_REQUESTED_ACTUAL_5S_VIDU")
 orig_start={};offset=0
 for k in range(1,9):
  orig_start[k]=offset
  offset+=sum(round(x*24) for x in MASTER_TIMINGS[k])
 # Validate every film shot's exact freeze frame against the original restoration base.
 for k,*_ in SCENES:
  bw=video_frame(cap,orig_start[k]+round(MASTER_TIMINGS[k][0]*24)-1)
  ref=cv2.imread(str(R/f"SOURCE_BW_{k:02d}.png"))
  if similarity(bw,ref)<.985:raise RuntimeError(f"VIDEO_ORIGINAL_FRAME_NOT_THE_SAME_SOURCE_{k}")
 cap.release();cap=cv2.VideoCapture(str(MASTER))
 lengths=[];chapters=[]
 for k,name,bw,fade,hold in SCENES:
  nm=round(MASTER_TIMINGS[k][0]*24)
  # Exact original motion duration. 4 restorations each <2.1s fixed.
  actual_bw=nm/24
  fadem=max(0,round(fade*FPS))
  holdm=max(0,round(hold*FPS))
  length=round(actual_bw*FPS)+(fadem+holdm if k!=8 else round(5.0*FPS))
  lengths.append(length)
 scene_starts=[0]
 for n in lengths[:-1]:scene_starts.append(scene_starts[-1]+n/FPS)
 nframes=sum(lengths);seconds=nframes/FPS
 if not 17<=seconds<=26:raise RuntimeError("DURATION_NOT_SUITED_TO_STORY")
 silent=R/"SILENT_MASTER_V98.mp4"
 enc=subprocess.Popen(["ffmpeg","-nostdin","-y","-v","error","-f","rawvideo","-pix_fmt","bgr24",
  "-s","720x1280","-r",str(FPS),"-i","-","-an","-c:v","libx264",
  "-crf","18","-preset","veryfast","-pix_fmt","yuv420p","-movflags","+faststart",str(silent)],
  stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 palette_samples=[];shot_time=0
 try:
  for index,(k,name,bw,fade,hold) in enumerate(SCENES):
   nm=round(MASTER_TIMINGS[k][0]*24)
   bw_out=round(nm/24*FPS)
   end_frame=None
   photo=cv2.imread(str(R/f"RESTORATION_FINAL_{k:02d}.jpg"))
   for fidx in range(bw_out):
    native=min(nm-1,int(fidx*24/FPS))
    frame=video_frame(cap,orig_start[k]+native)
    end_frame=frame.copy()
    if index==0 and fidx<round(1.15*FPS):
     # Gold typography without an opaque banner, never covering faces/objects.
     cv2.putText(frame,"BOMBAY  ·  1929",(40,82),cv2.FONT_HERSHEY_SIMPLEX,.81,(5,7,12),4,cv2.LINE_AA)
     cv2.putText(frame,"BOMBAY  ·  1929",(40,82),cv2.FONT_HERSHEY_SIMPLEX,.81,(231,224,204),2,cv2.LINE_AA)
    enc.stdin.write(frame.tobytes())
   if k!=8:
    fadeframes=round(fade*FPS)
    for t in range(fadeframes):
     alpha=(t+1)/max(1,fadeframes);alpha=alpha*alpha*(3-2*alpha)
     out=cv2.addWeighted(end_frame,1-alpha,photo,alpha,0)
     enc.stdin.write(out.tobytes())
    for t in range(round(hold*FPS)):
     enc.stdin.write(photo.tobytes())
    stat=float(np.median(cv2.cvtColor(photo,cv2.COLOR_BGR2HSV)[:,:,1]))
    palette_samples.append({"scene":k,"image_median_saturation":round(stat,2)})
    duration=(bw_out+fadeframes+round(hold*FPS))/FPS
   else:
    if similarity(end_frame,cv2.imread(str(R/"SOURCE_BW_08.png")))<.985:raise RuntimeError("VIDU_ORIGINAL_BW_NOT_ANCHORED")
    for t in range(round(5*FPS)):
     idx=min(vn-1,round(t*vfps/FPS))
     vid.set(cv2.CAP_PROP_POS_FRAMES,idx)
     ok,f=vid.read()
     if not ok:raise RuntimeError("NEW_VIDU_REAL_MOTION_SOURCE_TRUNCATED")
     enc.stdin.write(f.tobytes())
    duration=(bw_out+round(5*FPS))/FPS
   chapters.append({"scene":k,"name":name,"start_s":round(shot_time,3),
       "duration_s":round(duration,3),"archival_bw_motion_s":round(bw_out/FPS,3),
       "real_photo_hold_s":round(hold,3) if k!=8 else 0,
       "effect":"authentic moving B/W freeze to photo" if k!=8 else "one real Vidu full-motion B/W to color 5s",
       "image_sha256":sha(R/f"RESTORATION_FINAL_{k:02d}.jpg"),
       "source_exact_bw_frame_sha256":sha(R/f"SOURCE_BW_{k:02d}.png")})
   shot_time+=duration
 finally:
  cap.release();vid.release();enc.stdin.close()
  error=enc.stderr.read().decode(errors="replace")
  if enc.wait()!=0:raise RuntimeError("VIDEO_ENCODER_FAILED "+error[-700:])
 sound=music(seconds,scene_starts)
 sh(["ffmpeg","-nostdin","-y","-v","error","-i",str(silent),"-i",str(sound),
   "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","160k",
   "-shortest","-movflags","+faststart",str(FIN)],120)
 sh(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(FIN),"-f","null","-"],160)
 probe=json.loads(sh(["ffprobe","-v","error","-show_entries","format=duration,size:stream=codec_name,width,height",
   "-of","json",str(FIN)]))
 true_duration=float(probe["format"]["duration"])
 if abs(true_duration-seconds)>.15:raise RuntimeError("VIDEO_TIMELINE_WRONG")
 if not {"h264","aac"}.issubset({s.get("codec_name") for s in probe["streams"]}):
  raise RuntimeError("VIDEO_AUDIO_TRACK_MISSING")
 # Authentic source/photo/movie chapter contact sheet and actual final video frames
 cap=cv2.VideoCapture(str(FIN))
 contact=Image.new("RGB",(5*230,2*440),(13,17,22));draw=ImageDraw.Draw(contact)
 for i,c in enumerate(chapters):
  t_bw=c["start_s"]+min(.5,c["archival_bw_motion_s"]*.65)
  t_col=c["start_s"]+c["archival_bw_motion_s"]+(min(.7,c["real_photo_hold_s"]*.4) if i<4 else 2.0)
  for row,when in enumerate([t_bw,t_col]):
   cap.set(cv2.CAP_PROP_POS_MSEC,when*1000);ok,f=cap.read()
   if not ok:raise RuntimeError("FINAL_VIDEO_CONTACT_FRAME_MISSING")
   im=Image.fromarray(cv2.cvtColor(f,cv2.COLOR_BGR2RGB)).resize((224,400))
   contact.paste(im,(i*230+3,row*440+29))
   draw.text((i*230+4,row*440+6),f"{c['scene']} {c['name'][:19]}"+(" B/W" if row==0 else " COLOR"),fill="white")
 cap.release()
 contact.save(R/"V98_FIVE_SOURCE_TO_RESTORATION_PAIRS.jpg",quality=92)
 image=Image.open(R/"RESTORATION_FINAL_08.jpg").convert("RGB")
 title=ImageDraw.Draw(image)
 try:font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",43)
 except:font=ImageFont.load_default()
 title.text((38,74),"BOMBAY · 1929",font=font,fill=(10,13,20),stroke_width=2,stroke_fill=(4,6,9))
 title.text((38,73),"BOMBAY · 1929",font=font,fill=(243,227,189))
 image.save(R/"COVER_V98.jpg",quality=94)
 texts={
 "FACEBOOK":"BOMBAY · 1929. Tra mercati, lavoratori e sorrisi, la città torna a vivere. Quattro veri frammenti storici si fermano in fotografie ricostruite con IA; un quinto momento prosegue a colori in un video animato con Vidu. I colori e i dettagli sono ricostruzioni interpretative, non originali.",
 "INSTAGRAM":"BOMBAY · 1929 🎞️ Una città. Cinque momenti autentici. Quattro fotografie restaurate e cinque secondi di movimento ricostruito a colori. Filmato originale del 1929, restauro AI interpretativo. #LaStoriaRivive #HistoryReels",
 "TIKTOK":"Bombay nel 1929: dalle persone reali in bianco e nero a fotografie moderne… poi uno sguardo si anima davvero per cinque secondi. Ricostruzione AI, non pellicola originale a colori.",
 "YOUTUBE":"BOMBAY · 1929 | THE CITY COMES ALIVE — La Storia Rivive V98\n\nCinque momenti distinti dalla pellicola storica Street Scenes in Bombay (January 1929). Quattro frammenti autentici B/N diventano fotografie ricostruite con modelli image-to-image. Una quinta ripresa originale prosegue in un video AI a colori di 5 secondi realizzato con Vidu. Le immagini, i colori, i volti e il movimento AI sono interpretazioni moderne, non riprese originarie a colori. Le riprese storiche sono archivio pubblico Wikimedia Commons: https://commons.wikimedia.org/wiki/File:Street_Scenes_in_Bombay,_India_(real_sound),_Jan_1929.webm"}
 for k,v in texts.items(): (R/f"POST_{k}.txt").write_text(v+"\n")
 report={"version":"V98","status":"RENDERED_ARTISTIC_REVIEW_PENDING",
  "source":"Street Scenes in Bombay, January 1929, Wikimedia Commons","source_historical_epoch":1929,
  "five_different_actual_archival_shots":True,"classic_real_I2I_photographs":4,
  "vidu_genuine_generated_motion_shots":1,"new_paid_vidu_tasks":1,
  "vidu_provider_task_id":task["task_id"],"vidu_paid_credits":task["credits_paid"],
  "frame_to_frame_5th_source_corr":task["motion_QA"]["first_frame_corr_with_exact_original_bw"],
  "vidu_after_color_real_motion":task["motion_QA"]["moving_color_after_1s"],
  "one_music_score_across_all_scenes":True,"large_opaque_title_band":False,
  "duration_s":round(true_duration,3),"fps":FPS,"resolution":[720,1280],
  "source_shot_timeline":chapters,"shot_color_palette_samples":palette_samples,
  "full_MP4_decoding_passed":True,"real_animation_source_video_sha256":task["original_generated_MP4_sha256"],
  "final_mp4_sha256":sha(FIN),"source_rights_italy":"PENDING",
  "human_facial_and_artistic_QA":"PENDING","published_social":False,"published_site":False}
 (R/"V98_QA_PUBLIC.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 kit=R/"BOMBAY_1929_V98_ANDROID.zip"
 with zipfile.ZipFile(kit,"w",zipfile.ZIP_DEFLATED) as z:
  for f in [FIN,R/"COVER_V98.jpg",R/"V98_QA_PUBLIC.json",R/"V98_FIVE_SOURCE_TO_RESTORATION_PAIRS.jpg",*[R/f"POST_{x}.txt" for x in texts]]:
   z.write(f,f.name)
 with zipfile.ZipFile(kit) as z:
  if z.testzip():raise RuntimeError("ANDROID_ZIP_CORRUPTED")
 print("V98_REAL_FIVE_SCENE_MP4_COMPLETE",FIN.name,"bytes",FIN.stat().st_size,"duration",true_duration,
   "new_Vidu_credits",task["credits_paid"],"ZIP",kit.stat().st_size,flush=True)
if __name__=="__main__":render()
