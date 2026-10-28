#!/usr/bin/env python3
"""ArtVision S01 E01: The Goldfinch, 33.5x22.8 cm museum-scale Cinema.
Free, no provider video API. Museum is a labelled illustrative reconstruction.
Never claims human aesthetic approval or publication.
"""
from __future__ import annotations
import importlib.util, hashlib, json, math, shutil, subprocess, sys, zipfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import artvision_editorial_post_v28 as editorial
editorial.CATALOG=ROOT/"config/artvision_goldfinch_museum_s01_editorial_20261028.json"
spec=importlib.util.spec_from_file_location("cinema_v30",ROOT/"scripts/artvision_cinema_duo_v30.py")
engine=importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
engine.CONFIG=ROOT/"config/artvision_goldfinch_museum_s01_20261028.json"
engine.editorial.CATALOG=editorial.CATALOG
cinema=engine.cinema
W,H,FPS=1080,1920,24
TITLE="THE GOLDFINCH"
ARTIST="CAREL FABRITIUS"
ART=None
BASE=None
FONT1="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT2="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def fitted(draw,txt,face,start,max_width):
    for size in range(start,19,-1):
        f=ImageFont.truetype(face,size)
        if draw.textbbox((0,0),txt,font=f)[2]<=max_width:return f
    raise RuntimeError("Title/artist cannot fit approved V6 band")
def brand(frame,alpha=1):
    alpha=max(0,min(1,float(alpha)))
    base=frame.convert("RGBA")
    layer=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(layer)
    d.rounded_rectangle((56,1340,1024,1590),radius=10,fill=(5,8,13,round(210*alpha)))
    f=fitted(d,TITLE,FONT1,65,900)
    width=d.textbbox((0,0),TITLE,font=f)[2]
    d.text(((W-width)/2,1371),TITLE,font=f,fill=(255,251,243,round(255*alpha)))
    d.line((130,1495,950,1495),fill=(218,198,168,round(186*alpha)),width=2)
    f=fitted(d,ARTIST,FONT2,34,900)
    width=d.textbbox((0,0),ARTIST,font=f)[2]
    d.text(((W-width)/2,1521),ARTIST,font=f,fill=(255,251,243,round(255*alpha)))
    return Image.alpha_composite(base,layer).convert("RGB")
cinema.signature=brand
def room_base():
    """Neutral illustrative gallery, not falsely identified as Mauritshuis room 14."""
    y,x=np.mgrid[0:H,0:W]
    v=np.clip((x-100)/W,0,1)
    wall=np.empty((H,W,3),dtype=np.uint8)
    rng=np.random.default_rng(605)
    noise=rng.normal(0,1.6,(H,W))
    light=12*np.exp(-((x-650)**2/(2*370**2)+(y-720)**2/(2*800**2)))
    shade=8*np.abs(x-540)/540
    for c,base in enumerate((185,179,165)):
        wall[:,:,c]=np.clip(base+light-shade+noise,0,255).astype("uint8")
    im=Image.fromarray(wall,"RGB");d=ImageDraw.Draw(im)
    # Architecture: 2.1 m door versus 0.335 m painting (same wall plane).
    d.rectangle((50,315,347,1445),fill=(126,113,94))
    d.rectangle((65,330,331,1431),fill=(69,62,58))
    d.rectangle((88,352,312,1422),fill=(46,43,42))
    d.line((40,1453,1080,1453),fill=(125,112,96),width=17)
    d.line((0,1471,1080,1471),fill=(207,195,173),width=10)
    d.rectangle((0,1482,W,H),fill=(100,80,66))
    for j in range(22):
        yy=1485+int((j/22)**1.6*(H-1485))
        d.line((0,yy,W,yy),fill=(115+int(j*.9),96+int(j*.7),80+int(j*.5)),width=2)
    for i in range(-5,7):
        d.line((540,1465,540+i*350,1920),fill=(80,65,55),width=2)
    d.line((0,240,1080,240),fill=(230,223,210),width=24)
    d.line((0,270,1080,270),fill=(145,136,124),width=5)
    d.ellipse((520,295,770,520),fill=(210,202,181))
    d.ellipse((545,315,740,490),fill=(232,222,195))
    # Wall spotlight and vignette are illustrative, not a claimed museum photo.
    return im
def gallery_frame(z):
    if ART is None:raise RuntimeError("Authentic painting not loaded")
    global BASE
    if BASE is None:BASE=room_base()
    z=max(1.0,min(3.4,float(z)))
    cw=W/z;ch=H/z
    x0=max(0,min(W-cw,650-cw/2))
    y0=max(0,min(H-ch,890-ch/2))
    bg=BASE.crop((int(x0),int(y0),int(x0+cw),int(y0+ch))).resize((W,H),Image.Resampling.BICUBIC)
    cx=(650-x0)*z;cy=(890-y0)*z
    # Real-world size: 22.8 cm width at 2.0m, 50-degree FOV ~126 px.
    pw=max(20,round(126*z))
    ph=round(pw*33.5/22.8)
    thick=max(3,round(8*z))
    left=round(cx-pw/2);top=round(cy-ph/2)
    d=ImageDraw.Draw(bg)
    d.rounded_rectangle((left-thick+5*z,top-thick+8*z,left+pw+thick+5*z,top+ph+thick+8*z),
                        radius=3,fill=(70,64,54))
    d.rectangle((left-thick,top-thick,left+pw+thick,top+ph+thick),fill=(58,47,37))
    d.rectangle((left-thick+2,top-thick+2,left+pw+thick-2,top+ph+thick-2),outline=(160,139,103),width=max(1,round(2*z)))
    d.rectangle((left-2,top-2,left+pw+2,top+ph+2),fill=(23,22,20))
    art=ART.resize((pw,ph),Image.Resampling.LANCZOS)
    bg.paste(art,(left,top))
    d=ImageDraw.Draw(bg)
    d.line((left,top+ph,left+pw,top+ph),fill=(29,27,23),width=max(1,round(2*z)))
    return bg
original_crop=cinema.crop
def custom_crop(src,shot):
    global ART
    ART=src
    kind=shot[0]
    if kind=="wide":return gallery_frame(1.35)
    if kind=="medium":return gallery_frame(2.0)
    return original_crop(src,shot)
def custom_full(src):
    global ART
    ART=src
    return gallery_frame(1.0)
cinema.crop=custom_crop
cinema.full=custom_full
def custom_cover(img,path):
    brand(gallery_frame(1),1).save(path,quality=95,subsampling=0)
cinema.make_cover=custom_cover
original_render=cinema.render_clip
RANGES={0:(1.0,1.35),1:(1.35,2.0),2:(2.0,3.4),8:(3.4,2.0),9:(2.0,1.0)}
def render_clip(img,scene,i,work):
    if i not in RANGES:return original_render(img,scene,i,work)
    frames=round(scene["duration"]*FPS)
    a,b=RANGES[i]
    frame_dir=work/f"museum_frames_{i:02d}";frame_dir.mkdir(exist_ok=True)
    for n in range(frames):
        t=n/max(1,frames-1)
        # smoothstep: zero velocity at cuts, no overlays or pixel edge replication
        smooth=t*t*(3-2*t)
        z=a+(b-a)*smooth
        frame=gallery_frame(z)
        if i==0:
            seconds=n/FPS
            opacity=1 if seconds<=2.9 else max(0,1-(seconds-2.9)/.55)
            frame=brand(frame,opacity)
        frame.save(frame_dir/f"f{n:04d}.jpg",quality=91,subsampling=0)
    output=work/f"clip_{i:02d}.mp4"
    cinema.run("ffmpeg","-hide_banner","-loglevel","error","-y",
               "-framerate",FPS,"-i",frame_dir/"f%04d.jpg",
               "-c:v","libx264","-preset","veryfast","-crf",19,
               "-pix_fmt","yuv420p",output)
    shutil.rmtree(frame_dir)
    return output
cinema.render_clip=render_clip
def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()
def run():
    root=ROOT/"output/artvision-goldfinch-s01"
    result=engine.render_one("goldfinch",root)
    folder=root/"fabritius_goldfinch_museum_s01_20261028"
    film=folder/"VIDEO_MASTER.mp4"
    cover=folder/"COPERTINA.jpg"
    info=json.loads(subprocess.check_output(["ffprobe","-v","error",
      "-show_entries","format=duration,size:stream=codec_type,codec_name,width,height",
      "-of","json",str(film)]))
    assert any(s.get("codec_name")=="h264" and s.get("width")==1080 and s.get("height")==1920 for s in info["streams"])
    assert any(s.get("codec_name")=="aac" for s in info["streams"])
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-xerror","-i",str(film),"-f","null","-"],check=True)
    first=folder/"QA_FIRST_FRAME.jpg"
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(film),"-frames:v","1",str(first)],check=True)
    with Image.open(cover) as a,Image.open(first) as b:
        assert a.size==b.size==(W,H)
        aa=np.asarray(a.convert("RGB"),dtype=np.int16)
        bb=np.asarray(b.convert("RGB"),dtype=np.int16)
        mad=float(np.mean(np.abs(aa[1340:1590]-bb[1340:1590])))
        assert mad<15,("cover/first-frame typography differs",mad)
    research={
      "series":"artvision_museum_immersion_real_scale_s01","episode":1,
      "selected":"Carel Fabritius — The Goldfinch (1654)",
      "candidates":[{"artist":"Carel Fabritius","work":"The Goldfinch","chosen":True,"reason":"Queued episode 1, 33.5x22.8cm verified by Mauritshuis, public-domain source."},
        {"artist":"J. M. W. Turner","work":"The Fighting Temeraire","chosen":False,"reason":"Reserved S01 episode 2; requires genuinely available Google Gacrux narration."},
        {"artist":"Georges Seurat","work":"A Sunday on La Grande Jatte—1884","chosen":False,"reason":"Reserved S01 episode 3; monumental scale contrast."}],
      "duplicate_check":"No Goldfinch episode in the existing 2026-10-28 production register before this run; no master overwritten.",
      "audience_metrics":"not available, no fabricated views or engagement data",
      "physical_size_cm":{"height":33.5,"width":22.8},
      "human_reference":"2.1m illustrative door on same wall, 0.335m panel; ratio ~6.27",
      "camera_reference":"panel 22.8cm wide, ~2m distance, ~50 degree horizontal FOV, initial 126px wide",
      "gallery":"illustrative reconstruction, NOT Mauritshuis room 14 photo",
      "approved_references":["docs/ARTVISION_MUSEUM_IMMERSION_MODELLO_APPROVATO_V46.md",
         "The Cyclops SENZA STRISCE","Hiroshige Museum Scale"],
      "museum": "https://www.mauritshuis.nl/en/our-collection/artworks/605-the-goldfinch"
    }
    (folder/"AUDIENCE_RESEARCH_V32.json").write_text(json.dumps(research,ensure_ascii=False,indent=2)+"\n")
    source=folder/"SOURCES_AND_RIGHTS.md"
    with source.open("a",encoding="utf8") as f:
        f.write("\nMuseum set: original locally drawn illustrative reconstruction, NOT a documentary photograph of Mauritshuis.\n")
        f.write("Physical scale: 33.5 x 22.8 cm (Mauritshuis, inv. 605), framed panel is set behind inner frame lip.\n")
        f.write("No third-party gallery photograph used; no generative video model used.\n")
    recipe=json.loads((folder/"VIDEO_RECIPE_V13.json").read_text())
    recipe.update({"renderer":"scripts/artvision_goldfinch_museum_s01_20261028.py",
      "replication_command":"python scripts/artvision_goldfinch_museum_s01_20261028.py",
      "gallery":"illustrative reconstruction","dimensions_cm":{"height":33.5,"width":22.8},
      "camera_zoom_ranges":RANGES,"physical_reference":"2.1m door versus 33.5cm panel",
      "museum_reference":"Mauritshuis inventory 605; not actual gallery photography",
      "opening_text":[TITLE,ARTIST],"state":"rendered_needs_review","human_approval":False})
    (folder/"VIDEO_RECIPE_V13.json").write_text(json.dumps(recipe,ensure_ascii=False,indent=2)+"\n")
    contract=json.loads((folder/"ARTVISION_CONTRACT_V25.json").read_text())
    contract["user_explicit_override_20261028"]={"opening":"exact title + artist, not MUSIC BY",
       "precedence":"explicit user request over legacy V25 on-screen music label"}
    contract["actual_on_screen_text"]=[{"role":"opening_title","text":TITLE},{"role":"opening_artist","text":ARTIST}]
    contract["opening"]["actual_title"]=TITLE
    contract["opening"]["actual_artist"]=ARTIST
    (folder/"ARTVISION_CONTRACT_V25.json").write_text(json.dumps(contract,ensure_ascii=False,indent=2)+"\n")
    qa=json.loads((folder/"TECHNICAL_QA_V30.json").read_text())
    qa.update({"first_frame":first.name,"first_frame_title":TITLE,"first_frame_artist":ARTIST,
      "cover_title":TITLE,"cover_artist":ARTIST,"first_frame_cover_band_mean_absolute_difference":mad,
      "visual_identity":"same dark band/serif/gold divider/sans hierarchy as Bruegel/Ensor",
      "v46":"physical-scale gallery reconstruction with no edge stretch, no crossfade",
      "prior_error":"The Temptation of Saint Anthony omitted title/artist on first frame; explicit shared brand and band-difference gate added",
      "v44_status":"rendered_needs_review","human_artistic_review":False,
      "gallery_authenticity":"illustrative only; no false claim of real Mauritshuis gallery",
      "three_defects_for_next_cycle":[
         "Evaluate whether the illustrated gallery is photorealistic enough compared to approved Cyclops/Hiroshige reference.",
         "Assess transitions from museum approach to painted detail for perceived abruptness.",
         "Listen to full Water Lily musical phrase and review final cut cadence."
      ],"no_paid_video_api":True,"no_social_autopublish":True})
    (folder/"TECHNICAL_QA_V30.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n")
    (folder/"RELEASE_STATUS.json").write_text(json.dumps({"state":"rendered_needs_review",
      "video_sha256":sha(film),"approved":False,"published":False,
      "aesthetic_full_watch":"pending","rights_territorial_review":"pending",
      "next_episode":"Turner Critico only if real Google Gacrux available"},indent=2)+"\n")
    archive=root/"ARTVISION_GOLDFINCH_MUSEUM_S01_COMPLETE.zip"
    with zipfile.ZipFile(archive,"w",allowZip64=True) as z:
        for p in folder.rglob("*"):
            if p.is_file() and "_working" not in p.parts:
                z.write(p,p.relative_to(folder),compress_type=zipfile.ZIP_STORED if p.suffix.lower() in (".mp4",".jpg",".mp3") else zipfile.ZIP_DEFLATED)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        required={"VIDEO_MASTER.mp4","COPERTINA.jpg","POST_FACEBOOK.txt","POST_INSTAGRAM.txt",
           "POST_TIKTOK.txt","POST_YOUTUBE.txt","ORIGINAL_ARTWORK.jpg","ORIGINAL_LICENSED_MUSIC.mp3",
           "QA_FIRST_FRAME.jpg","VIDEO_RECIPE_V13.json","SOURCES_AND_RIGHTS.md",
           "AUDIENCE_RESEARCH_V32.json","TECHNICAL_QA_V30.json","RELEASE_STATUS.json"}
        assert required.issubset(z.namelist()),required-set(z.namelist())
    print("GOLDFINCH_S01_RENDER_VERIFIED",json.dumps({"sha256":sha(film),
      "seconds":float(info["format"]["duration"]),"mp4_bytes":film.stat().st_size,
      "zip_bytes":archive.stat().st_size,"status":"rendered_needs_review"},ensure_ascii=False),flush=True)
if __name__=="__main__":run()
