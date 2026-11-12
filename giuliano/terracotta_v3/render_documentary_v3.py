#!/usr/bin/env python3
"""Giuliano V3 documentary film: original factual narration, 40 proof-matched scenes, source-verified photography.
Strict no fake archival footage, no uncontrolled AI image substitution, no publication.
"""
import hashlib, html, json, math, os, re, subprocess, sys, time, urllib.parse, zipfile
from pathlib import Path
import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import gemini_voice
from gemini_voice import synthesize
gemini_voice.STYLE = "An authoritative Italian historical documentary television narrator for Sky Arte / National Geographic-style educational history. Clear factual broadcast delivery, warm confident male voice with sober cinematic intensity and engaging pace, precise diction, articulate historical dates and names. Read the statements as informative journalism, not as a poem or artwork critique; no theatrical narration, no overly slow pauses, no intimate whispers, no fake suspense. Slightly brisk natural news-documentary tempo, maintaining clarity."

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"output"/"giuliano_terracotta_v3"
MEDIA=OUT/"media"
W,H,FPS=1080,1920,24
# Real museum photos, independently described/licensed at Wikimedia Commons.
# The order matches the exact sentence order in the narration.
STORYBOARD_PATH=ROOT/"giuliano"/"terracotta_v3"/"SHOTS_DOCUMENTARY.json"
PLAN=json.loads(STORYBOARD_PATH.read_text(encoding="utf8"))
SHOTS=PLAN["shots"]
FILES=[row["source_file"] for row in SHOTS]
if len(SHOTS)<38 or len(set(FILES))<30:
 raise RuntimeError("V3: must have 38+ scenes and 30+ distinct authentic sources")
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

def make_canvas(path,out,beat,i):
 im=ImageOps.exif_transpose(Image.open(path)).convert("RGB")
 # Crisp full-bleed real photographs: do not place small horizontal photos over a large blurry background.
 # The camera sees the authentic artefact; no AI reconstruction, no fabricated museum frames.
 crop_width,crop_height=1200,2134
 focusx=.48 if i%5==0 else (.53 if i%5==3 else .50)
 focusy=.47 if beat["semantic"] in ("portrait","armour","officer","archer_standing") else .52
 if beat["semantic"]=="chariot_detail":
  w,h=im.size
  im=im.crop((int(w*.19),int(h*.08),int(w*.82),int(h*.92)))
 framed=ImageOps.fit(im,(crop_width,crop_height),Image.Resampling.LANCZOS,centering=(focusx,focusy))
 framed=framed.resize((1200,2134),Image.Resampling.LANCZOS)
 # Short evidence chips are placed in the safe lower area, never presented as dialogue subtitles.
 text=(beat.get("overlay") or "").strip()
 if text:
  overlay=Image.new("RGBA",framed.size,(0,0,0,0))
  dr=ImageDraw.Draw(overlay)
  dr.rounded_rectangle((60,1790,1140,1900),radius=14,fill=(9,14,20,205),outline=(166,140,93,115),width=2)
  fs=46 if len(text)<24 else 36
  dr.text((85,1817),text,font=font(fs,True),fill=(247,232,201,255))
  framed=Image.alpha_composite(framed.convert("RGBA"),overlay).convert("RGB")
 framed.save(out,quality=94,subsampling=0)

def cover_from(photograph,path):
 im=ImageOps.exif_transpose(Image.open(photograph)).convert("RGB")
 im=ImageOps.fit(im,(W,H),Image.Resampling.LANCZOS,centering=(.50,.43)).convert("RGBA")
 sh=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(sh)
 for y in range(600,H):
  alpha=int(236*((y-600)/(H-600))**1.35)
  d.line((0,y,W,y),fill=(7,11,18,alpha))
 d.rectangle((0,0,W,120),fill=(0,0,0,95))
 im=Image.alpha_composite(im,sh);d=ImageDraw.Draw(im)
 d.text((70,72),"CHINA  ·  ARCHAEOLOGY",font=font(30,True),fill="#e1c999")
 d.text((64,1320),"THE",font=font(82,True),fill="#f2ddad")
 d.text((60,1428),"TERRACOTTA",font=font(113,True),fill="#fff6dc")
 d.text((62,1562),"ARMY",font=font(156,True),fill="#fff6dc")
 d.line((70,1750,W-70,1750),fill="#cbad72",width=3)
 d.text((70,1790),"THE EMPEROR'S SILENT LEGION",font=font(36),fill="#f1e2c6")
 im.convert("RGB").save(path,quality=95,subsampling=0)

def contact_sheet(canvases,out):
 width=1300;cols=8;cellw=160;cellh=300
 rows=(len(canvases)+cols-1)//cols
 sheet=Image.new("RGB",(width,rows*cellh+20),(15,19,24));d=ImageDraw.Draw(sheet)
 for i,p in enumerate(canvases):
  im=Image.open(p).convert("RGB")
  im.thumbnail((148,265),Image.Resampling.LANCZOS)
  x=(i%cols)*cellw+8;y=(i//cols)*cellh+8
  sheet.paste(im,(x,y))
  d.text((x,y+269),str(i+1),fill="#ddd1b8",font=font(18,True))
 sheet.save(out,quality=92)

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
 OUT.mkdir(parents=True,exist_ok=True);MEDIA.mkdir(exist_ok=True)
 script=(ROOT/"giuliano"/"terracotta_v3"/"SCENEGGIATURA_IT.txt").read_text(encoding="utf-8").strip()
 expected="\n".join(s["narration"] for s in SHOTS)
 if script!=expected:
  raise RuntimeError("V3 script differs from the exactly synced 40-shot documentary storyboard")
 print("V3_SOURCE_PREFLIGHT",len(SHOTS),"shots",len(set(FILES)),"different target photos",flush=True)
 unique_names=list(dict.fromkeys(FILES))
 info_list=fetch_metadata(unique_names)
 info_by_name=dict(zip(unique_names,info_list))
 photos=[None]*len(SHOTS); seen={}
 for i,beat in enumerate(SHOTS):
  filename=beat["source_file"]
  source=info_by_name.get(filename)
  dest=MEDIA/("raw_%02d.jpg"%i)
  if filename in seen:
   prev=seen[filename]
   dest.write_bytes((MEDIA/("raw_%02d.jpg"%prev)).read_bytes())
   photos[i]={**photos[prev],"stage_index":i,"duplicate_photo":True}
   continue
  if source is None:
   print("SOURCE_METADATA_UNAVAILABLE",i+1,filename,flush=True)
   continue
  try:
   meta=download_commons(source,dest)
   meta["stage_index"]=i
   photos[i]=meta;seen[filename]=i
   print("VERIFIED_REAL_PHOTO",i+1,filename,meta["license"],flush=True)
   time.sleep(.25)
  except Exception as exc:
   print("SINGLE_SOURCE_FAILED",i+1,filename,str(exc)[:180],flush=True)
 # Semantically precise fallback only. Never substitute kneeling archers for standing archers.
 role_matches={
   "formation":{"formation","pit"},
   "portrait":{"portrait","armour","officer"},
   "armour":{"armour","officer"},
   "officer":{"officer","armour"},
   "detail":{"detail","armour"},
   "archer_standing":{"archer_standing"},
   "archer_kneeling":{"archer_kneeling"},
   "excavation":{"excavation"},
   "horse":{"horse"},
   "pigment":{"pigment"},
   "reconstruction":{"reconstruction"},
   "weapons":{"weapons"},
   "mound":{"mound"},
   "pit":{"pit","formation"},
   "acrobat":{"acrobat"},
   "chariot":{"chariot","chariot_detail"},
   "chariot_detail":{"chariot","chariot_detail"}
 }
 for i,photo in enumerate(photos):
  if photo is not None:continue
  role=SHOTS[i]["semantic"]
  candidates=[j for j,p in enumerate(photos) if p is not None and SHOTS[j]["semantic"] in role_matches.get(role,{role})]
  if not candidates:
   raise RuntimeError("No safe source matches spoken subject "+role+" in scene "+str(i+1))
  j=min(candidates,key=lambda t:abs(t-i))
  target=MEDIA/("raw_%02d.jpg"%i)
  target.write_bytes((MEDIA/("raw_%02d.jpg"%j)).read_bytes())
  photos[i]={**photos[j],"stage_index":i,"substituted_source":True,
    "requested_file_unavailable":SHOTS[i]["source_file"],"reused_from_scene":j+1}
  print("SAME_SUBJECT_VERIFIED_FALLBACK",i+1,"from",j+1,role,flush=True)
 count_distinct=len({x["image_sha256"] for x in photos})
 if count_distinct<29:
  raise RuntimeError(f"V3 source quality gate: only {count_distinct} distinct photographs; min 29")
 print("PHOTO_QA_PASS",len(SHOTS),"cuts",count_distinct,"distinct photo files",flush=True)
 (OUT/"PHOTO_CREDITS_V3.json").write_text(json.dumps(photos,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 (OUT/"PHOTO_CREDITS_V3.txt").write_text("REAL PHOTOS (Wikimedia Commons). Photo crops and digital camera movement are editorial.\n"+
   "\n".join(f'{x["stage_index"]+1:02}. {x["file"]} | {x["photographer"]} | {x["license"]} | {x["commons_page"]} | {x["license_url"]}' for x in photos)+"\n",encoding="utf8")
 canvases=[]
 for i,(beat,p) in enumerate(zip(SHOTS,photos)):
  target=MEDIA/("scene_%02d.jpg"%i)
  make_canvas(MEDIA/("raw_%02d.jpg"%i),target,beat,i)
  canvases.append(target)
 # Genuine close-up face for the cinema title, not a distant visitor hall.
 hero_index=9
 cover_from(MEDIA/("raw_%02d.jpg"%hero_index),OUT/"COVER_V3.jpg")
 contact_sheet(canvases,OUT/"CONTACT_SHEET_V3.jpg")
 print("ASSET_REVIEW_READY",len(canvases),flush=True)
 # One human-sounding documentary voice Google Gacrux, only AFTER validated photo bank.
 audio,timed=synthesize(script,OUT/"audio")
 duration=len(audio)/24000
 if not (115<=duration<=220) or len(timed)!=len(SHOTS):
  raise RuntimeError(f"V3 invalid voice length/alignment: seconds={duration},lines={len(timed)}")
 alignment=json.loads((OUT/"audio"/"ALLINEAMENTO_VOCE.json").read_text())
 if alignment.get("method")!="asr_with_interpolation" or (alignment.get("matched_fraction") or 0)<.65:
  raise RuntimeError("Real audio sentence sync not reliable; no ready-made MP4")
 for i,(line,a,b) in enumerate(timed):
  if line!=SHOTS[i]["narration"]:raise RuntimeError("V3 sentence mismatch "+str(i+1))
 print("VOICE_V3_VERIFIED",round(duration,2),len(timed),alignment.get("matched_fraction"),flush=True)
 intro=round(float(PLAN.get("intro_seconds",2.35))*FPS)/FPS
 titleframes=round(intro*FPS)
 title=OUT/"title.mp4"
 shell(["ffmpeg","-hide_banner","-loglevel","error","-y","-loop","1","-framerate",FPS,
     "-i",OUT/"COVER_V3.jpg","-vf",
     f"zoompan=z='min(1.0+on*.00016,1.06)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={titleframes}:s={W}x{H}:fps={FPS},format=yuv420p",
     "-frames:v",titleframes,"-c:v","libx264","-pix_fmt","yuv420p","-preset","veryfast","-crf","18",title])
 scenes=[];clips=[title]
 for i,((spoken,a,b),beat,photo) in enumerate(zip(timed,SHOTS,photos)):
  left=0 if i==0 else (timed[i-1][2]+a)/2
  right=duration if i==len(timed)-1 else (b+timed[i+1][1])/2
  frames=max(1,round(FPS*max(.25,right-left)))
  clip=OUT/("scene_%02d.mp4"%i)
  inc=.000020 if i%3 else .000030
  vf=(f"zoompan=z='min(1.008+on*{inc:.6f},1.085)':"
      f"x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={frames}:"
      f"s={W}x{H}:fps={FPS},format=yuv420p")
  shell(["ffmpeg","-hide_banner","-loglevel","error","-y","-loop","1","-framerate",FPS,
        "-i",canvases[i],"-vf",vf,"-frames:v",frames,"-an","-c:v","libx264",
        "-pix_fmt","yuv420p","-preset","veryfast","-crf","20","-r",FPS,clip])
  clips.append(clip)
  scenes.append({"scene":i+1,"sentence":spoken,"subject":beat["semantic"],
    "source":photo["commons_page"],"licence":photo["license"],
    "voice_start_sec":round(a+intro,3),"voice_end_sec":round(b+intro,3),
    "visual_start_sec":round(left+intro,3),"visual_end_sec":round(right+intro,3),
    "title_or_info_text":beat.get("overlay",""),
    "same_subject_fallback":bool(photo.get("substituted_source")),
    "frame_source_sha256":photo["image_sha256"]})
 concat=OUT/"concat.txt"
 concat.write_text("".join("file '"+str(f.absolute())+"'\n" for f in clips))
 no_audio=OUT/"video_silent.mp4"
 shell(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0",
       "-i",concat,"-c","copy",no_audio])
 original_music(duration+intro,OUT/"original_music.wav")
 movie=OUT/"THE_TERRACOTTA_ARMY_GIULIANO_DOCUMENTARY_V3.mp4"
 delay=round(intro*1000)
 shell(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",no_audio,
       "-i",OUT/"audio"/"VOCE.wav","-i",OUT/"original_music.wav",
       "-filter_complex",
       f"[1:a]adelay={delay}|{delay},volume=1.0[voice];[2:a]volume=0.23[music];[voice][music]amix=inputs=2:duration=first:dropout_transition=0[a]",
       "-map","0:v:0","-map","[a]","-c:v","copy","-c:a","aac","-b:a","192k",
       "-ar","48000","-shortest","-movflags","+faststart",movie])
 shell(["ffmpeg","-hide_banner","-loglevel","error","-xerror","-i",movie,"-f","null","-"])
 probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries",
   "format=duration,size:stream=codec_name,width,height,r_frame_rate","-of","json",movie],text=True))
 qa={
  "status":"TECHNICAL_MP4_PASS_ARTISTIC_REVIEW_PENDING",
  "video_sha256":sha(movie),"probe":probe,
  "voice":"Google Gemini Gacrux (new Italian broadcast-documentary performance)",
  "voice_seconds":duration,"intro_seconds":intro,
  "audio_alignment":"real Whisper ASR, sentence-match fraction "+str(alignment.get("matched_fraction")),
  "scene_count":len(scenes),"different_photo_count":count_distinct,
  "human_subject_identity_claims":False,"source_rights_checked":True,
  "statistical_claims_source":"UNESCO / UCL / National Geographic / TUM",
  "music":"original royalty-free synthesized film soundscape",
  "publication_authorized":False,
  "note":"This video uses animated photographic framing, NOT actual moving footage or recreated historical actors",
  "scene_to_sentence_alignment":scenes}
 (OUT/"QA_V3.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 (OUT/"TESTO_SOCIAL.txt").write_text(
  "THE TERRACOTTA ARMY | 1974: uno scavo per un pozzo svela un esercito di migliaia di guerrieri d'argilla. "
  "Erano colorati, possedevano vere armi in bronzo e proteggevano la tomba del primo imperatore cinese. "
  "La camera sepolcrale centrale non è stata ancora scavata. "
  "Fonti: UNESCO, UCL, TUM e National Geographic. Fotografie e licenze nel pacchetto. #Archeologia #Cina #Storia #TerracottaArmy\n",
  encoding="utf8")
 (OUT/"README.txt").write_text(
  "GIULIANO — THE TERRACOTTA ARMY — DOCUMENTARIO V3 (REVISIONE)\n"
  f"{len(scenes)} tagli sincronizzati con la voce, {count_distinct} fotografie autentiche distinte.\n"
  "Apertura con titolo cinematografico, montaggio verticale 1080x1920.\n"
  "Ciascuna frase è abbinata al soggetto che descrive, senza inviti a guardare immagini inesistenti.\n"
  "Voce: Google Gemini Gacrux, interpretazione giornalistica storico-documentaria.\n"
  "Controllo FFmpeg: PASS. Revisione artistica umana: DA COMPLETARE. Non pubblicato.\n"
  "Le immagini sono fotografie con movimento di montaggio, non filmati storici animati.\n",
  encoding="utf8")
 pack=OUT/"GIULIANO_TERRACOTTA_V3_VIDEO_COVER_SOCIAL.zip"
 with zipfile.ZipFile(pack,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
  for p in [movie,OUT/"COVER_V3.jpg",OUT/"CONTACT_SHEET_V3.jpg",
      OUT/"README.txt",OUT/"TESTO_SOCIAL.txt",OUT/"PHOTO_CREDITS_V3.txt",
      OUT/"PHOTO_CREDITS_V3.json",OUT/"QA_V3.json",
      ROOT/"giuliano"/"terracotta_v3"/"SCENEGGIATURA_IT.txt",STORYBOARD_PATH]:
   z.write(p,p.name)
 with zipfile.ZipFile(pack) as z:
  if z.testzip() is not None:raise RuntimeError("ZIP CRC failed")
 print(json.dumps({"result":"SUCCESS_V3_MP4","duration_seconds":duration+intro,
   "photos_unique":count_distinct,"cuts":len(scenes),"mp4_sha256":sha(movie),
   "zip_sha256":sha(pack),"mp4_bytes":movie.stat().st_size,"zip_bytes":pack.stat().st_size}),flush=True)
if __name__=="__main__": main()
