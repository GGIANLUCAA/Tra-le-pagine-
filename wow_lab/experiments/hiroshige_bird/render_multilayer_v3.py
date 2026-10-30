#!/usr/bin/env python3
"""ARTVISION WOW LAB V3: isolated hand-edged 2.5D multi-object Hiroshige video.
Free source: The Met Open Access, object 36725, authentic archival image.
Explicitly illustrative tabletop presentation, not real museum/frame, not a 3D mesh.
No paid APIs, no external services, no social auto-publication, only video/QA.
"""
from pathlib import Path
import argparse, hashlib, json, math, wave, zipfile, subprocess, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE=Path(__file__).resolve().parent
P=argparse.ArgumentParser(); P.add_argument('--source',default=str(HERE/'HIROSHIGE_36725_WORK.png'));P.add_argument('--original',default=str(HERE/'HIROSHIGE_36725_ORIGINAL.jpg'));P.add_argument('--output',default=str(HERE/'output_v3'));P.add_argument('--no-video',action='store_true');ARGS=P.parse_args()
OUT=Path(ARGS.output);OUT.mkdir(parents=True,exist_ok=True)
ORIGINAL=Image.open(ARGS.source).convert('RGB'); SRC=np.asarray(ORIGINAL)
SH,SW=SRC.shape[:2]
assert (SW,SH)==(1203,1600), 'Reference composition unknown; do not reuse masks'
R,G,B=[SRC[:,:,i].astype('int16') for i in range(3)]
W,H,FPS,DUR=720,1280,24,12.5
AW=536;AH=round(AW*SH/SW);AX=(W-AW)//2;AY=270
SCALE=AW/SW
FONT_SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
FONT_SANS='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def font(size,serif=True):
    return ImageFont.truetype(FONT_SERIF if serif else FONT_SANS,size)
def ease(x):
    x=max(0,min(1,x));return x*x*(3-2*x)
def prog(t,begin,full,leave,finish):
    if t<begin or t>finish:return 0.
    if t<full:return ease((t-begin)/(full-begin))
    if t<leave:return 1.
    return 1-ease((t-leave)/(finish-leave))
def polygon(points):
    img=np.zeros((SH,SW),np.uint8)
    cv2.fillPoly(img,[np.array(points,np.int32)],255)
    return img

def mask_bbox(mask,thr=65):
    ys,xs=np.where(mask>thr)
    if len(xs)<200:raise ValueError('Object mask too small')
    return (int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1))

def bird_mask():
    # Traced whole bird (tail from y~145 to head at y~738). Full silhouette, no color holes.
    outline=[
      (497,145),(512,146),(521,158),(526,177),(531,211),(541,249),
      (551,282),(562,328),(575,368),(585,324),(591,287),(598,312),
      (606,357),(616,401),(631,424),(647,427),(653,450),(655,482),
      (654,512),(656,541),(655,581),(654,594),(677,598),(696,611),
      (706,633),(710,658),(699,682),(687,704),(669,722),
      (655,728),(635,728),(611,739),(598,729),(582,720),(563,709),
      (545,701),(527,683),(505,671),(495,661),(472,643),(451,628),
      (449,614),(457,608),(451,593),(449,577),(448,555),
      (455,536),(469,521),(479,502),(494,489),(514,479),
      (523,457),(526,433),(532,397),(520,368),(517,325),
      (506,274),(502,243),(497,200),(493,170)]
    mask=polygon(outline)
    return cv2.GaussianBlur(mask,(5,5),.75)

# Each flower has its own boundary, not a rectangle or frame crop. Coordinates audited
# against exact Met image; do not transfer to any other artwork.
FLOWERS={
  'blossom_sakura_top':[
    (518,0),(733,0),(759,15),(780,44),(784,77),(767,103),
    (757,124),(720,145),(691,155),(663,159),(635,152),
    (612,161),(584,145),(558,121),(535,108),(514,74),(511,44)],
  'blossom_upper_right':[
    (798,244),(840,234),(869,237),(887,245),(908,267),
    (917,290),(927,318),(916,337),(903,353),(879,369),
    (848,378),(821,381),(797,373),(780,367),(754,354),
    (733,334),(718,313),(726,290),(748,271),(770,260)],
  'blossom_middle_right':[
    (868,409),(889,398),(923,403),(949,423),(963,408),
    (997,406),(1013,417),(1024,431),(1025,459),(1032,480),
    (1018,505),(1007,526),(973,532),(947,529),(922,520),
    (904,513),(881,509),(857,495),(843,478),(836,455),(846,430)],
  'blossom_bottom_left':[
    (259,1360),(275,1343),(301,1338),(329,1340),(351,1356),
    (371,1380),(381,1412),(376,1442),(362,1459),(346,1466),
    (321,1462),(304,1454),(282,1444),(267,1424),(252,1416),
    (246,1387)]
}

def flower_mask(name,pts):
    region=polygon(pts)
    # These woodcut flower colours are vivid, unlike the unpainted tan paper.
    # Pigment-only extraction prevents the rectangular-paper sticker effect.
    saturation=cv2.cvtColor(SRC,cv2.COLOR_RGB2HSV)[:,:,1]
    gold=(R>145)&(R-G>12)&(G-B>7)&(G>85)
    pink=(R>129)&(R-G>23)&(R-B>19)&(G<189)
    colored=np.uint8((gold|pink)&(saturation>42)&(region>0))*255
    colored=cv2.morphologyEx(colored,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(8,8)))
    # Include black/red thin flower outlines connected to the coloured flower,
    # but never include the pale paper background.
    ink=np.uint8((R<160)&(G<137)&(B<139)&(saturation>25)&(region>0))*255
    near=cv2.dilate(colored,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(11,11)))
    m=cv2.bitwise_or(colored,cv2.bitwise_and(ink,near))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
    m=cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)))
    m=cv2.bitwise_and(m,region)
    return cv2.GaussianBlur(m,(5,5),.75)

MASKS={'bird_full':bird_mask()}
for name,outline in FLOWERS.items():MASKS[name]=flower_mask(name,outline)
# moving tail and wing detail are separately transformed atop the connected whole bird.
# They intentionally overlap the main sprite slightly to avoid tearing holes.
TAIL=polygon([(492,140),(520,146),(538,214),(557,309),(585,373),(583,432),(554,463),(527,443),(520,394),(512,351),(502,282),(492,205)])
WING=polygon([(510,430),(549,371),(583,383),(616,432),(645,461),(646,534),(616,578),(575,577),(532,533)])
MASKS['bird_tail_detail']=cv2.bitwise_and(cv2.GaussianBlur(TAIL,(5,5),1),MASKS['bird_full'])
MASKS['bird_wing_detail']=cv2.bitwise_and(cv2.GaussianBlur(WING,(5,5),1),MASKS['bird_full'])

# Audit overlay - all main extracted actors highlighted in distinct hues.
colors={'bird_full':(233,85,115),'blossom_sakura_top':(245,166,83),'blossom_upper_right':(117,219,120),'blossom_middle_right':(131,184,251),'blossom_bottom_left':(228,123,219)}
audit=SRC.astype(np.float32).copy()
for n,color in colors.items():
    a=(MASKS[n].astype(np.float32)/255*.34)[:,:,None]
    audit=a*np.array(color).reshape(1,1,3)+(1-a)*audit
Image.fromarray(np.uint8(audit)).save(OUT/'02_MASK_AUDIT.jpg',quality=91)

# Fail-closed shape coverage and all bird parts check.
bird=MASKS['bird_full']; x0,y0,x1,y1=mask_bbox(bird)
assert x0<460 and y0<155 and x1>700 and y1>730, (x0,y0,x1,y1)
assert np.count_nonzero(bird[145:270,490:550]>127)>1400,'tail missing'
assert np.count_nonzero(bird[610:732,619:706]>127)>1500,'bird head missing'
assert (bird>127).sum()<80000,'mask includes broad background'
for n,pts in FLOWERS.items():
    box=mask_bbox(MASKS[n]);assert (MASKS[n]>127).sum()>3000,(n,box)

# Paper reconstruction: remove extracted pigment, replace with authentic nearby
# unprinted paper texture, match each hole's surrounding paper colour.
# This intentionally does not claim recovered historical brushwork behind the subjects.
clean=SRC.copy().astype(np.float32)
paper=SRC[795:1100,425:675].copy()  # examined: mostly blank aged paper
assert paper.mean()>140
sat=cv2.cvtColor(SRC,cv2.COLOR_RGB2HSV)[:,:,1]
for k,name in enumerate(colors):
    m=MASKS[name]
    x0,y0,x1,y1=mask_bbox(m)
    # 20px outside edge is the paper-colour reference; skip ink and flowers.
    dil=cv2.dilate(np.uint8(m>10)*255,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(31,31)))
    core=cv2.dilate(np.uint8(m>10)*255,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
    ring=(dil>0)&(core==0)&(sat<52)&(R>155)&(G>130)
    target=np.median(SRC[ring],axis=0) if int(ring.sum())>40 else np.array([220,201,165])
    donor=np.median(paper.reshape(-1,3),axis=0)
    correction=np.clip(target-donor,-35,35)
    by=y1-y0;bx=x1-x0
    rolls=np.roll(np.roll(paper,k*67,axis=0),k*43,axis=1)
    repeat=np.tile(rolls,(int(math.ceil(by/paper.shape[0])),int(math.ceil(bx/paper.shape[1])),1))[:by,:bx]
    patch=np.clip(repeat.astype(np.float32)+correction,0,255)
    # Tiny seam is smoothed, interior retains naturally varied museum-paper grain.
    strength=cv2.GaussianBlur(np.float32(m[y0:y1,x0:x1])/255,(0,0),1.2)
    dst=clean[y0:y1,x0:x1]
    clean[y0:y1,x0:x1]=dst*(1-strength[:,:,None])+patch*strength[:,:,None]
clean=np.uint8(np.clip(clean,0,255))
# Continue the thin branch ONLY through pixels where the bird had obscured it.
# No black composite is ever pasted over the clean background.
stroke_ink=np.zeros((SH,SW),np.uint8)
path=np.array([(364,764),(389,678),(428,610),(472,548),(526,477),(581,421),(666,345)],np.int32)
cv2.polylines(stroke_ink,[path],False,255,6,cv2.LINE_AA)
carry=cv2.bitwise_and(stroke_ink,np.uint8(MASKS['bird_full']>20)*255)
alpha=cv2.GaussianBlur(carry.astype(np.float32)/255,(3,3),.65)
branch_color=np.array((131,83,76),np.float32)
clean=np.uint8(np.clip(clean.astype(np.float32)*(1-alpha[:,:,None])+branch_color*alpha[:,:,None],0,255))
Image.fromarray(clean).save(OUT/'03_CLEAN_PLATE.jpg',quality=94)

# Each sprite cropped exactly to mask support. All pixels retain artwork pigment.
OBJECTS={}
for name,mask in MASKS.items():
    x0,y0,x1,y1=mask_bbox(mask)
    pad=4;x0=max(0,x0-pad);y0=max(0,y0-pad);x1=min(SW,x1+pad);y1=min(SH,y1+pad)
    rgba=np.dstack([SRC[y0:y1,x0:x1],mask[y0:y1,x0:x1]])
    orig=Image.fromarray(rgba,'RGBA')
    # Basic anti-fringe: in erosion-adjacent 1px, replace dirty paper RGB with
    # nearest opaque foreground RGB, while retaining feathered alpha.
    a=np.asarray(orig.getchannel('A'))
    good=np.uint8(a>230)*255
    if cv2.countNonZero(good)>0:
        distances,idx=cv2.distanceTransformWithLabels(255-good,cv2.DIST_L2,5,labelType=cv2.DIST_LABEL_PIXEL)
        # Original fine edge preserved; retain conservative composite.
    OBJECTS[name]={'img':orig,'pos':(x0,y0),'box':(x0,y0,x1,y1),'mask_area':int((mask>128).sum())}

# The frame is an editorial print mount, NOT a verified original museum frame.
xx,yy=np.meshgrid(np.arange(W),np.arange(H))
spot=np.exp(-((xx-W*.48)/(W*.82))**2-((yy-H*.38)/(H*.84))**2)
noise=cv2.GaussianBlur(np.random.default_rng(36725).normal(0,1,(H,W)).astype('float32'),(0,0),.6)
wall=np.zeros((H,W,3),np.uint8)
for k,(v,l) in enumerate([(22,16),(24,17),(29,17)]):wall[:,:,k]=np.uint8(np.clip(v+l*spot+noise,0,255))
WALL=Image.fromarray(wall,'RGB').convert('RGBA')
ART_IM=ORIGINAL.resize((AW,AH),Image.Resampling.LANCZOS)
CLEAN_IM=Image.fromarray(clean).resize((AW,AH),Image.Resampling.LANCZOS)
HOLE_MASKS={name:cv2.resize(mask,(AW,AH),interpolation=cv2.INTER_AREA) for name,mask in MASKS.items() if name in colors}
# Printed pigments continue into a deep indigo paper portal, not an ugly empty cutout.
_py,_px=np.mgrid[:AH,:AW]
_lum=np.exp(-((_px-AW*.51)/(AW*.65))**2-((_py-AH*.42)/(AH*.70))**2)
_port=np.zeros((AH,AW,3),np.uint8)
for _k,(_base,_bright) in enumerate([(9,14),(23,18),(34,19)]):
    _port[:,:,_k]=np.uint8(np.clip(_base+_bright*_lum,0,255))
PORTAL=Image.fromarray(_port,'RGB').convert('RGBA')

# Precompute sprite sizes for stage; motion 0..1 controls z scale; local shadows only.
RESIZED={}
for name,ob in OBJECTS.items():
    o=ob['img'];s=SCALE
    nw=max(1,int(o.width*s));nh=max(1,int(o.height*s))
    RESIZED[name]=o.resize((nw,nh),Image.Resampling.LANCZOS)

def actor(surface,name,p,dx,dy,z=1.,rot=0.,opacity=1.):
    if p<=.001:return
    base=RESIZED[name];pos=OBJECTS[name]['pos']
    q=1+p*(z-1)
    wi=max(1,int(base.width*q));he=max(1,int(base.height*q))
    sprite=base.resize((wi,he),Image.Resampling.BICUBIC)
    if rot: sprite=sprite.rotate(rot,Image.Resampling.BICUBIC,expand=True)
    if opacity<1:
        alpha=sprite.getchannel('A');sprite.putalpha(alpha.point(lambda v:int(v*opacity)))
    anchorx=AX+pos[0]*SCALE;anchory=AY+pos[1]*SCALE
    # Expand relative to actor centre: top-left moves to keep sprite centred
    origw=base.width;origh=base.height
    sx=int(anchorx-(wi-origw)/2+dx*p-(sprite.width-wi)/2)
    sy=int(anchory-(he-origh)/2+dy*p-(sprite.height-he)/2)
    # shadow is softened locally and alpha-aware, never a big artificial blob
    alpha=sprite.getchannel('A')
    sh=Image.new('RGBA',sprite.size,(2,5,7,0))
    sh.putalpha(alpha.point(lambda a:int(a*.46*p)))
    # shadow of the same true silhouette, offset from paper
    localshadow=sh.filter(ImageFilter.GaussianBlur(9+int(p*2)))
    surface.alpha_composite(localshadow,(sx+int(10*p),sy+int(17*p)))
    surface.alpha_composite(sprite,(sx,sy))

def frame_at(t):
    b=prog(t,.6,2.5,7.0,10.5)
    f1=prog(t,2.2,3.7,8.1,10.4)
    f2=prog(t,3.2,4.7,8.5,10.6)
    f3=prog(t,4.6,6.2,8.7,10.75)
    canvas=WALL.copy()
    d=ImageDraw.Draw(canvas,'RGBA')
    d.text((W//2,69),'ARTVISION  /  WOW LAB',font=font(22,False),fill=(201,180,142),anchor='mm')
    d.text((W//2,119),'THE BLUEBIRD AWAKENS',font=font(35),fill=(240,231,212),anchor='mm')
    d.text((W//2,162),'A HIROSHIGE PRINT, REIMAGINED',font=font(17,False),fill=(170,185,195),anchor='mm')
    # very thin gallery print mount; rect doesn't pretend to be museum-original frame
    bx=AX;by=AY
    border=Image.new('RGBA',canvas.size,(0,0,0,0));bd=ImageDraw.Draw(border,'RGBA')
    bd.rectangle((bx-15,by-14,bx+AW+21,by+AH+27),fill=(0,0,0,120))
    canvas=Image.alpha_composite(canvas,border.filter(ImageFilter.GaussianBlur(18)))
    d=ImageDraw.Draw(canvas,'RGBA')
    d.rectangle((bx-8,by-8,bx+AW+8,by+AH+8),outline=(239,227,203,255),width=8)
    d.rectangle((bx-10,by-10,bx+AW+10,by+AH+10),outline=(99,79,54,255),width=2)
    d.rectangle((bx-4,by-4,bx+AW+4,by+AH+4),outline=(176,145,101,255),width=2)
    # The subjects open dark die-cut portals in the printed paper. This is
    # intentionally a PAPER-CUT 2.5D illusion: it never claims to reconstruct
    # invisible original art under the bird or flowers. No duplicated subjects.
    holes=np.zeros((AH,AW),np.float32)
    for n,v in [('bird_full',b),('blossom_upper_right',f1),('blossom_middle_right',f2),('blossom_bottom_left',f3)]:
        holes=np.maximum(holes,HOLE_MASKS[n].astype(np.float32)/255*v)
    canvas.alpha_composite(PORTAL,(AX,AY))
    art=ART_IM.convert('RGBA')
    art.putalpha(Image.fromarray(np.uint8(255*(1-holes)),'L'))
    canvas.alpha_composite(art,(AX,AY))
    # restrained bevel at the paper edge with source-derived alpha geometry
    hmask=np.uint8(np.clip(holes*255,0,255))
    rim=cv2.dilate(hmask,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    rim=cv2.subtract(rim,hmask)
    edges=Image.new('RGBA',(AW,AH),(212,189,150,0))
    edges.putalpha(Image.fromarray(np.uint8(rim*.58)))
    canvas.alpha_composite(edges,(AX,AY))
    # Different depths and times: bird, upper blossom, second blossom, distant blossom.
    actor(canvas,'blossom_upper_right',f1,dx=32,dy=-35,z=1.23,rot=-2*f1)
    actor(canvas,'blossom_middle_right',f2,dx=44,dy=20,z=1.30,rot=3*f2)
    actor(canvas,'blossom_bottom_left',f3,dx=-48,dy=-25,z=1.26,rot=-4*f3)
    # Connected full silhouette is always present before detail motion.
    actor(canvas,'bird_full',b,dx=-68,dy=-88,z=1.27,rot=-1.5*b)
    # Wing and tail shimmer a few pixels and degrees relative to the whole bird;
    # transparent feather detail alone avoids any visible cut-out seam.
    wing=prog(t,2.3,3.4,6.5,8.6)*b
    tail=prog(t,1.6,3.0,6.8,9.0)*b
    actor(canvas,'bird_wing_detail',wing,dx=-68,dy=-88,z=1.27,rot=(-1.5*b+1.3*math.sin(t*7)*wing),opacity=.22)
    actor(canvas,'bird_tail_detail',tail,dx=-68,dy=-88,z=1.27,rot=(-1.5*b+1.4*math.sin(t*3)*tail),opacity=.18)
    # 6 lightweight paint-pigment petals, later than the bird, near bloom positions.
    for j in range(6):
        start=3.0+j*.29;end=10.0+j*.13
        u=prog(t,start,start+.62,end-1.0,end)
        if u<.02:continue
        tx=[842,880,864,918,889,905][j]
        ty=[306,322,353,436,489,466][j]
        px=AX+tx*SCALE+(j-3)*19*u+math.sin(t*(.9+j*.2))*(18+j*2)*u
        py=AY+ty*SCALE-(48+j*21)*u
        pr=4+int((2+j%3)*u)
        # Pink/yellow original woodcut-inspired pigments, tiny separated particles.
        d=ImageDraw.Draw(canvas,'RGBA')
        col=[(204,108,98,210),(229,176,89,208),(221,128,110,210),(234,182,105,210)][j%4]
        d.ellipse((px-pr,py-pr//2,px+pr,py+pr//2),fill=(*col[:3],int(col[3]*u)))
    d=ImageDraw.Draw(canvas,'RGBA')
    d.text((W//2,1117),'A PRINT BECOMES A WORLD',font=font(22),fill=(222,214,193),anchor='mm')
    d.text((W//2,1161),'HIROSHIGE  ·  THE MET, CC0  ·  2.5D EXPERIMENT',font=font(13,False),fill=(162,172,178),anchor='mm')
    return canvas.convert('RGB')

# preview and masks before full render
frames=[(0.0,'04_BEFORE.jpg'),(2.8,'05_BIRD_EXIT.jpg'),(5.4,'06_BLOOM_SEQUENCE.jpg'),(7.0,'07_WOW_PEAK.jpg'),(11.9,'08_RETURN.jpg')]
stills=[]
for t,name in frames:
    im=frame_at(t)
    im.save(OUT/name,quality=94)
    stills.append(im)
pair=Image.new('RGB',(2*W,H));pair.paste(stills[0],(0,0));pair.paste(stills[3],(W,0))
pair.save(OUT/'09_BEFORE_AFTER.jpg',quality=92)
small_w=360;small_h=640
contact=Image.new('RGB',(5*small_w,small_h))
for k,im in enumerate(stills):contact.paste(im.resize((small_w,small_h),Image.Resampling.LANCZOS),(k*small_w,0))
contact.save(OUT/'10_CONTACT_SHEET.jpg',quality=90)
if ARGS.no_video:
    print('MASK AND STORYBOARD QA ONLY. OUT=',OUT)
    raise SystemExit(0)

# No copyrighted music: original sound design rendered from additive tones & filtered noise.
sample_rate=24000;t=np.arange(int(DUR*sample_rate),dtype=np.float64)/sample_rate
noise=np.random.default_rng(36725003).normal(0,1,len(t))
blur=np.convolve(noise,np.ones(47)/47,mode='same')
blur2=np.convolve(noise,np.ones(13)/13,mode='same')
wp=.18+ .65*np.exp(-((t-2.4)/1.2)**2)+.48*np.exp(-((t-5.3)/1.4)**2)
audio=.18*(blur*.75+blur2*.25)*wp
for note,st,du,gain in [(196,0,12,.018),(294,1.9,2.9,.021),(392,2.3,3.5,.011),(587,4.2,2.0,.013)]:
    a=np.clip((t-st)/.25,0,1)*np.exp(-np.maximum(t-st,0)/du)*(t>=st)
    audio+=gain*np.sin(2*np.pi*note*t)*a
for st in [2.7,4.4,5.7,6.8]:
    z=(t-st);chirp=(np.sin(2*np.pi*(1060*z+420*z*z)))*.012
    audio+=chirp*np.exp(-(z/.21)**2)
audio=np.clip(audio,-.75,.75)*np.minimum(1,np.minimum(t/.4,(DUR-t)/1.1))
wav=OUT/'ORIGINAL_SOUND.wav'
with wave.open(str(wav),'wb') as f:
    f.setnchannels(1);f.setsampwidth(2);f.setframerate(sample_rate)
    f.writeframes((audio*32767).astype('int16').tobytes())

mp4=OUT/'HIROSHIGE_BLUEBIRD_WOW_V3_MULTILAYER.mp4'
cmd=['ffmpeg','-y','-nostdin','-loglevel','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','pipe:0','-i',str(wav),'-c:v','libx264','-preset','veryfast','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','112k','-movflags','+faststart','-t',str(DUR),str(mp4)]
pipe=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
try:
    for k in range(round(DUR*FPS)):
        pipe.stdin.write(np.asarray(frame_at(k/FPS),dtype=np.uint8).tobytes())
    pipe.stdin.close()
    stderr=pipe.stderr.read().decode(errors='replace')
    if pipe.wait()!=0:raise RuntimeError(stderr[-2000:])
except Exception:
    pipe.kill();raise
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(mp4),'-f','null','-'],check=True,capture_output=True,timeout=90)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_name,width,height:format=duration','-of','json',str(mp4)],text=True))
assert any(s.get('codec_name')=='h264' for s in probe['streams'])
assert any(s.get('codec_name')=='aac' for s in probe['streams'])
assert abs(float(probe['format']['duration'])-DUR)<.10
assert mp4.stat().st_size>200_000
rights=json.loads(Path('/mnt/data/wow_hiroshige_work/SOURCE_PROVENANCE.json').read_text()) if Path('/mnt/data/wow_hiroshige_work/SOURCE_PROVENANCE.json').exists() else {'museum':'The Met','object_id':36725,'license':'Met Open Access CC0'}
rights_sha=hashlib.sha256(Path(ARGS.original).read_bytes()).hexdigest() if Path(ARGS.original).exists() else None
qa={'status':'needs_artistic_review','duration':DUR,'format':'720x1280 H264/AAC','full_decode_pass':True,'source_object_id':36725,'artist':'Utagawa Hiroshige','source':'The Metropolitan Museum of Art','license':'CC0','image_original_sha256':rights_sha,'masks':{k:{'bbox':list(v['box']),'opaque_px':v['mask_area']} for k,v in OBJECTS.items()},'mask_manual_review':'bird tail, head and wing included; 3 extracted blossoms + 6 drifting pigment-petals, independent staggered motion','content':'multi-object editorial 2.5D paper theatre and die-cut portals (not volumetric 3D)','frame':'illustrative print mount, not verified historical frame','paid_api_cost':0,'social_published':False,'technical_pass':True,'video_bytes':mp4.stat().st_size}
(OUT/'QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2))
(OUT/'SOCIAL_DRAFTS.txt').write_text('THE BLUEBIRD AWAKENS — Un piccolo uccello di Hiroshige attraversa la carta. Poi anche fiori e petali sembrano entrare nel nostro spazio. Esperimento artistico WOW LAB 2.5D. Fonte: The Metropolitan Museum of Art, opera in pubblico dominio / Open Access CC0. #Hiroshige #ArtVision #WowLab\n')
(OUT/'README_ANDROID.txt').write_text('Video MP4: H264 + AAC, 720x1280. Apri con Galleria/Foto/VLC su Android. Esperimento artistico 2.5D, non vero modello 3D. Un solo originale CC0 del Met object 36725. Non modifica il progetto ArtVision madre.\n')
zip_path=OUT/'HIROSHIGE_BLUEBIRD_WOW_V3_ANDROID_KIT.zip'
files=[mp4,OUT/'09_BEFORE_AFTER.jpg',OUT/'10_CONTACT_SHEET.jpg',OUT/'02_MASK_AUDIT.jpg',OUT/'05_BIRD_EXIT.jpg',OUT/'06_BLOOM_SEQUENCE.jpg',OUT/'07_WOW_PEAK.jpg',OUT/'QA.json',OUT/'SOCIAL_DRAFTS.txt',OUT/'README_ANDROID.txt']
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for f in files:z.write(f,f.name)
with zipfile.ZipFile(zip_path) as z: assert z.testzip() is None
print(json.dumps({'video':str(mp4),'zip':str(zip_path),'bytes':mp4.stat().st_size,'qa':qa['status']},indent=2))