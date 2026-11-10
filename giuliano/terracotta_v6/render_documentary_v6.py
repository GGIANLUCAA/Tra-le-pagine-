#!/usr/bin/env python3
"""Giuliano V6: strict historical-documentary editing with 34 fresh factual beats, dual-angle inserts, real-photo provenance, cinematic sound design, and mobile verified MP4. NOT AI historical footage."""
import hashlib, html, json, math, os, re, subprocess, sys, time, urllib.parse, zipfile
from pathlib import Path
import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import gemini_voice
from gemini_voice import synthesize
gemini_voice.STYLE = "Italian professional television documentary presenter. Restrained, thoughtful, evidence-led, nuanced natural speech, conversational but authoritative. Avoid overemphasis, theatrical narration, melodrama, synthetic trailer voice and repetitive sentence-ending cadence. Allow subtle human hesitations and varied phrase length. Sound like a serious archaeology journalist, not a museum guide. The central question is why excavating fragile heritage can destroy evidence. Speak clearly and naturally."

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"output"/"giuliano_terracotta_v6"
MEDIA=OUT/"media"
W,H,FPS=1080,1920,24
# Real museum photos, independently described/licensed at Wikimedia Commons.
# The order matches the exact sentence order in the narration.
STORYBOARD_PATH=ROOT/"giuliano"/"terracotta_v6"/"SHOTS_DOCUMENTARY_V6.json"
PLAN=json.loads(STORYBOARD_PATH.read_text(encoding="utf8"))
SHOTS=PLAN["shots"]
FILES=list(dict.fromkeys(f for row in SHOTS for f in (row["source_file"],row.get("second_file")) if f))
if len(SHOTS)<32 or len(set(FILES))<28:
 raise RuntimeError("V6 needs 32+ factual beats and 30+ authentic distinct photographic sources")
UA="GiulianoTerracottaV6Film/1.0 (editorial Wikimedia Commons photographic attribution)"
def shell(cmd):
 print("+", " ".join(map(str,cmd)),flush=True)
 subprocess.run(list(map(str,cmd)),check=True)
def sha(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
 return h.hexdigest()
def strip_html(t):
 return re.sub(r"\s+"," ",html.unescape(re.sub("<[^>]+>"," ",t or ""))).strip()
def fetch_metadata(filenames):
 """A single Commons API query for all exact verified file titles; avoids 31 independent API queries."""
 session=requests.Session()
 session.headers.update({"User-Agent":UA,"Accept":"application/json"})
 api="https://commons.wikimedia.org/w/api.php"
 result={}
 for start in range(0,len(filenames),22):
  group=filenames[start:start+22]
  params={"action":"query","format":"json","prop":"imageinfo",
       "iiprop":"url|extmetadata|size","iiurlwidth":"1800",
       "redirects":1,"titles":"|".join("File:"+n for n in group)}
  last=None
  for n in range(4):
   try:
    r=session.get(api,params=params,timeout=70)
    r.raise_for_status()
    pages=r.json()["query"]["pages"]
    for page in pages.values():
     if "missing" in page or not page.get("imageinfo"):
      continue
     title=page["title"][5:]
     info=page["imageinfo"][0]
     ext=info.get("extmetadata",{})
     lic=strip_html(ext.get("LicenseShortName",{}).get("value",""))
     terms=strip_html(ext.get("UsageTerms",{}).get("value",""))
     lic_url=ext.get("LicenseUrl",{}).get("value","")
     low=(lic+" "+terms).lower()
     allowed=("cc0" in low or "cc by" in low or "cc-by" in low or "public domain" in low or low.startswith("pd-"))
     restricted=any(tag in low for tag in ["noncommercial","non-commercial","-nc","no derivatives","-nd"])
     if not allowed or restricted:
      raise RuntimeError("Unacceptable photo licence "+title+" ("+lic+")")
     if not info.get("thumburl") and not info.get("url"):
      continue
     key=title.replace("_"," ").casefold()
     result[key]={"file":title,"url":info.get("thumburl") or info["url"],
        "commons_page":"https://commons.wikimedia.org/wiki/"+urllib.parse.quote("File:"+title.replace(" ","_")),
        "photographer":strip_html(ext.get("Artist",{}).get("value","Unspecified")),
        "license":lic,"license_url":lic_url,
        "source_width":info.get("width"),"source_height":info.get("height")}
    break
   except (requests.RequestException,ValueError) as exc:
    last=exc
    if n==3:raise RuntimeError("Commons metadata fetch failed") from last
    time.sleep(6*(n+1))
 for name in filenames:
  key=name.replace("_"," ").casefold()
  if key not in result:
   print("MISSING_LICENSED_SOURCE",name,flush=True)
 return [result.get(name.replace("_"," ").casefold()) for name in filenames]

def download_commons(metadata,dest):
 # Licensed original remains linked to Wikimedia. Alternate delivery endpoints
 # only resize/copy the SAME identified original to avoid GitHub runner 429.
 original=metadata["url"]
 delivery=[
  ("weserv","https://images.weserv.nl/?"+urllib.parse.urlencode({"url":original,"w":"1800","output":"jpg","q":"91"})),
  ("wsrv","https://wsrv.nl/?"+urllib.parse.urlencode({"url":original,"w":"1800","output":"jpg","q":"91"})),
  ("direct",original),
 ]
 session=requests.Session()
 session.headers.update({"User-Agent":UA})
 last=None
 for mode,link in delivery:
  for attempt in range(2):
   try:
    r=session.get(link,timeout=75)
    r.raise_for_status()
    dest.write_bytes(r.content)
    with Image.open(dest) as im:
     im.verify()
    if dest.stat().st_size<14000:raise RuntimeError("Photo below minimum integrity size")
    print("IMAGE_DELIVERY",mode,metadata["file"],dest.stat().st_size,flush=True)
    return {**metadata,"delivery_method":mode,
         "image_sha256":sha(dest),"bytes":dest.stat().st_size}
   except (requests.RequestException,OSError,ValueError,RuntimeError) as err:
    last=err
    print("DELIVERY_FAIL",mode,attempt,metadata["file"],type(err).__name__,str(err)[:150],flush=True)
    if attempt==0:time.sleep(3)
 raise RuntimeError("No original-preserving image delivery for "+metadata["file"]) from last

def font(sz,bold=False):
 options=(
  ["/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
   "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] if bold
  else ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
 )
 for p in options:
  if Path(p).exists():return ImageFont.truetype(p,sz)
 return ImageFont.load_default()

def add_gradient(im,darkness=.82,start=.65):
 overlay=Image.new("RGBA",im.size,(0,0,0,0)); dr=ImageDraw.Draw(overlay)
 for y in range(int(im.height*start),im.height):
  rel=max(0.0,min(1.0,(y/im.height-start)/(1-start)))
  a=int(180*darkness*rel**1.4)
  dr.line((0,y,im.width,y),fill=(5,8,12,min(230,a)))
 return Image.alpha_composite(im.convert("RGBA"),overlay).convert("RGB")

def make_canvas(path,out,beat,i,is_title=False,is_insert=False):
 """Editorial layouts: preserve authentic wide pits; crop portraits only when the feature remains legible."""
 source=ImageOps.exif_transpose(Image.open(path)).convert("RGB")
 source=ImageEnhance.Contrast(source).enhance(1.07)
 source=ImageEnhance.Color(source).enhance(1.035)
 rw,rh=1200,2134
 if beat.get("presentation") in ("wide","hero") and i%3==2 and not is_title and not(is_insert and beat.get("semantic") in ("portrait","acrobat")):
  bg=ImageOps.fit(source,(rw,rh),Image.Resampling.LANCZOS)
  bg=bg.filter(ImageFilter.GaussianBlur(34))
  bg=Image.blend(bg,Image.new("RGB",(rw,rh),(8,11,15)),.76)
  main=ImageOps.contain(source,(rw-72,1190),Image.Resampling.LANCZOS)
  x=(rw-main.width)//2; y=385+(1190-main.height)//2
  bg.paste(main,(x,y))
  d=ImageDraw.Draw(bg)
  d.line((x,y+main.height+14,x+main.width,y+main.height+14),fill=(170,141,89),width=3)
 else:
  if beat.get("presentation")=="detail" and is_insert:
   # Real second still image remains legible, no synthetic pixels or invented objects.
   focus=(.5,.5)
  else:
   focus=(.50,.44 if beat.get("presentation")=="portrait" else .5)
  bg=ImageOps.fit(source,(rw,rh),Image.Resampling.LANCZOS,centering=focus)
 bg=add_gradient(bg,.90,.68)
 d=ImageDraw.Draw(bg)
 kicker={"DISCOVERY":"01 / LA SCOPERTA","THE ARMY":"02 / I GUERRIERI",
         "COLOUR":"03 / I COLORI PERDUTI","BRONZE":"04 / LE ARMI",
         "THE EMPEROR":"05 / L'IMPERATORE","THE UNOPENED TOMB":"06 / LA TOMBA"}
 # All text stays inside portrait/social safe areas.
 d.rectangle((0,0,rw,142),fill=(9,13,17)) if i in (0,12,19,25,30) else None
 d.text((66,58),kicker.get(beat.get("chapter"),"ARCHEOLOGIA"),font=font(29,True),fill=(213,186,133)) if i in (0,12,19,25,30) else None
 
 if is_title:
  d.text((84,1503),"THE",font=font(110,True),fill=(246,236,209))
  d.text((80,1637),"TERRACOTTA",font=font(126,True),fill=(255,248,231))
  d.text((84,1798),"ARMY",font=font(148,True),fill=(255,248,231))
  d.line((84,1975,1100,1975),fill=(213,174,100),width=4)
 else:
  label=(beat.get("overlay") or "").strip()
  if label and i in (0,2,14,20,30):
   # Deliberately restrained factual chips: no fake dramatic subtitles.
   d.rounded_rectangle((55,1740,1150,1878),radius=14,fill=(7,11,15))
   size=54 if len(label)<=25 else 42
   d.text((90,1779),label,font=font(size,True),fill=(255,236,194))
 bg.save(out,quality=93,subsampling=0)

def cover_from(path,out):
 image=ImageOps.fit(ImageOps.exif_transpose(Image.open(path)).convert("RGB"),
                    (W,H),Image.Resampling.LANCZOS,centering=(.5,.38))
 image=add_gradient(image,.98,.45)
 d=ImageDraw.Draw(image)
 d.rectangle((0,0,W,120),fill=(5,8,12))
 d.text((64,50),"DOCUMENTARIO STORICO",font=font(32,True),fill=(217,180,113))
 d.text((54,1370),"THE",font=font(97,True),fill="#f8e8bb")
 d.text((50,1488),"TERRACOTTA",font=font(110,True),fill="#ffffff")
 d.text((54,1630),"ARMY",font=font(148,True),fill="#ffffff")
 d.text((64,1810),"L'ESERCITO SEPOLTO",font=font(49,True),fill="#dec08d")
 image.save(out,quality=94,subsampling=0)

def contact_sheet(canvases,out):
 cols=8;cw=145;ch=278;rows=math.ceil(len(canvases)/cols)
 image=Image.new("RGB",(cols*cw+12,rows*ch+20),(10,13,18));d=ImageDraw.Draw(image)
 for i,p in enumerate(canvases):
  frame=Image.open(p).convert("RGB")
  frame.thumbnail((130,239),Image.Resampling.LANCZOS)
  x=8+(i%cols)*cw;y=8+(i//cols)*ch
  image.paste(frame,(x,y))
  d.text((x,y+242),str(i+1),font=font(19,True),fill=(230,212,176))
 image.save(out,quality=90)

def original_music(duration,out):
 """Original score, programmed: evolving minor pads, discrete low-string-like waves, three acts, pauses."""
 import soundfile as sf
 sr=24000;n=int((duration+.6)*sr)
 t=np.arange(n,dtype=np.float32)/sr
 signal=np.zeros(n,np.float32)
 # Original harmonic bed, with changing orchestration by chapter.
 for f,a in [(55,.021),(82.41,.015),(110,.009),(164.81,.012),(220,.006)]:
  signal += a*np.sin(2*np.pi*f*t + .25*np.sin(2*np.pi*.065*t))
 # A cinematic slow pulse, more frequent during the archaeological discovery.
 for sec in np.arange(1,duration-1,3.4):
  lo=int(sec*sr);hi=min(n,lo+int(1.6*sr))
  local=np.arange(hi-lo,dtype=np.float32)/sr
  wave=np.sin(2*np.pi*(59+5*np.exp(-local*2))*local)
  signal[lo:hi] += .052*np.exp(-local*3.8)*wave
 # Bell harmonic highlights at established chapter reveals, not every edit.
 for ratio,f in [(0.0,329.6),(.36,261.6),(.57,220),(.75,293.7),(.92,174.6)]:
  lo=min(n-1,int((duration*ratio+.4)*sr))
  hi=min(n,lo+int(4.1*sr))
  local=np.arange(hi-lo,dtype=np.float32)/sr
  signal[lo:hi] += .026*np.exp(-local*.85)*(
   np.sin(2*np.pi*f*local)+.24*np.sin(2*np.pi*2*f*local))
 # Subtle lower volume under voice; first 2 seconds have a clean sonic title.
 fade=np.minimum(1,np.minimum(t/1.4,(duration+.4-t)/2.8))
 signal*=np.clip(fade,0,1)
 sf.write(out,np.clip(signal,-.75,.75),sr)

def zoom_filter(frames,index,motion):
 s=f"{W}x{H}";n=max(1,frames)
 if motion=="hold":inc=.000008
 elif motion=="push":inc=.000035
 elif motion=="pull":inc=.000018
 else:inc=.000023
 if motion=="pan_left":
  x="'(iw-iw/zoom)*(1-on/%s)'"%n
 elif motion=="pan_right":
  x="'(iw-iw/zoom)*(on/%s)'"%n
 else:x="'iw/2-iw/zoom/2'"
 y="'ih/2-ih/zoom/2'"
 return f"zoompan=z='min(1.015+on*{inc:.6f},1.095)':x={x}:y={y}:d={frames}:s={s}:fps={FPS},format=yuv420p"

def main():
 OUT.mkdir(parents=True,exist_ok=True);MEDIA.mkdir(parents=True,exist_ok=True)
 script=(ROOT/"giuliano"/"terracotta_v6"/"VOCE_DOCUMENTARIO_V6.txt").read_text(encoding="utf8").strip()
 expected="\n".join(beat["text"] for beat in SHOTS)
 if script!=expected:raise RuntimeError("Narration and real-image decision list are not identical")
 if "avviciniamoci" in script.lower() or "guardiamo" in script.lower():raise RuntimeError("Artwork-narrator rhetoric forbidden")
 names=FILES
 infos=fetch_metadata(names)
 raw={}
 semantic_by_file={}
 for beat in SHOTS:
  semantic_by_file.setdefault(beat["source_file"],set()).add(beat["semantic"])
  if beat.get("second_file"):semantic_by_file.setdefault(beat["second_file"],set()).add(beat["semantic"])
 for name,info in zip(names,infos):
  if info is None:
   print("MISSING_PHOTO_METADATA",name,flush=True)
   continue
  dst=MEDIA/("source_%02d.jpg"%names.index(name))
  try:
   raw[name]={"path":dst,"meta":download_commons(info,dst)}
   print("PHOTO_V6",name,raw[name]["meta"]["license"],flush=True)
   time.sleep(.15)
  except Exception as err:
   print("SOURCE_V6_UNAVAILABLE",name,str(err)[:160],flush=True)
 if len({x["meta"]["image_sha256"] for x in raw.values()})<29:
  raise RuntimeError("Too few real, independently licensed photographs")
 print("SOURCE_GATE_OK",len(raw),"unique verified photo files",flush=True)
 # Only semantic fallback, no fabricated art or fake museum shots.
 safe={
  "formation":{"formation","pit"}, "pit":{"pit","formation"},
  "portrait":{"portrait","armour"}, "armour":{"armour","portrait"},
  "horse":{"horse"}, "archer":{"archer"}, "pigment":{"pigment","reconstruction"},
  "reconstruction":{"reconstruction"}, "weapons":{"weapons"},
  "mound":{"mound"}, "acrobat":{"acrobat"}, "chariot":{"chariot"}
 }
 def resolve(name,beat,optional=False):
  if name in raw:return raw[name],False
  role=beat["semantic"]
  choices=[raw[k] for k in names if k in raw and semantic_by_file.get(k,set())&safe.get(role,{role})]
  if not choices and optional:return None,True
  if not choices:raise RuntimeError("Cannot show required object, no matching real source: "+role+" / "+name)
  return choices[0],True
 inventory=[]
 for i,beat in enumerate(SHOTS):
  primary,fallback=resolve(beat["source_file"],beat)
  other=None;secondary_fallback=False
  if beat.get("second_file"):
   other,secondary_fallback=resolve(beat["second_file"],beat,optional=True)
   if other and other["meta"]["image_sha256"]==primary["meta"]["image_sha256"]:
    other=None
  inventory.append((primary,other,fallback,secondary_fallback))
 all_credits=[]
 for i,(beat,(p,q,fb,fbs)) in enumerate(zip(SHOTS,inventory),1):
  for pos,item,was_sub in [("A",p,fb),("B",q,fbs)]:
   if item:
    all_credits.append({"beat":i,"position":pos,"requested_file":beat["source_file"] if pos=="A" else beat.get("second_file"),
      "substituted":was_sub,**item["meta"]})
 (OUT/"PHOTO_CREDITS_V6.json").write_text(json.dumps(all_credits,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 (OUT/"PHOTO_CREDITS_V6.txt").write_text("REAL WIKIMEDIA COMMONS IMAGES — license and author credits.\n"+
  "\n".join(f'{x["beat"]:02d}{x["position"]}. {x["file"]} | {x["photographer"]} | {x["license"]} | {x["commons_page"]} | {x.get("license_url","")}' for x in all_credits)+"\n",encoding="utf8")
 # Google Gemini must be generated after genuine photo rights / QA preflight.
 audio,timed=synthesize(script,OUT/"audio")
 duration=len(audio)/24000
 if not 105<=duration<=235:
  raise RuntimeError(f"Voice duration invalid: {duration}")
 # Gemini voice alignment is sentence-level; some editorial beats contain two
 # or three written sentences. Group them by exact spoken text without
 # re-synthesizing or changing a single recorded sample.
 sentence_segments=len(timed)
 grouped=[];pos=0
 for beat in SHOTS:
  wanted=re.sub(r"\s+"," ",beat["text"]).strip()
  collected=[]
  while pos<len(timed):
   collected.append(timed[pos]);pos+=1
   joined=" ".join(x[0] for x in collected).strip()
   if joined==wanted:
    grouped.append((wanted,collected[0][1],collected[-1][2]))
    break
   if len(joined)>len(wanted)+12:
    raise RuntimeError("Google voice segment differs from storyboard: "+joined[:90])
  else:
   raise RuntimeError("Ran out of timed segments before beat "+str(len(grouped)+1))
 if pos!=len(timed) or len(grouped)!=len(SHOTS):
  raise RuntimeError(f"Extra audio segments {len(timed)}; grouped only {len(grouped)} beats")
 print("VOICE_SENTENCES_GROUPED",sentence_segments,"->",len(grouped),"beats",flush=True)
 timed=grouped
 alignment=json.loads((OUT/"audio"/"ALLINEAMENTO_VOCE.json").read_text(encoding="utf8"))
 fraction=alignment.get("matched_fraction") or 0
 if alignment.get("method")!="asr_with_interpolation" or fraction<.65:
  raise RuntimeError("ASR alignment not reliable enough for video")
 print("VOICE_V6_OK",round(duration,3),"seconds",len(timed),"sentences",round(fraction,3),flush=True)
 fps=FPS
 clips=[]; timeline=[];canvases=[]
 # Determine 55–65 cuts from genuine voice timecodes; never blindly cut every fixed N seconds.
 for i,((spoken,a,b),beat,(photo,other,fb,fbs)) in enumerate(zip(timed,SHOTS,inventory)):
  if spoken!=beat["text"]:raise RuntimeError("Actual Google voice text mismatch at "+str(i+1))
  left=0 if i==0 else (timed[i-1][2]+a)/2
  right=duration if i==len(timed)-1 else (b+timed[i+1][1])/2
  seconds=right-left
  pieces=[(photo,seconds,False)]
  if other and seconds>=4.4:
   frac=.46 if i==11 else .52
   pieces=[(photo,seconds*frac,False),(other,seconds*(1-frac),True)]
  current=left
  for k,(part,secs,is_insert) in enumerate(pieces):
   canvas=MEDIA/(f"canvas_{i:02d}_{k}.jpg")
   make_canvas(part["path"],canvas,beat,i,is_title=(i==0 and k==0),
               is_insert=is_insert)
   canvases.append(canvas)
   frames=max(1,round(secs*fps))
   clip=OUT/(f"shot_{i:02d}_{k}.mp4")
   move=beat.get("motion","push") if k==0 else ("pull" if i%2 else "pan_right")
   vf=zoom_filter(frames,len(clips),move)
   shell(["ffmpeg","-hide_banner","-loglevel","error","-y",
     "-loop","1","-framerate",fps,"-i",canvas,"-vf",vf,
     "-frames:v",frames,"-an","-c:v","libx264","-pix_fmt","yuv420p",
     "-preset","veryfast","-crf","21","-r",fps,clip])
   clips.append(clip)
   timeline.append({"beat":i+1,"shot":len(clips),"spoken":spoken,
      "source":part["meta"]["commons_page"],"sha256":part["meta"]["image_sha256"],
      "semantic":beat["semantic"],"chapter":beat["chapter"],"motion":move,
      "visual_start":round(current,3),"visual_end":round(current+secs,3),
      "voice_begin":round(a,3),"voice_end":round(b,3),
      "requested_role":beat["presentation"],"secondary":is_insert,
      "source_is_reconstruction":beat["semantic"]=="reconstruction",
      "fallback_source":(fb if k==0 else fbs)})
   current+=secs
 if len(clips)<42:raise RuntimeError(f"V6 cut gate failed: only {len(clips)} shots")
 if not any(row["source_is_reconstruction"] for row in timeline):
  raise RuntimeError("Labelled color reconstruction missing")
 print("CUT_GATE_PASS",len(clips),"actual camera shots",flush=True)
 concat=OUT/"concat.txt"
 concat.write_text("".join("file '"+str(c.absolute())+"'\n" for c in clips),encoding="utf8")
 silent=OUT/"silent_v6.mp4"
 shell(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0",
    "-i",concat,"-c","copy",silent])
 original_music(duration,OUT/"score_original_v6.wav")
 movie=OUT/"GIULIANO_TERRACOTTA_V6_CINEMATIC.mp4"
 shell(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",silent,
   "-i",OUT/"audio"/"VOCE.wav","-i",OUT/"score_original_v6.wav",
   "-filter_complex","[1:a]acompressor=threshold=-22dB:ratio=2.3:attack=6:release=160,volume=1.17[voice];[2:a]volume=0.18[music];[voice][music]amix=inputs=2:duration=first:dropout_transition=0,alimiter=limit=0.95[a]",
   "-map","0:v:0","-map","[a]","-c:v","copy","-c:a","aac","-b:a","192k","-ar","48000","-shortest","-movflags","+faststart",movie])
 shell(["ffmpeg","-hide_banner","-loglevel","error","-xerror","-i",movie,"-f","null","-"])
 mobile=OUT/"GIULIANO_TERRACOTTA_V6_ANDROID.mp4"
 shell(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",movie,
   "-vf","scale=720:1280:flags=lanczos","-c:v","libx264","-preset","veryfast","-crf","29",
   "-c:a","aac","-b:a","112k","-movflags","+faststart",mobile])
 shell(["ffmpeg","-hide_banner","-loglevel","error","-xerror","-i",mobile,"-f","null","-"])
 hero=inventory[1][0]["path"]
 cover_from(hero,OUT/"COVER_V6.jpg")
 contact_sheet(canvases,OUT/"CONTACT_SHEET_V6.jpg")
 probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries",
 "format=duration,size:stream=codec_name,width,height,r_frame_rate","-of","json",str(movie)],text=True))
 qa={"status":"MP4_FULL_DECODE_PASS_ARTISTIC_REVIEW_REQUIRED",
    "filename":movie.name,"sha256":sha(movie),"duration_seconds":duration,
    "format":probe,"camera_shots":len(timeline),"narrative_beats":len(SHOTS),
    "unique_actual_photo_count":len({x["sha256"] for x in timeline}),
    "voice":"Google Gemini Gacrux newly synthesized",
    "voice_ASR_method":alignment.get("method"),"voice_ASR_matched_fraction":fraction,
    "source_licenses_verified":True,"music":"original generated instrumental score",
    "historical_clips_ai_generated":0,"needs_review":True,"published":False,
    "scene_timeline":timeline}
 (OUT/"QA_V6.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 (OUT/"DESCRIZIONE_SOCIAL_IT.txt").write_text(
  "THE TERRACOTTA ARMY · Un esercito rimasto sotto terra per oltre duemila anni. "
  "Scoperto nel 1974: statue dipinte, armi vere, migliaia di punte di freccia "
  "e una camera funeraria che nessuno ha ancora scavato. "
  "Documentario di Giuliano. Fonti: UNESCO, UCL, Metropolitan Museum. "
  "Ricostruzioni moderne dei colori esplicitamente segnalate. "
  "#Storia #Archeologia #Cina #TerracottaArmy\n",encoding="utf8")
 (OUT/"README.txt").write_text(
  "GIULIANO - TERRACOTTA ARMY V6 DIRECTOR CUT.\n"
  f"Duration {duration:.1f}s | real photos {qa['unique_actual_photo_count']} | actual cuts {len(timeline)}\n"
  "1080x1920 master; 720x1280 lightweight Android version; original score; new Google Gacrux voice.\n"
  "Narrative matched to individual photo topics. No invented footage, no publishing.\n"
  "ffmpeg full decode MP4: PASS. Creative review: REQUIRED.\n",encoding="utf8")
 pack=OUT/"GIULIANO_TERRACOTTA_V6_COMPLETO.zip"
 with zipfile.ZipFile(pack,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
  for f in [movie,mobile,OUT/"COVER_V6.jpg",OUT/"CONTACT_SHEET_V6.jpg",
       OUT/"QA_V6.json",OUT/"PHOTO_CREDITS_V6.json",OUT/"PHOTO_CREDITS_V6.txt",
       OUT/"DESCRIZIONE_SOCIAL_IT.txt",OUT/"README.txt",
       ROOT/"giuliano"/"terracotta_v6"/"VOCE_DOCUMENTARIO_V6.txt",STORYBOARD_PATH]:
   z.write(f,f.name)
 with zipfile.ZipFile(pack) as z:
  if z.testzip():raise RuntimeError("Complete package integrity test failed")
 print(json.dumps({"result":"SUCCESS_V6_MP4","duration":duration,"cuts":len(timeline),
  "unique_photos":qa["unique_actual_photo_count"],"master_size":movie.stat().st_size,
  "mobile_size":mobile.stat().st_size,"zip_size":pack.stat().st_size,
  "master_sha256":sha(movie),"mobile_sha256":sha(mobile),"zip_sha256":sha(pack)}),flush=True)
if __name__=="__main__": main()
