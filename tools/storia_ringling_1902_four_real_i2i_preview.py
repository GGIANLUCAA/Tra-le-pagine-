#!/usr/bin/env python3
"""Ringling Brothers Parade, 1902: four genuine DDColor+Finegrain I2I photographic
restorations, plus exact fifth B/W anchor for 1 video animation.
Fail closed if <4 real Finegrain reconstructions or wrong source. No Vidu POST.
This produces a real playable 4-photo + archival-only proof MP4, correctly NOT final.
"""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys,zipfile
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=Path("output/storia_ringling_1902_v1");OUT.mkdir(parents=True,exist_ok=True)
SRC=OUT/"RINGLING_1902_AUTHENTIC_FILM.webm"
EXPECTED_SHA="bdb3dcce3b7feacc017853ba42c0fdcb66eff357ded3f3853380df0860f8b69e"
PAGE="https://commons.wikimedia.org/wiki/File:Ringling_Brothers_Parade_Film_(1902).webm"
# One distinct group at each time, not five crops of a repeated parade carriage.
SCENES=[
 {"t":20.0,"center":474,"length":1.3,"tag":"grand ornate moving circus carriage, authentic decorated wagon, large wood wheels, horses and period street crowd"},
 {"t":80.0,"center":474,"length":1.25,"tag":"mounted riders and live horses of the 1902 Ringling circus parade marching past ornate stone buildings"},
 {"t":132.0,"center":474,"length":1.35,"tag":"two genuine Asian elephants and their Mahout riders walking in the 1902 circus parade, anatomically correct elephant trunks and legs"},
 {"t":176.0,"center":474,"length":1.3,"tag":"Victorian woman with a period bicycle at curb, authentic passing parade carriage and pedestrians in 1902"},
 {"t":212.0,"center":474,"length":1.15,"tag":"mounted uniformed circus parade performer on a white horse with period saddle and exact crowd"}
]
def sha(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for z in iter(lambda:f.read(1<<20),b""):h.update(z)
 return h.hexdigest()
def run(args,timeout=170):
 p=subprocess.run(args,timeout=timeout,text=True,capture_output=True)
 if p.returncode:raise RuntimeError("SUBPROCESS_FAILED "+str(args[:6])+" "+p.stderr[-700:])
 return p.stdout
def main():
 if not SRC.is_file() or sha(SRC)!=EXPECTED_SHA:raise RuntimeError("EXACT_RINGLING_1902_ORIGINAL_FILM_MISSING_OR_CHANGED")
 spec=importlib.util.spec_from_file_location("v80_source_photo_pipeline",ROOT/"src/storia_v80_new_york_venice.py")
 v80=importlib.util.module_from_spec(spec);spec.loader.exec_module(v80)
 meta={"city":"RINGLING CIRCUS","year":"1902","page":PAGE,"shots":SCENES}
 records=v80.grab_stills(SRC,meta,OUT)
 if len(records)!=5:raise RuntimeError("FIVE_DIFFERENT_TRUE_SHOT_RECORDS_NOT_VERIFIED")
 # Fifth image is NEVER a Finegrain photo until the real provider generates one.
 photo_records=[]
 prior=OUT/"PHOTO_QA.json"
 if prior.exists():
  try:
   old=json.loads(prior.read_text())
   for x in old:
    i=int(x["scene"])
    if i in (1,2,3,4) and x.get("sha256")==records[i-1]["sha256"] and
       x.get("model")=="DDColor+free Finegrain image enhancer" and
       x.get("photo_file")==f"PHOTO_AI_{i:02d}.png" and
       (OUT/x["photo_file"]).is_file() and sha(OUT/x["photo_file"])==x["photo_sha256"]:
     photo_records.append(x)
   print("REUSED_TRUE_FINEGRAIN_IMAGES",sorted(x["scene"] for x in photo_records),flush=True)
  except Exception as exc:
   print("IGNORED_INVALID_PARTIAL_I2I_CACHE",type(exc).__name__,flush=True)
 remaining=[j for j in (1,2,3,4) if j not in {x["scene"] for x in photo_records}]
 if remaining:
  # NO DDColor fallback: the rejected elephant image must be made generatively,
  # then graded to historical neutral saturation rather than saturated cartoon.
  from gradio_client import Client,handle_file
  import inspect,os
  kw={"verbose":False};api_params=inspect.signature(Client).parameters
  token=os.environ.get("HF_TOKEN")
  if token:
   if "hf_token" in api_params:kw["hf_token"]=token
   elif "token" in api_params:kw["token"]=token
  client=Client("finegrain/finegrain-image-enhancer",**kw)
  for i in remaining:
   raw=OUT/f"FRAME_{i:02d}_SOURCE.png"
   conditioning=OUT/f"PHOTO_COLOR_BASE_{i:02d}.jpg"
   if not conditioning.is_file():
    dd,model,_=v80.load_dd()
    p=v80.natural_color(dd,model,raw)
    cv2.imwrite(str(conditioning),cv2.resize(p,(576,1024)),[cv2.IMWRITE_JPEG_QUALITY,96])
   prompt=("Photorealistic contemporary photographic restoration of the EXACT 1902 original circus parade film frame. "
    +SCENES[i-1]["tag"]+". Maintain precisely the REAL elephant, horse, riders, wheels, trunks, tusks, "
    "limb anatomies, pedestrians, clothes and stone buildings that visibly exist. Preserve all positions, "
    "geometry, camera view, and source composition. Natural historic documentary daylight; realistic "
    "neutral skin, brown leather, soft grey elephant skin, realistic wool and timber, vivid yet restrained colors. "
    "NO invented people, animals or objects, no hallucinated details, no faces on architecture.")
   neg=("cartoon, CGI, extra animals, trunk morph, split heads, duplicated legs, painted texture, "
    "saturated neon red, orange oversaturation, modern clothes, extra faces, changed background, "
    "person becoming horse, limbs fused, text, watermarks, artificial skin")
   print("SINGLE_MISSING_REAL_FINEGRAIN_IMAGE",i,flush=True)
   result=client.predict(handle_file(str(conditioning)),prompt,neg,1902+i,2,1.08,.96,6,112,144,.38,18,"DDIM",api_name="/process")
   val=result[1] if isinstance(result,(list,tuple)) and len(result)>1 else result
   if isinstance(val,dict):val=val.get("path")
   if not val or not Path(str(val)).is_file():raise RuntimeError("FAILED_NEW_FINEGRAIN_PROVIDER_IMAGE_"+str(i))
   im=cv2.imread(str(val))
   if im is None:raise RuntimeError("REAL_FINEGRAIN_IMAGE_UNREADABLE")
   im=cv2.resize(im,(720,1280))
   saturation=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
   avg=float(saturation[:,:,1].mean())
   if avg>105:
    saturation[:,:,1]=np.uint8(np.clip(saturation[:,:,1].astype("float32")*(105/avg),0,220))
    im=cv2.cvtColor(saturation,cv2.COLOR_HSV2BGR)
   geom=v80.similarity(cv2.imread(str(raw)),im)
   sat=float(cv2.cvtColor(im,cv2.COLOR_BGR2HSV)[:,:,1].mean())
   if geom<.75 or sat<12 or sat>135:raise RuntimeError("REAL_FINEGRAIN_PHOTO_FAILS_SOURCE_OR_NATURAL_COLOR_QA_"+str((i,round(geom,3),round(sat,1))))
   target=OUT/f"PHOTO_AI_{i:02d}.png"
   cv2.imwrite(str(target),im,[cv2.IMWRITE_PNG_COMPRESSION,2])
   photo_records.append({**records[i-1],"photo_file":target.name,"photo_sha256":sha(target),
     "geom_corr":round(geom,3),"sat":round(sat,1),
     "model":"DDColor+free Finegrain image enhancer",
     "source_locked_semantic_review":"PENDING_HUMAN"})
 photo_records=sorted(photo_records,key=lambda x:x["scene"])
 prior.write_text(json.dumps(photo_records,ensure_ascii=False,indent=2)+"\n")
 if len(photo_records)!=4 or [x["scene"] for x in photo_records]!=[1,2,3,4]:
  raise RuntimeError("V99_NOT_ENOUGH_FOUR_VERIFIED_GENERATIVE_PHOTO_RESTORATIONS_"+str(len(photo_records)))
 for j,(photo,source) in enumerate(zip(photo_records,records[:4]),1):
  if photo["scene"]!=j or photo["sha256"]!=source["sha256"] or photo.get("geom_corr",0)<.69 or photo.get("model")!="DDColor+free Finegrain image enhancer":raise RuntimeError("RESTORED_SOURCE_OR_MODEL_WRONG_"+str(j))
  if sha(OUT/photo["photo_file"])!=photo["photo_sha256"]:raise RuntimeError("CHANGED_REAL_PHOTO_"+str(j))
 # Four authentic film shots B/W->exact frozen frame->real I2I colored photo.
 # Final shot: authentic B/W moving video only; not advertised as Vidu.
 n_total=0;fps=30;W,H=720,1280
 TMP=OUT/"V1_VIDEO_SILENT.mp4"
 enc=subprocess.Popen(["ffmpeg","-nostdin","-y","-v","error","-f","rawvideo","-pix_fmt","bgr24","-s","720x1280",
  "-r","30","-i","-","-an","-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p",
  "-movflags","+faststart",str(TMP)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 chapter=[]
 try:
  for i,record in enumerate(records):
   shot=SCENES[i];cap=cv2.VideoCapture(str(SRC));sfps=cap.get(cv2.CAP_PROP_FPS)
   origin=cv2.imread(str(OUT/record["source_frame"]))
   if origin is None:raise RuntimeError("SOURCE_FRAME_MISSING")
   # source exact last frame, all crops constant throughout shot.
   cap.set(cv2.CAP_PROP_POS_MSEC,(shot["t"]-shot["length"])*1000)
   raw=[]
   for k in range(round(shot["length"]*sfps)+1):
    ok,f=cap.read()
    if not ok:break
    raw.append(v80.crop(f,shot["center"]))
   cap.release()
   if len(raw)<24:raise RuntimeError("NO_REAL_ORIGINAL_MOVING_FILM_"+str(i+1))
   start=n_total/fps
   count=round(shot["length"]*fps)
   for k in range(count):
    frame=raw[min(len(raw)-1,round((k/max(1,count-1))*(len(raw)-1)))]
    if k>=count-3:frame=origin
    gray=cv2.cvtColor(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR)
    enc.stdin.write(gray.tobytes());n_total+=1
   if i==4:
    chapter.append({"scene":i+1,"source_t_s":shot["t"],"output_start_s":round(start,3),
       "duration_s":round(n_total/fps-start,3),"kind":"true_archival_motion_for_future_source_locked_vidu"})
    continue
   color=cv2.imread(str(OUT/photo_records[i]["photo_file"]))
   if color is None or color.shape[:2]!=(1280,720):raise RuntimeError("I2I_COLOR_PHOTO_WRONG_GEOMETRY")
   # source-locked photo reveal, no image-wide color optical flow.
   for k in range(10):
    blend=(k+1)/10;blend=blend*blend*(3-2*blend)
    enc.stdin.write(cv2.addWeighted(cv2.cvtColor(cv2.cvtColor(origin,cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR),
                   1-blend,color,blend,0).tobytes());n_total+=1
   for k in range(round(1.86*fps)):
    enc.stdin.write(color.tobytes());n_total+=1
   chapter.append({"scene":i+1,"source_t_s":shot["t"],"output_start_s":round(start,3),
     "duration_s":round(n_total/fps-start,3),"kind":"BW_FILM_FREEZE_REAL_I2I_PHOTOGRAPH",
     "photo_sha256":photo_records[i]["photo_sha256"],"source_frame_sha256":record["sha256"],
     "photo_model":photo_records[i]["model"]})
   print("V1_TRUE_GENERATIVE_PHOTO_REVEALED",i+1,round(n_total/fps,3),flush=True)
 finally:
  enc.stdin.close();err=enc.stderr.read().decode(errors="replace")
  if enc.wait()!=0:raise RuntimeError("VIDEO_ENCODE_FAILED "+err[-900:])
 # Baked original score, single piece and no voice or watermarks.
 duration=n_total/fps
 mus=v80.create_audio(duration,[{"output_start_sec":x["output_start_s"],
   "reveal_at_relative_sec":min(x["duration_s"]-.1,1.4)} for x in chapter],OUT)
 FINAL=OUT/"RINGLING_CIRCUS_1902_FOUR_FINEGRAIN_RESTORATIONS_QA_PREVIEW.mp4"
 run(["ffmpeg","-nostdin","-y","-v","error","-i",str(TMP),"-i",str(mus),
  "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","160k",
  "-shortest","-movflags","+faststart",str(FINAL)],120)
 run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(FINAL),"-f","null","-"],140)
 contact=Image.new("RGB",(5*190,2*350),(12,16,20));draw=ImageDraw.Draw(contact)
 for j,rec in enumerate(records):
  s=cv2.imread(str(OUT/rec["source_frame"]))
  if s is None:raise RuntimeError("MISSING_SOURCE_CONTACT_IMAGE")
  im=Image.fromarray(cv2.cvtColor(s,cv2.COLOR_BGR2RGB)).resize((187,333))
  contact.paste(im,(j*190,17))
  if j<4:
   p=Image.open(OUT/photo_records[j]["photo_file"]).convert("RGB").resize((187,333))
   contact.paste(p,(j*190,367))
  draw.text((j*190+4,3),f"{int(SCENES[j]['t'])} s",fill=(250,244,223))
 draw.text((4*190+5,360),"VIDU NOT YET",fill=(250,200,160))
 contact.save(OUT/"RINGLING_1902_FIVE_SOURCE_VS_REAL_I2I_CONTACT.jpg",quality=91)
 cover=Image.open(OUT/photo_records[2]["photo_file"]).convert("RGB")
 cover.save(OUT/"COVER_CIRCUS_1902.jpg",quality=94)
 posts={
  "FACEBOOK":"1902 · RINGLING BROTHERS CIRCUS PARADE. Una parata vera di oltre un secolo fa: carri, cavalli, elefanti e persone nelle strade americane. Il film è autentico; i colori e i dettagli delle fotografie sono ricostruiti digitalmente con IA. Fonte: Wikimedia Commons. Anteprima in lavorazione.",
  "INSTAGRAM":"RINGLING CIRCUS · 1902. Horses, elephants and extravagant parade floats frozen from original movie footage and restored as contemporary-looking photographs. AI color reconstructions are interpretive, not original color film. #HistoryReels #Circus1902",
  "TIKTOK":"1902: una parata incredibile torna a vivere. Filmati B/N reali, fermo immagine autentico, ricostruzione fotografica AI. I colori non sono originali. #LaStoriaRivive",
  "YOUTUBE":"RINGLING BROTHERS CIRCUS PARADE · 1902\n\nOriginal film: https://commons.wikimedia.org/wiki/File:Ringling_Brothers_Parade_Film_(1902).webm\nFour source-locked image-to-image photo restorations, fifth original black and white moving shot awaiting Vidu. Review version, NOT the definitive 4+1 video. Rights in Italy and artistic QA pending."
 }
 for p,t in posts.items(): (OUT/f"POST_{p}.txt").write_text(t+"\n",encoding="utf8")
 report={"title":"RINGLING CIRCUS · 1902","status":"FOUR_REAL_FINEGRAIN_PHOTOGRAPHS_QA_PREVIEW_NOT_4PLUS1_FINAL",
   "source_page":PAGE,"source_film_sha256":sha(SRC),"true_photo_count":4,
   "new_vidu_video_count":0,"new_paid_provider_posts":0,"credits_spent":0,
   "last_original_source_frame_t":212.0,"chapters":chapter,
   "geometry_fidelity_review":"PENDING_HUMAN",
   "copyright_italy":"PENDING_REVIEW",
   "full_V98_benchmark_artistic_approved":False,
   "duration_s":duration,"video_sha256":sha(FINAL),"video_size":FINAL.stat().st_size,
   "resolution":[720,1280],"fps":30,"audio_present":True}
 (OUT/"RINGLING_V1_PREVIEW_QA.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 pack=OUT/"RINGLING_CIRCUS_1902_QA_PREVIEW_ANDROID.zip"
 with zipfile.ZipFile(pack,"w",zipfile.ZIP_DEFLATED) as z:
  for f in [FINAL,OUT/"RINGLING_1902_FIVE_SOURCE_VS_REAL_I2I_CONTACT.jpg",OUT/"COVER_CIRCUS_1902.jpg",
            OUT/"RINGLING_V1_PREVIEW_QA.json",*[OUT/f"POST_{x}.txt" for x in posts]]:
   z.write(f,f.name)
 with zipfile.ZipFile(pack) as z:
  if z.testzip():raise RuntimeError("ANDROID_ZIP_CRC_BAD")
 print("REAL_NEW_RINGLING_1902_VIDEO_REVIEW_CREATED",FINAL.name,"bytes",FINAL.stat().st_size,"seconds",duration,
       "four_actual_I2I_photographs",len(photo_records),"new_vidu_credits",0,flush=True)
if __name__=="__main__":main()
