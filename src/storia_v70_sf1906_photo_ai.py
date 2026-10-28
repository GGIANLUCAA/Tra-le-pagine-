#!/usr/bin/env python3
"""Generate source-locked actual high-detail AI stills from public-domain 1906 San Francisco film.
Uses DDColor ONNX semantic color and free Finegrain Gradio image-to-image; 0 Vidu/paid tokens.
Real images are never represented as authentic 1906 color photographs.
"""
import importlib.util,hashlib,io,json,subprocess,os,zipfile
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageEnhance
from gradio_client import Client,handle_file
ROOT=Path(__file__).resolve().parents[1]
OUT=Path("output/storia_v70_sf1906");OUT.mkdir(parents=True,exist_ok=True)
SOURCE=OUT/"SAN_FRANCISCO_1906_HD_ORIGINALE.webm"
spec=importlib.util.spec_from_file_location("ddcolor_v60",ROOT/"src/storia_rivive_real_ai_v60.py")
dd=importlib.util.module_from_spec(spec);spec.loader.exec_module(dd)
sc=importlib.util.spec_from_file_location("source_v70",ROOT/"src/storia_v70_sf1906_source_scout.py")
src=importlib.util.module_from_spec(sc);sc.loader.exec_module(src)
SHOTS=[
 {"id":"01","name":"Il passante","sec":236.0,"x":810,"motion":1.75,"reveal":.36,"hold":3.6,"seed":71,
  "subject":"a real walking man in dark coat and period top hat near the camera; white stone facades beyond",
  "emphasis":"human eyes, natural skin, mustache/eyebrows, jacket buttons, wool fabric, the exact original face and pose"},
 {"id":"02","name":"L'automobile","sec":164.0,"x":625,"motion":1.60,"reveal":.32,"hold":3.25,"seed":107,
  "subject":"a very early 1906 motor car crossing Market Street with pedestrians and ornate period storefronts",
  "emphasis":"brass and steel wheel hardware, authentic rubber tires, brick and stone facades, original cars and people"},
 {"id":"03","name":"Il ciclista","sec":128.0,"x":630,"motion":1.65,"reveal":.34,"hold":3.30,"seed":149,
  "subject":"a real young male cyclist riding past an early automobile in 1906 Market Street, ornate buildings and passersby",
  "emphasis":"realistic 1906 bicycle frame and rubber tires, original man's face and suit, street facades, authentic natural colors"},
 {"id":"04","name":"Le persone al molo","sec":476.0,"x":725,"motion":1.60,"reveal":.34,"hold":3.45,"seed":181,
  "subject":"men and women walking and waiting in front of authentic San Francisco Ferry Building facade in 1906, period dresses and bowler hats",
  "emphasis":"natural faces where readable, black Victorian fabrics and hats, fabric seams, stone facade geometry and patterns"}
]
NEG="invented people, new cars, changed face, face swap, more people, extra limbs, changed body positions, unrealistic skin, plastic people, neon colors, modern clothes, modern street, fantasy objects, changed architecture, oversaturated red-magenta, fictional text, glowing skin, illegible fake shop lettering, oversharpened halos, cartoons, paintings"
PROMPT="High-resolution perfectly focused 1906 documentary color PHOTOGRAPH restored from exactly the supplied original source image. Preserve every existing subject's identity, number, expression, clothing, architecture and framing. Photographic dynamic range, natural believable period-appropriate colors and fine color texture; this is the SAME moment and camera position. Restore nuanced micro-details on " 

def sha(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()

def source_frame(capture,sec):
 capture.set(cv2.CAP_PROP_POS_MSEC,sec*1000)
 ok,frame=capture.read()
 if not ok or frame.shape[:2]!=(1072,1440):raise RuntimeError("Historical exact source frame missing")
 return frame

def ddcolor_input(frame,session):
 reduced=cv2.resize(frame,(720,576),interpolation=cv2.INTER_AREA)
 colors=dd.infer_ab(session,reduced)
 lab_l=dd.l_channel(frame)
 ab=cv2.resize(colors,(frame.shape[1],frame.shape[0]),interpolation=cv2.INTER_CUBIC)
 lab=np.dstack((lab_l,np.clip(ab*1.09,-110,110))).astype(np.float32)
 rgb=np.clip(cv2.cvtColor(lab,cv2.COLOR_LAB2RGB)*255,0,255).astype(np.uint8)
 return cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR)

def visual_geometry(a,b):
 def prep(im):
  g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
  g=cv2.resize(g,(72,128),interpolation=cv2.INTER_AREA)
  return cv2.GaussianBlur(g,(9,9),0).astype(np.float32)
 x=prep(a);y=prep(b)
 return float(np.corrcoef(x.ravel(),y.ravel())[0,1])

def produce():
 rights=src.original()
 if rights["license_marked"].lower()!="public domain":
  raise RuntimeError("Original source declared license changed")
 if rights["file_sha256"]!="c8b30802c0fbeb5f9ec3dc9af3e4f71ef627a863d4abba5550b63998cb46725a":
  raise RuntimeError("Not the exact genuine original film previously reviewed")
 session,model_meta=dd.download_model()
 # Reuse two REAL AI restorations already passed technical inspection, avoiding gratuitous quota spend.
 artifact_id="12853454516"
 token=os.environ.get("GH_TOKEN","")
 if not token:raise RuntimeError("Read token required to reuse already-generated images")
 artifact_url=f"https://api.github.com/repos/GGIANLUCAA/Tra-le-pagine-/actions/artifacts/{artifact_id}/zip"
 art=OUT/"V70_ORIGINAL_TWO_PHOTOS_REUSED.zip"
 subprocess.run(["curl","--fail","--location","--retry","3","--connect-timeout","20",
  "--max-time","150","-H","Authorization: Bearer "+token,
  "-H","Accept: application/vnd.github+json",artifact_url,"-o",str(art)],check=True,timeout=160)
 with zipfile.ZipFile(art) as z:
  if z.testzip():raise RuntimeError("Original AI photo artifact ZIP CRC failed")
  old_manifest=json.loads(z.read("RESTORATION_QA.json"))
  if old_manifest["original_video_sha256"]!=rights["file_sha256"] or len(old_manifest["results"])!=2:
   raise RuntimeError("Original AI photograph provenance mismatch")
  for r in old_manifest["results"]:
   for file in (r["photo"],r["source_frame"],r["ddcolor_image"]):
    (OUT/file).write_bytes(z.read(file))
   if sha(OUT/r["photo"])!=r["photo_sha256"] or sha(OUT/r["source_frame"])!=r["source_frame_sha256"]:
    raise RuntimeError("SHA of preserved real AI photo mismatch")
 print("REAL_AI_IMAGES_REUSED_WITHOUT_REGENERATION",2,flush=True)
 cap=cv2.VideoCapture(str(SOURCE))
 if not cap.isOpened():raise RuntimeError("Source cannot open")
 client=Client("finegrain/finegrain-image-enhancer",verbose=False)
 results=list(old_manifest['results'])
 try:
  for i,s in enumerate(SHOTS):
   if i<2:continue
   frame=source_frame(cap,s["sec"])
   crop=frame[:,s["x"]:s["x"]+603]
   if crop.shape[:2]!=(1072,603):raise RuntimeError("Invalid vertical native crop")
   original_file=OUT/f"FOTO_ORIGINALE_BN_{i+1:02d}.png"
   cv2.imwrite(str(original_file),crop)
   colored=ddcolor_input(frame,session)[:,s["x"]:s["x"]+603]
   colored=cv2.resize(colored,(540,960),interpolation=cv2.INTER_AREA)
   # Mild chroma moderation to avoid artificial pink overtones from old experiments.
   colored=cv2.cvtColor(np.asarray(ImageEnhance.Color(Image.fromarray(cv2.cvtColor(colored,cv2.COLOR_BGR2RGB))).enhance(.88)),cv2.COLOR_RGB2BGR)
   reference=OUT/f"BASE_COLORE_AI_{i+1:02d}.jpg"
   cv2.imwrite(str(reference),colored,[cv2.IMWRITE_JPEG_QUALITY,96])
   print("START_ACTUAL_GENERATIVE_AI",i+1,s["name"],flush=True)
   try:
    returned=client.predict(handle_file(str(reference)),
      PROMPT+s["emphasis"]+"; scene description: "+s["subject"],NEG,
      s["seed"],2,1.21,.97,6,112,144,.55,18,"DDIM",api_name="/process")
    generated=returned[1] if isinstance(returned,(list,tuple)) else returned
    if isinstance(generated,dict):generated=generated.get("path")
    if not generated or not Path(str(generated)).is_file():raise RuntimeError("Free photo model returned no file")
    photo=cv2.imread(str(generated))
    if photo is None:raise RuntimeError("Generated result cannot decode")
    photo=cv2.resize(photo,(1080,1920),interpolation=cv2.INTER_AREA)
    corr=visual_geometry(cv2.resize(crop,(1080,1920),interpolation=cv2.INTER_AREA),photo)
    sat=float(cv2.cvtColor(photo,cv2.COLOR_BGR2HSV)[:,:,1].mean())
    if corr<.73 or sat<12 or sat>176:raise RuntimeError(f"Generated photo fails approximate geometry/chroma threshold ({corr:.3f},{sat:.1f})")
    png=OUT/f"FOTO_FOTOGRAFICA_AI_{i+1:02d}.png"
    cv2.imwrite(str(png),photo,[cv2.IMWRITE_PNG_COMPRESSION,3])
    result={"scene":i+1,**s,"photo":png.name,"photo_sha256":sha(png),
      "source_frame":original_file.name,"source_frame_sha256":sha(original_file),
      "ddcolor_image":reference.name,"coarse_layout_corr":round(corr,3),
      "mean_saturation":round(sat,2),"actual_model":"finegrain/finegrain-image-enhancer",
      "generative_not_historically_exact":True}
    results.append(result)
    print("REAL_GENERATIVE_PHOTO_PASSED_TECHNICAL_GATE",i+1,png.stat().st_size,corr,flush=True)
   except Exception as e:
    print("GENERATIVE_RESTORATION_FAIL_OR_QUOTA",i+1,type(e).__name__,str(e)[:900],flush=True)
    break
 finally:
  cap.release()
 # Save all generated files even if last free model attempt fails.
 doc={"version":"V70","original_video_sha256":sha(SOURCE),"license_claim":"Public domain (Wikimedia Commons)",
      "source_page":src.PAGE,"original_raster":[1440,1072],"source_fps":24,
      "ddcolor":model_meta,"model":"Finegrain public Gradio Space, no payment or Vidu",
      "created_photographic_images":len(results),"requested":len(SHOTS),
      "results":results,"faces_and_details_historically_verifiable":False,
      "human_artistic_review":"REQUIRED before release","source_scan_Italy_clearance":"PENDING separate publication review",
      "no_paid_credits":True}
 (OUT/"RESTORATION_QA.json").write_text(json.dumps(doc,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 if results:
  board=Image.new("RGB",(len(results)*360,2*640),"#151719")
  d=ImageDraw.Draw(board)
  for i,r in enumerate(results):
   old=Image.open(OUT/r["source_frame"]).convert("RGB");new=Image.open(OUT/r["photo"]).convert("RGB")
   old=old.resize((350,620));new=new.resize((350,620))
   board.paste(old,(i*360+5,20));board.paste(new,(i*360+5,660))
   d.text((i*360+10,2),r["name"]+" · fonte",fill="white")
   d.text((i*360+10,642),r["name"]+" · fotografia AI",fill="white")
  board.save(OUT/"CONTATTI_PRIMA_DOPO_AI_V70.jpg",quality=89)
 if len(results)<3:raise RuntimeError("Insufficient actual photos for beautiful 20s film; not acceptable to fill with weak upscales.")
 print("AI_PHOTOS_READY_FOR_EDITORIAL_REVIEW",len(results),flush=True)
if __name__=="__main__":produce()
