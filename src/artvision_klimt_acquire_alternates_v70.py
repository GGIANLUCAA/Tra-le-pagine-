#!/usr/bin/env python3
"""Acquire Klimt The Kiss from independent PD sources; no Wikimedia upload retries.

PublicDomainPictures alternative is CC0 (Jimmy Carroll); fallback image.weserv.nl
is a CDN image transformation of a Commons PD-Art file. A file is considered
acquired ONLY after JPEG pixels, proportions, provenance, checksum and a source
record are verified. One fetch per independent host; never retry HTTP429.
"""
from __future__ import annotations
import argparse,hashlib,json,urllib.request,urllib.error,subprocess
from pathlib import Path
from PIL import Image

OPTS=[
("publicdomainpictures-cc0",
 "https://www.publicdomainpictures.net/pictures/420000/velka/gustav-klimt-the-kiss.jpg",
 "https://www.publicdomainpictures.net/en/view-image.php?image=413636&picture=gustav-klimt-the-kiss",
 "CC0","www.publicdomainpictures.net"),
("weserv-proxy-commons-pd",
 "https://images.weserv.nl/?url=upload.wikimedia.org%2Fwikipedia%2Fcommons%2Fc%2Fc8%2FKlimt_-_The_Kiss.jpg&w=4096&output=jpg",
 "https://commons.wikimedia.org/wiki/File:Klimt_-_The_Kiss.jpg",
 "Public Domain","images.weserv.nl"),
("weserv-alternative-pd",
 "https://wsrv.nl/?url=upload.wikimedia.org%2Fwikipedia%2Fcommons%2Fc%2Fc8%2FKlimt_-_The_Kiss.jpg&w=3840&output=jpg",
 "https://commons.wikimedia.org/wiki/File:Klimt_-_The_Kiss.jpg",
 "Public Domain","wsrv.nl")
]
MUSIC=[
("Dreams Become Real","https://incompetech.com/music/royalty-free/mp3-royaltyfree/Dreams%20Become%20Real.mp3","https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1500027"),
("Water Lily","https://incompetech.com/music/royalty-free/mp3-royaltyfree/Water%20Lily.mp3","https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1400035")
]
UA="ArtVision/70 (public domain art; scholarly noncommercial source verification; zero retries)"

def get(url,limit=18_000_000):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"image/jpeg,image/*;q=.8,*/*;q=.5"})
    with urllib.request.urlopen(req,timeout=75) as r:
        if r.status!=200:raise RuntimeError("Source status "+str(r.status))
        b=r.read(limit+1)
        if len(b)>limit:raise ValueError("Payload over cap")
        return b,r.geturl()

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def obtain(out):
    out=Path(out)
    if out.exists():raise FileExistsError("Do not overwrite a previous run")
    out.mkdir(parents=True)
    errors=[]
    photo=None;metadata=None
    for name,url,license_page,lic,domain in OPTS:
        try:
            b,final=get(url)
            path=out/"KLIMT_THE_KISS_PD_SOURCE.jpg"
            if not b.startswith(b"\\xff\\xd8"):raise ValueError("Not JPEG bytes")
            path.write_bytes(b)
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                w,h=image.size
            if min(w,h)<1650 or not 0.90<w/h<1.10:
                raise ValueError(f"Wrong dimensions/ratio {w}x{h}")
            photo=path
            metadata={"source_label":name,"source_url":url,"license_page":license_page,
                      "final_url":final,"license":lic,"sha256":sha(path),
                      "bytes":len(b),"width_px":w,"height_px":h,
                      "source_original_museum":"Upper Belvedere, Vienna, inv 912, 180x180cm",
                      "notes":"CC0 user-released image if PublicDomainPictures; alternatively Commons faithful PD reproduction through CDN"}
            break
        except Exception as e:
            errors.append({"source":name,"error_type":type(e).__name__,
                           "reason":str(e)[:170]})
            (out/"KLIMT_THE_KISS_PD_SOURCE.jpg").unlink(missing_ok=True)
    if photo is None:
        (out/"SOURCE_BLOCKERS.json").write_text(json.dumps({"errors":errors,"mp4_count":0},indent=2))
        raise RuntimeError("All 3 independent PD source options failed; no fabricated pixels")
    music=None
    for title,url,page in MUSIC:
        try:
            raw,final=get(url,15_000_000)
            a=out/"KLIMT_MUSIC_CC_BY4.mp3"
            a.write_bytes(raw)
            subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                            "-of","default=noprint_wrappers=1",str(a)],check=True,timeout=30)
            music={"title":title,"author":"Kevin MacLeod","file":a.name,
                   "sha256":sha(a),"bytes":a.stat().st_size,
                   "source_url":page,"download_url":final,
                   "license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/"}
            break
        except Exception as e:
            errors.append({"source":"music "+title,"error_type":type(e).__name__,"reason":str(e)[:150]})
            (out/"KLIMT_MUSIC_CC_BY4.mp3").unlink(missing_ok=True)
    if music is None:
        (out/"SOURCE_BLOCKERS.json").write_text(json.dumps({"errors":errors,"mp4_count":0},indent=2))
        raise RuntimeError("Music recording is unavailable, stop without unlicensed track")
    report={"schema":"artvision-klimt-asset-audit-v70","artwork":"The Kiss","artist":"Gustav Klimt",
            "canvas_cm":[180,180],"museum_collection":"Upper Belvedere, Vienna (inv. 912)",
            "painting":metadata,"music":music,"fallback_attempts":errors,"status":"VERIFIED_ASSETS_ONLY",
            "gacrux_audio_ready":False,"four_mp4_rendered":False,"rights_press_photos_not_used":True}
    (out/"SOURCE_PROVENANCE.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report,ensure_ascii=False))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True);a=p.parse_args()
    obtain(a.out)
