#!/usr/bin/env python3
"""ArtVision Critico: VERMEER — racconto breve e naturale. File autonomo, i master precedenti non vengono modificati."""
from __future__ import annotations
import asyncio, hashlib, io, json, math, os, subprocess, sys, time
from pathlib import Path
from urllib.request import Request,urlopen
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"modules"/"artvision"))
sys.path.insert(0,str(ROOT/"modules"/"artvision_critico"))
sys.path.insert(0,str(ROOT/"src"))
from identita_visiva_v6 import cover as v6cover
from render_dali import choose_voice,music_get,get_duration
CFG=Path(__file__).with_name("vermeer_perla_breve_v1.json")
OUT=ROOT/"output"/"vermeer-perla-breve-v1"
W,H,FPS=1080,1920,20
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
INK=(13,15,20); IVORY=(251,247,237); GOLD=(219,193,157)
FRAME_X,FRAME_Y,FRAME_W,FRAME_H=58,252,964,1198

def proc(args):
    subprocess.run(list(map(str,args)),check=True)

def fetch_art(cfg,out):
    from urllib.parse import urlencode
    errors=[]
    candidates=[]
    # A real MediaWiki API call supplies the current thumbnail URL without guessing
    # Wikimedia's hashed upload path. This gives an exact reproducible art source.
    for width in [3200,2400,1800]:
        try:
            url="https://commons.wikimedia.org/w/api.php?"+urlencode({
              "action":"query","format":"json","prop":"imageinfo",
              "iiprop":"url","iiurlwidth":width,"titles":cfg["commons_title"]})
            req=Request(url,headers={"User-Agent":"ArtVisionCritico/1.2 (https://github.com/GGIANLUCAA/Tra-le-pagine-; noncommercial education)",
                                     "Accept":"application/json"})
            with urlopen(req,timeout=35) as r: data=json.load(r)
            for page in data["query"]["pages"].values():
                for info in page.get("imageinfo",[]):
                    candidates.append(info.get("thumburl") or info.get("url"))
            if candidates:break
        except Exception as e:
            errors.append("Wiki API: "+repr(e))
            print("API alternate source requested:",str(e)[:200],flush=True)
    candidates +=cfg["image_candidates"]
    for url in candidates:
        if not url:continue
        try:
            rq=Request(url,headers={"User-Agent":"ArtVisionCritico/1.2 (https://github.com/GGIANLUCAA/Tra-le-pagine-; educational art criticism)",
                "Referer":"https://commons.wikimedia.org/"})
            with urlopen(rq,timeout=90) as r:
                typ=r.headers.get("Content-Type","")
                if "image" not in typ and "octet-stream" not in typ:
                    raise ValueError("Not an image: "+typ)
                data=r.read(33_000_000)
            if not 150_000<len(data)<33_000_000:
                raise ValueError("Bad image byte count "+str(len(data)))
            with Image.open(io.BytesIO(data)) as im:photo=ImageOps.exif_transpose(im).convert("RGB")
            if min(photo.size)<1200:raise ValueError("Too small: "+str(photo.size))
            ratio=photo.width/photo.height
            if not .77<ratio<.92:raise ValueError("Wrong art aspect: "+str(photo.size))
            if max(photo.size)>4600:photo.thumbnail((4600,4600),Image.Resampling.LANCZOS)
            imgpath=out/"VERMEER_QUADRO_SORGENTE.jpg"
            photo.save(imgpath,quality=95,subsampling=0)
            print("SOURCE VERIFIED",photo.size,url,hashlib.sha256(data).hexdigest(),flush=True)
            return cv2.imread(str(imgpath)),{"url":url,"size":photo.size,"sha256":hashlib.sha256(data).hexdigest()}
        except Exception as e:
            errors.append(repr(e))
            print("Alternate artwork failed:",repr(e)[:350],flush=True)
    raise RuntimeError("No valid high-resolution painting source: "+"; ".join(errors))

def alpha(x):
    q=min(1.,max(0.,x))
    return q*q*(3-2*q)

def write_on(img,st,y,size=42,col=IVORY,font=FONT):
    original=Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
    d=ImageDraw.Draw(original)
    for pt in range(size,17,-1):
        f=ImageFont.truetype(font,pt)
        length=d.textbbox((0,0),st,font=f)[2]
        if length<W-140:break
    x=(W-length)//2
    d.text((x,y),st,font=f,fill=col)
    return cv2.cvtColor(np.asarray(original),cv2.COLOR_RGB2BGR)

def dark_canvas(img):
    tiny=cv2.resize(img,(120,155),interpolation=cv2.INTER_AREA)
    blur=cv2.resize(tiny,(W,H),interpolation=cv2.INTER_LINEAR)
    blur=cv2.GaussianBlur(blur,(0,0),60)
    black=np.zeros((H,W,3),np.uint8);black[:]=INK
    return cv2.addWeighted(black,.84,blur,.16,0)

def brand_template(art,small_title):
    # Light editorial layout: no chapter title, no 'Tra le Pagine' banner.
    frame=dark_canvas(art)
    cv2.line(frame,(125,165),(955,165),(117,111,104),1,cv2.LINE_AA)
    frame=write_on(frame,"ART VISION  ·  CRITICA D'ARTE",104,23,GOLD,SANS)
    frame=write_on(frame,"JOHANNES VERMEER   ·   1665",1615,26,IVORY,FONT)
    cv2.line(frame,(170,1682),(910,1682),(102,113,128),1,cv2.LINE_AA)
    return frame

def crop_center(art,focus,zoom):
    ih,iw=art.shape[:2];ar=FRAME_W/FRAME_H
    h=min(ih,iw/ar);w=h*ar
    zw=max(2,round(w/zoom));zh=max(2,round(h/zoom))
    cx=min(iw-zw/2,max(zw/2,focus[0]*iw))
    cy=min(ih-zh/2,max(zh/2,focus[1]*ih))
    patch=cv2.getRectSubPix(art,(zw,zh),(cx,cy))
    return cv2.resize(patch,(FRAME_W,FRAME_H),interpolation=cv2.INTER_AREA if zw>FRAME_W else cv2.INTER_CUBIC)

def scene_frame(art,beat,p,base):
    frame=base.copy()
    # Filmic micro-drift; camera stays precisely on the object narrated.
    z=beat["zoom_start"]+(beat["zoom_end"]-beat["zoom_start"])*alpha(p)
    focus=(beat["focus"][0]+.007*math.sin(p*math.pi),beat["focus"][1]-.004*math.sin(p*math.pi))
    if z<1.015:focus=(.5,.5)
    image=crop_center(art,focus,z)
    frame[FRAME_Y:FRAME_Y+FRAME_H,FRAME_X:FRAME_X+FRAME_W]=image
    cv2.rectangle(frame,(FRAME_X-3,FRAME_Y-3),(FRAME_X+FRAME_W+3,FRAME_Y+FRAME_H+3),(142,126,106),1,cv2.LINE_AA)
    return frame

def opening(art,cfg):
    frame=dark_canvas(art)
    frame=write_on(frame,"ART VISION  ·  CRITICA D'ARTE",116,24,GOLD,SANS)
    frame=write_on(frame,"E SE NON FOSSE",252,57,IVORY,FONT)
    frame=write_on(frame,"UNA PERLA?",326,65,IVORY,FONT)
    cv2.line(frame,(172,440),(908,440),(110,117,123),1,cv2.LINE_AA)
    ih,iw=art.shape[:2];hh=1110;ww=round(hh*iw/ih)
    pic=cv2.resize(art,(ww,hh),interpolation=cv2.INTER_AREA)
    x=(W-ww)//2;y=465
    frame[y:y+hh,x:x+ww]=pic
    cv2.rectangle(frame,(x-3,y-3),(x+ww+3,y+hh+3),(145,127,104),1,cv2.LINE_AA)
    # Essential: V6 band typography/palette remain identical to earlier videos.
    frame=v6cover(frame,cfg["artist"],cfg["music"]["composer"])
    return frame

def end_icons(frame,percent):
    # Silent, minimal like + subscribe symbols, not speech or loud call to action.
    im=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)).convert("RGBA")
    layer=Image.new("RGBA",(W,H),(0,0,0,0))
    d=ImageDraw.Draw(layer)
    a=round(255*alpha(percent))
    fg=(232,219,198,a); faded=(151,133,112,round(a*.7))
    # Outline heart, classic restrained sign for like.
    d.arc((450,1740,480,1770),180,360,fill=fg,width=3)
    d.arc((480,1740,510,1770),180,360,fill=fg,width=3)
    d.line(((450,1755),(480,1790),(510,1755)),fill=fg,width=3,joint="curve")
    d.ellipse((581,1736,644,1799),outline=fg,width=3)
    d.polygon([(607,1751),(607,1784),(628,1767)],outline=fg)
    d.line((544,1768,564,1768),fill=faded,width=2)
    return cv2.cvtColor(np.asarray(Image.alpha_composite(im,layer).convert("RGB")),cv2.COLOR_RGB2BGR)

def render(cfg,art,src,voice,vsecs,bounds,engine,music,proof,out):
    beats=cfg["beats"]
    assert len(bounds)==len(beats),"Speech-scene alignment mismatch"
    pad=2.3;tail=4.2;length=math.ceil(pad+vsecs+tail)
    intro=opening(art,cfg)
    cv2.imwrite(str(out/"COPERTINA_VERMEER_PERLA.jpg"),intro,[cv2.IMWRITE_JPEG_QUALITY,96])
    templates=[brand_template(art,b["title"]) for b in beats]
    final_template=brand_template(art,"UNO SGUARDO CHE RESTA")
    silent=out/"VIDEO_BASE.mp4"
    ff=subprocess.Popen(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo",
      "-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
      "-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",
      "-threads","2","-movflags","+faststart",str(silent)],stdin=subprocess.PIPE)
    current=0;last_index=-1;previous_frame=None;transition_origin=None;transition_at=0
    print("PRODUCTION",len(beats),"scenes",round(vsecs,2),"voice seconds",length,"video seconds",flush=True)
    total=length*FPS
    for k in range(total):
        t=k/FPS
        vocal=t-pad
        while current<len(bounds)-1 and vocal>=bounds[current]:current+=1
        if current!=last_index:
            transition_origin=previous_frame.copy() if previous_frame is not None else None
            transition_at=t;last_index=current
        start=0 if current==0 else bounds[current-1]
        end=bounds[current]
        progress=(vocal-start)/max(.2,end-start)
        if t<3.1:
            frame=intro.copy()
        elif t>=pad+vsecs:
            frame=scene_frame(art,{"focus":[.5,.5],"zoom_start":1.,"zoom_end":1.},0,final_template)
            percent=(t-(pad+vsecs))/tail
            frame=end_icons(frame,(percent-.11)/.33)
            if percent>.77:frame=cv2.convertScaleAbs(frame,alpha=max(.0,1-(percent-.77)/.23),beta=0)
        else:
            frame=scene_frame(art,beats[current],progress,templates[current])
            if transition_origin is not None and t-transition_at<.85:
                blend=alpha((t-transition_at)/.85)
                frame=cv2.addWeighted(transition_origin,1-blend,frame,blend,0)
        try:ff.stdin.write(frame.tobytes())
        except BrokenPipeError:raise RuntimeError("FFmpeg raw video pipeline ended")
        previous_frame=frame
        if k%(FPS*25)==0:print("FILM",round(t),"/",length,flush=True)
    ff.stdin.close()
    if ff.wait()!=0:raise RuntimeError("Failed video encode, rc="+str(ff.returncode))
    master=out/"ARTVISION_VERMEER_PERLA_CRITICO_BREVE_V1.mp4"
    # No narrator changes; single continuous Gacrux performance; slow music fades.
    args=["ffmpeg","-hide_banner","-loglevel","error","-y",
        "-i",silent,"-i",voice,"-stream_loop","-1","-i",music,
        "-filter_complex",
        f"[1:a]adelay={int(pad*1000)}|{int(pad*1000)},volume=1.0[v];"+
        f"[2:a]volume=0.062,afade=t=in:st=0:d=3.5,afade=t=out:st={max(0,length-5.5)}:d=5.5[m];"+
        "[v][m]amix=inputs=2:duration=longest:normalize=0[a]",
        "-map","0:v:0","-map","[a]","-t",str(length),"-c:v","copy",
        "-c:a","aac","-b:a","192k","-movflags","+faststart",master]
    proc(args)
    meta=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries",
      "format=duration,size:stream=codec_type,width,height","-of","json",str(master)]))
    assert {s["codec_type"] for s in meta["streams"]}=={"video","audio"}
    assert abs(float(meta["format"]["duration"])-length)<1
    assert (next(s for s in meta["streams"] if s["codec_type"]=="video")["width"],next(s for s in meta["streams"] if s["codec_type"]=="video")["height"])==(W,H)
    assert master.stat().st_size>10_000_000
    scene_meta=[{"id":b["id"],"title":b["title"],"from":round(pad+(0 if i==0 else bounds[i-1]),2),
       "to":round(pad+bounds[i],2),"focus":b["focus"],"zoom_start":b["zoom_start"],"zoom_end":b["zoom_end"]} for i,b in enumerate(beats)]
    (out/"REGIA_E_SYNC.json").write_text(json.dumps({"video":master.name,"seconds":length,
       "voice":engine,"voice_seconds":vsecs,"source":src,"music":proof,"scenes":scene_meta},ensure_ascii=False,indent=2),encoding="utf8")
    (out/"COPIONE.txt").write_text("\n\n".join(b["speech"] for b in beats),encoding="utf8")
    (out/"FONTI_DIRITTI_MUSICA.txt").write_text(
      "Opera: Johannes Vermeer, La ragazza con l'orecchino di perla (c. 1665), Mauritshuis, L'Aia. Originale nel pubblico dominio.\n"+
      "Riproduzione fotografica: "+cfg["source_page"]+" — Wikimedia Commons PD-Art; controllare sempre le condizioni di riuso nel paese destinazione.\n"+
      "FONTI ANALISI:\n"+"\n".join(cfg["sources"])+"\n"+
      "Musica: Night on the Docks - Piano, Kevin MacLeod (incompetech.com) CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/ . "+
      "Loop, taglio, volume ridotto e fade. https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100135\n"+
      "Voce: "+engine+"\nNessuna pubblicazione automatica sui social.\n",encoding="utf8")
    print("VERMEER MASTER VERIFIED",length,"seconds",master.stat().st_size,"bytes",engine,flush=True)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    cfg=json.loads(CFG.read_text(encoding="utf8"))
    art,src=fetch_art(cfg,OUT)
    voice,duration,bounds,engine=choose_voice(cfg["beats"],OUT)
    music,proof=music_get(cfg,OUT)
    if music is None:raise RuntimeError("Audio musicale verificato non disponibile")
    render(cfg,art,src,voice,duration,bounds,engine,music,proof,OUT)

if __name__=="__main__":main()
