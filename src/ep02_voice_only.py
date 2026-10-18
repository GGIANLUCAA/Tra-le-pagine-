from pathlib import Path
import json,sys,shutil
sys.path.insert(0,"src")
from gemini_voice import synthesize
ep=Path("episodes/02_arte_della_gioia")
out=Path("output_ep02");out.mkdir(exist_ok=True)
script=(ep/"testo.txt").read_text(encoding="utf-8")
audio,timed=synthesize(script,out)
(out/"TIMING_FRASI.json").write_text(json.dumps([{"text":sentence,"start":start,"end":end} for sentence,start,end in timed],indent=2,ensure_ascii=False),encoding="utf-8")
shutil.copy2(ep/"testo.txt",out/"COPIONE.txt")
print("EP02",len(timed),"frasi",len(audio)/24000,"secondi")
