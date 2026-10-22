#!/usr/bin/env python3
"""Acquisisce SOLO l'opera curata dal museo e una musica gia censita da ArtVision.
Usa Archivio V7 (host allowlist + API) e Atelier V4 (recording+ffprobe).
Nessuna API AI, scraping social, generazione immagini o pubblicazione.
"""
import argparse
import hashlib
import io
import json
import sys
import urllib.parse
import urllib.request
import urllib.parse
from pathlib import Path

from PIL import Image, ImageOps
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"modules"/"artvision"))
from src.archivio_media_v7 import api_json,allowed_media_url,check_signature,NoRedirect
from atelier_v4 import TRACKS,audio_download
from enigma_v1 import validate

WHITELIST={"evening_fall_piano","calmant"}
def fetch_art(data,out):
    name=data["source"]["file_title"]
    if "/" in name or "\\" in name or len(name)>220:raise ValueError("Titolo opera per Commons non valido")
    url="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({
        "action":"query","format":"json","formatversion":"2",
        "titles":"File:"+name,"prop":"imageinfo","iiprop":"url|size|extmetadata",
        "iiurlwidth":"3000"})
    obj=api_json(url,timeout=30)
    pages=obj.get("query",{}).get("pages",[])
    if len(pages)!=1 or not pages[0].get("imageinfo"):
        raise RuntimeError("Foto Commons non trovata, niente immagini inventate")
    info=pages[0]["imageinfo"][0]
    meta=info.get("extmetadata") or {}
    lic=str((meta.get("LicenseShortName") or {}).get("value","")).lower()
    usage=str((meta.get("UsageTerms") or {}).get("value","")).lower()
    # Lo stesso file deve essere dichiarato PDM e la scheda museale deve essere citata.
    if data["source"]["license"]=="PDM" and not ("public domain" in lic or "public domain" in usage or "pd"==lic):
        raise RuntimeError("Licenza PDM NON dimostrata da Commons; controlla prima l'originale")
    asset_url=info.get("thumburl") or info.get("url") or ""
    url_parts=urllib.parse.urlsplit(asset_url)
    if not ((allowed_media_url(asset_url,"openverse","image") or
             (url_parts.scheme=="https" and url_parts.hostname=="thumb.wikimedia.org" and
              not url_parts.username and not url_parts.password and url_parts.port is None))
            and not url_parts.fragment):
        raise RuntimeError("Dominio immagine diverso dalla CDN ufficiale Wikimedia")
    request=urllib.request.Request(asset_url,headers={"User-Agent":"TraLePagine-ArtVisionEnigma/1.0 (source research)"})
    opener=urllib.request.build_opener(NoRedirect)
    with opener.open(request,timeout=45) as response:
        if int(response.headers.get("Content-Length") or 0)>24000000:
            raise RuntimeError("File troppo grande")
        raw=response.read(24_000_001)
    if len(raw)>24_000_000 or not check_signature(raw,"image"):
        raise RuntimeError("Immagine fuori limite o file non immagine")
    with Image.open(io.BytesIO(raw)) as original:
        im=ImageOps.exif_transpose(original).convert("RGB")
        if min(im.size)<650:raise RuntimeError("Foto troppo piccola")
        im.thumbnail((3000,3700),Image.Resampling.LANCZOS)
        out_path=out/"opera_museale.jpg"
        im.save(out_path,quality=94,subsampling=0)
    return out_path,{"url":asset_url,"source_page":data["source"]["file_page"],
        "museum_evidence":data["source"]["museum_evidence"],"license_displayed":lic,
        "usage_terms_displayed":usage,"image_sha256":hashlib.sha256(out_path.read_bytes()).hexdigest(),
        "width":im.width,"height":im.height,"origin":"Wikimedia Commons, museo citato; riverificare prima di monetizzare"}

def run(config,out):
    data=json.loads(config.read_text(encoding="utf8"))
    seconds=validate(data)
    if data["music"]["id"] not in WHITELIST:
        raise RuntimeError("Musica non presente nella whitelist di brani originali gia verificati")
    track=TRACKS[data["music"]["id"]]
    if track["title"]!=data["music"]["title"] or track["author"]!=data["music"]["artist"]:
        raise ValueError("Metadati musica differenti dalla libreria Atelier V4")
    out.mkdir(parents=True,exist_ok=True)
    photo,image_proof=fetch_art(data,out)
    audio,audio_proof=audio_download(track,out,seconds)
    proof={"image":image_proof,"audio":audio_proof,"publication_approved":False,
        "commercial_rights_and_museum_terms_need_editorial_review":True,
        "public_social_caption_credit_required":True}
    (out/"FONTI_E_DIRITTI.json").write_text(json.dumps(proof,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    return photo,audio

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--config",type=Path,required=True)
    p.add_argument("--out",type=Path,default=Path("output/enigma-assets"))
    a=p.parse_args()
    photo,audio=run(a.config,a.out)
    print("Materiali autentici pronti",photo,audio)

if __name__=="__main__":main()
