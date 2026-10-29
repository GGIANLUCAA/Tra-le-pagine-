#!/usr/bin/env python3
"""La Storia Rivive V86 — San Francisco, 14 April 1906
Four different authentic 1906 moving film -> restored photographic color stills
plus ONE fifth, different REAL film shot at 43s, reanimated by Vidu as a 5s
full-motion color insert after the original B/W film's last sub-second.
One soundtrack, source SHA verification, android direct-download pack.
No billable Vidu actions in this script. Not automatic social publication.
"""
from __future__ import annotations
import hashlib,json,math,subprocess,wave,zipfile
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path("output/storia_v86_sf1906");R.mkdir(parents=True,exist_ok=True)
ORIGINAL=Path("output/storia_v70_sf1906/SAN_FRANCISCO_1906_HD_ORIGINALE.webm")
MASTER=R/"SAN_FRANCISCO_1906_WOW_FOTO_GENERATIVE_V70.mp4"
VIDU=R/"VIDU_SF1906_05_COLOR_MOTION.mp4"
FINAL=R/"SAN_FRANCISCO_1906_V86_4FOTO_1VIDU.mp4"
V70_SHA="eaa9c566451690b85f67756420852b8e49d9350b0794618adaf110ff5a2e477d"
ORIGINAL_SHA="c8b30802c0fbeb5f9ec3dc9af3e4f71ef627a863d4abba5550b63998cb46725a"
FPS=30
# Source V70 documented shot order, each unique original film time and exact AI photo.
# Frame sums (moving + reveal + fixed AI photography):
# pedestrian 52+11+108=171; motorcar 48+10+98=156; cyclist 50+10+99=159; ferry 48+10+104=162.
# Use around two seconds of hold rather than letting static photos dominate.
# Never use Vidu for any of these four, and do not regenerate any existing image.
SHOTS=[
 dict(title="CYCLIST",source_offset=327,start=327,end=327+50+10+58,source_time=128,original_photo="FOTO_FOTOGRAFICA_AI_03.png"),
 dict(title="EARLY MOTORCAR",source_offset=171,start=171,end=171+48+10+58,source_time=164,original_photo="FOTO_FOTOGRAFICA_AI_02.png"),
 dict(title="PEDESTRIANS",source_offset=0,start=26,end=52+11+60,source_time=236,original_photo="FOTO_FOTOGRAFICA_AI_01.png"),
 dict(title="FERRY BUILDING",source_offset=486,start=486,end=486+48+10+60,source_time=476,original_photo="FOTO_FOTOGRAFICA_AI_04.png")
]
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def run(argv,limit=230):
 p=subprocess.run(argv,capture_output=True,text=True,timeout=limit)
 if p.returncode:raise RuntimeError("COMMAND_FAILED "+" ".join(map(str,argv[:5]))+" "+p.stderr[-1500:])
 return p.stdout
def check():
 if not MASTER.is_file() or sha(MASTER)!=V70_SHA:raise RuntimeError("V70_ORIGINAL_FOUR_RESTORED_SCENES_NOT_VERIFIED")
 if not ORIGINAL.is_file() or sha(ORIGINAL)!=ORIGINAL_SHA:raise RuntimeError("1906_TRUE_MOVING_FILM_NOT_VERIFIED")
 if not VIDU.is_file() or VIDU.stat().st_size<100000:raise RuntimeError("MISSING_NEW_REAL_VIDU_VIDEO")
 p=json.loads((R/"FIFTH_SCENE_RESTORATION_QA.json").read_text())
 q=json.loads((R/"SF1906_VIDU_SINGLE_TASK_QA_PRIVATE.json").read_text())
 if p.get("photo_quality_gate_passed") is not True:raise RuntimeError("FIFTH_PHOTO_PREVIEW_NOT_SOURCE_LOCKED")
 if q.get("provider_state")!="success" or q.get("paid_post_count")!=1 or not q.get("task_id"):
  raise RuntimeError("VIDU_TASK_NOT_REAL_SUCCESS")
 if q.get("color_transition_per_frame")!=True:raise RuntimeError("VIDU_WRONG_MOVING_COLOR_METHOD")
 for n in range(1,5):
  pic=R/f"FOTO_FOTOGRAFICA_AI_{n:02d}.png"
  if not pic.is_file() or pic.stat().st_size<80000:raise RuntimeError("CLASSIC_PHOTO_MISSING "+str(pic))
 r=json.loads(run(["ffprobe","-v","error","-show_entries","format=duration:stream=width,height,codec_name","-of","json",str(VIDU)]))
 dur=float(r["format"]["duration"])
 if not 4.7<dur<5.6:raise RuntimeError("VIDU_DURATION_WRONG")
 return p,q,dur
def create_video(duration_vidu):
 # Video's only paid generation is [2:v] (5s), never more.
 parts=[]
 for i,x in enumerate(SHOTS):
  parts.append(f"[0:v]trim=start_frame={x['start']}:end_frame={x['end']},setpts=PTS-STARTPTS,scale=720:1280:flags=lanczos,setsar=1,fps=30,format=yuv420p[s{i}]")
 # Native 1906 film frame at t43 is the EXACT source for the fifth Vidu colorized anchor;
 # keep the real B/W moving original for ~.86 second and cut into Vidu at same pose.
 parts.append("[1:v]trim=start=42.14:end=43.0,setpts=PTS-STARTPTS,crop=603:1072:600:0,scale=720:1280:flags=lanczos,fps=30,setsar=1,hue=s=0,format=yuv420p[orig5]")
 parts.append("[2:v]trim=duration=5.0,setpts=PTS-STARTPTS,scale=720:1280:flags=lanczos,fps=30,setsar=1,format=yuv420p[vid5]")
 parts.append("".join("[s"+str(i)+"]" for i in range(4))+"[orig5][vid5]concat=n=6:v=1:a=0,format=yuv420p[all]")
 serif="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
 parts.append("[all]drawbox=x=0:y=65:w=720:h=200:color=black@0.28:t=fill:enable='between(t,0,1.6)',"+
              f"drawtext=fontfile={serif}:text='SAN FRANCISCO':fontsize=44:fontcolor=white:x=(w-text_w)/2:y=103:enable='between(t,0,1.6)',"+
              f"drawtext=fontfile={serif}:text='1906':fontsize=48:fontcolor=0xEAD3A2:x=(w-text_w)/2:y=173:enable='between(t,0,1.6)'[v]")
 silent=R/"V86_VIDEO_TRACK.mp4"
 cmd=["ffmpeg","-nostdin","-y","-v","error","-i",str(MASTER),"-i",str(ORIGINAL),"-i",str(VIDU),
      "-filter_complex",";".join(parts),"-map","[v]","-c:v","libx264","-preset","veryfast","-crf","18",
      "-pix_fmt","yuv420p","-movflags","+faststart",str(silent)]
 run(cmd,250)
 meta=json.loads(run(["ffprobe","-v","error","-show_entries","format=duration:stream=codec_name,width,height","-of","json",str(silent)]))
 duration=float(meta["format"]["duration"])
 if not 18<=duration<=25:raise RuntimeError("HYBRID_DURATION_NOT_SOCIAL_FRIENDLY "+str(duration))
 return silent,duration
def music(duration,starts):
 sr=32000;t=np.arange(round(sr*duration),dtype=np.float32)/sr
 sound=np.zeros_like(t)
 # A composed original sustained score, not excerpts from existing copyrighted pieces.
 chords=[[130.81,196.0,261.63],[146.83,174.61,220],[110,164.81,220],[130.81,164.81,246.94],[146.83,220,293.66]]
 for n,start in enumerate(starts):
  end=starts[n+1] if n+1<len(starts) else duration
  mask=(t>=start)&(t<end)
  u=t[mask]-start
  z=np.zeros_like(u)
  for ix,f in enumerate(chords[n%len(chords)]):
   z+=(0.022-.002*ix)*np.sin(2*np.pi*f*u+ix*.30)
   z+=.003*np.sin(2*np.pi*f*2.003*u+ix*.25)
  sound[mask]+=z
 # Short subtle rises at transitions to restored stills, never five distinct unrelated songs.
 for start in starts:
  d=t-start;m=(d>=0)&(d<.52)
  sound[m]+=.03*np.sin(2*np.pi*(112*d[m]+70*d[m]**2))*np.exp(-9*d[m])
 env=np.minimum(1,t/.6)*np.minimum(1,np.maximum(0,(duration-t)/.80))
 sound=np.tanh(sound*2.3)*env
 wav=R/"SCORE_ORIGINALE_V86.wav"
 with wave.open(str(wav),"wb") as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr)
  w.writeframes((np.column_stack([sound,np.roll(sound,int(.013*sr))*.94])*19000).astype("<i2").tobytes())
 return wav
def contact(duration,chapter):
 cap=cv2.VideoCapture(str(FINAL))
 board=Image.new("RGB",(5*230,430),(16,19,22))
 d=ImageDraw.Draw(board)
 for i,x in enumerate(chapter):
  # Show the restored color moment for classic; after t=1s for the new Vidu segment.
  when=x["start_s"]+min(x["duration_s"]-.10,2.5 if i<4 else 2.0)
  cap.set(cv2.CAP_PROP_POS_MSEC,when*1000)
  ok,f=cap.read()
  if not ok:raise RuntimeError("FINAL_CONTACT_FRAME_MISSING")
  frame=Image.fromarray(cv2.cvtColor(f,cv2.COLOR_BGR2RGB)).resize((224,400))
  board.paste(frame,(i*230+3,25))
  d.text((i*230+5,5),x["title"],fill=(253,244,221))
 cap.release()
 board.save(R/"CONFRONTO_CINQUE_SCENE_V86.jpg",quality=92)
def make():
 restoration,task,vduration=check()
 silent,duration=create_video(vduration)
 classical=[(x["end"]-x["start"])/FPS for x in SHOTS]
 leader=.86
 expected=sum(classical)+leader+5.0
 if abs(expected-duration)>.12:raise RuntimeError("EXPECTED_REAL_SCENE_DURATION_MISMATCH")
 starts=[0];acc=0
 for dur in classical:
  acc+=dur;starts.append(acc)
 wav=music(duration,starts)
 run(["ffmpeg","-nostdin","-y","-v","error","-i",str(silent),"-i",str(wav),
      "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","160k",
      "-metadata","comment=Real moving archival 1906 footage, AI-reconstructed color stills and 1 Vidu video scene; digital reconstruction disclosure",
      "-shortest","-movflags","+faststart",str(FINAL)],100)
 run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(FINAL),"-f","null","-"],130)
 chapters=[];offset=0
 for k,(shot,dur) in enumerate(zip(SHOTS,classical),1):
  chapters.append({"slot":k,"title":shot["title"],"type":"REAL_BW_FILM_TO_REAL_AI_RESTORED_PHOTO",
     "source_historical_film_timestamp_s":shot["source_time"],"start_s":round(offset,3),
     "duration_s":round(dur,3),"photo_sha256":sha(R/shot["original_photo"])})
  offset+=dur
 chapters.append({"slot":5,"title":"HORSE CARRIAGES LIVE","type":"REAL_BW_ARCHIVAL_MOTION_THEN_VIDU_CONTINUOUS_COLOR_MOVING_VIDEO",
   "historical_source_timestamp_s":43.0,"original_BW_motion_s":.86,"vidu_new_motion_s":5.0,
   "start_s":round(offset,3),"duration_s":round(leader+5.0,3),
   "start_photo_sha256":restoration["restored_photo_sha256"],"new_vidu_task_id":task["task_id"],
   "human_semantic_review":"PENDING"})
 contact(duration,chapters)
 cover=R/"COPERTINA.jpg"
 im=Image.open(R/"FOTO_FOTOGRAFICA_AI_03.png").convert("RGB").resize((720,1280))
 d=ImageDraw.Draw(im,"RGBA")
 d.rounded_rectangle((24,38,694,235),radius=18,fill=(8,11,16,153))
 try:
  font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",48)
  small=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",25)
 except:font=ImageFont.load_default();small=font
 d.text((48,75),"SAN FRANCISCO",font=font,fill=(254,245,228,255))
 d.text((48,157),"APRIL 14 · 1906",font=small,fill=(231,207,163,255))
 im.save(cover,quality=94)
 posts={
  "FACEBOOK":"SAN FRANCISCO · 1906. Quattro giorni prima del terremoto, Market Street era già un fiume di tram, carrozze, ciclisti e vite. Quattro momenti della pellicola autentica diventano fotografie restaurate, poi un quinto momento prende vita a colori. Riprese originali dei Miles Brothers, Library of Congress. Colori e movimento Vidu ricostruiti con IA; non sono riprese storiche originali a colori. #LaStoriaRivive #SanFrancisco1906",
  "INSTAGRAM":"SAN FRANCISCO · 1906. Quattro giorni prima che tutto cambiasse. 🎞️ Quattro fermo-immagine fotografici restaurati e una scena finale che continua a muoversi a colori. Film autentico dei fratelli Miles, restauri e animazione AI interpretativi. #HistoryReels #SanFrancisco",
  "TIKTOK":"La San Francisco di 120 anni fa, pochi giorni prima del terremoto. Guarda il film autentico fermarsi in fotografie modernissime… e poi riprendere vita! 🎞️ Ricostruzione AI dei colori e del movimento, non film originale a colori.",
  "YOUTUBE":"SAN FRANCISCO · 1906 | THE PAST MOVES AGAIN\n\nFilm originale: Miles Brothers, A Trip Down Market Street Before the Fire, girato 14 aprile 1906. Fonte: Library of Congress https://www.loc.gov/item/00694408/ . Quattro scene storiche realmente in movimento B/N diventano fotografie a colori ricostruite con IA. Una quinta scena originale distinta si collega a un inserto video animato da Vidu Q2 Pro Fast per cinque secondi: colori, volti e movimento ricostruiti digitalmente, non originali autentici. Controllo artistico e diritti territoriali in revisione."
 }
 for k,v in posts.items():(R/f"POST_{k}.txt").write_text(v+"\n",encoding="utf8")
 report={"version":"V86_SF1906_NEW_SUBJECT_4CLASSIC_1VIDU","status":"TECHNICAL_PREVIEW_ARTISTIC_REVIEW_REQUIRED",
   "subject":"Market Street, San Francisco, filmed April 14, 1906, four days before the earthquake",
   "source_original":"https://www.loc.gov/item/00694408/","source_original_sha256":ORIGINAL_SHA,
   "original_4_classic_master_sha256":V70_SHA,"real_ai_photographs":4,
   "vidu_5th_scene_source_frame_time":43.0,"vidu_task_id":task["task_id"],
   "vidu_original_video_sha256":task.get("vidu_original_sha256"),
   "vidu_moving_color_sha256":sha(VIDU),"vidu_api_credits_provider_reported":task.get("provider_credits"),
   "new_vidu_paid_calls":1,"five_distinct_historical_shots":True,
   "era_coherent":True,"scene_count":5,"classic_count":4,"vidu_count":1,
   "duration_s":round(duration,3),"resolution":[720,1280],"fps":FPS,
   "first_1s_bw_to_color_on_true_vidu_generated_motion":True,
   "source_rights":"LOC original collection public domain, territory/model/derivative publication reviews pending",
   "new_generated_video_is_interpretation":True,"full_ffmpeg_decode_passed":True,
   "social_published":False,"site_published":False,"artistic_review":"PENDING",
   "final_sha256":sha(FINAL),"chapters":chapters}
 (R/"QA_PUBLIC_V86.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 kit=R/"SAN_FRANCISCO_1906_V86_ANDROID.zip"
 with zipfile.ZipFile(kit,"w",zipfile.ZIP_DEFLATED) as z:
  for p in [FINAL,cover,R/"QA_PUBLIC_V86.json",R/"CONFRONTO_CINQUE_SCENE_V86.jpg",*[R/f"POST_{k}.txt" for k in posts]]:
   z.write(p,p.name)
 with zipfile.ZipFile(kit) as z:
  if z.testzip():raise RuntimeError("ANDROID_KIT_CRC_ERROR")
 print("V86_FINISHED_REAL_5SCENE_MP4",FINAL,FINAL.stat().st_size,"DURATION",duration,"VIDU_SINGLE_TASK",task["task_id"],flush=True)
if __name__=="__main__":make()
