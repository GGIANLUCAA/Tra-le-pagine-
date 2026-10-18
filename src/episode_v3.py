#!/usr/bin/env python3
"""Tra le Pagine V3: validate creative assets BEFORE spending TTS credits,
and check/brand delivered artifacts AFTER rendering.
Designed to work with the existing src/render.py unchanged.
"""
import argparse
import io
import json
import math
import re
import subprocess
import sys
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path("episodes")
LOGO="TRA LE PAGINE"
FONT_SERIF="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SANS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def fail(message):
    raise ValueError(message)

def load(episode):
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,70}",episode):
        fail("Nome episodio non valido")
    ep=ROOT/episode
    if not ep.is_dir(): fail(f"Cartella mancante: {ep}")
    for name in ("testo.txt","metadata.json","scene_cues.json","DESCRIZIONE_SOCIAL.txt"):
        if not (ep/name).is_file():fail(f"File obbligatorio mancante: {ep/name}")
    metadata=json.loads((ep/"metadata.json").read_text(encoding="utf-8"))
    for field in ("episode","title","author"):
        if not str(metadata.get(field,"")).strip(): fail(f"Metadato mancante: {field}")
    script=(ep/"testo.txt").read_text(encoding="utf-8").strip()
    return ep,metadata,script

def validate(episode):
    ep,metadata,script=load(episode)
    words=len(script.split())
    if not 230 <= words <= 700:
        fail(f"Copione: {words} parole, attese 230–700 per un video da 2–4 minuti")
    cues=json.loads((ep/"scene_cues.json").read_text(encoding="utf-8"))
    if not isinstance(cues,list) or not 8<=len(cues)<=38:
        fail("Storyboard: previste 8–38 inquadrature")
    # Match src/render.py sentence splitter, including punctuation abbreviations.
    phrases=[x.strip() for x in re.split(
        r'(?<=[.!?])\s+(?=[A-ZÀ-ÙÈÉ«“])',
        re.sub(r'\s+',' ',script)) if x.strip()]
    order=[c.get("start_sentence") for c in cues]
    if not all(isinstance(i,int) and 0<=i<len(phrases) for i in order):
        fail(f"Indici frase non validi, tot frasi: {len(phrases)}")
    if order[0]!=0 or any(a>=b for a,b in zip(order,order[1:])):
        fail("Cue points non crescenti o prima scena non a zero")
    assets={c.get("asset") for c in cues}
    if not assets or any(not isinstance(a,int) or a<1 or a>35 for a in assets):
        fail("Asset immagine non valido")
    # Never substitute primitive debug graphics for publish-ready images.
    premium=ep/"scene_premium.zip"
    missing=[]
    if premium.is_file():
        with zipfile.ZipFile(premium) as z:
            names={Path(x.filename).stem.lower():x for x in z.infolist()
                   if not x.is_dir()}
            if sum(v.file_size for v in names.values())>160_000_000:
                fail("Archivio immagini troppo grande")
            for num in assets:
                obj=names.get(f"scena_{num:02}")
                if not obj or Path(obj.filename).suffix.lower() not in (".jpg",".jpeg",".png",".webp"):
                    missing.append(num)
                elif not 35_000<=obj.file_size<=12_000_000:
                    fail(f"Immagine {num:02}: dimensione non credibile")
    else:
        for num in assets:
            path=ep/"images"/f"scena_{num:02}.jpg"
            if not path.is_file() or path.stat().st_size<35_000:
                missing.append(num)
    if missing:
        fail("ILLUSTRAZIONI PREMIUM MANCANTI: "+", ".join(f"scena_{n:02}" for n in sorted(missing))+
             ". Non iniziare audio né video finché non ci sono.")
    print(f"PRONTO PER RENDER: {episode}: {metadata['title']}, {words} parole, "
          f"{len(phrases)} frasi, {len(cues)} inquadrature e {len(assets)} illustrazioni.")
    return ep,metadata

def font(path,size):
    return ImageFont.truetype(path,size)

def wrap(draw,text,face,maxwidth):
    words=text.split()
    lines=[];line=""
    for word in words:
        proposed=(line+" "+word).strip()
        if line and draw.textbbox((0,0),proposed,font=face)[2]>maxwidth:
            lines.append(line)
            line=word
        else:
            line=proposed
    if line:lines.append(line)
    return lines

def branded_cover(outdir,ep,meta):
    """Build cover from a clean narrative scene, not from an old titled cover.

    The historical output COPERTINA.jpg can contain old labels. Using it would
    cause overlapping text. Extract scena_01 from the episode illustrations.
    """
    archive=ep/"scene_premium.zip"
    im=None
    if archive.is_file():
        with zipfile.ZipFile(archive) as z:
            scene=next((entry for entry in z.infolist()
                        if re.fullmatch(r"scena_01\\.(?:jpg|jpeg|png|webp)",
                                        Path(entry.filename).name,re.IGNORECASE)),None)
            if scene is not None:
                im=Image.open(io.BytesIO(z.read(scene))).convert("RGB")
    else:
        for suffix in (".jpg",".jpeg",".png",".webp"):
            path=ep/"images"/("scena_01"+suffix)
            if path.is_file():
                im=Image.open(path).convert("RGB")
                break
    if im is None:
        fail("Impossibile creare copertina: manca la scena 01 senza scritte")
    im=ImageOps.fit(im,(1080,1920),centering=(.5,.43),method=Image.Resampling.LANCZOS)
    overlay=Image.new("RGBA",im.size,(0,0,0,0))
    d=ImageDraw.Draw(overlay)
    # Petrol blue at top and bottom; image is still visible in the middle.
    for y in range(0,475):
        alpha=int(214*(1-y/475)**1.5)
        d.line((0,y,1080,y),fill=(12,42,53,alpha))
    for y in range(1250,1920):
        alpha=int(218*((y-1250)/(1920-1250))**1.2)
        d.line((0,y,1080,y),fill=(12,42,53,alpha))
    gold=(205,166,102,255);ivory=(248,242,230,255)
    sans=font(FONT_SANS,40)
    header=LOGO
    box=d.textbbox((0,0),header,font=sans)
    d.text(((1080-(box[2]-box[0]))//2,114),header,font=sans,fill=gold)
    d.line((205,190,875,190),fill=gold,width=3)
    title=str(meta["title"]).upper()
    face=font(FONT_SERIF,66)
    lines=wrap(d,title,face,914)
    while len(lines)>3:
        face=font(FONT_SERIF,int(face.size*.91))
        lines=wrap(d,title,face,914)
    lineheight=face.size+19
    y=1400-(len(lines)-1)*lineheight
    for line in lines:
        bb=d.textbbox((0,0),line,font=face)
        d.text(((1080-(bb[2]-bb[0]))//2,y),line,font=face,fill=ivory,stroke_width=2,
               stroke_fill=(12,42,53,200))
        y+=lineheight
    author=str(meta["author"]).upper()
    a=font(FONT_SANS,34)
    bb=d.textbbox((0,0),author,font=a)
    d.text(((1080-(bb[2]-bb[0]))//2,y+29),author,font=a,fill=gold)
    d.line((260,1805,820,1805),fill=gold,width=2)
    d.text((325,1830),"UNA STORIA ALLA VOLTA",font=font(FONT_SANS,28),fill=ivory)
    final=Image.alpha_composite(im.convert("RGBA"),overlay).convert("RGB")
    target=outdir/"COPERTINA_SERIE.jpg"
    final.save(target,quality=92,optimize=True)
    print("Copertina coordinata:",target)

def postflight(episode,out):
    ep,meta=validate(episode)
    mp4=out/"TRA_LE_PAGINE_EP01.mp4" # filename used internally by current renderer
    if not mp4.is_file() or mp4.stat().st_size<200_000:
        fail("MP4 assente o troppo piccolo")
    run=subprocess.run(["ffprobe","-v","error","-show_entries",
                        "format=duration:stream=codec_type,width,height",
                        "-of","json",str(mp4)],capture_output=True,text=True,check=True)
    info=json.loads(run.stdout)
    duration=float(info["format"]["duration"])
    streams=info.get("streams",[])
    video=next((s for s in streams if s["codec_type"]=="video"),None)
    audio=next((s for s in streams if s["codec_type"]=="audio"),None)
    if not 100<=duration<=270:fail(f"Durata sospetta: {duration:.1f}s")
    if not video or not audio:fail("Video o audio mancante")
    if video.get("width")!=720 or video.get("height")!=1280:
        fail("Formato video inatteso, atteso 720x1280 dal generatore corrente")
    state=(out/"STATO_IMMAGINI.txt").read_text(encoding="utf-8") if (out/"STATO_IMMAGINI.txt").exists() else ""
    if "ANTEPRIMA TECNICA" in state:fail("Il renderer ha usato illustrazioni provvisorie")
    label=re.sub(r"[^A-Z0-9]+","_",meta["episode"].upper()).strip("_")
    target=out/f"TRA_LE_PAGINE_EP{label}.mp4"
    mp4.rename(target)
    branded_cover(out,ep,meta)
    (out/"CONTROLLO_QUALITA.txt").write_text(
        f"EPISODIO {label}: {meta['title']}\n"
        f"Durata {duration:.1f} secondi; 720x1280, audio presente.\n"
        "Controlli automatici superati. RESTA NECESSARIA REVISIONE UMANA COMPLETA.\n"
        "Non pubblicato automaticamente.\n",encoding="utf-8")
    print("PRODUZIONE TECNICA RIUSCITA:",target)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--episode",required=True)
    ap.add_argument("--post",action="store_true")
    ap.add_argument("--out",default="output")
    args=ap.parse_args()
    if args.post:postflight(args.episode,Path(args.out))
    else:validate(args.episode)
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("ERRORE BLOCCANTE:",exc,file=sys.stderr)
        sys.exit(2)
