#!/usr/bin/env python3
"""V79: re-edit ONLY Blake Critico Museum from existing, SHA-pinned free WAV.

No synthesis, no Google or Vidu credentials, no modification to original
ArtVision 4x1 masters, no new painting, no money-spending API calls.
"""
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import artvision_blake_render_v74 as engine
import artvision_blake_voice_sync_v78 as sync

OUT=ROOT/"output/artvision-blake-museum-v79"
STAGING=ROOT/".staging/v78_voice"
PINNED_WAV_SHA256="bf13fb1a71935bb6aad0f9b3f91339d6a825d2d5b508374b8a8b7f3e114c602b"

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()

def main():
    voice=STAGING/"KOKORO_NICOLA_BLAKE_V77.wav"
    provenance=STAGING/"VOICE_V77_PROVENANCE.json"
    if not voice.is_file() or sha(voice)!=PINNED_WAV_SHA256:
        raise RuntimeError("Pinned original Italian WAV missing or mismatched; no re-synthesis")
    v=json.loads(provenance.read_text(encoding="utf-8"))
    if v.get("wav_sha256")!=PINNED_WAV_SHA256 or v.get("google_api_calls")!=0:
        raise RuntimeError("Free-voice provenance not verified")
    starts=sync.from_voice_report(v)
    engine.OUT=OUT
    artwork,music,source=engine.acquire()
    art=engine.Image.open(artwork).convert("RGB")
    room=engine.visual.room()
    original=engine.visual.museum_frame
    engine.visual.museum_frame=lambda art,room,t,duration,critic=False: (
        sync.critico_museum(art,room,t,duration,starts) if critic
        else original(art,room,t,duration,critic=critic)
    )
    state=engine.render_one("critico_museum",art,room,music,voice,
              voice_provider_label="Kokoro Nicola (offline Italian trial, not Gacrux)")
    state.update(version="V79",reuse_exact_v78_wav=True,
        source_voice_sha256=PINNED_WAV_SHA256,tts_calls=0,video_ai_calls=0,
        frame_limited_to_exterior_shot=True,subject_frame_review="pending_human")
    engine.write_json(OUT/"V79_EDITED_CRITICO_MUSEUM_STATE.json",state)
    print("MUSEUM_V79_RENDER_VERIFIED",json.dumps(state,ensure_ascii=False),flush=True)

if __name__=="__main__":main()
