#!/usr/bin/env python3
"""ArtVision V78 third one-off pilot: Joseph Wright of Derby, NG725, National Gallery.
User explicitly requested ONE new four-film artwork, NOT serial unlock.
Source photograph captures the artwork and its actual, documented frame.
Only real Gacrux can fill Critico slots; zero paid calls without verified free gate.
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
import artvision_wright_visual_v78 as visual

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"output/artvision-wright-air-pump-v78"
DOSSIER=ROOT/"docs/productions/2026-10-29-wright-air-pump-v78"
SCRIPT=DOSSIER/"COPIONE_CRITICO_V78.txt"
TITLE="An Experiment on a Bird in the Air Pump"
ARTIST="Joseph Wright of Derby"
SOURCE_PAGE="https://commons.wikimedia.org/wiki/File:An_Experiment_on_a_Bird_in_an_Air_Pump_by_Joseph_Wright_of_Derby%2C_1768.jpg"
SOURCE_IMAGE="https://uploads6.wikiart.org/images/joseph-wright/an-experiment-on-a-bird-in-the-air-pump-1768.jpg"
SOURCE_SHA1="8999bf5baa1b5c6f4332786797129fe01da84398" # Wikimedia Commons related file; WikiArt distributor hash checked via byte size and recorded separately
MUSIC_PAGE="https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100747"
MUSIC_MP3="https://incompetech.com/music/royalty-free/mp3-royaltyfree/Dark%20Times.mp3"
MUSIC_LICENSE="https://creativecommons.org/licenses/by/4.0/"
NATIONAL_GALLERY="https://www.nationalgallery.org.uk/paintings/joseph-wright-of-derby-an-experiment-on-a-bird-in-the-air-pump"
SLOTS=("critico_standard","critico_museum","cinema_standard","cinema_museum")
RENDER_VERSIONS={"cinema_standard":44.0,"cinema_museum":52.0}

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
    artpath=OUT/"NATIONAL_GALLERY_WRIGHT_PD_ART.jpg"
    song=OUT/"KEVIN_MACLEOD_DARK_TIMES_CC_BY.mp3"
    if artpath.exists():
        if artpath.stat().st_size!=4147734:
            raise RuntimeError("WikiArt source byte count mismatch; reject unknown picture")
        artrec={"url":SOURCE_IMAGE,"bytes":artpath.stat().st_size,"sha256":sha256(artpath)}
    else:
        artrec=download(SOURCE_IMAGE,artpath)
    with Image.open(artpath) as a:
        a.verify()
    with Image.open(artpath) as a:
        if a.size!=(5639,4226):raise ValueError("Wrong Wright public-domain reproduction dimensions: "+str(a.size))
    if artpath.stat().st_size!=4147734:
        raise ValueError("Unexpected WikiArt distribution byte count; do not quietly substitute images")
    true_source_sha1=hashlib.sha1(artpath.read_bytes()).hexdigest()
    if song.exists():musicrec={"url":MUSIC_MP3,"bytes":song.stat().st_size,"sha256":sha256(song)}
    else:musicrec=download(MUSIC_MP3,song,minbytes=1_000_000,maxbytes=14_000_000)
    probe=subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration",
                                   "-of","json",str(song)])
    if float(json.loads(probe)["format"]["duration"])<90:
        raise ValueError("Music is not the correct complete recording")
    records={
      "schema":"artvision-wright-v78-provenance",
      "work":{"name":TITLE,"artist":ARTIST,"year":"1768",
              "museum":"National Gallery, London","accession":"NG725",
              "painting_cm":{"height":183.0,"width":244.0},
              "dimensions_source":NATIONAL_GALLERY,"medium":"oil on canvas"},
      "artwork":{"source_page":SOURCE_PAGE,
                 "rights":"Public domain mark; WikiArt direct high-resolution distribution of Commons artwork file",
                 "source_sha1":true_source_sha1,"related_commons_sha1":SOURCE_SHA1,**artrec},
      "music":{"title":"Dark Times","artist":"Kevin MacLeod",
               "isrc":"USUAN1100747","source":MUSIC_PAGE,"license":"CC BY 4.0","license_url":MUSIC_LICENSE,**musicrec},
      "museum":{"actual_gallery_photo_used":False,
                "frame_status":"authentic_historic_frame_documented_not_reproduced_source_photo_unavailable",
                "room_status":"declared_fictional_gallery_staging",
                "frame_description":"19th-century English gilded frame documented by National Gallery but NOT included in selected public-domain source image. No invented decorative frame; clean unframed digital gallery staging only.",
                "physical_reference":"oil canvas 183x244cm; human-scale viewer distance approximately 3.5m",
                "source_offscreen_during_details":True,"same_room_on_exit":True,
                "frame_documentation":NATIONAL_GALLERY},
      "no_ai_generated_artwork":True,
      "copyright_status_needs_publication_territory_review":True,
      "paid_video_calls":0,"social_autopublish":False
    }
    write_json(OUT/"SOURCE_MANIFEST.json",records)
    return artpath,song,records

def get_voice():
    """If not demonstrably FREE and billing-disabled, return no voice without a call."""
    import hashlib
    text=SCRIPT.read_text(encoding="utf-8").strip()
    check={"schema":"artvision-wright-gacrux-v78","source_script_sha256":hashlib.sha256(text.encode()).hexdigest(),
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
    title="An Experiment on a Bird in the Air Pump — Joseph Wright of Derby (1768), National Gallery, NG725."
    gallery="La sala museale è una scenografia digitale. La cornice storica è documentata ma non è riprodotta; la sala digitale presenta l'opera senza cornice fittizia."
    if variant=="cinema_standard":
        return {
          "facebook":"Una stanza, un uccello bianco, una decisione che cambia tutto. "+title+" La luce mostra i dettagli che potresti non notare.",
          "instagram":"Chi salverà il cacatua? Un dipinto del 1768 raccontato attraverso sei dettagli autentici. "+title+" #ArtVision #WrightOfDerby",
          "tiktok":"Sta per togliere l'aria alla campana di vetro. Guarda le reazioni. "+title+" #ArtTok #OilPainting",
          "youtube":"ONE BREATH FROM DEATH | Cinema Standard. Solo dettagli autentici dell'opera. "+title
        }
    if variant=="cinema_museum":
        return {
          "facebook":"Un dipinto di quasi due metri e mezzo. Dalla sala al cuore della scena, poi indietro nella stessa sala. "+title+" "+gallery,
          "instagram":"MUSEUM IMMERSION · Un quadro, una sola camera, una cornice storicamente documentata, qui non riprodotta. "+title+" "+gallery+" #MuseumImmersion",
          "tiktok":"Entra nel dipinto: un uccello bianco e una scelta sospesa. "+title+" "+gallery,
          "youtube":"MUSEUM IMMERSION · Ingresso e uscita continui a scala illustrativa di 183×244 cm. "+title+" "+gallery
        }
    if variant=="critico_standard":
        return {
          "facebook":"Scienza e morale si incontrano in questa dimostrazione settecentesca. Analisi professionale di "+title,
          "instagram":"Perché alcuni spettatori soffrono e altri osservano? Critico d'arte, spiegazione storica e dettagli autentici. "+title,
          "tiktok":"Il dettaglio più importante non è la pompa, ma come le persone guardano l'esperimento. "+title,
          "youtube":"CRITICO D'ARTE · Analisi dell'illuminazione, dei testimoni e dell'esperimento. "+title
        }
    return {
       "facebook":"Lo stesso racconto Critico, la stessa voce Gacrux, con una camera continua dentro l'opera. "+title+" "+gallery,
       "instagram":"MUSEUM CRITICO · La scena vista da vicino senza tagli artificiosi né cornici inventate. "+title+" "+gallery,
       "tiktok":"Entro nella sala, poi nel quadro, mentre il critico racconta cosa sta accadendo. "+title+" "+gallery,
       "youtube":"CRITICO MUSEUM · Stesso copione e WAV del Critico Standard, camera immersiva e cornice storica non ricostruita. "+title+" "+gallery
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
        "# Joseph Wright of Derby, An Experiment on a Bird in the Air Pump\n"
        "National Gallery NG725, 1768; source: "+SOURCE_PAGE+"\n"
        "Unframed painting reproduction PD Mark, WikiArt CDN image; Commons-related SHA1 "+SOURCE_SHA1+"\n"
        "Music: Dark Times by Kevin MacLeod, CC BY 4.0: "+MUSIC_PAGE+"\n"
        "Museum wall is digital staging, historical gilded frame documented but not recreated because source frame photo is rate-limited.\n"
        "No AI or invented painted content, no added fictitious frame.\n",encoding="utf-8")
    if critic:
        shutil.copy2(SCRIPT,folder/"COPIONE_CRITICO.txt")
        shutil.copy2(voice,folder/"VOCE_GACRUX.wav")
    state={"variant":name,"status":"rendered_needs_review","video":mp4.name,
           "video_sha256":sha256(mp4),"source_artwork_sha256":sha256(OUT/"NATIONAL_GALLERY_WRIGHT_PD_ART.jpg"),
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
    summary={"schema":"artvision-wright-4x1-v78","work":TITLE,"museum":"National Gallery",
             "explicit_one_off_new_pilot_only":True,"four_variants":outcomes,
             "rendered_count":len(hashes),"four_finished":len(hashes)==4,
             "all_approved":False,"site_playback_verified":False,
             "new_paid_calls":0,"video_AI_calls":0,"no_social_publishing":True,
             "status":"rendered_needs_human_review" if len(hashes)==4 else "partial_cinema_only_voice_blocked"}
    write_json(OUT/"WRIGHT_4X1_FINAL_STATE.json",summary)
    print("ARTVISION_WRIGHT_4X1_RESULT",json.dumps(summary,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
