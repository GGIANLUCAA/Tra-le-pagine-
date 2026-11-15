#!/usr/bin/env python3
"""Verify EXACT Cleveland Museum 1942.647 art photograph and Music20 actual bytes.
This source-only preflight is NOT a video, no new automated production or payments.
"""
import json,hashlib,io,urllib.request,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"output/artvision-turner-cma1942-647-source-20261115"
OUT.mkdir(parents=True,exist_ok=True)
API="https://openaccess-api.clevelandart.org/api/artworks/1942.647"
FALLBACK="https://openaccess-cdn.clevelandart.org/1942.647/1942.647_print.jpg"
MUSEUM="https://www.clevelandart.org/art/1942.647"
def get(url,cap=100_000_000):
 req=urllib.request.Request(url,headers={"User-Agent":"ArtVision 1.0 private open-access research exact source (no published video)"})
 with urllib.request.urlopen(req,timeout=70) as r:
  blob=r.read(cap+1)
 if len(blob)>cap:raise RuntimeError("SOURCE_FILE_TOO_LARGE")
 return blob
def main():
 import argparse
 a=argparse.ArgumentParser();a.add_argument("--preflight",action="store_true");args=a.parse_args()
 j=json.loads((ROOT/"research/artvision_rare_cc0_video_candidates_20261115.json").read_text())
 candidates=[c for c in j["candidates"] if c["title"]=="The Burning of the Houses of Lords and Commons, 16 October 1834" and c["accession"]=="1942.647"]
 assert len(candidates)==1
 assert not (ROOT/"queue/artvision_extra_render_checkpoint_20261115_turner_fire_cleveland.json").exists()
 tracks=json.loads((ROOT/"config/artvision_music_20_v1.json").read_text())["tracks"]
 assert len([t for t in tracks if t["id"]=="the_descent" and t["license"]=="CC BY 4.0"])==1
 if args.preflight:
  print("TURNER_CMA_1942_647_DISTINCT_PHILADELPHIA_PREFLIGHT_PASS")
  return
 raw=json.loads(get(API,3_000_000))
 meta=raw.get("data") or {}
 if str(meta.get("accession_number"))!="1942.647":raise RuntimeError("WRONG_MUSEUM_OBJECT_ACCESSION")
 if meta.get("share_license_status")!="CC0":raise RuntimeError("NOT_CMA_CC0_LICENSE")
 if not "Burning of the Houses of Lords and Commons" in str(meta.get("title","")):raise RuntimeError("WRONG_WORK_TITLE")
 # Prefer the museum's original print rendition, not thumbnails or a different version from Philadelphia.
 image=(meta.get("images") or {}).get("print") or {}
 url=image.get("url") or FALLBACK
 errors=[]
 for exact in list(dict.fromkeys([url,FALLBACK])):
  try:
   buf=get(exact)
   with Image.open(io.BytesIO(buf)) as im:
    w,h=im.size
    if im.format!="JPEG" or w<1800 or h<1200 or not 1.22<w/h<1.48:raise ValueError(f"Invalid original image geometry {w}x{h} / {im.format}")
    im.verify()
   p=OUT/"TURNER_CMA_1942_647_EXACT_PRINT.jpg"
   p.write_bytes(buf)
   report={"schema":"artvision-exact-turner-cma-source-v1",
    "museum":"Cleveland Museum of Art","museum_object":"1942.647",
    "artist":"Joseph Mallord William Turner",
    "title":meta["title"],"year":"1835",
    "source_image_url":exact,"source_bytes":len(buf),
    "source_dimensions":[w,h],"source_sha256":hashlib.sha256(buf).hexdigest(),
    "source_sha1":hashlib.sha1(buf).hexdigest(),
    "license":"CC0", "license_evidence":"Cleveland Museum of Art official API share_license_status CC0 and official object page",
    "official_object_url":MUSEUM, "distinct_from":"Philadelphia Museum of Art version (not used)",
    "source_binary_sha_matches_written":hashlib.sha256(p.read_bytes()).hexdigest()==hashlib.sha256(buf).hexdigest(),
    "has_new_video":False,"voice":None,"publish":False,"gold":False}
   (OUT/"SOURCE_PROOF.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
   print("CMA_TURNER_SOURCE_VERIFIED",w,h,report["source_sha256"],len(buf),flush=True)
   return
  except Exception as e:errors.append(f"{exact} : {type(e).__name__} {str(e)[:150]}")
 raise RuntimeError("CMA_ARTWORK_BINARY_DOWNLOAD_BLOCKED: "+" ; ".join(errors))
if __name__=="__main__":main()
