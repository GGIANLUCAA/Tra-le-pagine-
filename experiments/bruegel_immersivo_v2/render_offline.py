#!/usr/bin/env python3
"""Bruegel immersive social art critic, real MP4 using offline Italian voice.
Reuses authenticated image and authentic painting-only shots; no cloud TTS.
"""
import hashlib,json,math,os,shutil,sys,zipfile
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
from PIL import Image
import render as r
from render import BEATS,BUILD,DEST,OUTPUT,W,H,FPS,sha,run

def main():
 imagepath,url,pixels=r.download_original()
 image=Image.open(imagepath).convert("RGB")
 r.cover(image).save(DEST/"COPERTINA.jpg",quality=94,optimize=True)
 script="\n\n".join(x["spoken"] for x in BEATS)
 (DEST/"COPIONE_ITALIANO.txt").write_text(script,encoding="utf-8")
 meta=json.loads((BUILD/"VOICE_CHAPTER_RANGES.json").read_text())
 assert meta["voice"]=="Supertonic 3 M3" and len(meta["chapters"])==len(BEATS)
 voice,sr=sf.read(BUILD/"VOCE.wav",dtype="float32")
 assert sr==44100 and voice.ndim==1 and voice.size>sr*50 and np.isfinite(voice).all()
 voice=resample_poly(voice,80,147).astype(np.float32)
 assert voice.size>24000*70,voice.size/24000
 wav=DEST/"VOCE_ITALIANA_NATURALE.wav"
 sf.write(wav,voice,24000)
 # Internal encoder expects this path, but no Gacrux claim is made in public deliverables.
 shutil.copy2(wav,DEST/"VOCE_GACRUX.wav")
 durations=meta["chapters"]
 assert 70<float(len(voice))/24000<180
 assert abs(float(durations[-1][1])-len(voice)/24000)<1.0
 spans=[]
 timed=[]
 for b,(a,z) in zip(BEATS,durations):
  a,z=float(a),float(z)
  assert z>a>=0
  spans.append((a,z))
  phrases=r.gemini_voice.sentences(b["spoken"])
  count=[max(1,len(r.gemini_voice.tokens(p))) for p in phrases]
  cur=a;total=sum(count)
  for i,(p,n) in enumerate(zip(phrases,count)):
   end=z if i==len(phrases)-1 else cur+(z-a)*n/total
   timed.append((p,cur,end));cur=end
 r.make_srt(timed)
 entries=r.make_frames(image,BEATS)
 segments=r.videos_for_shots(entries,spans)
 final_duration=r.finish(segments,len(voice)/24000)
 (DEST/"CREDITI_E_FONTI.txt").write_text(
 "The Fight Between Carnival and Lent, Pieter Bruegel the Elder (1559), oil on panel, "
 "118 x 164.5 cm, Kunsthistorisches Museum Vienna, GG 1016.\n"
 "Research: https://bruegel.at/en/carnival-vs-lent/\n"
 "Authentic source photo (Public Domain Mark): https://commons.wikimedia.org/wiki/File:The_Fight_Between_Carnival_and_Lent.jpg\n"
 "Actual original-image URL: "+url+"\n"
 "Voice: Supertonic 3 open weight, male Italian M3, offline synthesis, no paid API; "
 "narration chapter durations measured directly. Sentence timings are approximate.\n"
 "Music: original synthesized soundtrack built locally. "
 "No synthetic additions to the historic painting; all detail shots are original source crops.\n"
 "Unpublished experimental art-critic pilot. No official historic museum installation is depicted.\n",encoding="utf-8")
 (DEST/"DESCRIZIONE_SOCIAL_IT.txt").write_text(
 "Una piazza delle Fiandre, una festa, un duello e un dettaglio che cambia tutto. "
 "Nel 1559 Bruegel non dipinge solo Carnevale e Quaresima: guarda dentro un'intera società. "
 "Segui la voce, esplora il quadro, scopri perché questo capolavoro è ancora attuale.\n\n"
 "The Fight Between Carnival and Lent · Pieter Bruegel il Vecchio · 1559 · Kunsthistorisches Museum.\n"
 "#Bruegel #StoriaDellArte #CriticaDArte #Rinascimento\n",encoding="utf-8")
 info={"status":"RENDERED_REAL_MP4_FFMPEG_FULL_DECODE_PASS_ARTISTIC_REVIEW_PENDING","video":OUTPUT.name,
 "sha256":sha(OUTPUT),"bytes":OUTPUT.stat().st_size,"duration_seconds":round(final_duration,3),
 "resolution":[W,H],"frames":len(segments),"source_sha256":sha(imagepath),"source_pixels":list(pixels),
 "voice_engine":"Supertonic 3 Italian M3 open weights","voice_sha256":sha(wav),
 "narration_duration":round(len(voice)/24000,3),"chapter_sync":"measured audio-chapter boundaries",
 "sentence_sync":"interpolated, review before publication","music":"original additive composition",
 "full_decode":"PASS","artistically_approved":False,"published":False,"cost_api_paid":0}
 (DEST/"VERIFICA_QA.json").write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding="utf-8")
 out=DEST/"BRUEGEL_1559_CRITICO_IMMERSIVO_V2_CONSEGNA.zip"
 with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
  for name in [OUTPUT.name,wav.name,"COPERTINA.jpg","COPIONE_ITALIANO.txt",
               "DESCRIZIONE_SOCIAL_IT.txt","CREDITI_E_FONTI.txt",
               "SOTTOTITOLI_OPZIONALI_IT.srt","VERIFICA_QA.json"]:
   z.write(DEST/name,arcname=name)
 with zipfile.ZipFile(out) as z:
  assert z.testzip() is None
 print("OFFLINE VOICE VIDEO DELIVERED",json.dumps(info,ensure_ascii=False),flush=True)

if __name__=="__main__":main()
