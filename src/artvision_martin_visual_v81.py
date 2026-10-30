"""John Martin — Great Day of His Wrath (Tate N05613): museum-correct V81 4x1.
Actual photographed period exhibition frame sourced from 2010 Tate Britain image by Szilas.
Never draw an imaginary ornamental border. Same frame appears only in opening/exit.
The artwork pixels come from a documented reproduction; no AI fill or made-up scenes.
Frame photo is CC BY-SA 4.0 and must be correctly credited; museum wall is scenography.
"""
from __future__ import annotations
import math
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps

W,H,FPS=720,1280,15
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIF="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
def font(n,serif=False):return ImageFont.truetype(SERIF if serif else FONT,int(n))
def smooth(t):
    t=max(0.,min(1.,float(t)))
    return t*t*(3-2*t)
def mix(a,b,t):return a+(b-a)*t

# Seven distinct, authored points. Each aligns with the matching critic paragraph.
# Normalized (x,y) locations refer to the original unframed painting.
BEATS=[
 ("THE WORLD BREAKS",(.51,.46),2.10),
 ("THE SIXTH SEAL",(.62,.26),1.92),
 ("THE FALLING CITY",(.66,.51),2.00),
 ("TINY HUMAN FIGURES",(.40,.89),2.30),
 ("LIGHT THROUGH STONE",(.50,.25),2.12),
 ("THE COLOSSAL ROCKS",(.22,.37),2.03),
 ("THE FINAL VIEW",(.50,.50),1.0)
]
# Aperture of the ORIGINAL PHOTO with its true Tate 2010 gilded frame;
# photo is never presented as proof of an artist-original historical frame.
APERTURE=(.089,.118,.911,.880)

def title_overlay(im,t,title="THE END OF EVERYTHING",end=4.1):
    if t<0 or t>end:return im
    a=min(1.,t/.58,(end-t)/.55)
    if a<=0:return im
    lay=Image.new("RGBA",im.size,(0,0,0,0))
    d=ImageDraw.Draw(lay)
    d.rounded_rectangle((30,54,690,190),radius=9,fill=(7,9,12,int(194*a)))
    for y,s,z in [(67,title,32),(140,"JOHN MARTIN  ·  1851–53",20)]:
        f=font(z,serif=(y==67)); bb=d.textbbox((0,0),s,font=f)
        d.text(((W-(bb[2]-bb[0]))/2,y),s,font=f,fill=(248,236,219,int(255*a)))
    return Image.alpha_composite(im.convert("RGBA"),lay).convert("RGB")

def room(seed=563):
    rng=np.random.default_rng(seed);yy,xx=np.mgrid[0:H,0:W]
    grain=rng.normal(0,1.35,(H,W))
    lit=20*np.exp(-((xx-360)/470)**2-((yy-440)/520)**2)
    a=np.empty((H,W,3),dtype=np.uint8)
    for c,base in enumerate((61,61,57)):
        a[:,:,c]=np.clip(base+lit*(1,.99,.89)[c]+grain,0,255)
    out=Image.fromarray(a);d=ImageDraw.Draw(out)
    d.rectangle((0,1095,W,H),fill=(36,35,34))
    d.line((0,1094,W,1094),fill=(93,88,76),width=3)
    d.rectangle((334,795,386,816),fill=(183,178,155))
    d.text((342,799),"N05613",font=font(9),fill=(43,45,43))
    return out

def original_photo_mounted(art,frame):
    """No invented border: ONLY documented 2010 Tate photo border.
    Paste public-domain art within the real frame's existing aperture.
    The frame pixels come from the actual photograph, not custom primitives."""
    out=frame.copy().convert("RGB")
    l,t,r,b=APERTURE
    x0=int(frame.width*l);y0=int(frame.height*t)
    x1=int(frame.width*r);y1=int(frame.height*b)
    patch=art.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS)
    out.paste(patch,(x0,y0))
    return out

def physical_museum_view(art,real_frame,roomimg,z,focus):
    # Shared artwork plane: the real frame is pulled out of shot, never faded away.
    framed=original_photo_mounted(art,real_frame)
    fx,fy=focus
    aw=490.
    ah=aw*real_frame.height/real_frame.width
    px,py=360.,437.
    l,t,r,b=APERTURE
    cpx=px+((l+r)/2-.5)*aw
    cpy=py+((t+b)/2-.5)*ah
    targetx=px+(l+fx*(r-l)-.5)*aw
    targety=py+(t+fy*(b-t)-.5)*ah
    fraction=smooth(min(1.,max(0.,(z-1)/5)))
    camx=mix(cpx,targetx,fraction);camy=mix(cpy,targety,fraction)
    transform=np.float32([[z,0,W/2-z*camx],[0,z,H/2-z*camy]])
    back=cv2.warpAffine(np.asarray(roomimg),transform,(W,H),
                        flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
    out=Image.fromarray(back)
    x=(px-aw/2-camx)*z+W/2
    y=(py-ah/2-camy)*z+H/2
    pw=aw*z;ph=ah*z
    if x>W or y>H or x+pw<0 or y+ph<0:return out
    if z<4.0:
        ImageDraw.Draw(out).rectangle((x+4*z,y+5*z,x+pw+4*z,y+ph+5*z),fill=(17,18,18))
    x0=max(0,int(math.floor(x)));x1=min(W,int(math.ceil(x+pw)))
    y0=max(0,int(math.floor(y)));y1=min(H,int(math.ceil(y+ph)))
    if x0>=x1 or y0>=y1:return out
    sx0=max(0,(x0-x)/pw*framed.width);sx1=min(framed.width,(x1-x)/pw*framed.width)
    sy0=max(0,(y0-y)/ph*framed.height);sy1=min(framed.height,(y1-y)/ph*framed.height)
    piece=framed.crop((sx0,sy0,sx1,sy1)).resize((x1-x0,y1-y0),Image.Resampling.BICUBIC)
    out.paste(piece,(x0,y0))
    return out

def detail_crop(art,focus,mag):
    # Camera only over real painted pixels, not outside the canvas.
    iw,ih=art.size
    cw=min(iw,ih*(W/H))/max(1.,mag)
    ch=cw*H/W
    cx=float(np.clip(focus[0]*iw,cw/2,iw-cw/2))
    cy=float(np.clip(focus[1]*ih,ch/2,ih-ch/2))
    return art.crop((cx-cw/2,cy-ch/2,cx+cw/2,cy+ch/2)).resize((W,H),Image.Resampling.LANCZOS)

def whole_art(art):
    out=Image.new("RGB",(W,H),(17,19,21))
    p=ImageOps.contain(art,(int(W*.96),int(H*.80)),Image.Resampling.LANCZOS)
    out.paste(p,((W-p.width)//2,(H-p.height)//2))
    return out

def scene(art,idx,u,mode):
    if idx==6:return whole_art(art)
    _,focus,mag=BEATS[idx]
    x=mag*(.985+.024*smooth(u)) if mode=="critic" else mag*(.97+.052*smooth(u))
    return detail_crop(art,focus,x)

def scene_idx(t,duration,weights):
    cum=0
    for idx,w in enumerate(weights):
        end=cum+duration*w
        if t<end:
            return idx,smooth((t-cum)/max(.01,end-cum)),cum
        cum=end
    return len(weights)-1,1.,cum-duration*weights[-1]

def critico_standard(art,t,duration):
    # Paragraph-relative, no repeated fake scene; two variants share exactly one WAV.
    idx,u,_=scene_idx(t,duration,[.16,.14,.17,.17,.15,.12,.09])
    result=scene(art,idx,u,"critic")
    return title_overlay(result,t,"THE DAY THE EARTH COLLAPSED")

def cinema_standard(art,t,duration):
    idx,u,start=scene_idx(t,duration,[.19,.13,.18,.13,.15,.15,.07])
    result=scene(art,idx,u,"cinema")
    if idx>0 and t-start<.38:
        result=Image.blend(scene(art,idx-1,1,"cinema"),result,smooth((t-start)/.38))
    return title_overlay(result,t,"WHEN MOUNTAINS COLLAPSE")

def museum_frame(art,actual_frame,roomimg,t,duration,critic=False):
    # The only point where gold frame is visible: real museum exterior at
    # entrance / end. Pure art throughout narration. Frame never overlays details.
    entrance=9.0 if critic else 8.0
    leave=10.0
    if t<entrance:
        u=smooth(t/entrance)
        z=mix(1.,13.5,u)
        focus=(mix(.5,.55,u),mix(.5,.39,u))
    elif t<duration-leave:
        u=(t-entrance)/max(.01,duration-entrance-leave)
        # Single spatial continuous trip between 7 picture regions; no teleport.
        pts=[(.55,.39),(.62,.24),(.64,.51),(.42,.85),(.52,.23),(.24,.37),(.50,.50)]
        x=min(len(pts)-2,int(u*(len(pts)-1)))
        k=smooth(u*(len(pts)-1)-x)
        focus=(mix(pts[x][0],pts[x+1][0],k),mix(pts[x][1],pts[x+1][1],k))
        z=13.5+1.3*math.sin(u*math.pi)**2
    else:
        u=smooth((t-(duration-leave))/leave)
        focus=(mix(.50,.50,u),mix(.50,.50,u))
        z=mix(13.5,1.,u)
    out=physical_museum_view(art,actual_frame,roomimg,z,focus)
    return title_overlay(out,t,"ENTER THE APOCALYPSE")

def cover(art,variant):
    out=Image.new("RGB",(1080,1920),(18,18,19))
    p=ImageOps.contain(art,(1010,1140),Image.Resampling.LANCZOS)
    out.paste(p,((1080-p.width)//2,460))
    d=ImageDraw.Draw(out)
    for y,title in [(91,"THE GREAT DAY"),(185,"OF HIS WRATH")]:
        f=font(66,serif=True);bb=d.textbbox((0,0),title,font=f)
        d.text(((1080-bb[2]+bb[0])//2,y),title,font=f,fill=(245,221,181))
    sub=("CRITICO D'ARTE" if "critico" in variant else "CINEMA EDITION")
    if "museum" in variant:sub="MUSEUM IMMERSION · "+sub
    d.text((70,1720),sub,font=font(29),fill=(232,210,181))
    d.text((70,1792),"JOHN MARTIN · 1851–53",font=font(26),fill=(179,184,183))
    d.text((70,1842),"TATE BRITAIN · N05613",font=font(24),fill=(165,168,168))
    return out
