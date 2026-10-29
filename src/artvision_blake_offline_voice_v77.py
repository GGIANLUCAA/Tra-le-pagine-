#!/usr/bin/env python3
"""Experimental no-API Italian voice and Blender-free ArtVision Blake Critico drafts.

Does not replace the approved Google Gacrux voice or qualify as Gold Master.
Runs on a standard public-repo GitHub runner at no API costs. Downloads only
Apache 2.0 Kokoro weights and Brooklyn/MacLeod assets; no API secrets.
"""
import hashlib
import json
import os
import sys
import shutil
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import artvision_blake_render_v74 as engine

VOICE="im_nicola"
ENGINE="Kokoro-82M"
MODEL_SOURCE="https://huggingface.co/hexgrad/Kokoro-82M"
SAMPLE_RATE=24000
OUT=ROOT/"output/artvision-blake-free-voice-v77"

def sha256(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for part in iter(lambda: f.read(2**20),b""):h.update(part)
    return h.hexdigest()

def synthesize():
    from kokoro import KPipeline
    source=engine.SCRIPT.read_text(encoding="utf-8").strip()
    paragraphs=[p.strip() for p in source.split("\n\n") if p.strip()]
    if len(paragraphs)!=7 or not 250<=len(source.split())<=320:
        raise ValueError("Exact compact V73 source script expected")
    if os.getenv("GEMINI_API_KEY") or os.getenv("VIDU_API_KEY"):
        # Do not send, use or print any API keys in this workflow.
        raise RuntimeError("Offline TTS job must not carry commercial API secrets")
    print("OFFLINE_TTS_LOADING: Kokoro Italian male, no API calls",flush=True)
    import torch
    torch.set_num_threads(2)
    pipeline=KPipeline(lang_code="i",repo_id="hexgrad/Kokoro-82M")
    pieces=[]
    per_paragraph=[]
    for i,p in enumerate(paragraphs):
        chunklist=[]
        for j,(graphemes,phonemes,audio) in enumerate(
            pipeline(p,voice=VOICE,speed=.98,split_pattern=r"\n+")
        ):
            x=np.asarray(audio,dtype=np.float32).reshape(-1)
            if x.size<1000 or not np.all(np.isfinite(x)):
                raise ValueError("TTS returned empty or invalid audio")
            chunklist.append(x)
        if not chunklist:
            raise ValueError("No audible chunks for paragraph "+str(i+1))
        pieces.extend(chunklist)
        if i<len(paragraphs)-1:
            pieces.append(np.zeros(int(.40*SAMPLE_RATE),dtype=np.float32))
        per_paragraph.append({"paragraph":i+1,"text":p,"output_seconds":round(sum(len(x) for x in chunklist)/SAMPLE_RATE,3)})
        print("OFFLINE_TTS_PARAGRAPH",i+1,"of",len(paragraphs),flush=True)
    data=np.concatenate(pieces)
    peak=float(np.max(np.abs(data)))
    if peak<.04 or len(data)/SAMPLE_RATE<50:
        raise ValueError("Voice too short or silent")
    if peak>.94:
        data=data*(.94/peak)
    OUT.mkdir(parents=True,exist_ok=True)
    path=OUT/"KOKORO_NICOLA_BLAKE_V77.wav"
    sf.write(path,data,SAMPLE_RATE,subtype="PCM_16")
    sf.write(OUT/"ASCOLTA_NICOLA_PRIMI_22S.wav",data[:22*SAMPLE_RATE],SAMPLE_RATE,subtype="PCM_16")
    report={"schema":"artvision-offline-italian-voice-v77","artwork":"William Blake - Brooklyn 15.368",
            "model":ENGINE,"model_repository":MODEL_SOURCE,"model_license":"Apache-2.0",
            "voice":VOICE,"language":"it-IT",
            "is_gacrux":False,"replaces_gacrux":False,"suitable_for_final_without_owner_quality_approval":False,
            "google_api_calls":0,"paid_service_calls":0,
            "source_script_sha256":hashlib.sha256(source.encode()).hexdigest(),
            "wav_sha256":sha256(path),"wav_seconds":round(len(data)/SAMPLE_RATE,3),
            "wav_peak_normalized":round(float(np.max(np.abs(data))),4),
            "voice_asset":str(path.relative_to(ROOT)),
            "paragraphs":per_paragraph}
    engine.write_json(OUT/"VOICE_V77_PROVENANCE.json",report)
    print("OFFLINE_VOICE_PRODUCED",json.dumps({k:report[k] for k in ("voice","is_gacrux","google_api_calls","wav_seconds","wav_sha256")}),flush=True)
    return path,report

def run():
    # ISOLATION: no overwrite of the original 2 Cinema V76 or official pilots.
    engine.OUT=OUT
    artfile,music,source=engine.acquire()
    voice,report=synthesize()
    art=engine.Image.open(artfile).convert("RGB")
    room=engine.visual.room()
    results={}
    label="Kokoro Nicola (offline Italian trial, not Gacrux)"
    for variant in ("critico_standard","critico_museum"):
        results[variant]=engine.render_one(variant,art,room,music,voice,voice_provider_label=label)
    a,b=results["critico_standard"],results["critico_museum"]
    if a["voice_sha256"]!=b["voice_sha256"]:
        raise ValueError("Narrated pair did not reuse the EXACT same WAV")
    if a["video_sha256"]==b["video_sha256"]:
        raise ValueError("Critico variants are not distinct")
    summary={"schema":"artvision-blake-free-voice-trial-v77",
       "status":"two_experimental_critic_videos_rendered_needs_voice_review",
       "voice":"Kokoro Italian Nicola, not Google Gacrux",
       "approved_gold_master":False,"replaces_official_critico":False,
       "google_tts_calls":0,"paid_api_calls":0,
       "critic_pair_shared_voice_sha256":a["voice_sha256"],
       "results":results}
    engine.write_json(OUT/"EXPERIMENT_V77_STATUS.json",summary)
    print("EXPERIMENT_V77_RESULT",json.dumps(summary,ensure_ascii=False),flush=True)

if __name__=="__main__":
    run()
