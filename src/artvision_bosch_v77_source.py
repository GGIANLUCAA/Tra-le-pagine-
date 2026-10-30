#!/usr/bin/env python3
"""Bosch fourth 4×1 source fetch. Public-domain painting, exactly one artwork.

No Google TTS, no video AI, no retries on HTTP429; images from pre-existing
Wikimedia PD source through an independent image delivery proxy if necessary.
"""
from pathlib import Path
from urllib.parse import urlencode,quote,urlsplit
from urllib.request import Request,urlopen
from PIL import Image
from io import BytesIO
import json,hashlib

BASE=Path("output/artvision-bosch-v77-sources")
BASE.mkdir(parents=True,exist_ok=True)
PD="https://commons.wikimedia.org/wiki/File:The_Garden_of_Earthly_Delights_by_BoschFXD.jpg"
TITLES=[
 "File:The Garden of Earthly Delights by BoschFXD.jpg",
 "File:The Garden of Earthly Delights by Hieronymus Bosch.jpg",
 "File:The Garden of Earthly Delights by Bosch High Resolution 2.jpg"
]
RECORD={"schema":"artvision-bosch-source-v77","artwork":"The Garden of Earthly Delights",
"artist":"Hieronymus Bosch","museum":"Museo Nacional del Prado, Madrid",
"official_catalog":"https://www.museodelprado.es/en/the-collection/art-work/the-garden-of-earthly-delights-triptych/02388242-6d6a-4e9e-a992-e1311eab3609",
"source":"faithful reproductions of public-domain two-dimensional art on Wikimedia Commons",
"historical_frame_known":False,"museum_gallery_image_licensed":False,
"alternate_museum_scene":"Original creative conservation-style reconstruction, NOT historical Prado display",
"photo_not_official_room":True,"attempts":[],"status":"blocked_without_verified_art"}
def fetch(url,max_bytes=26000000):
 u=urlsplit(url)
 if u.scheme!="https" or u.hostname not in ("commons.wikimedia.org","upload.wikimedia.org","images.weserv.nl","wsrv.nl"):
  raise ValueError("Unexpected network origin "+str(u.hostname))
 request=Request(url,headers={"User-Agent":"ArtVision-4x1-BoschV77/1.0 (noncommercial historical painting research, https://github.com/GGIANLUCAA/Tra-le-pagine-)","Accept":"image/jpeg,application/json,*/*"})
 with urlopen(request,timeout=95) as resp:
  if resp.status!=200:raise RuntimeError("HTTP "+str(resp.status))
  b=resp.read(max_bytes+1)
 if len(b)>max_bytes:raise ValueError("Download exceeded size cap")
 return b
def verify(data):
 if not data.startswith(b"\xff\xd8"):raise ValueError("Source is not JPEG")
 with Image.open(BytesIO(data)) as im:
  im.verify()
 with Image.open(BytesIO(data)) as im:
  w,h=im.size
  if w<3300 or h<2000 or not 1.65<w/h<2.1:
   raise ValueError("Not the expected open-triptych image, dims "+str((w,h)))
  result=im.convert("RGB")
  result.thumbnail((7500,5200),Image.Resampling.LANCZOS)
 return result,w,h

resolved=[]
for title in TITLES:
 try:
  q={"action":"query","format":"json","formatversion":"2","titles":title,
     "prop":"imageinfo","iiprop":"url|size|extmetadata","iiurlwidth":7000}
  raw=fetch("https://commons.wikimedia.org/w/api.php?"+urlencode(q),max_bytes=1000000)
  result=json.loads(raw)
  info=result["query"]["pages"][0]["imageinfo"][0]
  lic=str(info.get("extmetadata",{}).get("LicenseShortName",{}).get("value","")).lower()
  if not any(z in lic for z in ("public","pd-")):
    raise ValueError("Not marked public domain: "+lic)
  url=info.get("thumburl") or info.get("url")
  if not url:raise ValueError("No image source url")
  resolved.append((title,url,lic))
 except Exception as e:
  RECORD["attempts"].append({"title":title,"metadata_error":type(e).__name__+":"+str(e)[:140]})
if not resolved:
 # Known exact public-domain source uploaded by Wikimedia with stable path.
 resolved.append((TITLES[0],"https://commons.wikimedia.org/wiki/Special:Redirect/file/The_Garden_of_Earthly_Delights_by_BoschFXD.jpg?width=6500","PD-Art public domain (manual referenced source)"))
# First proxy each verified exact title, then direct fallback to alternate host.
for title,source,lic in resolved:
 for mode in ("weserv","wsrv","direct"):
  try:
   if mode=="weserv":u="https://images.weserv.nl/?"+urlencode({"url":source,"w":"6800","output":"jpg","q":"90"})
   elif mode=="wsrv":u="https://wsrv.nl/?"+urlencode({"url":source,"w":"6000","output":"jpg","q":"88"})
   else:u=source
   content=fetch(u)
   image,w,h=verify(content)
   path=BASE/"BOSCH_GARDEN_FULL_TRIPTYCH_PD.jpg"
   image.save(path,quality=91,subsampling=0)
   record={"source_title":title,"source_page":PD,"source_url":source,
     "retrieved_url":u,"license":lic,"original_px":[w,h],
     "local_px":list(image.size),"local_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
     "local_bytes":path.stat().st_size}
   RECORD.update({"status":"verified_authentic_open_triptych","painting":record})
   (BASE/"SOURCE_AND_RIGHTS.json").write_text(json.dumps(RECORD,ensure_ascii=False,indent=2)+"\n")
   print(json.dumps(RECORD,ensure_ascii=False))
   raise SystemExit(0)
  except Exception as e:
   RECORD["attempts"].append({"title":title,"mode":mode,"error":type(e).__name__+":"+str(e)[:160]})
(BASE/"SOURCE_AND_RIGHTS.json").write_text(json.dumps(RECORD,ensure_ascii=False,indent=2)+"\n")
raise SystemExit("No valid high-resolution public-domain Bosch painting source. Sources were tried once; no invented file.")
