#!/usr/bin/env python3
"""One verified Google Gemini Gacrux Italian narration, no retries or substitute voices."""
from pathlib import Path
import sys,os,json,hashlib
import soundfile as sf,numpy as np
sys.path.insert(0,str(Path.cwd()/"src"))
from gemini_voice import synthesize,sentences
P=Path("episodes/sleepy_hollow_20261028/COPIONE_ITALIANO.txt")
OUT=Path("output/sleepy_hollow_gacrux_20261028");OUT.mkdir(parents=True,exist_ok=True)
script=P.read_text(encoding="utf-8").strip()
paras=[x.strip() for x in script.split("\n\n") if x.strip()]
if len(paras)!=14:raise RuntimeError(f"Expected 14 story beats, got {len(paras)}")
if not os.environ.get("GEMINI_API_KEY"):raise RuntimeError("No configured Gacrux integration; do not substitute")
if not 300<=len(script.split())<=450:raise RuntimeError("Unexpected word count")
# The existing approved repo integration makes exactly ONE Google speech request if uncached.
voice,timed=synthesize(script,OUT)
wav=OUT/"VOCE.wav"
data,sr=sf.read(wav,dtype="float32")
duration=len(data)/sr
if not 115<=duration<=250:raise RuntimeError(f"Unexpected audio duration {duration}")
if float(np.sqrt(np.mean(data.astype(np.float64)**2)))<.004:raise RuntimeError("Narration signal too quiet")
if len(timed)!=len(sentences(script)):raise RuntimeError("Sentence alignment incomplete")
starts=[];cursor=0
for p in paras:
    starts.append(float(timed[cursor][1]))
    cursor+=len(sentences(p))
if cursor!=len(timed):raise RuntimeError("Paragraph segmentation mismatch")
starts[0]=0.
if any(a>=b for a,b in zip(starts,starts[1:])):raise RuntimeError("Nonmonotonic timing")
align=json.loads((OUT/"ALLINEAMENTO_VOCE.json").read_text())
manifest={"schema":"sleepy-hollow-voice-timing-v13","voice":"Google Gemini Gacrux",
 "model":"gemini-3.8-flash-tts","duration":duration,"wav_sha256":hashlib.sha256(wav.read_bytes()).hexdigest(),
 "script_sha256":hashlib.sha256(script.encode()).hexdigest(),"alignment":align,
 "scenes":[{"beat":i+1,"start":starts[i],"end":starts[i+1] if i+1<len(starts) else duration,
 "narration":paras[i]} for i in range(len(paras))]}
(OUT/"SCENE_TIMELINE.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
(OUT/"COPIONE_ITALIANO.txt").write_text(script+"\n",encoding="utf-8")
print("GACRUX GENERATED ONCE",duration,"seconds; alignment",align.get("method"),align.get("matched_fraction"),flush=True)
