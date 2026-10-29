"""Exact paragraph-timed pictorial direction for the ArtVision Blake Critico trial.

No paid API calls, no new painting pixels, no fake camera cuts. Timings come
from the ACTUAL generated offline voice paragraphs, not guessed proportions.
The original Gacrux Gold Master and other modules remain untouched.
"""
from __future__ import annotations
import math
from bisect import bisect_right
from PIL import Image
import artvision_blake_visual_v74 as visual

# Every paragraph matches ONE named Blake detail or documented visual fact.
# All coordinates refer exclusively to Brooklyn Museum accession 15.368.
SHOTS = [
    {"id":"immense_dragon_small_art", "mode":"detail","focus":(.51,.32),"zoom":2.10},
    {"id":"blake_watercolor_sheet", "mode":"whole"},
    {"id":"apocalypse_heads_horns", "mode":"detail","focus":(.51,.21),"zoom":2.55},
    {"id":"dragon_body_wings", "mode":"detail","focus":(.52,.40),"zoom":2.20},
    {"id":"dragons_coiling_tail", "mode":"detail","focus":(.46,.70),"zoom":2.50},
    {"id":"woman_golden_light", "mode":"detail","focus":(.72,.72),"zoom":2.25},
    {"id":"artists_entire_vision", "mode":"whole"},
]

def from_voice_report(report):
    paragraphs=report["paragraphs"]
    if len(paragraphs)!=len(SHOTS):
        raise ValueError("Source Gacrux/Kokoro script has changed or missing 7 paragraphs")
    starts=[0.]
    total=0.
    for i,p in enumerate(paragraphs):
        seconds=float(p["output_seconds"])
        if not 5 < seconds < 40 or int(p["paragraph"])!=i+1:
            raise ValueError("Invalid real voice paragraph timing")
        total+=seconds
        if i<len(paragraphs)-1:total+=.4
        starts.append(round(total,3))
    actual=float(report["wav_seconds"])
    if abs(starts[-1]-actual)>.12:
        raise ValueError("Paragraph timings do not reconcile with actual WAV")
    return starts

def _render_shot(art,index,t,scene_start,scene_end):
    shot=SHOTS[index]
    if shot["mode"]=="whole":
        out=Image.new("RGB",(visual.W,visual.H),(16,17,19))
        p=art.copy()
        p.thumbnail((int(visual.W*.90),int(visual.H*.88)),Image.Resampling.LANCZOS)
        out.paste(p,((visual.W-p.width)//2,(visual.H-p.height)//2))
        return out
    u=visual.smooth((t-scene_start)/max(.5,scene_end-scene_start))
    fx,fy=shot["focus"]
    zoom=shot["zoom"]*(.96+.07*u)
    return visual.crop_art(art,fx,fy,zoom,t)

def critico_standard(art,t,duration,starts):
    if len(starts)!=len(SHOTS)+1:raise ValueError("Seven precise narrative segments required")
    i=max(0,min(len(SHOTS)-1,bisect_right(starts,t)-1))
    frame=_render_shot(art,i,t,starts[i],starts[i+1])
    if i>0 and starts[i] <= t < starts[i]+.42:
        # Deliberately shorten transitions rather than a visible hard cut.
        prev=_render_shot(art,i-1,starts[i]-.05,starts[i-1],starts[i])
        frame=Image.blend(prev,frame,visual.smooth((t-starts[i])/.42))
    if t<3.5:
        frame=visual.label(frame,82,["THE GREAT RED DRAGON"],
                           "WILLIAM BLAKE · CRITICO D'ARTE",
                           opacity=min(1.,t/.6,(3.5-t)/.6))
    return frame

def _pose_at(t,keys):
    if t<=keys[0][0]:return keys[0][1:]
    if t>=keys[-1][0]:return keys[-1][1:]
    for i in range(len(keys)-1):
        a=keys[i];b=keys[i+1]
        if a[0]<=t<=b[0]:
            u=visual.smooth((t-a[0])/(b[0]-a[0]))
            return tuple(visual.lerp(a[j],b[j],u) for j in (1,2,3))
    raise AssertionError("Camera timeline incomplete")

def _museum_keys(starts,duration):
    # No scene switch: each pose is physically interpolated inside SAME room.
    # Intro enters; Bible heads/body/tail/woman follow the actual spoken beat,
    # then viewer exits continuously through the same physical frame.
    exit_start=max(starts[6]+5.,duration-12.)
    keys=[
        (0.,1.,.50,.50),
        (min(11.,starts[1]*.70),18.,.51,.32),
        (starts[1],18.,.51,.32),
        (starts[2],17.,.50,.50),
        (starts[3],20.,.51,.21),
        (starts[4],20.,.52,.40),
        (starts[5],22.,.46,.70),
        (starts[6],22.,.72,.72),
        (exit_start,17.,.50,.50),
        (duration,1.,.50,.50)
    ]
    if any(a[0]>=b[0] for a,b in zip(keys,keys[1:])):
        raise ValueError("Continuous camera keys not chronologically ordered")
    return keys

def critico_museum(art,roomimg,t,duration,starts):
    keys=_museum_keys(starts,duration)
    zoom,fx,fy=_pose_at(t,keys)
    frame=visual.museum(art,roomimg,zoom,(fx,fy))
    if t<3.5:
        frame=visual.label(frame,74,["A DRAGON","IN A SMALL ROOM"],
                           "WILLIAM BLAKE · CRITICO D'ARTE",
                           opacity=min(1.,t/.65,(3.5-t)/.7))
    return frame
