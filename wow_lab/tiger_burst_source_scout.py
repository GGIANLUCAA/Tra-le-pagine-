#!/usr/bin/env python3
"""WOW LAB tiger stage 1: read-only museum CC0 source scout. NEVER renders/publishes."""
import hashlib, io, json, os, pathlib, urllib.request
from PIL import Image, ImageOps

ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT/"runs"/os.environ["GITHUB_RUN_ID"]
ID=73553

def get(url,limit=32_000_000):
    if not url.startswith("https://"): raise RuntimeError("HTTPS required")
    req=urllib.request.Request(url,headers={"User-Agent":"WOW-LAB-public-domain-art-scout","Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=35) as stream:
        body=stream.read(limit+1)
    if not body or len(body)>limit: raise RuntimeError("Empty or oversized source")
    return body

def main():
    c=json.loads((ROOT/"config.json").read_text())
    if not all(c.get(k) for k in ("no_vidu","no_paid_services","no_social_publish","no_core_config_edits","no_core_automation_edits")):
        raise RuntimeError("WOW LAB security switches changed")
    rec=json.loads(get("https://collectionapi.metmuseum.org/public/collection/v1/objects/73553",3_000_000))
    if rec.get("objectID") != ID or rec.get("isPublicDomain") is not True: raise RuntimeError("Met CC0 not verified")
    url=rec.get("primaryImage")
    if not url or not url.startswith("https://images.metmuseum.org/"): raise RuntimeError("Nonofficial or missing source image")
    imagebytes=get(url)
    with Image.open(io.BytesIO(imagebytes)) as f:
        im=ImageOps.exif_transpose(f).convert("RGB")
    if min(im.size)<900: raise RuntimeError("Image source too small")
    OUT.mkdir(parents=True,exist_ok=False)
    (OUT/"SOURCE_MET_73553.jpg").write_bytes(imagebytes)
    thumb=im.copy();thumb.thumbnail((1150,1600))
    thumb.save(OUT/"SOURCE_PREVIEW.jpg",quality=94)
    manifest={"object_id":ID,"title":rec.get("title"),"artist":rec.get("artistDisplayName"),"date":rec.get("objectDate"),
      "source":rec.get("objectURL"),"image_url":url,"isPublicDomain":True,"license":"Metropolitan Museum Open Access CC0",
      "sha256":hashlib.sha256(imagebytes).hexdigest(),"width":im.width,"height":im.height,
      "render_approved":False,"status":"SOURCE_ONLY_MASK_REQUIRED","paid_api_cost":0}
    (OUT/"SOURCE_QA.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print(json.dumps(manifest,ensure_ascii=False))

if __name__=="__main__":
    main()
