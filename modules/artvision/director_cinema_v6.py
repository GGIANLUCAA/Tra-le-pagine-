#!/usr/bin/env python3
"""ArtVision V6 / cinema-led hand-curated Van Gogh original-art film.
Not a slide show: the edit maps perceptual motifs and music to distinct gestures.
Input: licensed museum images from the existing open-access export.
No generative modifications of artworks. Music attribution belongs in public post caption.
"""
from __future__ import annotations
import argparse, json, math, shutil, subprocess, time
from pathlib import Path
from functools import lru_cache
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

W,H,FPS = 1080,1920,24
ARTIST = 'VINCENT VAN GOGH'
MUSIC_BY='MUSIC BY KEVIN MACLEOD'
# Hand-composed dramatic composition. Fractions indicate semantic loci within each real work.
# mode: portrait=immersive, texture=close observation, reveal=detail->broad crop,
# whole=full artwork, breath=near-still, glide=short evocative camera.
# The cross-links of blues/yellows, faces/gestures, horizons/tunnels are intentional.
STORY = [
# Movement I — face to color: an arresting portrait hook, the world seen through pigment.
('Self-Portrait with a Straw Hat','portrait',(.51,.32),3.0,'Eyes and yellow straw hat; opening human connection','cut'),
('Self-Portrait with a Straw Hat','texture',(.56,.31),2.25,'Signature swirling face/hat impasto','cut'),
('Irises','portrait',(.34,.40),2.6,'Blue iris petals answer orange hat','match'),
('Sunflowers','texture',(.47,.54),2.5,'Gold texture answers blue iris','match'),
('Roses','portrait',(.52,.49),2.85,'Green and white blossoms','dissolve'),
('Roses','texture',(.38,.34),2.5,'White petals in mint green','cut'),
('Oleanders','portrait',(.53,.49),2.65,'Pink oleanders echo roses','match'),
('Oleanders','texture',(.65,.37),2.4,'Oleander petals detail','cut'),
('Bouquet of Flowers','portrait',(.49,.46),2.65,'Burst of wild colors in vase','cut'),
('Bouquet of Flowers','texture',(.55,.77),2.25,'Warm red petals against dark palette','cut'),
('Irises','whole',(.50,.50),3.6,'First collective release: full Irises','dissolve'),
# Movement II — countryside; graphic match cuts of sky, plants and gestural brushwork.
('Wheat Field with Cypresses','portrait',(.52,.31),3.0,'Sky vortices, luminous wheat','cut'),
('Wheat Field with Cypresses','texture',(.70,.34),2.50,'Cypress texture against sky','cut'),
('Two Poplars','portrait',(.53,.37),2.9,'Tree verticals and cobalt skyline','match'),
('Two Poplars','texture',(.48,.20),2.40,'Blue-sky paint and yellow branches','cut'),
('The Large Plane Trees','portrait',(.40,.39),2.75,'Structure of tree trunks','match'),
('The Large Plane Trees','texture',(.72,.69),2.45,'Stones, trees and road','cut'),
('The Flowering Orchard','portrait',(.54,.51),3.25,'Air and green branches','dissolve'),
('The Flowering Orchard','texture',(.47,.26),2.45,'Delicate tree blossoms','cut'),
('Women Picking Olives','portrait',(.47,.50),2.95,'Human figures among pale olive trees','match'),
('Women Picking Olives','texture',(.36,.54),2.4,'Gesture of woman in olive grove','cut'),
('Olive Trees','portrait',(.52,.48),3.0,'Purple earth and olive foliage','cut'),
('Olive Trees','texture',(.62,.66),2.40,'Lavender soil impasto','cut'),
('Wheat Field with Cypresses','whole',(.5,.5),3.9,'Hold entire sky and wheat field','dissolve'),
# Movement III — human faces and touch, slow intimate half-time.
('First Steps','portrait',(.57,.56),3.15,'Tender scene, parent and child','cut'),
('First Steps','texture',(.44,.56),2.6,'Child reaching out','cut'),
('First Steps','whole',(.5,.5),3.3,'A full emotional composition','dissolve'),
('Adeline Ravoux','portrait',(.52,.37),3.0,'Adeline portrait - a still gaze','match'),
('Adeline Ravoux','texture',(.52,.27),2.45,'Luminous cheek and face','cut'),
('La Berceuse','portrait',(.53,.34),3.2,'An intimate quiet mother','dissolve'),
('La Berceuse','texture',(.49,.69),2.45,'Interlaced hands and shawl','cut'),
("L'Arlésienne",'portrait',(.51,.40),2.9,'Profile of woman reading','match'),
("L'Arlésienne",'texture',(.56,.76),2.4,'Book and hands, inward world','cut'),
('The Zouave','portrait',(.50,.38),2.7,'Human stare, vibrant uniform','cut'),
('Self-Portrait with a Straw Hat','portrait',(.50,.36),2.9,'Artist returns in a mirror','match'),
('Self-Portrait with a Straw Hat','whole',(.5,.5),3.1,'Whole self-portrait held','dissolve'),
# Movement IV — pulse; shorter yet legible montage with painterly match cuts.
('Sunflowers','portrait',(.50,.50),2.5,'Golden fire of the sunflowers','match'),
('Sunflowers','texture',(.57,.53),2.30,'Golden spiked petals','cut'),
('Irises','texture',(.65,.54),2.35,'Blues answer bright yellows','match'),
('Oleanders','texture',(.51,.38),2.4,'Flower forms in pink and green','cut'),
('Shoes','portrait',(.50,.51),2.65,'A painterly image of worn shoes','cut'),
('Shoes','texture',(.65,.47),2.50,'Stitches and laces texture','cut'),
('Corridor in the Asylum','portrait',(.49,.48),2.75,'Graphic tunnel, inner perspective','dissolve'),
('Corridor in the Asylum','texture',(.53,.54),2.35,'The converging lines of corridor','cut'),
('Two Poplars','portrait',(.54,.34),2.75,'Cobalt sky and trees return','match'),
('Wheat Field with Cypresses','portrait',(.54,.40),2.90,'Landscape becomes triumphantly light','cut'),
('Bouquet of Flowers','portrait',(.51,.48),2.60,'An incandescent bouquet','match'),
# Movement V — return and release, explicit variation (some whole first, some detail first).
('The Flowering Orchard','whole',(.5,.5),3.5,'Nature revealed in full, a visual exhale','dissolve'),
('Olive Trees','whole',(.5,.5),3.0,'Pastel land held for contemplation','cut'),
('Roses','portrait',(.52,.51),2.65,'Bloom light motif returns','match'),
('Irises','portrait',(.43,.47),2.85,'The blue iris refrain','cut'),
('Irises','texture',(.61,.56),2.25,'Final blue detail, nearly still','cut'),
('Sunflowers','whole',(.5,.5),3.35,'Final answer: golden flower composition','dissolve'),
('Self-Portrait with a Straw Hat','portrait',(.51,.33),3.25,'Look back to the artist one last time','match'),
('Irises','whole',(.50,.50),4.15,'Quiet full work closes circular narrative','dissolve'),
]
# Directed cinematic shots, transformed to exactly 150 seconds.

class Shot:
 def __init__(self,k,source,kind,focus,duration,why,join):
  self.index=k;self.art=source;self.kind=kind;self.focus=focus;self.duration=duration;self.why=why;self.join=join

def load_artworks(root):
 root=Path(root)
 obj=json.loads((root/'artworks.json').read_text())
 artworks=obj['metadata']
 output=[]
 for rec in artworks:
  p=root/'original_images'/Path(rec['file']).name
  if not p.is_file():continue
  try:
   with Image.open(p) as im:
    im.verify()
   rec=dict(rec,file=str(p));output.append(rec)
  except Exception:pass
 return output

def resolve_items(artworks, seconds):
 sc=[]
 for title,kind,focus,weight,why,join in STORY:
  match=next((item for item in artworks if title.lower() in item['title'].lower()),None)
  if not match:continue
  sc.append(Shot(len(sc),match,kind,focus,weight,why,join))
 if len(sc)<37:raise RuntimeError(f'Only {len(sc)} curated shots found. Need >=37 before rendering, never guess paintings.')
 total=sum(x.duration for x in sc)
 scale=seconds/total
 for x in sc:x.duration*=scale
 return sc

def compute(src,focal,zoom=1.,motion=(0,0)):
 ih,iw=src.shape[:2]
 # All crops come from the original artwork; no synthesized content.
 ratio=W/H
 if iw/ih>ratio:
  bh=ih;bw=ih*ratio
 else:
  bw=iw;bh=iw/ratio
 cw=bw/zoom;ch=bh/zoom
 fx=np.clip(focal[0]+motion[0],.12,.88);fy=np.clip(focal[1]+motion[1],.12,.88)
 center=(max(cw/2,min(iw-cw/2,fx*iw)),max(ch/2,min(ih-ch/2,fy*ih)))
 rect=cv2.getRectSubPix(src,(max(2,int(cw)),max(2,int(ch))),center)
 return cv2.resize(rect,(W,H),interpolation=cv2.INTER_AREA if rect.shape[1]>W else cv2.INTER_CUBIC)

def gradient_bg(src):
 # only used for true full-work reveal; full painting not color-graded
 sm=cv2.resize(src,(W//7,H//7),interpolation=cv2.INTER_AREA)
 bg=cv2.resize(sm,(W,H),interpolation=cv2.INTER_CUBIC)
 bg=cv2.GaussianBlur(bg,(0,0),50)
 return cv2.addWeighted(bg,.48,np.zeros_like(bg),.52,0)

def whole(src, pre=None):
 if pre is None:pre=gradient_bg(src)
 bh,bw=src.shape[:2]
 scale=min(W*.95/bw,H*.88/bh)
 nw=int(bw*scale);nh=int(bh*scale)
 art=cv2.resize(src,(nw,nh),interpolation=cv2.INTER_AREA if scale<1 else cv2.INTER_CUBIC)
 x=(W-nw)//2;y=(H-nh)//2
 canvas=pre.copy()
 # restrained drop shadow using real image silhouette (background only)
 cv2.rectangle(canvas,(max(0,x-7),max(0,y-7)),(min(W-1,x+nw+7),min(H-1,y+nh+7)),(12,12,14),-1)
 canvas[y:y+nh,x:x+nw]=art
 return canvas

def ease(p):
 p=max(0.,min(1.,p));return p*p*(3-2*p)

def frame_shot(src, shot, t, bg=None, full=None):
 k=shot.kind;f=shot.focus
 s=ease(t)
 if k=='whole':return full.copy() if full is not None else whole(src,bg)
 if k=='portrait':zoom=1.055+.06*s;movement=(.022*(s-.5),-.010*(s-.5))
 elif k=='texture':zoom=1.43+.02*s;movement=(.006*(s-.5),-.006*(s-.5))
 elif k=='glide':zoom=1.09+.09*s;movement=(.050*(s-.5),-.018*(s-.5))
 else:zoom=1.03+.05*s;movement=(0,0)
 ih,iw=src.shape[:2]
 # Avoid zooming beyond reasonable effective pixel density; native 2k+ strongly preferred.
 bw=min(iw,ih*W/H)
 source_per_video=bw/W
 cap=min(zoom,max(1.02,source_per_video*.92))
 return compute(src,f,cap,movement)

def load_images(shots):
 result={}
 for shot in shots:
  id=shot.art['id']+'_'+shot.art['source']
  if id in result:continue
  with Image.open(shot.art['file']) as orig:
   im=ImageOps.exif_transpose(orig).convert('RGB')
   if max(im.size)>4200:im.thumbnail((4200,4200),Image.Resampling.LANCZOS)
  result[id]=cv2.cvtColor(np.array(im),cv2.COLOR_RGB2BGR)
 return result

def label_title(img,t):
 # invariant cinema-intro typography, adapted to perceived readability over light art
 alpha=max(0.,min(1.,1.0-(max(0,t-2.9)/.55)))
 if alpha==0:return img
 im=Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB)).convert('RGBA')
 ol=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(ol)
 d.rounded_rectangle((56,H-580,W-56,H-330),radius=10,fill=(5,8,13,int(190*alpha)))
 paths=['/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
 ft=ImageFont.truetype(paths[0],62)
 fm=ImageFont.truetype(paths[1],21)
 name='VINCENT VAN GOGH';bbox=d.textbbox((0,0),name,font=ft)
 d.text(((W-(bbox[2]-bbox[0]))/2,H-533),name,fill=(255,251,243,int(255*alpha)),font=ft)
 sub=MUSIC_BY;bb=d.textbbox((0,0),sub,font=fm)
 d.text(((W-(bb[2]-bb[0]))/2,H-399),sub,fill=(218,208,192,int(246*alpha)),font=fm)
 d.line((130,H-425,W-130,H-425),fill=(218,198,168,int(186*alpha)),width=2)
 return cv2.cvtColor(np.asarray(Image.alpha_composite(im,ol).convert('RGB')),cv2.COLOR_RGB2BGR)

def render(shots,root,out,duration=150, fps=FPS):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 sources=load_images(shots)
 bgs={};fulls={}
 for key,src in sources.items():
  bgs[key]=gradient_bg(src);fulls[key]=whole(src,bgs[key])
 frames_total=round(duration*fps);silent=out/'silent_v6.mp4'
 writer=cv2.VideoWriter(str(silent),cv2.VideoWriter_fourcc(*'mp4v'),fps,(W,H))
 if not writer.isOpened():raise RuntimeError('VideoWriter could not open')
 written=0;previous=None;shots_log=[];start=time.monotonic()
 try:
  for i,shot in enumerate(shots):
   key=shot.art['id']+'_'+shot.art['source']
   n=round(shot.duration*fps)
   if i==len(shots)-1:n=frames_total-written
   if n<=0:raise RuntimeError('shot duration too short')
   t0=written/fps
   trans=7 if shot.join=='dissolve' and previous is not None else (2 if shot.join=='match' and previous is not None else 0)
   frozen_previous=previous.copy() if previous is not None else None
   for f in range(n):
    t=f/max(n-1,1)
    img=frame_shot(sources[key],shot,t,bgs[key],fulls[key])
    at=written/fps
    if at<3.45:img=label_title(img,at)
    if trans and f<trans:
     alpha=ease((f+1)/(trans+1));img=cv2.addWeighted(frozen_previous,1-alpha,img,alpha,0)
    if at>=duration-1.9:
     img=cv2.convertScaleAbs(img,alpha=max(.05,min(1,(duration-at)/1.9)))
    writer.write(img);written+=1
    previous=img
   shots_log.append({'start':round(t0,3),'end':round(written/fps,3),'work':shot.art['title'],'source':shot.art['source'],
    'mode':shot.kind,'focus':shot.focus,'editorial_reason':shot.why,'transition':shot.join})
   if i%5==0:print('V6 film shot',i+1,'/',len(shots),'t',round(written/fps,1),shot.art['title'],flush=True)
 finally:writer.release()
 if written!=frames_total:raise RuntimeError(f'Frame mismatch: {written} vs {frames_total}')
 p=Path(root)/'licensed_piano_music.mp3'
 movie=out/'ARTVISION_VAN_GOGH_CINEMA_V6.mp4'
 command=['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(silent),'-i',str(p),
 '-map','0:v:0','-map','1:a:0','-t',str(duration),'-c:v','libx264','-preset','veryfast','-crf','20',
 '-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-af',f'volume=0.91,afade=t=in:st=0:d=0.7,afade=t=out:st={duration-3.4}:d=3.4',
 '-movflags','+faststart',str(movie)]
 subprocess.run(command,check=True)
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss','1.2','-i',str(movie),'-frames:v','1',str(out/'COPERTINA_CINEMA_V6.jpg')],check=True)
 (out/'STORYBOARD_V6.json').write_text(json.dumps(shots_log,ensure_ascii=False,indent=2))
 print('ARTVISION V6 FINISHED',len(shots),'shots',round(time.monotonic()-start,1),'s',flush=True)
 return movie,shots_log

def main():
 a=argparse.ArgumentParser();a.add_argument('--assets',default='/mnt/data/v6_museum_assets')
 a.add_argument('--out',default='/mnt/data/ArtVision_Cinema_V6');a.add_argument('--duration',type=int,default=150)
 args=a.parse_args();art=load_artworks(args.assets);print('original works',len(art),flush=True)
 shots=resolve_items(art,args.duration);print('planned shots',len(shots),'works',len(set(s.art['id'] for s in shots)),flush=True)
 render(shots,args.assets,args.out,args.duration)

if __name__=='__main__':main()