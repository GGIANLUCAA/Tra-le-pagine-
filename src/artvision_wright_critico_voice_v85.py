#!/usr/bin/env python3
"""One genuine shared Gacrux WAV for Wright 4x1. This job is run ONCE only.

No video AI calls, no API secret leakage; store the output even if ASR fails.
The two Critico variants use the exact same audio bytes, not two voice calls.
"""
import hashlib,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"output/artvision_wright_critico_v85"
SOURCE=ROOT/"modules/artvision_critico/production_series/wright_air_pump_v85.json"
sys.path.insert(0,str(ROOT/"src"))
import gemini_voice
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    j=json.loads(SOURCE.read_text(encoding="utf8"))
    beats=j["beats"]
    assert len(beats)==10 and j["artwork"]=="An Experiment on a Bird in the Air Pump"
    script="\n\n".join(x["speech"] for x in beats)
    words=len(script.split())
    if words<390 or words>700:raise RuntimeError("Script length/identity failed")
    assert gemini_voice.VOICE=="Gacrux" and gemini_voice.MODEL=="gemini-3.8-flash-tts"
    (OUT/"COPIONE_ESATTO_V85.txt").write_text(script,encoding="utf8")
    report={"title":j["artwork"],"artist":j["artist"],"beats":10,"words":words,
      "script_SHA256":hashlib.sha256(script.encode()).hexdigest(),
      "model":gemini_voice.MODEL,"voice":gemini_voice.VOICE,
      "one_and_only_Google_TTS_call_allowed":True,"google_billing_cost":"unverified",
      "paid_video_AI_calls":0,"shared_by":["critico_standard","critico_museum"],
      "automatic_repeat_calls_prohibited":True,"V25_approved":False}
    if not os.environ.get("GEMINI_API_KEY"):
        report["status"]="BLOCKED_SECRET_MISSING_NO_CALL"
        save(OUT/"VOICE_RESULT_V85.json",report)
        raise RuntimeError(report["status"])
    try:
        a,timing=gemini_voice.synthesize(script,OUT)
        wav=OUT/"VOCE.wav"
        if not wav.exists():raise RuntimeError("Google returned no genuine WAV")
        import soundfile as sf
        import numpy as np
        raw,sr=sf.read(wav,dtype="float32")
        if sr!=24000 or raw.ndim!=1 or not len(raw) or not np.isfinite(raw).all():
            raise RuntimeError("Gacrux WAV invalid")
        seconds=len(raw)/sr
        if not 140<=seconds<=440:raise RuntimeError("Unexpected natural duration")
        alignment=json.loads((OUT/"ALLINEAMENTO_VOCE.json").read_text())
        report.update(status="GACRUX_ONE_REAL_WAV",wav_sha256=sha(wav),wav_bytes=wav.stat().st_size,
            duration_seconds=seconds,aligned_sentences=len(timing),alignment=alignment,
            ASR_requires_human_review=True)
    except Exception as err:
        report.update(status="VOICE_ATTEMPT_FAILED_DO_NOT_AUTO_RETRY",reason=type(err).__name__+":"+str(err)[:220],
          genuine_wav_preserved=(OUT/"VOCE.wav").exists())
    save(OUT/"VOICE_RESULT_V85.json",report)
    print(json.dumps(report,ensure_ascii=False))
    if report["status"]!="GACRUX_ONE_REAL_WAV":raise SystemExit(2)
if __name__=="__main__":main()
