#!/usr/bin/env python3
"""ArtVision V47: new Ensor episode, authentic 1890 KMSKA painting, V28 dossier.
Explicit 28/10 user opening override: title + artist, not legacy V25 music-on-screen.
No paid API, no social publication, no automatic artistic approval.
"""
from __future__ import annotations
import importlib.util, hashlib, json, subprocess, sys, zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import artvision_editorial_post_v28 as editorial
editorial.CATALOG=ROOT/"config/artvision_ensor_intrigue_editorial_20261028.json"
spec=importlib.util.spec_from_file_location("cinema_v30",ROOT/"scripts/artvision_cinema_duo_v30.py")
engine=importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
engine.CONFIG=ROOT/"config/artvision_ensor_intrigue_20261028.json"
engine.editorial.CATALOG=editorial.CATALOG
cinema=engine.cinema
W,H=1080,1920
TITLE="THE INTRIGUE"
ARTIST="JAMES ENSOR"
def fit(draw,txt,fontfile,initial,maxwidth):
    n=initial
    while n>20:
        f=ImageFont.truetype(fontfile,n)
        if draw.textbbox((0,0),txt,font=f)[2]<=maxwidth:return f
        n-=1
    raise RuntimeError("Typography will not fit")
def brand(frame,alpha=1):
    """Match approved Bruegel band, serif title, gold divider, sans artist."""
    base=frame.convert("RGBA")
    layer=Image.new("RGBA",(W,H),(0,0,0,0))
    d=ImageDraw.Draw(layer)
    alpha=max(0,min(1,float(alpha)))
    d.rounded_rectangle((56,1340,1024,1590),radius=10,fill=(5,8,13,round(210*alpha)))
    serif="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
    sans="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    f=fit(d,TITLE,serif,65,900)
    box=d.textbbox((0,0),TITLE,font=f)
    d.text(((W-(box[2]-box[0]))/2,1371),TITLE,font=f,fill=(255,251,243,round(255*alpha)))
    d.line((130,1495,950,1495),fill=(218,198,168,round(186*alpha)),width=2)
    f=fit(d,ARTIST,sans,34,900)
    box=d.textbbox((0,0),ARTIST,font=f)
    d.text(((W-(box[2]-box[0]))/2,1521),ARTIST,font=f,fill=(255,251,243,round(255*alpha)))
    return Image.alpha_composite(base,layer).convert("RGB")
cinema.signature=brand
def cover(frame,path):
    brand(frame,1).save(path,quality=95,subsampling=0)
cinema.make_cover=cover
def full(art):
    # Solid dark museum matte, never ghosted image or stretched edge.
    bg=Image.new("RGB",(W,H),(9,11,16))
    whole=art.convert("RGB").copy()
    whole.thumbnail((1010,1500),Image.Resampling.LANCZOS)
    x=(W-whole.width)//2;y=(H-whole.height)//2
    ImageDraw.Draw(bg).rectangle((x-10,y-10,x+whole.width+10,y+whole.height+10),fill=(32,30,29))
    bg.paste(whole,(x,y))
    return bg
cinema.full=full
def run():
    out=ROOT/"output/artvision-ensor-20261028"
    result=engine.render_one("intrigue",out)
    folder=out/"ensor_intrigue_20261028_0215"
    film=folder/"VIDEO_MASTER.mp4"
    coverfile=folder/"COPERTINA.jpg"
    with Image.open(coverfile) as im:
        assert im.size==(1080,1920)
        im.verify()
    metadata=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration,size:stream=codec_type,codec_name,width,height","-of","json",str(film)]))
    streams=metadata["streams"]
    assert any(x.get("codec_type")=="video" and x.get("codec_name")=="h264" and x.get("width")==1080 and x.get("height")==1920 for x in streams)
    assert any(x.get("codec_type")=="audio" and x.get("codec_name")=="aac" for x in streams)
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-xerror","-i",str(film),"-f","null","-"],check=True)
    first=folder/"QA_FIRST_FRAME_V47.jpg"
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(film),"-frames:v","1",str(first)],check=True)
    with Image.open(first) as im:
        assert im.size==(1080,1920)
        im.verify()
    # Structural visual check only; human visual review remains pending.
    research={
      "format":"artvision_cinema","selected":"James Ensor, The Intrigue (1890)",
      "comparison":[{"work":"The Intrigue","artist":"James Ensor","selected":True,"why":"Original 1890 Antwerp canvas; uncanny eleven masks; documented CC0 5000x2990 photo."},
                    {"work":"The Apparition","artist":"Gustave Moreau","selected":False,"why":"Interesting but image provenance not completed this cycle."},
                    {"work":"The Nightmare","artist":"Henry Fuseli","selected":False,"why":"Already treated in earlier Critico production; avoid repetition."}],
      "audience_signal":"qualitative only; no social trend metrics",
      "duplicate_check":"No Ensor Intrigue entry in 25 V31 cycle records and no repository code search match before production.",
      "dimensions_cm":{"width":149,"height":89.5,"source":"https://kmska.be/en/masterpiece/the-intrigue"},
      "museum_immersion":"not used; subject-specific opaque portrait cuts instead",
      "human_artistic_review":"pending"}
    (folder/"AUDIENCE_RESEARCH_V32.json").write_text(json.dumps(research,ensure_ascii=False,indent=2)+"\n")
    media={"authentic_image":"ORIGINAL_ARTWORK.jpg","image_source":"https://commons.wikimedia.org/wiki/File:De_intrige,_James_Ensor,_1890,_Koninklijk_Museum_voor_Schone_Kunsten_Antwerpen,_1856.002.jpeg",
           "image_rights":"CC0 1.0 / photo Hugo Maertens / Art in Flanders","music":"The Descent — Kevin MacLeod",
           "recording_rights":"CC BY 4.0, ISRC USUAN1200094","on_screen":"Title + artist, as explicitly required 28/10; music credit in V28 post footer",
           "no_paid_api":True,"source_review":"publication territorial review pending"}
    (folder/"MEDIA_SOURCING_V33.json").write_text(json.dumps(media,ensure_ascii=False,indent=2)+"\n")
    qa=json.loads((folder/"TECHNICAL_QA_V30.json").read_text())
    qa.update({"title_first_frame":TITLE,"artist_first_frame":ARTIST,"cover_title":TITLE,"cover_artist":ARTIST,
       "visual_identity":"Bruegel approved title/artist dark-band typography; no alternate cover style",
       "first_frame_actual_file":first.name,
       "visual_check":"title and artist rendered in both cover and opening; independent human visual inspection still pending",
       "prior_defect":"The Temptation of Saint Anthony opening lacked mandatory identity; blocked by this renderer's shared brand function",
       "legacy_v25_exception":"V25 expects MUSIC BY text on opening; explicit 28/10 user instruction requires exact title + artist, so V25 manifest is legacy-incompatible on this one point.",
       "v44_status":"rendered_needs_review","human_approval":False,"social_published":False,
       "next_cycle_improvements":["Avoid overly similar central masks on adjacent shots","Evaluate full horizontal painting readability on mobile","Listen to the complete music arc and tighten final cadence"]})
    (folder/"TECHNICAL_QA_V30.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n")
    contract=json.loads((folder/"ARTVISION_CONTRACT_V25.json").read_text())
    contract["user_explicit_override_20261028"]={"opening":"TITLE + ARTIST, not MUSIC BY","precedence":"explicit user request over legacy V25"}
    contract["actual_on_screen_text"]=[{"role":"opening_title","text":"The Intrigue"},{"role":"opening_artist","text":"JAMES ENSOR"}]
    (folder/"ARTVISION_CONTRACT_V25.json").write_text(json.dumps(contract,ensure_ascii=False,indent=2)+"\n")
    recipe=json.loads((folder/"VIDEO_RECIPE_V13.json").read_text())
    recipe["opening_override"]="Title and artist identical on cover and first video frame; music credited in posts"
    recipe["dimensions_cm"]={"width":149,"height":89.5}
    recipe["human_approval"]=False
    (folder/"VIDEO_RECIPE_V13.json").write_text(json.dumps(recipe,ensure_ascii=False,indent=2)+"\n")
    zpath=out/"ARTVISION_ENSOR_INTRIGUE_20261028_COMPLETE.zip"
    with zipfile.ZipFile(zpath,"w",allowZip64=True) as z:
        for p in folder.rglob("*"):
            if p.is_file() and "_working" not in p.parts:
                z.write(p,p.relative_to(folder),compress_type=zipfile.ZIP_STORED if p.suffix.lower() in (".mp4",".jpg",".mp3") else zipfile.ZIP_DEFLATED)
    with zipfile.ZipFile(zpath) as z:
        assert z.testzip() is None
        required={"VIDEO_MASTER.mp4","COPERTINA.jpg","POST_FACEBOOK.txt","POST_INSTAGRAM.txt","POST_TIKTOK.txt","POST_YOUTUBE.txt","AUDIENCE_RESEARCH_V32.json","MEDIA_SOURCING_V33.json","TECHNICAL_QA_V30.json","QA_FIRST_FRAME_V47.jpg","VIDEO_RECIPE_V13.json","ORIGINAL_ARTWORK.jpg","ORIGINAL_LICENSED_MUSIC.mp3"}
        assert required.issubset(set(z.namelist())),required-set(z.namelist())
    print("V47_ENSOR_RENDER_VERIFIED",json.dumps({"sha256":hashlib.sha256(film.read_bytes()).hexdigest(),"duration":metadata["format"]["duration"],"size":film.stat().st_size,"zip":zpath.stat().st_size,"status":"rendered_needs_review"},ensure_ascii=False),flush=True)
if __name__=="__main__":run()
