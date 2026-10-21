#!/usr/bin/env python3
"""Isolated production watchdog: Botticelli only. Never touch any previous episode."""
from __future__ import annotations
import asyncio, json, os, signal, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from render_series_v2 import OUTROOT,PARENT,get_art,produce
from render_dali import audio_gemini,audio_edge,music_get
def timeout_handler(signum,frame):
    raise TimeoutError("Google voice synthesis exceeded 180 seconds; safeguard activated")
def main():
    cfg=json.loads((PARENT/"botticelli_venere.json").read_text(encoding="utf8"))
    out=OUTROOT/cfg["id"];out.mkdir(parents=True,exist_ok=True)
    img,source=get_art(cfg,out)
    voice=None
    if os.getenv("GEMINI_API_KEY",""):
        signal.signal(signal.SIGALRM,timeout_handler)
        try:
            signal.alarm(180)
            print("BOTTICELLI isolated Gemini voice attempt",flush=True)
            voice=audio_gemini(cfg["beats"],out)
        except Exception as e:
            print("BOTTICELLI Gemini unavailable/timeout, fallback: "+repr(e),flush=True)
        finally:
            signal.alarm(0)
    if voice is None:
        voice=asyncio.run(audio_edge(cfg["beats"],out))
    track,proof=music_get(cfg,out)
    if track is None:raise RuntimeError("No licensed music")
    produce(cfg,img,source,*voice,track,proof,out)
if __name__=="__main__":main()
