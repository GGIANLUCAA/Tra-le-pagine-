#!/usr/bin/env python3
"""V95.1 free final polish on the REAL New York 1911 Vidu-generated clip.
First second becomes mono->color over the exact SAME frames; subsequent
four seconds retain physical movement; mild warm-cast correction.
Preserve four original archival-to-photo chapters and unchanged music.
No Vidu API secrets or billable calls. User review still required.
"""
import hashlib,json,subprocess,zipfile
from pathlib import Path
import numpy as np,cv2
ROOT=Path("output/storia_new_york_1911_v951")
ROOT.mkdir(parents=True,exist_ok=True)
SOURCE=ROOT/"NEW_YORK_1911_V95_REAL_VIDU.mp4"
OLD_QA=ROOT/"V95_QA.json"
FINAL=ROOT/"NEW_YORK_1911_V951_COLOR_MOTION_REFINED.mp4"
VIDEO_BEGIN=12.0
VIDEO_END=17.10
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for ch in iter(lambda:f.read(1<<20),b""):h.update(ch)
 return h.hexdigest()
def run(argv,timeout=160):
 p=subprocess.run(argv,capture_output=True,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError("FFMPEG_FAILED "+" ".join(map(str,argv[:6]))+" "+p.stderr[-850:])
 return p.stdout
def stat(frame):
 hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
 return round(float(np.median(hsv[:,:,1])),1)
def process():
 if not SOURCE.is_file() or not OLD_QA.is_file():raise RuntimeError("EXISTING_NY_MOVING_VIDU_EPISODE_NOT_FOUND")
 qa=json.loads(OLD_QA.read_text(encoding="utf8"))
 if sha(SOURCE)!=qa["final_mp4_sha256"]:raise RuntimeError("REAL_PAID_EPISODE_HASH_MISMATCH")
 if qa.get("vidu_credits")!=16 or not qa.get("vidu_task_id"):
  raise RuntimeError("REAL_SINGLE_VIDU_TASK_PROOF_MISSING")
 cap=cv2.VideoCapture(str(SOURCE))
 fps=cap.get(cv2.CAP_PROP_FPS);n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
 w,h=int(cap.get(3)),int(cap.get(4))
 if (w,h)!=(720,1280) or not 29<n/fps<30 or fps!=30:
  raise RuntimeError("VIDEO_TIMING_UNEXPECTED")
 TMP=ROOT/"VIDEO_RETOUCHED_NO_AUDIO.mp4"
 enc=subprocess.Popen([
  "ffmpeg","-nostdin","-y","-v","error",
  "-f","rawvideo","-pix_fmt","bgr24","-s","720x1280","-r","30","-i","-",
  "-an","-c:v","libx264","-preset","veryfast","-crf","18",
  "-pix_fmt","yuv420p","-movflags","+faststart",str(TMP)
 ],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 samples=[]
 prev=None
 try:
  for i in range(n):
   ok,im=cap.read()
   if not ok:raise RuntimeError("SOURCE_VIDEO_TRUNCATED")
   t=i/fps
   if VIDEO_BEGIN<=t<VIDEO_END:
    # Mild documentary white-balance correction on the already generated,
    # moving colored video, *not* propagation/warping of chroma in optical flow.
    mat=im.astype(np.float32)
    mat[:,:,0]=np.clip(mat[:,:,0]*1.14+1.0,0,255)
    mat[:,:,1]=np.clip(mat[:,:,1]*1.01,0,255)
    mat[:,:,2]=np.clip(mat[:,:,2]*.88,0,255)
    graded=mat.astype(np.uint8)
    local=t-VIDEO_BEGIN
    a=max(0,min(1,(local-.04)/1.00))
    a=a*a*(3-2*a)
    gray=cv2.cvtColor(cv2.cvtColor(graded,cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR)
    im=cv2.addWeighted(gray,1-a,graded,a,0)
    if i%15==0:
     g=cv2.resize(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY),(180,320))
     delta=None if prev is None else float(np.mean(np.abs(g.astype("float32")-prev.astype("float32"))))
     prev=g
     samples.append({"t":round(local,2),"median_saturation":stat(im),
                     "mean_grayscale_motion":round(delta,2) if delta is not None else None})
   enc.stdin.write(im.tobytes())
 finally:
  cap.release();enc.stdin.close()
  e=enc.stderr.read().decode(errors="replace")
  if enc.wait():raise RuntimeError("VIDEO_ENCODING_FAILED "+e[-800:])
 # Reattach the unchanged continuous music; never restart music at the Vidu boundary.
 run(["ffmpeg","-nostdin","-y","-v","error","-i",str(TMP),"-i",str(SOURCE),
     "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","copy",
     "-shortest","-movflags","+faststart",str(FINAL)],160)
 run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(FINAL),"-f","null","-"],170)
 info=json.loads(run(["ffprobe","-v","error","-show_entries","format=duration,size:stream=codec_name,width,height","-of","json",str(FINAL)],25))
 s=[q for q in samples if 1.1<=q["t"]<=4.6]
 moving=sum((q["mean_grayscale_motion"] or 0)>.85 for q in s)
 if not s or moving<max(3,len(s)//2) or not any(q["median_saturation"]>=38 for q in s):
  raise RuntimeError("GENERATED_COLOR_MOTION_QA_BLOCKED")
 if not {"h264","aac"}.issubset({x.get("codec_name") for x in info["streams"]}):
  raise RuntimeError("AUDIO_OR_VIDEO_TRACK_MISSING")
 report={
  "version":"V95.1 NY 1911 free polish",
  "mode":"ONE NEW REAL Vidu inserted in four pre-existing original-film-to-photo cycles",
  "new_vidu_task":qa["vidu_task_id"],"new_paid_vidu_generation_during_this_polish":0,
  "total_existing_vidu_task_spend_credits":16,
  "actual_vidu_output_sha":qa["vidu_actual_clip_sha256"],
  "source_master_sha256":sha(SOURCE),"output_mp4_sha256":sha(FINAL),
  "duration_seconds":float(info["format"]["duration"]),
  "media":info,
  "technique":"gradual first-second mono-to-color on the SAME genuinely moving Vidu generated frames; mild BGR warm cast correction; original audio track preserved; ZERO optic flow",
  "seamless_audio_preserved":True,"historical_film_not_changed_outside_vidu":True,
  "vidu_segment_range_s":[VIDEO_BEGIN,VIDEO_END],"real_motion_after_color_intervals_passed":moving,
  "vidu_samples":samples,"faces_qa":"PENDING_HUMAN_REVIEW",
  "source_rights_italy":"PENDING_REVIEW","full_v94_approved":False,
  "four_classical_photography_caveat":"DDColor-only not modern-photographic reconstruction of faces",
  "social_site_published":False,"format":"La Storia Rivive"}
 (ROOT/"V951_QA.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 for file in ("COVER.jpg","POST_FACEBOOK.txt","POST_INSTAGRAM.txt","POST_TIKTOK.txt","POST_YOUTUBE.txt"):
  if not (ROOT/file).is_file():raise RuntimeError("MISSING_EXISTING_EDITORIAL_PACKAGE_FILE "+file)
 kit=ROOT/"NEW_YORK_1911_V951_ANDROID.zip"
 with zipfile.ZipFile(kit,"w",zipfile.ZIP_DEFLATED) as z:
  for file in [FINAL,ROOT/"V951_QA.json",ROOT/"COVER.jpg",*[ROOT/f"POST_{x}.txt" for x in ("FACEBOOK","INSTAGRAM","TIKTOK","YOUTUBE")]]:
   z.write(file,file.name)
 with zipfile.ZipFile(kit) as z:
  if z.testzip():raise RuntimeError("ZIP_CRC_FAILED")
 print("V951_REAL_NY_VIDEO_REFINED",FINAL.name,FINAL.stat().st_size,"SECONDS",report["duration_seconds"],"VIDEO_MOVE",moving,"NO_NEW_PAID_CREDITS",flush=True)
if __name__=="__main__":process()
