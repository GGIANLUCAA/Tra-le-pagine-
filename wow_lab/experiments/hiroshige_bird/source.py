#!/usr/bin/env python3
"""Acquire Hiroshige Weeping Cherry and Bluebird, The Met open access 36725."""
import io,json,hashlib,time,urllib.request
from pathlib import Path
from PIL import Image,ImageOps
OBJECT_ID=36725
out=Path(__file__).resolve().parent/"sources";out.mkdir(exist_ok=True)
def download(url,cap=26000000):
    if not url.startswith("https://"):raise ValueError("Only HTTPS image sources permitted")
    for i in range(3):
        try:
            rq=urllib.request.Request(url,headers={"User-Agent":"ArtVision-WowLab-NoncommercialStudy/2.0","Accept":"*/*"})
            with urllib.request.urlopen(rq,timeout=35) as f:data=f.read(cap+1)
            if len(data)<1024 or len(data)>cap:raise RuntimeError("Empty or oversized image")
            return data
        except Exception:
            if i==2:raise
            time.sleep(i*2+1)
rec=json.loads(download(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{OBJECT_ID}",2000000))
assert rec["objectID"]==OBJECT_ID and rec["isPublicDomain"] is True
assert "Hiroshige" in rec["artistDisplayName"] and "Bluebird" in rec["title"]
assert rec.get("accessionNumber")=="JP253",repr(rec.get("accessionNumber"))
for key in ("primaryImage","primaryImageSmall"):
    url=rec.get(key,"")
    if not url:continue
    try:
        raw=download(url)
        img=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
        if min(img.size)<850:raise RuntimeError("Source too small")
        (out/"HIROSHIGE_36725_ORIGINAL.jpg").write_bytes(raw)
        img.thumbnail((1600,1600),Image.Resampling.LANCZOS)
        img.save(out/"HIROSHIGE_36725_WORK.png")
        meta={"museum":"The Metropolitan Museum of Art","artwork_id":OBJECT_ID,
              "title":rec["title"],"artist":rec["artistDisplayName"],"year":rec["objectDate"],
              "license":"Met Open Access CC0","isPublicDomain":True,
              "accession":rec.get("accessionNumber"),"object_url":rec.get("objectURL"),
              "original_url":url,"original_sha256":hashlib.sha256(raw).hexdigest(),
              "original_size":list(Image.open(io.BytesIO(raw)).size),"working_size":list(img.size)}
        (out/"SOURCE_PROVENANCE.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2))
        print(json.dumps(meta,ensure_ascii=False))
        break
    except Exception as ex:
        print("Candidate image failed:",repr(ex))
else:raise RuntimeError("No verified source image accessible")
