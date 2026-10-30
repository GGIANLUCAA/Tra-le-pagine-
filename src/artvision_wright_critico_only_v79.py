#!/usr/bin/env python3
"""ArtVision Wright V79: produce ONLY missing Critico pair, no Cinema rerender.
Uses exactly one verified Google Gemini Gacrux WAV for both distinct variants.
Fail closed on billing uncertainty, without any payable TTS call.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artvision_wright_render_v78 as v
import artvision_wright_visual_v78 as visual

def main():
    out = v.OUT
    out.mkdir(parents=True, exist_ok=True)
    status = {
        "schema": "artvision-wright-critico-v79",
        "work": v.TITLE,
        "only_missing_slots": ["critico_standard", "critico_museum"],
        "existing_cinema_mp4_not_touched": True,
        "required_voice": "Google Gemini 3.8 Flash TTS Gacrux",
        "same_exact_wav_required": True,
        "payment_safety": "no API call unless free quota AND billing disabled independently confirmed",
        "two_critico_finished": False,
        "approved_master": False,
        "private_site_verified": False,
    }
    voice = v.get_voice()
    if voice is None:
        status.update(state="blocked_no_verified_free_gacrux",rendered_count=0,
                      no_silent_critico=True,no_paid_calls=True)
        v.write_json(out/"WRIGHT_V79_MISSING_CRITICO_STATE.json",status)
        print("V79_BLOCKED: real Gacrux WAV absent, independent no-cost attestation absent; 0 videos falsely released",flush=True)
        return
    artpath,music,_ = v.acquire()
    art=Image.open(artpath).convert("RGB")
    gallery=visual.room()
    result={}
    for slot in status["only_missing_slots"]:
        result[slot]=v.render_one(slot,art,gallery,music,voice)
    sha={x["voice_sha256"] for x in result.values()}
    if len(sha)!=1 or next(iter(sha))!=v.sha256(voice):
        raise RuntimeError("V79_SHARED_GACRUX_WAV_HASH_MISMATCH")
    hashes={x["video_sha256"] for x in result.values()}
    if len(hashes)!=2:
        raise RuntimeError("V79_MISSING_OR_DUPLICATE_MP4")
    status.update(state="rendered_needs_artistic_review",
                  rendered_count=2,two_critico_finished=True,
                  shared_voice_sha256=next(iter(sha)),variants=result)
    v.write_json(out/"WRIGHT_V79_MISSING_CRITICO_STATE.json",status)
    print("ARTVISION_WRIGHT_V79_CRITICO_PAIR",json.dumps(status,ensure_ascii=False),flush=True)

if __name__ == "__main__":
    main()
