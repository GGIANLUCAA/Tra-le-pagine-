#!/usr/bin/env python3
"""Delitto e castigo: archival still research with the existing free V7 adapter.
Scenes are *illustrative* historical images, not evidence or film footage.
No synthetic clipart, no Google TTS and no renderer changes.
Run before a video workflow: fails closed if too few suitable images are found.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import time
import re
import html
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps, UnidentifiedImageError
from archivio_media_v7 import discover, download_approved

SEARCHES = {
    1: ("St Petersburg painting", "Saint Petersburg painting", "Saint Petersburg landscape"),
    2: ("Nevsky Prospekt", "Saint Petersburg canal", "Saint Petersburg historical"),
    3: ("old room interior painting", "poor room interior", "small room painting"),
    4: ("books candle painting", "old books candle", "library interior painting"),
    5: ("old woman portrait painting", "elderly woman portrait", "old woman painting"),
    6: ("old staircase interior", "wooden door historical", "stairway old building"),
    7: ("sick person painting", "bedroom painting interior", "old bed painting"),
    8: ("19th century man portrait painting", "Russian man portrait painting", "gentleman painting"),
    9: ("Russian woman portrait painting", "young woman painting", "woman portrait painting"),
   10: ("two people painting interior", "woman and man painting", "prayer woman painting"),
   11: ("Siberia winter landscape", "Russia winter snow painting", "Siberian snow"),
   12: ("sunrise Russia landscape painting", "winter sunrise painting", "Russian landscape sun"),
}
BAD_TITLE = ("flag", "icon", "logo", "coats of arms", "stamp", "poster", "book cover", "screenshot", "map", "diagram")
SCENE_COUNT = 12


def quality_photo(raw: bytes):
    with Image.open(io.BytesIO(raw)) as im:
        if im.width < 380 or im.height < 350:
            raise ValueError("Immagine a risoluzione insufficiente")
        if im.width*im.height>35_000_000:
            raise ValueError("Immagine eccessivamente grande")
        image=ImageOps.exif_transpose(im).convert("RGB")
    return image


def grade_photo(src: Image.Image, output: Path, mood: str):
    """Natural historical still; original art stays in view, gently moving backdrop."""
    target=(1080,1920)
    backdrop=ImageOps.fit(src,target,method=Image.Resampling.LANCZOS)
    backdrop=backdrop.filter(ImageFilter.GaussianBlur(32))
    backdrop=ImageEnhance.Brightness(backdrop).enhance(.52)
    inset=ImageOps.contain(src,(1020,1810),method=Image.Resampling.LANCZOS)
    inset=ImageEnhance.Color(inset).enhance(.82 if mood!="hope" else .95)
    if mood=="cool":
        inset=ImageEnhance.Brightness(inset).enhance(.91)
    x=(1080-inset.width)//2
    y=(1920-inset.height)//2
    backdrop.paste(inset,(x,y))
    output.parent.mkdir(parents=True,exist_ok=True)
    backdrop.save(output,quality=93,optimize=True)
    if output.stat().st_size<35_000:
        raise ValueError("Risultato JPEG troppo piccolo")
    return {"file":output.name,"width":1080,"height":1920,"bytes":output.stat().st_size}


def commons_results(query):
    """Query Wikimedia Commons directly; thumbnail artwork stays with the original author."""
    qs=urllib.parse.urlencode({
        "action":"query","generator":"search","gsrsearch":query,
        "gsrnamespace":"6","gsrlimit":"16","prop":"imageinfo",
        "iiprop":"url|size|mime|extmetadata","iiurlwidth":"1200",
        "format":"json","formatversion":"2",
    })
    req=urllib.request.Request(
        "https://commons.wikimedia.org/w/api.php?"+qs,
        headers={"Accept":"application/json","User-Agent":
                 "TraLePagineBookVideo/1.0 (educational audiovisual research; github.com/GGIANLUCAA/Tra-le-pagine-)"})
    with urllib.request.urlopen(req,timeout=12) as response:
        payload=response.read(2_000_001)
        if len(payload)>2_000_000:raise ValueError("Commons API response too large")
        data=json.loads(payload)
    out=[]
    for page in data.get("query",{}).get("pages",[]):
        info=(page.get("imageinfo") or [{}])[0]
        if info.get("mime") not in ("image/jpeg","image/png","image/webp"):
            continue
        if int(info.get("width",0))<600 or int(info.get("height",0))<400:
            continue
        metadata=info.get("extmetadata") or {}
        def val(name):
            return str((metadata.get(name) or {}).get("value",""))
        short=val("LicenseShortName").casefold()
        licurl=val("LicenseUrl")
        if not (("public domain" in short or "pd-" in short or "cc0" in short)
                or ("cc by" in short and "sa" not in short and "nc" not in short and "nd" not in short)):
            continue
        source=info.get("thumburl") or info.get("url") or ""
        if not source.startswith("https://upload.wikimedia.org/"):
            continue
        out.append({
            "asset_title":str(page.get("title",""))[:200],
            "author":re.sub(r"<[^>]*>","",html.unescape(val("Artist")))[:150] or "Autore da verificare",
            "license":short,"license_url":licurl,
            "source_url":"https://commons.wikimedia.org/wiki/"+urllib.parse.quote(
                str(page.get("title","")).replace(" ","_")),
            "download_url":source
        })
    return out


def commons_download(item):
    """Only allowed Wikimedia CDN, bounded JPEG/PNG/WEBP; do not accept redirects outside CDN."""
    url=item["download_url"]
    if urllib.parse.urlsplit(url).hostname!="upload.wikimedia.org":
        raise ValueError("Host Wikimedia inatteso.")
    req=urllib.request.Request(url,headers={"User-Agent":"TraLePagineBookVideo/1.0"})
    with urllib.request.urlopen(req,timeout=16) as res:
        if urllib.parse.urlsplit(res.url).hostname!="upload.wikimedia.org":
            raise ValueError("Redirect fuori da Wikimedia.")
        if int(res.headers.get("Content-Length","0"))>12_000_000:
            raise ValueError("File troppo grande.")
        raw=res.read(12_000_001)
    if len(raw)>12_000_000 or len(raw)<500:
        raise ValueError("Immagine troppo grande o vuota.")
    return raw,hashlib.sha256(raw).hexdigest()


# Historically grounded illustrations, recorded on Wikimedia Commons in the
# category Crime and Punishment. Avoid unrelated search results and future models.
CURATED={
  1:"Karazin3.jpg",
  2:"Dostojevski Misdaad en straf 02.jpg",
  3:"Karazin1.jpg",
  4:"Karazin2.jpg",
  5:"Protsentshitsa.jpg",
  6:"AVRO Televisie De Student Raskolnikoff gebaseerd op een verhaal van Dostojevs, Bestanddeelnr 913-0363.jpg",
  7:"AVRO Televisie De Student Raskolnikoff gebaseerd op een verhaal van Dostojevs, Bestanddeelnr 913-0364.jpg",
  8:"AVRO Televisie De Student Raskolnikoff gebaseerd op een verhaal van Dostojevs, Bestanddeelnr 913-0365.jpg",
  9:"Grabar Crime and Punishment Sonya visiting Marmeladov 1894.jpg",
  10:"Klodt Michail Petrovich - Raskolnikov and Marmeladov.jpg",
  11:"Nicolae Vermont - Suflete slave (Crima si pedeapsa).jpg",
  12:"AVRO Televisie. De Student Raskolnikoff gebaseerd op een verhaal van Dostojevs, Bestanddeelnr 913-0367.jpg",
}


def wikimedia_original_file_url(name: str):
    """Commons stable file name + Wikimedia storage MD5 directory."""
    if not name.endswith((".jpg",".jpeg",".JPG")) or len(name)>200:
        raise ValueError("Invalid curated file name")
    filename=name.replace(" ","_")
    digest=hashlib.md5(filename.encode("utf-8")).hexdigest()
    return "https://upload.wikimedia.org/wikipedia/commons/"+digest[0]+"/"+digest[:2]+"/"+urllib.parse.quote(filename,safe="()")


def download_curated(name,delay=9):
    """Respect Commons CDN: one request every several seconds and retry 429."""
    from urllib.error import HTTPError
    url=wikimedia_original_file_url(name)
    for i in range(4):
        time.sleep(delay if i==0 else min(90,30*(i+1)))
        try:
            data,sha=commons_download({"download_url":url})
            return data,sha,url
        except HTTPError as e:
            if e.code in (429,502,503):
                print("Wikimedia in pausa",e.code,"file",name[:40],"tentativo",i+1,flush=True)
                continue
            raise
    raise RuntimeError("Commons rate limit after four controlled attempts")


def find_images(episode: Path, *, sleep=0.4):
    images=episode/"images"
    images.mkdir(parents=True,exist_ok=True)
    provenance=[]
    used_hashes=set()
    for idx,queries in SEARCHES.items():
        chosen=None
        attempts=[]
        # Curated, book-specific artwork is first choice, not unrelated paintings.
        try:
            selected=CURATED[idx]
            raw,digest,url=download_curated(selected)
            original=quality_photo(raw)
            dest=images/f"scena_{idx:02d}.jpg"
            result=grade_photo(original,dest,"hope" if idx==12 else "cool")
            chosen={"asset":idx,"query":"curated Crime and Punishment historic illustration",
                    "search_topic":SEARCHES[idx][0],
                    "title":selected,"author":"Autore indicato nella pagina originale Wikimedia",
                    "source_url":"https://commons.wikimedia.org/wiki/File:"+
                                 urllib.parse.quote(selected.replace(" ","_")),
                    "license":"Verificare pagina Commons","license_url":
                    "https://commons.wikimedia.org/wiki/File:"+
                                 urllib.parse.quote(selected.replace(" ","_")),
                    "sha256_original":digest,
                    "display_type":"illustrazione storica del romanzo o foto di sua rappresentazione, non scena reale",
                    **result}
            used_hashes.add(digest)
        except Exception as e:
            attempts.append("Curated "+CURATED[idx]+": "+str(e)[:120])
        if not chosen:
            print("CURATED NON DISPONIBILE",idx,attempts[-1],flush=True)
        if not chosen:
          for query in queries:
            # FIRST: direct Commons API (independent of Openverse availability).
            try:
                suggestions=commons_results(query)
            except Exception as e:
                attempts.append(f"Commons {query}: {str(e)[:100]}")
                suggestions=[]
            for item in suggestions:
                title=item["asset_title"].casefold()
                if any(word in title for word in BAD_TITLE):
                    continue
                try:
                    raw,digest=commons_download(item)
                    if digest in used_hashes:
                        continue
                    original=quality_photo(raw)
                    dest=images/f"scena_{idx:02d}.jpg"
                    result=grade_photo(original,dest,"hope" if idx==12 else "cool")
                    chosen={"asset":idx,"query":query,"search_topic":SEARCHES[idx][0],
                            "title":item["asset_title"],"author":item["author"],
                            "source_url":item["source_url"],"license":item["license"],
                            "license_url":item["license_url"],
                            "sha256_original":digest,
                            "display_type":"opera o fotografia illustrativa, non scena reale del romanzo",
                            **result}
                    used_hashes.add(digest)
                    break
                except Exception as e:
                    attempts.append(f"Commons thumb: {str(e)[:95]}")
            if chosen:
                break
            time.sleep(sleep)
        if not chosen:
            # Secondary fallback: Openverse, limited to one query because
            # the anonymous service can time out during production.
            query=queries[0]
            try:
                from tempfile import TemporaryDirectory
                suggestions=discover("openverse","image",query,6)
                for entry in suggestions:
                    if any(word in entry["title"].casefold() for word in BAD_TITLE):
                        continue
                    try:
                        with TemporaryDirectory(prefix="tlp08_") as t:
                            metadata=download_approved(entry,Path(t))
                            digest=metadata["sha256"]
                            if digest in used_hashes:continue
                            raw=(Path(t)/metadata["file"]).read_bytes()
                            original=quality_photo(raw)
                            dest=images/f"scena_{idx:02d}.jpg"
                            result=grade_photo(original,dest,"hope" if idx==12 else "cool")
                            chosen={"asset":idx,"query":query,"search_topic":SEARCHES[idx][0],
                                    "title":entry["title"],"author":entry["author"],
                                    "source_url":entry["source_url"],
                                    "license":entry["license"],"license_url":entry["license_url"],
                                    "sha256_original":digest,
                                    "display_type":"opera o fotografia illustrativa, non scena reale del romanzo",
                                    **result}
                            used_hashes.add(digest)
                            break
                    except Exception as e:
                        attempts.append(f"Openverse file: {str(e)[:95]}")
            except Exception as e:
                attempts.append(f"Openverse fallback: {str(e)[:100]}")
        if not chosen:
            print("SCENA FALLITA",idx,"ERRORI:",attempts[-10:],flush=True)
            report=episode/"PROVENIENZA_IMMAGINI.json"
            report.write_text(json.dumps({"images":provenance,"failed_scene":idx,
                    "search_errors":attempts[-8:]},
                    indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
            raise RuntimeError(f"Nessuna illustrazione reale valida per scena {idx:02d};"
                               " non avviare la voce.")
        provenance.append(chosen)
        print("SCENA",str(idx).zfill(2),"OK",chosen["title"][:62],chosen["bytes"],flush=True)
    (episode/"PROVENIENZA_IMMAGINI.json").write_text(
        json.dumps({"episode":episode.name,"images":provenance,
                    "visual_note":"Immagini illustrative di archivio, da verificare manualmente."},
                   ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return provenance


def storyboard_contact_sheet(episode):
    from PIL import ImageDraw, ImageFont
    files=sorted((episode/"images").glob("scena_*.jpg"))
    canvas=Image.new("RGB",(960,((len(files)+3)//4)*470),(15,35,44))
    draw=ImageDraw.Draw(canvas)
    for i,f in enumerate(files):
        with Image.open(f) as original:
            thumb=ImageOps.contain(original,(228,406),method=Image.Resampling.LANCZOS)
            x=(i%4)*240+(240-thumb.width)//2
            y=(i//4)*470+6
            canvas.paste(thumb,(x,y))
        draw.text(((i%4)*240+12,(i//4)*470+418),f"SCENA {i+1:02d}",
                  fill=(238,207,164))
    target=episode/"STORYBOARD_VISIVO.jpg"
    canvas.save(target,quality=85,optimize=True)
    return target


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--episode",default="episodes/08_delitto_e_castigo")
    ap.add_argument("--preview-only",action="store_true")
    args=ap.parse_args()
    path=Path(args.episode)
    if path.name!="08_delitto_e_castigo" or not path.is_dir():
        raise SystemExit("Episodio errato o mancante")
    found=find_images(path)
    collage=storyboard_contact_sheet(path)
    print("SCENE COMPLETE:",len(found),"/",SCENE_COUNT,"collage:",collage)
    print("NESSUNA VOCE GENERATA IN QUESTO PASSAGGIO.")


if __name__=="__main__":
    main()
