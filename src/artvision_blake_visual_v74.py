"""Original ArtVision Blake pilot V74 visual compositor (offline, no paid AI).

Uses only exact authentic Brooklyn Museum source pixels. Room and art mount are openly declared scenic reconstructions, never a documented
museum installation or an authentic historical frame. V77: no fake gilt borders.
All four variants share one source artwork with independently designed staging.
"""
from __future__ import annotations
import math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W,H,FPS=720,1280,15
SERIF="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def font(size,serif=False):
    return ImageFont.truetype(SERIF if serif else SANS,int(size))

def smooth(t):
    t=max(0.,min(1.,float(t)))
    return t*t*(3-2*t)

def lerp(a,b,u):return a+(b-a)*u

def label(im,top,lines,small=None,opacity=1.,right=False):
    if opacity<=0:return im
    layer=Image.new("RGBA",im.size,(0,0,0,0))
    d=ImageDraw.Draw(layer)
    lines=list(lines)
    d.rectangle((0,top-30,W,top+len(lines)*60+54),fill=(10,13,18,int(165*opacity)))
    for i,line in enumerate(lines):
        f=font(38 if len(line)<22 else 29,serif=True)
        b=d.textbbox((0,0),line,font=f)
        x=(W-(b[2]-b[0]))/2
        d.text((x,top+i*56),line,font=f,fill=(239,225,191,int(255*opacity)))
    if small:
        f=font(18)
        b=d.textbbox((0,0),small,font=f)
        x=(W-(b[2]-b[0]))/2
        d.text((x,top+len(lines)*58+3),small,font=f,fill=(215,205,190,int(255*opacity)))
    return Image.alpha_composite(im.convert("RGBA"),layer).convert("RGB")

def source_regions(art):
    # Actual photographic reproduction is 1586x2000, with the image surrounded
    # by its original handwritten paper borders. Never mix NGA versions.
    return art.crop((int(art.width*.107),int(art.height*.087),
                     int(art.width*.891),int(art.height*.881)))

def crop_art(art,fx,fy,zoom=1.0,t=0.0):
    """Portrait viewport from authentic source; gentle optical movement only."""
    iw,ih=art.size
    aspect=W/H
    source_ratio=iw/ih
    base_w=min(iw,ih*aspect)
    cw=max(80.,base_w/max(1,zoom))
    ch=cw/aspect
    fx=np.clip(fx+0.006*math.sin(t*.31),.12,.88)
    fy=np.clip(fy+0.004*math.cos(t*.29),.12,.88)
    x=int(np.clip(fx*iw-cw/2,0,iw-cw))
    y=int(np.clip(fy*ih-ch/2,0,ih-ch))
    p=art.crop((x,y,int(x+cw),int(y+ch))).resize((W,H),Image.Resampling.LANCZOS)
    return p

def room(seed=86):
    rng=np.random.default_rng(seed)
    yy,xx=np.mgrid[0:H,0:W]
    grain=rng.normal(0,2.6,(H,W))
    glow=22*np.exp(-((xx-390)/265)**2-((yy-480)/450)**2)
    wall=np.empty((H,W,3),dtype=np.uint8)
    for c,base in enumerate((84,81,73)):
        wall[:,:,c]=np.clip(base+glow*(1,1.03,.96)[c]+grain,0,255)
    im=Image.fromarray(wall,"RGB")
    d=ImageDraw.Draw(im)
    # Period architectural trim, calibrated to a human-scale doorway; all scenic.
    d.rectangle((0,0,60,995),fill=(69,67,60))
    d.rectangle((65,0,78,990),fill=(115,109,93))
    d.rectangle((638,0,650,995),fill=(114,107,92))
    d.rectangle((656,0,W,995),fill=(68,65,59))
    for x in (107,613):
        d.line((x,65,x,963),fill=(125,116,99),width=3)
    d.rectangle((77,103,642,121),fill=(126,116,101))
    d.rectangle((77,133,642,139),fill=(45,45,42))
    d.rectangle((77,925,642,950),fill=(112,104,91))
    d.line((40,987,700,987),fill=(162,151,127),width=18)
    d.rectangle((0,1002,W,H),fill=(74,53,42))
    # Floorboards with depth and subtle reflected light; no decorative filler images.
    for j in range(15):
        y=1002+int((j/14)**1.6*(H-1002))
        d.line((0,y,W,y),fill=(120+j,84+j//2,62+j//3),width=2)
    for x in range(-350,1400,100):
        d.line((360,1002,x,H),fill=(48,39,33),width=2)
    # Two small gallery lamps with soft translucent illumination.
    for x in (130,588):
        light=Image.new("RGBA",(W,H),(0,0,0,0))
        ld=ImageDraw.Draw(light)
        for radius in range(96,0,-6):
            a=round(1.7*(96-radius))
            ld.ellipse((x-radius,190-radius,x+radius,190+radius),fill=(246,206,136,max(0,min(9,a//12))))
        im=Image.alpha_composite(im.convert("RGBA"),light).convert("RGB")
        d=ImageDraw.Draw(im)
        d.ellipse((x-14,160,x+14,192),fill=(151,119,69))
        d.ellipse((x-9,166,x+9,181),fill=(232,205,144))
    return im

def museum(art,roomimg,zoom,focus,mode="museum"):
    """One physical painting plane; same frame traversed without fake fade."""
    fx,fy=focus
    # At zoom 1: 43 cm wide sheet viewed at ~3.5 m, human-scale wall.
    px,py=370,528
    aw,ah=112.,141.
    # Brooklyn 15.368: watercolor on paper; historical frame NOT documented.
    # Preserve the actual sheet, use a modest neutral conservation-style surround.
    # Outer size follows the 55.1 x 43.3 cm physical sheet, not an oversized oil frame.
    bx,by=aw+10,ah+10
    # Camera aim: focus inside artwork at high zoom, not empty wall.
    camx=lerp(360,px+(fx-.5)*aw,smooth(min(1,(zoom-1)/6)))
    camy=lerp(545,py+(fy-.5)*ah,smooth(min(1,(zoom-1)/6)))
    scale=float(zoom)
    mat=np.float32([[scale,0,W/2-scale*camx],[0,scale,H/2-scale*camy]])
    base=cv2.warpAffine(np.asarray(roomimg),mat,(W,H),
                        flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
    out=Image.fromarray(base,"RGB")
    d=ImageDraw.Draw(out)
    left=(px-bx/2-camx)*scale+W/2
    top=(py-by/2-camy)*scale+H/2
    ow,oh=bx*scale,by*scale
    # Neutral, conservation-style presentation (RECONSTRUCTION, not original frame).
    # Contact shadow and mount all track the SAME physical plane.
    if left>W+40 or top>H+40 or left+ow<-40 or top+oh<-40:
        return out
    def rect(a,b,c,e,fill,width=None):
        if width is None:d.rectangle((a,b,c,e),fill=fill)
        else:d.rectangle((a,b,c,e),outline=fill,width=width)
    rect(left+2*scale,top+3*scale,left+ow+3*scale,top+oh+4*scale,(32,31,30))
    rect(left,top,left+ow,top+oh,(45,44,43))  # fine graphite edge
    rect(left+2*scale,top+2*scale,left+ow-2*scale,top+oh-2*scale,
         (207,200,185))  # neutral warm-paper mount, not bright gold
    rect(left+4*scale,top+4*scale,left+ow-4*scale,top+oh-4*scale,
         (80,75,68),max(1,int(.65*scale)))  # subtle bevel at sheet
    sheet_left=left+5*scale
    sheet_top=top+5*scale
    sheet_w=aw*scale
    sheet_h=ah*scale
    dx0=max(0,int(math.floor(sheet_left)))
    dy0=max(0,int(math.floor(sheet_top)))
    dx1=min(W,int(math.ceil(sheet_left+sheet_w)))
    dy1=min(H,int(math.ceil(sheet_top+sheet_h)))
    if dx1>dx0 and dy1>dy0:
        # Direct sampling from ORIGINAL full-quality artwork at every frame:
        # camera does not magnify a tiny pre-rendered thumbnail.
        sx0=(dx0-sheet_left)/sheet_w*art.width
        sy0=(dy0-sheet_top)/sheet_h*art.height
        sx1=(dx1-sheet_left)/sheet_w*art.width
        sy1=(dy1-sheet_top)/sheet_h*art.height
        crop=art.crop((sx0,sy0,sx1,sy1))
        im=crop.resize((dx1-dx0,dy1-dy0),Image.Resampling.BICUBIC)
        out.paste(im,(dx0,dy0))
    return out

# Editorially motivated locations in the exact original Brooklyn reproduction.
DETAILS=[
 ("THE WINGS",(.53,.31),2.00),
 ("THE CROWN",(.51,.20),2.55),
 ("THE BODY",(.52,.49),2.0),
 ("THE COILED TAIL",(.46,.73),2.3),
 ("THE WOMAN",(.76,.73),2.5),
 ("THE STRUGGLE",(.51,.79),2.15),
 ("THE WHOLE VISION",(.50,.52),1.0),
]

def cinema_standard(art,t,duration):
    """Narrative edits with clean 0.32s source-faithful dissolves, no hard flashes."""
    schedule=[
        (0.,4.4,.50,.26,2.4,"THE DRAGON"),
        (4.4,10.2,.5,.53,1.02,"WILLIAM BLAKE"),
        (10.2,16.8,.49,.25,2.4,"THREE FACES"),
        (16.8,23.0,.50,.47,2.5,"WINGS OF THE ABYSS"),
        (23.0,29.0,.49,.76,2.7,"THE COILED TAIL"),
        (29.0,35.0,.73,.73,2.7,"THE WOMAN"),
        (35.0,duration,.5,.52,1.0,"A PROPHECY ON PAPER")]
    def render_shot(shot,now):
        start,end,fx,fy,mag,title=shot
        u=max(0.,min(1.,(now-start)/max(.1,end-start)))
        zoom=mag*(.97+.055*smooth(u))
        if title in ("WILLIAM BLAKE","A PROPHECY ON PAPER"):
            result=Image.new("RGB",(W,H),(17,18,21))
            sheet=art.copy()
            sheet.thumbnail((int(W*.86),int(H*.81)),Image.Resampling.LANCZOS)
            result.paste(sheet,((W-sheet.width)//2,(H-sheet.height)//2))
        else:
            result=crop_art(art,fx,fy,zoom,now)
        return result
    idx=next((i for i,s in enumerate(schedule) if s[0]<=t<s[1]),len(schedule)-1)
    result=render_shot(schedule[idx],t)
    if idx>0:
        boundary=schedule[idx][0]
        if 0<=t-boundary<.32:
            previous=render_shot(schedule[idx-1],boundary-.001)
            result=Image.blend(previous,result,smooth((t-boundary)/.32))
    if t<3.4:
        result=label(result,70,["THE GREAT","RED DRAGON"],"WILLIAM BLAKE  ·  1803–1805",
                     opacity=min(1.,t/.45,(3.6-t)/.6))
    return result

def critico_standard(art,t,duration):
    # One authored narrative, seven semantic focus points. Neither artificial
    # 'new scenes' nor a cut from a different Blake Dragon version.
    durations=[.11,.14,.15,.15,.15,.15,.15]
    bound=[0.]
    for frac in durations:bound.append(bound[-1]+frac*duration)
    i=next((j for j in range(7) if bound[j]<=t<bound[j+1]),6)
    if i==6:
        result=Image.new("RGB",(W,H),(16,17,18))
        p=art.copy();p.thumbnail((W*.84,H*.85),Image.Resampling.LANCZOS)
        result.paste(p,((W-p.width)//2,(H-p.height)//2))
    else:
        detail=DETAILS[i]
        start,end=bound[i:i+2]
        mag=detail[2]*(.94+.09*smooth((t-start)/(end-start)))
        result=crop_art(art,*detail[1],mag,t)
    if t<4:
        result=label(result,78,["THE GREAT RED DRAGON"],"WILLIAM BLAKE · CRITICO D'ARTE",opacity=min(1.,t/.6,(4-t)/.7))
    return result

def museum_frame(art,roomimg,t,duration,critic=False):
    enter=11 if not critic else 12
    exit_time=11 if not critic else 12
    # Entire movement is one continuously interpolated physical camera path,
    # not a cut between a flat gallery background and cropped artwork.
    if t<enter:
        u=smooth(t/enter)
        # V75 QA: reach source-original pixels fully inside the image plane,
        # not a giant frame lip or handwritten paper margin.
        zoom=lerp(1.,18.,u)
        focus=(lerp(.5,.52,u),lerp(.5,.34,u))
    elif t<duration-exit_time:
        u=(t-enter)/(duration-enter-exit_time)
        # These subject centers + a physical optical zoom keep both the
        # reconstructed neutral mount AND original paper edge offscreen.
        # The underlying image pixels are never invented or erased.
        points=[(.52,.34),(.51,.33),(.54,.49),(.48,.66),(.69,.67),(.5,.5)]
        v=u*(len(points)-1)
        idx=min(int(v),len(points)-2)
        k=smooth(v-idx)
        focus=tuple(lerp(a,b,k) for a,b in zip(points[idx],points[idx+1]))
        zoom=lerp(18.,22.,math.sin(math.pi*u)**2)
    else:
        u=smooth((t-(duration-exit_time))/exit_time)
        zoom=lerp(18.,1.,u)
        focus=(.5,.5)
    result=museum(art,roomimg,zoom,focus)
    if t<4:
        result=label(result,64,["A DRAGON","IN A SMALL ROOM"],
                     "WILLIAM BLAKE · BROOKLYN MUSEUM",opacity=min(1.,t/.7,(4-t)/.7))
    return result

def cover(art,variant):
    # 1080x1920 output cover: original painting on a deep charcoal paper wall.
    w,h=1080,1920
    out=Image.new("RGB",(w,h),(16,17,19))
    d=ImageDraw.Draw(out)
    sheet=art.copy();sheet.thumbnail((865,1390),Image.Resampling.LANCZOS)
    x=(w-sheet.width)//2;y=365
    # V77: same restrained paper-mount treatment as the Museum shot.
    # This is editorial scenography; no undocumented gilded antique frame.
    d.rectangle((x-14,y-14,x+sheet.width+14,y+sheet.height+14),fill=(45,44,43))
    d.rectangle((x-8,y-8,x+sheet.width+8,y+sheet.height+8),fill=(207,200,185))
    out.paste(sheet,(x,y))
    d=ImageDraw.Draw(out)
    lines=("THE GREAT","RED DRAGON")
    for i,line in enumerate(lines):
        f=font(70,True)
        box=d.textbbox((0,0),line,font=f)
        d.text(((w-(box[2]-box[0]))/2,60+i*86),line,font=f,fill=(241,220,181))
    subtitle="MUSEUM IMMERSION" if "museum" in variant else "CRITICO D'ARTE" if "critico" in variant else "CINEMATIC EDITION"
    d.text((95,1755),subtitle,font=font(34),fill=(222,204,164))
    d.text((95,1813),"WILLIAM BLAKE  ·  BROOKLYN MUSEUM",font=font(24),fill=(173,165,155))
    return out
