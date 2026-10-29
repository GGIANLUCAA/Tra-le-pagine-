#!/usr/bin/env python3
"""V74: video BW moving -> colored nearly-still photo gate. Not artistic/historic proof."""
import argparse,json
from pathlib import Path
import cv2,numpy as np

def inspect_video(path, sat_threshold=22, static_threshold=5.0):
 cap=cv2.VideoCapture(str(path)); fps=float(cap.get(cv2.CAP_PROP_FPS))
 if not cap.isOpened() or fps<12:raise RuntimeError("Cannot decode original")
 sat=[];diff=[];prev=None
 while True:
  ok,fr=cap.read()
  if not ok:break
  sm=cv2.resize(fr,(120,213),interpolation=cv2.INTER_AREA)
  gray=cv2.cvtColor(sm,cv2.COLOR_BGR2GRAY)
  sat.append(float(cv2.cvtColor(sm,cv2.COLOR_BGR2HSV)[:,:,1].mean()))
  diff.append(0 if prev is None else float(np.mean(np.abs(gray.astype(np.float32)-prev.astype(np.float32)))))
  prev=gray
 cap.release()
 if len(sat)<fps*2:raise RuntimeError("Too short")
 sat=np.asarray(sat); diff=np.asarray(diff); color=sat>sat_threshold
 for i in range(1,len(color)-1):
  if not color[i] and color[i-1] and color[i+1]:color[i]=True
 blocks=[];start=None
 for i in range(len(color)+1):
  yes=i<len(color) and color[i]
  if yes and start is None:start=i
  if not yes and start is not None:
   if i-start>=max(8,round(.45*fps)):
    prior=sat[max(0,start-round(.65*fps)):start]
    motion=float(np.median(diff[start+1:i])) if i>start+1 else 999
    bw_before=len(prior)>round(.2*fps) and float(np.median(prior))<18
    qualifies=bool(bw_before and motion<static_threshold)
    blocks.append({"from_s":round(start/fps,2),"to_s":round(i/fps,2),
                   "median_color_motion":round(motion,2),"preceded_by_bw":bool(bw_before),"qualifies":qualifies})
   start=None
 valid=sum(b["qualifies"] for b in blocks)
 return {"video":str(path),"duration_s":round(len(sat)/fps,2),
         "color_photo_blocks":blocks,"approved_pattern_cycles":valid,
         "warning":"Only structural detection: cannot certify photorealism, fidelity, provenance or rights"}

if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--video",type=Path,required=True)
 p.add_argument("--min-cycles",type=int,default=3);p.add_argument("--report",type=Path)
 args=p.parse_args()
 r=inspect_video(args.video)
 r["structural_pass"]=r["approved_pattern_cycles"]>=args.min_cycles
 if args.report:
  args.report.parent.mkdir(parents=True,exist_ok=True)
  args.report.write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
 print(json.dumps(r,indent=2,ensure_ascii=False))
 if not r["structural_pass"]:raise SystemExit("REJECT_REFERENCE_MISMATCH")
