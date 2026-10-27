#!/usr/bin/env python3
"""V39: acquire matched 1871 engravings before Gacrux; never use unrelated filler."""
from __future__ import annotations
import hashlib,html,json,re,time
from io import BytesIO
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from PIL import Image,ImageDraw,ImageOps

ROOT=Path("episodes/nautilus_20261027")
SOURCE="https://www.gutenberg.org/cache/epub/54873/pg54873-images.html"
BASE="https://www.gutenberg.org/cache/epub/54873/images/"
SPLIT=re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-ÙÈÉ«“])",re.U)

def fetch(url,maxlen=16_000_000):
    with urlopen(Request(url,headers={"User-Agent":"TraLePagineStudio/1.0 (historical editorial)" ,"Accept":"text/html,image/jpeg,*/*"}),timeout=50) as r:
        data=r.read(maxlen+1)
    if len(data)>maxlen:raise RuntimeError("Oversized historical asset: "+url)
    return data

def captions_from(htmltext):
    refs={}
    pat=r'<img\b[^>]*src="images/(im\d+)\.jpg"[^>]*>\s*<p class="caption"[^>]*>(.*?)</p>'
    for m in re.finditer(pat,htmltext,re.I|re.S):
        raw=re.sub(r"<[^>]+>"," ",m.group(2))
        caption=" ".join(html.unescape(raw).split())
        refs[m.group(1)]=caption
    return refs

def scene_frame(art,index):
    # Single archival illustration, fully legible. No ghosting / image crossfades.
    art=ImageOps.exif_transpose(art.convert("RGB"))
    w,h=960,1707
    out=Image.new("RGB",(w,h),(14,30,42))
    dr=ImageDraw.Draw(out)
    for yy in range(h):
        k=yy/h
        dr.line((0,yy,w,yy),fill=(int(10+13*k),int(27+9*k),int(43+9*k)))
    # Slight variations in matte geometry follow the actual scene, without cutting art.
    urgency=index in (1,2,5,6,17,18,19,20,21,22)
    pad=47 if urgency else 65
    box=(pad,92,w-pad,h-98)
    dr.rounded_rectangle(box,radius=18,fill=(238,224,201),outline=(190,157,103),width=5)
    max_size=(box[2]-box[0]-38,box[3]-box[1]-39)
    kept=ImageOps.contain(art,max_size,Image.Resampling.LANCZOS)
    xx=(w-kept.width)//2;yy=(h-kept.height)//2
    out.paste(kept,(xx,yy))
    dr=ImageDraw.Draw(out)
    dr.rectangle((22,22,w-22,h-22),outline=(181,152,101),width=3)
    return out

def make():
    metadata=json.loads((ROOT/"scene_plan_verne.json").read_text(encoding="utf-8"))
    plan=metadata["scenes"]
    paras=[p.strip() for p in (ROOT/"testo.txt").read_text(encoding="utf-8").split("\n\n") if p.strip()]
    if not plan or len(paras)!=len(plan) or any(a["narration"]!=b for a,b in zip(plan,paras)):
        raise RuntimeError("Narration/storyboard mismatch")
    page=fetch(SOURCE,9_000_000).decode("utf-8","replace")
    labels=captions_from(page)
    requested=[p["source_image_id"] for p in plan]
    if len(set(requested))!=len(requested):raise RuntimeError("Duplicated source illustrations")
    missing=[img for img in requested if not labels.get(img)]
    if missing:raise RuntimeError("Uncaptioned or missing original scans (no filler): "+repr(missing))
    larger=set(re.findall(r'href="images/(imx\d+)\.jpg"',page,re.I))
    (ROOT/"images").mkdir(exist_ok=True)
    manifest=[];cues=[];start=0
    for i,(row,para) in enumerate(zip(plan,paras),1):
        key=row["source_image_id"]
        num=key.removeprefix("im")
        preferred="imx"+num if "imx"+num in larger else key
        uri=BASE+preferred+".jpg"
        tried_large=False
        try:
            src=fetch(uri,16_000_000)
        except (HTTPError,URLError) as err:
            if preferred==key:raise
            # Exactly one documented fallback to the smaller authentic scan.
            tried_large=True
            preferred=key
            uri=BASE+key+".jpg"
            src=fetch(uri,16_000_000)
        with Image.open(BytesIO(src)) as image:
            image.load()
            if min(image.size)<180:raise RuntimeError("Original artwork too small: "+key)
            im=scene_frame(image,i)
        imagefile=ROOT/"images"/("scena_%02d.jpg"%i)
        im.save(imagefile,"JPEG",quality=92,optimize=True)
        if imagefile.stat().st_size<35_000:raise RuntimeError("Artwork incomplete "+key)
        cue={"asset":i,"start_sentence":start,"description":row["visual_intent"],
             "narration_anchor":SPLIT.split(para)[0]}
        cues.append(cue)
        start+=len([x for x in SPLIT.split(para) if x.strip()])
        manifest.append({"asset":i,"image":str(imagefile),"image_id":key,
           "original_caption":labels[key],"source_page":SOURCE,"source_url":uri,
           "source_sha256":hashlib.sha256(src).hexdigest(),
           "output_sha256":hashlib.sha256(imagefile.read_bytes()).hexdigest(),
           "artist":"Alphonse de Neuville / Édouard Riou (original illustrated Hetzel edition)",
           "rights":"Original historical engraving; public domain in Italy by author death dates; digital reproduction and provider terms to confirm",
           "fallback_smaller_authentic":tried_large,
           "visual_review":"needs_final_human_review"})
        print("SOURCE",i,key,labels[key],"bytes",len(src),flush=True)
        time.sleep(.14)
    (ROOT/"scene_cues.json").write_text(json.dumps(cues,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (ROOT/"PROVENIENZA_IMMAGINI.json").write_text(json.dumps({
       "schema":"verne-historical-image-provenance-v1",
       "work":"Vingt mille lieues sous les mers", "text_author":"Jules Verne",
       "visual_artists":"Alphonse de Neuville and Édouard Riou",
       "original_ed":"J. Hetzel, historical illustrated edition, 1871",
       "source":SOURCE,"images":manifest,
       "note":"Authoritative original illustrations; art and speech correspondence requires artistic review",
       "publication":"not performed"},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("PREFLIGHT SUCCESS",len(plan),"matched, original scans saved",flush=True)

if __name__=="__main__":make()
