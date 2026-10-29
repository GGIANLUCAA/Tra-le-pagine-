#!/usr/bin/env python3
"""ARTVISION POP-OUT V2 — CPU-only painting-locked 2.5D depth-field renderer.
Synthetic depth geometry, not a reconstructed real 3D person. No APIs, no AI-generated imagery.
Original public-domain painting from Mauritshuis (image obtained through research).
"""
from __future__ import annotations
import json, math, os, hashlib, argparse, tempfile, subprocess, time
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Self-contained experimental renderer: source from file or Wikimedia Commons,
# no paid calls. The 960px Commons reproduction is of the Mauritshuis painting.
WIKIMEDIA_SOURCE = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/"
    "Johannes_Vermeer_-_Girl_with_a_Pearl_Earring_-_670_-_Mauritshuis.jpg/"
    "960px-Johannes_Vermeer_-_Girl_with_a_Pearl_Earring_-_670_-_Mauritshuis.jpg"
)
import io
from urllib.request import Request, urlopen

parser=argparse.ArgumentParser(description="Experimental source-locked Vermeer Pop-Out V2")
parser.add_argument('--source',type=Path,help='Optional locally provided legitimate artwork JPEG/PNG')
parser.add_argument('--mask',type=Path,help='Optional edited greyscale mask, same aspect as source')
parser.add_argument('--out',type=Path,default=Path('output/experiment-vermeer-popout-v2'))
parser.add_argument('--stills-only',action='store_true')
args=parser.parse_args()
OUTPUT=args.out.resolve()
OUTPUT.mkdir(parents=True,exist_ok=True)
if args.source:
    if not args.source.is_file():raise FileNotFoundError(f"Missing source image: {args.source}")
    raw=args.source.read_bytes()
    origin=str(args.source)
else:
    request=Request(WIKIMEDIA_SOURCE, headers={'User-Agent':'ArtVision-PopOut-Creative-Experiment/2.0 (public domain artwork)'})
    with urlopen(request, timeout=45) as response:
        raw=response.read(8_000_000)
    origin=WIKIMEDIA_SOURCE
source=Image.open(io.BytesIO(raw)).convert('RGB')
if source.width<600 or source.height<700:raise ValueError('Source image too small for trial')
source=source.resize((845,1000), Image.Resampling.LANCZOS)
SOURCE=OUTPUT/'ORIGINAL_PICTURE_NORMALIZED.png'
source.save(SOURCE)
W,H=720,1280
FPS=24
DURATION=8
painting_width=540
painting_height=round(painting_width*1000/845)
px=(W-painting_width)//2; py=310
pcx=px+painting_width/2; pcy=py+painting_height/2

def get_font(size):
  for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf','/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf']:
    if Path(p).exists(): return ImageFont.truetype(p,size)
  return ImageFont.load_default()

font_title=get_font(27);font_sub=get_font(18);font_small=get_font(16)

if args.mask:
    MASK=args.mask
    mask_np=np.asarray(Image.open(MASK).convert('L').resize(source.size,Image.Resampling.BILINEAR),dtype=np.uint8)
else:
    # Hand-declared polygon acts only as GrabCut guidance; final edges are
    # computed directly from original pixels. Check visually before publication.
    mask_points=[(251,999),(286,931),(318,850),(342,784),(369,700),(411,635),
      (364,603),(317,566),(275,520),(259,473),(257,419),(258,363),
      (277,307),(290,270),(314,229),(353,194),(404,167),(446,151),
      (473,135),(510,116),(545,117),(583,134),(626,161),(661,201),
      (684,269),(704,361),(732,480),(766,593),(792,693),(813,735),
      (800,763),(768,779),(738,771),(709,803),(704,871),(731,999)]
    w0,h0=source.size
    seeds=np.zeros((h0,w0),np.uint8)
    cv2.fillPoly(seeds,[np.asarray(mask_points,np.int32)],255)
    outer=cv2.dilate(seeds,np.ones((31,31),np.uint8))
    inner=cv2.erode(seeds,np.ones((35,35),np.uint8))
    gc=np.full((h0,w0),cv2.GC_BGD,np.uint8)
    gc[outer>0]=cv2.GC_PR_BGD
    gc[seeds>0]=cv2.GC_PR_FGD
    gc[inner>0]=cv2.GC_FGD
    for x,y,r in [(350,430,22),(425,450,24),(520,305,30),(520,195,20),
                  (625,590,20),(463,815,25),(530,910,30),(688,668,16)]:
        cv2.circle(gc,(x,y),r,int(cv2.GC_FGD),-1)
    gc[:12,:]=cv2.GC_BGD
    model_bg=np.zeros((1,65),np.float64);model_fg=np.zeros((1,65),np.float64)
    cv2.grabCut(cv2.cvtColor(np.array(source),cv2.COLOR_RGB2BGR),gc,None,model_bg,model_fg,5,cv2.GC_INIT_WITH_MASK)
    extracted=(np.isin(gc,[cv2.GC_FGD,cv2.GC_PR_FGD]).astype(np.uint8)*255)
    n,labels,stats,_=cv2.connectedComponentsWithStats(extracted,8)
    keep=np.zeros_like(extracted)
    for i in range(1,n):
        if stats[i,cv2.CC_STAT_AREA]>75:keep[labels==i]=255
    keep=cv2.morphologyEx(keep,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    mask_np=cv2.GaussianBlur(keep,(5,5),.9)
    MASK=OUTPUT/'AUTO_FOREGROUND_MASK.png'
    Image.fromarray(mask_np).save(MASK)
if int((mask_np>128).sum())<35000:raise ValueError('Subject segmentation failed, review mask')

source_np=np.array(source);h,w=source_np.shape[:2]
mask_np=np.array(Image.open(MASK).convert('L'))
# Clean plate: dark original canvas material with authentic original dark area sampled.
# A fill, not an assertion of image fidelity; center texture is generated from its visible left side.
rng=np.random.default_rng(88)
bgplate=source_np.astype(np.float32)
# Color sample from unobstructed original area (especially dark canvas mid-left):
# Fill based on the actual paint's unobstructed left margin, not a dark silhouette.
# Avoid leaving a ghost copy of the girl when the figure lifts from the surface.
left=source_np[:,18:195].astype(np.float32)
rowmedian=np.median(left,axis=1)
rowmedian=cv2.GaussianBlur(rowmedian[:,None,:],(1,99),0)[:,0,:]
rowmedian=np.maximum(9,rowmedian)
coarse=rng.normal(0,1,(26,24)).astype(np.float32)
coarse=cv2.resize(coarse,(w,h),interpolation=cv2.INTER_CUBIC)
coarse=cv2.GaussianBlur(coarse,(0,0),6)
fine=rng.normal(0,2.3,(h,w))
fill=np.clip(rowmedian[:,None,:]+coarse[:,:,None]*1.6+fine[:,:,None],0,255)
expanded=cv2.dilate((mask_np>20).astype(np.uint8),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(105,105)),iterations=1)
feather=cv2.GaussianBlur(expanded.astype(np.float32),(0,0),19)[:,:,None]
cleanplate=np.uint8(np.clip(source_np*(1-feather)+fill*feather,0,255))

# Depth field anchored to visible contours; hand-tuned smooth surface, not guessed hidden geometry.
yg,xg=np.mgrid[0:h,0:w].astype(np.float32)
def gauss(cx,cy,rx,ry,amp):
  return amp*np.exp(-.5*((xg-cx)/rx)**2-.5*((yg-cy)/ry)**2)

depth = np.full((h,w),.22,np.float32)
# shoulders / coat folded relief
depth += gauss(482,800,162,190,.27) + gauss(449,960,180,125,.09)
# face sculpted as an oval bulge with extra nose/cheeks
# nasal bridge points toward viewer, face extends more than scarf or coat
depth += gauss(384,439,143,188,.34) + gauss(280,463,43,70,.035)
depth += gauss(370,392,72,98,.015) + gauss(400,514,90,82,.022)
# turban (different depth from face) and drape (behind head)
depth += gauss(478,303,187,151,.28) + gauss(532,162,95,64,.17)
depth += gauss(701,538,62,213,.17)
# shoulder seam, collar, pearl relief
depth += gauss(463,613,93,54,.11)+gauss(528,544,27,27,.14)
# clamp and smooth, no pixel geometry noise
depth=cv2.GaussianBlur(np.clip(depth,0,1.20),(0,0),10)
# face receives approx 1.0; generate normal map to justify side lighting gently
normx=-cv2.Sobel(depth,cv2.CV_32F,1,0,ksize=3)/8
normy=-cv2.Sobel(depth,cv2.CV_32F,0,1,ksize=3)/8
# frame source drawn in image-plane; separate 3D perspective transform later
frame_pad=32
FW,FH=painting_width+2*frame_pad,painting_height+2*frame_pad
frame=Image.new('RGBA',(FW,FH),(0,0,0,0));fdraw=ImageDraw.Draw(frame)
# precise decorative profile, warm gold, dark recessed internal lip
for i in range(frame_pad):
  if i<4: col=(46+7*i,33+5*i,17+3*i,255)
  elif i<10:col=(122+min(9*i,65),79+min(5*i,45),37+min(4*i,35),255)
  elif i<16:col=(202-3*(i-10),156-2*(i-10),79-(i-10),255)
  elif i<22:col=(79+4*(i-16),51+3*(i-16),30+2*(i-16),255)
  elif i<28:col=(156+6*(i-22),105+5*(i-22),54+3*(i-22),255)
  else:col=(31+6*(i-28),24+3*(i-28),19+2*(i-28),255)
  fdraw.rectangle((i,i,FW-i-1,FH-i-1),outline=col,width=1)
# tiny embossed decorative corners
for cx0 in [15,FW-15]:
 for cy0 in [15,FH-15]:
  fdraw.ellipse((cx0-8,cy0-8,cx0+8,cy0+8),fill=(142,93,46,255),outline=(223,172,96,255),width=2)
  fdraw.ellipse((cx0-3,cy0-3,cx0+3,cy0+3),fill=(239,191,109,255))
frame_np=np.array(frame)

def make_museum():
  # non-authentic scenic wall; no invented claims about actual gallery
  gy,gx=np.mgrid[0:H,0:W]
  light=np.exp(-(((gx-W/2)/480)**2+((gy-590)/720)**2))
  top=17+light*28
  grain=np.random.default_rng(22).normal(0,1.0,(H,W))
  wall=np.zeros((H,W,3),np.uint8)
  for k,v in enumerate([0.97,0.94,0.97]):wall[:,:,k]=np.clip(top*v+grain,0,255)
  wall[1090:,:,:]=np.clip(wall[1090:,:,:].astype(np.float32)*0.57,0,255).astype(np.uint8)
  wall[1090:1095,:,:]=[77,70,63]
  return wall
wall=make_museum()

# Perspective transform for flat painting/frame: yaw rotates scene gradually.
# Background remains in its own plane, face protrudes with DIFFERENT 3D coordinates.
def project_flat_quad(x0,y0,ww,hh, yaw, pan):
  corners=[(x0,y0),(x0+ww,y0),(x0+ww,y0+hh),(x0,y0+hh)]
  result=[]
  for xx,yy in corners:
    X=(xx-pcx)/painting_width
    Y=(yy-pcy)/painting_width
    zr=-math.sin(yaw)*X
    mag=2.75/(2.75-zr)
    xr=math.cos(yaw)*X
    result.append([pcx+pan+painting_width*xr*mag, pcy+painting_width*Y*mag])
  return np.array(result,dtype=np.float32)

# overlay texture on painting plane incl. transformed frame
src_orig=np.array(source)
resized=cv2.resize(src_orig,(painting_width,painting_height),interpolation=cv2.INTER_AREA)
plate_resized=cv2.resize(cleanplate,(painting_width,painting_height),interpolation=cv2.INTER_AREA)

# Foreground render in output screen space, inverse solution for textured surface mesh
XOUT,YOUT=np.meshgrid(np.arange(W,dtype=np.float32),np.arange(H,dtype=np.float32))


def foreground(pop,yaw,pan):
  # a convex volume with depth-dependent perspective; no texture hallucination
  angle=yaw*.8
  c,s=math.cos(angle),math.sin(angle)
  nx=(XOUT-(pcx+pan-255*pop))/painting_width
  ny=(YOUT-(pcy-69*pop))/painting_width
  u=(nx+0.5)*w
  v=ny*w+h*.5
  for k in range(5):
    dep=cv2.remap(depth,u.astype(np.float32),v.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
    xnorm=(u-w*.5)/w
    Z=pop*(0.11+dep*.60)
    Zr=-s*xnorm+c*Z
    magn=2.75/np.maximum(1.35,2.75-Zr)
    xnorm=(nx/magn-s*Z)/max(.5,c)
    ynorm=ny/magn+0.07*Z
    u=(xnorm+.5)*w
    v=ynorm*w+h*.5
  # remap artwork + alpha independently for high quality
  xf=u.astype(np.float32);yf=v.astype(np.float32)
  rgb=cv2.remap(src_orig,xf,yf,cv2.INTER_CUBIC,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0))
  alpha=cv2.remap(mask_np,xf,yf,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
  # remove hard straight cut along torso at the very bottom: limited lower fade
  fade=np.clip((1000-yf)/205,0,1)
  fade=fade*fade*(3-2*fade)
  alpha=alpha*fade
  # mild changing shading from synthetic normal field, preserving original identity/paint
  nr=cv2.remap(normx,xf,yf,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
  shade=np.clip(1+pop*(.09*np.sin(angle*1.5)+nr*.13),.93,1.10)
  rgb=np.uint8(np.clip(rgb.astype(np.float32)*shade[:,:,None],0,255))
  return rgb,alpha.astype(np.float32)


def overlay_on(frame,im,alpha):
  return np.uint8(np.clip(frame.astype(np.float32)*(1-alpha[:,:,None]/255)+im.astype(np.float32)*(alpha[:,:,None]/255),0,255))


def render(progress, seconds=0):
  # slow parallax orbit, pauses to demonstrate volume
  angle=math.radians(15)*progress + (math.radians(5)*max(0,min(1,(seconds-4.65)/2.2)))
  pan=-15*progress
  base=wall.copy()
  # dark contact shadow on wall, perspective-aware frame
  shadow=np.zeros((H,W),np.uint8)
  quad=project_flat_quad(px-frame_pad+15,py-frame_pad+22,FW,FH,angle,pan)
  cv2.fillConvexPoly(shadow,np.round(quad).astype(np.int32),120)
  shadow=cv2.GaussianBlur(shadow,(0,0),19)
  base=np.uint8(np.clip(base.astype(np.float32)*(1-shadow[:,:,None]/255*.64),0,255))
  # floor/wall gallery remains fixed while artwork plane rotates
  src_corners=np.float32([[0,0],[painting_width,0],[painting_width,painting_height],[0,painting_height]])
  quad=project_flat_quad(px,py,painting_width,painting_height,angle,pan)
  matrix=cv2.getPerspectiveTransform(src_corners,quad)
  art = cv2.warpPerspective(resized,matrix,(W,H),flags=cv2.INTER_LINEAR)
  clean=cv2.warpPerspective(plate_resized,matrix,(W,H),flags=cv2.INTER_LINEAR)
  artmask=cv2.warpPerspective(np.ones((painting_height,painting_width),np.uint8)*255,matrix,(W,H),flags=cv2.INTER_NEAREST)
  # keep original painting until figure separates, revealing source-colour-based dark region
  inpaintmix=min(1,progress*7)
  artlayer=np.uint8(np.clip(art.astype(np.float32)*(1-inpaintmix)+clean.astype(np.float32)*inpaintmix,0,255))
  base=overlay_on(base,artlayer,artmask.astype(np.float32))
  # frame is artistically reconstructed / no claim of museum-authentic exact frame
  scorners=np.float32([[0,0],[FW,0],[FW,FH],[0,FH]])
  fquad=project_flat_quad(px-frame_pad,py-frame_pad,FW,FH,angle,pan)
  fmatrix=cv2.getPerspectiveTransform(scorners,fquad)
  frgb=cv2.warpPerspective(frame_np[:,:,:3],fmatrix,(W,H),flags=cv2.INTER_LINEAR)
  fa=cv2.warpPerspective(frame_np[:,:,3],fmatrix,(W,H),flags=cv2.INTER_LINEAR)
  base=overlay_on(base,frgb,fa.astype(np.float32))
  if progress>0:
    fg, a=foreground(progress,angle,pan)
    # cast ghost-free contact shadow on canvas/wall, behind the foreground and in front of frame
    sdx=int(progress*9);sdy=int(progress*12)
    translation=np.float32([[1,0,sdx],[0,1,sdy]])
    sh=cv2.warpAffine(a,translation,(W,H))
    sh=cv2.GaussianBlur(sh,(0,0),40)
    # to avoid giant shadow artifacts, keep it restrained
    base=np.uint8(np.clip(base.astype(np.float32)*(1-sh[:,:,None]/255*.08*progress),0,255))
    base=overlay_on(base,fg,a)
  # minimal elegant UI and non-false labels; title appears 0-1.5s
  canvas=Image.fromarray(base)
  d=ImageDraw.Draw(canvas)
  d.text((W//2,90),'ARTVISION  ·  3D STUDIO',font=font_sub,fill=(205,181,147),anchor='mm')
  d.text((W//2,133),'GIRL WITH A PEARL EARRING',font=font_title,fill=(245,238,220),anchor='mm')
  d.text((W//2,167),'JOHANNES VERMEER  ·  c. 1665',font=font_small,fill=(173,169,154),anchor='mm')
  d.text((W//2,1086),'MUSEUM POP-OUT  ·  V2 DEPTH MESH',font=font_sub,fill=(226,202,157),anchor='mm')
  d.text((W//2,1126),'Artwork: Mauritshuis  ·  3D effect: reconstruction',font=font_small,fill=(160,159,160),anchor='mm')
  return np.asarray(canvas,dtype=np.uint8)


def smoothstep(x):
  x=max(0,min(1,x));return x*x*(3-2*x)

def main():
  a=render(0);b=render(.62);c=render(1)
  Image.fromarray(a).save(OUTPUT/'01_ORIGINALE.jpg',quality=91)
  Image.fromarray(b).save(OUTPUT/'02_MOMENTO_USCITA.jpg',quality=91)
  Image.fromarray(c).save(OUTPUT/'03_POP_OUT_PARALLASSE_3D.jpg',quality=93)
  compare=np.hstack([a,c]);Image.fromarray(compare).save(OUTPUT/'04_PRIMA_DOPO.jpg',quality=92)
  if args.stills_only:
    print('Rendered review stills');return
  # Direct H264 video encoding, no paid APIs or GPU, ambient audio created locally
  mp4=OUTPUT/'05_VERMEER_POP_OUT_V2_CAMERA_3D.mp4'
  cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}',
       '-framerate',str(FPS),'-i','-', '-f','lavfi','-i', 'aevalsrc=0.005*sin(2*PI*110*t)+0.003*sin(2*PI*164.8*t)+0.004*sin(2*PI*220*t):s=48000',
       '-t',str(DURATION),'-c:v','libx264','-preset','ultrafast','-crf','22','-pix_fmt','yuv420p',
       '-c:a','aac','-b:a','96k','-movflags','+faststart',str(mp4)]
  process=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
  start=time.monotonic()
  try:
    for i in range(FPS*DURATION):
      t=i/FPS
      # opening 0.45s, 2.9s extraction, smooth shallow orbit; hold end for effect inspection
      p=smoothstep((t-.4)/4.2)
      if t>4.6:
        # show actual orbital parallax once emerged, subject changes perspective relative to fixed frame
        p=.92 + .08*math.sin((t-4.6)/(DURATION-4.6)*math.pi/2)
      img=render(p,t)
      process.stdin.write(img.tobytes())
      if i%48==0:print('frame',i,'/',FPS*DURATION,'elapsed',round(time.monotonic()-start,1),flush=True)
    process.stdin.close()
    err=process.stderr.read().decode(errors='replace')
    ret=process.wait()
    if ret:raise RuntimeError(err[-1500:])
  except Exception:
    process.kill();raise
  (OUTPUT/'SOURCE_NOTE.txt').write_text('Artwork: Johannes Vermeer, Girl with a Pearl Earring, Mauritshuis inventory 670.\nSource image: '+origin+'\nThis is a public-domain painting; reuse conditions for museum-provided photographs should be reviewed independently.\nEffect is a synthetic 2.5D depth field on the original painting, not reconstruction of hidden face parts. Scenic frame/room are reconstructions, not actual Mauritshuis.\nNo paid API or GPU, no ArtVision official master modified.\n',encoding='utf8')
  meta={
    'schema':'artvision-popout-v2-cpu','artwork':'Girl with a Pearl Earring','artist':'Johannes Vermeer',
    'source':'Mauritshuis inventory 670', 'source_location':origin,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'mask_sha256':hashlib.sha256(MASK.read_bytes()).hexdigest(),
    'method':'source-locked manual GrabCut segmentation and hand-tuned curved depth mesh with perspective and orbital parallax (2.5D)',
    'is_full_3d_mesh':False,'generated_ai_image':False,'paid_api_calls':0,'modifies_production':False,
    'limits':'Unseen surfaces not reconstructed; face contour changes with perspective approximations; scenic frame reconstructed, gallery not authentic.',
  }
  for f in sorted(OUTPUT.glob('0*')):
    if f.is_file():meta[f.name]={'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
  (OUTPUT/'MANIFEST_V2.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding='utf8')
  print('Video complete:',mp4,mp4.stat().st_size, 'runtime',round(time.monotonic()-start,2))

if __name__=='__main__':main()