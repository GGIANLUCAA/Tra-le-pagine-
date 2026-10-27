#!/usr/bin/env python3
"""Generate one authorized Nils narration in the existing Gemini Gacrux voice.
NO image/video generative APIs, and no TTS retries. Store audio even if alignment fails.
"""
from __future__ import annotations
import hashlib, json, os, sys, shutil
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/"src"))
from gemini_voice import synthesize, sentences
import numpy as np, soundfile as sf

P=Path("episodes/nils_holgersson_20261027/COPIONE_ITALIANO.txt")
OUT=Path("output/nils_gacrux_20261027")
OUT.mkdir(parents=True,exist_ok=True)
script=P.read_text(encoding="utf-8").strip()
paragraphs=[x.strip() for x in script.split("\n\n") if x.strip()]
if len(paragraphs)!=16:raise RuntimeError(f"Expected 16 story beats, found {len(paragraphs)}")
if not os.environ.get("GEMINI_API_KEY"):raise RuntimeError("GEMINI_API_KEY secret absent; no substitution")
if not 310<=len(script.split())<=520:raise RuntimeError("Unexpected transcript length")
# Exactly one synthesis attempt by the repository's approved Google Gemini Gacrux implementation.
voice,timed=synthesize(script,OUT)
wav=OUT/"VOCE.wav"
if not wav.is_file():raise RuntimeError("Voice WAV missing")
audio,sr=sf.read(wav,dtype="float32")
duration=len(audio)/sr
if not 120<=duration<=270 or float(np.sqrt(np.mean(audio.astype(np.float64)**2)))<.005:
    raise RuntimeError(f"Voice duration or signal rejected: {duration}")
if len(timed)!=len(sentences(script)):raise RuntimeError("Incomplete sentence alignments")
indices=[];cursor=0
for p in paragraphs:
    indices.append(cursor)
    cursor+=len(sentences(p))
if cursor!=len(timed):raise RuntimeError("Text paragraph splitter disagrees with narration alignment")
starts=[float(timed[i][1]) for i in indices]
starts[0]=0.0
if any(a>=b for a,b in zip(starts,starts[1:])):raise RuntimeError("Bad scene timeline")
align_path=OUT/"ALLINEAMENTO_VOCE.json"
algn=json.loads(align_path.read_text()) if align_path.exists() else {}
timeline={"schema":"nils-narrative-speech-sync-v1","model":"gemini-3.8-flash-tts",
 "voice":"Gacrux","script_sha256":hashlib.sha256(script.encode()).hexdigest(),
 "wav_sha256":hashlib.sha256(wav.read_bytes()).hexdigest(),
 "duration_seconds":duration,"alignment_method":algn.get("method","unknown"),
 "matched_fraction":algn.get("matched_fraction"),
 "scenes":[{"scene":i+1,"start_seconds":starts[i],
             "end_seconds":starts[i+1] if i+1<len(starts) else duration,
             "narration":paragraphs[i]} for i in range(len(paragraphs))]}
(OUT/"SCENE_TIMELINE.json").write_text(json.dumps(timeline,ensure_ascii=False,indent=2),encoding="utf-8")
(OUT/"COPIONE_ITALIANO.txt").write_text(script+"\n",encoding="utf-8")
print(f"GACRUX COMPLETE: {duration:.2f}s, 16 scenes, alignment={algn.get('method')}",flush=True)
