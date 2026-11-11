#!/usr/bin/env python3
"""Experimental Creative Reveals: local, optional, no API and no master writes."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

EFFECTS = ("auto", "none", "ink", "watercolor", "line_art")
FORMATS = ("libri", "artvision_cinema", "artvision_critico", "controluce")
MOODS = ("fiaba", "mistero", "illustrato", "neutro")

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def recommend(fmt: str, mood: str) -> tuple[str, str]:
    if fmt.startswith("artvision_"):
        return "none", "Conserva l'opera autentica: nessun effetto applicato automaticamente."
    if mood == "fiaba":
        return "watercolor", "Acquerello suggerito per l'atmosfera illustrata."
    if mood == "mistero":
        return "ink", "Inchiostro suggerito per l'atmosfera di mistero."
    if mood == "illustrato":
        return "line_art", "Tratto a matita e colore derivati dalla stessa immagine."
    return "none", "Nessun effetto privo di motivazione narrativa."

def create_demo_image(path: Path, width: int = 720, height: int = 1280) -> None:
    """Original procedural illustration ONLY; never a factual artwork."""
    if path.exists():
        raise FileExistsError("La sorgente di prova esiste già: " + str(path))
    W,H = width,height
    arr=np.empty((H,W,3),dtype=np.uint8)
    for y in range(H):
        t=y/H
        arr[y,:,:]=[int(20+42*t),int(34+34*t),int(69+29*t)]
    im=Image.fromarray(arr, mode="RGB")
    d=ImageDraw.Draw(im)
    d.ellipse((int(.56*W),int(.13*H),int(.89*W),int(.13*H+.33*W)),fill=(236,206,145))
    rng=np.random.default_rng(17)
    for x,y in rng.random((115,2)):
        cx,cy=int(x*W),int(y*H*.62)
        r=1+int((x*y*997)%3)
        d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(221,216,192))
    d.polygon([(0,int(.70*H)),(int(.17*W),int(.60*H)),(int(.32*W),int(.68*H)),(int(.51*W),int(.57*H)),(int(.78*W),int(.68*H)),(W,int(.59*H)),(W,H),(0,H)],fill=(49,68,84))
    d.polygon([(0,int(.81*H)),(int(.35*W),int(.70*H)),(int(.72*W),int(.78*H)),(W,int(.73*H)),(W,H),(0,H)],fill=(27,52,61))
    x1,x2=int(.20*W),int(.80*W)
    y1,y2=int(.47*H),int(.89*H)
    d.rectangle((x1,y1,x2,y2),fill=(30,35,53),outline=(215,164,109),width=5)
    d.polygon([(x1-int(.03*W),y1),(W//2,int(.35*H)),(x2+int(.03*W),y1)],fill=(38,41,60),outline=(215,164,109),width=5)
    left,right=int(.40*W),int(.60*W)
    d.rectangle((left,int(.64*H),right,y2),fill=(212,157,102))
    d.arc((left,int(.57*H),right,int(.72*H)),180,360,fill=(212,157,102),width=6)
    d.ellipse((int(.55*W),int(.79*H),int(.56*W),int(.80*H)),fill=(45,40,44))
    d.line((int(.5*W),y2,int(.28*W),H),fill=(191,149,110),width=4)
    d.line((int(.5*W),y2,int(.72*W),H),fill=(191,149,110),width=4)
    im.filter(ImageFilter.GaussianBlur(.5)).save(path)

def fit_source(path: Path, width: int, height: int) -> np.ndarray:
    with Image.open(path) as im:
        source=np.asarray(im.convert("RGB"))
    h,w=source.shape[:2]
    if min(h,w)<32:
        raise ValueError("Immagine sorgente troppo piccola")
    scale=min(width/w,height/h)
    nw,nh=max(1,round(w*scale)),max(1,round(h*scale))
    resized=cv2.resize(source,(nw,nh),interpolation=cv2.INTER_AREA if scale<1 else cv2.INTER_CUBIC)
    result=np.full((height,width,3),(245,239,223),dtype=np.uint8)
    x,y=(width-nw)//2,(height-nh)//2
    result[y:y+nh,x:x+nw]=resized
    return result

def organic_field(height: int, width: int, effect: str, seed: int) -> np.ndarray:
    rng=np.random.default_rng(seed)
    yy,xx=np.mgrid[0:height,0:width].astype(np.float32)
    x=xx/max(width-1,1)
    y=yy/max(height-1,1)
    rough=np.zeros((height,width),np.float32)
    for n, weight in [(5,.24),(15,.12),(45,.05)]:
        small=rng.random((max(2,round(height/width*n)),n),dtype=np.float32)
        rough+=(cv2.resize(small,(width,height),interpolation=cv2.INTER_CUBIC)-.5)*weight
    if effect=="ink":
        field=np.sqrt(((x-.29)/1.05)**2+((y-.34)/1.10)**2)+rough*.8
    elif effect=="watercolor":
        field=.44*x+.54*y+.075*np.sin(x*8+y*5)+rough
    else:
        field=x+.14*y+rough*.4
    return ((field-field.min())/(field.max()-field.min()+1e-6)).astype(np.float32)

def outline_background(source: np.ndarray) -> np.ndarray:
    gray=cv2.cvtColor(source,cv2.COLOR_RGB2GRAY)
    edges=cv2.Canny(cv2.GaussianBlur(gray,(5,5),1.),65,145)
    paper=np.full_like(source,(245,239,223))
    paper[edges>0]=[82,77,77]
    return paper

def render(image_path: Path, output: Path, *, effect: str="auto", fmt: str="libri",
           mood: str="fiaba", duration: float=3., fps: int=24,
           width: int=540, height: int=960, seed: int=23) -> dict:
    if effect not in EFFECTS or fmt not in FORMATS or mood not in MOODS:
        raise ValueError("Format, atmosfera o effetto sconosciuto")
    if not .5<=duration<=15 or not 10<=fps<=60:
        raise ValueError("Durata o FPS fuori limite")
    if width%2 or height%2 or min(width,height)<64 or width*height>1920*1080:
        raise ValueError("Usare dimensioni pari, massimo 1920x1080 pixel totali")
    manifest=output.with_suffix(".json")
    partial=output.with_name(output.stem+".incomplete.mp4")
    if image_path.resolve()==output.resolve() or any(p.exists() for p in (output,manifest,partial)):
        raise FileExistsError("Originali e anteprime preesistenti non si sovrascrivono")
    selected,reason=recommend(fmt,mood) if effect=="auto" else (effect,"Tecnica scelta esplicitamente soltanto per questa prova.")
    source=fit_source(image_path,width,height)
    background=outline_background(source) if selected=="line_art" else np.full_like(source,(245,239,223))
    field=None if selected=="none" else organic_field(height,width,selected,seed)
    count=round(duration*fps)
    if count<2:
        raise ValueError("La prova necessita almeno due fotogrammi")
    output.parent.mkdir(parents=True,exist_ok=True)
    cmd=["ffmpeg","-hide_banner","-loglevel","error","-nostdin","-y",
         "-f","rawvideo","-pix_fmt","rgb24","-s:v",f"{width}x{height}",
         "-r",str(fps),"-i","pipe:0","-an","-c:v","libx264",
         "-preset","veryfast","-crf","20","-pix_fmt","yuv420p",
         "-movflags","+faststart",str(partial)]
    try:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        assert proc.stdin is not None
        for i in range(count):
            if selected=="none":
                frame=source
            else:
                p=float(np.clip(i/max((count-1)*.85,1),0,1))
                p=p*p*(3-2*p)
                feather={"ink":.07,"watercolor":.14,"line_art":.06}[selected]
                alpha=np.ones_like(field) if p>=1 else np.clip((p-field)/feather+.50,0,1)
                a=alpha[:,:,None]
                frame=(source.astype(np.float32)*a+background.astype(np.float32)*(1-a)).astype(np.uint8)
            proc.stdin.write(frame.tobytes())
        proc.stdin.close()
        err=proc.stderr.read().decode("utf-8",errors="replace") if proc.stderr else ""
        if proc.stderr is not None:
            proc.stderr.close()
        code=proc.wait()
        if code!=0 or not partial.is_file() or partial.stat().st_size==0:
            raise RuntimeError("FFmpeg fallito: "+err[-800:])
        partial.replace(output)
    except Exception:
        if partial.exists():
            partial.unlink()
        raise
    report={"schema":"creative-reveals-experiment-v1",
            "status":"rendered_needs_artistic_review",
            "source":str(image_path),"source_sha256":digest(image_path),
            "output":str(output),"output_sha256":digest(output),
            "effect_request":effect,"director_suggestion":selected,"reason":reason,
            "duration_seconds":duration,"frames":count,"fps":fps,
            "size":[width,height],"format":fmt,"mood":mood,"seed":seed,
            "paid_or_ai_calls":0,"is_master":False,"source_untouched":True,
            "auto_published":False,
            "source_rights":"synthetic_original_demo" if image_path.name=="PROCEDURAL_SOURCE.png" else "verify_before_publication",
            "utc":datetime.now(timezone.utc).isoformat()}
    manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report

def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--image",type=Path,help="Optional licensed still, no automatic network download")
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--effect",choices=EFFECTS,default="auto")
    ap.add_argument("--format",dest="fmt",choices=FORMATS,default="libri")
    ap.add_argument("--mood",choices=MOODS,default="fiaba")
    ap.add_argument("--duration",type=float,default=3.)
    ap.add_argument("--fps",type=int,default=24)
    ap.add_argument("--width",type=int,default=540)
    ap.add_argument("--height",type=int,default=960)
    ap.add_argument("--seed",type=int,default=23)
    args=ap.parse_args()
    source=args.image
    if source is None:
        source=args.out.parent/"PROCEDURAL_SOURCE.png"
        source.parent.mkdir(parents=True,exist_ok=True)
        create_demo_image(source)
    if not source.is_file():
        ap.error("Immagine sorgente non trovata")
    result=render(source,args.out,effect=args.effect,fmt=args.fmt,mood=args.mood,
                  duration=args.duration,fps=args.fps,width=args.width,height=args.height,seed=args.seed)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
