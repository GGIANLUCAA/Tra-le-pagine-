#!/usr/bin/env python3
"""Only original museum source + fixed-20 music verification. No rendering or publishing."""
from pathlib import Path
import io,json,hashlib,urllib.request,subprocess
from PIL import Image,ImageDraw,ImageFont
OUT=Path("output/owner-titans-goblet-source");OUT.mkdir(parents=True,exist_ok=True)
met_api="https://collectionapi.metmuseum.org/public/collection/v1/objects/10499"
official="https://www.metmuseum.org/art/collection/search/10499"
met_iiif="https://collectionapi.metmuseum.org/api/collection/v1/iiif/10499/1660910/main-image"
music_url="https://incompetech.com/music/royalty-free/mp3-royaltyfree/Myst%20on%20the%20Moor.mp3"
def download(url,maxsize):
  req=urllib.request.Request(url,headers={"User-Agent":"ArtVisionResearch/1.0 (exact original Met Open Access private assessment)"})
  with urllib.request.urlopen(req,timeout=75) as r:return r.read(maxsize+1)
report={"artwork":"The Titan's Goblet","artist":"Thomas Cole","year":1833,"Met_objectID":10499,"accession":"04.29.2","museum_page":official,"Met_Open_Access_CC0":"REQUIRES_EXACT_METADATA_CONFIRMATION","full_download":False,"music20_id":"myst_on_the_moor","music20_attribution":"Myst on the Moor Kevin MacLeod (incompetech.com) CC BY 4.0"}
try:
  j=json.loads(download(met_api,500000))
  assert j["objectID"]==10499 and j["title"]=="The Titan's Goblet" and j["isPublicDomain"] is True and "Thomas Cole" in j["artistDisplayName"],"MET_OBJECT_VERIFICATION_FAILED"
  report["Met_Open_Access_CC0"]="PASS_IN_MUSEUM_API"
  candidates=[j.get("primaryImage"),met_iiif]
except Exception as e:
  print("MET_API_TEMPORARY_ERROR",type(e).__name__,str(e)[:180],flush=True)
  candidates=[met_iiif]
for link in dict.fromkeys(x for x in candidates if x):
 try:
  b=download(link,16000000)
  assert len(b)>150000 and len(b)<16000000
  with Image.open(io.BytesIO(b)) as im:
   assert im.format=="JPEG" and im.width>=1600 and im.height>=1800 and .68<im.width/im.height<.95
   im.verify()
  dest=OUT/"ORIGINAL_MET_COLE_TITANS_GOBLET.jpg";dest.write_bytes(b)
  with Image.open(io.BytesIO(b)) as im:
   m=im.convert("RGB");m.thumbnail((960,960));m.save(OUT/"IMAGE_PREVIEW.jpg",quality=86)
   report.update({"source_url":link,"source_bytes":len(b),"source_sha256":hashlib.sha256(b).hexdigest(),"source_sha1":hashlib.sha1(b).hexdigest(),"source_px":[im.width,im.height],"full_download":True})
  break
 except Exception as e:print("MET_IMAGE_ATTEMPT_FAILED",type(e).__name__,str(e)[:240],flush=True)
if not report["full_download"]:raise RuntimeError("NO_EXACT_MET_IMAGE; DO NOT GENERATE_VIDEO")
try:
 b=download(music_url,20000000)
 assert 100000<len(b)<20000000 and (b[:3]==b'ID3' or b[:2] in (b'\xff\xfb',b'\xff\xf3',b'\xff\xf2'))
 track=OUT/"MYST_ON_THE_MOOR_OFFICIAL.mp3";track.write_bytes(b)
 probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_format","-show_streams","-of","json",str(track)]))
 duration=float(probe["format"]["duration"])
 assert duration>60 and any(s.get("codec_type")=="audio" for s in probe["streams"])
 report.update({"music_bytes":len(b),"music_sha256":hashlib.sha256(b).hexdigest(),"music_seconds":duration,"music_license":"CC BY 4.0 attribution required","music_url":music_url,"music_provenance":"official Incompetech track + ffprobe"})
except Exception as e:raise RuntimeError("MUSIC_20_NOT_VERIFIED: "+type(e).__name__+" "+str(e)[:170])
(OUT/"SOURCE_MUSIC_CHECK.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print("EXACT_TITAN_SOURCE_MUSIC_OK",json.dumps(report),flush=True)
