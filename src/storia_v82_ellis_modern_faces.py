#!/usr/bin/env python3
"""V82 source-locked Ellis Island 1903 facial photo restoration experiment.
Use official GFPGAN1.4 ONLY inside curated existing face ellipses. Do not alter any
non-face pixels. Generated facial details remain hypotheses, not identity evidence.
"""
from pathlib import Path
import sys,os,hashlib,json,zipfile,subprocess,math,types,importlib.util
import numpy as np
import cv2
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path("output/storia_v82_ellis/input")
OUT=Path("output/storia_v82_ellis/final");OUT.mkdir(parents=True,exist_ok=True)
SRC_VIDEO=SOURCE/"LA_STORIA_RIVIVE_ELLIS_ISLAND_1903_V80_VOLTI_HD.mp4"
OUTPUT=OUT/"LA_STORIA_RIVIVE_NEW_YORK_1903_VOLTI_V82.mp4"
W,H=720,1280
# Verified facial positions in already generated V80 images: [x0,y0,x1,y1].
# Small objects not listed here are not touched by GFPGAN or masks, so cannot become
# invented people. No face detection, zero uncontrolled person detections.
KNOWN_FACE_ROIS={
 1:[{"person":"center existing adult with hat","box":[270,336,405,479],"weight":.88}],
 2:[{"person":"right adult already in frame","box":[488,245,579,354],"weight":.85},
    {"person":"left woman in headscarf already in frame","box":[268,516,358,609],"weight":.81}],
 3:[{"person":"central woman already in frame","box":[409,417,520,544],"weight":.88}]
}
# Frames after true-video-to-AI-photo transition. Color frame has no movement.
STILLS=[
 {"scene":1,"start":2.30,"full_color":2.65,"end":7.03},
 {"scene":2,"start":9.54,"full_color":9.86,"end":14.01},
 {"scene":3,"start":16.58,"full_color":16.93,"end":21.50}
]

def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
 return h.hexdigest()

def subprocess_checked(cmd,timeout=160):
 q=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)
 if q.returncode:raise RuntimeError(" ".join(map(str,cmd[:4]))+" "+q.stderr[-900:])
 return q.stdout

def import_gfpganer():
 # BasicSR still references a torchvision legacy module removed from modern builds.
 import torchvision.transforms as tv
 from torchvision.transforms.functional import rgb_to_grayscale
 shim=types.ModuleType("torchvision.transforms.functional_tensor")
 shim.rgb_to_grayscale=rgb_to_grayscale
 sys.modules.setdefault("torchvision.transforms.functional_tensor",shim)
 setattr(tv,"functional_tensor",shim)
 from gfpgan.utils import GFPGANer
 return GFPGANer

def face_crop(photo,face):
 x0,y0,x1,y1=face["box"];cx=(x0+x1)/2;cy=(y0+y1)/2
 # Square, aligned as approximately upright faces; not whole scene.
 side=int(max(x1-x0,y1-y0)*1.55)
 xx=max(0,min(W-side,int(cx-side/2)))
 yy=max(0,min(H-side,int(cy-side/2)))
 return (xx,yy,xx+side,yy+side),photo[yy:yy+side,xx:xx+side].copy()

def restore_photos():
 GFPGANer=import_gfpganer()
 model=Path("models/GFPGANv1.4.pth")
 if not model.is_file() or model.stat().st_size<200_000_000:raise RuntimeError("Official GFPGAN v1.4 weight missing")
 restorer=GFPGANer(model_path=str(model),upscale=1,arch="clean",channel_multiplier=2,
                  bg_upsampler=None,device="cpu")
 details=[]
 for scene in range(1,4):
  photo=SOURCE/f"FOTO_AI_{scene:02d}_FACE_HD.png"
  old=cv2.imread(str(photo))
  if old is None or old.shape[:2]!=(H,W):raise RuntimeError("Wrong source photo dimensions")
  current=old.copy();face_metrics=[]
  for face in KNOWN_FACE_ROIS[scene]:
   box,patch=face_crop(current,face)
   if min(patch.shape[:2])<120:raise RuntimeError("Source face crop too small")
   crop=cv2.resize(patch,(512,512),interpolation=cv2.INTER_CUBIC)
   # Photograph-specific face restoration, NOT scene rewriting.
   _,restored,_=restorer.enhance(crop,has_aligned=True,paste_back=False,
                                weight=.65)
   if not restored:raise RuntimeError("Face model returned empty result")
   revised=cv2.resize(restored[0],(patch.shape[1],patch.shape[0]),interpolation=cv2.INTER_AREA)
   x0,y0,x1,y1=face["box"]
   xx0,yy0,xx1,yy1=box
   X,Y=np.meshgrid(np.arange(xx0,xx1,dtype=np.float32),
                   np.arange(yy0,yy1,dtype=np.float32))
   cx=(x0+x1)/2;cy=(y0+y1)/2
   rx=(x1-x0)/2;ry=(y1-y0)/2
   # A gradual elliptical feather only on the pre-verified skin/face area;
   # outside the region every pixel of old photo remains unchanged.
   radius=np.sqrt(((X-cx)/(rx+1))**2+((Y-cy)/(ry+1))**2)
   alpha=np.clip((1.05-radius)/.20,0,1)*face["weight"]
   region=current[yy0:yy1,xx0:xx1]
   merged=np.clip(region.astype(np.float32)*(1-alpha[...,None])+
                  revised.astype(np.float32)*alpha[...,None],0,255).astype(np.uint8)
   current[yy0:yy1,xx0:xx1]=merged
   original_face=old[y0:y1,x0:x1]
   new_face=current[y0:y1,x0:x1]
   blur_old=cv2.Laplacian(cv2.cvtColor(original_face,cv2.COLOR_BGR2GRAY),cv2.CV_32F).var()
   blur_new=cv2.Laplacian(cv2.cvtColor(new_face,cv2.COLOR_BGR2GRAY),cv2.CV_32F).var()
   if blur_new<blur_old*1.13:
    print("FACE_DETAIL_INSUFFICIENT",scene,face["person"],blur_old,blur_new,flush=True)
    # Refuse face-only changes that decrease/leave unchanged details.
    current[y0:y1,x0:x1]=old[y0:y1,x0:x1]
    status="PHOTO_RESTORATION_REJECTED_ON_DETAIL_GATE"
   else:status="PHOTO_RESTORATION_CANDIDATE_REQUIRES_VISUAL_IDENTITY_REVIEW"
   info={"person":face["person"],"face_box":face["box"],"source_crop":box,
         "detail_before":round(float(blur_old),1),"detail_after":round(float(blur_new),1),
         "status":status}
   face_metrics.append(info)
   print("V82_CURATED_FACE",scene,info,flush=True)
  final=OUT/f"FOTO_AI_{scene:02d}_FACE_MODERN_V82.png"
  cv2.imwrite(str(final),current,[cv2.IMWRITE_PNG_COMPRESSION,2])
  untouched=((old.astype(np.int16)-current.astype(np.int16))==0).all(axis=2)
  # > 92% of scene should stay identical; only faces are changed.
  unmodified=float(untouched.mean())
  if unmodified<.94:raise RuntimeError("An inpaint spread outside curated facial ROIs")
  details.append({"scene":scene,"original_sha":sha(photo),"new_photo_sha":sha(final),
                  "unmodified_scene_fraction":round(unmodified,4),"faces":face_metrics})
 (OUT/"FACE_REVIEW_V82.json").write_text(json.dumps(details,indent=2,ensure_ascii=False))
 return details

def contact_sheet():
 pics=Image.new("RGB",(1000,3*315+42),(18,21,24));d=ImageDraw.Draw(pics)
 try:f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",19)
 except:f=ImageFont.load_default()
 for ix in range(1,4):
  a=cv2.imread(str(SOURCE/f"FOTO_AI_{ix:02d}_FACE_HD.png"))
  b=cv2.imread(str(OUT/f"FOTO_AI_{ix:02d}_FACE_MODERN_V82.png"))
  face=KNOWN_FACE_ROIS[ix][0]["box"]
  x0,y0,x1,y1=face;cx=(x0+x1)//2;cy=(y0+y1)//2
  size=175
  x0=max(0,cx-size);y0=max(0,cy-size);x1=min(W,cx+size);y1=min(H,cy+size)
  for side,img in enumerate([a,b]):
   crop=Image.fromarray(cv2.cvtColor(img[y0:y1,x0:x1],cv2.COLOR_BGR2RGB)).resize((472,292))
   pics.paste(crop,(side*500+4,ix*315-274))
   d.text((side*500+8,ix*315-296),f"SCENE {ix} — "+("BEFORE" if side==0 else "V82 FACE DETAIL CANDIDATE"),font=f,fill="white")
 pics.save(OUT/"FACE_CLOSEUP_COMPARE_V82.jpg",quality=92)

def render(existing):
 cap=cv2.VideoCapture(str(SRC_VIDEO))
 fps=cap.get(cv2.CAP_PROP_FPS);dur=cap.get(cv2.CAP_PROP_FRAME_COUNT)/max(fps,1)
 if fps<25 or dur<20 or dur>25:raise RuntimeError("unexpected V80 reference movie")
 stills={i:cv2.imread(str(OUT/f"FOTO_AI_{i:02d}_FACE_MODERN_V82.png")) for i in range(1,4)}
 silent=OUT/"V82_VIDEO_TRACK.mp4"
 proc=subprocess.Popen(["ffmpeg","-nostdin","-y","-v","error","-f","rawvideo","-pix_fmt","bgr24",
  "-s",f"{W}x{H}","-r","30","-i","-","-c:v","libx264","-preset","veryfast",
  "-crf","18","-pix_fmt","yuv420p","-movflags","+faststart",str(silent)],
  stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 frame=0
 try:
  while True:
   ok,fr=cap.read()
   if not ok:break
   t=frame/fps
   for s in STILLS:
    if s["start"]<=t<s["end"]:
     # Same absolute scene, same photo, only local face difference.
     a=np.clip((t-s["start"])/(s["full_color"]-s["start"]),0,1)
     if a>0:
      photo=stills[s["scene"]]
      fr=cv2.addWeighted(fr,1-a,photo,a,0)
     break
   proc.stdin.write(fr.tobytes())
   frame+=1
 finally:
  cap.release();proc.stdin.close();err=proc.stderr.read().decode(errors="replace")
  if proc.wait()!=0:raise RuntimeError("MP4 encoder "+err[-850:])
 if abs(frame/fps-dur)>.05:raise RuntimeError("Inaccurate clip duration")
 # Retain ORIGINAL music and title, replace only existing color photo pixels.
 subprocess_checked(["ffmpeg","-nostdin","-y","-v","error","-i",str(silent),"-i",str(SRC_VIDEO),
 "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","copy","-movflags","+faststart",str(OUTPUT)],120)
 subprocess_checked(["ffmpeg","-v","error","-xerror","-i",str(OUTPUT),"-f","null","-"],120)
 return round(frame/fps,3)

def deliver(details,duration):
 (OUT/"COVER.jpg").write_bytes((OUT/"FOTO_AI_03_FACE_MODERN_V82.png").read_bytes())
 qa={"version":"V82","title":"NEW YORK · 1903","duration_seconds":duration,
 "source":"https://www.loc.gov/item/00694367/","source_audio":"original V80 soundtrack",
 "source_video":"V80 Ellis original moving historical film + 3 already generated same-frame AI photos",
 "faces":"4 curated existing faces processed with official GFPGAN v1.4, never the entire frame",
 "new_history_people_added":False,"no_new_people_outside_manual_faces":True,
 "limits":"Generated facial details are conjectural and MAY ALTER HISTORICAL IDENTITY",
 "human_artistic_identity_review":"PENDING",
 "technical_quality":"source-comparison-only; not historical identity validation",
 "zero_vidu_credits":True,"paid_api_calls":0,"uploaded_to_social":False,"uploaded_to_private_site":False,
 "video_sha256":sha(OUTPUT),"face_detail_metrics":details}
 (OUT/"PROVENANCE_AND_QA.json").write_text(json.dumps(qa,indent=2,ensure_ascii=False))
 kit=OUT/"NEW_YORK_1903_V82_MODERN_FACES_KIT.zip"
 with zipfile.ZipFile(kit,"w",compression=zipfile.ZIP_DEFLATED) as z:
  for file in [OUTPUT,OUT/"FACE_CLOSEUP_COMPARE_V82.jpg",OUT/"COVER.jpg",OUT/"FACE_REVIEW_V82.json",OUT/"PROVENANCE_AND_QA.json"]:
   z.write(file,file.name)
 with zipfile.ZipFile(kit) as z:
  if z.testzip() is not None:raise RuntimeError("ZIP CRC failed")
 print("V82_FACE_HD_FILM_READY",OUTPUT,OUTPUT.stat().st_size,kit,flush=True)
if __name__=="__main__":
 m=restore_photos()
 contact_sheet()
 dur=render(m)
 deliver(m,dur)
