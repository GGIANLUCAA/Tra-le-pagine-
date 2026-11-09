#!/usr/bin/env python3
"""Giuliano Terracotta V4: verified real-motion documentary + evidence-locked 62 photo beats.

No invented archaeology, no AI-generated ancient footage, no publish. Photographic edits
are transparent and creators/licences preserved in the deliverable ZIP.
"""
from __future__ import annotations
import io,json,math,os,shutil,subprocess,sys,time,zipfile,hashlib,urllib.parse,html,re
from pathlib import Path
import numpy as np
import requests
from PIL import Image,ImageOps,ImageDraw,ImageFont,ImageFilter,ImageEnhance

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"giuliano"/"terracotta_v3"))
import render_documentary_v3 as base
base.gemini_voice.STYLE=(
 "Voice over in Italian for an authoritative, fascinating premium historical "
 "television documentary, energetic but controlled and journalistically precise. "
 "Warm natural baritone male voice, articulate and confident, with authentic "
 "human phrasing and subtle emphasis on astonishing concrete facts. A conversational "
 "broadcast cadence, not poetry, not a theatrical art-criticism monologue. "
 "Short meaningful pauses between revelations, otherwise maintain momentum. "
 "Accurate Italian dates and Chinese name pronunciation, no synthetic overacting."
)
DIR=ROOT/"output"/"giuliano_terracotta_v4"
MEDIA=DIR/"media";CLIPS=DIR/"clips";FPS=24;W,H=1080,1920
PLAN_PATH=ROOT/"giuliano"/"terracotta_v4"/"REGIA_EVIDENZE.json"
SCRIPT_PATH=ROOT/"giuliano"/"terracotta_v4"/"SCENEGGIATURA_GIORNALISTICA_IT.txt"
PLAN=json.loads(PLAN_PATH.read_text(encoding="utf8"))
BEATS=PLAN["beats"]
BASE_FILM="Terracotta Army Pit 1 2014.webmhd.webm"
API="https://commons.wikimedia.org/w/api.php"
UA="GiulianoDocumentary-VerifiedMedia/4.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-)"
def run(a):base.shell(a)
def sha(p):return base.sha(p)
def fontsize(size,bold=False):
 return base.font(size,bold)
def srcreport(title):
 url="https://commons.wikimedia.org/wiki/"+urllib.parse.quote("File:"+title.replace(" ","_"))
 return url
def verify_film():
 """Download a genuine 2014 16-second video of Pit 1 (CC BY-SA 4.0), before TTS."""
 fn=MEDIA/"TERRACOTTA_REAL_MOTION_2014.webm"
 sess=requests.Session();sess.headers.update({"User-Agent":UA})
 q={"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata|size",
    "titles":"File:"+BASE_FILM}
 r=sess.get(API,params=q,timeout=50);r.raise_for_status()
 obj=r.json()["query"]["pages"]
 info=next(iter(obj.values()))["imageinfo"][0]
 l=base.strip_html(info.get("extmetadata",{}).get("LicenseShortName",{}).get("value",""))
 if "by-sa" not in l.lower() and "cc0" not in l.lower():raise RuntimeError("Video rights missing: "+l)
 link=info["url"]
 error=None
 for candidate in (link,
      "https://commons.wikimedia.org/wiki/Special:Redirect/file/"+urllib.parse.quote(BASE_FILM.replace(" ","_"))):
  try:
   rr=sess.get(candidate,timeout=120,stream=True);rr.raise_for_status()
   with open(fn,"wb") as out:
    for chunk in rr.iter_content(1024*256):
     if chunk:out.write(chunk)
   if fn.stat().st_size<500000:raise RuntimeError("Genuine film too small")
   prob=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries",
     "format=duration,size:stream=width,height,codec_name","-of","json",str(fn)],text=True))
   secs=float(prob["format"]["duration"])
   if not (10<=secs<=30):raise RuntimeError("Unexpected verified film length")
   print("VERIFIED_REAL_2014_MOVING_FILM",secs,l,fn.stat().st_size,flush=True)
   return fn,{"file":BASE_FILM,"source":srcreport(BASE_FILM),"license":l,
     "sha256":sha(fn),"duration":secs,"size":fn.stat().st_size}
  except Exception as ex:
   print("FILM_FETCH_FAIL",type(ex).__name__,str(ex)[:160],flush=True)
   error=ex
 raise RuntimeError("Authentic moving film unavailable, don't claim video-based V4") from error
def photo_sources():
 allnames=list(dict.fromkeys(n for b in BEATS for n in b["sources"]))
 infos=base.fetch_metadata(allnames)
 result={};fails=[]
 for n,info in zip(allnames,infos):
  if info is None:
   fails.append((n,"rights/metadata missing"));continue
  path=MEDIA/("source_"+str(len(result)).zfill(2)+".jpg")
  try:
   r=base.download_commons(info,path)
   with Image.open(path) as im:
    w,h=im.size
   if w<950 or h<850:raise RuntimeError(f"Low fidelity source {w}x{h}")
   result[n]={"metadata":r,"path":path,"w":w,"h":h}
   print("V4_PHOTO_OK",len(result),n,r["license"],w,h,flush=True)
   time.sleep(.12)
  except Exception as ex:
   fails.append((n,str(ex)[:140]))
 for n,msg in fails:print("V4_PHOTO_REJECTED",n,msg,flush=True)
 print("V4_VISUAL_BANK",len(result),"of",len(allnames),"verified real files",flush=True)
 if len(result)<38:
  raise RuntimeError(f"Only {len(result)} authentic photo sources: below 38 threshold")
 # Never switch a missing kneeling archer to a standing statue or a replica to a real original.
 resolved=[]
 for b in BEATS:
  local=[{"name":n,**result[n]} for n in b["sources"] if n in result]
  if not local:raise RuntimeError("Beat "+str(b["id"])+" has no actual evidence")
  resolved.append(local)
 return resolved,allnames,fails

def cinematic_canvas(item,beat,shot_idx,out):
 raw=ImageOps.exif_transpose(Image.open(item["path"])).convert("RGB")
 ratio=raw.width/raw.height
 role=beat["semantic"]
 # A wide archaeological panorama should remain understandable, NOT be cropped to a fake
 # random face: an editorial dual-panel displays the full scene and a separate authentic crop.
 if ratio>1.40 and role in ("formation","excavations","mystery","mausoleum","final"):
  full=ImageOps.contain(raw,(W,920),Image.Resampling.LANCZOS)
  bg=Image.new("RGB",(W,H),(7,12,18))
  x=(W-full.width)//2;bg.paste(full,(x,270+(800-full.height)//2))
  detail=ImageOps.fit(raw,(W,700),Image.Resampling.LANCZOS,
                 centering=(.36+(.07*(shot_idx%4)),.52))
  bg.paste(detail,(0,1120))
  d=ImageDraw.Draw(bg)
  d.rectangle((0,1102,W,1110),fill=(160,132,90))
 else:
  center=(.50,.50)
  if role=="portraits":center=(.50,.32)
  if role=="acrobat":center=(.50,.46)
  bg=ImageOps.fit(raw,(W,H),Image.Resampling.LANCZOS,centering=center)
  bg=ImageEnhance.Contrast(bg).enhance(1.035)
 # soft real-film photographic tone, not changing original object coloration
 ov=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(ov)
 for y in range(1460,H):
  alpha=int(168*((y-1460)/(H-1460))**1.6)
  d.line((0,y,W,y),fill=(4,8,13,alpha))
 caption=(beat.get("overlay") or "").strip()
 chapter={3:"01 · LA SCOPERTA",13:"02 · I COLORI",17:"03 · LE ARMI",
          22:"04 · L'IMPERATORE",27:"05 · IL MISTERO"}.get(beat["id"])
 if chapter:
  d.rectangle((0,0,W,145),fill=(7,11,16,170))
  d.text((70,55),chapter,font=fontsize(38,True),fill=(233,209,169,255))
 if caption:
  if role=="replica":caption="RICOSTRUZIONE MODERNA · NON ORIGINALE"
  fs=41 if len(caption)<30 else 34
  d.rounded_rectangle((58,1670,W-58,1800),radius=13,
    fill=(7,12,17,215),outline=(202,168,114,125),width=2)
  d.text((90,1710),caption,font=fontsize(fs,True),fill=(250,238,213,255))
 bg=Image.alpha_composite(bg.convert("RGBA"),ov).convert("RGB")
 bg.save(out,quality=94,subsampling=0)

def film_title_image(out):
 layer=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(layer)
 d.rectangle((0,0,W,210),fill=(6,10,15,145))
 d.text((62,75),"GIULIANO   ·   HISTORY DOCUMENTARY",font=fontsize(33,True),
      fill=(232,214,181,255))
 for y in range(1060,1920):
  alpha=int(215*(y-1060)/860)
  d.line((0,y,W,y),fill=(7,10,14,alpha))
 d.text((65,1340),"THE",font=fontsize(78,True),fill=(241,219,180,255))
 d.text((60,1440),"TERRACOTTA",font=fontsize(110,True),fill=(251,242,222,255))
 d.text((61,1560),"ARMY",font=fontsize(158,True),fill=(251,242,222,255))
 d.line((65,1752,W-60,1752),fill=(218,174,110,255),width=4)
 d.text((70,1782),"2,000 YEARS UNDERGROUND",font=fontsize(36,True),
        fill=(238,216,177,255))
 layer.save(out)
def cover_image(realportrait,out):
 raw=Image.open(realportrait).convert("RGB")
 bg=ImageOps.fit(raw,(W,H),Image.Resampling.LANCZOS,centering=(.52,.34))
 layer=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(layer)
 for y in range(850,H):
  d.line((0,y,W,y),fill=(5,8,13,int(230*(y-850)/(H-850))))
 d.text((65,1270),"THE",font=fontsize(82,True),fill="#ecd2a0")
 d.text((60,1375),"TERRACOTTA",font=fontsize(112,True),fill="#fcf1d7")
 d.text((65,1515),"ARMY",font=fontsize(168,True),fill="#fcf1d7")
 d.line((72,1735,1006,1735),fill="#e1b875",width=4)
 d.text((72,1780),"L'ESERCITO CHE IL TEMPO NASCOSE",font=fontsize(35,True),fill="#eddfc3")
 Image.alpha_composite(bg.convert("RGBA"),layer).convert("RGB").save(out,quality=95)

def render_photo(img,frames,index,out):
 # Not one identical Ken Burns animation everywhere: scene-specific anchored framing.
 amount=.00034 if index%4==0 else .00018 if index%4==1 else .00028
 driftx={0:"(iw-iw/zoom)*0.48",1:"(iw-iw/zoom)*0.25",
       2:"(iw-iw/zoom)*0.68",3:"(iw-iw/zoom)*0.48"}[index%4]
 drifty={0:"(ih-ih/zoom)*0.42",1:"(ih-ih/zoom)*0.56",
        2:"(ih-ih/zoom)*0.46",3:"(ih-ih/zoom)*0.60"}[index%4]
 vf=(f"zoompan=z='min(1.009+on*{amount:.6f},1.095)':"
     f"x='{driftx}':y='{drifty}':d={frames}:s={W}x{H}:fps={FPS},"
     "format=yuv420p")
 run(["ffmpeg","-hide_banner","-loglevel","error","-y","-loop","1",
      "-framerate",FPS,"-i",img,"-vf",vf,"-frames:v",frames,
      "-c:v","libx264","-pix_fmt","yuv420p","-preset","veryfast",
      "-crf","21","-r",FPS,"-an",out])
def render_real_film(src,frames,index,overlay,clip):
 # Genuine moving camera footage; darkened soft background and full original landscape
 # in front so the view of the hundreds of warriors is not lost in a vertical crop.
 offset=0.6 if index==0 else 6.8
 fg=f"scale={W}:-2"
 vf=(f"[0:v]split=2[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,"
      f"crop={W}:{H},boxblur=32:3,eq=brightness=-0.08[bg];"
      f"[b]{fg}[fg];[bg][fg]overlay=x=(W-w)/2:y=(H-h)/2,format=yuv420p[laid];"
      f"[laid][1:v]overlay=0:0:format=auto,format=yuv420p[v]")
 run(["ffmpeg","-hide_banner","-loglevel","error","-y",
      "-ss",str(offset),"-i",src,"-loop","1","-framerate",FPS,
      "-i",overlay,"-filter_complex",vf,"-map","[v]","-frames:v",frames,
      "-an","-c:v","libx264","-preset","veryfast","-crf","20",
      "-pix_fmt","yuv420p","-r",FPS,clip])
def music_original(total,cues,path):
 import soundfile as sf
 sr=24000;n=int((total+1)*sr)
 t=np.arange(n,dtype=np.float32)/sr
 rng=np.random.default_rng(1257)
 signal=np.zeros(n,np.float32)
 # Evolving cinematic atmosphere: layered low strings and airy high textures.
 for f,level in [(55,.025),(82.41,.020),(110,.008),(164.81,.009),(220,.006)]:
  vibr=np.sin(2*np.pi*.053*t+.4)
  signal+=level*np.sin(2*np.pi*f*t+.09*vibr) * (.72+.28*np.sin(2*np.pi*.023*t+1))
 noise=rng.normal(0,.0013,n).astype(np.float32)
 # Break the constant drone with quiet transient beats at documented revelations.
 for sec,weight in cues:
  lo=max(0,int(sec*sr));hi=min(n,lo+int(1.8*sr))
  z=np.arange(hi-lo,dtype=np.float32)/sr
  signal[lo:hi] += (.055*weight)*np.exp(-3.8*z)*np.sin(2*np.pi*(65-19*z)*z)
  signal[lo:hi] += (.006*weight)*np.exp(-14*z)*rng.normal(0,1,len(z)).astype(np.float32)
 signal+=noise
 fade=np.minimum(1,np.minimum(t/1.2,(total+.8-t)/1.8))
 signal*=np.clip(fade,0,1)
 signal=np.clip(signal,-.95,.95)
 sf.write(path,signal,sr)
def make_contact(items,path):
 cols=9;cellw=150;cellh=285
 sheet=Image.new("RGB",(cols*cellw,math.ceil(len(items)/cols)*cellh+8),(15,17,20))
 draw=ImageDraw.Draw(sheet)
 for i,p in enumerate(items):
  im=Image.open(p).convert("RGB")
  im.thumbnail((140,245))
  x=(i%cols)*cellw+5;y=(i//cols)*cellh+5
  sheet.paste(im,(x,y))
  draw.text((x,y+248),str(i+1),font=fontsize(17,True),fill=(232,207,168))
 sheet.save(path,quality=90)
def main():
 for d in (DIR,MEDIA,CLIPS):d.mkdir(parents=True,exist_ok=True)
 script=SCRIPT_PATH.read_text(encoding="utf8").strip()
 if script!="\n".join(b["narration"] for b in BEATS):
  raise RuntimeError("Voice script and evidence timeline disagree")
 if len(BEATS)<28:raise RuntimeError("V4 requires enough sourced documentary beats")
 film,filmmeta=verify_film()
 photo_bank,requested,fail=photo_sources()
 photos=[];credit={}
 for beat,assets in zip(BEATS,photo_bank):
  local=[]
  for j,asset in enumerate(assets):
   canvas=MEDIA/f"beat_{beat['id']:02d}_{j:02d}.jpg"
   cinematic_canvas(asset,beat,j,canvas)
   local.append({"kind":"photo","path":canvas,"original":asset["metadata"]["commons_page"],
     "source_name":asset["name"],"sha256":asset["metadata"]["image_sha256"]})
   credit[asset["name"]]=asset["metadata"]
  photos.append(local)
 hero=next((x["path"] for xs in photo_bank for x in xs if x["name"]=="2011 Qin Terracotta Warrior 01.jpg"),
           photo_bank[8][0]["path"])
 cover_image(hero,DIR/"COVER_V4.jpg")
 film_title_image(DIR/"TITLE_OVERLAY_V4.png")
 Image.new("RGBA",(W,H),(0,0,0,0)).save(DIR/"TRANSPARENT_V4.png")
 contact_imgs=[p["path"] for items in photos for p in items]
 make_contact(contact_imgs,DIR/"CONTACT_SHEET_V4.jpg")
 print("VISUAL_PREFLIGHT_COMPLETE",len(contact_imgs),
       "photo slots",len(credit),"distinct photo sources",flush=True)
 # Voice generated once only after verified rights + sources + actual moving film.
 waveform,aligned=base.synthesize(script,DIR/"audio")
 length=len(waveform)/24000
 aligninfo=json.loads((DIR/"audio"/"ALLINEAMENTO_VOCE.json").read_text())
 fraction=float(aligninfo.get("matched_fraction") or 0)
 print("GOOGLE_GACRUX_DOCUMENTARY",length,fraction,len(aligned),flush=True)
 if not (108<=length<=175) or len(aligned)!=len(BEATS) or fraction<.78:
  raise RuntimeError("Voice timing confidence not sufficient for documentary")
 for i,(line,a,b) in enumerate(aligned):
  if line!=BEATS[i]["narration"]:raise RuntimeError("Unmatched spoken sentence "+str(i+1))
 ready=[];edl=[];global_i=0
 for i,(beat,timed,stills) in enumerate(zip(BEATS,aligned,photos)):
  spoken,a,b=timed
  left=0 if i==0 else (aligned[i-1][2]+a)/2
  right=length if i==len(BEATS)-1 else (b+aligned[i+1][1])/2
  scenes=([{"kind":"real_footage","path":film,"original":filmmeta["source"],
             "source_name":BASE_FILM,"sha256":filmmeta["sha256"]}]
          if beat["id"] in (1,5) else [])+stills
  total=max(len(scenes),round(max(.2,right-left)*FPS))
  base_frames=total//len(scenes)
  slices=[base_frames]*len(scenes)
  for k in range(total-sum(slices)):slices[k%len(slices)]+=1
  offset=0
  for j,(shot,frames) in enumerate(zip(scenes,slices)):
   clip=CLIPS/f"shot_{global_i:03d}.mp4"
   if shot["kind"]=="real_footage":
    render_real_film(shot["path"],frames,0 if beat["id"]==1 else 1,
                     DIR/"TITLE_OVERLAY_V4.png" if beat["id"]==1
                     else DIR/"TRANSPARENT_V4.png",clip)
   else:
    render_photo(shot["path"],frames,global_i,clip)
   ready.append(clip)
   edl.append({"shot":global_i+1,"beat":beat["id"],"type":shot["kind"],
     "narration":spoken,"role":beat["semantic"],"source":shot["original"],
     "source_name":shot["source_name"],"source_sha256":shot["sha256"],
     "time_in":round(left+offset/FPS,3),"time_out":round(left+(offset+frames)/FPS,3),
     "overlay":beat.get("overlay",""),"license_checked":True})
   offset+=frames;global_i+=1
 # Independent playable full film from authenticated stills and actual filmed movement.
 concat=DIR/"concat.txt"
 concat.write_text("".join("file '"+str(x.resolve())+"'\n" for x in ready))
 silent=DIR/"picture_lock.mp4"
 run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0",
      "-i",concat,"-c","copy",silent])
 cues=[(0,1.0)]+[(aligned[i-1][1],1.0) for i in (3,13,17,22,27)]
 music_original(length,cues,DIR/"ORIGINAL_SCORE_V4.wav")
 filmout=DIR/"THE_TERRACOTTA_ARMY_V4_WOW_DOCUMENTARY.mp4"
 run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",silent,
      "-i",DIR/"audio"/"VOCE.wav","-i",DIR/"ORIGINAL_SCORE_V4.wav",
      "-filter_complex",
      "[1:a]highpass=f=75,volume=1.05[v];"
      "[2:a]volume=0.49[m];[m][v]sidechaincompress=threshold=0.015:ratio=9:attack=15:release=240[du];"
      "[v][du]amix=inputs=2:duration=first:normalize=0,"
      "loudnorm=I=-16:TP=-1.5:LRA=10[a]",
      "-map","0:v:0","-map","[a]","-c:v","copy","-c:a","aac",
      "-b:a","192k","-ar","48000","-shortest","-movflags","+faststart",filmout])
 run(["ffmpeg","-hide_banner","-loglevel","error","-xerror","-i",filmout,"-f","null","-"])
 probe=json.loads(subprocess.check_output(["ffprobe","-v","error",
   "-show_entries","format=duration,size:stream=codec_name,width,height,avg_frame_rate",
   "-of","json",str(filmout)],text=True))
 seconds=float(probe["format"]["duration"])
 if abs(seconds-length)>1:raise RuntimeError("Decoded film duration differs from actual Google narration")
 if len(edl)<55 or len(credit)<38 or not any(s["type"]=="real_footage" for s in edl):
  raise RuntimeError("WOW technical thresholds not satisfied")
 qa={"status":"TECHNICAL_MASTER_PASS_HUMAN_ARTISTIC_APPROVAL_PENDING",
   "video_path":str(filmout),"video_sha256":sha(filmout),"probe":probe,
   "voice":"Google Gemini Gacrux, new journalist-documentary take",
   "voice_alignment_method":aligninfo.get("method"),"asr_match_fraction":fraction,
   "beating_photographs":len(contact_imgs),"unique_real_photographs":len(credit),
   "genuine_video_shots":sum(s["type"]=="real_footage" for s in edl),
   "genuine_film_source":filmmeta,"cuts":len(edl),
   "no_ai_historical_footage":True,"modern_replica_explicitly_labeled":True,
   "no_publication":True,"artistic_review_still_needed":True,
   "edit_decision_list":edl}
 (DIR/"QA_V4.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 (DIR/"PHOTO_AND_VIDEO_CREDITS_V4.json").write_text(json.dumps(
     {"photos":list(credit.values()),"film":filmmeta,"adaptation_note":
      "Crops, editorial typography and camera motion. Photo/video licences remain governed by linked source pages."},
      ensure_ascii=False,indent=2)+"\n")
 (DIR/"PHOTO_AND_VIDEO_CREDITS_V4.txt").write_text(
  "REAL FILM: "+BASE_FILM+" | "+filmmeta["license"]+" | "+filmmeta["source"]+"\n"+
  "\n".join(f"{n} | {v['photographer']} | {v['license']} | {v['commons_page']} | {v['license_url']}"
    for n,v in credit.items())+"\n",encoding="utf8")
 (DIR/"SOCIAL_TEXT_V4.txt").write_text(
  "THE TERRACOTTA ARMY | Nel 1974, vicino a Xi'an, un pozzo rivelò un esercito di "
  "migliaia di guerrieri. Un tempo erano colorati, accanto a loro c'erano vere armi "
  "di bronzo e il mausoleo dell'imperatore custodisce ancora segreti non scavati. "
  "Documentario con fotografie autentiche e riprese reali del 2014. "
  "Fonti UNESCO e UCL; attribuzioni e licenze incluse. "
  "#TerracottaArmy #Archeologia #Documentario #Storia\n")
 (DIR/"README_V4.txt").write_text(
  "GIULIANO · THE TERRACOTTA ARMY · DOCUMENTARY V4\n"
  f"Actual MP4: {seconds:.2f} sec / {W}x{H} / H.264 / AAC.\n"
  f"{len(edl)} authentic visual shots, {len(credit)} different original photos, "
  f"{qa['genuine_video_shots']} real video shots from licensed 2014 archival footage.\n"
  "Voice: Google Gemini Gacrux NEW documentary interpretation.\n"
  "No synthetic historical scene; modern color replicas explicitly labeled.\n"
  "Real video is on Wikimedia Commons; credits attached.\n"
  "Technical: full FFmpeg decode PASS. Artistic approval: pending. No social/site publication.\n",
  encoding="utf8")
 pack=DIR/"TERRACOTTA_V4_VIDEO_COVER_FONTI.zip"
 with zipfile.ZipFile(pack,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
  for p in [filmout,DIR/"COVER_V4.jpg",DIR/"CONTACT_SHEET_V4.jpg",
    DIR/"QA_V4.json",DIR/"SOCIAL_TEXT_V4.txt",DIR/"PHOTO_AND_VIDEO_CREDITS_V4.json",
    DIR/"PHOTO_AND_VIDEO_CREDITS_V4.txt",DIR/"README_V4.txt",PLAN_PATH,SCRIPT_PATH]:
   z.write(p,p.name)
 with zipfile.ZipFile(pack) as z:
  if z.testzip():raise RuntimeError("ZIP CRC failed")
 print(json.dumps({"status":"V4_COMPLETE_PROOF_CHECKED",
   "movie":str(filmout),"zip":str(pack),"duration":seconds,
   "total_visual_shots":len(edl),"distinct_authentic_photos":len(credit),
   "real_video_shots":qa["genuine_video_shots"],"asr_fraction":fraction,
   "mp4_sha256":sha(filmout),"zip_sha256":sha(pack)}),flush=True)
if __name__=="__main__":
 main()
