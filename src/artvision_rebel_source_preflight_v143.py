#!/usr/bin/env python3
"""V143 non-render source photo verification: Sailko 2016 exact Brussels painting, CC BY 3.0.
Produces actual low-resolution JPEG reviews and metadata; no assumed frame approval.
"""
import hashlib, json, urllib.request
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

OUT=Path("/tmp/artvision_rebel_source_v143")
OUT.mkdir(parents=True,exist_ok=True)
BASE="https://upload.wikimedia.org/wikipedia/commons/thumb/"
FILENAMES=[
 ("sailko_37","Pieter_bruegel_il_vecchio,_Caduta_degli_angeli_ribelli,_1562,_37.JPG", (1280,853)),
 ("sailko_01","Pieter_bruegel_il_vecchio,_Caduta_degli_angeli_ribelli,_1562,_01.JPG", (1280,984)),
]
def sha(p):
 return hashlib.sha256(p.read_bytes()).hexdigest()
items=[]
for tag,filename,expect in FILENAMES:
 md5=hashlib.md5(filename.encode("utf8")).hexdigest()
 path=f"{md5[0]}/{md5[:2]}"
 from urllib.parse import quote
 url=f"{BASE}{path}/{quote(filename)}/1280px-{quote(filename)}"
 page="https://commons.wikimedia.org/wiki/File:"+filename
 dest=OUT/(tag+"_WIKIMEDIA_1280_DERIVATIVE.jpg")
 req=urllib.request.Request(url,headers={"User-Agent":"ArtVision-RMFB-source-review/1.0 (CC BY 3.0 provenance QA)","Accept":"image/jpeg,image/*"})
 with urllib.request.urlopen(req,timeout=60) as resp:
  mime=resp.headers.get("Content-Type","")
  assert mime.startswith("image/"),mime
  data=resp.read(7_000_001)
  assert 100_000<len(data)<7_000_000, len(data)
 dest.write_bytes(data)
 with Image.open(dest) as im:
  assert im.format=="JPEG" and im.size==expect, (filename,im.size)
  im=ImageOps.exif_transpose(im).convert("RGB")
  im.thumbnail((750,750))
  im.save(OUT/(tag+"_PREVIEW.jpg"),quality=90)
 items.append(dict(name=tag,source_page=page,source=url,pixels=list(expect),bytes=dest.stat().st_size,sha256=sha(dest),author="Sailko",photograph_date="2016-03-09",license="CC BY 3.0 Unported",painting="Pieter Bruegel the Elder, The Fall of the Rebel Angels, 1562, RMFAB Brussels 584",art_frame_identified="PENDING HUMAN VISUAL SOURCE REVIEW",historical_frame_proven="NO"))
report={"purpose":"verify exact licensed photo sources BEFORE cinema_museum; no MP4, no render",
        "source_pages_checked":["https://commons.wikimedia.org/wiki/File:"+f for _,f,_ in FILENAMES],
        "paint_dimensions_cm":[117,162],"photos":items,
        "museum_approved":False,"Gold_V25":False,"paid_api_calls":0}
(OUT/"SOURCE_V143_QA.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
