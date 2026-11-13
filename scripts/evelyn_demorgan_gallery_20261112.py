#!/usr/bin/env python3
"""Evelyn De Morgan: authentic-art 50-second mobile gallery, isolated owner review.
No image generation, paid services, autopublication or change to production owner.
"""
from __future__ import annotations
import hashlib, json, subprocess, urllib.parse, urllib.request, time, zipfile
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFilter, ImageFont
OUT=Path("output/evelyn-demorgan-gallery-20261112"); OUT.mkdir(parents=True,exist_ok=True)
W,H,FPS=720,1280,25
# Commons exact titles, checked against Wikimedia Commons category. The public-domain
# painting and the photograph's own license are distinct: final commercial reuse TBD.
ART=[
 ("The Storm Spirits",1900,"The Storm Spirits, by Evelyn De Morgan.jpg",4.7,(.70,.40)),
 ("The Love Potion",1903,"The Love PotionFXD.jpg",4.6,(.44,.41)),
 ("Boreas and Oreithyia",1896,"Evelyn de Morgan - Boreas and Oreithyia, 1896.jpg",4.4,(.49,.39)),
 ("The Sea Maidens",1886,"Evelyn de Morgan - The Sea Maidens, 1885-1886.jpg",4.8,(.54,.47)),
 ("The Gilded Cage",1919,"The Gilded Cage, by Evelyn De Morgan.jpg",4.6,(.49,.52)),
 ("Night and Dawn",1910,"Evelyn de Morgan - Night and Dawn.jpg",4.3,(.51,.38)),
 ("Clytie",1887,"Clytie, by Evelyn Pickering de Morgan.jpg",4.3,(.52,.43)),
 ("The Barred Gate",1910,"Evelyn De Morgan - The Barred Gate.jpg",4.1,(.52,.44)),
 ("The Angel with the Serpent",1875,"Evelyn de Morgan - The Angel with the Serpent, 1870-1875.jpg",4.5,(.53,.46)),
 ("The Little Sea Maid",1888,"Evelyn de Morgan - The Little Sea Maid, 1880-1888.jpg",4.5,(.50,.38)),
 ("The Cadence of Autumn",1905,"Evelyn de Morgan - The Cadence of Autumn.jpg",4.2,(.55,.50)),
]
# Cue structure bespoke: most complete works stay on screen 3-4 sec,
# occasional details are short but readable, never >1 photograph per second.
BEATS=["full","detail_then_full","full","full_then_detail","full",
       "full","detail_then_full","full","full_then_detail","full","full"]
MUSIC_URL="https://incompetech.com/music/royalty-free/mp3-royaltyfree/The%20Parting.mp3"
MUSIC_PAGE="https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100638"
USER_AGENT="ArtVisionArtistGallery/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-)"
def shasum(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
    return h.hexdigest()
def run(args,timeout=300):
    p=subprocess.run([str(x) for x in args],text=True,capture_output=True,timeout=timeout)
    if p.returncode: raise RuntimeError("Command failed: "+" ".join(map(str,args[:5]))+"\n"+p.stderr[-1300:])
    return p.stdout
def download(url,local,limit=18000000,minimum=25000):
    req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT})
    with urllib.request.urlopen(req,timeout=38) as f:
        data=f.read(limit+1)
    if not minimum<=len(data)<=limit: raise ValueError(f"invalid bytes {len(data)}")
    local.write_bytes(data)
    return len(data)
def commons_urls(filename):
    key=filename.replace(" ","_")
    md5=hashlib.md5(key.encode("utf8")).hexdigest()
    escaped=urllib.parse.quote(key,safe="._-")
    return [
        "https://upload.wikimedia.org/wikipedia/commons/"+md5[0]+"/"+md5[:2]+"/"+escaped,
        "https://commons.wikimedia.org/wiki/Special:Redirect/file/"+escaped,
    ]
def source(entry):
    title,year,file,duration,focus=entry
    p=OUT/("ART_"+hashlib.sha1(file.encode()).hexdigest()[:11]+".jpg")
    failures=[]
    for url in commons_urls(file):
        for attempt in range(2):
            try:
                download(url,p)
                with Image.open(p) as img:
                    img.load()
                    if img.format not in ("JPEG","PNG") or min(img.size)<450:
                        raise ValueError("image too small or invalid")
                    pixels=img.size
                return {"title":title,"year":year,"commons_filename":file,
                    "page":"https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(file.replace(" ","_")),
                    "uri":url,"bytes":p.stat().st_size,"sha256":shasum(p),
                    "pixels":list(pixels),"local":str(p),"planned_seconds":duration,"focus":focus}
            except Exception as e:
                failures.append(type(e).__name__+": "+str(e)[:90])
                time.sleep(.35)
    print("SOURCE_UNAVAILABLE",title,failures[-1] if failures else "",flush=True)
    return None
def font(px,serif=False):
    a="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf" if serif else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    try:return ImageFont.truetype(a,px)
    except OSError:return ImageFont.load_default()
def full_canvas(source_image):
    img=Image.open(source_image).convert("RGB")
    # True complete work in the 9:16 frame; background comes from original work.
    bg=ImageOps.fit(img,(W,H),Image.Resampling.LANCZOS)
    bg=bg.filter(ImageFilter.GaussianBlur(54)).point(lambda px:int(px*.31))
    art=ImageOps.contain(img,(W-30,H-215),Image.Resampling.LANCZOS)
    x=(W-art.width)//2;y=(H-art.height)//2-12
    bg.paste(art,(x,y))
    d=ImageDraw.Draw(bg)
    d.rectangle((x-2,y-2,x+art.width+1,y+art.height+1),outline=(197,173,141),width=2)
    return bg
def detail_canvas(source_image,focus):
    img=Image.open(source_image).convert("RGB")
    # Crop from ORIGINAL only; no synthesized scenery, no hallucinated figures.
    return ImageOps.fit(img,(W,H),Image.Resampling.LANCZOS,centering=focus)
def render_frame(base,label=None,year=None,opening=False):
    out=base.copy()
    d=ImageDraw.Draw(out)
    if opening:
        d.rounded_rectangle((30,65,W-30,210),radius=14,fill=(15,19,26))
        d.text((W//2,87),"EVELYN DE MORGAN",anchor="mt",
               font=font(35,True),fill=(239,224,206))
        d.text((W//2,169),"1855 — 1919",anchor="mt",
               font=font(21),fill=(204,185,164))
    elif label:
        d.rounded_rectangle((34,H-146,W-34,H-62),radius=8,fill=(17,19,22))
        d.text((W//2,H-126),label[:43],anchor="mt",
               font=font(22,True),fill=(238,232,216))
        if year:d.text((W//2,H-92),str(year),anchor="mt",
                       font=font(15),fill=(191,181,165))
    return out
def main():
    got=[]
    for e in ART:
        item=source(e)
        if item:got.append(item)
    if len(got)<8:raise RuntimeError(f"BLOCKED_SOURCE: {len(got)} exact authentic paintings < 8, no render")
    print("SOURCE_LOCKED_PAINTINGS",len(got),flush=True)
    audio=OUT/"THE_PARTING_CC_BY4.mp3"
    download(MUSIC_URL,audio,limit=24000000,minimum=150000)
    run(["ffprobe","-v","error","-show_entries","stream=codec_type","-of","default=nw=1",audio],timeout=25)
    print("MUSIC_LOCKED",audio.stat().st_size,flush=True)
    # start with an attention-holding artwork, finish with a calm painting.
    files=[];timestamps=[];t=0.
    for index,p in enumerate(got):
        fmt=next((BEATS[i] for i,base in enumerate(ART) if base[0]==p["title"]),"full")
        candidates=[]
        if fmt=="detail_then_full":
            candidates=[("detail",min(1.7,p["planned_seconds"]*.36)),
                        ("full",p["planned_seconds"]-min(1.7,p["planned_seconds"]*.36))]
        elif fmt=="full_then_detail":
            candidates=[("full",p["planned_seconds"]-1.65),("detail",1.65)]
        else:candidates=[("full",p["planned_seconds"])]
        if index==0:
            candidates=[("full",2.2),("full",p["planned_seconds"]-2.2)]
        for k,(kind,length) in enumerate(candidates):
            if kind=="full":frame=full_canvas(p["local"])
            else:frame=detail_canvas(p["local"],p["focus"])
            frame=render_frame(frame,
                label=p["title"] if kind=="full" and not(index==0 and k==0) else None,
                year=p["year"],opening=index==0 and k==0)
            output=OUT/f"SHOT_{len(files)+1:02d}.jpg"
            frame.save(output,quality=91,optimize=True)
            files.append((output,length))
            timestamps.append({"painting":p["title"],"shot":kind,"start_s":round(t,2),
                               "seconds":round(length,2),"source_sha256":p["sha256"]})
            t+=length
    total=round(t,2)
    assert total>=35 and total<=70, total
    script=OUT/"sequence.ffconcat"
    records=["ffconcat version 1.0"]
    for filename,length in files:
        records.extend(["file '"+str(filename.resolve()).replace("'","'\\''")+"'",
                        "duration "+str(length)])
    records.append("file '"+str(files[-1][0].resolve())+"'")
    script.write_text("\n".join(records)+"\n",encoding="utf8")
    mp4=OUT/"EVELYN_DE_MORGAN_GALLERY_REVIEW.mp4"
    run(["ffmpeg","-y","-hide_banner","-loglevel","error",
         "-safe","0","-f","concat","-i",script,
         "-ss","30","-i",audio,
         "-filter_complex",f"[0:v]fps={FPS},scale={W}:{H},format=yuv420p[v];"
         f"[1:a]afade=t=in:st=0:d=0.8,"
         f"afade=t=out:st={max(1,total-2.2):.2f}:d=2,"
         f"loudnorm=I=-17:TP=-2:LRA=8[a]",
         "-map","[v]","-map","[a]","-t",str(total),
         "-c:v","libx264","-preset","veryfast","-crf","19",
         "-c:a","aac","-b:a","160k","-movflags","+faststart",mp4],timeout=370)
    p=json.loads(run(["ffprobe","-v","error","-show_streams","-show_format","-of","json",mp4]).strip())
    v=next(s for s in p["streams"] if s["codec_type"]=="video")
    a=next(s for s in p["streams"] if s["codec_type"]=="audio")
    length=float(p["format"]["duration"])
    if v["codec_name"]!="h264" or a["codec_name"]!="aac" or (v["width"],v["height"])!=(W,H):
        raise RuntimeError("QA_STREAM_FAILURE")
    if abs(length-total)>.40:raise RuntimeError("QA_DURATION_FAILURE")
    run(["ffmpeg","-hide_banner","-v","error","-xerror","-i",mp4,"-f","null","-"],timeout=360)
    last=OUT/"LAST_FRAME.jpg"
    run(["ffmpeg","-v","error","-y","-ss",str(length-.25),"-i",mp4,"-frames:v","1",last],timeout=40)
    with Image.open(last) as im:
        L=im.convert("L").resize((64,64))
        if sum(x<8 for x in L.getdata())>3500:raise RuntimeError("QA_BLACK_TAIL")
    # Quality proof real MP4 snapshots (not previews generated from source stills).
    shots=[];time_cursor=0
    for index,pnt in enumerate(got):
        second=next(s for s in timestamps if s["painting"]==pnt["title"] and s["shot"]=="full")["start_s"]+1.1
        jpg=OUT/f"PROOF_{index+1:02d}.jpg"
        run(["ffmpeg","-y","-v","error","-ss",str(second),"-i",mp4,
             "-frames:v","1","-vf","scale=230:409",jpg],timeout=35)
        shots.append((jpg,pnt))
    cols=4;rows=(len(shots)+cols-1)//cols
    sheet=Image.new("RGB",(cols*238,rows*450),(15,17,21))
    d=ImageDraw.Draw(sheet)
    for i,(jpg,pnt) in enumerate(shots):
        x=(i%cols)*238;y=(i//cols)*450
        with Image.open(jpg) as im:sheet.paste(im,(x,y))
        d.text((x+8,y+415),pnt["title"][:24],font=font(14),fill=(235,228,215))
    sheet.save(OUT/"CONTACT_SHEET.jpg",quality=90)
    Image.open(files[0][0]).save(OUT/"COVER.jpg",quality=93)
    caption=f"""EVELYN DE MORGAN · WORLDS OF LIGHT AND SHADOW

In {len(got)} paintings, Evelyn De Morgan transforms myth, nature and the human figure into images of astonishing intensity.

Artwork and image source links are documented in SOURCE_MANIFEST.json. Original canvases preserved, including full compositions.
Music: The Parting — Kevin MacLeod (incompetech.com).
Licensed under Creative Commons Attribution 4.0: https://creativecommons.org/licenses/by/4.0/
Music edited for length, start time, loudness and fades.

#EvelynDeMorgan #Symbolism #PreRaphaelite #ArtHistory
"""
    (OUT/"SOCIAL_CAPTION.txt").write_text(caption,encoding="utf8")
    manifest={"artist":"Evelyn De Morgan","format":"review-only artist gallery, NOT ArtVision 4x1",
        "source_images":got,"storyboard":timestamps,
        "music":{"name":"The Parting","author":"Kevin MacLeod","license":"CC BY 4.0",
            "source":MUSIC_PAGE,"sha256":shasum(audio),"audio_start_seconds":30},
        "video":{"file":str(mp4),"bytes":mp4.stat().st_size,"sha256":shasum(mp4),
            "duration_seconds":length,"width":W,"height":H,
            "codec_video":"h264","codec_audio":"aac","complete_decode":"PASS"},
        "status":"TECHNICAL_PASS_ARTISTIC_PENDING","rights":"individual image-page license checks before publication",
        "published":False,"gold_approved":False,"paid_calls":0}
    (OUT/"SOURCE_MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    package=OUT/"EVELYN_DE_MORGAN_COMPLETE.zip"
    with zipfile.ZipFile(package,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
        for item in [mp4,OUT/"COVER.jpg",OUT/"CONTACT_SHEET.jpg",
                     OUT/"SOCIAL_CAPTION.txt",OUT/"SOURCE_MANIFEST.json"]:
            z.write(item,arcname=item.name)
    with zipfile.ZipFile(package) as z:
        if z.testzip():raise RuntimeError("QA_CRC_FAILURE")
    print("FINAL_VIDEO_VERIFIED",json.dumps(manifest["video"]),flush=True)
    print("ARTWORKS",len(got),"SHOTS",len(files),"TOTAL_SECONDS",total,flush=True)
    print("FINAL_REVIEW_ARTIFACT",str(package),flush=True)
if __name__=="__main__":main()
