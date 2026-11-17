#!/usr/bin/env python3
"""Owner 17 Nov 2026: second distinct source-gated Salvator Rosa Cinema Standard.
Authentic museum painting, quiet human-paced shots, no fake frames/voice/Gold.
Private review only. No paid API, no publication.
"""
from __future__ import annotations
import hashlib
import io
import json
import subprocess
import time
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "artvision-extra-salvator-rosa-witchcraft-evening-v1"
OUT.mkdir(parents=True, exist_ok=True)
ARTIST = "Salvator Rosa"
TITLE = "Scenes of Witchcraft: Evening"
ACCESSION = "1977.37.3"
OFFICIAL = "https://www.clevelandart.org/art/1977.37.3"
SOURCES = [
    ("CMA_OPEN_ACCESS_CDN", "https://openaccess-cdn.clevelandart.org/1977.37.3/1977.37.3_print.jpg"),
    ("WIKIMEDIA_COMMONS_CMA_CC0", "https://commons.wikimedia.org/wiki/Special:Redirect/file/Clevelandart_1977.37.3.jpg"),
]
EXPECTED_COMMONS_SHA1 = "c76bc6320217f9c901247331214d4c34081c06b9"

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1024*1024), b""):
            h.update(b)
    return h.hexdigest()

def cmd(args: list[str], *, timeout=600):
    p = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    if p.returncode:
        raise RuntimeError("Command failed: " + " ".join(args[:8]) + "\n" + p.stderr[-2500:])
    return p.stdout

def dedup_gate():
    path = ROOT / "data" / "archivio-generale" / "opere.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    existing = [w for w in data.get("works", [])
                if w.get("artist","").casefold() == ARTIST.casefold()
                and w.get("title","").casefold() == TITLE.casefold()]
    for w in existing:
        states = [v.get("state") for v in w.get("variants", {}).values()]
        if "render_documentato" in states:
            raise ValueError("ANTI_DUPLICATE_EXISTING_RENDER_DOCUMENTED " + TITLE)
    for f in (ROOT / "queue").glob("artvision_extra_render_checkpoint_*salvator*rosa*evening*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        if d.get("status") not in ("AUTHORIZED_EDITORIALLY_PREFLIGHT_ONLY_NO_MP4",
                                   "PRE_RENDER_NO_MP4", "RENDER_FAILED_NO_MP4"):
            raise ValueError("ANTI_DUPLICATE_NEWER_CHECKPOINT " + str(f))
    print("UNIQUE_SLOT_GATE_PASS")

def get_authentic_painting():
    errors = []
    for source, url in SOURCES:
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "ArtVision-SourceValidation/1.0 (museum artwork review)",
                "Accept": "image/jpeg,image/png,image/*;q=0.8,*/*;q=0.1"})
            with urllib.request.urlopen(req, timeout=35) as response:
                content = response.read(30_000_001)
                final_url = response.geturl()
                content_type = response.headers.get("Content-Type","")
            if len(content) > 30_000_000 or len(content) < 150_000:
                raise ValueError("File size out of safe range " + str(len(content)))
            if "image" not in content_type and content[:3] != b"\xff\xd8\xff":
                raise ValueError("Not an image response: " + content_type)
            if source == "WIKIMEDIA_COMMONS_CMA_CC0":
                actual_sha1 = hashlib.sha1(content).hexdigest()
                if actual_sha1 != EXPECTED_COMMONS_SHA1:
                    raise ValueError("Commons published SHA1 mismatch " + actual_sha1)
            picture = Image.open(io.BytesIO(content))
            picture.verify()
            picture = Image.open(io.BytesIO(content)).convert("RGB")
            w,h = picture.size
            if w < 2500 or h < 2500 or w*h > 75_000_000:
                raise ValueError("Original pixels insufficient or unreasonable: " + str((w,h)))
            out = OUT / "ORIGINAL_ARTWORK.jpg"
            out.write_bytes(content)
            (OUT / "SOURCES_RIGHTS.json").write_text(json.dumps({
                "artwork": TITLE, "artist": ARTIST, "year": "c. 1645–49",
                "museum": "The Cleveland Museum of Art", "accession": ACCESSION,
                "official_object": OFFICIAL,
                "rights": "Cleveland Museum of Art Open Access, CC0",
                "rights_primary_url": "https://www.clevelandart.org/open-access",
                "license_status": "MUSEUM_OBJECT_CC0_RUNTIME_IMAGE_BINARY_VERIFIED",
                "source_kind": source, "source_url": url, "final_url": final_url,
                "source_bytes": len(content), "source_pixels": [w,h],
                "source_sha256": sha256(out), "source_sha1": hashlib.sha1(content).hexdigest(),
                "licensing_notes": "CMA official object page explicitly permits copy/modify/distribute. If Commons source, exact known CMA file SHA1 is checked.",
                "cinema_variant": "cinema_standard", "production_review": "TECHNICAL_PENDING",
                "artistic_review": "PENDING", "published": False, "gold": False,
                "paid_api": False, "tts": "none"
            }, indent=2),encoding="utf-8")
            print("AUTHENTIC_SOURCE_VERIFIED",source,(w,h),len(content),sha256(out))
            return picture
        except Exception as e:
            errors.append(source + ": " + repr(e))
            print("SOURCE_STRATEGY_FAILED", errors[-1])
            time.sleep(1)
    raise RuntimeError("BOTH_FREE_IMAGE_STRATEGIES_FAILED\n" + "\n".join(errors))

def font(sz:int, bold:bool=False):
    names = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
             "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"]
    for p in names:
        if Path(p).exists():
            return ImageFont.truetype(p,sz)
    return ImageFont.load_default()

# 11 shots: no split screen, no fake elements, never < 3 s.
SHOTS = [
    ("The entire circular composition", (0,0,1,1), 4.0, "A SPELL IN THE DARK", True),
    ("The gathering of witches", (.02,.35,.62,.98), 3.0, "THREE FIGURES GATHER", False),
    ("The fire at the cauldron", (.10,.45,.66,.99), 3.0, "FIRE LIGHTS THE CAULDRON", False),
    ("The witch stirring the cauldron", (.04,.38,.56,.91), 3.0, "THE POTION TAKES SHAPE", False),
    ("The hovering skeletal apparition", (.31,.03,.97,.70), 3.0, "ABOVE THEM: A SKELETON", False),
    ("The hourglass", (.40,.04,.95,.56), 3.0, "AN HOURGLASS: TIME RUNS OUT", False),
    ("The nocturnal landscape", (.12,.01,.98,.70), 3.0, "THE MOON WATCHES", False),
    ("The group below the apparition", (.04,.28,.98,.96), 3.0, "PAINTED FEAR, NOT A REAL RITUAL", False),
    ("Close detail of light and shadow", (.08,.43,.80,.98), 3.0, "ROSA PAINTS WITH FIRE", False),
    ("Return to the complete tondo", (0,0,1,1), 3.0, "A CIRCLE OF EVENINGMARES", False),
    ("Final complete painting", (0,0,1,1), 4.0, "SALVATOR ROSA · 1645–49", False),
]

def plate(img:Image.Image, rect, caption, opener, index):
    W,H = 1080,1920
    dim = ImageOps.fit(img,(W,H),method=Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(55))
    canvas = Image.blend(dim,Image.new("RGB",(W,H),(9,11,18)),.82)
    x0,y0,x1,y1 = rect
    iw,ih = img.size
    crop = img.crop((int(x0*iw),int(y0*ih),int(x1*iw),int(y1*ih)))
    art = ImageOps.contain(crop,(1020,1140),method=Image.Resampling.LANCZOS)
    x = (W-art.width)//2
    y = 310 + (1140-art.height)//2
    dr = ImageDraw.Draw(canvas)
    dr.rounded_rectangle((x-8,y-8,x+art.width+8,y+art.height+8),
                         radius=9,fill=(17,17,23),outline=(74,69,59),width=3)
    canvas.paste(art,(x,y))
    dr = ImageDraw.Draw(canvas)
    dr.text((W//2,115), "ARTVISION · CINEMA", font=font(25,True),
            fill=(202,183,142),anchor="mm",stroke_width=0)
    if opener:
        dr.text((W//2,200),"THE EVENING OF",font=font(55,True),
                fill=(248,240,220),anchor="mm")
        dr.text((W//2,267),"WITCHCRAFT",font=font(57,True),
                fill=(248,240,220),anchor="mm")
    else:
        dr.text((W//2,213),"SCENES OF WITCHCRAFT: EVENING",
                font=font(32,True),fill=(242,232,211),anchor="mm")
    dr.text((W//2,1530),caption,font=font(32,True),
            fill=(239,233,214),anchor="mm")
    dr.line((270,1598,810,1598), fill=(175,151,100), width=2)
    dr.text((W//2,1655),"Salvator Rosa  ·  Cleveland Museum of Art",
            font=font(24),fill=(184,190,190),anchor="mm")
    dr.text((W//2,1720),"Original painting · CC0 · 1977.37.3",
            font=font(20),fill=(137,147,147),anchor="mm")
    return canvas

def render(img):
    plates = OUT / "plates"
    plates.mkdir(exist_ok=True)
    clips = OUT / "clips"
    clips.mkdir(exist_ok=True)
    storyboard = []
    t=0.0
    concat_lines=[]
    for i, (description,box,seconds,caption,opener) in enumerate(SHOTS,1):
        plate_file=plates / ("scene_%02d.jpg"%i)
        shot=plate(img,box,caption,opener,i)
        shot.save(plate_file,quality=93,subsampling=0)
        if i==1:
            shot.save(OUT/"COVER.jpg",quality=93,subsampling=0)
        clip=clips / ("shot_%02d.mp4"%i)
        frames=int(round(seconds*24))
        vf=("zoompan=z='min(zoom+0.00050,1.045)':"
            "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            "d=1:s=1080x1920:fps=24,format=yuv420p")
        cmd(["ffmpeg","-hide_banner","-loglevel","error","-y",
            "-loop","1","-framerate","24","-i",str(plate_file),
            "-vf",vf,"-frames:v",str(frames),"-an","-c:v","libx264",
            "-preset","veryfast","-crf","20","-pix_fmt","yuv420p",str(clip)],timeout=270)
        concat_lines.append("file '"+str(clip.resolve()).replace("'","'\\''")+"'")
        storyboard.append({"shot":i,"start_s":round(t,2),"end_s":round(t+seconds,2),
                           "source_crop":list(box),"description":description,
                           "on_screen":caption,"source_kind":"museum_artwork_only"})
        t+=seconds
    listfile=OUT/"concat.txt"
    listfile.write_text("\n".join(concat_lines)+"\n",encoding="utf-8")
    dest=OUT/"VIDEO_SILENT_PRIVATE.mp4"
    cmd(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0",
         "-i",str(listfile),"-c","copy","-movflags","+faststart",str(dest)],timeout=300)
    probe=json.loads(cmd(["ffprobe","-v","error","-show_format","-show_streams",
                          "-of","json",str(dest)]))
    video=[s for s in probe["streams"] if s.get("codec_type")=="video"]
    assert len(video)==1 and video[0]["width"]==1080 and video[0]["height"]==1920
    assert 34.0 <= float(probe["format"]["duration"]) <= 37.0
    cmd(["ffmpeg","-v","error","-xerror","-i",str(dest),"-map","0",
         "-f","null","-"],timeout=400)
    (OUT/"STORYBOARD.json").write_text(json.dumps({
        "title":TITLE,"artist":ARTIST,"duration_s":t,
        "shot_count":len(storyboard),"human_style_rules":"3-4 s clips, slow camera, no 1s flashes, no voice/AI-generated artifacts",
        "shots":storyboard,"music":"V330 real recording to be verified in following step",
        "artistic_review":"PENDING"
    },indent=2),encoding="utf-8")
    (OUT/"SOCIAL_COPY.txt").write_text(
        "TITLE: The Witches and the Hourglass | Salvator Rosa\n"
        "HOOK: A cauldron glows. Above the witches floats a skeleton holding an hourglass.\n"
        "SHORT: Three figures gather around a cauldron. Above them, a skeletal apparition holds an hourglass, a symbol of life's brevity.\n"
        "INSTAGRAM: A witchcraft scene at dusk. The hourglass is the clue. What else do you notice?\n"
        "FACEBOOK: Salvator Rosa turned a circle of canvas into an eerie evening. Explore his 17th-century Scenes of Witchcraft: Evening at the Cleveland Museum of Art.\n"
        "TIKTOK: Look up: what does the skeleton hold?\n"
        "YOUTUBE SHORTS: Salvator Rosa's Witches and the Hourglass\n"
        "HASHTAGS: #SalvatorRosa #ArtHistory #WitchcraftArt #ClevelandMuseumOfArt #ArtVision\n"
        "CREDIT: Salvator Rosa, Scenes of Witchcraft: Evening, c. 1645-49, The Cleveland Museum of Art, 1977.37.3. CMA Open Access CC0.\n"
        "MUSIC: Complete using real V330 track proof and attribution in package.\n"
        "WARNING: No supernatural event is claimed factual; all details originate from museum artwork.\n",
        encoding="utf-8")
    print("SILENT_MP4_RENDERED_TECH_PASS",str(dest),round(t,2),sha256(dest))

if __name__=="__main__":
    dedup_gate()
    image=get_authentic_painting()
    render(image)
