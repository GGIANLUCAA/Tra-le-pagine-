#!/usr/bin/env python3
"""Giuliano / Terracotta Army pilot. Original script; genuine Commons photographs.
No generated historical footage, no publication, no paid video calls.
"""
import hashlib, html, json, math, os, re, subprocess, sys, time, urllib.parse, zipfile
from pathlib import Path
import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import gemini_voice
from gemini_voice import synthesize
gemini_voice.STYLE = "natural, compelling Italian factual documentary voice for a premium social history film; warm mature calm authority, dynamic pace, clear concrete emphasis, concise pauses, not a theatrical or sentimental audiobook, no exaggerated drama"

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"output"/"giuliano_terracotta_v2"
MEDIA=OUT/"media"
W,H,FPS=720,1280,20
# Real museum photos, independently described/licensed at Wikimedia Commons.
# The order matches the exact sentence order in the narration.
STORYBOARD_PATH=ROOT/"giuliano"/"terracotta_v2"/"STORYBOARD.json"
PLAN=json.loads(STORYBOARD_PATH.read_text(encoding="utf8"))
SHOTS=PLAN["shots"]
FILES=[row["file"] for row in SHOTS]
if len(SHOTS)<28 or len(set(FILES))<26:
 raise RuntimeError("Need 28+ shots and 26+ unique genuine photos")
UA="GiulianoTerracottaFilm/1.0 (editorial Wikimedia Commons image attribution)"
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
 for start in range(0,len(filenames),35):
  group=filenames[start:start+35]
  params={"action":"query","format":"json","prop":"imageinfo",
       "iiprop":"url|extmetadata|size","iiurlwidth":"1280",
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
   raise RuntimeError("Commons licensing or metadata missing for "+name)
 return [result[name.replace("_"," ").casefold()] for name in filenames]

def download_commons(metadata,dest):
 # Licensed original remains linked to Wikimedia. Alternate delivery endpoints
 # only resize/copy the SAME identified original to avoid GitHub runner 429.
 original=metadata["url"]
 delivery=[
  ("weserv","https://images.weserv.nl/?"+urllib.parse.urlencode({"url":original,"w":"1280","output":"jpg","q":"91"})),
  ("wsrv","https://wsrv.nl/?"+urllib.parse.urlencode({"url":original,"w":"1280","output":"jpg","q":"91"})),
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

def font(sz):
 for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
           "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
  if Path(p).exists():return ImageFont.truetype(p,sz)
 return ImageFont.load_default()
def make_canvas(path,out,shot_type):
 im=Image.open(path)
 im=ImageOps.exif_transpose(im).convert("RGB")
 # Photographic framing: full-bleed portrait detail; wide excavations remain legible.
 bg=ImageOps.fit(im,(900,1600),method=Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(25))
 bg=Image.blend(bg,Image.new("RGB",bg.size,(9,13,18)),.25)
 if im.width/im.height < .76:
  fg=ImageOps.fit(im,(900,1600),method=Image.Resampling.LANCZOS)
  bg=fg
 else:
  fg=ImageOps.contain(im,(900,1420),method=Image.Resampling.LANCZOS)
  left=(900-fg.width)//2; top=(1600-fg.height)//2
  bg.paste(fg,(left,top))
 if shot_type=="modern_reconstruction_of_colors":
  d=ImageDraw.Draw(bg)
  d.rounded_rectangle((22,1480,540,1555),radius=10,fill=(7,13,20))
  d.text((42,1497),"COLOR RECONSTRUCTION",font=font(30),fill="#e7ddc5")
 bg.save(out,quality=94,subsampling=0)
def cover_from(canvas,path):
 im=Image.open(canvas).convert("RGB").resize((720,1280))
 overlay=Image.new("RGBA",im.size,(0,0,0,0))
 d=ImageDraw.Draw(overlay)
 for y in range(620,1280):
  opacity=int(220*(y-620)/660)
  d.line((0,y,720,y),fill=(4,8,11,opacity))
 im=Image.alpha_composite(im.convert("RGBA"),overlay)
 d=ImageDraw.Draw(im)
 d.text((38,965),"THE ARMY",font=font(71),fill="#f6e9cb")
 d.text((38,1050),"THAT NEVER LIVED",font=font(42),fill="#f6e9cb")
 d.text((40,1155),"THE TERRACOTTA WARRIORS",font=font(23),fill="#e3d2b0")
 im.convert("RGB").save(path,quality=94)

def original_music(duration,out):
 # Entirely original understated instrumental soundscape, no sampled recordings.
 sr=24000; n=int((duration+2)*sr); t=np.arange(n,dtype=np.float32)/sr
 music=np.zeros(n,np.float32)
 for f,amp in [(73.42,.032),(110.0,.012),(146.83,.021),(174.61,.012),(220,.014)]:
  music += amp*np.sin(2*np.pi*f*t + .15*np.sin(2*np.pi*.061*t))
 for second,note in [(2,293.66),(10,349.23),(18,440),(29,349.23),(43,293.66),
                    (55,261.63),(66,220),(78,293.66),(90,220),(104,146.83)]:
  if second > duration:break
  a=int(second*sr);b=min(n,a+int(2.5*sr))
  tt=np.arange(b-a,dtype=np.float32)/sr
  music[a:b]+=.016*np.exp(-tt*1.5)*np.sin(2*np.pi*note*tt)
 fade=np.minimum(1,np.minimum(np.arange(n)/float(sr*2),np.arange(n)[::-1]/float(sr*3)))
 music*=np.clip(fade,0,1)
 import soundfile as sf
 sf.write(out,music,sr)
def main():
 OUT.mkdir(parents=True,exist_ok=True); MEDIA.mkdir(exist_ok=True)
 script=(ROOT/"giuliano"/"terracotta_v2"/"VOCE_DOCUMENTARIO_IT.txt").read_text(encoding="utf-8").strip()
 expected="\n\n".join(x["text"] for x in SHOTS)
 if script!=expected:
  raise RuntimeError("Voice/storyboard mismatch; refusing unsynchronized production")
 print("BEATS:",len(SHOTS),"UNIQUE SOURCES:",len(set(FILES)),flush=True)
 # Verify metadata and all pictures before a paid/limited Google voice request.
 infos=fetch_metadata(FILES)
 photos=[]
 rate_limited=False
 for i,(beat,info) in enumerate(zip(SHOTS,infos)):
  target=MEDIA/("raw_%02d.jpg"%i)
  meta=None
  if not rate_limited:
   try:
    meta=download_commons(info,target)
    print("LICENSED",i+1,"of",len(SHOTS),meta["file"],meta["license"],flush=True)
    time.sleep(.5)
   except Exception as error:
    # Site rate limits only affect MEDIA retrieval; no need to regenerate valid photos/voice.
    # Never substitute an unrelated historic subject: take a previously licensed image
    # with the same documentary role (e.g. tomb mound for tomb mound).
    rate_limited=True
    print("SOURCE_RATE_LIMIT_FALLBACK",i+1,type(error).__name__,str(error)[:180],flush=True)
  if meta is None:
   role=beat["subject"]
   groups={"mound":{"mound"},"wide_end":{"wide_hook","pit1"},"paint_remains":{"paint","paint_trace"},
           "chariot":{"chariot"},"archer":{"archer"},"weapons":{"weapons"}}
   allowed=groups.get(role,{role})
   possibles=[j for j in range(len(photos)) if SHOTS[j]["subject"] in allowed]
   if not possibles:
    raise RuntimeError("No previously licensed photo with matching topic for scene "+str(i+1))
   prev=possibles[-1]
   target.write_bytes((MEDIA/("raw_%02d.jpg"%prev)).read_bytes())
   meta={**photos[prev],"substituted_source":True,"replacement_for":info["file"],
         "fallback_source_index":prev+1}
   print("MATCHED_SOURCE_REUSED",i+1,"from",prev+1,"role",role,flush=True)
  meta["stage_index"]=i
  photos.append(meta)
 if len({x["image_sha256"] for x in photos})<24:
  raise RuntimeError("Insufficient different authentic photos; do not produce a dull repeated montage")
 print("IMAGE_PREFLIGHT",len(photos),"cuts",len({x["image_sha256"] for x in photos}),"unique real photos",flush=True)
 (OUT/"ATTRIBUZIONI_FOTO.json").write_text(json.dumps(photos,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 (OUT/"ATTRIBUZIONI_FOTO.txt").write_text(
  "Fotografie REALI Wikimedia Commons; ritagli, fondali sfocati e camera digitale.\n"+
  "\n".join(f'{x["stage_index"]+1:02d}. {x["file"]} | {x["photographer"]} | {x["license"]} | {x["commons_page"]} | {x["license_url"]}' for x in photos)+"\n",encoding="utf8")
 imagefiles=[]
 for i,(beat,photo) in enumerate(zip(SHOTS,photos)):
  canvas=MEDIA/("canvas_%02d.jpg"%i)
  make_canvas(MEDIA/("raw_%02d.jpg"%i),canvas,beat["subject"])
  imagefiles.append(canvas)
 cover_from(imagefiles[0],OUT/"COVER_V2.jpg")
 print("PHOTO_PREFLIGHT_PASSED",len(photos),flush=True)
 audio,timed=synthesize(script,OUT/"audio")
 duration=len(audio)/24000
 if not 75<=duration<=145 or len(timed)!=len(SHOTS):
  raise RuntimeError(f"Voice timing validation failed: duration={duration}, aligned={len(timed)}")
 print("VOICE_OK",duration,len(timed),flush=True)
 # Timecodes come from ASR word-aligned real Gacrux audio, not invented.
 align_path=OUT/"audio"/"ALLINEAMENTO_VOCE.json"
 alignment=json.loads(align_path.read_text(encoding="utf8"))
 if alignment.get("method")!="asr_with_interpolation" or (alignment.get("matched_fraction") or 0)<.65:
  raise RuntimeError("ASR alignment was not adequate, abort synced render")
 segs=[];scenes=[]
 for i,((spoken,a,b),beat,photo) in enumerate(zip(timed,SHOTS,photos)):
  if spoken!=beat["text"]:
   raise RuntimeError("Scene n"+str(i+1)+" did not match speech content")
  start=0 if i==0 else (timed[i-1][2]+a)/2
  end=duration if i==len(timed)-1 else (b+timed[i+1][1])/2
  seconds=max(.5,end-start)
  frames=max(1,round(FPS*seconds))
  output=OUT/("shot_%02d.mp4"%i)
  # Tiny, motivated documentary camera movement; alternate subtle push/hold.
  inc=.000025 if i%2==0 else .000016
  vf=(f"zoompan=z='min(1.009+on*{inc:.6f},1.09)':"
      f"x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={frames}:"
      f"s={W}x{H}:fps={FPS},format=yuv420p")
  shell(["ffmpeg","-hide_banner","-loglevel","error","-y",
       "-loop","1","-framerate",str(FPS),"-i",imagefiles[i],"-vf",vf,
       "-frames:v",str(frames),"-an","-c:v","libx264","-pix_fmt","yuv420p",
       "-preset","veryfast","-crf","20","-r",str(FPS),output])
  segs.append(output)
  scenes.append({"scene":i+1,"spoken_text":spoken,"subject":beat["subject"],
       "voice_start":round(a,3),"voice_end":round(b,3),
       "visual_start":round(start,3),"visual_end":round(end,3),
       "source":photo["commons_page"],"source_sha256":photo["image_sha256"]})
 concat=OUT/"concat.txt"
 concat.write_text("".join("file '"+str(x.absolute())+"'\n" for x in segs))
 base=OUT/"silent.mp4"
 shell(["ffmpeg","-hide_banner","-loglevel","error","-y",
       "-f","concat","-safe","0","-i",concat,"-c","copy",base])
 original_music(duration,OUT/"music.wav")
 movie=OUT/"GIULIANO_TERRACOTTA_DOCUMENTARIO_V2_REVIEW.mp4"
 shell(["ffmpeg","-hide_banner","-loglevel","error","-y",
       "-i",base,"-i",OUT/"audio"/"VOCE.wav","-i",OUT/"music.wav",
       "-filter_complex","[1:a]volume=1.0[voice];[2:a]volume=0.24[music];[voice][music]amix=inputs=2:duration=first:dropout_transition=0[a]",
       "-map","0:v:0","-map","[a]","-c:v","copy","-c:a","aac",
       "-b:a","160k","-ar","48000","-shortest","-movflags","+faststart",movie])
 shell(["ffmpeg","-hide_banner","-loglevel","error","-xerror","-i",movie,"-f","null","-"])
 probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries",
       "format=duration,size:stream=codec_name,width,height","-of","json",str(movie)],text=True))
 qa={"status":"RENDERED_NEEDS_ARTISTIC_REVIEW","video_sha256":sha(movie),"probe":probe,
     "voice":"Google Gemini Gacrux","audio_alignment_method":alignment.get("method"),
     "audio_matched_fraction":alignment.get("matched_fraction"),
     "scenes":scenes,"unique_photos":len({p["image_sha256"] for p in photos}),
     "frames_from_original_licensed_photos":True,"video_ai_clips":0,
     "publication_authorized":False,"source_licences_checked":True}
 (OUT/"QA_V2.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 (OUT/"TESTO_SOCIAL.txt").write_text(
  "THE TERRACOTTA ARMY — Nel 1974 un pozzo rivelò migliaia di guerrieri di argilla. "
  "Erano dipinti, avevano armi vere e custodiscono ancora segreti archeologici. "
  "Fonte: UNESCO / UCL / Wikimedia Commons.\n",encoding="utf8")
 (OUT/"README.txt").write_text(
  "DOCUMENTARIO SOCIAL V2 DI GIULIANO — PROVA DA RIVEDERE\n"
  f"Film: {len({p['image_sha256'] for p in photos})} foto reali e {len(scenes)} inquadrature, voce Google Gacrux, montaggio per frasi ASR.\\n"
  "Tutti i filmati sono movimenti editoriali sulle foto, non ricostruzioni AI.\n"
  "QA FFmpeg completo: PASS. Valutazione artistica umana: DA FARE.\n"
  "Non pubblicato. Fotografie con licenze e attribuzioni nello ZIP.\n",encoding="utf8")
 zipout=OUT/"GIULIANO_TERRACOTTA_DOCUMENTARIO_V2_PACCHETTO.zip"
 with zipfile.ZipFile(zipout,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
  for p in [movie,OUT/"COVER_V2.jpg",OUT/"README.txt",OUT/"TESTO_SOCIAL.txt",
     OUT/"ATTRIBUZIONI_FOTO.txt",OUT/"ATTRIBUZIONI_FOTO.json",OUT/"QA_V2.json",
     ROOT/"giuliano"/"terracotta_v2"/"VOCE_DOCUMENTARIO_IT.txt",
     STORYBOARD_PATH]:
   z.write(p,arcname=p.name)
 with zipfile.ZipFile(zipout) as z:
  if z.testzip():raise RuntimeError("ZIP CRC check failed")
 print(json.dumps({"duration":duration,"scenes":len(scenes),
                   "unique_photos":qa["unique_photos"],
                   "mp4_sha256":sha(movie),"zip_sha256":sha(zipout),
                   "mp4_path":str(movie),"zip_path":str(zipout)}),flush=True)
if __name__=="__main__": main()
