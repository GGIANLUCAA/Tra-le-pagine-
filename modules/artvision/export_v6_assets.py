#!/usr/bin/env python3
"""Temporary legitimate asset bundle for professional V6 art-direction work.
Only museum public-domain/CC0 data and CC BY licensed recording, NEVER referenced social clips.
"""
from pathlib import Path
import json, shutil
from artvision import collect, download_pictures
from universal_atelier_v5 import promote_museum_sources, TRACKS
from atelier_v4 import audio_download

base=Path("output/artvision-assets")
base.mkdir(parents=True,exist_ok=True)
works,errs=collect("Vincent van Gogh",limit=48)
if len(works)<20:raise RuntimeError("Too few licensed authentic artworks for curated V6")
photos,failures=download_pictures(works,base/"original_images",max_works=26)
promoted=promote_museum_sources(photos)
if len(photos)<18:raise RuntimeError("Insufficient high-quality authorized photos for film")
track=TRACKS["dreams_become_real"]
audio,music_proof=audio_download(track,base,150)
audio.rename(base/"licensed_piano_music.mp3")
music_proof["note"]="Original copyrighted recording, reused under CC BY 4.0 with full public caption attribution"
(base/"music_rights.json").write_text(json.dumps(music_proof,ensure_ascii=False,indent=2),encoding="utf-8")
(base/"artworks.json").write_text(json.dumps({"artist":"Vincent van Gogh",
"metadata":photos,"source_errors":errs,"download_errors":failures,
"print_master_upgrades":promoted,"publication_approved":False},ensure_ascii=False,indent=2),encoding="utf-8")
print("V6 ASSETS READY",len(photos),"museum images, real licensed music, metadata preserved",flush=True)
