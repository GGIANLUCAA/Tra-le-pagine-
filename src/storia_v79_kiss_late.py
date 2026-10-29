#!/usr/bin/env python3
"""V79 one extra DISTINCT 1896 action: the actual kiss, photo-real image-to-image, one free pass."""
from pathlib import Path
import cv2, numpy as np,json,hashlib,importlib.util
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
D=Path('output/storia_v79_kiss_late');D.mkdir(parents=True,exist_ok=True)
SOURCE=Path('output/storia_v79_volti/KISS_1896.webm')
T=10.38; CX=870
def main():
 from gradio_client import Client,handle_file
 cap=cv2.VideoCapture(str(SOURCE))
 cap.set(cv2.CAP_PROP_POS_MSEC,T*1000)
 ok,fr=cap.read();cap.release()
 if not ok:raise RuntimeError('No original film frame at 10.38')
 hh,ww=fr.shape[:2];cw=round(hh*9/16);x=max(0,min(ww-cw,CX-cw//2))
 fr=fr[:,x:x+cw]
 org=D/'KISS_1896_LATE_ORIGINALE.png';cv2.imwrite(str(org),fr)
 spec=importlib.util.spec_from_file_location('dd',ROOT/'src/storia_rivive_real_ai_v60.py')
 dd=importlib.util.module_from_spec(spec);spec.loader.exec_module(dd)
 session,_=dd.download_model()
 ab=dd.infer_ab(session,cv2.resize(fr,(720,576)))
 lab=np.dstack((dd.l_channel(fr),np.clip(cv2.resize(ab,(fr.shape[1],fr.shape[0]))*1.05,-110,110))).astype('float32')
 rgb=np.clip(cv2.cvtColor(lab,cv2.COLOR_LAB2RGB)*255,0,255).astype('uint8')
 color=cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR)
 base=D/'KISS_1896_LATE_COLOR_BASE.jpg'
 cv2.imwrite(str(base),cv2.resize(color,(576,1024)),[cv2.IMWRITE_JPEG_QUALITY,96])
 prompt=("Faithful source-guided photographic restoration of THIS EXACT historic 1896 film frame: "
 "two genuine mature adult actors kissing on camera, the same two exact people as the input, "
 "woman with rounded face and swept-back short curls, ruffled high-neck period dress; "
 "man with full dark moustache and beard, neat short dark hair and formal black suit. "
 "Restore sharp but natural modern photographic detail on their real faces: "
 "eyelids, wrinkles, textured skin, individual hairs, plausible warm colors and natural lighting. "
 "Maintain EXACT eye closures, profiles, original positions, ages and gestures, do not beautify. "
 "No extra people, no replaced faces, no new hands or clothes; image-to-image photograph not painting.")
 neg=("new face, age change, youthful glamour, strange hands, extra fingers, stranger, added object, different hairstyle, cartoon, sepia, face duplication, painting, monochrome, fake text, artifacts")
 client=Client('finegrain/finegrain-image-enhancer',verbose=False)
 res=client.predict(handle_file(str(base)),prompt,neg,607,2,1.22,.98,6,128,144,.39,20,'DDIM',api_name='/process')
 candidate_path=res[1] if isinstance(res,(list,tuple)) and len(res)>1 else res
 if isinstance(candidate_path,dict):candidate_path=candidate_path.get('path')
 candidate=cv2.imread(str(candidate_path))
 if candidate is None:raise RuntimeError('Free image restoration failed, no fabricated substitute')
 candidate=cv2.resize(candidate,(720,1280))
 old=D/'KISS_1896_LATE_AI_BASE.png';cv2.imwrite(str(old),candidate)
 # Neutralize orange/sepia hue without degrading face's brightness/geometry.
 lab=cv2.cvtColor(candidate,cv2.COLOR_BGR2LAB).astype('float32')
 lab[:,:,1]=128+(lab[:,:,1]-128)*.67
 lab[:,:,2]=128+(lab[:,:,2]-128)*.68
 natural=cv2.cvtColor(np.clip(lab,0,255).astype('uint8'),cv2.COLOR_LAB2BGR)
 restored=natural.copy();method='finegrain_ddcolor_natural'
 try:
  c=Client('sczhou/CodeFormer',verbose=False)
  p=D/'KISS_1896_LATE_NATURAL.png';cv2.imwrite(str(p),natural)
  response=c.predict(handle_file(str(p)),True,False,False,1,.80,api_name='/inference')
  q=response[0] if isinstance(response,(list,tuple)) else response
  if isinstance(q,dict):q=q.get('path')
  cf=cv2.imread(str(q))
  if cf is None:raise RuntimeError('No CodeFormer result')
  cf=cv2.resize(cf,(720,1280))
  Y,X=np.mgrid[:1280,:720]
  # Primary actor(s) occupy image central region, background unchanged.
  mask=.67*np.exp(-2*((X-380)**2/315**2+(Y-500)**2/415**2))
  restored=np.clip(natural.astype('float32')*(1-mask[:,:,None])+cf.astype('float32')*mask[:,:,None],0,255).astype('uint8')
  method='finegrain_ddcolor_codeformer_fidelity_0.80_masked'
 except Exception as e:print('OPTIONAL_FACE_ENHANCER_UNAVAILABLE',str(e)[:420],flush=True)
 photo=D/'KISS_1896_LATE_V79_FACE_RESTORED.png'
 cv2.imwrite(str(photo),restored,[cv2.IMWRITE_PNG_COMPRESSION,3])
 a=cv2.GaussianBlur(cv2.cvtColor(cv2.resize(fr,(90,160)),cv2.COLOR_BGR2GRAY),(7,7),0).astype('float32')
 b=cv2.GaussianBlur(cv2.cvtColor(cv2.resize(restored,(90,160)),cv2.COLOR_BGR2GRAY),(7,7),0).astype('float32')
 corr=float(np.corrcoef(a.ravel(),b.ravel())[0,1]);sat=float(cv2.cvtColor(restored,cv2.COLOR_BGR2HSV)[:,:,1].mean())
 if corr<.68 or sat<17:raise RuntimeError(f'PHOTO_NOT_FIDELITOUS_OR_COLORLESS {corr} {sat}')
 (D/'PHOTO_LATE_QA.json').write_text(json.dumps({'source_time':T,'movie_key':'KISS_1896','source_film':'The Kiss 1896 Wikimedia Commons original','method':method,'global_structure_corr':corr,'saturation':sat,'human_identity_review_required':True,'no_paid_credits':True},indent=2))
 board=Image.new('RGB',(920,560),(14,16,20));draw=ImageDraw.Draw(board)
 for i,p in enumerate([org,old,photo]):
  board.paste(Image.open(p).convert('RGB').resize((300,530)),(i*305+2,27))
  draw.text((i*305+5,5),['ORIGINAL 1896','AI COLOR','HD FINAL'][i],fill='white')
 board.save(D/'KISS_1896_LATE_QA_COMPARE.jpg',quality=90)
 print('V79_THIRD_HD_FACE_READY',photo,method,corr,sat,flush=True)
if __name__=='__main__':main()
