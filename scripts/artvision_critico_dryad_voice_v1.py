#!/usr/bin/env python3
"""ArtVision Critico Dryad: real Italian neural/Google voice asset, no paid API.

Free Google Translate TTS through gTTS is attempted first. If Google is
unavailable, Edge Neural Italian is a strictly private editorial fallback;
the fallback's commercial rights are unverified. Stop rather than output
silence/robotic placeholder. Each BEAT is a complete thought with hard
boundaries so video shots match EXACT spoken content. Do not claim Gacrux.
"""
from __future__ import annotations
import asyncio,hashlib,json,subprocess,sys,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/"research/artvision_critico_dryad_20261113_narration.json"
OUT=ROOT/"output/artvision-critico-dryad-voice-v1"
OUT.mkdir(parents=True,exist_ok=True)

def sha(path):
 return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run(command):
 p=subprocess.run(command,capture_output=True,text=True,timeout=70)
 if p.returncode:raise RuntimeError(p.stderr[-1800:])
 return p.stdout

def audio_probe(path):
 p=run(["ffprobe","-v","error","-show_entries","format=duration,size:"
       "stream=codec_name,sample_rate,channels","-of","json",path])
 return json.loads(p)

def google_voice(beats):
 from gtts import gTTS
 for beat in beats:
  dest=OUT/f"BEAT_{beat['i']:02d}.mp3"
  last=None
  for attempt in range(2):
   try:
    gTTS(text=beat["text"],lang="it",tld="it",slow=False,
         timeout=22).save(str(dest))
    if dest.stat().st_size<700:raise RuntimeError("TTS produced empty audio")
    break
   except Exception as e:
    last=e;dest.unlink(missing_ok=True)
    print("GOOGLE_TTS_RETRY",beat["i"],type(e).__name__,str(e)[:180],flush=True)
    time.sleep(1.3*(attempt+1))
  else:raise RuntimeError("GOOGLE_TTS_FAILED_BEAT_"+str(beat["i"])) from last

async def edge_voice(beats):
 import edge_tts
 for b in beats:
  dest=OUT/f"BEAT_{b['i']:02d}.mp3"
  # Italian neural voice in the repository's old voice tests.
  for attempt in range(2):
   try:
    speech=edge_tts.Communicate(b["text"],voice="it-IT-DiegoNeural",
                               rate="-7%",pitch="-2Hz")
    await speech.save(str(dest))
    if dest.stat().st_size<700:raise RuntimeError("Edge produced empty audio")
    break
   except Exception as e:
    dest.unlink(missing_ok=True)
    print("EDGE_TTS_RETRY",b["i"],type(e).__name__,str(e)[:180],flush=True)
    if attempt==1:raise
    await asyncio.sleep(2.0)

def main():
 data=json.loads(PLAN.read_text("utf8"))
 beats=data["beats"]
 assert len(beats)==20 and [b["i"] for b in beats]==list(range(1,21))
 print("VOICE_PREFLIGHT",len(beats),sum(len(b["text"].split()) for b in beats),"words",flush=True)
 provider="Google Translate gTTS Italian (not Google Cloud/Gacrux)"
 try:
  google_voice(beats)
 except Exception as e:
  print("GOOGLE_TTS_NO_COST_UNAVAILABLE; TRY PRIVATE_EDGE_NEURAL",type(e).__name__,flush=True)
  for p in OUT.glob("BEAT_*.mp3"):p.unlink()
  asyncio.run(edge_voice(beats))
  provider="Microsoft Edge Read Aloud / it-IT-DiegoNeural PRIVATE PREVIEW ONLY; commercial rights NOT CLEARED"
 durations=[]
 report=[]
 for b in beats:
  p=OUT/f"BEAT_{b['i']:02d}.mp3"
  info=audio_probe(p)
  length=float(info["format"]["duration"])
  if not (3.1<length<36) or p.stat().st_size<1000:
   raise RuntimeError(f"Invalid synthesized speech {b['i']}: {length} seconds")
  run(["ffmpeg","-v","error","-xerror","-i",p,"-map","0:a:0","-f","null","-"])
  report.append({"i":b["i"],"label":b["label"],"text":b["text"],
   "duration_seconds":round(length,3),"file":p.name,"file_sha256":sha(p)})
  durations.append(length)
 # Each semantic beat separated by 320 milliseconds for human listening, and
 # 0.6sec for final, exact frame timestamps computed from actual PCM after conversion.
 res={"schema":"artvision-critico-dryad-real-voice-v1","voice_provider":provider,
  "audio_is_real_downloaded_neural_voice":True,"source":str(PLAN.relative_to(ROOT)),
  "narration_sha256":sha(PLAN),"beats":report,"total_raw_voice_seconds":round(sum(durations),3),
  "duration_with_deliberate_pauses_estimate_s":round(sum(durations)+len(durations)*.32,2),
  "voice_licensed_for_commercial_publication":False,
  "voice_credit_and_terms_review":"PENDING","google_cloud_paid_calls":0,
  "human_naturalness_listening_review":"PENDING","published":False}
 (OUT/"VOICE_MANIFEST.json").write_text(json.dumps(res,ensure_ascii=False,indent=2)+"\n","utf8")
 print("REAL_VOICE_SUCCESS",json.dumps({"provider":provider,"beats":len(beats),
  "seconds":res["total_raw_voice_seconds"],"source_sha256":res["narration_sha256"]}),flush=True)

if __name__=="__main__":
 main()
