#!/usr/bin/env python3
"""Synthesize ONE real Google Gacrux narration for both Klimt Critico videos.

Explicit user authority: ArtVision 4x1 Klimt pilot, shared voice. No video-AI API.
A single call/cache reuse; do not retry paid generation. Preserve WAV if later
ASR fails; "estimated" timings are NOT qualified as synchronization.
"""
import hashlib,json,os,sys,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from gemini_voice import synthesize,voice_profile
from gemini_voice import _sha as sha
from gemini_voice import MODEL,VOICE
from gemini_voice import _cached_audio
import soundfile as sf
import numpy as np

OUT=ROOT/"output/klimt_gacrux_v71"
OUT.mkdir(parents=True,exist_ok=True)
SCRIPT=ROOT/"modules/artvision_critico/production_series/klimt_bacio.json"
REPORT=OUT/"VOICE_RESULT_V71.json"

def main():
    j=json.loads(SCRIPT.read_text(encoding="utf8"))
    if j.get("artwork")!="Il Bacio" or j.get("artist")!="Gustav Klimt" or len(j["beats"])!=9:
        raise ValueError("Klimt source script changed; refuse TTS")
    text="\n\n".join(b["speech"] for b in j["beats"])
    words=len(text.split())
    if words<300 or words>750:raise ValueError("Incomplete 9-beat Critico script")
    if MODEL!="gemini-3.8-flash-tts" or VOICE!="Gacrux":
        raise ValueError("Unapproved voice profile")
    report={"schema":"artvision-klimt-one-Gacrux-two-Critico-v71",
      "artist":"Gustav Klimt","title":"The Kiss",
      "script_sha256":hashlib.sha256(text.encode()).hexdigest(),
      "script_words":words,"beats":len(j["beats"]),
      "profile":voice_profile(),"same_wav_required_for":["critico_standard","critico_museum"],
      "paid_video_AI_calls":0,"number_of_new_TTS_calls_max":1,
      "TTS_charge":"not audited; user authorized use of supplied Google API",
      "video_mp4_count":0,"V25_approval":False,"social_published":False}
    (OUT/"CRITICO_SCRIPT_EXACT.txt").write_text(text+"\n",encoding="utf8")
    if not os.environ.get("GEMINI_API_KEY"):
        report.update(status="BLOCKED_GEMINI_API_KEY_MISSING",calls=0)
        REPORT.write_text(json.dumps(report,indent=2)+"\n");raise ValueError(report["status"])
    try:
        data,timed=synthesize(text,OUT)
        wav=OUT/"VOCE.wav"
        if not wav.exists():raise ValueError("No genuine WAV exists")
        a,sr=sf.read(wav,dtype="float32")
        if sr!=24000 or a.ndim!=1 or not len(a) or not np.isfinite(a).all():
            raise ValueError("Invalid Gacrux audio")
        duration=len(a)/sr
        if duration<95 or duration>470:raise ValueError("Unexpected Critico narration duration")
        alignment=json.loads((OUT/"ALLINEAMENTO_VOCE.json").read_text())
        if alignment.get("method")!="asr_with_interpolation" or (alignment.get("matched_fraction") or 0)<.38:
            report.update(status="WAV_GENUINE_ALIGNMENT_INCOMPLETE",
                          wav_sha256=sha(wav),duration_seconds=duration,
                          ASR=alignment,requires_manual_alignment=True)
        else:
            report.update(status="WAV_GACRUX_ASR_TIMED",
                          wav_sha256=sha(wav),wav_bytes=wav.stat().st_size,
                          duration_seconds=duration,
                          timed_sentence_count=len(timed),
                          ASR=alignment)
        report["voice_shared_exact_source"] = "VOCE.wav"
    except Exception as e:
        report.update(status="VOICE_JOB_FAILED_NO_AUTOMATIC_RETRY",error_type=type(e).__name__,
                      error=str(e)[:280],WAV_preserved=(OUT/"VOCE.wav").is_file(),
                      calls_max=1)
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(report,ensure_ascii=False))
    if report["status"] not in ("WAV_GACRUX_ASR_TIMED","WAV_GENUINE_ALIGNMENT_INCOMPLETE"):
        raise SystemExit(2)
if __name__=="__main__":main()
