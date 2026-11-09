#!/usr/bin/env python3
"""One-time owner render: a NEW Cinema Standard for The Alchemist (1771).
No museum fiction, no old master modifications, no publishing or paid API.
"""
import hashlib, json, subprocess, urllib.request, wave, math
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

out=Path('output/artvision-owner-alchemist-cinema-v1')
out.mkdir(parents=True,exist_ok=True)
source=out/'ORIGINAL_ARTWORK.jpg'
file_page='https://commons.wikimedia.org/wiki/File:Joseph_Wright_of_Derby_The_Alchemist.jpg'
urls=['https://upload.wikimedia.org/wikipedia/commons/9/9c/Joseph_Wright_of_Derby_The_Alchemist.jpg',
      'https://commons.wikimedia.org/wiki/Special:Redirect/file/Joseph_Wright_of_Derby_The_Alchemist.jpg']
used=None
for url in urls:
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'ArtVision/1.0 (authentic PD artwork verification; open-source rendering)'})
        with urllib.request.urlopen(req,timeout=70) as res: data=res.read(12000000)
        if len(data)<500000: raise ValueError('too small')
        source.write_bytes(data)
        with Image.open(source) as im:
            im.verify()
        with Image.open(source) as im:
            if im.size!=(4724,6126): raise ValueError(f'wrong image size {im.size}')
        used=url
        break
    except Exception as exc:
        print('SOURCE_REJECTED',str(exc)[:130],flush=True)
if not used: raise RuntimeError('Source verification failed: render aborted; no simulated painting')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
print('SOURCE_SHA256',sha(source),flush=True)
shots=[
 ('REACTION',4,(.57,.71,.47),(.56,.71,.43)),
 ('WHOLE_PAINTING',5,(.5,.5,1),(.5,.5,1)),
 ('ALCHEMIST',6,(.48,.75,.60),(.46,.75,.53)),
 ('LUMINOUS_FLASK',6,(.60,.70,.45),(.57,.70,.40)),
 ('WITNESSES',6,(.28,.60,.49),(.29,.60,.45)),
 ('APPARATUS',6,(.70,.55,.53),(.69,.54,.47)),
 ('WORKSHOP',6,(.37,.45,.65),(.40,.44,.58)),
 ('GOTHIC_WINDOWS',6,(.78,.28,.58),(.75,.30,.52)),
 ('ALCHEMIST_DETAIL',6,(.49,.75,.52),(.45,.76,.48)),
 ('FLASK_DETAIL',6,(.57,.71,.37),(.56,.71,.34)),
 ('WHOLE_PAINTING',8,(.5,.5,1),(.5,.5,1)),
]
fps=20;W,H=720,1280
duration=sum(s[1] for s in shots)
# Original atmospheric score. No downloaded song, no third-party performance rights.
sr=22050;n=round((duration+.3)*sr);t=np.arange(n)/sr
mix=np.zeros(n,dtype=np.float64)
prog=[(110,164.81,220),(87.31,130.81,174.61),(73.42,110,146.83),(82.41,123.47,164.81)]
for j,start in enumerate(np.arange(0,duration,8.0)):
    end=min(duration+.3,start+9)
    a,b=int(start*sr),min(n,int(end*sr));u=t[a:b]-start
    env=np.minimum(u/1.2,1)*np.minimum((end-start-u)/1.4,1)
    for k,f in enumerate(prog[j%4]):
        mix[a:b]+=.042*np.clip(env,0,1)*(np.sin(2*np.pi*f*u+.05*np.sin(2*np.pi*.13*u))+.12*np.sin(2*np.pi*f*2*u))/(1+k*.25)
    for beat in [0,3,6]:
        x=int((start+beat)*sr)
        if x<n:
            m=min(int(2.1*sr),n-x);z=np.arange(m)/sr
            f=prog[j%4][beat//3]*2
            mix[x:x+m]+=.023*np.exp(-2.4*z)*np.sin(2*np.pi*f*z)
mix+=.025*np.sin(2*np.pi*55*t)
mix*=np.minimum(1,t/2.5)*np.clip((duration-t)/3,0,1)
mix=np.tanh(mix*1.45)
with wave.open(str(out/'SCORE_ORIGINALE.wav'),'wb') as f:
    f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr)
    f.writeframes((mix*32767).astype('<i2').tobytes())

img=cv2.imread(str(source),cv2.IMREAD_COLOR)
assert img is not None
sh,sw=img.shape[:2]
if sh>3200:
    q=3200/sh;img=cv2.resize(img,(int(sw*q),3200),interpolation=cv2.INTER_AREA)
sh,sw=img.shape[:2]
cover=Image.new('RGB',(1080,1920),(11,13,17))
painting=Image.open(source).convert('RGB')
painting.thumbnail((1080,1510),Image.Resampling.LANCZOS)
cover.paste(painting,((1080-painting.width)//2,184))
d=ImageDraw.Draw(cover)
d.rectangle((0,0,1080,180),fill=(11,13,17))
d.rectangle((0,1715,1080,1920),fill=(11,13,17))
f1=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',72)
f2=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',28)
d.text((540,87),'THE ALCHEMIST',font=f1,anchor='mm',fill=(236,223,196))
d.text((540,1816),'JOSEPH WRIGHT OF DERBY · 1771',font=f2,anchor='mm',fill=(220,213,204))
cover.save(out/'COPERTINA.jpg',quality=93)

cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(fps),'-i','pipe:0',
     '-i',str(out/'SCORE_ORIGINALE.wav'),'-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',
     '-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(out/'VIDEO_REVIEW.mp4')]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
contact=[]
for i,(label,sec,start,end) in enumerate(shots):
    count=int(sec*fps)
    for k in range(count):
        q=k/max(1,count-1);e=q*q*(3-2*q)
        x,y,h=(start[v]*(1-e)+end[v]*e for v in range(3))
        if label=='WHOLE_PAINTING':
            frame=np.full((H,W,3),(16,14,12),dtype=np.uint8)
            hh=min(H,int(W*sh/sw))
            frame[(H-hh)//2:(H-hh)//2+hh]=cv2.resize(img,(W,hh),interpolation=cv2.INTER_AREA)
        else:
            ch=min(sh,int(sh*h));cw=min(sw,int(ch*W/H))
            xx=max(0,min(sw-cw,int(x*sw-cw/2)))
            yy=max(0,min(sh-ch,int(y*sh-ch/2)))
            frame=cv2.resize(img[yy:yy+ch,xx:xx+cw],(W,H),interpolation=cv2.INTER_AREA)
        if i==0 and k<3*fps:
            overlay=frame.copy()
            cv2.rectangle(overlay,(0,72),(W,221),(13,14,18),-1)
            frame=cv2.addWeighted(overlay,.68,frame,.32,0)
            cv2.putText(frame,'THE ALCHEMIST',(65,135),cv2.FONT_HERSHEY_SIMPLEX,1.12,(236,230,213),2,cv2.LINE_AA)
            cv2.putText(frame,'JOSEPH WRIGHT  |  1771',(66,179),cv2.FONT_HERSHEY_SIMPLEX,.47,(216,205,189),1,cv2.LINE_AA)
        p.stdin.write(frame.tobytes())
        if k==count//2 and len(contact)<12:
            contact.append(cv2.resize(frame,(216,384),interpolation=cv2.INTER_AREA))
p.stdin.close()
if p.wait()!=0:raise RuntimeError('FFmpeg rendering failed')
sheet=np.full((1152,864,3),16,dtype=np.uint8)
for j,frame in enumerate(contact):sheet[(j//4)*384:(j//4+1)*384,(j%4)*216:(j%4+1)*216]=frame
cv2.imwrite(str(out/'CONTATTO_REGIA.jpg'),sheet)

rights={'painting':'The Alchemist Discovering Phosphorus','artist':'Joseph Wright of Derby','date':1771,
        'museum':'Derby Museum and Art Gallery','accession':'1883-152','painting_cm':{'height':127,'width':101.6},
        'source_page':file_page,'original_download_url':used,'original_sha256':sha(source),'pixels':[4724,6126],
        'source_status':'PD-Art/PDM Commons; check Italian territorial reuse before commercial release',
        'museum_object':'https://derbymuseums.org/collection/joseph-wright-of-derby/',
        'score':'Original music synthesized for this render; no third-party recording',
        'museum_reconstruction':'none','commercial_publication':'NOT CLEARED'}
(out/'FONTI_E_DIRITTI.json').write_text(json.dumps(rights,indent=2),encoding='utf8')
(out/'STORYBOARD_REGIA.json').write_text(json.dumps({'camera_shots':[{'subject':a,'seconds':b,'from':c,'to':d} for a,b,c,d in shots],
    'total_seconds':duration,'format':'cinema_standard','needs_visual_review':True},indent=2),encoding='utf8')
posts={'public_title':'The Alchemist — Joseph Wright of Derby (1771)',
'facebook':'Una scoperta che sembra magia. Nel 1771 Joseph Wright dipinge il momento in cui una luce inattesa trasforma un laboratorio in un teatro dello stupore. Guarda chi osserva la reazione nell’ombra. #arte #storiadellarte',
'instagram':'Luce, mistero e curiosità scientifica: quanti dettagli riesci a vedere? The Alchemist, 1771. #ArtHistory #JosephWright #Arte',
'tiktok':'Un lampo misterioso in un laboratorio del 1771. Il dettaglio più sorprendente è nascosto nell’ombra. #arttok #arte',
'youtube_shorts':'The Alchemist (1771) di Joseph Wright: un laboratorio, una luce sorprendente e il confine tra scienza e meraviglia.',
'credits':'Joseph Wright of Derby, The Alchemist Discovering Phosphorus (1771), Derby Museum and Art Gallery. Artwork: Wikimedia Commons PD-Art/PDM. Original score: generated for this video.'}
(out/'SOCIAL_POSTS.json').write_text(json.dumps(posts,ensure_ascii=False,indent=2),encoding='utf8')
(out/'ISTRUZIONI.md').write_text('THE ALCHEMIST — Cinema Standard da revisionare. MP4 + copertina + quattro testi specifici social + fonti + storyboard. Opera e audio autentici/originali. Il video NON è Gold e NON è pubblicato. Verificare artisticamente il MP4 a velocità normale e controllare diritti territoriali prima di qualsiasi distribuzione. Non aggiornare i 26/36 Museum perché questa è la seconda coda.\n',encoding='utf8')
print('NEW_MP4_GENERATED_SHA256',sha(out/'VIDEO_REVIEW.mp4'),flush=True)
