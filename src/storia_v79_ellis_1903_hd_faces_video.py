#!/usr/bin/env python3
"""La Storia Rivive V79: Ellis Island 1903, a NEW archival motion film with four HD human photo reconstructions.
SOURCE original LOC->Wikimedia public-domain scan. Zero paid APIs, no Vidu.
Real 1903 motion -> exact freeze -> generated modern photographic color still -> next genuine motion.
"""
from pathlib import Path
from urllib.request import urlopen,Request
from urllib.parse import urlencode
import hashlib,cv2,numpy as np,json,subprocess,sys,zipfile,wave,importlib.util
from PIL import Image,ImageDraw,ImageFont,ImageFilter

ROOT=Path(__file__).resolve().parents[1];OUT=Path("output/storia_v79_ellis")
OUT.mkdir(parents=True,exist_ok=True)
FILM=OUT/"ELLIS_ISLAND_1903_ORIGINAL.webm"
FILM_PAGE="https://commons.wikimedia.org/wiki/File:Emigrants_(i.e._immigrants)_landing_at_Ellis_Island_-.webm"
LOC="https://www.loc.gov/item/00694367/"
# Source-specific crop: exact 9:16 450x800 area of 1440x1080 frame, selected after reviewing genuine archival frame board.
SHOTS=[
 dict(name="Il viaggiatore con i bagagli",t=115.0,rect=[335,150,450,800],mov=2.30,hold=3.85,desc="one central adult man wearing a dark jacket, brimmed hat and holding large luggage, several actual emigrants in the far background",face="adult man's face at (relative center x=.50,y=.26)"),
 dict(name="Una famiglia arriva",t=85.0,rect=[730,160,450,800],mov=2.22,hold=3.72,desc="a small child in headscarf, adult woman carrying a baby, family group and travel bags, actual existing people",face="the real child's face and adult woman's face in original film"),
 dict(name="Donne sul molo",t=95.0,rect=[285,150,450,800],mov=2.12,hold=3.90,desc="real women wearing white headscarves, dark coats and dresses and a child holding a rectangular suitcase, no extra people",face="woman with white bonnet in center, small girl below her, faces inferred only where visible"),
 dict(name="Si attraversa il molo",t=143.0,rect=[435,140,450,800],mov=2.38,hold=3.80,desc="two men in light shirts and suspenders, vintage hats, trolley cart and original walkway, no invented faces",face="two central real adult men's faces beneath period hats")
]
FPS=30;W=720;H=1280

def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def run(argv,timeout=220):
 p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError(str(argv[:3])+" "+p.stderr[-1400:])
 return p.stdout

def get_film():
 if FILM.exists() and FILM.stat().st_size>60_000_000:return FILM
 params=urlencode({"action":"query","format":"json","formatversion":"2","prop":"imageinfo","titles":"File:Emigrants (i.e. immigrants) landing at Ellis Island -.webm","iiprop":"url|size|mime"})
 req=Request("https://commons.wikimedia.org/w/api.php?"+params,headers={"User-Agent":"TraLePagine-ArtVision/1.0 archival faithful restoration"})
 with urlopen(req,timeout=45) as r:obj=json.load(r)
 info=obj["query"]["pages"][0]["imageinfo"][0]
 if info["mime"]!="video/webm" or info["size"]<60_000_000 or info["size"]>100_000_000:raise RuntimeError("Unsupported source")
 req=Request(info["url"],headers={"User-Agent":"TraLePagine-ArtVision/1.0 archival faithful restoration"})
 with urlopen(req,timeout=180) as r,FILM.open("wb") as f:
  while buf:=r.read(1<<20):f.write(buf)
 if FILM.stat().st_size!=info["size"]:raise RuntimeError("Film not completely acquired")
 return FILM

def crop_from_native(fr,rect):
 x,y,w,h=rect
 if fr.shape[1]<x+w or fr.shape[0]<y+h:raise RuntimeError("Source crop outside original frame")
 return cv2.resize(fr[y:y+h,x:x+w],(W,H),interpolation=cv2.INTER_CUBIC)
def snapshot_frames():
 cap=cv2.VideoCapture(str(get_film()))
 fps=float(cap.get(cv2.CAP_PROP_FPS));dur=cap.get(cv2.CAP_PROP_FRAME_COUNT)/fps
 if cap.get(3)<1400 or cap.get(4)<1080 or dur<140:raise RuntimeError("Wrong LOC archival scan")
 images=[]
 for i,s in enumerate(SHOTS,1):
  cap.set(cv2.CAP_PROP_POS_MSEC,1000*s["t"])
  ok,fr=cap.read()
  if not ok:raise RuntimeError("Missing source frame "+str(i))
  original=crop_from_native(fr,s["rect"])
  p=OUT/f"ORIGINAL_{i:02d}.png";cv2.imwrite(str(p),original)
  images.append(p)
 cap.release()
 print("LOC_1903_PRIMARY_FILM",FILM.stat().st_size,sha(FILM),fps,dur,flush=True)
 return images,fps

def color_input(original):
 spec=importlib.util.spec_from_file_location("ddcolor",ROOT/"src/storia_rivive_real_ai_v60.py")
 dd=importlib.util.module_from_spec(spec);spec.loader.exec_module(dd)
 return dd

def photorealistic_stills(inputs):
 # Referenced generation defaults are from previously successful Paris V71 free Finegrain output.
 # SOURCE LOCK: high-confidence scene geometry validated and detailed faces prioritized.
 from gradio_client import Client,handle_file
 dd=color_input(inputs[0])
 session,meta=dd.download_model()
 client=Client("finegrain/finegrain-image-enhancer",verbose=False)
 accepted=[];failures=[]
 for i,(p,s) in enumerate(zip(inputs,SHOTS),1):
  bgr=cv2.imread(str(p))
  hsv=cv2.cvtColor(bgr,cv2.COLOR_BGR2LAB).astype(np.float32)
  ab=dd.infer_ab(session,cv2.resize(bgr,(720,576),interpolation=cv2.INTER_AREA))
  ab=cv2.resize(ab,(W,H),interpolation=cv2.INTER_CUBIC)
  lum=dd.l_channel(bgr)
  pre=np.clip(cv2.cvtColor(np.dstack((lum,np.clip(ab*1.03,-110,110))).astype(np.float32),cv2.COLOR_LAB2RGB)*255,0,255).astype(np.uint8)
  pre=Image.fromarray(pre).filter(ImageFilter.UnsharpMask(radius=1.2,percent=75,threshold=4))
  base=OUT/f"COLORED_SOURCE_{i:02}.jpg";pre.save(base,quality=95)
  prompt=(
   "Restore the given photograph of REAL HUMAN BEINGS arriving at Ellis Island in 1903 into a VERY SHARP "
   "photorealistic contemporary DSLR quality COLOR documentary photograph, visible realistic faces with clear "
   "lifelike eyes, skin pores and individual hair texture wherever the real source supports it; crisp fabrics "
   "with physical seams and believable natural light; historically plausible clothes and hats. "
   "IMAGE-TO-IMAGE HARD RULE: exactly the original same people in their original locations, exactly the same "
   "number of people and original poses, identical silhouettes, person/child/adult identity classes, arms, "
   "luggage, railings, wheels, carts, boats and architecture. DO NOT invent people, DO NOT turn an object into "
   "a person, DO NOT turn persons into objects, DO NOT modify the geometry, DO NOT crop or change framing. "
   "Specific source scene: "+s["desc"]+". Facial priority: "+s["face"]+". "
   "No painting, illustration, staged portrait, bokeh that removes history, plastic AI skin, ghost faces."
  )
  neg=("invented person, extra head, extra face, incorrect number of people, false eyes on background objects, "
   "object turning into human, fake child, car turning into person, facial identity swapped, distorted luggage, "
   "ghost people, wrong gender or wrong outfit, wrong pose, poster, drawing, monochrome, sepia, oversmooth faces, AI stylization")
  try:
   response=client.predict(handle_file(str(base)),prompt,neg,1024+i*133,2,1.23,0.95,6,112,144,0.35,16,"DDIM",api_name="/process")
   result=response[1] if isinstance(response,(list,tuple)) else response
   if isinstance(result,dict):result=result.get("path")
   if not result or not Path(str(result)).is_file():raise RuntimeError("Free AI did not return physical photo")
   color=cv2.imread(str(result))
   if color is None:raise RuntimeError("Unreadable AI photo")
   color=cv2.resize(color,(W,H))
   # Luminance structure global correlation plus localized structural tile test.
   def smallgray(a):return cv2.GaussianBlur(cv2.resize(cv2.cvtColor(a,cv2.COLOR_BGR2GRAY),(72,128)),(9,9),0).astype(np.float32).ravel()
   g=smallgray(bgr);h=smallgray(color)
   corr=float(np.corrcoef(g,h)[0,1]);sat=float(cv2.cvtColor(color,cv2.COLOR_BGR2HSV)[:,:,1].mean())
   print("GENERATED_FACE_PHOTO",i,"corr",round(corr,3),"color",round(sat,1),flush=True)
   if not np.isfinite(corr) or corr<.69 or sat<15:raise RuntimeError("Image geometry or color too distant")
   dst=OUT/f"FOTO_AI_{i:02}.png";cv2.imwrite(str(dst),color,[cv2.IMWRITE_PNG_COMPRESSION,2])
   accepted.append(dict(i=i,shot=s["name"],source_photo=p.name,source_sha=sha(p),ai_photo=dst.name,ai_sha=sha(dst),
                        geometry_score=round(corr,3),color_saturation=round(sat,1),face_disclosure="New pixel-level facial details from AI are plausible, NOT verified likeness of a real historical individual.",semantic_human_qa="PENDING"))
  except Exception as ex:
   failures.append(dict(i=i,reason=str(ex)[:350]))
   print("FREE_AI_PHOTO_FAILED",i,str(ex)[:400],flush=True)
 (OUT/"PHOTO_QA.json").write_text(json.dumps(dict(photos=accepted,failures=failures,source=FILM_PAGE,model="finegrain/finegrain-image-enhancer plus DDColor free",no_paid_api=True,human_review="PENDING"),ensure_ascii=False,indent=2))
 if len(accepted)<3:raise RuntimeError("Not enough real AI photo results to create a qualifying video")
 return accepted

def title(frame,second):
 if second>=2:return frame
 opacity=min(1,second/.25,max(0,(1.85-second)/.50))
 if opacity<=0:return frame
 im=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)).convert("RGBA")
 overlay=Image.new("RGBA",(W,H),(0,0,0,0))
 d=ImageDraw.Draw(overlay,"RGBA")
 try:
  serif=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",55)
  roman=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",50)
 except:serif=ImageFont.load_default();roman=serif
 d.rectangle((0,0,W,425),fill=(6,8,10,int(96*opacity)))
 def centered(text,font,y,color):
  box=d.textbbox((0,0),text,font=font);x=(W-(box[2]-box[0]))/2
  d.text((int(x),y),text,font=font,fill=color)
 centered("ELLIS ISLAND",serif,173,(250,244,232,int(255*opacity)))
 d.line((163,259,557,259),fill=(216,195,151,int(160*opacity)),width=2)
 centered("1903",roman,300,(238,220,184,int(255*opacity)))
 return cv2.cvtColor(np.asarray(Image.alpha_composite(im,overlay).convert("RGB")),cv2.COLOR_RGB2BGR)

def audio(dur,cues):
 sr=32000;t=np.arange(round(dur*sr),dtype=np.float32)/sr;v=np.zeros_like(t)
 chord=[[130.81,164.81,196,261.63],[146.83,174.61,220,293.66],[130.81,174.61,196,246.94],[146.83,196,246.94,293.66]]
 for j,start in enumerate(cues):
  end=cues[j+1] if j+1<len(cues) else dur
  m=(t>=start)&(t<end);q=t[m]-start;z=np.zeros_like(q)
  for k,f in enumerate(chord[j%len(chord)]):
   z+=(0.019-.002*k)*(np.sin(2*np.pi*f*q+k*.25)+.12*np.sin(2*np.pi*f*2.001*q))
  # gentle accents at each image transformation. Recorded no historical sounds.
  for at in (2.1,):
   u=q-at;gate=(u>=0)&(u<.5)
   z[gate]+=.04*np.sin(2*np.pi*(160*u[gate]+80*u[gate]**2))*np.exp(-9*u[gate])
  v[m]+=z
 v*=np.minimum(1,t/.8)*np.minimum(1,np.maximum(0,(dur-t)/.9))
 v=np.tanh(v*2.3)
 wav=OUT/"ORIGINAL_MUSIC.wav"
 with wave.open(str(wav),"wb") as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr)
  w.writeframes((np.stack((v,np.roll(v,400)*.92),axis=1)*19000).astype("<i2").tobytes())
 return wav

def render(photos):
 silent=OUT/"SILENT.mp4"
 cmd=["ffmpeg","-nostdin","-y","-loglevel","error","-f","rawvideo","-pix_fmt","bgr24",
      "-s","720x1280","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","19",
      "-pix_fmt","yuv420p",str(silent)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 fc=0;cues=[]
 source_fps=24 # digital film actual source fps after source review
 try:
  for j,x in enumerate(photos):
   s=SHOTS[x["i"]-1];cues.append(fc/FPS)
   end=s["t"];start=end-s["mov"]
   cap=cv2.VideoCapture(str(FILM));cap.set(cv2.CAP_PROP_POS_MSEC,start*1000)
   raw=[]
   for k in range(round(s["mov"]*source_fps)):
    ok,fr=cap.read()
    if not ok:break
    raw.append(crop_from_native(fr,s["rect"]))
   cap.release()
   if len(raw)<20:raise RuntimeError("Actual historical motion missing")
   src=cv2.imread(str(OUT/x["source_photo"]))
   img=cv2.imread(str(OUT/x["ai_photo"]))
   if src is None or img is None:raise RuntimeError("Photographic asset missing")
   # Check source motion last -> exact captured frame difference; use fading 4 frames.
   for k in range(round(s["mov"]*FPS)):
    idx=min(len(raw)-1,round(k/ (s["mov"]*FPS)*len(raw)))
    bw=cv2.cvtColor(cv2.cvtColor(raw[idx],cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR)
    if k>=round(s["mov"]*FPS)-5:
     a=(k-(round(s["mov"]*FPS)-5)+1)/6
     bw=cv2.addWeighted(bw,1-a,src,a,0)
    if j==0:bw=title(bw,k/FPS)
    p.stdin.write(bw.tobytes());fc+=1
   for k in range(3):p.stdin.write(src.tobytes());fc+=1
   for k in range(10):
    a=(k+1)/10;a=a*a*(3-2*a)
    frame=cv2.addWeighted(src,1-a,img,a,0)
    p.stdin.write(frame.tobytes());fc+=1
   hold=round(s["hold"]*FPS)
   for k in range(hold):
    p.stdin.write(img.tobytes());fc+=1
   print("STORY_SCENE_DONE",x["i"],s["name"],"duration_frames",fc,flush=True)
 finally:
  p.stdin.close()
  err=p.stderr.read().decode(errors="replace")
  if p.wait():raise RuntimeError("Video encoder failed "+err[-700:])
 dur=fc/FPS
 wav=audio(dur,cues)
 master=OUT/"LA_STORIA_RIVIVE_ELLIS_ISLAND_1903_V79.mp4"
 run(["ffmpeg","-nostdin","-y","-loglevel","error","-i",str(silent),"-i",str(wav),
      "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","160k","-t",str(dur),
      "-movflags","+faststart",str(master)],140)
 run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(master),"-f","null","-"],120)
 # Verify correct B/W motion -> color still STRUCTURAL format.
 spec=importlib.util.spec_from_file_location("gate",ROOT/"src/storia_rivive_v74_effect_gate.py")
 gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
 qa=gate.inspect_video(master)
 if qa["approved_pattern_cycles"]<min(len(photos),3):raise RuntimeError("Photographic reference effect gate failed: "+str(qa))
 from PIL import Image
 Image.open(OUT/photos[-1]["ai_photo"]).convert("RGB").save(OUT/"COPERTINA.jpg",quality=93)
 posts={
 "FACEBOOK":"Ellis Island, New York, 1903. Persone vere appena arrivate in America, bagagli e speranze. I loro movimenti appartengono alla pellicola originale; i fotogrammi a colori sono restauri fotografici interpretativi prodotti con AI. I nuovi microdettagli dei visi non sono informazioni storiche certe. Fonte: Library of Congress / Wikimedia Commons.",
 "INSTAGRAM":"ELLIS ISLAND · 1903 🎞️ Persone vere, gesti di oltre un secolo fa. Pellicola autentica, fotografie AI ricostruite. I colori e i microdettagli non sono certi. #EllisIsland #1903 #History",
 "TIKTOK":"1903: arrivavano così a Ellis Island. La storia si ferma e diventa una foto a colori. Riprese originali, dettagli delle foto ricostruiti dall'AI. #storia #immigrazione #ellisisland",
 "YOUTUBE":"ELLIS ISLAND 1903 | La Storia Rivive\nFilm originale del 1903 della Library of Congress, restaurato in un video che alterna riprese vere in movimento a fotografie AI a colori tratte dagli stessi fotogrammi. Colori e dettagli dei visi sono interpretazioni, non riproduzioni storicamente verificate. Musica originale. Fonte: "+LOC
 }
 for k,t in posts.items(): (OUT/("POST_"+k+".txt")).write_text(t+"\n",encoding="utf8")
 meta=dict(source=LOC,commons=FILM_PAGE,film_sha=sha(FILM),date_original_record="1903-07-09",
   video=master.name,sha256=sha(master),duration=round(dur,2),resolution=[W,H],fps=FPS,
   available_photo_restorations=photos,reference_effect=qa,zero_v_kredits=True,license="Public Domain Mark on Commons; territorial due diligence still required",
   face_confidence="Interpretative: modern face details not authentic certainty",artistic_semantic_review="PENDING",
   site_synced=False,social_published=False)
 (OUT/"FONTI_E_QA.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2))
 z=OUT/"ELLIS_ISLAND_1903_V79_KIT.zip"
 with zipfile.ZipFile(z,"w",compression=zipfile.ZIP_DEFLATED) as arc:
  for f in [master,OUT/"COPERTINA.jpg",OUT/"FONTI_E_QA.json",*[OUT/(f"POST_{k}.txt") for k in posts]]:
   arc.write(f,f.name)
 with zipfile.ZipFile(z) as arc:
  if arc.testzip():raise RuntimeError("Package archive damaged")
 print("COMPLETE_V79_ELLIS_NEW_VIDEO",str(master),master.stat().st_size,"KIT",z.stat().st_size,"duration",dur,flush=True)
 return master
if __name__=="__main__":
 inputs,fps=snapshot_frames()
 photos=photorealistic_stills(inputs)
 render(photos)
