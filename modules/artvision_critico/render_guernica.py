#!/usr/bin/env python3
"""Guernica — ArtVision Critico V2 (additivo). Cinema V6 e Dalí V1 restano intatti."""
from __future__ import annotations
import json, math, os, sys, time, hashlib, subprocess
from pathlib import Path
from urllib.request import Request, urlopen
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"modules"/"artvision"))
sys.path.insert(0,str(ROOT/"modules"/"artvision_critico"))
sys.path.insert(0,str(ROOT/"src"))
from identita_visiva_v6 import cover,signature
from render_dali import choose_voice, music_get, download, get_duration
W,H,FPS=1080,1920,20
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BASE=Path(__file__).with_name("guernica_picasso_v1.json")
OUT=ROOT/"output"/"picasso-guernica-critico-v1"
INK=(13,15,20); GOLD=(218,198,168); OFF=(242,237,231)

def command(args):
    print("CMD:", " ".join(map(str,args[:12])),flush=True)
    subprocess.run([str(a) for a in args],check=True)

def text_fit(d,st,maxwidth,size=50,face=FONT):
    for sz in range(size,16,-1):
        f=ImageFont.truetype(face,sz)
        if d.textbbox((0,0),st,font=f)[2]<=maxwidth:return f
    return ImageFont.truetype(face,17)

def label_center(frame,st,cy,size=50,color=OFF,face=FONT,shadow=False):
    im=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
    draw=ImageDraw.Draw(im)
    ft=text_fit(draw,st,W-125,size,face)
    bbox=draw.textbbox((0,0),st,font=ft)
    x=(W-(bbox[2]-bbox[0]))/2
    if shadow:draw.text((x+2,cy+2),st,font=ft,fill=(0,0,0))
    draw.text((x,cy),st,font=ft,fill=color)
    return cv2.cvtColor(np.array(im),cv2.COLOR_RGB2BGR)

def obtain(cfg,out):
    failures=[]
    for url in cfg["image_candidates"]:
        try:
            meta=download(url,out/"quadro.jpg")
            img=cv2.imread(str(out/"quadro.jpg"))
            ih,iw=img.shape[:2]
            if iw/ih<1.85:raise RuntimeError("Il quadro scaricato non e' panoramico: "+str((iw,ih)))
            print("GUERNICA IMAGE",iw,ih,meta["sha256"][:16],flush=True)
            return img,meta
        except Exception as e:
            print("IMAGE FALLBACK:",str(e)[:200],flush=True);failures.append(str(e))
    raise RuntimeError("Nessuna fonte verificabile: "+" | ".join(failures))

def ease(x):
    x=max(0.,min(1.,x));return x*x*(3-2*x)

def crop_window(img,focus,zoom,target_ratio):
    ih,iw=img.shape[:2]
    base_h=min(ih,iw/target_ratio)
    base_w=base_h*target_ratio
    cw=min(iw,max(2,int(base_w/zoom)));ch=min(ih,max(2,int(base_h/zoom)))
    cx=min(iw-cw/2,max(cw/2,focus[0]*iw))
    cy=min(ih-ch/2,max(ch/2,focus[1]*ih))
    patch=cv2.getRectSubPix(img,(cw,ch),(cx,cy))
    return patch, (cx-cw/2,cy-ch/2,cw,ch)

def fit(patch,tw,th):
    return cv2.resize(patch,(tw,th),interpolation=cv2.INTER_AREA if patch.shape[1]>tw else cv2.INTER_CUBIC)

def background(img):
    color=np.zeros((H,W,3),np.uint8);color[:]=INK
    low=cv2.resize(img,(120,60))
    back=cv2.resize(low,(W,H))
    back=cv2.GaussianBlur(back,(0,0),56)
    return cv2.addWeighted(color,.86,back,.14,0)

def artwork_band(img,width=966):
    ih,iw=img.shape[:2]; hh=round(width*ih/iw)
    return cv2.resize(img,(width,hh),interpolation=cv2.INTER_AREA)

def thin_frame(frame,x,y,w,h):
    cv2.rectangle(frame,(x-2,y-2),(x+w+2,y+h+2),(113,104,94),1,cv2.LINE_AA)

def draw_intro(base,img,cfg):
    f=base.copy()
    artwork=artwork_band(img,982);ah=artwork.shape[0];y=620
    f[y:y+ah,49:1031]=artwork
    thin_frame(f,49,y,982,ah)
    cv2.line(f,(172,530),(908,530),(141,134,124),1,cv2.LINE_AA)
    f=label_center(f,"IL GRIDO CHE NON SENTI",241,63)
    f=label_center(f,"GUERNICA",356,75)
    f=label_center(f,"1937 · UNA STORIA DENTRO IL QUADRO",555,26,GOLD,SANS)
    f=cover(f,cfg["artist"],cfg["music"]["composer"])
    return f

def make_panorama(base,img,title):
    f=base.copy()
    pic=artwork_band(img,990);y=560;hh=pic.shape[0]
    f[y:y+hh,45:1035]=pic
    thin_frame(f,45,y,990,hh)
    f=label_center(f,title.upper(),1082,45)
    f=label_center(f,"LO SGUARDO RITORNA ALL'INSIEME",1192,23,GOLD,SANS)
    return f

def make_gallery(base,img,beat,p):
    f=base.copy()
    iw=img.shape[1];ih=img.shape[0]
    pic=artwork_band(img,984);oh=pic.shape[0]
    top_y=248; f[top_y:top_y+oh,48:1032]=pic
    thin_frame(f,48,top_y,984,oh)
    za,zb=beat["zoom_start"],beat["zoom_end"]
    z=max(1.04,za+(zb-za)*ease(p))
    drift=.005*math.sin(p*math.pi*2)
    patch,rect=crop_window(img,(beat["focus"][0]+drift,beat["focus"][1]),z,966/740)
    # locator in panorama: outline, not an opaque shape covering the work
    x0=48+round(rect[0]*984/iw);y0=top_y+round(rect[1]*oh/ih)
    x1=48+round((rect[0]+rect[2])*984/iw);y1=top_y+round((rect[1]+rect[3])*oh/ih)
    cv2.rectangle(f,(x0,y0),(x1,y1),(178,201,219),2,cv2.LINE_AA)
    detail=fit(patch,966,740);bottom_y=752
    f[bottom_y:bottom_y+740,57:1023]=detail
    thin_frame(f,57,bottom_y,966,740)
    return f

def make_immersive(base,img,beat,p):
    f=base.copy()
    z=max(1.0,beat["zoom_start"]+(beat["zoom_end"]-beat["zoom_start"])*ease(p))
    fx=beat["focus"][0]+.007*math.sin(math.pi*2*p)
    patch,_=crop_window(img,(fx,beat["focus"][1]),z,990/1380)
    detail=fit(patch,990,1380)
    f[205:1585,45:1035]=detail
    thin_frame(f,45,205,990,1380)
    return f

def draw_brand(frame,title):
    f=frame
    cv2.line(f,(80,150),(1000,150),(131,118,91),1,cv2.LINE_AA)
    f=label_center(f,"TRA LE PAGINE  ·  ART VISION CRITICO",86,23,GOLD,SANS)
    f=label_center(f,title.upper(),1645,37,OFF,FONT)
    f=label_center(f,"PABLO PICASSO  /  GUERNICA",1780,21,GOLD,SANS)
    return f

def outro_symbols(frame,a):
    # Una firma di chiusura SOLO grafica: cuore, play con +. Niente voce o annunci.
    f=frame.copy()
    canvas=np.zeros_like(f)
    ctr_y=1800
    cv2.circle(canvas,(467,ctr_y),28,(234,225,211),2,cv2.LINE_AA)
    cv2.ellipse(canvas,(457,1796),(11,11),0,160,380,(234,225,211),2,cv2.LINE_AA)
    cv2.ellipse(canvas,(477,1796),(11,11),0,160,380,(234,225,211),2,cv2.LINE_AA)
    cv2.line(canvas,(447,1804),(467,1823),(234,225,211),2,cv2.LINE_AA)
    cv2.line(canvas,(467,1823),(487,1804),(234,225,211),2,cv2.LINE_AA)
    cv2.circle(canvas,(613,ctr_y),28,(234,225,211),2,cv2.LINE_AA)
    triangle=np.array([(605,1785),(605,1815),(627,1800)],np.int32)
    cv2.polylines(canvas,[triangle],True,(234,225,211),2,cv2.LINE_AA)
    cv2.line(canvas,(540,1800),(558,1800),(141,134,124),2,cv2.LINE_AA)
    return cv2.addWeighted(f,1.,canvas,ease(a),0)

def render(cfg,img,out,voice,secs,bounds,engine,music,proof,source):
    start=time.monotonic()
    base=background(img)
    intro=draw_intro(base,img,cfg)
    cv2.imwrite(str(out/"COPERTINA_GUERNICA_PICASSO.jpg"),intro,[cv2.IMWRITE_JPEG_QUALITY,96])
    beats=cfg["beats"];assert len(bounds)==len(beats), (len(bounds),len(beats))
    pad=2.4;tail=4.5;length=math.ceil(pad+secs+tail)
    frames=length*FPS
    video=out/"VIDEO_SENZA_AUDIO.mp4"
    ff=subprocess.Popen(["ffmpeg","-hide_banner","-loglevel","error","-y",
      "-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
      "-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",
      "-threads","2","-movflags","+faststart",str(video)],stdin=subprocess.PIPE)
    previous=None; shot=0;cached={}
    panorama_indices={0,1,2,13,14,15}
    immersive_indices={3,6,10,11,12}
    for k in range(frames):
        t=k/FPS;narr=t-pad
        while shot<len(bounds)-1 and narr>=bounds[shot]:shot+=1
        beat=beats[shot]
        lo=0 if shot==0 else bounds[shot-1];hi=bounds[shot]
        p=ease((narr-lo)/max(.2,hi-lo))
        if t<2.95: frame=intro.copy()
        elif shot in panorama_indices:
            if shot not in cached: cached[shot]=draw_brand(make_panorama(base,img,beat["title"]),beat["title"])
            frame=cached[shot].copy()
        elif shot in immersive_indices: frame=draw_brand(make_immersive(base,img,beat,p),beat["title"])
        else: frame=draw_brand(make_gallery(base,img,beat,p),beat["title"])
        # Dissolvenza leggera che evita un taglio brusco anche se cambia inquadratura.
        if previous is not None and t>3 and narr>lo and narr-lo<.65:
            opacity=ease((narr-lo)/.65)
            frame=cv2.addWeighted(previous,1-opacity,frame,opacity,0)
        # Ultimi secondi: pittura intera + invito grafico non pronunciato.
        if t>=pad+secs:
            if 15 not in cached: cached[15]=draw_brand(make_panorama(base,img,"Il quadro resta con noi"),"Il quadro resta con noi")
            frame=cached[15].copy()
            f=(t-(pad+secs))/tail
            if f>.25: frame=outro_symbols(frame,(f-.25)/.38)
            if f>.75: frame=cv2.convertScaleAbs(frame,alpha=max(0.0,1-(f-.75)/.25),beta=0)
        if k%FPS==0: previous=frame.copy()
        try:ff.stdin.write(frame.tobytes())
        except BrokenPipeError:raise RuntimeError("ffmpeg encode crashed")
        if k%(FPS*30)==0:print("Guernica render",round(t),"/",length,"seconds",flush=True)
    ff.stdin.close()
    if ff.wait()!=0:raise RuntimeError("FFmpeg video encode failed "+str(ff.returncode))
    final=out/"ARTVISION_PICASSO_GUERNICA_CRITICO_V1.mp4"
    # SINGLE continuous voice, no mid-video voice switches; music dips and fades gracefully at both ends.
    common=["ffmpeg","-hide_banner","-loglevel","error","-y","-i",video,"-i",voice]
    if music:
        common+=["-stream_loop","-1","-i",music,
          "-filter_complex",f"[1:a]adelay={int(pad*1000)}|{int(pad*1000)},volume=1.0[v];[2:a]volume=0.066,afade=t=in:st=0:d=3.0,afade=t=out:st={max(0,length-5)}:d=5[m];[v][m]amix=inputs=2:duration=first:normalize=0[a]",
          "-map","0:v:0","-map","[a]"]
    else:
        common+=["-filter_complex",f"[1:a]adelay={int(pad*1000)}|{int(pad*1000)}[a]","-map","0:v:0","-map","[a]"]
    common+=["-t",str(length),"-c:v","copy","-c:a","aac","-b:a","192k","-movflags","+faststart",final]
    command(common)
    trackmeta=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration,size:stream=codec_type,width,height","-of","json",str(final)]))
    assert {i["codec_type"] for i in trackmeta["streams"]}=={"video","audio"}
    assert abs(float(trackmeta["format"]["duration"])-length)<1
    assert final.stat().st_size>2_000_000
    report={"video":final.name,"seconds":get_duration(final),"dimensions":[W,H],"fps":FPS,
      "voice":engine,"voice_seconds":secs,"source":source,"music":proof,
      "scene_count":len(beats),"timings":[{"scene":b["title"],"from":round(pad+(0 if i==0 else bounds[i-1]),2),"to":round(pad+bounds[i],2),"focus":b["focus"]} for i,b in enumerate(beats)],
      "render_seconds":round(time.monotonic()-start),"rights":"Anteprima critica privata. Non autorizzazione automatica alla pubblicazione."}
    (out/"REGIA_E_SYNC_GUERNICA.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
    (out/"SCRIPT_CRITICO_GUERNICA.txt").write_text("\n\n".join(b["speech"] for b in beats),encoding="utf8")
    (out/"DIRITTI_FONTI_E_CREDITI.txt").write_text(
      cfg["rights_notice"]+"\n"+"\n".join(cfg["sources"])+"\nVoce: "+engine+
      "\nMusica: Night on the Docks - Piano, Kevin MacLeod, CC BY 4.0, https://creativecommons.org/licenses/by/4.0/ - loop e mix con volume ridotto.\n"+
      "Immagine fotografica: Wikimedia Commons, Pizieno, CC0 fotografo; diritto d'autore opera distinto.\n",
      encoding="utf8")
    print("MASTER GUERNICA VERIFIED",length,final.stat().st_size,engine,flush=True)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    cfg=json.loads(BASE.read_text(encoding="utf8"))
    img,source=obtain(cfg,OUT)
    voice,secs,bounds,engine=choose_voice(cfg["beats"],OUT)
    music,proof=music_get(cfg,OUT)
    if music is None:raise RuntimeError("Music absent: do not publish silent music edition")
    render(cfg,img,OUT,voice,secs,bounds,engine,music,proof,source)

if __name__=="__main__":main()
