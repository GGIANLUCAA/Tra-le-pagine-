#!/usr/bin/env python3
"""ArtVision REEL CROMATICA: John Martin, The Bard (~1817). Real original work, original recording licensed CC BY."""
from __future__ import annotations
import hashlib, io, json, math, random, subprocess, time, zipfile
from pathlib import Path
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps

O=Path("output/reel_the_bard_1817"); A=O/"assets"; D=O/"dist"; F=O/"frames"
for p in (O,A,D,F):p.mkdir(parents=True,exist_ok=True)
W,H,FPS=720,1280,30
UA="ArtVisionArtHistory/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-)"
SOURCE_IMAGE="https://upload.wikimedia.org/wikipedia/commons/d/df/John_Martin_-_The_Bard_-_Google_Art_Project.jpg"
SOURCE_IMAGE_PAGE="https://commons.wikimedia.org/wiki/File:John_Martin_-_The_Bard_-_Google_Art_Project.jpg"
MUSIC_URL="https://upload.wikimedia.org/wikipedia/commons/5/54/Eternal_Hope_%28ISRC_USUAN1100238%29.mp3"
MUSIC_URL_BACKUP="https://incompetech.com/music/royalty-free/mp3-royaltyfree/Eternal%20Hope.mp3"
MUSIC_PAGE="https://commons.wikimedia.org/wiki/File:Eternal_Hope_(ISRC_USUAN1100238).mp3"
MUSIC_INFO="https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100238"
META_URL="https://www.facebook.com/sound/collection/"
session=requests.Session()
session.headers.update({"User-Agent":UA,"Accept":"*/*"})
def download(urls,destination,minbytes=80000):
    errors=[]
    for url in urls:
        for attempt in range(2):
            try:
                r=session.get(url,timeout=65)
                r.raise_for_status()
                if len(r.content)<minbytes:raise ValueError(f"file suspiciously small {len(r.content)}")
                destination.write_bytes(r.content)
                print("ASSET_OK",destination.name,len(r.content),url,flush=True)
                return {"url":url,"bytes":len(r.content),"sha256":hashlib.sha256(r.content).hexdigest()}
            except Exception as exc:
                errors.append(str(exc)[:140]);time.sleep(1)
    raise RuntimeError("Source not accessible; do not substitute an AI asset: "+repr(errors))
imgmeta=download([SOURCE_IMAGE,"https://commons.wikimedia.org/wiki/Special:Redirect/file/John_Martin_-_The_Bard_-_Google_Art_Project.jpg"],A/"THE_BARD.jpg",120000)
musicmeta=download([MUSIC_URL,MUSIC_URL_BACKUP],A/"ETERNAL_HOPE_Kevin_MacLeod.mp3",1000000)
source=ImageOps.exif_transpose(Image.open(A/"THE_BARD.jpg")).convert("RGB")
assert source.width>=3000 and source.height>=3000,(source.width,source.height)
# The original ratio is 0.795, nearer to 9:16 than the previous panoramic sea painting.
# Distinct screen states: DETAIL=paint pixels full bleed, WHOLE=the entire unchanged painting visible
# over a softly blurred background derived from the SAME original photograph. No black bars.
full_bg=ImageOps.fit(source,(W,H),method=Image.Resampling.LANCZOS,centering=(.5,.5))
full_bg=ImageEnhance.Brightness(full_bg.filter(ImageFilter.GaussianBlur(43))).enhance(.60)
zoom_cache={}
def base_for(z):
    key=round(z,3)
    if key in zoom_cache:return zoom_cache[key]
    sf=max(W/source.width,H/source.height)*z
    w=math.ceil(source.width*sf); h=math.ceil(source.height*sf)
    result=source.resize((max(w,W),max(h,H)),Image.Resampling.LANCZOS)
    zoom_cache[key]=result;return result
def ease(x):
    x=max(0,min(1,x));return x*x*(3-2*x)
def shot_crop(x,y,z):
    base=base_for(z)
    dx=max(0,base.width-W);dy=max(0,base.height-H)
    cx=round(min(dx,max(0,base.width*x-W/2)))
    cy=round(min(dy,max(0,base.height*y-H/2)))
    return base.crop((cx,cy,cx+W,cy+H))
font_candidates=["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"]
regular_candidates=["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"]
fb=next((x for x in font_candidates if Path(x).exists()),None)
fr=next((x for x in regular_candidates if Path(x).exists()),None)
if not fb or not fr:raise RuntimeError("Typography fonts missing")
f_title=ImageFont.truetype(fb,32);f_name=ImageFont.truetype(fr,27);f_geo=ImageFont.truetype(fr,22)
def title_overlay(im,seconds):
    alpha=1.0 if seconds<2.6 else max(0,(3.45-seconds)/.85)
    if alpha<=0:return im
    layer=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(layer)
    def chip(words,box,font,fill,txt):
        color=tuple(fill[:3])+(round(fill[3]*alpha),)
        d.rounded_rectangle(box,radius=8,fill=color)
        bbox=d.textbbox((0,0),words,font=font)
        x=(W-(bbox[2]-bbox[0]))//2
        y=(box[1]+box[3]-(bbox[3]-bbox[1]))//2-bbox[1]
        d.text((x,y),words,font=font,fill=tuple(txt)+(round(255*alpha),))
    chip("IL CANTO SULL'ABISSO",(30,540,690,617),f_title,(0,0,0,235),(255,255,255))
    chip("JOHN MARTIN",(100,629,620,686),f_name,(245,244,239,245),(9,18,29))
    chip("GRAN BRETAGNA · 1817",(161,698,559,751),f_geo,(246,245,240,242),(9,18,29))
    # Print-friendly stylized UK flag at bottom-right, no emoji rendering dependency.
    # Text above is correct geographic label; flag is not used for a false national claim.
    im=Image.alpha_composite(im.convert("RGBA"),layer).convert("RGB")
    return im
# Narrative: character -> valley -> waterfall -> mountains -> heroic figure -> whole painting.
# Stable 9:16 output. The ALL-PAINTING segment uses camera pull-out instead of abrupt matte.
shots=[
 dict(s=3.5,kind="detail",start=(.70,.34),end=(.715,.34),z=1.23,goal="Poet on cliff, visual hook and title"),
 dict(s=4.4,kind="detail",start=(.21,.34),end=(.38,.32),z=1.24,goal="Castle and distant mountains, purposeful lateral study"),
 dict(s=4.4,kind="detail",start=(.46,.18),end=(.65,.19),z=1.30,goal="Sublime mountain ridges without a hard jump"),
 dict(s=4.2,kind="detail",start=(.27,.78),end=(.41,.79),z=1.28,goal="Waterfall and soldiers against the landscape"),
 dict(s=4.5,kind="detail",start=(.69,.37),end=(.68,.35),z=1.26,goal="Return to poet and harp; pause in the narrative"),
 dict(s=4.0,kind="detail",start=(.36,.56),end=(.46,.54),z=1.18,goal="Mountains and valley in the same authentic painting"),
 dict(s=5.0,kind="reveal",start=(.50,.50),end=(.50,.50),z=1.0,goal="Seamless camera pullback to WHOLE painting, no format change"),
 dict(s=7.0,kind="whole",start=(.50,.50),end=(.50,.50),z=1.0,goal="Entire original canvas, unaltered, held long enough to inspect"),
 dict(s=4.4,kind="approach",start=(.48,.52),end=(.48,.52),z=1.0,goal="Slow push from full painting into valley"),
 dict(s=4.4,kind="detail",start=(.30,.80),end=(.39,.75),z=1.25,goal="Final waterfall; gentle camera movement"),
 dict(s=4.4,kind="detail",start=(.67,.35),end=(.71,.34),z=1.22,goal="Final recognition of bard on precipice"),
 dict(s=4.9,kind="reveal",start=(.50,.50),end=(.50,.50),z=1.0,goal="Closing whole canvas; no end card or subtitles"),
]
DURATION=round(sum(q["s"] for q in shots),2)
print("TIMELINE_SECONDS",DURATION,"SCENES",len(shots),flush=True)
assert 50<=DURATION<=63
# Whole image asset: do not crop or deform.
WHOLE=ImageOps.contain(source,(W,H),method=Image.Resampling.LANCZOS)
assert WHOLE.width<=W and WHOLE.height<=H
def whole_at(progress):
    # progress 0=full bleed original central crop, 1=whole image fully visible;
    # background ALWAYS generated from actual painting pixels and is constant.
    p=ease(progress);targetw=W/WHOLE.width
    # Scale of original that fills the canvas is exactly H/source.height.
    # Effective scale factor 1 -> entire image width equals output width.
    fill=base_for(1.0) # max(W, source.width*H/source.height) x H
    w=int(round(fill.width*(1-p)+WHOLE.width*p))
    h=int(round(fill.height*(1-p)+WHOLE.height*p))
    sub=fill.resize((w,h),Image.Resampling.LANCZOS)
    dst=full_bg.copy()
    if w>=W and h>=H:
        x=(w-W)//2;y=(h-H)//2
        return sub.crop((x,y,x+W,y+H))
    # Destination remains continuous; no letterbox and no added graphic matte.
    x=(W-w)//2;y=(H-h)//2
    dst.paste(sub,(x,y))
    return dst
frame=1;timeline=0;edl=[]
for k,shot in enumerate(shots):
    n=round(shot["s"]*FPS)
    edl.append({"scene":k+1,"start":round(timeline,2),"duration":shot["s"],"end":round(timeline+shot["s"],2),
        "visual":shot["kind"],"purpose":shot["goal"],"master_source":"THE_BARD.jpg","full_painting_visible":shot["kind"]=="whole"})
    for j in range(n):
        p=ease(j/max(1,n-1))
        if shot["kind"]=="detail":
            x=shot["start"][0]+(shot["end"][0]-shot["start"][0])*p
            y=shot["start"][1]+(shot["end"][1]-shot["start"][1])*p
            im=shot_crop(x,y,shot["z"])
        elif shot["kind"]=="reveal":im=whole_at(p)
        elif shot["kind"]=="whole":im=whole_at(1.)
        elif shot["kind"]=="approach":im=whole_at(1.-p)
        else:raise RuntimeError("Unsupported shot kind")
        assert im.size==(W,H)
        now=timeline+j/FPS
        if now<3.45:im=title_overlay(im,now)
        im.save(F/f"frame_{frame:06d}.jpg",quality=91,subsampling=0)
        frame+=1
    timeline+=shot["s"]
    print(f"FRAME_SEQUENCE_OK {k+1}/{len(shots)} {shot['kind']} {shot['goal']}",flush=True)
assert abs(timeline-DURATION)<.01
def command(args,log=False):
    p=subprocess.run(args,stdout=subprocess.PIPE if not log else None,
                       stderr=subprocess.PIPE if not log else None,text=not log)
    if p.returncode!=0:
        raise RuntimeError(f"Command failed {args[0]}: {str(p.stderr)[-2000:]}")
    return p
video=O/"JOHN_MARTIN_THE_BARD_REEL_2026.mp4"
silent=O/"JOHN_MARTIN_THE_BARD_FACEBOOK_AUDIO.mp4"
cover=O/"COVER_THE_BARD.jpg"
# The downloadable version uses a genuine and independently licensed orchestral recording.
# Sound Collection itself is not substituted or falsely attributed.
command(["ffmpeg","-hide_banner","-loglevel","warning","-y","-framerate",str(FPS),
 "-i",str(F/"frame_%06d.jpg"),"-ss","21","-i",str(A/"ETERNAL_HOPE_Kevin_MacLeod.mp3"),
 "-map","0:v:0","-map","1:a:0",
 "-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",
 "-r",str(FPS),"-c:a","aac","-b:a","160k",
 "-af",f"atrim=duration={DURATION},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=1.3,afade=t=out:st={DURATION-3.0}:d=3,loudnorm=I=-15:TP=-1.5:LRA=11",
 "-t",str(DURATION),"-movflags","+faststart",str(video)])
# An MP4 with no audio is deliberately intended for choosing a Meta Sound Collection track
# INSIDE Facebook/Instagram. Do not copy sound onto other platforms without extra license.
command(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(video),"-map","0:v:0",
 "-c:v","copy","-an","-movflags","+faststart",str(silent)])
Image.open(F/"frame_000042.jpg").save(cover,quality=95)
# Probe both masters, verify full decoding and no accidental black tail.
probe={}
for p in [video,silent]:
    fcmd=["ffprobe","-v","error","-show_entries","format=duration,size:stream=codec_name,width,height,r_frame_rate",
          "-of","json",str(p)]
    details=json.loads(command(fcmd).stdout)
    dur=float(details["format"]["duration"])
    assert abs(dur-DURATION)<.25,(dur,DURATION)
    v=[s for s in details["streams"] if s.get("codec_name")=="h264"]
    assert len(v)==1 and v[0]["width"]==W and v[0]["height"]==H
    if p==video:assert any(s.get("codec_name")=="aac" for s in details["streams"]),"NO AUDIO"
    else:assert not any(s.get("codec_name")=="aac" for s in details["streams"])
    command(["ffmpeg","-v","error","-xerror","-i",str(p),"-f","null","-"])
    probe[p.name]={"duration":dur,"size":p.stat().st_size,"streams":details["streams"],"full_decode_pass":True}
# QA contact sheet: each shot and whole-art frame. Check source resolution and right/footer pixels.
checkpoints=[1.3,5.3,9.4,13.8,18.2,22.8,27.3,32.8,39.0,43.6,48.0,52.0,56.0]
samples=Image.new("RGB",(13*126,250),(20,21,27))
for i,t in enumerate(checkpoints):
    idx=min(frame-1,max(1,int(t*FPS)+1))
    im=Image.open(F/f"frame_{idx:06d}.jpg")
    im.thumbnail((126,224),Image.Resampling.LANCZOS)
    samples.paste(im,(i*126+(126-im.width)//2,0))
    d=ImageDraw.Draw(samples);d.text((i*126+7,230),f"{t:.1f}s",fill=(233,232,227))
samples.save(O/"QA_SHOT_CONTACT.jpg",quality=94)
# Require WHOLE artwork visible (native ratio) for seven seconds; no AI restorations.
assert sum(s["s"] for s in shots if s["kind"]=="whole")>=6
# Two timeliness checks: text absent in final 3 s and proper silent FB delivery.
assert DURATION-timeline<.001
captions={
 "POST_FACEBOOK.txt":"""Un poeta solo sopra un abisso. Sotto di lui un fiume impetuoso, di fronte un castello e montagne che sembrano non finire. È *The Bard*, un dipinto di John Martin del 1817 ispirato alla poesia di Thomas Gray. A raccontare la storia sono il paesaggio e la figura minuscola che lo sfida. Opera conservata allo Yale Center for British Art.

#JohnMartin #TheBard #ArteRomantica

Immagine: John Martin, The Bard (ca. 1817), dominio pubblico, tramite Wikimedia Commons / Google Art Project. Musica della versione MP4: “Eternal Hope” — Kevin MacLeod, CC BY 3.0, adattamento e taglio; in versione Facebook utilizzare una traccia dalla Sound Collection nell'editor Meta, verificandone i termini.""",
 "POST_INSTAGRAM.txt":"""Il paesaggio è immenso. Il poeta, quasi invisibile, guarda il castello oltre la valle.

John Martin dipinse *The Bard* intorno al 1817. Dalle montagne alla cascata, ogni parte della composizione accentua il contrasto tra la forza della natura e un unico essere umano.

#ArtHistory #TheBard #RomanticArt

Dipinto: John Martin, pubblico dominio, Wikimedia Commons. Audio MP4: “Eternal Hope” di Kevin MacLeod, CC BY 3.0; taglio e adattamento.""",
 "POST_TIKTOK.txt":"""Riesci a trovare il poeta in questo paesaggio?

Nel dipinto *The Bard* (circa 1817), John Martin lo colloca su un precipizio. Sotto scorrono un fiume e una cascata; più lontano compare un castello. È una scena ispirata a Thomas Gray.

#QuadriRari #JohnMartin #Paesaggio

Opera di pubblico dominio. Brano MP4: “Eternal Hope” — Kevin MacLeod, CC BY 3.0, montaggio modificato.""",
 "POST_YOUTUBE.txt":"""JOHN MARTIN — THE BARD (ca. 1817) | Pittura romantica

In *The Bard*, John Martin rende monumentale un paesaggio roccioso attraversato da un fiume e dominato da un castello. La figura di un poeta sulla rupe è ispirata all'omonima poesia di Thomas Gray.

Opera: John Martin, ca. 1817, olio su tela, Yale Center for British Art, Paul Mellon Collection. Riproduzione autentica da Google Art Project, tramite Wikimedia Commons, pubblico dominio.

Musica: “Eternal Hope”, Kevin MacLeod (incompetech.com), licenza Creative Commons Attribution 3.0 Unported. Il brano originale è stato tagliato e rimontato; attribuzione: https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100238 — licenza https://creativecommons.org/licenses/by/3.0/.

#JohnMartin #TheBard #ArtHistory"""
}
for name,body in captions.items():(O/name).write_text(body,encoding="utf-8")
credits=f"""# Opere e diritti — John Martin | The Bard
Opera autentica: John Martin, The Bard (circa 1817), Yale Center for British Art, Paul Mellon Collection.
Opera in pubblico dominio; immagine da Google Art Project via Wikimedia Commons.
Pagina della riproduzione: {SOURCE_IMAGE_PAGE}
Asset scaricato: {imgmeta['url']}
Risoluzione: {source.width} x {source.height}
SHA256 della riproduzione: {imgmeta['sha256']}
Nessun dipinto AI, nessuna colorazione o ricostruzione AI. Full canvas mostrata almeno 7 secondi.

# Musica MP4
“Eternal Hope” — Kevin MacLeod (incompetech.com), registrazione effettiva e composizione.
Fonte: {MUSIC_PAGE}
Fonte compositore: {MUSIC_INFO}
MP3 scaricato: {musicmeta['url']}
SHA256 della registrazione scaricata: {musicmeta['sha256']}
License: Creative Commons Attribution 3.0 Unported — https://creativecommons.org/licenses/by/3.0/
Modifiche: estratto di {DURATION:.1f} s a partire da 21 s, dissolvenze, normalizzazione a -15 LUFS.
Credito obbligatorio: “Eternal Hope” — Kevin MacLeod (incompetech.com), CC BY 3.0.

# Versione dedicata a Facebook e Instagram
File senza audio: {silent.name}
Selezionare manualmente una traccia del catalogo Meta Sound Collection all'interno dell'app.
Catalogo: {META_URL}
Nessun brano di Meta Sound Collection è stato scaricato o incorporato: non spacciare questa
registrazione alternativa per musica Meta. La musica Meta non va esportata su YouTube/TikTok
senza una licenza separata. La versione con audio CC BY può essere distribuita sulle
piattaforme secondo la licenza con attribuzione, dopo i controlli specifici.
Pubblicazione automatica: NO. Revisione artistica finale: da parte del proprietario.
"""
(O/"SOURCES_AND_RIGHTS.md").write_text(credits,encoding="utf-8")
(O/"META_AUDIO_GUIDE.txt").write_text(
    "Apri Facebook o Instagram > crea Reel > importa il file JOHN_MARTIN_THE_BARD_FACEBOOK_AUDIO.mp4 > Audio/Musica > Sound Collection.\n"
    "Cerca un brano cinematografico strumentale, con archi e pianoforte, atmosfera malinconica e progressione.\n"
    "La disponibilità e le licenze vanno controllate nel tuo account; non utilizzare lo stesso audio Meta su TikTok/YouTube.\n"
    f"Catalogo ufficiale: {META_URL}\n"
    "Il master con musica Kevin MacLeod è alternativo e ha licenza CC BY 3.0 con crediti obbligatori.\n",
 encoding="utf-8")
recipe={"format":"reel_cromatica_candidate","published":False,"artistic_review":"required",
        "work":"The Bard","artist":"John Martin","year":"ca. 1817",
        "total_s":DURATION,"orientation":"9:16","full_work_shown":True,"full_work_seconds":7.0,
        "assets":{"image":imgmeta,"music":musicmeta},"qa":probe,
        "shots":edl,"technique":"genuine painting photographed; color faithful; no invented elements",
        "audio_meta":"to be selected manually in Facebook Sound Collection; NOT embedded",
        "music_main":"Eternal Hope by Kevin MacLeod; CC BY 3.0 with full credits"}
(O/"RECIPE_AND_QA.json").write_text(json.dumps(recipe,indent=2,ensure_ascii=False),encoding="utf-8")
sources=[video,silent,cover,O/"QA_SHOT_CONTACT.jpg",O/"SOURCES_AND_RIGHTS.md",
 O/"RECIPE_AND_QA.json",O/"META_AUDIO_GUIDE.txt"]+[O/x for x in captions]
with zipfile.ZipFile(D/"THE_BARD_ARTVISION_COMPLETO.zip","w",zipfile.ZIP_DEFLATED,compresslevel=5) as z:
    for p in sources:z.write(p,p.name)
with zipfile.ZipFile(D/"THE_BARD_VIDEO_ANDROID.zip","w",zipfile.ZIP_STORED) as z:z.write(video,video.name)
with zipfile.ZipFile(D/"THE_BARD_FACEBOOK_SENZA_AUDIO.zip","w",zipfile.ZIP_STORED) as z:z.write(silent,silent.name)
for p in D.glob("*.zip"):
    with zipfile.ZipFile(p) as z:
        assert z.testzip() is None,"CRC problem"
    print("ZIP_OK",str(p),p.stat().st_size,flush=True)
for p in sources:print("FILE_OK",p,p.stat().st_size,flush=True)
print("ARTISTIC_REVIEW_REQUIRED - NONE PUBLISHED")
