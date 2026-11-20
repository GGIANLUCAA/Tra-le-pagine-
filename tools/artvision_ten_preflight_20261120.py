#!/usr/bin/env python3
import concurrent.futures, json, hashlib, io, os, requests
from PIL import Image
from pathlib import Path
ITEMS=[
(10499,"The Titan's Goblet","Thomas Cole"),
(10480,"The Aegean Sea","Frederic Edwin Church"),
(10207,"An Arctic Summer: Boring Through the Pack in Melville Bay","William Bradford"),
(11050,"Approaching Thunder Storm","Martin Johnson Heade"),
(10946,"A Gorge in the Mountains (Kauterskill Clove)","Sanford Robinson Gifford"),
(11325,"Sunset on the Sea","John Frederick Kensett"),
(11396,"Stage Fort across Gloucester Harbor","Fitz Henry Lane"),
(11080,"The Falls of Niagara","Edward Hicks"),
(10482,"The Parthenon","Frederic Edwin Church"),
(11130,"Northeaster","Winslow Homer"),
(10481,"Heart of the Andes","Frederic Edwin Church"),
(10154,"The Rocky Mountains, Lander's Peak","Albert Bierstadt"),
(11122,"The Gulf Stream","Winslow Homer")
]
OUT=Path("output/artvision_10_preflight")
OUT.mkdir(parents=True,exist_ok=True)
HEADERS={"User-Agent":"ArtVision-OpenAccess-Research/1.0 (github.com/GGIANLUCAA/Tra-le-pagine-)"}
def check(it):
    object_id,title,artist=it
    result={"id":object_id,"expected_title":title,"expected_artist":artist}
    try:
        r=requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}",headers=HEADERS,timeout=35)
        r.raise_for_status()
        x=r.json()
        result.update({"actual_title":x.get("title"),"actual_artist":x.get("artistDisplayName"),
          "year":x.get("objectDate"),"license_flag":x.get("isPublicDomain"),"medium":x.get("medium"),
          "object_url":x.get("objectURL"),"primary_image":x.get("primaryImage"),"small":x.get("primaryImageSmall")})
        url=x.get("primaryImage") or x.get("primaryImageSmall")
        if not x.get("isPublicDomain") or not url:raise RuntimeError("Not image-ready Public Domain")
        z=requests.get(url,headers=HEADERS,timeout=70)
        z.raise_for_status()
        data=z.content
        img=Image.open(io.BytesIO(data));img.load()
        result.update({"pixels":[img.width,img.height],"source_sha256":hashlib.sha256(data).hexdigest(),
                       "image_kb":round(len(data)/1024),"valid":img.width>=1100 and img.height>=650,
                       "ratio":round(img.width/img.height,3)})
        if result["valid"]:
          Path(OUT/f"{object_id}.jpg").write_bytes(data)
    except Exception as exc:result.update({"valid":False,"error":str(exc)[:500]})
    print("PREFLIGHT",json.dumps(result,ensure_ascii=False),flush=True)
    return result
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as exe:
    rows=list(exe.map(check,ITEMS))
(OUT/"RESULTS.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2))
print("READY_COUNT",len([x for x in rows if x["valid"]]),"OF",len(rows),flush=True)
