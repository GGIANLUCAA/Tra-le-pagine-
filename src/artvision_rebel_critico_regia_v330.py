#!/usr/bin/env python3
"""V330 Bruegel Rebel Angels critic standard: genuine one-shot Gacrux, source locked.
Zero non-free API authorizations; no museum simulation; no touching V135.
"""
import argparse, hashlib, json, os, sys, subprocess, wave, zipfile
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import soundfile as sf

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import gemini_voice
from artvision_critico_review_capture_v1 import capture as capture_artvision_focus
from director_reference_v326 import analyze_scenes, inspect_black_tail

OUT=Path("/tmp/rebel_angels_critico_v330")
RECIPE=ROOT/"modules/artvision_critico/production_series/bruegel_rebel_angels_v144.json"
ART_SHA="09f675e7861da808ede4bc1f85573e97884fdbcc6c1d6cb482e3e449d58aace5"
W,H,FPS=720,1280,20
DELAY,TAIL=3.5,6.0

def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for x in iter(lambda:f.read(1<<20),b""):h.update(x)
 return h.hexdigest()

def run(cmd):
 q=subprocess.run(list(map(str,cmd)),text=True,capture_output=True)
 if q.returncode:raise RuntimeError("FFmpeg: "+q.stderr[-1600:])
 return q.stdout

def load():
 q=json.loads(RECIPE.read_text())
 assert q["work_id"]=="bruegel_fall_rebel_angels_1562_rmfb_584"
 assert q["public_title"]=="The Fall of the Rebel Angels"
 assert q["accession"]=="584" and q["variant"]=="critico_standard"
 assert len(q["chapters"])==9
 script="\n\n".join(c["text"] for c in q["chapters"])
 assert 155<=len(script.split())<=235
 return q,script

def art_check():
 q,_=load()
 art=OUT/"ORIGINAL_ARTWORK.jpg"
 assert art.is_file() and sha(art)==ART_SHA, "Genuine previously checked artwork missing or wrong"
 with Image.open(art) as im:
  assert im.size == (3840,2772) and im.format=="JPEG"
 return art

def voice():
 raise RuntimeError('V330 never synthesizes voice: reuse original V144 only')

 q,script=load()
 art_check()
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/"COPIONE_ESATTO_V330.txt").write_text(script,encoding="utf8")
 assert gemini_voice.MODEL=="gemini-3.8-flash-tts" and gemini_voice.VOICE=="Gacrux"
 if os.environ.get("ARTVISION_GEMINI_PROJECT_BILLING_TIER")!="Free" or not os.environ.get("GEMINI_API_KEY"):
  (OUT/"VOICE_RESULT_V330.json").write_text(json.dumps({"status":"BLOCKED_NO_FREE_ACCOUNT","new_tts_calls":0}))
  raise RuntimeError("Free second account gate absent: zero voice calls")
 try:
  # Small local Whisper avoids the older base model mismatches; no separate ASR API.
  os.environ["ARTVISION_ASR_MODEL"]="small"
  data,timed=gemini_voice.synthesize(script,OUT)
  wav=OUT/"VOCE.wav"
  duration=len(data)/24000
  align=json.loads((OUT/"ALLINEAMENTO_VOCE.json").read_text())
  if not (70<=duration<=160 and align.get("method")=="asr_with_interpolation" and (align.get("matched_fraction") or 0)>=.85):
   raise RuntimeError("Audio stored, but alignment rejected; DO NOT RE-CALL TTS")
  result={"status":"ONE_GENUINE_VOICE_WAV_READY","wav_sha256":sha(wav),"duration_seconds":duration,
    "ASR_match":align["matched_fraction"],"one_voice_for_future_museum":True,
    "authorised_account":"owner-attested Free/no billing second account","Gold_V25":False,
    "museum_approved":False,"published":False}
  (OUT/"VOICE_RESULT_V330.json").write_text(json.dumps(result,indent=2))
 except Exception as e:
  (OUT/"VOICE_RESULT_V330.json").write_text(json.dumps({
   "status":"VOICE_FAILED_NO_AUTOMATIC_RETRY","reason":repr(e)[:250],
   "wav_preserved":(OUT/"VOCE.wav").is_file(),"Gold_V25":False},indent=2))
  raise

def verified_voice(script,chapters):
 wav=OUT/"VOCE.wav"
 cache=json.loads((OUT/"VOICE_CACHE_V13.json").read_text())
 align=json.loads((OUT/"ALLINEAMENTO_VOCE.json").read_text())
 assert sha(wav)==cache["wav_sha256"]
 assert cache["cache_key"]==gemini_voice.cache_key(script)
 assert cache["profile"]["model"]=="gemini-3.8-flash-tts" and cache["profile"]["voice"]=="Gacrux"
 assert align.get("method")=="asr_with_interpolation" and (align.get("matched_fraction") or 0)>=.85
 pcm,sr=sf.read(wav,dtype="float32")
 assert sr==24000 and pcm.ndim==1 and np.isfinite(pcm).all()
 duration=len(pcm)/sr
 sentence_counts=[len(gemini_voice.sentences(c["text"])) for c in chapters]
 timed=cache["timed"]
 assert len(timed)==sum(sentence_counts)
 ends=[];i=0
 for count in sentence_counts:
  i+=count
  ends.append(float(timed[i-1][2]))
 assert ends[-1]<=duration+.1 and ends==sorted(ends)
 return wav,duration,ends,align

def title_card(paint):
 im=Image.new("RGB",(W,H),(16,18,19))
 d=ImageDraw.Draw(im)
 serif="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
 sans="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
 lines=[("THE FALL OF THE",31),("REBEL ANGELS",31)]
 for i,(s,size) in enumerate(lines):
  f=ImageFont.truetype(serif,size)
  bb=d.textbbox((0,0),s,font=f)
  d.text(((W-(bb[2]-bb[0]))//2,104+i*47),s,fill=(232,223,207),font=f)
 sub="PIETER BRUEGEL THE ELDER   ·   1562"
 f=ImageFont.truetype(sans,17)
 bb=d.textbbox((0,0),sub,font=f)
 d.text(((W-(bb[2]-bb[0]))//2,230),sub,fill=(184,175,158),font=f)
 x=paint.copy()
 x.thumbnail((W-28,860),Image.Resampling.LANCZOS)
 im.paste(x,((W-x.width)//2,318))
 return cv2.cvtColor(np.asarray(im),cv2.COLOR_RGB2BGR)

def full_plate(paint):
 im=paint.copy()
 back=ImageEnhance.Brightness(im.resize((W,H)).filter(ImageFilter.GaussianBlur(34))).enhance(.3)
 im.thumbnail((W-18,H-120),Image.Resampling.LANCZOS)
 back.paste(im,((W-im.width)//2,(H-im.height)//2))
 return cv2.cvtColor(np.asarray(back),cv2.COLOR_RGB2BGR)

# These are distinct, motivated camera trajectories, not a generic auto-zoom.
# x,y normalized to the GENUINE full painting; h is a true source-pixel crop.
# Chapter 3 changes subject at its ASR-confirmed second sentence.
ROUTES = {
 2: ((.53,.47,1780),(.53,.50,1480)),   # Michael, his sword and the adversaries
 3: ((.45,.20,1720),(.48,.25,1620)),   # illuminated sky
 4: ((.70,.57,1850),(.69,.61,1650)),   # hybrid beings on the right
 5: ((.24,.73,1700),(.22,.74,1510)),   # toothed creature on the left
 6: ((.46,.71,1650),(.47,.72,1510)),   # butterfly-like figure
 7: ((.53,.54,2340),(.52,.51,2090)),   # relationship of light and darkness
}
ROUTE_CH3_LOWER = ((.49,.55,1990),(.50,.57,1860))


def _ease(u):
 u=max(0.,min(1.,float(u)))
 # Give the viewer a readable hold at entry and before an exit.
 v=max(0.,min(1.,(u-.12)/.76))
 return v*v*(3.-2.*v)


def shot(paint,chapter,u,audit=None,chapter_index=2,part=0):
 ih,iw=paint.shape[:2]
 pair=ROUTE_CH3_LOWER if chapter_index==3 and part==1 else ROUTES[chapter_index]
 t=_ease(u)
 cx=(pair[0][0]*(1-t)+pair[1][0]*t)*iw
 cy=(pair[0][1]*(1-t)+pair[1][1]*t)*ih
 crop_h=round(pair[0][2]*(1-t)+pair[1][2]*t)
 crop_h=max(1,min(ih,crop_h))
 crop_w=round(crop_h*W/H)
 crop_w=max(1,min(iw,crop_w))
 x0=max(0,min(iw-crop_w,round(cx-crop_w/2)))
 y0=max(0,min(ih-crop_h,round(cy-crop_h/2)))
 crop=paint[y0:y0+crop_h,x0:x0+crop_w]
 if crop.size==0:raise RuntimeError("Invalid painting crop")
 if audit is not None:
  audit["camera_crop_xyxy"]=[x0/iw,y0/ih,(x0+crop_w)/iw,(y0+crop_h)/ih]
  audit["director_reason"]={2:"archangel_michael",3:"sky_then_fall",
     4:"hybrid_monsters",5:"open_mouthed_creature",6:"butterfly_figure",
     7:"light_dark_relationship"}[chapter_index]
 return cv2.resize(crop,(W,H),interpolation=cv2.INTER_AREA)


def opening_frame(artwork, sec):
 # An image-led opening replaces the previous black-title-first 2 seconds.
 frame=shot(artwork,None,min(1.,sec/max(DELAY,.1)),chapter_index=2)
 canvas=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)).convert("RGBA")
 layer=Image.new("RGBA",canvas.size,(0,0,0,0))
 draw=ImageDraw.Draw(layer)
 draw.rectangle((0,55,W,275),fill=(11,16,19,178))
 serif="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
 font=ImageFont.truetype(serif,46)
 for k,text in enumerate(("THE FALL OF THE","REBEL ANGELS")):
  bbox=draw.textbbox((0,0),text,font=font)
  draw.text(((W-(bbox[2]-bbox[0]))/2,97+k*66),text,font=font,
            fill=(240,232,211,255))
 return cv2.cvtColor(np.asarray(Image.alpha_composite(canvas,layer).convert("RGB")),cv2.COLOR_RGB2BGR)

def original_music(total):
 # Fully generated ambient sine textures, no external samples.
 sr=32000
 t=np.arange(round(sr*total),dtype=np.float64)/sr
 music=np.zeros_like(t)
 for start,length,frequencies in [
  (0.,total*.48,[65.41,98.0,130.81]),
  (total*.29,total*.46,[73.42,110.0,146.83]),
  (total*.63,total*.4,[58.27,87.31,116.54])
 ]:
  dt=t-start
  a=np.clip(np.minimum(dt/3.5,(length-dt)/4),0,1)
  for j,f in enumerate(frequencies):
   music+=(0.03/(1+j*.65))*a*np.sin(2*np.pi*f*t+(.1+j*.07)*np.sin(.35*t))
 fade=np.clip(t/2,0,1)*np.clip((total-t)/3,0,1)
 pcm=np.int16(np.clip(music*fade,-.8,.8)*28000)
 p=OUT/"MUSIC_ORIGINAL_V330.wav"
 with wave.open(str(p),"wb") as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes(pcm.tobytes())
 return p

def render():
 q,script=load()
 artpath=art_check()
 chapters=q["chapters"]
 wav,voice_dur,ends,align=verified_voice(script,chapters)
 timed=json.loads((OUT/"VOICE_CACHE_V13.json").read_text(encoding="utf8"))["timed"]
 counts=[len(gemini_voice.sentences(x["text"])) for x in chapters]
 assert len(timed)==sum(counts) and counts[3]>=2
 chapter3_second_sentence_s=float(timed[sum(counts[:3])+1][1])
 assert (0 if 3==0 else ends[2])+.15 < chapter3_second_sentence_s < ends[3]-.15
 total_frames=round((DELAY+voice_dur+TAIL)*FPS)
 total=total_frames/FPS
 image=Image.open(artpath).convert("RGB")
 whole=full_plate(image)
 cover=title_card(image)
 artwork=cv2.imread(str(artpath),cv2.IMREAD_COLOR)
 assert artwork.shape[:2]==(2772,3840)
 music=original_music(total)
 shared=OUT/"BRUEGEL_REBEL_CRITICO_SHARED_AUDIO_V330.m4a"
 ms=round(DELAY*1000)
 run(["ffmpeg","-v","error","-y","-i",wav,"-i",music,
   "-filter_complex",f"[0:a]adelay={ms}|{ms},volume=1[v];[1:a]volume=.22[m];[v][m]amix=inputs=2:duration=longest:dropout_transition=0,alimiter=limit=.95[a]",
   "-map","[a]","-c:a","aac","-b:a","160k",shared])
 raw=OUT/"SILENT_TEMP_V330.mp4"
 target=OUT/"BRUEGEL_THE_FALL_OF_THE_REBEL_ANGELS_CRITICO_STANDARD_V330_REVIEW.mp4"
 cmd=["ffmpeg","-hide_banner","-loglevel","error","-y",
      "-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0","-an",
      "-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",str(raw)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 contact=[]
 camera_trace=[]
 from bisect import bisect_right
 try:
  for n in range(total_frames):
   sec=n/FPS
   if sec<DELAY:
    frame=opening_frame(artwork,sec)
   elif sec>=DELAY+voice_dur:
    frame=whole
   else:
    spoken=sec-DELAY
    ix=min(len(chapters)-1,bisect_right(ends,spoken))
    beg=0 if ix==0 else ends[ix-1]
    end=ends[ix]
    audit={}
    part=1 if ix==3 and spoken>=chapter3_second_sentence_s else 0
    part_start=chapter3_second_sentence_s if ix==3 and part else beg
    part_end=end if part or ix!=3 else chapter3_second_sentence_s
    u=max(0,min(1,(spoken-part_start)/max(.1,part_end-part_start)))
    if ix in (0,1,8):
     frame=whole
    else:
     frame=shot(artwork,chapters[ix],u,audit,chapter_index=ix,part=part)
    if n%10==0:
     camera_trace.append({"time_s":round(sec,4),"chapter_index":ix,
       "kind":"detail" if audit else "whole_plate",
       "director_reason":audit.get("director_reason","whole_painting_context"),
       "camera_crop_xyxy":audit.get("camera_crop_xyxy")})
   if n%160==0:contact.append((sec,cv2.resize(frame,(180,320))))
   proc.stdin.write(np.ascontiguousarray(frame).tobytes())
  proc.stdin.close()
  err=proc.stderr.read()
  if proc.wait():raise RuntimeError(err.decode("utf8","replace")[-1000:])
 except Exception:
  proc.kill()
  raise
 run(["ffmpeg","-v","error","-y","-i",raw,"-i",shared,"-map","0:v:0","-map","1:a:0",
      "-c:v","copy","-c:a","copy","-movflags","+faststart",target])
 run(["ffmpeg","-v","error","-xerror","-i",target,"-f","null","-"])
 cap=cv2.VideoCapture(str(target))
 assert cap.isOpened()
 readback={"frames":int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
           "fps":float(cap.get(cv2.CAP_PROP_FPS)),
           "width":int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
           "height":int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}
 cap.release()
 assert readback["frames"]==total_frames and readback["width"]==W and readback["height"]==H and abs(readback["fps"]-FPS)<.01
 raw.unlink()
 grid=np.full((4*340,4*194,3),19,dtype=np.uint8)
 for i,(sec,frame) in enumerate(contact[:16]):
  xx=i%4*194+7; yy=i//4*340+7
  grid[yy:yy+320,xx:xx+180]=frame
  cv2.putText(grid,f"{sec:.1f}s",(xx,yy+331),cv2.FONT_HERSHEY_SIMPLEX,.34,(230,230,230),1)
 cv2.imwrite(str(OUT/"CONTACT_SHEET_V330.jpg"),grid)
 Image.fromarray(cv2.cvtColor(cover,cv2.COLOR_BGR2RGB)).save(OUT/"COVER.jpg",quality=93)
 (OUT/"RIGHTS_AND_CREDITS.txt").write_text(
   "Pieter Bruegel the Elder, The Fall of the Rebel Angels, 1562. Royal Museums of Fine Arts of Belgium, accession 584, 117x162 cm oil on oak panel.\n"
   "Painting: independent faithful PD-Art scan, Wikimedia Commons: "+q["source_page"]+"\n"
   "SHA256 original painting: "+ART_SHA+"\n"
   "Voice: ONE natural Google Gacrux recording from owner-attested second Free/no-billing project; future Museum MUST reuse exactly this WAV. Original synthesised music, no recordings used.\n"
   "Museum variant blocked: Sailko photo retrieval HTTP429; frame not yet verified. No fake museum, no automatic Gold or publication. Territorial rights check pending.\n",
   encoding="utf8")
 (OUT/"SOCIAL_DRAFT_UNPUBLISHED.txt").write_text(
   "The Fall of the Rebel Angels · Pieter Bruegel the Elder, 1562.\n\n"
   "Angelic light crashes into an army of impossible hybrid creatures in this astonishing vision of chaos and order.\n\n"
   "Royal Museums of Fine Arts of Belgium, Brussels, collection 584. Artwork reproduction: Wikimedia Commons PD-Art. Original narration and soundtrack.\n"
   "DRAFT — NOT PUBLISHED.\n",encoding="utf8")
 qa={"work":q["public_title"],"artist":q["artist"],"year":1562,"accession":"584",
    "source_art_sha256":ART_SHA,"shared_voice_wav_sha256":sha(wav),"source_voice_aac_sha256":sha(shared),
    "asr_matched_fraction":align["matched_fraction"],"human_listening_review":"PENDING",
    "file":{"name":target.name,"bytes":target.stat().st_size,"sha256":sha(target),
      "duration_s":total,"frames":total_frames,"fps":FPS,"resolution":[W,H],"full_ffmpeg_decode":"PASS"},
    "variant":"critico_standard","museum_variant_rendered":False,"museum_approved":False,
    "Gold_V25":False,"social_published":False,"site_player_verified":False,"new_paid_video_calls":0}
 focus=capture_artvision_focus(
  video=target, wav=wav, voice_cache=OUT/"VOICE_CACHE_V13.json",
  output_dir=OUT/"FOCUS_REVIEW_V1", variant="critico_standard",
  voice_offset_s=DELAY, video_duration_s=total,
  camera_trace=camera_trace, expected_video_sha256=sha(target))
 qa["narrative_focus_review"]={
  "status":focus["status"],
  "report":"FOCUS_REVIEW_V1/ARTVISION_CRITICO_REAL_MP4_FOCUS_QA.json",
  "real_mp4_frames":focus["real_frames_extracted"],
  "semantic_review_pending":True, "Gold_V25":False}
 timeline=[{"artwork":"The Fall of the Rebel Angels",
     "start":0,"end":DELAY,"kind":"opening","framing":"archangel",
     "move":"slow_reveal","camera_reason":"visual_hook"}]
 for ix,chapter in enumerate(chapters):
  first=0 if ix==0 else ends[ix-1]
  timeline.append({"artwork":"The Fall of the Rebel Angels",
   "start":round(DELAY+first,3),"end":round(DELAY+ends[ix],3),
   "kind":"painting_detail","framing":("context" if ix in (0,1,8) else "subject_"+str(ix)),
   "move":("static" if ix in (0,1,8) else "slow_pan"),
   "spoken_anchor":chapter["text"][:100],
   "visual_anchor":("full_painting_context" if ix in (0,1,8) else
     {2:"archangel_Michael",3:"light_sky_and_falling_figures",
     4:"hybrid_creatures",5:"left_open_mouthed_creature",
     6:"butterfly_form",7:"light_and_shadow"}.get(ix,"artwork")),
   "camera_reason":"narrated_subject_follow"})
 timeline.append({"artwork":"The Fall of the Rebel Angels",
   "start":round(DELAY+voice_dur,3),"end":round(total,3),
   "kind":"end_artwork","framing":"full_painting","move":"static",
   "camera_reason":"closing_visual_hold"})
 direction_block,direction_warn,direction_facts=analyze_scenes(timeline,short=False)
 tail_warn,tail_facts=inspect_black_tail(target,total)
 qa["director_v330"]={
  "type":"NONDESTRUCTIVE_PRIVATE_CRITICO_STANDARD_REVISION",
  "narration_wav_preserved":True, "new_tts_calls":0,
  "previous_master_changed":False,
  "actual_camera_track_measurements":len(camera_trace),
  "chapter3_split_on_real_asr_sentence":round(chapter3_second_sentence_s,3),
  "timeline":timeline,
  "v326_blocking":direction_block,"v326_warnings":direction_warn,
  "v326_facts":direction_facts,
  "black_tail_warnings":tail_warn,"black_tail_facts":tail_facts,
  "artistic_review":"PENDING_NOT_CERTIFIED",
  "baseline_ab_result":"COMPARE_IN_WORKFLOW",
  "notes":"Meaning anchors are storyboard claims, not human verified art regions."}
 assert not direction_block
 report=OUT/"QA_V330.json"
 report.write_text(json.dumps(qa,indent=2,ensure_ascii=False)+"\n")
 package=OUT/"REBEL_ANGELS_CRITICO_STANDARD_V330_REVIEW_PACKAGE.zip"
 with zipfile.ZipFile(package,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=3) as z:
  for f in [target,OUT/"COVER.jpg",OUT/"CONTACT_SHEET_V330.jpg",report,
            OUT/"RIGHTS_AND_CREDITS.txt",OUT/"SOCIAL_DRAFT_UNPUBLISHED.txt",OUT/"COPIONE_ESATTO_V330.txt"]:
   z.write(f,arcname=f.name)
  for f in sorted((OUT/"FOCUS_REVIEW_V1").rglob("*")):
   if f.is_file():z.write(f,arcname=str(f.relative_to(OUT)))
 with zipfile.ZipFile(package) as z: assert z.testzip() is None
 print(json.dumps({"status":"ONE_REAL_CRITICO_REVIEW_MP4","mp4":qa["file"],"package":{"name":package.name,"bytes":package.stat().st_size,"sha256":sha(package),"crc":"PASS"},"voice_wav_sha256":sha(wav),"human_qa":"PENDING","museum_approved":False,"Gold_V25":False},indent=2))

def main():
 p=argparse.ArgumentParser(description="Reuse VERIFIED V144 Gacrux WAV only; no voice synthesis or paid calls")
 p.add_argument("--phase",choices=["render"],required=True)
 p.parse_args()
 OUT.mkdir(parents=True,exist_ok=True)
 render()
if __name__=="__main__":main()
