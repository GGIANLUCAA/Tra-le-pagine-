#!/usr/bin/env python3
"""Böcklin third version (NG 2/80) ONE Google Gacrux narration for two Critico.
Fail closed on billing verification; never assume existing secret is free-tier.
A successful WAV is preserved; no automatic retries.
"""
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import gemini_voice

OUT=ROOT/"output/artvision_bocklin_critico_v102"
SOURCE=ROOT/"modules/artvision_critico/production_series/bocklin_isle_of_dead_1883_v100.json"

def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1048576),b""):h.update(b)
    return h.hexdigest()

def report(d):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"VOICE_RESULT_V102.json").write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(d,ensure_ascii=False))

def main():
    j=json.loads(SOURCE.read_text(encoding="utf8"))
    beats=j["critico"]["chapters"]
    assert j["work_id"]=="bocklin_isle_of_dead_1883_berlin_ng2_80" and len(beats)==9
    speech="\n\n".join(x["text"] for x in beats)
    words=len(speech.split())
    assert 160<=words<=240 and gemini_voice.VOICE=="Gacrux" and gemini_voice.MODEL=="gemini-3.8-flash-tts"
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"COPIONE_ESATTO_V102.txt").write_text(speech,encoding="utf8")
    result={"work_id":j["work_id"],"words":words,"chapters":9,"voice":"Gacrux",
            "model":gemini_voice.MODEL,"script_sha256":hashlib.sha256(speech.encode()).hexdigest(),
            "one_shared_voice_for":["critico_standard","critico_museum"],
            "no_new_paid_API_authorized":True,"project_tier_evidence":"owner_attested_free_no_billing_linked_second_account_2026-10-30","V25_Gold":False}
    # The owner's second AI Studio account was explicitly reported Free and
    # without a linked billing account on 30 Oct 2026, and GEMINI_API_KEY2 was set.
    # Workflow injects ONLY this second key and flags that attested tier. No claim
    # of an independent Google billing audit: the primary key is never used here.
    # See https://ai.google.dev/gemini-api/docs/billing
    if os.getenv("ARTVISION_GEMINI_PROJECT_BILLING_TIER")!="Free":
        result["status"]="BLOCKED_BILLING_TIER_NOT_VERIFIED_FREE_NO_TTS_CALL"
        report(result)
        return 0
    if not os.getenv("GEMINI_API_KEY"):
        result["status"]="BLOCKED_GEMINI_KEY_MISSING_NO_TTS_CALL"
        report(result)
        return 0
    try:
        data,timed=gemini_voice.synthesize(speech,OUT)
        wav=OUT/"VOCE.wav"
        alignment=json.loads((OUT/"ALLINEAMENTO_VOCE.json").read_text(encoding="utf8"))
        duration=len(data)/gemini_voice.SAMPLE_RATE
        if not wav.is_file() or not 65<=duration<=170:
            raise ValueError("WAV missing or duration beyond 65–170 seconds")
        result.update(status="ONE_SHARED_GACRUX_WAV_READY",wav_sha256=sha(wav),
                      duration_seconds=duration,alignment=alignment,
                      speech_timing_count=len(timed),human_listening_review="pending",
                      actual_billing_cost="free_tier_declared_not_invoice_verified")
    except Exception as err:
        result.update(status="VOICE_ATTEMPT_FAILED_DO_NOT_RETRY_AUTOMATICALLY",
                      error=type(err).__name__+":"+str(err)[:220],
                      wav_preserved=(OUT/"VOCE.wav").exists())
    report(result)
    if result["status"]!="ONE_SHARED_GACRUX_WAV_READY":
        return 2
    return 0

if __name__=="__main__":
    raise SystemExit(main())
