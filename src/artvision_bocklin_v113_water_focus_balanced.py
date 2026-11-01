#!/usr/bin/env python3
"""ArtVision Böcklin V113: offline focus acqua, revisione non distruttiva di V112.
Usa solo pixel del video V112, preserva AAC originale, nessuna nuova AI/TTS.
"""
import hashlib, json, math, subprocess
from pathlib import Path
import cv2
import numpy as np

SOURCE=Path('/mnt/data/BOECKLIN_CRITICO_MUSEUM_V112_MUSEO_RICOMPOSTO_REVIEW.mp4')
OUTPUT=Path('/mnt/data/BOECKLIN_CRITICO_MUSEUM_V113_ACQUA_NITIDA_MUSEO_REVIEW.mp4')
QA=Path('/mnt/data/BOECKLIN_CRITICO_MUSEUM_V113_QA.json')
EXPECTED='a15b42e399077bef9424258d8c198790a7659333f8ff25141bdf4d17a2254f5d'
AAC_EXPECTED='3f46d52d8e0a09974bd144c62a77f5357c1ec5cc63e9c3cee956c8853edd505e'
W,H,FPS,N=720,1280,20,2213
START,FULL,HOLD,END=28.2,30.25,39.5,41.2
ZMAX,CYMAX=1.45,835.0

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()

def run(args):
 r=subprocess.run([str(x) for x in args],capture_output=True)
 if r.returncode:raise RuntimeError(' '.join(map(str,args))+'\n'+r.stderr.decode(errors='replace')[-2000:])
 return r.stdout

def ease(x):
 x=np.clip(x,0,1)
 return x*x*(3-2*x)

def camera(t):
 if t<START or t>END:return 1.,360.,640.,0.
 if t<FULL:
  a=ease((t-START)/(FULL-START))
  return 1+(ZMAX-1)*a,360.,640+(CYMAX-640)*a,a
 if t<HOLD:
  u=(t-FULL)/(HOLD-FULL)
  return ZMAX+.004*math.sin(math.pi*u)**2,360.+.6*math.sin(2*math.pi*u),CYMAX+1.1*math.sin(2*math.pi*u),1.
 a=ease((t-HOLD)/(END-HOLD))
 return 1+(ZMAX-1)*(1-a),360.,640+(CYMAX-640)*(1-a),1-a

def focus(frame,t):
 z,cx,cy,a=camera(t)
 if a<=0:return frame
 if not 640/z-2 <= cy <= H-640/z+2:
  raise ValueError(f'Camera out of source bounds: t={t} z={z} cy={cy}')
 M=np.float32([[z,0,360-z*cx],[0,z,640-z*cy]])
 res=cv2.warpAffine(frame,M,(W,H),flags=cv2.INTER_LANCZOS4,borderMode=cv2.BORDER_REPLICATE)
 strength=.60*a
 if strength>0.001:
  blur=cv2.GaussianBlur(res,(0,0),.65)
  res=cv2.addWeighted(res,1+strength,blur,-strength,0)
 return res

def aac(p):
 return run(['ffmpeg','-v','error','-i',p,'-map','0:a:0','-c:a','copy','-f','adts','pipe:1'])

def lap(frame):
 g=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
 return float(cv2.Laplacian(cv2.resize(g,(180,320)),cv2.CV_64F).var())

def main():
 if sha(SOURCE)!=EXPECTED:raise RuntimeError('V112 source SHA mismatch; refusing to modify')
 if OUTPUT.exists():raise RuntimeError('Output exists, no overwrite')
 cap=cv2.VideoCapture(str(SOURCE))
 if int(cap.get(cv2.CAP_PROP_FRAME_COUNT))!=N or abs(cap.get(cv2.CAP_PROP_FPS)-FPS)>.01:
  raise RuntimeError('Source frame count or fps mismatch')
 tmp=OUTPUT.with_suffix('.silent.tmp.mp4')
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}',
  '-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',
  '-threads','3',str(tmp)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 peak=0.;over=0;prev=None;count=0;sharp_source=[];sharp_modified=[]
 try:
  for i in range(N):
   ok,f=cap.read()
   if not ok:raise RuntimeError('Truncated source')
   t=i/FPS
   if START<=t<=END:count+=1
   out=focus(f,t)
   if 32<=t<=38 and i%10==0:
    sharp_source.append(lap(f));sharp_modified.append(lap(out))
   sm=cv2.resize(cv2.cvtColor(out,cv2.COLOR_BGR2GRAY),(180,320))
   if prev is not None:
    mad=float(np.abs(sm.astype('int16')-prev.astype('int16')).mean())
    peak=max(peak,mad)
    over+=mad>35
   prev=sm
   proc.stdin.write(out.tobytes())
 finally:
  cap.release();proc.stdin.close()
 err=proc.stderr.read().decode(errors='replace')
 if proc.wait()!=0:raise RuntimeError('Encoder error: '+err[-1000:])
 run(['ffmpeg','-v','error','-y','-i',tmp,'-i',SOURCE,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','copy','-shortest','-movflags','+faststart',OUTPUT])
 tmp.unlink()
 run(['ffmpeg','-v','error','-xerror','-i',OUTPUT,'-f','null','-'])
 a,b=aac(SOURCE),aac(OUTPUT)
 if a!=b or hashlib.sha256(b).hexdigest()!=AAC_EXPECTED:raise RuntimeError('Audio not bit identical')
 v=cv2.VideoCapture(str(OUTPUT));n=int(v.get(cv2.CAP_PROP_FRAME_COUNT));v.release()
 if n!=N:raise RuntimeError('Frame count mismatch')
 ratio=float(np.mean(sharp_modified)/np.mean(sharp_source))
 qa={'work':'Boecklin Die Toteninsel 1883 NG 2/80','version':'V113','variant':'Critico Museum',
  'source_V112_sha256':EXPECTED,'output':OUTPUT.name,'output_bytes':OUTPUT.stat().st_size,
  'output_sha256':sha(OUTPUT),'duration_seconds':N/FPS,'frames':N,'fps':FPS,'size':'720x1280',
  'full_ffmpeg_decode':'PASS','aac_ADTS_sha256':AAC_EXPECTED,'AAC_bit_identical':True,
  'changed_interval_seconds':[START,END],'frames_processed_in_interval':count,
  'focus':{'voice_water_video_seconds':[29.72,39.70],'max_zoom':ZMAX,'center_y':CYMAX,'sharpen_amount':.6,'interpolation':'Lanczos4',
   'sharpness_ratio_to_V112_32_38s':round(ratio,4),'sharpness_loss_percent':round(100*(1-ratio),2)},
  'V57_peak_MAD':round(peak,3),'V57_frames_above_35':over,
  'room_intro_outro':'Preserved V112 content; digital reconstruction, not real Berlin room',
  'no_new_TTS_AI_API_spend':True,'social_published':False,'new_artwork':False,'masters_preserved':True,
  'library_uploaded':False,'R2_imported':False,'android_site_playback_verified':False,'Gold_V25':False,'human_full_watch':False}
 QA.write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(qa,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
