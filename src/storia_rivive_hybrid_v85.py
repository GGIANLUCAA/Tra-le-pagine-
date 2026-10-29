#!/usr/bin/env python3
"""V85: free hybrid montage of four genuine classic BW->photo sequences followed
by the one verified V84 Vidu fully moving-color scene (marciapiede 1900).
NO Vidu API calls, no new paid credits, no public/site auto-publish.
This is a technical preview: classic source year 1918, final Vidu 1900.
"""
from pathlib import Path
import hashlib,json,math,subprocess,sys,wave,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import cv2
ROOT=Path("output/storia_hybrid_v85")
ROOT.mkdir(parents=True,exist_ok=True)
OLD=ROOT/"BASE_V83.mp4"
NEW=ROOT/"VIDU_V84_WALKWAY_COLOR_MOTION.mp4"
FINAL=ROOT/"LA_STORIA_RIVIVE_PARIS_V85_4PLUS1_FINALE_VIDU.mp4"
EXPECTED={
 "BASE_V83.mp4":"3cfc6c56450b4fdccc44444fd253bf03cb12c019115b68d2dd7b9308347300c6",
 "VIDU_V84_WALKWAY_COLOR_MOTION.mp4":"52a33e09d6ca2999c1fa612569447be2a479de6d15892b5d4e91690d6ed5ae45"}
# Order by source light/exposure: tram 64 -> newsstand 74 -> cinema 100 -> station 103 -> Vidu ~130.
# This avoids V83's high contrast Vidu 137 -> next source 74.
SCENES=[
 ("TRAM · PARIS 1918",17.833,21.733),
 ("NEWSSTAND · PARIS 1918",6.900,10.067), # skip 0.833s burned-in old title and preserve remaining real original moving B/W
 ("CINEMA · PARIS 1918",14.067,17.833),
 ("STATION · PARIS 1918",10.067,14.067)]
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def sh(args,timeout=200):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError("V85_FAILED "+" ".join(map(str,args[:5]))+" "+p.stderr[-1100:])
 return p.stdout
def frame(path,t):
 c=cv2.VideoCapture(str(path));c.set(cv2.CAP_PROP_POS_MSEC,float(t)*1000)
 ok,f=c.read();c.release()
 if not ok:raise RuntimeError("FRAME_MISSING "+str(path)+" at "+str(t))
 return cv2.resize(f,(180,320))
def metric(img):
 x=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
 return float(x.mean()),float(np.median(cv2.cvtColor(img,cv2.COLOR_BGR2HSV)[:,:,1]))
def make():
 for p in (OLD,NEW):
  if not p.is_file() or sha(p)!=EXPECTED[p.name]:raise RuntimeError("UNVERIFIED_SOURCE "+str(p))
 fmt=json.loads(sh(["ffprobe","-v","error","-show_entries","format=duration","-of","json",str(NEW)]))
 vdur=float(fmt["format"]["duration"])
 if not 4.8<vdur<5.2:raise RuntimeError("WRONG_VIDU_5SECOND_CLIP")
 # Only one scene is Vidu: the same known released clip. Other four are source-locked classical images.
 parts=[]
 for i,(title,a,b) in enumerate(SCENES):
  parts.append(f"[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS,fps=30,scale=720:1280,setsar=1,format=yuv420p[v{i}]")
 parts.append("[1:v]fps=30,scale=720:1280,setsar=1,hue=s=1.23,setpts=PTS-STARTPTS,format=yuv420p[v4]")
 parts.append("".join(f"[v{i}]" for i in range(5))+"concat=n=5:v=1:a=0,format=yuv420p[conc]")
 font="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
 parts.append("[conc]"+
  "drawbox=x=0:y=95:w=720:h=270:color=black@0.33:t=fill:enable='between(t,0,1.5)',"+
  f"drawtext=fontfile={font}:text='PARIS':fontsize=67:fontcolor=white:x=(w-text_w)/2:y=170:enable='between(t,0,1.5)',"+
  f"drawtext=fontfile={font}:text='1900-1918':fontsize=42:fontcolor=0xEAD1A4:x=(w-text_w)/2:y=267:enable='between(t,0,1.5)'[v]")
 silent=ROOT/"TEMP_V85_SILENT.mp4"
 cmd=["ffmpeg","-nostdin","-y","-v","error","-i",str(OLD),"-i",str(NEW),
      "-filter_complex",";".join(parts),"-map","[v]","-c:v","libx264","-preset","veryfast",
      "-crf","19","-pix_fmt","yuv420p","-movflags","+faststart",str(silent)]
 sh(cmd,220)
 probe=json.loads(sh(["ffprobe","-v","error","-show_entries","format=duration","-of","json",str(silent)]))
 duration=float(probe["format"]["duration"])
 if not 19.0<duration<22.0:raise RuntimeError("WRONG_FIVE_SCENE_LENGTH")
 # One original continuous licensed score, not five cut pieces and not five unrelated songs.
 sr=32000;t=np.arange(round(duration*sr),dtype="float32")/sr
 score=np.zeros_like(t)
 for i,f in enumerate([130.81,164.81,196.0,261.63]):
  score+=(.018-.0015*i)*np.sin(2*np.pi*f*t+i*.34)*(0.76+.24*np.sin(.5*t+i))
 boundaries=[0,3.9,7.1,10.9,14.9]
 for cue in boundaries:
  dt=t-cue;on=(dt>=0)&(dt<.72)
  score[on]+=.025*np.sin(2*np.pi*(95*dt[on]+63*dt[on]**2))*np.exp(-8*dt[on])
 score=np.tanh(score*2)*np.minimum(1,t/.6)*np.minimum(1,np.maximum(0,(duration-t)/.7))
 audio=ROOT/"ORIGINAL_SCORE_V85.wav"
 with wave.open(str(audio),"wb") as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr)
  w.writeframes((np.column_stack([score,np.roll(score,int(sr*.014))*.94])*18000).astype("<i2").tobytes())
 sh(["ffmpeg","-nostdin","-y","-v","error","-i",str(silent),"-i",str(audio),
     "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","160k",
     "-shortest","-movflags","+faststart",str(FINAL)],120)
 sh(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(FINAL),"-f","null","-"],140)
 offsets=[0]
 for _,a,b in SCENES:offsets.append(offsets[-1]+b-a)
 offsets.append(offsets[-1]+vdur)
 exposure=[]
 for i in range(1,5):
  st=offsets[i]
  prev=metric(frame(FINAL,max(0,st-.09)))
  nxt=metric(frame(FINAL,min(duration-.03,st+.09)))
  exposure.append({"between":i,"approx_time_s":round(st,3),"gray_mean_before":round(prev[0],2),
                   "gray_mean_after":round(nxt[0],2),"exposure_jump":round(abs(prev[0]-nxt[0]),2)})
 # Source provenance is period-mixed: don't call this a single historic continuous camera take.
 cover=ROOT/"COPERTINA.jpg"
 cv2.imwrite(str(cover),cv2.VideoCapture(str(FINAL)).read()[1])
 posts={
 "FACEBOOK":"PARIS · 1900–1918. Quattro veri frammenti di pellicola d'epoca diventano fotografie restaurate; nel finale il passato riprende a muoversi a colori. Riprese storiche reali, fotografie e movimento a colori sono ricostruzioni AI interpretative. Anteprima tecnica.",
 "INSTAGRAM":"PARIS · 1900–1918. Il passato si ferma quattro volte, poi torna a vivere. 🎞️ 4 restauri fotografici + 1 clip Vidu in movimento, con fonti storiche autentiche. #LaStoriaRivive",
 "TIKTOK":"Quattro fotografie dal passato. La quinta scena si anima davvero a colori. Parigi 1900–1918 · ricostruzione AI. #HistoryReels",
 "YOUTUBE":"PARIS 1900–1918 | La Storia Rivive — HYBRID V85\n\nAnteprima tecnica non definitiva. Quattro frammenti originali della Parigi del 1918 sono accompagnati da fotografie AI restaurate; l'ultima clip è una ricostruzione animata con Vidu tratta da un fotogramma della Parigi del 1900. Colori, volti e movimento AI sono interpretazioni, non documento originale a colori. Fonti: progetto V68 / V76 Wikimedia Commons, lavoro V84. Revisione artistica e diritti Italia in sospeso."}
 for k,v in posts.items():(ROOT/f"POST_{k}.txt").write_text(v+"\n",encoding="utf8")
 qa={"version":"V85","status":"TECHNICAL_PREVIEW_NEEDS_HUMAN_REVIEW",
     "duration_s":round(duration,3),"bytes":FINAL.stat().st_size,"video_sha256":sha(FINAL),
     "input_hashes":{p.name:sha(p) for p in (OLD,NEW)},
     "scene_order":[str(x[0]) for x in SCENES]+["VIDU MOVING WALKWAY · PARIS 1900"],
     "total_scenes":5,"classic_scenes":4,"vidu_scenes":1,"paid_vidu_requests_for_this_montage":0,
     "vidu_original_task":"1013449168682758144","vidu_was_reused_from_five_authorized_experiments":True,
     "first_second_transition":"per-frame grayscale to existing true Vidu colored frames, not optical flow, no still photo pans",
     "vidu_motion_last_four_seconds":True,
     "vidu_final_chroma_boost":"mild hue saturation multiplier 1.23; no additional AI generation",
     "cut_rhythm":"static originals with source photo freezes, Vidu as moving climax",
     "exposure_seams":exposure,
     "era_consistency":"MIXED 1900 and 1918 — demo only",
     "rights_italy":"PENDING","human_semantic_review":"PENDING","social_published":False,
     "website_published":False,"delivery":"github_release_preview_only"}
 (ROOT/"QA_V85.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n")
 zpath=ROOT/"PARIS_V85_4PLUS1_ANDROID.zip"
 with zipfile.ZipFile(zpath,"w",zipfile.ZIP_DEFLATED) as z:
  for p in [FINAL,cover,ROOT/"QA_V85.json",*[ROOT/f"POST_{k}.txt" for k in posts]]:
   z.write(p,p.name)
 with zipfile.ZipFile(zpath) as z:
  if z.testzip():raise RuntimeError("ZIP_CRC_FAILURE")
 print("V85_PREVIEW_REAL_MP4",FINAL,FINAL.stat().st_size,"duration",duration,"ZIP",zpath.stat().st_size,flush=True)
 print("V85_EXPOSURE_JUMPS",exposure,flush=True)
if __name__=="__main__":make()
