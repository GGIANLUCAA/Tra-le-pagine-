#!/usr/bin/env python3
"""One-off manual Commons preview for public-domain 1871 Jules Verne engravings.
No crawl, no automatic license certification and no retry storms.
"""
import io,json,os,re,time,html
from pathlib import Path
from urllib.parse import urlencode
import requests
from PIL import Image,ImageDraw,ImageFont
ROOT=Path("output/ventimila-commons"); ROOT.mkdir(parents=True,exist_ok=True)
API="https://commons.wikimedia.org/w/api.php"
session=requests.Session()
session.headers.update({"User-Agent":"TraLePagineEditorialResearch/1.0 (one-off noncommercial educational inspection; GitHub @GGIANLUCAA)"})
params={"action":"query","generator":"categorymembers",
        "gcmtitle":"Category:Illustrations from Twenty Thousand Leagues Under the Sea by Neuville and Riou",
        "gcmtype":"file","gcmlimit":48,"prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":650,"format":"json"}
records=[]
try:
    res=session.get(API,params=params,timeout=25);res.raise_for_status()
    pages=res.json().get("query",{}).get("pages",{})
    candidates=[]
    for page in pages.values():
        image=(page.get("imageinfo") or [{}])[0]
        url=image.get("thumburl") or image.get("url")
        if url and any(url.lower().split("?")[0].endswith(x) for x in (".jpg",".jpeg",".png",".webp")):
            candidates.append((page,image,url))
    candidates.sort(key=lambda p:p[0].get("title",""))
    for n,(page,info,url) in enumerate(candidates[:20]):
        try:
            r=session.get(url,timeout=15)
            if r.status_code==429:break
            r.raise_for_status()
            im=Image.open(io.BytesIO(r.content)).convert("RGB")
            if min(im.size)<100:continue
            name=f"{n:02d}.jpg"
            im.save(ROOT/name,quality=90)
            meta=info.get("extmetadata",{})
            records.append({"file":name,"title":page["title"],
                "source_page":"https://commons.wikimedia.org/wiki/"+page["title"].replace(" ","_"),
                "original":info.get("descriptionurl"),"author":html.unescape(re.sub("<[^>]+>"," ",meta.get("Artist",{}).get("value",""))),
                "license_short_name":meta.get("LicenseShortName",{}).get("value","unverified"),
                "description":html.unescape(re.sub("<[^>]+>"," ",meta.get("ImageDescription",{}).get("value","")))[:400]})
        except Exception as e:
            records.append({"title":page.get("title"),"error":type(e).__name__})
except Exception as exc:
    (ROOT/"ERROR.txt").write_text(type(exc).__name__+": "+str(exc)[:200])
(ROOT/"sources.json").write_text(json.dumps(records,ensure_ascii=False,indent=2))
available=[x for x in records if "file" in x]
if available:
    w,h=150,245; sheet=Image.new("RGB",(w*6,h*4),(241,235,223))
    d=ImageDraw.Draw(sheet)
    for i,row in enumerate(available[:24]):
        im=Image.open(ROOT/row["file"]); im.thumbnail((w-8,h-42))
        x=(i%6)*w;y=(i//6)*h
        sheet.paste(im,(x+(w-im.width)//2,y+3))
        title=row["title"].split("by Neuville and Riou")[-1].split(".jpg")[0][-18:]
        d.text((x+3,y+h-36),row["file"]+" "+title,fill=(24,29,36))
    sheet.save(ROOT/"CONTACT.jpg",quality=90)
print("Downloaded for review only:",len(available))
