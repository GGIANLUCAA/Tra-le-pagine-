#!/usr/bin/env python3
"""GIULIANO Antikythera — factual film renderer and director gate, no AI video.

Input: licensed original museum photos + modern CC BY reconstruction MP4s,
from the source scout. First check full provenance, then single approved
Google Gacrux narration. Build shot cuts from REAL spoken sentence alignment.
Always fail closed on source/voice/QA issues; do not auto-publish.
"""
import hashlib,json,math,os,subprocess,sys,wave,zipfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps,ImageFilter,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import gemini_voice
from giuliano_antikythera_preflight_v1 import inspect as preflight
BRIEF=ROOT/"research/giuliano_antikythera_v1/BRIEF_AI_DIRECTOR.json"
OUT=ROOT/"output"/"giuliano_antikythera_film_v1"
MEDIA=OUT/"sources"
W,H,FPS=720,1280,24
OUT.mkdir(parents=True,exist_ok=True)
def ff(*args,quiet=True):
 cmd=["ffmpeg","-nostdin","-hide_banner","-loglevel","error" if quiet else "info","-y",*map(str,args)]
 subprocess.run(cmd,check=True)
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
 return h.hexdigest()
def font(n=30,b=False):
 name="DejaVuSans-Bold.ttf" if b else "DejaVuSans.ttf"
 return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/"+name,n)
def metadata():
 return json.loads((MEDIA/"FONTI_VIDEO_QA.json").read_text(encoding="utf-8"))
def picks(meta):
 pics=[r for r in meta["items"] if r["type"]=="photo" and r.get("depicts")=="original_fragment_candidate"]
 pids=[r for r in pics if Path(r["local_path"]).name in {"authentic_02.jpg","authentic_04.jpg","authentic_05.jpg","authentic_06.jpg","authentic_07.jpg","authentic_08.jpg","authentic_09.jpg"}]
 film={r["name"]:r for r in meta["items"] if r["type"]=="reconstruction_video"}
 if len(pids)<7 or len(film)!=2:raise RuntimeError("Not enough verified original photos or licensed moving media")
 for r in meta["items"]:
  target=MEDIA/Path(r["local_path"]).relative_to(Path(r["local_path"]).parents[1])
  # GitHub Actions artifact relocation may shift root; use the original file's last two path parts.
  if r["type"]=="photo":target=MEDIA/"museum_photos"/Path(r["local_path"]).name
  else:target=MEDIA/r["name"]
  if not target.is_file() or sha(target)!=r["sha256"]:
   raise RuntimeError("Untrusted/corrupt source "+str(target))
  r["real_local_path"]=target
 return pics,film
def image_source(scene,pics):
 order={"museum":[4,0,1,2,3,5,6],"macro":[0,5,6,3,4,1,2],
        "front":[3,1,4,0,6,5,2],"other":[2,5,1,0,3,6,4],
        "mechanism":[4,1,2,5,6,3,0]}
 kind=scene["asset_id"]
 idx=order.get(kind,[0])[int(scene["id"][1:])%7] if kind in order else 0
 return pics[idx]["real_local_path"]
def diagram(out,kind,topic):
 im=Image.new("RGB",(W,H),(13,25,34));d=ImageDraw.Draw(im)
 for y in range(0,H,20):d.line([(0,y),(W,y)],fill=(18,30,40),width=1)
 d.text((39,49),"GIULIANO / ANTICITERA",font=font(25,True),fill=(230,208,168))
 if kind=="map":
  d.text((42,185),"MAR EGEO",font=font(76,True),fill=(245,231,206))
  d.text((44,272),"Scoperta del relitto · 1900",font=font(27),fill=(194,204,214))
  d.ellipse((242,445,489,740),outline=(69,106,129),width=3)
  d.text((42,435),"GRECIA",font=font(34),fill=(195,195,181))
  d.text((418,778),"CRETA",font=font(35),fill=(195,195,181))
  d.ellipse((340,672,358,690),fill=(238,178,100))
  d.text((92,707),"ANTICITERA",font=font(40,True),fill=(239,192,122))
  d.line((300,727,348,681),fill=(239,192,122),width=3)
  d.text((41,1140),"SCHEMA GEOGRAFICO ILLUSTRATIVO",font=font(21),fill=(173,191,201))
 elif kind=="calendar":
  saros=topic=="ciclo_saros"
  d.text((40,174),"223 MESI LUNARI" if saros else "19 ANNI",font=font(66,True),fill=(243,220,172))
  d.text((43,275),"Ciclo di Saros · Eclissi" if saros else "235 mesi lunari · Ciclo metonico",font=font(29),fill=(205,209,202))
  for radius in (245,180,95):
   d.ellipse((360-radius,645-radius,360+radius,645+radius),outline=(109,144,148),width=3)
  d.ellipse((334,618,388,672),fill=(232,186,109))
  d.ellipse((560,620,603,663),fill=(186,198,209))
  d.arc((90,375,630,915),start=215,end=339,fill=(229,185,119),width=8)
  d.text((54,1060),"CICLI CALCOLATI CON RUOTE DENTATE",font=font(25,True),fill=(209,216,205))
  d.text((54,1128),"SCHEMA DIDATTICO · NON UN QUADRANTE REALE",font=font(18),fill=(166,179,186))
 elif kind=="xray":
  d.text((40,177),"DENTRO IL BRONZO",font=font(45,True),fill=(235,221,191))
  d.text((43,246),"Raggi X e lettura delle iscrizioni",font=font(27),fill=(191,198,207))
  for n in range(15):
   xx=85+n*38
   d.line((xx,420,xx+120,960),fill=(65,118,143),width=3)
  d.ellipse((177,565,542,930),outline=(233,183,112),width=18)
  for a in range(18):
   ang=a*math.pi/9;cx=359+166*math.cos(ang);cy=748+166*math.sin(ang)
   d.ellipse((cx-10,cy-10,cx+10,cy+10),fill=(233,183,112))
  d.text((39,1090),"ILLUSTRAZIONE SCIENTIFICA",font=font(26,True),fill=(226,208,171))
  d.text((39,1140),"NON È UNA RADIOGRAFIA ORIGINALE",font=font(20),fill=(184,196,206))
 im.save(out,quality=92)
def still_canvas(image,target,title=False):
 im=ImageOps.exif_transpose(Image.open(image)).convert("RGB")
 bg=ImageOps.fit(im,(W,H),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(30))
 bg=Image.blend(bg,Image.new("RGB",(W,H),(9,14,21)),.69)
 fg=ImageOps.contain(im,(W-32,820),Image.Resampling.LANCZOS)
 x=(W-fg.width)//2;y=255+(820-fg.height)//2
 bg.paste(fg,(x,y))
 d=ImageDraw.Draw(bg)
 d.line((x,y+fg.height+16,x+fg.width,y+fg.height+16),fill=(197,165,120),width=3)
 if title:
  d.text((37,62),"GIULIANO / DOCUMENTARI",font=font(22,True),fill=(229,196,139))
  d.text((27,1058),"THE ANCIENT",font=font(59,True),fill=(255,249,236))
  d.text((27,1136),"COMPUTER",font=font(73,True),fill=(255,249,236))
 bg.save(target,quality=92)
def clip_photo(canvas,dur,out):
 ff("-loop","1","-framerate",FPS,"-i",canvas,"-t",f"{dur:.5f}",
    "-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p","-r",FPS,"-an",out)
def clip_video(src,dur,out,start):
 # Aspect-safe original 16:9 in 9:16 cinema, with a matching blurred background.
 crop=("[0:v]split=2[b][f];[b]scale=720:1280:force_original_aspect_ratio=increase,"
       "crop=720:1280,boxblur=18:4[back];"
       "[f]scale=720:1280:force_original_aspect_ratio=decrease[front];"
       "[back][front]overlay=(W-w)/2:(H-h)/2,"
       "drawbox=x=0:y=63:w=iw:h=84:color=black@0.76:t=fill,"
       "drawtext=text='RICOSTRUZIONE MODERNA':fontcolor=white:"
       "fontsize=27:x=(w-text_w)/2:y=90,format=yuv420p[v]")
 ff("-stream_loop","-1","-ss",f"{start:.3f}","-i",src,
    "-filter_complex",crop,"-map","[v]","-t",f"{dur:.5f}",
    "-r",FPS,"-c:v","libx264","-preset","veryfast",
    "-crf","23","-pix_fmt","yuv420p","-an",out)
def timed_beats(brief,voice_timed,audio_dur):
 lines=[x["narration_excerpt"] for x in brief["scenes"]]
 groups=[gemini_voice.sentences(line) for line in lines]
 wanted=sum(len(g) for g in groups)
 if wanted!=len(voice_timed):raise RuntimeError(f"ASR sentence alignment unexpected: {len(voice_timed)} != {wanted}")
 starts=[];idx=0
 for group in groups:
  if not group:raise RuntimeError("Empty voiced scene")
  starts.append(float(voice_timed[idx][1]))
  idx+=len(group)
 starts[0]=0.
 intervals=[]
 for i,shot in enumerate(brief["scenes"]):
  start=starts[i]
  end=starts[i+1] if i+1<len(starts) else audio_dur+1.2
  if end<start+1:raise RuntimeError("Invalid phrase timing, do not fabricate synchronization")
  intervals.append((start,end))
 return intervals
def main():
 brief=json.loads(BRIEF.read_text(encoding="utf-8"))
 meta=metadata()
 if meta["status"]!="candidate_sources_downloaded_preproduction":raise RuntimeError("Licensing/source stage did not pass")
 pics,films=picks(meta)
 shots=brief["scenes"]
 # Actual locally available media becomes the source of truth for the creation gate.
 generated={}
 for kind in ("map","calendar","xray"):
  p=MEDIA/(kind+".jpg")
  diagram(p,kind,kind)
  generated[kind]=p
 registered={"museum":pics[4]["real_local_path"],"macro":pics[0]["real_local_path"],
 "front":pics[3]["real_local_path"],"other":pics[2]["real_local_path"],
 "mechanism":pics[4]["real_local_path"],
 "gear_motion":films["antikythera_gears_20s.mp4"]["real_local_path"],
 "gear_exploded":films["antikythera_exploded_15s.mp4"]["real_local_path"],**generated}
 render_brief=json.loads(json.dumps(brief))
 for s in render_brief["scenes"]:
  file=registered[s["asset_id"]]
  s["asset_checksum_verified"]=s["asset_download_verified"]=True
  s["local_asset"]=str(file.relative_to(MEDIA))
  s["asset_sha256"]=sha(file)
 gate=preflight(render_brief,asset_dir=MEDIA,phase="render")
 (OUT/"RENDER_PREFLIGHT_QA.json").write_text(json.dumps(gate,indent=2,ensure_ascii=False)+"\n")
 if not gate["ready_for_voice_or_render"]:
  raise RuntimeError("Director gate blocking actual production: "+str(gate["issues"][:2]))
 text="\n\n".join(s["narration_excerpt"] for s in shots)
 gemini_voice.STYLE=("Calm, natural Italian documentary voice, confident but conversational. "
 "Like a thoughtful television reporter in a museum. No dramatic trailer reading, no fake suspense. "
 "Vary sentence pacing naturally with factual clarity, allowing breath between ideas.")
 wav_dir=OUT/"audio"
 audio,timed=gemini_voice.synthesize(text,wav_dir)
 audio_dur=len(audio)/24000
 if not (125<=audio_dur<=170):raise RuntimeError("Narration length outside approved 2m05-2m50 range")
 intervals=timed_beats(brief,timed,audio_dur)
 shotsdir=OUT/"shots";shotsdir.mkdir(exist_ok=True)
 video_offsets={"gear_motion":[1,4,8,12,0,6,9],"gear_exploded":[1,5,8,0]}
 vcounter={"gear_motion":0,"gear_exploded":0}
 files=[];timeline=[]
 for i,(shot,(begin,end)) in enumerate(zip(shots,intervals)):
  duration=end-begin
  if duration<2.45:
   # Avoid the Moai 1-second image error: keep the previous visual for short clauses.
   if files:
    timeline.append({"id":shot["id"],"voice_line":shot["narration_excerpt"],"visual_carried_from_previous":True,
                    "start_s":round(begin,3),"end_s":round(end,3)})
    # Extend previous segment by the short clause without showing a third image.
    prev=files[-1]
    olddur=prev[2]
    newdur=olddur+duration
    if prev[3]=="photo":clip_photo(prev[4],newdur,prev[0])
    else:clip_video(prev[4],newdur,prev[0],prev[5])
    files[-1]=(prev[0],prev[1],newdur,prev[3],prev[4],prev[5])
    continue
   raise RuntimeError("Opening phrase too short for safe montage")
  out=shotsdir/(f"{i+1:02d}.mp4")
  kind=shot["asset_id"]
  if kind in video_offsets:
   n=vcounter[kind];vcounter[kind]+=1
   offset=video_offsets[kind][n%len(video_offsets[kind])]
   film=registered[kind]
   clip_video(film,duration,out,offset)
   media_kind="reconstruction_video";memo=film
  else:
   src=image_source(shot,pics) if shot["visual_kind"]=="photo" else registered[kind]
   canvas=shotsdir/(f"{i+1:02d}.jpg")
   still_canvas(src,canvas,i==0) if shot["visual_kind"]=="photo" else canvas.write_bytes(Path(src).read_bytes())
   clip_photo(canvas,duration,out)
   media_kind="photo";memo=canvas
  files.append((out,shot["id"],duration,media_kind,memo,0))
  timeline.append({"id":shot["id"],"voice_line":shot["narration_excerpt"],"start_s":round(begin,3),"end_s":round(end,3),
      "media_kind":media_kind,"media_source":str(registered.get(kind,"original diagram")),"duration":round(duration,3)})
 durations=[x[2] for x in files]
 if min(durations)<2.45:raise RuntimeError("Undersized visual still remains")
 concat=OUT/"segments.txt"
 concat.write_text("".join("file '"+str(row[0].resolve())+"'\n" for row in files),encoding="utf-8")
 silent=OUT/"ANTIKYTHERA_SILENT.mp4"
 ff("-f","concat","-safe","0","-i",concat,"-c:v","copy","-movflags","+faststart",silent)
 # Original ambient score, mixed well under broadcast narration.
 samples=round((audio_dur+2)*24000)
 t=np.arange(samples,dtype=np.float32)/24000
 pad=(np.sin(2*np.pi*110*t)*.009+np.sin(2*np.pi*164.82*t)*.004+
      np.sin(2*np.pi*220*t)*.003)*(np.minimum(1,t/4)*np.minimum(1,(samples/24000-t)/4))
 import soundfile as sf
 score=OUT/"ORIGINAL_AMBIENT_SCORE.wav"
 sf.write(score,pad.astype("float32"),24000)
 sound=OUT/"MIX.wav"
 ff("-i",wav_dir/"VOCE.wav","-i",score,"-filter_complex",
    "[0:a]volume=1.1[a];[1:a]volume=0.5[b];[a][b]amix=inputs=2:duration=longest:dropout_transition=0[m]",
    "-map","[m]","-c:a","pcm_s16le",sound)
 hd=OUT/"GIULIANO_ANTICITERA_CINEMA_HD.mp4"
 ff("-i",silent,"-i",sound,"-map","0:v:0","-map","1:a:0",
    "-c:v","libx264","-crf","20","-preset","veryfast","-pix_fmt","yuv420p",
    "-vf","scale=1080:1920:flags=lanczos","-c:a","aac","-b:a","160k",
    "-movflags","+faststart","-shortest",hd)
 ff("-v","error","-xerror","-i",hd,"-f","null","-")
 android=OUT/"GIULIANO_ANTICITERA_ANDROID.mp4"
 ff("-i",hd,"-vf","scale=720:1280:flags=lanczos","-c:v","libx264",
    "-preset","veryfast","-crf","28","-c:a","aac","-b:a","112k","-movflags","+faststart",android)
 ff("-v","error","-xerror","-i",android,"-f","null","-")
 # Explicitly do not claim real speech-to-frame perfection: alignment ASR has a confidence rating.
 aligns=json.loads((wav_dir/"ALLINEAMENTO_VOCE.json").read_text())
 qa={"status":"VIDEO_COMPLETE_TECHNICAL_QA_ARTISTIC_REVIEW_PENDING",
     "g0dm0d3_role":"Existing zero-inference AI Director V1 preflight used before rendering",
     "source_count":len(pics),"modern_reconstruction_label_present":True,
     "original_1900_diver_video_faked":False,"narration_seconds":round(audio_dur,2),
     "planned_seconds":brief["target_duration_seconds"],"visual_shots":len(files),
     "shortest_shot_s":round(min(durations),3),"voice_alignment":aligns,
     "timeline":timeline,"premiere_authorized":False,"published":False,
     "hd_sha256":sha(hd),"android_sha256":sha(android)}
 (OUT/"QA_FILM.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 cover=OUT/"COVER_ANTICITERA.jpg"
 still_canvas(pics[4]["real_local_path"],cover,True)
 (OUT/"ATTRIBUZIONI.txt").write_text(
 "GIULIANO · THE ANCIENT COMPUTER\n"
 "Fotografie: Wikimedia Commons, singoli autori e licenze elencati in sources/FONTI_VIDEO_QA.json.\n"
 "Ricostruzioni video: Antikythera Mechanism reconstruction by taciclei, CC BY 4.0; modificate per il formato verticale.\n"
 "ATTENZIONE: la posizione dei pianeti nelle sequenze 3D resta una ricostruzione scientifica, non certezza storica.\n"
 "Nessuna ripresa d'immersione del 1900 è presentata come autentica.\n"
 "Fonti: antikythera.org.gr, Museo archeologico nazionale di Atene, Nature 2006 e Nature Astronomy 2018.\n"
 "Testo, narrazione italiana e colonna sonora originali. Nessuna pubblicazione automatica.\n",encoding="utf-8")
 pack=OUT/"GIULIANO_ANTICITERA_COMPLETO.zip"
 with zipfile.ZipFile(pack,"w",zipfile.ZIP_DEFLATED,compresslevel=5) as z:
  for p in [hd,android,cover,OUT/"QA_FILM.json",OUT/"ATTRIBUZIONI.txt",MEDIA/"FONTI_VIDEO_QA.json"]:
   z.write(p,p.name)
 with zipfile.ZipFile(pack) as z:
  if z.testzip():raise RuntimeError("Corrupt ZIP")
 print("ANTIKYTHERA_COMPLETED_MP4",{ "voice_s":round(audio_dur,2),
   "shots":len(files),"hd_bytes":hd.stat().st_size,"android_bytes":android.stat().st_size,
   "zip_bytes":pack.stat().st_size},flush=True)
if __name__=="__main__":main()
