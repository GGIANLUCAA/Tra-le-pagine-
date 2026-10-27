"""Run Whisper ASR on previously produced Gacrux WAV without generating new speech."""
import json
from pathlib import Path
from faster_whisper import WhisperModel
p=Path("source_audio/VOCE.wav")
m=WhisperModel("base",device="cpu",compute_type="int8",cpu_threads=4)
segments,meta=m.transcribe(str(p),language="it",beam_size=3,word_timestamps=True,vad_filter=False)
words=[];full=[]
for seg in segments:
  full.append({"start":seg.start,"end":seg.end,"text":seg.text})
  for w in seg.words or []:words.append({"word":w.word,"start":w.start,"end":w.end,"prob":w.probability})
out=Path("output/canterville-word-alignment");out.mkdir(parents=True,exist_ok=True)
(out/"WORDS_ASR.json").write_text(json.dumps({"words":words,"segments":full,"language":meta.language,"n_words":len(words)},ensure_ascii=False,indent=2))
print("ASR_WORDS",len(words),"SEGMENTS",len(full),flush=True)
