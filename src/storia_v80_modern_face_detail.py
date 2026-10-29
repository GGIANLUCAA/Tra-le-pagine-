#!/usr/bin/env python3
"""V80 face detail revision: one CodeFormer 0.56 pass on three previously produced
source-locked 1896 and 1900 face photos. Preserve camera proportions and facial identity.
Output not historically verifiable at pixel level; never claim face match proven.
"""
from pathlib import Path
import cv2, numpy as np, json,hashlib
from PIL import Image,ImageDraw
D=Path("output/storia_v79_refined");D.mkdir(parents=True,exist_ok=True)
CONFIG=[
 dict(key="KISS_1896",folder="output/storia_v79_volti",photo="KISS_1896_V79_FACE_RESTORED.png",faces=[(182,320,195,255),(433,480,240,310)],w=0.54),
 dict(key="KISS_1896_LATE",folder="output/storia_v79_kiss_late",photo="KISS_1896_LATE_V79_FACE_RESTORED.png",faces=[(152,170,200,240),(481,253,222,290)],w=0.55),
 dict(key="KISS_1900",folder="output/storia_v79_volti",photo="KISS_1900_V79_FACE_RESTORED.png",faces=[(409,519,240,355)],w=0.55)
]
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def compare(a,b):
 h,w=a.shape[:2];aa=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY);bb=cv2.cvtColor(b,cv2.COLOR_BGR2GRAY)
 aa=cv2.GaussianBlur(cv2.resize(aa,(90,160)),(5,5),0).astype('float32').ravel()
 bb=cv2.GaussianBlur(cv2.resize(bb,(90,160)),(5,5),0).astype('float32').ravel()
 return float(np.corrcoef(aa,bb)[0,1])
def clean_small_scratchlines(im,key):
 # Deterministic film-scratch line cleanup in identified, ultra-thin known coordinates only,
 # without hallucinating entire objects / faces.
 line_positions={'KISS_1896':[(163,155,975),(198,160,900)],'KISS_1896_LATE':[(159,200,1270),(194,40,620)],'KISS_1900':[]}
 mask=np.zeros(im.shape[:2],np.uint8)
 for x,y0,y1 in line_positions[key]:
  mask[y0:y1,max(0,x-1):min(im.shape[1],x+2)]=255
 return cv2.inpaint(im,mask,1.1,cv2.INPAINT_TELEA) if mask.any() else im
def face_mask(h,w,faces,weight=0.78):
 yy,xx=np.mgrid[:h,:w]
 mask=np.zeros((h,w),np.float32)
 for cx,cy,rx,ry in faces:
  f=np.exp(-2.2*((xx-cx)**2/(rx**2)+(yy-cy)**2/(ry**2))).astype('float32')
  mask=np.maximum(mask,f)
 return np.clip(mask*weight,0,weight)
def natural_color(im,key):
 # Color-conservative adjustment only on selected faces; no changes to architecture/props.
 lab=cv2.cvtColor(im,cv2.COLOR_BGR2LAB).astype('float32')
 h,w=im.shape[:2]
 masks={s['key']:face_mask(h,w,s['faces'],1) for s in CONFIG}
 m=masks[key]
 if key=='KISS_1896_LATE':
  lab[:,:,1]+=11*m
  lab[:,:,2]+=13*m
 elif key=='KISS_1896':
  lab[:,:,2]-=4*m
 elif key=='KISS_1900':
  lab[:,:,1]+=1*m
  lab[:,:,2]-=3*m
 lab[:,:,0]=np.clip(lab[:,:,0]*1.045,0,255)
 return cv2.cvtColor(np.clip(lab,0,255).astype('uint8'),cv2.COLOR_LAB2BGR)
def main():
 from gradio_client import Client,handle_file
 try:
  client=Client("sczhou/CodeFormer",verbose=False)
  print("CODEFORMER_READY",flush=True)
 except Exception as e:
  print("MODEL_UNAVAILABLE",str(e)[:320],flush=True)
  client=None
 reports=[];previous=[];finals=[]
 for item in CONFIG:
  key=item['key'];src=Path(item['folder'])/item['photo']
  if not src.exists():raise RuntimeError("MISSING_REAL_AI_PHOTO "+str(src))
  pre=cv2.imread(str(src));h,w=pre.shape[:2]
  if (h,w)!=(1280,720):raise RuntimeError('PHOTO_SIZE_MISMATCH')
  tmp=D/(key+"_NATURAL.png")
  natural=natural_color(clean_small_scratchlines(pre,key),key)
  cv2.imwrite(str(tmp),natural)
  candidate=None;method="natural_color_and_scratch_clean_only"
  if client:
   try:
    result=client.predict(handle_file(str(tmp)),True,False,False,1,float(item["w"]),api_name="/inference")
    loc=result[0] if isinstance(result,(tuple,list)) else result
    if isinstance(loc,dict):loc=loc.get('path')
    candidate=cv2.imread(str(loc))
    if candidate is None:raise RuntimeError('MISSING_MODEL_IMAGE')
    candidate=cv2.resize(candidate,(w,h))
    method="CodeFormer_fidelity_"+str(item["w"])
   except Exception as e:
    print("FACE_MODEL_FAILED",key,str(e)[:420],flush=True)
  if candidate is not None:
   m=face_mask(h,w,item['faces'],weight=.77)
   photo=np.clip(natural.astype('float32')*(1-m[:,:,None])+candidate.astype('float32')*m[:,:,None],0,255).astype('uint8')
  else:photo=natural
  c=compare(pre,photo)
  print("CANDIDATE_STRUCTURE",key,c,flush=True)
  if not np.isfinite(c) or c<.81:
   photo=natural;method="REJECTED_STRONG_FACE_SHAPE_DRIFT:"+method
  # No reintroduction of global original grain
  dest=D/(key+"_V80_MODERN_PHOTO.png")
  cv2.imwrite(str(dest),photo,[cv2.IMWRITE_PNG_COMPRESSION,2])
  reports.append(dict(key=key,source_ai_file=src.as_posix(),source_ai_sha=sha(src),output=dest.name,output_sha=sha(dest),global_geometry_correlation=round(c,4),method=method,visual_human_identity_review="PENDING",facial_features_historical_verification="UNKNOWABLE_FROM_LOW_DETAIL_FILM"))
  previous.append(Image.fromarray(cv2.cvtColor(pre,cv2.COLOR_BGR2RGB)))
  finals.append(Image.fromarray(cv2.cvtColor(photo,cv2.COLOR_BGR2RGB)))
 canv=Image.new('RGB',(1200,3*700),(17,18,21));draw=ImageDraw.Draw(canv)
 for i,(a,b) in enumerate(zip(previous,finals)):
  canv.paste(a.resize((565,660)),(13,i*700+28))
  canv.paste(b.resize((565,660)),(616,i*700+28))
  draw.text((15,i*700+8),reports[i]['key']+' · OLD PHOTO',fill=(245,245,235))
  draw.text((620,i*700+8),reports[i]['key']+' · HIGH DETAIL PHOTO',fill=(245,245,235))
 canv.save(D/'V80_MODERN_FACES_QA.jpg',quality=92)
 (D/'FACE_DETAIL_QA_V80.json').write_text(json.dumps({"photos":reports,"not_new_historical_photographs":True,"human_review_required":True,"zero_vidu_credits":True},ensure_ascii=False,indent=2))
 print("V80_THREE_FACES_REFINED",flush=True)
if __name__=="__main__":main()
