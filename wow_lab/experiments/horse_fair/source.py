#!/usr/bin/env python3
"""WOW LAB horse 87.25: download Met CC0 source without external generator."""
from pathlib import Path
from urllib.request import Request,urlopen
import json,io,hashlib,time
from PIL import Image,ImageOps
ID=435702
root=Path(__file__).resolve().parent
out=root/"assets";out.mkdir(exist_ok=True)
def grab(url,cap):
  for i in range(3):
    try:
      req=Request(url,headers={"User-Agent":"ArtVision-WowLab-Source/1.0","Accept":"*/*"})
      with urlopen(req,timeout=40) as r:raw=r.read(cap+1)
      if len(raw)>cap or not raw:raise ValueError("response invalid")
      return raw
    except Exception as ex:
      if i>=2:raise
      time.sleep(i*2+1)
rec=json.loads(grab(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{ID}",2_000_000))
assert rec.get("objectID")==ID,rec.get("objectID")
assert rec.get("isPublicDomain") is True,"Met record is not marked public domain"
assert rec.get("accessionNumber")=="87.25",rec.get("accessionNumber")
assert "Rosa Bonheur" in rec.get("artistDisplayName","")
assert rec.get("classification") in ("Paintings","Paintings (artworks)","Paintings (Western)") or "oil" in rec.get("medium","").lower()
errors=[]
for url in [rec.get("primaryImage"),rec.get("primaryImageSmall")]:
  if not url or not url.startswith("https://"):continue
  try:
    raw=grab(url,24_000_000)
    with Image.open(io.BytesIO(raw)) as f:
      im=ImageOps.exif_transpose(f).convert("RGB")
    if min(im.size)<800:raise ValueError("source too small")
    (out/"HORSE_FAIR_MET_ORIGINAL.jpg").write_bytes(raw)
    im.thumbnail((1800,1800),Image.Resampling.LANCZOS)
    im.save(out/"HORSE_FAIR_MET_WORK.png")
    info={"museum":"The Metropolitan Museum of Art","object_id":ID,
          "title":rec.get("title"),"artist":rec.get("artistDisplayName"),
          "year":rec.get("objectDate"),"isPublicDomain":True,
          "license":"Met Open Access / CC0", "image_url":url,
          "object_url":rec.get("objectURL"),
          "source_sha256":hashlib.sha256(raw).hexdigest(),
          "original_dimensions":list(Image.open(io.BytesIO(raw)).size),
          "working_dimensions":list(im.size),"accession":"87.25"}
    (out/"PROVENANCE.json").write_text(json.dumps(info,ensure_ascii=False,indent=2))
    print(json.dumps(info,ensure_ascii=False))
    break
  except Exception as ex:errors.append(str(ex)[:150])
else:raise RuntimeError("No genuine CC0 image: "+"; ".join(errors))
