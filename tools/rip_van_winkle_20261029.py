#!/usr/bin/env python3
"""Rip Van Winkle: 17 original Rackham plates, truthful preview only; no TTS or paid APIs."""
from __future__ import annotations
import hashlib,json,math,subprocess,zipfile
from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from PIL import Image,ImageOps,ImageDraw,ImageFont,ImageFilter
import numpy as np
import soundfile as sf

EP=Path("episodes/rip_van_winkle_20261029")
OUT=Path("output/rip_van_winkle_20261029")
SOURCE="https://www.gutenberg.org/cache/epub/60976/pg60976-images.html"
NAVY=(19,34,48);GOLD=(196,158,104);PAPER=(236,227,208)
def sha(data):return hashlib.sha256(data).hexdigest()
def ff(*args):subprocess.run([str(a) for a in args],check=True)
def font(n,bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/"+("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),n)
def make_frame(im):
    im=ImageOps.exif_transpose(im.convert("RGB"))
    bg=ImageOps.fit(im,(720,1280),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(34))
    bg=Image.blend(bg,Image.new("RGB",(720,1280),NAVY),.85)
    d=ImageDraw.Draw(bg)
    d.rounded_rectangle((30,55,690,1225),radius=10,fill=PAPER,outline=GOLD,width=3)
    art=ImageOps.contain(im,(626,1114),Image.Resampling.LANCZOS)
    bg.paste(art,((720-art.width)//2,(1280-art.height)//2))
    return bg
def cover(frame):
    im=frame.copy();d=ImageDraw.Draw(im)
    d.rectangle((0,0,720,300),fill=NAVY)
    d.text((360,50),"TRA LE PAGINE",font=font(31,True),fill=GOLD,anchor="ma")
    d.text((360,127),"RIP VAN WINKLE",font=font(48,True),fill=PAPER,anchor="ma")
    d.text((360,208),"WASHINGTON IRVING",font=font(26),fill=PAPER,anchor="ma")
    d.rectangle((0,1130,720,1280),fill=NAVY)
    d.text((360,1194),"ILLUSTRAZIONI DI ARTHUR RACKHAM",font=font(19),fill=GOLD,anchor="ma")
    im.save(OUT/"COPERTINA.jpg",quality=93)
def music(duration):
    sr=24000;n=int(sr*duration);y=np.zeros(n,np.float32)
    # Original quiet, suspended three-note theme; no copyrighted recording.
    notes=[(50,0),(57,1.4),(53,2.8),(48,4.2),(55,5.6),(52,7.0),(50,8.4),(45,9.8)]
    for k in range(math.ceil(duration/11.2)):
        for note,offset in notes:
            pos=k*11.2+offset
            if pos>=duration:continue
            length=min(n-int(pos*sr),int(2.4*sr))
            if length<=0:continue
            t=np.arange(length,dtype=np.float32)/sr
            hz=440*2**((note-69)/12)
            env=np.minimum(1,t/.08)*np.exp(-t/1.0)
            wave=np.sin(2*np.pi*hz*t)+.18*np.sin(4*np.pi*hz*t)
            y[int(pos*sr):int(pos*sr)+length]+=.028*wave*env
    t=np.arange(n,dtype=np.float32)/sr
    y*=np.minimum(1,t/1.2)*np.minimum(1,np.maximum(0,duration-t)/2)
    sf.write(OUT/"MUSICA_ORIGINALE.wav",np.clip(y,-.4,.4),sr)
def run():
    OUT.mkdir(parents=True,exist_ok=True)
    images=OUT/"ILLUSTRAZIONI";images.mkdir(exist_ok=True)
    plan=json.loads((EP/"scene_plan_rip.json").read_text(encoding="utf8"))["scenes"]
    paragraphs=[x.strip() for x in (EP/"testo.txt").read_text(encoding="utf8").split("\n\n") if x.strip()]
    assert len(plan)==len(paragraphs)==17
    assert len({x["source_plate_index"] for x in plan})==17
    assert all(p["narration"]==t for p,t in zip(plan,paragraphs))
    s=requests.Session();s.headers["User-Agent"]="TraLePagineStudio/1.0 (one book, 17 public-domain historical illustrations)"
    r=s.get(SOURCE,timeout=60);r.raise_for_status()
    soup=BeautifulSoup(r.content,"html.parser")
    # These anchors follow the color plates, in the exact order of the printed list.
    links=[a for a in soup.find_all("a") if "see larger view" in a.get_text(" ",strip=True).lower()]
    if len(links)!=24:raise RuntimeError("Expected 24 illustrated plates; got "+str(len(links))+"; no speculative mapping")
    provenance=[];cache={};frames=[]
    for row in plan:
        index=row["source_plate_index"]
        if not 0<=index<24:raise RuntimeError("Invalid source plate index")
        a=links[index]
        img=a.find_previous("img")
        if img is None:raise RuntimeError("Missing original image near plate "+str(index))
        href=a.get("href","")
        if not href.lower().split("?")[0].endswith((".jpg",".jpeg",".png",".webp")):
            href=img.get("src","")
        url=urljoin(SOURCE,href)
        if url not in cache:
            res=s.get(url,timeout=60);res.raise_for_status()
            if len(res.content)>15000000:raise RuntimeError("Oversize original")
            with Image.open(BytesIO(res.content)) as raw:
                raw.load()
                if min(raw.size)<250 or max(raw.size)<500:raise RuntimeError("Original plate too small")
                cache[url]=(res.content,raw.convert("RGB"),list(raw.size))
        raw,im,dim=cache[url]
        output=images/("scena_%02d.jpg"%row["scene"])
        make_frame(im).save(output,quality=93,optimize=True)
        if output.stat().st_size<20000:raise RuntimeError("Invalid scene JPG")
        frames.append(output)
        provenance.append({"scene":row["scene"],"source_plate_index":index,
            "source_url":url,"source_page":SOURCE,"original_dimensions":dim,
            "original_sha256":sha(raw),"output_sha256":sha(output.read_bytes()),
            "visual_intent":row["visual_intent"],"scene_match_note":row["scene_match_note"],
            "rights":"Washington Irving (d.1859), Arthur Rackham (d.1939), original 1905 illustration: public domain Italy/USA",
            "semantic_visual_review":"pending actual contact sheet inspection"})
        print("PLATE",row["scene"],index,dim,url,flush=True)
    cover(Image.open(frames[-1]).convert("RGB"))
    thumb_w,thumb_h=180,320
    sheet=Image.new("RGB",(4*thumb_w,5*(thumb_h+25)),NAVY)
    draw=ImageDraw.Draw(sheet)
    for i,p in enumerate(frames):
        im=Image.open(p).resize((thumb_w,thumb_h),Image.Resampling.LANCZOS)
        x=(i%4)*thumb_w;y=(i//4)*(thumb_h+25)
        sheet.paste(im,(x,y));draw.text((x+7,y+thumb_h+3),str(i+1),fill=PAPER,font=font(15,True))
    sheet.save(OUT/"STORYBOARD_COMPLETO.jpg",quality=91)
    (OUT/"PROVENIENZA_IMMAGINI.json").write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding="utf8")
    for name in ("testo.txt","metadata.json","PROJECT_V13.json","SCHEDE_VISUALI_V35.json",
                 "scene_plan_rip.json","FONTI_E_DIRITTI.md","DESCRIZIONE_SOCIAL.txt",
                 "POST_FACEBOOK.txt","POST_INSTAGRAM.txt","POST_TIKTOK.txt","POST_YOUTUBE.txt"):
        (OUT/name).write_bytes((EP/name).read_bytes())
    (OUT/"MUSICA_CREDITI.txt").write_text("Rip Van Winkle — tema sospeso. Composizione e sintesi originale Tra le Pagine; nessun campione di terzi.\n",encoding="utf8")
    duration=26.0
    music(duration)
    concat=OUT/"STILLS_CONCAT.txt"
    with concat.open("w") as f:
        for p in frames:
            f.write("file '"+str(p.resolve())+"'\nduration "+str(duration/17)+"\n")
        f.write("file '"+str(frames[-1].resolve())+"'\n")
    preview=OUT/"RIP_VAN_WINKLE_ANTEPRIMA_VISIVA_26S_NON_NARRATA.mp4"
    ff("ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0",
       "-i",concat,"-i",OUT/"MUSICA_ORIGINALE.wav","-vf","fps=24,format=yuv420p",
       "-t",duration,"-map","0:v:0","-map","1:a:0","-sn","-c:v","libx264",
       "-preset","veryfast","-crf","24","-c:a","aac","-b:a","128k",
       "-movflags","+faststart",preview)
    ff("ffmpeg","-hide_banner","-loglevel","error","-xerror","-i",preview,"-f","null","-")
    probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_format","-show_streams","-of","json",str(preview)],text=True))
    v=next(x for x in probe["streams"] if x["codec_type"]=="video")
    a=next(x for x in probe["streams"] if x["codec_type"]=="audio")
    if (v["width"],v["height"],v["codec_name"],a["codec_name"])!=(720,1280,"h264","aac"):
        raise RuntimeError("Preview technical QA failed")
    state={"episode":EP.name,"status":"visual_preview_only_not_complete","preview_sha256":sha(preview.read_bytes()),
        "preview_duration_seconds":float(probe["format"]["duration"]),
        "unique_original_illustrations":len(cache),"shots":len(frames),
        "voice":"NOT GENERATED","gacrux_free_quota_confirmed":False,
        "narrated_master_exists":False,"artistic_review":"pending",
        "V13":"draft_pending_full_preflight","V35":"pending semantic review",
        "archive_import":"not_performed","social_publish":"not_performed","paid_video_calls":0}
    (OUT/"QA_STATO_REALE.json").write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf8")
    with zipfile.ZipFile(OUT/"RIP_VAN_WINKLE_PACCHETTO_VISUALE_NON_FINALE.zip","w",zipfile.ZIP_DEFLATED,compresslevel=2) as z:
        for p in sorted(OUT.iterdir()):
            if p.is_file() and p.suffix not in (".zip",):z.write(p,p.name)
        for p in frames:z.write(p,"ILLUSTRAZIONI/"+p.name)
    with zipfile.ZipFile(OUT/"RIP_VAN_WINKLE_PACCHETTO_VISUALE_NON_FINALE.zip") as z:
        if z.testzip() is not None:raise RuntimeError("ZIP CRC failed")
    print("PREVIEW_VERIFIED",json.dumps(state,ensure_ascii=False),flush=True)
if __name__=="__main__":run()
