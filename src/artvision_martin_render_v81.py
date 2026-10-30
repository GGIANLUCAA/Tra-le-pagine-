#!/usr/bin/env python3
"""ArtVision V81 | John Martin The Great Day of His Wrath | four original MP4.
Real 2010 Tate framed photo by Szilas, CC BY-SA 4.0, frame ONLY in museum intro/outro.
Painting from verified public-domain reproduction; user-authorized free Gemini Gacrux.
Four independent film hashes; no paid video generation or automatic publication.
"""
from __future__ import annotations
import hashlib
import json
import os
import shutil
import subprocess
import sys
import textwrap
import time
import zipfile
from pathlib import Path
import requests
from PIL import Image, ImageFile
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
import artvision_martin_visual_v81 as visual

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"output/artvision-martin-wrath-v81"
DOSSIER=ROOT/"docs/productions/2026-10-30-martin-wrath-v81"
SCRIPT=DOSSIER/"COPIONE_CRITICO_V81.txt"
TITLE="The Great Day of His Wrath"
ARTIST="John Martin"
SOURCE_PAGE="https://commons.wikimedia.org/wiki/File:John_Martin_-_The_Great_Day_of_His_Wrath_-_Google_Art_Project.jpg"
SOURCE_IMAGE="https://uploads6.wikiart.org/images/john-martin/the-great-day-of-his-wrath-1853.jpg"
SOURCE_SHA256="13c1131f595fad2be7af4bafffb6b069c7e5322d352495f231ea3b2f04252fd9"
FRAME_PAGE="https://commons.wikimedia.org/wiki/File:John_Martin_-_Apocalypse_-_with_frame.jpg"
FRAME_IMAGE="https://cache.getarchive.net/Prod/thumb/cdn2/L3Bob3RvLzIwMjMvMDYvMDMvam9obi1tYXJ0aW4tYXBvY2FseXBzZS13aXRoLWZyYW1lLTg4ZjFmNy0xMDI0LmpwZw%3D%3D/1280/897/jpg"
FRAME_SHA256="71bed3fc4b1b37d06988fa803645efba400e12c23eb3669b54d7dbd3c89ec424"
FRAME_LICENSE="https://creativecommons.org/licenses/by-sa/4.0/"
MUSIC_PAGE="https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100747"
MUSIC_MP3="https://incompetech.com/music/royalty-free/mp3-royaltyfree/Dark%20Times.mp3"
MUSIC_LICENSE="https://creativecommons.org/licenses/by/4.0/"
TATE_PAGE="https://www.tate.org.uk/art/artworks/martin-the-great-day-of-his-wrath-n05613"
SLOTS=("critico_standard","critico_museum","cinema_standard","cinema_museum")
RENDER_VERSIONS={"cinema_standard":46.0,"cinema_museum":51.0}

def sha256(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for part in iter(lambda:f.read(1024*1024),b""):h.update(part)
    return h.hexdigest()

def write_json(path,value):
    Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def download(url,dest,minbytes=500_000,maxbytes=15_000_000):
    if dest.exists():raise FileExistsError("Do not overwrite pinned asset "+str(dest))
    r=requests.get(url,timeout=75,headers={"User-Agent":"ArtVisionV74/1.0 (artwork and CC-BY licensed media attribution)"})
    r.raise_for_status()
    if not r.url.startswith("https://"):
        raise RuntimeError("Source redirect not secure")
    data=r.content
    if not minbytes<=len(data)<=maxbytes:
        raise RuntimeError("Unexpected source byte count: "+str(len(data)))
    dest.write_bytes(data)
    return {"url":r.url,"bytes":len(data),"sha256":sha256(dest)}

def acquire():
    OUT.mkdir(parents=True,exist_ok=True)
    artpath=OUT/"TATE_N05613_PAINTING.jpg"
    framepath=OUT/"TATE_N05613_FRAME_ACTUAL_2010_SZILAS.jpg"
    song=OUT/"KEVIN_MACLEOD_DARK_TIMES_CC_BY.mp3"
    if not artpath.exists():
        a=download(SOURCE_IMAGE,artpath,minbytes=100_000,maxbytes=12_000_000)
    if sha256(artpath)!=SOURCE_SHA256:raise RuntimeError("Wrong painting bytes; no substitution allowed")
    with Image.open(artpath) as a:
        a.verify()
    with Image.open(artpath) as a:
        if a.size!=(1000,640):raise RuntimeError("Wrong John Martin painting dimensions")
    if not framepath.exists():
        download(FRAME_IMAGE,framepath,minbytes=100_000,maxbytes=12_000_000)
    if sha256(framepath)!=FRAME_SHA256:raise RuntimeError("Wrong REAL Tate 2010 framed photo")
    with Image.open(framepath) as f:
        f.verify()
    with Image.open(framepath) as f:
        if f.size!=(1024,717):raise RuntimeError("Frame image metadata changed")
    if song.exists():musicrec={"url":MUSIC_MP3,"bytes":song.stat().st_size,"sha256":sha256(song)}
    else:musicrec=download(MUSIC_MP3,song,minbytes=1_000_000,maxbytes=14_000_000)
    probe=subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration",
                                   "-of","json",str(song)])
    if float(json.loads(probe)["format"]["duration"])<90:
        raise RuntimeError("Wrong music duration")
    records={
       "schema":"artvision-martin-v81-source-provenance",
       "work":{"name":TITLE,"artist":ARTIST,"date":"1851–1853","museum":"Tate Britain",
               "accession":"N05613","medium":"oil on canvas",
               "canvas_cm":{"width":303.2,"height":196.5},"museum_url":TATE_PAGE},
       "artwork":{"url":SOURCE_IMAGE,"source_page":SOURCE_PAGE,"sha256":sha256(artpath),
                  "pixels":[1000,640],"public_domain_artwork":True,
                  "resolution_caveat":"Source is 1000x640; 1080 output is upscale, NOT true 4K",
                  "rights_review_before_publication":True},
       "frame":{"photo_url":FRAME_PAGE,"download_mirror":FRAME_IMAGE,
                "sha256":sha256(framepath),"pixels":[1024,717],
                "photo_credit":"Szilas, photograph in Tate Britain, 31 July 2010",
                "photo_license":"CC BY-SA 4.0","license_url":FRAME_LICENSE,
                "frame_status":"authentic_documented_photo_2010",
                "not_claimed_original_artist_frame":True,
                "aperture_normalized":list(visual.APERTURE),
                "visible_only_first_and_last_museum_shots":True,
                "exact_same_frame_on_return":True,
                "actual_room_photo_used":False,
                "gallery_reconstruction_status":"synthetic_wall_declared"},
       "music":{"title":"Dark Times","artist":"Kevin MacLeod","license":"CC BY 4.0",
                "isrc":"USUAN1100747","page":MUSIC_PAGE,"license_url":MUSIC_LICENSE,**musicrec},
       "no_ai_artwork_generation":True,"no_vidu":True,"no_paid_video_calls":True,
       "social_auto_publishing":False
    }
    write_json(OUT/"SOURCE_MANIFEST.json",records)
    return artpath,framepath,song,records

def get_voice():
    """If not demonstrably FREE and billing-disabled, return no voice without a call."""
    import hashlib
    text=SCRIPT.read_text(encoding="utf-8").strip()
    check={"schema":"artvision-martin-gacrux-v81","source_script_sha256":hashlib.sha256(text.encode()).hexdigest(),
           "word_count":len(text.split()),"same_WAV_required":True,"payment_consent":False,
           "provider":"Google Gemini Gacrux","api_calls":0,"status":"not_attempted"}
    voicefile=OUT/"VOICE_GACRUX.wav"
    # Existing exact cache may be reused without an API call.
    sys.path.insert(0,str(ROOT/"src"))
    try:
        import gemini_voice
        cache=OUT/"voice_cache"
        cache.mkdir(exist_ok=True)
        if gemini_voice._cached_audio(text,cache):
            wav=cache/"VOCE.wav"
            if wav.is_file() and wav.stat().st_size>60_000:
                shutil.copy2(wav,voicefile)
                check.update(status="verified_cached_Gacrux",wav_sha256=sha256(voicefile))
                write_json(OUT/"GACRUX_GATE_V81.json",check)
                return voicefile
    except Exception as exc:
        check["cache_check_note"]=type(exc).__name__
    free=os.getenv("GEMINI_TTS_FREE_QUOTA_CONFIRMED","").lower()=="true"
    disabled=os.getenv("GEMINI_TTS_PROJECT_BILLING_DISABLED_CONFIRMED","").lower()=="true"
    haskey=bool(os.getenv("GEMINI_API_KEY"))
    check.update(free_quota_attested=free,billing_disabled_attested=disabled,key_present=bool(haskey))
    if not(free and disabled and haskey):
        check["status"]="blocked_free_billing_disabled_not_attested"
        write_json(OUT/"GACRUX_GATE_V74.json",check)
        print("GACRUX_BLOCKED_NO_COST: no substitution, no critic master",flush=True)
        return None
    # At most ONE Google call, no retries, only with explicit repository owner
    # attestation of a no-charge TTS project.
    try:
        import gemini_voice
        gemini_voice.synthesize(text,cache)
        wav=cache/"VOCE.wav"
        if not wav.exists() or wav.stat().st_size<60_000:
            raise ValueError("No real Gacrux WAV")
        shutil.copy2(wav,voicefile)
        check.update(status="real_Gacrux_generated_free_attested",api_calls=1,
                     wav_sha256=sha256(voicefile))
    except Exception as e:
        check.update(status="blocked_synthesis_failed_no_retry",
                     attempted_once=True,failed_type=type(e).__name__,error=str(e)[:250])
        write_json(OUT/"GACRUX_GATE_V74.json",check)
        print("GACRUX_FAILED_NO_RETRY: "+type(e).__name__,flush=True)
        return None
    write_json(OUT/"GACRUX_GATE_V74.json",check)
    return voicefile

def social(variant):
    title="John Martin, The Great Day of His Wrath (1851–53), Tate Britain N05613."
    rights="Cornice fotografata alla Tate nel 2010 da Szilas, CC BY-SA 4.0. Sala digitale ricostruita. Fotografia riutilizzata e compositata. Fonte e licenza nei crediti."
    if variant=="cinema_standard":
        return {
          "facebook":"Un mondo si spezza. Grandi montagne precipitano in un abisso e minuscole figure cercano salvezza. "+title,
          "instagram":"La fine del mondo, dipinta 170 anni fa: luce, abissi e figure minuscole. "+title+" #ArtVision #JohnMartin #ArtHistory",
          "tiktok":"E se il mondo si spezzasse in due? Guarda i minuscoli esseri umani nel quadro. "+title+" #ArtTok",
          "youtube":"WHEN MOUNTAINS COLLAPSE | Cinema Standard, dipinto autentico e musica. "+title}
    if variant=="cinema_museum":
        return {
          "facebook":"Dalla vera cornice fotografata alla Tate entriamo nell'opera apocalittica e ne usciamo solo alla fine. "+title+" "+rights,
          "instagram":"MUSEUM IMMERSION. La cornice reale resta fuori dai dettagli; torna solo nel finale. "+title+" "+rights,
          "tiktok":"Una cornice esposta alla Tate, un'apocalisse dentro il dipinto. "+title+" "+rights,
          "youtube":"MUSEUM IMMERSION | John Martin: entrata continua, solo pittura centrale, ritorno alla cornice del 2010. "+title+" "+rights}
    if variant=="critico_standard":
        return {
          "facebook":"Un'analisi chiara del Giudizio finale di Martin: la scala, la luce, le rocce e gli uomini minuscoli. "+title,
          "instagram":"Perché John Martin dipinse uomini così piccoli? La risposta è nella scala del paesaggio. "+title+" #CriticoArte",
          "tiktok":"Non sono semplici montagne: un'intera città sta cadendo nell'abisso. "+title,
          "youtube":"CRITICO STANDARD — John Martin, Giudizio finale e sublime romantico. "+title}
    return {
        "facebook":"Stessa identica voce del Critico Standard, ma camminiamo dentro il dipinto dalla sua cornice. "+title+" "+rights,
        "instagram":"CRITICO MUSEUM — una sola registrazione Gacrux, viaggio visivo con cornice reale solo ai bordi del video. "+title+" "+rights,
        "tiktok":"Entra nel quadro con il critico: dentro la pittura non c'è nessuna cornice. "+title+" "+rights,
        "youtube":"CRITICO MUSEUM — identico racconto, camera continua, cornice documentata. "+title+" "+rights}

def ffprobe(path):
    data=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams",
                                             "-show_format","-of","json",str(path)]))
    video=[x for x in data["streams"] if x.get("codec_type")=="video"]
    audio=[x for x in data["streams"] if x.get("codec_type")=="audio"]
    if len(video)!=1 or len(audio)!=1:raise ValueError("one video plus one audio required")
    if video[0].get("codec_name")!="h264" or audio[0].get("codec_name")!="aac":
        raise ValueError("H264/AAC required")
    if video[0].get("width")!=1080 or video[0].get("height")!=1920:
        raise ValueError("9:16 1080 delivery required")
    return {"duration_seconds":float(data["format"]["duration"]),
            "bytes":int(data["format"]["size"]),
            "video_codec":video[0]["codec_name"],"audio_codec":audio[0]["codec_name"],
            "pixels":[video[0]["width"],video[0]["height"]]}

def render_one(name,art,actual_frame,roomimg,song,voice=None):
    critic=name.startswith("critico")
    if critic and voice is None:raise ValueError("No silent Critico allowed")
    if critic:
        vinfo=json.loads(subprocess.check_output(["ffprobe","-v","error",
                     "-show_entries","format=duration","-of","json",str(voice)]))
        voice_duration=float(vinfo["format"]["duration"])
        duration=voice_duration+1.5
    else:
        duration=RENDER_VERSIONS[name]
    frames=round(duration*visual.FPS)
    duration=frames/visual.FPS
    folder=OUT/name
    folder.mkdir(parents=True,exist_ok=False)
    mp4=folder/(name.upper()+".mp4")
    if mp4.exists():raise FileExistsError(mp4)
    total=duration
    filters=f"[1:a]volume={'0.13' if critic else '0.40'},afade=t=in:st=0:d=0.9,afade=t=out:st={max(0,total-2.5):.3f}:d=2.5[m]"
    if critic:
        filters+=";[m][2:a]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[out]"
    else:filters+=";[m]anull[out]"
    command=[
      "ffmpeg","-hide_banner","-loglevel","error","-y",
      "-f","rawvideo","-pix_fmt","rgb24","-s",f"{visual.W}x{visual.H}",
      "-r",str(visual.FPS),"-i","pipe:0",
      "-stream_loop","-1","-i",str(song)]
    if critic:command+=["-i",str(voice)]
    command+=["-filter_complex",filters,"-map","0:v:0","-map","[out]",
             "-vf","scale=1080:1920:flags=lanczos,format=yuv420p",
             "-c:v","libx264","-preset","veryfast","-crf","20",
             "-c:a","aac","-b:a","160k",
             "-t",f"{total:.4f}","-movflags","+faststart",str(mp4)]
    print("RENDER_START",name,"duration",round(total,2),"frames",frames,flush=True)
    start=time.time()
    p=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    try:
        for i in range(frames):
            t=i/visual.FPS
            if name=="cinema_standard":img=visual.cinema_standard(art,t,total)
            elif name=="critico_standard":img=visual.critico_standard(art,t,total)
            else:img=visual.museum_frame(art,actual_frame,roomimg,t,total,critic=critic)
            if img.size!=(visual.W,visual.H):raise RuntimeError("Wrong render frame size")
            p.stdin.write(np.asarray(img.convert("RGB"),dtype=np.uint8).tobytes())
            if i%225==0:
                print("RENDER_FRAME",name,i,"/",frames,"elapsed",round(time.time()-start),flush=True)
        p.stdin.close()
        stderr=p.stderr.read().decode("utf-8","replace")
        status=p.wait()
        if status:raise RuntimeError("Video encoding failed: "+stderr[-1000:])
    except Exception:
        p.kill()
        p.wait()
        raise
    info=ffprobe(mp4)
    if abs(info["duration_seconds"]-total)>.9:raise ValueError("Render duration mismatch")
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-xerror",
                    "-i",str(mp4),"-f","null","-"],check=True)
    visual.cover(art,name).save(folder/"COPERTINA.jpg",quality=92)
    for platform,text in social(name).items():
        credit='\n\nMusica: "Dark Times", Kevin MacLeod (incompetech.com), CC BY 4.0: '+MUSIC_LICENSE
        (folder/("POST_"+platform.upper()+".txt")).write_text(text+credit+"\n",encoding="utf-8")
    (folder/"SOURCE_AND_RIGHTS.md").write_text(
        "# John Martin, The Great Day of His Wrath (Tate N05613)\\n"
        "Oil canvas 1851–53, 196.5 × 303.2cm. "+TATE_PAGE+"\\n"
        "Painting: documented reproduction "+SOURCE_PAGE+" sha256 "+SOURCE_SHA256+"\\n"
        "2010 actual Tate framed photo: Szilas, CC BY-SA 4.0, "+FRAME_PAGE+"\\n"
        "Adaptations: mounted high-resolution painting area inside the real photographed frame; "
        "virtual gallery wall only. Photo license: "+FRAME_LICENSE+"\\n"
        "Music: Dark Times by Kevin MacLeod, CC BY 4.0: "+MUSIC_PAGE+" / "+MUSIC_LICENSE+"\\n"
        "The historical 2010 photo does NOT establish the original artist-era frame. "
        "All Museum shots remain subject to final artistic review. "
        "Artwork file itself is only 1000x640, so delivered 1080 resolution is upscaled.\\n",
        encoding="utf-8")

    if critic:
        shutil.copy2(SCRIPT,folder/"COPIONE_CRITICO.txt")
        shutil.copy2(voice,folder/"VOCE_GACRUX.wav")
    state={"variant":name,"status":"rendered_needs_review","video":mp4.name,
           "video_sha256":sha256(mp4),"source_artwork_sha256":sha256(OUT/"TATE_N05613_PAINTING.jpg"),
           "music_sha256":sha256(song),"native_render_pixels":[visual.W,visual.H],
           "delivery_pixels":[1080,1920],"fps":visual.FPS,
           "voice_sha256":sha256(voice) if critic else None,
           "studio_voice":"Google Gemini Gacrux" if critic else None,
           "same_WAV_for_both_critico":True if critic else None,
           "human_full_speed_review":"pending","artistic_gold_master":False,
           "private_archive_verified":False,"social_published":False,**info}
    write_json(folder/"TECHNICAL_QA.json",state)
    with zipfile.ZipFile(OUT/(name+"_COMPLETE.zip"),"w",allowZip64=True) as z:
        for file in folder.iterdir():
            if file.is_file():z.write(file,file.name,compress_type=zipfile.ZIP_STORED if file.suffix in (".mp4",".jpg",".wav") else zipfile.ZIP_DEFLATED)
        z.write(OUT/"SOURCE_MANIFEST.json","SOURCE_MANIFEST.json")
    with zipfile.ZipFile(OUT/(name+"_COMPLETE.zip")) as z:
        if z.testzip() is not None:raise RuntimeError("Package ZIP CRC mismatch")
    print("RENDER_VERIFIED",json.dumps(state,ensure_ascii=False),flush=True)
    return state

def main():
    artfile,framefile,music,manifest=acquire()
    art=Image.open(artfile).convert("RGB")
    actual_frame=Image.open(framefile).convert("RGB")
    roomimg=visual.room()
    outcomes={}
    # Four separate MP4s. Gacrux is synthesized once and WAV reused exactly.
    # First ensure voice availability, but still render the two free Cinema slots if missing.
    voice=get_voice()
    names=("critico_standard","critico_museum","cinema_standard","cinema_museum")
    for name in names:
        if name.startswith("critico") and voice is None:
            outcomes[name]={"status":"blocked_gacrux_unavailable","mp4_exists":False}
            continue
        outcomes[name]=render_one(name,art,actual_frame,roomimg,music,voice if name.startswith("critico") else None)
    created=[v for v in outcomes.values() if v.get("video_sha256")]
    hashes=[v["video_sha256"] for v in created]
    if len(hashes)!=len(set(hashes)):raise RuntimeError("Duplicate output videos")
    if voice is not None:
        if outcomes["critico_standard"]["voice_sha256"]!=outcomes["critico_museum"]["voice_sha256"]:
            raise RuntimeError("Same WAV must drive both Critico variants")
    state={"schema":"artvision-martin-4x1-v81","work":TITLE,
           "source_museum":"Tate Britain","unique_one_off_user_approved":True,
           "four_variants":outcomes,"rendered_count":len(hashes),"four_rendered":len(hashes)==4,
           "frame_status":"real_2010_Tate_photo_frame_not_artist_original_claim",
           "artistic_gold_master":False,"private_archive_verified":False,
           "needs_full_speed_artistic_review":True,
           "new_vidu_paid_calls":0,"social_auto_published":False}
    write_json(OUT/"MARTIN_V81_4X1_STATE.json",state)
    print("MARTIN_V81_4X1_RESULT",json.dumps(state,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
