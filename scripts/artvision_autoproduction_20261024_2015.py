#!/usr/bin/env python3
"""ArtVision V31: real museum-source Symbolist collection; no ghosting, no fake video."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, math, shutil, subprocess, sys, time, zipfile
from pathlib import Path
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import artvision_editorial_post_v28 as editorial
from artvision_contract_gate_v25 import check_preflight
from artvision_image_acquisition import ImageStore
spec=importlib.util.spec_from_file_location("artvision_v29",ROOT/"scripts/artvision_storm_rembrandt_v29.py")
cinema=importlib.util.module_from_spec(spec)
spec.loader.exec_module(cinema)
W,H,FPS=1080,1920,24
CONFIG=ROOT/"config/artvision_autoproduction_20261024_2015.json"
UA="ArtVisionMuseumCollectionV31/1.0 (github.com/GGIANLUCAA/Tra-le-pagine-)"
def run(*args):
    subprocess.run([str(a) for a in args],check=True)
def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
    return h.hexdigest()
def probe(path):
    return json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries",
      "format=duration,size","-show_entries","stream=codec_type,codec_name,width,height",
      "-of","json",str(path)],text=True))
def fetch(url,dest,kind,minimum):
    errs=[]
    for attempt in range(2):
        try:
            with requests.get(url,headers={"User-Agent":UA},timeout=90,stream=True) as resp:
                resp.raise_for_status()
                c=resp.headers.get("Content-Type","").lower()
                if "text/html" in c or "application/json" in c:raise RuntimeError("Not an asset "+c)
                with dest.open("wb") as out:
                    for block in resp.iter_content(1024*512):
                        if block:out.write(block)
            if dest.stat().st_size<150000:raise RuntimeError("Asset too small")
            if kind=="image":
                with Image.open(dest) as im:
                    im.verify()
                with Image.open(dest) as im:
                    if im.width<minimum[0] or im.height<minimum[1]:
                        raise RuntimeError("Not source resolution: "+str(im.size))
                    print("IMAGE_OK",dest.name,im.size,dest.stat().st_size,flush=True)
            else:
                if not any(x.get("codec_type")=="audio" for x in probe(dest)["streams"]):
                    raise RuntimeError("No audio stream")
                print("AUDIO_OK",dest.stat().st_size,flush=True)
            return
        except Exception as exc:
            errs.append(type(exc).__name__+": "+str(exc)[:160])
            dest.unlink(missing_ok=True)
            time.sleep(attempt+1)
    raise RuntimeError("DOWNLOAD_BLOCKED "+str(dest)+": "+" | ".join(errs))
def whole_image(im):
    # A single opaque painting on a plain dark mat. No previous painting is ever visible.
    bg=Image.new("RGB",(W,H),(8,11,16))
    painting=ImageOps.contain(im,(1030,1700),Image.Resampling.LANCZOS)
    x=(W-painting.width)//2;y=(H-painting.height)//2
    d=ImageDraw.Draw(bg)
    d.rectangle((x-9,y-9,x+painting.width+9,y+painting.height+9),fill=(48,40,31))
    d.rectangle((x-3,y-3,x+painting.width+3,y+painting.height+3),fill=(10,11,14))
    bg.paste(painting,(x,y))
    return bg
def planned_manifest(cfg):
    title=cfg["title_en"];artist=cfg["opening_text"];music=cfg["music"]
    shots=cfg["scenes"]
    techniques=[{"id":name,"why":{
       "human_gaze_start":"An uncanny eye is visible from the opening frame",
       "locked_hold":"The painting remains stable long enough for close inspection",
       "visual_hierarchy":"Detail precedes full image only when it changes understanding",
       "motivated_cut":"Every new painting or detail contributes a different symbol",
       "detail_return":"A full painting returns after its central detail is understood",
       "rhythmic_rest":"A final unhurried still image follows the music's resolution",
       "camera_seasick_gate":"No camera swing, oscillation or restless automatic zoom"}[name]} for name in cfg["techniques"]]
    return {
      "schema":"artvision-release-contract-v25","video_id":cfg["slug"],
      "format":"artvision_cinema","approved_baseline":"cinema_v6",
      "artwork":{"artist":artist,"title_en":title,"title_language":"en",
                 "identity_source":cfg["artworks"][0]["museum_url"]},
      "opening":{"identity_preset":"modules/artvision/IDENTITA_VISIVA_FISSA_V6.json",
                 "artist_text":artist,"composer":music["artist"],
                 "music_credit_text":"MUSIC BY "+music["artist"].upper()},
      "cover":{"identity_family":"cinema_v6","title_en":title,"artist":artist,
               "language":"en","existing_design_unchanged":True},
      "on_screen_text":[{"role":"opening_artist","text":artist},
                        {"role":"opening_music","text":"MUSIC BY "+music["artist"].upper()}],
      "voice":False,"subtitles":False,
      "first_seven_seconds":[
       {"second":s,"what_visible":v,"why":"A true detail of Redon's 1914 painting introduces the mysterious symbolist eye"}
       for s,v in [(0,"One genuine enormous Cyclops eye appears beneath the fixed V6 artist credit"),
                   (1,"The eye remains legible and holds attention without camera motion"),
                   (3,"The original eye is still in focus as the artist signature fades away"),
                   (5,"The painting opens gradually to reveal the giant behind the hill"),
                   (7,"The larger head and hillside clarify the mysterious painted subject")]],
      "scenes":[{"source_id":"artwork_"+s["art"],"subject":s["purpose"],"purpose":s["purpose"],
                 "shot":s["kind"],"motion":s["motion"],"duration_seconds":s["seconds"]} for s in shots],
      "transition_reviews_plan":[{"why":"Move from eye to hill while preserving one opaque painting"},
                                 {"why":"Switch Redon's dream to Moreau's divine myth without transparent overlap"},
                                 {"why":"Switch Moreau's crowded divine vision to Böcklin's stillness using a clean cut"}],
      "music_cues":[{"seconds":0,"reason":"Start of a real licensed soundtrack excerpt"},
                    {"seconds":20,"reason":"First painting change after a documented score excerpt"},
                    {"seconds":48,"reason":"Visual calm deepens while the musical texture continues"}],
      "duration_reason":"Fourteen independently motivated views across three genuine museum artworks, ending with a longer contemplative full-frame hold.",
      "selected_techniques":techniques,
      "sources":[{"id":a["id"],"url":a["commons"],"license":"Public domain faithful photographic reproduction",
                  "credit":a["artist"]+", "+a["museum"],"status":"verified"} for a in cfg["artworks"]],
      "music":{"title":music["name"],"composer":music["artist"],"origin":"external_licensed",
               "license":music["license"],"evidence":music["page"],
               "emotional_arc":"Mystery and wonder soften into stillness without artificial beat cuts",
               "rights_status":"verified"},
      "copy_languages":{"facebook":"it","instagram":"it","tiktok":"it","youtube":"it"},
      "editorial_standard":"artvision_editorial_v28",
      "archive_only_after_authorization":True,"social_autopublish":False,
      "publication":{"status":"not_published"},
      "outputs":{"video":"VIDEO_MASTER.mp4","cover":"COPERTINA.jpg",
                 "facebook":"POST_FACEBOOK.txt","instagram":"POST_INSTAGRAM.txt",
                 "tiktok":"POST_TIKTOK.txt","youtube":"POST_YOUTUBE.txt",
                 "recipe":"VIDEO_RECIPE_V13.json","techniques":"TECNICHE_REGIA.md",
                 "replication":"ISTRUZIONI_REPLICA.md","rights":"SOURCES_AND_RIGHTS.md",
                 "music_manifest":"MUSIC_RELEASE_V20.json"}
    }
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--preflight-only",action="store_true")
    parser.add_argument("--out",default="output/artvision-v31-symbolist")
    args=parser.parse_args()
    cfg=json.loads(CONFIG.read_text(encoding="utf8"))
    manifest=planned_manifest(cfg)
    issues=check_preflight(manifest)
    if issues:raise RuntimeError("V25 PREFLIGHT BLOCKED: "+"; ".join(issues))
    if editorial.validate_entry(cfg["editorial_key"],editorial.config()["entries"][cfg["editorial_key"]]):
        raise RuntimeError("V28 editorial research is incomplete")
    if args.preflight_only:
        print("V25_PREFLIGHT_PASS",cfg["slug"],len(cfg["scenes"]))
        return
    base=Path(args.out)/cfg["slug"]
    base.mkdir(parents=True,exist_ok=True)
    work=base/"_work";work.mkdir(exist_ok=True)
    assets={}
    image_store=ImageStore()
    for a in cfg["artworks"]:
        dest=base/("ORIGINAL_"+a["id"].upper()+".jpg")
        a["download_used"]=image_store.acquire(
            a["commons"], [a["url"]]+a.get("mirrors",[]), dest,
            minimum=tuple(a["expected_min"]), min_bytes=150000, ordered=True)
        assets[a["id"]]=dest
    music=cfg["music"];track=base/"ORIGINAL_LICENSED_MUSIC.mp3"
    fetch(music["url"],track,"audio",None)
    frames={k:Image.open(v).convert("RGB") for k,v in assets.items()}
    cinema.ARTIST=cfg["opening_text"]
    cinema.TITLE=cfg["title_en"]
    cinema.COMPOSER=music["artist"]
    cinema.STORY=[(s["kind"],s["x"],s["y"],s["z"],s["seconds"],s["motion"],s["purpose"]) for s in cfg["scenes"]]
    total=sum(s["seconds"] for s in cfg["scenes"])
    accents,analysis=cinema.audio_analysis(track,work,music["offset"],total+3)
    shots=cinema.align_shots(accents)
    clips=[]
    notes=["# Regia originale — Visions of Symbolism","","Three genuine paintings; a dream eye, an overwhelming god, then the silent island.",
           "No transparent overlap of any two paintings, no oscillation, no false AI repainting.",
           "The approved V6 opening and cover font, palette, band, music line and fade remain unchanged.","",
           "## Fourteen artwork-specific shots"]
    previews=Image.new("RGB",(4*320,4*560),(11,13,18))
    pen=ImageDraw.Draw(previews)
    t=0.
    for i,(s,shot) in enumerate(zip(cfg["scenes"],shots)):
        frame=frames[s["art"]]
        item=whole_image(frame) if s["kind"]=="full" else cinema.crop(frame,cinema.STORY[i])
        clips.append(cinema.render_clip(item,shot,i,work))
        thumb=item.resize((280,498),Image.Resampling.LANCZOS)
        px=(i%4)*320+20;py=(i//4)*560+10
        previews.paste(thumb,(px,py))
        pen.text((px,py+506),s["art"].upper()+" "+s["kind"],fill="white",
                 font=ImageFont.truetype(cinema.FONT2,19))
        notes.append(f"- {t:.2f}–{t+shot['duration']:.2f}s | {s['art']} | {s['kind']} | "
                     f"focal=({s['x']:.2f},{s['y']:.2f}) zoom={s['z']:.2f} "
                     f"motion={s['motion']}: {s['purpose']}")
        t+=shot["duration"]
        print("SCENE",i+1,s["art"],s["kind"],round(t,2),flush=True)
    previews.save(base/"STORYBOARD_REAL_ARTWORK.jpg",quality=91)
    (base/"TECNICHE_REGIA.md").write_text("\n".join(notes)+"\n",encoding="utf8")
    concat=work/"concat.txt"
    concat.write_text("".join("file '"+str(p.resolve())+"'\n" for p in clips),encoding="utf8")
    silent=work/"silent.mp4"
    run("ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",concat,"-c:v","copy",silent)
    duration=float(probe(silent)["format"]["duration"])
    if not 45<=duration<=120:raise RuntimeError("Unexpected duration "+str(duration))
    master=base/"VIDEO_MASTER.mp4"
    run("ffmpeg","-hide_banner","-loglevel","error","-y","-i",silent,
        "-ss",music["offset"],"-i",track,"-map","0:v:0","-map","1:a:0",
        "-c:v","copy","-af",f"aresample=48000,volume=0.9,afade=t=in:st=0:d=0.45,afade=t=out:st={duration-4:.2f}:d=4,loudnorm=I=-19:TP=-2:LRA=11",
        "-c:a","aac","-b:a","192k","-t",duration,"-movflags","+faststart",master)
    # Cover uses the same genuine Redon opening source and immutable V6 typography.
    coverframe=cinema.crop(frames["redon"],cinema.STORY[0])
    cinema.make_cover(coverframe,base/"COPERTINA.jpg")
    editorial.write_posts(cfg["editorial_key"],base,overwrite=False)
    errors=editorial.validate_folder(base)
    if errors:raise RuntimeError("V28_POST_BLOCKED: "+";".join(errors))
    (base/"ARTVISION_CONTRACT_V25.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    rights=["# Sources and verified rights","", "Three independent public-domain historical artworks (not an original triptych).",
            "Reproductions are sourced from Commons PD-Art pages; confirm local cultural-heritage and photography law before commercial reuse.",""]
    for a in cfg["artworks"]:
        rights += [f"## {a['artist']} — {a['title_en']} ({a['year']})",
                   "Museum: "+a["museum"],"Museum evidence: "+a["museum_url"],
                   "Image rights: Commons public-domain reproduction "+a["commons"],
                   "Original image downloaded: "+a.get("download_used",a["url"]),
                   "SHA256: "+sha(assets[a["id"]]),""]
    rights += ["## Soundtrack",f"{music['name']} — {music['artist']} (recording licensed CC BY 4.0)",
               "Recording source: "+music["url"],"License proof: "+music["page"],
               "License: "+music["license_url"],"ISRC: "+music["isrc"],
               "SHA256: "+sha(track),"Transformations: selected excerpt, fades, normalization.",
               "Attribution included in all four posts. Platform copyright check before publication.",""]
    (base/"SOURCES_AND_RIGHTS.md").write_text("\n".join(rights),encoding="utf8")
    recipe={"schema":"video-recipe-v13","video_id":cfg["slug"],"format":"artvision_cinema",
            "subtype":"artvision_collection","approved_baseline":"cinema_v6",
            "title_en":cfg["title_en"],"artist":" / ".join(a["artist"] for a in cfg["artworks"]),
            "renderer":"scripts/artvision_autoproduction_20261024_2015.py",
            "replication_command":"python scripts/artvision_autoproduction_20261024_2015.py --out output/artvision-v31-symbolist",
            "fps":FPS,"width":W,"height":H,"duration_measured_seconds":duration,
            "sha256_mp4":sha(master),"source_images":[{"id":a["id"],"sha256":sha(assets[a["id"]]),"url":a["url"]} for a in cfg["artworks"]],
            "music":{"source":music,"sha256":sha(track),"measured_audio_events":analysis},
            "scenes":[dict(shot,art=s["art"]) for shot,s in zip(shots,cfg["scenes"])],
            "transition":"opaque hard cuts only; no simultaneous scene overlays",
            "visual_preset":"modules/artvision/IDENTITA_VISIVA_FISSA_V6.json",
            "no_social_autopublish":True,"gold_master_approved":False}
    (base/"VIDEO_RECIPE_V13.json").write_text(json.dumps(recipe,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    release={"schema_version":1,"video":{"id":cfg["slug"],"format":"artvision_cinema","subtype":"collection"},
             "music":{"title":music["name"],"artist":music["artist"],"origin":"external_licensed",
                      "source_url":music["page"],"recording_proof_url":music["page"],
                      "license_name":music["license"],"license_url":music["license_url"],
                      "license_checked_on":"2026-10-24","allow_commercial":True,
                      "permitted_platforms":["facebook","instagram","tiktok","youtube"],
                      "credit_required":True,"music_embedded":True,
                      "credit_text":f'"{music["name"]}" Kevin MacLeod (incompetech.com) / CC BY 4.0 / {music["license_url"]}',
                      "music_source_sha256":sha(track)},
             "qa":{"music_fit_reviewed":False,"full_watch_listen":False,"audio_mix_reviewed":False,
                   "visual_rights_reviewed":False,"caption_ready":True,"originality_reviewed":False},
             "release":{"user_authorized_publication":False},
             "publish_status":"review_required"}
    (base/"MUSIC_RELEASE_V20.json").write_text(json.dumps(release,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    (base/"ISTRUZIONI_REPLICA.md").write_text(
       "# Replication — ArtVision Symbolist Visions V31\n\n"
       "From Android: GitHub Actions runs the Python 3.11 script in the repository.\n"
       "Command: python scripts/artvision_autoproduction_20261024_2015.py --out output/artvision-v31-symbolist\n"
       "Uses Pillow, numpy, requests, ffmpeg, ffprobe, and approved Cinema V6 signature.\n"
       "Inputs: config/artvision_autoproduction_20261024_2015.json and config/artvision_editorial_v28.json.\n"
       "Source hashes and exact shot timing are stored in VIDEO_RECIPE_V13.json.\n"
       "No changes to previously approved master files.\n"
       "The new video awaits human artistic review and has NOT been posted on social media.\n",encoding="utf8")
    qa_dir=base/"QA_V25";qa_dir.mkdir(exist_ok=True)
    timestamps=[0,1,3,5,7]+[round(duration*x,2) for x in (.23,.47,.68,.89)]
    contact=Image.new("RGB",(9*220,410),(10,12,17));draw=ImageDraw.Draw(contact)
    for i,sec in enumerate(timestamps):
        name=f"FRAME_{sec:02d}.jpg" if isinstance(sec,int) else f"SCENE_{sec:.2f}.jpg"
        p=qa_dir/name
        run("ffmpeg","-hide_banner","-loglevel","error","-y","-ss",sec,"-i",master,"-frames:v","1","-q:v","3",p)
        im=Image.open(p).convert("RGB").resize((216,384),Image.Resampling.LANCZOS)
        contact.paste(im,(i*220+2,0))
        draw.text((i*220+8,390),str(sec)+"s",fill="white")
    contact.save(base/"QA_CONTACT_SHEET.jpg",quality=90)
    run("ffmpeg","-hide_banner","-loglevel","error","-xerror","-i",master,"-f","null","-")
    media=probe(master)
    if not any(s.get("codec_type")=="video" and s.get("codec_name")=="h264" and s.get("width")==W and s.get("height")==H for s in media["streams"]):
        raise RuntimeError("Video codec/dimensions QA failure")
    if not any(s.get("codec_type")=="audio" and s.get("codec_name")=="aac" for s in media["streams"]):
        raise RuntimeError("Audio codec QA failure")
    report={"status":"TECHNICAL_PASS_ARTISTIC_REVIEW_PENDING","duration_seconds":float(media["format"]["duration"]),
            "size_bytes":master.stat().st_size,"sha256_mp4":sha(master),
            "full_ffmpeg_decode":True,"video_codec":"h264","audio_codec":"aac","size":[W,H],
            "frames_sampled":timestamps,"three_transition_examples":[round(duration*x,2) for x in (.23,.47,.68)],
            "no_transparent_cross_scene_blend":True,"v25_preflight":"PASS",
            "v28_editorial":"PASS_OBJECTIVE_CAPTION_CHECKS","approval":"human_visual_review_pending",
            "social_published":False}
    (base/"TECHNICAL_QA_V31.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    archive=Path(args.out)/"ARTVISION_V31_VISIONS_OF_SYMBOLISM_20261024_2015_COMPLETE.zip"
    with zipfile.ZipFile(archive,"w") as z:
        for p in base.rglob("*"):
            if not p.is_file() or "_work" in p.parts:continue
            method=zipfile.ZIP_STORED if p.suffix.lower() in (".mp4",".jpg",".mp3") else zipfile.ZIP_DEFLATED
            z.write(p,p.relative_to(base),compress_type=method)
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise RuntimeError("ZIP CRC failure")
    shutil.rmtree(work)
    print("MASTER_COMPLETE",json.dumps(report),str(archive),archive.stat().st_size,flush=True)
if __name__=="__main__":
    main()

# Workflow trigger: dedicated V31 production cycle, distinct from previous MP4.

# Editorial V28 exact collection credit verified before production.
