#!/usr/bin/env python3
"""Bosch Critico V21: acquisizione museale + voce riusando gli strumenti Critico V2.
Produce materiale VERO e le tempistiche voce; nessun finto video né pubblicazione."""
import json,hashlib,io,os,sys,urllib.parse,urllib.request
from pathlib import Path
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"modules"/"artvision_critico"))
from render_dali import choose_voice, music_get
CONFIG=Path(__file__).with_name("bosch_giardino_delizie_v21.json")
OUT=ROOT/"output"/"bosch-critico-v21"
def acquire():
    cfg=json.loads(CONFIG.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True,exist_ok=True)
    base="https://commons.wikimedia.org/w/api.php"
    q={"action":"query","format":"json","formatversion":"2","prop":"imageinfo","iiprop":"url|size|extmetadata","iiurlwidth":7800,"titles":cfg["commons_title"]}
    req=urllib.request.Request(base+"?"+urllib.parse.urlencode(q),headers={"User-Agent":"TraLePagine-BoschCritico/1.0 (educational artwork analysis)","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=45) as r:obj=json.load(r)
    info=obj["query"]["pages"][0]["imageinfo"][0]
    lic=str((info.get("extmetadata",{}).get("LicenseShortName") or {}).get("value","")).lower()
    usage=str((info.get("extmetadata",{}).get("UsageTerms") or {}).get("value","")).lower()
    if not ("public domain" in lic+usage or "pd"==lic or "pd-art" in lic):
        raise ValueError("Fonte senza prova pubblico dominio, fermarsi: "+lic)
    url=info.get("url") if int(info.get("width") or 0)<8000 else info.get("thumburl")
    if not url:raise ValueError("Versione Wikimedia ad alta risoluzione non disponibile")
    parts=urllib.parse.urlsplit(url)
    if parts.scheme!="https" or parts.hostname not in ("upload.wikimedia.org","thumb.wikimedia.org") or parts.username or parts.password or parts.port:
        raise ValueError("URL fuori domini Wikimedia verificati")
    req=urllib.request.Request(url,headers={"User-Agent":"TraLePagine-BoschCritico/1.0"})
    with urllib.request.urlopen(req,timeout=100) as r:
        raw=r.read(42_000_001)
    if len(raw)>42_000_000 or not raw.startswith(b"\xff\xd8\xff"):raise ValueError("Immagine insicura o oversized")
    with Image.open(io.BytesIO(raw)) as im:
        painting=ImageOps.exif_transpose(im).convert("RGB")
        assert min(painting.size)>3300,painting.size
        if max(painting.size)>8500:painting.thumbnail((8500,8500),Image.Resampling.LANCZOS)
        painting.save(OUT/"PAINTING.jpg",quality=94,subsampling=0)
        dims=list(painting.size)
    print("Painting",dims,"bytes",len(raw),flush=True)
    voice,sec,bounds,engine=choose_voice(cfg["beats"],OUT)
    print("Voice",engine,"seconds",sec,flush=True)
    music,proof=music_get(cfg,OUT)
    if music is None:raise RuntimeError("Registrazione musicale non ottenuta con licenza verificabile")
    (OUT/"MUSIC.mp3").write_bytes(music.read_bytes())
    meta={"episode":cfg["id"],"art":{"source_page":cfg["source_page"],"resolved_url":url,"dims":dims,"licence":lic,"sha256":hashlib.sha256((OUT/"PAINTING.jpg").read_bytes()).hexdigest()},"voice":{"engine":engine,"duration":sec,"beat_ends":bounds,"file":"VOCE.wav"},"music":proof,"publication_approved":False}
    (OUT/"ASSETS_TIMING.json").write_text(json.dumps(meta,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (OUT/"COPIONE.txt").write_text("\n\n".join(b["speech"] for b in cfg["beats"])+"\n",encoding="utf-8")
    return meta
if __name__=="__main__":
    print(json.dumps(acquire(),ensure_ascii=False,indent=2))
