#!/usr/bin/env python3
"""John Martin Critico V82 — replace ONLY overlong/unsynchronized Critico pair.
Single Gacrux WAV, 9 semantic paragraphs, scene boundaries guided by audio silences.
Two new distinct MP4, ZIP and source/QA, Cinema V81 untouched.
"""
from __future__ import annotations
import json
import sys
import math
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import artvision_martin_render_v81 as renderer
import artvision_martin_critico_visual_v82 as visual

OUTPUT=ROOT/"output/artvision-martin-wrath-critico-v82"
SCRIPT=ROOT/"docs/productions/2026-10-30-martin-wrath-v82/COPIONE_CRITICO_V82.txt"

def semantic_boundaries(text,wav):
    """Silence-guided paragraph entry estimates. Not a word-for-word ASR claim."""
    paragraphs=[p.strip() for p in text.split("\n\n") if p.strip()]
    if len(paragraphs)!=9:raise ValueError("V82 requires exactly 9 semantic paragraphs")
    data,rate=sf.read(str(wav),dtype="float32")
    if data.ndim==2:data=data.mean(axis=1)
    if rate!=24000:raise ValueError("Wrong Gacrux sample rate")
    dur=len(data)/rate
    # Speech delivery speed varies naturally; interpolate from syllables and
    # punctuation, then snap each boundary toward a real low-energy pause.
    sizes=[]
    for p in paragraphs:
        words=p.split()
        estimated=sum(max(1,sum(c in "aeiouàèéìòù" for c in w.lower())) for w in words)
        sizes.append(estimated + 2.3*p.count(".") + 1.5*p.count(":"))
    cumulative=np.cumsum(sizes)/sum(sizes)
    boundaries=[0.0]
    win=int(rate*.095)
    audio=np.asarray(data[:len(data)//win*win],dtype=np.float32)
    rms=np.sqrt(np.maximum(1e-12,np.mean(audio.reshape(-1,win)**2,axis=1)))
    # Avoid a silent gap anywhere too far from semantic estimate.
    for i in range(8):
        target=dur*float(cumulative[i])
        lo=max(boundaries[-1]+3.3,target-2.0)
        hi=min(dur-(8-i)*3.3,target+2.0)
        if hi<lo:boundary=target
        else:
            x0=int(lo/.095);x1=min(len(rms),int(hi/.095))
            region=rms[x0:x1]
            if region.size:
                q=float(np.quantile(region,.16))
                candidates=np.where(region<=q)[0]+x0
                if len(candidates):
                    # Favor the closest suitable lull, not the globally quietest syllable.
                    centers=candidates*.095+.0475
                    boundary=float(centers[np.argmin(abs(centers-target))])
                else:boundary=target
            else:boundary=target
        boundary=max(boundaries[-1]+3.3,min(dur-(8-i)*3.3,boundary))
        boundaries.append(boundary)
    boundaries.append(dur)
    return paragraphs,boundaries,{"method":"paragraph_syllable_estimates_silence_guided",
       "fully_ASR_verified":False,"semantic_sync_review_required":True,"audio_seconds":dur,
       "estimated_scene_boundaries_seconds":[round(t,3) for t in boundaries],
       "paragraphs":[{"paragraph":i+1,"spoken":p,
           "scene":visual.SCENE_EDIT[i][0][0],"start":round(boundaries[i],2),
           "end":round(boundaries[i+1],2)} for i,p in enumerate(paragraphs)]}

def main():
    # User explicitly authorizes Free Tier; workflow is responsible for providing
    # attestation and no-pay-per-call controls. No video service cost.
    renderer.OUT=OUTPUT
    renderer.DOSSIER=SCRIPT.parent
    renderer.SCRIPT=SCRIPT
    renderer.visual=visual
    OUTPUT.mkdir(parents=True,exist_ok=True)
    source,frame,music,provenance=renderer.acquire()
    voice=renderer.get_voice()
    if voice is None:
        result={"schema":"martin-critico-v82","status":"blocked_real_Gacrux_unavailable",
                "completed_mp4":0,"no_silent_critico":True,"existing_cinema_unchanged":True}
        renderer.write_json(OUTPUT/"MARTIN_CRITICO_V82_STATE.json",result)
        print("V82_GATE_FAIL_NO_AUDIO",json.dumps(result),flush=True)
        return
    script=SCRIPT.read_text(encoding="utf-8").strip()
    paragraphs,bounds,alignment=semantic_boundaries(script,voice)
    visual.assign_narrative_timing(bounds)
    renderer.write_json(OUTPUT/"MARTIN_CRITICO_V82_SEMANTIC_TIMING.json",alignment)
    art=Image.open(source).convert("RGB")
    framed=Image.open(frame).convert("RGB")
    gallery=visual.room()
    states={}
    for name in ("critico_standard","critico_museum"):
        states[name]=renderer.render_one(name,art,framed,gallery,music,voice)
    a,b=states["critico_standard"],states["critico_museum"]
    if a["voice_sha256"]!=b["voice_sha256"]:raise RuntimeError("Two Critico must share exact WAV")
    if a["video_sha256"]==b["video_sha256"]:raise RuntimeError("Two distinct variant renders required")
    status={"schema":"martin-critico-v82","status":"rendered_needs_artistic_review",
            "correction_of":"overlong V81 Critico pair","only_two_critico_rendered":True,
            "cinema_standard_and_museum_untouched":True,
            "copione_words":len(script.split()),"storyboard_semantic_beats":len(paragraphs),
            "newly_rendered_mp4":2,
            "single_shared_Gacrux_sha256":a["voice_sha256"],"variants":states,
            "manual_visual_review_required":True,"private_archive_verified":False,
            "film_gold_master":False,"new_vidu_paid_calls":0}
    renderer.write_json(OUTPUT/"MARTIN_CRITICO_V82_STATE.json",status)
    print("MARTIN_CRITICO_V82_RESULT",json.dumps(status,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
