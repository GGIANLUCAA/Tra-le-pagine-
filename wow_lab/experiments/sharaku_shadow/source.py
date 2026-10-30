#!/usr/bin/env python3
"""One artwork only. Verified Met source, CC0; fail closed. WOW LAB independent."""
import urllib.request,io,json,hashlib,time
from pathlib import Path
from PIL import Image,ImageOps
ID=37358;OUT=Path(__file__).resolve().parent/"source";OUT.mkdir(parents=True,exist_ok=True)
def get(url,limit=30000000):
    if not url.startswith("https://"):raise ValueError("HTTPS only")
    for retry in range(3):
        try:
            request=urllib.request.Request(url,headers={"User-Agent":"WOW-LAB-Standalone-CC0-Research/1.0","Accept":"*/*"})
            with urllib.request.urlopen(request,timeout=35) as r:data=r.read(limit+1)
            if len(data)>limit:raise ValueError("oversized")
            return data
        except Exception:
            if retry==2:raise
            time.sleep(2+retry)
rec=json.loads(get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{ID}",2000000))
assert rec.get("objectID")==ID and rec.get("isPublicDomain") is True,rec
assert "Sharaku" in rec.get("artistDisplayName",""), rec.get("artistDisplayName")
assert "Otani" in rec.get("title","") or "Oniji" in rec.get("title",""), rec.get("title")
for url in [rec.get("primaryImage"),rec.get("primaryImageSmall"),"https://images.metmuseum.org/CRDImages/as/original/DP130228.jpg"]:
    if not url:continue
    try:
        raw=get(url)
        im=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
        if min(im.size)<600:raise ValueError(f"too small {im.size}")
        (OUT/"SHARAKU_ORIGINAL.jpg").write_bytes(raw)
        original_size=im.size
        im.thumbnail((1800,2200),Image.Resampling.LANCZOS)
        im.save(OUT/"SHARAKU_WORK.png")
        meta={"met_object_id":ID,"title":rec.get("title"),"artist":rec.get("artistDisplayName"),
          "license":"Metropolitan Museum Open Access / CC0","public_domain":True,
          "object_url":rec.get("objectURL"),"image_url":url,
          "sha256":hashlib.sha256(raw).hexdigest(),"original_size":original_size,"work_size":im.size}
        (OUT/"PROVENANCE.json").write_text(json.dumps(meta,indent=2))
        print(json.dumps(meta))
        break
    except Exception as e:print("REJECT SOURCE:",str(e)[:200])
else:raise RuntimeError("No valid CC0 image returned")
