#!/usr/bin/env python3
"""Optional illustration reveals V2, offline and non-destructive.
Requires OpenCV, NumPy, Pillow, FFmpeg. One source still, never two shots blended.
"""
from __future__ import annotations
import argparse, hashlib, json, math, subprocess
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

KINDS=("stroke_draw","object_stagger","pigment_bloom","director_mix","none","auto")
MOODS=("storybook","mystery","soft","neutral")
PAPER=np.array([251,248,241],np.uint8)

def sha256(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for data in iter(lambda:f.read(1024*1024),b""): h.update(data)
    return h.hexdigest()

def recommend(format_name,mood):
    if format_name.startswith("artvision"): return "none","Authentic art: no automatic repainting"
    if mood=="neutral":return "none","No effect without narrative reason"
    if mood=="mystery":return "stroke_draw","Progressive ink and information"
    if mood=="soft":return "pigment_bloom","Soft pigment within illustrated objects"
    return "director_mix","Outline first and locally ordered color"

def load_image(path,width,height):
    if Path(path).suffix.lower() not in (".png",".jpg",".jpeg",".webp"):
        raise ValueError("Provide a still, not an MP4 master")
    with Image.open(path) as im:
        im.load()
        src=np.asarray(im.convert("RGB"))
    h,w=src.shape[:2]
    if min(w,h)<64:raise ValueError("Source image too small")
    scale=min(width/w,height/h)
    nw,nh=max(1,round(w*scale)),max(1,round(h*scale))
    src=cv2.resize(src,(nw,nh),interpolation=cv2.INTER_AREA if scale<1 else cv2.INTER_CUBIC)
    dst=np.full((height,width,3),PAPER,np.uint8)
    x,y=(width-nw)//2,(height-nh)//2
    dst[y:y+nh,x:x+nw]=src
    return dst

def group_masks(source):
    h,w=source.shape[:2]
    border=np.concatenate([source[0],source[-1],source[:,0],source[:,-1]])
    med=np.median(border,axis=0)
    is_paper=(np.mean(med)>206 and np.max(med)-np.min(med)<35)
    if not is_paper:
        return np.ones((h,w),np.uint8)*255,[np.ones((h,w),np.uint8)*255],False
    diff=np.linalg.norm(source.astype(np.float32)-med,axis=2)
    fg=((diff>40)&(np.min(source,axis=2)<238)).astype(np.uint8)*255
    joined=cv2.morphologyEx(fg,cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(13,13)))
    count,labels,stats,centers=cv2.connectedComponentsWithStats(joined,8)
    area=max(34,round(h*w*.00012))
    valid=[(i,int(stats[i,cv2.CC_STAT_AREA]),float(centers[i][0]),float(centers[i][1]))
           for i in range(1,count) if stats[i,cv2.CC_STAT_AREA]>=area]
    selected=sorted(valid,key=lambda item:-item[1])[:14]
    selected=sorted(selected,key=lambda item:(item[3]//(h/3),item[2]))
    return fg,[np.uint8(labels==i)*255 for i,*_ in selected],True

def textured_field(height,width,seed):
    rng=np.random.default_rng(seed)
    noise=np.zeros((height,width),np.float32)
    for n,weight in ((8,.20),(24,.09),(72,.035)):
        a=rng.random((max(2,int(height/width*n)),n),dtype=np.float32)
        noise+=(cv2.resize(a,(width,height),interpolation=cv2.INTER_CUBIC)-.5)*weight
    return noise

def stroke_times(source,foreground):
    h,w=foreground.shape
    gray=cv2.cvtColor(source,cv2.COLOR_RGB2GRAY)
    edge=cv2.Canny(cv2.GaussianBlur(gray,(3,3),.65),52,135)
    edge=cv2.bitwise_and(edge,foreground)
    paths,_=cv2.findContours(edge,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
    paths=[p[:,0,:] for p in paths if len(p)>=13]
    paths.sort(key=lambda p:(np.min(p[:,1])//max(1,h//3),np.min(p[:,0])))
    total=sum(len(p) for p in paths)
    times=np.full((h,w),1.5,np.float32)
    if total==0:return times,np.zeros((h,w),np.uint8)
    offset=0
    for c in paths:
        original_len=len(c)
        if len(c)>4000:c=c[::max(1,len(c)//4000)]
        step=max(1,len(c)//200)
        for ix in range(0,len(c)-1,step):
            a,b=c[ix],c[min(ix+step,len(c)-1)]
            cv2.line(times,tuple(a),tuple(b),float((offset+ix)/total),1,cv2.LINE_8)
        offset+=original_len
    return times,np.uint8(times<1.1)*255

def animation_maps(source,seed):
    h,w=source.shape[:2]
    fg,groups,paper=group_masks(source)
    pen,pen_mask=stroke_times(source,fg)
    noise=textured_field(h,w,seed)
    yy,xx=np.indices((h,w),dtype=np.float32)
    arrival=np.ones((h,w),np.float32)
    arrival[fg>0]=.86+noise[fg>0]*.15
    n=max(1,len(groups))
    for j,m in enumerate(groups):
        coords=cv2.findNonZero(m)
        if coords is None:continue
        x0,y0,bw,bh=cv2.boundingRect(coords)
        dist=np.sqrt(((xx-x0)/(bw+1))**2+((yy-y0)/(bh+1))**2)
        local=(dist/math.sqrt(2)*.62+noise*.9).clip(-.08,.78)
        temp=.11+.55*j/n+local*(.63/math.sqrt(n))
        arrival[m>0]=temp[m>0]
    return pen,pen_mask,arrival,len(groups),paper

def frame_at(src,maps,effect,t):
    pen,mask,arrival,_,_=maps
    paper=np.full_like(src,PAPER)
    if effect=="none" or t>=.98:return src.copy()
    if effect=="object_stagger":
        a=np.clip((t-arrival)/.055+.5,0,1)
        return np.uint8(paper*(1-a[:,:,None])+src*a[:,:,None])
    pencil=paper.copy()
    pencil[(mask>0)&(pen<=min(1,t/.67))]=(87,78,70)
    if effect=="stroke_draw":
        a=np.clip((t-.58)/.36,0,1)
        return np.uint8(pencil*(1-a)+src*a) if a>0 else pencil
    if effect=="pigment_bloom":
        a=np.clip((t-arrival*.92)/.16+.45,0,1)
        return np.uint8(paper*(1-a[:,:,None])+src*a[:,:,None])
    if effect=="director_mix":
        color=np.clip((t-.12-arrival*.76)/.10+.4,0,1)
        frame=np.uint8(paper*(1-color[:,:,None])+src*color[:,:,None])
        pencil_on=(mask>0)&(pen<min(1,t/.73))&(color<.80)
        frame[pencil_on]=(87,78,70)
        return frame
    raise ValueError("Unknown effect")

def render(image,output,*,effect="auto",mood="storybook",format_name="libri",
           duration=3.,fps=24,width=360,height=640,seed=13):
    image,output=Path(image),Path(output)
    if effect not in KINDS or mood not in MOODS:raise ValueError("Invalid effect or mood")
    if not .5<=duration<=12 or not 10<=fps<=60:raise ValueError("Invalid duration or FPS")
    if min(width,height)<64 or width%2 or height%2 or width*height>1920*1080:
        raise ValueError("Even dimensions, at most Full HD")
    if output.suffix.lower()!=".mp4":raise ValueError("MP4 output required")
    manifest=output.with_suffix(".json")
    pending=output.with_name(output.stem+".rendering.mp4")
    if any(p.exists() for p in (output,manifest,pending)) or image.resolve()==output.resolve():
        raise FileExistsError("Never overwrite a source, master or previous preview")
    if not image.is_file() or image.stat().st_size<=0:raise ValueError("Missing source")
    chosen,reason=recommend(format_name,mood) if effect=="auto" else (effect,"Explicit one-scene experiment")
    src=load_image(image,width,height)
    maps=animation_maps(src,seed)
    if chosen!="none" and not maps[4]:
        chosen,reason="none","Full-frame / nonpaper source: fail closed without alteration"
    frames=round(duration*fps)
    output.parent.mkdir(parents=True,exist_ok=True)
    cmd=["ffmpeg","-hide_banner","-loglevel","error","-nostdin","-y",
         "-f","rawvideo","-pix_fmt","rgb24","-s:v",f"{width}x{height}",
         "-r",str(fps),"-i","pipe:0","-an","-c:v","libx264",
         "-preset","veryfast","-crf","20","-pix_fmt","yuv420p",
         "-movflags","+faststart",str(pending)]
    proc=None
    try:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        for i in range(frames):
            t=min(1.,i/max(1,frames-1)/.90)
            proc.stdin.write(frame_at(src,maps,chosen,t).tobytes())
        proc.stdin.close()
        err=proc.stderr.read().decode(errors="replace")
        code=proc.wait()
        proc.stderr.close()
        if code or not pending.is_file() or pending.stat().st_size<1000:
            raise RuntimeError("FFmpeg failed: "+err[-800:])
        pending.rename(output)
    except Exception:
        if proc is not None and proc.poll() is None:proc.kill()
        pending.unlink(missing_ok=True)
        raise
    report={"schema":"illustration-reveals-lab-v2",
            "status":"technical_preview_needs_artist_review",
            "requested":effect,"selected":chosen,"reason":reason,
            "source":str(image),"source_sha256":sha256(image),
            "output":str(output),"output_sha256":sha256(output),
            "duration_seconds":duration,"fps":fps,"frames":frames,
            "size":[width,height],"detected_objects":maps[3],
            "paper_background_detected":maps[4],"api_calls":0,
            "source_untouched":True,"master_modified":False,
            "audio_modified":False,"autopublish":False,
            "permanent_effect":False}
    manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--image",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--effect",choices=KINDS,default="auto")
    p.add_argument("--mood",choices=MOODS,default="storybook")
    p.add_argument("--format",dest="format_name",default="libri")
    p.add_argument("--duration",type=float,default=3.)
    p.add_argument("--fps",type=int,default=24)
    p.add_argument("--width",type=int,default=360)
    p.add_argument("--height",type=int,default=640)
    p.add_argument("--seed",type=int,default=13)
    a=p.parse_args()
    print(json.dumps(render(a.image,a.out,effect=a.effect,mood=a.mood,
          format_name=a.format_name,duration=a.duration,fps=a.fps,
          width=a.width,height=a.height,seed=a.seed),indent=2,ensure_ascii=False))

if __name__=="__main__":main()
