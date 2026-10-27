"""One-shot fetch of the illustrated public-domain Gutenberg edition #120 (Louis Rhead).
Does NOT retry Wikimedia 429. No API cost, no asset invention.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from io import BytesIO
from zipfile import ZipFile
from PIL import Image
import hashlib,json
url="https://www.gutenberg.org/cache/epub/120/pg120-h.zip"
out=Path("output/isola-gutenberg-rhead");out.mkdir(parents=True,exist_ok=True)
manifest=[]
try:
    with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; IllustratedPublicDomainBook/1.0)"}),timeout=50) as resp:
        blob=resp.read(45_000_000)
    print("GUTENBERG_ZIP",len(blob))
    z=ZipFile(BytesIO(blob))
    for info in z.infolist():
        if not info.filename.lower().endswith((".jpg",".jpeg",".png")) or info.file_size>9_000_000: continue
        content=z.read(info)
        try:
            with Image.open(BytesIO(content)) as im:
                w,h=im.size
                im.verify()
        except Exception:continue
        if w<280 or h<280:continue
        index=len(manifest)+1
        target=out/f"{index:02d}.jpg"
        with Image.open(BytesIO(content)) as im:
            im.convert("RGB").save(target,quality=94,optimize=True)
        manifest.append({"index":index,"original":info.filename,"width":w,"height":h,"sha256":hashlib.sha256(content).hexdigest(),"source":url,"illustrator":"Louis Rhead (1857-1926)","publication":"Gutenberg #120, public-domain illustrated edition"})
        print("ILLUSTRATION",index,w,h,info.filename,flush=True)
except Exception as exc:
    print("SOURCE_FAILED",type(exc).__name__,str(exc)[:120],flush=True)
(out/"MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print("COLLECTED",len(manifest),flush=True)
if len(manifest)<12:raise SystemExit("Insufficient book illustrations. Do not call video complete.")
