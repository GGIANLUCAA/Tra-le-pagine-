#!/usr/bin/env python3
"""ArtVision V52B Joseph Wright Cinema: authentic art, free render, review-only release."""
from __future__ import annotations
import importlib.util, hashlib, json, subprocess, sys, zipfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import artvision_editorial_post_v28 as editorial
editorial.CATALOG=ROOT/"config/artvision_wright_air_pump_editorial_20261028.json"
spec=importlib.util.spec_from_file_location("cinema_v30",ROOT/"scripts/artvision_cinema_duo_v30.py")
engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
engine.CONFIG=ROOT/"config/artvision_wright_air_pump_20261028.json"
engine.editorial.CATALOG=editorial.CATALOG
cinema=engine.cinema
W,H=1080,1920
TITLE_LINES=["AN EXPERIMENT ON A BIRD","IN THE AIR PUMP"]
TITLE="An Experiment on a Bird in the Air Pump"
ARTIST="JOSEPH WRIGHT 'OF DERBY'"
SERIF="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1048576),b""):h.update(b)
    return h.hexdigest()

def fit(d,s,face,start,maxw):
    for n in range(start,21,-1):
        f=ImageFont.truetype(face,n)
        if d.textbbox((0,0),s,font=f)[2]<=maxw:return f
    raise RuntimeError("Unreadable title/artist: blocking render")

def brand(frame,alpha=1):
    """Approved V6 band: unchanged position/palette/hierarchy, exact title + artist."""
    a=max(0,min(1,float(alpha)))
    base=frame.convert("RGBA")
    overlay=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(overlay)
    d.rounded_rectangle((56,1340,1024,1590),radius=10,fill=(5,8,13,round(210*a)))
    for line,y,size in [(TITLE_LINES[0],1360,42),(TITLE_LINES[1],1417,48)]:
        f=fit(d,line,SERIF,size,900)
        bb=d.textbbox((0,0),line,font=f)
        d.text(((W-(bb[2]-bb[0]))/2,y),line,font=f,fill=(255,251,243,round(255*a)))
    d.line((130,1495,950,1495),fill=(218,198,168,round(186*a)),width=2)
    f=fit(d,ARTIST,SANS,32,900);bb=d.textbbox((0,0),ARTIST,font=f)
    d.text(((W-(bb[2]-bb[0]))/2,1521),ARTIST,font=f,fill=(255,251,243,round(255*a)))
    return Image.alpha_composite(base,overlay).convert("RGB")

cinema.signature=brand
def cover(frame,path):
    brand(frame,1).save(path,quality=95,subsampling=0)
cinema.make_cover=cover

def full(art):
    """Opaque, single authentic artwork, no ghosting or replicated-edge stretch."""
    bg=Image.new("RGB",(W,H),(11,12,17))
    whole=art.convert("RGB").copy()
    whole.thumbnail((1020,1500),Image.Resampling.LANCZOS)
    x=(W-whole.width)//2;y=(H-whole.height)//2
    ImageDraw.Draw(bg).rectangle((x-10,y-10,x+whole.width+10,y+whole.height+10),fill=(39,34,28))
    bg.paste(whole,(x,y))
    return bg
cinema.full=full

def main():
    out=ROOT/"output/artvision-wright-air-pump-v52b-20261028"
    slug="wright_air_pump_20261028_0915"
    result=engine.render_one("air_pump",out)
    folder=out/slug
    film=folder/"VIDEO_MASTER.mp4"
    coverfile=folder/"COPERTINA.jpg"
    original=folder/"ORIGINAL_ARTWORK.jpg"
    track=folder/"ORIGINAL_LICENSED_MUSIC.mp3"
    framefile=folder/"QA_FIRST_FRAME_V52B.jpg"
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(film),
                    "-frames:v","1",str(framefile)],check=True)
    with Image.open(original) as src:
        expected=brand(cinema.crop(src.convert("RGB"),cinema.STORY[0]),1)
    with Image.open(coverfile) as c, Image.open(framefile) as first:
        assert c.size==first.size==(W,H)
        ca=np.asarray(c.convert("RGB"),dtype=np.int16)
        fa=np.asarray(first.convert("RGB"),dtype=np.int16)
        ea=np.asarray(expected,dtype=np.int16)
        mad_cover=float(np.abs(ca[1340:1590]-ea[1340:1590]).mean())
        mad_first=float(np.abs(fa[1340:1590]-ea[1340:1590]).mean())
        assert mad_cover<12 and mad_first<16,(mad_cover,mad_first)
        for y0,y1 in [(1355,1407),(1410,1475),(1516,1568)]:
            bright=np.sum(np.all(ca[y0:y1,150:930]>210,axis=2))
            assert bright>130,("Missing opening title line or artist",y0,bright)
    info=json.loads(subprocess.check_output(["ffprobe","-v","error",
        "-show_entries","format=duration,size:stream=codec_type,codec_name,width,height",
        "-of","json",str(film)]))
    assert any(s.get("codec_name")=="h264" and s.get("width")==W and s.get("height")==H for s in info["streams"])
    assert any(s.get("codec_name")=="aac" for s in info["streams"])
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-xerror",
                    "-i",str(film),"-f","null","-"],check=True)
    assert editorial.validate_folder(folder)==[],editorial.validate_folder(folder)
    research={
      "format":"artvision_cinema","chosen":"Joseph Wright 'of Derby' — An Experiment on a Bird in the Air Pump",
      "candidates":[
        {"title":"An Experiment on a Bird in the Air Pump","artist":"Joseph Wright 'of Derby'","decision":"selected","why":"Distinct unproduced 1768 work; human reactions to science, public-domain faithful image."},
        {"title":"The Tower of Babel","artist":"Pieter Bruegel the Elder","decision":"not selected","why":"Bruegel very recently used; provenance still to check."},
        {"title":"The Night Watch","artist":"Rembrandt van Rijn","decision":"not selected","why":"Rembrandt has numerous earlier production modules and potential duplicates."}],
      "audience_metrics":"unavailable; qualitative editorial comparison only",
      "duplicate_check":"Checked recent docs/productions and repository code search; no standalone Wright Air Pump production found before this cycle.",
      "primary_museum":"https://www.nationalgallery.org.uk/paintings/joseph-wright-of-derby-an-experiment-on-a-bird-in-the-air-pump",
      "artwork_dimensions_cm":{"height":183,"width":244},
      "museum_scene":"not used; physical size recorded without inventing a museum room",
      "narrative_wow":"The scientist looks at us while the child cannot look at the bird: the spectator becomes responsible for the unresolved outcome.",
      "series_queue":"S01 E01 and E03 already rendered_needs_review; E02 Turner Critico blocked for missing verified Gacrux narration. This is a separate standalone and does not change the S01 queue.",
      "no_paid_video_api":True}
    (folder/"AUDIENCE_RESEARCH_V32.json").write_text(json.dumps(research,ensure_ascii=False,indent=2)+"\n")
    rights=folder/"SOURCES_AND_RIGHTS.md"
    with rights.open("a",encoding="utf8") as f:
        f.write("\nPhysical scale: 183 × 244 cm, National Gallery NG725; no museum-room reconstruction used.\n")
        f.write("National Gallery official page states the painting is on loan to Derby Museums until 1 November 2026; do not assert it is on display in London.\n")
        f.write("Original artwork is PD-Art as described by Wikimedia Commons; territorial photographic/cultural-heritage restrictions require review before public commercial use.\n")
        f.write("No synthetic animation, no generated persons, no paid video model, no social publication.\n")
    recipe=json.loads((folder/"VIDEO_RECIPE_V13.json").read_text())
    recipe.update({"actual_renderer":"scripts/artvision_wright_air_pump_20261028.py",
      "replication_command":"python scripts/artvision_wright_air_pump_20261028.py",
      "opening_title_exact":TITLE,"opening_title_lines":TITLE_LINES,
      "opening_artist_exact":ARTIST,"cover_brand":"V6 dark band, serif white title, gold divider, sans white artist",
      "dimensions_cm":{"height":183,"width":244},
      "no_gallery_scene":True,"artwork_is_animated":False,
      "review_state":"rendered_needs_review","human_approved":False})
    (folder/"VIDEO_RECIPE_V13.json").write_text(json.dumps(recipe,ensure_ascii=False,indent=2)+"\n")
    contract=json.loads((folder/"ARTVISION_CONTRACT_V25.json").read_text())
    contract["user_explicit_override_20261028"]="Opening must show exact artwork title and artist; composer is credited in V28 posts, not on screen."
    contract["actual_on_screen_text"]=[{"role":"opening_title","text":TITLE},
        {"role":"opening_artist","text":ARTIST}]
    (folder/"ARTVISION_CONTRACT_V25.json").write_text(json.dumps(contract,ensure_ascii=False,indent=2)+"\n")
    qa=json.loads((folder/"TECHNICAL_QA_V30.json").read_text())
    qa.update({"v44_status":"rendered_needs_review","human_approved":False,
       "first_frame_and_cover_verified_against_expected_brand":True,
       "title":TITLE,"artist":ARTIST,"cover_brand_mad":mad_cover,"first_frame_brand_mad":mad_first,
       "past_defect":"The Temptation of Saint Anthony lacked title or artist in first frame; both exact strings now mandatory in cover and opening, structurally and visually compared.",
       "rejected_previous_v52":"Initial V52 contact sheet revealed opening on empty cage instead of the bird; wrong normalized x=0.70. This corrected V52B uses x=0.50, y=0.27 and all shot coordinates visually checked against original. Old artifact retained, not approved.",
       "actual_video_sha256":sha(film),"full_ffmpeg_decode":True,"ffprobe":info,
       "no_edge_stretch":"No replicated-edge padding used; full-speed human visual review still pending.",
       "no_ghosting":"Only opaque hard cuts and a solid dark matte around full image.",
       "audio_recording_sha256":sha(track),"artwork_sha256":sha(original),
       "rights_review":"Commons PD-Art and music CC BY verified by source documentation; territorial and platform clearance still pending.",
       "artistic_review":"pending, not a Gold Master",
       "next_cycle_improvements":[
           "Verify at normal speed whether two consecutive right-side human closeups feel repetitive.",
           "Assess whether the white bird remains readable against the dark glass on a small Android screen.",
           "Listen to the complete musical closing: a successful AAC track does not guarantee a satisfying cadence."],
       "social_published":False,"no_paid_video_api":True})
    (folder/"TECHNICAL_QA_V30.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n")
    (folder/"RELEASE_STATUS.json").write_text(json.dumps({
      "status":"rendered_needs_review","sha256":sha(film),"human_approval":False,
      "publication":"not_published","rights_territorial_review":"pending",
      "s01_turner_critico":"blocked_voice_unavailable"},ensure_ascii=False,indent=2)+"\n")
    (folder/"ISTRUZIONI_REPLICA.md").write_text(
      "# ArtVision V52B — Wright of Derby\n\n"
      "Run: python scripts/artvision_wright_air_pump_20261028.py\n"
      "Source: config/artvision_wright_air_pump_20261028.json\n"
      "Posts: config/artvision_wright_air_pump_editorial_20261028.json\n"
      "Renderer: scripts/artvision_cinema_duo_v30.py + existing V6 signature adaptation.\n"
      "No paid video calls. No automatic social publishing or Gold Master approval.\n",encoding="utf8")
    archive=out/"ARTVISION_V52B_WRIGHT_AIR_PUMP_COMPLETE_REVIEW.zip"
    with zipfile.ZipFile(archive,"w",allowZip64=True) as z:
        for p in folder.rglob("*"):
            if p.is_file() and "_working" not in p.parts:
                z.write(p,p.relative_to(folder),
                  compress_type=zipfile.ZIP_STORED if p.suffix.lower() in (".mp4",".jpg",".mp3") else zipfile.ZIP_DEFLATED)
        for path in ("scripts/artvision_wright_air_pump_20261028.py",
            "config/artvision_wright_air_pump_20261028.json",
            "config/artvision_wright_air_pump_editorial_20261028.json"):
            z.write(ROOT/path,path,compress_type=zipfile.ZIP_DEFLATED)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        required={"VIDEO_MASTER.mp4","COPERTINA.jpg","POST_FACEBOOK.txt",
          "POST_INSTAGRAM.txt","POST_TIKTOK.txt","POST_YOUTUBE.txt",
          "POST_EDITORIAL_RESEARCH.json","AUDIENCE_RESEARCH_V32.json",
          "VIDEO_RECIPE_V13.json","SOURCES_AND_RIGHTS.md","MUSIC_RELEASE_V20.json",
          "TECHNICAL_QA_V30.json","QA_FIRST_FRAME_V52B.jpg",
          "ORIGINAL_ARTWORK.jpg","ORIGINAL_LICENSED_MUSIC.mp3"}
        assert required.issubset(z.namelist()),required-set(z.namelist())
    print("ARTVISION_V52B_RENDERED_NEEDS_REVIEW",json.dumps({
      "sha256":sha(film),"duration":info["format"]["duration"],
      "mp4_bytes":film.stat().st_size,"zip_bytes":archive.stat().st_size,
      "cover_mad":mad_cover,"first_frame_mad":mad_first},ensure_ascii=False),flush=True)

if __name__=="__main__":main()
