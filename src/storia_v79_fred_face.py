#!/usr/bin/env python3
"""V79 original 1894 Fred Ott source photographic face recovery. 1 free model call, no paid credits."""
from pathlib import Path
import cv2, numpy as np, json
from PIL import Image,ImageDraw
SRC=Path('output/storia_v79_volti')
OUT=Path('output/storia_v79_fred');OUT.mkdir(parents=True,exist_ok=True)
def main():
 from gradio_client import Client,handle_file
 a=cv2.imread(str(SRC/'SNEEZE_1894_COLORE_BASE.jpg'))
 if a is None:raise RuntimeError("No genuine historical source frame")
 a=cv2.resize(a,(720,1280))
 lab=cv2.cvtColor(a,cv2.COLOR_BGR2LAB).astype(np.float32)
 lab[:,:,1]=128+(lab[:,:,1]-128)*.48
 lab[:,:,2]=128+(lab[:,:,2]-128)*.52
 b=cv2.cvtColor(np.clip(lab,0,255).astype(np.uint8),cv2.COLOR_LAB2BGR)
 p=OUT/'FRED_1894_COLORE_NATURALE.png';cv2.imwrite(str(p),b)
 ok=False
 try:
  cli=Client('sczhou/CodeFormer',verbose=False)
  res=cli.predict(handle_file(str(p)),True,False,False,1,.75,api_name='/inference')
  r=res[0] if isinstance(res,(tuple,list)) else res
  if isinstance(r,dict):r=r.get('path')
  c=cv2.imread(str(r))
  if c is None:raise RuntimeError('AI face output not readable')
  c=cv2.resize(c,(720,1280))
  # Use restored face detail locally, preserve background and costume.
  yy,xx=np.mgrid[:1280,:720]
  mask=np.exp(-2*((xx-315)**2/315**2+(yy-515)**2/460**2))*.77
  fin=(b.astype('float32')*(1-mask[:,:,None])+c.astype('float32')*mask[:,:,None]).clip(0,255).astype('uint8')
  ok=True
 except Exception as e:
  print("FRED_AI_NOT_AVAILABLE",str(e)[:500],flush=True)
  fin=b
 out=OUT/'SNEEZE_1894_V79_FACE_RESTORED.png'
 cv2.imwrite(str(out),fin,[cv2.IMWRITE_PNG_COMPRESSION,3])
 bw=cv2.imread(str(SRC/'SNEEZE_1894_ORIGINALE.png'))
 board=Image.new('RGB',(3*300,550),(12,14,18));d=ImageDraw.Draw(board)
 for i,im in enumerate([cv2.resize(bw,(720,1280)),a,fin]):
  board.paste(Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB)).resize((295,520)),(i*300+2,25))
  d.text((i*300+5,3),['1894 SOURCE','DDCOLOR','FACE RESTORED'][i],fill='white')
 board.save(OUT/'FRED_1894_RESTAURO_CONFRONTO.jpg',quality=92)
 (OUT/'FRED_1894_QA.json').write_text(json.dumps({"success_model":ok,"method":"CodeFormer w=0.75 local weighted face fusion if model served; otherwise DDColor base","face_identity_is_hypothetical":True,"rights":"Wikimedia Commons public domain source; verify Italian reuse","no_paid_api":True},indent=2),encoding='utf8')
 print("FRED_PHOTO_GENERATED",ok,out,flush=True)
if __name__=="__main__":main()
