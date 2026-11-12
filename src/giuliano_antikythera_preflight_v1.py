#!/usr/bin/env python3
"""GIULIANO EP03: rights-aware source preflight and 20s silent visual test.
No API keys, no voice synthesis, no new spending, no publication.
"""
from __future__ import annotations
import hashlib, html, json, os, re, subprocess, sys, time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"giuliano/antikythera/EP03_SCRIPT_SHOTMAP_V1.json"
OUT=ROOT/"output/GIULIANO_03_SOURCE_PREFLIGHT"
API="https://commons.wikimedia.org/w/api.php"
UA="Tra-le-Pagine-Giuliano-Research/1.0 (CC source verification; offline pilot)"

def get_bytes(url, maxbytes=60_000_000, attempts=2):
    for attempt in range(attempts):
        try:
            req=Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
            with urlopen(req,timeout=48) as response:
                declared=int(response.headers.get("Content-Length","0") or "0")
                if declared > maxbytes: raise ValueError("oversized media")
                chunks=[]; n=0
                while True:
                    c=response.read(1024*1024)
                    if not c:break
                    n+=len(c)
                    if n>maxbytes:raise ValueError("media exceeds allowed bytes")
                    chunks.append(c)
                return b"".join(chunks)
        except Exception:
            if attempt+1==attempts:raise
            time.sleep(3)
    raise RuntimeError("request failed")

def api_titles(titles):
    params={"action":"query","prop":"imageinfo","iiprop":"url|mime|size|sha1|extmetadata",
            "iiurlwidth":"1450","format":"json","formatversion":2,
            "titles":"|".join("File:"+v for v in titles)}
    result=json.loads(get_bytes(API+"?"+urlencode(params),maxbytes=3_000_000))
    if "error" in result:raise RuntimeError("MediaWiki API: "+str(result["error"]))
    pages=result.get("query",{}).get("pages",[])
    return {p.get("title","").removeprefix("File:"):p for p in pages}

def license_text(info):
    extra=info.get("extmetadata",{})
    return html.unescape(re.sub("<[^>]+>"," ",str(extra.get("LicenseShortName",{}).get("value","")))).strip()

def safe_license(actual, expected):
    a=actual.lower().replace("-"," ").replace("_"," ")
    e=expected.lower().replace("-"," ").replace("_"," ")
    if "nc" in a.split() or "nd" in a.split(): return False
    if e=="public domain": return "public domain" in a or a.startswith("pd ")
    if e=="cc0":return "cc0" in a
    if "by sa" in e:return "by sa 4.0" in a or ("by 4.0" in a and "sa" not in a)
    if "by 4.0" in e:return "by 4.0" in a and "sa" not in a
    return False

def digest(data):return hashlib.sha256(data).hexdigest()

def cmd(*args):
    p=subprocess.run(list(args),capture_output=True,text=True,timeout=180,check=False)
    if p.returncode:raise RuntimeError("command failed "+str(args[:3])+"\n"+p.stderr[-700:])
    return p.stdout

def plate(path, title, subtitle):
    im=Image.open(path).convert("RGB")
    w,h=720,1280
    background=ImageOps.fit(im,(w,h),method=Image.Resampling.LANCZOS)
    from PIL import ImageFilter, ImageEnhance
    background=ImageEnhance.Brightness(background.filter(ImageFilter.GaussianBlur(30))).enhance(.22)
    fitting=ImageOps.contain(im,(680,1060),method=Image.Resampling.LANCZOS)
    background.paste(fitting,((w-fitting.width)//2,(h-fitting.height)//2-18))
    draw=ImageDraw.Draw(background)
    draw.rectangle((0,1135,720,1280),fill=(14,17,19))
    draw.text((25,1153),title[:65],fill=(230,226,211),font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",22))
    draw.text((25,1191),subtitle[:75],fill=(190,194,199),font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",15))
    draw.text((25,1240),"ANTEPRIMA VISIVA · SENZA VOCE · NON PUBBLICARE",fill=(211,157,101),font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",14))
    background.save(OUT/(path.stem+"_plate.jpg"),quality=88)

def make_contact(results):
    imgs=[r for r in results if r.get("state")=="verified" and r["kind"]=="image"]
    if not imgs:return
    w=480;h=480
    board=Image.new("RGB",(w*2,h*((len(imgs)+1)//2)),(20,21,24))
    d=ImageDraw.Draw(board);f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",16)
    for i,r in enumerate(imgs):
        im=Image.open(OUT/r["local_file"]).convert("RGB")
        im=ImageOps.contain(im,(440,392))
        x=(i%2)*w+(w-im.width)//2;y=(i//2)*h+20+(380-im.height)//2
        board.paste(im,(x,y))
        d.text(((i%2)*w+18,(i//2)*h+410),r["id"]+"  "+r["actual_license"],fill=(224,226,219),font=f)
        d.text(((i%2)*w+18,(i//2)*h+438),r["sha256"][:16],fill=(150,160,164),font=f)
    board.save(OUT/"CONTACT_SHEET_SOURCES.jpg",quality=87)

def video_clip(kind,src,out,seconds):
    vf="scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2:color=0x15181d,format=yuv420p"
    if kind=="image":
        cmd("ffmpeg","-y","-v","error","-loop","1","-framerate","24","-i",str(src),"-t",str(seconds),
            "-vf",vf,"-r","24","-an","-c:v","libx264","-preset","veryfast","-crf","24","-pix_fmt","yuv420p",str(out))
    else:
        cmd("ffmpeg","-y","-v","error","-ss","8","-i",str(src),"-t",str(seconds),
            "-vf",vf,"-r","24","-an","-c:v","libx264","-preset","veryfast","-crf","24","-pix_fmt","yuv420p",str(out))

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    m=json.loads(MANIFEST.read_text("utf-8"))
    assert m["publication_allowed"] is False and m["external_paid_calls_allowed"] is False
    assets=m["assets"]
    pages=api_titles([a["file"] for a in assets if not a.get("direct_url")])
    result=[]
    for a in assets:
        row={"id":a["id"],"file":a["file"],"kind":a["kind"],"source_page":a.get("source_page") or "https://commons.wikimedia.org/wiki/File:"+a["file"].replace(" ","_"),"expected_license":a["expect"]}
        if a.get("direct_url"):
            try:
                rights=get_bytes(a["license_page"],maxbytes=100_000).decode("utf-8")
                if not ("renders, videos" in rights and "Creative Commons Attribution 4.0" in rights):
                    raise ValueError("Independent media license cannot be verified")
                actual="CC BY 4.0"
                info={"url":a["direct_url"],"size":0}
            except Exception as exc:
                row.update({"state":"blocked_unverified_license","error":str(exc)[:160]})
                result.append(row)
                continue
        else:
            page=pages.get(a["file"],{})
            info=(page.get("imageinfo") or [{}])[0]
            actual=license_text(info)
        row["actual_license"]=actual
        if not info.get("url") or not safe_license(actual,a["expect"]):
            row["state"]="blocked_unverified_license";result.append(row);continue
        if a["kind"]=="video" and int(info.get("size",0))>52_000_000:
            row["state"]="blocked_size";result.append(row);continue
        url=(info.get("thumburl") or info.get("url")) if a["kind"]=="image" else info.get("url")
        try:
            data=get_bytes(url,maxbytes=52_000_000)
            ext=".jpg" if a["kind"]=="image" else (".mp4" if a.get("direct_url") else ".ogv")
            name=a["id"]+ext
            path=OUT/name;path.write_bytes(data)
            if a["kind"]=="image":
                with Image.open(path) as im:
                    im.load()
                    if im.width<320 or im.height<320:raise ValueError("resolution too low")
                plate(path,a["subject"],"Fonte autentica • "+actual)
            else:
                probe=json.loads(cmd("ffprobe","-v","error","-show_entries","stream=codec_type:format=duration",
                    "-of","json",str(path)))
                if float(probe.get("format",{}).get("duration",0))<12:raise ValueError("short film")
            row.update({"state":"verified","sha256":digest(data),"bytes":len(data),"local_file":name,"origin_url":info["url"]})
        except Exception as exc:
            row["state"]="download_failed";row["error"]=str(exc)[:250]
        result.append(row)
    make_contact(result)
    images=[r for r in result if r["state"]=="verified" and r["kind"]=="image"]
    videos=[r for r in result if r["state"]=="verified" and r["kind"]=="video"]
    report={"schema":"giuliano-03-licensed-source-preflight-v1","status":"source_research_only","source_count":len(assets),
        "images_verified":len(images),"scientific_videos_verified":len(videos),"assets":result,
        "cost_eur":0,"audio_generated":False,"finished_documentary":False,
        "notes":["All verified material is independently attributed; this is a silent proof, not a finished GIULIANO episode.",
                 "The 2021 clips are research reconstructions, not footage of the original ancient mechanism."]}
    if len(images)>=2 and len(videos)>=2:
        shots=[(images[0],4),(videos[0],6),(images[1],4),(videos[1],6)]
        files=[]
        for i,(r,sec) in enumerate(shots):
            source=OUT/r["local_file"]
            if r["kind"]=="image":source=OUT/(source.stem+"_plate.jpg")
            output=OUT/("shot_"+str(i).zfill(2)+".mp4")
            video_clip(r["kind"],source,output,sec);files.append(output)
        concat=OUT/"concat.txt"
        concat.write_text("".join("file '"+p.name+"'\n" for p in files),encoding="utf-8")
        preview=OUT/"GIULIANO_03_SILENT_MATERIALS_TEST_20s.mp4"
        cmd("ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",str(concat),"-c","copy","-movflags","+faststart",str(preview))
        cmd("ffmpeg","-v","error","-xerror","-i",str(preview),"-f","null","-")
        report["silent_materials_preview_mp4"]=preview.name
        report["preview_verified_full_decode"]=True
    else:
        report["blocker"]="insufficient_verified_public_media_for_preview"
    (OUT/"SOURCE_QA_REPORT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    text="\n".join(r["id"]+": "+r["state"]+" ("+r.get("actual_license","?")+") - "+r["source_page"] for r in result)
    (OUT/"ATTRIBUTION_AND_SOURCE_STATUS.txt").write_text(text+"\n",encoding="utf-8")
    print("PREFLIGHT:",len(images),"images",len(videos),"scientific clips; preview:",report.get("silent_materials_preview_mp4","blocked"))
    for r in result: print("SOURCE",r["id"],r["state"],r.get("actual_license",""),r.get("error","")[:120])
    if len(images)<2 or len(videos)<2:sys.exit(2)

if __name__=="__main__":
    main()
