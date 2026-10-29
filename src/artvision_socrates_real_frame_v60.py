#!/usr/bin/env python3
"""Retrieve the *actual* Socrates frame photograph, with attribution and audit.
No video generation, publication, voice API, or museum approval.
"""
import argparse, hashlib, json, urllib.request
from pathlib import Path
from PIL import Image

SOURCE="https://commons.wikimedia.org/wiki/File:David_-_The_Death_of_Socrates_-_with_frame.jpg"
BINARY="https://upload.wikimedia.org/wikipedia/commons/0/0f/David_-_The_Death_of_Socrates_-_with_frame.jpg"
LICENSE="https://creativecommons.org/licenses/by-sa/4.0/"
META="https://www.metmuseum.org/art/collection/search/436105"

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def prepare(dest):
    dest=Path(dest)
    if dest.exists(): raise FileExistsError("do not replace existing source or manifest")
    dest.mkdir(parents=True)
    photo=dest/"SOCRATES_FRAME_SZILAS_ORIGINAL_CC_BY_SA_4.jpg"
    request=urllib.request.Request(BINARY,headers={
        "User-Agent":"ArtVision/60 (public domain artwork; CC BY-SA licensed frame photo; noncommercial audit)"})
    with urllib.request.urlopen(request,timeout=90) as r:
        if r.status!=200 or not r.geturl().startswith("https://upload.wikimedia.org/"):
            raise ValueError("Not verified Commons original")
        content=r.read(12000001)
    if len(content)>12000000 or len(content)<400000:
        raise ValueError("Suspicious photo byte count")
    photo.write_bytes(content)
    with Image.open(photo) as im:
        im.verify()
    with Image.open(photo) as im:
        dimensions=list(im.size)
    if min(dimensions)<1700:
        raise ValueError("Insufficient quality frame reference")
    record={
        "schema":"artvision-socrates-authentic-frame-v60",
        "artwork":"The Death of Socrates","met_object_id":436105,
        "source_page":SOURCE,"raw_original_url":BINARY,
        "photo_author":"Szilas","photo_date":"2008-10-23",
        "license":"CC BY-SA 4.0","license_url":LICENSE,
        "rights":"Photograph of exact work and its existing physical frame. Attribution, link, modifications and ShareAlike required if adapted.",
        "file":photo.name,"sha256":sha(photo),"dimensions_px":dimensions,
        "museum_object":META,
        "canvas_cm":[129.5,196.2],
        "met_measured_outer_frame_cm":[168.27533,233.68047,14.605029],
        "frame_note":"Real Szilas photograph is frame source; perspective and precise geometry need manual QA. No proof of present-day gallery installation, no V25 approval.",
        "status":"SOURCE_ONLY_NO_MUSEUM_RENDER",
        "paid_api_calls":0,"cinema_museum_rendered":False
    }
    # Licensed 2024 reference for Met gallery architectural finishes only.
    # Gallery 632, not the current installation of object 436105.
    gallery_url="https://upload.wikimedia.org/wikipedia/commons/b/bd/Paintings_in_Metropolitan_Museum_of_Art_20240523.jpg"
    gallery_file=dest/"MET_GALLERY_632_2024_YIYUANJU_CC_BY_SA_4.jpg"
    request=urllib.request.Request(gallery_url,headers={"User-Agent":"ArtVision/60 (CC BY-SA 4.0 licensed reference; source audit)"})
    with urllib.request.urlopen(request,timeout=90) as g:
        if g.status!=200 or not g.geturl().startswith("https://upload.wikimedia.org/"):
            raise ValueError("Gallery reference must originate from Commons")
        gallery_bytes=g.read(12000001)
    if not 500000<len(gallery_bytes)<12000000:
        raise ValueError("Unexpected gallery photo size")
    gallery_file.write_bytes(gallery_bytes)
    with Image.open(gallery_file) as im:
        im.verify()
    with Image.open(gallery_file) as im:
        gw,gh=im.size
    if min(gw,gh)<1800: raise ValueError("Gallery reference too small")
    record["gallery_reference"]={
        "file":gallery_file.name,"sha256":sha(gallery_file),"dimensions_px":[gw,gh],
        "source_page":"https://commons.wikimedia.org/wiki/File:Paintings_in_Metropolitan_Museum_of_Art_20240523.jpg",
        "photo_author":"颐园居","photo_date":"2024-05-23",
        "license":"CC BY-SA 4.0","license_url":LICENSE,
        "truth":"The photographed room is Gallery 632, not a verified image of Socrates' current Gallery 634. Can guide architectural reconstruction only; any scene combining it with Socrates must be explicitly disclosed as composited."
    }
    (dest/"FRAME_SOURCE_V60.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(record,ensure_ascii=False,indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    args=p.parse_args()
    prepare(args.out)
