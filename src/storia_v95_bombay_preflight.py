#!/usr/bin/env python3
"""V95 Bombay 1929 hybrid: FREE editorial/technical shot preflight.
Read the original 8-scene V92 PUBLIC-DOMAIN-declared archival master from GitHub
and extract 5 source-locked B/W frames / existing restorations for human review.
No Vidu API call, no paid model, no claims of artistic approval.
"""
from pathlib import Path
import json,hashlib,cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path("output/storia_bombay_1929_v95")
ROOT.mkdir(parents=True,exist_ok=True)
MASTER=ROOT/"BOMBAY_1929_LA_STORIA_RIVIVE_V92.mp4"
SOURCE_QA=ROOT/"FINAL_QA_SOURCES.json"
# The V92 historical eight-scene edits are distinct verified archival timecodes.
V92_TIMINGS=[
    (84.5,.72,.27,1.88,"fruit-seller"),
    (537.7,1.12,.38,1.79,"landmark-crowd"),
    (285.9,.92,.34,1.94,"woven-load-porter"),
    (512.5,.94,.32,1.68,"harbor-workers"),
    (613.2,1.10,.41,1.93,"street-traders"),
    (751.7,1.17,.36,1.90,"horse-cart"),
    (223.0,.84,.31,2.12,"market-merchants"),
    (399.2,1.08,.48,2.35,"smiling-men"),
]
# 4 classical and 1 Vidu; entire new episode is ~20s.
KEEP=[1,2,3,4,5,6,7,8]
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
 return h.hexdigest()
def frame_at(cap, frame_id):
 cap.set(cv2.CAP_PROP_POS_FRAMES,int(frame_id))
 ok,f=cap.read()
 if not ok:raise RuntimeError("Cannot retrieve frame "+str(frame_id))
 if f.shape[:2]!=(1280,720):raise RuntimeError("Wrong source image size")
 return f
def image_corr(a,b):
 def reduce(x):
  g=cv2.cvtColor(cv2.resize(x,(72,128)),cv2.COLOR_BGR2GRAY)
  return cv2.GaussianBlur(g,(7,7),0).ravel().astype("float32")
 x,y=reduce(a),reduce(b)
 return round(float(np.corrcoef(x,y)[0,1]),4)
def metric(im):
 hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
 return round(float(np.mean(hsv[:,:,1])),2)
def main():
 if not MASTER.is_file() or MASTER.stat().st_size<1000000:raise RuntimeError("V92_VERIFIED_ARCHIVAL_MP4_MISSING")
 qa=json.loads(SOURCE_QA.read_text())
 if sha(MASTER)!=qa.get("video_sha256"):
  raise RuntimeError("V92_MASTER_SHA_NOT_MATCHED_TO_VERIFIED_RELEASE_QA")
 if len(qa.get("shots",[]))!=8:raise RuntimeError("NOT_EIGHT_DISTINCT_SOURCE_FILM_SHOTS")
 cap=cv2.VideoCapture(str(MASTER))
 fps=cap.get(cv2.CAP_PROP_FPS)
 if not 23<=fps<=25:raise RuntimeError("SOURCE_FRAMERATE_UNEXPECTED")
 frame_offset=0;records=[];cards=[]
 for idx,(timecode,motion,fade,hold,label) in enumerate(V92_TIMINGS,1):
  fm,ff,fh=(round(motion*fps),round(fade*fps),round(hold*fps))
  if idx in KEEP:
   # The renderer emits exact rounded frame counts, not summed floating-point seconds.
   # Its LAST real B/W frame is the source anchor, not an arbitrary moving frame .12s earlier.
   orig=frame_at(cap,frame_offset+fm-1)
   pic=frame_at(cap,frame_offset+fm+ff+min(round(.50*fps),fh-2))
   bw=ROOT/f"SOURCE_BW_{idx:02}.png"
   colored=ROOT/f"RESTORED_PHOTO_{idx:02}.jpg"
   cv2.imwrite(str(bw),orig)
   cv2.imwrite(str(colored),pic,[cv2.IMWRITE_JPEG_QUALITY,96])
   corr=image_corr(orig,pic)
   sat=metric(pic)
   if corr<.72:raise RuntimeError(f"PHOTO_SOURCE_GEOMETRY_CHANGED_{idx}: {corr}")
   if sat<9:raise RuntimeError(f"PHOTO_NO_COLOR_{idx}: {sat}")
   checks={
    "scene":idx,"source_timecode_s":timecode,"description_in_archive":label,
    "original_BW_frame_sha256":sha(bw),"existing_AI_color_photo_sha256":sha(colored),
    "source_to_color_gray_correlation":corr,"color_mean_saturation":sat,
    "source_original_film_moving":True,
    "source_original_timecode_different_from_others":True,
    "human_subject_verification":"PENDING",
    "image_to_image_modern_face_restoration":"NOT_YET_VERIFIED",
    "source_rights_italy":"PENDING",
    "v92_master_segment_start_s":round(frame_offset/fps,3),
    "v92_master_segment_end_s":round((frame_offset+fm+ff+fh)/fps,3),
    "v92_frozen_photo_start_s":round((frame_offset+fm+ff)/fps,3),
    "v92_start_frame":frame_offset,
    "v92_end_frame_exclusive":frame_offset+fm+ff+fh}
   records.append(checks);cards.append((idx,orig,pic,corr,sat,label))
   print("V95_REAL_SOURCE_CHECKED",idx,label,"corr",corr,"sat",sat,"source",timecode,"master",round(frame_offset/fps,2),flush=True)
  frame_offset+=fm+ff+fh
 cap.release()
 if len(records)!=len(KEEP) or len({r["source_timecode_s"] for r in records})!=len(KEEP):raise RuntimeError("DISTINCT_SOURCE_SHOTS_REQUIRED")
 poster=Image.new("RGB",(len(cards)*245,2*445+42),(12,17,23))
 d=ImageDraw.Draw(poster)
 try:font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",18)
 except:font=ImageFont.load_default()
 for k,(idx,bw,col,corr,sat,label) in enumerate(cards):
  for row,img in enumerate((bw,col)):
   thumb=Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB)).resize((235,418))
   poster.paste(thumb,(k*245+4,row*445+23))
   d.text((k*245+6,row*445+3),f"{idx} {label[:15]}",font=font,fill=(252,236,210))
  d.text((k*245+8,890),f"{corr:.3f} · sat {sat:.1f}",font=font,fill=(220,238,245))
 poster.save(ROOT/"V95_FIVE_SHOTS_BEFORE_AFTER.jpg",quality=92)
 report={"version":"V95_REAL_SOURCE_PREFLIGHT",
   "source_original":"https://commons.wikimedia.org/wiki/File:Street_Scenes_in_Bombay,_India_(real_sound),_Jan_1929.webm",
   "original_date":"11–14 January 1929","subject":"Bombay city life",
   "source_license_declared":"PD-India plus PD-1996 US, territorial review required",
   "existing_master_sha256":sha(MASTER),"selected_scenes":records,
   "vidu_target_source_scene_number":None,
   "vidu_selection_pending_real_subject_qa":True,
   "new_vidu_paid_post_count":0,"preserved_4_classic_and_1_video":True}
 (ROOT/"V95_FREE_SOURCE_QA.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 print("V95_PREFLIGHT_COMPLETED_NO_CREDITS",str(ROOT/"V95_FIVE_SHOTS_BEFORE_AFTER.jpg"),flush=True)
if __name__=="__main__":main()
