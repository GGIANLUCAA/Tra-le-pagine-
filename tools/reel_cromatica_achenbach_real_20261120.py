#!/usr/bin/env python3
"""ArtVision Cromatica: reel made only with authentic public-domain paintings."""
from __future__ import annotations
from PIL import Image, ImageDraw, ImageFont, ImageOps
from pathlib import Path
from io import BytesIO
import hashlib, json, math, os, subprocess, wave, zipfile
import numpy as np
import requests

ROOT = Path("output/reel_achenbach_real")
ASSETS = ROOT / "assets"
FRAMES = ROOT / "frames"
DIST = ROOT / "dist"
for p in (ROOT, ASSETS, FRAMES, DIST):
    p.mkdir(parents=True, exist_ok=True)
W,H,FPS=720,1280,30
USER_AGENT = "ArtVisionMuseumResearch/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-)"
PAINTINGS = {
    "main": dict(title="Storm at Sea off the Norwegian Coast",year=1837,artist="Andreas Achenbach",
       page="https://sammlung.staedelmuseum.de/en/work/storm-at-sea-off-the-norwegian-coast",
       license="Public Domain (painting and Stadel image)",
       urls=[
          "https://upload.wikimedia.org/wikipedia/commons/8/86/MK_17354_Andreas_Achenbach-Ein_Seesturm_an_der_norwegischen_K%C3%BCste.jpg",
          "https://cdn.staedelmuseum.de/images/44/cc/875/thumb-xl.jpg",
       ]),
    "sunset": dict(title="Sunset after a Storm on the Coast of Sicily",year=1853,artist="Andreas Achenbach",
       page="https://www.metmuseum.org/art/collection/search/437975",
       license="Public Domain / The Metropolitan Museum of Art Open Access",
       urls=[
         "https://collectionapi.metmuseum.org/api/collection/v1/iiif/437975/2268027/main-image",
       ]),
    "coast": dict(title="Storm at the Coast",year=1855,artist="Andreas Achenbach",
       page="https://commons.wikimedia.org/wiki/File:Andreas_Achenbach_-_Storm_at_the_Coast_-_NG.M.00228_-_National_Museum_of_Art,_Architecture_and_Design.jpg",
       license="Painting public domain; digitized image CC BY 4.0, National Museum Norway",
       urls=[
         "https://upload.wikimedia.org/wikipedia/commons/9/97/Andreas_Achenbach_-_Storm_at_the_Coast_-_NG.M.00228_-_National_Museum_of_Art%2C_Architecture_and_Design.jpg",
       ]),
}
session=requests.Session()
session.headers.update({"User-Agent": USER_AGENT,"Accept":"image/jpeg,image/png,image/*;q=0.9,*/*;q=0.3"})
images={}
metadata=[]
for key, spec in PAINTINGS.items():
    got=False
    for url in spec["urls"]:
        try:
            r=session.get(url, timeout=45)
            r.raise_for_status()
            data=r.content
            if len(data)<15000: raise RuntimeError("Image unusually small")
            im=ImageOps.exif_transpose(Image.open(BytesIO(data))).convert("RGB")
            if im.width < 720 or im.height < 450: raise RuntimeError("Insufficient image size")
            path=ASSETS / (key + ".jpg")
            im.save(path, quality=94,subsampling=0)
            images[key]=im
            metadata.append({k:spec[k] for k in ("title","year","artist","page","license")} |
                {"actual_download_url":url,"pixels":[im.width,im.height],
                 "sha256":hashlib.sha256(data).hexdigest(),"asset":str(path)})
            print(f"Verified {key}: {im.width}x{im.height} {len(data)} bytes {url}",flush=True)
            got=True
            break
        except Exception as exc:
            print(f"Source attempt failed for {key}: {str(exc)[:140]}",flush=True)
    if key=="main" and not got: raise SystemExit("BLOCKER: authentic MAIN painting unavailable")
    if not got: print(f"Optional supporting painting {key} unavailable; main preserved",flush=True)
# The video will never fall back to AI content.
def choose(key):
    if key in images: return key
    return "main"
shots=[
 dict(key="main",duration=2.1,kind="detail",x=.20,dx=.045,zoom=1.04,reason="La nave tra le onde, apertura"),
 dict(key="main",duration=3.2,kind="full",reason="Mostrare il quadro e tutto il paesaggio"),
 dict(key="main",duration=2.4,kind="detail",x=.75,dx=-.07,zoom=1.15,reason="Rocce e schiuma a destra"),
 dict(key="coast",duration=3.1,kind="detail",x=.37,dx=.055,zoom=1.04,reason="Contrasto con altra costa autentica"),
 dict(key="sunset",duration=3.4,kind="detail",x=.66,dx=-.07,zoom=1.03,reason="La luce ritorna, secondo paesaggio"),
 dict(key="main",duration=2.6,kind="detail",x=.41,dx=.06,zoom=1.12,reason="Il frangersi delle onde"),
 dict(key="main",duration=3.4,kind="full",reason="Respiro, opera intera"),
 dict(key="sunset",duration=2.9,kind="full",reason="La luce nel paesaggio intero"),
 dict(key="main",duration=2.9,kind="full",reason="Chiusura sull'opera originale, senza testo"),
]
assert abs(sum(x["duration"] for x in shots)-26.0)<0.0001
FONT_REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
f1=ImageFont.truetype(FONT_BOLD,35); f2=ImageFont.truetype(FONT_REG,27); f3=ImageFont.truetype(FONT_REG,21)

def smooth(t): return t*t*(3-2*t)
def gradient():
    canvas=Image.new("RGB",(W,H))
    pix=ImageDraw.Draw(canvas)
    for y in range(H):
        q=y/(H-1)
        pix.line([(0,y),(W,y)],fill=(int(15+10*q),int(22+11*q),int(33+13*q)))
    return canvas
bg=gradient()
def add_title(im):
    draw=ImageDraw.Draw(im)
    lines=[
       ("IL MARE SENZA PIETÀ",f1, "#FFFFFF","#05080D",(31,527,689,608)),
       ("Andreas Achenbach",f2,"#0B1020","#FFFFFF",(69,623,651,681)),
       ("Germania · 1837",f3,"#0B1020","#FFFFFF",(209,695,511,746)),
    ]
    for title,font,textcol,fill,box in lines:
        draw.rounded_rectangle(box,radius=8,fill=fill)
        bounds=draw.textbbox((0,0),title,font=font)
        tx=(W-(bounds[2]-bounds[0]))/2
        ty=(box[1]+box[3]-(bounds[3]-bounds[1]))/2-bounds[1]
        draw.text((int(tx),int(ty)),title,font=font,fill=textcol)
    # Genuine German flag made of three colored bars, avoiding missing emoji font glyphs.
    for c,yy in (("#000000",708),("#DD0000",716),("#FFCE00",724)):
        draw.rectangle((477,yy,496,yy+7),fill=c)
    return im

frame_no=1
timeline=0.
report=[]
for i,shot in enumerate(shots):
    key=choose(shot["key"])
    source=images[key]
    n=round(shot["duration"]*FPS)
    entry={**shot,"resolved_source":key,"start":round(timeline,2),"end":round(timeline+shot["duration"],2),"frames":n}
    report.append(entry)
    if shot["kind"]=="detail":
        scale=(H*shot["zoom"])/source.height
        ww=math.ceil(source.width*scale); hh=math.ceil(source.height*scale)
        if ww<W or hh<H: 
            scale=max(W/source.width,H/source.height)*1.04
            ww=math.ceil(source.width*scale);hh=math.ceil(source.height*scale)
        base=source.resize((ww,hh),Image.Resampling.LANCZOS)
    else:
        # Original entire landscape visible: never crop a ship, cliff or horizon.
        fit=ImageOps.contain(source,(W-8,730),Image.Resampling.LANCZOS)
    for k in range(n):
        t=smooth(k/max(1,n-1))
        if shot["kind"]=="full":
            im=bg.copy()
            # Small, motivated change in framing, while all original painting remains visible.
            z=0.985+0.015*t
            fit_frame=fit.resize((int(fit.width*z),int(fit.height*z)),Image.Resampling.LANCZOS)
            px=(W-fit_frame.width)//2;py=(H-fit_frame.height)//2
            im.paste(fit_frame,(px,py))
        else:
            mx=max(0,ww-W);my=max(0,hh-H)
            fraction=min(1,max(0,shot["x"]+shot["dx"]*t))
            cx=round(mx*fraction)
            cy=round(my*.49)
            im=base.crop((cx,cy,cx+W,cy+H))
        global_t=timeline+k/FPS
        if global_t<4.0: im=add_title(im)
        im.save(FRAMES/f"frame_{frame_no:06d}.jpg",quality=89,subsampling=0)
        frame_no+=1
    timeline+=shot["duration"]
    print(f"Rendered shot {i+1}/9: {key}, {shot['duration']:.1f}s",flush=True)

# Original instrumental score; composed algorithmically, no borrowed recording.
SR=32000
t=np.arange(int(26*SR),dtype=np.float32)/SR
sound=np.zeros_like(t)
progression=[
  (0.0,6.5,[55.0,82.41,110.0,164.81]),
  (6.5,13.0,[51.91,77.78,103.83,155.56]),
  (13.0,19.5,[65.41,98.0,130.81,196.00]),
  (19.5,26.0,[55.0,82.41,110.0,164.81])
]
for start,end,notes in progression:
    start_i=int(start*SR); end_i=int(end*SR)
    tt=t[start_i:end_i]-start
    a=np.minimum(1,np.maximum(0,tt/1.4))
    z=np.minimum(1,np.maximum(0,(end-start-tt)/1.7))
    envelope=np.sin((np.minimum(a,z))*np.pi/2)**2
    for j,f in enumerate(notes):
        wobble=1+0.0014*np.sin(2*np.pi*0.11*tt+j)
        voice=np.sin(2*np.pi*f*tt*wobble+.4*j)+.25*np.sin(2*np.pi*f*2*tt+.2*j)
        sound[start_i:end_i]+=voice.astype(np.float32)*envelope*(.048 if j<2 else .029)
# slow pulse is subtly musical, not a repetitive sound effect
sound*=.75+.25*np.sin(np.pi*np.clip(t/26,0,1))**2
# Reverberation taps give a spacious, cinematic tail
for delay,amp in [(int(.31*SR),.17),(int(.69*SR),.1),(int(1.19*SR),.06)]:
    sound[delay:]+=sound[:-delay]*amp
fade=np.minimum(1,t/1.25)*np.minimum(1,(26-t)/2.6)
sound*=np.clip(fade,0,1)
peak=max(np.max(np.abs(sound)),1e-9)
sound=sound/peak*.72
with wave.open(str(ROOT/"music_original.wav"),"wb") as wf:
    wf.setnchannels(1);wf.setsampwidth(2);wf.setframerate(SR)
    wf.writeframes((np.clip(sound,-1,1)*32767).astype("<i2").tobytes())

video=ROOT/"REEL_ACHENBACH_CROMATICA_REALE.mp4"
cmd=[
 "ffmpeg","-hide_banner","-loglevel","warning","-y",
 "-framerate","30","-i",str(FRAMES/"frame_%06d.jpg"),
 "-i",str(ROOT/"music_original.wav"),
 "-map","0:v:0","-map","1:a:0",
 "-c:v","libx264","-preset","veryfast","-crf","20",
 "-pix_fmt","yuv420p","-r","30",
 "-c:a","aac","-b:a","160k","-af","loudnorm=I=-15:TP=-1:LRA=11",
 "-t","26","-movflags","+faststart",str(video)]
subprocess.run(cmd,check=True)
cover=ROOT/"COVER_ACHENBACH.jpg"
# Native reel frame: title in first two seconds, no invented cover.
Image.open(FRAMES/"frame_000016.jpg").save(cover,quality=93)
print("Video encoded",video,video.stat().st_size,flush=True)

social={
"POST_FACEBOOK.txt":"""Un mare che sembra sul punto di inghiottire tutto. Nel 1837 Andreas Achenbach dipinse Storm at Sea off the Norwegian Coast: una nave minuscola, onde che si infrangono contro le rocce e un cielo che lascia entrare una luce quasi impossibile. La tela misura 179 × 272 cm ed è conservata allo Städel Museum di Francoforte. In questa scena la natura sembra molto più grande dell'uomo.

#AndreasAchenbach #PitturaRomantica #ArteDelMare

Opere: Andreas Achenbach, pubblico dominio. Fonte principale: Städel Museum; immagini aggiuntive accreditate nel documento fonti. Musica strumentale originale di questa produzione.""",
"POST_INSTAGRAM.txt":"""Una nave piccolissima contro una parete di mare e roccia.

Andreas Achenbach dipinse Storm at Sea off the Norwegian Coast nel 1837. Lo sguardo passa dalla schiuma bianca alla cima degli scogli, poi incontra un cielo insolitamente luminoso. Una scena di pericolo, ma anche una straordinaria composizione di luce e movimento.

#Arte #AndreasAchenbach #PaesaggiMarini

Opere di pubblico dominio; riproduzioni e attribuzioni nel documento fonti. Musica strumentale originale.""",
"POST_TIKTOK.txt":"""Quanto può essere piccola una nave davanti al mare?

Nel 1837 Andreas Achenbach dipinse questa tempesta sulla costa norvegese. Guarda le rocce a destra, la schiuma in basso e la barca travolta dalle onde.

Storm at Sea off the Norwegian Coast — Städel Museum.

#ArteNascosta #Tempesta #Achenbach

Opere di pubblico dominio, crediti immagini nel documento fonti. Musica originale.""",
"POST_YOUTUBE.txt":"""ANDREAS ACHENBACH — STORM AT SEA OFF THE NORWEGIAN COAST (1837)

Un grande dipinto romantico di onde, rocce e luce. Una nave cerca di resistere alla furia del mare. L'opera principale è conservata allo Städel Museum di Francoforte, misura 179 × 272 cm ed è di pubblico dominio.

Il video mostra riproduzioni autentiche di opere di Andreas Achenbach; nessun dipinto è stato ricreato con intelligenza artificiale.

#AndreasAchenbach #StormAtSea #ArtHistory

Crediti: Städel Museum e, se presenti, Metropolitan Museum of Art e National Museum Norway. Licenze specifiche nel documento SOURCES_AND_RIGHTS.md. Colonna sonora strumentale originale."""
}
for name,body in social.items(): (ROOT/name).write_text(body,encoding="utf-8")
lines=["# ArtVision · Reel cromatica · fonti e diritti",
       "Questo video impiega ESCLUSIVAMENTE fotografie di quadri storici autentici, nessuna opera generata con AI.",
       "Il dipinto principale è Storm at Sea off the Norwegian Coast (1837), Städel Museum, Francoforte.",
       "Le riprese sono movimenti e ritagli digitali delle opere senza inventare, colorare o alterare le figure.",
       "La musica è una composizione strumentale originale generata per questa produzione.",
       "Il video NON è pubblicato ed è in attesa di revisione artistica.",
       ""]
for m in metadata:
    lines += [f"## {m['title']} ({m['year']})",
       "Artista: Andreas Achenbach",f"Fonte: {m['page']}",
       f"File effettivamente scaricato: {m['actual_download_url']}",
       f"Diritti del file: {m['license']}",
       f"Dimensioni: {m['pixels'][0]} × {m['pixels'][1]} px",
       f"SHA256 file d'origine: {m['sha256']}",""]
(ROOT/"SOURCES_AND_RIGHTS.md").write_text("\n".join(lines),encoding="utf-8")
(ROOT/"EDITOR_REPORT.json").write_text(json.dumps({"status":"rendered_needs_review",
"format":"reel_cromatica_v1_candidate","seconds":26,"resolution":"720x1280",
"fps":30,"audio":"original instrumental music","scenes":report,"sources":metadata,
"publishing_allowed":False,"artistic_review_complete":False},
ensure_ascii=False,indent=2),encoding="utf-8")
probe=subprocess.run(["ffprobe","-v","error","-show_entries",
 "format=duration,size","-of","json",str(video)],
 capture_output=True,text=True,check=True)
actual=json.loads(probe.stdout)["format"]
if not (25.5<=float(actual["duration"])<=26.4): raise RuntimeError("Duration QA failed")
if video.stat().st_size<150000: raise RuntimeError("Video output implausibly small")
# Contact sheet from actual frames to inspect shot pacing, start, and tail.
tpoints=[.5,2.8,5.9,8.9,11.8,14.9,17.7,21.5,24.7]
sheet=Image.new("RGB",(9*160,290),(20,23,28))
for i,st in enumerate(tpoints):
    nr=min(frame_no-1,max(1,int(st*FPS)+1))
    snap=Image.open(FRAMES/f"frame_{nr:06d}.jpg")
    snap.thumbnail((155,270))
    sheet.paste(snap,(i*160+(160-snap.width)//2,(270-snap.height)//2))
sheet.save(ROOT/"QA_CONTACT_SHEET.jpg",quality=90)
for x in [video,cover,ROOT/"SOURCES_AND_RIGHTS.md",ROOT/"EDITOR_REPORT.json",ROOT/"QA_CONTACT_SHEET.jpg",ROOT/"music_original.wav"]:
    print("DELIVERABLE",x,x.stat().st_size,flush=True)
allfiles=[video,cover,ROOT/"SOURCES_AND_RIGHTS.md",ROOT/"EDITOR_REPORT.json",ROOT/"QA_CONTACT_SHEET.jpg",ROOT/"music_original.wav"] + [ROOT/name for name in social]
with zipfile.ZipFile(DIST/"ARTVISION_CROMATICA_REALE_COMPLETO.zip","w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for path in allfiles: z.write(path,path.name)
with zipfile.ZipFile(DIST/"ARTVISION_VIDEO_ANDROID.zip","w",zipfile.ZIP_STORED) as z:
    z.write(video,video.name)
for zp in DIST.glob("*.zip"):
    with zipfile.ZipFile(zp) as z:
        if z.testzip(): raise RuntimeError("ZIP CRC verification failed")
    print("ZIP_READY",zp,zp.stat().st_size,flush=True)
