#!/usr/bin/env python3
"""Private ArtVision Cinema Standard: Albert Bierstadt / The Last of the Buffalo.
Only existing public-domain museum artwork and real licensed musical recording.
No TTS, no synthetic animals, no publication, no Gold, no API spending.
"""
from __future__ import annotations
import hashlib, io, json, subprocess, urllib.request, zipfile, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"output/artvision-bierstadt-buffalo-20261115"
OUT.mkdir(parents=True,exist_ok=True)
TITLE="The Last of the Buffalo"
ARTIST="Albert Bierstadt"
OBJECT="2014.79.5"
NGA="https://www.nga.gov/artworks/124525-last-buffalo"
COMMONS="https://commons.wikimedia.org/wiki/File:The_Last_of_the_Buffalo.jpg"
SOURCE_URLS=[
 "https://upload.wikimedia.org/wikipedia/commons/3/30/The_Last_of_the_Buffalo.jpg",
 "https://commons.wikimedia.org/wiki/Special:Redirect/file/The_Last_of_the_Buffalo.jpg",
]
EXPECTED_SHA1="aaef7503f34ae7591bac8c0a5221e782ee52cf9f"
EXPECTED_PIXELS=(10602,6252)
W,H,FPS=720,1280,20
TRANSITION=.48
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def sha(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
 return h.hexdigest()

def get_source():
 errors=[]
 for url in SOURCE_URLS:
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"ArtVision source-verification/1.0 (noncommercial private QA)"})
   with urllib.request.urlopen(req,timeout=90) as f:
    blob=f.read(50_000_001)
   if len(blob)>50_000_000:raise ValueError("Artwork file too large")
   if hashlib.sha1(blob).hexdigest()!=EXPECTED_SHA1:raise ValueError("Wrong original SHA1")
   with Image.open(io.BytesIO(blob)) as im:
    if im.size!=EXPECTED_PIXELS or im.format!="JPEG":raise ValueError(f"Wrong pixels/format: {im.size}/{im.format}")
    im.verify()
   dest=OUT/"ORIGINAL_ARTWORK_2014.79.5.jpg"
   dest.write_bytes(blob)
   return dest,url
  except Exception as ex:
   errors.append({"source":url,"reason":str(ex)[:200]})
 raise RuntimeError("BLOCKED_EXACT_MUSEUM_PAINTING_BINARY: "+json.dumps(errors))

def txt(draw,x,y,msg,font,fill):
 draw.text((x,y),msg,font=font,fill=fill,stroke_width=0)

# Every panel is extracted from the exact painting, not AI-generated.
# Rectangles are normalized source coordinates; metadata labels are editorial, not semantic detection pass.
SHOTS=[
 ("opening composition",(0,0,1,1),4.7),
 ("central mounted hunter",(.32,.30,.61,.82),5.0),
 ("foreground bison left",(.05,.58,.36,.99),5.0),
 ("bleached remains / foreground",(.00,.63,.31,.96),4.7),
 ("herd and river plain",(.03,.31,.49,.69),5.0),
 ("mounted hunter and bull",(.29,.33,.65,.88),5.2),
 ("riders entering from right",(.67,.32,.99,.84),5.0),
 ("distant herd panorama",(.05,.16,.92,.53),5.0),
 ("foreground bison right",(.54,.55,.98,.98),5.0),
 ("wide empty sky and mountain",(.0,.0,1,.62),4.9),
 ("closing complete painting",(0,0,1,1),5.4),
]

def panel(base,idx,scene):
 label,box,duration=scene
 a,b,c,d=box
 iw,ih=base.size
 crop=base.crop((round(a*iw),round(b*ih),round(c*iw),round(d*ih)))
 backdrop=ImageOps.fit(base,(W,H),method=Image.Resampling.BILINEAR)
 backdrop=backdrop.filter(ImageFilter.GaussianBlur(55))
 backdrop=ImageEnhance.Brightness(backdrop).enhance(.28)
 detail=ImageOps.contain(crop,(W-12,H-30),method=Image.Resampling.LANCZOS)
 top=(H-detail.height)//2
 left=(W-detail.width)//2
 backdrop.paste(detail,(left,top))
 draw=ImageDraw.Draw(backdrop)
 if idx==0:
  draw.rectangle((0,75,W,306),fill=(9,10,8,226))
  ft=ImageFont.truetype(BOLD,46)
  small=ImageFont.truetype(FONT,20)
  txt(draw,30,92,"THE LAST OF",ft,(253,242,216))
  txt(draw,30,150,"THE BUFFALO",ft,(253,242,216))
  txt(draw,32,233,"ALBERT BIERSTADT  ·  1888–1889",small,(221,213,195))
 if idx==len(SHOTS)-1:
  draw.rectangle((0,940,W,1182),fill=(9,10,8,222))
  txt(draw,26,961,"THE LAST OF THE BUFFALO",ImageFont.truetype(BOLD,29),(253,245,225))
  txt(draw,28,1013,"Albert Bierstadt · 1888–1889",ImageFont.truetype(FONT,21),(222,213,190))
  txt(draw,28,1058,"National Gallery of Art, Washington",ImageFont.truetype(FONT,20),(218,213,197))
  txt(draw,28,1097,"Open Access · Public Domain",ImageFont.truetype(FONT,18),(218,213,197))
 dest=OUT/f"SCENE_{idx+1:02}.png"
 backdrop.save(dest,optimize=True)
 return dest

def render_video(panels):
 durations=[row[2] for row in SHOTS]
 args=["ffmpeg","-hide_banner","-loglevel","error","-y"]
 for file in panels:args+=["-loop","1","-framerate",str(FPS),"-i",str(file)]
 filters=[]
 for i,seconds in enumerate(durations):
  filters.append(f"[{i}:v]trim=duration={seconds},setpts=PTS-STARTPTS,fps={FPS},format=yuv420p,zoompan=z='min(zoom+0.00008,1.016)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},trim=duration={seconds},setpts=PTS-STARTPTS[v{i}]")
 prev="v0"
 for i in range(1,len(panels)):
  offset=sum(durations[:i])-i*TRANSITION
  nxt=f"x{i}"
  filters.append(f"[{prev}][v{i}]xfade=transition=fade:duration={TRANSITION:.2f}:offset={offset:.2f}[{nxt}]")
  prev=nxt
 duration=sum(durations)-(len(durations)-1)*TRANSITION
 filters.append(f"[{prev}]fade=t=out:st={duration-1.35:.2f}:d=1.35,format=yuv420p[vout]")
 dest=OUT/"SILENT_SOURCE_LOCKED.mp4"
 args+=["-filter_complex",";".join(filters),"-map","[vout]","-an","-c:v","libx264","-preset","veryfast","-crf","23","-pix_fmt","yuv420p","-movflags","+faststart",str(dest)]
 print("RENDERING_SOURCE_ONLY_VIDEO",flush=True)
 subprocess.run(args,check=True,timeout=1500)
 return dest,duration

def social_pack():
 credit='Image: Albert Bierstadt, The Last of the Buffalo (1888–1889), National Gallery of Art, Washington, Corcoran Collection, accession 2014.79.5. Artwork public domain; Wikimedia Commons original source. Music: "Lightless Dawn" Kevin MacLeod (incompetech.com). Licensed under CC BY 4.0: https://creativecommons.org/licenses/by/4.0/. Edited excerpt and fades.'
 pack={
  "title_en":"THE LAST OF THE BUFFALO | An American Landscape's Final Warning",
  "hook_it":"Guarda il cavallo bianco. Poi osserva che cosa giace davanti a lui.",
  "short_it":"Un'immagine grandiosa e inquietante: Bierstadt raccontò il tramonto dei bisonti delle Grandi Pianure.",
  "long_it":"In The Last of the Buffalo, Albert Bierstadt contrappone la corsa di cacciatori e animali alla vastità di un paesaggio quasi infinito. È un dipinto del 1888–1889, alla vigilia di una nuova attenzione verso la protezione del bisonte americano. Il quadro non è una fotografia né un resoconto etnografico: è una drammatizzazione artistica del suo tempo, ricca di ambiguità.",
  "facebook":"Una caccia tra luce dorata e tracce di morte. Perché Albert Bierstadt dipinse un paesaggio così enorme per raccontare una perdita? Scopri i dettagli dell'opera. #ArtVision #AlbertBierstadt #ArtHistory",
  "instagram":"Un cavallo bianco. Una mandria che si allontana. E i segni di un mondo in pericolo.\nThe Last of the Buffalo, Albert Bierstadt, 1888–1889.\n#ArtVision #AlbertBierstadt #PaintingDetails #AmericanArt",
  "tiktok":"Il dettaglio più inquietante non è la caccia. Guarda il primo piano. #ArtVision #ArtHistory #Bierstadt",
  "youtube_shorts":"THE LAST OF THE BUFFALO (1888–1889) | Albert Bierstadt. Un quadro monumentale sulla fine di un'epoca. #Shorts #ArtHistory #ArtVision",
  "keywords":["Albert Bierstadt","The Last of the Buffalo","National Gallery of Art","American art","19th century painting","bison conservation","public domain art"],
  "question_it":"Quale dettaglio ti colpisce di più: il cavaliere, la mandria o gli animali in primo piano?",
  "credits":credit,
  "cover_alt_it":"Dettaglio del dipinto The Last of the Buffalo: cavaliere su cavallo bianco, bisonti e prateria, con titolo bianco leggibile.",
  "fact_check_notes":["Oil on canvas; 1888–1889; NGA accession 2014.79.5","Representations of Indigenous subjects are artistic constructions and not ethnographic evidence.","No animal or human subject added with AI.","No automatic publication; artistic review pending."]
 }
 (OUT/"SOCIAL_PACK.json").write_text(json.dumps(pack,indent=2,ensure_ascii=False)+"\n","utf8")
 (OUT/"SOCIAL_PACK.txt").write_text("\n\n".join([f"{k.upper()}\n{v}" for k,v in pack.items() if isinstance(v,str)])+"\n","utf8")
 return pack

def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument("--preflight",action="store_true");a=p.parse_args()
 # Check source metadata and duplicate guard only; do not spend credits.
 research=json.loads((ROOT/"research/artvision_rare_cc0_video_candidates_20261115.json").read_text())
 match=[x for x in research["candidates"] if x["title"]==TITLE and x["accession"]==OBJECT]
 assert len(match)==1 and match[0]["rendered"] is False
 assert not (ROOT/"queue/artvision_extra_render_checkpoint_20261115_bierstadt_last_buffalo.json").exists()
 catalog=json.loads((ROOT/"config/artvision_music_20_v1.json").read_text())
 assert next(x for x in catalog["tracks"] if x["id"]=="lightless_dawn")["license"]=="CC BY 4.0"
 if a.preflight:
  print("PASS_SOURCE_EXACT_ARTIST_ACCESSION_V330_AND_ANTIDUPLICATE")
  return
 image,url=get_source()
 src_sha=sha(image)
 with Image.open(image) as img:
  base=img.convert("RGB")
  base.thumbnail((5400,3500),Image.Resampling.LANCZOS)
  panels=[panel(base,k,shot) for k,shot in enumerate(SHOTS)]
 video,duration=render_video(panels)
 social_pack()
 Image.open(panels[0]).save(OUT/"COVER.jpg",quality=93)
 info={
  "schema":"artvision-bierstadt-buffalo-cinema-v1",
  "artist":ARTIST,"title":TITLE,"year":"1888–1889","variant":"cinema_standard",
  "accession":OBJECT,"official_url":NGA,"image_source_page":COMMONS,"source_binary_url":url,
  "license":"Public domain faithful reproduction; NGA Open Access media",
  "source_size_bytes":image.stat().st_size,"source_pixels":list(EXPECTED_PIXELS),
  "source_sha1":EXPECTED_SHA1,"source_sha256":src_sha,
  "video_silent_sha256":sha(video),
  "technical_status":"SOURCE_VALIDATED_SILENT_RENDERED_AUDIO_V330_NEXT",
  "artistic_review":"PENDING","commercial_rights":"PUBLIC_DOMAIN_ART_WITH_FINAL_PLATFORM_QA_PENDING",
  "published":False,"gold":False,"tts_calls":0,"paid_api_calls":0,
  "shots":[{"name":s[0],"normalized_crop":list(s[1]),"duration_s":s[2]} for s in SHOTS],
  "music":"Lightless Dawn - Kevin MacLeod (verify separate V330 proof)",
  "total_seconds_estimate":duration,
 }
 (OUT/"SOURCE_STORYBOARD_QA.json").write_text(json.dumps(info,indent=2,ensure_ascii=False)+"\n","utf8")
 print("SOURCE_SHA256",src_sha,"SOURCE_PIXELS",EXPECTED_PIXELS,"VIDEO_SILENT_SHA256",sha(video),"SECONDS",duration,flush=True)

if __name__=="__main__":main()
