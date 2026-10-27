#!/usr/bin/env python3
"""Nautilus: natural Gacrux voice with scene-aligned original engravings; no subtitles."""
from __future__ import annotations
import json,math,subprocess,tempfile
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image
from gemini_voice import synthesize

EP=Path("episodes/nautilus_20261027")
OUT=Path("output/nautilus_20261027")
VIDEO_NAME="TRA_LE_PAGINE_VENTIMILA_LEGHE_SOTTO_I_MARI.mp4"
FPS=24
SR=24000

def command(*args):
 print("FFMPEG",str(args[-1]),flush=True)
 subprocess.run(list(map(str,args)),check=True)

def ocean_score(length,destination):
 """Original minor-mode atmospheric soundtrack, with sections tied to story arcs."""
 total=math.ceil((length+.1)*SR)
 track=np.zeros(total,dtype=np.float32)
 chapters=[(0.00,(45,52,57)),(.23,(47,54,59)),(.43,(48,55,60)),
           (.60,(43,50,55)),(.77,(44,51,56)),(.91,(45,52,57))]
 bounds=[int(f*length*SR) for f,_ in chapters]+[total]
 for k,(_,chord) in enumerate(chapters):
  a,z=bounds[k],bounds[k+1]
  n=max(0,z-a)
  if not n:continue
  t=np.arange(n,dtype=np.float32)/SR
  # Dark suspended harmony, no sampled/licensed material
  section=np.zeros(n,dtype=np.float32)
  for j,midi in enumerate(chord):
   hz=440.0*2**((midi-69)/12)
   section+= (.012/(j+1)**.6)*(
     np.sin(2*np.pi*hz*t+.11*j) + .22*np.sin(2*np.pi*2*hz*t))
  env=np.minimum(1,t/2.3)*np.minimum(1,(n/SR-t)/3.2)
  env=np.maximum(0,env)
  track[a:z]+=section*env
 notes=[57,62,64,60,57,55,59,62,60,57,64,62,59,55,52]
 sec=2.25
 for i in range(math.ceil(length/sec)):
  a=round(i*sec*SR);note=notes[(i*7+i//8)%len(notes)]
  size=min(total-a,round((2.25 if i%4 else 3.15)*SR))
  if size<=0:break
  t=np.arange(size,dtype=np.float32)/SR
  freq=440.0*2**((note-69)/12)
  # Soft plucked resonances; rests deliberately alternate
  amp=0.022 if i%7 not in (3,4) else .006
  env=np.minimum(1,t/.035)*np.exp(-t/(.82 if i%4 else 1.35))
  track[a:a+size]+=amp*(np.sin(2*np.pi*freq*t)+.19*np.sin(4*np.pi*freq*t))*env
 x=np.arange(total,dtype=np.float32)/SR
 track*=np.minimum(1,x/2.8)*np.minimum(1,np.maximum(0,length-x)/5.8)
 track=np.clip(track,-.25,.25)
 sf.write(destination,track,SR)
 return destination

def make():
 from episode_v3 import branded_cover
 plan=json.loads((EP/"scene_plan_verne.json").read_text(encoding="utf-8"))["scenes"]
 cues=json.loads((EP/"scene_cues.json").read_text(encoding="utf-8"))
 if len(plan)!=len(cues):raise RuntimeError("Storyboard/audio anchors disagree")
 for i in range(len(plan)):
  picture=EP/"images"/f"scena_{i+1:02d}.jpg"
  if not picture.is_file():raise RuntimeError("Original engraving missing: "+str(picture))
 OUT.mkdir(parents=True,exist_ok=True)
 branded_cover(OUT,EP,json.loads((EP/"metadata.json").read_text(encoding="utf-8")))
 voice,timed=synthesize((EP/"testo.txt").read_text(encoding="utf-8"),OUT)
 seconds=len(voice)/SR
 starts=[float(timed[c["start_sentence"]][1]) for c in cues]
 starts[0]=0.
 bounds=starts+[seconds]
 if any(y<=x for x,y in zip(bounds,bounds[1:])):
  raise RuntimeError("Unreliable voice cue ordering: voice needs new alignment")
 (OUT/"SINCRONIA_SCENE.json").write_text(json.dumps([
   {"scene":i+1,"image":plan[i]["source_image_id"],"start":round(starts[i],3),
    "end":round(bounds[i+1],3),"narration_anchor":cues[i]["narration_anchor"],
    "image_intent":plan[i]["visual_intent"]}
   for i in range(len(plan))],ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 with tempfile.TemporaryDirectory() as work:
  temp=Path(work)
  clips=[]
  for i,row in enumerate(plan):
   nframes=max(1,round((bounds[i+1]-bounds[i])*FPS))
   input_img=EP/"images"/f"scena_{i+1:02d}.jpg"
   for part in (["opening","scene"] if i==0 else ["scene"]):
    frames=nframes
    image=input_img
    if part=="opening":
     frames=min(nframes,round(3.5*FPS))
     image=OUT/"COPERTINA_SERIE.jpg"
    elif i==0:
     frames=max(0,nframes-round(3.5*FPS))
     if not frames:continue
    dest=temp/f"shot_{i:02d}_{part}.mp4"
    style=row["camera_style"] if part=="scene" else "locked"
    if style=="locked":
     vf="scale=720:1280,format=yuv420p"
    else:
     pos="(iw-iw/zoom)/2"
     if style=="slow_zoom_in":
      zoom="min(1.019,1+on*0.00007)"
      x=pos
     elif style=="slow_zoom_out":
      zoom="max(1.0,1.019-on*0.00007)"
      x=pos
     else:
      zoom="1.018"
      amount=f"min(1,on/{max(frames-1,1)})"
      x=f"(iw-iw/zoom)*{amount}" if style=="slow_pan_right" else f"(iw-iw/zoom)*(1-{amount})"
     vf=f"zoompan=z='{zoom}':x='{x}':y='(ih-ih/zoom)/2':d=1:s=720x1280:fps={FPS},format=yuv420p"
    command("ffmpeg","-hide_banner","-loglevel","error","-y","-loop","1",
            "-framerate",FPS,"-i",image,"-vf",vf,"-frames:v",frames,
            "-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p","-an",dest)
    clips.append(dest)
  listing=temp/"clips.txt"
  listing.write_text("".join(f"file '{p}'\n" for p in clips),encoding="utf-8")
  visual=temp/"video_only.mp4"
  command("ffmpeg","-hide_banner","-loglevel","error","-y",
          "-f","concat","-safe","0","-i",listing,"-c","copy",visual)
  backing=ocean_score(seconds,OUT/"MUSICA_ORIGINALE.wav")
  video=OUT/VIDEO_NAME
  command("ffmpeg","-hide_banner","-loglevel","error","-y",
          "-i",visual,"-i",OUT/"VOCE.wav","-i",backing,
          "-filter_complex","[1:a]volume=1.0[v];[2:a]volume=0.42[m];[v][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.93[a]",
          "-map","0:v:0","-map","[a]","-sn",
          "-c:v","copy","-c:a","aac","-b:a","160k",
          "-movflags","+faststart","-shortest",video)
 # Inspect the entire output for decode corruption, not just its extension.
 command("ffmpeg","-v","error","-xerror","-i",video,"-f","null","-")
 raw=subprocess.check_output(["ffprobe","-v","error","-show_format","-show_streams","-of","json",str(video)])
 data=json.loads(raw)
 streams=data["streams"]
 if len([s for s in streams if s.get("codec_type")=="video"])!=1:raise RuntimeError("No single video track")
 if len([s for s in streams if s.get("codec_type")=="audio"])!=1:raise RuntimeError("No single audio track")
 if any(s.get("codec_type")=="subtitle" for s in streams):raise RuntimeError("Unexpected subtitles")
 clip_seconds=float(data["format"]["duration"])
 if abs(clip_seconds-seconds)>2.0:raise RuntimeError("Missing video/audio at end")
 alignment=json.loads((OUT/"ALLINEAMENTO_VOCE.json").read_text())
 qa={"episode":"nautilus_20261027","format":"libri","status":"rendered_needs_artistic_review",
     "file":VIDEO_NAME,"duration_s":round(clip_seconds,2),"images":len(plan),
     "voice":"Google Gemini Gacrux","voice_alignment_method":alignment.get("method"),
     "visual_rights":"1871 original engravings, see provenance","source_review":"documented, final review pending",
     "music":"original ambient composition","publishing":"not_performed","site_import":"not_performed",
     "commercial_voice_terms_review":"pending"}
 (OUT/"QUALITY.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("MP4_RENDERED",json.dumps(qa,ensure_ascii=False),flush=True)

if __name__=="__main__":make()
