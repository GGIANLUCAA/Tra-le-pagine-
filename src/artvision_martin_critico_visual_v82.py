"""ArtVision Martin V82: Critico correction only.
9 narrated paragraphs, each visually mapped; shorter; meaningful changes, no invented scenes.
Museum: photo-real existing 2010 Tate frame visible ONLY during entry and final return;
continuous camera, original painted pixels for every internal shot.
"""
import math
from PIL import Image, ImageFilter, ImageDraw
import numpy as np
import artvision_martin_visual_v81 as old

W,H,FPS=old.W,old.H,old.FPS
APERTURE=old.APERTURE
room=old.room
BEAT_BOUNDARIES=None
# Directions here correspond ONE-TO-ONE to nine paragraphs of COPIONE_CRITICO_V82.
# Details from inspected image: lightning x=.16 y=.09; left rock x=.33 y=.27;
# city x=.90 y=.30; fiery chasm x=.65 y=.49;
# foreground people left (.27,.85) and right (.69,.87).
SCENE_EDIT=[
  # 0: first 3s person-hook then catastrophe; 1: identity full painting.
  [("PEOPLE CLINGING TO ROCKS",(.28,.83),1.12,.44),("THE CRUSHING ROCKS",(.33,.34),1.22,.56)],
  [("COMPLETE WORK",(.50,.50),0,.99)],
  [("THE SKY OVER THE ABYSS",(.49,.25),1.10,.99)],
  [("LIGHTNING",(.18,.09),1.19,.44),("FALLING ROCK",(.33,.26),1.15,.56)],
  [("CITY BREAKING APART",(.88,.35),1.25,.99)],
  [("FIERY CRATER",(.68,.49),1.13,.50),("BOTTOMLESS CHASM",(.49,.60),1.12,.50)],
  [("THE FLEEING LEFT GROUP",(.27,.84),1.18,.48),("THE FLEEING RIGHT GROUP",(.69,.84),1.20,.52)],
  [("PEOPLE AGAINST THE WORLD",(.30,.83),1.05,.35),("MONUMENTAL FULL VIEW",(.50,.50),0,.65)],
  [("THE COMPLETE VISION",(.50,.50),0,1.)]
]
# A continuous route inside the real painting. Never exit the painting interior.
MUSEUM_ROUTE=[
 (.29,.70,20.5), # people, first hook
 (.50,.47,19.2), # whole composition orientation
 (.49,.26,19.0), # sky
 (.26,.23,19.0), # lightning left
 (.78,.36,19.3), # city right
 (.65,.50,19.0), # crater center
 (.46,.71,22.0), # human figures (still strictly inside source aperture)
 (.51,.50,19.0), # sublime composition
 (.50,.48,19.0), # pull back at end
]

def assign_narrative_timing(bounds):
    """Actual voice-audio-derived paragraph boundaries (no fixed calendar edits)."""
    if len(bounds)!=10 or any(b>=c for b,c in zip(bounds,bounds[1:])):
        raise ValueError("Need 10 increasing semantic boundaries")
    global BEAT_BOUNDARIES
    BEAT_BOUNDARIES=tuple(float(x) for x in bounds)

def _bounds(duration):
    if BEAT_BOUNDARIES and abs(BEAT_BOUNDARIES[-1]-(duration-1.5))<4:
        return BEAT_BOUNDARIES
    # A truthful fallback, never assume a 2m25 fixed narration.
    weights=[22,25,26,22,20,23,25,23,23]
    total=sum(weights);r=[0.]
    for w in weights:r.append(r[-1]+(duration-1.5)*w/total)
    return r

def beat_at(t,duration):
    b=_bounds(duration)
    if t>=b[-1]:return 8,1.,b[8],b[9]
    for i in range(9):
        if b[i]<=t<b[i+1]:
            return i,(t-b[i])/max(.001,b[i+1]-b[i]),b[i],b[i+1]
    return 0,0.,0.,b[1]

def _frame_original(crop_img,crop_focus,level,progress):
    # Restrained image movement, no artificial depth warping.
    mag=level*(.987+.024*old.smooth(progress))
    return old.detail_crop(crop_img,crop_focus,mag)

def _wide(art,progress):
    # Natural museum-wide image with softly extended colors for vertical devices.
    base=art.resize((W,H),Image.Resampling.BICUBIC)
    base=base.filter(ImageFilter.GaussianBlur(radius=26))
    veil=Image.new("RGB",(W,H),(19,18,20))
    bg=Image.blend(base,veil,.51)
    canvas=art.copy()
    # Slow 2.5% photographic push; not a recycled zoom disguised as a new scene.
    scale=.955+.045*old.smooth(progress)
    canvas.thumbnail((int((W-34)*scale), int((H-90)*scale)),Image.Resampling.LANCZOS)
    x=(W-canvas.width)//2;y=(H-canvas.height)//2
    bg.paste(canvas,(x,y))
    return bg

def _shot(art,label,focus,zoom,u):
    if zoom<=0:return _wide(art,u)
    return _frame_original(art,focus,zoom,u)

def _shot_for_beat(art,i,u):
    shots=SCENE_EDIT[i]
    if len(shots)==1:
        name,focus,mag,_=shots[0]
        return _shot(art,name,focus,mag,u)
    a,b=shots
    cut=a[3]
    if u<cut:
        return _shot(art,a[0],a[1],a[2],u/max(.001,cut))
    after=(u-cut)/max(.001,1-cut)
    image=_shot(art,b[0],b[1],b[2],after)
    # 0.25s scene transition, not a crossfade over the narrative subject.
    if after<.055:
        previous=_shot(art,a[0],a[1],a[2],1.)
        image=Image.blend(previous,image,old.smooth(after/.055))
    return image

def critico_standard(art,t,duration):
    i,u,_,_=beat_at(t,duration)
    img=_shot_for_beat(art,i,u)
    if t<3.6:
        img=old.title_overlay(img,t,title="THE END OF EVERYTHING",end=3.6)
    return img

def _interp(a,b,x):
    return old.mix(a,b,old.smooth(x))

def _museum_route(t,duration):
    i,u,start,end=beat_at(t,duration)
    # A slow continuous pan to the semantic place, then a hold with 1.2% breath.
    last=MUSEUM_ROUTE[max(0,i-1)]
    current=MUSEUM_ROUTE[i]
    p=old.smooth(min(1.,u/.28))
    if i==0:
        last=current
    focus=(_interp(last[0],current[0],p),_interp(last[1],current[1],p))
    z=_interp(last[2],current[2],p)
    z*=1.+.006*old.smooth(u)
    return z,focus

def museum_frame(art,photo_frame,roomimg,t,duration,critic=False):
    if not critic:
        return old.museum_frame(art,photo_frame,roomimg,t,duration,critic=False)
    # Intro: real photographed frame remains only before moving fully into original.
    entry=5.6; exit_seconds=7.2
    if t<entry:
        p=old.smooth(t/entry)
        z=old.mix(1.,20.5,p)
        fx=old.mix(.50,.29,p); fy=old.mix(.50,.70,p)
    elif t<duration-exit_seconds:
        z,(fx,fy)=_museum_route(t,duration)
    else:
        p=old.smooth((t-(duration-exit_seconds))/exit_seconds)
        z=old.mix(19.,1.,p)
        fx=old.mix(.50,.50,p);fy=old.mix(.48,.50,p)
    # Geometry safety: central narration must never contain a visible frame pixel.
    if entry<=t<duration-exit_seconds:
        fx=float(np.clip(fx,.19,.81))
        fy=float(np.clip(fy,.22,.71))
        z=max(z,19.)
    out=old.physical_museum_view(art,photo_frame,roomimg,z,(fx,fy))
    if t<3.6:
        out=old.title_overlay(out,t,title="ENTER THE APOCALYPSE",end=3.6)
    return out

def cover(art,variant):
    return old.cover(art,variant)
