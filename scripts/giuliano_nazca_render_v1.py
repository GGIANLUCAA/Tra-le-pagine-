#!/usr/bin/env python3
"""GIULIANO 04 NAZCA - real licensed photo-and-aerial documentary.

Owner review ONLY. 27 source-linked voice-synced scenes, including four
moments from REAL Commons aerial footage. No video AI, synthetic ancient
figures, stock footage, fake 2024 glyph images, or new TTS calls.
"""
import hashlib,io,json,math,os,subprocess,urllib.request,zipfile
from pathlib import Path
from PIL import Image,ImageOps,ImageEnhance,ImageFilter,ImageDraw,ImageFont

W,H,FPS=1080,1920,25
SOURCE=Path("input/giuliano-nazca-licensed")
VOICE=Path("input/giuliano-nazca-voice")
BRIEF=Path("giuliano/nazca/EP04_BRIEF_SHOTMAP_V1.json")
OUT=Path("output/GIULIANO_04_NAZCA_MASTER")
SEGMENTS=OUT/"segments"
PLATES=OUT/"plates"
TITLE="NAZCA — THE DESERT THAT REMEMBERS"
MUSIC={
 "title":"Floating Cities","author":"Kevin MacLeod",
 "official_page":"https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1600018",
 "license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
 "isrc":"USUAN1600018",
 "url":"https://incompetech.com/music/royalty-free/mp3-royaltyfree/Floating%20Cities.mp3"
}
UA={"User-Agent":"TraLePagine-Giuliano-Nazca/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-)","Accept":"*/*"}
def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for c in iter(lambda:f.read(1<<20),b""):h.update(c)
 return h.hexdigest()
def jwrite(p,value):Path(p).write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def run(args,timeout=230):
 p=subprocess.run([str(x) for x in args],capture_output=True,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError("FFMPEG_OR_SYSTEM_COMMAND_FAILED "+str(args[:6])+" "+p.stderr[-2200:])
 return p.stdout
def font(size,serif=True):
 fontfiles=[
  "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf" if serif else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
  "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
 ]
 for f in fontfiles:
  if Path(f).is_file():return ImageFont.truetype(f,size)
 return ImageFont.load_default()
def validated_sources():
 data=json.loads((SOURCE/"SOURCE_CURATED.json").read_text())
 assert data["schema"]=="nazca-curated-existing-media-v1"
 assert data["status"]=="REAL_MEDIA_SHA_LICENSE_PASS"
 assert len(data["photos"])>=26
 assert data["real_video"]["duration_s"]>40
 for row in [*data["photos"],data["real_video"]]:
  assert row["author"] and row["license_url"] and row["license"]
  p=SOURCE/row["filename"]
  assert p.is_file() and sha(p)==row["sha256"],"SOURCE_BYTES_NOT_MATCH "+row["filename"]
 photo={x["title"].removeprefix("File:"):x for x in data["photos"]}
 return data,photo
def validated_voice():
 brief=json.loads(BRIEF.read_text())
 vp=json.loads((VOICE/"VOICE_PROFILE.json").read_text())
 align=json.loads((VOICE/"VOICE_TIMING.json").read_text())
 assert vp["model"]=="gemini-3.1-flash-tts-preview" and vp["voice"]=="Gacrux"
 assert vp["script_sha256"]==sha(BRIEF),"VOICE_SCRIPT_CHANGED_AFTER_SYNTHESIS"
 assert vp["wav_sha256"]==sha(VOICE/"VOCE.wav")
 assert len(align["scenes"])==len(brief["beats"])==27
 assert align["word_match_fraction"]>=.78 and align["duration_seconds"]<=165
 assert 85<=align["duration_seconds"]
 for beat,span in zip(brief["beats"],align["scenes"]):
  assert beat["id"]==span["id"] and beat["narration"]==span["narration"]
  assert span["duration"]>=2.2
  assert span["end"]>span["start"]
 return brief,vp,align
def soft_canvas(source,headline=None,subline=None,kind="still"):
 src=Image.open(source).convert("RGB")
 src=ImageOps.exif_transpose(src)
 bg=ImageOps.fit(src,(W,H),Image.Resampling.LANCZOS,centering=(.5,.5))
 bg=bg.filter(ImageFilter.GaussianBlur(63))
 bg=ImageEnhance.Color(bg).enhance(.78)
 bg=ImageEnhance.Brightness(bg).enhance(.31)
 layer=Image.new("RGB",(W,H),(18,21,24))
 layer=Image.blend(layer,bg,.65)
 # Keep the whole original geoglyph, not a 9:16 crop that cuts its body.
 main=ImageOps.contain(src,(W-44,H-375),Image.Resampling.LANCZOS)
 main=ImageEnhance.Contrast(main).enhance(1.07)
 # Horizontal feather across the photo edges, avoid an artificial hard frame.
 mask=Image.new("L",main.size,255)
 m=ImageDraw.Draw(mask)
 edge=min(24,max(6,main.height//22))
 for y in range(edge):
  alpha=round(255*(y+1)/edge)
  m.line((0,y,main.width,y),fill=alpha)
  m.line((0,main.height-1-y,main.width,main.height-1-y),fill=alpha)
 y=(H-main.height)//2-5
 layer.paste(main,((W-main.width)//2,y),mask)
 if headline:
  d=ImageDraw.Draw(layer)
  hfont=font(110 if len(headline)<8 else 53)
  b=d.textbbox((0,0),headline,font=hfont,stroke_width=0)
  tw=b[2]-b[0]
  x=max(32,(W-tw)//2)
  d.text((x,130),headline,font=hfont,fill=(246,239,221),
         stroke_width=2,stroke_fill=(18,23,30))
  if subline:
   sf=font(29,False)
   d.text((W//2,283),subline,font=sf,anchor="mm",
          fill=(235,223,202),stroke_width=1,stroke_fill=(18,23,30))
 return layer
def graphic(kind,poster_bg):
 # This is typography/data visualization, NOT an invented image of a new geoglyph.
 layer=soft_canvas(poster_bg)
 dark=Image.new("RGB",(W,H),(10,19,26))
 layer=Image.blend(layer,dark,.60)
 d=ImageDraw.Draw(layer)
 if kind=="AI SCREENING":
  d.text((W//2,420),"2024",font=font(90),anchor="mm",fill=(245,227,180))
  d.text((W//2,630),"IMMAGINI AEREE",font=font(48),anchor="mm",fill=(246,243,229))
  d.text((W//2,735),"↓",font=font(72),anchor="mm",fill=(210,192,142))
  d.text((W//2,852),"ANALISI ASSISTITA",font=font(41),anchor="mm",fill=(246,243,229))
  d.text((W//2,965),"↓",font=font(72),anchor="mm",fill=(210,192,142))
  d.text((W//2,1090),"VERIFICA SUL CAMPO",font=font(41),anchor="mm",fill=(246,243,229))
 else:
  d.text((W//2,620),"303",font=font(270),anchor="mm",fill=(244,223,166))
  d.text((W//2,810),"NUOVI GEOGLIFI",font=font(54),anchor="mm",fill=(250,243,228))
  d.text((W//2,890),"FIGURATIVI",font=font(54),anchor="mm",fill=(250,243,228))
  d.text((W//2,1040),"Confermati sul terreno",font=font(33,False),anchor="mm",fill=(226,213,184))
 d.text((W//2,1690),"SAKAI E COLL.  ·  PNAS 2024",font=font(28,False),
        anchor="mm",fill=(204,205,201))
 return layer
def music_download():
 mp=OUT/"FLOATING_CITIES_CC_BY4.mp3"
 if mp.is_file():raise RuntimeError("MUSIC_PREEXISTS_UNTRACKED")
 urls=[MUSIC["url"],"https://www.incompetech.com/music/royalty-free/mp3-royaltyfree/Floating%20Cities.mp3",
       "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Aftermath.mp3"]
 for url in urls:
  try:
   req=urllib.request.Request(url,headers=UA)
   with urllib.request.urlopen(req,timeout=40) as response:
    raw=response.read(14_000_001)
   if not 150_000<=len(raw)<=14_000_000:raise ValueError("MUSIC_SIZE_INVALID")
   mp.write_bytes(raw)
   probe=json.loads(run(["ffprobe","-v","error","-show_format","-of","json",mp],40))
   duration=float(probe["format"]["duration"])
   if duration<80:raise ValueError("MUSIC_DURATION_TOO_SHORT")
   used_title="Floating Cities" if "Floating" in url else "Aftermath"
   meta=dict(MUSIC)
   meta["title"]=used_title
   if used_title=="Aftermath":
    meta["official_page"]="https://commons.wikimedia.org/wiki/File:Aftermath_(ISRC_USUAN1100575).mp3"
    meta["isrc"]="USUAN1100575"
    meta["license"]="CC BY 3.0"
    meta["license_url"]="https://creativecommons.org/licenses/by/3.0/"
   meta.update({"source_url":url,"sha256":sha(mp),"duration":duration,"bytes":mp.stat().st_size})
   print("NAZCA_LICENSED_MUSIC_REAL",meta["title"],"seconds",duration,flush=True)
   return mp,meta
  except Exception as exc:
   mp.unlink(missing_ok=True)
   print("MUSIC_CANDIDATE_UNAVAILABLE",type(exc).__name__,str(exc)[:85],flush=True)
 raise RuntimeError("NO_CREDITED_LICENSED_REAL_MUSIC_AVAILABLE")
def segment_still(plate,seconds,dest,first,last):
 frames=max(1,round(seconds*FPS))
 # 3.5% total zoom over 6 seconds: subtle micro-motion, never a 1s flash.
 zoom="zoompan=z='min(zoom+0.00019,1.042)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=%dx%d:fps=%d"%(W,H,FPS)
 vf=zoom+",format=yuv420p"
 if last:
  vf+=",fade=t=out:st=%.2f:d=0.65"%max(.1,seconds-.70)
 run(["ffmpeg","-hide_banner","-loglevel","error","-y",
      "-loop","1","-framerate",str(FPS),"-i",plate,
      "-frames:v",frames,"-vf",vf,"-an","-r",str(FPS),
      "-c:v","libx264","-preset","veryfast","-crf","21",
      "-pix_fmt","yuv420p","-movflags","+faststart",dest],timeout=210)
 return frames
def segment_video(origin,offset,seconds,dest,first,last):
 # Real source 2011 Theora OGV. Retain motion; do not simulate ancient faces.
 fg=(f"[0:v]split=2[b][f];"
     f"[b]scale={W}:{H}:force_original_aspect_ratio=increase,"
     f"crop={W}:{H},boxblur=36:3,eq=brightness=-0.18:saturation=0.80[blur];"
     f"[f]scale={W}:-2:flags=lanczos[real];"
     f"[blur][real]overlay=x=(W-w)/2:y=(H-h)/2:shortest=1,format=yuv420p")
 if first:fg+=",fade=t=in:st=0:d=0.45"
 if last:fg+=",fade=t=out:st=%.3f:d=0.65"%max(.1,seconds-.72)
 fg+="[v]"
 run(["ffmpeg","-hide_banner","-loglevel","error","-y",
      "-ss",str(offset),"-i",origin,"-t",f"{seconds:.3f}",
      "-filter_complex",fg,"-map","[v]","-an","-r",str(FPS),
      "-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",
      "-movflags","+faststart",dest],timeout=190)
 return max(1,round(seconds*FPS))
def main():
 if os.environ.get("GIULIANO_NAZCA_RENDER_SOURCE_ONLY")!="1":
  raise SystemExit("RENDER_EXPLICIT_SOURCE_ONLY_FLAG_NOT_SET")
 OUT.mkdir(parents=True,exist_ok=True)
 SEGMENTS.mkdir(exist_ok=True);PLATES.mkdir(exist_ok=True)
 source,photos=validated_sources()
 brief,vprofile,timing=validated_voice()
 music,mm=music_download()
 done=[];seen_photo=set()
 for idx,(beat,t) in enumerate(zip(brief["beats"],timing["scenes"])):
  length=t["duration"];dst=SEGMENTS/("%02d.mp4"%(idx+1))
  headline="NAZCA" if idx==0 else None
  video=source["real_video"]
  row={"id":beat["id"],"cue":beat["narration"],"duration_s":length,
       "start_s":t["start"],"end_s":t["end"],"asset_type":beat["asset_type"],
       "narrative_reason":beat["direction"]}
  if beat["asset_type"]=="photo":
   chosen=photos.get(beat["asset_title"])
   if not chosen:raise RuntimeError("MISSING_LICENSED_PHOTO:"+beat["asset_title"])
   inp=SOURCE/chosen["filename"]
   plate=PLATES/("%02d.jpg"%(idx+1))
   layer=soft_canvas(inp)
   layer.save(plate,quality=93,subsampling=0)
   segment_still(plate,length,dst,idx==0,idx==len(brief["beats"])-1)
   seen_photo.add(chosen["title"])
   row.update({"media_source":chosen["title"],"license":chosen["license"],
               "source_sha256":chosen["sha256"],"source_kind":"real Commons still"})
  elif beat["asset_type"]=="film":
   offset=float(beat["film_start_s"])
   if not 0<=offset and offset+length<=video["duration_s"]:raise RuntimeError("VIDEO_TIME_RANGE_INVALID")
   if offset+length>=video["duration_s"]-.2:raise RuntimeError("VIDEO_TIME_EXCEEDS_SOURCE")
   segment_video(SOURCE/video["filename"],offset,length,dst,idx==0,idx==len(brief["beats"])-1)
   row.update({"media_source":video["title"],"license":video["license"],
               "source_sha256":video["sha256"],"source_kind":"real airborne documentary video",
               "source_start_s":offset})
  elif beat["asset_type"]=="graphic":
   plate=PLATES/("%02d.jpg"%(idx+1))
   graphic(beat["asset_title"],SOURCE/"nazca_00.jpg").save(plate,quality=91)
   segment_still(plate,length,dst,idx==0,idx==len(brief["beats"])-1)
   row.update({"media_source":"original graphic, PNAS Sakai et al. 2024",
               "license":"Original editorial typography; no scientific images copied",
               "source_kind":"nonphotographic statistics"})
  else:raise RuntimeError("UNKNOWN_BEAT_ASSET")
  if not dst.is_file() or dst.stat().st_size<11000:raise RuntimeError("SEGMENT_NOT_RENDERED")
  row["segment_sha256"]=sha(dst);done.append(row)
  print("NAZCA_TRUE_SHOT",row["id"],row["asset_type"],"seconds",length,"source",row["media_source"][:50],flush=True)
 if len(seen_photo)<19:raise RuntimeError("TOO_FEW_DISTINCT_AUTHENTIC_PHOTOS:"+str(len(seen_photo)))
 if sum(r["asset_type"]=="film" for r in done)<4:raise RuntimeError("REAL_VIDEO_UNDERUSED")
 concat=OUT/"scenes.ffconcat"
 concat.write_text("ffconcat version 1.0\n"+
                  "".join("file '"+x.resolve().as_posix()+"'\n" for x in sorted(SEGMENTS.glob("*.mp4"))))
 master=OUT/"GIULIANO_04_NAZCA_THE_DESERT_THAT_REMEMBERS_MASTER.mp4"
 duration=float(timing["duration_seconds"])
 audiofilter=(f"[1:a]loudnorm=I=-17:TP=-1.5:LRA=9[v];"
              f"[2:a]volume=0.10,afade=t=in:st=0:d=1.3,"
              f"afade=t=out:st={max(0,duration-2.2):.3f}:d=2.0[m];"
              f"[v][m]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
              f"alimiter=limit=0.94[a]")
 # concat video is H264 copy; preserve all 27 real scene durations.
 run(["ffmpeg","-hide_banner","-loglevel","error","-y",
      "-safe","0","-f","concat","-i",concat,
      "-i",VOICE/"VOCE.wav","-i",music,
      "-filter_complex",audiofilter,
      "-map","0:v:0","-map","[a]","-t",f"{duration:.3f}",
      "-c:v","copy","-c:a","aac","-b:a","192k",
      "-movflags","+faststart",master],timeout=340)
 android=OUT/"GIULIANO_04_NAZCA_ANDROID.mp4"
 run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",master,
      "-vf","scale=720:1280:flags=lanczos","-c:v","libx264","-preset","veryfast",
      "-crf","24","-pix_fmt","yuv420p","-c:a","aac","-b:a","144k",
      "-movflags","+faststart",android],timeout=420)
 outputs={}
 for fp in [master,android]:
  dat=json.loads(run(["ffprobe","-v","error","-show_format","-show_streams","-of","json",fp],50))
  stream_v=next(x for x in dat["streams"] if x.get("codec_type")=="video")
  stream_a=next(x for x in dat["streams"] if x.get("codec_type")=="audio")
  dur=float(dat["format"]["duration"])
  assert stream_v["codec_name"]=="h264" and stream_a["codec_name"]=="aac"
  assert 0<abs(dur-duration)<1.3 or abs(dur-duration)<=.01,(dur,duration)
  if fp==master:assert (stream_v["width"],stream_v["height"])==(1080,1920)
  else:assert (stream_v["width"],stream_v["height"])==(720,1280)
  run(["ffmpeg","-hide_banner","-v","error","-xerror","-i",fp,"-f","null","-"],timeout=500)
  outputs[fp.name]={"bytes":fp.stat().st_size,"sha256":sha(fp),"seconds":dur,
                    "resolution":[stream_v["width"],stream_v["height"]],
                    "video_codec":"h264","audio_codec":"aac","complete_decode":"PASS"}
  print("NAZCA_REAL_MP4_FULL_DECODE_PASS",fp.name,outputs[fp.name],flush=True)
 # QA contact sheet extracted from ACTUAL master (not assembled static plates).
 thumbdir=OUT/"qa_frames";thumbdir.mkdir()
 sheets=[];times=[]
 for i,beat in enumerate(done):
  t=float(beat["start_s"])+min(.9,beat["duration_s"]*.38)
  dest=thumbdir/("frame_%02d.jpg"%(i+1))
  run(["ffmpeg","-v","error","-y","-ss",f"{t:.3f}","-i",master,
       "-frames:v","1","-vf","scale=225:400",dest],timeout=45)
  with Image.open(dest) as im:
   img=im.convert("RGB").copy()
  sheets.append(img);times.append(t)
 sheet=Image.new("RGB",(225*5,445*((len(sheets)+4)//5)),(15,17,20))
 draw=ImageDraw.Draw(sheet)
 for i,im in enumerate(sheets):
  x=(i%5)*225;y=(i//5)*445
  sheet.paste(im,(x,y))
  draw.text((x+10,y+404),f"{i+1:02d} · {done[i]['start_s']:.1f}s",
            fill=(235,232,223),font=font(19,False))
 sheet.save(OUT/"CONTACT_SHEET_TRUE_MP4.jpg",quality=88)
 # Cover uses authentic aerial hummingbird photo; never AI-generated artwork.
 selected=photos["Líneas de Nazca, Nazca, Perú, 2015-07-29, DD 52.JPG"]
 cover=soft_canvas(SOURCE/selected["filename"])
 dc=ImageDraw.Draw(cover)
 dc.rectangle((0,0,W,420),fill=(14,20,26))
 dc.text((W//2,95),"GIULIANO 04",font=font(35,False),anchor="mm",fill=(229,217,184))
 dc.text((W//2,205),"NAZCA",font=font(125),anchor="mm",fill=(248,235,210))
 dc.text((W//2,320),"THE DESERT THAT REMEMBERS",font=font(32),anchor="mm",fill=(240,234,224))
 cover.save(OUT/"GIULIANO_04_NAZCA_COVER.jpg",quality=93)
 social=(
  "NAZCA — THE DESERT THAT REMEMBERS | GIULIANO 04\n\n"
  "Il colibrì, la scimmia, le geometrie nel deserto. Un lavoro di migliaia "
  "di persone e una scoperta che ha cambiato il modo di osservare Nazca: "
  "303 geoglifi figurativi confermati grazie a ricerca sul campo assistita dall'IA.\n\n"
  "Fonti scientifiche: UNESCO https://whc.unesco.org/en/list/700/ ; "
  "Sakai et al., PNAS (2024): https://doi.org/10.1073/pnas.2407652121\n"
  "Fotografie e riprese aeree: Wikimedia Commons, autori e licenze individuali "
  "in AUTHORS_CREDITS.txt e SOURCE_CURATED.json. Le fotografie mostrano "
  "figure già note, NON vengono spacciate per i 303 nuovi ritrovamenti.\n"
  "Musica: "+mm["title"]+" — Kevin MacLeod (incompetech.com), "+mm["license"]+
  ", "+mm["license_url"]+" ; modifica: taglio, ducking, volume, fade.\n"
  "Voce italiana: Google Gemini 3.1 Gacrux.\n"
  "#Nazca #NazcaLines #Peru #Archaeology #Giuliano #Geoglyphs\n"
 )
 (OUT/"SOCIAL_DESCRIPTION_IT.txt").write_text(social,encoding="utf-8")
 (OUT/"AUTHORS_CREDITS.txt").write_text((SOURCE/"AUTHORS_CREDITS.txt").read_text()+
   f"\nMUSIC | {mm['title']} | {mm['author']} | {mm['official_page']} | {mm['license_url']} | {mm['sha256']}\n"+
   "Edited for vertical format, spatial blur only from same original photograph; factual scientific graphics are original.\n",encoding="utf-8")
 write_cues={"schema":"nazca-shotmap-true-wav-v1","shots":done,
             "actual_photos_distinct":len(seen_photo),"real_video_shots":sum(x["asset_type"]=="film" for x in done),
             "graphic_shots":sum(x["asset_type"]=="graphic" for x in done),
             "voice_alignment":timing}
 jwrite(OUT/"SHOTMAP_REAL_VOICE.json",write_cues)
 manifest={"title":TITLE,"schema":"giuliano-nazca-master-verified-v1","publication_status":"OWNER_REVIEW_ONLY",
           "technical_status":"TECHNICAL_PASS_ARTISTIC_PENDING",
           "artistic_approval":False,"rights_review_required_for_CC_BY_SA_adaptations":True,
           "real_photos_used":len(seen_photo),"video_shots_from_licensed_real_aerial_footage":4,
           "has_unlicensed_video":False,"synthetic_video_calls":0,"google_tts_additional_calls_in_render":0,
           "film_owner_source_run":source["original_action_run"],
           "voice_profile":vprofile,"music":mm,"deliverables":outputs,
           "scientific_sources":brief["cited_research"]}
 jwrite(OUT/"QA_TECHNICAL.json",manifest)
 # Compact review ZIP - includes master, android, cover, credits, source attribution,
 # actual voice sync, social copy, QA and actual MP4 contact sheet.
 package=OUT/"GIULIANO_04_NAZCA_COMPLETE_REVIEW.zip"
 with zipfile.ZipFile(package,"w",zipfile.ZIP_DEFLATED,compresslevel=3) as z:
  for path in [master,android,OUT/"GIULIANO_04_NAZCA_COVER.jpg",
               OUT/"CONTACT_SHEET_TRUE_MP4.jpg",OUT/"SHOTMAP_REAL_VOICE.json",
               OUT/"AUTHORS_CREDITS.txt",OUT/"SOCIAL_DESCRIPTION_IT.txt",
               OUT/"QA_TECHNICAL.json",SOURCE/"SOURCE_CURATED.json",
               VOICE/"VOICE_PROFILE.json",VOICE/"VOICE_TIMING.json",BRIEF]:
   z.write(path,arcname=path.name)
 with zipfile.ZipFile(package) as z:
  assert z.testzip() is None
 print("GIULIANO_04_NAZCA_RENDER_COMPLETE",json.dumps({"duration":duration,"shots":len(done),
    "real_photos":len(seen_photo),"real_video_shots":4,
    "master":outputs[master.name],"android":outputs[android.name],
    "zip_bytes":package.stat().st_size},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
