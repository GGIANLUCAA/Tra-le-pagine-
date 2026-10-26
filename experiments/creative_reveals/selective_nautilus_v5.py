#!/usr/bin/env python3
"""Optional one-shot Nautilus scene reveal; no master modifications or AI video.
The target regions below are hand-mapped for an ORIGINAL 1024x1536 illustration.
Do not reuse that mask on unrelated stills, people, factual images, or artworks.
"""
from __future__ import annotations
import argparse,hashlib,json,subprocess,time
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

W,H,FPS=540,960,24
PORTHOLES=((273,676,15),(367,648,18),(475,617,19),(591,600,22),(896,637,65))
FISH=((650,407),(689,421),(751,445),(807,453),(856,469),(903,490),(840,946),(904,927))
HULL=((70,665),(305,552),(322,480),(346,423),(378,390),(425,350),(467,362),
      (499,423),(519,454),(611,473),(756,483),(847,506),(922,545),(1015,655),
      (922,703),(893,764),(750,824),(664,858),(553,819),(391,796),(243,752),
      (104,730),(60,688))

def checksum(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def ease(x):
    z=np.clip(x,0,1)
    return z*z*(3-2*z)

def loc(x,y):
    return round(x*W/1024),round(y*W/1024)+(H-round(1536*W/1024))//2

def load_still(path):
    with Image.open(path) as pil:
        if pil.size!=(1024,1536):
            raise ValueError("Unreviewed geometry: provide the exact reviewed 1024x1536 image only")
        arr=np.asarray(pil.convert("RGB"))
    bg=cv2.GaussianBlur(cv2.resize(arr,(W,H)),(0,0),23)
    fitted=cv2.resize(arr,(W,810),interpolation=cv2.INTER_AREA)
    bg[75:885]=fitted
    return bg

def prepare(image):
    base=image.astype(np.float32)
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    mask=np.zeros((H,W),np.uint8)
    cv2.fillPoly(mask,[np.array([loc(x,y) for x,y in HULL],np.int32)],255)
    region=cv2.GaussianBlur(mask.astype(np.float32)/255,(0,0),6)
    gray=cv2.cvtColor(image,cv2.COLOR_RGB2GRAY).astype(np.float32)
    blueprint=np.stack((gray*.54,gray*.78,gray*.90),axis=-1)
    edges=cv2.Canny(image,62,155).astype(np.float32)/255
    edgealpha=np.clip(edges*.55,0,1)[:,:,None]
    blueprint=blueprint*(1-edgealpha)+np.array([125,210,230],np.float32)*edgealpha
    lamps=[]
    for x,y,r in PORTHOLES:
        cx,cy=loc(x,y)
        radius=r*W/1024
        dist=np.sqrt((xx-cx)**2+(yy-cy)**2)
        gaussian=np.exp(-dist**2/(2*(radius*.72)**2))
        disc=np.clip((radius-dist)/4+.5,0,1)
        lamps.append((gaussian.astype(np.float32),disc.astype(np.float32)))
    fish=[]
    for x,y in FISH:
        cx,cy=loc(x,y)
        gauss=np.exp(-((xx-cx)**2+(yy-cy)**2)/(2*6**2))
        fish.append(gauss.astype(np.float32))
    return base,region,blueprint,lamps,fish

def frame(prepared,t,variant):
    base,region,blueprint,lamps,fish=prepared
    if variant=="clean":
        return np.uint8(base)
    out=base.copy()
    # The full sea remains opaque from frame one. Only the mapped submarine is a sketch.
    fraction=ease((t-1.65)/3.65)
    x=np.arange(W,dtype=np.float32)[None,:]/W
    filled=np.clip((fraction*1.35-x)/.22+.35,0,1)
    blue_alpha=region*(1-filled)
    out=out*(1-blue_alpha[:,:,None])+blueprint*blue_alpha[:,:,None]
    # Restore original colors; lightly warm the existing portholes in sequence.
    for i,(halo,disc) in enumerate(lamps):
        start=5+.43*i
        progress=ease((t-start)/1.2)
        out*=1-(1-progress)*disc[:,:,None]*.18
        lit=ease((t-start-.15)/.55)*(.68+.32*(1-ease((t-start-1.2)/1)))
        alpha=halo*lit*.10
        out=out*(1-alpha[:,:,None])+np.array([255,210,135],np.float32)*alpha[:,:,None]
    for i,spot in enumerate(fish):
        start=8+.18*i
        twinkle=ease((t-start)/.35)*(1-ease((t-start+.65)/.7))
        alpha=spot*twinkle*.32
        out=out*(1-alpha[:,:,None])+np.array([175,234,248],np.float32)*alpha[:,:,None]
    return np.uint8(np.clip(out,0,255))

def render(image,audio,output,variant="effect",duration=14.32):
    image,audio,output=map(Path,(image,audio,output))
    if variant not in {"effect","clean"}: raise ValueError("Unknown variant")
    if not 2<=duration<=30: raise ValueError("Duration must be between 2 and 30 seconds")
    if not image.is_file() or not audio.is_file(): raise FileNotFoundError("Source image or audio absent")
    manifest=output.with_suffix(".json")
    unfinished=output.with_name(output.stem+".incomplete.mp4")
    if any(x.exists() for x in (output,manifest,unfinished)): raise FileExistsError("Refuse overwrite")
    if output.suffix.lower()!=".mp4": raise ValueError("Output must be MP4")
    prepared=prepare(load_still(image))
    count=round(duration*FPS)
    output.parent.mkdir(parents=True,exist_ok=True)
    args=["ffmpeg","-hide_banner","-loglevel","error","-nostdin","-y",
          "-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),
          "-i","pipe:0","-i",str(audio),"-t",str(duration),"-map","0:v:0",
          "-map","1:a:0","-sn","-c:v","libx264","-preset","veryfast",
          "-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k",
          "-movflags","+faststart",str(unfinished)]
    proc=subprocess.Popen(args,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    start=time.monotonic()
    try:
        for i in range(count):
            proc.stdin.write(frame(prepared,i/FPS,variant).tobytes())
        proc.stdin.close()
        error=proc.stderr.read().decode(errors="replace")
        rc=proc.wait()
        if rc or not unfinished.exists() or unfinished.stat().st_size<10000:
            raise RuntimeError("FFmpeg failed: "+error[-300:])
        unfinished.rename(output)
    except BaseException:
        if proc.poll() is None: proc.kill()
        unfinished.unlink(missing_ok=True)
        raise
    result={"schema":"selective-reveal-preview-v1","status":"needs_artistic_and_audio_review",
            "source_sha256":checksum(image),"audio_sha256":checksum(audio),
            "output_sha256":checksum(output),"frames":count,"fps":FPS,
            "duration":duration,"variant":variant,"master_modified":False,
            "uses_ai_video_api":False,"source_original_illustration_only":True,
            "word_level_sync_verified":False,
            "render_wall_seconds":round(time.monotonic()-start,2)}
    manifest.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--image",required=True)
    parser.add_argument("--audio",required=True)
    parser.add_argument("--output",required=True)
    parser.add_argument("--variant",choices=("effect","clean"),default="effect")
    parser.add_argument("--duration",type=float,default=14.32)
    a=parser.parse_args()
    print(json.dumps(render(a.image,a.audio,a.output,a.variant,a.duration),indent=2))
