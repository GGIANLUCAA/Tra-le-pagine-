#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageOps
import urllib.request,io,json,time,hashlib
ID=36075;OUT=Path(__file__).resolve().parent/"source";OUT.mkdir(exist_ok=True)
def get(url,maxlen=30000000):
    if not url.startswith("https://"):raise RuntimeError("https only")
    for n in range(3):
        try:
            rq=urllib.request.Request(url,headers={"User-Agent":"WOWLAB-CC0-source-research/1.0"})
            with urllib.request.urlopen(rq,timeout=35) as r:b=r.read(maxlen+1)
            if not 100<len(b)<maxlen:raise RuntimeError("source size")
            return b
        except Exception:
            if n==2:raise
            time.sleep(n+2)
r=json.loads(get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{ID}",2000000))
assert r["objectID"]==ID and r["isPublicDomain"]
assert "Zhu Ling" in r["artistDisplayName"] and "Black Cat" in r["title"]
for u in [r.get("primaryImage"),r.get("primaryImageSmall")]:
    if not u:continue
    try:
        raw=get(u)
        im=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
        if min(im.size)<600:raise RuntimeError("small source")
        original_size=im.size
        (OUT/"CAT_ORIGINAL.jpg").write_bytes(raw)
        im.thumbnail((1800,2400),Image.Resampling.LANCZOS)
        im.save(OUT/"CAT_WORK.png")
        obj={"object_id":ID,"artist":r["artistDisplayName"],"title":r["title"],
         "museum_url":r["objectURL"],"source_url":u,"sha256":hashlib.sha256(raw).hexdigest(),
         "license":"Met Open Access CC0","is_public_domain":True,"original_size":original_size,"size":im.size}
        (OUT/"PROVENANCE.json").write_text(json.dumps(obj,indent=2))
        print(json.dumps(obj))
        break
    except Exception as e:print("image source rejected",e)
else:raise RuntimeError("No suitable source")
