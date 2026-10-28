#!/usr/bin/env python3
"""One free EPUB acquisition from a distinct public-domain archive after Commons 429.
No further Wikimedia requests, no paid image/video APIs.
"""
from pathlib import Path
import requests,json,hashlib,zipfile,io
from PIL import Image,ImageDraw,ImageOps
root=Path("output/sleepy_hollow_rackham_20261028");imgdir=root/"assets";imgdir.mkdir(parents=True,exist_ok=True)
url="https://litterature-jeunesse-libre.fr/bbs/download/1676/epub/1676.epub"
s=requests.Session();s.headers.update({"User-Agent":"TraLePagineStudio/1.0 (public domain Rackham illustrations, editorial QA)"})
r=s.get(url,timeout=45)
print("EPUB archive:",r.status_code,len(r.content),r.headers.get("Content-Type"),flush=True)
if r.status_code!=200 or len(r.content)<100000 or len(r.content)>30000000:raise RuntimeError("EPUB unavailable, stop without retry")
archive=zipfile.ZipFile(io.BytesIO(r.content))
images=[]
for item in archive.infolist():
    if item.is_dir() or not item.filename.lower().endswith((".jpg",".jpeg",".png",".webp")):continue
    if item.file_size<25000 or item.file_size>10000000:continue
    raw=archive.read(item)
    try:im=Image.open(io.BytesIO(raw));im.load()
    except Exception:continue
    if im.width<400 or im.height<450:continue
    images.append((item.filename,raw,im))
print("Candidate full illustrations:",len(images),[(a,c.size) for a,b,c in images],flush=True)
if len(images)<9:raise RuntimeError("Not enough story-specific Rackham illustrations, do not synthesize voice")
records=[]
for n,(name,raw,im) in enumerate(images,1):
    out=imgdir/f"rackham_{n:02d}.jpg"
    im.convert("RGB").save(out,quality=95)
    records.append({"index":n,"filename":out.name,"original_epub_path":name,
        "sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
        "source":url,"author":"Arthur Rackham (1867–1939)","edition":1928,
        "rights":"Original illustrations public domain in Italy (artist died 1939), no modern translation used",
        "size":list(im.size)})
(root/"ASSET_SOURCES.json").write_text(json.dumps(records,ensure_ascii=False,indent=2))
tw,th=270,370;cols=4;rows=(len(images)+cols-1)//cols
sheet=Image.new("RGB",(cols*tw,rows*(th+36)),(24,24,29));d=ImageDraw.Draw(sheet)
for i,rec in enumerate(records):
    im=Image.open(imgdir/rec["filename"]).convert("RGB");tile=ImageOps.contain(im,(tw-12,th-12))
    x=(i%cols)*tw+(tw-tile.width)//2;y=(i//cols)*(th+36)+(th-tile.height)//2
    sheet.paste(tile,(x,y));d.text(((i%cols)*tw+10,(i//cols)*(th+36)+th+3),f"PLATE {i+1:02d}",fill="white")
sheet.save(root/"RACKHAM_CONTACT_SHEET.jpg",quality=92)
print("PREVIEW READY",len(records),flush=True)
