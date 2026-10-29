#!/usr/bin/env python3
"""Klimt pilot V69: licensed source acquisition + prepared Cinema Standard review render.

One artwork only, no generative video AI and no narration. Does not pretend a
Museum rendition, user approval, 4x1 completion, or site import exists.
"""
from __future__ import annotations
import argparse, hashlib, json, urllib.request, urllib.parse, subprocess, zipfile
from pathlib import Path
from PIL import Image
from artvision_cinema_prepared_v55 import render,sha256

ART_PAGE="https://commons.wikimedia.org/wiki/File:Klimt_-_The_Kiss.jpg"
API="https://commons.wikimedia.org/w/api.php"
MUSIC_PAGE="https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1500027"
MUSIC_URL="https://incompetech.com/music/royalty-free/mp3-royaltyfree/Dreams%20Become%20Real.mp3"
CC="https://creativecommons.org/licenses/by/4.0/"
USER_AGENT="ArtVision/69 source-reviewed public-domain Klimt The Kiss (GitHub GGIANLUCAA/Tra-le-pagine-)"
DETAILS=[
  ("faces","detail",[0.54,0.26],4.2,"The couple's touching faces: the small naturalistic core inside Klimt's gold"),
  ("hands","detail",[0.53,0.40],4.6,"The fragile hand gestures convey intimate tenderness between the figures"),
  ("ornaments_man","detail",[0.42,0.48],5.0,"Dark masculine rectangular garment motifs emerge from genuine paint pixels"),
  ("ornaments_woman","detail",[0.61,0.56],5.0,"Circular and flowerlike garment patterns contrast with the man's shapes"),
  ("gold_surface","detail",[0.22,0.45],5.1,"Gold field and metallic pigment create the surrounding luminous abstraction"),
  ("flowers","detail",[0.46,0.84],5.2,"The small multicolored living flowers anchor a golden, abstract scene"),
  ("cliff_edge","detail",[0.68,0.75],4.7,"The meadow ends abruptly, bringing tension to an otherwise serene embrace"),
  ("faces_return","detail",[0.60,0.31],4.6,"Return to both human faces after exploring the expansive golden surface"),
  ("gesture_resolution","detail",[0.48,0.39],4.9,"A last look at the gesture before revealing the complete square painting"),
  ("square_full","whole",[0.50,0.50],7.2,"Hold on the full authentic 180-by-180-centimeter composition with dignity")
]

def fetch(url,maxbytes,allowed_host,min_bytes=90000):
    req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT,"Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=90) as r:
        u=urllib.parse.urlsplit(r.geturl())
        if r.status!=200 or u.scheme!="https" or u.hostname not in allowed_host:
            raise ValueError("Bad download origin/redirect: "+r.geturl())
        result=r.read(maxbytes+1)
        if not min_bytes<len(result)<=maxbytes:raise ValueError("Source unexpectedly tiny or over cap")
        return result,r.geturl()

def obtain_art(assets):
    query=API+"?"+urllib.parse.urlencode({
        "action":"query","format":"json","formatversion":2,
        "titles":"File:Klimt - The Kiss.jpg","prop":"imageinfo",
        "iiprop":"url|size|mime|extmetadata"})
    body,url=fetch(query,2_000_000,{"commons.wikimedia.org"},min_bytes=200)
    doc=json.loads(body)
    pages=doc.get("query",{}).get("pages",[])
    if len(pages)!=1 or pages[0].get("missing") is True:raise ValueError("Klimt Commons original not found")
    info=pages[0].get("imageinfo",[None])[0]
    if not info or info.get("mime")!="image/jpeg":
        raise ValueError("No verified original high-resolution JPEG")
    lic=str(info.get("extmetadata",{}).get("LicenseShortName",{}).get("value","")).lower()
    if "public" not in lic and "pd-" not in lic and "pd " not in lic:
        raise ValueError("Wikimedia license is not demonstrably public domain: "+lic)
    original=info.get("url","")
    raw,final=fetch(original,12_000_000,{"upload.wikimedia.org"})
    path=assets/"klimt_original_public_domain.jpg"
    path.write_bytes(raw)
    with Image.open(path) as im:
        im.verify()
    with Image.open(path) as im:
        w,h=im.size
    if min(w,h)<3500 or not 0.90<w/h<1.10:
        raise ValueError("Not authentic square high resolution painting; manual source review required")
    return {"file":path.name,"sha256":sha256(path),"source_url":ART_PAGE,
            "source_download":final,"license":"Public Domain",
            "width":w,"height":h}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    root=Path(args.out).resolve()
    if root.exists():raise FileExistsError("Never overwrite or rerender existing pilot output")
    assets=root/"verified_assets"
    assets.mkdir(parents=True)
    art=obtain_art(assets)
    music_raw,music_final=fetch(MUSIC_URL,14_000_000,{"incompetech.com"})
    music_path=assets/"dreams_become_real_original_recording.mp3"
    music_path.write_bytes(music_raw)
    subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=noprint_wrappers=1",str(music_path)],check=True)
    music={"file":music_path.name,"sha256":sha256(music_path),
           "recording_title":"Dreams Become Real","recording_artist":"Kevin MacLeod",
           "source_url":MUSIC_PAGE,"recording_download_url":music_final,
           "license":"CC BY 4.0","license_url":CC}
    art_path=assets/art["file"]
    planned=[{"file":art["file"],"sha256":art["sha256"],
      "detail_id":detail,"mode":mode,"focus":focus,"duration_seconds":duration,
      "purpose":purpose} for detail,mode,focus,duration,purpose in DETAILS]
    p={"schema":"artvision-cinema-prepared-v55-v1","variant":"cinema_standard",
       "title":"The Kiss","artist":"Gustav Klimt","music":music,
       "shots":planned,"rights":"Commons PD-Art faithful historical painting image; music recording CC BY 4.0"}
    (root/"PREPARED_CINEMA_STANDARD_PLAN.json").write_text(json.dumps(p,indent=2,ensure_ascii=False)+"\n")
    (root/"ARTWORK_RIGHTS_AND_PROVENANCE.json").write_text(
      json.dumps({"artwork":art,"music":music,"canvas_cm":[180,180],
       "museum_page":"https://sammlung.belvedere.at/objects/6678/",
       "official_press_gallery_photographs_forbidden_without_written_reuse_permission":True,
       "studio_preview_only_not_v25_gold":True,"new_video_ai_paid_calls":0},
       indent=2,ensure_ascii=False)+"\n")
    out=root/"film"
    video,cover=render(p,assets,{art_path.resolve(),music_path.resolve()},out)
    subprocess.run(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(video),"-f","null","-"],check=True,timeout=1200)
    probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_format","-show_streams","-of","json",str(video)]))
    streams={x.get("codec_type"):x for x in probe["streams"]}
    if (streams["video"].get("width"),streams["video"].get("height"))!=(1080,1920) or streams["video"]["codec_name"]!="h264" or streams["audio"]["codec_name"]!="aac":
        raise ValueError("MP4 stream format failed")
    thumbs=out/"QA_FRAMES";thumbs.mkdir()
    for t in (0.1,1,3,5,7):
        subprocess.run(["ffmpeg","-nostdin","-v","error","-ss",str(t),"-i",str(video),"-frames:v","1","-y",str(thumbs/f"sec_{t}.jpg")],check=True)
    report={"schema":"artvision-klimt-cinema-v69-technical-review","artwork":"The Kiss",
       "status":"rendered_needs_review","video_file":video.name,
       "video_sha256":sha256(video),"video_bytes":video.stat().st_size,
       "duration_seconds":float(probe["format"]["duration"]),
       "original_art_sha256":art["sha256"],"music_recording_sha256":music["sha256"],
       "technical_ffprobe_pass":True,"full_decode_pass":True,
       "first_0_1_3_5_7_frames_extracted":True,
       "museum_not_rendered":True,"four_variant_completed":False,
       "V13_V54_release_gate":"not_certified_by_this_standalone_renderer",
       "human_full_speed_review":"pending","V25_approved":False,
       "private_archive_imported":False,"paid_video_ai_calls":0}
    (root/"QA_REVIEW_V69.json").write_text(json.dumps(report,indent=2)+"\n")
    package=root/"KLIMT_CINEMA_STANDARD_V69_REVIEW_PACKAGE.zip"
    with zipfile.ZipFile(package,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=4) as z:
        for item in [video,cover,root/"PREPARED_CINEMA_STANDARD_PLAN.json",
                     root/"ARTWORK_RIGHTS_AND_PROVENANCE.json",root/"QA_REVIEW_V69.json"]:
            z.write(item,item.name)
        for pic in thumbs.glob("*.jpg"):
            z.write(pic,"QA_FRAMES/"+pic.name)
    with zipfile.ZipFile(package) as z:
        if z.testzip():raise ValueError("ZIP CRC FAILED")
    report["package_sha256"]=sha256(package)
    (root/"QA_REVIEW_V69.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))

if __name__=="__main__":main()
