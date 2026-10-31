#!/usr/bin/env python3
"""Exact Arnold Böcklin 1883 (NG 2/80) Cinema review renderer. No paid APIs.
Output is a review candidate, never human-approved Gold. Museum is a digitally
constructed environment with the actual painting/frame photographed by Sailko
(CC BY 3.0, 2018), not an authentic museum room.
"""
import argparse, hashlib, json, subprocess, urllib.request, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw

SOURCE="https://upload.wikimedia.org/wikipedia/commons/6/65/Arnold_B%C3%B6cklin_-_Die_Toteninsel_III_%28Alte_Nationalgalerie%2C_Berlin%29.jpg"
FRAME="https://upload.wikimedia.org/wikipedia/commons/6/69/Arnold_b%C3%B6cklin%2C_l%27isola_dei_morti%2C_1883%2C_01.jpg"
FPS=20

def run(args):
    subprocess.run(list(map(str,args)),check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1048576),b""):h.update(b)
    return h.hexdigest()

def obtain(url,path,wh):
    if not path.exists():
        request=urllib.request.Request(url,headers={"User-Agent":"ArtVision-Boecklin/1.0 (Wikimedia attribution)"})
        with urllib.request.urlopen(request,timeout=90) as src,open(path,"wb") as dst:
            if "image" not in src.headers.get("Content-Type",""):raise ValueError("Not an image")
            while True:
                b=src.read(1048576)
                if not b:break
                dst.write(b)
                if dst.tell()>50000000:raise ValueError("Oversized image")
    with Image.open(path) as im:
        if im.size!=wh or im.format!="JPEG":raise ValueError("Incorrect source version / image dimensions")
    return {"bytes":path.stat().st_size,"sha256":sha(path),"dimensions":list(wh)}

def portrait(im,x,y,zoom):
    w,h=im.size; ch=int(h/zoom);cw=int(ch*720/1280)
    left=max(0,min(w-cw,round(w*x-cw/2)))
    top=max(0,min(h-ch,round(h*y-ch/2)))
    return im.crop((left,top,left+cw,top+ch)).resize((1080,1920),Image.Resampling.LANCZOS)

def whole(im):
    bg=im.resize((1080,1920),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(48))
    bg=ImageEnhance.Brightness(bg).enhance(.35)
    fg=im.copy();fg.thumbnail((1060,1700),Image.Resampling.LANCZOS)
    bg.paste(fg,((1080-fg.width)//2,(1920-fg.height)//2))
    return bg

def room(photo):
    W,H=1080,1920
    wall=Image.new("RGB",(W,H),(58,61,62))
    # Digital gallery study, explicitly not Berlin Museum architecture.
    pw=1020;ph=round(photo.height*pw/photo.width)
    pic=photo.resize((pw,ph),Image.Resampling.LANCZOS)
    x=(W-pw)//2;y=(H-ph)//2
    sh=Image.new("RGBA",(W,H));d=ImageDraw.Draw(sh)
    d.rectangle((x+12,y+20,x+pw+24,y+ph+34),fill=(0,0,0,160))
    wall=Image.alpha_composite(wall.convert("RGBA"),sh.filter(ImageFilter.GaussianBlur(25)))
    wall.paste(pic,(x,y))
    return wall.convert("RGB")

def score(path,seconds):
    rate=32000;t=np.arange(int(seconds*rate),dtype=np.float64)/rate
    a=np.zeros_like(t)
    for j,(hz,vol) in enumerate([(73.42,.22),(110,.13),(146.83,.07),(174.61,.045)]):
        a+=vol*np.sin(2*np.pi*hz*t+.21*np.sin(2*np.pi*(.055+j*.013)*t))
    for sec in np.arange(2,seconds,5.5):
        dt=t-sec
        a+=.12*np.exp(-np.maximum(0,dt)*3)*(dt>=0)*np.sin(2*np.pi*55*dt)
    envelope=np.clip(np.minimum(np.minimum(t/2.5,(seconds-t)/3),1),0,1)
    pcm=(32760*np.tanh(a*1.8)*envelope*.72).astype("<i2")
    with wave.open(str(path),"wb") as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes(pcm.tobytes())

def render(name,im,fr,out,test=False):
    sequences={
      "cinema_standard":[(4,"boat",.36,.84,1.42),(6,"whole",0,0,1),
        (5,"cliff_left",.23,.43,1.15),(6,"cypresses",.52,.32,1.15),
        (5,"entrance",.52,.72,1.3),(7,"boat_figure",.37,.83,1.55),
        (5,"right_rock",.78,.37,1.15),(6,"whole",0,0,1)],
      "cinema_museum":[(7,"room",0,0,1),(5,"room",0,0,1),
        (5,"whole",0,0,1),(6,"boat",.37,.83,1.4),
        (6,"entrance",.52,.72,1.2),(6,"cypresses",.52,.32,1.1),
        (5,"right_rock",.78,.4,1.15),(5,"whole",0,0,1),(7,"room",0,0,1)]}
    shots=sequences[name][:2] if test else sequences[name]
    folder=out/name;folder.mkdir(exist_ok=True)
    pieces=[]
    for i,(seconds,key,x,y,z) in enumerate(shots):
        image=room(fr) if key=="room" else whole(im) if key=="whole" else portrait(im,x,y,z)
        pic=folder/f"{i:02d}.png";image.save(pic)
        count=seconds*FPS
        flt=("zoompan=z='min(1+on*0.00023,1.05)':"
             "x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':"
             f"d={count}:s=720x1280:fps={FPS},format=yuv420p")
        seg=folder/f"{i:02d}.mp4"
        run(["ffmpeg","-v","error","-y","-i",pic,"-vf",flt,
             "-frames:v",count,"-an","-c:v","libx264","-crf","19",
             "-preset","veryfast","-r",FPS,"-pix_fmt","yuv420p",seg])
        pieces.append(seg);pic.unlink()
    listing=folder/"list.txt"
    listing.write_text("".join(f"file '{s.resolve()}'\n" for s in pieces))
    silent=folder/"video.mp4"
    run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",listing,"-c","copy",silent])
    audio=folder/"score.wav";score(audio,sum(s[0] for s in shots))
    mp4=out/f"Boecklin_1883_{name}_V100_REVIEW.mp4"
    run(["ffmpeg","-v","error","-y","-i",silent,"-i",audio,"-map","0:v","-map","1:a",
         "-c:v","copy","-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart",
         "-metadata","comment=Digital museum reconstruction; frame photo Sailko CC BY 3.0",
         mp4])
    run(["ffmpeg","-v","error","-i",mp4,"-f","null","-"])
    return {"filename":mp4.name,"bytes":mp4.stat().st_size,"sha256":sha(mp4),
            "duration_seconds":sum(s[0] for s in shots),"ffmpeg_full_decode":"PASS",
            "status":"rendered_needs_human_review_NOT_V25_Gold"}

def main():
    p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True)
    p.add_argument("--test",action="store_true")
    p.add_argument("--source",type=Path);p.add_argument("--frame",type=Path)
    a=p.parse_args();out=a.output;out.mkdir(parents=True,exist_ok=True)
    art=a.source or out/"art_ng2_80.jpg";framed=a.frame or out/"frame_2018.jpg"
    original=obtain(SOURCE,art,(4933,2628)) if not a.test else {"synthetic_test":True}
    frame=obtain(FRAME,framed,(4680,2742)) if not a.test else {"synthetic_test":True}
    with Image.open(art) as im, Image.open(framed) as fr:
        im=im.convert("RGB");fr=fr.convert("RGB")
        files={n:render(n,im,fr,out,a.test) for n in ["cinema_standard","cinema_museum"]}
    report={"work":"Arnold Böcklin Die Toteninsel 1883 NG 2/80",
            "source":SOURCE,"source_art":original,"source_frame":frame,
            "frame_photo_credit":"Sailko CC BY 3.0",
            "room":"digitally reconstructed, not original Alte Nationalgalerie",
            "audio":"original synthesis, zero service calls",
            "two_cinema_MP4":files,"critico_MP4":0,"V25_approved":0,
            "R2_Android_playback_verified":False,"synthetic_test":a.test}
    (out/"QA_V100.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
    print(json.dumps(report,indent=2,ensure_ascii=False))
if __name__=="__main__":main()
