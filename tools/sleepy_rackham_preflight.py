#!/usr/bin/env python3
"""Free media preflight: public-domain Rackham 1928 plates on Wikimedia Commons."""
from pathlib import Path
import requests,json,hashlib,time
from PIL import Image,ImageDraw,ImageFont,ImageOps
from io import BytesIO
root=Path("output/sleepy_hollow_rackham_20261028")
imgdir=root/"assets";imgdir.mkdir(parents=True,exist_ok=True)
names=[f"MU KPB 019 The Legend of Sleepy Hollow - Illustrated by Arthur Rackham {n}.jpg" for n in range(1,12)]
s=requests.Session();s.headers.update({"User-Agent":"TraLePagineStudio/1.0 (editorial illustration provenance; GitHub Actions)"})
api="https://commons.wikimedia.org/w/api.php"
r=s.get(api,params={"action":"query","format":"json","prop":"imageinfo","iiprop":"url|size|mime","titles":"|".join("File:"+x for x in names)},timeout=35)
print("Commons API:",r.status_code, "bytes",len(r.content),flush=True)
r.raise_for_status()
pages=r.json()["query"]["pages"]
bytitle={x["title"].removeprefix("File:"):x for x in pages.values()}
records=[]
for n,name in enumerate(names,1):
    page=bytitle.get(name)
    if not page or "imageinfo" not in page:raise RuntimeError("No Commons metadata: "+name)
    info=page["imageinfo"][0]
    resp=s.get(info["url"],timeout=35)
    if resp.status_code!=200:raise RuntimeError(f"Download {n} HTTP {resp.status_code}")
    raw=resp.content
    im=Image.open(BytesIO(raw));im.load()
    if im.width<450 or im.height<500:raise RuntimeError(f"Image {n} too small {im.size}")
    out=imgdir/f"rackham_{n:02d}.jpg";out.write_bytes(raw)
    records.append({"index":n,"filename":out.name,"sha256":hashlib.sha256(raw).hexdigest(),
      "source":"https://commons.wikimedia.org/wiki/File:"+name.replace(" ","_"),
      "download_url":info["url"],"author":"Arthur Rackham (1867–1939)",
      "date":1928,"license":"Public Domain Mark 1.0 (life+70 in Italy)",
      "size":list(im.size)})
    print("Acquired",n,im.size,len(raw),flush=True)
(root/"ASSET_SOURCES.json").write_text(json.dumps(records,ensure_ascii=False,indent=2))
tw,th=260,370
sheet=Image.new("RGB",(4*tw,3*(th+36)),(23,25,29));d=ImageDraw.Draw(sheet)
for i,rec in enumerate(records):
    im=Image.open(imgdir/rec["filename"]).convert("RGB")
    tile=ImageOps.contain(im,(tw-12,th-12))
    x=(i%4)*tw+(tw-tile.width)//2;y=(i//4)*(th+36)+(th-tile.height)//2
    sheet.paste(tile,(x,y))
    d.text(((i%4)*tw+8,(i//4)*(th+36)+th+3),f"RACKHAM {i+1:02d}",fill="white")
sheet.save(root/"RACKHAM_CONTACT_SHEET.jpg",quality=92)
print("PREVIEW READY",flush=True)
