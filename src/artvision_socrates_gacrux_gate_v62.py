#!/usr/bin/env python3
"""Socrates ArtVision Critico V62: one genuine Gacrux recording, no paid fallback.

Never generate without a verified FREE-tier AND verified billing-disabled project.
A GEMINI_API_KEY alone is NEVER permission. Cache must match exact full script.
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"docs/productions/2026-10-29-socrates-critico-master-v60/COPIONE_GACRUX_V62.txt"
EXPECTED_MODEL="gemini-3.8-flash-tts"
EXPECTED_VOICE="Gacrux"

def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def save(path,result):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    return result

def validate_script():
    text=SCRIPT.read_text(encoding="utf8").strip()
    if len(text.split())!=366 or len(text.split("\n\n"))!=10:
        raise ValueError("Exact 366-word/10-beat Socrates master missing; refuse alternate text")
    return text

def validate_cache(text,voice_dir):
    sys.path.insert(0,str(ROOT/"src"))
    import gemini_voice as voice
    voice_dir=Path(voice_dir)
    cached=voice._cached_audio(text,voice_dir)
    if cached is None:return None
    data,entry=cached
    d=len(data)/voice.SAMPLE_RATE
    if voice.MODEL!=EXPECTED_MODEL or voice.VOICE!=EXPECTED_VOICE:
        raise ValueError("Provider model/voice changed; halt")
    if entry.get("profile")!=voice.voice_profile():
        raise ValueError("Voice model profile mismatch")
    timed=entry.get("timed")
    if not voice._valid_timing(timed,voice.sentences(text),d):
        raise ValueError("Timed sentences missing or mismatched")
    alignment=entry.get("alignment",{})
    if alignment.get("method") not in ("asr_with_interpolation","recovered_artifact_sentence_timing"):
        raise ValueError("Estimated timing alone is not verified sync")
    if alignment.get("method")=="asr_with_interpolation" and (alignment.get("matched_fraction") or 0)<.38:
        raise ValueError("ASR match quality below threshold")
    return {"wav_sha256":sha(voice_dir/"VOCE.wav"),"duration_seconds":d,
            "profile":voice.voice_profile(),"cache_key":voice.cache_key(text),
            "timed_sentence_count":len(timed),"alignment":alignment,
            "wave_file":str(voice_dir/"VOCE.wav")}

def run(output,cache):
    text=validate_script()
    result={"schema":"artvision-socrates-gacrux-v62","artwork":"The Death of Socrates",
            "slots":["critico_standard","critico_museum"],
            "script_sha256":hashlib.sha256(text.encode()).hexdigest(),
            "same_recording_required_for_both":True,
            "external_video_paid_calls":0,"social_publication":False,
            "v25_approval":False}
    try:
        cached=validate_cache(text,cache)
    except (ValueError,OSError,KeyError) as ex:
        cached=None
        result["rejected_cache_reason"]=str(ex)[:180]
    if cached is not None:
        result.update(status="VOICE_GACRUX_CACHED_EXACT_VERIFIED",paid_tts_calls=0,voice=cached)
        return save(output,result)
    free=os.environ.get("GEMINI_TTS_FREE_QUOTA_CONFIRMED","").lower()=="true"
    no_billing=os.environ.get("GEMINI_TTS_PROJECT_BILLING_DISABLED_CONFIRMED","").lower()=="true"
    if not (free and no_billing):
        result.update(status="blocked_voice_free_tier_not_verified",paid_tts_calls=0,
                      blocker="Requires owner-verified free Gemini quota AND billing-disabled project. Secret alone never consents.",
                      free_quota_attested=free,billing_disabled_attested=no_billing)
        return save(output,result)
    if not os.environ.get("GEMINI_API_KEY"):
        result.update(status="blocked_voice_missing_secret",paid_tts_calls=0)
        return save(output,result)
    sys.path.insert(0,str(ROOT/"src"))
    import gemini_voice as voice
    if voice.MODEL!=EXPECTED_MODEL or voice.VOICE!=EXPECTED_VOICE:
        raise ValueError("Gacrux exact model mismatch")
    cache=Path(cache);cache.mkdir(parents=True,exist_ok=True)
    try:
        voice.synthesize(text,cache) # at most ONE synthesis; no retry on failure
    except Exception as exc:
        result.update(status="blocked_tts_attempt_failed_no_retry",attempted_once=True,
                      exception_type=type(exc).__name__,exception_message=str(exc)[:200],
                      approval_required_before_retry=True)
        return save(output,result)
    try:
        info=validate_cache(text,cache)
        if info is None:raise ValueError("No exact verified voice cache returned")
        result.update(status="VOICE_GACRUX_GENERATED_REAL",tts_calls=1,voice=info)
    except Exception as exc:
        result.update(status="blocked_voice_alignment_pending",tts_calls=1,
                      exception_type=type(exc).__name__,exception_message=str(exc)[:200],
                      note="Preserve WAV/cache, do not call Gemini again; fix actual ASR alignment.")
    return save(output,result)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    p.add_argument("--cache",required=True)
    a=p.parse_args()
    print(json.dumps(run(a.out,a.cache),ensure_ascii=False))
