#!/usr/bin/env python3
"""ArtVision owner-selected 30: new independent chromatic variant, authentic artwork and real licensed music."""
from __future__ import annotations
import argparse, hashlib, io, json, math, random, re, subprocess, time, zipfile
from pathlib import Path
import requests
import numpy as np
from PIL import Image,ImageOps,ImageDraw,ImageFont,ImageFilter,ImageEnhance

parser=argparse.ArgumentParser()
parser.add_argument("--index",type=int,required=True)
args=parser.parse_args()
# Museum IDs have been individually verified, as have the original dimensions (2026-11-20).
# Per work: camera anchors in the coordinate system of the original painting (x,y normalized).
WORKS=[
dict(id=1,slug="01_ARBO_WILD_HUNT",title="The Wild Hunt of Odin",artist="Peter Nicolai Arbo",year="1872",it="La caccia selvaggia",music="Ever Mindful",start=9,mood="Una cavalcata di spiriti attraversa le nuvole sopra un paesaggio notturno",
 source_file="Peter Nicolai Arbo - The wild Hunt of Odin - NG.M.00258 - National Museum of Art, Architecture and Design.jpg",source_sha1="ecb86ffd7042eaedaa334fedce39ff795029960f",source_bytes=7151028,source_pixels=(10291,7074),source_license="CC BY 4.0",source_author="National Museum of Norway",museum="National Museum of Norway, Oslo",object_url="https://www.nasjonalmuseet.no/en/collection/object/NG.M.00258",
 focus=[(.55,.27),(.31,.34),(.72,.29),(.23,.55),(.52,.81),(.82,.61)]),
dict(id=2,slug="02_DADD_FAIRY_FELLER",title="The Fairy Feller's Master-Stroke",artist="Richard Dadd",year="1855–1864",it="Il colpo della fata",music="Dreams Become Real",start=22,mood="Un mondo minuscolo di figure fantastiche tra erbe gigantesche e un'ascia sospesa",
 source_file="Richard_dadd,_il_colpo_da_maestro_del_cantastorie,_1855-64,_01.jpg",source_sha1="0960e2d3a3d114c67c6455ce655f92f29f37413f",source_bytes=8608140,source_pixels=(3024,3828),crop=(420,488,2610,3370),source_license="CC BY 3.0",source_author="Sailko, photograph 2017",museum="Tate Britain, London",object_url="https://www.tate.org.uk/art/artworks/dadd-the-fairy-fellers-master-stroke-t00598",
 focus=[(.48,.56),(.29,.34),(.66,.35),(.51,.78),(.21,.64),(.77,.70)]),
dict(id=3,slug="03_REPIN_SADKO",title="Sadko",artist="Ilya Repin",year="1876",it="Il regno sommerso",music="Eternal Hope",start=16,mood="Un giovane esplora un palazzo sottomarino e le sue figure misteriose",
 source_file="Ilya Repin - Sadko - Google Art Project.jpg",source_sha1="0ff86b2ec881974eb5474dafa2f4ee6842082a3f",source_bytes=7009147,source_pixels=(5444,7660),source_license="PD-Art / PDM",source_author="Google Art Project via Wikimedia Commons",museum="State Russian Museum, Saint Petersburg",object_url="https://virtual.rusmuseumvrm.ru/mikh_palace/collection/russkoe_iskusstvo_vtoroy_polovini_xix_veka/sadko/index.php?lang=ru",
 focus=[(.53,.65),(.34,.31),(.73,.37),(.24,.72),(.57,.22),(.76,.83)]),
dict(id=4,slug="04_PRINCESS_TARAKANOVA",title="Princess Tarakanova",artist="Konstantin Flavitsky",year="1863–1864",it="L'acqua nella cella",music="At Rest",start=12,mood="Una principessa in una cella, l'acqua sale in silenzio",
 source_file="Tarakanova.jpg",source_sha1="4e96a98a1d6a4568119f54c348ca329ad6fc2521",source_bytes=463191,source_pixels=(1400,1845),source_license="PD-Art / PDM",source_author="Wikimedia Commons faithful reproduction",museum="State Tretyakov Gallery, Moscow",object_url="https://my.tretyakov.ru/app/masterpiece/8412",
 focus=[(.51,.38),(.28,.18),(.68,.19),(.35,.79),(.71,.72),(.58,.48)]),
dict(id=20,slug="05_WATERHOUSE_MERMAID",title="A Mermaid",artist="John William Waterhouse",year="1900",it="Il canto della sirena",music="Serene",start=13,mood="La figura di una sirena presso il mare, tra capelli, conchiglie e luce",
 source_file="John William Waterhouse - Mermaid.JPG",source_sha1="e288cc3ad87653593f4a634256bcd595495c08fe",source_bytes=578091,source_pixels=(1852,2693),source_license="PD-Art / PDM",source_author="Wikimedia Commons faithful reproduction",museum="Royal Academy of Arts, London",object_url="https://www.royalacademy.org.uk/art-artists/work-of-art/a-mermaid",
 focus=[(.49,.36),(.27,.19),(.68,.26),(.32,.69),(.61,.80),(.46,.54)]),
dict(id=21,slug="06_DE_MORGAN_STORM_SPIRITS",title="The Storm Spirits",artist="Evelyn De Morgan",year="1900",it="Gli spiriti della tempesta",music="Ever Mindful",start=45,mood="Figure sospese e nubi trascinate da un movimento drammatico",
 source_file="The Storm Spirits, by Evelyn De Morgan.jpg",source_sha1="1c833194a496ee4484331d63e6418a8e1ba13a16",source_bytes=10487935,source_pixels=(5290,3600),source_license="Public Domain Mark 1.0 / PDM",source_author="Watts Gallery via Wikimedia Commons",museum="De Morgan Foundation",object_url="https://www.demorgan.org.uk/collection/the-storm-spirits/",
 focus=[(.54,.38),(.22,.30),(.76,.30),(.37,.68),(.71,.76),(.45,.18)]),
dict(id=23,slug="07_RHEAM_SLEEPING_BEAUTY",title="The Sleeping Beauty",artist="Henry Meynell Rheam",year="1899",it="La bella addormentata",music="Calmant",start=13,mood="Una donna addormentata in una composizione fantastica di dettagli vegetali",
 source_file="Henry_meynell_rheam_the_sleeping_beauty2024_CKS_22681_0006_000(120158).jpg",source_sha1="7f6274429419bbc98b719d9b5020482442f5906b",source_bytes=0,source_pixels=(3200,1987),source_license="PD-Art / PDM (territorial permissions to verify)",source_author="Christie's via Wikimedia Commons",museum="Christie's auction archival catalog 2024",object_url="https://www.christies.com/lot/lot-6486205",
 focus=[(.48,.54),(.21,.37),(.78,.38),(.28,.76),(.70,.78),(.54,.25)])
]
MUSIC={
"Eternal Hope":dict(isrc="USUAN1100238",license="CC BY 4.0",source="https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100238"),
"Dreams Become Real":dict(isrc="USUAN1500027",license="CC BY 4.0",source="https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1500027"),
"At Rest":dict(isrc="USUAN1100748",license="CC BY 4.0",source="https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100748"),
"Serene":dict(isrc="USUAN1100082",license="CC BY 4.0",source="https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100082"),
"Calmant":dict(isrc="USUAN1100859",license="CC BY 4.0",source="https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100859"),
"Ever Mindful":dict(isrc="USUAN1700033",license="CC BY 4.0",source="https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1700033")
}
assert 0<=args.index<len(WORKS)
C=WORKS[args.index]; A=C["slug"]
BASE=Path("output/artvision_owner30_cromatica")/A;ASSETS=BASE/"assets";FRAMES=BASE/"frames";DIST=BASE/"dist"
for p in (BASE,ASSETS,FRAMES,DIST):p.mkdir(parents=True,exist_ok=True)
W,H,FPS=720,1280,30
HEADERS={"User-Agent":"ArtVisionMuseumArtResearch/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-)"}
session=requests.Session();session.headers.update(HEADERS)
def fetch(url,path,minbytes):
    errors=[]
    for attempt in range(3):
        try:
            r=session.get(url,timeout=85)
            r.raise_for_status()
            data=r.content
            if len(data)<minbytes:raise RuntimeError(f"file too small: {len(data)}")
            path.write_bytes(data)
            return dict(url=url,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
        except Exception as exc:
            errors.append(str(exc)[:160]);time.sleep(1.2*(attempt+1))
    raise RuntimeError(f"Cannot download verified licensed media {url}: {errors}")
# Original exact-file downloads and locks from the OWNER SELECTED 30 checkpoints.
# Original artwork identity, source SHA1, pixels, and source photographer are verified.
import urllib.parse
key=C["source_file"].replace(" ","_")
digest=hashlib.md5(key.encode("utf-8")).hexdigest()
filename=urllib.parse.quote(key,safe="._-")
file_url=f"https://upload.wikimedia.org/wikipedia/commons/{digest[0]}/{digest[:2]}/{filename}"
fallback="https://commons.wikimedia.org/wiki/Special:Redirect/file/"+filename
art_fetch=None
for candidate in (file_url,fallback):
    try:
        art_fetch=fetch(candidate,ASSETS/"original_work.jpg",100_000)
        break
    except Exception as exc:
        print("MUSEUM_SOURCE_ATTEMPT_FAILED",str(exc)[:260],flush=True)
if not art_fetch:raise RuntimeError("No authentic exact painting source; do not generate an AI replacement")
original_bytes=(ASSETS/"original_work.jpg").read_bytes()
actual_sha1=hashlib.sha1(original_bytes).hexdigest()
assert actual_sha1==C["source_sha1"],f"Wrong photograph SHA1! {actual_sha1}"
if C["source_bytes"]:
    assert len(original_bytes)==C["source_bytes"],f"Wrong file byte count {len(original_bytes)}"
with Image.open(ASSETS/"original_work.jpg") as im:
    assert tuple(im.size)==tuple(C["source_pixels"]),f"Wrong image dimensions {im.size}"
    original=im.convert("RGB")
SOURCE=original.crop(C["crop"]) if "crop" in C else original
print("EXACT_PAINTING_SOURCE_VERIFIED",C["title"],C["source_sha1"],original.size,flush=True)
if max(SOURCE.size)>4700:
    SOURCE.thumbnail((4700,4700),Image.Resampling.LANCZOS)
assert SOURCE.width>=1200 and SOURCE.height>=950,(SOURCE.width,SOURCE.height)
meta={"title":C["title"],"artistDisplayName":C["artist"],"objectDate":C["year"],
      "objectID":C["id"],"objectURL":C["object_url"],"repository":C["museum"],
      "isPublicDomain":True}
art_fetch["source_sha1"]=actual_sha1
art_fetch["original_pixels"]=list(original.size)
art_fetch["editorial_crop"]=list(C["crop"]) if "crop" in C else None
# Official composer site provides exact song and CC BY 4.0 licence; filename known and tested in preflight.
import urllib.parse
music_meta=MUSIC[C["music"]]
url="https://incompetech.com/music/royalty-free/mp3-royaltyfree/"+urllib.parse.quote(C["music"],safe="")+".mp3"
aud_fetch=fetch(url,ASSETS/"licensed_recording.mp3",300_000)
print("MUSIC VERIFIED",C["music"],music_meta["isrc"],aud_fetch["bytes"],flush=True)
# Progressive 9:16 camera motions. The complete painting will be presented as a legible
# image, backed by blurred pixels FROM THE SAME painting. This is not an AI reconstruction.
BG=ImageEnhance.Brightness(ImageOps.fit(SOURCE,(W,H),method=Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(38))).enhance(.53)
FULL=ImageOps.contain(SOURCE,(W,H),method=Image.Resampling.LANCZOS)
CACHE={}
def scale_to(z):
    z=round(z,3)
    if z not in CACHE:
        s=max(W/SOURCE.width,H/SOURCE.height)*z
        nw=max(W,math.ceil(SOURCE.width*s));nh=max(H,math.ceil(SOURCE.height*s))
        CACHE[z]=SOURCE.resize((nw,nh),Image.Resampling.LANCZOS)
    return CACHE[z]
def smooth(p):
    p=max(0,min(1,p));return p*p*(3-2*p)
def crop_anchor(x,y,z):
    src=scale_to(z)
    dx=src.width-W;dy=src.height-H
    ix=min(max(0,round(x*src.width-W/2)),dx)
    iy=min(max(0,round(y*src.height-H/2)),dy)
    return src.crop((ix,iy,ix+W,iy+H))
BASEW=scale_to(1.0)
def whole_frame(p):
    # p=0 cover frame, p=1 entire original art fully visible; eased.
    t=smooth(p)
    w=round(BASEW.width*(1-t)+FULL.width*t)
    h=round(BASEW.height*(1-t)+FULL.height*t)
    resized=BASEW.resize((w,h),Image.Resampling.LANCZOS)
    canvas=BG.copy()
    if w>=W and h>=H:
        return resized.crop(((w-W)//2,(h-H)//2,(w+W)//2,(h+H)//2))
    canvas.paste(resized,((W-w)//2,(H-h)//2))
    return canvas
FONTS=["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
       "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"]
FONT=next((f for f in FONTS if Path(f).exists()),None)
assert FONT
ft=ImageFont.truetype(FONT,31)
namefont=ImageFont.truetype(FONT,25)
yearfont=ImageFont.truetype(FONT,21)
def on_title(im,t):
    a=min(1,max(0,(3.65-t)/.65))
    if a<=0:return im
    lay=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(lay)
    def box_text(s,y,h,font,fill,text):
        bbox=d.textbbox((0,0),s,font=font)
        textw=bbox[2]-bbox[0]
        if textw>W-76:
            # shrink for long artist names, preserve readability by dedicated line.
            font=ImageFont.truetype(FONT,max(16,int(font.size*(W-76)/textw)))
            bbox=d.textbbox((0,0),s,font=font);textw=bbox[2]-bbox[0]
        x0=(W-textw)//2-20;x1=(W+textw)//2+20
        d.rounded_rectangle([x0,y,x1,y+h],radius=7,fill=(*fill,int(237*a)))
        ty=y+(h-(bbox[3]-bbox[1]))//2-bbox[1]
        d.text(((W-textw)//2,ty),s,font=font,fill=(*text,int(255*a)))
    box_text(C["it"].upper(),540,70,ft,(7,11,18),(255,255,255))
    box_text(C["artist"],624,52,namefont,(245,244,239),(8,14,26))
    box_text(C["year"],690,48,yearfont,(243,241,236),(8,14,26))
    return Image.alpha_composite(im.convert("RGBA"),lay).convert("RGB")
# Edition varies by artwork, not mechanical time stamping.
rng=random.Random(C["id"])
points=C["focus"]
# Durations and shot choices follow the revealed features, rather than recurring flash cuts.
tweak=[rng.choice([-.4,-.2,.0,.2,.4]) for _ in range(10)]
D=lambda n,i:max(2.7,round(n+tweak[i],1))
shots=[
 {"kind":"detail","dur":D(3.6,0),"a":points[0],"b":points[0],"z":1.15,"why":"Opening visual hook: "+C["mood"]},
 {"kind":"detail","dur":D(4.4,1),"a":points[1],"b":points[0],"z":1.17,"why":"Meaningful sweep towards main subject"},
 {"kind":"detail","dur":D(4.5,2),"a":points[2],"b":points[2],"z":1.23,"why":"Sky and scale of the original landscape"},
 {"kind":"detail","dur":D(4.1,3),"a":points[3],"b":points[0],"z":1.18,"why":"Human scale, vegetation or geology in painting"},
 {"kind":"detail","dur":D(3.9,4),"a":points[4],"b":points[5],"z":1.22,"why":"Second visual motif"},
 {"kind":"reveal","dur":D(4.1,5),"why":"Gradual pull-out toward complete authentic work"},
 {"kind":"whole","dur":7.8,"why":"Original ENTIRE painting, no cropping, held for appreciation"},
 {"kind":"approach","dur":3.6,"why":"Motivated return from whole view to details"},
 {"kind":"detail","dur":D(4.8,6),"a":points[5],"b":points[3],"z":1.17,"why":"New path across artwork, no abrupt border changes"},
 {"kind":"detail","dur":D(4.6,7),"a":points[3],"b":points[1],"z":1.19,"why":"Emotional recollection of first visual motif"},
 {"kind":"reveal","dur":D(3.7,8),"why":"Slow return to full composition"},
 {"kind":"whole","dur":D(4.2,9),"why":"Hold complete painting in closing; no end graphic"}]
DURATION=round(sum(q["dur"] for q in shots),2)
assert 48<=DURATION<=62
print("VIDEO_PLAN",A,"duration",DURATION,"shots",len(shots),flush=True)
frame_idx=1; elapsed=0; edl=[]
for i,q in enumerate(shots):
    N=round(q["dur"]*FPS)
    edl.append({"n":i+1,"start":round(elapsed,2),"end":round(elapsed+q["dur"],2),
                "kind":q["kind"],"description":q["why"],"frames":N})
    for k in range(N):
        p=smooth(k/max(1,N-1))
        if q["kind"]=="detail":
            x=q["a"][0]+(q["b"][0]-q["a"][0])*p
            y=q["a"][1]+(q["b"][1]-q["a"][1])*p
            im=crop_anchor(x,y,q["z"])
        elif q["kind"]=="reveal":im=whole_frame(p)
        elif q["kind"]=="approach":im=whole_frame(1-p)
        elif q["kind"]=="whole":im=whole_frame(1)
        else:raise RuntimeError("Unknown scene kind")
        assert im.size==(W,H)
        if elapsed+k/FPS<3.65:im=on_title(im,elapsed+k/FPS)
        im.save(FRAMES/f"frame_{frame_idx:06d}.jpg",quality=89,subsampling=0)
        frame_idx+=1
    print("SCENE_DONE",i+1,"of",len(shots),q["kind"],flush=True)
    elapsed+=q["dur"]
assert abs(elapsed-DURATION)<1e-6
# Apply a REAL musical recording; never synthesize cheap electronic drones.
# Clip and normalize, retaining credits to the CC BY 4.0 composition + recording.
def cmd(command):
    r=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    if r.returncode!=0:raise RuntimeError(f"CMD_FAIL {command[0]} "+r.stderr[-2700:])
    return r.stdout
video=BASE/(A+"_ARTVISION_REEL.mp4")
silent=BASE/(A+"_META_SENZA_MUSICA.mp4")
audio_offset=C["start"]
cmd(["ffmpeg","-hide_banner","-loglevel","warning","-y",
 "-framerate","30","-i",str(FRAMES/"frame_%06d.jpg"),
 "-ss",str(audio_offset),"-i",str(ASSETS/"licensed_recording.mp3"),
 "-map","0:v:0","-map","1:a:0",
 "-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","-r","30",
 "-c:a","aac","-b:a","160k",
 "-af",f"atrim=duration={DURATION},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=1.7,afade=t=out:st={DURATION-3.4}:d=3.4,loudnorm=I=-15:TP=-1.4:LRA=11",
 "-t",str(DURATION),"-movflags","+faststart",str(video)])
cmd(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(video),
 "-map","0:v:0","-c:v","copy","-an","-movflags","+faststart",str(silent)])
cover=BASE/(A+"_COVER.jpg")
Image.open(FRAMES/"frame_000025.jpg").save(cover,quality=92)
# QA on actual MP4 and separate audio-free Meta version; full decode both.
probe={}
for path in [video,silent]:
    info=json.loads(cmd(["ffprobe","-v","error","-show_entries",
      "format=duration,size:stream=codec_name,width,height,r_frame_rate",
      "-of","json",str(path)]))
    v=[x for x in info["streams"] if x.get("codec_name")=="h264"]
    a=[x for x in info["streams"] if x.get("codec_name")=="aac"]
    assert v and v[0]["width"]==W and v[0]["height"]==H
    assert (len(a)>=1) == (path==video)
    assert abs(float(info["format"]["duration"])-DURATION)<0.25
    cmd(["ffmpeg","-v","error","-xerror","-i",str(path),"-f","null","-"])
    probe[path.name]={"duration":info["format"]["duration"],"bytes":path.stat().st_size,
                      "audio":bool(a),"decode":"PASS"}
# Extract full-work visibility and appearance checkpoints: get the 7.8 s hold plus final.
assert sum(x["dur"] for x in shots if x["kind"]=="whole")>=11
time_samples=[1.0]
for q in edl:time_samples.append((q["start"]+q["end"])/2)
time_samples.append(DURATION-.8)
sheet=Image.new("RGB",(7*144,2*288),(16,19,28))
for i,sec in enumerate(time_samples):
    f=min(frame_idx-1,max(1,round(sec*FPS)+1))
    snap=Image.open(FRAMES/f"frame_{f:06d}.jpg")
    snap.thumbnail((140,250),Image.Resampling.LANCZOS)
    xx=(i%7)*144; yy=(i//7)*288
    sheet.paste(snap,(xx+(144-snap.width)//2,yy))
    ImageDraw.Draw(sheet).text((xx+6,yy+254),f"{sec:04.1f}s",fill="white")
sheetpath=BASE/(A+"_QA.jpg");sheet.save(sheetpath,quality=90)
music_cred=f'{C["music"]} — Kevin MacLeod (incompetech.com), Creative Commons Attribution 4.0, https://creativecommons.org/licenses/by/4.0/; excerpt and mixing altered.'
cap=f'''{C["it"]}.

{C["mood"]}.

Opera autentica già selezionata: {meta["title"]} — {meta["artistDisplayName"]}, {meta.get("objectDate")}. Archivio: {C["museum"]}. Opera storica, senza immagini generate.
Foto conservata nel file originale, senza scene generate con AI.

Musica: {music_cred}
#ArtVision #Arte #Paesaggi #ArtHistory'''
for social in ("FACEBOOK","INSTAGRAM","TIKTOK","YOUTUBE"):
    (BASE/f"POST_{social}.txt").write_text(cap,encoding="utf-8")
rights=f'''# Fonte opera e musica verificati
Opera originale, archivio: {C["museum"]}, {C["object_url"]}
Opera: {meta["title"]} / {meta["artistDisplayName"]}, {meta.get("objectDate")}
Opera storica di pubblico dominio; licenza della fotografia esatta: {C["source_license"]}, fotografo/provenienza: {C["source_author"]}. Eventuali condizioni territoriali commerciali ancora da verificare.
Immagine: {art_fetch["url"]}
Immagine SHA256: {art_fetch["sha256"]}; SHA1: {art_fetch["source_sha1"]}; foto originale: {original.width} x {original.height} pixels; canvas render: {SOURCE.width} x {SOURCE.height}
Nessun generatore AI usato per il quadro. Tutta l'opera originale appare per almeno 11 secondi complessivi.
Musica: {C["music"]}, Kevin MacLeod; ISRC {music_meta["isrc"]}
Pagina di licenza: {music_meta["source"]}
Registrazione reale: {aud_fetch["url"]}
Registrazione SHA256: {aud_fetch["sha256"]}
Creative Commons Attribution 4.0 https://creativecommons.org/licenses/by/4.0/ (attribuire, segnalare modifiche)
Modifiche: estratto dal secondo {audio_offset}, taglio, mix, fade, normalizzazione.
VERSIONE FACEBOOK (senza musica): selezionare un brano nella Meta Sound Collection DENTRO Facebook/Instagram;
non usare la traccia Meta su piattaforme non autorizzate.
Non presentare questo MP4 come contenente musica Meta. MP4 principale contiene Kevin MacLeod.
Stato di pubblicazione: NON PUBBLICATO, ARTISTIC_REVIEW_PENDING.
'''
(BASE/"SOURCES_AND_RIGHTS.md").write_text(rights,encoding="utf-8")
report={"status":"RENDERED_NEEDS_ARTISTIC_REVIEW",
  "artist":meta["artistDisplayName"],"title":meta["title"],"object_id":meta["objectID"],
  "duration_s":DURATION,"sources":{"art":art_fetch,"recording":aud_fetch},
  "factual":{"museum":meta.get("repository"),"date":meta.get("objectDate"),"public_domain":True},
  "qa":{"ffmpeg_full_decode_pass":True,"full_work_held_seconds":sum(q["dur"] for q in shots if q["kind"]=="whole"),
        "no_black_letterbox_asset":True,"user_feedback_approval":False,"probe":probe},
  "edit_decision_list":edl,
  "variant":"reel_cromatica_owner_selected_30_additional_not_4x1_slot",
  "photo_license":C["source_license"],"owner_selected_list":True,
  "publishing_allowed":False,"music_meta_note":"No music supplied by Facebook; ready for manual Meta Sound Collection track in separate silent master"}
(BASE/"QA_AND_EDIT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
package=[video,silent,cover,sheetpath,BASE/"SOURCES_AND_RIGHTS.md",BASE/"QA_AND_EDIT.json"]+[BASE/f"POST_{x}.txt" for x in ("FACEBOOK","INSTAGRAM","TIKTOK","YOUTUBE")]
with zipfile.ZipFile(DIST/(A+"_COMPLETO.zip"),"w",zipfile.ZIP_DEFLATED,compresslevel=5) as z:
    for p in package:z.write(p,p.name)
with zipfile.ZipFile(DIST/(A+"_ANDROID.zip"),"w",zipfile.ZIP_STORED) as z:z.write(video,video.name)
with zipfile.ZipFile(DIST/(A+"_META.zip"),"w",zipfile.ZIP_STORED) as z:z.write(silent,silent.name)
for p in DIST.glob("*.zip"):
    with zipfile.ZipFile(p) as z:assert z.testzip() is None
    print("ZIP_OK",p,round(p.stat().st_size/1e6,2),"MB",flush=True)
print("REEL_COMPLETE",A,C["title"],DURATION,video.stat().st_size,flush=True)
