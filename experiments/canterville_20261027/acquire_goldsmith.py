"""Collect and verify 1906 Wallace Goldsmith illustrations from Project Gutenberg #14522.
Fetch one HTML page and exact <img src> links; stop on HTTP 429. Keep original order.
"""
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from io import BytesIO
from PIL import Image
from html.parser import HTMLParser
import hashlib,json,time,re
PAGE="https://www.gutenberg.org/cache/epub/14522/pg14522-images.html"
root=Path("output/canterville-illustrations")
root.mkdir(parents=True,exist_ok=True)
class Extract(HTMLParser):
    def __init__(self):super().__init__();self.items=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower()=="img":
            d=dict(attrs)
            if d.get("src"):self.items.append((d["src"],d.get("alt","")))
manifest=[]
try:
    with urlopen(Request(PAGE,headers={"User-Agent":"TraLePagine-Illustrated-Reading/1.0 (limited request)"}),timeout=30) as r:
        html=r.read(2_500_000).decode("utf8",errors="replace")
    ext=Extract();ext.feed(html)
    print("DISCOVERED_IMAGE_TAGS",len(ext.items),flush=True)
    for index,(src,alt) in enumerate(ext.items,1):
        url=urljoin(PAGE,src)
        try:
            with urlopen(Request(url,headers={"User-Agent":"TraLePagine-Illustrated-Reading/1.0 (limited request)"}),timeout=28) as r:
                b=r.read(12_000_000)
            with Image.open(BytesIO(b)) as im:
                w,h=im.size
                if min(w,h)<170:continue
                im.convert("RGB").save(root/f"{len(manifest)+1:02d}.jpg",quality=95)
            manifest.append({"index":len(manifest)+1,"url":url,"alt":alt,"width":w,"height":h,"sha256":hashlib.sha256(b).hexdigest(),"illustrator":"Wallace Goldsmith (1873-1945)","book":"1906 Canterville edition via Project Gutenberg #14522"})
            print("SAVED",len(manifest),w,h,alt[:50],flush=True)
        except HTTPError as e:
            print("HTTP_ERROR",e.code,url,flush=True)
            if e.code==429:break
        except Exception as e:print("ASSET_ERROR",type(e).__name__,url,flush=True)
        time.sleep(0.35)
except Exception as e:print("FETCH_FAIL",type(e).__name__,str(e)[:150],flush=True)
(root/"MANIFEST.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf8")
print("ACQUIRED",len(manifest),flush=True)
if len(manifest)<9:raise SystemExit("insufficient original illustrations")
