#!/usr/bin/env python3
import os,io,base64,hashlib,json,urllib.request,subprocess
import numpy as np,cv2
from PIL import Image,ImageOps,ImageEnhance
from pathlib import Path
root=Path(os.getenv('RUNNER_TEMP','/tmp'))/'cane_olympic'
root.mkdir(exist_ok=True)
url='https://commons.wikimedia.org/wiki/Special:FilePath/King_County_Aquatic_Center_diving_tower_and_well_-_23_November_2022.jpg?width=960'
req=urllib.request.Request(url,headers={'User-Agent':'TraLePaginePersonalVideo/1.0 (source from Wikimedia Commons)','Accept':'image/jpeg'})
with urllib.request.urlopen(req,timeout=45) as resp: raw=resp.read(6500000)
photo=Image.open(io.BytesIO(raw));photo.load();print('PHOTO',photo.size)
photo=ImageOps.fit(photo.convert('RGB'),(720,1280),method=Image.Resampling.LANCZOS,centering=(.45,.5))
repo=os.environ['GITHUB_REPOSITORY'];sha='6ad7cb0997a27957c50065039687c3df56b4614d'
blob=subprocess.check_output(['gh','api',f'repos/{repo}/git/blobs/{sha}'],text=True)
src=json.loads(blob);im0=Image.open(io.BytesIO(base64.b64decode(src['content']))).convert('RGB').resize((720,1280))
im=cv2.cvtColor(np.asarray(im0),cv2.COLOR_RGB2BGR)
h,w=im.shape[:2];m=np.zeros((h,w),np.uint8)
cv2.ellipse(m,(320,565),(273,358),0,0,360,cv2.GC_PR_BGD,-1)
cv2.ellipse(m,(310,545),(190,303),0,0,360,cv2.GC_PR_FGD,-1)
for c,a in [((393,390),(94,119)),((310,620),(146,183)),((185,508),(55,52)),((185,752),(34,98)),((476,738),(38,126)),((316,834),(39,83))]:cv2.ellipse(m,c,a,0,0,360,cv2.GC_FGD,-1)
cv2.rectangle(m,(0,0),(720,210),cv2.GC_BGD,-1);cv2.rectangle(m,(0,975),(720,1280),cv2.GC_BGD,-1);cv2.rectangle(m,(590,210),(720,970),cv2.GC_BGD,-1)
cv2.grabCut(im,m,None,np.zeros((1,65),np.float64),np.zeros((1,65),np.float64),7,cv2.GC_INIT_WITH_MASK)
alpha=np.where((m==1)|(m==3),255,0).astype('uint8');alpha=cv2.GaussianBlur(alpha,(5,5),1)
cut=np.dstack((np.asarray(im0),alpha))[220:966,62:590,:]
dog=Image.fromarray(cut,'RGBA');dog.thumbnail((240,347),Image.Resampling.LANCZOS)
x=int(os.environ.get('DOG_X','266')); y=int(os.environ.get('DOG_Y','630'))
base=photo.convert('RGBA');base.alpha_composite(dog,(x,y))
out=ImageEnhance.Contrast(base.convert('RGB')).enhance(1.04)
p=root/'CANE_OLIMPICO_PRIMO_FOTOGRAMMA.jpg';out.save(p,quality=94,subsampling=0,optimize=True)
body=p.read_bytes();digest=hashlib.sha256(body).hexdigest()
resp=subprocess.run(['gh','api','-X','POST',f'repos/{repo}/git/blobs','--input','-'],input=json.dumps({'content':base64.b64encode(body).decode(),'encoding':'base64'}),capture_output=True,text=True,check=True)
blob_sha=json.loads(resp.stdout)['sha']
reqid=os.environ['STAGE_REQUEST_ID']
d={'schema':'cane_olympic_v3_anchor','id':reqid,'git_blob_sha':blob_sha,'sha256':digest,'stage':'ready','frame_size':[720,1280],'public_media_released':False,'vidu_credits_spent':0,'source_dog_from':'previous approved frame of grey-beige dog','photo_background':'King County Aquatic Center diving tower and well - 23 November 2022.jpg','attribution':'Tanis Coralee Leonhardi / Wikimedia Commons CC BY-SA 4.0','license_url':'https://creativecommons.org/licenses/by-sa/4.0/','source_url':'https://commons.wikimedia.org/wiki/File:King_County_Aquatic_Center_diving_tower_and_well_-_23_November_2022.jpg'}
serialized=base64.b64encode((json.dumps(d,indent=2)+'\n').encode()).decode()
subprocess.run(['gh','api','-X','PUT',f'repos/{repo}/contents/queue/cane_olympic/{reqid}.json','-f','branch=main','-f',f'message=Stage private olympic dog source {reqid}','-f','content='+serialized],check=True,capture_output=True,text=True)
print('OLYMPIC_ANCHOR_READY',reqid,blob_sha,digest,len(body),dog.size)
