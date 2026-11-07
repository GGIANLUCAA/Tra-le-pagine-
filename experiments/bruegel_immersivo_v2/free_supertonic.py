#!/usr/bin/env python3
"""No cloud speech API: real Italian open-weight narration with Supertonic 3.
One speaker across all eight chapters. Audio exact paragraph boundaries for film editing.
"""
import json, time
from pathlib import Path
import numpy as np, soundfile as sf
from supertonic import TTS
from render import BEATS, BUILD

BUILD.mkdir(parents=True,exist_ok=True)
model=TTS(model_dir="assets",auto_download=False)
style=model.get_voice_style(voice_name="M3")
sr=44100
parts=[np.zeros(int(.20*sr),dtype=np.float32)]
boundaries=[]
elapsed=len(parts[0])/sr
for i,b in enumerate(BEATS):
 print("VOICE CHAPTER",i,"BEGIN",flush=True)
 t=time.monotonic()
 wav,duration=model.synthesize(text=b["spoken"],lang="it",voice_style=style,total_steps=12,speed=0.96)
 a=np.asarray(wav,dtype=np.float32).squeeze()
 if a.ndim==2:
  a=a.mean(axis=0) if a.shape[0]<a.shape[1] else a.mean(axis=1)
 assert a.ndim==1 and a.size>sr*2 and np.isfinite(a).all(),(i,a.shape)
 peak=np.max(np.abs(a))
 if peak>.91:a*=.91/peak
 fade=min(len(a)//10,int(sr*.035))
 if fade>0:
  a[:fade]*=np.linspace(0,1,fade)
  a[-fade:]*=np.linspace(1,0,fade)
 gap=np.zeros(int(sr*(.26 if i not in (4,6) else .42)),dtype=np.float32)
 start=elapsed
 elapsed+=(len(a)+len(gap))/sr
 boundaries.append([start,elapsed])
 parts.extend([a,gap])
 print("VOICE CHAPTER",i,"END",round(elapsed-start,2),"sec",round(time.monotonic()-t,2),"inference",flush=True)
audio=np.concatenate(parts)
sf.write(str(BUILD/"VOCE.wav"),audio,sr)
(BUILD/"VOICE_CHAPTER_RANGES.json").write_text(json.dumps({"voice":"Supertonic 3 M3","sample_rate":sr,"chapters":boundaries,"total_seconds":elapsed},indent=2),encoding="utf8")
print("ITALIAN_OPEN_VOICE_READY",round(elapsed,2),"seconds",flush=True)
