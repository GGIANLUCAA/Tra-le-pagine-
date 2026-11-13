#!/usr/bin/env python3
"""GIULIANO 04 Nazca: ONE natural Google Gacrux Italian voice, real ASR timing.

No speculative timestamps. Only execute if GitHub one-shot new request is
validated in CI. WAV is kept BEFORE ASR to avoid resynthesis after an issue.
"""
import hashlib,json,math,os,re,subprocess,sys,unicodedata
from difflib import SequenceMatcher
from pathlib import Path

SCRIPT=Path("giuliano/nazca/EP04_BRIEF_SHOTMAP_V1.json")
OUT=Path("output/GIULIANO_04_NAZCA_VOICE")
MODEL="gemini-3.1-flash-tts-preview"
VOICE="Gacrux"
SAMPLE_RATE=24000
def sha(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
 return h.hexdigest()
def write_json(path,obj):Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def tokens(s):
 s=unicodedata.normalize("NFKD",s.lower())
 s="".join(c for c in s if not unicodedata.combining(c))
 return re.findall(r"[a-z0-9]+(?:'[a-z0-9]+)?",s)
def load():
 doc=json.loads(SCRIPT.read_text())
 assert doc["schema"]=="giuliano-nazca-ep04-real-director-brief-v1"
 assert 25<=len(doc["beats"])<=32
 assert 230<=doc["word_count"]<=300
 assert doc["public_release_authorized"] is False
 text=" ".join(b["narration"] for b in doc["beats"])
 return doc,text
def align(phrases,wav,duration):
 from faster_whisper import WhisperModel
 model=WhisperModel("base",device="cpu",compute_type="int8")
 segments,info=model.transcribe(str(wav),language="it",beam_size=4,word_timestamps=True,
                                vad_filter=False,condition_on_previous_text=False)
 heard=[]
 for segment in segments:
  for word in segment.words or []:
   t=tokens(word.word)
   if len(t)==1 and 0<=word.start<word.end<=duration+.3:
    heard.append((t[0],float(word.start),float(word.end)))
 expected=[w for phrase in phrases for w in tokens(phrase)]
 observed=[x[0] for x in heard]
 mapping={}
 for tag,a,b,c,d in SequenceMatcher(None,expected,observed,autojunk=False).get_opcodes():
  if tag=="equal":
   for k in range(b-a):mapping[a+k]=(heard[c+k][1],heard[c+k][2])
 match=len(mapping)/max(1,len(expected))
 if match<.78:raise ValueError(f"ASR_MATCH_TOO_LOW {len(mapping)}/{len(expected)} {match:.3f}; preserve WAV, do not render guessed sync")
 # Interpolate any skipped particles, then expand scene boundaries by a breath.
 starts={}
 for i in range(len(expected)):
  if i in mapping:starts[i]=mapping[i]
  else:
   prev=next((j for j in range(i-1,-1,-1) if j in mapping),None)
   nxt=next((j for j in range(i+1,len(expected)) if j in mapping),None)
   if prev is not None and nxt is not None:
    l=mapping[prev][1];r=mapping[nxt][0];p=(i-prev)/(nxt-prev)
    m=l+(r-l)*p;starts[i]=(m,m+.12)
   elif prev is not None:
    m=mapping[prev][1]+(i-prev)*.19;starts[i]=(m,m+.10)
   elif nxt is not None:
    m=max(0,mapping[nxt][0]-(nxt-i)*.19);starts[i]=(m,m+.10)
   else:raise ValueError("ASR_NO_USABLE_WORDS")
 boundaries=[0.0]
 offset=0
 for phrase in phrases[:-1]:
  offset+=len(tokens(phrase))
  # Split at midpoint between words at sentence boundary; avoid 1s flash cuts.
  a=starts[offset-1][1];b=starts[offset][0]
  split=max(a,min(b,(a+b)/2)) if b>=a else (a+b)/2
  boundaries.append(max(0,min(duration,float(split))))
 boundaries.append(duration)
 scenes=[]
 for i,phrase in enumerate(phrases):
  a,b=boundaries[i],boundaries[i+1]
  if b<=a or b-a<2.20:
   raise ValueError(f"SHOT_BOUNDARY_TOO_BRIEF scene={i+1} sec={b-a:.2f}")
  scenes.append({"id":f"N{i+1:02}","start":round(a,3),"end":round(b,3),
                 "duration":round(b-a,3),"narration":phrase,
                 "time_basis":"Whisper Italian ASR aligned with interpolation; owner artistic review needed"})
 return {"schema":"nazca-real-gacrux-word-alignment-v1","method":"Whisper base + SequenceMatcher, interpolated unmatched words",
         "word_match_fraction":round(match,4),"words_expected":len(expected),"words_matched":len(mapping),
         "duration_seconds":round(duration,3),"requires_sync_review":True,
         "scenes":scenes}
def main():
 if os.environ.get("GIULIANO_NAZCA_GOOGLE_TTS_ONCE")!="1":
  raise SystemExit("VOICE_REQUEST_BLOCKED: owner-approved one-shot flag not set")
 key=os.environ.get("GEMINI_API_KEY","")
 if not key:raise SystemExit("NO_EXISTING_GOOGLE_KEY; do not buy new credits")
 doc,spoken=load()
 OUT.mkdir(parents=True,exist_ok=True)
 output=OUT/"VOCE.wav"
 # A retry after Google succeeded must not incur a second charge.
 if output.exists():raise SystemExit("VOICE_WAV_ALREADY_EXISTS; resume downstream using cached artifact")
 from google import genai
 from google.genai import types
 import numpy as np,soundfile as sf
 client=genai.Client(api_key=key,http_options=types.HttpOptions(api_version="v1beta"))
 try:
  model=client.models.get(model=MODEL)
  if not model.name.endswith(MODEL):raise RuntimeError("MODEL_GET_MISMATCH")
  print("GOOGLE_VOICE_MODEL_GET_OK",model.name,flush=True)
  # Exactly ONE generation call, no retries; never embed authentication in prompts.
  response=client.models.generate_content(
   model=MODEL,
   contents=("Racconta il testo esattamente come scritto in italiano, "
             "con voce maschile Gacrux naturale, calma e cinematografica. "
             "Un vero narratore di documentari: curiosità sobria, pause "
             "naturali, nessun tono enfatico da trailer. Non aggiungere "
             "parole o introduzioni. TESTO:\n"+spoken),
   config=types.GenerateContentConfig(response_modalities=["AUDIO"],
      max_output_tokens=16384,
      speech_config=types.SpeechConfig(voice_config=types.VoiceConfig(
       prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE)))))
  candidate=response.candidates[0] if response.candidates else None
  parts=(candidate.content.parts if candidate and candidate.content else None) or []
  audio_parts=[p.inline_data for p in parts if getattr(p,"inline_data",None) and
               getattr(p.inline_data,"data",None)]
  if not audio_parts:
   usage=response.usage_metadata
   diag={"schema":"nazca-google-tts-nonaudio-v1",
         "status":"NO_AUDIO_RETURNED","model":MODEL,
         "finish_reason":str(getattr(candidate,"finish_reason",None)),
         "usage_prompt_tokens":getattr(usage,"prompt_token_count",None),
         "usage_candidates_tokens":getattr(usage,"candidates_token_count",None),
         "usage_thoughts_tokens":getattr(usage,"thoughts_token_count",None),
         "code":"No data in candidate; never claim produced narration",
         "automatic_retries":False}
   write_json(OUT/"GOOGLE_TTS_NONAUDIO_DIAGNOSTIC.json",diag)
   print("GOOGLE_TTS_REJECTED_OR_TRUNCATED",json.dumps(diag),flush=True)
   raise RuntimeError("GOOGLE_TTS_NO_AUDIO; diagnostics saved, no automatic retries")
  raw=audio_parts[0].data
  if isinstance(raw,str):
   import base64
   raw=base64.b64decode(raw)
  if not raw or len(raw)%2:raise RuntimeError("GOOGLE_TTS_MISSING_VALID_PCM")
  pcm=np.frombuffer(raw,dtype="<i2").astype(np.float32)/32768.0
  duration=len(pcm)/SAMPLE_RATE
  if not 95<=duration<=200:raise RuntimeError("GOOGLE_TTS_DURATION_OUT_OF_SOCIAL_RANGE "+str(duration))
  maxpeak=float(np.max(np.abs(pcm)))
  if maxpeak>.94:pcm*=.94/maxpeak
  sf.write(output,pcm,SAMPLE_RATE,subtype="PCM_16")
  print("GOOGLE_GACRUX_REAL_VOICE_SAVED",round(duration,3),"seconds",sha(output),flush=True)
 finally:
  client.close()
 (OUT/"NARRATION_TEXT.txt").write_text(spoken+"\n",encoding="utf-8")
 profile={"schema":"nazca-gacrux-voice-v1","model":MODEL,"api_version":"v1beta","transport":"models.generate_content",
          "voice":VOICE,"sample_rate":SAMPLE_RATE,"duration_seconds":duration,
          "wav_sha256":sha(output),"script_sha256":sha(SCRIPT),"google_tts_generation_calls":1,
          "claim_caching":True,"regeneration_without_new_owner_consent_forbidden":True}
 write_json(OUT/"VOICE_PROFILE.json",profile)
 # Only the first source for downstream render; align offline as an independent step.
 timing=align([b["narration"] for b in doc["beats"]],output,duration)
 write_json(OUT/"VOICE_TIMING.json",timing)
 print("NAZCA_ASR_REAL_SYNC_MATCH",timing["word_match_fraction"],
       "scenes",len(timing["scenes"]),"duration",duration,flush=True)
if __name__=="__main__":main()
