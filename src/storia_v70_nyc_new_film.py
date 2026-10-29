#!/usr/bin/env python3
"""V70 actual NEW film: NYC 1903 source; never fabricate or silently substitute Paris.
Only public PD/CC0 candidate. Strict actual photo & geometry QA. Fail closed.
"""
import hashlib,io,json,os,subprocess,urllib.request
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
from gradio_client import Client,handle_file
O=Path("output/storia_v70_nyc1903");O.mkdir(parents=True,exist_ok=True)
URL="https://commons.wikimedia.org/wiki/Special:Redirect/file/Scenes_in_New_York_City%2C_1903.webm"
W,H,FPS=1080,1920,30
def run(cmd,timeout=160):
 p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError(str(cmd[:3])+" "+p.stderr[-1400:])
 return p.stdout
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fetch():
 dst=O/"NEW_YORK_1903_ARCHIVAL_ORIGINAL.webm"
 run(["curl","-L","--fail","--retry","3","--max-time","160","-A","Tra-le-Pagine-History/1.0",
      URL,"-o",str(dst)],175)
 if dst.stat().st_size<1000000:raise RuntimeError("No real historical film")
 return dst
def score(frame):
 gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
 gray=cv2.resize(gray,(360,640))
 lap=cv2.Laplacian(gray,cv2.CV_32F).var()
 return float(np.log1p(lap))
def source_frames(video):
 cap=cv2.VideoCapture(str(video))
 if not cap.isOpened():raise RuntimeError("Cannot decode real NYC 1903 film")
 fps=cap.get(cv2.CAP_PROP_FPS);length=cap.get(cv2.CAP_PROP_FRAME_COUNT)/fps
 width,height=map(int,(cap.get(3),cap.get(4)))
 print("ACTUAL_SOURCE",width,height,fps,length,flush=True)
 if width<900 or height<600 or length<30:raise RuntimeError("NYC source unexpectedly poor")
 picks=[]
 for t in np.linspace(6,min(length-6,100),30):
  cap.set(cv2.CAP_PROP_POS_MSEC,float(t)*1000)
  ok,f=cap.read()
  if not ok:continue
  h,w=f.shape[:2]
  cw=int(h*9/16)
  crop=f[:,(w-cw)//2:(w+cw)//2]
  if crop.shape[1]<300:continue
  val=score(crop)
  picks.append((val,float(t),crop))
 cap.release()
 picks.sort(reverse=True,key=lambda a:a[0])
 chosen=[]
 for q in picks:
  if all(abs(q[1]-p[1])>9 for p in chosen):chosen.append(q)
  if len(chosen)==4:break
 if len(chosen)<4:raise RuntimeError("No 4 distinct source moments")
 chosen.sort(key=lambda x:x[1])
 for i,(_,t,im) in enumerate(chosen,1):
  im=cv2.resize(im,(W,H),interpolation=cv2.INTER_LANCZOS4)
  cv2.imwrite(str(O/f"NYC_ORIGINAL_{i:02}.png"),im)
  print("REAL_FRAME_SELECTED",i,round(t,2),flush=True)
 return chosen
def structure(a,b):
 x=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY);y=cv2.cvtColor(b,cv2.COLOR_BGR2GRAY)
 def small(z):return cv2.GaussianBlur(cv2.resize(z,(72,128)),(9,9),0).astype(np.float32)
 x,y=small(x),small(y)
 return float(np.corrcoef(x.ravel(),y.ravel())[0,1])
def generate(chosen):
 client=Client("finegrain/finegrain-image-enhancer",verbose=False)
 outputs=[]
 for i,(_,t,frame) in enumerate(chosen,1):
  input_path=O/f"NYC_ORIGINAL_{i:02}.png"
  prompt=("Original real street film in New York City 1903, natural full-color documentary photograph, preserve "
    "EXACT existing people, clothing, gestures, building shapes and framing; physically plausible skin and hair "
    "texture, subtle textile fibers and architectural detail, lifelike color, sharp believable documentary photo; "
    "NO changes to identities, number of people, poses, or building signage.")
  neg="different faces, extra people, invented objects, made-up signs, painting, illustration, deformed eyes, artificial glamour, plastic skin, different perspective, anachronistic vehicles"
  print("REAL_AI_IMAGE_REQUEST",i,flush=True)
  v=client.predict(handle_file(str(input_path)),prompt,neg,210+i*19,2,1.22,.96,6,112,144,.49,20,"DDIM",api_name="/process")
  img=v[1] if isinstance(v,(list,tuple)) else v
  if isinstance(img,dict):img=img.get("path")
  if not img or not Path(img).is_file():raise RuntimeError("Actual generative image missing")
  out=O/f"NYC_GENERATIVE_{i:02}.png"
  Image.open(img).convert("RGB").resize((W,H),Image.Resampling.LANCZOS).save(out)
  source=cv2.imread(str(input_path));photo=cv2.imread(str(out))
  corr=structure(source,photo)
  print("ACTUAL_AI_GEOMETRY_CHECK",i,corr,flush=True)
  if corr<.86:raise RuntimeError(f"AI altered source scene too much {i}: {corr}")
  outputs.append(out)
 return outputs
def render(video,chosen,outputs):
 target=O/"NEW_YORK_1903_RESTAURO_V70.mp4"
 cap=cv2.VideoCapture(str(video));srcfps=cap.get(5)
 frames=[]
 # Render actual source motion (not still-only pan) and truly restored photo.
 for i,(_,t,_) in enumerate(chosen):
  cap.set(0 if False else cv2.CAP_PROP_POS_MSEC,max(0,t-1.35)*1000)
  raw=[]
  for k in range(round(1.35*srcfps)):
   ok,fr=cap.read()
   if not ok:break
   hh,ww=fr.shape[:2];cw=int(hh*9/16);fr=fr[:,(ww-cw)//2:(ww+cw)//2]
   raw.append(cv2.resize(fr,(W,H),interpolation=cv2.INTER_LINEAR))
  if not raw:raise RuntimeError("Source motion missing")
  photo=cv2.imread(str(outputs[i]))
  n=round(1.3*FPS)
  for k in range(n):frames.append(raw[min(len(raw)-1,int(k*len(raw)/n))])
  for k in range(12):
   a=(k+1)/12;a=a*a*(3-2*a)
   frames.append(cv2.addWeighted(raw[-1],1-a,photo,a,0))
  for k in range(round(3.5*FPS)):frames.append(photo)
 cap.release()
 silent=O/"V70_TEMP_SILENT.mp4"
 proc=subprocess.Popen(["ffmpeg","-nostdin","-y","-v","error","-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r","30","-i","-","-c:v","libx264","-preset","ultrafast","-crf","21","-pix_fmt","yuv420p",str(silent)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 for fr in frames:proc.stdin.write(fr.tobytes())
 proc.stdin.close();err=proc.stderr.read().decode()
 if proc.wait()!=0:raise RuntimeError(err[-1200:])
 duration=len(frames)/FPS
 # Original film is silent. Use synthesized original minimal soundscape only, not false archival audio.
 run(["ffmpeg","-nostdin","-y","-v","error","-i",str(silent),"-f","lavfi",
      "-i",f"aevalsrc=0.014*sin(2*PI*196*t)+0.011*sin(2*PI*293.66*t)+0.007*sin(2*PI*392*t):s=44100:d={duration}",
      "-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","128k","-t",str(duration),
      "-movflags","+faststart",str(target)],160)
 run(["ffmpeg","-v","error","-xerror","-i",str(target),"-f","null","-"])
 return target,duration
def main():
 src=fetch()
 shots=source_frames(src)
 photos=generate(shots)
 vid,dur=render(src,shots,photos)
 report={"source":URL,"original_sha256":sha(src),"restored_photo_sha256":[sha(p) for p in photos],
 "video_sha256":sha(vid),"duration":dur,"real_archive_footage":True,
 "generated_photos":"actual free Finegrain model inference, AI interpretive detail",
 "identity_accuracy":"NOT HISTORICALLY CERTIFIED","license_territory":"MUST REVIEW BEFORE PUBLIC RELEASE",
 "paid_gpu":False,"vidu_credits":0,"published_to_private_site":False}
 (O/"QA_V70.json").write_text(json.dumps(report,indent=2))
 print("V70_REAL_NEW_VIDEO_CREATED",vid,vid.stat().st_size,flush=True)
if __name__=="__main__":main()
