"""Generate the verified 03 Siddharta narration and timing without generating video placeholders."""
import json,shutil,sys
from pathlib import Path
sys.path.insert(0,"src")
from gemini_voice import synthesize
ep=Path("episodes/03_siddharta")
out=Path("output_ep03")
out.mkdir(parents=True,exist_ok=True)
script=(ep/"testo.txt").read_text(encoding="utf-8")
audio,timed=synthesize(script,out)
(out/"TIMING_FRASI.json").write_text(json.dumps([{"text":t,"start":a,"end":b} for t,a,b in timed],ensure_ascii=False,indent=2),encoding="utf-8")
shutil.copy2(ep/"testo.txt",out/"COPIONE.txt")
shutil.copy2(ep/"scene_cues.json",out/"SCENE.json")
print("EPISODIO 03:",len(timed),"frasi allineate;",round(len(audio)/24000,2),"secondi")
