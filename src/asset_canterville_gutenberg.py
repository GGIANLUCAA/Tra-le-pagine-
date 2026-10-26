#!/usr/bin/env python3
"""Fetch the historical public-domain illustrations of Canterville (Goldsmith, 1906).

Only a single illustrated public-domain Gutenberg book, on-demand; no scraping of
unrelated results. Raw images with provenance are preserved before artistic framing.
"""
from __future__ import annotations
from html.parser import HTMLParser
import io
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit
from urllib.request import urlopen, Request
from PIL import Image, ImageOps

BASE="https://www.gutenberg.org/cache/epub/14522/pg14522-images.html"
USER_AGENT="TraLePagine-CantervilleBookVideo/1.0 (illustrated public-domain ebook)"


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower()!='img':
            return
        a=dict(attrs)
        src=a.get('src') or ''
        if re.search(r'\.(?:png|jpg|jpeg|gif)
            self.images.append({"url":urljoin(BASE,src),"alt":a.get('alt','')})


def get(url, max_bytes=15_000_000):
    parsed=urlsplit(url)
    if parsed.scheme!="https" or parsed.netloc!="www.gutenberg.org":
        raise ValueError("Host sorgente non autorizzato")
    req=Request(url,headers={"User-Agent":USER_AGENT,"Accept":"text/html,image/jpeg,image/png,image/gif"})
    with urlopen(req,timeout=45) as response:
        raw=response.read(max_bytes+1)
    if len(raw)>max_bytes:
        raise ValueError("File fuori limite")
    return raw


def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    page=get(BASE,2_000_000).decode("utf-8","replace")
    parser=Parser();parser.feed(page)
    print("Available HTML illustrations:", len(parser.images), [i["url"].rsplit("/",1)[-1] for i in parser.images], flush=True)
    result=[];seen=set()
    for x in parser.images:
        url=x["url"]
        if url in seen:
            continue
        seen.add(url)
        if len(result)>=24:
            break
        try:
            body=get(url)
            with Image.open(io.BytesIO(body)) as raw:
                raw.load()
                image=ImageOps.exif_transpose(raw).convert("RGB")
            if min(image.size)<200:
                continue
            path=out/f"illustrazione_{len(result)+1:02d}.jpg"
            image.save(path,quality=96,optimize=True)
            result.append({"id":len(result)+1,"file":path.name,"source_url":url,
                           "source_page":BASE,"alt":x["alt"],"width":image.width,"height":image.height,
                           "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                           "source":"Oscar Wilde, The Canterville Ghost, illustrated by Wallace Goldsmith, John W. Luce, 1906",
                           "copyright":"Historic US public-domain edition; assess applicable law before commercial publication",
                           "editorial_review":"pending","visual_review":"pending"})
            print("SAVED",path.name,image.size,x["alt"][:65],flush=True)
        except Exception as exc:
            print("SKIPPED",re.sub(r'[^a-z0-9._/-]','',url)[-60:],type(exc).__name__,flush=True)
    (out/"FONTI_ILLUSTRAZIONI.json").write_text(json.dumps({
        "title":"The Canterville Ghost", "illustrator":"Wallace Goldsmith",
        "original_publication":1906, "source_ebook":BASE,
        "count":len(result),"editorial_use":"Book adaptation; source illustrations only, not misleading photos",
        "assets":result},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if len(result)<6:
        raise RuntimeError("Too few valid illustrations, cannot produce storyboard")
    print("BOOK ILLUSTRATIONS",len(result),flush=True)


if __name__=="__main__":
    import sys
    run(sys.argv[1] if len(sys.argv)>1 else "output/canterville_illustrations")
,src,re.I) and not src.startswith("http"):
            self.images.append({"url":urljoin(BASE,src),"alt":a.get('alt','')})


def get(url, max_bytes=15_000_000):
    parsed=urlsplit(url)
    if parsed.scheme!="https" or parsed.netloc!="www.gutenberg.org":
        raise ValueError("Host sorgente non autorizzato")
    req=Request(url,headers={"User-Agent":USER_AGENT,"Accept":"text/html,image/jpeg,image/png,image/gif"})
    with urlopen(req,timeout=45) as response:
        raw=response.read(max_bytes+1)
    if len(raw)>max_bytes:
        raise ValueError("File fuori limite")
    return raw


def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    page=get(BASE,2_000_000).decode("utf-8","replace")
    parser=Parser();parser.feed(page)
    result=[];seen=set()
    for x in parser.images:
        url=x["url"]
        if url in seen:
            continue
        seen.add(url)
        if len(result)>=24:
            break
        try:
            body=get(url)
            with Image.open(io.BytesIO(body)) as raw:
                raw.load()
                image=ImageOps.exif_transpose(raw).convert("RGB")
            if min(image.size)<200:
                continue
            path=out/f"illustrazione_{len(result)+1:02d}.jpg"
            image.save(path,quality=96,optimize=True)
            result.append({"id":len(result)+1,"file":path.name,"source_url":url,
                           "source_page":BASE,"alt":x["alt"],"width":image.width,"height":image.height,
                           "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                           "source":"Oscar Wilde, The Canterville Ghost, illustrated by Wallace Goldsmith, John W. Luce, 1906",
                           "copyright":"Historic US public-domain edition; assess applicable law before commercial publication",
                           "editorial_review":"pending","visual_review":"pending"})
            print("SAVED",path.name,image.size,x["alt"][:65],flush=True)
        except Exception as exc:
            print("SKIPPED",re.sub(r'[^a-z0-9._/-]','',url)[-60:],type(exc).__name__,flush=True)
    (out/"FONTI_ILLUSTRAZIONI.json").write_text(json.dumps({
        "title":"The Canterville Ghost", "illustrator":"Wallace Goldsmith",
        "original_publication":1906, "source_ebook":BASE,
        "count":len(result),"editorial_use":"Book adaptation; source illustrations only, not misleading photos",
        "assets":result},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if len(result)<9:
        raise RuntimeError("Too few valid illustrations, cannot produce storyboard")
    print("BOOK ILLUSTRATIONS",len(result),flush=True)


if __name__=="__main__":
    import sys
    run(sys.argv[1] if len(sys.argv)>1 else "output/canterville_illustrations")
