#!/usr/bin/env python3
"""San Francisco 1906 V97: authentic 1906 source + free generative still-photo preflight.
NO Vidu POST, NO fake final. A bad free model MUST fail rather than publish DDColor.
"""
from pathlib import Path
import os
import imageio_ffmpeg
# Self-contained ffmpeg for minimal GitHub runners; do not depend on apt mirrors.
_bin=Path("/tmp/storia_sf1906_bin")
_bin.mkdir(parents=True,exist_ok=True)
_ff=_bin/"ffmpeg"
if not _ff.exists():_ff.symlink_to(imageio_ffmpeg.get_ffmpeg_exe())
os.environ["PATH"]=str(_bin)+os.pathsep+os.environ.get("PATH","")
from urllib.request import Request,urlopen
from urllib.parse import urlencode
import json,cv2,numpy as np,hashlib,zipfile,subprocess
from PIL import Image,ImageDraw
import importlib.util
R=Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location("historic_base",R/"src/storia_v80_new_york_venice.py")
base=importlib.util.module_from_spec(sp);sp.loader.exec_module(base)
OUT=Path("output/storia_sf_1906_v97");OUT.mkdir(parents=True,exist_ok=True)
META={"city":"SAN FRANCISCO","year":"1906",
"commons":"File:A Trip down market street (1906).webm",
"page":"https://commons.wikimedia.org/wiki/File:A_Trip_down_market_street_(1906).webm",
"description":"Miles Brothers authentic 1906 moving film of Market Street days before earthquake",
"shots":[
{"t":18.0,"center":720,"length":1.35,"tag":"busy Market Street moving cable car and horse carts"},
{"t":74.0,"center":720,"length":1.3,"tag":"authentic 1906 San Francisco traffic and pedestrians"},
{"t":161.0,"center":720,"length":1.4,"tag":"early automobiles, horse carts and moving cable cars in 1906"},
{"t":312.0,"center":720,"length":1.35,"tag":"Market Street 1906 moving crowd and urban life"},
{"t":411.0,"center":720,"length":1.15,"tag":"original historic moving San Francisco 1906 street view"}
]}
def write(path,doc):path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+"\n")
def main():
 src,info=base.acquire(META,OUT)
 records=base.grab_stills(src,META,OUT)
 dd,ss,model=base.load_dd()
 # Source-locked neural color is only the first step; never count as photo.
 photos=base.enhanced_ai_images(META,records[:4],OUT,dd,ss)
 if len(photos)!=4:raise RuntimeError("V97_FAIL_CLOSED_ALL_FOUR_REAL_IMAGE2IMAGE_REQUIRED_"+str(len(photos)))
 # Explicitly exclude hallucinations; correlation is NOT a substitute for a visual reviewer.
 board=Image.new("RGB",(5*215,2*405),(13,15,18));draw=ImageDraw.Draw(board)
 for j,r in enumerate(records):
  im=Image.open(OUT/r["source_frame"]).convert("RGB").resize((210,370))
  board.paste(im,(j*215,22))
  draw.text((j*215+4,5),f"ORIGINAL {j+1} / {r['source_time']}s",fill="white")
  if j<4:
   color=Image.open(OUT/photos[j]["photo_file"]).convert("RGB").resize((210,370))
   board.paste(color,(j*215,425))
   draw.text((j*215+4,407),f"AI I2I {j+1}",fill="white")
  else:
   draw.text((j*215+4,407),"VIDU NOT YET GENERATED",fill=(240,200,150))
 board.save(OUT/"SF1906_FIVE_SCENE_SOURCE_VS_PHOTO.jpg",quality=91)
 write(OUT/"V97_PREVIEW_STATUS.json",{"status":"FOUR_PHOTOS_GENERATED_BUT_NOT_ARTISTICALLY_APPROVED",
 "video_final":False,"vidu_requests":0,"source":info,"scene_records":records,
 "photos":photos,"next":"Real source-frame QA; then ONE authorized prepaid Vidu job; source-anchored final montage V96"})
 # 4 real source->real image-to-image cycles, last authentic original-only scene.
 # Deliberately QA PREVIEW (no Vidu); NEVER call this a final V96 4+1 video.
 w,h,fps=720,1280,30
 silent=OUT/"SF1906_V97_PREVIEW_SILENT.mp4"
 proc=subprocess.Popen(["ffmpeg","-nostdin","-y","-v","error","-f","rawvideo","-pix_fmt","bgr24",
 "-s",f"{w}x{h}","-r",str(fps),"-i","-","-c:v","libx264","-preset","veryfast","-crf","21",
 "-pix_fmt","yuv420p",str(silent)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 frames=0
 try:
  for i,r in enumerate(records):
   s=META["shots"][i]
   cap=cv2.VideoCapture(str(src));source_fps=cap.get(cv2.CAP_PROP_FPS)
   cap.set(cv2.CAP_PROP_POS_MSEC,(s["t"]-s["length"])*1000)
   count=max(5,round(s["length"]*source_fps))
   original=[]
   for _ in range(count):
    ok,f=cap.read()
    if not ok:break
    original.append(base.crop(f,s["center"]))
   cap.release()
   if len(original)<5:raise RuntimeError("ORIGINAL_MOTION_MISSING")
   n=round(s["length"]*fps)
   for k in range(n):
    f=original[min(len(original)-1,round(k*(len(original)-1)/max(1,n-1)))]
    f=cv2.cvtColor(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR)
    proc.stdin.write(f.tobytes());frames+=1
   if i==4:continue
   bw=cv2.imread(str(OUT/r["source_frame"]))
   bw=cv2.cvtColor(cv2.cvtColor(bw,cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR)
   photo=cv2.imread(str(OUT/photos[i]["photo_file"]))
   for k in range(11):
    a=(k+1)/11
    proc.stdin.write(cv2.addWeighted(bw,1-a,photo,a,0).tobytes());frames+=1
   for k in range(round(1.65*fps)):
    proc.stdin.write(photo.tobytes());frames+=1
 finally:
  proc.stdin.close()
  err=proc.stderr.read().decode(errors="replace")
  if proc.wait():raise RuntimeError("VIDEO_ENCODER_FAIL "+err[-600:])
 dur=frames/fps
 wav=base.create_audio(dur,[{"output_start_sec":0,"reveal_at_relative_sec":1.35},
 {"output_start_sec":3.35,"reveal_at_relative_sec":1.3},
 {"output_start_sec":6.7,"reveal_at_relative_sec":1.4},
 {"output_start_sec":10.1,"reveal_at_relative_sec":1.35},
 {"output_start_sec":13.5,"reveal_at_relative_sec":1.15}],OUT)
 final=OUT/"SF1906_V97_FOUR_RESTORATIONS_QA_PREVIEW_NOT_FINAL.mp4"
 base.cmd(["ffmpeg","-nostdin","-y","-v","error","-i",str(silent),"-i",str(wav),
 "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","128k",
 "-movflags","+faststart",str(final)],120)
 base.cmd(["ffmpeg","-v","error","-xerror","-i",str(final),"-f","null","-"],120)
 write(OUT/"V97_PREVIEW_STATUS.json",{"status":"QA_PREVIEW_ONLY_NOT_FINAL",
 "video_file":final.name,"video_sha256":base.sha(final),"duration_s":dur,
 "four_free_image_to_image_photos":4,"fifth_vidu":"NOT_GENERATED",
 "final_v96_approved":False,"source":info,"photos":photos,"vidu_requests":0,
 "rights_italy":"REVIEW_REQUIRED_BEFORE_PUBLICATION",
 "human_visual_review":"PENDING","why_not_final":"No Vidu generated and no human face fidelity sign-off"})
 with zipfile.ZipFile(OUT/"SF1906_V97_QA_PREVIEW_KIT.zip","w",zipfile.ZIP_DEFLATED) as z:
  for f in [final,OUT/"SF1906_FIVE_SCENE_SOURCE_VS_PHOTO.jpg",OUT/"V97_PREVIEW_STATUS.json"]:
   z.write(f,f.name)
 print("SF1906_QA_PREVIEW_REAL_MP4_READY",final,final.stat().st_size,"duration",dur,flush=True)
if __name__=="__main__":main()
