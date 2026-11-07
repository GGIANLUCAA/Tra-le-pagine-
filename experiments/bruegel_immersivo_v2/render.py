#!/usr/bin/env python3
"""Bruegel 1559 · immersive art critic. Isolated new pilot, no social publishing, no invented artwork.
One authentic public-domain painting + ONE natural Italian Gemini Gacrux narration;
voice aligned to storyboard sentences and full MP4/AAC decode verified.
"""
import hashlib, json, math, os, shutil, subprocess, sys, time, zipfile
from pathlib import Path
import numpy as np
import requests
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"src"))
import gemini_voice

DEST=Path("output/bruegel_1559_critico_immersivo_v2")
BUILD=DEST/"build"
DEST.mkdir(parents=True,exist_ok=True); BUILD.mkdir(parents=True,exist_ok=True)
W,H,FPS=1080,1920,25
BASE="BRUEGEL_1559_CRITICO_IMMERSIVO_V2"
OUTPUT=DEST/(BASE+".mp4")
SOURCE_COMMONS="https://commons.wikimedia.org/wiki/File:The_Fight_Between_Carnival_and_Lent.jpg"
COLLECTION="Kunsthistorisches Museum Vienna, collection GG 1016"
SOURCE_URLS=[
 "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/The_Fight_Between_Carnival_and_Lent.jpg/7680px-The_Fight_Between_Carnival_and_Lent.jpg",
 "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/The_Fight_Between_Carnival_and_Lent.jpg/6144px-The_Fight_Between_Carnival_and_Lent.jpg",
 "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/The_Fight_Between_Carnival_and_Lent.jpg/3840px-The_Fight_Between_Carnival_and_Lent.jpg"
]
# Each block has an evidence-grounded stage (no inaccurate compositing or fake reconstruction).
BEATS=[
 {"spoken":"Fermati un istante. In questa piazza si mangia, si prega, si ride. E si soffre. Bruegel ha dipinto tutto nello stesso respiro.",
  "frames":[("crowd_front",.52,.77,.34,"in"),("full",0,0,0,"in")]},
 {"spoken":"Siamo nelle Fiandre, nel 1559. Il pittore ci solleva sopra i tetti: l'osteria, la chiesa, i mercanti, i mendicanti. Le figure sono minuscole, ma ogni gesto conta.",
  "frames":[("roofs",.48,.22,.37,"right"),("upper_square",.51,.44,.40,"down")]},
 {"spoken":"Guarda in basso a sinistra. Il Carnevale avanza a cavallo di una botte. La sua lancia è uno spiedo carico di carne. È l'eccesso che si presenta come un principe.",
  "frames":[("carnival_wide",.32,.76,.28,"right"),("carnival_close",.34,.80,.17,"in"),("carnival_context",.20,.75,.27,"up")]},
 {"spoken":"Dall'altra parte lo aspetta la Quaresima. È magra, seduta su un carretto, e brandisce una pala da forno con due aringhe. Un duello impossibile, che mette di fronte il banchetto e il digiuno.",
  "frames":[("lent_wide",.65,.79,.28,"left"),("lent_close",.65,.82,.18,"in"),("opposing_sides",0,0,0,"in")]},
 {"spoken":"Ma la scena più tagliente è quasi nascosta. Spostati verso la chiesa. I poveri escono da una porta laterale, mentre i benestanti usano quella principale. C'è chi chiede l'elemosina e chi la distribuisce. Bruegel osserva la pietà, e anche la sua messa in scena.",
  "frames":[("church_wide",.84,.33,.37,"up"),("church_gate",.89,.46,.26,"left"),("alms",.91,.56,.22,"in")]},
 {"spoken":"Adesso cerca il buffone, al centro. Porta una torcia accesa, in pieno giorno. Come se servisse una luce speciale per vedere quello che abbiamo sotto gli occhi.",
  "frames":[("torch_context",.48,.60,.29,"in"),("torch_detail",.47,.58,.19,"left")]},
 {"spoken":"Ecco il segreto di questa folla: nessuno è soltanto virtuoso, nessuno è soltanto ridicolo. La festa convive con la devozione, la generosità con la vanità.",
  "frames":[("crowd_left",.23,.53,.33,"down"),("crowd_right",.77,.51,.33,"up")]},
 {"spoken":"Bruegel non ci consegna un vincitore. Ci lascia sospesi sopra la piazza. A osservare le loro contraddizioni. E, forse, a riconoscere le nostre.",
  "frames":[("full",0,0,0,"out"),("full_final",0,0,0,"out")]}
]
def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()

def run(cmd):
 p=subprocess.run([str(z) for z in cmd],capture_output=True,text=True)
 if p.returncode:
  raise RuntimeError("Command failed: "+" ".join(map(str,cmd[:7]))+"\n"+p.stderr[-2200:])
 return p.stdout

def font(size,bold=False):
 choices=(["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf","/usr/share/fonts/truetype/liberation2/LiberationSerif-Bold.ttf"]
          if bold else ["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf","/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf"])
 for name in choices:
  if Path(name).exists():return ImageFont.truetype(name,size)
 return ImageFont.load_default()

def download_original():
 target=BUILD/"ORIGINAL_ARTWORK_AUTHENTIC.jpg"
 if target.is_file():
  with Image.open(target) as restored:
   restored.load()
   pixels=restored.size
  if pixels==(3840,2798) and sha(target)=="27dfcb114dd8ff6d45e1661c96f8f9e2489df993eb877bd1592406d64fd9ffce":
   return target,SOURCE_URLS[-1],pixels
  raise RuntimeError("Invalid stored image bytes")
 errors=[]
 for url in SOURCE_URLS:
  try:
   print("TRY ART",url,flush=True)
   with requests.get(url,timeout=90,headers={"User-Agent":"Mozilla/5.0 (Art historical narrated mini-documentary; Commons public domain attribution)"},stream=True) as r:
    r.raise_for_status()
    with target.open("wb") as f:
     for block in r.iter_content(1<<18):
      if block:f.write(block)
   Image.MAX_IMAGE_PIXELS=400000000
   with Image.open(target) as im:
    im.load()
    assert im.width >= 3800 and im.height >= 2700
    assert 1.33 < im.width/im.height < 1.5
    dims=im.size
   return target,url,dims
  except Exception as ex:
   errors.append(f"{url}: {type(ex).__name__}: {str(ex)[:140]}")
   target.unlink(missing_ok=True)
 raise RuntimeError("The genuine source is not obtainable; refuse to invent it. "+repr(errors))

def cover(art):
 cw,ch=1080,1920
 canvas=Image.new("RGB",(cw,ch),(18,20,24))
 painting=art.copy()
 painting.thumbnail((1010,1050),Image.Resampling.LANCZOS)
 # Deep navy wall, not claiming to be a real museum.
 ambient=art.resize((cw,ch),Image.Resampling.BILINEAR).filter(ImageFilter.GaussianBlur(70))
 ambient=ImageEnhance.Brightness(ambient).enhance(.15)
 canvas=Image.blend(canvas,ambient,.22)
 px=(cw-painting.width)//2;py=440
 sh=Image.new("RGBA",(painting.width+55,painting.height+55))
 d=ImageDraw.Draw(sh)
 d.rectangle((23,27,painting.width+36,painting.height+39),fill=(0,0,0,145))
 sh=sh.filter(ImageFilter.GaussianBlur(21))
 canvas.paste(sh,(px-25,py-25),sh)
 canvas.paste(painting,(px,py))
 draw=ImageDraw.Draw(canvas)
 draw.text((72,110),"PIETER BRUEGEL THE ELDER",font=font(37,True),fill=(225,204,161))
 draw.line((72,176,322,176),fill=(190,160,103),width=3)
 draw.text((72,208),"THE FIGHT BETWEEN",font=font(54,True),fill=(248,243,229))
 draw.text((72,277),"CARNIVAL AND LENT",font=font(54,True),fill=(248,243,229))
 draw.text((72,1645),"1559  ·  OIL ON OAK PANEL",font=font(31),fill=(226,210,176))
 draw.text((72,1698),"KUNSTHISTORISCHES MUSEUM, VIENNA",font=font(25),fill=(208,199,178))
 draw.line((72,1765,1009,1765),fill=(129,115,90),width=1)
 return canvas

def full_composition(art,final=False):
 canvas=Image.new("RGB",(W,H),(12,13,18))
 # atmospheric dark, NOT a fabricated wall/frame
 back=art.resize((W,H),Image.Resampling.BILINEAR).filter(ImageFilter.GaussianBlur(60))
 back=ImageEnhance.Brightness(back).enhance(.22)
 canvas=Image.blend(canvas,back,.39)
 fitted=art.copy()
 fitted.thumbnail((1072,1050),Image.Resampling.LANCZOS)
 x=(W-fitted.width)//2;y=(H-fitted.height)//2
 canvas.paste(fitted,(x,y))
 # very narrow black separation, not a fake historical frame
 dr=ImageDraw.Draw(canvas)
 dr.rectangle((x-2,y-2,x+fitted.width+1,y+fitted.height+1),outline=(36,29,25),width=3)
 if final:
  dr.text((W//2,270),"THE FIGHT BETWEEN",font=font(37,True),fill=(240,232,210),anchor="mm")
  dr.text((W//2,329),"CARNIVAL AND LENT",font=font(37,True),fill=(240,232,210),anchor="mm")
  dr.text((W//2,1706),"PIETER BRUEGEL THE ELDER  ·  1559",font=font(25),fill=(230,210,174),anchor="mm")
 return canvas

def artwork_crop(art,cx,cy,width_fraction):
 iw,ih=art.size
 sw=int(iw*width_fraction)
 sh=int(sw*H/W)
 if sh>ih:
  sh=ih;sw=int(sh*W/H)
 # Preserve all exact original painted pixels, no AI-added detail.
 left=max(0,min(iw-sw,int(cx*iw-sw*.5)))
 top=max(0,min(ih-sh,int(cy*ih-sh*.5)))
 cropped=art.crop((left,top,left+sw,top+sh))
 base=cropped.resize((W,H),Image.Resampling.LANCZOS)
 return ImageEnhance.Contrast(base).enhance(1.012)

def art_still(art,frame):
 key,x,y,width,_=frame
 if key in ("full","opposing_sides"):return full_composition(art)
 if key=="full_final":return full_composition(art,True)
 return artwork_crop(art,x,y,width)

def audio_score(seconds):
 # Fully original ambient film score: low bowed harmonics, sparse pizzicato and muted bells.
 # Derived from sine waves and controlled noise; no copyrighted recordings.
 sr=24000;n=int((seconds+.8)*sr);audio=np.zeros(n,np.float32)
 # low D minor - B flat - G minor - A minor progression, no musical quotation
 chord_cycles=[(73.42,110,146.83),(58.27,116.54,174.61),(65.41,98,196.0),(55.0,110,164.81)]
 for k in range(math.ceil(seconds/17)):
  a0=k*17;freqs=chord_cycles[k%len(chord_cycles)]
  start=int(a0*sr);end=min(n,int((a0+18)*sr))
  if end<=start:continue
  t=np.arange(end-start,dtype=np.float64)/sr
  env=np.minimum(1,t/2.2)*np.minimum(1,(end-start)/sr-t+.6)/1.0
  env=np.clip(env,0,1).astype(np.float32)
  for j,hz in enumerate(freqs):
   tone=(np.sin(2*np.pi*hz*t)+.19*np.sin(2*np.pi*hz*2.008*t))*.010/(1+j*.7)
   audio[start:end]+=tone.astype(np.float32)*env
 # barely audible pulse / footstep-like subdued rhythm, not falsely claimed historical ambience
 for k in range(math.ceil(seconds/.89)):
  pos=int(sr*k*.89)
  if pos>=n:break
  m=min(int(sr*.15),n-pos)
  t=np.arange(m,dtype=np.float32)/sr
  audio[pos:pos+m]+=(.003*np.sin(2*np.pi*81*t)*np.exp(-t*22))
 for moment in (0.40, seconds*.49):
  pos=int(moment*sr)
  m=min(int(sr*1.8),n-pos)
  if m<=0:continue
  t=np.arange(m,dtype=np.float32)/sr
  bell=sum(np.sin(2*np.pi*f*t) * w for f,w in ((392,1),(784,.31),(1176,.13)))
  audio[pos:pos+m]+=(.017*bell*np.exp(-t*3.1)).astype(np.float32)
 fade=int(sr*1.8);audio[:fade]*=np.linspace(0,1,fade)
 audio[-fade:]*=np.linspace(1,0,fade)
 sf.write(BUILD/"ORIGINAL_SCORE.wav",np.clip(audio,-.95,.95),sr)
 return BUILD/"ORIGINAL_SCORE.wav"

def make_frames(art,blocks):
 entries=[]
 for i,b in enumerate(blocks):
  for j,frame in enumerate(b["frames"]):
   p=BUILD/f"shot_{i:02d}_{j:02d}.jpg"
   art_still(art,frame).save(p,quality=95,optimize=True,subsampling=0)
   entries.append((i,j,frame,p))
 return entries

def determine_times(timed,duration):
 counts=[len(gemini_voice.sentences(b["spoken"])) for b in BEATS]
 if len(timed)!=sum(counts):raise RuntimeError("Voice timing count mismatch")
 spans=[];idx=0;last=0
 for n in counts:
  ending=float(timed[idx+n-1][2]);idx+=n
  ending=max(last+.4,min(duration,ending))
  spans.append((last,ending))
  last=ending
 if duration>last:spans[-1]=(spans[-1][0],duration)
 if len(spans)!=len(BEATS) or any(b-a<3 for a,b in spans):
  raise RuntimeError("Not enough spoken time for distinct real footage details "+repr(spans))
 return spans

def videos_for_shots(entries,spans):
 segments=[]
 # make shot runtime exactly track the same one-take voice paragraph boundaries
 for i,b in enumerate(BEATS):
  start,end=spans[i]
  frames=[e for e in entries if e[0]==i]
  for j,entry in enumerate(frames):
   weight=1/len(frames)
   duration=(end-start)*weight
   name,focusx,focusy,fract,motion=entry[2]
   out=BUILD/f"segment_{i:02d}_{j:02d}.mp4"
   still=entry[3]
   nframes=max(1,round(duration*FPS))
   # Slow real camera glide across still authentic artwork; no invented characters/motions
   sign={"left":-1,"right":1,"up":0,"down":0,"in":0,"out":0}.get(motion,0)
   step=0.00012 if motion!="out" else 0.00008
   z=f"min(zoom+{step},1.034)"
   dx=f"iw/2-iw/zoom/2+on*{sign*.075}"
   dy=f"ih/2-ih/zoom/2+on*{(-.055 if motion=='up' else (.055 if motion=='down' else 0))}"
   vf=f"zoompan=z='{z}':x='max(0,min(iw-iw/zoom,{dx}))':y='max(0,min(ih-ih/zoom,{dy}))':d=1:s={W}x{H}:fps={FPS},format=yuv420p"
   run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y","-loop","1","-framerate",str(FPS),
         "-i",still,"-vf",vf,"-frames:v",str(nframes),"-an","-c:v","libx264","-threads","2",
         "-preset","veryfast","-crf","19","-pix_fmt","yuv420p","-r",str(FPS),out])
   segments.append((i,j,str(out),nframes/FPS,name))
   print("SHOT",i,j,name,round(nframes/FPS,2),"sec",flush=True)
 return segments

def make_srt(timed):
 def srtstamp(t):
  ms=max(0,round(t*1000))
  h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
  return f"{h:02}:{m:02}:{s:02},{ms:03}"
 parts=[]
 for i,(words,a,b) in enumerate(timed):
  parts.append(f"{i+1}\n{srtstamp(a)} --> {srtstamp(b)}\n{words}\n")
 (DEST/"SOTTOTITOLI_OPZIONALI_IT.srt").write_text("\n".join(parts),encoding="utf-8")

def finish(segments,voice_dur):
 listfile=BUILD/"concat.txt"
 listfile.write_text("".join(f"file '{Path(p).resolve()}'\n" for _,_,p,_,_ in segments))
 silent=BUILD/"film_senza_audio.mp4"
 run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y","-safe","0","-f","concat","-i",listfile,"-c","copy",silent])
 score=audio_score(voice_dur)
 # Preserve uncut, intelligible narration and subdued original music
 run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y","-i",silent,"-i",DEST/"VOCE_GACRUX.wav","-i",score,
      "-filter_complex","[1:a]volume=1.12,highpass=f=70,lowpass=f=11900[v];[2:a]volume=0.55[m];[v][m]amix=inputs=2:duration=first:dropout_transition=0,alimiter=limit=0.93[a]",
      "-map","0:v:0","-map","[a]","-c:v","copy","-c:a","aac","-b:a","192k",
      "-ar","44100","-ac","2","-movflags","+faststart","-shortest",OUTPUT])
 run(["ffmpeg","-hide_banner","-loglevel","error","-xerror","-i",OUTPUT,"-f","null","-"])
 import av
 with av.open(str(OUTPUT)) as container:
  vids=[s for s in container.streams if s.type=="video"]
  auds=[s for s in container.streams if s.type=="audio"]
  assert len(vids)==1 and vids[0].codec_context.width==W and vids[0].codec_context.height==H
  assert vids[0].codec_context.name=="h264" and len(auds)==1 and auds[0].codec_context.name=="aac"
  dur=container.duration/av.time_base
 assert 70<=dur<=160 and OUTPUT.stat().st_size>2500000,(dur,OUTPUT.stat().st_size)
 return dur

def synthesize_supported_gemini(script):
 """Google Gemini standard generateContent TTS; not the separate unsupported Interactions gateway."""
 import io
 import re
 from google import genai
 from google.genai import types
 client=genai.Client(api_key=os.environ["GEMINI_API_KEY"])
 prompt=("Read the following Italian text EXACTLY, with no added or omitted words. "
         "Perform it as a beautiful, credible Italian documentary narration by a mature man, rich warm timbre, "
         "magnetic but unforced, real breath and varied emotional weight, unhurried consonants, "
         "gentle suspense at the church, compassionate not saccharine, a thoughtful closing. "
         "No comedy, no booming trailer announcer, no robot rhythm, no extra introductions. "
         "Speak Italian with clear natural pronunciation of Bruegel. Read only this text:\n\n"+script)
 model="gemini-2.5-flash-preview-tts"
 print("REAL GOOGLE GEMINI TTS generateContent model",model,flush=True)
 try:
  response=client.models.generate_content(
   model=model,
   contents=prompt,
   config=types.GenerateContentConfig(
    response_modalities=["AUDIO"],
    speech_config=types.SpeechConfig(
     voice_config=types.VoiceConfig(
      prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Gacrux")
     )
    )
   )
  )
 except Exception as exc:
  raise RuntimeError("TTS unavailable on current Free API key; not substituting old rejected Edge voice: "+str(exc)[:500])
 parts=[]
 for cand in response.candidates or []:
  if cand.content:
   for part in cand.content.parts or []:
    if part.inline_data and part.inline_data.data:
     parts.append(part.inline_data)
 assert parts,"No real Gemini audio bytes returned"
 blob=parts[0].data
 if isinstance(blob,str):
  import base64
  blob=base64.b64decode(blob)
 raw=bytes(blob)
 if raw[:4]==b"RIFF":
  audio,sr=sf.read(io.BytesIO(raw),dtype="float32")
 else:
  mime=(parts[0].mime_type or "").lower()
  m=re.search(r"rate[=; ]+(\d+)",mime)
  sr=int(m.group(1)) if m else 24000
  assert len(raw)%2==0,"Unexpected speech encoding "+mime
  audio=np.frombuffer(raw,dtype="<i2").astype(np.float32)/32768
 if audio.ndim==2:
  audio=audio.mean(axis=1)
 assert sr>=16000 and len(audio)>sr*60,"Generated speech empty, too short or corrupt"
 if sr!=24000:
  from scipy.signal import resample_poly
  div=math.gcd(sr,24000)
  audio=resample_poly(audio,24000//div,sr//div).astype(np.float32)
  sr=24000
 audio=np.asarray(audio,dtype=np.float32)
 assert np.isfinite(audio).all()
 peak=float(np.max(np.abs(audio)))
 if peak>.94:
  audio*=.94/peak
 wav=BUILD/"VOCE.wav"
 sf.write(wav,audio,24000)
 duration=len(audio)/24000
 print("REAL GACRUX VOICE generated",round(duration,2),"seconds",flush=True)
 timed=gemini_voice.align(gemini_voice.sentences(script),wav,duration)
 (BUILD/"VOICE_CACHE_V13.json").write_text(json.dumps(
  {"provider":"Google Gemini TTS","model":model,"voice":"Gacrux",
   "sha256":sha(wav),"duration_seconds":duration,"reusable_audio":True},indent=2),encoding="utf-8")
 return audio,timed

def main():
 if os.getenv("ARTVISION_GEMINI_PROJECT_BILLING_TIER")!="Free":
  raise RuntimeError("Free/no-billing Gemini account not verified; refuse API call")
 if not os.getenv("GEMINI_API_KEY"):
  raise RuntimeError("Second-account Free Gemini secret missing; cannot produce the requested excellent natural voice")
 src,url,dim=download_original()
 print("AUTHENTIC SOURCE",dim,sha(src),flush=True)
 im=Image.open(src).convert("RGB")
 c=cover(im)
 c.save(DEST/"COPERTINA.jpg",quality=94,optimize=True)
 script="\n\n".join(x["spoken"] for x in BEATS)
 (DEST/"COPIONE_ITALIANO.txt").write_text(script,encoding="utf-8")
 # Natural single-take mature Italian documentary narrator; zero comedy / fake interpretation.
 gemini_voice.MODEL="gemini-3.1-flash-tts-preview"  # available on Gemini API, unlike unavailable 3.8 for this account
 gemini_voice.STYLE=("Perform in standard Italian as a superb human documentary actor, intimate but magnetic, "
 "warm low-mid male voice, luminous clarity, genuine fascination, expressive dynamics and intentional silences. "
 "Sound as though walking slowly through an extraordinary painting, discovering real visual details for the first time. "
 "First sentence quietly gripping, not shouted. Build subtle suspense approaching the church and restrained compassion "
 "when describing the poor; return to philosophical insight in the last two sentences. Avoid commercial announcer, "
 "robotic monotony, sugary pathos, whisper gimmicks, singsong and exaggerated trailer intensity. "
 "Factual art-history storytelling; keep exact Italian words and natural pronunciation of Bruegel.")
 import gemini_voice as g
 g._save_voice_cache # use original single-request cache + ASR.
 print("GACRUX MODEL",g.MODEL,"VOICE",g.VOICE,flush=True)
 old=BUILD/"VOCE.wav"
 # generate voice at BUILD and retain a real WAV backup at DEST for future no-rebill edits
 data,timed=synthesize_supported_gemini(script)
 shutil.copy2(old,DEST/"VOCE_GACRUX.wav")
 duration=len(data)/g.SAMPLE_RATE
 print("VOICE_SECONDS",round(duration,3),"ALIGN",json.loads((BUILD/"ALLINEAMENTO_VOCE.json").read_text()),flush=True)
 assert len(data)>g.SAMPLE_RATE*70, "Speech too short"
 spans=determine_times(timed,duration)
 make_srt(timed)
 entries=make_frames(im,BEATS)
 segments=videos_for_shots(entries,spans)
 video_duration=finish(segments,duration)
 (DEST/"CREDITI_E_FONTI.txt").write_text(
  "The Fight Between Carnival and Lent — Pieter Bruegel the Elder, 1559. "+
  "Oil on oak panel, approx. 118 × 164.5 cm, Kunsthistorisches Museum Vienna, GG 1016.\n"+
  "Descrizione e lettura storico-artistica: ricerca del Kunsthistorisches Museum: https://bruegel.at/en/carnival-vs-lent/ .\n"+
  "Immagine originale fedele del quadro, PD-Art/Public Domain Mark, Wikimedia Commons: "+SOURCE_COMMONS+"\n"+
  "File derivato realmente scaricato da: "+url+"\n"+
  "La composizione è un dipinto, non un video storico; movimenti di camera solo da ritagli pittorici autentici.\n"+
  "La lettura simbolica è commento critico, non cronaca di eventi reali.\n"+
  "Voce: Google Gemini Gacrux, unica registrazione italiana sintetica; musica originale generata da sinusoidi in locale.\n"+
  "Nessuna cornice storica inventata, nessuna messa in scena museale falsa, nessuna pubblicazione automatica.\n",encoding="utf-8")
 (DEST/"DESCRIZIONE_SOCIAL_IT.txt").write_text(
  "Una piazza, due eserciti, un'intera umanità. Nel capolavoro del 1559, Pieter Bruegel racconta "
  "Carnevale e Quaresima, ma basta spostare lo sguardo verso la chiesa per scoprire una critica sociale "
  "molto più profonda. Un viaggio tra i dettagli autentici di un quadro che sembra ancora parlarci oggi.\n\n"
  "Pieter Bruegel il Vecchio, The Fight Between Carnival and Lent (1559), Kunsthistorisches Museum Vienna.\n"
  "#Bruegel #StoriaDellArte #Arte #Pittura #Rinascimento #CriticaDArte\n",encoding="utf-8")
 align=json.loads((BUILD/"ALLINEAMENTO_VOCE.json").read_text())
 manifest={"status":"RENDERED_MP4_REAL_TECH_QA_PASS_ARTISTIC_REVIEW_PENDING","title":"The Fight Between Carnival and Lent",
 "video":OUTPUT.name,"bytes":OUTPUT.stat().st_size,"sha256":sha(OUTPUT),"duration_seconds":round(video_duration,3),
 "source_image":url,"source_pixels":dim,"source_sha256":sha(src),"narrator":"Google Gemini Gacrux",
 "voice_sha256":sha(DEST/"VOCE_GACRUX.wav"),"voice_seconds":round(duration,3),
 "alignment_method":align["method"],"alignment_match_fraction":align.get("matched_fraction"),
 "frames":len(segments),"resolution":[W,H],"codec_video":"h264","codec_audio":"aac","full_ffmpeg_decode":"PASS",
 "artwork_authentic":True,"museum_frame_claim":False,"published":False,"human_artistic_approval":False,
 "run_isolated":True}
 (DEST/"VERIFICA_QA.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
 # concise package, includes voice WAV so no need for another generated TTS if reviewer requests recuts
 bundle=DEST/(BASE+"_CONSEGNA.zip")
 with zipfile.ZipFile(bundle,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
  for name in (OUTPUT.name,"COPERTINA.jpg","VOCE_GACRUX.wav","COPIONE_ITALIANO.txt",
               "SOTTOTITOLI_OPZIONALI_IT.srt","CREDITI_E_FONTI.txt","DESCRIZIONE_SOCIAL_IT.txt","VERIFICA_QA.json"):
   z.write(DEST/name,arcname=name)
 with zipfile.ZipFile(bundle) as z:
  assert z.testzip() is None and OUTPUT.name in z.namelist()
 print("COMPLETE",json.dumps(manifest,ensure_ascii=False),flush=True)

if __name__=="__main__":main()
