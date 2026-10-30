#!/usr/bin/env python3
"""V80 independent TWO authentic city films, each with photoreal AI still photos.
New York 1903 Ellis Island, Venice 1896 Grand Canal. No paid services. Fail closed.
"""
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
import os,sys,cv2,json,hashlib,subprocess,zipfile,wave,html,math,importlib.util
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=Path("output/storia_v80_new_cities");OUT.mkdir(parents=True,exist_ok=True)
W,H,FPS=720,1280,30
UA="TraLePagine-StoriaRivive-V80/1.0 (historical research; https://github.com/GGIANLUCAA/Tra-le-pagine-)"
FILMS={
"NEW_YORK_1903":{
 "city":"NEW YORK","year":"1903",
 "commons":"File:Emigrants (i.e. immigrants) landing at Ellis Island -.webm",
 "page":"https://commons.wikimedia.org/wiki/File:Emigrants_(i.e._immigrants)_landing_at_Ellis_Island_-.webm",
 "loc":"https://www.loc.gov/item/00694367/",
 "description":"1903 authentic emigrants arriving at Ellis Island, New York, disembarking with their luggage",
 "shots":[
  {"t":91.5,"center":1030,"length":2.1,"tag":"family arriving with luggage"},
  {"t":103.2,"center":720,"length":2.1,"tag":"immigrant woman in period clothes carrying baggage"},
  {"t":115.8,"center":590,"length":2.15,"tag":"immigrant man with suitcases and hat"},
  {"t":141.0,"center":835,"length":2.2,"tag":"family and people carrying baggage at the dock"}
 ]
},
"VENICE_1896":{
 "city":"VENICE","year":"1896",
 "commons":"File:Venise Panorama du Grand Canal 1896.webm",
 "page":"https://commons.wikimedia.org/wiki/File:Venise_Panorama_du_Grand_Canal_1896.webm",
 "description":"authentic Lumiere film, Alexandre Promio 1896 camera moving on a boat through the Grand Canal, Venice",
 "shots":[
  {"t":9.5,"center":670,"length":2.2,"tag":"stone facades and water reflections of Grand Canal Venice 1896"},
  {"t":18.3,"center":680,"length":2.2,"tag":"gondola and real Renaissance era Venetian architecture on canal"},
  {"t":29.5,"center":660,"length":2.2,"tag":"Venice Grand Canal palace facades water and boats"},
  {"t":40.7,"center":690,"length":2.25,"tag":"real late nineteenth century Venice waterfront detail and reflections"}
 ]
}
}
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def cmd(argv,timeout=250):
 p=subprocess.run(argv,capture_output=True,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError(" ".join(map(str,argv[:5]))+" "+p.stderr[-1250:])
 return p.stdout
def acquire(meta,d):
 name=meta["commons"]
 api="https://commons.wikimedia.org/w/api.php?"+urlencode({
 "action":"query","format":"json","formatversion":"2","prop":"imageinfo","titles":name,
 "iiprop":"url|size|mime|extmetadata"})
 req=Request(api,headers={"User-Agent":UA,"Accept":"application/json"})
 with urlopen(req,timeout=50) as r:data=json.load(r)
 pg=data["query"]["pages"][0]
 if "imageinfo" not in pg:raise RuntimeError("SOURCE_NOT_FOUND "+str(pg)[:250])
 item=pg["imageinfo"][0]
 if item["mime"]!="video/webm" or not(10_000_000<int(item["size"])<160_000_000):raise RuntimeError("unexpected master source")
 rights={k:html.unescape(v.get("value","")) for k,v in item.get("extmetadata",{}).items() if k in ["LicenseShortName","LicenseUrl","Copyrighted","Artist","Credit"]}
 # Explicitly no claim that PD US covers ALL international usage automatically.
 if "PD" not in str(rights) and "Public Domain" not in str(rights) and "publicdomain" not in str(rights).lower():
  print("RIGHTS_REVIEW_REQUIRED",meta["city"],rights,flush=True)
 source=d/"ORIGINAL_ARCHIVE.webm"
 if not source.exists() or source.stat().st_size!=item["size"]:
  request=Request(item["url"],headers={"User-Agent":UA})
  with urlopen(request,timeout=180) as r,open(source,"wb") as f:
   while b:=r.read(1<<20):
    f.write(b)
    if f.tell()>160_000_000:raise RuntimeError("oversized original")
 if source.stat().st_size!=item["size"]:raise RuntimeError("incomplete original")
 v=cv2.VideoCapture(str(source))
 fps=v.get(cv2.CAP_PROP_FPS);w=v.get(cv2.CAP_PROP_FRAME_WIDTH);h=v.get(cv2.CAP_PROP_FRAME_HEIGHT)
 duration=v.get(cv2.CAP_PROP_FRAME_COUNT)/max(fps,1);v.release()
 if fps<15 or w<1300 or h<900 or duration<44:raise RuntimeError(f"poor original {w}x{h} fps {fps} duration {duration}")
 info={"original_page":meta["page"],"exact_source_filename":name,"original_url":item["url"],
  "original_sha256":sha(source),"original_size":source.stat().st_size,"width":w,"height":h,"fps":fps,"duration":duration,
  "rights_on_commons":rights,"rights_italy_final_review":"PENDING","color_is_hypothetical":True}
 (d/"SOURCE_QA.json").write_text(json.dumps(info,ensure_ascii=False,indent=2))
 print("ARCHIVE_ORIGINAL_ACQUIRED",meta["city"],w,h,duration,source.stat().st_size,flush=True)
 return source,info
def crop(frame,center):
 h,w=frame.shape[:2];cw=int(h*9/16)
 x0=max(0,min(w-cw,int(center-cw/2)))
 return cv2.resize(frame[:,x0:x0+cw],(W,H),interpolation=cv2.INTER_CUBIC)
def grab_stills(source,meta,d):
 cap=cv2.VideoCapture(str(source))
 records=[]
 for i,s in enumerate(meta["shots"],1):
  cap.set(cv2.CAP_PROP_POS_MSEC,float(s["t"])*1000)
  ok,fr=cap.read()
  if not ok:raise RuntimeError("missing film frame at "+str(s["t"]))
  pic=crop(fr,s["center"])
  filename=f"FRAME_{i:02d}_SOURCE.png"
  cv2.imwrite(str(d/filename),pic,[cv2.IMWRITE_PNG_COMPRESSION,3])
  records.append({"scene":i,"source_time":s["t"],"source_frame":filename,"sha256":sha(d/filename),"desc":s["tag"]})
 cap.release()
 canvas=Image.new("RGB",(4*220,480),(17,18,22))
 for j,r in enumerate(records):
  im=Image.open(d/r["source_frame"]).convert("RGB").resize((215,385))
  canvas.paste(im,(j*220+2,30))
  ImageDraw.Draw(canvas).text((j*220+6,5),f"{meta['city']} {r['source_time']}s",fill="white")
 canvas.save(d/"REAL_FILM_SCENES.jpg",quality=90)
 (d/"FRAME_QA.json").write_text(json.dumps(records,indent=2))
 return records
def load_dd():
 p=ROOT/"src/storia_rivive_real_ai_v60.py"
 sp=importlib.util.spec_from_file_location("ddcolor_v80",p)
 d=importlib.util.module_from_spec(sp);sp.loader.exec_module(d)
 ss,meta=d.download_model()
 return d,ss,meta
def natural_color(dd,session,source):
 # Preserve the original luminance and source silhouettes, only predict color channels.
 bgr=cv2.imread(str(source))
 bgrres=cv2.resize(bgr,(720,576),interpolation=cv2.INTER_AREA)
 ab=dd.infer_ab(session,bgrres)
 l=dd.l_channel(bgr)
 ab=cv2.resize(ab,(W,H),interpolation=cv2.INTER_LINEAR)
 rgb=np.clip(cv2.cvtColor(np.dstack((l,np.clip(ab*1.10,-110,110))).astype("float32"),cv2.COLOR_LAB2RGB)*255,0,255).astype("uint8")
 return cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR)
def similarity(a,b):
 def down(im):
  if im.ndim==3:im=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
  im=cv2.GaussianBlur(cv2.resize(im,(72,128)),(7,7),0).astype(np.float32)
  return im.ravel()
 s=down(a);t=down(b)
 return float(np.corrcoef(s,t)[0,1])
def enhanced_ai_images(meta,records,d,dd,ss):
 from gradio_client import Client,handle_file
 import inspect
 kwargs={"verbose":False}
 params=inspect.signature(Client).parameters
 token=os.environ.get("HF_TOKEN")
 if token:
  if "hf_token" in params:kwargs["hf_token"]=token
  elif "token" in params:kwargs["token"]=token
 client=Client("finegrain/finegrain-image-enhancer",**kwargs)
 produced=[]
 for r in records:
  i=r["scene"];source=cv2.imread(str(d/r["source_frame"]))
  base=natural_color(dd,ss,d/r["source_frame"])
  basefile=d/f"PHOTO_COLOR_BASE_{i:02d}.jpg"
  cv2.imwrite(str(basefile),cv2.resize(base,(576,1024)),[cv2.IMWRITE_JPEG_QUALITY,96])
  prompt=(f"Extremely detailed modern photographic restoration of the EXACT historical black-and-white film frame. "
   f"Photorealistic natural COLOR photographic materials, realistic eyes and skin only for actual visible people, "
   f"realistic detailed period clothing and architecture. Scene: {r['desc']}. "
   f"Maintain the EXACT number and exact positions of people, faces, animals, vehicles, suitcases, rails, wheels and buildings. "
   f"All recognizable structural components of the source MUST remain structures. "
   f"NO extra figures, NO objects transforming into people, NO new faces in blurred areas, "
   f"NO invented identities or textual lettering. Preserve precise camera viewpoint and geometry.")
  neg=("extra people, new faces, imaginary people, cars transforming into people, wheels transforming to bodies, "
   "extra humans, hallucinated limbs, wrong buildings, new animals, perspective changes, cartoon, painting, "
   "skin airbrushed, plastic skin, added objects, invented text")
  print("PHOTO_AI_GENERATION",meta["city"],i,flush=True)
  try:
   # Using a public free Gradio space. One attempt per image; no paid or Vidu calls.
   result=client.predict(handle_file(str(basefile)),prompt,neg,1903+i*17,2,1.1,.96,6,112,144,.39,18,"DDIM",api_name="/process")
   p=result[1] if isinstance(result,(tuple,list)) else result
   if isinstance(p,dict):p=p.get("path")
   if not p or not Path(str(p)).is_file():raise RuntimeError("empty AI image")
   candidate=cv2.imread(str(p))
   if candidate is None:raise RuntimeError("invalid generated image")
   candidate=cv2.resize(candidate,(W,H),interpolation=cv2.INTER_CUBIC)
   corr=similarity(source,candidate)
   sat=float(cv2.cvtColor(candidate,cv2.COLOR_BGR2HSV)[:,:,1].mean())
   if not np.isfinite(corr) or corr<.69 or sat<15 or sat>150:raise RuntimeError(f"rejected photographic candidate geometry={corr:.3f} sat={sat:.1f}")
   # No global source luminance blend: V77 destroyed face detail.
   target=d/f"PHOTO_AI_{i:02d}.png"
   cv2.imwrite(str(target),candidate,[cv2.IMWRITE_PNG_COMPRESSION,2])
   produced.append({**r,"photo_file":target.name,"photo_sha256":sha(target),
    "geom_corr":round(corr,3),"sat":round(sat,1),"model":"DDColor+free Finegrain image enhancer",
    "source_locked_semantic_review":"PENDING_HUMAN"})
   print("ACCEPT_PHOTO_CANDIDATE",meta["city"],i,"correlation",round(corr,3),flush=True)
  except Exception as e:
   print("PHOTO_AI_REJECTED_OR_FREE_QUOTA",meta["city"],i,type(e).__name__,str(e)[:280],flush=True)
   # Preserve old scene but do NOT pass color-only base as a true generative photo.
 (d/"PHOTO_QA.json").write_text(json.dumps(produced,ensure_ascii=False,indent=2))
 if len(produced)<3:raise RuntimeError(f"NOT_ENOUGH_TRUE_NEW_GENERATIVE_PHOTOS_{meta['city']}_{len(produced)}")
 return produced
def title_over_frame(frame,t,meta):
 fade=min(1.,t/.35,max(0.,(1.8-t)/.40))
 if fade<=0:return frame
 im=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)).convert("RGBA")
 layer=Image.new("RGBA",(W,H),(0,0,0,0));dr=ImageDraw.Draw(layer)
 try:
  serif=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",61)
  year=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",51)
 except:serif=ImageFont.load_default();year=serif
 for y in range(90,420,4):
  a=int(110*fade*max(0,1-(y-90)/335))
  dr.rectangle((0,y,W,y+4),fill=(8,11,16,a))
 for txt,font,dy,col in [(meta["city"],serif,154,(250,248,241,int(255*fade))),
                          (meta["year"],year,252,(230,203,153,int(250*fade)))]:
  bb=dr.textbbox((0,0),txt,font=font);x=(W-(bb[2]-bb[0]))//2
  dr.text((x,dy),txt,font=font,fill=col)
 dr.line((185,120,535,120),fill=(215,189,145,int(190*fade)),width=2)
 dr.line((213,336,507,336),fill=(215,189,145,int(155*fade)),width=2)
 return cv2.cvtColor(np.asarray(Image.alpha_composite(im,layer).convert("RGB")),cv2.COLOR_RGB2BGR)
def create_audio(duration,scene_info,d):
 sr=32000;t=np.arange(int(duration*sr),dtype=np.float32)/sr
 chord=[[130.81,164.81,196.0],[146.83,196.0,246.94],[164.81,207.65,261.63],[130.81,174.61,220.0]]
 v=np.zeros_like(t)
 for j,s in enumerate(scene_info):
  start=s["output_start_sec"];end=scene_info[j+1]["output_start_sec"] if j+1<len(scene_info) else duration
  mask=(t>=start)&(t<end);tt=t[mask]-start;sig=np.zeros_like(tt)
  for k,f in enumerate(chord[j%4]):
   sig+=.028*np.sin(2*np.pi*f*tt+k*.4)*(0.7+.3*np.sin(.7*tt))
   sig+=.003*np.sin(2*np.pi*2*f*tt)
  delta=tt-s["reveal_at_relative_sec"];hit=(delta>=0)&(delta<.55)
  sig[hit]+=.07*np.sin(2*np.pi*(150*delta[hit]+90*delta[hit]**2))*np.exp(-9*delta[hit])
  v[mask]=sig
 v*=np.minimum(1,t/.8)*np.minimum(1,np.maximum(0,(duration-t)/.8))
 v=np.tanh(v*2.0)
 path=d/"ORIGINAL_MUSIC.wav"
 with wave.open(str(path),"wb") as f:
  f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr)
  f.writeframes((np.column_stack((v,np.roll(v,int(sr*.013))*.94))*18000).astype("<i2").tobytes())
 return path
def render(meta,source,photos,d,source_info):
 output=d/f"LA_STORIA_RIVIVE_{meta['city']}_{meta['year']}_V80.mp4"
 silence=d/"VIDEO_NO_AUDIO.mp4"
 process=subprocess.Popen(["ffmpeg","-nostdin","-y","-v","error","-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
  "-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p","-movflags","+faststart",str(silence)],
  stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 frames=0;scenes=[]
 try:
  for si,p in enumerate(photos):
   sh=meta["shots"][p["scene"]-1]
   if sha(d/p["source_frame"])!=p["sha256"] or sha(d/p["photo_file"])!=p["photo_sha256"]:
    raise RuntimeError("IMAGE_INTEGRITY_CHANGED")
   still=cv2.imread(str(d/p["photo_file"]))
   origin=cv2.cvtColor(cv2.imread(str(d/p["source_frame"])),cv2.COLOR_BGR2GRAY)
   origin=cv2.cvtColor(origin,cv2.COLOR_GRAY2BGR)
   start=frames/FPS
   cap=cv2.VideoCapture(str(source))
   fps_in=cap.get(cv2.CAP_PROP_FPS);motion_sec=sh["length"]
   cap.set(cv2.CAP_PROP_POS_MSEC,(sh["t"]-motion_sec)*1000)
   raw=[]
   for _ in range(max(6,round(motion_sec*fps_in))):
    ok,frame=cap.read()
    if not ok:break
    raw.append(crop(frame,sh["center"]))
   cap.release()
   if len(raw)<max(6,round(motion_sec*fps_in*.65)):raise RuntimeError("MISSING_REAL_MOVEMENT")
   n=round(motion_sec*FPS)
   for k in range(n):
    index=min(len(raw)-1,round(k*(len(raw)-1)/(n-1)))
    frame=cv2.cvtColor(cv2.cvtColor(raw[index],cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR)
    if k>=n-4:frame=cv2.addWeighted(frame,(n-1-k)/4,origin,1-(n-1-k)/4,0)
    if si==0 and k/FPS<1.8:frame=title_over_frame(frame,k/FPS,meta)
    process.stdin.write(frame.tobytes());frames+=1
   for _ in range(3):process.stdin.write(origin.tobytes());frames+=1
   for k in range(10):
    a=(k+1)/10;a=a*a*(3-2*a)
    process.stdin.write(cv2.addWeighted(origin,1-a,still,a,0).tobytes());frames+=1
   hold=3.65 if si==len(photos)-1 else (3.25 if si%2==0 else 3.12)
   for _ in range(round(hold*FPS)):
    process.stdin.write(still.tobytes());frames+=1
   scenes.append({"name":sh["tag"],"original_seconds":sh["t"],"output_start_sec":round(start,3),
       "reveal_at_relative_sec":round(n/FPS+.10,3),"photo_hold":hold,
       "source_frame_sha":p["sha256"],"ai_photo_sha":p["photo_sha256"]})
   print("REAL_ORIGINAL_FILM_AND_AI_STILL",meta["city"],si+1,"duration_now",round(frames/FPS,2),flush=True)
 finally:
  process.stdin.close();err=process.stderr.read().decode(errors="replace")
  if process.wait():raise RuntimeError("video_encoder_failed "+err[-900:])
 length=frames/FPS
 audio=create_audio(length,scenes,d)
 cmd(["ffmpeg","-nostdin","-y","-v","error","-i",str(silence),"-i",str(audio),"-map","0:v:0","-map","1:a:0",
 "-c:v","copy","-c:a","aac","-b:a","160k","-t",str(length),"-movflags","+faststart",str(output)],150)
 cmd(["ffmpeg","-v","error","-xerror","-i",str(output),"-f","null","-"],150)
 probe=json.loads(cmd(["ffprobe","-v","error","-show_entries","stream=codec_name,width,height,r_frame_rate:format=duration,size","-of","json",str(output)],25))
 if float(probe["format"]["duration"])<19 or len(probe["streams"])<2:raise RuntimeError("INCOMPLETE_VIDEO")
 # Strict user-approved structure: true monochrome motion then at least 3 colored photographs.
 module=ROOT/"src/storia_rivive_v74_effect_gate.py"
 sp=importlib.util.spec_from_file_location("gate",module);gate=importlib.util.module_from_spec(sp);sp.loader.exec_module(gate)
 report=gate.inspect_video(output)
 if report["approved_pattern_cycles"]<3:raise RuntimeError("NOT_THE_USER_APPROVED_EFFECT "+json.dumps(report)[:400])
 # Visual QA contact sheet; actual generated photographs, not stock.
 board=Image.new("RGB",(3*245,2*462),(12,14,16));d2=ImageDraw.Draw(board)
 for ix,p in enumerate(photos[:3]):
  s=Image.open(d/p["source_frame"]).convert("RGB").resize((234,416))
  t=Image.open(d/p["photo_file"]).convert("RGB").resize((234,416))
  board.paste(s,(ix*245+4,26))
  board.paste(t,(ix*245+4,485))
  d2.text((ix*245+8,6),f"ACTUAL FILM {ix+1}",fill="white")
  d2.text((ix*245+8,466),f"AI PHOTO {ix+1}",fill="white")
 board.save(d/"BEFORE_AFTER_ACTUAL_GENERATED.jpg",quality=92)
 cover=Image.open(d/photos[-1]["photo_file"]).convert("RGB")
 cover.save(d/"COVER.jpg",quality=94)
 notes={"FACEBOOK":f"{meta['city']} · {meta['year']}. A moving film from more than a century ago becomes a vivid photographic moment. Authentic archival footage; colors and reconstructed fine details are AI interpretations. Source: {meta['page']}.",
 "INSTAGRAM":f"{meta['city']} · {meta['year']}. Real historical motion, then a moment frozen in color. Faces and colors restored with AI are interpretations, not documented originals. #HistoryReels #RestoredHistory",
 "TIKTOK":f"{meta['city']} in {meta['year']} — watch history come to life. Original archival footage, AI reconstructed photographic stills. The film is real; its colors are hypothetical. #history",
 "YOUTUBE":f"{meta['city']} · {meta['year']} | La Storia Rivive\nOriginal historical motion pictures restored through same-frame AI photographic reconstruction. Digital color and small details are artistic interpretations, not historical evidence. Original archive: {meta['page']}."}
 for k,v in notes.items():(d/f"POST_{k}.txt").write_text(v+"\n",encoding="utf8")
 qa={"title":f"{meta['city']} · {meta['year']}","version":"V80",
  "source":source_info,"true_historical_moving_film":True,
  "photo_AI_images":photos,"real_photo_count":len(photos),"scenes":scenes,
  "duration_s":length,"video":output.name,"sha256":sha(output),"probe":probe,"format_check":report,
  "no_invented_motion":True,"photo_faces_are_interpretative":True,
  "human_semantic_review":"PENDING","not_native_4k":True,"original_music":True,
  "vidu_credits_used":0,"no_paid_requests":True,"uploaded_to_private_site":False,"social_published":False}
 (d/"QA.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2))
 package=d/f"LA_STORIA_RIVIVE_{meta['city']}_{meta['year']}_KIT.zip"
 with zipfile.ZipFile(package,"w",compression=zipfile.ZIP_DEFLATED) as z:
  for f in [output,d/"COVER.jpg",d/"BEFORE_AFTER_ACTUAL_GENERATED.jpg",d/"QA.json",
    d/"SOURCE_QA.json",d/"PHOTO_QA.json",*[d/f"POST_{k}.txt" for k in notes]]:
   z.write(f,f.name)
 with zipfile.ZipFile(package) as z:
  if z.testzip():raise RuntimeError("zip CRC error")
 print("V80_VIDEO_READY",output,output.stat().st_size,"ZIP",package,package.stat().st_size,flush=True)
if __name__=="__main__":
 dd,ss,model=load_dd()
 report={"model":model,"statuses":[]}
 for key,meta in FILMS.items():
  d=OUT/key;d.mkdir(parents=True,exist_ok=True)
  try:
   source,sourceinfo=acquire(meta,d)
   records=grab_stills(source,meta,d)
   photos=enhanced_ai_images(meta,records,d,dd,ss)
   render(meta,source,photos,d,sourceinfo)
   report["statuses"].append({"film":key,"status":"VIDEO_RENDERED","photos":len(photos)})
  except Exception as e:
   print("V80_FILM_FAILED",key,type(e).__name__,str(e)[:650],flush=True)
   report["statuses"].append({"film":key,"status":"FAILED_NOT_PUBLISHED","error":str(e)})
  (OUT/"REPORT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
 if not any(x["status"]=="VIDEO_RENDERED" for x in report["statuses"]):
  raise RuntimeError("No film passed artistic and technical quality gates; report only, no video release")
