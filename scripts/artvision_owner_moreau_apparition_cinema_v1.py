#!/usr/bin/env python3
"""One-time owner render: a NEW Cinema Standard for Moreau The Apparition (1876).
No museum fiction, no old master modifications, no publishing or paid API.
"""
import hashlib, json, subprocess, urllib.request, wave, math
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

out=Path('output/artvision-owner-moreau-apparition-cinema-v1')
out.mkdir(parents=True,exist_ok=True)
source=out/'ORIGINAL_ARTWORK.jpg'
file_page='https://commons.wikimedia.org/wiki/File:The_Apparition,_Gustave_Moreau_1876.jpg'
urls=['https://upload.wikimedia.org/wikipedia/commons/6/6c/The_Apparition%2C_Gustave_Moreau_1876.jpg',
      'https://commons.wikimedia.org/wiki/Special:Redirect/file/The_Apparition,_Gustave_Moreau_1876.jpg']
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
            if im.size!=(1684,2500): raise ValueError(f'wrong image size {im.size}')
        used=url
        break
    except Exception as exc:
        print('SOURCE_REJECTED',str(exc)[:130],flush=True)
if not used: raise RuntimeError('Source verification failed: render aborted; no simulated painting')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
print('SOURCE_SHA256',sha(source),flush=True)
shots=[
 ('THE VISION',4,(.57,.43,.45),(.57,.43,.42)),
 ('WHOLE_PAINTING',5,(.50,.50,1),(.50,.50,1)),
 ('SALOME',6,(.29,.73,.57),(.30,.69,.53)),
 ('THE SEVERED HEAD',6,(.56,.43,.48),(.58,.41,.43)),
 ('HER GESTURE',5.5,(.35,.57,.55),(.36,.54,.51)),
 ('THE TEMPLE',5.5,(.52,.17,.57),(.51,.22,.52)),
 ('THE COURT',6,(.20,.45,.60),(.24,.48,.53)),
 ('THE JEWELS',6,(.34,.78,.48),(.35,.76,.45)),
 ('THE HALO',6,(.56,.41,.46),(.57,.42,.42)),
 ('SALOME AND VISION',6,(.45,.61,.72),(.47,.59,.68)),
 ('WHOLE_PAINTING',8,(.50,.50,1),(.50,.50,1)),
]
fps=20;W,H=1080,1920
duration=sum(s[1] for s in shots)
# Original atmospheric score. No downloaded song, no third-party performance rights.
sr=22050;n=round((duration+.3)*sr);t=np.arange(n)/sr
mix=np.zeros(n,dtype=np.float64)
prog=[(98,146.83,196),(82.41,123.47,164.81),(110,164.81,220),(73.42,110,146.83)]
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
d.text((540,87),'THE APPARITION',font=f1,anchor='mm',fill=(236,223,196))
d.text((540,1816),'GUSTAVE MOREAU · 1876',font=f2,anchor='mm',fill=(220,213,204))
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
            cv2.putText(frame,'THE APPARITION',(65,135),cv2.FONT_HERSHEY_SIMPLEX,1.12,(236,230,213),2,cv2.LINE_AA)
            cv2.putText(frame,'GUSTAVE MOREAU  |  1876',(66,179),cv2.FONT_HERSHEY_SIMPLEX,.47,(216,205,189),1,cv2.LINE_AA)
        p.stdin.write(frame.tobytes())
        if k==count//2 and len(contact)<12:
            contact.append(cv2.resize(frame,(216,384),interpolation=cv2.INTER_AREA))
p.stdin.close()
if p.wait()!=0:raise RuntimeError('FFmpeg rendering failed')
sheet=np.full((1152,864,3),16,dtype=np.uint8)
for j,frame in enumerate(contact):sheet[(j//4)*384:(j//4+1)*384,(j%4)*216:(j%4+1)*216]=frame
cv2.imwrite(str(out/'CONTATTO_REGIA.jpg'),sheet)

rights={'painting':"L'Apparition (watercolour, 1876)",'artist':'Gustave Moreau','date':1876,
        'museum':"Musée d'Orsay / Louvre Département des Arts graphiques",'accession':'RF 2130, Recto',
        'painting_cm':{'height':106,'width':72.2},
        'source_page':file_page,'original_download_url':used,'original_sha256':sha(source),'pixels':[1684,2500],
        'source_status':'PD-Art/PDM Commons; territorial/commercial reuse conditions pending final review',
        'museum_object':'https://www.musee-orsay.fr/en/artworks/lapparition-203510',
        'score':'Original synthesised score, no third-party recording',
        'museum_reconstruction':'none; Cinema Standard only','commercial_publication':'NOT CLEARED'}
(out/'FONTI_E_DIRITTI.json').write_text(json.dumps(rights,indent=2),encoding='utf8')
(out/'STORYBOARD_REGIA.json').write_text(json.dumps({'camera_shots':[{'subject':a,'seconds':b,'from':c,'to':d} for a,b,c,d in shots],
    'total_seconds':duration,'format':'cinema_standard','needs_visual_review':True},indent=2),encoding='utf8')
posts={'public_title':'The Apparition — Gustave Moreau (1876)',
'facebook':'Un volto sospeso nel vuoto, una luce impossibile, una donna immobile. Nel 1876 Gustave Moreau dipinse questa inquietante visione di Salomè. Un acquerello simbolista che trasforma un episodio biblico in un sogno enigmatico. #arte #storiadellarte #GustaveMoreau',
'instagram':'Una testa luminosa fluttua davanti a Salomè. Perché Moreau dipinse una scena tanto inquietante? The Apparition, 1876. #ArtHistory #Symbolism #Moreau',
'tiktok':'Una visione impossibile, dipinta nel 1876. Guarda lo sguardo di Salomè e la luce nel buio. #arttok #arte #symbolism',
'youtube_shorts':'The Apparition (1876): la visione di Salomè secondo Gustave Moreau. Acquerello, Musée d’Orsay, RF 2130. Una regia sui dettagli originali.',
'credits':'Gustave Moreau, L’Apparition (1876), watercolour, Musée d’Orsay / Louvre, RF 2130. Original reproduction: Wikimedia Commons, PD-Art/PDM; territorial rights review pending. Original audio generated for this video.'}
(out/'SOCIAL_POSTS.json').write_text(json.dumps(posts,ensure_ascii=False,indent=2),encoding='utf8')
(out/'ISTRUZIONI.md').write_text('THE APPARITION — Cinema Standard da revisionare. MP4 + copertina + quattro testi specifici social + fonti + storyboard. Opera e audio autentici/originali. Il video NON è Gold e NON è pubblicato. Verificare artisticamente il MP4 a velocità normale e controllare diritti territoriali prima di qualsiasi distribuzione. Non aggiornare i 26/36 Museum perché questa è la seconda coda.\n',encoding='utf8')
print('NEW_MP4_GENERATED_SHA256',sha(out/'VIDEO_REVIEW.mp4'),flush=True)
