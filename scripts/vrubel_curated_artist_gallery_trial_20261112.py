#!/usr/bin/env python3
"""Isolated, no-AI, source-locked Vrubel artist gallery reel; personal review only."""
import hashlib, io, json, os, subprocess, sys, time, urllib.parse, urllib.request, zipfile
from pathlib import Path
from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageFont

OUT=Path("output/vrubel-curated-gallery-20261112")
OUT.mkdir(parents=True,exist_ok=True)
# Exact Wikimedia Commons file titles: author Mikhail Vrubel (1856-1910).
# The user-requested format is a SHORT artist gallery, not a 4x1 ArtVision master.
ART=[
 ("Artist portrait",1900,"Vrubel 1900.jpg",2.5,"portrait",.52),
 ("The Swan Princess",1900,"Tsarevna-Lebed by Mikhail Vrubel.jpg",2.9,"portrait",.48),
 ("Pan",1899,"1899 Vrubel Pan anagoria.JPG",2.85,"portrait",.47),
 ("Lilacs",1901,"'Lilacs' by Mikhail Vrubel, unfinished, 1901, Tretyakov Gallery.jpg",2.4,"crop",.52),
 ("The Demon Seated",1890,"Vrubel Demon.jpg",3.5,"crop",.48),
 ("Bogatyr",1898,"Vrubel Bogatyr.jpg",2.9,"portrait",.50),
 ("A Lady in Lilac",1900,"Врубель - Дама в лиловом (1900).jpg",2.7,"portrait",.50),
 ("Six-winged Seraph",1904,"Vrubel Azrail.jpg",3.3,"crop",.47),
 ("The Demon Downcast",1902,"Vrubel Fallen Demon.jpg",3.25,"crop",.39),
]
MUSIC_TITLE="Aftermath"
MUSIC_AUTHOR="Kevin MacLeod"
MUSIC_PAGE="https://commons.wikimedia.org/wiki/File:Aftermath_(ISRC_USUAN1100575).mp3"
MUSIC_LICENSE="https://creativecommons.org/licenses/by/3.0/"
MUSIC_URL="https://incompetech.com/music/royalty-free/mp3-royaltyfree/Aftermath.mp3"
W,H,FPS=720,1280,25
UA={"User-Agent":"ArtVision-Owner-Editorial-Proof/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-)","Accept":"image/avif,image/webp,image/png,image/jpeg,image/*,*/*;q=0.7"}

def sha(path,algo="sha256"):
    h=hashlib.new(algo)
    with open(path,"rb") as f:
        for part in iter(lambda:f.read(1<<20),b""):h.update(part)
    return h.hexdigest()

def get(url,destination,minimum=20000):
    request=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(request,timeout=35) as response:
        data=response.read(20_000_001)
    if len(data)<minimum or len(data)>20_000_000:raise ValueError("unexpected byte length "+str(len(data)))
    destination.write_bytes(data)
    return len(data)

def commons_urls(filename):
    key=filename.replace(" ","_")
    md5=hashlib.md5(key.encode("utf8")).hexdigest()
    encoded=urllib.parse.quote(key,safe="._-")
    return [
      "https://upload.wikimedia.org/wikipedia/commons/"+md5[0]+"/"+md5[:2]+"/"+encoded,
      "https://commons.wikimedia.org/wiki/Special:Redirect/file/"+encoded,
    ]

def download_art(label,year,filename):
    destination=OUT/("source_"+str(year)+"_"+hashlib.md5(filename.encode()).hexdigest()[:9]+".jpg")
    errors=[]
    for url in commons_urls(filename):
        for attempt in range(2):
            try:
                get(url,destination)
                with Image.open(destination) as im:
                    im.load()
                    if im.format not in ("JPEG","PNG") or min(im.size)<(540 if label=="Artist portrait" else 740):
                        raise ValueError("image too small/invalid")
                    dims=im.size
                return dict(title=label,year=year,commons_file=filename,
                            page="https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(filename.replace(" ","_")),
                            retrieved_url=url,sha256=sha(destination),size=destination.stat().st_size,
                            dimensions=list(dims),file=str(destination))
            except Exception as e:
                errors.append(type(e).__name__+" "+str(e)[:160])
                time.sleep(.65*(attempt+1))
    print("SOURCE_UNAVAILABLE",label," | ".join(errors[-3:]),flush=True)
    return None

def font(size,serif=False):
    candidates=["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf" if serif else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for p in candidates:
        if Path(p).exists():return ImageFont.truetype(p,size)
    return ImageFont.load_default()

def shot_image(image_path,mode,focus,opening=False):
    src=Image.open(image_path).convert("RGB")
    # Crop only actual painting pixels; no invented background/content.
    if mode in ("portrait","crop"):
        canvas=ImageOps.fit(src,(W,H),method=Image.Resampling.LANCZOS,
            centering=(focus,.50))
    else:
        # On very wide paintings preserve the WHOLE canvas; do not slice away the artwork.
        bg=ImageOps.fit(src,(W,H),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(62))
        bg=bg.point(lambda x:int(x*.23))
        canvas=bg.copy()
        art=ImageOps.contain(src,(W-30,H-200),Image.Resampling.LANCZOS)
        canvas.paste(art,((W-art.width)//2,(H-art.height)//2))
    if opening:
        d=ImageDraw.Draw(canvas)
        # Single restrained artist label at the top: no marketing UI or artificial frame.
        d.rectangle((0,0,W,125),fill=(12,16,21))
        d.text((W//2,39),"MIKHAIL VRUBEL",anchor="mt",font=font(35,True),
               fill=(239,229,214),stroke_width=0)
        d.text((W//2,95),"1856 — 1910",anchor="mm",font=font(16),
               fill=(190,181,170))
    return canvas

def run(cmd, timeout=420):
    result=subprocess.run([str(x) for x in cmd],capture_output=True,text=True,timeout=timeout)
    if result.returncode:
        raise RuntimeError("COMMAND_FAILED "+str(cmd[:5])+" "+result.stderr[-1700:])
    return result

def main():
    selected=[]
    for label,year,filename,duration,mode,focus in ART:
        info=download_art(label,year,filename)
        if info:
            info.update(duration=duration,mode=mode,focus=focus,role=("artist_portrait" if label=="Artist portrait" else "painting"))
            selected.append(info)
    if len(selected)<7:
        raise RuntimeError("BLOCKED_SOURCE: fewer than 7 verified real sources. No fake reel rendered.")
    print("VERIFIED_DISTINCT_ARTWORKS",len(selected),flush=True)

    audio=OUT/"AFTERMATH_CC_BY_3.mp3"
    get(MUSIC_URL,audio,minimum=100000)
    run(["ffprobe","-v","error","-show_entries","stream=codec_type","-of","csv=p=0",audio],40)
    print("LICENSED_MUSIC_DOWNLOADED",audio.stat().st_size,flush=True)

    images=[]
    for i,info in enumerate(selected):
        frame=shot_image(info["file"],info["mode"],info["focus"],opening=i==0)
        still=OUT/("shot_%02d.jpg"%(i+1))
        frame.save(still,quality=91,optimize=True)
        images.append(still)
    total=sum(x["duration"] for x in selected)
    # Concatenated stills with modest transitions: a gallery, not a fake animation.
    cut=OUT/"shots.ffconcat"
    rows=["ffconcat version 1.0"]
    for im,item in zip(images,selected):
        rows+=["file '"+im.resolve().as_posix().replace("'","'\\''")+"'",
               "duration "+str(item["duration"])]
    rows+=["file '"+images[-1].resolve().as_posix()+"'"]
    cut.write_text("\n".join(rows)+"\n",encoding="utf8")
    master=OUT/"VRUBEL_REAL_ARTIST_GALLERY_REVIEW_V2.mp4"
    # Image slides on real paintings, 25fps, without artificial AI motion.
    # AA at low image dimensions is achieved by the Lanczos still render above.
    run(["ffmpeg","-y","-hide_banner","-loglevel","error",
         "-safe","0","-f","concat","-i",cut,
         "-ss","11","-i",audio,
         "-filter_complex",f"[0:v]fps={FPS},scale={W}:{H},format=yuv420p[v];[1:a]volume=0.65,afade=t=in:st=0:d=0.6,afade=t=out:st={max(0,total-1.3):.2f}:d=1.2[a]",
         "-map","[v]","-map","[a]","-t",f"{total:.2f}",
         "-c:v","libx264","-preset","veryfast","-crf","19",
         "-c:a","aac","-b:a","160k","-movflags","+faststart",master],timeout=360)

    ffprobe=run(["ffprobe","-v","error","-show_format","-show_streams","-of","json",master],60)
    probe=json.loads(ffprobe.stdout)
    streams=probe["streams"]
    v=next(x for x in streams if x.get("codec_type")=="video")
    a=next(x for x in streams if x.get("codec_type")=="audio")
    duration=float(probe["format"]["duration"])
    if v["codec_name"]!="h264" or a["codec_name"]!="aac" or v["width"]!=W or v["height"]!=H:
        raise RuntimeError("QA_FAIL_BAD_STREAMS")
    if abs(duration-total)>.3:raise RuntimeError("QA_FAIL_DURATION "+str(duration)+" versus "+str(total))
    run(["ffmpeg","-v","error","-xerror","-i",master,"-f","null","-"],timeout=420)
    # Last frame is not blank.
    last=OUT/"last_frame.jpg"
    run(["ffmpeg","-v","error","-y","-ss",f"{max(0,duration-.3):.2f}","-i",master,"-frames:v","1",last],40)
    with Image.open(last) as im:
        s=im.convert("L").resize((64,64))
        if sum(1 for x in s.getdata() if x<8)>3400:raise RuntimeError("QA_FAIL_BLACK_ENDING")

    cover=OUT/"COVER_V2.jpg"
    Image.open(images[0]).save(cover,quality=92)
    # Meaningfully inspect one true rendered frame per scene, not title placeholders.
    thumbs=[]
    position=0
    for i,info in enumerate(selected):
        thumb=OUT/("QA_FRAME_%02d.jpg"%(i+1))
        run(["ffmpeg","-v","error","-y","-ss",f"{position+info['duration']*.45:.2f}","-i",master,
             "-frames:v","1","-vf","scale=270:480",thumb],40)
        thumbs.append(thumb)
        info["start_s"]=round(position,2)
        position+=info["duration"]
    sheet=Image.new("RGB",(4*270,((len(thumbs)+3)//4)*520),(13,15,20))
    draw=ImageDraw.Draw(sheet)
    for i,p in enumerate(thumbs):
        x=(i%4)*270;y=(i//4)*520
        sheet.paste(Image.open(p),(x,y))
        draw.text((x+10,y+485),selected[i]["title"][:27],font=font(17),fill=(236,231,218))
    sheet.save(OUT/"CONTACT_SHEET_V2.jpg",quality=87)
    social=(
      "MIKHAIL VRUBEL | A WORLD BETWEEN DREAMS\n\n"
      "A portrait of the artist and eight paintings. No invented scenes, no artificial character animation. "
      "A visual journey from The Swan Princess to The Demon Downcast.\n\n"
      "#MikhailVrubel #Symbolism #ArtHistory #Paintings\n\n"
      "Music: Aftermath — Kevin MacLeod (incompetech.com), CC BY 3.0 "
      +MUSIC_LICENSE+"\n"
      "Edits: shortened to excerpt, volume adjusted, fade in/out.\n"
      "Artwork images: Wikimedia Commons, each page in SOURCE_MANIFEST.json; "
      "source and commercial reuse to be independently confirmed before publishing.\n"
    )
    (OUT/"SOCIAL_CAPTION.txt").write_text(social,encoding="utf8")
    manifest={
      "title":"Mikhail Vrubel | A World Between Dreams",
      "status":"TECHNICAL_PASS_ARTISTIC_PENDING",
      "format":"isolated_artist_gallery_trial_not_4x1",
      "branch":"feature/artvision-curated-agent-skills-20261112",
      "artwork_count":sum(x.get("role")=="painting" for x in selected),"portrait_count":sum(x.get("role")=="artist_portrait" for x in selected),"works":selected,
      "audio":{"title":MUSIC_TITLE,"author":MUSIC_AUTHOR,"page":MUSIC_PAGE,
               "license":MUSIC_LICENSE,"source":MUSIC_URL,"sha256":sha(audio)},
      "video":{"path":str(master),"sha256":sha(master),
               "bytes":master.stat().st_size,"seconds":duration,
               "dimensions":[W,H],"video_codec":v["codec_name"],
               "audio_codec":a["codec_name"],"complete_decode":"PASS"},
      "artistically_approved":False,"museum_approved":False,
      "publication_authorized":False,"paid_video_calls":0,
    }
    (OUT/"SOURCE_MANIFEST.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    with zipfile.ZipFile(OUT/"VRUBEL_REVIEW_PACKAGE_V2.zip","w",zipfile.ZIP_DEFLATED,compresslevel=4) as z:
        for filename in [master,cover,OUT/"CONTACT_SHEET_V2.jpg",OUT/"SOURCE_MANIFEST.json",OUT/"SOCIAL_CAPTION.txt"]:
            z.write(filename,arcname=filename.name)
    with zipfile.ZipFile(OUT/"VRUBEL_REVIEW_PACKAGE_V2.zip") as z:
        if z.testzip():raise RuntimeError("QA_FAIL_ZIP_CRC")
    print("VIDEO_DELIVERED",json.dumps(manifest["video"]),flush=True)
    print("CREATIVE_STATUS TECHNICAL_PASS_ARTISTIC_PENDING",flush=True)

if __name__=="__main__":
    main()
