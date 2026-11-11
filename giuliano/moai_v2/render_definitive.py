#!/usr/bin/env python3
"""GIULIANO EP02 definitive recut: genuine photo sources + annotated scientific mesh motion.
The original verified Google narration and music are remuxed, NEVER synthesized.
No archival/experiment footage is fabricated or copied from proprietary news footage.
"""
import os,sys,json,hashlib,subprocess,time,math,html,re,zipfile,urllib.parse,shutil
from pathlib import Path
import numpy as np, cv2, requests, trimesh
from PIL import Image,ImageOps,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"output"/"giuliano_moai_v2"/"base"
OUT=ROOT/"output"/"giuliano_moai_v2"/"final"
ASSETS=ROOT/"giuliano"/"moai_v2"/"assets"
FPS=24;W=1080;H=1920
OUT.mkdir(parents=True,exist_ok=True)
def run(*args):
 print("RUN",*map(str,args),flush=True)
 subprocess.run(list(map(str,args)),check=True)
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for c in iter(lambda:f.read(1024*1024),b""):h.update(c)
 return h.hexdigest()
def font(n=28,bold=False):
 p="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
 return ImageFont.truetype(p,n)
def audiohash(p):
 pr=subprocess.Popen(["ffmpeg","-nostdin","-v","error","-i",str(p),"-map","0:a:0","-ac","1","-ar","24000","-f","s16le","-"],stdout=subprocess.PIPE)
 h=hashlib.sha256()
 while True:
  b=pr.stdout.read(262144)
  if not b:break
  h.update(b)
 if pr.wait():raise RuntimeError("Audio PCM decoding failed "+str(p))
 return h.hexdigest()
def load_base():
 old=BASE/"GIULIANO_MOAI_V1_CINEMATIC.mp4"; q=BASE/"QA_MOAI.json"
 if not old.is_file() or not q.is_file():raise RuntimeError("Missing verified V1.1 film; no paid re-synthesis allowed")
 qa=json.loads(q.read_text(encoding="utf8"))
 if qa["sha256"]!=sha(old):raise RuntimeError("Wrong original master")
 if qa["narrative_beats"]!=34 or qa["camera_shots"]<55:raise RuntimeError("Base chronology differs")
 print("ORIGINAL_FILM_QA",qa["duration_seconds"],qa["camera_shots"],qa["unique_actual_photo_count"],flush=True)
 return old,qa
FILES=[
 {"beat":4,"file":"Ahu Akivi Easter Island.jpg","kind":"platform"},
 {"beat":23,"file":"Ahu Akivi, Easter Island (16491363758).jpg","kind":"platform"},
 {"beat":24,"file":"Ahu Akiwi.JPG","kind":"platform"},
 {"beat":25,"file":"Rapa Nui Moai (Easter Island).jpg","kind":"pukao"},
 {"beat":26,"file":"Ahu Akivi, Easter Island (2052720494).jpg","kind":"platform"},
 {"beat":27,"file":"ANAKENA - EASTER ISLAND.jpg","kind":"platform"},
 {"beat":28,"file":"Rapa Nui Moai (Easter Island).jpg","kind":"pukao"},
 {"beat":33,"file":"Tapati Festival (16686175785).jpg","kind":"culture"},
 {"beat":33,"file":"Tapati Festival (16660237656).jpg","kind":"culture"},
]
# Do not use Ahu Akivi for 1974 discovery; beat 4's chronology must show quarry instead.
FILES[0]={"beat":30,"file":"Moai Rapa Nui.jpg","kind":"quarry"}
def metadata_and_download():
 session=requests.Session()
 session.headers.update({"User-Agent":"GiulianoMoaiEpisode2Director/2.0 (museum photograph metadata licensing)","Accept":"application/json"})
 names=list(dict.fromkeys(x["file"] for x in FILES))
 resp=session.get("https://commons.wikimedia.org/w/api.php",
 params={"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata|size","iiurlwidth":"1750","redirects":1,"titles":"|".join("File:"+n for n in names)},timeout=65)
 resp.raise_for_status()
 candidates={}
 for page in resp.json()["query"]["pages"].values():
  if not page.get("imageinfo"):continue
  inf=page["imageinfo"][0];ext=inf.get("extmetadata",{})
  lic=re.sub("<[^>]*>","",html.unescape(ext.get("LicenseShortName",{}).get("value","")))
  terms=re.sub("<[^>]*>","",html.unescape(ext.get("UsageTerms",{}).get("value","")))
  all_l=(lic+" "+terms).lower()
  if not any(t in all_l for t in ["cc by","cc-by","cc0","public domain","pd-"]):continue
  if any(t in all_l for t in ["noncommercial","-nc","no derivatives","-nd"]):continue
  key=page["title"][5:].replace("_"," ").casefold()
  candidates[key]=(inf,lic,page["title"][5:],ext)
 print("EXTRA_PHOTOS_LICENSED",len(candidates),"/",len(names),flush=True)
 results={}
 for n in names:
  m=candidates.get(n.replace("_"," ").casefold())
  if not m:
   print("PHOTO_SKIPPED_NO_OPEN_LICENSE",n,flush=True);continue
  info,lic,fullname,ext=m
  p=OUT/("extra_%02d.jpg"%names.index(n))
  origin=info.get("thumburl") or info.get("url")
  proxies=[
    "https://images.weserv.nl/?"+urllib.parse.urlencode({"url":origin,"w":"1750","output":"jpg","q":"91"}),
    origin
  ]
  for link in proxies:
   try:
    res=session.get(link,timeout=75)
    res.raise_for_status()
    p.write_bytes(res.content)
    with Image.open(p) as im:im.verify()
    if p.stat().st_size<18000:raise RuntimeError("Very small image")
    results[n]={"path":str(p),"file":fullname,"sha":sha(p),"license":lic,
       "author":re.sub("<[^>]*>","",html.unescape(ext.get("Artist",{}).get("value","Unspecified"))),
       "url":"https://commons.wikimedia.org/wiki/"+urllib.parse.quote("File:"+fullname.replace(" ","_"))}
    break
   except Exception as e:
    print("SOURCE_RETRY",n,str(e)[:90],flush=True)
  time.sleep(.10)
 (OUT/"EXTRA_IMAGE_CREDITS.json").write_text(json.dumps(list(results.values()),ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 if len(results)<5:raise RuntimeError("Additional visual material insufficient: "+str(len(results)))
 return results
def canvas_extra(src,out,what):
 im=ImageOps.exif_transpose(Image.open(src)).convert("RGB")
 bg=ImageOps.fit(im,(W,H),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(38))
 bg=Image.blend(bg,Image.new("RGB",(W,H),(8,12,19)),.68)
 main=ImageOps.contain(im,(W-45,1220),Image.Resampling.LANCZOS)
 x=(W-main.width)//2;y=330+(1220-main.height)//2
 bg.paste(main,(x,y))
 d=ImageDraw.Draw(bg)
 d.line((x,y+main.height+18,x+main.width,y+main.height+18),fill=(209,164,95),width=3)
 d.text((70,90),"RAPA NUI  /  DOCUMENTAZIONE REALE",font=font(28,True),fill=(240,218,173))
 label={"platform":"PIATTAFORME CERIMONIALI","pukao":"AHU NAU NAU  /  PUKAO","culture":"RAPA NUI  /  CULTURA VIVA","quarry":"RANO RARAKU  /  LA CAVA"}[what]
 d.text((75,1740),label,font=font(32,True),fill=(251,231,188))
 bg.save(out,quality=92)
def beat_spans(qa,beat):
 rows=[x for x in qa["scene_timeline"] if x["beat"]==beat]
 if not rows:raise RuntimeError("Beat missing "+str(beat))
 return sorted(rows,key=lambda x:x["visual_start"])
def add_new_photos(qa,photos):
 scenes=[]
 occurrence={}
 for info in FILES:
  p=photos.get(info["file"])
  if not p:continue
  beat=info["beat"]
  slices=beat_spans(qa,beat)
  count=occurrence.get(beat,0)
  if count>=len(slices):continue
  occurrence[beat]=count+1
  shot=slices[-(count+1)]
  # Replace the complete shot: leaving 0.08s edges made visible photo flashes.
  t0=float(shot["visual_start"])
  t1=float(shot["visual_end"])
  if t1-t0<2.25:continue
  canvas=OUT/(f"extra_canvas_{beat:02d}_{count}.jpg")
  canvas_extra(p["path"],canvas,info["kind"])
  clip=OUT/(f"extra_insert_{beat:02d}_{count}.mp4")
  seconds=t1-t0
  run("ffmpeg","-nostdin","-hide_banner","-v","error","-y",
      "-loop","1","-framerate",FPS,"-i",canvas,"-t",f"{seconds:.4f}",
      "-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",
      "-r",FPS,"-an",clip)
  scenes.append({"type":"photo","begin":round(t0,4),"end":round(t1,4),"clip":clip,
   "beat":beat,"source":p["url"],"license":p["license"],"photo_sha":p["sha"]})
 return scenes
def shaded_3d_frame(mesh, faces, normals, sec, nsecs, variation=0):
 w,h=720,1280
 yy=np.arange(h,dtype=np.float32)[:,None];xx=np.arange(w,dtype=np.float32)[None,:]
 grad=yy/h
 img=np.zeros((h,w,3),dtype=np.uint8)
 # BGR cinematic dark blue with amber horizon gradient.
 img[:,:,0]=np.clip(23+14*grad+5*(xx/w),0,255)
 img[:,:,1]=np.clip(24+17*grad,0,255)
 img[:,:,2]=np.clip(24+27*grad,0,255)
 cv2.rectangle(img,(0,1020),(w,h),(29,35,44),-1)
 for a in range(30,720,90):
  cv2.line(img,(a,1020),(a-90,h),(54,60,66),1,cv2.LINE_AA)
 for y in (1020,1090,1180):
  cv2.line(img,(0,y),(w,y),(59,65,70),1,cv2.LINE_AA)
 t=sec/nsecs
 # The sway is a deliberately idealized explanatory model, not the field trial.
 theta=np.sin(sec*2*math.pi*.55+variation*.40)*math.radians(7.0)
 yaw=.40+variation*.28
 s=np.sin(theta);c=np.cos(theta)
 cy=np.cos(yaw);sy=np.sin(yaw)
 V=mesh.copy()
 X=V[:,0]*cy+V[:,2]*sy
 Z=-V[:,0]*sy+V[:,2]*cy
 Y=V[:,1]
 # rotate in projected world around base, rise slightly on each rocking cycle
 xx0=X*c-Y*s
 yy0=X*s+Y*c + abs(s)*.045
 proj_x=360+(xx0-(t-.5)*.25)*690+Z*90
 proj_y=1005-yy0*620+Z*55
 pix=np.column_stack((proj_x,proj_y)).astype(np.float32)
 depth=Z
 order=np.argsort(depth[faces].mean(axis=1))
 L=np.array([-.35,.45,.82]);L/=np.linalg.norm(L)
 # Underpaint the complete projected sculpture to eliminate isolated background pinholes.
 cv2.fillConvexPoly(img,cv2.convexHull(pix.astype(np.int32)),(160,171,191),lineType=cv2.LINE_AA)
 # Keep the original research mesh intact; use restrained natural sandstone tones.
 for idx in order:
  f=faces[idx]
  pts=pix[f]
  if np.any(~np.isfinite(pts)):continue
  normal=normals[idx]
  brightness=.52+max(0,float(normal@L))*.31
  base=(min(226,int(108+112*brightness)),
        min(231,int(111+118*brightness)),
        min(238,int(123+121*brightness)))
  cv2.fillConvexPoly(img,pts.astype(np.int32),base,lineType=cv2.LINE_AA)
 # Controlling ropes illustrated, not a photographed experiment.
 attach_y=int(1005-.83*620)
 attach_x=int(360-(t-.5)*.25*690)
 left=(50,620+int(10*math.sin(sec*2.7)))
 right=(665,620-int(10*math.sin(sec*2.7)))
 active=sec*1.1%2<1
 cv2.line(img,(attach_x-25,attach_y),left,(87,163,232) if active else (56,96,139),4,cv2.LINE_AA)
 cv2.line(img,(attach_x+25,attach_y),right,(87,163,232) if not active else (56,96,139),4,cv2.LINE_AA)
 # Abstract force vectors - original instructional diagram, not fake excavator imagery.
 cv2.arrowedLine(img,(120,875),(230,875),(120,190,245),6,cv2.LINE_AA,tipLength=.18)
 cv2.arrowedLine(img,(600,875),(490,875),(120,190,245),6,cv2.LINE_AA,tipLength=.18)
 # Typographic art direction.
 layer=Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
 d=ImageDraw.Draw(layer)
 d.rectangle((0,0,w,126),fill=(9,16,25))
 d.text((28,31),"COME 'CAMMINA' UN MOAI",font=font(29,True),fill=(251,226,178))
 d.text((28,78),"SIMULAZIONE 3D  ·  NON RIPRESA DEL TEST",font=font(18,True),fill=(211,200,181))
 d.text((34,1070),"TRAZIONE ALTERNATA DELLE CORDE",font=font(21,True),fill=(240,220,191))
 if variation==2:
  d.text((34,1120),"4,35 t    |    18 persone",font=font(25,True),fill=(251,236,207))
  d.text((34,1164),"100 m  /  40 min   ·   Test 2025",font=font(20),fill=(223,209,188))
 else:
  d.text((34,1122),"Oscillazione laterale + avanzamento",font=font(20),fill=(225,215,197))
 d.text((26,1236),"Modello 3D: Lipo & Hunt  ·  MIT  |  Ipotesi di trasporto",font=font(14),fill=(193,182,159))
 return cv2.cvtColor(np.array(layer),cv2.COLOR_RGB2BGR)
def scientific_animation(qa):
 mesh=trimesh.load(ASSETS/"SimplifiedMoai.obj",force="mesh",process=False)
 raw=np.asarray(mesh.vertices,dtype=np.float32)
 scale=float(raw[:,1].max()-raw[:,1].min())
 if not 0.5<scale<2.5 or len(raw)<4000:raise RuntimeError("Unexpected source mesh geometry")
 raw[:,0]=(raw[:,0]-(raw[:,0].min()+raw[:,0].max())/2)/scale
 raw[:,1]=(raw[:,1]-raw[:,1].min())/scale
 raw[:,2]=(raw[:,2]-(raw[:,2].min()+raw[:,2].max())/2)/scale
 original_faces=np.asarray(mesh.faces,dtype=np.int32)
 # Render all mesh faces: sub-sampling made artificial black gaps in the CGI moai.
 faces=original_faces
 tri=raw[faces]
 nn=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
 nn/=np.maximum(1e-6,np.linalg.norm(nn,axis=1))[:,None]
 places=[(13,0),(15,1)]
 edits=[]
 for beat,variation in places:
  slices=beat_spans(qa,beat)
  begin=min(float(x["visual_start"]) for x in slices)+.04
  end=max(float(x["visual_end"]) for x in slices)-.04
  dur=end-begin
  out=OUT/(f"SCIENTIFIC_WALKING_{beat:02d}.mp4")
  frames=round(dur*FPS)
  cmd=["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
      "-f","rawvideo","-pixel_format","bgr24","-video_size","720x1280",
      "-framerate",str(FPS),"-i","-",
      "-vf","scale=1080:1920:flags=lanczos",
      "-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p","-an",str(out)]
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
  for i in range(frames):
   frame=shaded_3d_frame(raw,faces,nn,i/FPS,dur,variation)
   proc.stdin.write(frame.tobytes())
  proc.stdin.close()
  if proc.wait()!=0:raise RuntimeError("3D scientific motion render failed")
  edits.append({"type":"original_3d_explainer","beat":beat,"begin":round(begin,4),
     "end":round(end,4),"clip":out,"source":"https://github.com/clipo/moai_walking",
     "credit":"Carl Lipo & Terry Hunt, MIT license","label":"SIMULAZIONE 3D, NON RIPRESA DEL TEST"})
  print("SCIENCE_MOVING_VIDEO",beat,frames,round(dur,2),out.stat().st_size,flush=True)
 return edits
def genuine_field_experiment(qa):
  """Insert actual field-test footage; no AI reenactment or unlicensed substitute.
  Binghamton's official article embeds this recording. EurekAlert's same
  research media ID 1095278 lists reuse restrictions: 'Credit Carl Lipo'.
  """
  source="https://www.youtube.com/watch?v=z6wvgrMn8Ow"
  raw=OUT/"ORIGINAL_LIPO_TEST.mp4"
  local=os.environ.get("MOAI_AUTHENTIC_TEST_FILE","").strip()
  if local and Path(local).is_file():
    shutil.copyfile(local,raw)
  else:
    run(sys.executable,"-m","yt_dlp","--no-playlist","--no-progress",
        "--merge-output-format","mp4",
        "-f","bv*[height<=720]+ba/b[height<=720]/best",
        "-o",str(raw),source)
  if not raw.exists() or raw.stat().st_size<250000:
    raise RuntimeError("Genuine experiment footage could not be acquired: no fake recreation")
  probe=json.loads(subprocess.check_output([
    "ffprobe","-v","error","-show_entries",
    "format=duration:stream=width,height,codec_type","-of","json",str(raw)],text=True))
  if float(probe.get("format",{}).get("duration",0))<12:
    raise RuntimeError("Real experiment recording is shorter than the intended sequence")
  spans=beat_spans(qa,18)+beat_spans(qa,19)+beat_spans(qa,20)
  start=min(float(x["visual_start"]) for x in spans)
  finish=max(float(x["visual_end"]) for x in spans)
  duration=finish-start
  out=OUT/"VERO_TEST_LIPO_CON_CREDITI.mp4"
  # Fit the entire horizontal frame to avoid cropping either rope team.
  filt=("[0:v]split=2[a][b];"
        "[a]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,boxblur=28:3[bg];"
        "[b]scale=1080:1920:force_original_aspect_ratio=decrease[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2,"
        "drawbox=x=0:y=0:w=iw:h=142:color=black@0.8:t=fill,"
        "drawtext=text='FILMATO REALE DEL TEST':fontcolor=white:"
        "fontsize=37:x=(w-text_w)/2:y=22,"
        "drawtext=text='Riprese e credito: Carl Lipo':fontcolor=white:"
        "fontsize=29:x=(w-text_w)/2:y=79,format=yuv420p[v]")
  run("ffmpeg","-nostdin","-v","error","-y","-i",raw,
      "-filter_complex",filt,"-map","[v]","-t",f"{duration:.4f}",
      "-an","-r",FPS,"-c:v","libx264","-preset","veryfast",
      "-crf","21","-pix_fmt","yuv420p",out)
  run("ffmpeg","-nostdin","-v","error","-xerror","-i",out,"-f","null","-")
  return {"type":"authentic_2025_field_trial",
          "begin":round(start,4),"end":round(finish,4),
          "clip":out,"beat":18,
          "source":source,"credit":"Carl Lipo, Binghamton University",
          "permission_record":"https://www.eurekalert.org/multimedia/1095278",
          "source_sha256":sha(raw)}

def compose(base,qa,edits):
 edits=sorted(edits,key=lambda x:x["begin"])
 prev=0
 for e in edits:
  if e["begin"]<prev-.05:raise RuntimeError("Overlapping visual insert "+repr(e))
  prev=e["end"]
 cmd=["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y","-i",str(base)]
 for e in edits:cmd.extend(["-i",str(e["clip"])])
 chain=["[0:v]format=yuv420p[v0]"]
 for i,e in enumerate(edits,1):
  chain.append(f"[{i}:v]setpts=PTS-STARTPTS+{e['begin']:.4f}/TB[cut{i}]")
  chain.append(f"[v{i-1}][cut{i}]overlay=x=0:y=0:enable='between(t,{e['begin']:.4f},{e['end']:.4f})':eof_action=pass:shortest=0:format=auto[v{i}]")
 final=OUT/"THE_WALKING_GIANTS_GIULIANO_DEFINITIVO_HD.mp4"
 cmd+=["-filter_complex",";".join(chain),"-map",f"[v{len(edits)}]","-map","0:a:0",
       "-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",
       "-c:a","copy","-r",FPS,"-movflags","+faststart",str(final)]
 print("FINAL_MONTAGE_EDIT_COUNT",len(edits),flush=True)
 run(*cmd)
 run("ffmpeg","-nostdin","-v","error","-xerror","-i",final,"-f","null","-")
 if audiohash(base)!=audiohash(final):raise RuntimeError("Voice + soundtrack integrity not preserved")
 mobile=OUT/"THE_WALKING_GIANTS_GIULIANO_ANDROID.mp4"
 run("ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y","-i",final,
    "-vf","scale=720:1280:flags=lanczos","-c:v","libx264","-preset","veryfast",
    "-crf","29","-c:a","aac","-b:a","112k","-movflags","+faststart",mobile)
 run("ffmpeg","-nostdin","-v","error","-xerror","-i",mobile,"-f","null","-")
 return final,mobile
def main():
 base,qa=load_base()
 verified=metadata_and_download()
 photos=add_new_photos(qa,verified)
 science=scientific_animation(qa)
 # Exclude photographic photos that overlap the animated scientific explanation.
 scenes=photos+science
 movie,mobile=compose(base,qa,scenes)
 cover=BASE/"COVER_MOAI.jpg"
 shutil.copyfile(cover,OUT/"COVER_DEFINITIVA.jpg")
 contact=Image.new("RGB",(1400,630),(8,13,20));d=ImageDraw.Draw(contact)
 for i,x in enumerate(photos[:7]):
  rec=next((x2 for x2 in FILES if x2["beat"]==x["beat"] and verified.get(x2["file"],{}).get("sha")==x["photo_sha"]),None)
  if not rec:continue
  a=Image.open(verified[rec["file"]]["path"])
  a=ImageOps.fit(a.convert("RGB"),(190,320),Image.Resampling.LANCZOS)
  col=i%7
  contact.paste(a,(5+col*199,52))
 d.text((28,12),"GIULIANO • THE WALKING GIANTS / NUOVI REPERTI FOTOGRAFICI",font=font(24,True),fill=(243,221,180))
 contact.save(OUT/"NOVITA_FOTOGRAFICHE.jpg",quality=91)
 report={
  "status":"MASTER_AND_ANDROID_FULL_DECODE_PASS",
  "edition":"Giuliano Episode 2 - Field Test Real Footage V3",
  "duration_seconds":qa["duration_seconds"],
  "old_unique_photographs":qa["unique_actual_photo_count"],
  "new_unique_licensed_photographs":len({x["photo_sha"] for x in photos}),
  "minimum_distinct_photos":qa["unique_actual_photo_count"]+len({x["photo_sha"] for x in photos}),
  "genuine_new_experiment_clip_included":True,
  "genuine_field_test_duration_seconds":round(authentic["end"]-authentic["begin"],2),
  "genuine_field_test_source_sha256":authentic["source_sha256"],
  "external_experiment_video":"https://www.binghamton.edu/news/story/5830/easter-islands-statues-actually-walked-and-physics-backs-it-up",
  "scientific_3d_animated_beats":[x["beat"] for x in science],
  "animated_video_seconds":round(sum(x["end"]-x["begin"] for x in science),2),
  "model_source":"https://github.com/clipo/moai_walking MIT (Carl Lipo & Terry Hunt)",
  "original_Google_voice_and_score_pcm_unchanged":True,
  "source_photo_license_checked":True,
  "total_new_picture_edits":len(scenes),
  "master_sha256":sha(movie),"android_sha256":sha(mobile),
  "artistic_review_still_needed":True,"published":False,
  "timeline":[{k:(str(v) if isinstance(v,Path) else v) for k,v in x.items()} for x in scenes]}
 (OUT/"QA_DEFINITIVO.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 text="THE WALKING GIANTS — VERSIONE DEFINITIVA\n"
 text+="Durata originale, voce Gacrux e musica mantenute; nuove foto con licenze verificate e filmati 3D tecnici originali.\n"
 text+="ATTENZIONE: i tre segmenti del moai che oscilla sono ANIMAZIONI SCIENTIFICHE, non riprese dell'esperimento del 2025.\n"
 text+="Filmato autentico dell'esperimento di Carl Lipo: https://www.binghamton.edu/news/story/5830/easter-islands-statues-actually-walked-and-physics-backs-it-up\n"
 text+="Pubblicazione: NON AUTORIZZATA IN AUTOMATICO. Controllo artistico da effettuare.\n"
 (OUT/"LEGGIMI_ANDROID.txt").write_text(text,encoding="utf8")
 zf=OUT/"THE_WALKING_GIANTS_GIULIANO_COMPLETO.zip"
 with zipfile.ZipFile(zf,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
  for p in [movie,mobile,OUT/"COVER_DEFINITIVA.jpg",OUT/"NOVITA_FOTOGRAFICHE.jpg",
   OUT/"QA_DEFINITIVO.json",OUT/"EXTRA_IMAGE_CREDITS.json",OUT/"LEGGIMI_ANDROID.txt",
   ASSETS/"MIT_LICENSE_CARL_LIPO_TERRY_HUNT.txt"]:
   z.write(p,p.name)
 with zipfile.ZipFile(zf) as z:
  if z.testzip():raise RuntimeError("ZIP CRC FAILED")
 print(json.dumps({"result":"GIULIANO_MOAI_FINAL_V2_SUCCESS","duration":qa["duration_seconds"],
  "extra_photos":report["new_unique_licensed_photographs"],"animated_seconds":report["animated_video_seconds"],
  "hd_bytes":movie.stat().st_size,"android_bytes":mobile.stat().st_size,
  "zip_bytes":zf.stat().st_size,"hd_sha256":sha(movie),"zip_sha256":sha(zf)}),flush=True)
if __name__=="__main__":main()
