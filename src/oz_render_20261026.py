#!/usr/bin/env python3
"""Oz: scene-anchored Gacrux narrative with restrained camera and original piano."""
import json,math,subprocess,tempfile
from pathlib import Path
import numpy as np
import soundfile as sf
from gemini_voice import synthesize
EP=Path("episodes/oz_dorothy_20261026")
OUT=Path("output/oz_dorothy_20261026")
FPS=24
NAME="TRA_LE_PAGINE_IL_MERAVIGLIOSO_MAGO_DI_OZ.mp4"

def cmd(*args):
 print("RUN:",str(args[0]),str(args[-1]),flush=True)
 subprocess.run([str(x) for x in args],check=True)

def music(seconds,out):
 rate=24000;n=math.ceil(rate*(seconds+.2));sound=np.zeros(n,np.float32)
 # Own composed accompaniment, not a third-party recording.
 beats=[(0,3,7,10),(5,9,12,16),(8,0,3,7),(7,11,2,5),
        (0,3,7,10),(3,7,10,14),(5,9,0,4),(7,11,2,5)]
 step=0.82;length=math.ceil(seconds/step)
 for k in range(length):
  chord=beats[(k//12)%len(beats)]
  degree=chord[[0,1,2,1,3,2,1,0,1,2,3,2][k%12]]
  note=50+degree
  if k%12 in (0,6):note-=12
  t0=int(k*step*rate);dur=min(n-t0,int((1.6 if k%3 else 2.15)*rate))
  if dur<=0:continue
  t=np.arange(dur,dtype=np.float32)/rate
  f=440*2**((note-69)/12)
  timbre=(np.sin(2*np.pi*f*t)+.21*np.sin(2*np.pi*(2*f)*t)+.11*np.sin(2*np.pi*(3*f)*t))
  attack=np.minimum(1,t/.018);env=attack*np.exp(-t/(.58 if k%3 else 1.15))
  sound[t0:t0+dur]+=.055*timbre*env
  if k%4==0:
   for offset in (0,7,12):
    bass=note-12+offset;freq=440*2**((bass-69)/12)
    bd=min(n-t0,int(3.2*rate));bt=np.arange(bd,dtype=np.float32)/rate
    sound[t0:t0+bd]+=.013*np.sin(2*np.pi*freq*bt)*np.exp(-bt/1.6)
 for delay,amount in [(int(.14*rate),.16),(int(.29*rate),.08)]:
  sound[delay:]+=amount*sound[:-delay].copy()
 x=np.arange(n,dtype=np.float32)/rate
 sound*=np.minimum(1,x/2.2)*np.minimum(1,np.maximum(0,seconds-x)/5.3)
 sound=np.clip(sound,-.25,.25)
 sf.write(out,sound,rate)
 return out

def render():
 OUT.mkdir(parents=True,exist_ok=True)
 plan=json.loads((EP/"scene_plan_oz.json").read_text())["scenes"]
 cues=json.loads((EP/"scene_cues.json").read_text())
 if len(plan)!=len(cues):raise RuntimeError("Scene plan/cues mismatch")
 for k in range(len(cues)):
  if not (EP/"images"/f"scena_{k+1:02d}.jpg").exists():raise RuntimeError("Missing verified art")
 narration=(EP/"testo.txt").read_text(encoding="utf-8")
 wav,timed=synthesize(narration,OUT)
 dur=len(wav)/24000
 starts=[float(timed[cue["start_sentence"]][1]) for cue in cues]
 starts[0]=0
 boundaries=starts+[dur]
 if any(b<=a for a,b in zip(boundaries,boundaries[1:])):
  raise RuntimeError("Voice timing not monotonic; check alignment before render")
 (OUT/"SINCRONIA_SCENE.json").write_text(json.dumps([
  {"scene":i+1,"from_sec":round(starts[i],3),"to_sec":round(boundaries[i+1],3),
   "first_sentence":cues[i]["narration_anchor"],"visual":plan[i]["intent"]}
  for i in range(len(plan))],ensure_ascii=False,indent=2))
 with tempfile.TemporaryDirectory() as tmpname:
  temp=Path(tmpname);files=[]
  for i,row in enumerate(plan):
   frames=max(1,round((boundaries[i+1]-boundaries[i])*FPS))
   original=EP/"images"/f"scena_{i+1:02d}.jpg"
   output=temp/f"clip_{i+1:02d}.mp4"
   style=row["camera_style"]
   if style=="locked":
    filter_="scale=720:1280,format=yuv420p"
   else:
    # 2% restrained center zoom; picture is already safely letterboxed.
    incr="0.000075" if style=="slow_scale_down" else "0.00011"
    filter_=("zoompan=z='min(zoom+"+incr+",1.025)':"
             "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
             "d=1:s=720x1280:fps=24,format=yuv420p")
   cmd("ffmpeg","-hide_banner","-loglevel","error","-y",
       "-loop","1","-framerate",FPS,"-i",original,"-vf",filter_,
       "-frames:v",frames,"-an","-c:v","libx264","-preset","veryfast",
       "-crf",24,"-pix_fmt","yuv420p",output)
   files.append(output)
  listing=temp/"list.txt"
  listing.write_text("".join("file '"+str(x)+"'\n" for x in files))
  stitched=temp/"visuals.mp4"
  cmd("ffmpeg","-hide_banner","-loglevel","error","-y",
      "-f","concat","-safe","0","-i",listing,"-c","copy",stitched)
  backing=music(dur,OUT/"MUSICA_ORIGINALE.wav")
  final=OUT/NAME
  cmd("ffmpeg","-hide_banner","-loglevel","error","-y",
      "-i",stitched,"-i",OUT/"VOCE.wav","-i",backing,
      "-filter_complex","[1:a]volume=1.0[v];[2:a]volume=.34[m];[v][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.93[a]",
      "-map","0:v:0","-map","[a]","-sn",
      "-c:v","copy","-c:a","aac","-b:a","160k","-movflags","+faststart","-shortest",final)
 cmd("ffmpeg","-v","error","-xerror","-i",final,"-f","null","-")
 raw=subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration:stream=codec_type,width,height","-of","json",str(final)])
 probe=json.loads(raw)
 if not any(x["codec_type"]=="video" for x in probe["streams"]):raise RuntimeError("No video")
 if not any(x["codec_type"]=="audio" for x in probe["streams"]):raise RuntimeError("No audio")
 if any(x["codec_type"]=="subtitle" for x in probe["streams"]):raise RuntimeError("Unexpected subtitle")
 report={"status":"rendered_needs_artistic_review","episode":"oz_dorothy_20261026",
         "duration_s":round(dur,2),"source_images":len(plan),"voice":"Google Gemini Gacrux",
         "video":NAME,"source":"1900 Denslow originals, public domain",
         "rights_note":"Google API voice commercial use not independently certified",
         "subtitle_policy":"off","publication":"not_performed","site_import":"not_performed",
         "audio_alignment":"ASR when available; inspect voice timing"}
 (OUT/"QUALITY.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print("COMPLETE",report,flush=True)

if __name__=="__main__":render()
