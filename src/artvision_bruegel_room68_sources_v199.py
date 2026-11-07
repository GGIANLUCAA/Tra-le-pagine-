#!/usr/bin/env python3
"""ArtVision V199 source-only: 2016 museum Room 68 photographs, no film rendering.
No invented museum. Distinguish metadata category from actual photo geometry.
"""
from __future__ import annotations
import hashlib,json,os,time,urllib.parse,urllib.request
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from io import BytesIO

OUT=Path(os.getenv("SOURCE_OUT","/tmp/artvision_bruegel_room68_v199"))
OUT.mkdir(parents=True,exist_ok=True)
NAMES={
"ROOM68_KONINKLIJKE_44":"Koninklijke Musea voor Schone Kunsten van België 44.jpg",
"REBEL_SAILKO_11":"Pieter bruegel il vecchio, Caduta degli angeli ribelli, 1562, 11.JPG",
"REBEL_SAILKO_19":"Pieter bruegel il vecchio, Caduta degli angeli ribelli, 1562, 19.JPG",
"REBEL_SAILKO_36":"Pieter bruegel il vecchio, Caduta degli angeli ribelli, 1562, 36.JPG",
"REBEL_SAILKO_01":"Pieter bruegel il vecchio, Caduta degli angeli ribelli, 1562, 01.JPG"
}
HEADER={"User-Agent":"ArtVisionMuseumResearch/1.0 (educational source audit; CC attribution; 0 paid calls)"}
def load(url,retries=2):
    err=None
    for trial in range(retries):
        try:
            req=urllib.request.Request(url,headers=HEADER)
            with urllib.request.urlopen(req,timeout=50) as response:
                return response.read()
        except Exception as e:
            err=e
            if trial+1<retries:time.sleep(2*(trial+1))
    raise err

rows=[];errors=[];tiles=[]
for key,name in NAMES.items():
    entry={"candidate_id":key,"commons_title":name,"source_only":True,
           "actual_gallery_contains_this_exact_painting":"UNVERIFIED",
           "full_room_approved":False,"museum_gold_master":False,
           "artistic_full_speed_review":"NOT_PERFORMED"}
    try:
        params={"action":"query","format":"json","titles":"File:"+name,"prop":"imageinfo",
                "iiprop":"url|sha1|size|mime|extmetadata","iiurlwidth":960}
        q=json.loads(load("https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(params)))
        obj=next(iter(q["query"]["pages"].values()))
        if "imageinfo" not in obj:raise ValueError("Missing Commons imageinfo")
        info=obj["imageinfo"][0]
        lic=info.get("extmetadata",{}).get("LicenseShortName",{}).get("value","")
        attribution=info.get("extmetadata",{}).get("Artist",{}).get("value","")
        entry.update({"commons_url":info.get("descriptionurl"),
            "original_url":info.get("url"),"original_sha1":info.get("sha1"),
            "original_size_bytes":info.get("size"),"original_pixels":[info.get("width"),info.get("height")],
            "license_short_name":lic,"attribution_raw_html":attribution[:400],
            "license_compliant_for_video":False,
            "license_notes":"needs per-photo CC attribution and rights QA"})
        if not any(v in lic for v in ["CC BY","CC0"]):
            entry["status"]="UNSUPPORTED_LICENSE";rows.append(entry);continue
        url=info.get("thumburl")
        if not url:raise ValueError("Commons thumbnail link unavailable")
        blob=load(url)
        pic=Image.open(BytesIO(blob)).convert("RGB")
        if pic.width<250 or pic.height<200:raise ValueError("Tiny source image")
        entry["thumb_bytes"]=len(blob);entry["thumb_pixels"]=pic.size
        entry["thumb_sha256"]=hashlib.sha256(blob).hexdigest()
        dest=OUT/(key+".jpg")
        dest.write_bytes(blob)
        entry["filename"]=dest.name;entry["status"]="THUMB_SOURCE_DOWNLOADED_NEEDS_HUMAN_VISUAL_REVIEW"
        rows.append(entry)
        tile=Image.new("RGB",(640,530),(22,22,25))
        canvas=ImageOps.contain(pic,(620,445),Image.Resampling.LANCZOS)
        tile.paste(canvas,((640-canvas.width)//2,18+(445-canvas.height)//2))
        d=ImageDraw.Draw(tile)
        d.text((15,468),key,fill=(255,255,255))
        d.text((15,489),f"{pic.width}x{pic.height} · {lic} · source-only",fill=(208,208,208))
        tiles.append(tile)
    except Exception as e:
        entry["status"]="ERROR";entry["error"]=type(e).__name__+": "+str(e)[:240]
        errors.append({"candidate_id":key,"message":entry["error"]})
        rows.append(entry)
    print(json.dumps({k:entry.get(k) for k in ("candidate_id","status","original_pixels","license_short_name","error")},ensure_ascii=False),flush=True)
if tiles:
    sheet=Image.new("RGB",(1280,530*((len(tiles)+1)//2)),(15,15,16))
    for i,im in enumerate(tiles):sheet.paste(im,((i%2)*640,(i//2)*530))
    sheet.save(OUT/"ROOM68_REBEL_CONTACT_V199.jpg",quality=90)
record={"schema":"artvision-room68-photo-study-v199",
        "project":"ArtVision 4x1 only","work":"The Fall of the Rebel Angels (1562), inv 584",
        "museum":"Royal Museums of Fine Arts of Belgium / Old Masters Room 68",
        "evidence":"Wikimedia Commons Room 68 category and work-specific Sailko photographs",
        "not_authenticated_full_room_current":True,
        "no_paid_calls":True,"no_video_render":True,"no_gold_approval":True,
        "photo_candidates":rows,"errors":errors,
        "next_gate":"Manual visual comparison: room geometry, frame exact-work identity, license, dates, same room entrance/exit"}
(OUT/"SOURCE_AND_GATE_V199.json").write_text(json.dumps(record,indent=2,ensure_ascii=False),encoding="utf-8")
print("V199_DONE candidates",len(rows),"thumbs",len(tiles),"errors",len(errors),flush=True)
