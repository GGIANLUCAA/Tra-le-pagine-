#!/usr/bin/env python3
"""ArtVision Critico V32. Narrated criticism in Italian, genuine Gacrux, NO GHOSTING.
Gold Master Cinema V6 and Critico V2 remain unmodified. Real painting per frame.
This is a format-specific Critico gate: the silence-only V25 Cinema gate is NOT used
because it intentionally disallows narration.
"""
from __future__ import annotations
import argparse,hashlib,io,json,math,os,pathlib,re,shutil,subprocess,sys,urllib.parse,urllib.request,zipfile
import numpy as np
import soundfile as sf
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"modules"/"artvision")]
from gemini_voice import synthesize,sentences
from identita_visiva_v6 import cover as original_v6_cover,signature as original_v6_signature
import artvision_editorial_post_v28 as editorial
CONFIG=json.loads((ROOT/"config/artvision_critico_v32_three.json").read_text(encoding="utf8"))
editorial.CATALOG=ROOT/"config/artvision_critico_v32_posts.json"
W,H,FPS=1080,1920,24
HEADER={"User-Agent":"ArtVisionCriticoV32/1.0 (+https://github.com/GGIANLUCAA/Tra-le-pagine-)","Accept":"image/jpeg,image/*;q=0.9,*/*;q=0.1"}

def sha(path):
 h=hashlib.sha256()
 with pathlib.Path(path).open("rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
 return h.hexdigest()
def get(url,maxbytes=30000000,timeout=55):
 if not url.startswith("https://"):raise ValueError("Only real HTTPS image/music originals are admissible")
 request=urllib.request.Request(url,headers=HEADER)
 with urllib.request.urlopen(request,timeout=timeout) as r:
  if r.status!=200:raise ValueError("Archive unavailable HTTP "+str(r.status))
  data=r.read(maxbytes+1)
 if len(data)>maxbytes:raise ValueError("Archive media exceeds approved limit")
 return data
def image_source(profile,dir):
 if profile["source_kind"]=="cleveland_cc0":
  a=profile["accession"]
  url="https://openaccess-cdn.clevelandart.org/"+a+"/"+a+"_print.jpg"
  # The museum accession and CC0 status were preflight checked independently.
  license_name="CC0 / Cleveland Museum of Art Open Access"
 else:
  title=profile["original_artwork_title"]
  q=urllib.parse.urlencode({"action":"query","format":"json","formatversion":"2","titles":title,
     "prop":"imageinfo","iiprop":"size|url|extmetadata","iiurlwidth":3400})
  obj=json.loads(get("https://commons.wikimedia.org/w/api.php?"+q,3000000,32))
  node=obj["query"]["pages"][0]
  info=node["imageinfo"][0]
  lic=str((info.get("extmetadata",{}).get("LicenseShortName") or {}).get("value","")).casefold()
  usage=str((info.get("extmetadata",{}).get("UsageTerms") or {}).get("value","")).casefold()
  if not any(w in lic+" "+usage for w in ("public domain","pd-art","pd-old")):
   raise ValueError("Holbein reproduction requires verified public-domain status: "+lic[:100])
  url=info.get("thumburl") or info.get("url")
  if urllib.parse.urlsplit(url).hostname not in ("upload.wikimedia.org","thumb.wikimedia.org"):
   raise ValueError("Image host no longer verified Wikimedia")
  license_name="Public Domain faithful reproduction (Commons image description)"
 data=get(url,23000000,80)
 if not data.startswith((b"\xff\xd8",b"\x89PNG")):raise ValueError("Archive did not return genuine JPG or PNG")
 with Image.open(io.BytesIO(data)) as i:
  i.load();im=ImageOps.exif_transpose(i).convert("RGB")
 if min(im.size)<1900:raise ValueError("Insufficient painting resolution "+str(im.size))
 if max(im.size)>5200:im.thumbnail((5200,5200),Image.Resampling.LANCZOS)
 path=dir/"ARTWORK_ORIGINAL.jpg";im.save(path,quality=95,subsampling=0,optimize=True)
 metadata={"art_url":url,"source_page":profile["source_page"],"museum":profile["museum"],
           "rights":license_name,"painting_sha256":sha(path),
           "original_file_size":len(data),"dimensions":list(im.size)}
 (dir/"SOURCE_VERIFIED.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+"\n")
 print("VERIFIED PAINTING",im.size,len(data),profile["source_page"],flush=True)
 return im,metadata

def paragraphs(profile):
 if profile.get("script_file"):
  text=(ROOT/profile["script_file"]).read_text(encoding="utf8").strip()
  paras=[x.strip() for x in re.split(r"\n\s*\n",text) if x.strip()]
  if len(paras)!=len(profile["shots"]):raise ValueError("Holbein actual Gacrux script paragraph count changed")
  return text,paras,profile["shots"]
 paragraphs=[b["speech"].strip() for b in profile["beats"]]
 return "\n\n".join(paragraphs),paragraphs,profile["beats"]

def voice_from_source(profile,ep,text):
 input_dir=ROOT/"input_voice"/"holbein"
 for name in ("VOICE_TAKE_V4.json","VOCE.wav","COPIONE_IT.txt","ALLINEAMENTO_VOCE.json"):
  if not (input_dir/name).is_file():raise FileNotFoundError("Previously approved voice artifact is incomplete: "+name)
 m=json.loads((input_dir/"VOICE_TAKE_V4.json").read_text(encoding="utf8"))
 if m.get("engine")!="Google Gemini Gacrux":raise ValueError("Unapproved narrator in restored voice")
 if hashlib.sha256(text.encode("utf8")).hexdigest()!=m["script_sha256"]:
  raise ValueError("Existing Holbein voice script hash does not match the preserved transcript")
 if sha(input_dir/"VOCE.wav")!=m["voice_sha256"]:
  raise ValueError("Restored Holbein original voice failed hash validation")
 if (input_dir/"COPIONE_IT.txt").read_text(encoding="utf8").strip()!=text:
  raise ValueError("Restored Holbein voice transcript does not match")
 shutil.copy2(input_dir/"VOCE.wav",ep/"VOCE.wav")
 shutil.copy2(input_dir/"ALLINEAMENTO_VOCE.json",ep/"ALLINEAMENTO_VOCE.json")
 return m["alignment"],m["duration_seconds"],m["engine"],"REUSED_VERIFIED_GOOGLE_GACRUX_V4"

def narration(profile,ep,text,paras):
 if profile.get("voice_reuse"):timed,duration,engine,origin=voice_from_source(profile,ep,text)
 else:
  audio,timed=synthesize(text,ep)
  duration=len(audio)/24000
  engine="Google Gemini Gacrux";origin="ORIGINAL_ONE_TAKE_GACRUX"
 with sf.SoundFile(ep/"VOCE.wav") as wav:
  if wav.channels!=1 or wav.samplerate!=24000:raise RuntimeError("Narration should be a mono 24kHz recording")
 dur=len(sf.read(ep/"VOCE.wav")[0])/24000
 if abs(dur-duration)>.08:raise RuntimeError("Voice sample duration mismatch")
 if len(timed)!=len(sentences(text)):
  raise RuntimeError("Sentence-alignment length changed: must not guess timing")
 boundary=[];used=0;prev=0
 for para in paras:
  n=len(sentences(para));used+=n
  if n<1:raise ValueError("Empty narration paragraph")
  stop=float(timed[used-1][2])
  if stop-prev<3.3:raise RuntimeError("Too short speech segment: review natural take rather than rapid cut")
  boundary.append((prev,stop))
  prev=stop
 if used!=len(timed):raise RuntimeError("Some spoken sentences have no corresponding shot")
 if duration-boundary[-1][1]>2:
  boundary[-1]=(boundary[-1][0],duration)
 (ep/"VOICE_ALIGNMENT_BEATS.json").write_text(json.dumps({
  "method":json.loads((ep/"ALLINEAMENTO_VOCE.json").read_text()).get("method","unknown"),
  "alignments":boundary,"voice_duration":duration,
  "note":"Sentence times come from Gacrux alignment metadata; inspect and listen at visual cuts.",
  "voice_source":origin,"engine":engine},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 (ep/"COPIONE_IT.txt").write_text(text+"\n",encoding="utf8")
 print("REAL NARRATION",engine,round(duration,2),"seconds",len(timed),"sentences",flush=True)
 return boundary,duration,engine

def painting_frame(im,kind,xy):
 canvas=Image.new("RGB",(W,H),(17,18,24))
 dr=ImageDraw.Draw(canvas)
 if kind=="full":
  original=im.copy()
  original.thumbnail((1010,1590),Image.Resampling.LANCZOS)
  x=(W-original.width)//2;y=(H-original.height)//2
  canvas.paste(original,(x,y))
  dr.rectangle((x-2,y-2,x+original.width+2,y+original.height+2),outline=(144,130,102),width=2)
  return canvas
 iw,ih=im.size;ratio=W/H
 limitw=min(iw,ih*ratio)
 limith=limitw/ratio
 zoom={"detail":1.42,"medium":1.12,"portrait":1.21}.get(kind,1.18)
 cw=limitw/zoom;ch=limith/zoom
 fx,fy=[float(v) for v in xy]
 cx=max(cw/2,min(iw-cw/2,iw*fx))
 cy=max(ch/2,min(ih-ch/2,ih*fy))
 bounds=(round(cx-cw/2),round(cy-ch/2),round(cx+cw/2),round(cy+ch/2))
 crop=im.crop(bounds).resize((W,H),Image.Resampling.LANCZOS)
 return crop

def intro_signature(frame,profile):
 # Same fixed 1080x1920 V6 artist/music typography. The artwork itself remains opaque.
 import cv2
 array=cv2.cvtColor(np.asarray(frame),cv2.COLOR_RGB2BGR)
 signed=original_v6_signature(array,0.,profile["artist"],profile["music"]["composer"],force_visible=True)
 return Image.fromarray(cv2.cvtColor(signed,cv2.COLOR_BGR2RGB))
def cover(profile,im,ep):
 import cv2
 base=painting_frame(im,"full",(.5,.5))
 ar=cv2.cvtColor(np.asarray(base),cv2.COLOR_RGB2BGR)
 branded=original_v6_cover(ar,profile["artist"],profile["music"]["composer"])
 canvas=Image.fromarray(cv2.cvtColor(branded,cv2.COLOR_BGR2RGB))
 d=ImageDraw.Draw(canvas)
 title=profile["title"].upper()
 fontfile="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
 font=ImageFont.truetype(fontfile,59)
 while d.textbbox((0,0),title,font=font)[2]>950 and font.size>29:
  font=ImageFont.truetype(fontfile,font.size-1)
 box=d.textbbox((0,0),title,font=font)
 d.text(((W-(box[2]-box[0]))/2,160),title,font=font,fill=(248,240,221),stroke_width=1,stroke_fill=(10,12,17))
 path=ep/"COPERTINA.jpg";canvas.save(path,quality=95)
 return path

def get_track(music,ep):
 data=get(music["url"],26000000,70)
 if len(data)<100000:raise RuntimeError("Music source does not contain an authentic usable recording")
 p=ep/"MUSIC.mp3";p.write_bytes(data)
 subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
  "-of","default=nw=1:nk=1",str(p)],capture_output=True,text=True,timeout=30,check=True)
 return p

def compose_scenes(art,profile,beats,limits,ep):
 scenes=[];files=ep/"_SCENE_FRAMES";files.mkdir(exist_ok=True)
 idx=0
 for i,(b,(start,end)) in enumerate(zip(beats,limits)):
  detail=list(b["detail"])
  secondary=list(b["wide"])
  why=b["why"]
  total=end-start
  primary=round(total*(.58 if i!=len(beats)-1 else .43),3)
  secondary_sec=round(total-primary,3)
  kinds=["detail","full" if i in (1,3,len(beats)-1) else "medium"]
  for k,(kind,fx,dur) in enumerate(zip(kinds,(detail,secondary),(primary,secondary_sec))):
   if dur<=1.4:raise RuntimeError("Scene too short to read at natural narration pace")
   idx+=1
   img=painting_frame(art,kind,fx)
   # Optional V6 opening identity: the first screen contains the real first detail.
   if idx==1:
    intro_sec=min(2.85,max(1.5,dur*.66))
    signed=intro_signature(img,profile)
    path=files/f"{idx:03d}_BRANDING.jpg";signed.save(path,quality=95)
    scenes.append({"file":path,"duration":intro_sec,"purpose":"The V6 opening signature on the genuine first artwork detail","beat":i,"type":"opening"})
    dur-=intro_sec
   if dur>1.15:
    path=files/f"{idx:03d}_{kind.upper()}.jpg";img.save(path,quality=94)
    scenes.append({"file":path,"duration":dur,"purpose":why,"beat":i,"type":kind})
 if len(scenes)<12:raise RuntimeError("At least 12 motivated framed shots expected for Critico")
 txt=ep/"SCENE_LIST.txt"
 # JPEGs are opaque, no image layers overlap. The concat demuxer holds one at a time.
 with txt.open("w",encoding="utf8") as f:
  for x in scenes:
   f.write("file '"+str(x["file"].resolve()).replace("'","'\\''")+"'\n")
   f.write("duration "+f"{x['duration']:.5f}"+"\n")
  f.write("file '"+str(scenes[-1]["file"].resolve()).replace("'","'\\''")+"'\n")
 (ep/"REGIA_DETTAGLI_E_SYNC.json").write_text(json.dumps([
  {"time_start":round(sum(y["duration"] for y in scenes[:i]),3),
   "duration":round(s["duration"],3),"purpose":s["purpose"],"type":s["type"],
   "spoken_beat":s["beat"],"one_opaque_image":True,"transition":"hard_cut_no_overlap"}
  for i,s in enumerate(scenes)],ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 return scenes,txt

def render_video(profile,ep,limits,scenes,music,voice_duration):
 raw=ep/"_VISUAL_ONLY.mp4"
 target=round(voice_duration+2.2,3)
 cmd=["ffmpeg","-hide_banner","-loglevel","error","-y",
  "-f","concat","-safe","0","-i",str(ep/"SCENE_LIST.txt"),
  "-r",str(FPS),"-pix_fmt","yuv420p","-c:v","libx264",
  "-preset","veryfast","-crf","19","-threads","2",
  "-movflags","+faststart","-t",str(voice_duration),str(raw)]
 subprocess.run(cmd,check=True,timeout=1100)
 output=ep/"VIDEO_MASTER.mp4"
 # Music is deliberately quiet, single recording throughout. Audio fades never
 # mix two paintings; only opaque visual cuts are ever used.
 filt=f"[1:a]adelay=180|180,volume=1.0,afade=t=in:st=0:d=0.15[v];"+\
  f"[2:a]volume=0.048,afade=t=in:st=0:d=2,afade=t=out:st={max(0,target-2.8):.2f}:d=2.8[m];"+\
  "[v][m]amix=inputs=2:duration=longest:normalize=0[a]"
 subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
  "-i",str(raw),"-i",str(ep/"VOCE.wav"),"-stream_loop","-1","-i",str(music),
  "-filter_complex",filt,"-map","0:v:0","-map","[a]","-t",str(voice_duration),
  "-c:v","copy","-c:a","aac","-b:a","192k","-movflags","+faststart",str(output)],
  check=True,timeout=300)
 raw.unlink(missing_ok=True)
 return output

def ffmeta(path):
 return json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams",
  "-show_format","-of","json",str(path)],timeout=35))
def review_frames(video,scenes,ep):
 checkpoints=[0,1,3,5,7]
 p=0
 for x in scenes[:-1]:
  p+=x["duration"]
  if p>=8:checkpoints.append(max(0,p-.04))
 out=ep/"QA_FRAMES";out.mkdir(exist_ok=True)
 saved=[]
 for sec in checkpoints[:32]:
  p=out/f"SEC_{sec:07.2f}.jpg"
  subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-ss",f"{sec:.2f}",
    "-i",str(video),"-frames:v","1","-q:v","3","-y",str(p)],check=True,timeout=18)
  if p.exists() and p.stat().st_size>11000:saved.append(p)
 tiles=saved[::max(1,len(saved)//12)][:12]
 thumbw,thumbh=180,340
 sheet=Image.new("RGB",(thumbw*len(tiles),thumbh),(12,16,22))
 d=ImageDraw.Draw(sheet)
 for i,p in enumerate(tiles):
  with Image.open(p) as im:
   im.thumbnail((thumbw-6,thumbh-26),Image.Resampling.LANCZOS);sheet.paste(im,(i*thumbw+(thumbw-im.width)//2,3))
  d.text((i*thumbw+8,thumbh-21),p.stem[4:]+"s",fill=(220,225,229))
 sheet.save(ep/"QA_CONTACT_SHEET.jpg",quality=92)

def post_and_metadata(profile,episode,ep,scenes,voice_dur,engine,source):
 files=editorial.write_posts(episode,ep,overwrite=True)
 errors=editorial.validate_folder(ep)
 if errors:raise ValueError("Critico V32 post checks failed: "+repr(errors))
 rule={"visual_transition_policy":{"image_opacity":1.0,"max_simultaneous_source_images":1,
    "frames_with_two_visuals":0},"crossfade_seconds":0,"overlap_frames":0,
    "transition_style":"hard_cut_only",
    "transitions":[{"type":"hard_cut","at":round(sum(s["duration"] for s in scenes[:i+1]),3),"overlap_frames":0}
         for i in range(len(scenes)-1)],"source_profile":"ArtVision Critico V32",
    "voice":True,"format":"artvision_critico","music":profile["music"]["title"],
    "publication":"NOT_PUBLISHED","visuals":len(scenes)}
 (ep/"VIDEO_RECIPE_V13.json").write_text(json.dumps(rule,ensure_ascii=False,indent=2)+"\n")
 sources={"work_title_en":profile["title"],"artist":profile["artist_full"],
  "museum":profile["museum"],"artwork":source,"primary_museum_source":profile["museum_source"] if profile.get("museum_source") else profile["source_page"],
  "music":profile["music"],"voice":{"engine":engine,"duration_seconds":voice_dur,
  "artificial_speech_disclosure":"Google Gemini Gacrux, natural one-pass text-to-speech (not a human recording)"},
  "license_caveat":"Recheck territory/platform rights and soundtrack attribution before commercial publication."}
 (ep/"FONTI_E_CREDITI.json").write_text(json.dumps(sources,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 (ep/"ISTRUZIONI_REPLICA.md").write_text(
  f"# Critico V32 — {profile['artist_full']} — {profile['title']}\n\n"
  f"Usare: python scripts/artvision_critico_v32_natural_three.py --episode {episode}\n\n"
  "Preset: Critico V2 + voce Gacrux V4 + direttore V23/V25 con regola anti-ghosting del 24 ottobre.\n"
  "La voce è una sola interpretazione, non un assemblaggio di voci diverse.\n"
  "Il video presenta una sola immagine opaca per fotogramma; tagli netti, senza trasparenza.\n"
  "Controllare con attenzione la sincronizzazione stimata di voce e scena, essendo l'allineamento ASR facoltativo.\n"
  "Il post riguarda esclusivamente l'opera, non il montaggio o la tecnologia di produzione.\n"
  "Pubblicazione e monetizzazione NON autorizzate automaticamente.\n",encoding="utf8")
 return files

def final_verify(episode,ep,profile,source,voice_duration,voice_engine,scenes):
 movie=ep/"VIDEO_MASTER.mp4"
 m=ffmeta(movie)
 video=[s for s in m["streams"] if s["codec_type"]=="video"]
 audio=[s for s in m["streams"] if s["codec_type"]=="audio"]
 assert len(video)==1 and video[0]["codec_name"]=="h264" and (video[0]["width"],video[0]["height"])==(1080,1920)
 assert len(audio)==1 and audio[0]["codec_name"]=="aac"
 duration=float(m["format"]["duration"])
 if abs(duration-voice_duration)>1.3:raise RuntimeError(f"Voice/video duration not synchronized: {duration}, {voice_duration}")
 if movie.stat().st_size<1500000:raise ValueError("MP4 too small to constitute a real movie")
 subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-xerror","-i",str(movie),"-f","null","-"],
  check=True,timeout=450)
 report={"schema":"artvision-critico-v32-final","status":"TECHNICALLY_VERIFIED_AESTHETIC_REVIEW_REQUIRED",
  "episode":episode,"title":profile["title"],"artist":profile["artist_full"],
  "duration_seconds":duration,"voice_seconds":voice_duration,
  "codec":"H264/AAC","resolution":[1080,1920],
  "voice":voice_engine,"spoken_narration_present":True,
  "distinct_visual_crops":len(scenes),"no_ghosting_policy":True,
  "art_source":source,"master_sha256":sha(movie),
  "music":profile["music"],"automatic_publication":False,
  "alignment_accuracy":"estimated if ASR was not available — manually review spoken cut timings",
  "note":"Automatic full decode and selected frame samples are technical evidence, not human aesthetic approval."}
 (ep/"FINAL_QA.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 for name in ("COPERTINA.jpg","COPIONE_IT.txt","REGIA_DETTAGLI_E_SYNC.json","VIDEO_RECIPE_V13.json","FONTI_E_CREDITI.json",
  "POST_FACEBOOK.txt","POST_INSTAGRAM.txt","POST_TIKTOK.txt","POST_YOUTUBE.txt",
  "POST_EDITORIAL_RESEARCH.json","QA_CONTACT_SHEET.jpg","VOICE_ALIGNMENT_BEATS.json"):
  assert (ep/name).is_file() and (ep/name).stat().st_size>200,name
 pack=ep.parent/f"ARTVISION_CRITICO_V32_{episode.upper()}_COMPLETE.zip"
 with zipfile.ZipFile(pack,"w",allowZip64=True) as z:
  for p in ep.rglob("*"):
   if p.is_file() and "_SCENE_FRAMES" not in p.parts and "QA_FRAMES" not in p.parts:
    typ=zipfile.ZIP_STORED if p.suffix.lower() in (".mp4",".jpg",".wav",".mp3") else zipfile.ZIP_DEFLATED
    z.write(p,p.relative_to(ep),compress_type=typ)
 with zipfile.ZipFile(pack) as z:assert z.testzip() is None
 print("FINAL_REAL_CRITIC_FILM",episode,"duration",duration,"bytes",movie.stat().st_size,flush=True)

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--episode",choices=CONFIG["episodes"],required=True)
 args=ap.parse_args()
 ep_name=args.episode;profile=CONFIG["episodes"][ep_name]
 ep=ROOT/"output/artvision-critico-v32"/ep_name
 ep.mkdir(parents=True,exist_ok=True)
 text,paras,beats=paragraphs(profile)
 art,source=image_source(profile,ep)
 boundaries,voice_sec,engine=narration(profile,ep,text,paras)
 track=get_track(profile["music"],ep)
 cover(profile,art,ep)
 scenes,_=compose_scenes(art,profile,beats,boundaries,ep)
 movie=render_video(profile,ep,boundaries,scenes,track,voice_sec)
 post_and_metadata(profile,ep_name,ep,scenes,voice_sec,engine,source)
 # Machine-checked no-ghosting policy gate, plus source-code scan.
 subprocess.run([sys.executable,str(ROOT/"src/artvision_no_ghosting_gate_v1.py"),
  "--manifest",str(ep/"VIDEO_RECIPE_V13.json"),"--source-file",str(pathlib.Path(__file__))],
  check=True,timeout=35)
 review_frames(movie,scenes,ep)
 final_verify(ep_name,ep,profile,source,voice_sec,engine,scenes)
if __name__=="__main__":main()
