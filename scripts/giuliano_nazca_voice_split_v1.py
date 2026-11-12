#!/usr/bin/env python3
"""Nazca Gacrux recovery: two short, independently preserved audio chunks.

Google 3.1 returned SAFETY/non-audio to two single long transcripts.
This first-party text is benign archaeology, so perform up to two *short*
requests, once each. No auto-retry, no paid provider fallback. Retain each
successful WAV before proceeding to avoid regenerating the first half.
"""
from pathlib import Path
import argparse,base64,hashlib,json,os,sys
import numpy as np
import soundfile as sf
from google import genai
from google.genai import types

from giuliano_nazca_voice_v1 import sha,align,write_json,SAMPLE_RATE

BRIEF=Path("giuliano/nazca/EP04_BRIEF_SHOTMAP_V1.json")
OUT=Path("output")
MODEL="gemini-3.1-flash-tts-preview"
VOICE="Gacrux"
SPLIT=13
def script():
 doc=json.loads(BRIEF.read_text())
 if doc["schema"]!="giuliano-nazca-ep04-real-director-brief-v1":
  raise ValueError("NAZCA_BRIEF_CHANGED")
 if len(doc["beats"])!=27 or not 230<=doc["word_count"]<=300:
  raise ValueError("UNEXPECTED_SCENE_COUNT_OR_LENGTH")
 return doc
def phrase_parts(doc):
 return [doc["beats"][:SPLIT],doc["beats"][SPLIT:]]
def check_split():
 doc=script()
 for i,phrases in enumerate(phrase_parts(doc),1):
  wc=sum(len(s["narration"].split()) for s in phrases)
  if not 90<=wc<=150:raise ValueError("SPLIT_WORDS_OUT_OF_RANGE "+str(wc))
  print("NAZCA_GACRUX_SHORT_PART_VALIDATED",i,"beats",len(phrases),"words",wc,flush=True)
def work_part(part):
 if os.environ.get("GIULIANO_NAZCA_TWO_SHORT_REQUESTS_ONCE")!="1":
  raise RuntimeError("ONE_SHOT_OWNER_REQUEST_NOT_VERIFIED")
 doc=script()
 phrase=phrase_parts(doc)[part-1]
 text=" ".join(s["narration"] for s in phrase)
 directory=OUT/f"GIULIANO_04_NAZCA_GACRUX_PART{part}"
 directory.mkdir(parents=True,exist_ok=True)
 audio=directory/f"PART{part}.wav"
 if audio.exists():raise RuntimeError("EXISTING_PART_WOULD_BE_OVERWRITTEN")
 key=os.environ.get("GEMINI_API_KEY","")
 if not key:raise RuntimeError("EXISTING_GEMINI_API_KEY_NOT_AVAILABLE")
 client=genai.Client(api_key=key,http_options=types.HttpOptions(api_version="v1beta"))
 try:
  proof=client.models.get(model=MODEL)
  if not proof.name.endswith(MODEL):raise RuntimeError("VOICE_MODEL_ID_MISMATCH")
  print("NAZCA_GACRUX_DOCUMENTED_TTS_PRECHECK",part,proof.name,flush=True)
  resp=client.models.generate_content(
   model=MODEL,
   contents=("Sintesi vocale italiana. Leggi il seguente testo di documentario "
             "archeologico esattamente come scritto, senza commenti, "
             "con tono naturale, sobrio e curioso.\n"
             "TESTO DA NARRARE:\n"+text),
   config=types.GenerateContentConfig(
    response_modalities=["AUDIO"],max_output_tokens=16384,
    speech_config=types.SpeechConfig(voice_config=types.VoiceConfig(
     prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE)))))
  candidate=resp.candidates[0] if resp.candidates else None
  parts=(candidate.content.parts if candidate and candidate.content else None) or []
  audio_parts=[p.inline_data for p in parts if getattr(p,"inline_data",None)
               and getattr(p.inline_data,"data",None)]
  if not audio_parts:
   usage=resp.usage_metadata
   diag={"part":part,"status":"NO_AUDIO","finish_reason":str(getattr(candidate,"finish_reason",None)),
         "candidate_tokens":getattr(usage,"candidates_token_count",None),
         "prompt_tokens":getattr(usage,"prompt_token_count",None),
         "no_auto_retry":True}
   write_json(directory/"GOOGLE_NONAUDIO.json",diag)
   print("NAZCA_GOOGLE_PART_FAIL_CLOSED",diag,flush=True)
   raise RuntimeError("GOOGLE_TTS_SHORT_PART_NO_AUDIO, stop and review diagnostic")
  b=audio_parts[0].data
  if isinstance(b,str):b=base64.b64decode(b)
  if not b or len(b)%2:raise RuntimeError("TTS_INVALID_PCM")
  wav=np.frombuffer(b,dtype="<i2").astype(np.float32)/32768.0
  duration=len(wav)/SAMPLE_RATE
  if not 30<=duration<=105:raise RuntimeError("TTS_PART_DURATION_OUTSIDE_EXPECTATION")
  sf.write(audio,wav,SAMPLE_RATE,subtype="PCM_16")
  meta={"schema":"nazca-split-Gacrux-voice-chunk-v1","part":part,
        "model":MODEL,"voice":VOICE,"duration_seconds":round(duration,4),
        "wav_sha256":sha(audio),"script_sha256":sha(BRIEF),
        "text_sha256":hashlib.sha256(text.encode()).hexdigest(),
        "narrated_beats":[s["id"] for s in phrase],
        "one_api_call_no_retry":True}
  write_json(directory/f"PART{part}_PROOF.json",meta)
  print("NAZCA_GACRUX_SHORT_REAL_PART_SUCCESS",part,duration,meta["wav_sha256"],flush=True)
 finally:client.close()
def assemble():
 doc=script()
 from pathlib import Path
 from giuliano_nazca_voice_v1 import tokens
 total=[]
 audios=[]
 for idx,beats in enumerate(phrase_parts(doc),1):
  source=OUT/f"GIULIANO_04_NAZCA_GACRUX_PART{idx}"
  info=json.loads((source/f"PART{idx}_PROOF.json").read_text())
  p=source/f"PART{idx}.wav"
  expected=" ".join(x["narration"] for x in beats)
  assert info["script_sha256"]==sha(BRIEF)
  assert info["text_sha256"]==hashlib.sha256(expected.encode()).hexdigest()
  assert info["wav_sha256"]==sha(p) and info["voice"]==VOICE
  data,sr=sf.read(p,dtype="float32")
  assert sr==SAMPLE_RATE and data.ndim==1 and data.size>50000
  audios.append(data)
  total.append(info)
 gap=np.zeros(int(SAMPLE_RATE*.24),dtype=np.float32)
 joined=np.concatenate([audios[0],gap,audios[1]])
 dur=len(joined)/SAMPLE_RATE
 if not 80<=dur<=165:raise RuntimeError("COMBINED_SOCIAL_AUDIO_LENGTH_OUTSIDE_POLICY")
 target=OUT/"GIULIANO_04_NAZCA_VOICE"
 target.mkdir(exist_ok=True)
 wav=target/"VOCE.wav"
 sf.write(wav,joined,SAMPLE_RATE,subtype="PCM_16")
 full_text=" ".join(b["narration"] for b in doc["beats"])
 (target/"NARRATION_TEXT.txt").write_text(full_text+"\n",encoding="utf-8")
 prof={"schema":"nazca-gacrux-voice-v1","model":MODEL,"voice":VOICE,
       "api_version":"v1beta","transport":"models.generate_content",
       "sample_rate":SAMPLE_RATE,"duration_seconds":dur,
       "wav_sha256":sha(wav),"script_sha256":sha(BRIEF),
       "google_tts_generation_calls":2,"parts":total,
       "stitched_with_silence_seconds":0.24,"requires_listening_review":True}
 write_json(target/"VOICE_PROFILE.json",prof)
 print("NAZCA_TWO_REAL_GACRUX_PARTS_JOINED",round(dur,3),sha(wav),flush=True)
 timing=align([x["narration"] for x in doc["beats"]],wav,dur)
 write_json(target/"VOICE_TIMING.json",timing)
 print("NAZCA_REAL_ASR_ALIGNMENT",timing["word_match_fraction"],"beats",len(timing["scenes"]),flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument("--part",type=int,choices=(1,2))
 p.add_argument("--assemble",action="store_true");p.add_argument("--validate-only",action="store_true")
 a=p.parse_args();check_split()
 if a.validate_only:return
 if a.assemble:assemble();return
 if a.part:work_part(a.part);return
 p.error("Choose --part or --assemble")
if __name__=="__main__":main()
