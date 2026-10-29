#!/usr/bin/env python3
"""V79 original La Storia Rivive cinematic montage of three distinct authentic vintage films,
real B/W movement -> exact source-frame freeze -> modern-quality source-anchored AI facial photo.
Zero paid AI, original composed audio, export and QA.
"""
from pathlib import Path
import cv2,numpy as np,zipfile,wave,subprocess,math,json,hashlib
from PIL import Image,ImageDraw,ImageFont
OUT=Path("output/storia_v79_volti")
FINAL=Path("output/storia_v79_final");FINAL.mkdir(parents=True,exist_ok=True)
FPS=30;W,H=720,1280
SHOTS=[
 dict(key='SNEEZE_1894',name='Un volto nel 1894',year='1894',t=2.52,cx=721,motion=2.32,hold=3.55,photo_dir='output/storia_v79_fred',photo='SNEEZE_1894_V79_FACE_RESTORED.png'),
 dict(key='KISS_1896',name='Il primo bacio del cinema',year='1896',t=4.12,cx=873,motion=2.44,hold=3.80,photo_dir='output/storia_v79_face_fix',photo='KISS_1896_V79_FACE_RESTORED.png'),
 dict(key='KISS_1900',name='Il cinema scopre i volti',year='1900',t=34.15,cx=369,motion=2.90,hold=4.05,photo_dir='output/storia_v79_face_fix',photo='KISS_1900_V79_FACE_RESTORED.png')
]
def hash_file(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def run(args,timeout=160):
 r=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
 if r.returncode:raise RuntimeError(' '.join(args[:5])+'\n'+r.stderr[-1200:])
 return r.stdout
def crop(im,x):
 h,w=im.shape[:2]
 cw=round(h*9/16)
 left=max(0,min(w-cw,round(x-cw/2)))
 return im[:,left:left+cw]
def make_title(frame,t):
 if t>=1.64:return frame
 fade=min(1,t/.3,max(.0,(1.64-t)/.45))
 if fade<=.002:return frame
 pil=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)).convert('RGBA')
 layer=Image.new('RGBA',(W,H),(0,0,0,0))
 d=ImageDraw.Draw(layer)
 d.rounded_rectangle((28,40,691,185),radius=13,fill=(6,8,13,int(155*fade)))
 try:
  a=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',55)
  b=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',24)
 except:a=ImageFont.load_default();b=ImageFont.load_default()
 def center(s,font,y,color):
  box=d.textbbox((0,0),s,font=font); xx=(W-(box[2]-box[0]))//2
  d.text((xx,y),s,font=font,fill=color)
 center('AMERICA',a,53,(252,247,238,int(255*fade)))
 center('1894 — 1900',b,126,(231,204,168,int(245*fade)))
 return cv2.cvtColor(np.asarray(Image.alpha_composite(pil,layer).convert('RGB')),cv2.COLOR_RGB2BGR)
def produce_audio(length,events,path):
 sr=32000;t=np.arange(round(length*sr),dtype=np.float32)/sr
 # Original minimalist cinematic piano/string-like score with emotional cadence.
 v=np.zeros(len(t),dtype=np.float32)
 chords=[(146.83,220.,293.66),(164.81,246.94,329.63),(130.81,196.,261.63)]
 for j,(at,ev) in enumerate(events):
  end=events[j+1][0] if j<len(events)-1 else length
  m=(t>=at)&(t<end);q=t[m]
  q=q-at
  z=np.zeros(len(q),dtype=np.float32)
  for k,f in enumerate(chords[j]):
   z+=(0.016-.002*k)*np.sin(2*np.pi*f*q+.24*k)
   z+=.005*np.sin(2*np.pi*2.005*f*q+.17*k)
  for t0 in np.arange(0,end-at,0.88):
   u=q-t0;sel=(u>=0)&(u<1.6)
   z[sel]+=.018*np.sin(2*np.pi*chords[j][1]*u[sel])*np.exp(-3.1*u[sel])
  photo_at=float(ev-at)
  u=q-photo_at;sel=(u>=0)&(u<.72)
  z[sel]+=.030*np.sin(2*np.pi*(220*u[sel]+110*u[sel]*u[sel]))*np.exp(-8*u[sel])
  v[m]+=z
 v*=np.minimum(1,t/.6)*np.minimum(1,(length-t)/.7)
 v=np.tanh(v*1.9)
 stereo=np.column_stack((v,np.roll(v,int(.012*sr))*.9))
 with wave.open(str(path),'wb') as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr)
  w.writeframes((np.clip(stereo,-1,1)*18500).astype('<i2').tobytes())
def make():
 metadata=json.loads((OUT/'FONTI_VERIFICATE.json').read_text(encoding='utf8'))['sources']
 accepted={r['key']:r for r in metadata}
 for s in SHOTS:
  if s['key'] not in accepted:raise RuntimeError('SOURCE_NOT_VERIFIED')
  p=OUT/(s['key']+'.webm')
  if hash_file(p)!=accepted[s['key']]['sha256']:raise RuntimeError('HISTORIC_SOURCE_SHA_FAIL '+s['key'])
  photo=Path(s['photo_dir'])/s['photo']
  if not photo.is_file():raise RuntimeError('REAL_RESTORATION_NOT_AVAILABLE '+str(photo))
  # Reject colorless or extremely changed photos, but visual face QC is separate and necessary.
  bgr=cv2.imread(str(photo))
  if bgr is None:raise RuntimeError('RESTORED_FACE_UNREADABLE')
  saturation=float(cv2.cvtColor(bgr,cv2.COLOR_BGR2HSV)[:,:,1].mean())
  if saturation<17 or saturation>145:raise RuntimeError('BAD_COLOR_IMAGE '+s['key']+' '+str(saturation))
 video=FINAL/'LA_STORIA_RIVIVE_I_VOLTI_DEL_CINEMA_1894_1900.mp4'
 temp=FINAL/'MUTO_TEMP.mp4'
 enc=subprocess.Popen(['ffmpeg','-nostdin','-y','-loglevel','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','veryfast','-crf','17','-pix_fmt','yuv420p',str(temp)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 frames=0;notes=[];times=[]
 try:
  for idx,s in enumerate(SHOTS):
   src=OUT/(s['key']+'.webm')
   cap=cv2.VideoCapture(str(src))
   nativefps=float(cap.get(cv2.CAP_PROP_FPS))
   cap.set(cv2.CAP_PROP_POS_MSEC,(s['t']-s['motion'])*1000)
   raw=[]
   for i in range(math.ceil(s['motion']*nativefps)):
    ok,fr=cap.read()
    if not ok:break
    bw=cv2.cvtColor(cv2.cvtColor(fr,cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR)
    raw.append(cv2.resize(crop(bw,s['cx']),(W,H),interpolation=cv2.INTER_CUBIC))
   cap.release()
   if len(raw)<10:raise RuntimeError('NO_GENUINE_MOVEMENT '+s['key'])
   a=cv2.imread(str(OUT/(s['key']+'_ORIGINALE.png')))
   if a is None:raise RuntimeError('PHOTO_SOURCE_FRAME_NOT_FOUND '+s['key'])
   exact_bw=cv2.resize(cv2.cvtColor(cv2.cvtColor(a,cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR),(W,H),interpolation=cv2.INTER_CUBIC)
   photo=cv2.resize(cv2.imread(str(Path(s['photo_dir'])/s['photo'])),(W,H))
   begin=frames/FPS
   times.append(begin)
   count=round(s['motion']*FPS)
   for k in range(count):
    fr=raw[min(len(raw)-1,round(k*(len(raw)-1)/(count-1)))]
    if k>=count-4:
     alpha=(k-count+5)/5
     fr=cv2.addWeighted(fr,1-alpha,exact_bw,alpha,0)
    if idx==0:fr=make_title(fr,k/FPS)
    enc.stdin.write(fr.tobytes());frames+=1
   for _ in range(4):enc.stdin.write(exact_bw.tobytes());frames+=1
   transition=9
   for j in range(transition):
    alpha=(j+1)/transition;alpha=alpha*alpha*(3-2*alpha)
    fr=cv2.addWeighted(exact_bw,1-alpha,photo,alpha,0)
    enc.stdin.write(fr.tobytes());frames+=1
   photo_starts=frames/FPS
   hold=round(s['hold']*FPS)
   for _ in range(hold):enc.stdin.write(photo.tobytes());frames+=1
   notes.append(dict(name=s['name'],archive_file=accepted[s['key']]['commons_page'],
       original_video_sha256=accepted[s['key']]['sha256'],
       face_photo_sha256=hash_file(Path(s['photo_dir'])/s['photo']),
       source_frame_time=s['t'],motion_duration=round(count/FPS,3),
       photo_duration=round(hold/FPS,3),
       photo_starts=round(photo_starts,3),source_movement_authentic=True,
       photo_reconstructed_AI=True,
       physical_identity_historically_verified=False))
   times[-1]=(begin,photo_starts)
   print('REAL_FOOTAGE_TO_FACE_PHOTO',s['key'],round(frames/FPS,2),flush=True)
 finally:
  enc.stdin.close();err=enc.stderr.read().decode(errors='replace')
  if enc.wait()!=0:raise RuntimeError('ENCODER_FAILED '+err[-1400:])
 duration=frames/FPS
 score=FINAL/'MUSICA_ORIGINALE.wav'
 produce_audio(duration,times,score)
 run(['ffmpeg','-nostdin','-y','-v','error','-i',str(temp),'-i',str(score),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k','-t',str(duration),'-movflags','+faststart',str(video)],120)
 run(['ffmpeg','-v','error','-xerror','-i',str(video),'-f','null','-'],160)
 spec=__import__('importlib.util',fromlist=['spec_from_file_location']).spec_from_file_location('gate','src/storia_rivive_v74_effect_gate.py')
 import importlib.util
 gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
 check=gate.inspect_video(video)
 if check['approved_pattern_cycles']<3:raise RuntimeError('USER_GOLD_EFFECT_NOT_PRESENT '+str(check))
 cover=FINAL/'COPERTINA.jpg'
 p=Image.open(Path(SHOTS[1]['photo_dir'])/SHOTS[1]['photo']).convert('RGB').resize((720,1280))
 d=ImageDraw.Draw(p,'RGBA')
 d.rounded_rectangle((28,34,692,177),radius=13,fill=(11,13,21,135))
 try:
  ft=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',50)
  sm=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',24)
 except:ft=ImageFont.load_default();sm=ImageFont.load_default()
 d.text((62,44),'I VOLTI DEL CINEMA',font=ft,fill=(250,245,230,255))
 d.text((72,120),'AMERICA · 1894–1900',font=sm,fill=(242,214,176,255))
 p.save(cover,quality=93)
 posts={
 'FACEBOOK':'Come apparivano davvero i volti dei primi film? Tre pellicole originali del 1894, 1896 e 1900 tornano in movimento. Ogni fotogramma si ferma e diventa una fotografia a colori ricostruita con AI. Occhi, pelle e alcuni dettagli sono interpretazioni fotografiche, non prove dell’aspetto storico. Filmati: Wikimedia Commons/Library of Congress. #LaStoriaRivive #Cinema',
 'INSTAGRAM':'Un volto del 1894. Un bacio del 1896. Il cinema del 1900. 🎞️ Riprese originali, fotografie AI a colori ricostruite. Dettagli interpretativi. #HistoryReels #EarlyCinema',
 'TIKTOK':'Queste persone sono state filmate oltre 125 anni fa. 🎥 Il movimento è autentico; i volti a colori sono ricostruzioni AI, non fotografie d’epoca. #storia #cinema',
 'YOUTUBE':'AMERICA 1894–1900 | I volti dei primi film\n\nTre differenti pellicole originali: Fred Ott’s Sneeze (1894), The Kiss (1896) e The Kiss (1900). Il filmato in movimento è autentico, ogni fermo immagine colorato è una ricostruzione AI. I microdettagli e i colori non sono storicamente verificabili. Fonti Wikimedia Commons / Library of Congress. Audio originale creato per il montaggio.'
 }
 for platform,copy in posts.items():(FINAL/('POST_'+platform+'.txt')).write_text(copy+'\n',encoding='utf8')
 provenance={
  'title':'I volti del cinema · America 1894–1900',
  'video_file':video.name,'video_sha256':hash_file(video),
  'duration_seconds':round(duration,3),'technical_full_decode_passed':True,
  'structural_gold_format_gate':check,
  'historical_films':notes,
  'facial_details_are_modern_reconstructions_not_true_historical_record':True,
  'user_approved_identity_matches':'PENDING_USER_VISUAL_REVIEW',
  'Italian_commercial_reuse_rights':'NOT_SPECIFICALLY_CLEARED',
  'archival_original_audio_included':False,
  'music_original_newly_composed':True,
  'vidu_credits_used':0,'paid_AI_calls_used':0,'private_site_upload_verified':False,'social_published':False,
  'quality_target':'Modern-looking skin, eyes, hair with image-to-image source shape lock and no invented additional people'
 }
 (FINAL/'FONTI_E_QA.json').write_text(json.dumps(provenance,indent=2,ensure_ascii=False))
 pack=FINAL/'I_VOLTI_DEL_CINEMA_1894_1900_KIT.zip'
 with zipfile.ZipFile(pack,'w',compression=zipfile.ZIP_DEFLATED) as z:
  for p in [video,cover,FINAL/'FONTI_E_QA.json',*[FINAL/('POST_'+x+'.txt') for x in posts]]:z.write(p,p.name)
 with zipfile.ZipFile(pack) as z:
  if z.testzip():raise RuntimeError('CORRUPT_ZIP')
 print('V79_COMPLETED_TRUE_FILM_AND_RESTORED_FACES',video,video.stat().st_size,'secs',duration,flush=True)
if __name__=='__main__':make()
