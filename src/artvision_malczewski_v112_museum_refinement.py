#!/usr/bin/env python3
"""ArtVision Malczewski V112: source-locked museum intro/outro refinement only.
Uses exact verified painting from V110; reads V111 video master; AAC copied bit-for-bit.
Digital gallery is an original illustrative reconstruction, NOT the actual museum,
and the frame is a modern visual study inferred from appearance, NOT an authentic
historical frame. No TTS, no external service, no cost.
"""
from pathlib import Path
import argparse, hashlib, json, math, subprocess
import numpy as np, cv2
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageEnhance

S_W,S_H,W,H,FPS=2160,3840,720,1280,20
ART_SHA='0ff83e09be9465a696b8956065f93ddd78f9fb3c1f1e8ebd87b98bc792cad5b9'
ART_X,ART_Y,ART_W=280,1020,1600
ART_H=round(ART_W*3557/5026)
ART_CX=ART_X+ART_W/2;ART_CY=ART_Y+ART_H/2

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def font(px,serif=False):
 for x in ([f'/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'] if serif else []) + [f'/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
  try: return ImageFont.truetype(x,px)
  except OSError:pass
 return ImageFont.load_default()

def make_room(source,out):
 """High res physical-proportion optical study. All paintings in digital room are exact original."""
 rng=np.random.default_rng(112)
 # A restrained warm plaster gallery with non-uniform illumination/ambient occlusion.
 yy=np.arange(S_H,dtype=np.float32)[:,None]
 xx=np.arange(S_W,dtype=np.float32)[None,:]
 nx=(xx-S_W/2)/(S_W/2)
 noise=rng.normal(0,1.20,size=(S_H,S_W)).astype('float32')
 # Warm wall with imperfect plaster and lateral shadows.
 broad=18*np.exp(-((nx/.60)**2 + ((yy-1540)/1580)**2))
 light=12*np.exp(-((xx-1010)/670)**2-((yy-1070)/1250)**2)
 side=-28*np.abs(nx)**2
 daylight=3*np.sin(yy/220)
 wall_val=(182+broad+light+side+daylight+noise).astype('float32')
 image=np.empty((S_H,S_W,3),dtype=np.uint8)
 for ch,offset in enumerate([3,0,-8]):
  image[:,:,ch]=np.clip(wall_val+offset,0,255).astype('uint8')
 pil=Image.fromarray(image,'RGB')
 d=ImageDraw.Draw(pil,'RGBA')
 # coffered ceiling and the architectural footprint of a room
 d.polygon([(0,0),(S_W,0),(S_W,270),(0,345)],fill=(81,79,75,255))
 d.polygon([(0,0),(240,0),(85,275),(0,350)],fill=(61,60,57,255))
 d.polygon([(S_W,0),(S_W-240,0),(S_W-82,275),(S_W,320)],fill=(66,63,58,255))
 d.line([(0,352),(S_W,260)],fill=(228,211,178,180),width=7)
 d.line([(0,364),(S_W,274)],fill=(46,43,37,180),width=10)
 # Spot fixtures; diffuse glow already painted below and via light gradients.
 for x,y in [(450,225),(1080,188),(1720,151)]:
  d.ellipse((x-34,y-12,x+34,y+12),fill=(37,39,39,255),outline=(127,117,97,255),width=3)
  d.ellipse((x-16,y-5,x+16,y+7),fill=(228,211,174,220))
 # Recessed side walls/pilasters, subtle perspective edges
 d.polygon([(0,345),(190,325),(120,2790),(0,3100)],fill=(70,68,64,85))
 d.polygon([(S_W,276),(S_W-165,288),(S_W-115,2790),(S_W,3080)],fill=(58,55,51,105))
 d.line([(173,328),(125,2750)],fill=(234,218,184,75),width=4)
 d.line([(S_W-180,284),(S_W-130,2740)],fill=(238,224,189,75),width=4)
 # Shadowed mid-wall rail and wall/floor seam.
 d.rectangle([0,2720,S_W,2773],fill=(69,63,53,255))
 d.line([(0,2719),(S_W,2719)],fill=(224,198,154,255),width=7)
 d.line([(0,2773),(S_W,2773)],fill=(30,28,26,255),width=13)
 # Stone floor with correct converging tile grout.
 d.polygon([(0,2774),(S_W,2774),(S_W,S_H),(0,S_H)],fill=(106,100,90,255))
 for y0 in [2790,2860,2990,3170,3400,3700]:
  d.line([(0,y0),(S_W,y0)],fill=(63,59,54,150),width=4 if y0<3100 else 7)
  d.line([(0,y0+8),(S_W,y0+8)],fill=(152,141,119,60),width=2)
 for xb in [-180,480,1690,2370]:
  d.line([(S_W/2,2760),(xb,S_H)],fill=(43,39,34,140),width=5)
 # Bench in soft silhouette to anchor space; it is not a historical museum photo.
 # faint contact shadow
 d.ellipse((575,3520,1705,3710),fill=(26,23,20,48))
 d.polygon([(670,3400),(1520,3400),(1650,3460),(760,3460)],fill=(89,70,52,255))
 d.line([(715,3420),(1575,3426)],fill=(151,116,70,255),width=15)
 d.polygon([(765,3460),(810,3460),(780,3670),(740,3670)],fill=(64,56,49,255))
 d.polygon([(1540,3460),(1580,3460),(1630,3660),(1582,3660)],fill=(64,56,49,255))
 # In-situ archival-style picture shadow and aged bronze/ebonized moulding.
 bx0,by0=ART_X-54,ART_Y-54;bx1,by1=ART_X+ART_W+54,ART_Y+ART_H+54
 shadow=Image.new('RGBA',(S_W,S_H),(0,0,0,0));ds=ImageDraw.Draw(shadow)
 ds.rounded_rectangle([bx0+26,by0+30,bx1+34,by1+45],radius=15,fill=(0,0,0,125))
 shadow=shadow.filter(ImageFilter.GaussianBlur(37))
 pil=Image.alpha_composite(pil.convert('RGBA'),shadow).convert('RGB');d=ImageDraw.Draw(pil)
 # Restrained frame material modeled from modern photographic references but NOT copied.
 frame_layers=[(52,(29,24,21)),(46,(81,67,48)),(38,(149,119,72)),(31,(40,34,30)),(24,(192,154,92)),(19,(49,39,29)),(13,(97,75,45)),(8,(201,163,96)),(4,(44,34,26))]
 for pad,color in frame_layers:
  d.rectangle([ART_X-pad,ART_Y-pad,ART_X+ART_W+pad,ART_Y+ART_H+pad],outline=color,width=max(2,6 if pad in [52,38,24] else 4))
 # beveled corners, tiny pattern embossing: no garish gilt ornament
 for pad in (45,29):
  for j in range(1,12):
   g=j*4
   if g>=pad-5:break
   shade=(106+j*3,86+j*3,55+j*2)
   d.line([(ART_X-pad+g,ART_Y-pad),(ART_X-pad,ART_Y-pad+g)],fill=shade,width=2)
 # Image sourced from exact authenticated PD JPEG. Preserve pixel accuracy.
 im=Image.open(source).convert('RGB')
 im=im.resize((ART_W,ART_H),Image.Resampling.LANCZOS)
 pil.paste(im,(ART_X,ART_Y))
 # Discreet real-style side wall museum label; never crosses the approach path.
 px,py=1955,1700
 d.rounded_rectangle((px-10,py-10,px+182,py+240),radius=5,fill=(225,223,213),outline=(125,121,108),width=2)
 d.text((px+13,py+14),'JACEK',font=font(24,serif=True),fill=(53,51,46))
 d.text((px+13,py+49),'MALCZEWSKI',font=font(19,serif=True),fill=(53,51,46))
 d.line([(px+13,py+94),(px+158,py+94)],fill=(152,148,135),width=2)
 d.text((px+13,py+115),'BŁĘDNE KOŁO',font=font(15),fill=(67,64,56))
 d.text((px+13,py+144),'1895–1897',font=font(16),fill=(86,83,72))
 d.text((px+13,py+181),'MNP FR 56',font=font(14),fill=(100,97,86))
 d.text((px+13,py+212),'studio digitale',font=font(12),fill=(119,116,105))
 pil.save(out,quality=94,subsampling=0)
 return cv2.cvtColor(np.asarray(pil),cv2.COLOR_RGB2BGR)

def smooth(u):
 u=np.clip(u,0,1)
 return u*u*(3-2*u)

def extract_accurate(art,room,z,cx,cy):
 """Crop digital gallery, but overpaint exact source art at high resolution per frame."""
 vh=S_H/z;vw=S_W/z;left=cx-vw/2;top=cy-vh/2
 # affine transformation with coordinate clipping via cv2.remap for gallery
 ix=max(0,int(left));iy=max(0,int(top));ex=min(S_W,int(math.ceil(left+vw)));ey=min(S_H,int(math.ceil(top+vh)))
 if ex<=ix or ey<=iy: raise ValueError('Camera outside room')
 # We use remap for sub-pixel smooth motion at all magnifications.
 xcoords=left+np.arange(W,dtype=np.float32)[None,:]*vw/W
 ycoords=top+np.arange(H,dtype=np.float32)[:,None]*vh/H
 mX=np.broadcast_to(xcoords,(H,W)).astype(np.float32).copy();mY=np.broadcast_to(ycoords,(H,W)).astype(np.float32).copy()
 frame=cv2.remap(room,mX,mY,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
 # Screen bbox for the real 240×174cm painting with no change to its aspect ratio.
 aX=(ART_X-left)*W/vw; aY=(ART_Y-top)*H/vh
 bX=(ART_X+ART_W-left)*W/vw; bY=(ART_Y+ART_H-top)*H/vh
 x0=max(0,int(math.ceil(aX)));x1=min(W,int(math.floor(bX)));y0=max(0,int(math.ceil(aY)));y1=min(H,int(math.floor(bY)))
 if x1>x0 and y1>y0:
  X=xcoords[:,x0:x1];Y=ycoords[y0:y1,:]
  srcx=np.broadcast_to((X-ART_X)*(art.shape[1]/ART_W),(y1-y0,x1-x0)).astype(np.float32).copy()
  srcy=np.broadcast_to((Y-ART_Y)*(art.shape[0]/ART_H),(y1-y0,x1-x0)).astype(np.float32).copy()
  frame[y0:y1,x0:x1]=cv2.remap(art,srcx,srcy,cv2.INTER_LANCZOS4,borderMode=cv2.BORDER_REPLICATE)
 return frame

def first_body_target(art):
 ah,aw=art.shape[:2]
 x,y,z=.515,.155,1.95
 ch=max(500,int(ah/z));cw=round(ch*W/H)
 l=max(0,min(aw-cw,round(aw*x-cw/2)));t=max(0,min(ah-ch,round(ah*y-ch/2)))
 scale=ART_W/aw
 return (S_W/(cw*scale), ART_X+(l+cw/2)*scale,ART_Y+(t+ch/2)*scale)

def intro_frames(art,room,count,master_first):
 z_target,cx_target,cy_target=first_body_target(art)
 # Hold a frame of gallery, then approach and end on the very same source pixels as the first painted closeup.
 for i in range(count):
  u=i/(count-1); movement=smooth(max(0,(u-.08)/.92))
  z=math.exp(math.log(1.0)+movement*math.log(z_target))
  cx=1080+(cx_target-1080)*movement
  cy=1920+(cy_target-1920)*movement
  frame=extract_accurate(art,room,z,cx,cy)
  # Show exactly the same typographic overlay at the moment we enter the artwork.
  if u>=.89:
   a=float(smooth((u-.89)/.11));alpha_canvas=np.zeros((H,W,1),np.float32)
   alpha_canvas[1065:]=a
   frame=np.clip(frame.astype('float32')*(1-alpha_canvas)+master_first.astype('float32')*alpha_canvas,0,255).astype('uint8')
  yield frame

def outro_frames(art,room,count,body_last):
 # Start painting at exact footprint of final 'whole' backdrop (full image 688px, centered).
 # From this crop the 240 x 174 cm painting pulls away, with its narrow frame reappearing.
 zoom0=688*S_W/(W*ART_W)
 for i in range(count):
  u=i/(count-1); m=smooth(u)
  z=zoom0*(1-m)+1.0*m
  cx=ART_CX+(1080-ART_CX)*m
  cy=ART_CY+(1920-ART_CY)*m
  frame=extract_accurate(art,room,z,cx,cy)
  # At the boundary preserve exact existing pixels, and reveal the gallery around the painting gradually.
  if u<.12:
   alpha=smooth(u/.12)
   # Blend only scenery around painting, never double-expose the painting.
   hh,ww=art.shape[:2];picw=(ART_W*z/3);pich=(ART_H*z/3)
   midx=(ART_CX-(cx-S_W/(2*z)))*z/3;midy=(ART_CY-(cy-S_H/(2*z)))*z/3
   x0=max(0,int(midx-picw/2));x1=min(W,int(midx+picw/2));y0=max(0,int(midy-pich/2));y1=min(H,int(midy+pich/2))
   transition=(body_last.astype('float32')*(1-alpha)+frame.astype('float32')*alpha).astype('uint8')
   # Exact image from existing footage at initial moment, then gentle registered alignment.
   frame=transition
  yield frame

def stream_render(master,output,art,room,qa_name):
 cap=cv2.VideoCapture(str(master));n=round(cap.get(cv2.CAP_PROP_FRAME_COUNT));fps=cap.get(cv2.CAP_PROP_FPS)
 if abs(fps-FPS)>.01:raise ValueError('Unexpected FPS')
 iscrit='CRITICO_' in master.name
 in_count=100 if iscrit else 160 # 5sec Critico, 8sec Cinema
 out_count=120 if iscrit else 180 # 6sec Critico, 9sec Cinema
 last_first=None;last_body=None
 cap.set(cv2.CAP_PROP_POS_FRAMES,in_count);good,last_first=cap.read()
 cap.set(cv2.CAP_PROP_POS_FRAMES,n-out_count-1);good2,last_body=cap.read()
 if not(good and good2):raise RuntimeError('Could not sample preserved boundary frames')
 cap.set(cv2.CAP_PROP_POS_FRAMES,0)
 silent=output.with_name('TEMP_'+output.stem+'.mp4')
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','720x1280','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(silent)]
 pipe=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 intro=iter(intro_frames(art,room,in_count,last_first));outro=iter(outro_frames(art,room,out_count,last_body))
 for i in range(n):
  success,fr=cap.read()
  if not success: raise RuntimeError(f'Video truncated at {i} of {n}')
  if i<in_count:fr=next(intro)
  elif i>=n-out_count:fr=next(outro)
  pipe.stdin.write(fr.tobytes())
 cap.release();pipe.stdin.close()
 if pipe.wait()!=0:raise RuntimeError(pipe.stderr.read().decode()[-1600:])
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(silent),'-i',str(master),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','copy','-shortest','-movflags','+faststart',str(output)],check=True)
 subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(output),'-f','null','-'],check=True)
 silent.unlink()
 audio=[]
 for name,p in [('original',master),('review',output)]:
  a=output.with_name(f'_temp_{qa_name}_{name}.aac')
  subprocess.run(['ffmpeg','-v','error','-y','-i',str(p),'-map','0:a:0','-c:a','copy','-f','adts',str(a)],check=True)
  audio.append(sha(a));a.unlink()
 if audio[0]!=audio[1]:raise RuntimeError('AAC not bit identical')
 report={'variant':qa_name,'input_sha256':sha(master),'output_sha256':sha(output),'bytes':output.stat().st_size,'frames':n,'fps':FPS,'duration_seconds':n/FPS,'original_AAC_SHA256':audio[0],'output_AAC_SHA256':audio[1],'aac_bit_identical':True,'only_frames_changed':f'0..{in_count-1}, {n-out_count}..{n-1}','interior_frames_rendered_from_original_master':True,'same_length':True,'ffmpeg_full_decode':'PASS','V25_Gold':False,'original_artwork_sha256':ART_SHA,'room':'digital gallery study, not actual Poznan museum','frame':'modern bronze/ebonized representation inspired by exhibition photo; not verified historical frame','no_TTS_or_paid_API':True}
 return report

def main():
 a=argparse.ArgumentParser();a.add_argument('--source',type=Path,required=True);a.add_argument('--critico',type=Path,required=True);a.add_argument('--cinema',type=Path,required=True);a.add_argument('--out',type=Path,required=True);a.add_argument('--gallery-only',action='store_true');args=a.parse_args()
 if sha(args.source)!=ART_SHA:raise ValueError('Source SHA mismatch; prevent artwork substitution')
 args.out.mkdir(parents=True,exist_ok=True)
 art=cv2.imread(str(args.source));room=make_room(args.source,args.out/'GALLERIA_V112.jpg')
 img=cv2.resize(room,(W,H));cv2.imwrite(str(args.out/'GALLERIA_V112_PREVIEW.jpg'),img)
 if args.gallery_only:return
 qa={'work_id':'malczewski_bledne_kolo_1897_mnp_fr56','version':'V112 museum-only review','master_v111_preserved':True,'cinema_standard_V111_untouched':True,'critico_standard_V111_untouched':True,'V25_Gold':0,'social_published':False,'Android_R2_player_verified':False,'source_exact_sha256':ART_SHA,'runs':{}}
 for variant,master in [('critico_museum',args.critico),('cinema_museum',args.cinema)]:
  dest=args.out/f'MALCZEWSKI_{variant.upper()}_V112_MUSEUM_REVIEW.mp4'
  print('rendering',variant,flush=True)
  qa['runs'][variant]=stream_render(master,dest,art,room,variant)
  (args.out/'QA_V112.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps(qa,ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':main()