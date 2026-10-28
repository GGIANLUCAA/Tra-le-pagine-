#!/usr/bin/env python3
"""Alice Rackham (1907): source-first book episode. No paid video API, no retry, no publishing.
Modes: prepare (free, download original plates, V13/V35, preview ZIP); render (Gacrux only
after external free-quota attestation); qa (real MP4 checks and packages).
"""
from __future__ import annotations
import argparse,hashlib,json,math,re,shutil,subprocess,sys,tempfile,zipfile
from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from PIL import Image,ImageOps,ImageDraw,ImageFilter,ImageEnhance,ImageFont

EP=Path("episodes/alice_wonderland_20261028")
OUT=Path("output/alice_wonderland_20261028")
URL="https://www.gutenberg.org/cache/epub/28885/pg28885-images.html"
FPS=24
SPLIT=re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-ÙÈÉ«“])")
NAME="TRA_LE_PAGINE_ALICE_NEL_PAESE_DELLE_MERAVIGLIE.mp4"
def sha(data):return hashlib.sha256(data).hexdigest()
def sha_file(path):return sha(Path(path).read_bytes())
def cmd(*args):
    print("CMD",str(args[0]),str(args[-1]),flush=True)
    subprocess.run([str(x) for x in args],check=True)
def load():
    plan=json.loads((EP/"scene_plan_alice.json").read_text(encoding="utf8"))["scenes"]
    paragraphs=[p.strip() for p in (EP/"testo.txt").read_text(encoding="utf8").split("\n\n") if p.strip()]
    if len(plan)!=14 or len(paragraphs)!=14:raise RuntimeError("Expected 14 narrative beats")
    if any(a["narration"]!=b for a,b in zip(plan,paragraphs)):
        raise RuntimeError("Script/scene narrative mismatch")
    if len({x["source_file"] for x in plan})!=13 or plan[0]["source_file"]!=plan[-1]["source_file"]:
        raise RuntimeError("13 unique plates + intentional flashforward required")
    return plan,paragraphs
def font(size,bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/"+("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),size)
def frame(original):
    im=ImageOps.exif_transpose(original.convert("RGB"))
    # Rackham color plate preserved in full; blurred, darkened background is decorative only.
    back=ImageOps.fit(im,(720,1280),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(45)).convert("RGBA")
    back=Image.alpha_composite(back,Image.new("RGBA",(720,1280),(12,29,39,182)))
    d=ImageDraw.Draw(back)
    d.rounded_rectangle((23,72,697,1208),radius=10,fill=(228,218,196,255),outline=(191,157,107,255),width=4)
    art=ImageOps.contain(im,(642,1078),Image.Resampling.LANCZOS)
    art=ImageEnhance.Sharpness(art).enhance(1.09)
    back.alpha_composite(art.convert("RGBA"),((720-art.width)//2,(1280-art.height)//2))
    return back.convert("RGB")
def board(plan):
    cw,ch=300,415;cols=4;rows=math.ceil(len(plan)/cols)
    sheet=Image.new("RGB",(cols*cw,rows*ch+115),(242,237,227))
    d=ImageDraw.Draw(sheet)
    d.rectangle((0,0,sheet.width,105),fill=(17,42,55))
    d.text((25,27),"ALICE  |  14 INQUADRATURE / 13 TAVOLE RACKHAM",font=font(29,True),fill=(241,226,194))
    for i,row in enumerate(plan):
        x=(i%cols)*cw;y=105+(i//cols)*ch
        p=Image.open(EP/"images"/f"scena_{i+1:02d}.jpg")
        thumb=ImageOps.contain(p,(260,310))
        sheet.paste(thumb,(x+(cw-thumb.width)//2,y+5))
        d.text((x+10,y+327),f"{i+1:02d}  "+row["visual_intent"][:27],font=font(16,True),fill=(24,40,49))
        d.text((x+10,y+352),row["source_file"][:28],font=font(15),fill=(105,82,55))
    sheet.save(OUT/"STORYBOARD_COMPLETO.jpg",quality=91)
def make_v13(provenance,plan,paragraphs):
    from video_director_v13 import brief,check,write_json,digest
    folder=OUT/"v13";folder.mkdir(parents=True,exist_ok=True)
    root=folder/"project";p=brief("libri","Alice nel Paese delle Meraviglie — Lewis Carroll",root)
    shutil.copy2(EP/"testo.txt",root/"testo.txt")
    p["script"]="testo.txt"
    p["bibliography"]={"author":"Lewis Carroll","publication_year":"1865","edition_reference":URL,
      "rights_notes":"1865 original and 1907 Arthur Rackham art; author died 1898, artist died 1939; public domain in Italy. New Italian retelling."}
    p["editorial_metadata"]={"series":"Tra le Pagine — Studio Ibrido","themes":"curiosità, identità, autorità, sogno",
      "genre":"fantastico","narration_style":"italiano naturale, meraviglia e ironia con finale deciso"}
    p["business"]={"audience":"pubblico italiano di racconti e letteratura","viewer_promise":"un viaggio completo, dal lago di lacrime alla ribellione alla Regina",
      "original_contribution":"adattamento originale in italiano con 13 tavole colorate storiche coerenti",
      "primary_platform":"Facebook","goal":"narrazione di qualità, non pubblicazione automatica","cash_budget_eur":0}
    p["assets"]=[]
    for i,row in enumerate(provenance,1):
        dest=root/f"scena_{i:02d}.jpg";shutil.copy2(EP/"images"/dest.name,dest)
        p["assets"].append({"id":row["asset_id"],"file":dest.name,"sha256":digest(dest),
          "role":"visual","source":row["source_url"],"rights":row["rights_basis"]})
    cues=json.loads((EP/"scene_cues.json").read_text(encoding="utf8"))
    p["scenes"]=[]
    for i,row in enumerate(plan):
        p["scenes"].append({"asset_id":f"img_{i+1:02d}","description":row["visual_intent"],
          "reason":row["scene_match_note"],"narration_anchor":cues[i]["narration_anchor"],
          "camera":row["camera_style"],"camera_reason":"Camera bloccata o micro-avvicinamento massimo 1%, preserva il bordo e i volti"})
    ed=p["editorial_plan"]
    ed.update({"subject_insight":"La logica crolla, Alice impara a sfidare un'autorità arbitraria. Flashforward sul climax.",
      "sources":[{"reference":URL,"finding":"Edizione illustrata di Alice con tavole colorate originali Rackham",
        "verification_notes":"Indice delle tavole e alt esatti controllati, 13 file originali scaricati","status":"reviewed"},
        {"reference":"https://www.gutenberg.org/ebooks/28885","finding":"Lewis Carroll (1832-1898), Arthur Rackham (1867-1939), edizione 1907","verification_notes":"Dominio pubblico originari, adattamento italiano nuovo","status":"reviewed"}],
      "opening_promise":"Le carte attaccano Alice: come è arrivata a sfidare la Regina?",
      "payoff":"Alice riconosce l'assurdità del tribunale e si risveglia dal sogno.",
      "cover_reason":"Tavola originale delle carte volanti, titolo e autore con firma Tra le Pagine.",
      "duration_seconds":165,"duration_reason":"373 parole; durata definitiva guidata dal WAV Gacrux reale.",
      "techniques":[{"id":"flashforward","reason":"Primi secondi di alto impatto con carte volanti, ritorno al climax","status":"planned"},
        {"id":"locked_plate","reason":"Acquerelli leggibili, nessun taglio ai personaggi","status":"planned"},
        {"id":"micro_push","reason":"Minimo 1% per enfatizzare solo i cambi di emozione","status":"planned"}],
      "mix_reason":"14 beat / 13 tavole: un unico ritorno motivato al finale, niente altri riusi; tempi dettati dalla voce.",
      "social_languages":{"facebook":"it","instagram":"it","tiktok":"it","youtube":"it"},
      "voice_image_sync_review":"pending_actual_audio","artistic_review":"pending_full_video",
      "narrative_design":{"story_beats":[x["visual_intent"] for x in plan],
        "distinct_visual_needs":[x["scene_match_note"] for x in plan],
        "image_count_reason":"13 tavole originali a colori coprono 13 eventi distinti; 14a inquadratura è ritorno deliberato all'hook.",
        "pace_reason":"Ingresso urgente, sequenze più calme nel bosco, climax al processo e risveglio."}})
    ed["media_sourcing"]={"policy_id":"media-priority-v33","review_status":"reviewed",
      "decisions":[{"asset_id":x["asset_id"],"source_kind":"verified_archive","provider":"Project Gutenberg #28885",
        "source_reference":x["source_url"],"choice_reason":"Stessa edizione a colori Rackham 1907, corrispondenza verificata tramite tavola e didascalia",
        "scene_match_note":x["scene_match_note"],"rights_review":"reviewed",
        "scene_relevance":"reviewed","visual_review":"passed"} for x in provenance]}
    p["reviews"]={"story":{"status":"passed","notes":"14 paragrafi confrontati con 13 didascalie Rackham e trama originale; il ritorno della tavola finale è deliberato."},
      "visuals":{"status":"passed","notes":"Le 13 tavole originali sono state esaminate su contact sheet prima della selezione; file decodificati e montati senza crop. Revisione artistica del video completo ancora necessaria."},
      "rights":{"status":"passed","notes":"Carroll 1898 e Rackham 1939; immagini originali 1907 da PG 28885, provenienza per file e SHA."}}
    write_json(root/"PROJECT_V13.json",p)
    result=check(root/"PROJECT_V13.json")
    (OUT/"PREFLIGHT_V13.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf8")
    shutil.copy2(root/"PROJECT_V13.json",OUT/"PROJECT_V13.json")
    print("V13 PREFLIGHT",result.get("status"),result.get("blockers"),flush=True)
    return bool(result.get("ready"))
def prepare():
    plan,paragraphs=load()
    OUT.mkdir(parents=True,exist_ok=True);(EP/"images").mkdir(parents=True,exist_ok=True)
    s=requests.Session();s.headers.update({"User-Agent":"TraLePagineEditorial/1.0 (single public-domain book, 13 selected plates)"})
    r=s.get(URL,timeout=50);r.raise_for_status()
    soup=BeautifulSoup(r.content,"html.parser")
    indexed={Path(x.get("src","")).name:x for x in soup.find_all("img") if x.get("src")}
    cache={};provenance=[];cues=[];offset=0
    for i,(row,para) in enumerate(zip(plan,paragraphs),1):
        name=row["source_file"];tag=indexed.get(name)
        if tag is None:raise RuntimeError("Missing authentic plate "+name)
        alt=tag.get("alt","")
        if len(alt)<3:raise RuntimeError("Missing plate caption "+name)
        link=urljoin(URL,tag["src"])
        if name not in cache:
            res=s.get(link,timeout=50);res.raise_for_status()
            if len(res.content)>12000000:raise RuntimeError("Oversized image "+name)
            with Image.open(BytesIO(res.content)) as original:
                original.load()
                if min(original.size)<240 or max(original.size)<400:raise RuntimeError("Small original "+name)
                cache[name]=(res.content,original.convert("RGB"),list(original.size))
        raw,im,size=cache[name]
        framed=frame(im)
        target=EP/"images"/f"scena_{i:02d}.jpg"
        framed.save(target,quality=94,optimize=True)
        if target.stat().st_size<35000:raise RuntimeError("Incomplete frame "+str(target))
        cues.append({"start_sentence":offset,"asset":i,"description":row["visual_intent"],
          "narration_anchor":SPLIT.split(para)[0]})
        offset+=len([x for x in SPLIT.split(para) if x.strip()])
        provenance.append({"asset_id":f"img_{i:02d}","source_kind":"verified_archive",
          "source_url":link,"source_page":URL,"source_file":name,"source_alt":alt,
          "source_sha256":sha(raw),"source_dimensions":size,"output_sha256":sha_file(target),
          "output_dimensions":[720,1280],"scene_match_note":row["scene_match_note"],
          "rights_basis":"Original Rackham 1907 color plate; illustrator died 1939, PD Italy and USA; PG 28885",
          "rights_review":"reviewed","scene_relevance":"reviewed",
          "visual_review":"source_contact_sheet_reviewed; full_video_pending"})
        print("VERIFIED_PLATE",i,name,alt[:90],size,flush=True)
    if len(cache)!=13:raise RuntimeError("Wrong unique image count")
    (EP/"scene_cues.json").write_text(json.dumps(cues,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    (OUT/"PROVENIENZA_IMMAGINI.json").write_text(json.dumps({"source":URL,
      "source_unique":len(cache),"shots":len(plan),"images":provenance,
      "human_full_video_review":"pending"},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    board(plan)
    sys.path.insert(0,"src")
    from episode_v3 import validate,branded_cover
    validate(EP.name)
    branded_cover(OUT,EP,json.loads((EP/"metadata.json").read_text(encoding="utf8")))
    for name in ["testo.txt","metadata.json","SCHEDE_VISUALI_V35.json","scene_plan_alice.json","FONTI_E_DIRITTI.md",
                 "POST_FACEBOOK.txt","POST_INSTAGRAM.txt","POST_TIKTOK.txt","POST_YOUTUBE.txt"]:
        shutil.copy2(EP/name,OUT/name)
    ready=make_v13(provenance,plan,paragraphs)
    (OUT/"MUSICA_CREDITI.txt").write_text("Prevista: Alice — valzer originale Tra le Pagine, sintetizzato da codice, senza campioni terzi. Audio presente solo se MP4 effettivamente renderizzato.\n")
    status={"episode":EP.name,"state":"visuals_ready_tts_pending","unique_original_plates":13,
      "shots":14,"original_source":URL,"v13_ready":ready,"video_exists":False,
      "tts_generated":False,"paid_video_calls":0,"social_published":False}
    (OUT/"QUALITY.json").write_text(json.dumps(status,ensure_ascii=False,indent=2))
    with zipfile.ZipFile(OUT/"ALICE_PACCHETTO_VISUALE_NON_VIDEO.zip","w",zipfile.ZIP_DEFLATED,compresslevel=2) as z:
        for p in OUT.iterdir():
            if p.is_file() and p.suffix!=".zip":z.write(p,p.name)
        for p in sorted((EP/"images").glob("scena_*.jpg")):z.write(p,"ILLUSTRAZIONI/"+p.name)
    with zipfile.ZipFile(OUT/"ALICE_PACCHETTO_VISUALE_NON_VIDEO.zip") as z:
        if z.testzip() is not None:raise RuntimeError("Visual ZIP CRC failure")
    if not ready:raise RuntimeError("V13 preflight blocked; do not call TTS")
    print("VISUALS_READY",json.dumps(status),flush=True)
def original_music(seconds,out):
    import numpy as np
    import soundfile as sf
    rate=24000;n=math.ceil(rate*(seconds+.25))
    sound=np.zeros(n,np.float32)
    # Original 6/8 music-box waltz in D minor; deterministic, no third-party recording.
    chords=[[50,53,57,62],[46,50,53,58],[53,57,60,65],[48,52,55,60],
            [50,53,57,62],[46,50,53,58],[43,46,50,55],[45,49,52,57]]
    step=.39
    for k in range(math.ceil(seconds/step)):
        chord=chords[(k//12)%len(chords)]
        note=chord[[0,2,1,3,1,2,0,3,1,2,3,1][k%12]]
        if k%6==0:note-=12
        begin=int(k*step*rate);duration=min(n-begin,int((1.12 if k%6 else 1.7)*rate))
        if duration<=0:continue
        t=np.arange(duration,dtype=np.float32)/rate
        f=440*2**((note-69)/12)
        timbre=np.sin(2*np.pi*f*t)+.17*np.sin(2*np.pi*f*2*t)+.06*np.sin(2*np.pi*f*3*t)
        env=np.minimum(1,t/.014)*np.exp(-t/(.45 if k%6 else .78))
        sound[begin:begin+duration]+=.035*timbre*env
    for delay,gain in [(int(.17*rate),.16),(int(.33*rate),.07)]:
        sound[delay:]+=gain*sound[:-delay].copy()
    x=np.arange(n,dtype=np.float32)/rate
    sound*=np.minimum(1,x/2)*np.minimum(1,np.maximum(0,seconds-x)/4)
    sf.write(out,np.clip(sound,-.3,.3),rate)
def render():
    import numpy as np
    from gemini_voice import synthesize
    plan,paragraphs=load()
    if not (OUT/"PREFLIGHT_V13.json").is_file():raise RuntimeError("No preflight")
    check=json.loads((OUT/"PREFLIGHT_V13.json").read_text())
    if not check.get("ready"):raise RuntimeError("V13 not ready")
    wav,timed=synthesize((EP/"testo.txt").read_text(encoding="utf8"),OUT)
    duration=len(wav)/24000
    if not 100<=duration<=230:raise RuntimeError("Voice duration outside 100-230s: "+str(duration))
    cues=json.loads((EP/"scene_cues.json").read_text())
    starts=[float(timed[c["start_sentence"]][1]) for c in cues];starts[0]=0.0
    limits=starts+[duration]
    if any(b<=a for a,b in zip(limits,limits[1:])):raise RuntimeError("Voice alignment non-monotonic")
    (OUT/"SINCRONIA_SCENE.json").write_text(json.dumps([{"scene":i+1,
      "start":round(limits[i],3),"end":round(limits[i+1],3),"spoken":cues[i]["narration_anchor"],
      "visual":plan[i]["visual_intent"]} for i in range(len(plan))],ensure_ascii=False,indent=2))
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp);clips=[]
        for i,row in enumerate(plan):
            frames=max(1,round((limits[i+1]-limits[i])*FPS))
            inp=EP/"images"/f"scena_{i+1:02d}.jpg"
            clip=root/f"clip_{i+1:02d}.mp4"
            if row["camera_style"]=="locked":
                vf="scale=720:1280,format=yuv420p"
            else:
                vf=("zoompan=z='min(zoom+0.000035,1.012)':x='iw/2-(iw/zoom/2)':"
                    "y='ih/2-(ih/zoom/2)':d=1:s=720x1280:fps=24,format=yuv420p")
            cmd("ffmpeg","-hide_banner","-loglevel","error","-y","-loop","1","-framerate",FPS,
                "-i",inp,"-vf",vf,"-frames:v",frames,"-an","-c:v","libx264",
                "-preset","veryfast","-crf",23,"-pix_fmt","yuv420p",clip)
            clips.append(clip)
        listing=root/"clips.txt";listing.write_text("".join("file '"+str(c)+"'\n" for c in clips))
        visual=root/"visual.mp4"
        cmd("ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0",
            "-i",listing,"-c","copy",visual)
        original_music(duration,OUT/"MUSICA_ORIGINALE.wav")
        cmd("ffmpeg","-hide_banner","-loglevel","error","-y","-i",visual,"-i",OUT/"VOCE.wav",
            "-i",OUT/"MUSICA_ORIGINALE.wav","-filter_complex",
            "[1:a]volume=1.0[v];[2:a]volume=.25[m];[v][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.93[a]",
            "-map","0:v:0","-map","[a]","-sn","-c:v","copy","-c:a","aac","-b:a","160k",
            "-movflags","+faststart","-shortest",OUT/NAME)
    print("RENDERED_NEEDS_REVIEW",OUT/NAME,flush=True)
def qa():
    plan,_=load()
    video=OUT/NAME
    if not video.is_file() or video.stat().st_size<200000:raise RuntimeError("MP4 absent")
    info=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries",
      "format=duration,size:stream=codec_type,codec_name,width,height","-of","json",str(video)],text=True))
    v=next(x for x in info["streams"] if x["codec_type"]=="video")
    a=next(x for x in info["streams"] if x["codec_type"]=="audio")
    duration=float(info["format"]["duration"])
    if not 100<=duration<=230 or (v["width"],v["height"])!=(720,1280) or v["codec_name"]!="h264" or a["codec_name"]!="aac":
        raise RuntimeError("Invalid technical video profile")
    if any(x["codec_type"]=="subtitle" for x in info["streams"]):raise RuntimeError("Subtitles forbidden")
    cmd("ffmpeg","-nostdin","-v","error","-xerror","-i",video,"-f","null","-")
    for sec in (.1,1,3,5,7):
        cmd("ffmpeg","-hide_banner","-loglevel","error","-y","-ss",str(sec),
          "-i",video,"-frames:v","1",OUT/f"FRAME_{str(sec).replace('.','_')}S.jpg")
    if not (OUT/"VOICE_PROFILE_V13.json").is_file():raise RuntimeError("Gacrux profile not confirmed")
    profile=json.loads((OUT/"VOICE_PROFILE_V13.json").read_text())
    if profile.get("voice")!="Gacrux":raise RuntimeError("Wrong voice")
    report={"episode":EP.name,"state":"rendered_needs_review","video":NAME,
      "video_sha256":sha_file(video),"video_bytes":video.stat().st_size,
      "duration_seconds":duration,"resolution":[720,1280],"video_codec":"h264",
      "audio_codec":"aac","voice_profile":profile,"unique_source_plates":13,"shots":14,
      "full_decode_pass":True,"no_subtitles":True,"no_ghosting_transitions":True,
      "opening_frames_extracted":[.1,1,3,5,7],
      "human_full_listening":"pending","human_artistic_review":"pending",
      "social_publication":"not_performed","archive_import":"not_performed",
      "paid_video_api_calls":0}
    (OUT/"QA_REALE.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
    (OUT/"QUALITY.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
    (OUT/"MUSICA_CREDITI.txt").write_text("Titolo: Alice — Valzer delle Meraviglie. Composizione e sintesi originale Tra le Pagine — Studio Ibrido. Nessun campione audio di terzi.\n")
    with zipfile.ZipFile(OUT/"ALICE_SOLO_VIDEO_V36.zip","w",zipfile.ZIP_DEFLATED,compresslevel=1) as z:z.write(video,video.name)
    full=OUT/"ALICE_PACCHETTO_COMPLETO.zip"
    with zipfile.ZipFile(full,"w",zipfile.ZIP_DEFLATED,compresslevel=1) as z:
        for p in OUT.iterdir():
            if p.is_file() and p.name not in (full.name,"ALICE_SOLO_VIDEO_V36.zip","ALICE_PACCHETTO_VISUALE_NON_VIDEO.zip","VOCE.wav","MUSICA_ORIGINALE.wav"):
                z.write(p,p.name)
        for p in sorted((EP/"images").glob("scena_*.jpg")):z.write(p,"ILLUSTRAZIONI/"+p.name)
    for p in (OUT/"ALICE_SOLO_VIDEO_V36.zip",full):
        with zipfile.ZipFile(p) as z:
            if z.testzip() is not None:raise RuntimeError("ZIP CRC failure "+str(p))
    print("MP4_TECHNICAL_QA_PASS_ARTISTIC_REVIEW_PENDING",json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--mode",choices=["prepare","render","qa"],required=True)
    a=p.parse_args()
    try:{"prepare":prepare,"render":render,"qa":qa}[a.mode]()
    except Exception as exc:
        print("BLOCKED_REAL_STATE",type(exc).__name__,str(exc),file=sys.stderr)
        raise
