#!/usr/bin/env python3
"""Owner preview ONLY, La Storia Rivive: real V1 Magicien film remaster. Never claim full AI video, no publish."""
from __future__ import annotations
import argparse, pathlib, subprocess, json, zipfile, shutil, hashlib, cv2, numpy as np
def run(c):
 p=subprocess.run(c,capture_output=True,text=True,timeout=300)
 if p.returncode: raise RuntimeError("CMD_FAILED "+p.stderr[-600:])
def digest(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--source",required=True);ap.add_argument("--source-zip",required=True)
 ap.add_argument("--out",default="output/storia_cinema_magicien_1898_v2")
 a=ap.parse_args()
 root=pathlib.Path(a.out);root.mkdir(parents=True,exist_ok=True)
 prior=pathlib.Path(a.source);oldzip=pathlib.Path(a.source_zip)
 assert prior.is_file() and oldzip.is_file()
 cap=cv2.VideoCapture(str(prior))
 fps=float(cap.get(cv2.CAP_PROP_FPS));n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
 w=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));h=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
 assert fps==24 and n>460 and w==1080 and h==1920,(fps,n,w,h)
 start=round(3.20*fps)
 cap.set(cv2.CAP_PROP_POS_FRAMES,start)
 temp=root/"MOVING_SOCIAL_V2_SILENT_720.mp4"
 proc=subprocess.Popen(["ffmpeg","-nostdin","-y","-v","error","-f","rawvideo","-pix_fmt","bgr24",
     "-s","720x1280","-r","24","-i","-","-an","-c:v","libx264","-preset","veryfast",
     "-crf","18","-pix_fmt","yuv420p",str(temp)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 if proc.stdin is None:raise RuntimeError("ENCODER_STDIN_MISSING")
 actualframes=0
 try:
  for i in range(start,n):
   ok,frame=cap.read()
   if not ok:break
   frame=cv2.resize(frame,(720,1280),interpolation=cv2.INTER_AREA)
   originalt=i/fps
   if originalt>=6.71:  # AI photo remains untouched: only reduce false red/purple spills during real film
    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    hue=hsv[:,:,0];sat=hsv[:,:,1];val=hsv[:,:,2]
    red=((hue<=13)|(hue>=168))&(sat>=45)
    purple=((hue>=126)&(hue<=167))&(sat>=45)
    black=val<=65
    s=sat.astype(np.float32)*.78
    s[red|purple]=np.minimum(s[red|purple],12)
    s[black]=np.minimum(s[black],7)
    hsv[:,:,1]=np.clip(s,0,255).astype(np.uint8)
    frame=cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
   proc.stdin.write(frame.tobytes())
   actualframes+=1
 finally:
  cap.release()
  proc.stdin.close()
  err=proc.stderr.read().decode(errors="ignore")
  if proc.wait()!=0:raise RuntimeError("ENCODER_FAIL "+err[-700:])
 assert actualframes>=360,actualframes
 final=root/"MAGICIEN_1898_V2_SOCIAL_REVIEW.mp4"
 run(["ffmpeg","-nostdin","-y","-v","error","-i",str(temp),
       "-ss",str(start/fps),"-i",str(prior),"-map","0:v:0","-map","1:a:0",
       "-vf","scale=1080:1920:flags=lanczos","-c:v","libx264","-preset","veryfast","-crf","19",
       "-pix_fmt","yuv420p","-c:a","aac","-b:a","96k","-shortest",
       "-movflags","+faststart",str(final)])
 run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(final),"-f","null","-"])
 probe=cv2.VideoCapture(str(final));fps2=probe.get(cv2.CAP_PROP_FPS);n2=probe.get(cv2.CAP_PROP_FRAME_COUNT)
 width=int(probe.get(cv2.CAP_PROP_FRAME_WIDTH));height=int(probe.get(cv2.CAP_PROP_FRAME_HEIGHT));probe.release()
 assert width==1080 and height==1920 and 15<n2/fps2<18
 for typ,codec in [("v","h264"),("a","aac")]:
  p=subprocess.run(["ffprobe","-v","error","-select_streams",typ,"-show_entries","stream=codec_name",
                    "-of","default=nw=1:nk=1",str(final)],capture_output=True,text=True,check=True)
  assert p.stdout.strip()==codec,(typ,p.stdout)
 report={"state":"TECHNICAL_MP4_PASS_VISUAL_ARTISTIC_REVIEW_PENDING",
         "new_video":False,"version":"REMASTER of previously generated Magicien 1898 V1, NOT a different film",
         "mp4":final.name,"video_sha256":digest(final),"duration_s":round(float(n2/fps2),3),
         "resolution":[1080,1920],"fps":fps2,"source_sha256":digest(prior),
         "changes":["Original opening intertitle trimmed, moving source now begins first frame",
                   "Strong synthetic red/magenta color spills desaturated only during historic moving section",
                   "Kept exact source-matched authentic B/W freeze and actual free Finegrain I2I photo, not rewritten"],
         "constraints":["Moving stage remains original footage with neural chroma, NOT generative photorealistic moving frames",
                       "Still-photo face eyeglasses plausibility requires owner/human QA; do NOT call final approved",
                       "Still-photo framing left and theatrical costume remains interpretive, not verified period colors",
                       "1080p vertical upsample is not a native 4K archive"],
         "human_visual_approval":False,"site_social_published":False,"vidu_new_post":False,"paid_calls":0}
 (root/"V2_VISUAL_REPORT.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
 with zipfile.ZipFile(oldzip) as z:
  names=[n for n in z.namelist() if n not in ("MAGICIEN_1898_SOCIAL_VISUAL_REVIEW.mp4","VISUAL_REPORT.json")]
  for name in names:
   (root/name).parent.mkdir(parents=True,exist_ok=True)
   (root/name).write_bytes(z.read(name))
 pack=root/"MAGICIEN_1898_V2_SOCIAL_REVIEW_AND_COPY.zip"
 with zipfile.ZipFile(pack,"w",zipfile.ZIP_DEFLATED,compresslevel=4) as z:
  z.write(final,final.name)
  z.write(root/"V2_VISUAL_REPORT.json","V2_VISUAL_REPORT.json")
  for name in names:z.write(root/name,name)
 with zipfile.ZipFile(pack) as z:assert z.testzip() is None
 print("VERIFIED_REAL_V2_VIDEO_REVIEW_ONLY",json.dumps(report),flush=True)
 print("ZIP_SHA",digest(pack),"ZIP_CRC_PASS",flush=True)
if __name__=="__main__":main()
