#!/usr/bin/env python3
"""ArtVision Critico V1: film educativo Dalí. Modulo ADITIVO, non altera Cinema V6.
Prova privata: l'immagine è protetta da copyright; non pubblicare automaticamente.
"""
from __future__ import annotations
import argparse, asyncio, hashlib, io, json, math, os, re, subprocess, sys, time
from pathlib import Path
from urllib.request import Request, urlopen
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "modules" / "artvision"))
sys.path.insert(0, str(ROOT / "src"))
from identita_visiva_v6 import signature, cover

W, H, FPS = 1080, 1920, 20
OUT = ROOT / "output" / "dali-critico-v1"
SETTINGS = Path(__file__).with_name("dali_sogno_ape.json")

def cmd(args):
    print("RUN:", " ".join(map(str,args[:8])), flush=True)
    subprocess.run(list(map(str,args)), check=True)

def get_duration(media):
    d = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration",
                                 "-of","default=noprint_wrappers=1:nokey=1",str(media)])
    return float(d.decode().strip())

def download(url, target, limit=42_000_000):
    req = Request(url, headers={"User-Agent":"Mozilla/5.0 (compatible; ArtVisionCriticalReview/1.0)",
                                "Referer": "https://www.museothyssen.org/"})
    with urlopen(req, timeout=60) as resp:
        typ=resp.headers.get("Content-Type","")
        if "text/html" in typ: raise ValueError("HTML instead of image")
        data=resp.read(limit + 1)
    if len(data)<50_000 or len(data)>limit: raise ValueError("Source too small or exceeds 42 MB")
    with Image.open(io.BytesIO(data)) as image:
        photo=ImageOps.exif_transpose(image).convert("RGB")
    if min(photo.size)<950: raise ValueError(f"Source resolution inadequate: {photo.size}")
    if max(photo.size)>5200: photo.thumbnail((5200,5200),Image.Resampling.LANCZOS)
    target.parent.mkdir(parents=True,exist_ok=True)
    photo.save(target,quality=96,subsampling=0)
    return {"url":url,"width":photo.width,"height":photo.height,
            "sha256":hashlib.sha256(target.read_bytes()).hexdigest()}

def load_art(cfg, out):
    p=out/"quadro_sorgente.jpg"
    failures=[]
    for url in cfg["image_candidates"]:
        try:
            meta=download(url,p)
            print("ARTWORK VERIFIED",meta,flush=True)
            return cv2.imread(str(p),cv2.IMREAD_COLOR),meta
        except Exception as e:
            failures.append(str(e))
            print("Image candidate failed:",str(e)[:250],flush=True)
    raise RuntimeError("Nessuna riproduzione ad alta risoluzione accessibile: "+"; ".join(failures))

def audio_gemini(beats,out):
    from gemini_voice import synthesize, sentences
    # Recitazione CONTINUA: una sola timbrica, pausa tra paragrafi.
    script="\n\n".join(b["speech"] for b in beats)
    samples,timed=synthesize(script,out)
    duration=len(samples)/24000
    counts=[len(sentences(b["speech"])) for b in beats]
    boundaries=[]
    if len(timed)==sum(counts):
        idx=0
        for n in counts:
            idx+=n
            boundaries.append(min(duration,float(timed[idx-1][2])))
        if any(boundaries[i]<=boundaries[i-1] for i in range(1,len(boundaries))):
            boundaries=[]
    if not boundaries:
        weights=[max(10,len(re.findall(r"\w+",b["speech"]))) for b in beats]
        c=0
        boundaries=[]
        for x in weights:
            c+=x
            boundaries.append(duration*c/sum(weights))
    return out/"VOCE.wav",duration,boundaries,"Gemini Gacrux (Google)"

async def audio_edge(beats,out):
    # Fallback senza crediti aggiuntivi. Non spacciare la voce sintetica per umana.
    import edge_tts
    wavs=[]
    for i, beat in enumerate(beats):
        mp3=out/f"edge_{i:02}.mp3"
        for trial in range(3):
            try:
                await edge_tts.Communicate(beat["speech"],voice="it-IT-DiegoNeural",
                    rate="-4%",pitch="-2Hz").save(str(mp3))
                if mp3.stat().st_size<2000: raise IOError("empty voice")
                break
            except Exception:
                if trial==2:raise
                await asyncio.sleep(2*(trial+1))
        wav=out/f"edge_{i:02}.wav"
        cmd(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",mp3,
             "-ar","24000","-ac","1",wav])
        wavs.append(wav)
    import soundfile as sf
    arrays=[]
    boundaries=[]
    cursor=0.0
    for wav in wavs:
        sig,sr=sf.read(str(wav),dtype="float32")
        if sig.ndim>1: sig=sig.mean(axis=1)
        arrays.append(sig)
        cursor+=len(sig)/sr
        boundaries.append(cursor)
        arrays.append(np.zeros(int(.28*sr),dtype="float32"))
        cursor+=.28
    samples=np.concatenate(arrays)
    voice=out/"VOCE.wav"
    sf.write(str(voice),samples,24000)
    return voice,len(samples)/24000,boundaries,"Microsoft Edge Italian Neural (fallback)"

def choose_voice(beats,out):
    if os.getenv("GEMINI_API_KEY","").strip():
        try:
            return audio_gemini(beats,out)
        except Exception as e:
            print("Gemini failed, trying Edge neural:",repr(e),flush=True)
    return asyncio.run(audio_edge(beats,out))

def music_get(cfg,out):
    url=cfg["music"]["download"]
    p=out/"musica_autorizzata.mp3"
    try:
        req=Request(url,headers={"User-Agent":"Mozilla/5.0"})
        with urlopen(req,timeout=50) as r:
            data=r.read(22_000_000)
        if len(data)<150000 or data[:15].lower().startswith(b"<!doctype"):
            raise RuntimeError("invalid music response")
        p.write_bytes(data)
        length=get_duration(p)
        if length<45: raise RuntimeError("Track shorter than 45 seconds")
        return p, {"url":url, "seconds":length,"sha256":hashlib.sha256(data).hexdigest()}
    except Exception as exc:
        # Nessuna licenza inventata; il risultato resta completo con sola voce.
        print("Music unavailable, voice-only soundtrack:",str(exc),flush=True)
        return None,{"status":"unavailable; voice only"}

def bg_blurred(original):
    low=cv2.resize(original,(W//8,H//8),interpolation=cv2.INTER_AREA)
    canvas=cv2.resize(low,(W,H),interpolation=cv2.INTER_LINEAR)
    canvas=cv2.GaussianBlur(canvas,(0,0),35)
    return cv2.addWeighted(canvas,.45,np.zeros_like(canvas),.55,0)

def whole(img,bg):
    sh,sw=img.shape[:2]
    scale=min((W-90)/sw,(H-185)/sh)
    w,h=max(1,round(sw*scale)),max(1,round(sh*scale))
    resized=cv2.resize(img,(w,h),interpolation=cv2.INTER_AREA if scale<1 else cv2.INTER_CUBIC)
    x,y=(W-w)//2,(H-h)//2
    frame=bg.copy()
    cv2.rectangle(frame,(x-5,y-5),(x+w+5,y+h+5),(10,12,17),-1)
    frame[y:y+h,x:x+w]=resized
    return frame

def ease(p):
    q=min(1.,max(0.,p))
    return q*q*(3-2*q)

def crop(img,focus,zoom):
    ih,iw=img.shape[:2]
    basew=min(iw,ih*W/H)
    baseh=basew*H/W
    cw=max(2,min(iw,round(basew/zoom)))
    ch=max(2,min(ih,round(baseh/zoom)))
    cx=min(iw-cw/2,max(cw/2,focus[0]*iw))
    cy=min(ih-ch/2,max(ch/2,focus[1]*ih))
    pic=cv2.getRectSubPix(img,(cw,ch),(cx,cy))
    return cv2.resize(pic,(W,H),interpolation=cv2.INTER_AREA if cw>W else cv2.INTER_CUBIC)

def draw_upper_cover(frame):
    im=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)).convert("RGBA")
    mask=Image.new("RGBA",im.size,(0,0,0,0))
    d=ImageDraw.Draw(mask)
    # Non toccare la firma visiva fissa di V6 in basso.
    text="IL SOGNO DI UN'APE"
    ft=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",52)
    bb=d.textbbox((0,0),text,font=ft)
    x=(W-(bb[2]-bb[0]))//2
    d.rounded_rectangle((80,165,W-80,286),radius=9,fill=(5,8,13,165))
    d.text((x,194),text,font=ft,fill=(255,251,243,255))
    return cv2.cvtColor(np.asarray(Image.alpha_composite(im,mask).convert("RGB")),cv2.COLOR_RGB2BGR)

def render(cfg,img,voice,voicelen,bounds,engine,out,music,metadata,music_proof):
    beats=cfg["beats"]
    pad=2.4
    length=math.ceil(voicelen+pad+2.1)
    total_frames=math.ceil(length*FPS)
    original_whole=whole(img,bg_blurred(img))
    cover_img=draw_upper_cover(cover(original_whole.copy(),cfg["artist"],cfg["music"]["composer"]))
    cv2.imwrite(str(out/"COPERTINA_DALI_CRITICO.jpg"),cover_img,[cv2.IMWRITE_JPEG_QUALITY,96])
    silent=out/"silenziato.avi"
    writer=cv2.VideoWriter(str(silent),cv2.VideoWriter_fourcc(*"MJPG"),FPS,(W,H))
    if not writer.isOpened(): raise RuntimeError("VideoWriter non disponibile")
    schedule=[]
    prev=0.
    for i,beat in enumerate(beats):
        end=bounds[i]
        start=prev; prev=end
        if i==0: start=0
        schedule.append({"id":beat["id"],"titolo":beat["title"],"inizio":round(pad+start,2),
                         "fine":round(pad+end,2),"focus":beat["focus"],
                         "zoom":[beat["zoom_start"],beat["zoom_end"]]})
    print("Shots",len(schedule),"runtime",length,"seconds",flush=True)
    shot=0
    start=time.monotonic()
    try:
        for k in range(total_frames):
            t=k/FPS
            narr=max(0,t-pad)
            while shot<len(bounds)-1 and narr>=bounds[shot]:
                shot+=1
            beat=beats[shot]
            lo=0 if shot==0 else bounds[shot-1]
            hi=bounds[shot]
            frac=ease((narr-lo)/max(.1,hi-lo))
            if beat["zoom_start"]==1.0 and beat["zoom_end"]==1.0:
                frame=original_whole.copy()
            else:
                za,zb=beat["zoom_start"],beat["zoom_end"]
                focus=beat["focus"]
                # Diverse angolazioni coerenti all'oggetto spiegato.
                drift=.009*math.sin(frac*math.pi*2)
                zoom=za+(zb-za)*frac
                frame=crop(img,(min(.97,focus[0]+drift),focus[1]),zoom)
            if t < 3.5:
                frame=signature(frame,t,cfg["artist"],cfg["music"]["composer"])
            if shot>=len(beats)-1 and t>length-1.8:
                alpha=max(0.,min(1.,(length-t)/1.8))
                frame=cv2.convertScaleAbs(frame,alpha=alpha,beta=0)
            writer.write(frame)
            if k%(FPS*40)==0:print("Rendered",round(t),"of",length,"s",flush=True)
    finally:
        writer.release()
    mixed=out/"ARTVISION_DALI_SOGNO_DELL_APE_CRITICO_V1.mp4"
    # La voce deve restare dominante; sottofondo CC BY continuo, unico brano.
    args=["ffmpeg","-hide_banner","-loglevel","error","-y","-i",silent,"-i",voice]
    if music:
        args+=["-stream_loop","-1","-i",music,
               "-filter_complex",f"[1:a]adelay={round(pad*1000)}|{round(pad*1000)},volume=1.0[v];[2:a]volume=0.075,afade=t=in:st=0:d=2.5[mu];[v][mu]amix=inputs=2:duration=longest:dropout_transition=0[a]",
               "-map","0:v:0","-map","[a]"]
    else:
        args+=["-filter_complex",f"[1:a]adelay={round(pad*1000)}|{round(pad*1000)}[a]",
               "-map","0:v:0","-map","[a]"]
    args+=["-t",str(length),"-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",
           "-r",str(FPS),"-c:a","aac","-b:a","192k","-movflags","+faststart",mixed]
    cmd(args)
    report={"status":"private_preview_not_for_publication","video":mixed.name,
            "seconds":get_duration(mixed),"resolution":[W,H],"fps":FPS,
            "audio_engine":engine,"artwork":metadata,"music":music_proof,
            "voice_seconds":voicelen,"beats":schedule,"elapsed_render_s":round(time.monotonic()-start)}
    (out/"REGIA_DETTAGLI_E_SYNC.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    (out/"SCRIPT_CRITICO.txt").write_text("\n\n".join(b["speech"] for b in beats),encoding="utf-8")
    (out/"DIRITTI_E_CREDITI.txt").write_text(
        "ANTEPRIMA PRIVATA, NON PUBBLICARE SENZA VERIFICA DIRITTI DELL'OPERA.\n"
        "Opera: Salvador Dalí, Un secondo prima del risveglio da un sogno causato dal volo di un'ape intorno a una melagrana.\n"
        "© Salvador Dalí, Fundació Gala-Salvador Dalí / VEGAP; Museo Thyssen-Bornemisza Madrid.\n"
        "La riproduzione non è dichiarata libera: chiedere permesso ai titolari o verificare eccezioni per critica applicabili.\n"
        "Datazioni: Fondazione Dalí c.1944, Museo Thyssen 1947.\n"
        f"Voce: {engine}.\n"
        "Musica: Night on the Docks - Piano di Kevin MacLeod (incompetech.com), CC BY 4.0; "
        "https://creativecommons.org/licenses/by/4.0/ — taglio, loop, volume sotto narrazione.\n"
        "Pagina ufficiale: https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100135\n"
        "Fuori campo e storyboard originali. Nessuna pubblicazione automatica.\n",
        encoding="utf-8")
    print("FILM COMPLETED",mixed,len(schedule),"beats",flush=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",default=str(OUT))
    args=p.parse_args()
    out=Path(args.out)
    out.mkdir(parents=True,exist_ok=True)
    cfg=json.loads(SETTINGS.read_text(encoding="utf-8"))
    img,source=load_art(cfg,out)
    voice,duration,bounds,engine=choose_voice(cfg["beats"],out)
    background,music_proof=music_get(cfg,out)
    render(cfg,img,voice,duration,bounds,engine,out,background,source,music_proof)

if __name__=="__main__":
    main()
