#!/usr/bin/env python3
"""V83 conservative color timing on REAL already generated Vidu moving frames.
No new generative frames, no still-photo animation, no Vidu API/credits.
Flow-guided chroma from the verified last frame; original moving luminance is kept.
Never claim this processing recovers real historical colors or accurate faces.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
import cv2,numpy as np

def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
def sat(frame):
 return float(np.median(cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)[:,:,1]))
def gray(frame):
 return cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
def corr(a,b):
 x=cv2.resize(gray(a),(72,128)).ravel().astype("float32")
 y=cv2.resize(gray(b),(72,128)).ravel().astype("float32")
 return float(np.corrcoef(x,y)[0,1])
def verify_media(path):
 p=subprocess.run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(path),"-f","null","-"],capture_output=True,text=True,timeout=130)
 if p.returncode:raise RuntimeError("FULL_VIDEO_DECODE_FAILED "+p.stderr[-800:])
def retime(input_path,output_path):
 source=Path(input_path);dest=Path(output_path)
 if not source.is_file():raise RuntimeError("SOURCE_VIDU_MP4_MISSING")
 cap=cv2.VideoCapture(str(source));fps=cap.get(cv2.CAP_PROP_FPS)
 width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT));total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
 if width!=720 or height!=1280 or not 20<=fps<=35 or not 4.9<=total/fps<=6.1:raise RuntimeError("INPUT_NOT_VERIFIED_5S_VIDU_720")
 cap.set(cv2.CAP_PROP_POS_FRAMES,total-2)
 ok,last=cap.read()
 if not ok:raise RuntimeError("MISSING_END_REFERENCE_FRAME")
 ref_gray=cv2.resize(gray(last),(360,640),interpolation=cv2.INTER_AREA)
 ref_ab=cv2.resize(cv2.cvtColor(last,cv2.COLOR_BGR2LAB)[:,:,1:3],(360,640))
 yy,xx=np.indices((640,360),dtype=np.float32)
 cap.set(cv2.CAP_PROP_POS_FRAMES,0)
 ok,first=cap.read()
 if not ok or corr(first,last)<.88:raise RuntimeError("VIDU_MOTION_NOT_SCENE_LOCKED")
 cap.set(cv2.CAP_PROP_POS_FRAMES,0)
 dest.parent.mkdir(parents=True,exist_ok=True)
 args=["ffmpeg","-nostdin","-y","-v","error","-f","rawvideo","-pix_fmt","bgr24","-s","720x1280","-r",str(fps),"-i","-",
       "-an","-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p","-movflags","+faststart",str(dest)]
 proc=subprocess.Popen(args,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 qa=[];first_out=None;source_gray_prev=None;output_gray_prev=None
 try:
  for i in range(total):
   ok,frame=cap.read()
   if not ok:raise RuntimeError("TRUNCATED_SOURCE_VIDU")
   small=cv2.resize(gray(frame),(360,640))
   flow=cv2.calcOpticalFlowFarneback(small,ref_gray,None,.5,3,23,3,5,1.2,0)
   flow[:,:,0]=np.clip(flow[:,:,0],-20,20)
   flow[:,:,1]=np.clip(flow[:,:,1],-20,20)
   aligned=cv2.remap(ref_ab,xx+flow[:,:,0],yy+flow[:,:,1],cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
   oldlab=cv2.cvtColor(frame,cv2.COLOR_BGR2LAB)
   newlab=oldlab.copy()
   newlab[:,:,1:3]=cv2.resize(aligned,(width,height),interpolation=cv2.INTER_LINEAR)
   rec=cv2.cvtColor(newlab,cv2.COLOR_LAB2BGR)
   t=i/fps
   a=min(1,max(0,(t-.06)/.94));a=a*a*(3-2*a)
   current=cv2.addWeighted(frame,1-a,rec,a,0)
   if first_out is None:first_out=current
   proc.stdin.write(current.tobytes())
   if i%max(1,round(.4*fps))==0:
    g0=cv2.resize(gray(frame),(180,320));g1=cv2.resize(gray(current),(180,320))
    original_flow=0 if source_gray_prev is None else float(np.mean(np.abs(g0.astype("float32")-source_gray_prev.astype("float32"))))
    changed=0 if output_gray_prev is None else float(np.mean(np.abs(g1.astype("float32")-output_gray_prev.astype("float32"))))
    qa.append({"t":round(t,2),"original_saturation":round(sat(frame),2),
               "color_saturation":round(sat(current),2),
               "source_motion_luma_diff":round(original_flow,3),
               "output_motion_luma_diff":round(changed,3),
               "same_luma_corr":round(float(np.corrcoef(g0.ravel(),g1.ravel())[0,1]),4)})
    source_gray_prev=g0;output_gray_prev=g1
 finally:
  cap.release()
  proc.stdin.close()
  err=proc.stderr.read().decode(errors="replace")
  if proc.wait()!=0:raise RuntimeError("RETIME_ENCODE_FAILED "+err[-800:])
 verify_media(dest)
 post=[x for x in qa if x["t"]>=1.2]
 first_colored=next((x for x in qa if x["t"]>=1.0),None)
 color_ok=(first_colored is not None and first_colored["color_saturation"]>=17 and all(x["color_saturation"]>=17 for x in post))
 moving=sum(x["output_motion_luma_diff"]>=.9 for x in post)
 motion_ok=moving>=max(3,len(post)//2)
 shape_ok=min(x["same_luma_corr"] for x in qa)>.98
 first_match=corr(first,first_out)
 report={"status":"TECHNICAL_CHROMA_RETIME_NOT_HISTORICAL_RESTORATION","source_sha256":sha(source),
    "processed_sha256":sha(dest),"source_real_vidu_frames":total,"video_fps":fps,"duration_s":total/fps,
    "first_frame_original_alignment":round(first_match,4),"color_by_1s":color_ok,
    "sustained_motion_after_color":motion_ok,"no_geometry_recreation":shape_ok,
    "production_gate_pass":bool(color_ok and motion_ok and shape_ok and first_match>.99),
    "method":"motion-preserving source-luminance chroma guided by last Vidu frame; not newly generated movement",
    "warning":"AI imagery and model motion are interpretive, not documented moving color history",
    "samples":qa,"new_vidu_credits":0}
 sidecar=dest.with_name("VIDU_CHROMA_RETIME_QA.json")
 sidecar.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 print("V83_CHROMA_POSTPROCESS",json.dumps({k:v for k,v in report.items() if k!="samples"}),flush=True)
 if not report["production_gate_pass"]:raise RuntimeError("CHROMA_RETIME_NOT_APPROVED: inspect before mixing; no paid retry")
 return report
if __name__=="__main__":
 a=argparse.ArgumentParser()
 a.add_argument("--input",required=True);a.add_argument("--output",required=True)
 p=a.parse_args()
 retime(p.input,p.output)
