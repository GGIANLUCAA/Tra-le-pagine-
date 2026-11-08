#!/usr/bin/env python3
"""V3: serious cinematic art critic with stronger sourced script and Qwen3 Italian speech.
Revision remains an isolated review sample until the owner judges voice and narrative.
"""
import json,hashlib,zipfile,shutil
from pathlib import Path
import numpy as np,soundfile as sf
from scipy.signal import resample_poly
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"bruegel_immersivo_v2"))
import render as r
from storyboard import BEATS,SOURCES

r.BEATS=BEATS
OUT=Path("output/bruegel_1559_critico_qwen_v3")
STAGE=OUT/"build"
r.DEST=OUT;r.BUILD=STAGE
r.OUTPUT=OUT/"BRUEGEL_1559_CRITICO_QWEN_V3.mp4"
OUT.mkdir(parents=True,exist_ok=True)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for x in iter(lambda:f.read(1024*1024),b""):
   h.update(x)
 return h.hexdigest()

def main():
 art_path,url,pixels=r.download_original()
 image=r.Image.open(art_path).convert("RGB")
 r.cover(image).save(OUT/"COPERTINA.jpg",quality=93)
 voice_meta=json.loads((STAGE/"chapters.json").read_text())
 assert voice_meta["model"]=="Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice"
 assert len(voice_meta["files"])==len(BEATS)
 sr=None;pieces=[];spans=[];timed=[];elapsed=0.0
 from render import gemini_voice
 for i,(beat,record) in enumerate(zip(BEATS,voice_meta["files"])):
  wav=STAGE/record["file"]
  data,rate=sf.read(wav,dtype="float32")
  assert data.ndim==1 and len(data)>rate*5
  if sr is None:
   sr=rate
   start_silence=np.zeros(int(sr*.15),dtype=np.float32)
   pieces.append(start_silence);elapsed+=len(start_silence)/sr
  assert rate==sr
  a=elapsed
  # Preserve actual chapter edges, not estimated total word timings.
  pieces.append(data);elapsed+=len(data)/sr
  padding=np.zeros(int(sr*.24),dtype=np.float32)
  pieces.append(padding);elapsed+=len(padding)/sr
  z=elapsed;spans.append((a,z))
  sentences=gemini_voice.sentences(beat["spoken"])
  tokens=[max(1,len(gemini_voice.tokens(q))) for q in sentences]
  count=sum(tokens);now=a
  for j,(sentence,num) in enumerate(zip(sentences,tokens)):
   finish=z if j==len(sentences)-1 else now+(z-a)*(num/count)
   timed.append((sentence,now,finish));now=finish
 audio=np.concatenate(pieces)
 assert 70<=len(audio)/sr<=155,(len(audio)/sr,[(round(a,1),round(z,1)) for a,z in spans])
 sf.write(OUT/"VOCE_QWEN_ITALIANO.wav",audio,sr)
 # Existing muxer uses a legacy filename internally; ship correctly labelled source.
 shutil.copy2(OUT/"VOCE_QWEN_ITALIANO.wav",OUT/"VOCE_GACRUX.wav")
 r.make_srt(timed)
 shots=r.make_frames(image,BEATS)
 segments=r.videos_for_shots(shots,spans)
 duration=r.finish(segments,len(audio)/sr)
 script="\n\n".join(b["spoken"] for b in BEATS)
 (OUT/"COPIONE_RIVISTO.txt").write_text(script,encoding="utf-8")
 (OUT/"FONTI_E_LICENZE.txt").write_text(
  "Pieter Bruegel the Elder, The Fight Between Carnival and Lent, 1559, "
  "Kunsthistorisches Museum, Vienna, GG 1016. Original public-domain image, "+
  "Wikimedia Commons: https://commons.wikimedia.org/wiki/File:The_Fight_Between_Carnival_and_Lent.jpg\n"
  "Research:\n"+"\n".join(SOURCES)+"\nVoice: open-source Qwen3 TTS 0.6B CustomVoice, Ryan, Italian language. "
  "Voice is AI-generated and is not passed off as a human actor.\n"
  "Music: original generated atmospheric score. Camera only moves over genuine painting pixels, not animated reconstructions.\n"
  "The artistic interpretation of charity, sincerity and appearance is explicitly a critical reading.\n",encoding="utf-8")
 (OUT/"SOCIAL_IT.txt").write_text(
  "Un dettaglio vicino alla chiesa cambia il significato dell'intero quadro. "
  "Pieter Bruegel, 1559: una piazza, il Carnevale, la Quaresima e il teatro delle apparenze. "
  "Guarda chi entra, chi esce e cosa ci svela una torcia accesa in pieno giorno.\n"
  "#Bruegel #Arte #StoriaDellArte #CriticaDArte\n",encoding="utf-8")
 m={"version":"v3_immersive_rewrite","status":"review_not_approved",
    "video":r.OUTPUT.name,"bytes":r.OUTPUT.stat().st_size,"sha256":sha(r.OUTPUT),
    "duration_seconds":round(duration,2),"resolution":[r.W,r.H],"shot_count":len(segments),
    "image_source":url,"image_sha256":sha(art_path),"image_pixels":list(pixels),
    "voice_model":voice_meta["model"],"voice_speaker":voice_meta["speaker"],"voice_seconds":round(len(audio)/sr,2),
    "actual_chapter_boundaries":spans,"sentence_alignment":"interpolated_not_verified",
    "full_ffmpeg_decode":"PASS","published":False,"human_approved":False,
    "no_publication_or_main_branch_changes":True}
 (OUT/"QA_V3.json").write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding="utf-8")
 with zipfile.ZipFile(OUT/"BRUEGEL_CRITICO_V3_COMPLETO.zip","w",compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
  for name in [r.OUTPUT.name,"VOCE_QWEN_ITALIANO.wav","COPERTINA.jpg","COPIONE_RIVISTO.txt",
               "FONTI_E_LICENZE.txt","SOCIAL_IT.txt","SOTTOTITOLI_OPZIONALI_IT.srt","QA_V3.json"]:
   z.write(OUT/name,arcname=name)
 with zipfile.ZipFile(OUT/"BRUEGEL_CRITICO_V3_COMPLETO.zip") as z:
  assert z.testzip() is None
 print("V3_FILM_RENDERED_AND_VERIFIED",json.dumps(m,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
