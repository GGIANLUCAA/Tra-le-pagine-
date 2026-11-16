#!/usr/bin/env python3
"""ArtVision Critico / Cinema Series V2: batch four public-domain artwork episodes.
Additive engine: NEVER modifies ArtVision V6, books, Dalí, Picasso, Munch, Vermeer.
One shared universal cover: artwork title (localizable) + artist, NO Italian captions.
"""
from __future__ import annotations
import argparse, hashlib, io, json, math, os, re, subprocess, sys, time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"modules"/"artvision_critico"))
sys.path.insert(0,str(ROOT/"src"))
from render_dali import choose_voice, music_get
W,H,FPS=1080,1920,24
RX0,RY0,RX1,RY1=56,235,1024,1665
PARENT=Path(__file__).parent
FONTS={
 "display":"/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
 "sans":"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
}
INK=(13,15,21);GOLD=(218,198,168);IVORY=(248,244,236)
COLOR_TITLE=(250,246,241)
DRAW_FONT=FONTS["display"]
OUTROOT=ROOT/"output"/"artvision-serie-quattro"

def run(args):
    subprocess.run([str(a) for a in args],check=True)

def fps_seconds(path):
    return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=noprint_wrappers=1:nokey=1",str(path)]).decode().strip())

def check_image(cfg,im):
    ratio=im.width/im.height
    if min(im.size)<1150:raise ValueError("Insufficient resolution "+str(im.size))
    if not cfg["image_ratio_min"]<ratio<cfg["image_ratio_max"]:
        raise ValueError("Wrong painting crop/aspect ratio "+str(im.size)+" ratio "+str(ratio))
    return ratio

def get_art(cfg,out):
    title=cfg["commons_title"]
    # Gli zoom molto stretti hanno bisogno del file originale a piena
    # risoluzione: il thumbnailer Wikimedia qui si ferma a 3840 px, quindi per
    # gli episodi che richiedono il massimo dettaglio si prova prima l'upload
    # originale (con fallback automatico ai thumbnail se e' troppo pesante).
    prefer_original=bool(cfg.get("source_prefer_original"))
    limit=6000 if prefer_original else 4300
    urls=[]
    # Wikimedia API resolves exact upload filename and correct SHA directory.
    for thumb in (3600,3000,2200):
        query=urlencode({"action":"query","format":"json","prop":"imageinfo",
          "iiprop":"url","iiurlwidth":thumb,"titles":title})
        api=cfg.get("commons_imageinfo_url","https://commons.wikimedia.org/w/api.php")+"?"+query
        try:
            req=Request(api,headers={"User-Agent":"ArtVisionCriticoSeries/2.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-; educational project)","Accept":"application/json"})
            with urlopen(req,timeout=35) as resp:
                j=json.load(resp)
            for page in j.get("query",{}).get("pages",{}).values():
                for row in page.get("imageinfo",[]):
                    for key in (("url","thumburl") if prefer_original else ("thumburl","url")):
                        if row.get(key) and row[key] not in urls:urls.append(row[key])
            if urls:break
        except Exception as e:print("Image API retry",repr(e)[:170],flush=True)
    filename=title.removeprefix("File:")
    urls.append("https://commons.wikimedia.org/wiki/Special:Redirect/file/"+quote(filename,safe="")+"?width=3200")
    errors=[]
    for u in urls:
        try:
            r=Request(u,headers={"User-Agent":"ArtVisionCriticoSeries/2.0 (educational art analysis; https://github.com/GGIANLUCAA/Tra-le-pagine-)","Referer":"https://commons.wikimedia.org/"})
            with urlopen(r,timeout=100) as h:
                typ=h.headers.get("Content-Type","")
                if not typ.startswith("image/") and "octet-stream" not in typ:
                    raise ValueError("Not image: "+typ)
                buf=h.read(35_000_000)
            if not 170000<len(buf)<35_000_000:raise ValueError("Bad byte count "+str(len(buf)))
            with Image.open(io.BytesIO(buf)) as img:
                painting=ImageOps.exif_transpose(img).convert("RGB")
            ratio=check_image(cfg,painting)
            if max(painting.size)>limit:painting.thumbnail((limit,limit),Image.Resampling.LANCZOS)
            p=out/"ARTWORK_SOURCE.jpg";painting.save(p,quality=95,subsampling=0)
            print("PAINTING VERIFIED:",cfg["artist"],painting.size,"ratio",round(ratio,3),u,flush=True)
            return cv2.imread(str(p)),{"url":u,"width":painting.width,"height":painting.height,"sha256":hashlib.sha256(buf).hexdigest()}
        except Exception as e:
            print("Artwork candidate failed:",repr(e)[:240],flush=True)
            errors.append(repr(e))
    raise RuntimeError("No authentic sufficiently high-resolution image: "+"; ".join(errors))

def backdrop(art):
    thumb=cv2.resize(art,(124,90),interpolation=cv2.INTER_AREA)
    blur=cv2.resize(thumb,(W,H),interpolation=cv2.INTER_LINEAR)
    blur=cv2.GaussianBlur(blur,(0,0),64)
    flat=np.zeros((H,W,3),np.uint8);flat[:]=INK
    return cv2.addWeighted(flat,.86,blur,.14,0)

def small_smooth(x):
    q=min(1.,max(0.,x));return q*q*(3-2*q)

def push(x):
    # Carellata da cinema: un brevissimo respiro d'avvio (nessuno strappo sul
    # taglio), poi la spinta decisa del "Zum" che copre gran parte della
    # distanza, quindi una planata che posa il dettaglio al centro. Velocita'
    # massima all'inizio, nulla all'ultimo fotogramma: mai fermate di colpo.
    q=min(1.,max(0.,x))
    lead=small_smooth(min(1.,q/.12))
    dash=1-(1-q)**2.0
    return .12*lead+.88*dash

def font_to_fit(draw,st,maxw,maxsize,minsize=22,face=DRAW_FONT):
    for pts in range(maxsize,minsize-1,-1):
        f=ImageFont.truetype(face,pts)
        b=draw.textbbox((0,0),st,font=f)
        if b[2]-b[0]<=maxw:return f
    return ImageFont.truetype(face,minsize)

def multiline_title(draw,title):
    # Preserve a true shared cover layout. No episode-specific bait words.
    words=title.upper().split()
    if len(words)<3:return [title.upper()]
    lines=[];line=""
    for word in words:
        candidate=(line+" "+word).strip()
        f=font_to_fit(draw,candidate,870,87,62)
        width=draw.textbbox((0,0),candidate,font=f)[2]
        if width>745 and line and len(lines)<2:
            lines.append(line);line=word
        else:line=candidate
    if line:lines.append(line)
    if len(lines)>2:return [title.upper()]
    return lines

def cover_universal(art,cfg):
    # 1080×1920: identical title region, framed authentic painting, same artist zone.
    frame=backdrop(art)
    ih,iw=art.shape[:2]
    image_ar=iw/ih
    # Wide paintings in identical 990-wide bounding viewport; square/portrait fill maximum.
    mw,mh=960,1080
    sc=min(mw/iw,mh/ih)
    pw,ph=max(1,round(iw*sc)),max(1,round(ih*sc))
    resized=cv2.resize(art,(pw,ph),interpolation=cv2.INTER_AREA if sc<1 else cv2.INTER_CUBIC)
    x=(W-pw)//2
    y=535+(1080-ph)//2
    frame[y:y+ph,x:x+pw]=resized
    cv2.rectangle(frame,(x-3,y-3),(x+pw+3,y+ph+3),(140,125,103),2,cv2.LINE_AA)
    canvas=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
    d=ImageDraw.Draw(canvas)
    # canvas è già in RGB: i colori di progetto sono in RGB (vedi INK/GOLD/IVORY
    # e index.html), quindi vanno passati diretti. L'oro resta oro.
    gold=GOLD;ivory=IVORY
    d.line((157,193,923,193),fill=gold,width=2)
    title=cfg["artwork"].upper()
    # Uniform cover: always centered in same title area with slightly enlarged
    # typography relative to prior approved versions.
    lines=multiline_title(d,title)
    size=92 if len(lines)==1 else 81
    for i,line in enumerate(lines):
        ft=font_to_fit(d,line,910,size,44)
        bounds=d.textbbox((0,0),line,font=ft)
        width=bounds[2]-bounds[0]
        d.text(((W-width)/2,249+i*109),line,font=ft,fill=ivory,
               stroke_width=1,stroke_fill=(25,24,22))
    d.line((182,1683,898,1683),fill=gold,width=2)
    artist=cfg["artist"].upper()
    font=font_to_fit(d,artist,900,52,33)
    w=d.textbbox((0,0),artist,font=font)[2]
    d.text(((W-w)/2,1737),artist,font=font,fill=ivory)
    d.line((385,1831,695,1831),fill=gold,width=2)
    return cv2.cvtColor(np.asarray(canvas),cv2.COLOR_RGB2BGR)

def full_art(frame,art):
    ih,iw=art.shape[:2];sc=min(970/iw,1495/ih)
    sw,sh=max(2,int(iw*sc)),max(2,int(ih*sc))
    image=cv2.resize(art,(sw,sh),interpolation=cv2.INTER_AREA if sc<1 else cv2.INTER_CUBIC)
    x=(W-sw)//2;y=215+(1495-sh)//2
    frame[y:y+sh,x:x+sw]=image
    return frame

def crop_into(patch,art,fx,fy,zoom,ratio):
    # Ritaglia il quadro centrando ESATTAMENTE il proverbio raccontato, anche
    # quando è a ridosso del bordo: fuori tela resta lo sfondo della pagina,
    # così il dettaglio spiegato resta al centro dell'inquadratura.
    th,tw=patch.shape[:2]
    ih,iw=art.shape[:2]
    baseh=min(ih,iw/ratio);basew=baseh*ratio
    cw=max(2,round(basew/max(1,zoom)));ch=max(2,round(baseh/max(1,zoom)))
    # Si centra il proverbio, ma senza sfondare il bordo: al massimo il 14% del
    # fotogramma resta fuori tela, così l'immagine non si svuota di lato.
    over=.14
    x0=round(fx*iw-cw/2);y0=round(fy*ih-ch/2)
    x0=int(min(iw-cw+over*cw,max(-over*cw,x0)))
    y0=int(min(ih-ch+over*ch,max(-over*ch,y0)))
    sx0=max(0,x0);sy0=max(0,y0);sx1=min(iw,x0+cw);sy1=min(ih,y0+ch)
    if sx1<=sx0 or sy1<=sy0:return
    px0=max(0,min(tw-1,round((sx0-x0)*tw/cw)));py0=max(0,min(th-1,round((sy0-y0)*th/ch)))
    px1=min(tw,round((sx1-x0)*tw/cw));py1=min(th,round((sy1-y0)*th/ch))
    if px1<=px0 or py1<=py0:return
    sub=art[sy0:sy1,sx0:sx1]
    resized=cv2.resize(sub,(px1-px0,py1-py0),
        interpolation=cv2.INTER_AREA if sx1-sx0>px1-px0 else cv2.INTER_CUBIC)
    patch[py0:py1,px0:px1]=resized

def paste_clipped(frame,image,x,y):
    fh,fw=frame.shape[:2];ih,iw=image.shape[:2]
    x0=max(0,x);y0=max(0,y);x1=min(fw,x+iw);y1=min(fh,y+ih)
    if x1<=x0 or y1<=y0:return
    frame[y0:y1,x0:x1]=image[y0-y:y1-y,x0-x:x1-x]

def frame_beat(background,art,beat,p,ratio):
    frame=background.copy()
    ih,iw=art.shape[:2]
    if beat.get("wide"):
        # Apertura "come una fotografia che prende vita": il quadro e' dapprima
        # incorniciato e quasi fermo, poi una carrellata decisa lo fa entrare
        # nel campo verso la zona dei primi proverbi, in sincrono con la voce
        # ("Da lontano... Da vicino"). Nessun bordo: il quadro riempie il campo.
        s=(RX1-RX0)/iw*(0.82+.60*push(p))
        nw,nh=max(2,round(iw*s)),max(2,round(ih*s))
        image=cv2.resize(art,(nw,nh),interpolation=cv2.INTER_AREA if s<1 else cv2.INTER_CUBIC)
        dx=round(-70*small_smooth(p)); dy=round(-30*small_smooth(p))
        paste_clipped(frame,image,RX0+((RX1-RX0)-nw)//2+dx,RY0+((RY1-RY0)-nh)//2+dy)
        return frame
    # Dettaglio: apertura sul contesto (zoom basso per far vedere le figure
    # intorno), carrellata sul particolare narrato che resta il protagonista,
    # infine un leggero rilascio morbido per preparare lo sguardo al racconto dopo.
    q=min(1.,max(0.,p))
    if q<.5:
        env=push(q/.5)                 # 0 -> 1  (spinta sul dettaglio)
    else:
        env=1.0-.14*small_smooth((q-.5)/.5)   # 1 -> 0.86 (rilascio morbido)
    z=beat["zoom_start"]+(beat["zoom_end"]-beat["zoom_start"])*env
    cw=min(ih,iw/(968/1430))*(968/1430)/max(1,z)   # larghezza reale del ritaglio
    fx=beat["focus"][0]+(.030*cw)/iw*math.sin(math.pi*q)
    fy=beat["focus"][1]+(.020*cw)/ih*math.sin(math.pi*q)
    patch=background[RY0:RY1,RX0:RX1].copy()
    crop_into(patch,art,fx,fy,max(1,z),968/1430)
    frame[RY0:RY1,RX0:RX1]=patch
    return frame

def closing_card(background,cfg):
    # Cartellino d'opera: il finale è una scheda di museo, non un invito social.
    # Stessa tipografia dell'opera: filetti d'oro, nome, autore, anno e sede.
    canvas=Image.fromarray(cv2.cvtColor(background,cv2.COLOR_BGR2RGB))
    d=ImageDraw.Draw(canvas)
    gold=GOLD;ivory=IVORY
    quiet=(214,205,190)
    cy=980
    d.line((330,cy-190,750,cy-190),fill=gold,width=2)
    artist=cfg["artist"].upper()
    f=font_to_fit(d,artist,760,44,26)
    d.text(((W-d.textbbox((0,0),artist,font=f)[2])/2,cy-160),artist,font=f,fill=gold)
    title=cfg["artwork"]
    f=font_to_fit(d,title,880,80,40)
    d.text(((W-d.textbbox((0,0),title,font=f)[2])/2,cy-84),title,font=f,fill=ivory)
    meta=" · ".join(x for x in (cfg.get("year",""),cfg.get("museum","")) if x)
    if meta:
        f=font_to_fit(d,meta,820,40,24)
        d.text(((W-d.textbbox((0,0),meta,font=f)[2])/2,cy+56),meta,font=f,fill=quiet)
    d.line((330,cy+150,750,cy+150),fill=gold,width=2)
    return cv2.cvtColor(np.asarray(canvas),cv2.COLOR_RGB2BGR)

def produce(cfg,img,source,voice,vsec,bounds,engine,music,proof,out):
    beats=cfg["beats"]
    assert len(beats)==len(bounds)
    cover=cover_universal(img,cfg)
    cv2.imwrite(str(out/"COPERTINA.jpg"),cover,[cv2.IMWRITE_JPEG_QUALITY,96])
    base=backdrop(img)
    ratio=img.shape[1]/img.shape[0]
    pad=0.22 if cfg.get("immediate_visual_hook") else 2.8
    tail=5.2 if cfg.get("immediate_visual_hook") else 4.1
    duration=math.ceil(pad+vsec+tail)
    raw=out/"BASE_VIDEO.mp4"
    ff=subprocess.Popen(["ffmpeg","-hide_banner","-loglevel","error","-y",
      "-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),
      "-i","-","-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p",
      "-threads","2","-movflags","+faststart",str(raw)],stdin=subprocess.PIPE)
    # Cache identity-free transitions as a retained picture only per beat.
    previous=None;oldbeat=-1;transition=None;enter_at=0
    card=closing_card(base,cfg)
    dark=np.zeros((H,W,3),np.uint8);dark[:]=INK
    def close_frame_at(q):
        # Chiusura in movimento: il quadro si allontana lentamente (zoom out)
        # come un respiro finale. Parte dallo stesso zoom e dalla stessa deriva
        # con cui termina la battuta 19 (wide), cosi' non c'e' nessun salto.
        fr=base.copy()
        ih,iw=img.shape[:2]
        s=(RX1-RX0)/iw*(1.22-.30*small_smooth(min(1.,q)))
        nw,nh=max(2,round(iw*s)),max(2,round(ih*s))
        image=cv2.resize(img,(nw,nh),interpolation=cv2.INTER_AREA if s<1 else cv2.INTER_CUBIC)
        dx=round(-30*(1-small_smooth(min(1.,q)))); dy=round(-14*(1-small_smooth(min(1.,q))))
        paste_clipped(fr,image,RX0+((RX1-RX0)-nw)//2+dx,RY0+((RY1-RY0)-nh)//2+dy)
        return fr
    print("VIDEO BATCH",cfg["id"],"voice",round(vsec,1),"timeline",duration,"frames",duration*FPS,flush=True)
    frames=duration*FPS
    for k in range(frames):
        t=k/FPS
        narr=t-pad
        idx=0
        while idx<len(bounds)-1 and narr>=bounds[idx]:idx+=1
        if idx!=oldbeat:
            transition=previous.copy() if previous is not None else None
            enter_at=t;oldbeat=idx
        begin=0 if idx==0 else bounds[idx-1];stop=bounds[idx]
        p=(narr-begin)/max(.2,stop-begin)
        if t<3.25 and not cfg.get("immediate_visual_hook"):fr=cover.copy()
        elif t>pad+vsec:
            # Chiusura: il quadro si allontana lentamente, poi si dissolve nel
            # cartellino d'opera e infine scende al buio. Sempre in movimento.
            q=(t-(pad+vsec))/tail
            if q<.28:fr=close_frame_at(q)
            elif q<.52:
                b=small_smooth((q-.28)/.24)
                fr=cv2.addWeighted(close_frame_at(q),1-b,card,b,0)
            elif q<.88:fr=card.copy()
            else:
                b=small_smooth((q-.88)/.12)
                fr=cv2.addWeighted(card,1-b,dark,b,0)
        else:
            fr=frame_beat(base,img,beats[idx],p,ratio)
            if transition is not None and t-enter_at<.28:
                blend=small_smooth((t-enter_at)/.28)
                fr=cv2.addWeighted(transition,1-blend,fr,blend,0)
        try:ff.stdin.write(fr.tobytes())
        except BrokenPipeError:raise RuntimeError("FFmpeg encode crashed")
        previous=fr
        if k%(FPS*35)==0:print("RENDER",cfg["id"],round(t),"/",duration,flush=True)
    ff.stdin.close()
    if ff.wait()!=0:raise RuntimeError("Video render ffmpeg returned error "+str(ff.returncode))
    master=out/("ARTVISION_"+cfg["id"].upper()+".mp4")
    ffargs=["ffmpeg","-hide_banner","-loglevel","error","-y","-i",raw,
      "-i",voice,"-stream_loop","-1","-i",music,
      "-filter_complex",
      f"[1:a]adelay={round(pad*1000)}|{round(pad*1000)},atrim=0:{duration},asetpts=PTS-STARTPTS,volume=1.0[v];"+
      f"[2:a]atrim=0:{duration},asetpts=PTS-STARTPTS,volume=0.085,"+
      f"afade=t=in:st=0:d=3,afade=t=out:st={max(0,duration-6)}:d=6[m];"+
      "[v][m]amix=inputs=2:duration=longest:normalize=0[a]",
      "-map","0:v:0","-map","[a]","-c:v","copy","-c:a","aac","-b:a","192k",
      "-movflags","+faststart","-t",str(duration),str(master)]
    run(ffargs)
    meta=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries",
      "format=duration:stream=codec_type,width,height","-of","json",str(master)]))
    assert {s["codec_type"] for s in meta["streams"]}=={"audio","video"}
    assert (next(s for s in meta["streams"] if s["codec_type"]=="video")["width"],
      next(s for s in meta["streams"] if s["codec_type"]=="video")["height"])==(W,H)
    assert abs(float(meta["format"]["duration"])-duration)<1
    assert master.stat().st_size>cfg.get("min_master_bytes",8_000_000)
    report={"episode":cfg["id"],"video":master.name,"seconds":duration,"voice_seconds":vsec,
      "engine":engine,"resolution":[W,H],"art":source,"music":proof,
      "cover_layout":"universal V2: localized title + artist only",
      "subtitle_overlay":False,"episode_sources":cfg["sources"],"beats":[{"title":b["title_internal"],
      "from":round(pad+(0 if i==0 else bounds[i-1]),2),"to":round(pad+bounds[i],2),
      "focus":b["focus"]} for i,b in enumerate(beats)]}
    (out/"REGIA_SINCRONIZZAZIONE.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
    (out/"COPIONE_IT.txt").write_text("\n\n".join(b["speech"] for b in beats),encoding="utf8")
    (out/"DIRITTI_E_FONTI.txt").write_text(
      "ArtVision Critico - "+cfg["artist"]+" / "+cfg["artwork"]+".\n"+
      "Opera storica in pubblico dominio in Italia. Fotografia / stampa di pubblico dominio: verificare pagina Wikimedia e norme di destinazione.\n"+
      "Riproduzione usata: "+cfg["commons_title"]+"\n"+
      "Voce: "+engine+"\n"+
      "Musica: "+cfg["music"].get("title","?")+" di "+cfg["music"].get("composer","Kevin MacLeod")+
      " (https://incompetech.com), "+cfg["music"].get("license","CC BY 4.0")+" "+
      "https://creativecommons.org/licenses/by/4.0/ — ripetizione, volume attenuato, fade iniziale/finale e mix con voce.\n"+
      "Fonti:\n"+"\n".join(cfg["sources"])+"\n",
      encoding="utf8")
    print("MASTER VERIFIED",cfg["id"],master.stat().st_size,"bytes",duration,"seconds",engine,flush=True)

def main():
    cli=argparse.ArgumentParser(
        description="ArtVision Critico V2: legacy episodes or verified per-artwork JSON (V53 paired series).")
    source=cli.add_mutually_exclusive_group(required=True)
    source.add_argument("--episode", help="Existing JSON episode basename in production_series/")
    source.add_argument("--config", type=Path, help="Path to a prepared and verified JSON for a new painting")
    cli.add_argument("--require-gacrux", action="store_true",
                     help="Require actual Google Gemini Gacrux, never silently use Edge fallback")
    args=cli.parse_args()
    cfg_path=args.config if args.config else PARENT/(args.episode+".json")
    if not cfg_path.is_file():
        cli.error("Episode JSON not found: "+str(cfg_path))
    cfg=json.loads(cfg_path.read_text(encoding="utf8"))
    episode_id=cfg.get("id")
    if not isinstance(episode_id,str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{2,80}",episode_id):
        cli.error("JSON needs a safe, nonempty id of 3-81 lowercase letters/numbers/_/-")
    if args.episode and episode_id!=args.episode:
        cli.error("Episode ID and JSON id differ")
    required_fields=("artist","artwork","commons_title","image_ratio_min",
                     "image_ratio_max","sources","beats","music")
    missing=[key for key in required_fields if key not in cfg]
    if missing:cli.error("Incomplete episode JSON: "+", ".join(missing))
    if not isinstance(cfg["beats"],list) or len(cfg["beats"])<3 or any(
        not b.get("speech") or not isinstance(b.get("focus"),list) or len(b["focus"])!=2
        for b in cfg["beats"]):
        cli.error("Critico requires researched narration and visual focus for each beat")
    # New custom V53 episodes always require a real Google Gemini voice (any
    # configured timbre); legacy V2 rendering retains its historical fallback
    # unless explicitly constrained. Edge is never accepted here.
    require_gacrux=args.require_gacrux or args.config is not None
    if require_gacrux and not os.getenv("GEMINI_API_KEY","").strip():
        raise RuntimeError("blocked_voice_unavailable: GEMINI_API_KEY absent; "
                           "do not replace Critico with silent Cinema or Edge")
    output=OUTROOT/episode_id
    output.mkdir(parents=True,exist_ok=True)
    painting,source=get_art(cfg,output)
    voice,sec,bounds,engine=choose_voice(cfg["beats"],output)
    if require_gacrux and "Gemini" not in engine:
        raise RuntimeError("blocked_voice_unavailable: real Google Gemini voice not produced ("+engine+"); "
                           "render is forbidden (no fallback approval)")
    if "Gemini" not in engine:
        print("WARNING: Gemini unavailable, alternative Edge voice used. Clearly disclosed in metadata.",flush=True)
    music,proof=music_get(cfg,output)
    if music is None:raise RuntimeError("Licensed background track not found, prevent missing music delivery")
    produce(cfg,painting,source,voice,sec,bounds,engine,music,proof,output)

if __name__=="__main__":main()
