#!/usr/bin/env python3
"""V149 Rembrandt Night Watch official Rijksmuseum IIIF critic standard: genuine one-shot Gacrux, source locked.
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

OUT=Path("/tmp/nightwatch_critico_v149")
RECIPE=ROOT/"modules/artvision_critico/production_series/night_watch_v149.json"
ART_SHA="RUNTIME_VERIFIED_RIJKSMUSEUM_IIIF_PJEZO"
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
 assert q["work_id"]=="rembrandt_night_watch_1642_rijks_sk_c_5"
 assert q["public_title"]=="The Night Watch"
 assert q["accession"]=="SK-C-5" and q["variant"]=="critico_standard"
 assert len(q["chapters"])==9
 script="\n\n".join(c["text"] for c in q["chapters"])
 assert 180<=len(script.split())<=290
 return q,script

def art_check():
 q,_=load()
 original=OUT/"ORIGINAL_ARTWORK.jpg"
 meta=OUT/"OFFICIAL_IIIF_SOURCE_V149.json"
 assert original.is_file() and meta.is_file(), "Official Rijksmuseum IIIF pixels and manifest absent; no TTS"
 src=json.loads(meta.read_text(encoding="utf8"))
 assert src["iiif_id"]=="PJEZO" and src["museum_object_number"]=="SK-C-5"
 assert src["image_url"]=="https://iiif.micr.io/PJEZO/full/5200,/0/default.jpg"
 assert sha(original)==src["sha256"] and original.stat().st_size==src["bytes"],"Mismatched downloaded image hash"
 with Image.open(original) as im:
  assert im.format=="JPEG" and im.width==5200 and 3900<im.height<4600
  assert src["width"]==im.width and src["height"]==im.height
 return original

def voice():
 q,script=load()
 art_check()
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/"COPIONE_ESATTO_V149.txt").write_text(script,encoding="utf8")
 assert gemini_voice.MODEL=="gemini-3.8-flash-tts" and gemini_voice.VOICE=="Gacrux"
 if os.environ.get("ARTVISION_GEMINI_PROJECT_BILLING_TIER")!="Free" or not os.environ.get("GEMINI_API_KEY"):
  (OUT/"VOICE_RESULT_V149.json").write_text(json.dumps({"status":"BLOCKED_NO_FREE_ACCOUNT","new_tts_calls":0}))
  raise RuntimeError("Free second account gate absent: zero voice calls")
 try:
  # Small local Whisper avoids the older base model mismatches; no separate ASR API.
  os.environ["ARTVISION_ASR_MODEL"]="small"
  data,timed=gemini_voice.synthesize(script,OUT)
  wav=OUT/"VOCE.wav"
  duration=len(data)/24000
  align=json.loads((OUT/"ALLINEAMENTO_VOCE.json").read_text())
  if not (70<=duration<=180 and align.get("method")=="asr_with_interpolation" and (align.get("matched_fraction") or 0)>=.85):
   raise RuntimeError("Audio stored, but alignment rejected; DO NOT RE-CALL TTS")
  result={"status":"ONE_GENUINE_VOICE_WAV_READY","wav_sha256":sha(wav),"duration_seconds":duration,
    "ASR_match":align["matched_fraction"],"one_voice_for_future_museum":True,
    "authorised_account":"owner-attested Free/no billing second account","Gold_V25":False,
    "museum_approved":False,"published":False}
  (OUT/"VOICE_RESULT_V149.json").write_text(json.dumps(result,indent=2))
 except Exception as e:
  (OUT/"VOICE_RESULT_V149.json").write_text(json.dumps({
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
 lines=[("THE NIGHT WATCH",40)]
 for i,(s,size) in enumerate(lines):
  f=ImageFont.truetype(serif,size)
  bb=d.textbbox((0,0),s,font=f)
  d.text(((W-(bb[2]-bb[0]))//2,104+i*47),s,fill=(232,223,207),font=f)
 sub="REMBRANDT VAN RIJN   ·   1642"
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

def shot(paint,chapter,u):
 # Portrait camera uses source-pixel coordinates; hold 3D bodies intact.
 x,y,ch=chapter["cx"],chapter["cy"],chapter["crop_height_px"]
 ih,iw=paint.shape[:2]
 ch=int(ch*(1-.065*u))
 cropw=int(ch*W/H)
 cx=int(iw*(x+.008*(u-.5)))
 cy=int(ih*(y-.006*(u-.5)))
 x0=max(0,min(iw-cropw,cx-cropw//2))
 y0=max(0,min(ih-ch,cy-ch//2))
 region=paint[y0:y0+ch,x0:x0+cropw]
 if region.size==0:raise RuntimeError("Out-of-bounds crop")
 return cv2.resize(region,(W,H),interpolation=cv2.INTER_AREA)

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
 p=OUT/"MUSIC_ORIGINAL_V149.wav"
 with wave.open(str(p),"wb") as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes(pcm.tobytes())
 return p

def render():
 q,script=load()
 artpath=art_check()
 chapters=q["chapters"]
 wav,voice_dur,ends,align=verified_voice(script,chapters)
 total_frames=round((DELAY+voice_dur+TAIL)*FPS)
 total=total_frames/FPS
 image=Image.open(artpath).convert("RGB")
 whole=full_plate(image)
 cover=title_card(image)
 artwork=cv2.imread(str(artpath),cv2.IMREAD_COLOR)
 assert 3900<artwork.shape[0]<4600 and artwork.shape[1]==5200
 music=original_music(total)
 shared=OUT/"NIGHT_WATCH_CRITICO_SHARED_AUDIO_V149.m4a"
 ms=round(DELAY*1000)
 run(["ffmpeg","-v","error","-y","-i",wav,"-i",music,
   "-filter_complex",f"[0:a]adelay={ms}|{ms},volume=1[v];[1:a]volume=.22[m];[v][m]amix=inputs=2:duration=longest:dropout_transition=0,alimiter=limit=.95[a]",
   "-map","[a]","-c:a","aac","-b:a","160k",shared])
 raw=OUT/"SILENT_TEMP_V149.mp4"
 target=OUT/"REMBRANDT_THE_NIGHT_WATCH_CRITICO_STANDARD_V149_REVIEW.mp4"
 cmd=["ffmpeg","-hide_banner","-loglevel","error","-y",
      "-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0","-an",
      "-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",str(raw)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 contact=[]
 from bisect import bisect_right
 try:
  for n in range(total_frames):
   sec=n/FPS
   if sec<DELAY:
    frame=cover if sec<2 else whole
   elif sec>=DELAY+voice_dur:
    frame=whole if sec<DELAY+voice_dur+TAIL/2 else cover
   else:
    spoken=sec-DELAY
    ix=min(len(chapters)-1,bisect_right(ends,spoken))
    beg=0 if ix==0 else ends[ix-1]
    end=ends[ix]
    u=max(0,min(1,(spoken-beg)/max(.1,end-beg)))
    frame=whole if ix in (1,8) else shot(artwork,chapters[ix],u)
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
 cv2.imwrite(str(OUT/"CONTACT_SHEET_V149.jpg"),grid)
 Image.fromarray(cv2.cvtColor(cover,cv2.COLOR_BGR2RGB)).save(OUT/"COVER.jpg",quality=93)
 (OUT/"RIGHTS_AND_CREDITS.txt").write_text(
   "Rembrandt van Rijn, The Night Watch, 1642, Rijksmuseum accession SK-C-5.\n"
   "This is a resized image served by the OFFICIAL Rijksmuseum IIIF image identifier PJEZO; not the earlier exact Commons 14168x11528 source and not claimed to share that byte hash.\n"
   "Official Rijksmuseum image source: https://iiif.micr.io/PJEZO/full/5200,/0/default.jpg\n"
   "Official IIIF documentation confirms SK-C-5 maps to PJEZO: https://data.rijksmuseum.nl/tutorials/iiif/\n"
   "Official image source SHA256: "+sha(artpath)+"\n"
   "Visual confirmation of treatment of the historical canvas borders is pending; do not label digitally reconstructed edges authentic.\n"
   "Voice: one genuine Gacrux narration on owner's attested Free/no-billing second account, stored WAV for later permitted reuse; original synthesized music, no third-party recordings.\n"
   "This is Critico Standard review only, not a Museum room, frame or digital inpainting. Commercial territorial rights and artistic QA pending; NOT Gold and NOT published.\n",
   encoding="utf8")
 (OUT/"SOCIAL_DRAFT_UNPUBLISHED.txt").write_text(
   "The Night Watch · Rembrandt van Rijn, 1642.\n\n"
   "A captain's gesture and a burst of light transform a civic guard portrait into a scene alive with movement.\n\n"
   "Rijksmuseum SK-C-5. Official museum IIIF reproduction, original voice and soundtrack. Review copy only.\n"
   "DRAFT ONLY — NOT PUBLISHED.\n",encoding="utf8")
 qa={"work":q["public_title"],"artist":q["artist"],"year":1642,"accession":"SK-C-5",
    "source_art_sha256":sha(artpath),"shared_voice_wav_sha256":sha(wav),"source_voice_aac_sha256":sha(shared),
    "asr_matched_fraction":align["matched_fraction"],"human_listening_review":"PENDING",
    "file":{"name":target.name,"bytes":target.stat().st_size,"sha256":sha(target),
      "duration_s":total,"frames":total_frames,"fps":FPS,"resolution":[W,H],"full_ffmpeg_decode":"PASS"},
    "source_iiif_id":"PJEZO","variant":"critico_standard","museum_variant_rendered":False,"museum_approved":False,
    "Gold_V25":False,"social_published":False,"site_player_verified":False,"new_paid_video_calls":0}
 report=OUT/"QA_V149.json"
 report.write_text(json.dumps(qa,indent=2,ensure_ascii=False)+"\n")
 package=OUT/"NIGHT_WATCH_CRITICO_STANDARD_V149_REVIEW_PACKAGE.zip"
 with zipfile.ZipFile(package,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=3) as z:
  for f in [target,OUT/"COVER.jpg",OUT/"CONTACT_SHEET_V149.jpg",report,
            OUT/"RIGHTS_AND_CREDITS.txt",OUT/"SOCIAL_DRAFT_UNPUBLISHED.txt",OUT/"COPIONE_ESATTO_V149.txt"]:
   z.write(f,arcname=f.name)
 with zipfile.ZipFile(package) as z: assert z.testzip() is None
 print(json.dumps({"status":"ONE_REAL_CRITICO_REVIEW_MP4","mp4":qa["file"],"package":{"name":package.name,"bytes":package.stat().st_size,"sha256":sha(package),"crc":"PASS"},"voice_wav_sha256":sha(wav),"human_qa":"PENDING","museum_approved":False,"Gold_V25":False},indent=2))

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--phase",required=True,choices=["voice","render"])
 a=p.parse_args()
 OUT.mkdir(parents=True,exist_ok=True)
 if a.phase=="voice":voice()
 else:render()
if __name__=="__main__":main()
