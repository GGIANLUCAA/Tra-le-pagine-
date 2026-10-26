#!/usr/bin/env python3
"""One illustrated 1906 public-domain edition of Oscar Wilde, with source ledger."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
from PIL import Image, ImageOps
import hashlib
import io
import json
import sys

SOURCE = "https://www.gutenberg.org/cache/epub/14522/pg14522-images.html"
AGENT = "TraLePagine-OriginalIllustrations/1.0"


class ImageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.records = []

    def handle_starttag(self, tag, attrs):
        if tag != "img":
            return
        attrs = dict(attrs)
        ref = attrs.get("src", "")
        if ref.lower().endswith((".jpg", ".jpeg", ".png", ".gif")) and not ref.startswith("http"):
            self.records.append({"url": urljoin(SOURCE, ref), "alt": attrs.get("alt", "")})


def fetch(url, max_bytes=15_000_000):
    host = urlsplit(url)
    if host.scheme != "https" or host.netloc != "www.gutenberg.org":
        raise ValueError("Only original Gutenberg edition assets allowed")
    with urlopen(Request(url, headers={"User-Agent": AGENT}), timeout=40) as r:
        data = r.read(max_bytes+1)
    if len(data) > max_bytes:
        raise ValueError("Out-of-bounds image")
    return data


def run(dest):
    dest=Path(dest)
    dest.mkdir(parents=True,exist_ok=True)
    page=fetch(SOURCE,2_000_000).decode("utf-8",errors="replace")
    parser=ImageParser()
    parser.feed(page)
    print("Available images",len(parser.records),[(x["url"].rsplit("/",1)[-1],x["alt"][:40]) for x in parser.records],flush=True)
    results=[]
    visited=set()
    for entry in parser.records[:30]:
        url=entry["url"]
        if url in visited:
            continue
        visited.add(url)
        try:
            payload=fetch(url)
            with Image.open(io.BytesIO(payload)) as img:
                img.load()
                img=ImageOps.exif_transpose(img).convert("RGB")
                if min(img.size)<190:
                    continue
                out=dest/("illustrazione_%02d.jpg"%(len(results)+1))
                img.save(out,quality=96,optimize=True)
                result={"file":out.name,"number":len(results)+1,"source":url,
                        "alt":entry["alt"],"width":img.width,"height":img.height,
                        "sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
                        "author":"Wallace Goldsmith","work":"The Canterville Ghost (1906)",
                        "copyright_note":"Historical public-domain edition; check applicable local law",
                        "manual_review":"required"}
                results.append(result)
                print("SAVED",out.name,img.size,entry["alt"][:80],flush=True)
        except Exception as exc:
            print("SKIPPED",url.rsplit("/",1)[-1],type(exc).__name__,flush=True)
    if len(results)<6:
        raise ValueError("Only %s illustrations; insufficient original source" % len(results))
    (dest/"FONTI_ILLUSTRAZIONI.json").write_text(
        json.dumps({"source_ebook":SOURCE,"illustrator":"Wallace Goldsmith",
                    "original_year":1906,"assets":results,
                    "note":"Authentic book illustrations, no generative images, require editorial review."},
                   ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("SUCCESS",len(results),flush=True)

if __name__=="__main__":
    run(sys.argv[1] if len(sys.argv)>1 else "output/canterville_illustrations")
