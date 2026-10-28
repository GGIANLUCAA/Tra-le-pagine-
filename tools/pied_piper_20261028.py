#!/usr/bin/env python3
"""Pifferaio Hamelin: original Greenaway images, truthful free preview; never paid video/TTS."""
from __future__ import annotations
import hashlib, json, math, re, shutil, subprocess, tempfile, zipfile
from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

EP=Path("episodes/pifferaio_hamelin_20261028")
OUT=Path("output/pifferaio_hamelin_20261028")
SOURCE="https://www.gutenberg.org/cache/epub/18343/pg18343-images.html"
NAVY=(19,39,52); GOLD=(181,143,91); PAPER=(241,232,210)
def sha(data): return hashlib.sha256(data).hexdigest()
def font(size,bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/"+("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),size)
def run(*args):
    subprocess.run([str(a) for a in args],check=True,stdout=subprocess.DEVNULL if args[0]=="ffmpeg" else None)
def write_json(path,obj):
    Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def frame(im):
    im=ImageOps.exif_transpose(im.convert("RGB"))
    back=ImageOps.fit(im,(720,1280),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(36))
    back=Image.blend(back,Image.new("RGB",(720,1280),NAVY),.78)
    d=ImageDraw.Draw(back)
    d.rounded_rectangle((23,59,697,1220),radius=14,fill=PAPER,outline=GOLD,width=4)
    art=ImageOps.contain(im,(638,1104),Image.Resampling.LANCZOS)
    back.paste(art,((720-art.width)//2,(1280-art.height)//2))
    return back
def read_plan():
    p=json.loads((EP/"scene_plan_pifferaio.json").read_text(encoding="utf-8"))["scenes"]
    paragraphs=[s.strip() for s in (EP/"testo.txt").read_text(encoding="utf-8").split("\n\n") if s.strip()]
    if len(p)!=16 or len(paragraphs)!=16 or any(x["narration"]!=y for x,y in zip(p,paragraphs)):
        raise RuntimeError("16 distinct narrative beats and exact script anchors required")
    return p,paragraphs
def extract_candidates(session):
    r=session.get(SOURCE,timeout=45);r.raise_for_status()
    soup=BeautifulSoup(r.content,"html.parser")
    found=[];seen=set()
    for tag in soup.find_all("img"):
        src=tag.get("src","")
        if not re.search(r"\.(?:png|jpe?g|gif)$",src,re.I):continue
        url=urljoin(SOURCE,src)
        if not url.startswith("https://www.gutenberg.org/") or url in seen:continue
        seen.add(url)
        marker=tag.find_previous(class_=re.compile("pagenum",re.I))
        raw=marker.get_text(" ",strip=True) if marker else ""
        match=re.search(r"(?:Pg|Page)?\s*(\d{1,3})",raw,re.I)
        page=int(match.group(1)) if match else None
        found.append({"url":url,"alt":tag.get("alt",""),"page":page,"src":src})
    if len(found)<16:raise RuntimeError("Insufficient authentic images in Gutenberg edition: "+str(len(found)))
    return found
def acquire():
    plan,paragraphs=read_plan()
    OUT.mkdir(parents=True,exist_ok=True);(EP/"images").mkdir(parents=True,exist_ok=True)
    session=requests.Session()
    session.headers.update({"User-Agent":"TraLePagine-Editorial/1.0 (single public-domain book; no scraping batches)"})
    candidates=extract_candidates(session)
    cache={};used=set();records=[];cues=[];offset=0
    split=re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-ÙÈÉ«“])")
    for i,(scene,paragraph) in enumerate(zip(plan,paragraphs),1):
        target=scene["target_page"]
        ranked=sorted(enumerate(candidates),key=lambda v:(
            abs((v[1]["page"] if v[1]["page"] is not None else (v[0]*48/max(1,len(candidates)-1)+1))-target),
            -len(v[1]["alt"]),v[0]))
        chosen=None
        for idx,c in ranked:
            if c["url"] in used:continue
            try:
                if c["url"] not in cache:
                    res=session.get(c["url"],timeout=45);res.raise_for_status()
                    if not 12000<len(res.content)<12000000:continue
                    with Image.open(BytesIO(res.content)) as orig:
                        orig.load()
                        if orig.width<220 or orig.height<220 or orig.width*orig.height<85000:continue
                        cache[c["url"]]=(res.content,orig.convert("RGB"),[orig.width,orig.height])
                chosen=c;break
            except requests.HTTPError as exc:
                if exc.response is not None and exc.response.status_code in (429,403):
                    raise RuntimeError("Source rate limited; stop, do not retry") from None
                continue
            except (OSError,ValueError,requests.RequestException):
                continue
        if chosen is None:raise RuntimeError("Not enough decodable original illustrations for scene "+str(i))
        used.add(chosen["url"])
        raw,im,size=cache[chosen["url"]]
        dest=EP/"images"/("scena_%02d.jpg"%i)
        frame(im).save(dest,"JPEG",quality=93,optimize=True)
        if dest.stat().st_size<35000:raise RuntimeError("Too-small frame "+str(dest))
        cues.append({"asset":i,"start_sentence":offset,"description":scene["visual_intent"],
                     "narration_anchor":split.split(paragraph)[0]})
        offset+=len([s for s in split.split(paragraph) if s.strip()])
        records.append({"scene":i,"asset_id":"img_%02d"%i,"file":str(dest),
          "output_sha256":sha(dest.read_bytes()),"source_url":chosen["url"],"source_page":SOURCE,
          "source_sha256":sha(raw),"source_dimensions":size,"source_alt":chosen["alt"],
          "edition_page_candidate":chosen["page"],"requested_page":target,
          "scene_match_note":scene["scene_match_note"],
          "rights_basis":"Robert Browning (died 1889), Kate Greenaway (died 1901); original public-domain artwork, verify exact reproduction",
          "rights_review":"source_artist_and_date_checked","scene_relevance":"PENDING_VISUAL_MATCH",
          "visual_review":"PENDING_HUMAN_REVIEW"})
        print("SOURCE_DOWNLOADED",i,chosen["src"],"page",chosen["page"],"size",size,flush=True)
    write_json(EP/"scene_cues.json",cues)
    write_json(OUT/"PROVENIENZA_IMMAGINI.json",{"source":SOURCE,"unique_images":len(used),
        "scenes":records,"editorial_approval":"pending human visual and story review"})
    from sys import path
    path.insert(0,"src")
    from episode_v3 import validate,branded_cover
    validate(EP.name)
    branded_cover(OUT,EP,json.loads((EP/"metadata.json").read_text(encoding="utf-8")))
    board(records,plan)
    for name in ("testo.txt","metadata.json","PROJECT_V13.json","SCHEDE_VISUALI_V35.json",
        "FONTI_E_DIRITTI.md","DESCRIZIONE_SOCIAL.txt","POST_FACEBOOK.txt",
        "POST_INSTAGRAM.txt","POST_TIKTOK.txt","POST_YOUTUBE.txt","scene_plan_pifferaio.json","scene_cues.json"):
        shutil.copy2(EP/name,OUT/name)
    write_json(OUT/"QUALITY.json",{"episode":EP.name,"state":"VISUALS_ACQUIRED_ART_REVIEW_PENDING",
        "source_images":len(used),"preview_only":True,"voice_generated":False,
        "complete_narrated_mp4":False,"gacrux_free_quota_attested":False,
        "paid_video_calls":0,"archive_imported":False,"social_published":False})
    make_preview(records)
    package(records)
    print("VISUAL_PREVIEW_COMPLETE_NOT_NARRATED",flush=True)
def board(records,plan):
    w,h=310,420;cols=4;rows=math.ceil(len(records)/cols)
    im=Image.new("RGB",(w*cols,rows*h+120),PAPER);d=ImageDraw.Draw(im)
    d.rectangle((0,0,im.width,105),fill=NAVY)
    d.text((30,30),"IL PIFFERAIO DI HAMELIN | 16 SCENE",font=font(29,True),fill=PAPER)
    for k,(r,s) in enumerate(zip(records,plan)):
        x=(k%cols)*w;y=105+(k//cols)*h
        pic=Image.open(r["file"])
        thumb=ImageOps.contain(pic,(w-28,h-100))
        im.paste(thumb,(x+(w-thumb.width)//2,y+5))
        d.text((x+10,y+h-83),"%02d "%(k+1)+s["narrative_function"][:28],font=font(16,True),fill=NAVY)
        d.text((x+10,y+h-55),"Fonte p.%s; match da revisionare"%r["edition_page_candidate"],font=font(14),fill=NAVY)
    im.save(OUT/"STORYBOARD_16_SCENE.jpg",quality=90)
def music(seconds,out):
    import numpy as np,soundfile as sf
    rate=24000;n=int((seconds+.2)*rate);sound=np.zeros(n,dtype=np.float32)
    # Original simple minor-key music-box theme, not a third-party recording.
    notes=[57,60,64,60,55,59,62,59,53,57,60,57,52,55,59,55]
    for k in range(int(seconds/.42)+1):
        pos=int(k*.42*rate);length=min(n-pos,int(.95*rate))
        if length<=0:break
        t=np.arange(length,dtype=np.float32)/rate
        f=440*2**((notes[k%len(notes)]-69)/12)
        tone=np.sin(2*np.pi*f*t)+.23*np.sin(2*np.pi*f*2*t)
        env=np.minimum(1,t/.018)*np.exp(-t/.48)
        sound[pos:pos+length]+=.045*tone*env
    t=np.arange(n,dtype=np.float32)/rate
    sound*=np.minimum(1,t/1.2)*np.minimum(1,np.maximum(0,seconds-t)/2.5)
    sf.write(out,np.clip(sound,-.4,.4),rate)
def make_preview(records):
    seconds=24.0
    wav=OUT/"MUSICA_ORIGINALE_PREVIEW.wav";music(seconds,wav)
    (OUT/"MUSICA_CREDITI.txt").write_text(
        "Anteprima: composizione sintetizzata originale Tra le Pagine, nessun sample di terzi. Nessuna voce. Non è il master narrato.\n",encoding="utf-8")
    with tempfile.TemporaryDirectory() as t:
        concat=Path(t)/"concat.txt"
        rows=[]
        for r in records:
            p=Path(r["file"]).resolve()
            rows.extend(["file '"+str(p).replace("'","'\\''")+"'","duration 1.5"])
        rows.append("file '"+str(Path(records[-1]["file"]).resolve())+"'")
        concat.write_text("\n".join(rows)+"\n")
        dest=OUT/"PIFFERAIO_ANTEPRIMA_24S_SENZA_VOCE.mp4"
        run("ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",concat,
            "-i",wav,"-vf","fps=24,format=yuv420p","-t","24","-c:v","libx264","-preset","veryfast",
            "-crf","24","-c:a","aac","-b:a","128k","-movflags","+faststart",dest)
    info=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format",
        "-of","json",str(dest)]))
    video=next(x for x in info["streams"] if x["codec_type"]=="video")
    audio=next(x for x in info["streams"] if x["codec_type"]=="audio")
    assert (video["width"],video["height"])==(720,1280) and audio["codec_name"]=="aac"
    assert 23.5<=float(info["format"]["duration"])<=24.5
    subprocess.run(["ffmpeg","-v","error","-i",str(dest),"-f","null","-"],check=True)
    write_json(OUT/"ANTEPRIMA_QA.json",{"file":dest.name,"sha256":sha(dest.read_bytes()),
        "duration_seconds":float(info["format"]["duration"]),"width":720,"height":1280,
        "video_codec":video["codec_name"],"audio_codec":audio["codec_name"],
        "voice":False,"status":"VISUAL_PREVIEW_NOT_NARRATED_NOT_APPROVED","decode_full":True})
def package(records):
    out=OUT/"PIFFERAIO_PACCHETTO_VISUALE_NON_FINALE.zip"
    with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED,compresslevel=2) as z:
        for f in OUT.iterdir():
            if f.is_file() and f!=out:z.write(f,f.name)
        for r in records:z.write(r["file"],"ILLUSTRAZIONI/"+Path(r["file"]).name)
    with zipfile.ZipFile(out) as z:assert z.testzip() is None
    p=OUT/"PIFFERAIO_ANTEPRIMA_SOLO_VIDEO_ANDROID.zip"
    with zipfile.ZipFile(p,"w",zipfile.ZIP_STORED) as z:
        f=OUT/"PIFFERAIO_ANTEPRIMA_24S_SENZA_VOCE.mp4";z.write(f,f.name)
    with zipfile.ZipFile(p) as z:assert z.testzip() is None
if __name__=="__main__":acquire()
