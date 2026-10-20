#!/usr/bin/env python3
"""Monet Cinema V6: selective high-resolution Wikimedia Commons museum paintings.
Separate fallback for Art Institute image CDN HTTP 403 (does not modify old engines).
Each file must have Commons license metadata that authorizes reuse, or be skipped.
"""
from __future__ import annotations
import hashlib, io, json, time, urllib.parse
from pathlib import Path
from PIL import Image,ImageOps
from export_caravaggio_v6 import metadata, valid_license, get

WORKS=[
 ("Impression, Sunrise","Monet - Impression, Sunrise.jpg"),
 ("Waterlilies in blue","Claude Monet - Waterlilies - Google Art Project.jpg"),
 ("The Japanese Bridge","Claude Monet - The Japanese Bridge - Google Art Project.jpg"),
 ("Haystacks","Claude Monet - Haystacks - Google Art Project.jpg"),
 ("Rouen Cathedral, Sunlight","Claude Monet - Rouen Cathedral, West Façade, Sunlight - Google Art Project.jpg"),
 ("Rouen Cathedral, Grey Weather","Claude Monet - The Cathedral in Rouen. The portal, Grey Weather - Google Art Project.jpg"),
 ("Waterloo Bridge, Sunlight","Claude Monet - Waterloo Bridge - Google Art Project.jpg"),
 ("Waterloo Bridge, London","Claude Monet - Waterloo Bridge in London - Google Art Project.jpg"),
 ("Woman with a Parasol","Claude Monet, Woman with a Parasol - Madame Monet and Her Son, 1875, NGA 61379.jpg"),
 ("Poplars","Claude Monet, French - Poplars - Google Art Project.jpg"),
 ("Garden at Sainte-Adresse","Garden at Sainte-Adresse.JPG"),
 ("Argenteuil, 1872","Claude Monet, Argenteuil, c. 1872, NGA 52186.jpg"),
 ("Haystacks at Summer's End","Claude Monet - Haystacks, end of Summer - Google Art Project.jpg"),
 ("Japanese Footbridge","Claude Monet - The Japanese bridge - Google Art Project.jpg"),
 ("Snow at Argenteuil","Claude Monet - Voir le d'Argenteuil (1874-75).jpg"),
 ("Water Lilies, late period","Claude Monet, Water Lilies, ca. 1915-1926.jpg"),
 ("Water Lilies, The Met","Water Lilies MET DT1856.jpg"),
 ("Water Lilies and Japanese Bridge","Water-Lilies-and-Japanese-Bridge-(1897-1899)-Monet.jpg"),
 ("Rouen Cathedral, Portal","Claude Monet - Rouen Cathedral, West Façade - Google Art Project.jpg"),
 ("Water Lilies, Agapanthus","Water Lilies (Agapanthus), by Claude Monet, Cleveland Museum of Art, 1960.81.jpg"),
 ("San Giorgio Maggiore, Twilight","Amgueddfa Cymru - San Giorgio Maggiore yn y Gwyll - San Giorgio Maggiore, Twilight - 220983.jpeg"),
 ("Snow at Argenteuil, 1875","Claude monet, neve ad argenteuil, 1875 ca..JPG"),
]
def export(folder):
    folder=Path(folder);dst=folder/"original_images";dst.mkdir(parents=True,exist_ok=True)
    records=[];failures=[]
    for title,fn in WORKS:
        try:
            info=metadata(fn,width=2500)
            if not valid_license(info):
                raise RuntimeError("No verified public domain / CC BY permission")
            ext=info.get("extmetadata") or {}
            license_name=ext.get("LicenseShortName",{}).get("value","")
            link=info.get("thumburl") or info.get("url")
            try:
                data=get(link,max_bytes=28_000_000)
            except Exception:
                info=metadata(fn,width=1900)
                link=info.get("thumburl") or info.get("url")
                data=get(link,max_bytes=20_000_000)
            with Image.open(io.BytesIO(data)) as original:
                original.load()
                im=ImageOps.exif_transpose(original).convert("RGB")
            if min(im.size)<650:raise RuntimeError("Image is too small: "+str(im.size))
            if max(im.size)>3700:im.thumbnail((3700,3700),Image.Resampling.LANCZOS)
            ident=hashlib.sha256(fn.encode("utf-8")).hexdigest()[:18]
            output=dst/(ident+".jpg");im.save(output,quality=94,subsampling=0,optimize=True)
            records.append({"id":ident,"title":title,"artist":"Claude Monet",
                "source":"Wikimedia Commons, sourced reproduction of authentic Claude Monet painting",
                "url":"https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(fn.replace(" ","_")),
                "image_url":link,"original_file":fn,"license":license_name,
                "license_url":str(ext.get("LicenseUrl",{}).get("value","")),
                "file":str(output),"width":im.width,"height":im.height,
                "sha256":hashlib.sha256(output.read_bytes()).hexdigest(),
                "attribution":str(ext.get("Attribution",{}).get("value",""))[:1200],
                "rights_checked":True})
            print("MONET CURATED",len(records),"/",len(WORKS),title,im.size,license_name,flush=True)
        except Exception as e:
            failures.append({"title":title,"file":fn,"error":str(e)[:250]})
            print("MONET SOURCE SKIPPED",title,str(e)[:190],flush=True)
        time.sleep(.7)
    if len(records)<12:
        raise RuntimeError("Insufficient Monet museum painting reproductions: "+str(len(records))+" / 12; "+json.dumps(failures,ensure_ascii=False)[:1000])
    return records,{"artic":"HTTP 403 on museum image CDN; switched to licensed Commons originals"},failures,[]
