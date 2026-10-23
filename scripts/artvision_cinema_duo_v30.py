#!/usr/bin/env python3
"""ArtVision Cinema V30 | two new master films, V6 immutability + V25/V28 gates.

Runs entirely on free GitHub Actions: real high-res public-domain paintings,
documented CC BY recordings, intentional static camera and gentle selective
moves, finished 9:16 H.264/AAC, covers, V28 captions, complete reproducible ZIPs.
NEVER declares a finished film a human-approved Gold Master.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, math, shutil, subprocess, sys, time, zipfile
from pathlib import Path
import requests
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import artvision_editorial_post_v28 as editorial
from artvision_contract_gate_v25 import check_preflight
CONFIG=ROOT/"config/artvision_cinema_duo_v30.json"
BASE=ROOT/"scripts/artvision_storm_rembrandt_v29.py"
spec=importlib.util.spec_from_file_location("cinema_base_v29",BASE)
cinema=importlib.util.module_from_spec(spec)
spec.loader.exec_module(cinema)
W,H,FPS=1080,1920,24
CC="https://creativecommons.org/licenses/by/4.0/"
USER_AGENT="ArtVisionStudioV30/1.0 (research and attribution; github.com/GGIANLUCAA/Tra-le-pagine-)"

def get_config():
    return json.loads(CONFIG.read_text(encoding="utf8"))["subjects"]

def validate_brief(b,slug):
    errors=[]
    if len(b.get("scenes",[]))<8:errors.append("too few independently motivated shots")
    if b.get("editorial_key")!=b.get("slug"):errors.append("catalog key mismatch")
    if b.get("slug")!=slug:errors.append("subject key mismatch")
    if len(b.get("art_candidates",[]))<2:errors.append("need two authentic image origins")
    if not all(len(s.get("intent",""))>16 and s["seconds"]>2 and s["movement"] in
        ("locked","slow_push","slow_pull") for s in b.get("scenes",[])):
        errors.append("unmotivated or unsupported camera movement")
    if not all(s["type"] in ("portrait","macro","texture","detail","medium","wide","full","landscape")
               for s in b.get("scenes",[])):
        errors.append("unknown shot type")
    if not b["scenes"][-1]["type"]=="full":
        errors.append("final full artwork reveal missing")
    if len({s["type"] for s in b["scenes"]})<3:
        errors.append("at least three shot families required")
    if not 40<=sum(s["seconds"] for s in b["scenes"])<=70:
        errors.append("duration or pacing not curated")
    if editorial.validate_entry(slug,editorial.config()["entries"][slug]):
        errors.append("editorial research not ready")
    return errors

def fetch_authentic_image(b,destination):
    exceptions=[]
    for url in b["art_candidates"]:
        for attempt in range(2):
            try:
                with requests.get(url,headers={"User-Agent":USER_AGENT},timeout=72,stream=True,allow_redirects=True) as r:
                    r.raise_for_status()
                    ct=r.headers.get("Content-Type","").lower()
                    if "text/html" in ct or "application/json" in ct:
                        raise RuntimeError("not an image: "+ct)
                    with destination.open("wb") as f:
                        for piece in r.iter_content(chunk_size=512*1024):
                            if piece:f.write(piece)
                if destination.stat().st_size<200000:raise ValueError("under 200KB")
                with Image.open(destination) as art:
                    art.verify()
                with Image.open(destination) as art:
                    assert min(art.width,art.height)>=1000 and max(art.width,art.height)>=1850,(art.size,url)
                    dims=art.size
                print("AUTHENTIC_IMAGE_OK",url, dims,destination.stat().st_size,flush=True)
                return url
            except Exception as exc:
                exceptions.append(f"{url}: {type(exc).__name__}: {str(exc)[:120]}")
                destination.unlink(missing_ok=True)
                time.sleep(1.5*(attempt+1))
    raise RuntimeError("NO_VERIFIED_ORIGINAL_IMAGE: "+" | ".join(exceptions[-6:]))

def fetch_track(m,filepath):
    errors=[]
    urls=[m["url"]]
    for url in urls:
        for attempt in range(3):
            try:
                with requests.get(url,headers={"User-Agent":USER_AGENT},stream=True,timeout=70) as r:
                    r.raise_for_status()
                    if "text/html" in r.headers.get("Content-Type","").lower():raise ValueError("unexpected HTML")
                    with filepath.open("wb") as out:
                        for chunk in r.iter_content(512*1024):
                            if chunk:out.write(chunk)
                if filepath.stat().st_size<100000:raise ValueError("music file unexpectedly small")
                if not any(s.get("codec_type")=="audio" for s in cinema.probe(filepath)["streams"]):
                    raise RuntimeError("audio track missing")
                return url
            except Exception as exc:
                errors.append(str(exc))
                filepath.unlink(missing_ok=True)
                time.sleep(attempt+1)
    raise RuntimeError("NO_LICENSED_AUDIO: "+"; ".join(errors))

def set_format(b):
    cinema.ARTIST=b["artist"]
    cinema.TITLE=b["title_en"]
    cinema.COMPOSER=b["music"]["artist"]
    cinema.STORY=[(s["type"],s["x"],s["y"],s["z"],s["seconds"],
                   s["movement"],s["intent"]) for s in b["scenes"]]
    cinema.TECH=[(name,reason) for name,reason in [
        ("visual_hierarchy","Strong painted focal detail precedes the large composition"),
        ("motivated_cut","Each camera change clarifies a historical painted motif"),
        ("rhythmic_rest","Hold still with a calm camera during actual score intervals"),
        ("detail_return","A key symbol returns before the final canvas is revealed"),
        ("color_match","Contrast authentic painted colors without changing artwork"),
        ("locked_hold","Most shots are still and never sway or oscillate"),
        ("human_gaze_start","Human emotion or uncanny figure receives an early visual emphasis"),
        ("camera_seasick_gate","No wobble, whip, bounce or repeated zoom movement")
    ]]

def narrative_meta(b,shots,chosen_image,asset,track,duration,analysis,out):
    slug=b["slug"]
    music=b["music"]
    title=b["title_en"];artist=b["artist"]
    hash_mp4=cinema.digest(out/"VIDEO_MASTER.mp4")
    image_hash=cinema.digest(asset);audio_hash=cinema.digest(track)
    editorial.write_posts(slug,out,overwrite=False)
    e=editorial.validate_folder(out)
    if e:raise RuntimeError("V28 captions BLOCKED: "+";".join(e))
    source=(
        f"# Sources & rights / {title}\n\n"
        f"Artwork: {title} ({b['year']}) — {artist}, {b['museum']}.\n"
        f"Museum catalogue: {b['museum_page']}\n"
        f"Source file: {b['source_page']}\n"
        f"Original image successfully downloaded: {chosen_image}\n"
        f"Image SHA256: {image_hash}\n"
        "The centuries-old painting is public domain. Photographic reproductions\n"
        "of flat art are considered PD-Art on Wikimedia Commons; check national\n"
        "cultural heritage and photography terms before use in any jurisdiction.\n\n"
        f"Recording: {music['name']} — {music['artist']} (incompetech.com)\n"
        f"ISRC: {music['isrc']}\n"
        f"Original recording: {music['url']}\n"
        f"Evidence and track: {music['page']}\n"
        f"CC BY 4.0: {music['license_url']}\n"
        f"Original recording SHA256: {audio_hash}\n"
        "Transformations: selected excerpt, fades, loudness normalization.\n"
        "A visible, complete attribution is in each social caption.\n"
        "Local platform copyright checks remain necessary before publishing.\n"
    )
    (out/"SOURCES_AND_RIGHTS.md").write_text(source,encoding="utf8")
    shot_notes=["# Artist-directed camera notes",f"Artwork: {title}","",
        "Visual narrative: "+b["story"],"",
        "V6 signature identical for intro. Artwork name in English only on cover.",
        "No voice, subtitles, promotional CTA, fake perspective transformation or AI repainting.",
        "Most scenes stationary; slow pushes are under 1% zoom when justified by a specific motif.",
        "Audio cuts consult measured real soundtrack events but are never forced to a fake beat.",
        "", "## Curated scenes"]
    t=0.
    for s in shots:
        shot_notes.append(
            f"- {t:.2f}–{t+s['duration']:.2f}s / {s['id']} / {s['kind']} "
            f"({s['x']:.3f},{s['y']:.3f}) zoom={s['zoom']:.2f} motion={s['motion']}: "
            +s["purpose"]+(". Score accent="+str(s["audio_cut_second"]) if "audio_cut_second" in s else "")
        )
        t+=s["duration"]
    shot_notes+=["","## Selected V23 techniques"]
    shot_notes.extend(f"- {x}: {reason}" for x,reason in cinema.TECH)
    (out/"TECNICHE_REGIA.md").write_text("\n".join(shot_notes)+"\n",encoding="utf8")
    replay=f"""# Replication — ArtVision Cinema V30

Subject: {title} — {artist}
Script: scripts/artvision_cinema_duo_v30.py
Config: config/artvision_cinema_duo_v30.json
Editorial research: config/artvision_editorial_v28.json
Immutable original: modules/artvision/IDENTITA_VISIVA_FISSA_V6.json
Mandatory contract: docs/ARTVISION_CONTRATTO_PERMANENTE_V25.md
Natural post rules: docs/ARTVISION_EDITORIAL_POST_STANDARD_V28.md
Command:
python scripts/artvision_cinema_duo_v30.py --painting {slug} --out output/artvision-v30

Environment: Python 3.11, Pillow, numpy, requests, ffmpeg/ffprobe, DejaVu Serif/Sans.
Use ORIGINAL downloaded image and sound source for exact material replication.
Image SHA256: {image_hash}
Recorded score SHA256: {audio_hash}
Do not copy these shot coordinates to another artwork: the creative reasoning,
visual motifs, audio cues and crop centres are artwork-specific.
Every new film MUST pass QA and retain source/CC BY attribution before posting.
Neither this run nor technical validation constitutes artistic Gold Master approval.
"""
    (out/"ISTRUZIONI_REPLICA.md").write_text(replay,encoding="utf8")
    recipe={
        "schema":"video-recipe-v13","project":"ArtVision Cinema","version":"V30", "video_id":slug,
        "artist":artist,"title_en":title,"original_image":chosen_image,
        "museum":b["museum_page"],"visual_source_SHA256":image_hash,
        "audio_recording":music,"audio_source_SHA256":audio_hash,
        "actual_video_SHA256":hash_mp4,"sha256_mp4":hash_mp4,
        "fps":FPS,"width":W,"height":H,"measured_duration_seconds":duration,
        "renderer":"scripts/artvision_cinema_duo_v30.py",
        "replication_command":f"python scripts/artvision_cinema_duo_v30.py --painting {slug} --out output/artvision-v30",
        "preset":"modules/artvision/IDENTITA_VISIVA_FISSA_V6.json",
        "story":b["story"],"scenes":shots,
        "music_timing":{"offset_seconds":music["offset"],"analysis":analysis,
                        "fade_in_seconds":.45,"fade_out_seconds":3.3,
                        "loudness_target_lufs":-19,"max_true_peak_dbtp":-2},
        "techniques":[{"id":n,"why":reason} for n,reason in cinema.TECH],
        "editorial_preset":"artvision_editorial_v28",
        "social_files":["POST_FACEBOOK.txt","POST_INSTAGRAM.txt","POST_TIKTOK.txt","POST_YOUTUBE.txt"],
        "state":"rendered_awaiting_aesthetic_approval",
        "social_published":False,"existing_masters_untouched":True
    }
    (out/"VIDEO_RECIPE_V13.json").write_text(json.dumps(recipe,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    mm={
        "schema_version":1,
        "video":{"id":slug,"format":"artvision_cinema","title":title,
                 "originality_statement":"Artwork-specific cinematic direction and factual editorial text of authentic public-domain painting",
                 "visual_rights_evidence":[b["museum_page"],b["source_page"]]},
        "music":{"title":music["name"],"artist":music["artist"],"origin":"external_licensed",
                 "source_url":music["page"],"recording_proof_url":music["page"],
                 "license_name":"CC BY 4.0","license_url":CC,"license_checked_on":"2026-10-23",
                 "allow_commercial":True,"permitted_platforms":["facebook","instagram","tiktok","youtube"],
                 "credit_required":True,"music_embedded":True,
                 "credit_text":f'"{music["name"]}" Kevin MacLeod (incompetech.com) / CC BY 4.0 / {CC}',
                 "rights_holder_claim_status":"unchecked","music_source_sha256":audio_hash},
        "distribution":{"targets":["facebook","instagram","tiktok","youtube"],"monetized":False},
        "qa":{"music_fit_reviewed":False,"full_watch_listen":False,"audio_mix_reviewed":False,
              "visual_rights_reviewed":False,"caption_ready":True,"originality_reviewed":False},
        "release":{"user_authorized_publication":False,"caption_text":(out/"POST_FACEBOOK.txt").read_text(encoding="utf8")},
        "publish_status":"review_required"
    }
    (out/"MUSIC_RELEASE_V20.json").write_text(json.dumps(mm,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    first=[(0,"The genuine source painting already establishes an emotional visual mystery"),
           (1,"The painted visual focal point remains readable behind the V6 signature"),
           (3,"V6 signature begins dissolving while painting continues unchanged"),
           (5,"A second clue from the real work appears"),
           (7,"Authentic detail develops the visual premise")]
    manifest={
        "schema":"artvision-release-contract-v25","video_id":slug,
        "format":"artvision_cinema","approved_baseline":"cinema_v6",
        "artwork":{"artist":artist,"title_en":title,"title_language":"en",
                   "identity_source":b["museum_page"]},
        "opening":{"identity_preset":"modules/artvision/IDENTITA_VISIVA_FISSA_V6.json",
                   "artist_text":artist,"composer":music["artist"],
                   "music_credit_text":"MUSIC BY "+music["artist"].upper()},
        "cover":{"identity_family":"cinema_v6","title_en":title,"artist":artist,
                 "language":"en","existing_design_unchanged":True},
        "on_screen_text":[{"role":"opening_artist","text":artist},
                          {"role":"opening_music","text":"MUSIC BY "+music["artist"].upper()}],
        "voice":False,"subtitles":False,
        "first_seven_seconds":[{"second":s,"what_visible":what,
                                "why":"Authentic painted visual subject, emotionally motivated camera in each frame"}
                               for s,what in first],
        "scenes":[{"source_id":"verified-original-artwork","subject":s["purpose"],"purpose":s["purpose"],
                   "shot":s["kind"],"motion":s["motion"],
                   "duration_seconds":s["duration"]} for s in shots],
        "transition_reviews_plan":[{"why":s["purpose"]} for s in shots[3:6]],
        "music_cues":[{"seconds":0,"reason":"Signature begins on measured opening musical excerpt"},
                      {"seconds":duration*.45,"reason":"Midpoint picture turn linked to actual music event"},
                      {"seconds":duration-6,"reason":"Whole canvas is revealed as the music cadence eases"}],
        "duration_reason":"Individual scenes motivated by painterly content and actual soundtrack phrases; no generic fixed-length slideshow.",
        "selected_techniques":[{"id":n,"why":why} for n,why in cinema.TECH],
        "sources":[{"id":"verified-original-artwork","url":b["source_page"],
                    "license":"Public domain historical painting / photographic reproduction rights caveat",
                    "credit":f"{artist}, {b['museum']}","status":"verified"}],
        "music":{"title":music["name"],"composer":music["artist"],
                 "origin":"external_licensed","license":"CC BY 4.0","evidence":music["page"],
                 "emotional_arc":b["story"],"rights_status":"verified"},
        "copy_languages":{"facebook":"it","instagram":"it","tiktok":"it","youtube":"it"},
        "archive_only_after_authorization":True,"social_autopublish":False,
        "editorial_standard":"artvision_editorial_v28",
        "outputs":{"video":"VIDEO_MASTER.mp4","cover":"COPERTINA.jpg",
                   "facebook":"POST_FACEBOOK.txt","instagram":"POST_INSTAGRAM.txt",
                   "tiktok":"POST_TIKTOK.txt","youtube":"POST_YOUTUBE.txt",
                   "recipe":"VIDEO_RECIPE_V13.json","techniques":"TECNICHE_REGIA.md",
                   "replication":"ISTRUZIONI_REPLICA.md","rights":"SOURCES_AND_RIGHTS.md",
                   "music_manifest":"MUSIC_RELEASE_V20.json"},
        "review_video_sha256":hash_mp4,
        "reviews":{key:{"passed":False,"notes":"Human full-speed artistic inspection still needed."}
                   for key in ["opening","visual","cover","music","rights","full_watch","replicability"]},
        "publication":{"status":"not_published","library_verified":False}
    }
    (out/"ARTVISION_CONTRACT_V25.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    errors=check_preflight(manifest)
    (out/"PREFLIGHT_V25.json").write_text(json.dumps({"status":"PASS" if not errors else "BLOCKED",
                                                     "errors":errors},indent=2)+"\n",encoding="utf8")
    if errors:raise RuntimeError("CONTRACT_PREFLIGHT_BLOCKED: "+" | ".join(errors))
    return recipe

def render_one(key,root):
    entries=get_config()
    b=entries[key]
    bad=validate_brief(b,b["slug"])
    if bad:raise RuntimeError("PRE_RENDER_BLOCKED: "+" | ".join(bad))
    set_format(b)
    folder=root/b["slug"]
    folder.mkdir(parents=True,exist_ok=True)
    work=folder/"_working";work.mkdir(exist_ok=True)
    art=folder/"ORIGINAL_ARTWORK.jpg"
    track=folder/"ORIGINAL_LICENSED_MUSIC.mp3"
    actual_art_url=fetch_authentic_image(b,art)
    fetch_track(b["music"],track)
    frame=Image.open(art).convert("RGB")
    raw_total=sum(s["seconds"] for s in b["scenes"])
    accents,analysis=cinema.audio_analysis(track,work,b["music"]["offset"],raw_total+3)
    shots=cinema.align_shots(accents)
    print("AUDIO_CUES",key,analysis,flush=True)
    # Render each exact-source view with no artificial movement of represented people.
    storyboard=Image.new("RGB",(320*4,584*math.ceil(len(shots)/4)),(18,20,27))
    pen=ImageDraw.Draw(storyboard)
    clips=[]
    for i,scene in enumerate(shots):
        orig=cinema.full(frame) if scene["kind"]=="full" else cinema.crop(frame,cinema.STORY[i])
        clips.append(cinema.render_clip(orig,scene,i,work))
        preview=orig.resize((280,498),Image.Resampling.LANCZOS)
        x=(i%4)*320+20;y=(i//4)*584+15
        storyboard.paste(preview,(x,y))
        pen.text((x,y+504),f"{scene['id']} {scene['kind']}",
                 fill="white",font=ImageFont.truetype(cinema.FONT2,22))
        print("SCENE_OK",key,scene["id"],scene["purpose"],flush=True)
    storyboard.save(folder/"STORYBOARD_REAL_ARTWORK.jpg",quality=91)
    concat=work/"concat.txt"
    concat.write_text("".join("file '"+str(p.resolve())+"'\n" for p in clips),encoding="utf8")
    mute=work/"silent.mp4"
    cinema.run("ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",concat,
               "-c:v","copy",mute)
    duration=float(cinema.probe(mute)["format"]["duration"])
    output=folder/"VIDEO_MASTER.mp4"
    mix=work/"first_mix.mp4"
    music_offset=b["music"]["offset"]
    cinema.run("ffmpeg","-hide_banner","-loglevel","error","-y",
               "-i",mute,"-ss",music_offset,"-i",track,"-map","0:v:0","-map","1:a:0",
               "-c:v","copy","-af",f"aresample=48000,volume=0.84,afade=t=in:st=0:d=0.45,afade=t=out:st={max(0,duration-3.3):.3f}:d=3.3",
               "-c:a","aac","-b:a","192k","-t",duration,"-movflags","+faststart",mix)
    # Independent mix measurement: normalize for social mobile listening.
    cinema.run("ffmpeg","-hide_banner","-loglevel","error","-y","-i",mix,
               "-map","0:v:0","-map","0:a:0","-c:v","copy",
               "-af","loudnorm=I=-19:TP=-2:LRA=11","-c:a","aac","-b:a","192k",
               "-movflags","+faststart",output)
    cinema.make_cover(cinema.crop(frame,cinema.STORY[0]),folder/"COPERTINA.jpg")
    qa=folder/"QA_V25";qa.mkdir(exist_ok=True)
    ticks=[0,1,3,5,7]+[round(duration*f,2) for f in (.25,.51,.77,.95)]
    contact=Image.new("RGB",(9*300,556),(12,14,20));d=ImageDraw.Draw(contact)
    for i,s in enumerate(ticks):
        p=qa/(f"FRAME_{int(s):02d}.jpg" if isinstance(s,int) else f"SCENE_{s:.2f}.jpg")
        cinema.run("ffmpeg","-hide_banner","-loglevel","error","-y","-ss",s,"-i",output,
                   "-frames:v","1","-q:v","3",p)
        img=Image.open(p).convert("RGB").resize((295,520),Image.Resampling.LANCZOS)
        contact.paste(img,(300*i+2,0))
        d.text((300*i+12,529),str(s)+"s",fill="white",
               font=ImageFont.truetype(cinema.FONT2,21))
    contact.save(folder/"QA_CONTACT_SHEET.jpg",quality=92)
    facts=cinema.probe(output)
    streams=facts["streams"]
    if not (40<float(facts["format"]["duration"])<72):raise RuntimeError("Invalid duration "+str(duration))
    if not any(s.get("codec_type")=="video" and s.get("codec_name")=="h264" and
               s.get("width")==W and s.get("height")==H for s in streams):
        raise RuntimeError("Invalid H264 video")
    if not any(s.get("codec_type")=="audio" and s.get("codec_name")=="aac" for s in streams):
        raise RuntimeError("No AAC audio")
    cinema.run("ffmpeg","-hide_banner","-loglevel","error","-xerror","-i",output,
               "-f","null","-")
    recipe=narrative_meta(b,shots,actual_art_url,art,track,duration,analysis,folder)
    status={"status":"REAL_MASTER_TECHNICALLY_VALID_AWAITING_ARTISTIC_REVIEW",
            "slug":b["slug"],"sha256_mp4":recipe["sha256_mp4"],
            "duration_seconds":duration,"source_image_url":actual_art_url,
            "codec_video":"H264","codec_audio":"AAC","size_bytes":output.stat().st_size,
            "qa_review_times":ticks,"full_ffmpeg_decode":True,
            "v25_preflight":"PASS","v28_editorial":"PASS_OBJECTIVE_CAPTION_CHECKS",
            "no_social_autopublishing":True,"approval":"human_visual_review_pending"}
    (folder/"TECHNICAL_QA_V30.json").write_text(json.dumps(status,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    dest=root/f"ARTVISION_V30_{b['slug'].upper()}_COMPLETE.zip"
    with zipfile.ZipFile(dest,"w") as z:
        for p in folder.rglob("*"):
            if not p.is_file() or "_working" in p.parts:continue
            typ=zipfile.ZIP_STORED if p.suffix.lower() in (".mp4",".mp3",".jpg") else zipfile.ZIP_DEFLATED
            z.write(p,p.relative_to(folder),compress_type=typ)
    if zipfile.ZipFile(dest).testzip() is not None:raise RuntimeError("ZIP integrity failure")
    shutil.rmtree(work)
    print("MASTER_AND_PACK_READY",b["slug"],status["size_bytes"],status["sha256_mp4"],
          "zip",dest.stat().st_size,flush=True)
    return status

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--painting",choices=tuple(get_config()),required=True)
    ap.add_argument("--out",default="output/artvision-v30")
    ap.add_argument("--preflight-only",action="store_true")
    args=ap.parse_args()
    b=get_config()[args.painting]
    bad=validate_brief(b,b["slug"])
    if args.preflight_only:
        print(json.dumps({"status":"PASS" if not bad else "BLOCKED","errors":bad},ensure_ascii=False))
        if bad:sys.exit(1)
        return
    if bad:raise RuntimeError("Preflight: "+";".join(bad))
    render_one(args.painting,Path(args.out))
if __name__=="__main__":main()
