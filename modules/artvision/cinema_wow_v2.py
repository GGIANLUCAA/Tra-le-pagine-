#!/usr/bin/env python3
"""ArtVision V2: cinematic music-led direction for AUTHENTIC museum artwork.
Independent optional renderer. No generative editing of artwork.
"""
from __future__ import annotations
import hashlib
import json
import math
import shutil
import subprocess
import wave
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

BPM = 100
BEAT = 60.0/BPM
SHOT_MODES = ["detail", "hero", "tracking", "full", "macro", "hero", "tracking", "duo"]

def source_image(path):
    with Image.open(path) as im:
        return np.array(ImageOps.exif_transpose(im).convert("RGB"))[:, :, ::-1].copy()

def focal_point(im):
    h,w = im.shape[:2]
    gray=cv2.cvtColor(cv2.resize(im,(120,120)),cv2.COLOR_BGR2GRAY)
    edges=cv2.Laplacian(gray,cv2.CV_32F)
    energy=cv2.GaussianBlur(abs(edges),(27,27),0)
    # Restrict to central readable composition; manual focal directions override in future.
    energy[:25]=0;energy[95:]=0;energy[:,:21]=0;energy[:,99:]=0
    y,x=np.unravel_index(np.argmax(energy),energy.shape)
    return float(np.clip(x/120,.27,.73)),float(np.clip(y/120,.27,.73))

def plan_storyboard(images,artist,duration):
    if duration < 18:raise ValueError("Minimum cinematic sample length 18s")
    count=len(images)
    if count < 6:raise ValueError("Six or more licensed artworks required")
    # First image: purposeful visual hook, not first search result.
    best_first = None
    if "van gogh" in artist.lower():
        best_first = next((j for j,rec in enumerate(images)
            if "two poplars" in rec["title"].lower()),None)
    if best_first is None:
        scores=[]
        for rec in images:
            thumb=cv2.resize(rec["frame"],(96,144),interpolation=cv2.INTER_AREA)
            hsv=cv2.cvtColor(thumb,cv2.COLOR_BGR2HSV)
            gray=cv2.cvtColor(thumb,cv2.COLOR_BGR2GRAY)
            scores.append(float(hsv[:,:,1].mean())*.70+float(gray.std())*.30)
        best_first=int(np.argmax(scores))
    plan=[]
    t=0.0;i=0
    while t < duration-2.7:
        left=duration-t
        f=t/duration
        if i==0:beats=4;mode="title";act="gancio"
        elif f < .08:beats=[1,2,2,3][i%4];mode=["macro","hero","detail","tracking"][i%4];act="gancio"
        elif f < .20:beats=[3,4,3,5][i%4];mode=SHOT_MODES[i%len(SHOT_MODES)];act="ingresso"
        elif f < .45:beats=[2,3,4,3][i%4];mode=SHOT_MODES[(i+2)%len(SHOT_MODES)];act="scoperta"
        elif f < .62:beats=[4,5,6,4][i%4];mode=SHOT_MODES[(i+3)%len(SHOT_MODES)];act="respiro"
        elif f < .85:beats=[1,2,3,2][i%4];mode=SHOT_MODES[(i+4)%len(SHOT_MODES)];act="crescendo"
        elif f < .96:beats=[1,1,2,1][i%4];mode=SHOT_MODES[(i+1)%len(SHOT_MODES)];act="climax"
        else:beats=4;mode="hero";act="risoluzione"
        seconds=min(beats*BEAT,max(.3,left-2.4))
        if seconds<=0:break
        image_index=best_first if i==0 else (i*5+3)%count
        focus=focal_point(images[image_index]["frame"])
        turn=(i%5-2)*.034
        focus=(float(np.clip(focus[0]+turn,.24,.76)),
               float(np.clip(focus[1]-turn*.6,.24,.76)))
        plan.append({"index":i,"start":round(t,3),"end":round(t+seconds,3),
                     "duration":seconds,"art_index":image_index,
                     "title":images[image_index]["title"],"mode":mode,"act":act,
                     "focus":focus,"transition":"soft" if i%5 in (2,3) else "cut",
                     "reason":("reveal artist identity" if mode=="title" else
                               "rhythmic artistic correspondence")})
        t+=seconds;i+=1
    if plan and duration-t < 1.0:
        plan[-1]["end"]=round(duration,3)
        plan[-1]["duration"]=plan[-1]["end"]-plan[-1]["start"]
    else:
        plan.append({"index":i,"start":round(t,3),"end":float(duration),
                     "duration":duration-t,"art_index":(i*5+3)%count,
                     "title":images[(i*5+3)%count]["title"],"mode":"outro","act":"risoluzione",
                     "focus":(.5,.5),"transition":"soft","reason":"final held image"})
    return plan

def full_framing(im,width,height):
    frame=np.full((height,width,3), (14,12,11),np.uint8)
    h,w=im.shape[:2]
    z=min((width-32)/w,(height-102)/h)
    nw,nh=max(1,int(w*z)),max(1,int(h*z))
    image=cv2.resize(im,(nw,nh),interpolation=cv2.INTER_AREA if z<1 else cv2.INTER_CUBIC)
    x=(width-nw)//2;y=(height-nh)//2
    cv2.rectangle(frame,(max(x-2,0),max(y-2,0)),(min(x+nw+1,width-1),min(y+nh+1,height-1)),(29,28,26),-1)
    frame[y:y+nh,x:x+nw]=image
    return frame

def motion_frame(im,p,focus,mode,width,height,full):
    if mode in ("full","outro"):
        return full.copy()
    ih,iw=im.shape[:2]
    if mode=="title":zoom=1.02+0.08*p
    elif mode=="macro":zoom=1.55+.17*p
    elif mode=="detail":zoom=1.28+.18*p
    elif mode=="hero":zoom=1.07+.16*p
    elif mode=="tracking":zoom=1.18+.09*p
    else:zoom=1.25+.14*p
    # Crop strictly inside original artwork; preserve aspect ratio and geometry.
    want=width/height
    if iw/ih>want:
        base_h=ih; base_w=ih*want
    else:
        base_w=iw; base_h=iw/want
    cw=base_w/zoom;ch=base_h/zoom
    fx,fy=focus
    if mode=="tracking":fx=float(np.clip(fx+(p-.5)*.22,.22,.78))
    else:fx=float(np.clip(fx+(p-.5)*.028,.20,.80))
    fy=float(np.clip(fy+(p-.5)*.046,.20,.80))
    x0=int(np.clip(fx*iw-cw/2,0,iw-cw));y0=int(np.clip(fy*ih-ch/2,0,ih-ch))
    crop=im[y0:y0+int(ch),x0:x0+int(cw)]
    return cv2.resize(crop,(width,height),interpolation=cv2.INTER_AREA if crop.shape[1]>width else cv2.INTER_CUBIC)

def text_frame(im,artist,p,width,height):
    shade=cv2.addWeighted(im,.49,np.zeros_like(im),.51,0)
    pil=Image.fromarray(cv2.cvtColor(shade,cv2.COLOR_BGR2RGB)).convert("RGBA")
    over=Image.new("RGBA",(width,height),(0,0,0,0))
    d=ImageDraw.Draw(over)
    font_path="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
    sub_path="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    text=artist.upper()
    size=min(56,max(25,int(width/(max(len(text),8)*.66))))
    f=ImageFont.truetype(font_path,size)
    f2=ImageFont.truetype(sub_path,17)
    alpha=int(255*min(1,p*4.4,max(0,(1-p)*4.5)))
    top=height*.44
    d.line((width*.10,top-34,width*.90,top-34),fill=(231,201,151,alpha),width=2)
    words=text.split();lines=[];line=""
    for word in words:
        new=(line+" "+word).strip()
        if d.textbbox((0,0),new,font=f)[2]>width*.85 and line:
            lines.append(line);line=word
        else:line=new
    if line:lines.append(line)
    for j,s in enumerate(lines):
        d.text((width*.10,top+j*(size+10)),s,font=f,fill=(250,242,224,alpha))
    d.text((width*.105,top+len(lines)*(size+10)+20),"ARTVISION · CINEMA",font=f2,fill=(229,198,148,alpha))
    return cv2.cvtColor(np.array(Image.alpha_composite(pil,over).convert("RGB")),cv2.COLOR_RGB2BGR)

def render_music(path,duration,sr=32000):
    """Original synthesized score with evolving pads, arpeggios and restrained pulse; no third-party samples."""
    t=np.arange(int(sr*duration),dtype=np.float64)/sr
    s=np.zeros(len(t),np.float64)
    chords=[(196.,246.94,293.66),(174.61,220.,261.63),
            (146.83,196.,246.94),(164.81,220.,277.18)]
    phrase=8*BEAT
    for j in range(math.ceil(duration/phrase)+1):
        begin=j*phrase; notes=chords[j%4]
        idx=np.where((t>=begin)&(t<min(duration,begin+phrase+1.5)))[0]
        if not len(idx):continue
        u=t[idx]-begin
        env=np.minimum(1.,u/.48)*np.minimum(1.,(phrase+1.5-u)/1.6)
        for k,f in enumerate(notes):
            s[idx]+=.033*env*(np.sin(2*np.pi*(f/2)*u)+.18*np.sin(2*np.pi*f*u))
    rng=np.random.default_rng(2748)
    for b in range(math.ceil(duration/BEAT)+1):
        beat_t=b*BEAT
        strength=.22 if beat_t/duration<.07 else (.5 if beat_t/duration<.6 else .95)
        # tonal bell melody on alternate beats
        if b%2==0:
            notes=chords[(b//8)%4]
            f=notes[(b//2)%3]*2
            ids=np.where((t>=beat_t)&(t<min(duration,beat_t+.52)))[0]
            u=t[ids]-beat_t
            s[ids]+=.042*np.exp(-u*5)*np.minimum(1,u*50)*(np.sin(2*np.pi*f*u)+.13*np.sin(4*np.pi*f*u))
        if beat_t < duration:
            ids=np.where((t>=beat_t)&(t<min(duration,beat_t+.24)))[0]
            u=t[ids]-beat_t
            if len(ids):
                phase=2*np.pi*(65*u+48*(1-np.exp(-u*28))/28)
                s[ids]+=.14*strength*np.sin(phase)*np.exp(-u*22)
        if b%4 in (1,3):
            ids=np.where((t>=beat_t)&(t<min(duration,beat_t+.09)))[0]
            u=t[ids]-beat_t
            s[ids]+=.045*strength*rng.standard_normal(len(ids))*np.exp(-u*42)
        for half in (0,.5):
            start=beat_t+half*BEAT
            ids=np.where((t>=start)&(t<min(duration,start+.038)))[0]
            u=t[ids]-start
            s[ids]+=.014*strength*rng.standard_normal(len(ids))*np.exp(-u*67)
    env=np.clip(np.minimum(1,t/1.0)*np.minimum(1,(duration-t)/1.7),0,1)
    s=np.tanh(s*1.4)*env*.82
    pcm=np.column_stack((s,s*.96))
    with wave.open(str(path),"wb") as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr)
        w.writeframes((np.clip(pcm,-.95,.95)*32767).astype("<i2").tobytes())

def make_video_cinematic(artworks,artist,duration,out,size=(720,1280),fps=24):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):raise RuntimeError("ffmpeg and ffprobe required")
    source=[dict(row,frame=source_image(row["file"])) for row in artworks]
    plan=plan_storyboard(source,artist,duration)
    # Save canonical source IDs and creative intentions, never image arrays.
    (out/"STORYBOARD_REGIA.json").write_text(json.dumps([
        {k:(list(v) if isinstance(v,tuple) else v) for k,v in shot.items()} for shot in plan
    ],ensure_ascii=False,indent=2),encoding="utf-8")
    tmp=out/"cinema_v2_tmp";tmp.mkdir(exist_ok=True)
    silent=tmp/"render.mp4"
    width,height=size
    writer=cv2.VideoWriter(str(silent),cv2.VideoWriter_fourcc(*"mp4v"),fps,(width,height))
    if not writer.isOpened():raise RuntimeError("VideoWriter could not start")
    frames=0;prev=None
    fulls=[full_framing(row["frame"],width,height) for row in source]
    try:
        for i,shot in enumerate(plan):
            count=max(1,round(float(shot["duration"])*fps))
            idx=int(shot["art_index"]); mode=shot["mode"]
            focus=shot["focus"]
            for k in range(count):
                p=k/max(count-1,1)
                frame=motion_frame(source[idx]["frame"],p,focus,mode,width,height,fulls[idx])
                if mode=="title":frame=text_frame(frame,artist,p,width,height)
                if mode=="duo":
                    ix=(idx+3)%len(source)
                    alt=motion_frame(source[ix]["frame"],1-p,source[ix].get("focus",(.50,.50)),"detail",width,height,fulls[ix])
                    frame[:,width//2+2:]=alt[:,width//2+2:]
                    cv2.line(frame,(width//2,80),(width//2,height-80),(219,197,163),2)
                if mode=="outro":
                    frame=cv2.convertScaleAbs(frame,alpha=max(0,min(1,(1-p)*3.1)))
                if prev is not None and shot["transition"]=="soft" and k<4:
                    a=(k+1)/4.
                    frame=cv2.addWeighted(prev,1-a,frame,a,0)
                writer.write(frame)
                frames+=1
            prev=frame.copy()
            print(f"Cinema V2 scene {i+1}/{len(plan)} {mode}",flush=True)
    finally:writer.release()
    wav=tmp/"musica_originale.wav"
    render_music(wav,frames/fps)
    final=out/"ARTVISION_VIDEO.mp4"
    proc=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(silent),
                         "-i",str(wav),"-c:v","libx264","-preset","veryfast","-crf","21",
                         "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k",
                         "-shortest","-movflags","+faststart",str(final)],capture_output=True,text=True)
    if proc.returncode:raise RuntimeError(proc.stderr[-2000:])
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-ss","0.95","-i",str(final),
                    "-frames:v","1",str(out/"COPERTINA.jpg")],check=True)
    probe=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration,size:"
                          "stream=codec_type,width,height","-of","json",str(final)],capture_output=True,text=True,check=True)
    q=json.loads(probe.stdout)
    actual=float(q["format"]["duration"])
    if abs(actual-duration)>2 or {st["codec_type"] for st in q["streams"]}!={"video","audio"}:
        raise RuntimeError(f"Cinematic quality control failed: {q}")
    shutil.rmtree(tmp,ignore_errors=True)
    return final,plan,q
