#!/usr/bin/env python3
"""One authorized Gemini Gacrux voice pass for The Selfish Giant, no retries.
Outputs original voice, ASR timings and provenance; never calls paid video models.
"""
from __future__ import annotations
import hashlib,json,os,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/"src"))
from gemini_voice import synthesize,sentences
import numpy as np,soundfile as sf
p=Path("episodes/il_gigante_egoista_20261028/COPIONE_ITALIANO.txt")
out=Path("output/il_gigante_egoista_20261028")
out.mkdir(parents=True,exist_ok=True)
script=p.read_text(encoding="utf-8").strip()
paragraphs=[x.strip() for x in script.split("\n\n") if x.strip()]
if len(paragraphs)!=16:raise RuntimeError(f"Expected 16 beats, found {len(paragraphs)}")
if not 300<=len(script.split())<=470:raise RuntimeError("Script word count outside validated range")
if not os.environ.get("GEMINI_API_KEY"):raise RuntimeError("GEMINI_API_KEY absent; do not substitute voice")
# Single call only, no retry. Gemini free tier/quota must accept; otherwise stop.
voice,timed=synthesize(script,out)
wav=out/"VOCE.wav"
audio,sr=sf.read(wav,dtype="float32")
duration=len(audio)/sr
if not 120<=duration<=260:raise RuntimeError(f"Voice outside 2-4.3min: {duration:.1f}s")
if float(np.sqrt(np.mean(audio.astype(np.float64)**2)))<.005:raise RuntimeError("Voice too quiet")
phrases=sentences(script)
if len(timed)!=len(phrases):raise RuntimeError("ASR sentence timing incomplete")
indices=[];cursor=0
for para in paragraphs:
    indices.append(cursor);cursor+=len(sentences(para))
if cursor!=len(timed):raise RuntimeError("Paragraph sentence mapping mismatch")
starts=[float(timed[i][1]) for i in indices];starts[0]=0.
if any(a>=b for a,b in zip(starts,starts[1:])):raise RuntimeError("Nonmonotonic timestamps")
alignment=json.loads((out/"ALLINEAMENTO_VOCE.json").read_text())
timeline={"schema":"gigante-narrative-sync-v1","provider":"Google Gemini","model":"gemini-3.8-flash-tts","voice":"Gacrux","language":"it","script_sha256":hashlib.sha256(script.encode()).hexdigest(),"wav_sha256":hashlib.sha256(wav.read_bytes()).hexdigest(),"duration_seconds":duration,"alignment":alignment,"scenes":[{"scene":i+1,"start_seconds":starts[i],"end_seconds":starts[i+1] if i+1<len(starts) else duration,"narration":paragraphs[i]} for i in range(16)]}
(out/"SCENE_TIMELINE.json").write_text(json.dumps(timeline,ensure_ascii=False,indent=2)+"\n")
(out/"COPIONE_ITALIANO.txt").write_text(script+"\n")
print("GACRUX GENERATED:",round(duration,2),"seconds; ASR",alignment.get("method"),"match",alignment.get("matched_fraction"),flush=True)
