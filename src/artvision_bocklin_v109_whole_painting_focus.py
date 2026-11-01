#!/usr/bin/env python3
"""ArtVision Böcklin V109: fix ONLY whole-painting focus in Museum chapters 2/8.
No network, TTS, AI or API; reconstruct verified painting pixels from Standard V102.
Original Museum V106 and Standard V102 are never overwritten.
"""
import argparse, hashlib, json, math, subprocess
from pathlib import Path
import cv2
import numpy as np

STD_SHA='096926e6ffb0de921fca72726deb4a136227150d1d1a224ccd42e329ee903777'
MUS_SHA='c1c54dba4f0198df3a8f82e11513378bccf2831647dca01741163250c857a263'
FPS=20; W=720; H=1280; N=2213
# V108 documented focus chapters: Std whole painting 16.95-28.20s, 79.10-90.85s.
# Replacement uses geometric pull-back and return only within those chapters.
INTERVALS=[{'start':17.0,'full':20.0,'hold':25.8,'end':28.15},
           {'start':79.1,'full':82.1,'hold':88.3,'end':90.8}]

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def run(a):
 p=subprocess.run(list(map(str,a)),capture_output=True)
 if p.returncode:raise RuntimeError('command failed: '+str(a)+' '+p.stderr.decode(errors='replace')[-2000:])
 return p.stdout

def frame_at(p,sec):
 c=cv2.VideoCapture(str(p));c.set(cv2.CAP_PROP_POS_MSEC,sec*1000);ok,f=c.read();c.release()
 if not ok or f.shape[:2]!=(H,W):raise RuntimeError('invalid frame')
 return f

def smooth(u):
 u=max(0.,min(1.,u));return u*u*(3-2*u)

def match_transform(src,frame):
 sift=cv2.SIFT_create(nfeatures=3500)
 k1,d1=sift.detectAndCompute(src,None);k2,d2=sift.detectAndCompute(frame,None)
 if d1 is None or d2 is None:raise RuntimeError('No SIFT keypoints')
 pairs=cv2.BFMatcher().knnMatch(d1,d2,k=2)
 good=[m for m,n in pairs if m.distance<.72*n.distance]
 if len(good)<25:raise RuntimeError('Not enough genuine painting feature matches')
 p1=np.float32([k1[m.queryIdx].pt for m in good]);p2=np.float32([k2[m.trainIdx].pt for m in good])
 M,mask=cv2.estimateAffinePartial2D(p1,p2,method=cv2.RANSAC,ransacReprojThreshold=5)
 if M is None or mask.sum()<20:raise RuntimeError('Painting affine registration failed')
 s=float(np.hypot(M[0,0],M[0,1]));cx=(360-M[0,2])/s;cy=(640-M[1,2])/s
 if not 3.2<s<6.5:raise RuntimeError('Implausible source crop scale')
 return [s,float(cx),float(cy)],int(mask.sum())

def compose(src,base,s,cx,cy):
 M=np.float32([[s,0,360-s*cx],[0,s,640-s*cy]])
 layer=cv2.warpAffine(src,M,(W,H),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_CONSTANT)
 mask=cv2.warpAffine(np.full(src.shape[:2],255,np.uint8),M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
 if np.all(mask==255):return layer
 out=base.copy()
 opaque=mask==255
 out[opaque]=layer[opaque]
 edges=(mask>0)&(mask<255)
 if edges.any():
  alpha=(mask[edges].astype(np.float32)/255)[:,None]
  out[edges]=np.clip(layer[edges]*alpha+out[edges]*(1-alpha),0,255).astype('uint8')
 return out

def motion(frame_index,interval,source_t,base,src,anchor_start,anchor_end):
 t=frame_index/FPS
 if t<interval['full']:
  u=smooth((t-interval['start'])/(interval['full']-interval['start']))
  state=[anchor_start[k]+(end-anchor_start[k])*u for k,end in enumerate([1.,352.,187.5])]
 elif t<interval['hold']:
  # Very subtle 0.8% gallery camera motion in the held whole painting.
  u=(t-interval['full'])/(interval['hold']-interval['full'])
  state=[1.+.008*math.sin(math.pi*u)**2,352.+1.2*math.sin(2*math.pi*u),187.5]
 else:
  u=smooth((t-interval['hold'])/(interval['end']-interval['hold']))
  state=[v+(anchor_end[k]-v)*u for k,v in enumerate([1.,352.,187.5])]
 return compose(src,base,*state)

def delta(p,seconds):
 cap=cv2.VideoCapture(str(p));out={}
 for t in seconds:
  cap.set(cv2.CAP_PROP_POS_MSEC,(t-.05)*1000);a,fa=cap.read();cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);b,fb=cap.read()
  if a and b:out[str(t)]=round(float(np.mean(np.abs(cv2.resize(fa,(180,320)).astype('int16')-cv2.resize(fb,(180,320)).astype('int16')))),3)
 cap.release();return out

def main():
 ap=argparse.ArgumentParser()
 for x in ('standard','museum','output','qa','comparison'):ap.add_argument('--'+x,type=Path,required=True)
 a=ap.parse_args();a.output.parent.mkdir(parents=True,exist_ok=True)
 if a.output.resolve() in (a.standard.resolve(),a.museum.resolve()):raise RuntimeError('Never overwrite originals')
 if sha(a.standard)!=STD_SHA or sha(a.museum)!=MUS_SHA:raise RuntimeError('Source SHA mismatch')
 base=frame_at(a.standard,24);src=base[452:827,8:712].copy()
 if src.shape!=(375,704,3):raise RuntimeError('Wrong painting crop from verified V102')
 anchors=[]
 for interval in INTERVALS:
  left,ni=match_transform(src,frame_at(a.museum,interval['start']))
  right,nj=match_transform(src,frame_at(a.museum,interval['end']))
  anchors.append((left,right,ni,nj))
 cap=cv2.VideoCapture(str(a.museum));n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
 if n!=N or abs(cap.get(cv2.CAP_PROP_FPS)-FPS)>.01:raise RuntimeError('Unexpected V106 video')
 silent=a.output.with_name(a.output.stem+'.video.tmp.mp4')
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}',
      '-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-threads','2',str(silent)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 changed=0
 try:
  for i in range(n):
   ok,f=cap.read()
   if not ok:raise RuntimeError('V106 truncated')
   for j,interval in enumerate(INTERVALS):
    if interval['start']<=i/FPS<=interval['end']:
     f=motion(i,interval,None,base,src,anchors[j][0],anchors[j][1]);changed+=1;break
   proc.stdin.write(f.tobytes())
 finally:
  cap.release();proc.stdin.close()
 err=proc.stderr.read().decode(errors='replace')
 if proc.wait():raise RuntimeError('FFmpeg encoder failed: '+err[-2000:])
 run(['ffmpeg','-v','error','-y','-i',silent,'-i',a.museum,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','copy','-shortest','-movflags','+faststart',a.output])
 silent.unlink()
 run(['ffmpeg','-v','error','-xerror','-i',a.output,'-f','null','-'])
 audio0=run(['ffmpeg','-v','error','-i',a.museum,'-map','0:a:0','-c:a','copy','-f','adts','pipe:1'])
 audio1=run(['ffmpeg','-v','error','-i',a.output,'-map','0:a:0','-c:a','copy','-f','adts','pipe:1'])
 ah=hashlib.sha256(audio0).hexdigest()
 if audio0!=audio1 or ah!='3f46d52d8e0a09974bd144c62a77f5357c1ec5cc63e9c3cee956c8853edd505e':raise RuntimeError('AAC audio changed')
 cp=cv2.VideoCapture(str(a.output));frames=int(cp.get(cv2.CAP_PROP_FRAME_COUNT));cp.release()
 if frames!=N:raise RuntimeError('Video frame count changed')
 samples=[24,85]
 c0=cv2.VideoCapture(str(a.museum));c1=cv2.VideoCapture(str(a.output));cs=cv2.VideoCapture(str(a.standard))
 sheet=np.full((3*320,4*180,3),25,np.uint8)
 for j,t in enumerate(samples):
  for k,c in enumerate((cs,c0,c1)):
   c.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,f=c.read();assert ok
   sm=cv2.resize(f,(180,320));sheet[k*320:(k+1)*320,j*360:j*360+180]=sm
   cv2.putText(sheet,['Standard V102','Museum V106','Museum V109'][k],(j*360+4,k*320+22),cv2.FONT_HERSHEY_SIMPLEX,.4,(255,255,255),1)
  sheet[2*320:3*320,j*360+180:j*360+360]=cv2.resize(frame_at(a.output,t+1),(180,320))
 for c in (c0,c1,cs):c.release()
 cv2.imwrite(str(a.comparison),sheet)
 d=[16.95,17.,20.,25.8,28.15,28.2,79.05,79.1,82.1,88.3,90.8,90.85]
 qa={'source_verified':{'standard_SHA256':STD_SHA,'museum_V106_SHA256':MUS_SHA},'output':{'filename':a.output.name,'bytes':a.output.stat().st_size,'sha256':sha(a.output),'duration_seconds':N/FPS,'frame_count':N,'codec':'H264/AAC','full_ffmpeg_decode':'PASS'},'chapters_corrected':[2,8],'whole_painting_hold_seconds':[[20,25.8],[82.1,88.3]],'intervals':INTERVALS,'modified_frames':changed,'geometric_match_inliers':[{'start':a[2],'end':a[3]} for a in anchors],'source_note':'704x375 exact painting area extracted from verified original Standard V102 at 24s; no new image source, original V102/V106 untouched; lower-resolution than original art file','aac_sha256':ah,'aac_bit_identical':True,'delta_MAD_before':delta(a.museum,d),'delta_MAD_after':delta(a.output,d),'gold_V25':False,'human_complete_review':'pending','R2_Android_playback':'not_verified','AI_TTS_API_calls':0,'social_published':False}
 a.qa.write_text(json.dumps(qa,indent=2,ensure_ascii=False),encoding='utf8')
 print(json.dumps(qa,indent=2,ensure_ascii=False))

if __name__=='__main__':main()