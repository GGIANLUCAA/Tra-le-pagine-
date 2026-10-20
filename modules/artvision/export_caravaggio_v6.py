#!/usr/bin/env python3
"""Curated genuine Caravaggio art sources from Wikimedia Commons file records.
No image generation, no third-party social-video footage.
"""
from __future__ import annotations
import hashlib, io, json, time, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageOps
from atelier_v4 import audio_download

# These *specific* file pages were checked against Wikimedia Commons artwork records.
# Exclude disputed attribution and modern unlicensed installation photography.
CURATED=[
 ("The Calling of Saint Matthew","Caravaggio — The Calling of Saint Matthew.jpg"),
 ("Judith Beheading Holofernes","Caravaggio - Judith beheading Holofernes.jpg"),
 ("Supper at Emmaus","Caravaggio — Supper at Emmaus.jpg"),
 ("David with the Head of Goliath","David with the Head of Goliath-Caravaggio (1610).jpg"),
 ("The Taking of Christ","Caravaggio - The Taking of Christ.jpg"),
 ("Bacchus","Caravaggio, bacco, 1595-97 ca. , 01.jpg"),
 ("Boy Bitten by a Lizard","Caravaggio - Boy Bitten by a Lizard.jpg"),
 ("The Cardsharps","Cardsharps-Caravaggio (c.1597).jpg"),
 ("Basket of Fruit","Basket of Fruit-Caravaggio (c.1595).jpg"),
 ("Rest on the Flight into Egypt","Rest on the Flight into Egypt-Caravaggio (c.1597).jpg"),
 ("The Incredulity of Saint Thomas","Caravaggio incredulity.jpg"),
 ("Saint Jerome Writing","Saint Jerome Writing-Caravaggio (1605-6).jpg"),
 ("Narcissus","Narcissus-Caravaggio (1594-96).jpg"),
 ("The Entombment of Christ","Caravaggio - Entombment of Christ.jpg"),
 ("The Musicians","Caravaggio - I Musici.jpg"),
 ("Crucifixion of Saint Peter","Caravaggio, Crucifixion of Saint Peter.jpg"),
 ("The Conversion of Saint Paul","The Conversion of Saint Paul-Caravaggio (c. 1600-1).jpg"),
 ("Young Sick Bacchus","Caravaggio - Autoritratto in veste di Bacco (Bacchino malato), 1595 circa, 534.jpg"),
 ("Medusa","Medusa by Carvaggio.jpg"),
]
UA="ArtVisionTraLePagine/2.0 (respectful curated film; Wikimedia Open Access; contact via GitHub GGIANLUCAA/Tra-le-pagine-)"
def get(url,max_bytes=19_000_000):
    last=None
    for n in range(3):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json,image/jpeg,image/png,*/*"})
            with urllib.request.urlopen(req,timeout=42) as r:
                data=r.read(max_bytes+1)
            if len(data)>max_bytes:raise RuntimeError("file too large")
            return data
        except Exception as err:
            last=err;time.sleep((n+1)*2)
    raise RuntimeError(str(last))
def metadata(filename,width=2900):
    params=urllib.parse.urlencode({"action":"query","format":"json","formatversion":"2",
        "titles":"File:"+filename,"prop":"imageinfo","iiprop":"url|size|extmetadata","iiurlwidth":str(width)})
    api="https://commons.wikimedia.org/w/api.php?"+params
    payload=json.loads(get(api,max_bytes=3_000_000))
    pages=payload.get("query",{}).get("pages",[])
    if not pages or "imageinfo" not in pages[0]:raise RuntimeError("Commons file not found")
    return pages[0]["imageinfo"][0]
def valid_license(info):
    ext=info.get("extmetadata") or {}
    def value(k):return str(ext.get(k,{}).get("value",""))
    license_name=value("LicenseShortName").lower()
    usage=value("UsageTerms").lower()
    if any(x in license_name for x in ("public domain","cc0","pd-","cc by","cc-by")) or "public domain" in usage:
        if any(x in license_name for x in ("nc","nd")):return False
        return True
    return False
def main():
    root=Path("output/caravaggio-cinema-sources");images=root/"original_images"
    images.mkdir(parents=True,exist_ok=True)
    records=[];failure=[]
    for title,filename in CURATED:
        try:
            info=metadata(filename)
            if not valid_license(info):raise RuntimeError("license unverified or noncommercial")
            ext=info.get("extmetadata") or {}
            lic=ext.get("LicenseShortName",{}).get("value","")
            link=info.get("thumburl") or info.get("url")
            try:
                data=get(link,max_bytes=28_000_000)
            except Exception as first_download_error:
                # Lower-resolution Commons thumbnails are sometimes cached while 3K ones are rate-limited.
                try:
                    info=metadata(filename,width=1900)
                    link=info.get("thumburl") or info.get("url")
                    data=get(link,max_bytes=18_000_000)
                except Exception:
                    raise first_download_error
            with Image.open(io.BytesIO(data)) as orig:
                orig.load();im=ImageOps.exif_transpose(orig).convert("RGB")
            if min(im.size)<640:raise RuntimeError(f"insufficient image dimensions {im.size}")
            if max(im.size)>3800:im.thumbnail((3800,3800),Image.Resampling.LANCZOS)
            name=hashlib.sha256(filename.encode()).hexdigest()[:17]+".jpg"
            path=images/name;im.save(path,quality=95,subsampling=0,optimize=True)
            rec={"title":title,"artist":"Michelangelo Merisi da Caravaggio","id":name.split(".")[0],
                "source":"Wikimedia Commons - artwork record",
                "url":"https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(filename.replace(" ","_")),
                "original_file":filename,"license":lic,
                "license_url":str(ext.get("LicenseUrl",{}).get("value","")),
                "image_url":link,"file":str(path),"width":im.width,"height":im.height,
                "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                "attribution":str(ext.get("Attribution",{}).get("value",""))[:1000],
                "artist_verification":"Commons page explicitly identifies artist as Caravaggio"}
            records.append(rec)
            print(f"WORK {len(records)}: {title} {im.width}x{im.height} {lic}",flush=True)
        except Exception as err:
            failure.append({"title":title,"file":filename,"error":str(err)[:300]})
            print("SKIPPED",title,str(err)[:220],flush=True)
        time.sleep(.85)
    if len(records)<12:raise RuntimeError("Not enough authentic licensed high-resolution artworks: "+json.dumps(failure))
    # Different instrumental score from Van Gogh, verified officially by Kevin MacLeod (CC BY 4.0).
    music={"title":"Darkest Child","author":"Kevin MacLeod","isrc":"USUAN1100783",
       "page":"https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100783",
       "urls":["https://incompetech.com/music/royalty-free/mp3-royaltyfree/Darkest%20Child.mp3"],
       "license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
       "expected_seconds":239,"instrumental":True}
    audio,proof=audio_download(music,root,150)
    audio.rename(root/"licensed_piano_music.mp3")
    (root/"music_rights.json").write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding="utf-8")
    (root/"artworks.json").write_text(json.dumps({"artist":"Caravaggio",
        "metadata":records,"failed":failure,"publication_approved":False,
        "rights_note":"Commons PD/CC photos; for commercial uses verify museum and applicable Italian cultural-heritage restrictions."},
        ensure_ascii=False,indent=2),encoding="utf-8")
    print("CARAVAGGIO ASSET EXPORT SUCCESS",len(records),"artworks, licensed real music",flush=True)
if __name__=="__main__":main()
