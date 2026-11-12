#!/usr/bin/env python3
"""NAZCA source scout: Commons imageinfo + license + byte validation, NO generation.

Selects diverse actual Nazca aerial photographs and a single real aerial video;
rejects missing, tiny, nonfree or license-indeterminate media. Reports only
what was actually downloaded and decoded, without pretending future master exists.
"""
import hashlib, html, io, json, os, re, subprocess, time, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont

OUT=Path("output/giuliano-nazca-scout"); OUT.mkdir(parents=True,exist_ok=True)
API="https://commons.wikimedia.org/w/api.php"
UA={"User-Agent":"TraLePagine-Giuliano-Nazca-SourceScout/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-; educational audiovisual attribution audit)","Accept":"application/json, image/*"}
QUERIES=[
    "Nazca lines geoglyph", "Nazca lines hummingbird","Nazca lines monkey",
    "Nazca lines spider","Nazca lines condor","Nazca lines whale",
    "Nazca lines astronaut","Nazca lines tree hands",
    "Nazca geoglyph trapezoid","Nazca lines desert aerial",
    "Líneas de Nazca","Nazca lines flower",
]
SEEDS=[
    "Nazca Lines Hummingbird.jpg", "NazcaLinesMonkey.jpg",
    "Nazca-Linien 062016 Hummingbird.jpg","Lignes de Nazca oiseau.jpg",
    "Nazca lines fiore, Nasca.jpg","04-Nazca Lines-nX-23.jpg",
    "Líneas de Nazca, Nazca, Perú, 2015-07-29, DD 52.JPG",
]
VIDEO="Perou geoglyphes de Nazca video.ogv"
ACCEPT=("cc by","public domain","cc0","pd-old","cc-by","attribution","público","dominio pubblico")
REJECT=("noncommercial","non-commercial","no derivatives","no-derivatives","cc by-nc","cc by-nd","fair use")
def req(params, attempts=2):
    url=API+"?"+urllib.parse.urlencode(params)
    for n in range(attempts):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=40) as r:
                return json.loads(r.read(4_000_000))
        except Exception as e:
            if n+1>=attempts: raise
            time.sleep(1.5*(n+1))
def metadata_titles(names):
    result=[]
    for i in range(0,len(names),20):
        j=req({"action":"query","titles":"|".join("File:"+x for x in names[i:i+20]),
               "prop":"imageinfo","iiprop":"url|extmetadata|size|mime",
               "iiurlwidth":"1920","format":"json","formatversion":"2"})
        for p in j.get("query",{}).get("pages",[]):
            info=(p.get("imageinfo") or [{}])[0]
            if "missing" not in p and info:
                result.append((p["title"],info))
    return result
def search(query):
    j=req({"action":"query","generator":"search","gsrnamespace":6,"gsrsearch":query,
           "gsrlimit":"35","prop":"imageinfo",
           "iiprop":"url|extmetadata|size|mime","iiurlwidth":"1920",
           "format":"json","formatversion":"2"})
    return [(p["title"],p["imageinfo"][0]) for p in j.get("query",{}).get("pages",[]) if p.get("imageinfo")]
def text(value):
    return re.sub(r"\s+"," ",re.sub(r"<[^>]*>"," ",html.unescape(str(value)))).strip()
def hash_file(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for c in iter(lambda:f.read(1<<20),b""):h.update(c)
    return h.hexdigest()
def license_record(info):
    meta=info.get("extmetadata") or {}
    short=text((meta.get("LicenseShortName") or {}).get("value",""))
    link=(meta.get("LicenseUrl") or {}).get("value","")
    author=text((meta.get("Artist") or {}).get("value",""))[:200]
    credit=text((meta.get("Credit") or {}).get("value",""))[:200]
    state=(short+" "+link).lower()
    allowed=(any(term in state for term in ("cc by","cc-by","cc0","public domain","pd-old"))
             and not any(term in state for term in REJECT))
    # Some Commons files use only 'Attribution' but lack explicit freedom; exclude.
    return {"license":short,"license_url":link,"author":author,"credit":credit,"allowed":allowed}
def retrieve(url,path,limit):
    r=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(r,timeout=70) as response:
        length=int(response.headers.get("Content-Length") or 0)
        if length>limit:raise ValueError("declared content too large")
        n=0
        with Path(path).open("wb") as out:
            while True:
                c=response.read(1<<20)
                if not c:break
                n+=len(c)
                if n>limit:raise ValueError("source exceeds per-file limit")
                out.write(c)
    return n
def family(title):
    n=title.lower()
    for key,terms in [
        ("hummingbird",("hummingbird","colibri","colibrí","kolibri")),
        ("monkey",("monkey","mono","affe")),
        ("spider",("spider","araña","spinne")),
        ("whale",("whale","ballena")),
        ("condor",("condor","cóndor")),
        ("astronaut",("astronaut","hombre-buho","owlman")),
        ("tree-hands",("hands","manos","árbol","tree")),
        ("flowers",("flower","fiore","flor")),
        ("birds",("bird","oiseau","ave","flamingo","heron","pájaro")),
        ("geometry",("lineas","líneas","trapezoid","geometry","lines","linien")),
    ]:
        if any(t in n for t in terms):return key
    return "desert"
def main():
    all_media={};issues=[]
    for title,info in metadata_titles(SEEDS+[VIDEO]):
        all_media[title]=(title,info)
    for q in QUERIES:
        try:
            results=search(q)
            for t,i in results:
                all_media.setdefault(t,(t,i))
            print("SCOUT_QUERY",q,"results",len(results),flush=True)
        except Exception as e:
            issues.append({"query":q,"error":type(e).__name__+" "+str(e)[:90]})
    ordered=sorted(all_media.values(),key=lambda item:(
        item[0].replace("File:","") not in SEEDS,
        not any(w in item[0].lower() for w in ("nazca","nasca","líneas","linien")),
        -min(3000,item[1].get("width",0)),
        item[0]))
    candidates=[];excluded=[]
    for title,info in ordered:
        mime=info.get("mime","").lower(); lic=license_record(info)
        if not lic["allowed"] or mime not in ("image/jpeg","image/png","image/webp"):
            excluded.append({"title":title,"reason":"license_or_mime","license":lic["license"],"mime":mime})
            continue
        if min(info.get("width",0),info.get("height",0))<700:
            continue
        candidates.append((title,info,lic))
    # Broad coverage: at most 4 images from each theme and ~3 per search family.
    chosen=[];per_family={};min_target=23
    for title,info,lic in candidates:
        k=family(title)
        if per_family.get(k,0)>= (8 if k=="geometry" else 4):continue
        chosen.append((title,info,lic,k));per_family[k]=per_family.get(k,0)+1
        if len(chosen)>=34:break
    if len(chosen)<min_target:
        for item in candidates:
            if item[0] not in {v[0] for v in chosen}:
                chosen.append((*item,family(item[0])))
                if len(chosen)>=min_target:break
    photos=[]
    for idx,(title,info,lic,k) in enumerate(chosen):
        url=info.get("thumburl") or info.get("url")
        if not url:continue
        target=OUT/("nazca_%02d.jpg"%len(photos))
        try:
            count=retrieve(url,target,10_000_000)
            with Image.open(target) as image:
                image.load()
                if min(image.size)<600:raise ValueError("photo lacks usable resolution")
                image=ImageOps.exif_transpose(image).convert("RGB")
                # Normalize JPEG: license and original Commons URL preserved in metadata.
                image.thumbnail((1920,1920),Image.Resampling.LANCZOS)
                image.save(target,quality=89,optimize=True)
                dims=list(image.size)
            photos.append({"id":"p%02d"%len(photos),"title":title,
                "page":"https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"),safe=":_()"),
                "source_url":info.get("url"),"download_url":url,
                "license":lic["license"],"license_url":lic["license_url"],
                "author":lic["author"],"credit":lic["credit"],"theme":k,
                "filename":target.name,"dimensions":dims,"sha256":hash_file(target),
                "bytes":target.stat().st_size,"transform":"thumbnail resize and JPEG compression, no invented pixels"})
            print("VERIFIED_NAZCA_PHOTO",len(photos),k,title[:85],dims,flush=True)
        except Exception as e:
            target.unlink(missing_ok=True)
            issues.append({"title":title,"error":type(e).__name__+" "+str(e)[:120]})
    real_video=None
    for title,info in metadata_titles([VIDEO]):
        lic=license_record(info)
        if not lic["allowed"] or info.get("mime") not in ("application/ogg","video/ogg"):
            issues.append({"video":title,"error":"video_license_or_mime_not_approved","license":lic["license"]})
            continue
        target=OUT/"NAZCA_REAL_AERIAL_SOURCE.ogv"
        try:
            count=retrieve(info["url"],target,42_000_000)
            process=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration:stream=codec_type,width,height",
                                    "-of","json",str(target)],capture_output=True,text=True,timeout=35,check=True)
            data=json.loads(process.stdout)
            if float(data.get("format",{}).get("duration",0))<15:raise ValueError("video too short")
            if not any(v.get("codec_type")=="video" for v in data.get("streams",[])):
                raise ValueError("no video track")
            real_video={"title":title,"page":"https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"),safe=":_()"),
                        "source_url":info["url"],"author":lic["author"],"license":lic["license"],
                        "license_url":lic["license_url"],"filename":target.name,"sha256":hash_file(target),
                        "bytes":count,"duration_s":float(data["format"]["duration"]),"type":"authentic aerial footage"}
            print("VERIFIED_NAZCA_REAL_VIDEO",count,real_video["duration_s"],flush=True)
        except Exception as e:
            target.unlink(missing_ok=True)
            issues.append({"video":title,"error":type(e).__name__+" "+str(e)[:150]})
    # Build contact sheet showing actual media frames and photo diversity.
    tiles=[]
    for photo in photos:
        with Image.open(OUT/photo["filename"]) as im:
            thumb=ImageOps.contain(im.convert("RGB"),(256,190),Image.Resampling.LANCZOS)
        tile=Image.new("RGB",(270,235),(15,18,23)); tile.paste(thumb,((270-thumb.width)//2,4))
        ImageDraw.Draw(tile).text((8,198),photo["id"]+" "+photo["theme"],fill=(245,233,206))
        tiles.append(tile)
    if tiles:
        sheet=Image.new("RGB",(270*5,235*((len(tiles)+4)//5)),(12,16,20))
        for i,im in enumerate(tiles):sheet.paste(im,((i%5)*270,(i//5)*235))
        sheet.save(OUT/"CONTACT_SHEET.jpg",quality=90)
    report={"schema":"nazca-source-scout-v1","status":"SOURCE_VERIFIED" if len(photos)>=18 and real_video else "INSUFFICIENT",
            "photos":photos,"real_video":real_video,"issues":issues,
            "photo_count":len(photos),"uses_generated_video":False,
            "source_policy":"Commons PD/CC BY/CC BY-SA; attribution and license retained; originals transformed by resizing only",
            "research_reference":"Sakai et al. 2024 PNAS doi:10.1073/pnas.2407652121 — 303 new geoglyphs; do not republish scientific figures without checking license",
            "release_authorized":False}
    (OUT/"SOURCE_SCOUT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print("NAZCA_SOURCE_SCOUT",report["status"],"photos",len(photos),"video",bool(real_video),"issues",len(issues),flush=True)
    if report["status"]!="SOURCE_VERIFIED":raise SystemExit("NAZCA_SOURCE_INSUFFICIENT; do not claim finished production")
if __name__=="__main__":main()
