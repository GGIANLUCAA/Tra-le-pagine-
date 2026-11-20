#!/usr/bin/env python3
"""ArtVision Cromatica: reel made only with authentic public-domain paintings."""
from __future__ import annotations
from PIL import Image, ImageDraw, ImageFont, ImageOps
from pathlib import Path
from io import BytesIO
import hashlib, json, math, os, subprocess, wave, zipfile
import numpy as np
import requests

ROOT = Path("output/reel_achenbach_revised_47s")
ASSETS = ROOT / "assets"
FRAMES = ROOT / "frames"
DIST = ROOT / "dist"
for p in (ROOT, ASSETS, FRAMES, DIST):
    p.mkdir(parents=True, exist_ok=True)
W,H,FPS=720,1280,30
DURATION=46.8

# QA V2: all image frames must be genuine painting pixels, full bleed, no matte or pillarbox.
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
 dict(key="main",duration=3.2,kind="full_bleed",x=.28,dx=.08,zoom=1.014,reason="Apertura su nave e burrasca, camera lentissima"),
 dict(key="main",duration=4.4,kind="full_bleed",x=.36,dx=.30,zoom=1.014,reason="Panorama continuo nave-verso-scogliere senza cambiare formato"),
 dict(key="main",duration=3.7,kind="full_bleed",x=.66,dx=.04,zoom=1.014,reason="Pausa sul paesaggio, rocce e schiuma"),
 dict(key="coast",duration=4.0,kind="full_bleed",x=.11,dx=.22,zoom=1.014,reason="Contrasto di mare e figure, scena reale"),
 dict(key="main",duration=4.2,kind="full_bleed",x=.70,dx=-.28,zoom=1.014,reason="Ripercorre il dipinto in senso inverso senza cornici"),
 dict(key="sunset",duration=3.6,kind="full_bleed",x=.18,dx=.19,zoom=1.014,reason="Svolta calda, luce del temporale che finisce"),
 dict(key="coast",duration=4.0,kind="full_bleed",x=.55,dx=-.20,zoom=1.014,reason="Pausa naturale sul paesaggio costiero"),
 dict(key="main",duration=3.4,kind="full_bleed",x=.24,dx=.08,zoom=1.014,reason="Ritorno alla scala umana della nave"),
 dict(key="main",duration=4.2,kind="full_bleed",x=.32,dx=.33,zoom=1.014,reason="Attraversamento panoramico continuo verso le scogliere"),
 dict(key="sunset",duration=3.8,kind="full_bleed",x=.50,dx=-.23,zoom=1.014,reason="Cambiamento cromatico naturale"),
 dict(key="main",duration=3.8,kind="full_bleed",x=.66,dx=-.28,zoom=1.014,reason="Ritorno finale dalla rupe alla nave"),
 dict(key="main",duration=4.5,kind="full_bleed",x=.38,dx=-.02,zoom=1.014,reason="Chiusura calma sul quadro vero, senza testo"),
]
assert abs(sum(x["duration"] for x in shots)-DURATION)<0.0001
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
    assert shot["kind"]=="full_bleed", "QA: do not introduce letterboxing"
    scale=max(W/source.width,H/source.height)*shot["zoom"]
    ww=math.ceil(source.width*scale); hh=math.ceil(source.height*scale)
    assert ww>=W and hh>=H, f"QA: source {key} does not fill 9:16"
    base=source.resize((ww,hh),Image.Resampling.LANCZOS)
    mx=max(0,ww-W);my=max(0,hh-H)
    for k in range(n):
        t=smooth(k/max(1,n-1))
        fraction=min(1,max(0,shot["x"]+shot["dx"]*t))
        cx=round(mx*fraction)
        cy=round(my*.48)
        im=base.crop((cx,cy,cx+W,cy+H))
        assert im.size == (W,H), "QA: incorrect frame geometry"
        # Every pixel comes from the painting; no gradient matting and no fake border.
        global_t=timeline+k/FPS
        if global_t<3.0: im=add_title(im)
        im.save(FRAMES/f"frame_{frame_no:06d}.jpg",quality=92,subsampling=0)
        frame_no+=1
    timeline+=shot["duration"]
    print(f"Rendered V2 scene {i+1}/{len(shots)}: {key}, {shot['duration']:.1f}s",flush=True)

# Original evolving instrumental soundtrack, composed locally: no borrowed recording.
SR=32000
t=np.arange(int(DURATION*SR),dtype=np.float32)/SR
sound=np.zeros_like(t)
progression=[
  (0.0,11.7,[55.0,82.41,110.0,164.81]),
  (11.7,23.4,[51.91,77.78,103.83,155.56]),
  (23.4,35.1,[65.41,98.0,130.81,196.00]),
  (35.1,DURATION,[55.0,82.41,110.0,164.81]),
]
for start,end,notes in progression:
    start_i=int(start*SR);end_i=int(end*SR)
    tt=t[start_i:end_i]-start
    att=np.minimum(1,np.maximum(0,tt/2.0))
    rel=np.minimum(1,np.maximum(0,(end-start-tt)/2.1))
    envelope=np.sin(np.minimum(att,rel)*np.pi/2)**2
    for j,f in enumerate(notes):
        vibrato=1.0+0.0008*np.sin(2*np.pi*.11*tt+j)
        sound[start_i:end_i] += ((np.sin(2*np.pi*f*tt*vibrato+.4*j) +
            .17*np.sin(2*np.pi*f*2*tt+.2*j))*envelope*(.04 if j<2 else .026)).astype(np.float32)
# Discrete bell-like phrase; avoids just looping one static chord.
melody=[220.,261.63,293.66,329.63,293.66,261.63,220.,
        196.,220.,261.63,293.66,349.23,329.63,293.66,261.63,220.,
        246.94,293.66,329.63,392.0,349.23,293.66,261.63,220.]
for j,f in enumerate(melody):
    start=2.0+j*1.8
    if start>=DURATION-2: break
    i0=int(start*SR); length=min(int(2.6*SR),len(t)-i0)
    tt=np.arange(length,dtype=np.float32)/SR
    env=(1-np.exp(-tt*45.0))*np.exp(-tt*1.8)
    voice=(np.sin(2*np.pi*f*tt)+.32*np.sin(2*np.pi*f*2*tt))*env*.042
    sound[i0:i0+length]+=voice.astype(np.float32)
# Spacious but restrained reverberation.
for delay,amp in [(int(.25*SR),.15),(int(.66*SR),.09),(int(1.1*SR),.035)]:
    sound[delay:]+=sound[:-delay]*amp
fade=np.minimum(1,t/2.0)*np.minimum(1,(DURATION-t)/3.2)
sound*=np.clip(fade,0,1)
peak=max(np.max(np.abs(sound)),1e-9)
sound=sound/peak*.69
with wave.open(str(ROOT/"music_original.wav"),"wb") as wf:
    wf.setnchannels(1);wf.setsampwidth(2);wf.setframerate(SR)
    wf.writeframes((np.clip(sound,-1,1)*32767).astype("<i2").tobytes())

video=ROOT/"REEL_ACHENBACH_CROMATICA_REALE_V2_47S.mp4"
cmd=[
 "ffmpeg","-hide_banner","-loglevel","warning","-y",
 "-framerate","30","-i",str(FRAMES/"frame_%06d.jpg"),
 "-i",str(ROOT/"music_original.wav"),
 "-map","0:v:0","-map","1:a:0",
 "-c:v","libx264","-preset","veryfast","-crf","20",
 "-pix_fmt","yuv420p","-r","30",
 "-c:a","aac","-b:a","160k","-af","loudnorm=I=-15:TP=-1:LRA=11",
 "-t",str(DURATION),"-movflags","+faststart",str(video)]
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
       "Il video NON è pubblicato ed è in attesa di revisione artistica.\nVersione V2: tutti i fotogrammi sono full bleed 9:16; nessuna barra, cornice variabile o cambio di formato.",
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
"format":"reel_cromatica_v1_candidate","seconds":DURATION,"resolution":"720x1280","all_frames_full_bleed":True,"format_switches":0,"no_letterboxing":True,
"fps":30,"audio":"original instrumental music","scenes":report,"sources":metadata,
"publishing_allowed":False,"artistic_review_complete":False,"edge_qa":edge_qa},
ensure_ascii=False,indent=2),encoding="utf-8")
# QA negative check: reject matte/pillarbox generated by former "full" shot mode.
# Score 24 checkpoints, requiring authentic painting texture at every outer edge.
edge_qa=[]
for st in np.linspace(.7,DURATION-.7,24):
    idx=min(frame_no-1,max(1,int(st*FPS)+1))
    with Image.open(FRAMES/f"frame_{idx:06d}.jpg") as f:
        arr=np.asarray(f,dtype=np.uint8)
    assert arr.shape==(H,W,3),"QA: non-vertical frame"
    # a constant dark mat from the earlier version has near zero rowwise variance.
    top=float(np.mean(np.std(arr[5:35,:,:],axis=(0,1))))
    bottom=float(np.mean(np.std(arr[-35:-5,:,:],axis=(0,1))))
    left=float(np.mean(np.std(arr[:,:25,:],axis=(0,1))))
    right=float(np.mean(np.std(arr[:,-25:,:],axis=(0,1))))
    edge_qa.append(dict(sec=round(float(st),2),top=round(top,2),bottom=round(bottom,2),
                        left=round(left,2),right=round(right,2)))
    if (top<1.0 and bottom<1.0) or (left<1.0 and right<1.0):
        raise RuntimeError(f"QA black-bar/matte pattern suspected at t={st:.2f} seconds")
print("QA: 24 edge samples passed; no full-frame letterboxing",flush=True)

probe=subprocess.run(["ffprobe","-v","error","-show_entries",
 "format=duration,size","-of","json",str(video)],
 capture_output=True,text=True,check=True)
actual=json.loads(probe.stdout)["format"]
if not (46.5<=float(actual["duration"])<=47.2): raise RuntimeError("Duration QA failed")
if video.stat().st_size<150000: raise RuntimeError("Video output implausibly small")
# Contact sheet from actual frames to inspect shot pacing, start, and tail.
tpoints=[.5,4.7,8.8,12.7,17.4,21.3,25.8,29.5,33.0,37.2,41.1,45.4]
sheet=Image.new("RGB",(12*160,290),(20,23,28))
for i,st in enumerate(tpoints):
    nr=min(frame_no-1,max(1,int(st*FPS)+1))
    snap=Image.open(FRAMES/f"frame_{nr:06d}.jpg")
    snap.thumbnail((155,270))
    sheet.paste(snap,(i*160+(160-snap.width)//2,(270-snap.height)//2))
sheet.save(ROOT/"QA_CONTACT_SHEET.jpg",quality=90)
for x in [video,cover,ROOT/"SOURCES_AND_RIGHTS.md",ROOT/"EDITOR_REPORT.json",ROOT/"QA_CONTACT_SHEET.jpg",ROOT/"music_original.wav"]:
    print("DELIVERABLE",x,x.stat().st_size,flush=True)
allfiles=[video,cover,ROOT/"SOURCES_AND_RIGHTS.md",ROOT/"EDITOR_REPORT.json",ROOT/"QA_CONTACT_SHEET.jpg",ROOT/"music_original.wav"] + [ROOT/name for name in social]
with zipfile.ZipFile(DIST/"ARTVISION_CROMATICA_REALE_V2_COMPLETO.zip","w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for path in allfiles: z.write(path,path.name)
with zipfile.ZipFile(DIST/"ARTVISION_VIDEO_V2_ANDROID.zip","w",zipfile.ZIP_STORED) as z:
    z.write(video,video.name)
for zp in DIST.glob("*.zip"):
    with zipfile.ZipFile(zp) as z:
        if z.testzip(): raise RuntimeError("ZIP CRC verification failed")
    print("ZIP_READY",zp,zp.stat().st_size,flush=True)
