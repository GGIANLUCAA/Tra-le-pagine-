#!/usr/bin/env python3
"""Render two real Böcklin NG 2/80 Critico MP4 from one verified Google Gacrux WAV.
No TTS or billable API calls here. No placeholder speech; fail closed.
Frame photo Sailko 2018 CC BY 3.0; museum room is a DIGITAL reconstruction.
"""
import argparse, hashlib, json, re, subprocess
from pathlib import Path
import cv2
import numpy as np
import soundfile as sf
from PIL import Image, ImageEnhance, ImageFilter
W,H,FPS=720,1280,20
DELAY,TAIL=1.4,3.0
ART_SHA="f9a7c33f1b7a2aae03aacd192706faee3740cfd9d1d277516dec39795f405ce3"
FRAME_SHA="72655ceea488c5f4ecf207dd5a419618685b0ee0c59d553f63cbbba0bb623b65"

def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for part in iter(lambda:f.read(1048576),b""): h.update(part)
    return h.hexdigest()

def ff(args):
    p=subprocess.run([str(i) for i in args],capture_output=True,text=True)
    if p.returncode: raise RuntimeError("FFmpeg: "+p.stderr[-1000:])

def split(s):
    return [a.strip() for a in re.split(r'(?<=[.!?])\s+(?=[A-ZÀ-ÙÈÉ«“])',re.sub(r'\s+',' ',s.strip())) if a.strip()]

def verified_voice(voice_dir,chapters):
    wav=voice_dir/"VOCE.wav";cache=voice_dir/"VOICE_CACHE_V13.json";align=voice_dir/"ALLINEAMENTO_VOCE.json"
    if not all(p.is_file() for p in (wav,cache,align)):
        raise RuntimeError("Missing genuine shared Gacrux WAV/cache/ASR; no synthetic substitution")
    c=json.loads(cache.read_text());a=json.loads(align.read_text())
    if c.get("wav_sha256")!=sha(wav): raise ValueError("WAV hash mismatch")
    p=c.get("profile",{})
    if p.get("model")!="gemini-3.8-flash-tts" or p.get("voice")!="Gacrux":
        raise ValueError("Voice provider mismatch")
    if a.get("method")!="asr_with_interpolation" or (a.get("matched_fraction") or 0)<.85:
        raise ValueError("No sufficiently grounded ASR alignment")
    x,sr=sf.read(wav,dtype="float32")
    if sr!=24000 or x.ndim!=1 or not np.isfinite(x).all(): raise ValueError("WAV invalid")
    duration=len(x)/sr
    if not 65<=duration<=170: raise ValueError("Narration duration inappropriate")
    timed=c.get("timed");count=sum(len(split(ch["text"])) for ch in chapters)
    if not timed or len(timed)!=count: raise ValueError("Wrong voice/chapters alignment")
    ends=[];i=0
    for ch in chapters:
        i+=len(split(ch["text"]));ends.append(float(timed[i-1][2]))
    if ends[-1]>duration+.1:raise ValueError("ASR exceeds voice recording")
    return wav,duration,ends,a

def crop(img,x,y,zoom):
    ih,iw=img.shape[:2];ch=min(ih,max(120,int(ih/zoom)));cw=min(iw,max(70,int(ch*W/H)))
    left=max(0,min(iw-cw,round(iw*x-cw/2)));top=max(0,min(ih-ch,round(ih*y-ch/2)))
    return cv2.resize(img[top:top+ch,left:left+cw],(W,H),interpolation=cv2.INTER_AREA)

def easing(u):
    u=max(0.,min(1.,u));return u*u*(3-2*u)

def full_painting(im):
    pil=Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB))
    bg=ImageEnhance.Brightness(pil.resize((W,H)).filter(ImageFilter.GaussianBlur(35))).enhance(.35)
    fg=pil.copy();fg.thumbnail((W-16,H-140),Image.Resampling.LANCZOS)
    bg.paste(fg,((W-fg.width)//2,(H-fg.height)//2))
    return cv2.cvtColor(np.asarray(bg),cv2.COLOR_RGB2BGR)

def room(photo):
    wall=np.empty((H*2,W*2,3),dtype=np.uint8);wall[:]=(60,60,58)
    ph,pw=photo.shape[:2];w=int(W*1.83);h=round(w*ph/pw)
    img=cv2.resize(photo,(w,h),interpolation=cv2.INTER_AREA)
    x=(wall.shape[1]-w)//2;y=(wall.shape[0]-h)//2
    wall[y:y+h,x:x+w]=img
    return wall

def score(seconds,path):
    sr=32000;t=np.arange(int(seconds*sr),dtype=np.float64)/sr
    sig=(.15*np.sin(2*np.pi*73.42*t)+.09*np.sin(2*np.pi*110*t)+.05*np.sin(2*np.pi*146.8*t))
    env=np.clip(np.minimum(t/2.5,(seconds-t)/3),0,1)
    sf.write(path,(sig*env).astype("float32"),sr)

def video(variant,im,photo,marks,out):
    coords=[(.37,.78,1.58),(.50,.50,1.),(.50,.9,1.6),(.37,.82,2.1),
            (.53,.65,1.7),(.54,.28,1.5),(.76,.30,1.65),(.50,.50,1.),(.42,.77,1.3)]
    gallery=room(photo);whole=full_painting(im)
    last=marks[-1];fname=out/(variant+"_silent.mp4")
    pipe=subprocess.Popen(["ffmpeg","-hide_banner","-loglevel","error","-y",
        "-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),
        "-i","pipe:0","-an","-c:v","libx264","-preset","veryfast",
        "-crf","21","-pix_fmt","yuv420p",str(fname)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for n in range(last):
            chapter=next((i for i in range(9) if n<marks[i+1]),8)
            start,end=marks[chapter],marks[chapter+1]
            x,y,z=coords[chapter];u=easing((n-start)/max(1,end-start))
            if variant=="critico_museum":
                px,py,pz=coords[max(0,chapter-1)]
                move=easing((n-start)/max(1,(end-start)*.35))
                x=px+(x-px)*move;y=py+(y-py)*move;z=pz+(z-pz)*move
                sec=n/FPS
                if sec<5:
                    progress=easing(sec/5)
                    image=crop(gallery,.5-.12*progress,.5+.09*progress,1+2.55*progress)
                elif sec>last/FPS-7:
                    progress=easing((sec-(last/FPS-7))/7)
                    image=crop(gallery,.38+.12*progress,.59-.09*progress,3.55-2.55*progress)
                else:
                    image=crop(im,x,y,max(1.10,z))
            else:
                image=whole if z<=1.01 else crop(im,x,y,z*(1+.03*u))
            pipe.stdin.write(image.tobytes())
    finally:
        pipe.stdin.close()
    err=pipe.stderr.read().decode("utf8","replace")
    if pipe.wait()!=0:raise RuntimeError("Renderer failed: "+err[-900:])
    return fname

def main():
    ap=argparse.ArgumentParser()
    for name in ("recipe","art","frame","voice_dir","output"):
        ap.add_argument("--"+name.replace("_","-"),type=Path,required=True)
    a=ap.parse_args();out=a.output;out.mkdir(parents=True,exist_ok=True)
    recipe=json.loads(a.recipe.read_text(encoding="utf8"))
    if recipe.get("work_id")!="bocklin_isle_of_dead_1883_berlin_ng2_80":
        raise ValueError("Not exact third 1883 version")
    if sha(a.art)!=ART_SHA or sha(a.frame)!=FRAME_SHA:
        raise ValueError("Wrong original artwork or photographed exact frame")
    chapters=recipe["critico"]["chapters"]
    if len(chapters)!=9:raise ValueError("Expected exactly 9 semantic chapters")
    wav,duration,ends,alignment=verified_voice(a.voice_dir,chapters)
    marks=[0]+[round((DELAY+t)*FPS) for t in ends]
    marks[-1]=max(marks[-1],round((DELAY+duration)*FPS))
    marks.append(round((DELAY+duration+TAIL)*FPS))
    if marks!=sorted(marks):raise ValueError("Nonmonotonic chapter alignment")
    art=cv2.imread(str(a.art));frame=cv2.imread(str(a.frame))
    if art is None or frame is None or art.shape[:2]!=(2628,4933) or frame.shape[:2]!=(2742,4680):
        raise ValueError("Artwork/frame image sizes do not match verified source")
    musical=out/"MUSIC_ORIGINAL.wav";score(marks[-1]/FPS,musical)
    shared=out/"Boecklin_Gacrux_SHARED_AUDIO_V102.m4a"
    delay=round(DELAY*1000)
    ff(["ffmpeg","-v","error","-y","-i",wav,"-i",musical,"-filter_complex",
        f"[0:a]volume=1,adelay={delay}|{delay}[v];[1:a]volume=.22[m];[v][m]amix=inputs=2:duration=longest:dropout_transition=0,alimiter=limit=.95[a]",
        "-map","[a]","-c:a","aac","-b:a","160k",shared])
    files={}
    for variant in ("critico_standard","critico_museum"):
        silent=video(variant,art,frame,marks,out)
        target=out/f"Boecklin_1883_{variant}_V102_GACRUX_REVIEW.mp4"
        ff(["ffmpeg","-v","error","-y","-i",silent,"-i",shared,"-map","0:v:0","-map","1:a:0",
            "-c:v","copy","-c:a","copy","-shortest","-movflags","+faststart",target])
        ff(["ffmpeg","-v","error","-xerror","-i",target,"-f","null","-"])
        files[variant]={"file":target.name,"bytes":target.stat().st_size,"sha256":sha(target),
            "ffmpeg_full_decode":"PASS","duration_seconds":marks[-1]/FPS,"V25_Gold":False}
        silent.unlink()
    qa={"artwork":"Arnold Böcklin 1883 NG 2/80","shared_voice_WAV_SHA256":sha(wav),
        "audio_AAC_source_SHA256":sha(shared),"alignment":alignment,"files":files,
        "artwork_source_SHA256":ART_SHA,"frame_photo_SHA256":FRAME_SHA,
        "room":"digital reconstruction, not real Berlin museum",
        "credit":"Frame photo 2018 Sailko CC BY 3.0",
        "R2_Android_verified":False,"V25_Gold":0,"no_api_calls_by_renderer":True}
    (out/"BOECKLIN_CRITICO_V102_QA.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2))
    print(json.dumps(qa,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
