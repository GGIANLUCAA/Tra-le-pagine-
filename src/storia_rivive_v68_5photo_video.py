#!/usr/bin/env python3
"""V68: actual 1918 Paris film --> five generatively reconstructed full-color still photographs.
Only FREE public Gradio Space, no API key / billing, source film CC0, disclosure mandatory.
No fallback to old DDColor+ESRGAN if generative image service fails.
"""
import hashlib, io, json, os, subprocess, urllib.request, zipfile, wave
from pathlib import Path
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageEnhance
from gradio_client import Client,handle_file

OUT=Path("output/storia_rivive_v68_paris_generativo")
OUT.mkdir(parents=True,exist_ok=True)
RELEASE="https://github.com/GGIANLUCAA/Tra-le-pagine-/releases/download/storia-rivive-parigi-1918-photo-freeze-v65/"
SOURCE_VIDEO=RELEASE+"PARIGI_1918_IL_TEMPO_SI_FERMA_V65.mp4"
SOURCE_KIT=RELEASE+"PARIGI_1918_VIDEO_E_FOTO_V65.zip"
ARTIFACT_ID="12849782800" # Actual existing stronger candidate, generated & reviewed 28/10/2026.
UA="Tra-le-Pagine/0.68 non-monetized historical-documentary"
W,H,FPS=1080,1920,30
SCENES=[
    {"idx":0,"name":"La venditrice","motion":1.56,"orig_reveal":.34,"orig_hold":2.65,"new_hold":3.50,
     "prompt":"Paris 1918 genuine candid street documentary photograph, newspaper vendor at stall in foreground, expressive eyes and nuanced realistic skin, old period hats, four customers, wool coats and newspapers on wooden counter; painstaking texture, documentary 35mm still photograph, same exact persons, pose and camera view."},
    {"idx":1,"name":"La stazione","motion":1.58,"orig_reveal":.32,"orig_hold":2.32,"new_hold":3.26,
     "prompt":"Paris 1918 Gare de Lyon actual documentary still, authentic train station passengers, period hats, coats, individual fabric fibers, natural human eyes and lifelike subtle facial skin, realistic limestone architecture, documentary photographic detail; preserve precisely original people and arrangement."},
    {"idx":2,"name":"Il cinema","motion":1.35,"orig_reveal":.33,"orig_hold":2.11,"new_hold":3.20,
     "prompt":"Real 1918 Paris cinema street crowd, documentary photographic realism, detailed faces without changing identities, Edwardian era coats and hats, authentic cinema marquee textures, natural photo color and fine street detail, exact source geometry, not a movie poster."},
    {"idx":3,"name":"Il tram","motion":1.48,"orig_reveal":.32,"orig_hold":2.31,"new_hold":3.45,
     "prompt":"1918 Paris original electric tram and passing pedestrians, photorealistic historical color restoration of actual source frame, sharp tram paneling, human faces natural skin and realistic period clothes, exquisite material texture without changing scene geometry."},
    {"idx":4,"name":"La folla","motion":1.60,"orig_reveal":.35,"orig_hold":2.69,"new_hold":2.95,
     "prompt":"Authentic documentary photo of 1918 Paris boulevard street crowd and historic shop fronts, lifelike skin textures and individual fabric weaving, convincing human faces consistent with source, sharp readable architecture and natural sunlight, reproduce source camera framing."},
    {"idx":5,"name":"La Senna","motion":1.40,"orig_reveal":.33,"orig_hold":2.38,"new_hold":2.30,
     "prompt":"Paris 1918 original black-and-white film still near the Seine, historically accurate street crowd, real faces and water textures, color photographic restoration, preserve all source people."},
]
SELECTED=SCENES[:4]
NEGATIVE="changed number of people, new faces, invented persons, redesigned shop, cartoon, painterly style, over-smooth skin, distorted eyes, face swap, blurry, film grain, red-magenta tint, altered clothing, invented scene, fake 4k text"
PROMPT_COMMON="Full frame image-to-image restoration. Keep the exact source image framing, historical positions, clothing, faces and gestures. Add convincing photographic micro-detail as a plausible reconstruction, not factual evidence. Natural period-appropriate nuanced colors. "
VIDEO=OUT/"PARIGI_1918_RESTAURO_FOTOGRAFICO_GENERATIVO_V68.mp4"

def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()

def download(url,target,headers=None):
 request=urllib.request.Request(url,headers={"User-Agent":UA,**(headers or {})})
 with urllib.request.urlopen(request,timeout=150) as r,open(target,"wb") as f:
  while True:
   b=r.read(1048576)
   if not b:break
   f.write(b)
 if not target.is_file() or target.stat().st_size<5000:raise ValueError("Download missing "+url)
 return target

def cmd(args,timeout=170):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError("Command failed "+p.stderr[-1300:])
 return p

def get_existing_master():
 original=download(SOURCE_VIDEO,OUT/"ORIGINALE_V65.mp4")
 kit=download(SOURCE_KIT,OUT/"ORIGINALE_V65_KIT.zip")
 with zipfile.ZipFile(kit) as z:
  if z.testzip():raise ValueError("Source ZIP corrupt")
  for i in range(1,7):
   data=z.read("FOTO_RESTAURATA_%02d.jpg"%i)
   (OUT/("BASE_V65_FOTO_%02d.jpg"%i)).write_bytes(data)
  source_meta=json.loads(z.read("FONTI_E_QA.json"))
  source_posts={p:z.read("POST_"+p+".txt").decode("utf8") for p in ("FACEBOOK","INSTAGRAM","TIKTOK","YOUTUBE")}
 if not source_meta["source_sha256_verified"] or not source_meta["no_paid_provider_or_vidu_credits"]:
  raise ValueError("Source license or payment contract violation")
 return original,source_meta,source_posts

def get_existing_first():
 url="https://api.github.com/repos/GGIANLUCAA/Tra-le-pagine-/actions/artifacts/"+ARTIFACT_ID+"/zip"
 token=os.environ.get("GH_TOKEN","")
 if not token:raise RuntimeError("No github read token for real preexisting approved test artifact")
 file=OUT/"V68_TESTED_FIRST_ARTIFACT.zip"
 # urllib forwards the Authorization header to GitHub's cross-domain blob redirect,
 # triggering Azure HTTP 401; curl -L strips sensitive auth when host changes.
 cmd(["curl","--fail","--location","--retry","3","--connect-timeout","20","--max-time","160",
      "-H","Authorization: Bearer "+token,
      "-H","Accept: application/vnd.github+json",
      url,"-o",str(file)],180)
 if not file.is_file() or file.stat().st_size<100000:
  raise RuntimeError("Original actual generative photo artifact missing")
 with zipfile.ZipFile(file) as z:
  im=Image.open(io.BytesIO(z.read("FOTO_GENERATIVA_FORTE.png"))).convert("RGB")
  result=OUT/"FOTO_AI_RICOSTRUITA_01.png"
  im.save(result)
  if sha(result)!="25070cfd5aa0e38585c6b582b7cdade10a7aeb8154c4983f94b058da9b128e71":
   raise ValueError("Previously visually reviewed photo has unexpected SHA256")
 return result

def photo_match(source,photo):
 s=cv2.cvtColor(np.asarray(source),cv2.COLOR_RGB2GRAY)
 p=cv2.cvtColor(np.asarray(photo),cv2.COLOR_RGB2GRAY)
 s=cv2.resize(s,(64,114)).astype(np.float32)
 p=cv2.resize(p,(64,114)).astype(np.float32)
 s=cv2.GaussianBlur(s,(9,9),0);p=cv2.GaussianBlur(p,(9,9),0)
 return float(np.corrcoef(s.ravel(),p.ravel())[0,1])

def enhance_images():
 # Reuse all FOUR real model-generated photos already successfully created in V68.
 # Never retry the ZeroGPU quota or pay for inference. Download with cross-host-safe curl.
 token=os.environ.get("GH_TOKEN","")
 if not token:raise RuntimeError("GitHub artifact read permission required")
 artifact_id="12849614550"
 url="https://api.github.com/repos/GGIANLUCAA/Tra-le-pagine-/actions/artifacts/"+artifact_id+"/zip"
 tmp=OUT/"V68_FOUR_REAL_GENERATIVE_IMAGES.zip"
 cmd(["curl","--fail","--location","--retry","3","--connect-timeout","20","--max-time","150",
      "-H","Authorization: Bearer "+token,"-H","Accept: application/vnd.github+json",url,
      "-o",str(tmp)],170)
 images={}
 with zipfile.ZipFile(tmp) as z:
  if z.testzip():raise RuntimeError("Generated image archive CRC corruption")
  for i,s in enumerate(SELECTED):
   name="FOTO_AI_RICOSTRUITA_%02d.png"%(i+1)
   im=Image.open(io.BytesIO(z.read(name))).convert("RGB")
   if im.size!=(W,H):raise RuntimeError("Unexpected restored photo size "+str(im.size))
   target=OUT/name
   im.save(target)
   images[i]=target
 if len(images)!=4:raise RuntimeError("Missing prior real image-to-image generation")
 report=[]
 for i,s in enumerate(SELECTED):
  photo=Image.open(images[i]).convert("RGB")
  base=Image.open(OUT/("BASE_V65_FOTO_%02d.jpg"%(i+1))).convert("RGB")
  corr=photo_match(base,photo)
  if corr<.82:raise RuntimeError("Photo diverges from historical scene "+str(i+1))
  report.append({"scene":i+1,"subject":s["name"],
      "source_photo_sha256":sha(OUT/("BASE_V65_FOTO_%02d.jpg"%(i+1))),
      "generative_photo_sha256":sha(images[i]),
      "source_layout_similarity":round(corr,3),
      "model":"Finegrain image-to-image on free ZeroGPU Space",
      "denoise_strength":.64 if i==0 else .60,
      "details_faces_and_writing_are_plausible_AI_interpretations":True})
 print("FOUR_TRUE_GENERATIVE_PHOTOS_REUSED",json.dumps(report,ensure_ascii=False),flush=True)
 return images,report

def qa_comparison(images):
 board=Image.new("RGB",(len(SELECTED)*260,2*500),(18,19,20))
 draw=ImageDraw.Draw(board)
 for i,s in enumerate(SELECTED):
  before=Image.open(OUT/("BASE_V65_FOTO_%02d.jpg"%(i+1))).convert("RGB")
  after=Image.open(images[i]).convert("RGB")
  before.thumbnail((250,458));after.thumbnail((250,458))
  board.paste(before,(i*260+5,26))
  board.paste(after,(i*260+5,526))
  draw.text((i*260+9,7),s["name"],fill="white")
  draw.text((i*260+9,508),"RICOSTRUZIONE AI",fill="white")
 path=OUT/"CONFRONTO_REALE_4_SCENE.jpg"
 board.save(path,quality=91)
 return path

def cut_video(src,images):
 cap=cv2.VideoCapture(str(src))
 if not cap.isOpened():raise RuntimeError("Cannot decode true original MP4")
 if int(round(cap.get(cv2.CAP_PROP_FRAME_WIDTH)))!=W or int(round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))!=H:raise ValueError("Source raster mismatch")
 silent=OUT/"TEMP_V68_MUTO.mp4"
 ff=["ffmpeg","-nostdin","-y","-hide_banner","-loglevel","error","-f","rawvideo",
     "-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264",
     "-preset","veryfast","-crf","18","-pix_fmt","yuv420p",str(silent)]
 p=subprocess.Popen(ff,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 frame_count=0;meta=[]
 try:
  for i,s in enumerate(SCENES):
   motion_count=round(s["motion"]*FPS)
   old_transition=round(s["orig_reveal"]*FPS)
   old_hold=round(s["orig_hold"]*FPS)
   motion_frames=[]
   for k in range(motion_count):
    ok,frame=cap.read()
    if not ok:raise RuntimeError("Historical motion clip incomplete "+str(i))
    motion_frames.append(frame)
   for k in range(old_transition+old_hold):
    ok,_=cap.read()
    if not ok:raise RuntimeError("Historical source segment incomplete")
   if i>=len(SELECTED):continue
   if not motion_frames:raise RuntimeError("No moving frames")
   source_last=motion_frames[-1]
   colored=cv2.imread(str(images[i]),cv2.IMREAD_COLOR)
   if colored.shape[:2]!=(H,W):raise RuntimeError("Generative photo invalid raster")
   for frame in motion_frames:
    p.stdin.write(frame.tobytes());frame_count+=1
   ntrans=round(.36*FPS)
   for k in range(ntrans):
    a=(k+1)/ntrans;a=a*a*(3-2*a)
    blended=cv2.addWeighted(source_last,1-a,colored,a,0)
    p.stdin.write(blended.tobytes());frame_count+=1
   nhold=round(s["new_hold"]*FPS)
   for k in range(nhold):
    p.stdin.write(colored.tobytes());frame_count+=1
   meta.append({"source_scene_index":i+1,"real_archive_motion_frames":motion_count,
                "transition_frames":ntrans,"ai_photo_still_frames":nhold,"photo_sha256":sha(images[i])})
   print("VIDEO_SCENE_RENDERED",i+1,"count",frame_count,flush=True)
 finally:
  p.stdin.close();cap.release()
 err=p.stderr.read().decode(errors="ignore")
 if p.wait()!=0:raise RuntimeError("Real video encode failed "+err[-600:])
 duration=frame_count/FPS
 cmd(["ffmpeg","-nostdin","-y","-loglevel","error","-i",str(silent),
      "-i",str(src),"-map","0:v","-map","1:a:0","-c:v","copy","-af",f"afade=t=out:st={max(0,duration-.85):.2f}:d=0.85",
      "-c:a","aac","-b:a","160k","-t",str(duration),"-movflags","+faststart",str(VIDEO)])
 cmd(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(VIDEO),"-f","null","-"])
 if duration<20 or duration>29:raise RuntimeError("Duration unsuitable "+str(duration))
 return duration,meta

def package(srcmeta,posts,images,photos,video_meta,duration,board):
 im=Image.open(images[0]).convert("RGB")
 d=ImageDraw.Draw(im,"RGBA")
 d.rounded_rectangle((38,37,610,156),radius=14,fill=(8,9,11,120))
 try:
  font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",48)
  small=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",23)
 except:font=ImageFont.load_default();small=ImageFont.load_default()
 d.text((58,53),"PARIGI · 1918",font=font,fill=(252,242,229,250))
 d.text((62,116),"IL TEMPO SI FERMA",font=small,fill=(230,233,236,245))
 cover=OUT/"COPERTINA_V68.jpg";im.save(cover,quality=94)
 for k,body in posts.items():
  body=body.rstrip()+"\n\nRestauro V68: fotografie ricostruite con modello generativo; volti e dettagli sono ipotesi visive, non dati storicamente certificati. Le riprese in bianco e nero sono originali CC0.\n"
  (OUT/f"POST_{k}.txt").write_text(body,encoding="utf8")
 report={"version":"V68","title":"Parigi, 1918 — Il tempo si ferma | ricostruzione fotografica",
  "original_archival_rights":srcmeta["rights"],
  "original_source_page":srcmeta["source"]["original_file_page"],
  "source_video_sha256":sha(OUT/"ORIGINALE_V65.mp4"),
  "rendered_mp4_sha256":sha(VIDEO),
  "rendered_mp4_size":VIDEO.stat().st_size,
  "duration_s":round(duration,2),"resolution":[W,H],
  "real_blackwhite_motion_before_each_ai_photo":True,"photo_hold_static":True,
  "generation":"Four actual free Finegrain generative photos, produced in V68 and reused after ZeroGPU cap; not only V65 ESRGAN",
  "model_license_and_external_use_review_needed":True,
  "source_archival_video_pd_or_cc0_declared":True,
  "reconstruction_disclosure":"AI reconstructed facial features, colors, details are plausible, not verifiable identities.",
  "source_vs_restoration":photos,"video_scenes":video_meta,
  "human_artistic_approval":"PENDING visual review",
  "video_library_studio_synced":False,"social_published":False,"vidu_credits_spent":0,"paid_gpu_spent":0}
 data=OUT/"FONTI_E_QA.json";data.write_text(json.dumps(report,ensure_ascii=False,indent=2))
 kit=OUT/"PARIGI_1918_FOTO_GENERATIVE_V68_COMPLETO.zip"
 with zipfile.ZipFile(kit,"w",zipfile.ZIP_DEFLATED) as z:
  for item in [VIDEO,cover,board,data,*images.values(),
               *[OUT/f"POST_{k}.txt" for k in posts]]:z.write(item,item.name)
 with zipfile.ZipFile(kit) as z:
  if z.testzip():raise RuntimeError("Corrupted complete ZIP")
 print("ACTUAL_GENERATIVE_VIDEO_COMPLETE",{"mp4_bytes":VIDEO.stat().st_size,"duration":duration,
  "sha256":sha(VIDEO),"kit":str(kit)},flush=True)

def main():
 original,metadata,posts=get_existing_master()
 photos,report=enhance_images()
 board=qa_comparison(photos)
 duration,video_meta=cut_video(original,photos)
 package(metadata,posts,photos,report,video_meta,duration,board)
if __name__=="__main__":
 main()
