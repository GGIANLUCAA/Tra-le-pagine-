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
        if im.width < 500 or im.height < 380:
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


def find_images(episode: Path, *, sleep=0.4):
    images=episode/"images"
    images.mkdir(parents=True,exist_ok=True)
    provenance=[]
    used_hashes=set()
    for idx,queries in SEARCHES.items():
        chosen=None
        attempts=[]
        for query in queries:
            # All sources are constrained to Openverse-indexed Wikimedia.
            # The full license must be checked in the original; this is an editorial preview.
            try:
                suggestions=discover("openverse","image",query,12)
            except Exception as e:
                attempts.append(f"API {query}: {str(e)[:100]}")
                time.sleep(max(1,sleep))
                continue
            for entry in suggestions:
                title=entry["title"].casefold()
                if any(word in title for word in BAD_TITLE):
                    continue
                try:
                    from tempfile import TemporaryDirectory
                    with TemporaryDirectory(prefix="tlp_08_") as t:
                        metadata=download_approved(entry,Path(t))
                        digest=metadata["sha256"]
                        if digest in used_hashes:
                            continue
                        raw=(Path(t)/metadata["file"]).read_bytes()
                        original=quality_photo(raw)
                        dest=images/f"scena_{idx:02d}.jpg"
                        result=grade_photo(original,dest,"hope" if idx==12 else "cool")
                        chosen={
                            "asset":idx,"query":query,"search_topic":SEARCHES[idx][0],
                            "title":entry["title"],"author":entry["author"],
                            "source_url":entry["source_url"],
                            "license":entry["license"],"license_url":entry["license_url"],
                            "sha256_original":digest,
                            "display_type":"opera o fotografia illustrativa, non scena reale del romanzo",
                            **result
                        }
                        used_hashes.add(digest)
                        break
                except Exception as e:
                    attempts.append(f"{entry['id']}: {str(e)[:95]}")
            if chosen:
                break
            time.sleep(sleep)
        if not chosen:
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
