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
from gemini_voice import synthesize

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"output"/"giuliano_terracotta"
MEDIA=OUT/"media"
W,H,FPS=720,1280,20
# Real museum photos, independently described/licensed at Wikimedia Commons.
# The order matches the exact sentence order in the narration.
FILES=[
 "Terracotta_Army_Pit_1_front_rank_detail.JPG",
 "Terracotta_Army_Pit_1_1.jpg",
 "Terracotta_Army_-_Pit_1.jpg",
 "Terracotta_Army,_View_of_Pit_1.jpg",
 "Terracotta_Army_Pit_1_-_4.jpg",
 "Terracotta_horse_and_two_soldiers.jpg",
 "Terracotta_Army_Pit_1_-_5.jpg",
 "China.Terracotta_statues026.jpg",
 "20230924_Pit_1_of_Terracotta_Army_01.jpg",
 "China.Terracotta_statues026.jpg",
 "Terracotta_horse_and_two_soldiers.jpg",
 "Terracotta_Army,_View_of_Pit_1.jpg",
 "Terracotta_Army_Pit_1_front_rank_detail.JPG",
]
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
def download_commons(filename, dest):
 s=requests.Session();s.headers["User-Agent"]=UA
 url="https://commons.wikimedia.org/w/api.php"
 title="File:"+filename.replace("_"," ")
 params={"action":"query","format":"json","prop":"imageinfo",
         "iiprop":"url|extmetadata|size","iiurlwidth":"1600","titles":title}
 exc=None
 for attempt in range(3):
  try:
   r=s.get(url,params=params,timeout=40); r.raise_for_status()
   pages=r.json()["query"]["pages"]
   item=next(iter(pages.values()))
   if "missing" in item:raise RuntimeError("Non esiste Commons file "+title)
   info=item["imageinfo"][0]
   ext=info.get("extmetadata",{})
   name=strip_html(ext.get("LicenseShortName",{}).get("value",""))
   terms=strip_html(ext.get("UsageTerms",{}).get("value",""))
   licenseurl=ext.get("LicenseUrl",{}).get("value","")
   if not any(t in (name+" "+terms+" "+licenseurl).lower() for t in
       ["cc by","cc0","cc-zero","public domain","cc-by","creativecommons.org"]):
    raise RuntimeError("Licenza non riconosciuta per "+filename+": "+name)
   photo_url=info.get("thumburl") or info.get("url")
   rr=s.get(photo_url,timeout=70);rr.raise_for_status()
   dest.write_bytes(rr.content)
   with Image.open(dest) as im:
    im.verify()
   author=strip_html(ext.get("Artist",{}).get("value","Autore non indicato"))
   return {"file":filename,"commons_page":"https://commons.wikimedia.org/wiki/"+urllib.parse.quote("File:"+filename),
           "photographer":author,"license":name,"license_url":licenseurl,
           "image_sha256":sha(dest),"bytes":dest.stat().st_size}
  except Exception as e:
   exc=e;print("Foto",filename,"tentativo",attempt+1,type(e).__name__,str(e)[:180],flush=True)
   if attempt<2:time.sleep(3*(attempt+1))
 raise RuntimeError("Immagine indispensabile non acquisita: "+filename) from exc

def font(sz):
 for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
           "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
  if Path(p).exists():return ImageFont.truetype(p,sz)
 return ImageFont.load_default()
def make_canvas(path,out):
 im=Image.open(path)
 im=ImageOps.exif_transpose(im).convert("RGB")
 # A transparent editorial distinction: preserve full authentic photograph
 # against an out-of-focus copy of itself, not AI reconstruction.
 bg=ImageOps.fit(im,(900,1600),method=Image.Resampling.LANCZOS,
       centering=(.5,.5)).filter(ImageFilter.GaussianBlur(36))
 bg=Image.blend(bg,Image.new("RGB",bg.size,(10,14,19)),.34)
 fg=ImageOps.contain(im,(880,1480),method=Image.Resampling.LANCZOS)
 ox=(900-fg.width)//2;oy=(1600-fg.height)//2
 bg.paste(fg,(ox,oy))
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
 d.text((46,980),"THE ARMY",font=font(66),fill="#f6e9cb",stroke_width=1,stroke_fill="#121211")
 d.text((46,1057),"THAT WAITED",font=font(52),fill="#f6e9cb",stroke_width=1,stroke_fill="#121211")
 d.text((49,1158),"THE TERRACOTTA WARRIORS",font=font(23),fill="#e3d2b0")
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
 OUT.mkdir(parents=True,exist_ok=True);MEDIA.mkdir(exist_ok=True)
 script=(ROOT/"giuliano"/"terracotta"/"VOCE_GACRUX_IT.txt").read_text(encoding="utf-8").strip()
 # Validate and preserve historic picture sources BEFORE spending any TTS request.
 # The opening and closing use the same photograph by design.
 credits=[]
 imagefiles=[]
 for i,name in enumerate(FILES):
  target=MEDIA/("img_%02d.jpg"%i)
  # Avoid needless duplicate HTTP downloads, but preserve separate stage frames.
  prev=next((j for j in range(i) if FILES[j]==name),None)
  if prev is None:
   meta=download_commons(name,target)
  else:
   target.write_bytes((MEDIA/("img_%02d.jpg"%prev)).read_bytes())
   meta={**credits[prev],"image_sha256":sha(target)}
  meta["stage_index"]=i
  credits.append(meta)
  canvas=MEDIA/("canvas_%02d.jpg"%i)
  make_canvas(target,canvas)
  imagefiles.append(canvas)
  # A small pause avoids Wikimedia Commons throttling after successive API hits.
  if prev is None:time.sleep(2)
 if len({c["image_sha256"] for c in credits})<7:
  raise RuntimeError("Preflight: fewer than seven real distinct historical pictures")
 print("IMAGE_PREFLIGHT_OK:",len(credits),"scenes",
       len({c["image_sha256"] for c in credits}),"verified photographs",flush=True)
 # Only after imagery is secured, make the single requested Gacrux call.
 audio,timed=synthesize(script,OUT/"audio")
 duration=len(audio)/24000
 print("Gacrux audio:",duration,"seconds; sentences:",len(timed),flush=True)
 if not 65 <= duration <= 150: raise RuntimeError("Narrazione durata non conforme")
 if len(timed)!=len(FILES):raise RuntimeError("Scene e frasi non corrispondono: "+str(len(timed)))
 (OUT/"ATTRIBUZIONI_FOTO.json").write_text(json.dumps(credits,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 (OUT/"ATTRIBUZIONI_FOTO.txt").write_text(
    "Fotografie autentiche / Wikimedia Commons. Adattamenti: ritaglio, fondale sfocato e lento movimento digitale.\n"+
    "\n".join(f'{c["stage_index"]+1:02d}. {c["file"]} / {c["photographer"]} / {c["license"]} / {c["commons_page"]} / {c["license_url"]}' for c in credits)+"\n",encoding="utf8")
 cover_from(imagefiles[0],OUT/"COVER.jpg")
 segs=[]; scenes=[]
 # The narrator's aligned sentence timecodes determine scene duration; no arbitrary sequence changes.
 for i,(text,a,b) in enumerate(timed):
  start=0 if i==0 else (timed[i-1][2]+a)/2
  end=duration if i==len(timed)-1 else (b+timed[i+1][1])/2
  seconds=max(.5,end-start);frames=max(1,round(FPS*seconds))
  output=OUT/("shot_%02d.mp4"%i)
  zincrement=.000030 if i%2==0 else .000025
  filt=(f"zoompan=z='min(1.015+on*{zincrement:.6f},1.075)':"
        f"x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={frames}:"
        f"s={W}x{H}:fps={FPS},format=yuv420p")
  shell(["ffmpeg","-hide_banner","-loglevel","error","-y","-loop","1",
         "-framerate",str(FPS),"-i",imagefiles[i],"-vf",filt,
         "-frames:v",str(frames),"-an","-c:v","libx264","-pix_fmt","yuv420p",
         "-preset","veryfast","-crf","21","-r",str(FPS),output])
  segs.append(output)
  scenes.append({"scene":i+1,"script":text,"audio_start_seconds":round(a,3),
   "audio_end_seconds":round(b,3),"visual_start_seconds":round(start,3),
   "visual_end_seconds":round(end,3),"media_filename":credits[i]["file"]})
 concat=OUT/"concat.txt"
 concat.write_text("".join("file '"+str(f.absolute())+"'\n" for f in segs))
 base=OUT/"silent.mp4"
 shell(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0",
        "-i",concat,"-c","copy",base])
 original_music(duration,OUT/"music.wav")
 movie=OUT/"GIULIANO_TERRACOTTA_CRITICO_REVIEW.mp4"
 # Deliberate music level below the single verified voice track; no voice replacement.
 shell(["ffmpeg","-hide_banner","-loglevel","error","-y",
        "-i",base,"-i",OUT/"audio"/"VOCE.wav","-i",OUT/"music.wav",
        "-filter_complex","[1:a]volume=1.0[voice];[2:a]volume=0.32[music];[voice][music]amix=inputs=2:duration=first:dropout_transition=0[a]",
        "-map","0:v:0","-map","[a]","-c:v","copy","-c:a","aac",
        "-b:a","160k","-ar","48000","-shortest","-movflags","+faststart",movie])
 shell(["ffmpeg","-hide_banner","-loglevel","error","-xerror","-i",movie,"-f","null","-"])
 probe=subprocess.check_output(["ffprobe","-v","error","-show_entries",
   "format=duration,size:stream=codec_name,width,height","-of","json",str(movie)],text=True)
 qa={"status":"RENDERED_NEEDS_ARTISTIC_REVIEW","audio_voice":"Google Gemini Gacrux",
  "visuals":"Authentic photographs with digital camera motion, NOT real moving historical footage",
  "video_sha256":sha(movie),"probe":json.loads(probe),"source_count":len({c["image_sha256"] for c in credits}),
  "scenes":scenes,"publication_authorized":False,"paid_video_calls":0,
  "source_constraints":"CC BY/CC BY-SA/CC0, attribution in ZIP. Verify all links before sharing."}
 (OUT/"QA.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n")
 (OUT/"README.txt").write_text(
  "GIULIANO - TERRACOTTA ARMY / PROVA DI REGIA NON PUBBLICATA\n"
  "MP4: vera voce Gacrux e foto autentiche Commons; movimento di camera su foto.\n"
  "QA automatico di decodifica completa: PASS. Review artistica umana: DA FARE.\n"
  "Nessuna ricostruzione video AI e nessuna clip con persone realmente animate.\n"
  "Diritti e crediti: vedi ATTRIBUZIONI_FOTO.txt.\n")
 zipout=OUT/"GIULIANO_TERRACOTTA_VIDEO_COVER_TESTI.zip"
 with zipfile.ZipFile(zipout,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
  for p in [movie,OUT/"COVER.jpg",OUT/"README.txt",
            OUT/"ATTRIBUZIONI_FOTO.txt",OUT/"QA.json",
            ROOT/"giuliano"/"terracotta"/"VOCE_GACRUX_IT.txt"]:
   z.write(p,arcname=p.name)
 with zipfile.ZipFile(zipout) as z:
  bad=z.testzip()
  if bad:raise RuntimeError("CRC ZIP errato "+bad)
 print(json.dumps({"mp4":str(movie),"video_sha":sha(movie),
                   "zip":str(zipout),"zip_sha":sha(zipout),
                   "duration":duration,"clips":len(segs)},indent=2),flush=True)
if __name__=="__main__": main()
