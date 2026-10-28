#!/usr/bin/env python3
"""ArtVision V55 Turner Cinema Standard: authentic painting, free render, review only."""
from __future__ import annotations
import importlib.util, hashlib, json, subprocess, sys, zipfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import artvision_editorial_post_v28 as editorial
editorial.CATALOG=ROOT/"config/artvision_turner_cinema_standard_v55_editorial.json"
spec=importlib.util.spec_from_file_location("cinema_v30",ROOT/"scripts/artvision_cinema_duo_v30.py")
engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
engine.CONFIG=ROOT/"config/artvision_turner_cinema_standard_v55.json"
engine.editorial.CATALOG=editorial.CATALOG
cinema=engine.cinema
W,H=1080,1920
TITLE_LINES=["THE FIGHTING","TEMERAIRE"]
TITLE="The Fighting Temeraire"
ARTIST="J. M. W. TURNER"
SERIF="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1048576),b""):h.update(b)
    return h.hexdigest()

def fit(d,s,face,start,maxw):
    for n in range(start,21,-1):
        f=ImageFont.truetype(face,n)
        if d.textbbox((0,0),s,font=f)[2]<=maxw:return f
    raise RuntimeError("Unreadable title/artist: blocking render")

def brand(frame,alpha=1):
    """Approved V6 band: unchanged position/palette/hierarchy, exact title + artist."""
    a=max(0,min(1,float(alpha)))
    base=frame.convert("RGBA")
    overlay=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(overlay)
    d.rounded_rectangle((56,1340,1024,1590),radius=10,fill=(5,8,13,round(210*a)))
    for line,y,size in [(TITLE_LINES[0],1360,42),(TITLE_LINES[1],1417,48)]:
        f=fit(d,line,SERIF,size,900)
        bb=d.textbbox((0,0),line,font=f)
        d.text(((W-(bb[2]-bb[0]))/2,y),line,font=f,fill=(255,251,243,round(255*a)))
    d.line((130,1495,950,1495),fill=(218,198,168,round(186*a)),width=2)
    f=fit(d,ARTIST,SANS,32,900);bb=d.textbbox((0,0),ARTIST,font=f)
    d.text(((W-(bb[2]-bb[0]))/2,1521),ARTIST,font=f,fill=(255,251,243,round(255*a)))
    return Image.alpha_composite(base,overlay).convert("RGB")

cinema.signature=brand
def cover(frame,path):
    brand(frame,1).save(path,quality=95,subsampling=0)
cinema.make_cover=cover

def full(art):
    """Opaque, single authentic artwork, no ghosting or replicated-edge stretch."""
    bg=Image.new("RGB",(W,H),(11,12,17))
    whole=art.convert("RGB").copy()
    whole.thumbnail((1020,1500),Image.Resampling.LANCZOS)
    x=(W-whole.width)//2;y=(H-whole.height)//2
    ImageDraw.Draw(bg).rectangle((x-10,y-10,x+whole.width+10,y+whole.height+10),fill=(39,34,28))
    bg.paste(whole,(x,y))
    return bg
cinema.full=full


def main():
    from artvision_delivery_v55 import pack, filehash
    out=ROOT/"output/artvision-turner-cinema-standard-v55"
    slug="turner_fighting_temeraire_cinema_standard_v55"
    if (out/slug/"VIDEO_MASTER.mp4").exists():
        raise RuntimeError("Turner Cinema Standard render already exists; do not overwrite")
    result=engine.render_one("temeraire",out)
    folder=out/slug
    film=folder/"VIDEO_MASTER.mp4"
    coverfile=folder/"COPERTINA.jpg"
    first=folder/"QA_FIRST_FRAME_V55.jpg"
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(film),"-frames:v","1",str(first)],check=True)
    with Image.open(coverfile) as c, Image.open(first) as f:
        assert c.size==f.size==(W,H)
        ca=np.asarray(c.convert("RGB"),dtype=np.int16)
        fa=np.asarray(f.convert("RGB"),dtype=np.int16)
        mad=float(np.abs(ca[1340:1590]-fa[1340:1590]).mean())
        assert mad<17,("First frame/cover title band mismatch",mad)
        for y0,y1 in [(1355,1407),(1410,1475),(1516,1568)]:
            assert np.sum(np.all(ca[y0:y1,150:930]>210,axis=2))>120,("Missing title or artist",y0)
    packdir=out/"V55_DELIVERY"
    manifest=pack(film,coverfile,
                  {k:folder/("POST_"+k.upper()+".txt") for k in ("facebook","instagram","tiktok","youtube")},
                  folder/"SOURCES_AND_RIGHTS.md",folder/"VIDEO_RECIPE_V13.json",packdir)
    android=packdir/"ARTVISION_TURNER_CINEMA_STANDARD_V55_SOLO_VIDEO_ANDROID.zip"
    with zipfile.ZipFile(android,"w",allowZip64=True) as z:
        z.write(film,film.name,compress_type=zipfile.ZIP_STORED)
    with zipfile.ZipFile(android) as z:
        assert z.testzip() is None and z.getinfo(film.name).file_size==film.stat().st_size
    (out/"RELEASE_STATE_V55.json").write_text(json.dumps({
      "video_sha256":filehash(film),"status":"rendered_needs_review",
      "archive":"archive_sync_pending","opening_review":"pending_real_full_speed_watch",
      "human_approved":False,"v55_manifest":manifest},ensure_ascii=False,indent=2)+"\n")
    print("TURNER_CINEMA_STANDARD_V55_RENDERED_NEEDS_REVIEW",filehash(film),flush=True)

if __name__=="__main__":
    main()
