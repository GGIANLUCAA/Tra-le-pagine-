#!/usr/bin/env python3
"""ArtVision Cinema V23: five artwork-specific, public-domain image films.
Isolated add-on; never overwrites Cinema V6 gold masters.
Original soundtrack: generated deterministically below, no third-party samples.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import random
import subprocess
import sys
import time
import urllib.parse
import wave

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H, FPS = 1080, 1920, 24
ROOT = "https://commons.wikimedia.org/wiki/File:"
WORKS = {
 "goya": dict(artist="FRANCISCO GOYA", name="SATURNO", subtitle="L'orrore nel buio", file="Francisco de Goya, Saturno devorando a su hijo (1819-1823).jpg",
       tone="dread", root=38, kind="minor", shots=[
       ("detail",2.5,.56,.32,1.40,"Il primo sguardo: gli occhi"),
       ("detail",5.5,.55,.27,1.13,"Il terrore negli occhi"),
       ("detail",7,.54,.53,1.12,"Le mani"),
       ("full",8,.5,.5,1.0,"Il dipinto appare intero"),
       ("detail",7,.56,.67,1.09,"Il gesto"),
       ("detail",8,.38,.38,1.02,"Il buio e la figura"),
       ("detail",7,.58,.26,1.18,"L'ultimo sguardo"),
       ("full",6,.5,.5,1.0,"Rivelazione e chiusura")]),
 "fuseli": dict(artist="HENRY FÜSSLI", name="L'INCUBO", subtitle="Il sonno ha un volto", file="John Henry Fuseli - The Nightmare.JPG",
       tone="phantom", root=37, kind="minor", shots=[
       ("detail",2,.59,.27,1.09,"Creatura al centro"),
       ("detail",5,.09,.39,1.04,"Occhi nella tenda"),
       ("detail",7,.85,.65,1.11,"Il volto della donna"),
       ("full",7,.5,.5,1,"Il teatro del sogno"),
       ("detail",7,.57,.3,1.05,"La creatura"),
       ("detail",8,.67,.64,1.05,"Corpo e tessuti"),
       ("detail",9,.09,.36,1.10,"Ritorno del cavallo"),
       ("full",5,.5,.5,1,"Opera completa")]),
 "bocklin": dict(artist="ARNOLD BÖCKLIN", name="L'ISOLA DEI MORTI", subtitle="Un viaggio senza ritorno", file="Arnold Böcklin - Die Toteninsel III (Alte Nationalgalerie, Berlin).jpg",
       tone="island", root=33, kind="minor", shots=[
       ("detail",3,.38,.78,1.12,"La piccola barca"),
       ("detail",6,.45,.50,1.02,"Ingresso"),
       ("detail",8,.32,.22,1.02,"Cipressi"),
       ("full",9,.5,.5,1,"Paesaggio intero"),
       ("detail",9,.66,.49,1.06,"Rocce"),
       ("detail",10,.42,.77,1.12,"Ritorno alla barca"),
       ("detail",9,.36,.45,1.03,"Mistero del passaggio"),
       ("full",8,.5,.5,1,"Silenzio finale")]),
 "waterhouse": dict(artist="JOHN W. WATERHOUSE", name="LA DAMA DI SHALOTT", subtitle="L'ultimo viaggio", file="John william waterhouse, the lady of shalott, 1888, 01.jpg",
       tone="elegy", root=40, kind="minor", shots=[
       ("detail",3,.49,.43,1.10,"Sguardo lontano"),
       ("detail",6,.29,.52,1.04,"Mano e stoffa"),
       ("detail",8,.78,.52,1.07,"La prua"),
       ("full",8,.5,.5,1,"La barca nel paesaggio"),
       ("detail",8,.52,.42,1.06,"Il volto"),
       ("detail",8,.27,.79,1.04,"L'acqua e i riflessi"),
       ("detail",9,.40,.33,1.03,"Silenzio"),
       ("full",7,.5,.5,1,"Ultima rivelazione")]),
 "friedrich": dict(artist="CASPAR D. FRIEDRICH", name="IL VIANDANTE", subtitle="Davanti all'infinito", file="Friedrich, Caspar David - Wanderer über dem Nebelmeer.jpg",
       tone="sublime", root=38, kind="major", shots=[
       ("detail",2,.47,.41,1.15,"La silhouette"),
       ("detail",6,.69,.28,1.04,"Le montagne lontane"),
       ("detail",7,.33,.70,1.01,"Pietra e appoggio"),
       ("full",7,.5,.5,1,"L'intero panorama"),
       ("detail",8,.47,.42,1.06,"Il viandante"),
       ("detail",8,.70,.33,1.03,"Orizzonte nella nebbia"),
       ("detail",6,.50,.83,1.04,"Le rocce"),
       ("full",5,.5,.5,1,"Il sublime si apre")]),
}

def ffmpeg(*args):
    cmd=["ffmpeg","-hide_banner","-loglevel","error","-y"]+list(map(str,args))
    subprocess.run(cmd,check=True)

def file_url(name):
    fname=name.replace(" ","_")
    h=hashlib.md5(fname.encode("utf-8")).hexdigest()
    return "https://upload.wikimedia.org/wikipedia/commons/"+h[:1]+"/"+h[:2]+"/"+urllib.parse.quote(fname,safe="(),-._")

def download(name,dest):
    headers={"User-Agent":"ArtVisionCinema/1.0 (github.com/GGIANLUCAA/Tra-le-pagine-; Wikimedia cultural reuse)","Accept":"image/avif,image/webp,image/jpeg,image/png,*/*"}
    urls=[file_url(name),"https://commons.wikimedia.org/wiki/Special:Redirect/file/"+urllib.parse.quote(name.replace(" ","_"),safe="(),-._")]
    errors=[]
    for url in urls:
        for retry in range(3):
            try:
                r=requests.get(url,headers=headers,timeout=70)
                r.raise_for_status()
                if len(r.content)<20000: raise ValueError("artwork image unexpectedly short")
                dest.write_bytes(r.content)
                with Image.open(dest) as im:
                    im.verify()
                with Image.open(dest) as im:
                    if im.width < 900 or im.height < 800: raise ValueError("low resolution image")
                return url
            except Exception as exc:
                errors.append(str(exc)[:190])
                time.sleep(1.5*(retry+1))
    raise RuntimeError("No authentic artwork downloaded: "+"; ".join(errors))

def fonts():
    regular="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    serif="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
    return regular,serif

def cover_fit(src,box):
    sw,sh=src.size; bw,bh=box
    s=min(bw/sw,bh/sh)
    return src.resize((max(1,round(sw*s)),max(1,round(sh*s))),Image.Resampling.LANCZOS)

def crop_focus(src,cx,cy,zoom):
    sw,sh=src.size
    bw=min(sw,round(sh*(W/H)))
    bh=round(bw*(H/W))
    bw=round(bw/zoom); bh=round(bh/zoom)
    x=max(0,min(sw-bw,round(cx*sw-bw/2)))
    y=max(0,min(sh-bh,round(cy*sh-bh/2)))
    out=src.crop((x,y,x+bw,y+bh)).resize((W,H),Image.Resampling.LANCZOS)
    return out

def scene_image(src,shot,out):
    kind,seconds,cx,cy,zoom,reason=shot
    if kind=="detail":
        frame=crop_focus(src,cx,cy,zoom)
    else:
        background=crop_focus(src,.5,.5,1.01).filter(ImageFilter.GaussianBlur(42))
        background=ImageEnhance.Brightness(background).enhance(.34)
        artwork,resample=cover_fit(src,(1030,1830))
        artwork=artwork.convert("RGB")
        frame=background
        x=(W-artwork.width)//2; y=(H-artwork.height)//2
        mat=Image.new("RGB",(artwork.width+20,artwork.height+20),(15,13,17))
        frame.paste(mat,(x-10,y-10))
        frame.paste(artwork,(x,y))
    # No artificial 3D character movement: art is a genuine still painting.
    frame.convert("RGB").save(out,"JPEG",quality=93,optimize=True)

def cover_image(src,info,out):
    frame=crop_focus(src,.50,.42,1.03).convert("RGB")
    d=ImageDraw.Draw(frame,"RGBA")
    # Soft lower gradient, coherent Cinema V6-inspired series family.
    for y in range(950,H):
        alpha=round(210*((y-950)/(H-950))**1.4)
        d.rectangle((0,y,W,y+1),fill=(5,5,9,alpha))
    regular,serif=fonts()
    ft=ImageFont.truetype(regular,32)
    title=ImageFont.truetype(serif,69)
    sub=ImageFont.truetype(regular,34)
    d.text((74,118),"ARTVISION  /  CINEMA",font=ft,fill=(243,224,189,255))
    d.line((74,168,405,168),fill=(207,178,135,225),width=2)
    d.text((74,1480),info["name"],font=title,fill=(253,243,224,255),stroke_width=1,stroke_fill=(30,20,22,240))
    d.text((76,1591),info["artist"],font=sub,fill=(232,220,194,255))
    frame.save(out,"JPEG",quality=93)

def score(seconds,root,kind,tone,out):
    # Original synthesized recording: no samples, no royalty encumbrances.
    sr=24000; count=int(seconds*sr)
    audio=np.zeros(count,dtype=np.float32)
    randomizer=random.Random(root*101+len(tone))
    beat={"dread":1.05,"phantom":.82,"island":1.13,"elegy":.88,"sublime":.76}[tone]
    minor=[0,3,7,10,12]; major=[0,4,7,11,12]; scale=minor if kind=="minor" else major
    roots={"dread":[0,-2,-5,-3],"phantom":[0,3,-2,-4],"island":[0,-5,-2,0],"elegy":[0,5,-2,-4],"sublime":[0,-5,5,0]}[tone]
    basefreq=440*2**((root-69)/12)
    chord_span=beat*8
    def tone_add(st,dur,freq,gain,decay=1.0,partials=(1,.35,.11)):
        s=max(0,int(st*sr)); e=min(count,s+int(dur*sr))
        n=e-s
        if n<=0:return
        t=np.arange(n,dtype=np.float32)/sr
        attack=np.minimum(1,t/.14)
        end=np.minimum(1,(dur-t)/.4)
        env=np.maximum(0,attack*end)*np.exp(-t*decay/dur)
        v=np.zeros(n,dtype=np.float32)
        for harmonic,amp in enumerate(partials,1):
            v+=amp*np.sin(2*np.pi*freq*harmonic*t)
        audio[s:e]+=gain*v*env
    # Long harmonic beds with overlapping bowed-like clusters.
    for block in range(math.ceil(seconds/chord_span)+1):
        start=block*chord_span
        shift=roots[block%len(roots)]
        for semitone,gain in [(0,.075),(scale[1],.036),(scale[2],.049),(12,.017)]:
            tone_add(start, chord_span+beat*2,basefreq*2**((shift+semitone)/12),gain,decay=.12,partials=(1,.28,.09))
    # Piano/harp-like notes, every beat and deliberate empty beats.
    for i in range(math.ceil(seconds/beat)):
        st=i*beat
        shift=roots[(i//8)%len(roots)]
        note=scale[(i*3+i//7)%len(scale)]
        if tone=="dread" and i%4==3: continue
        freq=basefreq*2**((shift+note+24)/12)
        tone_add(st,min(2.7,beat*2.6),freq,.044 if i%4 else .062,decay=3.8,partials=(1,.34,.16,.08))
        if i%8==0:
            tone_add(st,beat*3,basefreq*2**((shift-12)/12),.085,decay=1.5,partials=(1,.17))
    # Calm swells and a meaningful climax, ending with closure not an abrupt cut.
    t=np.arange(count,dtype=np.float32)/sr
    fade=np.minimum(1,np.maximum(0,(seconds-t)/3.0))
    swell=0.69+0.31*np.sin(np.pi*np.minimum(1,t/seconds))**2
    entrance=np.minimum(1,.38+t/2)
    signal=audio*fade*swell*entrance
    # Gentle echoes: simple original delay, no downloaded samples.
    for delay,weight in [(0.19,.14),(.38,.08)]:
        k=int(delay*sr)
        signal[k:]+=audio[:-k]*weight*fade[k:]*swell[k:]*entrance[k:]
    signal=np.tanh(signal*2.2).astype(np.float32)
    peak=np.max(np.abs(signal))
    if peak: signal*=.78/peak
    stereo=np.column_stack((signal,signal)).astype(np.float32)
    with wave.open(str(out),"wb") as f:
        f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr)
        f.writeframes((stereo*32767).astype("<i2").tobytes())

def labels(info,arturl,slug,mp4,cover,durations):
    caption={
      "goya":"Non è un mostro inventato dal cinema. È uno degli incubi più celebri dipinti da Goya. Osserva come il buio cambia ciò che riusciamo a vedere.",
      "fuseli":"Un sonno, un peso sul petto e uno sguardo nascosto nel buio. Füssli trasformò l'incubo in un'immagine impossibile da dimenticare.",
      "bocklin":"Una barca avanza in silenzio verso un'isola che sembra fuori dal tempo. Böcklin rende il mistero più potente proprio evitando di spiegarlo.",
      "waterhouse":"La dama di Shalott lascia alle spalle ciò che conosce. Waterhouse concentra una storia tragica in uno sguardo, una barca e una luce fragile.",
      "friedrich":"Una persona sola davanti a un mare di nebbia. Friedrich fa del paesaggio una domanda senza parole: quanto siamo piccoli davanti all'infinito?"
    }[slug]
    return {"title":info["name"],"artist":info["artist"],"format":"ArtVision Cinema V23",
      "status":"rendered_needs_artistic_review","video":mp4.name,"cover":cover.name,
      "artwork_file":info["file"],"image_page":ROOT+urllib.parse.quote(info["file"].replace(" ","_")),
      "downloaded_image":arturl,"image_rights":"public domain artwork; check reproductions and local rules before commercial posting",
      "music":"original synthesized score from scripts/artvision_five_20261023.py; no samples",
      "copyright_music":"original composition and recording by this production script",
      "voice":False,"fps":FPS,"frame_size":[W,H],"seconds":durations,"shot_reasons":[x[5] for x in info["shots"]],
      "facebook_caption":caption+"\n\n#ArtVision #Arte #Pittura",
      "production_notes":"Free original camera animation on documented public-domain painting. No AI-invented brushwork, subtitles or speech. Publication subject to visual and licensing review."}

def make(ident,out):
    info=WORKS[ident]; out.mkdir(parents=True,exist_ok=True)
    tmp=out/("_work_"+ident); tmp.mkdir(exist_ok=True)
    srcfile=tmp/"artwork.jpg"
    url=download(info["file"],srcfile)
    src=Image.open(srcfile).convert("RGB")
    clips=[]; durations=[]
    for index,shot in enumerate(info["shots"]):
        frame=tmp/f"frame_{index:02}.jpg"
        clip=tmp/f"scene_{index:02}.mp4"
        scene_image(src,shot,frame)
        duration=shot[1]; n=round(FPS*duration); durations.append(n/FPS)
        # Motion is an extremely small, non-oscillating advance, within one shot.
        vf=f"zoompan=z='min(1.0+on*0.000003,1.006)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={n}:s={W}x{H}:fps={FPS},format=yuv420p"
        ffmpeg("-loop","1","-framerate",FPS,"-i",frame,"-vf",vf,"-frames:v",n,
               "-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p","-an",clip)
        clips.append(clip)
        print(f"[{ident}] scene {index+1}/{len(info['shots'])}: {shot[5]}",flush=True)
    files=tmp/"concat.txt"
    files.write_text("".join("file '"+str(p.resolve()).replace("'","'\\''")+"'\n" for p in clips))
    sound=tmp/"original_score.wav"
    duration=sum(durations)
    score(duration,info["root"],info["kind"],info["tone"],sound)
    mp4=out/f"ARTVISION_CINEMA_V23_{ident.upper()}_FINALE.mp4"
    ffmpeg("-f","concat","-safe","0","-i",files,"-i",sound,
           "-c:v","copy","-c:a","aac","-b:a","160k","-shortest",
           "-movflags","+faststart",mp4)
    cover=out/f"ARTVISION_CINEMA_V23_{ident.upper()}_COPERTINA.jpg"
    cover_image(src,info,cover)
    manifest=labels(info,url,ident,mp4,cover,duration)
    manifest["sha256_mp4"]=hashlib.sha256(mp4.read_bytes()).hexdigest()
    manifest["size_bytes"]=mp4.stat().st_size
    (out/f"ARTVISION_CINEMA_V23_{ident.upper()}_RECIPE.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    (out/f"ARTVISION_CINEMA_V23_{ident.upper()}_POST_FACEBOOK.txt").write_text(manifest["facebook_caption"]+"\n\nOpera: "+manifest["image_page"]+"\nMusica originale ArtVision V23.",encoding="utf-8")
    # Real frames for review; not a synthetic or AI storyboard.
    for label,position in [("START",0.5),("MIDDLE",duration/2),("END",max(.5,duration-1))]:
        ffmpeg("-ss",f"{position:.2f}","-i",mp4,"-frames:v","1","-q:v","3",
               out/f"ARTVISION_CINEMA_V23_{ident.upper()}_{label}.jpg")
    print("RENDERED",mp4,round(duration,2),"seconds",mp4.stat().st_size,"bytes",flush=True)

def main():
    p=argparse.ArgumentParser(); p.add_argument("--painting",choices=list(WORKS),required=True)
    p.add_argument("--out",default="output/artvision_v23"); a=p.parse_args()
    make(a.painting,Path(a.out))

if __name__=="__main__":main()
