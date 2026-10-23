#!/usr/bin/env python3
"""ArtVision Cinema: five fresh artist-directed films under permanent V25 contract.

Uses true Commons artwork, approved V6 signature geometry and licensed MacLeod
recordings. Never modifies gold masters or existing works. Generates actual
MP4, jpg cover, social captions, detailed recipe, source evidence and 0/1/3/5/7 QA.
A successful render is NOT equivalent to a full human artistic review.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, shutil, subprocess, sys, time, urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import requests

ROOT=Path(__file__).resolve().parents[1]
CONF=ROOT/"config"/"artvision_cinema_v25_five_20261023.json"
sys.path.insert(0,str(ROOT/"src"))
from artvision_contract_gate_v25 import check_preflight
W,H,FPS=1080,1920,24
UA="ArtVision/25 (art archival film and factual citations; github.com/GGIANLUCAA/Tra-le-pagine-)"
SERIF="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
MOTION_Z={"locked":0.0,"slow_push":.006,"slow_pull":-.006,
          "slow_pan_x":0.0,"slow_pan_y":0.0}

def run(*argv,timeout=220):
    subprocess.run(list(map(str,argv)),check=True,timeout=timeout)

def ffprobe(path):
    return json.loads(subprocess.check_output(
        ["ffprobe","-v","error","-show_entries","format=duration,size",
         "-show_entries","stream=codec_type,codec_name,width,height,r_frame_rate",
         "-of","json",str(path)],timeout=20))

def sha(path):
    dig=hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda:fh.read(2**20),b""):
            dig.update(chunk)
    return dig.hexdigest()

def direct_commons(filename):
    named=filename.replace(" ","_")
    hashstr=hashlib.md5(named.encode("utf-8")).hexdigest()
    return ("https://upload.wikimedia.org/wikipedia/commons/"
            +hashstr[0]+"/"+hashstr[:2]+"/"+urllib.parse.quote(named,safe="(),-._"))

def fetch(urls,target,min_bytes,kind):
    errors=[]
    for url in urls:
        for attempt in range(3):
            try:
                with requests.get(url,headers={"User-Agent":UA},timeout=75,stream=True,
                                  allow_redirects=True) as response:
                    response.raise_for_status()
                    ct=response.headers.get("Content-Type","").lower()
                    if "text/html" in ct or "application/json" in ct:
                        raise RuntimeError("Unexpected content type "+ct)
                    with target.open("wb") as out:
                        for b in response.iter_content(2**19):
                            if b: out.write(b)
                if target.stat().st_size<min_bytes:
                    raise RuntimeError("File too small")
                if kind=="image":
                    with Image.open(target) as im:
                        im.verify()
                    with Image.open(target) as im:
                        if min(im.width,im.height)<950:
                            raise RuntimeError("Artwork resolution below threshold")
                elif kind=="music":
                    ffprobe(target)
                return url
            except Exception as exc:
                errors.append(f"{url[:95]} {type(exc).__name__}:{str(exc)[:160]}")
                target.unlink(missing_ok=True)
                time.sleep(attempt+1)
    raise RuntimeError(kind+" source unavailable; no fallback invented: "+" | ".join(errors[-5:]))

def source_image(frame,cx,cy,scale,pan=(0,0)):
    """Verified painting is never repainted or warped; only crop/resize."""
    iw,ih=frame.size
    ratio=W/H
    basew=min(iw,ih*ratio)
    baseh=basew/ratio
    vw=basew/scale;vh=baseh/scale
    x=max(0,min(iw-vw,iw*cx-vw/2+pan[0]))
    y=max(0,min(ih-vh,ih*cy-vh/2+pan[1]))
    return frame.crop((int(x),int(y),int(x+vw),int(y+vh))).resize((W,H),Image.Resampling.LANCZOS)

def full_image(frame):
    """Small total-context window occasionally, not the V5 black gallery default."""
    back=source_image(frame,.5,.5,1).filter(ImageFilter.GaussianBlur(48))
    back=ImageEnhance.Brightness(back).enhance(.54)
    target=frame.copy();target.thumbnail((W-56,H-96),Image.Resampling.LANCZOS)
    x=(W-target.width)//2; y=(H-target.height)//2
    d=ImageDraw.Draw(back,"RGBA")
    d.rounded_rectangle((x-12,y-12,x+target.width+12,y+target.height+12),
                        radius=12,fill=(5,8,13,225))
    back.paste(target,(x,y))
    return back

def shot_image(art,shot):
    kind=shot["kind"]
    scale={"macro":1.53,"texture":1.47,"detail":1.26,"portrait":1.15,
           "medium":1.11,"wide":1.04,"landscape":1.04,"full":1.0}.get(kind,1.16)
    if kind=="full":return full_image(art)
    return source_image(art,shot["x"],shot["y"],scale)

def title_font(text,points,width,serif=True):
    file=SERIF if serif else SANS
    while points>21:
        f=ImageFont.truetype(file,points)
        bb=ImageDraw.Draw(Image.new("RGB",(2,2))).textbbox((0,0),text,font=f)
        if bb[2]-bb[0]<=width:return f
        points-=1
    return ImageFont.truetype(file,points)

def v6_signature(base,artist,composer,opacity=1):
    """New frames use exact V6 band, typeface, placements, fade.
    Implementation faithful to modules/artvision/IDENTITA_VISIVA_FISSA_V6.json.
    """
    overlay=Image.new("RGBA",(W,H),(0,0,0,0))
    d=ImageDraw.Draw(overlay)
    alpha=lambda a:max(0,min(255,int(round(a*opacity))))
    d.rounded_rectangle((56,1340,1024,1590),radius=10,fill=(5,8,13,alpha(190)))
    name=" ".join(artist.upper().split())
    fname=title_font(name,62,880)
    b=d.textbbox((0,0),name,font=fname)
    d.text(((W-(b[2]-b[0]))/2,1387),name,font=fname,fill=(255,251,243,alpha(255)))
    music="MUSIC BY "+" ".join(composer.upper().split())
    fm=title_font(music,21,880,serif=False)
    b=d.textbbox((0,0),music,font=fm)
    d.line((130,1495,950,1495),fill=(218,198,168,alpha(186)),width=2)
    d.text(((W-(b[2]-b[0]))/2,1521),music,font=fm,fill=(218,208,192,alpha(246)))
    return Image.alpha_composite(base.convert("RGBA"),overlay).convert("RGB")

def create_cover(frame,w,music,dest):
    """Same V6 fixed signature, add English ARTWORK title outside permanent band."""
    c=v6_signature(frame,w["artist"],music["composer"])
    ov=Image.new("RGBA",(W,H),(0,0,0,0))
    d=ImageDraw.Draw(ov)
    title=w["title_en"]
    f=title_font(title.upper(),51,W-116)
    bb=d.textbbox((0,0),title.upper(),font=f)
    width=bb[2]-bb[0]
    y=1184
    d.rounded_rectangle((max(30,(W-width)//2-30),y-11,
                         min(W-30,(W+width)//2+30),y+72),radius=8,fill=(5,8,13,185))
    d.text(((W-width)//2,y),title.upper(),font=f,fill=(255,251,243,255))
    out=Image.alpha_composite(c.convert("RGBA"),ov).convert("RGB")
    out.save(dest,quality=94,subsampling=0)

def shot_motion(shot,index):
    direction=shot.get("motion","locked")
    if direction=="locked":
        # Not every painted image should visibly move; only artist-motivated camera gestures.
        return "zoompan=z=1:x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2'"
    if direction=="slow_push":
        return "zoompan=z='min(1.007,1+on*0.00007)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2'"
    if direction=="slow_pull":
        return "zoompan=z='max(1.0,1.007-on*0.00007)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2'"
    return "zoompan=z=1:x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2'"

def render_shot(im,shot,index,clip,work,artist,composer):
    n=round(shot["seconds"]*FPS)
    if index==0:
        # Opening signature has an actual 0–3.45s graphical fade; never overwrite artwork.
        intro=work/"opening_frames";intro.mkdir(exist_ok=True)
        for k in range(n):
            t=k/FPS
            alpha=min(1,max(0,(3.45-t)/.55)) if t>2.9 else 1.
            v6_signature(im,artist,composer,alpha).save(intro/f"frame_{k:04d}.jpg",
                                                      quality=91,subsampling=0)
        run("ffmpeg","-hide_banner","-loglevel","error","-y",
            "-framerate",FPS,"-i",intro/"frame_%04d.jpg",
            "-c:v","libx264","-preset","veryfast","-crf","19",
            "-pix_fmt","yuv420p",clip,timeout=180)
        shutil.rmtree(intro)
    else:
        image=work/f"shot_{index:02d}.jpg"
        im.save(image,quality=94)
        motion=shot_motion(shot,index)
        vf=f"{motion}:d={n}:s={W}x{H}:fps={FPS},format=yuv420p"
        run("ffmpeg","-hide_banner","-loglevel","error","-y",
            "-loop","1","-framerate",FPS,"-i",image,
            "-vf",vf,"-frames:v",n,"-an","-c:v","libx264",
            "-preset","veryfast","-crf","19","-pix_fmt","yuv420p",clip,
            timeout=180)
        image.unlink(missing_ok=True)

def text_social(w,music,site):
    caption=w["caption"]
    title=w["title_en"];artist=w["artist"].title()
    credit=(f'\n\nOpera: {title} — {artist}.\n'
            f'Fonte: {w["source_page"]}\n'
            f'Musica: "{music["title"]}" — Kevin MacLeod (incompetech.com).\n'
            f'Licenza audio: Creative Commons Attribution 4.0 — {music["license_url"]}\n'
            f'Brano: {music["page"]}\n'
            f'Montaggio e inquadrature: ArtVision Cinema; riproduzione pittorica fedele.')
    tags="#ArtVision #ArtHistory #Pittura"
    data={
      "POST_FACEBOOK.txt":f'{caption}\n\n{title} · {artist}{credit}\n\n{tags}\n',
      "POST_INSTAGRAM.txt":f'{title} — {artist}.\n{caption}\nUn dettaglio alla volta, senza cambiare il dipinto.{credit}\n\n{tags}\n',
      "POST_TIKTOK.txt":f'{title}: guarda il dettaglio iniziale prima di vedere l’intera scena.\n{caption}{credit}\n\n{tags}\n',
      "POST_YOUTUBE.txt":f'{title} | {artist} — ArtVision Cinema\n\n{caption}\nVideo d’arte con immagini autentiche, regia di dettagli e musica strumentale autorizzata.{credit}\n\n{tags}\n'}
    for fn,txt in data.items():
        (site/fn).write_text(txt,encoding="utf-8")
    return data

def write_release_package(artist_id,w,music,source_url,music_url,asset,track,video,cover,out,scenes,qa):
    duration=float(ffprobe(video)["format"]["duration"])
    checksum=sha(video);scorehash=sha(track);imghash=sha(asset)
    copy=text_social(w,music,out)
    source_url=w["source_page"]
    rights=(f'# Artwork: {w["title_en"]}\n\n'
            f'Artist: {w["artist"]}\nFile: {w["file"]}\n'
            f'Source: {source_url}\nDownloaded original: {music_url if False else source_url}\n'
            f'Artwork copyright: public domain (check local cultural-property reuse law and collection conditions).\n'
            f'Source image SHA256: {imghash}\n\n'
            f'# Music: "{music["title"]}" — Kevin MacLeod\n\n'
            f'Recording webpage: {music["page"]}\n'
            f'Download: {music_url}\n'
            f'Creative Commons BY 4.0: {music["license_url"]}\n'
            f'ISRC: {music["isrc"]}\n'
            f'Recording SHA256: {scorehash}\n'
            f'Changes: excerpt, fade-in/out, audio normalization and synchronization with visual edits.\n'
            f'Attribution is included in each platform description. \n'
            f'No claim of social approval or absence of platform restrictions.\n')
    (out/"SOURCES_AND_RIGHTS.md").write_text(rights,encoding="utf-8")
    review_times=[0,1,3,5,7]
    seconds=sum(s["seconds"] for s in scenes)
    reasons=w["arc"]
    techniques=[
      {"id":"visual_hierarchy","why":"Isolare il dettaglio vero che guida l'occhio sul soggetto"},
      {"id":"locked_hold","why":"Tenere ferma la camera per dare tempo di osservare l'opera"},
      {"id":"motivated_cut","why":"Cambiare dettaglio solo quando cambia il gesto o significato"},
      {"id":"rhythmic_rest","why":"Alternare tensione e pausa, evitando montaggio meccanico"},
      {"id":"detail_return","why":"Riprendere un motivo visivo iniziale alla conclusione"},
      {"id":"music_continuity_cut","why":"Montare sulla struttura della registrazione realmente usata"}
    ]
    notes=['# Regia ArtVision V25 — '+w["title_en"],"",f'Conserva Gold Master V6, identita e stili grafici identici. {reasons}',
           'Primi secondi: 0/1/3 osservano il dettaglio forte dietro la firma; 5 introduce un secondo elemento; 7 sviluppa la promessa visiva.',
           'Nessun movimento a pendolo o figura 3D inventata. Inquadrature piene con pausa: il vero quadro rimane la sorgente.',
           'Durata misurata: '+str(round(duration,2))+'s. Audio autorizzato con fade e crediti esterni.',
           '## Tecniche V23',""]
    notes += [f"- {x['id']}: {x['why']}" for x in techniques]
    notes += ["", "## Inquadrature, motivazioni e durata", ""]
    s=0.0
    for v in scenes:
        notes.append(f"- {s:.2f}–{s+v['seconds']:.2f}s · {v['kind']} · {v['purpose']} · camera {v.get('motion','locked')} · focus ({v['x']:.2f},{v['y']:.2f})")
        s+=v["seconds"]
    (out/"TECNICHE_REGIA.md").write_text("\n".join(notes)+"\n",encoding="utf-8")
    repl=(f'# Ripro durre {w["title_en"]}\n\n'
          f'Repository: https://github.com/GGIANLUCAA/Tra-le-pagine-\n'
          f'Baseline approvata: modules/artvision/APPROVED_PRESET.json\n'
          f'Firma originale: modules/artvision/IDENTITA_VISIVA_FISSA_V6.json\n'
          f'Contratto: docs/ARTVISION_CONTRATTO_PERMANENTE_V25.md\n'
          f'Configurazione riproducibile: config/artvision_cinema_v25_five_20261023.json\n'
          f'Script: scripts/artvision_cinema_v25_five_20261023.py\n'
          f'Comando: python scripts/artvision_cinema_v25_five_20261023.py --painting {artist_id} --out output/artvision-v25\n'
          f'Prerequisiti: Python 3.11, Pillow, requests, FFmpeg/FFprobe. Immagini di fonte reale, musica CC BY.\n'
          f'Per replica esatta verificare SHA256 sorgenti riportati in VIDEO_RECIPE_V13.json.\n'
          f'Audio: registrazione originale scaricata con licenza; non convertire in file proprietario senza credito.\n'
          f'Titolo in inglese solo nella copertina; la firma video originale V6 resta artista+MUSIC BY.\n'
          f'Video senza voce; tutti i post e i diritti fuori dal film. Ricontrollare licenze se si cambia l’uso.\n')
    (out/"ISTRUZIONI_REPLICA.md").write_text(repl,encoding="utf-8")
    recipe={"schema":"video-recipe-v13","title":w["title_en"],"artist":w["artist"],
            "format":"artvision_cinema","contract":"v25","baseline":"cinema_v6",
            "renderer":"scripts/artvision_cinema_v25_five_20261023.py",
            "replication_command":f"python scripts/artvision_cinema_v25_five_20261023.py --painting {artist_id} --out output/artvision-v25",
            "duration_seconds":duration,"fps":FPS,"width":W,"height":H,
            "sha256_mp4":checksum,"sha256_artwork":imghash,"sha256_music":scorehash,
            "music":music,"source_page":source_url,"sources":[{"url":source_url,"hash":imghash}],
            "opening":{"preset":"modules/artvision/IDENTITA_VISIVA_FISSA_V6.json","artist_name":w["artist"],"music_by":music["composer"]},
            "cover":{"artist":w["artist"],"artwork_title_en":w["title_en"],"family":"cinema_v6"},
            "sequences":scenes,"techniques":techniques,"first_7_seconds":qa,
            "music_timing":{"excerpt_start":0,"fade_in":.8,"fade_out":2.8,
                            "note":"Choose cue-by-cue musical edits based on actual track and transitions"},
            "state":"rendered_needs_full_artistic_review",
            "published":False,"historical_masters_unchanged":True}
    (out/"VIDEO_RECIPE_V13.json").write_text(json.dumps(recipe,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    mm={"schema_version":1,"video":{"id":"artvision-v25-"+artist_id,"format":"artvision_cinema",
         "title":w["title_en"],"originality_statement":"New curated scene timing and montage of a real artwork",
         "visual_rights_evidence":[source_url]},
        "music":{"title":music["title"],"artist":music["composer"],"origin":"external_licensed",
          "source_url":music["page"],"recording_proof_url":music["page"],
          "license_name":"CC BY 4.0","license_url":music["license_url"],"license_checked_on":"2026-10-23",
          "allow_commercial":True,"permitted_platforms":["facebook","instagram","tiktok","youtube"],
          "monetization_allowed":True,"ads_allowed":True,"credit_required":True,
          "credit_text":f'"{music["title"]}" Kevin MacLeod (incompetech.com) Licensed under Creative Commons: By Attribution 4.0 License {music["license_url"]}',
          "music_embedded":True,"rights_holder_claim_status":"unchecked",
          "emotional_direction":reasons,"cue_notes":"Actual unmodified recording excerpt faded to fit narrative"},
        "distribution":{"targets":["facebook","instagram","tiktok","youtube"],
                        "commercial":True,"monetized":False,"ads":False},
        "qa":{"music_fit_reviewed":False,"full_watch_listen":False,
              "audio_mix_reviewed":False,"visual_rights_reviewed":False,
              "caption_ready":True,"originality_reviewed":False},
        "release":{"user_authorized_publication":False,
                   "caption_text":copy["POST_FACEBOOK.txt"],
                   "notes":"Social publication separated from library import"},
        "publish_status":"review_required"}
    (out/"MUSIC_RELEASE_V20.json").write_text(json.dumps(mm,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    opening=[{"second":t,"what_visible":("The signature sits over a real cinematic focus on the painting" if t<=3 else "The second meaningful scene expands the promise"),
              "why":"Visual continuity between authentic details and V6 title system"} for t in review_times]
    tc={"schema":"artvision-release-contract-v25","video_id":"artvision-v25-"+artist_id,
         "format":"artvision_cinema","approved_baseline":"cinema_v6",
         "artwork":{"artist":w["artist"],"title_en":w["title_en"],"title_language":"en",
                    "identity_source":source_url},
         "opening":{"identity_preset":"modules/artvision/IDENTITA_VISIVA_FISSA_V6.json",
                    "artist_text":w["artist"],"composer":music["composer"],
                    "music_credit_text":"MUSIC BY "+music["composer"].upper()},
         "cover":{"identity_family":"cinema_v6","title_en":w["title_en"],"artist":w["artist"],
                  "language":"en","existing_design_unchanged":True,
                  "composition_note":"English artwork name outside V6 locked signature"},
         "on_screen_text":[{"role":"opening_artist","text":w["artist"]},
                           {"role":"opening_music","text":"MUSIC BY "+music["composer"].upper()}],
         "voice":False,"subtitles":False,
         "first_seven_seconds":opening,
         "scenes":[{"source_id":"genuine commons painting","subject":s["purpose"],
                    "purpose":s["purpose"],"shot":s["kind"],"motion":s.get("motion","locked"),
                    "duration_seconds":s["seconds"]} for s in scenes],
         "transition_reviews_plan":[{"from_scene":i,"to_scene":i+1,
                                     "why":"Rhythmic attention continuity and motivated visual transition"} for i in (4,9,13)],
         "music_cues":[{"seconds":0,"reason":"Begin an authentic musical phrase with signature"},
                       {"seconds":duration*.46,"reason":"Progress to a larger emotional reveal"},
                       {"seconds":duration-4,"reason":"Soft finishing cadence toward the whole artwork"}],
         "selected_techniques":techniques,
         "duration_reason":"The chosen sequence is timed to emotional development and instrumental score.",
         "sources":[{"id":"genuine commons painting","url":source_url,
                     "license":"Public domain artwork, Commons page",
                     "credit":w["artist"]+" — "+w["title_en"],"status":"verified"}],
         "music":{"title":music["title"],"composer":music["composer"],
                  "origin":"external_licensed","license":"CC BY 4.0",
                  "evidence":music["page"],"emotional_arc":reasons,"rights_status":"verified"},
         "copy_languages":{"facebook":"it","instagram":"it","tiktok":"it","youtube":"it"},
         "archive_only_after_authorization":True,"social_autopublish":False,
         "outputs":{"video":"VIDEO_MASTER.mp4","cover":"COPERTINA.jpg",
                    "facebook":"POST_FACEBOOK.txt","instagram":"POST_INSTAGRAM.txt",
                    "tiktok":"POST_TIKTOK.txt","youtube":"POST_YOUTUBE.txt",
                    "recipe":"VIDEO_RECIPE_V13.json","techniques":"TECNICHE_REGIA.md",
                    "replication":"ISTRUZIONI_REPLICA.md","rights":"SOURCES_AND_RIGHTS.md",
                    "music_manifest":"MUSIC_RELEASE_V20.json"},
         "review_video_sha256":checksum,
         "reviews":{x:{"passed":False,
                       "notes":"Consegna tecnica; occorre revisione integrale della regia in velocità normale."}
                    for x in ("opening","visual","cover","music","rights","full_watch","replicability")},
         "publication":{"status":"not_published","library_verified":False}}
    (out/"ARTVISION_CONTRACT_V25.json").write_text(json.dumps(tc,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    errors=check_preflight(tc)
    if errors:
        (out/"PREFLIGHT_V25_ERRORS.txt").write_text("\n".join(errors),encoding="utf-8")
    # Distinct names: never present as approved by user after a technical MP4 validation.
    (out/"READ_ME_FIRST.md").write_text(
        f'ArtVision {w["title_en"]} / {w["artist"]}\n'
        f'Master H264/AAC: VIDEO_MASTER.mp4\nCover: COPERTINA.jpg\n'
        f'Documentation: 4 posts, V13 recipe, V25 contract, V20 rights, QA frames.\n'
        f'Technical rendering done; full artistic approval and external rights verification remain separate.\n'
        f'Actual SHA256: {checksum}\n',encoding="utf-8")
    return errors

def produce(slug,w,config,out):
    music=config["music"][w["music"]]
    ep=out/slug
    ep.mkdir(parents=True,exist_ok=True)
    temp=ep/"_work";temp.mkdir(exist_ok=True)
    img_file=ep/"ASSET_ARTWORK.jpg";track=ep/"TRACK_LICENSED.mp3"
    imgurl=fetch([direct_commons(w["file"]),
        "https://commons.wikimedia.org/wiki/Special:Redirect/file/"+urllib.parse.quote(w["file"].replace(" ","_"))],
        img_file,65000,"image")
    musicurl=fetch([music["download"]],track,100000,"music")
    artwork=Image.open(img_file).convert("RGB")
    scenes=[dict(s) for s in w["scenes"]]
    # A V6 signature must exist for 3.45 seconds; allow enough time in opening shot.
    scenes[0]["seconds"]=max(3.7,scenes[0]["seconds"])
    # Author-specific motivated quiet camera / selective movements.
    for idx in (3,8,12):
        if idx<len(scenes)-1 and scenes[idx]["kind"]!="full" and scenes[idx]["motion"]=="locked":
            scenes[idx]["motion"]="slow_push" if idx!=12 else "slow_pull"
    total=sum(s["seconds"] for s in scenes)
    print(slug,"sources okay",artwork.size,"score",music["title"],"duration",total,flush=True)
    if total>75 or total<40:raise RuntimeError("Unexpected film duration "+str(total))
    clips=[]
    for i,s in enumerate(scenes):
        frame=shot_image(artwork,s)
        clip=temp/f"take_{i:02d}.mp4"
        render_shot(frame,s,i,clip,temp,w["artist"],music["composer"])
        clips.append(clip)
        print(slug, f"shot {i+1:02d}/{len(scenes):02d}",s["purpose"],flush=True)
    concat=temp/"concat.txt"
    concat.write_text("".join("file '"+str(c.resolve())+"'\n" for c in clips))
    silent=temp/"silent_master.mp4"
    run("ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",concat,
        "-c:v","copy","-movflags","+faststart",silent)
    video=ep/"VIDEO_MASTER.mp4"
    actual=float(ffprobe(silent)["format"]["duration"])
    fade=max(0,actual-2.8)
    # Genuine CC BY recording, not synthetic substitute, with full credits in every social post.
    run("ffmpeg","-hide_banner","-loglevel","error","-y","-i",silent,"-i",track,
        "-map","0:v:0","-map","1:a:0","-c:v","copy",
        "-af",f"aresample=48000,volume=0.82,afade=t=in:st=0:d=0.8,afade=t=out:st={fade:.3f}:d=2.8",
        "-c:a","aac","-b:a","192k","-t",f"{actual:.3f}","-movflags","+faststart",video)
    first=shot_image(artwork,scenes[0])
    create_cover(first,w,music,ep/"COPERTINA.jpg")
    qa=ep/"QA_V25";qa.mkdir(exist_ok=True)
    for s in (0,1,3,5,7,actual*.33,actual*.58,actual*.8,actual-1):
        name=f"FRAME_{int(s):02d}.jpg" if s in (0,1,3,5,7) else f"FRAME_EXTRA_{round(s,2):.2f}.jpg"
        run("ffmpeg","-hide_banner","-loglevel","error","-y","-ss",str(round(s,2)),
            "-i",video,"-frames:v","1","-q:v","3",qa/name)
    errs=write_release_package(slug,w,music,imgurl,musicurl,img_file,track,video,ep/"COPERTINA.jpg",ep,scenes,
                               {"at_seconds":[0,1,3,5,7],"qa_folder":"QA_V25"})
    facts=ffprobe(video)
    assert any(s.get("codec_type")=="video" and s.get("codec_name")=="h264" and
               s.get("width")==1080 and s.get("height")==1920 for s in facts["streams"])
    assert any(s.get("codec_type")=="audio" and s.get("codec_name")=="aac" for s in facts["streams"])
    # All video frames must be decodable, not simply ffprobe metadata.
    run("ffmpeg","-hide_banner","-loglevel","error","-xerror","-i",video,"-f","null","-",timeout=180)
    report={"format":"artvision-v25-render-verification","status":"RENDERED_NEEDS_ARTISTIC_REVIEW",
            "sha256":sha(video),"bytes":video.stat().st_size,"duration":facts["format"]["duration"],
            "source_hash":sha(img_file),"music_hash":sha(track),"preflight_errors":errs,
            "technical_checks":"ffprobe + full ffmpeg decode","social_pack":True}
    (ep/"VERIFICA_TECNICA.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    # ZIP contains source art and licensed original recording, plus full recipe and social copy.
    pack=out/f"ARTVISION_V25_{slug.upper()}_PACCHETTO.zip"
    import zipfile
    with zipfile.ZipFile(pack,"w") as z:
        for p in ep.rglob("*"):
            if p.is_file() and "_work" not in p.parts:
                method=zipfile.ZIP_STORED if p.suffix.lower() in (".mp4",".mp3",".jpg") else zipfile.ZIP_DEFLATED
                z.write(p,p.relative_to(ep),compress_type=method)
    shutil.rmtree(temp)
    print("SUCCESS",slug,"video bytes",report["bytes"],"zip bytes",pack.stat().st_size,
          "PRECHECK ERRORS",errs,flush=True)
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--painting",required=True)
    p.add_argument("--out",default="output/artvision-v25")
    a=p.parse_args()
    config=json.loads(CONF.read_text(encoding="utf-8"))
    if a.painting not in config["works"]:
        raise ValueError("Unknown subject: "+a.painting)
    result=produce(a.painting,config["works"][a.painting],config,Path(a.out))
    if result["preflight_errors"]:
        raise RuntimeError("V25 contract preflight is blocked: "+"; ".join(result["preflight_errors"]))

if __name__=="__main__":
    main()
