#!/usr/bin/env python3
"""V79 Volti 1894-1900, three real, DIFFERENT archived films -> three source-guided full-color AI photo stills.
No Vidu/paid API, never label AI-invented microtexture as proven historical identity.
"""
from pathlib import Path
import cv2,json,hashlib,os,importlib.util,time,shutil,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('output/storia_v79_volti');OUT.mkdir(parents=True,exist_ok=True)
SCENES=[
 dict(key='SNEEZE_1894',time=2.52,center_x=721,year='1894',person='Fred Ott',desc='A single adult man in 1894 with distinctive thick dark moustache, short dark hair, pale waistcoat, bowtie and jacket. Eyes partly lowered; no other persons.',denoise=.43),
 dict(key='KISS_1896',time=4.12,center_x=873,year='1896',person='May Irwin and John C. Rice',desc='The 1896 adult actress May Irwin with a rounded mature face, short curled pinned-up hairstyle, authentic wide period dress; adult actor John C. Rice has dark full beard/moustache, parted hair, formal dark suit. Preserve natural mature faces and weight; no extra people.',denoise=.34),
 dict(key='KISS_1900',time=34.15,center_x=369,year='1900',person='A kissing couple',desc='A man with conspicuous narrow dark moustache and short dark hair in a dark 1900 period suit, woman with dark piled-up period hairstyle and high-neck lace frilled dress. Natural mature facial shape and gestures, two original adults only.',denoise=.37)
]
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
def crop(frame,center):
 h,w=frame.shape[:2];cw=round(h*9/16)
 left=max(0,min(w-cw,round(center-cw/2)))
 return frame[:,left:left+cw]
def source_one(s):
 p=OUT/(s['key']+'.webm')
 if not p.is_file():raise RuntimeError('NEED_REAL_ARCHIVAL_MOVIE '+str(p))
 cap=cv2.VideoCapture(str(p))
 cap.set(cv2.CAP_PROP_POS_MSEC,s['time']*1000)
 ok,frame=cap.read();cap.release()
 if not ok:raise RuntimeError('CANNOT_READ_HISTORICAL_FRAME '+str(s))
 original=crop(frame,s['center_x'])
 if original.shape[1]<255:raise RuntimeError('PORTRAIT_SOURCE_TOO_NARROW')
 dest=OUT/(s['key']+'_ORIGINALE.png')
 cv2.imwrite(str(dest),original)
 return dest,original
def structural_metrics(a,b):
 a=cv2.resize(a,(96,170));b=cv2.resize(b,(96,170))
 ag=cv2.GaussianBlur(cv2.cvtColor(a,cv2.COLOR_BGR2GRAY),(7,7),0).astype('float32')
 bg=cv2.GaussianBlur(cv2.cvtColor(b,cv2.COLOR_BGR2GRAY),(7,7),0).astype('float32')
 corr=float(np.corrcoef(ag.ravel(),bg.ravel())[0,1])
 s=float(cv2.cvtColor(b,cv2.COLOR_BGR2HSV)[:,:,1].mean())
 return corr,s
def main():
 from gradio_client import Client,handle_file
 spec=importlib.util.spec_from_file_location('ddcolor',ROOT/'src/storia_rivive_real_ai_v60.py')
 dd=importlib.util.module_from_spec(spec);spec.loader.exec_module(dd)
 session,_=dd.download_model()
 client=Client('finegrain/finegrain-image-enhancer',verbose=False)
 photos=[]
 for i,s in enumerate(SCENES,1):
  origpath,original=source_one(s)
  # Color reference via neural DDColor but preserve original geometry / sharp monochrome L.
  base_small=cv2.resize(original,(720,576))
  ab=dd.infer_ab(session,base_small)
  col_ab=cv2.resize(ab,(original.shape[1],original.shape[0]),interpolation=cv2.INTER_CUBIC)
  L=dd.l_channel(original)
  rgb=np.clip(cv2.cvtColor(np.dstack((L,np.clip(col_ab*1.12,-100,100))).astype(np.float32),cv2.COLOR_LAB2RGB)*255,0,255).astype(np.uint8)
  bgr=cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR)
  # Finegrain model has its own resizing/output; use source-locked full-color I2I.
  base=OUT/(s['key']+'_COLORE_BASE.jpg')
  cv2.imwrite(str(base),cv2.resize(bgr,(576,1024),interpolation=cv2.INTER_CUBIC),[cv2.IMWRITE_JPEG_QUALITY,95])
  # Faces are large and visible: avoid any changes to count/identity/age/expressions.
  prompt=("TRUE-TO-SOURCE PHOTO RESTORATION of the input historical 1894–1900 movie frame. "
  "Transform the exact source image into a crisp highly realistic modern color photograph with detailed natural face, eyes, eyelashes, authentic skin pores, subtle wrinkles, individual hair strands, realistic fabric weave, believable human anatomy, and natural daylight. "
  "PRESERVE THE EXACT SAME ORIGINAL REAL PEOPLE: same number, ages, facial structure, nose, lips, eyes, moustaches, hairstyles, facial expressions and pose. "
  "Identity and historical camera perspective must be preserved, not glamourized, no face swap or beautification. "+
  s['desc']+
  " Preserve visible hands, clothing and historical props exactly; background dark and simple as original. "
  "Cinematic professional documentary photograph, lifelike high dynamic range, warm realistic skin tones, nuanced colors, lifelike detail, no visible AI artifacts.")
  negative=("different identity, face swap, youthful model, beauty retouch, extra people, invented limbs, invented hands, modern outfit, added objects, changed pose, uncanny smile, painted illustration, waxy skin, stylized face, plastic face, blurred facial details, sepia, grayscale, monochrome, watermarks, text, fantasy, anime")
  print('FREE_AI_START',i,s['key'],'denoise',s['denoise'],flush=True)
  try:
   response=client.predict(handle_file(str(base)),prompt,negative,230+i*79,2,1.22,1.0,6,132,144,float(s['denoise']),20,'DDIM',api_name='/process')
   q=response[1] if isinstance(response,(list,tuple)) and len(response)>1 else response
   if isinstance(q,dict):q=q.get('path')
   if not q or not Path(str(q)).is_file():raise RuntimeError('GENERATIVE_PHOTO_NOT_RETURNED')
   generated=cv2.imread(str(q))
   if generated is None:raise RuntimeError('GENERATIVE_PHOTO_NOT_READABLE')
   photo=cv2.resize(generated,(720,1280))
   source_resized=cv2.resize(original,(720,1280))
   corr,sat=structural_metrics(source_resized,photo)
   # A global similarity number only gates extreme hallucination; must still be visually reviewed.
   print('PHOTO_QA',s['key'],'similarity',round(corr,3),'saturation',round(sat,2),flush=True)
   if not np.isfinite(corr) or corr<.68 or sat<18 or sat>160:
    raise RuntimeError('DIFFERS_TOO_MUCH_FROM_SOURCE_OR_STILL_MONO')
   dest=OUT/(s['key']+'_FOTO_AI_HD.png')
   cv2.imwrite(str(dest),photo,[cv2.IMWRITE_PNG_COMPRESSION,2])
   photos.append(dict(key=s['key'],person=s['person'],year=s['year'],source=origpath.name,source_sha=sha(origpath),generated=dest.name,generated_sha=sha(dest),corr=round(corr,3),saturation=round(sat,2),needs_visual_identity_review=True))
   print('FREE_AI_COMPLETED',i,dest,flush=True)
  except Exception as e:
   print('FREE_AI_FAILED',i,type(e).__name__,str(e)[:500],flush=True)
   # do not blindly re-run paid/gradio endpoint or invent a stand-in
   continue
 (OUT/'PHOTO_QA_V79.json').write_text(json.dumps({"photos":photos,"original_sources":"Wikimedia Commons/LOC", "ai_photo_method":"source-guided finegrain + DDColor, no Vidu", "visual_face_identity_approved":False},ensure_ascii=False,indent=2))
 board=Image.new('RGB',(920,565*len(photos)),(12,14,19))
 draw=ImageDraw.Draw(board)
 for i,r in enumerate(photos):
  left=Image.open(OUT/r['source']).convert('RGB').resize((450,535))
  right=Image.open(OUT/r['generated']).convert('RGB').resize((450,535))
  y=i*565+24
  board.paste(left,(5,y));board.paste(right,(465,y))
  draw.text((15,i*565+5),r['person']+' - '+r['year']+'   ORIGINALE  |  FOTO AI',fill='white')
 board.save(OUT/'CONFRONTO_VISIVO_VOLTI_V79.jpg',quality=91)
 if len(photos)<2:raise RuntimeError('INSUFFICIENT_HIGH_QUALITY_GENERATIVE_FACES; user video not ready')
 print('V79_GENERATED_DIFFERENT_FACES',len(photos),flush=True)
if __name__=="__main__":main()
