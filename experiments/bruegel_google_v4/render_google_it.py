#!/usr/bin/env python3
"""Bruegel 1559: genuine Google-origin Italian TTS, authentic-image social video.

This variant deliberately uses Google Translate's Italian speech service via gTTS,
NOT Gemini, Qwen, Microsoft Edge or Supertonic. Do not mislabel it as premium
Google Cloud Neural2 / Chirp HD. No silent replacement if Google refuses service.
No publication or old-master replacement without human review.
"""
import hashlib, json, os, sys, zipfile
from pathlib import Path

import numpy as np
import soundfile as sf
from gtts import gTTS

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"bruegel_immersivo_v2"))
sys.path.insert(0,str(HERE.parent/"bruegel_immersivo_v3"))
import render as r
from storyboard import BEATS, SOURCES

ROOT=Path("output/bruegel_google_it_v4")
BUILD=ROOT/"build"
ROOT.mkdir(parents=True, exist_ok=True); BUILD.mkdir(parents=True,exist_ok=True)

r.BEATS=BEATS
r.DEST=ROOT
r.BUILD=BUILD
r.OUTPUT=ROOT/"BRUEGEL_GOOGLE_ITALIANO_CRITICO_V4.mp4"

def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for block in iter(lambda:f.read(1048576),b""):
            h.update(block)
    return h.hexdigest()

def italian_google_voice():
    sample_rate=24000
    joined=[]
    spans=[]
    sentence_timings=[]
    total=0.0
    initial=np.zeros(round(sample_rate*0.25), dtype=np.float32)
    joined.append(initial); total+=len(initial)/sample_rate
    for i,beat in enumerate(BEATS):
        text=beat["spoken"]
        mp3=BUILD/f"GOOGLE_CHAPTER_{i:02}.mp3"
        wav=BUILD/f"GOOGLE_CHAPTER_{i:02}.wav"
        if not mp3.is_file():
            print("GOOGLE_TRANSLATE_TTS",i,"CHARS",len(text),flush=True)
            speech=gTTS(text=text,lang="it",tld="it",slow=False)
            speech.save(str(mp3))
        assert mp3.is_file() and mp3.stat().st_size>3000,("Empty Google TTS reply",i)
        # Decode actual MP3, never replace with synthetic silence on errors.
        if not wav.exists():
            r.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y","-i",mp3,
                   "-ac","1","-ar",str(sample_rate),"-c:a","pcm_s16le",wav])
        samples,sr=sf.read(wav,dtype="float32")
        assert sr==sample_rate and samples.ndim==1 and np.isfinite(samples).all()
        dur=len(samples)/sample_rate
        assert 3.0 <= dur <= 58,(i,dur)
        start=total
        joined.append(samples)
        total+=dur
        # natural breath between paragraphs, more pronounced after act breaks
        gap=np.zeros(round(sample_rate*(0.35 if i not in (0,3) else 0.47)),dtype=np.float32)
        joined.append(gap);total+=len(gap)/sample_rate
        end=total
        spans.append((start,end))
        sentences=r.gemini_voice.sentences(text)
        weights=[max(1,len(r.gemini_voice.tokens(s))) for s in sentences]
        pos=start
        for idx,(sentence,count) in enumerate(zip(sentences,weights)):
            next_pos=end if idx==len(sentences)-1 else pos+(end-start)*count/sum(weights)
            sentence_timings.append((sentence,pos,next_pos))
            pos=next_pos
        print("GOOGLE_TTS_CHAPTER_READY",i,"seconds",round(dur,2),"MP3_BYTES",mp3.stat().st_size,flush=True)
    audio=np.concatenate(joined)
    assert 65 <= total <= 175,("Unexpected voice length",total)
    sf.write(ROOT/"VOCE_GOOGLE_ITALIANO.wav",audio,sample_rate)
    # Existing renderer expects this legacy input name; never upload it as mislabeled voice.
    muxing_path=ROOT/"VOCE_GACRUX.wav"
    if muxing_path.exists():
        muxing_path.unlink()
    muxing_path.symlink_to("VOCE_GOOGLE_ITALIANO.wav")
    (ROOT/"VOICE_PROVENANCE.json").write_text(json.dumps({
        "real_provider":"Google Translate Text-to-Speech","implementation":"gTTS 2.x",
        "locale":"it","language":"it","google_product_not_used":"Google Cloud Chirp/Neural2 or Gemini",
        "is_google_cloud_premium":False,"chapters":len(spans),
        "duration_seconds":total,"wav_sha256":sha(ROOT/"VOCE_GOOGLE_ITALIANO.wav"),
        "note":"Italian Google Translate voice, actual audio supplied by Google Translate service; no premium Natural2/Chirp claim."
    },ensure_ascii=False,indent=2),encoding="utf-8")
    return audio,spans,sentence_timings

def main():
    art,url,pixels=r.download_original()
    picture=r.Image.open(art).convert("RGB")
    r.cover(picture).save(ROOT/"COPERTINA_BRUEGEL.jpg",quality=95)
    narration="\n\n".join(b["spoken"] for b in BEATS)
    (ROOT/"COPIONE_ITALIANO.txt").write_text(narration,encoding="utf-8")
    voice,spans,timed=italian_google_voice()
    r.make_srt(timed)
    clips=r.make_frames(picture,BEATS)
    print("VISUAL_SHOTS",len(clips),"GOOGLE_VOICE",round(len(voice)/24000,2),flush=True)
    segments=r.videos_for_shots(clips,spans)
    duration=r.finish(segments,len(voice)/24000)
    assert r.OUTPUT.is_file() and r.OUTPUT.stat().st_size>2500000
    (ROOT/"FONTI_E_CREDITI.txt").write_text(
        "Pieter Bruegel il Vecchio · The Fight Between Carnival and Lent (1559), "
        "Kunsthistorisches Museum, Vienna, GG 1016.\n"
        "Immagine originale di pubblico dominio, Wikimedia Commons: "
        "https://commons.wikimedia.org/wiki/File:The_Fight_Between_Carnival_and_Lent.jpg\n"
        "File originale autenticato URL: "+url+"\n"
        "Fonti: "+"\n".join(SOURCES)+"\n"
        "Voce: Google Translate Text-to-Speech via gTTS, italiano (Italia), NON Google Cloud Chirp / Gemini premium.\n"
        "Musica: composizione digitale originale.\n"
        "Zoom e movimenti sono inquadrature del dipinto realmente esistente, non animazioni di persone.\n"
        "Film in revisione artistica: non pubblicato, non approvato.\n",encoding="utf-8")
    (ROOT/"TESTO_SOCIAL.txt").write_text(
        "Nel 1559 Bruegel dipinge una piazza in cui niente è come sembra. "
        "Due rivali si sfidano. Ma la parte più interessante potrebbe essere davanti alla chiesa. "
        "Segui i dettagli di Carnevale e Quaresima.\n"
        "#Bruegel #Arte #CriticaDArte #StoriaDellArte\n",encoding="utf-8")
    manifest={
      "status":"REAL_VIDEO_DECODE_VERIFIED_ARTISTIC_REVIEW_PENDING",
      "video_file":r.OUTPUT.name,"bytes":r.OUTPUT.stat().st_size,"sha256":sha(r.OUTPUT),
      "duration_seconds":round(duration,2),"resolution":[r.W,r.H],
      "voice_provider":"Google Translate TTS via gTTS","voice_sample_rate":24000,
      "voice_file":"VOCE_GOOGLE_ITALIANO.wav","voice_sha256":sha(ROOT/"VOCE_GOOGLE_ITALIANO.wav"),
      "source_sha256":sha(art),"source_pixels":list(pixels),"shots":len(segments),
      "audio_real":True,"no_alternate_voice_fallback":True,"full_ffmpeg_decode":"PASS",
      "sentence_alignment":"interpolated within authentic chapter durations",
      "artistic_approved":False,"social_published":False,"existing_masters_modified":False,
    }
    (ROOT/"QA_GOOGLE_V4.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    packed=ROOT/"BRUEGEL_GOOGLE_ITALIANO_VIDEO_E_FONTI.zip"
    with zipfile.ZipFile(packed,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
        for name in [r.OUTPUT.name,"VOCE_GOOGLE_ITALIANO.wav","COPERTINA_BRUEGEL.jpg",
                     "COPIONE_ITALIANO.txt","SOTTOTITOLI_OPZIONALI_IT.srt","FONTI_E_CREDITI.txt",
                     "TESTO_SOCIAL.txt","VOICE_PROVENANCE.json","QA_GOOGLE_V4.json"]:
            z.write(ROOT/name,arcname=name)
    with zipfile.ZipFile(packed) as z:
        assert z.testzip() is None and r.OUTPUT.name in z.namelist()
    print("GOOGLE_ITALIAN_REAL_MP4_READY",json.dumps(manifest,ensure_ascii=False),flush=True)

if __name__=="__main__":
    main()
