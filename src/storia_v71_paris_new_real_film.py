#!/usr/bin/env python3
"""La Storia Rivive V71 — PARIGI 1896-1900. REAL moving historical film + real free AI photo freeze.
No paid GPU, no Vidu. No unverified monochrome/illustration fallback.
"""
import os, json, hashlib, subprocess, zipfile, wave, math, importlib.util
from pathlib import Path
import cv2, numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=Path('output/storia_v71_paris');OUT.mkdir(parents=True,exist_ok=True)
URL='https://upload.wikimedia.org/wikipedia/commons/5/5a/A_Trip_Through_Paris%2C_France%2C_Late_1890s.webm'
PAGE='https://commons.wikimedia.org/wiki/File:A_Trip_Through_Paris,_France,_Late_1890s.webm'
S=[
 dict(t=218.,x=620,name='I pompieri a cavallo',date='1897',desc='the real Paris horse-drawn fire brigade and its firemen, equipment and period uniforms'),
 dict(t=300.,x=640,name='Il marciapiede mobile',date='1900',desc='the 1900 Paris Universal Exposition moving walkway, people, hats, garments and railings'),
 dict(t=31.,x=600,name='Notre-Dame',date='1896',desc='original horse carriages outside Paris Notre Dame cathedral, true stone facade'),
 dict(t=119.,x=650,name='Gli Champs-Elysees',date='1899',desc='original late 1890s Paris Champs Elysees street and passersby')
]
W,H,FPS=720,1280,30
def run(argv,limit=230):
 p=subprocess.run(argv,capture_output=True,text=True,timeout=limit)
 if p.returncode:raise RuntimeError(str(argv[:4])+' '+p.stderr[-900:])
 return p.stdout
def digest(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for block in iter(lambda:f.read(1<<20),b''):h.update(block)
 return h.hexdigest()
def crop(frame,x):
 h,w=frame.shape[:2];c=round(h*9/16);a=max(0,min(w-c,int(x-c/2)))
 return frame[:,a:a+c]
def get_source():
 p=OUT/'PELICOLA_PARIGI_ORIGINALE.webm'
 if not p.exists() or p.stat().st_size<10_000_000:
  run(['curl','-L','--fail','--show-error','--connect-timeout','25','--max-time','230','-A','Tra-le-Pagine-Arte/1.0 (research)','-o',str(p),URL],245)
 if p.stat().st_size<10_000_000:raise RuntimeError('NO_FILM')
 v=cv2.VideoCapture(str(p));w=v.get(3);h=v.get(4);fps=v.get(5);dur=v.get(7)/max(1,fps);v.release()
 if w<1000 or h<650 or dur<330:raise RuntimeError('WRONG_SOURCE')
 print('SOURCE_REAL',w,h,fps,dur,digest(p),flush=True)
 return p
def frames(source):
 v=cv2.VideoCapture(str(source));ret=[]
 for i,s in enumerate(S):
  v.set(cv2.CAP_PROP_POS_MSEC,s['t']*1000);ok,b=v.read()
  if not ok:raise RuntimeError('MISSING_SOURCE_FRAME '+str(i))
  c=crop(b,s['x']);p=OUT/('ORIGINAL_%02d.png'%(i+1));cv2.imwrite(str(p),c)
  ret.append(p)
 v.release()
 canvas=Image.new('RGB',(len(ret)*300,590),'#16171a');d=ImageDraw.Draw(canvas)
 for i,p in enumerate(ret):
  canvas.paste(Image.open(p).convert('RGB').resize((294,530)),(i*300+3,32))
  d.text((i*300+8,8),S[i]['name'],fill='white')
 canvas.save(OUT/'SCENE_ORIGINALI.jpg',quality=88)
 return ret
def structure(a,b):
 def f(im):
  g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
  return cv2.GaussianBlur(cv2.resize(g,(72,128),interpolation=cv2.INTER_AREA),(9,9),0).astype('float32')
 x=f(a).ravel();y=f(b).ravel()
 return float(np.corrcoef(x,y)[0,1])
def restore(inputs):
 from gradio_client import Client,handle_file
 sp=importlib.util.spec_from_file_location('ddcolor',ROOT/'src/storia_rivive_real_ai_v60.py')
 dd=importlib.util.module_from_spec(sp);sp.loader.exec_module(dd)
 session,model=dd.download_model()
 client=Client('finegrain/finegrain-image-enhancer',verbose=False)
 result=[]
 for i,(s,p) in enumerate(zip(S,inputs),1):
  source=cv2.imread(str(p));h,w=source.shape[:2]
  color=dd.infer_ab(session,cv2.resize(source,(720,576),interpolation=cv2.INTER_AREA))
  a=cv2.resize(color,(w,h),interpolation=cv2.INTER_CUBIC)
  l=dd.l_channel(source)
  rgb=np.clip(cv2.cvtColor(np.dstack((l,np.clip(a*1.04,-110,110))).astype('float32'),cv2.COLOR_LAB2RGB)*255,0,255).astype('uint8')
  base=OUT/('AI_BASE_%02d.jpg'%i)
  cv2.imwrite(str(base),cv2.resize(cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR),(576,1024)),[cv2.IMWRITE_JPEG_QUALITY,96])
  prompt=('Restoration of EXACT input historic frame into a high-quality realistic natural COLOR photograph. Preserve original geometry, exact existing people and identities, outfits, gestures and building structures. '+s['desc']+'. Believable real 1896-1900 light, detailed faces only where visible, natural skin and clothing, nuanced materials, no artistic illustration, no modern or extra objects, no invented writing.')
  neg='new faces, different people, invented storefront, extra limbs, modern equipment, plastic skin, fake texts, monochrome, watercolor, cartoon, oversaturation, fantasy, painted strokes'
  try:
   v=client.predict(handle_file(str(base)),prompt,neg,65+i*31,2,1.20,.97,6,112,144,.53,18,'DDIM',api_name='/process')
   q=v[1] if isinstance(v,(list,tuple)) else v
   if isinstance(q,dict):q=q.get('path')
   if not q or not Path(str(q)).is_file():raise RuntimeError('No AI image returned')
   photo=cv2.resize(cv2.imread(str(q)),(W,H))
   corr=structure(source,photo);sat=float(cv2.cvtColor(photo,cv2.COLOR_BGR2HSV)[:,:,1].mean())
   print('PHOTO_REAL_AI',i,corr,sat,flush=True)
   if not np.isfinite(corr) or corr<.72 or sat<15 or sat>180:raise RuntimeError('UNRELIABLE_PHOTOGRAPH')
   dst=OUT/('FOTO_AI_%02d.png'%i);cv2.imwrite(str(dst),photo,[cv2.IMWRITE_PNG_COMPRESSION,2])
   result.append(dict(i=i,name=s['name'],source=p.name,source_sha=digest(p),photo=dst.name,photo_sha=digest(dst),geometry=round(corr,3),color_saturation=round(sat,1)))
  except Exception as e:
   print('FREE_QUOTA_OR_IMAGE_REJECTED',i,type(e).__name__,str(e)[:500],flush=True)
   break
 (OUT/'PHOTO_QA.json').write_text(json.dumps(dict(source=PAGE,photos=result,no_paid_credits=True,art_review_required=True),ensure_ascii=False,indent=2))
 if len(result)<3:raise RuntimeError('FEWER_THAN_THREE_REAL_GENERATIVE_PHOTOS')
 return result
def music(dur,starts,path):
 sr=32000;t=np.arange(round(dur*sr),dtype='float32')/sr;v=np.zeros(len(t),dtype='float32')
 chords=[[146.83,196,246.94],[130.81,174.61,220],[164.81,207.65,261.63],[174.61,220,293.66]]
 for j,start in enumerate(starts):
  end=starts[j+1] if j+1<len(starts) else dur
  m=(t>=start)&(t<end);q=t[m]-start;z=np.zeros(len(q),dtype='float32')
  for k,f in enumerate(chords[j%4]):
   z+=(0.020+.003*k)*np.sin(2*np.pi*f*q+k*.4)
   z+=.005*np.sin(2*np.pi*(f*2.005)*q+k*.2)
  u=q-1.65;g=(u>=0)&(u<.7)
  z[g]+=.05*np.sin(2*np.pi*(260*u[g]+100*u[g]*u[g]))*np.exp(-8*u[g])
  v[m]+=z
 v*=np.minimum(1,t/.8)*np.minimum(1,(dur-t)/.8)
 v=np.tanh(v*2.4)
 with wave.open(str(path),'wb') as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr)
  w.writeframes((np.column_stack([v,np.roll(v,int(.014*sr))*.92])*18000).astype('<i2').tobytes())
def make(source,photos):
 silent=OUT/'UNMIXED.mp4';start=[];frames=0
 p=subprocess.Popen(['ffmpeg','-nostdin','-y','-loglevel','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',str(silent)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 try:
  for x in photos:
   s=S[x['i']-1]
   cap=cv2.VideoCapture(str(source));cap.set(cv2.CAP_PROP_POS_MSEC,(s['t']-1.65)*1000)
   nativefps=cap.get(cv2.CAP_PROP_FPS);raw=[]
   for k in range(round(1.65*nativefps)):
    ok,frame=cap.read()
    if not ok:break
    raw.append(cv2.resize(crop(frame,s['x']),(W,H),interpolation=cv2.INTER_CUBIC))
   cap.release()
   if len(raw)<8:raise RuntimeError('SOURCE_MOTION_MISSING')
   bw=cv2.resize(cv2.imread(str(OUT/x['source'])),(W,H));photo=cv2.imread(str(OUT/x['photo']))
   start.append(frames/FPS)
   for k in range(50):
    p.stdin.write(raw[min(len(raw)-1,round(k*(len(raw)-1)/49))].tobytes());frames+=1
   for k in range(10):
    a=(k+1)/10;a=a*a*(3-2*a)
    p.stdin.write(cv2.addWeighted(bw,1-a,photo,a,0).tobytes());frames+=1
   for k in range(94):
    p.stdin.write(photo.tobytes());frames+=1
   print('REAL_VIDEO_SCENE',x['name'],flush=True)
 finally:
  p.stdin.close();err=p.stderr.read().decode(errors='replace')
  if p.wait():raise RuntimeError('ENCODER_FAILED '+err[-1000:])
 dur=frames/FPS
 wav=OUT/'ORIGINAL_SCORE.wav';music(dur,start,wav)
 master=OUT/'LA_STORIA_RIVIVE_PARIGI_1900_V71.mp4'
 run(['ffmpeg','-nostdin','-y','-loglevel','error','-i',str(silent),'-i',str(wav),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(master)])
 run(['ffmpeg','-v','error','-xerror','-i',str(master),'-f','null','-'])
 cover=OUT/'COPERTINA.jpg'
 im=Image.open(OUT/photos[0]['photo']).convert('RGB');d=ImageDraw.Draw(im,'RGBA')
 try:
  font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',41)
  sm=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
 except:font=ImageFont.load_default();sm=ImageFont.load_default()
 d.rounded_rectangle((20,27,630,155),radius=14,fill=(10,10,16,120))
 d.text((44,43),'PARIGI · 1896–1900',font=font,fill=(250,243,229,255))
 d.text((45,113),'LA STORIA RIVIVE',font=sm,fill=(240,234,228,255));im.save(cover,quality=93)
 captions={
 'FACEBOOK':'Parigi, oltre 120 anni fa. Pompieri a cavallo, carrozze e perfino un marciapiede mobile: la vita correva già veloce. Le riprese sono autentiche; i fotogrammi fotografici a colori sono ricostruzioni AI con dettagli ipotizzati. Fonte: pellicole Lumière, Wikimedia Commons. #LaStoriaRivive #Parigi1900',
 'INSTAGRAM':'Un marciapiede mobile nel 1900? 🎞️ Parigi tra carri, pompieri e invenzioni. Pellicola vera, ricostruzioni AI dei fotogrammi a colori. #Storia #Parigi1900',
 'TIKTOK':'Prima dei social, Parigi era incredibile: guarda come si muovevano i pompieri e il primo marciapiede mobile! Vecchio film → fermo immagine → fotografia AI. I colori sono ricostruiti. #HistoryTok #Parigi',
 'YOUTUBE':'PARIGI 1896–1900 | La storia rivive\\nRiprese d’epoca dalle pellicole Lumière: movimento originale in bianco e nero, freeze e foto ricostruita a colori. Colori e microdettagli sono interpretazioni AI, non informazioni documentate. Fonte: '+PAGE
 }
 for k,t in captions.items():(OUT/('POST_'+k+'.txt')).write_text(t+'\n',encoding='utf8')
 qa=dict(source=PAGE,video=master.name,video_sha256=digest(master),duration=round(dur,2),true_motion=True,photos=photos,ai_color_interpretive=True,technical_decode_passed=True,artistic_review='PENDING',site_upload=False,cost_eur=0)
 (OUT/'QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2))
 zipp=OUT/'LA_STORIA_RIVIVE_PARIGI_1900_KIT.zip'
 with zipfile.ZipFile(zipp,'w',compression=zipfile.ZIP_DEFLATED) as z:
  for f in [master,cover,OUT/'PHOTO_QA.json',OUT/'QA.json',OUT/'SCENE_ORIGINALI.jpg',*[OUT/('POST_'+k+'.txt') for k in captions]]:z.write(f,f.name)
 with zipfile.ZipFile(zipp) as z:
  if z.testzip():raise RuntimeError('ZIP_INTEGRITY_ERROR')
 print('COMPLETED_PARIGI_MP4',master,master.stat().st_size,'ZIP',zipp,'duration',dur,flush=True)
if __name__=='__main__':
 source=get_source();source_frames=frames(source);photos=restore(source_frames);make(source,photos)
