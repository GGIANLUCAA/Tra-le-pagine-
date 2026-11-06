#!/usr/bin/env python3
"""V182 The Triumph of Death Cinema Museum. Authentic Prado 2013
Priscila Costa / Ministério da Cultura CC BY 2.0 frame photo at entry/exit; source Cinema V150 unchanged between.
Exactly its own original AAC; no TTS, no external paid services, no Gold.
"""
import argparse, hashlib, json, subprocess, zipfile, math
from functools import lru_cache
from pathlib import Path
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont

W,H,FPS,N=720,1280,20,960
MP4='BRUEGEL_THE_TRIUMPH_OF_DEATH_CINEMA_V150_REVIEW.mp4'
MP4_SHA='c460fe7fa72ac29425de67eec40f986add502c42ec9e4166050c7ce107804138'
PHOTO_PAGE='https://commons.wikimedia.org/wiki/File:Pieter_Bruegel_der_Aeltere_-_Der_Triumph_des_Todes_-_mit_Rahmen.jpg'
PHOTO_SHA='c7b99abad654ca86c1df05f51b14013cd877eb11b079fde71799636987a73517'
TITLE='THE TRIUMPH OF DEATH'
NAME='BRUEGEL_THE_TRIUMPH_OF_DEATH_CINEMA_MUSEUM_V182_REVIEW.mp4'
PKG='BRUEGEL_TRIUMPH_CINEMA_MUSEUM_V182_REVIEW_PACKAGE.zip'
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
 return h.hexdigest()
def run(args):
 r=subprocess.run(list(map(str,args)),capture_output=True)
 if r.returncode:raise RuntimeError(r.stderr.decode(errors='replace')[-1900:])
 return r.stdout
@lru_cache(maxsize=2)
def _museum_static_assets(photo_filename):
 # Preprocess and validate the REAL source image only once per render.
 # Every returned object is immutable by convention; staged() copies the
 # background before drawing, preserving byte-identical frames.
 mat=cv2.imread(photo_filename)
 if mat is None:raise ValueError("Authentic frame photo unreadable")
 ph,pw=mat.shape[:2]
 scale=min((W-96)/pw,(H*.56)/ph)
 sw,sh=int(scale*pw),int(scale*ph)
 img=cv2.resize(mat,(sw,sh),interpolation=cv2.INTER_AREA)
 background=np.full((H,W,3),(24,24,25),np.uint8)
 for y in range(H):
  v=int(16+13*(1-abs(y-H/2)/(H/2)))
  background[y,:]=(v+7,v+6,v+4)
 serif=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',24)
 sans=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
 return img,sw,sh,background,serif,sans

def staged(photo,t):
 img,sw,sh,background,serif,sans=_museum_static_assets(str(photo))
 im=background.copy()
 zoom=.93+.085*max(0,min(1,t))
 iw,ih=int(sw*zoom),int(sh*zoom)
 sub=cv2.resize(img,(iw,ih),interpolation=cv2.INTER_CUBIC)
 px=(W-iw)//2;py=(H-ih)//2+35
 x1,y1,x2,y2=max(0,px),max(0,py),min(W,px+iw),min(H,py+ih)
 if x1<x2 and y1<y2:im[y1:y2,x1:x2]=sub[y1-py:y2-py,x1-px:x2-px]
 pil=Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB))
 d=ImageDraw.Draw(pil)
 for title,y,font,col in [(TITLE,95,serif,(235,225,207)),('PIETER BRUEGEL · 1562–1563',155,sans,(194,185,165))]:
  b=d.textbbox((0,0),title,font=font)
  d.text(((W-b[2]+b[0])/2,y),title,font=font,fill=col)
 return cv2.cvtColor(np.asarray(pil),cv2.COLOR_RGB2BGR)
def main():
 p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--out',required=True)
 a=p.parse_args();base=Path(a.base);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
 mp4=base/MP4;photo=base/'TRIUMPH_OF_DEATH_PRADO_REAL_FRAME_PRISCILA_COSTA_2013.jpg'
 assert sha(mp4)==MP4_SHA and mp4.stat().st_size==20786590
 with Image.open(photo) as img:
  assert img.format=='JPEG' and img.size==(4368,2912)
  size=list(img.size)
 assert photo.stat().st_size==6770130 and sha(photo)==PHOTO_SHA, 'Real frame photo V182 differs from verified SHA256'
 cap=cv2.VideoCapture(str(mp4));assert cap.isOpened()
 assert int(cap.get(cv2.CAP_PROP_FRAME_COUNT))==N and int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))==W and int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))==H
 raw=out/'SILENT_TEMP_V182.mp4'
 ff=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','21','-pix_fmt','yuv420p',str(raw)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 contact=[];BOOK=100
 try:
  for n in range(N):
   ok,frame=cap.read()
   if not ok:raise ValueError('Unexpected master EOF at '+str(n))
   if n<BOOK:frame=staged(photo,n/(BOOK-1))
   elif n>=N-BOOK:frame=staged(photo,1-(n-N+BOOK)/(BOOK-1))
   if n in [0,40,100,139,140,250,480,700,940,1180,1420,1660,1900,2128,2266]:
    contact.append((n/FPS,cv2.resize(frame,(180,320))))
   ff.stdin.write(np.ascontiguousarray(frame).tobytes())
  ff.stdin.close();err=ff.stderr.read()
  if ff.wait():raise RuntimeError(err.decode(errors='replace')[-1800:])
 except Exception:
  ff.kill();raise
 finally:cap.release()
 target=out/NAME
 run(['ffmpeg','-v','error','-y','-i',raw,'-i',mp4,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','copy','-movflags','+faststart',target])
 run(['ffmpeg','-v','error','-xerror','-i',target,'-map','0','-f','null','-'])
 def audio_sha(p):return hashlib.sha256(run(['ffmpeg','-v','error','-i',p,'-map','0:a:0','-c:a','copy','-f','adts','pipe:1'])).hexdigest()
 a1,a2=audio_sha(mp4),audio_sha(target);assert a1==a2
 probe=cv2.VideoCapture(str(target));cnt=int(probe.get(cv2.CAP_PROP_FRAME_COUNT));fps=probe.get(cv2.CAP_PROP_FPS);probe.release()
 assert cnt==N and abs(fps-FPS)<.01
 raw.unlink()
 grid=np.full((4*340,4*194,3),21,np.uint8)
 for i,(sec,fr) in enumerate(contact):
  x=i%4*194+7;y=i//4*340+7;grid[y:y+320,x:x+180]=fr
  cv2.putText(grid,f'{sec:.1f}s',(x,y+330),cv2.FONT_HERSHEY_SIMPLEX,.35,(225,215,200),1)
 cv2.imwrite(str(out/'CONTACT_SHEET_V182.jpg'),grid)
 cv2.imwrite(str(out/'COVER.jpg'),staged(photo,.2),[cv2.IMWRITE_JPEG_QUALITY,94])
 (out/'RIGHTS_AND_CREDITS.txt').write_text(
  'The Triumph of Death (1562–1563), Pieter Bruegel the Elder, Prado P001393, 117 x 162 cm.\\n'
  'Real Prado framed painting photographed by Priscila Costa / Ministério da Cultura 30 June 2013, CC BY 2.0: '+PHOTO_PAGE+'\\n'
  'Original 4368x2912 JPEG 6770130 bytes SHA256 '+PHOTO_SHA+'. Prado 2013 frame is NOT asserted historic-original from 1562–1563.\\n'
  'Only actual framed photograph in intro and outro; neutral editorial background is NOT a claim of actual Prado architecture.\\n'
  'Cinema Standard V150 48s source preserved; original AAC copied with bit-identical ADTS, ZERO new voice/video API.\\n'
  'French heritage territorial/commercial permission, human artistic review and safe historical content review PENDING. Not Gold, not published.\\n',encoding='utf8')
 (out/'SOCIAL_DRAFT_UNPUBLISHED.txt').write_text(
  'THE TRIUMPH OF DEATH · Pieter Bruegel the Elder · 1562–1563.\\n'
  'A journey from the artwork as photographed in its real Prado frame to the color and drama of Bruegel’s 1562–1563 composition.\\n'
  'Museum photograph: Priscila Costa / Ministério da Cultura CC BY 2.0, June 2013. DRAFT ONLY; NO PUBLISHING.\\n',encoding='utf8')
 report={'work':'The Triumph of Death','variant':'cinema_museum','original_cinema_mp4_sha256':MP4_SHA,
 'original_aac_adts_sha256':a1,'new_aac_adts_sha256':a2,'same_aac_bit_identical':True,
 'authentic_photo_page':PHOTO_PAGE,'photo_license':'Priscila Costa / Ministério da Cultura CC BY 2.0, photo 30 June 2013', 'photo_license_url':'https://creativecommons.org/licenses/by/2.0/','photo_sha256':sha(photo),
 'photo_dimensions':size,'photo_bytes':photo.stat().st_size,'real_frame_only_intro_outro_seconds':2*BOOK/FPS,
 'frame_historical_originality_asserted':False,'actual_louvre_room_recreated':False,
 'file':{'name':target.name,'bytes':target.stat().st_size,'sha256':sha(target),'duration_s':N/FPS,'frames':cnt,'resolution':[W,H],'full_ffmpeg_decode':'PASS'},
 'human_artistic_review':'PENDING','museum_approved':False,'Gold_V25':False,'social_published':False,'new_paid_calls':0,'new_TTS_calls':0}
 (out/'QA_V182.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 archive=out/PKG
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3) as z:
  for item in [target,photo,out/'COVER.jpg',out/'CONTACT_SHEET_V182.jpg',out/'QA_V182.json',out/'RIGHTS_AND_CREDITS.txt',out/'SOCIAL_DRAFT_UNPUBLISHED.txt']:
   z.write(item,arcname=item.name)
 with zipfile.ZipFile(archive) as z:assert z.testzip() is None
 print(json.dumps({'status':'REAL_CINEMA_MUSEUM_REVIEW','file':report['file'],'zip':{'name':PKG,'size':archive.stat().st_size,'sha256':sha(archive),'crc':'PASS'},'photo':report['photo_sha256'],'AAC_IDENTICAL':True,'Gold_V25':False}))
if __name__=='__main__':main()
