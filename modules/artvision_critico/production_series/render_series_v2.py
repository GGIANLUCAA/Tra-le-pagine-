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
W,H,FPS=1080,1920,20
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
                    for key in ("thumburl","url"):
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
            if max(painting.size)>4300:painting.thumbnail((4300,4300),Image.Resampling.LANCZOS)
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
    gold=(GOLD[2],GOLD[1],GOLD[0])
    ivory=(IVORY[2],IVORY[1],IVORY[0])
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
    cv2.rectangle(frame,(x-2,y-2),(x+sw+2,y+sh+2),(131,120,100),1,cv2.LINE_AA)
    return frame

def crop_to(art,fx,fy,zoom,ratio,tw,th):
    ih,iw=art.shape[:2]
    baseh=min(ih,iw/ratio);basew=baseh*ratio
    cw=max(2,min(iw,round(basew/max(1,zoom))))
    ch=max(2,min(ih,round(baseh/max(1,zoom))))
    cx=min(iw-cw/2,max(cw/2,fx*iw))
    cy=min(ih-ch/2,max(ch/2,fy*ih))
    crop=cv2.getRectSubPix(art,(cw,ch),(cx,cy))
    return cv2.resize(crop,(tw,th),interpolation=cv2.INTER_AREA if cw>tw else cv2.INTER_CUBIC)

def frame_beat(background,art,beat,p,ratio):
    frame=background.copy()
    z=beat["zoom_start"]+(beat["zoom_end"]-beat["zoom_start"])*small_smooth(p)
    fx=beat["focus"][0]+.005*math.sin(math.pi*p)
    fy=beat["focus"][1]
    if ratio>1.15:
        # Both wide masterpiece and speaker-relevant detail are continuously visible.
        # Landscape top is whole painting; detail underneath follows narration.
        ih,iw=art.shape[:2]
        sc=min(970/iw,725/ih)
        sw,sh=round(iw*sc),round(ih*sc)
        whole=cv2.resize(art,(sw,sh),interpolation=cv2.INTER_AREA)
        x=(W-sw)//2;y=220+(700-sh)//2
        frame[y:y+sh,x:x+sw]=whole
        cv2.rectangle(frame,(x-2,y-2),(x+sw+2,y+sh+2),(127,119,102),1,cv2.LINE_AA)
        detail=crop_to(art,fx,fy,max(1.06,z),968/665,968,665)
        frame[965:1630,56:1024]=detail
        cv2.rectangle(frame,(54,963),(1025,1631),(127,119,102),1,cv2.LINE_AA)
    else:
        # Portrait and square paintings: a large unobstructed artwork, no captions.
        patch=crop_to(art,fx,fy,max(1,z),968/1430,968,1430)
        frame[235:1665,56:1024]=patch
        cv2.rectangle(frame,(54,233),(1025,1666),(127,119,102),1,cv2.LINE_AA)
    return frame

def silent_symbols(frame,progress):
    # minimal, exclusively iconographic, no written words, no spoken CTA
    level=small_smooth(progress)
    if level<=0:return frame
    import PIL
    canvas=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)).convert("RGBA")
    overlay=Image.new("RGBA",(W,H),(0,0,0,0))
    d=ImageDraw.Draw(overlay)
    a=int(242*level)
    stroke=(243,225,192,a)
    # Small heart left; outline play & + right
    d.line([(471,1778),(443,1750),(445,1735),(455,1728),(470,1732),(480,1740),
            (491,1731),(503,1728),(514,1736),(513,1750),(480,1780),(471,1778)],
          fill=stroke,width=3,joint="curve")
    d.ellipse((559,1723,619,1783),outline=stroke,width=3)
    d.polygon([(580,1739),(580,1767),(600,1753)],outline=stroke)
    return cv2.cvtColor(np.asarray(Image.alpha_composite(canvas,overlay).convert("RGB")),cv2.COLOR_RGB2BGR)

def produce(cfg,img,source,voice,vsec,bounds,engine,music,proof,out):
    beats=cfg["beats"]
    assert len(beats)==len(bounds)
    cover=cover_universal(img,cfg)
    cv2.imwrite(str(out/"COPERTINA.jpg"),cover,[cv2.IMWRITE_JPEG_QUALITY,96])
    base=backdrop(img)
    ratio=img.shape[1]/img.shape[0]
    pad=0.22 if cfg.get("immediate_visual_hook") else 2.8
    tail=3.0 if cfg.get("immediate_visual_hook") else 4.1
    duration=math.ceil(pad+vsec+tail)
    raw=out/"BASE_VIDEO.mp4"
    ff=subprocess.Popen(["ffmpeg","-hide_banner","-loglevel","error","-y",
      "-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),
      "-i","-","-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",
      "-threads","2","-movflags","+faststart",str(raw)],stdin=subprocess.PIPE)
    # Cache identity-free transitions as a retained picture only per beat.
    previous=None;oldbeat=-1;transition=None;enter_at=0
    close_frame=full_art(base.copy(),img)
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
            fr=close_frame.copy()
            q=(t-(pad+vsec))/tail
            if q>.18:fr=silent_symbols(fr,(q-.18)/.32)
            if q>.78:fr=cv2.convertScaleAbs(fr,alpha=max(0,1-(q-.78)/.22),beta=0)
        elif idx==len(beats)-1 and narr>bounds[-1]-3.1:
            fr=close_frame.copy()
        else:
            fr=frame_beat(base,img,beats[idx],p,ratio)
            if transition is not None and t-enter_at<.75:
                blend=small_smooth((t-enter_at)/.75)
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
      f"[1:a]adelay={round(pad*1000)}|{round(pad*1000)},volume=1.0[v];"+
      f"[2:a]volume=0.061,afade=t=in:st=0:d=3,afade=t=out:st={max(0,duration-6)}:d=6[m];"+
      "[v][m]amix=inputs=2:duration=first:normalize=0[a]",
      "-map","0:v:0","-map","[a]","-c:v","copy","-c:a","aac","-b:a","192k",
      "-movflags","+faststart","-t",str(duration),str(master)]
    run(ffargs)
    meta=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries",
      "format=duration:stream=codec_type,width,height","-of","json",str(master)]))
    assert {s["codec_type"] for s in meta["streams"]}=={"audio","video"}
    assert (next(s for s in meta["streams"] if s["codec_type"]=="video")["width"],
      next(s for s in meta["streams"] if s["codec_type"]=="video")["height"])==(W,H)
    assert abs(float(meta["format"]["duration"])-duration)<1
    assert master.stat().st_size>8_000_000
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
      "Musica: Night on the Docks - Piano di Kevin MacLeod (https://incompetech.com), CC BY 4.0 "+
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
    # New custom V53 episodes always require true Google Gacrux; legacy
    # V2 rendering retains its historical fallback unless explicitly constrained.
    require_gacrux=args.require_gacrux or args.config is not None
    if require_gacrux and not os.getenv("GEMINI_API_KEY","").strip():
        raise RuntimeError("blocked_voice_unavailable: GEMINI_API_KEY absent; "
                           "do not replace Critico with silent Cinema or Edge")
    output=OUTROOT/episode_id
    output.mkdir(parents=True,exist_ok=True)
    painting,source=get_art(cfg,output)
    voice,sec,bounds,engine=choose_voice(cfg["beats"],output)
    if require_gacrux and "Gemini Gacrux" not in engine:
        raise RuntimeError("blocked_voice_unavailable: Gacrux audio not actually produced; "
                           "render is forbidden (no fallback approval)")
    if "Gemini" not in engine:
        print("WARNING: Gemini unavailable, alternative Edge voice used. Clearly disclosed in metadata.",flush=True)
    music,proof=music_get(cfg,output)
    if music is None:raise RuntimeError("Licensed background track not found, prevent missing music delivery")
    produce(cfg,painting,source,voice,sec,bounds,engine,music,proof,output)

if __name__=="__main__":main()
