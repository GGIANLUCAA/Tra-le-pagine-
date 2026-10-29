#!/usr/bin/env python3
"""Free, non-narrated ASSET ACQUISITION for Peter Rabbit (1902).
NO video, NO TTS, NO paid APIs, NO automatic publishing.
Produces original-illustration source copies, 9:16 stills, cover, contact sheet,
and real per-file provenance hashes. This is not a final episode.
"""
from __future__ import annotations
import argparse, hashlib, io, json, os, textwrap
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont, ImageOps

URL = "https://www.gutenberg.org/cache/epub/14838/pg14838-images.html"
PLAN = Path("episodes/peter_rabbit_20261029/SCENE_E_FONTI.json")
W,H = 720,1280
def sha(b): return hashlib.sha256(b).hexdigest()
def font(size,serif=True):
    p="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf" if serif else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(p,size)
def background():
    im=Image.new("RGB",(W,H))
    pix=im.load()
    for y in range(H):
        v=y/H
        rgb=(int(245-12*v),int(238-16*v),int(222-19*v))
        for x in range(W):pix[x,y]=rgb
    return im
def draw_center(draw,y,txt,ft,fill):
    bbox=draw.textbbox((0,0),txt,font=ft)
    draw.text(((W-(bbox[2]-bbox[0]))/2,y),txt,font=ft,fill=fill)
def frame(src,num,opening=False):
    canvas=background()
    d=ImageDraw.Draw(canvas)
    d.rectangle((30,190,690,1070),outline=(155,121,83),width=2)
    # Original source art is contained in full, NEVER cropped through faces.
    art=ImageOps.contain(src.convert("RGB"),(620,810),Image.Resampling.LANCZOS)
    canvas.paste(art,((W-art.width)//2,220+(810-art.height)//2))
    d=ImageDraw.Draw(canvas)
    draw_center(d,82,"TRA LE PAGINE",font(27,False),(77,67,55))
    if opening:
        draw_center(d,1110,"PETER CONIGLIO",font(44),(62,56,50))
        draw_center(d,1172,"BEATRIX POTTER",font(23,False),(100,81,66))
    else:
        d.line((238,1135,482,1135),fill=(159,130,92),width=2)
    return canvas
def cover(src):
    im=background()
    art=ImageOps.contain(src.convert("RGB"),(650,780),Image.Resampling.LANCZOS)
    im.paste(art,((W-art.width)//2,270+(790-art.height)//2))
    d=ImageDraw.Draw(im)
    d.rectangle((22,22,698,1258),outline=(136,105,77),width=3)
    draw_center(d,91,"TRA LE PAGINE",font(28,False),(69,60,50))
    draw_center(d,173,"PETER CONIGLIO",font(48),(53,57,47))
    draw_center(d,234,"IL GIARDINO PROIBITO",font(24,False),(87,78,65))
    draw_center(d,1113,"BEATRIX POTTER",font(27),(65,57,47))
    draw_center(d,1165,"ILLUSTRAZIONI ORIGINALI · 1902",font(17,False),(93,82,72))
    return im
def main():
    a=argparse.ArgumentParser();a.add_argument("--out",default="output/peter_rabbit_20261029");args=a.parse_args()
    out=Path(args.out);orig=out/"ORIGINALI_1902";stills=out/"STILLS_9_16"
    orig.mkdir(parents=True,exist_ok=True);stills.mkdir(parents=True,exist_ok=True)
    plan=json.loads(PLAN.read_text(encoding="utf-8"))
    assert len(plan["scenes"])==20
    session=requests.Session();session.headers.update({"User-Agent":"TraLePagine-PublicDomainIllustrationResearch/1.0"})
    response=session.get(URL,timeout=55);response.raise_for_status()
    soup=BeautifulSoup(response.content,"html.parser")
    imgs=[im for im in soup.select("img") if "images/" in im.get("src","")]
    if len(imgs)<28:raise RuntimeError(f"Expected >=28 original 1902 illustrations; found {len(imgs)}")
    entries=[];hashes=set();images={}
    for scene in plan["scenes"]:
        index=scene["source_img_order_zero_based"]
        if not 0<=index<len(imgs):raise RuntimeError("Image index out of range")
        link=urljoin(response.url,imgs[index]["src"])
        r=session.get(link,timeout=55);r.raise_for_status()
        if len(r.content)<9000:raise RuntimeError(f"Image suspiciously small: {link}")
        original=Image.open(io.BytesIO(r.content));original.load()
        if original.width<250 or original.height<250:raise RuntimeError(f"Low resolution source: {link}")
        h=sha(r.content)
        if h in hashes:raise RuntimeError("Duplicate original illustration")
        hashes.add(h)
        n=scene["id"];stem=f"SCENA_{n:02d}"
        original_path=orig/(stem+Path(link).suffix.lower())
        original_path.write_bytes(r.content)
        rendered=frame(original,n,opening=(n==1))
        dest=stills/(stem+".jpg");rendered.save(dest,quality=94,subsampling=0,optimize=True)
        entries.append({"scene_id":n,"visual":scene["visual"],"source_url":link,
            "source_index":index,"source_sha256":h,"source_bytes":len(r.content),
            "source_dimensions":[original.width,original.height],
            "source_file":str(original_path.relative_to(out)),
            "rendered_file":str(dest.relative_to(out)),
            "rendered_sha256":sha(dest.read_bytes()),
            "rights_basis":"Beatrix Potter 1902, died 1943; public domain in Italy; scan attribution preserved",
            "image_qa":"dimension_and_full_contain_pass; artistic review pending",
            "paid_calls":0})
        images[n]=rendered
    # Cover uses the source of scene 7: a meaningful chase/encounter illustration.
    source_cover=Image.open(orig/(f"SCENA_07"+Path(entries[6]["source_url"]).suffix.lower()))
    cov=out/"COPERTINA_PETER_CONIGLIO.jpg"
    cover(source_cover).save(cov,quality=95,subsampling=0,optimize=True)
    sheet=Image.new("RGB",(4*230,5*420),(243,238,226))
    d=ImageDraw.Draw(sheet)
    for i in range(20):
        im=images[i+1];thumb=im.resize((216,384),Image.Resampling.LANCZOS)
        x=(i%4)*230+7;y=(i//4)*420+5
        sheet.paste(thumb,(x,y));d.text((x+4,y+387),f"SCENA {i+1:02d}",font=font(16,False),fill=(40,40,40))
    contact=out/"STORYBOARD_20_SCENE.jpg"
    sheet.save(contact,quality=88,optimize=True)
    report={"episode":plan["episode"],"status":"assets_acquired_not_narrated_not_final",
       "source_page":URL,"source_edition":"1902 Beatrix Potter", "scene_count":len(entries),
       "unique_source_hashes":len(hashes),"cover_sha256":sha(cov.read_bytes()),
       "contact_sheet_sha256":sha(contact.read_bytes()),
       "gacrux_free_quota_attested":os.environ.get("GEMINI_TTS_FREE_QUOTA_CONFIRMED","").lower()=="true",
       "gacrux_key_present":bool(os.environ.get("GEMINI_API_KEY")),
       "tts_calls":0,"paid_video_calls":0,"video_exists":False,
       "approval":"not_final","scenes":entries}
    (out/"ASSET_PROVENIENZA_QA.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    # Copy editorial text in the downloadable asset dossier without claiming a final master.
    for name in ("testo.txt","SCENE_E_FONTI.json","PROJECT_V13.json","SCHEDE_VISUALI_V35.json","POST_SOCIAL.json","FONTI_E_DIRITTI.md","STATO_20261029.md"):
        (out/name).write_bytes((PLAN.parent/name).read_bytes())
    print("REAL_ASSET_ACQUISITION",len(entries),"source hashes",len(hashes),
          "cover",cov.stat().st_size,"gacrux_quota_attested",report["gacrux_free_quota_attested"],
          "NO MP4 / NO TTS / NO PAID API")
if __name__=="__main__":main()
