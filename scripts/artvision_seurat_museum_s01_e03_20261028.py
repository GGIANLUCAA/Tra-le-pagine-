#!/usr/bin/env python3
"""S01 E03 Seurat: Cinema, real painting, no fake animation, zero paid APIs.
All rendered media are provisional until a full-speed human artistic review.
"""
from pathlib import Path
import hashlib, importlib.util, json, shutil, subprocess, sys, zipfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import artvision_editorial_post_v28 as editorial
editorial.CATALOG=ROOT/"config/artvision_seurat_museum_s01_e03_posts_20261028.json"
spec=importlib.util.spec_from_file_location("cinema_v30",ROOT/"scripts/artvision_cinema_duo_v30.py")
engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
engine.CONFIG=ROOT/"config/artvision_seurat_museum_s01_e03_20261028.json"
engine.editorial.CATALOG=editorial.CATALOG
cinema=engine.cinema
W,H,FPS=1080,1920,24
TITLE_LINES=["A SUNDAY ON LA GRANDE JATTE","— 1884"]
ARTIST="GEORGES SEURAT"
SERIF="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def fitted(draw,txt,face,size,max_width):
    while size>=22:
        font=ImageFont.truetype(face,size)
        if draw.textbbox((0,0),txt,font=font)[2]<=max_width:return font
        size-=1
    raise RuntimeError("Brand title would be unreadable")

def brand(frame,alpha=1):
    alpha=max(0,min(1,float(alpha)))
    base=frame.convert("RGBA")
    layer=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(layer)
    d.rounded_rectangle((56,1340,1024,1590),radius=10,fill=(5,8,13,round(190*alpha)))
    for line,y,size in zip(TITLE_LINES,(1355,1412),(52,47)):
        f=fitted(d,line,SERIF,size,900)
        b=d.textbbox((0,0),line,font=f)
        d.text(((W-(b[2]-b[0]))/2,y),line,font=f,fill=(255,251,243,round(255*alpha)))
    d.line((130,1495,950,1495),fill=(218,198,168,round(186*alpha)),width=2)
    f=fitted(d,ARTIST,SANS,33,900);b=d.textbbox((0,0),ARTIST,font=f)
    d.text(((W-(b[2]-b[0]))/2,1521),ARTIST,font=f,fill=(255,251,243,round(255*alpha)))
    return Image.alpha_composite(base,layer).convert("RGB")

cinema.signature=brand
def cover(image,path):
    brand(image,1).save(path,quality=95,subsampling=0)
cinema.make_cover=cover

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def run():
    dest=ROOT/"output/artvision-seurat-s01-e03"
    status=engine.render_one("seurat_jatte_s01_e03",dest)
    folder=dest/"seurat_jatte_s01_e03"
    film=folder/"VIDEO_MASTER.mp4";jpg=folder/"COPERTINA.jpg"
    first=folder/"QA_FIRST_FRAME.jpg"
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(film),
                    "-frames:v","1",str(first)],check=True)
    with Image.open(first) as a,Image.open(jpg) as b:
        assert a.size==b.size==(W,H)
        aa=np.asarray(a.convert("RGB"),dtype=np.int16)
        bb=np.asarray(b.convert("RGB"),dtype=np.int16)
        mad=float(np.mean(np.abs(aa[1340:1590]-bb[1340:1590])))
        assert mad<15,("cover and first frame typography differ",mad)
    probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries",
         "format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate",
         "-of","json",str(film)]))
    assert any(s.get("codec_name")=="h264" and s.get("width")==W and s.get("height")==H for s in probe["streams"])
    assert any(s.get("codec_name")=="aac" for s in probe["streams"])
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-xerror","-i",str(film),
                    "-f","null","-"],check=True)
    recipe=json.loads((folder/"VIDEO_RECIPE_V13.json").read_text())
    recipe.update({"actual_renderer":"scripts/artvision_seurat_museum_s01_e03_20261028.py",
        "actual_title":"A Sunday on La Grande Jatte — 1884",
        "actual_opening_title_lines":TITLE_LINES,"actual_opening_artist":ARTIST,
        "physical_dimensions_cm":{"height":207.5,"width":308.1},
        "museum_room_reconstruction":"none","artwork_is_animated":False,
        "no_i2v_provider":True,"queue_episode":"S01-E03",
        "approval_state":"rendered_needs_review","human_approved":False})
    (folder/"VIDEO_RECIPE_V13.json").write_text(json.dumps(recipe,ensure_ascii=False,indent=2)+"\n")
    contract=json.loads((folder/"ARTVISION_CONTRACT_V25.json").read_text())
    contract["opening"].update({"actual_title":"A Sunday on La Grande Jatte — 1884","actual_artist":ARTIST})
    contract["on_screen_text"]=[{"role":"opening_title","text":"A Sunday on La Grande Jatte — 1884"},
                                {"role":"opening_artist","text":ARTIST}]
    contract["user_explicit_override_20261028"]="Title AND artist mandatory on first frame; composer credit in social posts, not onscreen."
    (folder/"ARTVISION_CONTRACT_V25.json").write_text(json.dumps(contract,ensure_ascii=False,indent=2)+"\n")
    rights=folder/"SOURCES_AND_RIGHTS.md"
    with rights.open("a",encoding="utf8") as f:
        f.write("\nScale: 207.5 × 308.1 cm (Art Institute of Chicago, 1926.224).\n")
        f.write("This Cinema variant uses painting details and a final whole-artwork reveal; no gallery photograph or invented scale scene.\n")
        f.write("Source photograph is a faithful reproduction of public-domain flat art, PD-Art; territorial heritage rights must be checked before commercial distribution.\n")
    qa=json.loads((folder/"TECHNICAL_QA_V30.json").read_text())
    qa.update({"first_frame_and_cover_mad":mad,"exact_title_present_by_renderer":TITLE_LINES,
        "exact_artist_present_by_renderer":ARTIST,"visual_identity":"V6 dark band, serif title, gold rule, sans artist, fixed positions",
        "previous_incident":"The Temptation of Saint Anthony: missing exact title or artist in opening; title+artist now generated from shared function and verified against first frame.",
        "physical_scale_cm":{"height":207.5,"width":308.1},
        "museum_scale_scene":"not used; no false scale claim",
        "no_edge_stretch":"No edge-replication technique in renderer; sample-frame inspection still required",
        "full_decode_confirmed":True,"ffprobe":probe,
        "artistic_review":"pending; full-speed watching/listening and scene sync must be reviewed",
        "defects_to_improve_next_cycle":[
            "Review the final whole-canvas presentation: a horizontal painting occupies a limited part of a vertical frame.",
            "Review whether the monkey reveal and pointillism texture shots are distinct and properly readable on a phone.",
            "Listen to the final musical cadence at normal speed; technical AAC presence is not a subjective audio review."],
        "no_paid_video_api":True,"no_social_autopublish":True})
    (folder/"TECHNICAL_QA_V30.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n")
    (folder/"RELEASE_STATUS.json").write_text(json.dumps({
        "state":"rendered_needs_review","mp4_sha256":sha(film),
        "human_artistic_approval":False,"published":False,
        "rights_territorial_review":"pending",
        "turner_e02":"blocked until real Google Gacrux voice is available"
    },ensure_ascii=False,indent=2)+"\n")
    research={"selected":"Seurat — A Sunday on La Grande Jatte — 1884",
      "candidates":[{"work":"The Goldfinch","result":"already rendered V50; no duplicate"},
        {"work":"The Fighting Temeraire","result":"Critico voice Gacrux not verified; cannot fake narration"},
        {"work":"A Sunday on La Grande Jatte — 1884","result":"selected S01 E03, PD image, 207.5 × 308.1 cm"}],
      "audience_metrics":"unavailable; no invented popularity figures",
      "narrative_wow":"tiny leashed monkey hidden in an apparently serene bourgeois Sunday, followed by discovery of chromatic dots",
      "primary_museum":"https://www.artic.edu/artworks/27992/a-sunday-on-la-grande-jatte-1884",
      "format":"Cinema V6, no voice","social_autopublish":False}
    (folder/"AUDIENCE_RESEARCH_V32.json").write_text(json.dumps(research,ensure_ascii=False,indent=2)+"\n")
    (folder/"ISTRUZIONI_REPLICA.md").write_text(
        "# ArtVision Seurat S01 E03\n\nRun: `python scripts/artvision_seurat_museum_s01_e03_20261028.py`\n\n"
        "Uses existing V30 renderer and exact source configuration in config/artvision_seurat_museum_s01_e03_20261028.json.\n"
        "Four V28 posts are in config/artvision_seurat_museum_s01_e03_posts_20261028.json.\n"
        "Video, original art, original music, cover, QA and recipe are preserved in the ZIP.\n"
        "No approval or social publishing is implied.\n")
    archive=dest/"ARTVISION_SEURAT_S01_E03_REVIEW_COMPLETE.zip"
    with zipfile.ZipFile(archive,"w",allowZip64=True) as z:
        for p in folder.rglob("*"):
            if p.is_file() and "_working" not in p.parts:
                z.write(p,p.relative_to(folder),
                  compress_type=zipfile.ZIP_STORED if p.suffix.lower() in (".mp4",".jpg",".mp3") else zipfile.ZIP_DEFLATED)
        for p in ("scripts/artvision_seurat_museum_s01_e03_20261028.py",
                  "config/artvision_seurat_museum_s01_e03_20261028.json",
                  "config/artvision_seurat_museum_s01_e03_posts_20261028.json"):
            z.write(ROOT/p,p,compress_type=zipfile.ZIP_DEFLATED)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        required={"VIDEO_MASTER.mp4","COPERTINA.jpg","QA_FIRST_FRAME.jpg",
           "POST_FACEBOOK.txt","POST_INSTAGRAM.txt","POST_TIKTOK.txt","POST_YOUTUBE.txt",
           "VIDEO_RECIPE_V13.json","ORIGINAL_ARTWORK.jpg","ORIGINAL_LICENSED_MUSIC.mp3",
           "SOURCES_AND_RIGHTS.md","TECHNICAL_QA_V30.json","RELEASE_STATUS.json"}
        assert required.issubset(set(z.namelist())),required-set(z.namelist())
    print("SEURAT_E03_TECHNICALLY_VERIFIED",json.dumps({
      "mp4_sha256":sha(film),"seconds":probe["format"]["duration"],
      "mp4_bytes":film.stat().st_size,"zip_bytes":archive.stat().st_size,
      "cover_first_frame_mad":mad,"state":"rendered_needs_review"},ensure_ascii=False),flush=True)
if __name__=="__main__":run()
