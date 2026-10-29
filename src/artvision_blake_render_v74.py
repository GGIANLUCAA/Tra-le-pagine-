#!/usr/bin/env python3
"""Render William Blake Brooklyn 15.368 second pilot with verifiable assets.

Explicitly requested ONE second 4x1 pilot: V58 serial lock remains unchanged.
Only true Gacrux can fill Critico slots; no silent or substitute voice releases.
Renders only from original Brooklyn artwork, no other Blake painting or AI image.
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
import artvision_blake_visual_v74 as visual

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"output/artvision-blake-brooklyn-v74"
DOSSIER=ROOT/"docs/productions/2026-10-29-blake-red-dragon-brooklyn-v74"
SCRIPT=DOSSIER/"COPIONE_CRITICO_V74.txt"
TITLE="The Great Red Dragon and the Woman Clothed with the Sun"
ARTIST="William Blake"
SOURCE_PAGE="https://commons.wikimedia.org/wiki/File:The_Great_Red_Dragon_and_the_Woman_Clothed_with_the_Sun.jpg"
SOURCE_IMAGE="https://upload.wikimedia.org/wikipedia/commons/9/92/The_Great_Red_Dragon_and_the_Woman_Clothed_with_the_Sun.jpg"
SOURCE_SHA1="75782f11ff654abf909599525b3fa494bf20c4d7"
MUSIC_PAGE="https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100747"
MUSIC_MP3="https://incompetech.com/music/royalty-free/mp3-royaltyfree/Dark%20Times.mp3"
MUSIC_LICENSE="https://creativecommons.org/licenses/by/4.0/"
BROOKLYN="https://www.brooklynmuseum.org/opencollection/objects/4368"
SLOTS=("critico_standard","critico_museum","cinema_standard","cinema_museum")
RENDER_VERSIONS={"cinema_standard":42.0,"cinema_museum":51.0}

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
    artpath=OUT/"BROOKLYN_BLAKE_ORIGINAL.jpg"
    song=OUT/"KEVIN_MACLEOD_DARK_TIMES_CC_BY.mp3"
    if artpath.exists():
        if hashlib.sha1(artpath.read_bytes()).hexdigest()!=SOURCE_SHA1:
            raise RuntimeError("Unexpected original image SHA1; not Brooklyn source")
        artrec={"url":SOURCE_IMAGE,"bytes":artpath.stat().st_size,"sha256":sha256(artpath)}
    else:
        artrec=download(SOURCE_IMAGE,artpath)
    with Image.open(artpath) as a:
        a.verify()
    with Image.open(artpath) as a:
        if a.size!=(1586,2000):raise ValueError("Wrong Blake image dimensions: "+str(a.size))
    if hashlib.sha1(artpath.read_bytes()).hexdigest()!=SOURCE_SHA1:
        raise ValueError("Wrong Blake original; SHA1 does not match Commons Brooklyn 15.368")
    if song.exists():musicrec={"url":MUSIC_MP3,"bytes":song.stat().st_size,"sha256":sha256(song)}
    else:musicrec=download(MUSIC_MP3,song,minbytes=1_000_000,maxbytes=14_000_000)
    probe=subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration",
                                   "-of","json",str(song)])
    if float(json.loads(probe)["format"]["duration"])<90:
        raise ValueError("Music is not the correct complete recording")
    records={
      "schema":"artvision-blake-v74-provenance",
      "work":{"name":TITLE,"artist":ARTIST,"year":"circa 1803–1805",
              "museum":"Brooklyn Museum","object_id":4368,"accession":"15.368",
              "painting_cm":{"height":43.7,"width":34.8},
              "sheet_cm":{"height":55.1,"width":43.3},
              "dimensions_source":BROOKLYN,"medium":"black ink and watercolor over graphite"},
      "artwork":{"source_page":SOURCE_PAGE,"rights":"Public domain/no known copyright restrictions, Commons Brooklyn Museum partnership","source_sha1":SOURCE_SHA1,**artrec},
      "music":{"title":"Dark Times","artist":"Kevin MacLeod",
               "isrc":"USUAN1100747","source":MUSIC_PAGE,"license":"CC BY 4.0", "license_url":MUSIC_LICENSE,**musicrec},
      "museum":{"actual_gallery_photo_used":False,"frame_status":"declared_scenic_reconstruction",
                "room_status":"declared_scenic_reconstruction",
                "frame_description":"small dark wood frame with gilt inner lip, designed scenography only",
                "physical_reference":"sheet 55.1cm high, painting 43.7cm, room viewer distance 3.5m",
                "source_offscreen_during_details":True,"same_room_on_exit":True},
      "no_other_blake_work_or_ai_generated_artwork":True,
      "copyright_status_needs_publication_territory_review":True,
      "paid_video_calls":0,"social_autopublish":False
    }
    write_json(OUT/"SOURCE_MANIFEST.json",records)
    return artpath,song,records

def get_voice():
    """If not demonstrably FREE and billing-disabled, return no voice without a call."""
    import hashlib
    text=SCRIPT.read_text(encoding="utf-8").strip()
    check={"schema":"artvision-blake-gacrux-v74","source_script_sha256":hashlib.sha256(text.encode()).hexdigest(),
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
                write_json(OUT/"GACRUX_GATE_V74.json",check)
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
    if variant=="cinema_standard":
        return {
         "facebook":"Non è una scena di un film. È un piccolo acquerello di William Blake, dipinto oltre due secoli fa. Quante teste del drago riesci a distinguere? Opera: The Great Red Dragon and the Woman Clothed with the Sun, Brooklyn Museum.",
         "instagram":"Un drago che sembra immenso. Un'immagine larga appena 34,8 cm. 🐉 Le ali, la coda e la donna illuminata: scopri un capolavoro visionario di William Blake, 1803–1805. #WilliamBlake #ArtHistory #TheGreatRedDragon",
         "tiktok":"Questo drago non è CGI. William Blake lo dipinse più di 200 anni fa. Aspetta di vedere i dettagli nascosti tra le sue ali. #ArtTok #WilliamBlake #RareArt",
         "youtube":"THE GREAT RED DRAGON | William Blake — cinematic close-ups. Un viaggio nell'autentico acquerello del Brooklyn Museum: le ali, le corna e la figura della donna. Musica: Dark Times, Kevin MacLeod, CC BY 4.0."
        }
    if variant=="cinema_museum":
        return {
         "facebook":"Entriamo in una sala ricostruita e troviamo un'immagine sorprendentemente piccola. Poi la camera oltrepassa la cornice e rivela il drago di William Blake. La sala e la cornice sono una ricostruzione scenografica, non l'allestimento reale del Brooklyn Museum.",
         "instagram":"Sembra un portale verso un mondo gigantesco. Ma il dipinto misura solo 43,7 × 34,8 cm. Museum Immersion attraverso l'opera originale di Blake. Sala e cornice ricostruite. #MuseumImmersion #WilliamBlake #ArtExperience",
         "tiktok":"Un minuscolo quadro in una stanza silenziosa. Tre secondi dopo, il drago occupa tutto lo schermo. E alla fine torni esattamente da dove sei partito. #MuseumPOV #Blake #ArtHistory",
         "youtube":"WILLIAM BLAKE — Museum Immersion. La grandezza dell'Apocalisse in un piccolo foglio di carta: visita cinematografica a scala illustrativa, senza sostituire i pixel originali del dipinto. Sala e cornice scenografiche dichiarate."
        }
    if variant=="critico_standard":
        return {
         "facebook":"Perché William Blake mostra il drago di spalle? Una lettura essenziale del suo acquerello: Apocalisse, simbolismo e una composizione che concentra il conflitto tra forza e vulnerabilità.",
         "instagram":"Non serve un mostro in movimento per creare tensione. Nel 1803–1805 William Blake costruì il drago con pochi strumenti: inchiostro, grafite e acquerello. Una breve lettura d'arte. #CriticaDArte #WilliamBlake",
         "tiktok":"Il dettaglio più inquietante non è la coda del drago. Guarda come Blake costruisce il contrasto tra l'ombra e il corpo luminoso. #ArteSpiegata #Blake",
         "youtube":"CRITICO D'ARTE — William Blake e il Grande Drago Rosso. Analisi documentata e sintetica dell'opera del Brooklyn Museum, da Apocalisse 12 alla tecnica dell'acquerello."
        }
    return {
      "facebook":"Dal museo ricostruito al mondo visionario di Blake: la stessa analisi della versione Critico Standard, ma con un percorso continuo dentro il dipinto e ritorno nella sala.",
      "instagram":"Un racconto d'arte attraversando la cornice. Il drago di Blake visto da vicino, in una visita cinematografica attraverso una sala scenografica dichiarata. #MuseumImmersion #ArtCritic",
      "tiktok":"Un acquerello di 43 centimetri. Dentro, un drago enorme. Ecco perché il dipinto funziona anche quando la cornice scompare dall'inquadratura. #MuseumExperience #Blake",
      "youtube":"CRITICO MUSEUM — Il Grande Drago Rosso. Stesso copione e identico audio Gacrux del Critico Standard, con regia museale continua. Sala e cornice illustrate, non installazione reale."
    }

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

def render_one(name,art,roomimg,song,voice=None):
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
            else:img=visual.museum_frame(art,roomimg,t,total,critic=critic)
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
        "# William Blake, The Great Red Dragon and the Woman Clothed with the Sun\n"
        "Brooklyn Museum 15.368, circa 1803–1805; source: "+SOURCE_PAGE+"\n"
        "Photo: Brooklyn Museum Commons partnership, no known restrictions, SHA1 "+SOURCE_SHA1+"\n"
        "Music: Dark Times by Kevin MacLeod, CC BY 4.0: "+MUSIC_PAGE+"\n"
        "Museum room and frame are reconstructed scenography, not a museum photograph or documented original frame.\n"
        "No AI painting reconstruction or other Blake Dragon version is used.\n",encoding="utf-8")
    if critic:
        shutil.copy2(SCRIPT,folder/"COPIONE_CRITICO.txt")
        shutil.copy2(voice,folder/"VOCE_GACRUX.wav")
    state={"variant":name,"status":"rendered_needs_review","video":mp4.name,
           "video_sha256":sha256(mp4),"source_artwork_sha256":sha256(OUT/"BROOKLYN_BLAKE_ORIGINAL.jpg"),
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
    artfile,music,manifest=acquire()
    art=Image.open(artfile).convert("RGB")
    roomimg=visual.room()
    voice=None
    outcomes={}
    # Video production remains one active rendering at a time.
    for name in ("cinema_standard","cinema_museum"):
        outcomes[name]=render_one(name,art,roomimg,music)
    voice=get_voice()
    if voice is not None:
        for name in ("critico_standard","critico_museum"):
            outcomes[name]=render_one(name,art,roomimg,music,voice)
    else:
        for name in ("critico_standard","critico_museum"):
            outcomes[name]={"status":"blocked_gacrux_unavailable_no_substitute","video_exists":False}
    hashes=[v.get("video_sha256") for v in outcomes.values() if v.get("video_sha256")]
    if len(hashes)!=len(set(hashes)):raise RuntimeError("Duplicate variant rendered")
    if voice:
        a,b=outcomes["critico_standard"],outcomes["critico_museum"]
        if a["voice_sha256"]!=b["voice_sha256"]:raise RuntimeError("Critico WAV mismatch")
    summary={"schema":"artvision-blake-4x1-v74","work":TITLE,"museum":"Brooklyn Museum",
             "explicit_second_pilot_only":True,"four_variants":outcomes,
             "rendered_count":len(hashes),"four_finished":len(hashes)==4,
             "all_approved":False,"site_playback_verified":False,
             "new_paid_calls":0,"video_AI_calls":0,"no_social_publishing":True,
             "status":"rendered_needs_human_review" if len(hashes)==4 else "partial_cinema_only_voice_blocked"}
    write_json(OUT/"BLake_4X1_FINAL_STATE.json",summary)
    print("ARTVISION_BLAKE_4X1_RESULT",json.dumps(summary,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
