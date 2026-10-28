#!/usr/bin/env python3
"""Free, read-only archival media acquisition for Coleridge; NO TTS or video API calls.
Creates genuine, separately sourced Doré engravings and an editorial preview package.
Does NOT create a finished MP4, and cannot approve artistic quality.
"""
from __future__ import annotations
import hashlib,json,math,re,subprocess,time,zipfile
from io import BytesIO
from pathlib import Path
from urllib.parse import urlencode,quote
from urllib.error import HTTPError
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw,ImageFont,ImageOps

EP=Path("episodes/marinaio_antico_20261028")
OUT=Path("output/marinaio_antico_20261028")
NAVY=(14,29,40)
GOLD=(207,173,119)
PAPER=(235,226,207)
API="https://commons.wikimedia.org/w/api.php"
UA="TraLePagineEditorial/1.0 (non-commercial archive illustration review; Wikimedia Commons)"
def fetch(url,limit=12_000_000):
    with urlopen(Request(url,headers={"User-Agent":UA,"Accept":"application/json,image/jpeg,*/*"}),timeout=55) as r:
        body=r.read(limit+1)
    if len(body)>limit:raise RuntimeError("oversize asset "+url)
    return body
def digest(data):return hashlib.sha256(data).hexdigest()
def font(size,bold=False):
    name="DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/"+name,size)
def wrap(draw,txt,maxw,face):
    lines=[];line=""
    for word in txt.split():
        candidate=(line+" "+word).strip()
        if line and draw.textbbox((0,0),candidate,font=face)[2]>maxw:
            lines.append(line);line=word
        else:line=candidate
    if line:lines.append(line)
    return lines
def get_source(plate):
    name="Der Alte Matrose b %02d.jpg"%plate
    title="File:"+name
    params=urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","titles":title})
    data=json.loads(fetch(API+"?"+params,3_000_000))
    pages=list(data["query"]["pages"].values())
    if len(pages)!=1 or "imageinfo" not in pages[0]:
        raise RuntimeError("Wikimedia metadata missing for "+name)
    info=pages[0]["imageinfo"][0]
    meta=info.get("extmetadata",{})
    lic=(meta.get("LicenseShortName") or {}).get("value","")
    mark=(meta.get("LicenseUrl") or {}).get("value","")
    if not ("public domain" in lic.lower() or "publicdomain" in mark.lower()):
        raise RuntimeError("Public-domain license not verified for "+name+": "+lic)
    url=info["url"]
    if not url.startswith("https://upload.wikimedia.org/"):
        raise RuntimeError("Unexpected image host")
    delivery="wikimedia_original"
    try:
        body=fetch(url)
    except HTTPError as err:
        if err.code != 429:raise
        # One non-paid cached-media fallback for shared GitHub runner rate limits.
        # Do not retry Wikimedia or generate substitute images.
        mirror="https://images.weserv.nl/?url="+quote(url,safe="")
        body=fetch(mirror)
        delivery="external_cached_proxy_of_same_wikimedia_source"
    with Image.open(BytesIO(body)) as test:
        test.load()
        if min(test.size)<500 or test.format!="JPEG":
            raise RuntimeError("Invalid or small source "+name)
        img=test.convert("RGB")
    return img,body,{"file":name,"source_page":"https://commons.wikimedia.org/wiki/File:Der_Alte_Matrose_b_%02d.jpg"%plate,
       "source_url":url,"license":lic,"license_url":mark,
       "author":"Gustave Doré (1832–1883)","work":"The Rime of the Ancient Mariner",
       "source_sha256":digest(body),"source_size":list(img.size),"download_route":delivery}
def frame(image):
    # Original art is contained, NEVER cropped; preserve figures, hands and full composition.
    w,h=720,1280
    canvas=Image.new("RGB",(w,h),NAVY)
    d=ImageDraw.Draw(canvas)
    d.rectangle((24,36,696,1244),fill=PAPER,outline=GOLD,width=3)
    contained=ImageOps.contain(image,(646,1150),Image.Resampling.LANCZOS)
    canvas.paste(contained,((w-contained.width)//2,(h-contained.height)//2))
    return canvas
def contact_sheet(plan):
    columns=4;tw,th=350,520;gap=22;top=115
    rows=math.ceil(len(plan)/columns)
    im=Image.new("RGB",(columns*(tw+gap)+gap,top+rows*(th+gap)+25),PAPER)
    d=ImageDraw.Draw(im)
    d.rectangle((0,0,im.width,96),fill=NAVY)
    d.text((35,27),"LA BALLATA DEL VECCHIO MARINAIO  |  20 SCENE",font=font(32,True),fill=(248,238,221))
    for i,row in enumerate(plan):
        x=gap+(i%columns)*(tw+gap);y=top+(i//columns)*(th+gap)
        d.rounded_rectangle((x,y,x+tw,y+th),radius=10,fill=(251,248,238),outline=GOLD,width=2)
        p=Image.open(EP/"images"/("scena_%02d.jpg"%(i+1)))
        thumb=ImageOps.contain(p,(tw-24,th-125),Image.Resampling.LANCZOS)
        im.paste(thumb,(x+(tw-thumb.width)//2,y+10+(th-125-thumb.height)//2))
        d.text((x+14,y+th-104),"%02d  |  Tavola Doré %02d"%(i+1,row["source_plate"]),font=font(19,True),fill=NAVY)
        for j,line in enumerate(wrap(d,row["visual_intent"],tw-28,font(17))[:2]):
            d.text((x+14,y+th-72+j*25),line,font=font(17),fill=NAVY)
    im.save(OUT/"STORYBOARD_COMPLETO.jpg",quality=88,optimize=True)
def main():
    plan=json.loads((EP/"scene_plan_mariner.json").read_text(encoding="utf8"))["scenes"]
    paragraphs=[p.strip() for p in (EP/"testo.txt").read_text(encoding="utf8").split("\n\n") if p.strip()]
    if len(plan)!=20 or len(paragraphs)!=20 or any(a["narration"]!=b for a,b in zip(plan,paragraphs)):
        raise RuntimeError("Narrative paragraph / source scene mismatch")
    if len(set(p["source_plate"] for p in plan))!=20:
        raise RuntimeError("Repeated engraving source, blocked")
    EP.joinpath("images").mkdir(parents=True,exist_ok=True)
    OUT.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for i,row in enumerate(plan,1):
        art,body,source=get_source(row["source_plate"])
        target=EP/"images"/("scena_%02d.jpg"%i)
        frame(art).save(target,"JPEG",quality=91,optimize=True)
        if target.stat().st_size<35_000:raise RuntimeError("Incomplete output image")
        manifest.append({"scene":i,"visual_intent":row["visual_intent"],"narration":row["narration"],
            "scene_relevance":row["source_relevance"],"camera":row["camera_style"],
            "rights_review":"Doré original in public domain; Commons license verified by machine; artistic review pending",
            "visual_review":"pending_human_review",
            "output_file":str(target),"output_sha256":digest(target.read_bytes()),**source})
        print("VERIFIED_IMAGE",i,source["file"],source["license"],flush=True)
        time.sleep(.2)
    (EP/"PROVENIENZA_IMMAGINI.json").write_text(json.dumps({"schema":"mariner-source-ledger-v1",
        "source":"Wikimedia Commons, individual files","count":len(manifest),
        "images":manifest,"human_rights_review":"pending",
        "public_domain_original_work":True},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    # V12 exact sentence cues; no estimated voice timestamps fabricated.
    split=re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-ÙÈÉ«“])")
    cues=[];offset=0
    for i,para in enumerate(paragraphs):
        cues.append({"asset":i+1,"start_sentence":offset,"description":plan[i]["visual_intent"],
            "narration_anchor":split.split(para)[0]})
        offset+=len([x for x in split.split(para) if x.strip()])
    (EP/"scene_cues.json").write_text(json.dumps(cues,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    from episode_v3 import validate,branded_cover
    validate("marinaio_antico_20261028")
    branded_cover(OUT,EP,json.loads((EP/"metadata.json").read_text()))
    contact_sheet(plan)
    for p in ("FACEBOOK","INSTAGRAM","TIKTOK","YOUTUBE"):
        (OUT/("POST_"+p+".txt")).write_text((EP/("POST_"+p+".txt")).read_text(encoding="utf8"),encoding="utf8")
    for name in ("testo.txt","PROJECT_V13.json","scene_plan_mariner.json","PROVENIENZA_IMMAGINI.json","scene_cues.json"):
        (OUT/name).write_bytes((EP/name).read_bytes())
    qa={"episode":"marinaio_antico_20261028","state":"visual_assets_ready_voice_quota_unconfirmed",
        "scene_count":20,"source_images_distinct":20,"format_target":"720x1280 9:16",
        "video_exists":False,"voice_exists":False,"audio_substitution":False,
        "paid_video_calls":0,"rights_original":"public_domain","visual_review":"pending",
        "archive_import":"not_performed","social_publication":"not_performed",
        "note":"Only genuine archival images, cover, storyboard and text; NO MP4 until Google Gacrux integration and free quota are confirmed."}
    (OUT/"QUALITY.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    with zipfile.ZipFile(OUT/"PACCHETTO_VISUALE_NON_VIDEO.zip","w",zipfile.ZIP_DEFLATED,compresslevel=2) as z:
        for p in OUT.iterdir():
            if p.is_file() and p.suffix!=".zip":z.write(p,p.name)
        for p in sorted((EP/"images").glob("scena_*.jpg")):z.write(p,"ILLUSTRAZIONI/"+p.name)
    with zipfile.ZipFile(OUT/"PACCHETTO_VISUALE_NON_VIDEO.zip") as z:
        if z.testzip() is not None:raise RuntimeError("ZIP CRC failed")
    print("FREE_VISUAL_PACKAGE_VERIFIED",json.dumps(qa,ensure_ascii=False),flush=True)
if __name__=="__main__":
    main()
