"""Acquire public-domain N.C. Wyeth 1911 Treasure Island plates for an isolated production test.
No generated or paid sources; do not retry 403/404/429 repeatedly.
"""
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import hashlib,json,time
from PIL import Image

FILES=[
"TI-billy.jpg",
"TI-BlackDog.jpg",
"TI-blindpew.jpg",
"TI-Gunn.jpg",
"TI-Israel.jpg",
"TI-JimHawkins.jpg",
"TI-JimLJParr.jpg",
"TI-knife.jpg",
"TI-parrot.jpg",
"TI-PreparingFormutiny.jpg",
"TI-Smollett (restored).jpg",
"TI-stockade.jpg",
"TI-treasure.jpg",
"TI-BlackSpot.jpg",
"N. C. Wyeth - Captain Smollet Defies the Mutineers.jpg",
"N. C. Wyeth - Treasure Island - Jim Hawkins leaves home.jpg",
"N. C. Wyeth - Treasure Island - Captain Bones routs Black Dog.jpg",
"N. C. Wyeth - Treasure Island - The Hostage.jpg",
"NC Wyeth - Jim Hawkins, Long John Silver and his Parrot.jpg",
]
root=Path("output/isola-wyeth-originals")
root.mkdir(parents=True,exist_ok=True)
manifest=[]
for idx,name in enumerate(FILES,1):
    canonical=name.replace(" ","_")
    md5=hashlib.md5(canonical.encode("utf-8")).hexdigest()
    url=f"https://upload.wikimedia.org/wikipedia/commons/{md5[0]}/{md5[:2]}/{quote(canonical)}"
    rec={"index":idx,"filename":name,"url":url,"commons":"https://commons.wikimedia.org/wiki/File:"+quote(canonical),"copyright_review":"Wyeth died 1945; 1911 illustrated edition; Commons metadata PD. Verify per-file before commercial release"}
    try:
        req=Request(url,headers={"User-Agent":"TraLePagine-CulturalProduction/1.0 (educational assets; one-time fetch)","Accept":"image/jpeg,image/*"})
        with urlopen(req,timeout=25) as resp:
            blob=resp.read(12_000_000)
        if not (blob[:2]==b"\\xff\\xd8" or blob[:8].startswith(b"\\x89PNG")):
            raise ValueError("not a jpeg/png image")
        target=root/f"{idx:02d}.jpg"
        target.write_bytes(blob)
        with Image.open(target) as im:
            im.verify()
        rec.update({"status":"ok","size_bytes":len(blob),"sha256":hashlib.sha256(blob).hexdigest()})
    except HTTPError as e:
        rec.update({"status":"http_error","code":e.code})
        print("SOURCE_HTTP",idx,e.code,name,flush=True)
    except Exception as e:
        rec.update({"status":"error","reason":type(e).__name__})
        print("SOURCE_ERR",idx,type(e).__name__,name,flush=True)
    else:
        print("ASSET",idx,len(blob),name,flush=True)
    manifest.append(rec)
    time.sleep(0.15)
(root/"MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf8")
ok=sum(x["status"]=="ok" for x in manifest)
print(f"ACQUIRED {ok}/{len(FILES)}",flush=True)
if ok<6: raise SystemExit("Insufficient original images. No fake success.")
