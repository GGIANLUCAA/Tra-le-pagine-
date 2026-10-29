#!/usr/bin/env python3
"""V79: optional zero-cost facial repair using official CodeFormer demo.
Only a trial, never claim identity preservation from mere face-sharpening.
No paid credits or API billing. Inputs are existing source-guided AI photos.
"""
from pathlib import Path
import cv2, numpy as np,json
D=Path('output/storia_v79_face_fix');D.mkdir(exist_ok=True,parents=True)
keys=['KISS_1896','KISS_1900']
def recolor(im,key):
 lab=cv2.cvtColor(im,cv2.COLOR_BGR2LAB).astype(np.float32)
 h,w=im.shape[:2]
 # Low-saturation color restoration: correct dramatic warm/cyan casts without changing geometry.
 a,b=lab[:,:,1],lab[:,:,2]
 if key=='KISS_1896':
  # reduce orange sepia (yellow and magenta cast); keep skin warm, avoid all-orange clothes
  lab[:,:,1]=128+(a-128)*.64
  lab[:,:,2]=128+(b-128)*.65
 else:
  # remove severe green cast; human skin has warm/positive red
  lab[:,:,1]=np.clip(128+(a-128)*.68 + 15,0,255)
  lab[:,:,2]=128+(b-128)*.82
 # For neutral skin tones, masked local color adjustments rather than a blind global tint.
 x,y=np.meshgrid(np.arange(w),np.arange(h))
 if key=='KISS_1896':
  center=(440,505);rx,ry=190,320;target_a,target_b=144,149
 else:
  center=(380,470);rx,ry=205,325;target_a,target_b=145,146
 smooth=np.exp(-2*((x-center[0])**2/(rx**2)+(y-center[1])**2/(ry**2))).astype(np.float32)
 bright=(lab[:,:,0]>67).astype(np.float32)
 smooth=smooth*bright
 # Offset faces toward plausible neutrals; do not invent shapes or features.
 face_ya,face_xa=center[1],center[0]
 local=lab[max(0,face_ya-60):min(h,face_ya+60),max(0,face_xa-65):min(w,face_xa+65)]
 meda=float(np.median(local[:,:,1]));medb=float(np.median(local[:,:,2]))
 lab[:,:,1]+=np.clip((target_a-meda)*smooth,-30,30)
 lab[:,:,2]+=np.clip((target_b-medb)*smooth,-30,30)
 raw=cv2.cvtColor(np.clip(lab,0,255).astype(np.uint8),cv2.COLOR_LAB2BGR)
 return raw
def detail(im):
 # Preserve texture; sharpen without turning grain/scratches into invented anatomical features.
 lab=cv2.cvtColor(im,cv2.COLOR_BGR2LAB)
 l,aa,bb=cv2.split(lab)
 smooth=cv2.bilateralFilter(l,5,26,7)
 clahe=cv2.createCLAHE(clipLimit=1.7,tileGridSize=(9,9)).apply(smooth)
 sharp=cv2.addWeighted(clahe,1.4,cv2.GaussianBlur(clahe,(0,0),1.1),-.4,0)
 l=cv2.addWeighted(l,.32,sharp,.68,0)
 return cv2.cvtColor(cv2.merge((l,aa,bb)),cv2.COLOR_LAB2BGR)
def main():
 from gradio_client import Client,handle_file
 src=Path('output/storia_v79_volti')
 try:
  cli=Client('sczhou/CodeFormer',verbose=False)
  print('CODEFORMER_CLIENT_CONNECTED',flush=True)
  print(str(cli.view_api(print_info=False))[:1100],flush=True)
 except Exception as e:
  print('CODEFORMER_UNAVAILABLE',str(e)[:350],flush=True)
  cli=None
 observations={}
 for key in keys:
  inp=cv2.imread(str(src/(key+'_FOTO_AI_HD.png')))
  if inp is None:raise RuntimeError('MISSING_PHOTO '+key)
  corrected=recolor(inp,key);corrected=detail(corrected)
  out=D/(key+'_COLOR_NATURAL.png')
  cv2.imwrite(str(out),corrected)
  final=corrected;source='offline_color_texture_refinement'
  if cli:
   try:
    raw=cli.predict(handle_file(str(out)),True,False,False,1,.82,api_name='/inference')
    imagep=raw[0] if isinstance(raw,(list,tuple)) else raw
    if isinstance(imagep,dict):imagep=imagep.get('path')
    restored=cv2.imread(str(imagep))
    if restored is None:raise RuntimeError('NO_MODEL_OUTPUT')
    restored=cv2.resize(restored,(720,1280))
    # Blend 65% restored face output, 35% source-guided HD to avoid model moving features too far.
    # Do not change any background outside the facial ROI.
    h,w=restored.shape[:2];Y,X=np.mgrid[:h,:w]
    if key=='KISS_1896':cx,cy,rx,ry=433,505,210,335
    else:cx,cy,rx,ry=389,490,215,345
    mask=np.exp(-2*((X-cx)**2/rx**2+(Y-cy)**2/ry**2))*0.68
    final=(corrected.astype('float32')*(1-mask[:,:,None])+restored.astype('float32')*mask[:,:,None]).clip(0,255).astype('uint8')
    source='codeformer_w082_local_facial_blend_068'
    print('CODEFORMER_DONE',key,flush=True)
   except Exception as e:
    print('CODEFORMER_CANDIDATE_UNAVAILABLE',key,type(e).__name__,str(e)[:400],flush=True)
  outfinal=D/(key+'_V79_FACE_RESTORED.png')
  cv2.imwrite(str(outfinal),final,[cv2.IMWRITE_PNG_COMPRESSION,3])
  observations[key]={'output':outfinal.name,'method':source,'face_identity_verified':False,'source_changed':False}
  print('FACE_COLOR_PHOTO',key,outfinal,flush=True)
 (D/'FACE_FIX_PROVENANCE.json').write_text(json.dumps(observations,indent=2,ensure_ascii=False))
 from PIL import Image,ImageDraw
 board=Image.new('RGB',(3*300,2*560),(10,12,16));draw=ImageDraw.Draw(board)
 for i,key in enumerate(keys):
  for j,path in enumerate([src/(key+'_ORIGINALE.png'),src/(key+'_FOTO_AI_HD.png'),D/(key+'_V79_FACE_RESTORED.png')]):
   board.paste(Image.open(path).convert('RGB').resize((296,523)),(j*300+2,i*560+30))
   draw.text((j*300+5,i*560+5),key+' '+['SOURCE','AI_BASE','REPAIRED'][j],fill='white')
 board.save(D/'BEFORE_AFTER_FACES.jpg',quality=91)
 print('FACE_FIX_FINISHED',flush=True)
if __name__=='__main__':main()
