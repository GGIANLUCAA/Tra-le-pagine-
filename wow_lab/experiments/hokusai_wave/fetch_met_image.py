#!/usr/bin/env python3
"""Fetch only the documented Met Public Domain impression JP1847, not a substitute image."""
import io, json, hashlib, sys, time
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assets"
OUT.mkdir(parents=True, exist_ok=True)
MUSEUM_URL = "https://collectionapi.metmuseum.org/public/collection/v1/objects/45434"
def fetch(url, cap=26_000_000):
    err = None
    for i in range(3):
        try:
            request = Request(url,headers={"User-Agent":"ArtVision-WOWLAB-CC0-Prototype/1.0","Accept":"*/*"})
            with urlopen(request,timeout=35) as r:
                b=r.read(cap+1)
            if len(b)>cap or len(b)<100:
                raise ValueError("Object too big or absent")
            return b
        except Exception as e:
            err=e
            time.sleep(i*2+1)
    raise RuntimeError(f"Fetch failed {url}: {err}")

rec=json.loads(fetch(MUSEUM_URL,2_000_000).decode("utf-8"))
assert rec["objectID"]==45434 and rec["isPublicDomain"] is True
assert "Hokusai" in rec["artistDisplayName"]
assert rec.get("primaryImage","").startswith("https://")
assert rec.get("objectNumber","")=="JP1847",rec.get("objectNumber")
candidates=[rec.get("primaryImage"),rec.get("primaryImageSmall")]
img=None
for url in candidates:
    if not url:continue
    try:
        original=fetch(url)
        with Image.open(io.BytesIO(original)) as src:
            img=ImageOps.exif_transpose(src).convert("RGB")
        if min(img.size)<900:
            raise ValueError("image too small")
        break
    except Exception as e:
        print("source candidate failed:",str(e)[:200])
if img is None:raise RuntimeError("No museum source image available")
(OUT/"HOKUSAI_MET_45434_ORIGINAL.jpg").write_bytes(original)
print("SOURCE_SIZE",img.size)
img.thumbnail((1600,1600),Image.Resampling.LANCZOS)
img.save(OUT/"HOKUSAI_MET_45434_WORKING.png")
meta={"source":"The Metropolitan Museum of Art",
      "object_id":45434,"accession":"JP1847",
      "title":rec["title"],"artist":rec["artistDisplayName"],
      "isPublicDomain":True,"rights":"Met Open Access CC0",
      "original_dimensions":list(Image.open(io.BytesIO(original)).size),
      "preview_dimensions":list(img.size),
      "objectURL":rec["objectURL"],"image_url":url,
      "sha256_original":hashlib.sha256(original).hexdigest()}
(OUT/"SOURCE_MANIFEST.json").write_text(json.dumps(meta,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps(meta,ensure_ascii=False))
