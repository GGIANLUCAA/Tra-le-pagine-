#!/usr/bin/env python3
"""OFFLINE acoustic-to-words alignment of a pre-existing genuine Socrates Gacrux WAV.

No Google API requests. Reject interpolation-only output as a final synced Critico.
"""
from pathlib import Path
import json,hashlib,sys
import numpy as np
import soundfile as sf

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import gemini_voice as voice
IN=ROOT/"output/artvision-socrates-gacrux-v66/voice"
SCRIPT=ROOT/"docs/productions/2026-10-29-socrates-critico-master-v60/COPIONE_GACRUX_V62.txt"
EXPECTED_WAV="b26b6826380c8dcc9b27a590bb6ecd43dd12107dafd367e429ad43351bd8a476"
EXPECTED_SCRIPT="c85c4017bec6efd0a75e46ee62b83ed4aeff14e6018e5f66f911b4fd941a0828"

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    text=SCRIPT.read_text(encoding="utf-8").strip()
    wav=IN/"VOCE.wav"
    assert sha(wav)==EXPECTED_WAV, "Voice bytes DIFFER: do not reuse"
    assert hashlib.sha256(text.encode()).hexdigest()==EXPECTED_SCRIPT, "Script differs"
    data,sr=sf.read(wav,dtype="float32")
    assert sr==24000 and data.ndim==1 and np.isfinite(data).all()
    secs=len(data)/sr
    old=voice._cached_audio(text,IN)
    assert old is not None and old[1].get("profile")==voice.voice_profile(), "Unproven Gacrux cache"
    phrases=voice.sentences(text)
    timings=voice.align(phrases,wav,secs)
    align=json.loads((IN/"ALLINEAMENTO_VOCE.json").read_text())
    print("ASR_METHOD",align.get("method"),"matched",align.get("matched_fraction"))
    if align.get("method")!="asr_with_interpolation" or (align.get("matched_fraction") or 0)<.38:
        raise RuntimeError("Real Gacrux WAV preserved; ASR not reliable; NOT claiming synced video")
    assert voice._valid_timing(timings,phrases,secs)
    voice._save_voice_cache(text,IN,timings)
    beats=[]
    i=0
    for j,paragraph in enumerate(text.split("\n\n")):
        n=len(voice.sentences(paragraph))
        assert n>0
        beats.append({"beat":j+1,"from":round(float(timings[i][1]),3),
                      "to":round(float(timings[i+n-1][2]),3),
                      "source_excerpt":paragraph[:96]})
        i+=n
    assert i==len(timings) and len(beats)==10
    report={"schema":"artvision-gacrux-real-asr-sync-v66","status":"verified_asr_with_interpolation",
            "script_sha256":EXPECTED_SCRIPT,"wav_sha256":EXPECTED_WAV,
            "voice_model":"gemini-3.8-flash-tts","voice":"Gacrux",
            "same_wav_for_variants":["critico_standard","critico_museum"],
            "duration_seconds":secs,"num_sentences":len(timings),
            "matched_fraction":align["matched_fraction"],
            "beats":beats,"full_speed_listening":"needs_review",
            "v25_approval":False,"new_api_calls":0}
    (IN/"GACRUX_SYNC_V66.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(report,ensure_ascii=False))
if __name__=="__main__":main()
