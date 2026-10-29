#!/usr/bin/env python3
"""One authorized Socrates Gacrux synthesis for two existing Critico variants.

User explicitly authorized the existing Gemini API for THIS Socrates narration
on 2026-10-29. Never calls a video AI service; never publishes or auto-approves.
Any unknown billing for this single TTS call is NOT claimed free.
"""
from pathlib import Path
import hashlib
import json
import os
import sys
import traceback
import numpy as np
import soundfile as sf

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import gemini_voice as voice

SCRIPT=ROOT/"docs/productions/2026-10-29-socrates-critico-master-v60/COPIONE_GACRUX_V62.txt"
EXPECTED_HASH="c85c4017bec6efd0a75e46ee62b83ed4aeff14e6018e5f66f911b4fd941a0828"
OUT=ROOT/"output/artvision-socrates-authorized-gacrux-v65"
OUT.mkdir(parents=True,exist_ok=True)
REPORT=OUT/"GACRUX_REAL_RESULT_V65.json"

def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for z in iter(lambda:f.read(1024*1024),b""):h.update(z)
    return h.hexdigest()

def write(r):
    REPORT.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf8")

def main():
    text=SCRIPT.read_text(encoding="utf8").strip()
    r={"schema":"artvision-gacrux-one-authorized-call-v65",
       "artwork":"The Death of Socrates","voice":"Gacrux",
       "model":"gemini-3.8-flash-tts","script_sha256":hashlib.sha256(text.encode()).hexdigest(),
       "authorized_scope":"One Socrates full-critique Gacrux recording; reuse IDENTICAL WAV for Standard and Museum",
       "source":"User explicit permission 2026-10-29; no video AI spend authorized",
       "charged_amount":"unknown; no claim of free tier",
       "video_mp4_rendered":False,"v25_approved":False,"published":False}
    if r["script_sha256"]!=EXPECTED_HASH or len(text.split())!=366 or len(text.split("\n\n"))!=10:
        raise ValueError("Original exact script changed; abort without network call")
    if os.getenv("SOCRATES_GACRUX_ONE_CALL_USER_AUTHORIZED","")!="true":
        raise ValueError("Explicit voice-only consent switch missing")
    if voice.MODEL!="gemini-3.8-flash-tts" or voice.VOICE!="Gacrux":
        raise ValueError("Exact requested Google voice/model not configured")
    if not os.environ.get("GEMINI_API_KEY"):
        r.update(status="blocked_missing_existing_secret",api_calls=0)
        write(r);return
    try:
        # Called at most once; local verified cache reuse does not invoke API.
        data,timed=voice.synthesize(text,OUT)
        path=OUT/"VOCE.wav"
        if not path.is_file():raise ValueError("Voice call returned no WAV")
        audio,sr=sf.read(path,always_2d=False)
        length=len(audio)/sr
        if sr!=24000 or audio.ndim!=1 or not np.all(np.isfinite(audio)):
            raise ValueError("Voice waveform invalid")
        if length<85 or length>360 or float(np.max(abs(audio)))<0.03:
            raise ValueError("Voice audio unexpectedly silent or wrong length")
        alignment=json.loads((OUT/"ALLINEAMENTO_VOCE.json").read_text())
        r.update(status="VOICE_GACRUX_WAV_REAL",
                 api_calls_max=1,wav_sha256=sha(path),
                 wav_bytes=path.stat().st_size,duration_seconds=length,
                 peak=float(np.max(abs(audio))),
                 timed_sentence_count=len(timed),
                 alignment=alignment,
                 waveform="actual_24000Hz_mono",
                 cache_sha256=sha(OUT/"VOICE_CACHE_V13.json"),
                 needs_human_normal_speed_listening=True)
    except Exception as exc:
        r.update(status="VOICE_TTS_ATTEMPT_FAILED_NO_AUTO_RETRY",
                 api_calls_max=1,error_type=type(exc).__name__,error=str(exc)[:500],
                 wav_preserved=(OUT/"VOCE.wav").is_file())
    write(r)
    print(json.dumps(r,ensure_ascii=False))
if __name__=="__main__":
    main()
