#!/usr/bin/env python3
"""Illustrated Oz episode: authentic 1900 drawings, original Italian narration, Gacrux.

No stock filler, no fake photographs, no paid image providers. Does not publish.
"""
from __future__ import annotations
import argparse
import hashlib
from html.parser import HTMLParser
import io
import json
import math
import re
import shutil
import subprocess
import sys
import time
import wave
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "https://www.gutenberg.org/cache/epub/43936/pg43936-images.html"
TITLE = "Il meraviglioso mago di Oz"
AUTHOR = "L. Frank Baum"
ARTIST = "W. W. Denslow"
SLUG = "TRA_LE_PAGINE_IL_MERAVIGLIOSO_MAGO_DI_OZ"
WIDTH, HEIGHT, FPS = 720, 1280, 20
AGENT = "Tra-le-Pagine-Original-Denslow-Episode/1.0"
# Each scene follows an actual story beat, NOT a fixed visual quota.
BEATS = [
    ("La casa nel cielo", 1, ["toto", "cyclone", "house"]),
    ("Kansas grigio", 1, ["dorothy and toto", "aunt", "uncle"]),
    ("Il ciclone", 1, ["toto by the ear", "cyclone", "wind"]),
    ("Il paese colorato", 2, ["munchkin", "dorothy"]),
    ("La via gialla", 2, ["yellow brick", "slippers", "witch"]),
    ("Lo Spaventapasseri", 3, ["scarecrow", "corn"]),
    ("Il Boscaiolo di Latta", 5, ["woodman", "tinman", "rust"]),
    ("Il Leone", 6, ["lion crying", "lion", "toto"]),
    ("Il campo dei papaveri", 8, ["poppy", "flowers", "lion"]),
    ("La regina dei topi", 9, ["mice", "queen", "lion"]),
    ("La Città di Smeraldo", 10, ["emerald city", "gate"]),
    ("Il Grande Oz", 11, ["oz", "head", "throne"]),
    ("La Strega dell'Ovest", 12, ["wicked", "witch", "monkeys"]),
    ("Il potere dell'acqua", 13, ["witch", "water", "dorothy"]),
    ("L'uomo dietro la tenda", 15, ["humbug", "oz", "curtain"]),
    ("Il cervello e il cuore", 16, ["brains", "heart", "wizard"]),
    ("La mongolfiera", 17, ["balloon", "oz"]),
    ("In cerca di Glinda", 21, ["glinda", "south", "journey"]),
    ("Le scarpette d'argento", 23, ["glinda", "shoes", "slippers"]),
    ("Il ritorno a casa", 24, ["home", "kansas", "dorothy"]),
    ("I desideri degli amici", 24, ["dorothy", "scarecrow", "lion"])


class TagReader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.chapter = 0
        self.images = []
        self.in_heading = False
        self.heading_text = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("h1", "h2", "h3", "h4"):
            self.in_heading = True
            self.heading_text = []
        if tag == "img":
            ref = a.get("src", "")
            if ref.lower().split("?")[0].endswith((".jpg", ".jpeg", ".png")):
                url = urljoin(SOURCE, ref)
                self.images.append({"url": url, "alt": a.get("alt", ""), "chapter": self.chapter})
    def handle_data(self, data):
        if self.in_heading:
            self.heading_text.append(data)
    def handle_endtag(self, tag):
        if tag in ("h1", "h2", "h3", "h4") and self.in_heading:
            heading = " ".join(self.heading_text).upper()
            match = re.search(r"CHAPTER\s+([IVXLCDM]+|\d+)", heading)
            if match:
                roman = match.group(1)
                try:
                    self.chapter = int(roman)
                except ValueError:
                    value = 0
                    for i, ch in enumerate(roman):
                        digit = dict(I=1, V=5, X=10, L=50, C=100, D=500, M=1000)[ch]
                        nxt = dict(I=1, V=5, X=10, L=50, C=100, D=500, M=1000).get(roman[i+1], 0) if i+1 < len(roman) else 0
                        value += -digit if nxt > digit else digit
                    self.chapter = value
            self.in_heading = False

def fetch(url, cap=18_000_000):
    u = urlparse(url)
    if u.scheme != "https" or u.hostname not in ("www.gutenberg.org", "gutenberg.org"):
        raise RuntimeError("Refused non-Gutenberg source URL: " + url)
    with urlopen(Request(url, headers={"User-Agent": AGENT}), timeout=50) as resp:
        data = resp.read(cap + 1)
    if len(data) > cap:
        raise RuntimeError("Source exceeds safe size limit")
    return data

def collect_assets(folder):
    folder.mkdir(parents=True, exist_ok=True)
    page = fetch(SOURCE, 3_800_000).decode("utf-8", "replace")
    parser = TagReader()
    parser.feed(page)
    candidates = [x for x in parser.images
                  if "/43936/" in x["url"] and "images/" in x["url"]
                  and not re.search(r"chapter\s+[ivx\d]+|copyright|dedication|frontispiece", x["alt"], re.I)]
    if len(candidates) < 25:
        raise RuntimeError("Original illustrated edition unavailable: %d illustrated candidates" % len(candidates))
    chapters_detected = len({x["chapter"] for x in candidates}) >= 6
    print("Original images in edition:", len(candidates), "chapter parsing", chapters_detected, flush=True)
    selected, used = [], set()
    for i, (title, chapter, hints) in enumerate(BEATS):
        scored = []
        for idx, item in enumerate(candidates):
            if item["url"] in used:
                continue
            alt = item["alt"].casefold()
            prox = abs(item["chapter"]-chapter) / 23 if chapters_detected else abs(idx / len(candidates) - (i+.5)/len(BEATS))
            points = max(0, 12 - 40 * prox)
            points += max((7 if hint in alt else 0) for hint in hints)
            if chapters_detected and item["chapter"] == chapter:
                points += 2
            scored.append((points, -idx, item))
        scored.sort(reverse=True)
        saved = None
        for _, _, item in scored[:12]:
            try:
                raw = fetch(item["url"])
                with Image.open(io.BytesIO(raw)) as opened:
                    opened.load()
                    img = ImageOps.exif_transpose(opened).convert("RGB")
                if min(img.size) < 260:
                    continue
                dest = folder / ("scene_%02d.jpg" % (i+1))
                img.save(dest, quality=94, optimize=True)
                saved = dict(item, scene=i+1, title=title, file=dest.name,
                             width=img.width, height=img.height,
                             sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),
                             original_author=ARTIST, year=1900,
                             rights_review="public-domain-authors-died-1915-1919-country-check-required")
                used.add(item["url"])
                break
            except Exception as exc:
                print("Source skipped", item["url"].rsplit("/",1)[-1], type(exc).__name__, flush=True)
        if not saved:
            raise RuntimeError("No usable, distinct, original illustration for beat: " + title)
        selected.append(saved)
        print("%02d" % (i+1), title, saved["alt"][:60], saved["url"].rsplit("/",1)[-1], flush=True)
        time.sleep(0.20)
    report = {"source_edition": SOURCE, "title": "The Wonderful Wizard of Oz",
              "authors": {"text": "L. Frank Baum (died 1919)",
                          "original_illustrations": "W. W. Denslow (died 1915)"},
              "illustration_year": 1900, "assets": selected,
              "note": "Public domain original authors/illustrator: verify territorial reuse and scan terms before monetization. No stock/AI image fallback."}
    write_json(folder.parent / "FONTI_ILLUSTRAZIONI.json", report)
    return selected

def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")

def font(size, bold=False):
    paths = (["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] if bold else
             ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"])
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def paragraph_lines(draw, text, ft, max_width):
    lines, current = [], ""
    for word in text.split():
        candidate = (current+" "+word).strip()
        if draw.textbbox((0,0), candidate, font=ft)[2] <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def fit_image(img, box, background):
    img = ImageOps.exif_transpose(img).convert("RGB")
    margin = 18
    tw, th = box[2]-box[0]-margin*2, box[3]-box[1]-margin*2
    img.thumbnail((tw, th), Image.Resampling.LANCZOS)
    left = box[0]+(box[2]-box[0]-img.width)//2
    top = box[1]+(box[3]-box[1]-img.height)//2
    background.paste(img, (left, top))
    return (left, top, left+img.width, top+img.height)

def make_frame(asset, original_path, dest, *, cover=False):
    canvas = Image.new("RGB", (WIDTH, HEIGHT), (11, 24, 38))
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((21, 16, WIDTH-21, HEIGHT-16), radius=15, outline=(173, 143, 91), width=3)
    d.text((48, 43), "TRA LE PAGINE", fill=(231,214,185), font=font(22, True))
    d.text((49, 77), "S T U D I O   I B R I D O", fill=(186,176,158), font=font(13))
    d.line((48, 118, WIDTH-48, 118), fill=(143,119,82), width=2)
    picture_box=(39,154,WIDTH-39,HEIGHT-192)
    d.rounded_rectangle((picture_box[0],picture_box[1],picture_box[2],picture_box[3]), 
                        radius=11, fill=(227,212,179))
    with Image.open(original_path) as im:
        bounds=fit_image(im, picture_box, canvas)
    d=ImageDraw.Draw(canvas)
    d.rectangle((bounds[0]-2,bounds[1]-2,bounds[2]+2,bounds[3]+2),outline=(190,161,109),width=2)
    if cover:
        d.rounded_rectangle((50, HEIGHT-295, WIDTH-50, HEIGHT-80),radius=12, fill=(7,19,32),outline=(170,142,94),width=2)
        y=HEIGHT-277
        for ln in paragraph_lines(d,"IL MERAVIGLIOSO MAGO DI OZ",font(40,True),WIDTH-135):
            d.text((75,y),ln,font=font(40,True),fill=(253,234,191))
            y+=54
        d.text((75,HEIGHT-146),"L. FRANK BAUM",font=font(23),fill=(225,222,212))
    else:
        d.line((48,HEIGHT-159,WIDTH-48,HEIGHT-159),fill=(143,119,82),width=2)
        for i, ln in enumerate(paragraph_lines(d,asset["title"],font(30,True),WIDTH-96)[:2]):
            w=d.textbbox((0,0),ln,font=font(30,True))[2]
            d.text(((WIDTH-w)//2,HEIGHT-137+i*36),ln,font=font(30,True),fill=(239,216,177))
        d.text((51,HEIGHT-44),"L. FRANK BAUM  ·  W. W. DENSLOW / 1900",
               font=font(15),fill=(166,169,168))
    canvas.save(dest, quality=92, optimize=True)

def original_music(seconds, target):
    rate=24000
    total=int((seconds+2)*rate)
    samples=np.zeros(total,dtype=np.float32)
    scale=[0,2,4,7,9,12]
    notes=[57,60,64,67,62,65,69,72,60,64,67,71]
    for bar, start in enumerate(np.arange(0, seconds+2, 2.9)):
        degrees=[0,2,4,2] if bar%3 else [0,2,5,4]
        root=notes[bar%len(notes)]
        for j,deg in enumerate(degrees):
            onset=start+j*.70
            freq=440.0*2**((root+scale[deg%len(scale)]-69)/12)
            a=int(onset*rate); n=min(int(.90*rate),total-a)
            if n<=0:continue
            t=np.arange(n,dtype=np.float32)/rate
            env=(1-np.exp(-t*45))*np.exp(-t*3.6)
            # Handmade gentle bell/piano-like tones; no imported copyrighted recording.
            tone=(np.sin(2*np.pi*freq*t)*.68 + np.sin(2*np.pi*2*freq*t)*.20+
                  np.sin(2*np.pi*3*freq*t)*.08)*env
            samples[a:a+n]+=tone.astype(np.float32)*0.052
    samples[:min(total,rate)]*=np.linspace(0,1,min(total,rate))
    k=min(total,int(2.0*rate))
    samples[-k:]*=np.linspace(1,0,k)
    samples=np.clip(samples,-.90,.90)
    with wave.open(str(target),"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
        w.writeframes((samples*32767).astype("<i2").tobytes())

def call(cmd):
    subprocess.run(cmd, check=True)

def video_assets(out, assets, voice_seconds):
    frames=out/"frames";frames.mkdir()
    for i,asset in enumerate(assets):
        make_frame(asset,out/"images"/asset["file"],frames/("frame_%02d.jpg"%(i+1)))
    cover=out/"COPERTINA.jpg"
    make_frame(assets[0],out/"images"/assets[0]["file"],cover,cover=True)
    return frames,cover

def render(out, frames, paragraphs, duration):
    # A paragraph is a narrative beat. Times follow the real spoken duration,
    # with proportional estimates explicitly documented, not passed off as ASR.
    lengths=[max(1,len(re.findall(r"\w+",p))) for p in paragraphs]
    total=sum(lengths)
    times=[duration*n/total for n in lengths]
    clips=out/"segments";clips.mkdir()
    files=[]
    for i,sec in enumerate(times):
        src=frames/("frame_%02d.jpg"%(i+1))
        dest=clips/("clip_%02d.mp4"%(i+1))
        moving=(i%5 not in (1,4))
        # Zoom affects only the safe mat border; the image itself is never cropped.
        vf=("zoompan=z='min(zoom+0.00006,1.022)':d=1:s=720x1280:fps=20,format=yuv420p"
            if moving else "format=yuv420p")
        call(["ffmpeg","-hide_banner","-v","error","-y",
              "-loop","1","-framerate",str(FPS),"-i",str(src),"-t",f"{sec:.3f}",
              "-vf",vf,"-r",str(FPS),"-c:v","libx264","-preset","veryfast",
              "-crf","21","-pix_fmt","yuv420p","-an",str(dest)])
        files.append(dest)
        print("Rendered scene",i+1,"seconds",round(sec,1),flush=True)
    listing=out/"segments.txt"
    listing.write_text("".join("file '"+p.resolve().as_posix()+"'\n" for p in files),encoding="utf-8")
    stitched=out/"VIDEO_SENZA_AUDIO.mp4"
    call(["ffmpeg","-hide_banner","-v","error","-y","-f","concat","-safe","0","-i",str(listing),
          "-c","copy",str(stitched)])
    soundtrack=out/"MUSICA_ORIGINALE.wav"
    original_music(duration,soundtrack)
    target=out/(SLUG+".mp4")
    call(["ffmpeg","-hide_banner","-v","error","-y","-i",str(stitched),
          "-i",str(out/"VOCE.wav"),"-i",str(soundtrack),
          "-filter_complex","[1:a]volume=1.0[v];[2:a]volume=0.42[m];[v][m]amix=inputs=2:duration=first:dropout_transition=0[a]",
          "-map","0:v:0","-map","[a]","-c:v","copy","-c:a","aac","-b:a","160k",
          "-shortest","-movflags","+faststart",str(target)])
    return target,times

def public_texts(out):
    posts={
    "FACEBOOK": """Quando Dorothy arriva a Oz, nessuno dei suoi nuovi amici sa davvero chi è.

Uno Spaventapasseri è convinto di non avere cervello. Un Boscaiolo di Latta sogna un cuore. Un Leone ha paura perfino della propria ombra. Eppure, per tutta la strada, ognuno di loro dimostra proprio la qualità che crede di non possedere.

Nel 1900 L. Frank Baum immaginò una fiaba americana diversa da quelle più cupe della tradizione europea: un mondo colorato, pieno di personaggi strani e domande semplici soltanto in apparenza. Le illustrazioni originali di W. W. Denslow fanno parte di quella stessa invenzione, con colori differenti per i vari paesi attraversati da Dorothy.

Il meraviglioso mago di Oz è anche la storia di chi cerca lontano ciò che ha già dentro di sé. Ma prima c'è una lunga strada gialla da percorrere, e nessuno può affrontarla da solo.

Il meraviglioso mago di Oz — L. Frank Baum, 1900.
Illustrazioni originali: W. W. Denslow, 1900.

#IlMagoDiOz #Libri #Classici #TraLePagine""",
    "INSTAGRAM": """Cervello, cuore, coraggio. I compagni di Dorothy attraversano Oz convinti che qualcuno debba regalare loro ciò che manca.

La storia racconta qualcosa di più sottile: lo Spaventapasseri trova soluzioni, il Boscaiolo si commuove per gli altri, il Leone prosegue anche quando trema. Dorothy intanto cerca una sola cosa: tornare dalle persone che ama.

Questa è la fiaba di L. Frank Baum nella sua atmosfera originale del 1900, accompagnata dalle immagini di W. W. Denslow, che diede un colore diverso ai paesi di Oz.

#IlMeravigliosoMagoDiOz #Letteratura #Fiabe #TraLePagine""",
    "TIKTOK": """Lo Spaventapasseri vuole un cervello. Il Boscaiolo di Latta desidera un cuore. Il Leone cerca il coraggio. E Dorothy vuole soltanto tornare a casa.

Nel romanzo di L. Frank Baum, il viaggio lungo la strada gialla rivela qualcosa che i protagonisti non riescono ancora a vedere di sé stessi. Una fiaba del 1900 che ha conservato intatta la sua meraviglia.

#MagoDiOz #Libri #TraLePagine""",
    "YOUTUBE": """Nel Kansas grigio di Dorothy, un ciclone solleva una piccola casa e la trasporta in un paese straordinario. Comincia così Il meraviglioso mago di Oz, il romanzo pubblicato da L. Frank Baum nel 1900.

Seguendo la strada di mattoni gialli, Dorothy incontra uno Spaventapasseri alla ricerca del cervello, un Boscaiolo di Latta che desidera un cuore e un Leone convinto di essere codardo. Tra papaveri incantati, scimmie alate e la Città di Smeraldo, i quattro amici scoprono che il misterioso Oz potrebbe essere molto diverso da come lo immaginavano.

Questo episodio ripercorre gli snodi del libro originale, non quelli del successivo film del 1939. Le immagini provengono dall'edizione storica illustrata da W. W. Denslow: un elemento essenziale dell'identità del romanzo, dove colori e ambientazioni contribuiscono al racconto.

Opera: The Wonderful Wizard of Oz (1900), L. Frank Baum.
Illustrazioni: W. W. Denslow, edizione 1900.
Fonte del testo e delle illustrazioni: Project Gutenberg, eBook 43936.
Musica: composizione originale di Tra le Pagine.
Voce narrante: Google Gemini Gacrux, utilizzo soggetto a verifica dei termini applicabili.

#IlMagoDiOz #LFrankBaum #Classici #TraLePagine"""
    }
    for p,txt in posts.items():
        (out/("POST_"+p+".txt")).write_text(txt+"\n",encoding="utf-8")
    return posts

def card(draw,xy,title,body,width):
    x,y=xy
    draw.rounded_rectangle((x,y,x+width,y+168),fill=(237,240,235),radius=15)
    draw.text((x+18,y+13),title,font=font(25,True),fill=(12,39,55))
    ft=font(19)
    for i,ln in enumerate(paragraph_lines(draw,body,ft,width-36)[:4]):
        draw.text((x+18,y+50+i*28),ln,font=ft,fill=(39,47,54))

def board(out, assets, paragraphs, seconds):
    w,h=1350,2350
    sheet=Image.new("RGB",(w,h),(246,240,226))
    d=ImageDraw.Draw(sheet)
    d.rectangle((0,0,w,200),fill=(10,35,53))
    d.text((54,24),"TRA LE PAGINE  /  STUDIO IBRIDO",font=font(27,True),fill=(231,217,190))
    d.text((54,78),"IL MERAVIGLIOSO MAGO DI OZ",font=font(43,True),fill=(255,239,208))
    d.text((54,140),"L. Frank Baum · Libri narrati · Illustrazioni W. W. Denslow, 1900",font=font(22),fill=(217,219,218))
    card(d,(46,225),"PROMESSA INIZIALE","Una bambina vola dentro una casa. Quando atterra, scopre che anche il coraggio può sembrare invisibile.",608)
    card(d,(685,225),"PERCHÉ QUESTO LIBRO","Fantasia riconoscibile, amicizia e ricerca di sé; immagini originali con identità cromatica del 1900.",617)
    card(d,(46,416),"STILE E REGIA","Illustrazioni originali, immagini integre, stacchi motivati e movimenti minimi. Nessun collage o volto tagliato.",608)
    card(d,(685,416),"PACCHETTO EDITORIALE","MP4, copertina, scene narrative distinte, musica originale, 4 post social, fonti e scheda testuale.",617)
    d.text((53,630),"STORYBOARD — SELEZIONE VISIVA",font=font(31,True),fill=(11,37,54))
    iw,ih=270,265
    for j,item in enumerate(assets[:12]):
        col,row=j%4,j//4
        x=48+col*327;y=688+row*430
        d.rounded_rectangle((x,y,x+iw+23,y+ih+94),radius=11,fill=(225,227,220))
        with Image.open(out/"images"/item["file"]) as pic:
            pic=pic.convert("RGB")
            pic.thumbnail((iw-10,ih-10),Image.Resampling.LANCZOS)
            sheet.paste(pic,(x+(iw-pic.width)//2,y+(ih-pic.height)//2))
        ttl=item["title"]
        for n,line in enumerate(paragraph_lines(d,ttl,font(18,True),iw-10)[:2]):
            d.text((x+12,y+ih+12+n*23),line,font=font(18,True),fill=(12,42,56))
    bottom=2050
    d.rounded_rectangle((46,bottom,w-46,h-52),radius=15,fill=(12,37,54))
    d.text((76,bottom+20),"FONTI, CREDITI, PUBBLICAZIONE",font=font(29,True),fill=(235,216,170))
    for i,line in enumerate([
        "Testo: The Wonderful Wizard of Oz, L. Frank Baum (1900).",
        "Immagini: W. W. Denslow, tavole dell'edizione originale (1900).",
        "Fonte primaria: Project Gutenberg — eBook 43936.",
        "Voce: Google Gemini Gacrux. Musica originale Tra le Pagine.",
        "Stato: render completo, revisione artistica e diritti da confermare."
    ]):
        d.text((76,bottom+71+37*i),line,font=font(19),fill=(234,234,224))
    sheet.save(out/"SCHEDA_PRESENTAZIONE.jpg",quality=90,optimize=True)

def dossier(out,assets,paragraphs,times,seconds,posts):
    lines=["# TRA LE PAGINE — IL MERAVIGLIOSO MAGO DI OZ","",
           "- Soggetto: L. Frank Baum, The Wonderful Wizard of Oz (1900)",
           "- Illustrazioni originali: W. W. Denslow (1900)",
           "- Format: libri e racconti con voce narrata italiana",
           "- Voce: Google Gemini Gacrux (effettiva, non simulata)",
           "- Durata voce misurata: %.2f secondi"%seconds,
           "- Sequenze originali selezionate: %d"%len(assets),
           "- Fonte verificabile: "+SOURCE,
           "- Stato: rendered_needs_review; nessuna pubblicazione automatica",
           "",
           "## Hook","Una casa attraversa il cielo. Dentro, una bambina tiene stretto un cane nero.",
           "",
           "## Perché questo libro",
           "Una fiaba con numerosi ambienti e personaggi distinti, resa visivamente coerente dalle tavole di Denslow.",
           "",
           "## Piano visivo V38: non uno stampino",
           "La durata viene dalla voce effettiva e le scene seguono i paragrafi narrativi.",
           "Le immagini sono prese dal libro originale e mostrate integralmente nel quadro.",
           "I tempi di frase sono stimati dalla proporzione delle parole del copione, non verificati con ASR.",
           "Il numero di illustrazioni viene da questa struttura narrativa, non è la nuova regola per altri video.",
           "",
           "## Storyboard, immagini e diritti"
           ]
    at=0.
    for i,(asset,text,sec) in enumerate(zip(assets,paragraphs,times),1):
        lines += ["","### Scena %02d — %s"%(i,asset["title"]),
                  "- Timeline stimata: %.1f–%.1f s"%(at,at+sec),
                  "- Narrazione: "+text,
                  "- Immagine: "+asset["file"],
                  "- Descrizione archivio: "+asset["alt"],
                  "- Fonte diretta: "+asset["url"],
                  "- Autore e data: W. W. Denslow, 1900",
                  "- SHA256: "+asset["sha256"]]
        at+=sec
    lines += ["","## Verifica diritti",
              "Baum (m. 1919) e Denslow (m. 1915): opere storicamente di pubblico dominio negli USA.",
              "Per l'Italia e ogni territorio commerciale verificare le regole locali e le condizioni della scansione.",
              "La voce Gacrux richiede verifica delle condizioni Google applicabili; i crediti non sostituiscono la licenza.",
              "",
              "## Descrizioni social pronte da revisionare"]
    for key,body in posts.items():
        lines += ["","### "+key,"",body]
    lines += ["","## File",SLUG+".mp4","COPERTINA.jpg","SCHEDA_PRESENTAZIONE.jpg",
              "FONTI_ILLUSTRAZIONI.json","VOCE.wav","MUSICA_ORIGINALE.wav","VIDEO_SOLO_MP4.zip"]
    (out/"SCHEDA_TESTO.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    write_json(out/"DOSSIER_SITO.json",{
        "publicTitle": TITLE, "bookAuthor": AUTHOR, "publicationYear":"1900",
        "seriesTitle":"Classici che parlano ancora", "category":"Libri e racconti",
        "project":"Tra le Pagine", "language":"it",
        "hook":paragraphs[0], "rightsStatus":"da_verificare",
        "publicationStatus":"da_revisionare","facebook":posts["FACEBOOK"],
        "instagram":posts["INSTAGRAM"],"tiktok":posts["TIKTOK"],"youtube":posts["YOUTUBE"],
        "sources":SOURCE, "imageCredits":ARTIST+" — edizione del 1900",
        "voiceCredits":"Google Gemini Gacrux","musicTitle":"Tema originale per Oz",
        "musicAuthor":"Tra le Pagine","musicLicense":"composizione originale, revisione metadata necessaria",
        "storyboard":"\n".join(a["title"] for a in assets),
        "socialInstructions":"Privato: rivedere testi e diritti prima della pubblicazione",
        "authoring":"original_episode_copy",
        "note":"Importazione R2 NON effettuata automaticamente; non inventare lo stato remoto."})

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    script=(ROOT/"voice_jobs/oz_20261026.txt").read_text(encoding="utf-8").strip()
    paragraphs=[x.strip() for x in re.split(r"\n\s*\n",script) if x.strip()]
    if len(paragraphs)!=len(BEATS):
        raise RuntimeError("Narration/visual beat count mismatch: %d vs %d"%(len(paragraphs),len(BEATS)))
    (out/"COPIONE.txt").write_text(script+"\n",encoding="utf-8")
    assets=collect_assets(out/"images")  # All source files BEFORE any API calls.
    frames,cover=video_assets(out,assets,0)
    print("Valid original images acquired; generating approved Gacrux voice.",flush=True)
    sys.path.insert(0,str(ROOT/"src"))
    from gemini_voice import synthesize, SAMPLE_RATE
    audio,_=synthesize(script,out)
    seconds=len(audio)/SAMPLE_RATE
    if seconds<90 or seconds>480:
        raise RuntimeError("Unexpected real speech length: %.1f"%seconds)
    target,times=render(out,frames,paragraphs,seconds)
    posts=public_texts(out)
    board(out,assets,paragraphs,seconds)
    dossier(out,assets,paragraphs,times,seconds,posts)
    for p in [target,cover,out/"SCHEDA_PRESENTAZIONE.jpg",out/"SCHEDA_TESTO.md"]:
        if not p.is_file() or p.stat().st_size<5000:
            raise RuntimeError("Mandatory deliverable missing: "+str(p))
    # The lightweight Android ZIP contains only the complete MP4.
    with zipfile.ZipFile(out/"VIDEO_SOLO_MP4.zip","w",compression=zipfile.ZIP_STORED) as zipout:
        zipout.write(target,target.name)
    # Keep compact final deliveries, not temporary per-shot encodes and boards.
    shutil.rmtree(out/"segments", ignore_errors=True)
    shutil.rmtree(out/"frames", ignore_errors=True)
    (out/"VIDEO_SENZA_AUDIO.mp4").unlink(missing_ok=True)
    (out/"segments.txt").unlink(missing_ok=True)
    status={"status":"rendered_needs_review", "video":target.name,
            "duration_voice_seconds":seconds,"scenes":len(assets),
            "source":SOURCE,"frame_images":"intact_original_1900_illustrations",
            "narration":"Google Gemini Gacrux",
            "timing":"paragraph_duration_estimated_from_spoken_word_ratios",
            "commercial_clearance":"not_finally_certified",
            "site_uploaded":False,"social_published":False}
    write_json(out/"STATUS.json",status)
    print(json.dumps(status,ensure_ascii=False,indent=2),flush=True)

if __name__=="__main__":
    main()
