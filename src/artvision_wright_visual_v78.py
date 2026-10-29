"""ArtVision V78 | Wright of Derby | 4x1 source-faithful visual director.
One authentic photograph INCLUDING the exhibited original gilded frame.
The museum room is declared cinematic staging, not a historical gallery.
No generic drawn border, no painting hallucinations, no paid APIs.
"""
from __future__ import annotations
import math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

W,H,FPS=720,1280,15
FONT_SERIF="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SANS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def font(n,serif=False):
    return ImageFont.truetype(FONT_SERIF if serif else FONT_SANS,int(n))

def smooth(t):
    x=max(0,min(1,float(t)))
    return x*x*(3-2*x)
def mix(a,b,t):return a+(b-a)*t

def title_overlay(im,t,start=0,end=3.9,who="JOSEPH WRIGHT OF DERBY",title="ONE BREATH FROM DEATH"):
    if t<start or t>end:return im
    opacity=min(1.,(t-start)/.55,(end-t)/.7)
    if opacity<=0:return im
    im=im.convert("RGBA")
    lay=Image.new("RGBA",im.size,(0,0,0,0));d=ImageDraw.Draw(lay)
    d.rounded_rectangle((38,53,682,202),radius=12,fill=(12,15,18,int(180*opacity)))
    for y,s,size in [(76,title,31),(146,who+"  ·  1768",19)]:
        f=font(size,True if y==76 else False);box=d.textbbox((0,0),s,font=f)
        d.text(((W-(box[2]-box[0]))/2,y),s,font=f,fill=(246,233,207,int(255*opacity)))
    return Image.alpha_composite(im,lay).convert("RGB")

def room(seed=725):
    rng=np.random.default_rng(seed)
    yy,xx=np.mgrid[0:H,0:W]
    grain=rng.normal(0,2.0,(H,W))
    glow=22*np.exp(-((xx-360)/430.)**2-((yy-460)/450.)**2)
    arr=np.empty((H,W,3),dtype=np.uint8)
    for ch,base in enumerate((61,68,68)):
        arr[:,:,ch]=np.clip(base+glow*(.94,1,.98)[ch]+grain,0,255)
    im=Image.fromarray(arr,"RGB");d=ImageDraw.Draw(im)
    # Single quiet exhibition wall, no fabricated architectural ornament.
    d.rectangle((0,1075,W,H),fill=(34,36,36))
    d.line((0,1074,W,1074),fill=(86,84,77),width=5)
    # Gallery floor shadows remain secondary to actual painting.
    for i in range(5):
        d.line((0,1100+i*40,W,1100+i*40),fill=(38+i*2,40+i*2,39+i*2),width=1)
    d.rounded_rectangle((318,768,402,797),radius=2,fill=(178,172,148))
    d.text((333,774),"NG725",font=font(13),fill=(41,43,45))
    return im

def museum(art,roomimg,zoom,focus):
    """Correct perspective to a single gallery plane; direct original resolution sampling."""
    fx,fy=focus
    pw=405.;ph=pw*art.height/art.width
    px,py=360.,455.
    # The actual physical 244x183cm oil canvas and photographed historical frame
    # occupy this rectangle at realistic human viewing distance, not tiny sheet scale.
    camx=mix(px,px+(fx-.5)*pw,smooth(min(1.,max(0,(zoom-1)/5))))
    camy=mix(py,py+(fy-.5)*ph,smooth(min(1.,max(0,(zoom-1)/5))))
    z=max(.5,float(zoom))
    M=np.float32([[z,0,W/2-z*camx],[0,z,H/2-z*camy]])
    base=cv2.warpAffine(np.asarray(roomimg),M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
    out=Image.fromarray(base,"RGB")
    x=(px-pw/2-camx)*z+W/2
    y=(py-ph/2-camy)*z+H/2
    ww=pw*z;hh=ph*z
    if x>W or y>H or x+ww<0 or y+hh<0:return out
    d=ImageDraw.Draw(out)
    if z<5:
        off=max(1,int(4*z))
        d.rectangle((x+off,y+off,x+ww+off,y+hh+off),fill=(26,27,27))
    x0=max(0,int(math.floor(x)));x1=min(W,int(math.ceil(x+ww)))
    y0=max(0,int(math.floor(y)));y1=min(H,int(math.ceil(y+hh)))
    if x1<=x0 or y1<=y0:return out
    sx0=max(0,(x0-x)/ww*art.width);sx1=min(art.width,(x1-x)/ww*art.width)
    sy0=max(0,(y0-y)/hh*art.height);sy1=min(art.height,(y1-y)/hh*art.height)
    p=art.crop((sx0,sy0,sx1,sy1)).resize((x1-x0,y1-y0),Image.Resampling.BICUBIC)
    out.paste(p,(x0,y0))
    return out

# Coherent semantic beats, taken from exact canvas; no fictitious new scenes.
DETAILS=[
    ("WHITE COCKATOO",(.56,.17),2.65),
    ("THE EXPERIMENTER",(.51,.35),2.55),
    ("THE YOUNG GIRL",(.81,.65),2.62),
    ("THE REFLECTION",(.57,.67),2.65),
    ("THE WITNESSES",(.23,.46),2.15),
    ("THE DECISION",(.66,.46),2.30),
    ("THE WHOLE ROOM",(.5,.51),1.0),
]

def detail_crop(art,focus,zoom):
    # A 9:16 viewport for precise details of the original 4:3 painting.
    iw,ih=art.size
    aspect=W/H
    cw=min(iw,ih*aspect)/max(1.,zoom)
    ch=cw/aspect
    cx=float(np.clip(focus[0]*iw,cw/2,iw-cw/2))
    cy=float(np.clip(focus[1]*ih,ch/2,ih-ch/2))
    return art.crop((cx-cw/2,cy-ch/2,cx+cw/2,cy+ch/2)).resize((W,H),Image.Resampling.LANCZOS)

def whole_art(art):
    out=Image.new("RGB",(W,H),(21,23,25))
    sheet=art.copy();sheet.thumbnail((int(W*.93),int(H*.83)),Image.Resampling.LANCZOS)
    out.paste(sheet,((W-sheet.width)//2,(H-sheet.height)//2))
    return out

def scene(art,idx,u,mode):
    if idx==6:return whole_art(art)
    _,focus,mag=DETAILS[idx]
    # Long holds for readable people and apparatus; no restless oscillation.
    z=mag*(.985+.032*smooth(u)) if mode=="critic" else mag*(.96+.065*smooth(u))
    return detail_crop(art,focus,z)

def critico_standard(art,t,duration):
    # Music and Gacrux are exactly shared with Critico Museum in the renderer.
    weights=[.10,.16,.18,.16,.14,.14,.12]
    bounds=[0.];[bounds.append(bounds[-1]+duration*w) for w in weights]
    idx=next((i for i in range(7) if bounds[i]<=t<bounds[i+1]),6)
    u=(t-bounds[idx])/max(.001,bounds[idx+1]-bounds[idx])
    result=scene(art,idx,u,"critic")
    return title_overlay(result,t,title="A BIRD. ONE DECISION.")

def cinema_standard(art,t,duration):
    # Different edit from Critico; ~6 key shot changes with 0.42s blends.
    weights=[.15,.17,.14,.14,.14,.14,.12]
    bounds=[0.];[bounds.append(bounds[-1]+duration*w) for w in weights]
    idx=next((i for i in range(7) if bounds[i]<=t<bounds[i+1]),6)
    u=(t-bounds[idx])/max(.001,bounds[idx+1]-bounds[idx])
    result=scene(art,idx,u,"cinema")
    if idx>0 and t-bounds[idx]<.42:
        result=Image.blend(scene(art,idx-1,1,"cinema"),result,smooth((t-bounds[idx])/.42))
    return title_overlay(result,t,title="WHO WILL SAVE THE BIRD?")

def museum_frame(art,roomimg,t,duration,critic=False):
    enter=9 if not critic else 11
    leave=10 if not critic else 11
    if t<enter:
        u=smooth(t/enter);z=mix(1,15,u)
        focus=(mix(.5,.55,u),mix(.5,.20,u))
    elif t<duration-leave:
        u=(t-enter)/max(.001,duration-enter-leave)
        pts=[(.55,.20),(.52,.38),(.81,.63),(.57,.66),(.25,.45),(.60,.50),(.5,.50)]
        idx=min(int(u*(len(pts)-1)),len(pts)-2)
        k=smooth(u*(len(pts)-1)-idx)
        focus=tuple(mix(a,b,k) for a,b in zip(pts[idx],pts[idx+1]))
        z=15+2.0*(math.sin(math.pi*u)**2)
    else:
        u=smooth((t-(duration-leave))/leave)
        z=mix(15,1,u)
        focus=(mix(.5,.5,u),mix(.5,.5,u))
    result=museum(art,roomimg,z,focus)
    return title_overlay(result,t,title="ENTER THE EXPERIMENT")

def cover(art,variant):
    out=Image.new("RGB",(1080,1920),(18,21,23))
    p=art.copy();p.thumbnail((1000,1150),Image.Resampling.LANCZOS)
    out.paste(p,((1080-p.width)//2,430))
    d=ImageDraw.Draw(out)
    for y,line in [(95,"THE AIR PUMP"),(190,"EXPERIMENT")]:
        f=font(71,True);bb=d.textbbox((0,0),line,font=f)
        d.text(((1080-(bb[2]-bb[0]))//2,y),line,font=f,fill=(239,221,187))
    cap="CRITICO D'ARTE" if "critico" in variant else "CINEMATIC EDITION"
    if "museum" in variant:cap="MUSEUM IMMERSION · "+cap
    d.text((73,1700),cap,font=font(30),fill=(224,206,169))
    d.text((73,1770),"JOSEPH WRIGHT OF DERBY  ·  1768",font=font(27),fill=(197,194,185))
    d.text((73,1818),"NATIONAL GALLERY · NG725",font=font(23),fill=(157,163,162))
    return out
