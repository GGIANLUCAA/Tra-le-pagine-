#!/usr/bin/env python3
"""Rembrandt Cinema V6: selective high-resolution Wikimedia Commons oil paintings.
Separate fallback for Art Institute image CDN HTTP 403 (does not modify old engines).
Each file must have Commons license metadata that authorizes reuse, or be skipped.
"""
from __future__ import annotations
import hashlib, io, json, time, urllib.parse
from pathlib import Path
from PIL import Image,ImageOps
from export_caravaggio_v6 import metadata, valid_license, get

WORKS=[
 ("The Night Watch","Rembrandt Harmensz. van Rijn - Nachtwacht - Google Art Project.jpg"),
 ("The Jewish Bride","Rembrandt Harmensz. van Rijn - Portret van een paar als oudtestamentische figuren, genaamd 'Het Joodse bruidje' - Google Art Project.jpg"),
 ("The Return of the Prodigal Son","Rembrandt - The Return of the Prodigal Son.jpg"),
 ("The Anatomy Lesson of Dr. Nicolaes Tulp","Rembrandt - The Anatomy Lesson of Dr Nicolaes Tulp.jpg"),
 ("Self Portrait, 1658","Rembrandt - Zelfportret - Google Art Project.jpg"),
 ("Self Portrait, 1659","Rembrandt van Rijn - Self-Portrait - Google Art Project.jpg"),
 ("Young Self Portrait","Rembrandt Harmensz. van Rijn - Zelfportret op jeugdige leeftijd - Google Art Project.jpg"),
 ("Self Portrait as Apostle Paul","Rembrandt Harmensz. van Rijn - Zelfportret als de apostel Paulus - Google Art Project.jpg"),
 ("Rembrandt and Saskia","Rembrandt - Rembrandt and Saskia in the Scene of the Prodigal Son - Google Art Project.jpg"),
 ("Aristotle and Homer","Rembrandt - Aristotle with a Bust of Homer - Google Art Project.jpg"),
 ("Belshazzar's Feast","Belshazzar’s feast, by Rembrandt.jpg"),
 ("Self Portrait with Velvet Beret","Rembrandt - Self-Portrait with Velvet Beret - Google Art Project.jpg"),
 ("Selfportrait - Rijksmuseum","Rembrandt Harmensz. van Rijn - Selfportrait - Google Art Project.jpg"),
 ("Large Self Portrait","Rembrandt Harmenszoon van Rijn - Large Self-Portrait - Google Art Project.jpg"),
 ("Self Portrait with Beret","Rembrandt Harmensz. van Rijn - Self-Portrait - Google Art Project.jpg"),
 ("Anatomy Lesson — alternate","Rembrandt, la lezione di anatomia del dottor tulp, 1632, 01.jpg"),
 ("The Blinding of Samson","Rembrandt - The Blinding of Samson - WGA19097.jpg"),
 ("The Anatomy Lesson - alternate","Rembrandt - The Anatomy Lesson of Dr. Nicolaes Tulp.jpg"),
 ("Aristotle — second photograph","Rembrandt - Aristotle with a Bust of Homer - WGA19232.jpg"),
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
            records.append({"id":ident,"title":title,"artist":"Rembrandt van Rijn",
                "source":"Wikimedia Commons, sourced reproduction of authentic Rembrandt van Rijn painting",
                "url":"https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(fn.replace(" ","_")),
                "image_url":link,"original_file":fn,"license":license_name,
                "license_url":str(ext.get("LicenseUrl",{}).get("value","")),
                "file":str(output),"width":im.width,"height":im.height,
                "sha256":hashlib.sha256(output.read_bytes()).hexdigest(),
                "attribution":str(ext.get("Attribution",{}).get("value",""))[:1200],
                "rights_checked":True})
            print("REMBRANDT OILS",len(records),"/",len(WORKS),title,im.size,license_name,flush=True)
        except Exception as e:
            failures.append({"title":title,"file":fn,"error":str(e)[:250]})
            print("REMBRANDT SOURCE SKIPPED",title,str(e)[:190],flush=True)
        time.sleep(.7)
    if len(records)<12:
        raise RuntimeError("Insufficient Rembrandt oil painting reproductions: "+str(len(records))+" / 12; "+json.dumps(failures,ensure_ascii=False)[:1000])
    return records,{"artic":"HTTP 403 on museum image CDN; switched to licensed Commons originals"},failures,[]
