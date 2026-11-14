#!/usr/bin/env python3
"""ArtVision private Cinema Standard pre-review: Ryder, The Race Track (1928.8).
Original artwork only, no synthesized detail, no voice, no publication. Music V330 is attached by the workflow.
"""
from __future__ import annotations
import hashlib, io, json, os, subprocess, urllib.request, zipfile
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageFilter, ImageEnhance

OUT = Path("output/artvision-owner-ryder-race-track-cinema-v1")
OUT.mkdir(parents=True, exist_ok=True)
API="https://openaccess-api.clevelandart.org/api/artworks/1928.8"
FALLBACK="https://openaccess-cdn.clevelandart.org/1928.8/1928.8_print.jpg"
CMA="https://www.clevelandart.org/art/1928.8"
def fetch(url, max_size=75_000_000):
    req=urllib.request.Request(url, headers={"User-Agent":"ArtVisionResearch/1.0 (private CC0 review; github project)"})
    with urllib.request.urlopen(req,timeout=40) as r:
        data=r.read(max_size+1)
    if len(data)>max_size: raise ValueError("Image exceeds size bound")
    return data
meta=None
url=FALLBACK
try:
    meta=json.loads(fetch(API,3_000_000).decode("utf-8")).get("data",{})
    if str(meta.get("accession_number",""))!="1928.8": raise ValueError("Wrong object")
    if meta.get("share_license_status")!="CC0": raise ValueError("CMA image is not CC0")
    options=meta.get("images") or {}
    url=((options.get("print") or {}).get("url")) or FALLBACK
except ValueError: raise
except Exception as exc:
    print("CMA metadata API not reachable, fallback to official CC0 object print image:",exc)
data=fetch(url)
im=Image.open(io.BytesIO(data)).convert("RGB")
w,h=im.size
if w<900 or h<650 or not 1.1<w/h<1.8: raise ValueError(f"Unexpected painting geometry {w}x{h}")
sha=hashlib.sha256(data).hexdigest()
(OUT/"ORIGINAL_ARTWORK.jpg").write_bytes(data)
print("Verified exact CMA artwork",url,w,h,sha)

W,H=1080,1920
FNT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def font(px,bold=False):
    return ImageFont.truetype(BOLD if bold else FNT,px)
def center_text(draw,text,y,ft,fill):
    bb=draw.textbbox((0,0),text,font=ft)
    draw.text(((W-(bb[2]-bb[0]))/2,y),text,font=ft,fill=fill)
def plate(i,crop,title=None,subtitle=None,end=False):
    backdrop=ImageOps.fit(im,(W,H)).filter(ImageFilter.GaussianBlur(60))
    backdrop=ImageEnhance.Brightness(backdrop).enhance(.24)
    bg=backdrop.copy()
    a,b,c,d=crop
    detail=im.crop((int(w*a),int(h*b),int(w*c),int(h*d)))
    maxbox=(1040,1120 if i not in (0,7) else 825)
    detail.thumbnail(maxbox,Image.Resampling.LANCZOS)
    border=Image.new("RGB",(detail.width+4,detail.height+4),(150,140,110))
    border.paste(detail,(2,2))
    left=(W-border.width)//2
    top=(H-border.height)//2-90
    bg.paste(border,(left,top))
    dr=ImageDraw.Draw(bg)
    if title:
        center_text(dr,"ARTVISION",240,font(34), (214,204,174))
        center_text(dr,title,375,font(68,True),(244,240,228))
        if subtitle:center_text(dr,subtitle,470,font(32),(213,208,191))
    if end:
        center_text(dr,"ALBERT PINKHAM RYDER",1450,font(35,True),(229,223,202))
        center_text(dr,"THE RACE TRACK",1518,font(48,True),(242,238,224))
        center_text(dr,"CLEVELAND MUSEUM OF ART • CC0",1610,font(23),(201,197,177))
    p=OUT/f"SHOT_{i+1:02}.png"
    bg.save(p,optimize=True)
    return p
# Designed explicitly around source artwork geometry; no invented motion/figures.
shots=[
 (0,1.00,(0,0,1,1),"THE RACE TRACK","DEATH ON A PALE HORSE",False),
 (1,1.00,(.25,.25,.72,.74),None,None,False), # rider+horse
 (2,1.00,(0,.08,.66,.63),None,None,False),   # sweeping race track
 (3,1.00,(.14,.47,.70,1),None,None,False),   # foreground snake
 (4,1.00,(.37,.13,1,.75),None,None,False),   # tree, sky, horse
 (5,1.00,(.22,.29,.85,.77),None,None,False), # rider in context
 (6,1.00,(0,0,1,1),None,None,False),         # full painting
 (7,1.00,(0,0,1,1),None,None,True),
]
paths=[plate(i,c,t,s,e) for i,z,c,t,s,e in shots]
# Crossfades, not rigid repeated hard cuts. Very subtle optical push toward genuine artwork only.
duration=[5.0,4.5,4.8,4.8,4.8,4.6,4.8,5.2]
fps=24
cmd=["ffmpeg","-hide_banner","-loglevel","error","-y"]
for p in paths: cmd+=["-loop","1","-framerate",str(fps),"-i",str(p)]
fs=[]
for i,seconds in enumerate(duration):
    count=int(seconds*fps)
    fs.append(f"[{i}:v]trim=duration={seconds},setpts=PTS-STARTPTS,scale=1080:1920,zoompan=z='min(zoom+0.00015,1.020)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps={fps},trim=duration={seconds},setpts=PTS-STARTPTS,fps={fps}[v{i}]")
offset=0
left="v0"
for i in range(1,len(paths)):
    offset += duration[i-1]-(.45 if i>1 else 0)
    label=f"x{i}"
    fs.append(f"[{left}][v{i}]xfade=transition=fade:duration=.45:offset={offset:.2f}[{label}]")
    left=label
cmd+=["-filter_complex",";".join(fs),"-map",f"[{left}]","-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p","-movflags","+faststart",str(OUT/"VIDEO_SILENT_PRIVATE.mp4")]
print("Rendering source-locked private Cinema. No AI generated elements.",flush=True)
subprocess.run(cmd,check=True)
report={
 "schema":"ryder-private-cinema-owner-v1", "title":"The Race Track (Death on a Pale Horse)", "artist":"Albert Pinkham Ryder", "year":"c. 1896-1908",
 "museum":"Cleveland Museum of Art", "object_id":"1928.8", "official_object_url":CMA,
 "source_image_url":url, "source_pixels":[w,h], "source_sha256":sha,
 "rights":"Cleveland Museum of Art Open Access CC0 for exact source; museum name is a credit, not an endorsement.",
 "source_exact_reused":True, "synthesized_subjects":False, "output_status":"PRIVATE_CINEMA_STANDARD_TECHNICAL_REVIEW_MUSIC_PENDING",
 "voice":"None; Cinema Standard format only. Critico awaits approved Google Gemini Gacrux.", "gallery_museum":"Not a Museum video; no synthetic museum claimed",
 "music_policy":"One of 20 verified original MP3 from V330 applied by workflow; no temporary synthesized substitute",
 "social_hook":"Perché la Morte corre su una pista deserta?", "publication":False, "gold":False,
 "artistic_review":"PENDING", "auto_paid_api_calls":0, "variant":"cinema_standard",
 "frame_stages":["opening full","rider","track","snake foreground","storm sky","rider context","full","end full"]
}
(OUT/"SOURCES_RIGHTS.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
(OUT/"SOCIAL_COPY.txt").write_text(
    "THE RACE TRACK — Albert Pinkham Ryder (c. 1896–1908)\n\n"
    "Una corsa senza pubblico. Un cavaliere impossibile. E un serpente quasi invisibile."
    " Ryder trasformò una pista in un'allegoria inquietante.\n\n"
    "Opera: Cleveland Museum of Art, 1928.8, Open Access CC0.\n"
    "Musica: verificare il titolo e i crediti reali dal report V330 prima di pubblicare.\n"
    "Stato: anteprima privata in revisione, non pubblicata.\n#ArtVision #ArtHistory #Ryder #MuseumArt\n",encoding="utf-8")
Image.open(paths[0]).save(OUT/"COVER.jpg",quality=92)
(OUT/"STORYBOARD.json").write_text(json.dumps({"shots":[{"index":i+1,"duration_s":duration[i],"crop":list(shots[i][2])} for i in range(len(shots))],"transition":"45-frame? No: .45s soft dissolve","voice":"none","note":"Slight optical motion only; visual attention follows source painting; no generated actors."},indent=2),encoding="utf-8")
