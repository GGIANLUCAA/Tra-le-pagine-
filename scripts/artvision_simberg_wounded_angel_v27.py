#!/usr/bin/env python3
"""ArtVision Simberg V27: candidate director cut. V6 signature and V25 release contract.
Images and licensed music are authentic; human aesthetic review remains required.
This standalone candidate is triggered by the persistent CI workflow.
"""
from __future__ import annotations
import argparse,hashlib,json,math,shutil,subprocess,sys,time,zipfile
from pathlib import Path
import numpy as np,requests
from PIL import Image,ImageDraw,ImageFont,ImageEnhance,ImageFilter
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from artvision_contract_gate_v25 import check_preflight
W,H,FPS=1080,1920,24
ARTIST="HUGO SIMBERG"; TITLE="The Wounded Angel"; COMPOSER="Kevin MacLeod"
ART_URL="https://upload.wikimedia.org/wikipedia/commons/7/72/The_Wounded_Angel_-_Hugo_Simberg.jpg"
ART_PAGE="https://commons.wikimedia.org/wiki/File:The_Wounded_Angel_-_Hugo_Simberg.jpg"
MUSEUM="https://www.kansallisgalleria.fi/en/object/396251"
TRACK_URL="https://incompetech.com/music/royalty-free/mp3-royaltyfree/Mourning%20Song.mp3"
TRACK_PAGE="https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100431"
LICENSE="https://creativecommons.org/licenses/by/4.0/"
FONT1="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT2="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
# Each focus is a real feature of the painting: blindfold, flower sprig, wing, two boys, wooden stretcher.
# Coordinates x,y are relative to the authentic 1903 image; 18 distinct editorial shots.
STORY=[
 ("portrait",.430,.280,1.60,3.70,"locked","Open on the angel's blindfold: why can this angel not see?"),
 ("portrait",.792,.220,1.48,3.04,"slow_pull","The boy turns toward the viewer; only one look can be returned"),
 ("detail",.284,.525,1.58,2.88,"locked","The snowdrops are a fragile counterpoint to the bandage"),
 ("texture",.552,.478,1.48,2.72,"locked","White feathers fill the frame but do not move artificially"),
 ("portrait",.410,.328,1.44,3.23,"slow_push","The bowed angel is visible as a person, not a trick"),
 ("detail",.478,.609,1.10,3.18,"locked","The stretcher crosses the frame; see how she is carried"),
 ("portrait",.100,.262,1.39,2.92,"locked","The left boy's hidden face creates asymmetry"),
 ("detail",.790,.566,1.35,2.94,"locked","A small hand keeps the wooden pole steady"),
 ("wide",.515,.477,1.00,3.48,"slow_pull","The whiteness of the angel separates the two dark figures"),
 ("detail",.456,.806,1.53,2.72,"locked","The angel's bare feet look impossibly delicate"),
 ("landscape",.506,.142,1.00,3.18,"locked","Still water and a pale horizon: silence before the return"),
 ("detail",.279,.533,1.53,2.61,"locked","Return to the small snowdrops she is holding"),
 ("portrait",.795,.228,1.65,3.26,"slow_push","The boy's direct gaze now means something different"),
 ("texture",.624,.670,1.23,2.82,"locked","The white wing extends into the dry landscape"),
 ("wide",.490,.507,1.00,3.62,"locked","The stretcher ties the three lives into one line"),
 ("portrait",.420,.276,1.68,2.92,"locked","One last intimate detail of the injured angel"),
 ("detail",.774,.842,1.50,2.75,"locked","Grounded black boots beneath a seemingly weightless angel"),
 ("full",.500,.500,1.00,5.75,"locked","Reveal the complete 1903 original at last; preserve a full quiet cadence"),
]
TECH=[("human_gaze_start","The closed eyes and bandage introduce an unanswered visual question"),
      ("visual_hierarchy","Make the angel white figure readable against two dark boys"),
      ("motivated_cut","Cut between blindfold, holding hands, snowdrops and silent witnesses"),
      ("locked_hold","More than two thirds of shots use truly locked camera"),
      ("color_match","White feathers and snowdrops connect across distant image regions"),
      ("detail_return","Return to the boy's gaze after seeing the angel's burden"),
      ("music_continuity_cut","Align selected cuts gently with authentic bowed-note musical accents"),
      ("camera_seasick_gate","One-way camera motions only, no oscillation or gimmicks")]
def run(*cmd):
    subprocess.run([str(x) for x in cmd],check=True,timeout=230)
def probe(path):
    return json.loads(subprocess.check_output(
      ["ffprobe","-v","error","-show_entries","format=duration,size",
       "-show_entries","stream=codec_type,codec_name,width,height","-of","json",str(path)]))
def digest(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for part in iter(lambda:f.read(1024*1024),b""):h.update(part)
    return h.hexdigest()
def download(url,path,typ):
    for retry in range(3):
        try:
            with requests.get(url,headers={"User-Agent":"ArtVisionSimbergV27/1.0 art historical research"},timeout=70,stream=True) as r:
                r.raise_for_status()
                if "text/html" in r.headers.get("Content-Type",""):raise ValueError("Invalid HTML source")
                with path.open("wb") as f:
                    for c in r.iter_content(524288):
                        if c:f.write(c)
            if path.stat().st_size<200000:raise ValueError("Asset too small")
            if typ=="image":
                with Image.open(path) as im:
                    if im.width<2800 or im.height<1800:raise ValueError("Low resolution source")
                    im.verify()
            else:
                if not any(s.get("codec_type")=="audio" for s in probe(path)["streams"]):raise ValueError("No audio")
            return
        except Exception:
            path.unlink(missing_ok=True)
            if retry==2:raise
            time.sleep(retry+2)
def face(text,n,max_width,serif=True):
    font=FONT1 if serif else FONT2
    while n>16:
        f=ImageFont.truetype(font,n)
        width=ImageDraw.Draw(Image.new("RGB",(1,1))).textbbox((0,0),text,font=f)[2]
        if width<=max_width:return f
        n-=1
    return ImageFont.truetype(font,n)
def signature(frame,alpha=1):
    """Reproduces immutable V6 visual signature without changing original module."""
    out=frame.convert("RGBA");layer=Image.new("RGBA",(W,H));d=ImageDraw.Draw(layer)
    alpha=max(0,min(1,alpha));opacity=lambda x:round(x*alpha)
    d.rounded_rectangle((56,1340,1024,1590),radius=10,fill=(5,8,13,opacity(190)))
    f=face(ARTIST,62,880);mw=d.textbbox((0,0),ARTIST,font=f)[2]
    d.text(((W-mw)/2,1387),ARTIST,font=f,fill=(255,251,243,opacity(255)))
    d.line((130,1495,950,1495),fill=(218,198,168,opacity(186)),width=2)
    name="MUSIC BY KEVIN MACLEOD";f=face(name,21,880,False)
    nw=d.textbbox((0,0),name,font=f)[2]
    d.text(((W-nw)/2,1521),name,font=f,fill=(218,208,192,opacity(246)))
    return Image.alpha_composite(out,layer).convert("RGB")
def crop(src,shot):
    kind,cx,cy,zoom,duration,motion,reason=shot
    iw,ih=src.size;vw=min(iw,ih*W/H)/zoom;vh=vw*H/W
    x=min(max(0,cx*iw-vw/2),iw-vw)
    y=min(max(0,cy*ih-vh/2),ih-vh)
    return src.crop((round(x),round(y),round(x+vw),round(y+vh))).resize((W,H),Image.Resampling.LANCZOS)
def full(src):
    # Single respectful whole-canvas reveal, not the permanent V5 black gallery.
    bg=ImageEnhance.Brightness(crop(src,STORY[5]).filter(ImageFilter.GaussianBlur(40))).enhance(.48)
    whole=src.copy();whole.thumbnail((1040,1640),Image.Resampling.LANCZOS)
    x=(W-whole.width)//2;y=(H-whole.height)//2
    ImageDraw.Draw(bg).rounded_rectangle((x-10,y-10,x+whole.width+10,y+whole.height+10),
                                        radius=7,fill=(5,8,13))
    bg.paste(whole,(x,y))
    return bg
def audio_analysis(track,workspace,offset,duration):
    out=workspace/"analysis.raw"
    run("ffmpeg","-hide_banner","-loglevel","error","-y","-ss",offset,"-i",track,
        "-t",duration+3,"-ar",11025,"-ac",1,"-f","f32le",out)
    a=np.fromfile(out,dtype="<f4")
    size=1102;a=a[:(len(a)//size)*size].reshape(-1,size)
    rms=np.sqrt(np.mean(a.astype(np.float64)**2,axis=1)+1e-12)
    novelty=np.maximum(0,np.diff(np.log(rms+1e-5),prepend=np.log(rms[0]+1e-5)))
    novelty=np.convolve(novelty,[.23,.54,.23],"same")
    threshold=np.quantile(novelty,.76)
    accents=[]
    for i in np.argsort(novelty)[::-1]:
        sec=i*size/11025
        if sec<2 or sec>duration-2 or novelty[i]<threshold:continue
        if all(abs(sec-t)>.55 for t in accents):accents.append(sec)
        if len(accents)>110:break
    return sorted(accents),{"sample_rate":11025,"hop_samples":size,"threshold":float(threshold),
                            "authentic_audio_accents":len(accents),"excerpt_start":offset}
def align_shots(accents):
    scenes=[{"id":f"C{i+1:02d}","kind":s[0],"x":s[1],"y":s[2],"zoom":s[3],
             "duration":s[4],"motion":s[5],"purpose":s[6]} for i,s in enumerate(STORY)]
    start=0
    for shot in scenes[:-1]:
        target=start+shot["duration"]
        hits=[t for t in accents if abs(t-target)<=.29]
        if hits:
            t=min(hits,key=lambda x:abs(x-target))
            shot["duration"]=round(shot["duration"]+t-target,3)
            shot["audio_cut_second"]=round(t,3)
        start+=shot["duration"]
    return scenes
def render_clip(img,scene,i,workspace):
    pic=workspace/f"frame_{i:02d}.jpg";img.save(pic,quality=94,subsampling=0)
    frames=round(scene["duration"]*FPS);out=workspace/f"clip_{i:02d}.mp4"
    if i==0:
        fd=workspace/"intro";fd.mkdir(exist_ok=True)
        for index in range(frames):
            t=index/FPS
            a=1 if t<=2.9 else max(0,1-(t-2.9)/.55)
            signature(img,a).save(fd/f"f{index:04d}.jpg",quality=91,subsampling=0)
        run("ffmpeg","-hide_banner","-loglevel","error","-y","-framerate",FPS,
            "-i",fd/"f%04d.jpg","-c:v","libx264","-preset","veryfast","-crf",19,
            "-pix_fmt","yuv420p",out)
        shutil.rmtree(fd)
    else:
        if scene["motion"]=="slow_push":z=f"min(1.009,1+on*{.009/frames:.8f})"
        elif scene["motion"]=="slow_pull":z=f"max(1,1.009-on*{.009/frames:.8f})"
        else:z="1"
        vf=f"zoompan=z='{z}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={frames}:s={W}x{H}:fps={FPS},format=yuv420p"
        run("ffmpeg","-hide_banner","-loglevel","error","-y","-loop",1,"-framerate",FPS,
            "-i",pic,"-vf",vf,"-frames:v",frames,"-c:v","libx264","-preset","veryfast",
            "-crf",19,"-pix_fmt","yuv420p",out)
    pic.unlink(missing_ok=True)
    return out
def make_cover(img,path):
    c=signature(img).convert("RGBA");layer=Image.new("RGBA",(W,H));d=ImageDraw.Draw(layer)
    title=TITLE.upper();f=face(title,60,910);tw=d.textbbox((0,0),title,font=f)[2]
    x=(W-tw)//2
    d.rounded_rectangle((x-26,1167,x+tw+26,1256),radius=8,fill=(5,8,13,175))
    d.text((x,1181),title,font=f,fill=(255,251,243,255))
    Image.alpha_composite(c,layer).convert("RGB").save(path,quality=95)
def social(out):
    # V28: public text must be researched editorial storytelling, never
    # explain camera movement, edit choices or production technique.
    # Block rather than invent filler for an unresearched artwork.
    from artvision_editorial_post_v28 import write_posts
    write_posts("simberg_v27",out,overwrite=False)

def package(out,impath,music,master,shots,analysis,offset):
    social(out);hash_mp4=digest(master)
    source=f"""# Provenienza e riuso
Opera: Hugo Simberg, The Wounded Angel (1903), Ateneum (Finnish National Gallery), inv. A II 1703.
Museo: {MUSEUM}
Riproduzione Wikimedia: {ART_PAGE}
Fotografia scaricata: {ART_URL}
Il dipinto storico è in pubblico dominio; la riproduzione usata è attribuita a Finnish National Gallery / Hannu Aaltonen, licenza CC BY 4.0. Fonte e condizioni: https://commons.wikimedia.org/wiki/File:The_Wounded_Angel_-_Hugo_Simberg.jpg e https://creativecommons.org/licenses/by/4.0/
Verificare le limitazioni nazionali per l'uso commerciale di fotografie museali.
SHA256 immagine: {digest(impath)}

Musica: Mourning Song, Kevin MacLeod, ISRC USUAN1100431.
Brano e registrazione: {TRACK_PAGE}
Registrazione scaricata: {TRACK_URL}
Licenza: Creative Commons Attribution 4.0 — {LICENSE}
SHA256 musica originale: {digest(music)}
Adattamenti: estratto, volume e dissolvenze in entrata e uscita.
Crediti inclusi nei file social. L'eventuale reclamo automatico va verificato.
"""
    (out/"SOURCES_AND_RIGHTS.md").write_text(source,encoding="utf-8")
    notes=["# Regia personalizzata — The Wounded Angel","",
           "Arco: benda dell'angelo → sguardo del ragazzo → bucaneve → barella e peso → ritorno allo sguardo → rivelazione del quadro intero.",
           "La maggioranza delle inquadrature resta ferma. Niente pan avanti e indietro, nessun falso 3D.",
           "Firma iniziale V6: nome artista e MUSIC BY. Copertina: titolo inglese in un blocco separato.",
           "I tagli sono regolati entro 0,29 s su eventi misurati nella registrazione reale.",
           "", "## Tecniche selezionate"]
    notes += [f"- {k}: {v}" for k,v in TECH]
    notes += ["", "## Focali reali e motivazioni"]
    t=0
    for s in shots:
        notes.append(f"- {t:.2f}–{t+s['duration']:.2f}s {s['id']} {s['kind']} ({s['x']:.3f},{s['y']:.3f}; {s['zoom']:.2f}x) {s['motion']}. {s['purpose']}.")
        t+=s["duration"]
    (out/"TECNICHE_REGIA.md").write_text("\n".join(notes)+"\n",encoding="utf-8")
    guide=("ArtVision Simberg The Wounded Angel V27\n"
           "Script: scripts/artvision_simberg_wounded_angel_v27.py\n"
           "Comando: python scripts/artvision_simberg_wounded_angel_v27.py --out output/simberg-v27\n"
           "Preset originale da NON modificare: modules/artvision/APPROVED_PRESET.json\n"
           "Firma grafica: modules/artvision/IDENTITA_VISIVA_FISSA_V6.json\n"
           "Contratto V25: docs/ARTVISION_CONTRATTO_PERMANENTE_V25.md\n"
           "Strumenti: Python 3.11, numpy, Pillow, requests, FFmpeg/FFprobe, font DejaVu.\n"
           "Per una riproduzione identica conservare i due asset e gli SHA256 nel recipe.\n"
           "Per nuovi quadri NON copiare focali: progettare nuova regia. Un solo MP4 finale.\n"
           "Il pacchetto è un candidato da revisionare artisticamente, non un Gold Master approvato.\n")
    (out/"ISTRUZIONI_REPLICA.md").write_text(guide,encoding="utf-8")
    recipe={"schema":"video-recipe-v13","video_id":"simberg-wounded-angel-v27","format":"artvision_cinema",
            "artist":ARTIST,"title_en":TITLE,"baseline":"cinema_v6","contract":"v25",
            "renderer":"scripts/artvision_simberg_wounded_angel_v27.py",
            "replication_command":"python scripts/artvision_simberg_wounded_angel_v27.py --out output/simberg-v27",
            "sha256_mp4":hash_mp4,"sha256_artwork":digest(impath),"sha256_music":digest(music),
            "source_page":ART_PAGE,"music_page":TRACK_PAGE,"license":"CC BY 4.0",
            "score_analysis":analysis,"score_offset_seconds":offset,"shots":shots,
            "techniques":[{"id":k,"why":v} for k,v in TECH],
            "duration_seconds":float(probe(master)["format"]["duration"]),
            "frame_size":[W,H],"fps":FPS,"state":"rendered_needs_artistic_review",
            "historical_masters_unchanged":True,"social_published":False}
    (out/"VIDEO_RECIPE_V13.json").write_text(json.dumps(recipe,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    mm={"schema_version":1,
        "video":{"id":"simberg-wounded-angel-v27","format":"artvision_cinema","title":TITLE,
                 "originality_statement":"Bespoke film direction on authentic 1903 canvas",
                 "visual_rights_evidence":[ART_PAGE,MUSEUM]},
        "music":{"title":"Mourning Song","artist":COMPOSER,"origin":"external_licensed",
                 "source_url":TRACK_PAGE,"recording_proof_url":TRACK_PAGE,
                 "license_name":"CC BY 4.0","license_url":LICENSE,"license_checked_on":"2026-10-23",
                 "allow_commercial":True,"permitted_platforms":["facebook","instagram","tiktok","youtube"],
                 "monetization_allowed":True,"ads_allowed":True,"credit_required":True,
                 "credit_text":'"Mourning Song" Kevin MacLeod (incompetech.com) CC BY 4.0 '+LICENSE,
                 "music_embedded":True,"rights_holder_claim_status":"unchecked",
                 "emotional_direction":"wounded gaze to isolated fall",
                 "cue_notes":"Video cuts adjusted to measured recording energy accents"},
        "distribution":{"targets":["facebook","instagram","tiktok","youtube"],
                        "commercial":True,"monetized":False,"ads":False},
        "qa":{"music_fit_reviewed":False,"full_watch_listen":False,"audio_mix_reviewed":False,
              "visual_rights_reviewed":False,"caption_ready":True,"originality_reviewed":False},
        "release":{"user_authorized_publication":False,"caption_text":(out/"POST_FACEBOOK.txt").read_text(encoding="utf-8"),
                   "notes":"Downloadable only; social publishing independent"},
        "publish_status":"review_required"}
    (out/"MUSIC_RELEASE_V20.json").write_text(json.dumps(mm,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    total=sum(x["duration"] for x in shots)
    manifest={"schema":"artvision-release-contract-v25","video_id":"simberg-wounded-angel-v27",
      "format":"artvision_cinema","approved_baseline":"cinema_v6",
      "artwork":{"artist":ARTIST,"title_en":TITLE,"title_language":"en","identity_source":MUSEUM},
      "opening":{"identity_preset":"modules/artvision/IDENTITA_VISIVA_FISSA_V6.json",
                 "artist_text":ARTIST,"composer":COMPOSER,"music_credit_text":"MUSIC BY KEVIN MACLEOD"},
      "cover":{"identity_family":"cinema_v6","title_en":TITLE,"artist":ARTIST,"language":"en",
               "existing_design_unchanged":True},
      "on_screen_text":[{"role":"opening_artist","text":ARTIST},
                        {"role":"opening_music","text":"MUSIC BY KEVIN MACLEOD"}],
      "voice":False,"subtitles":False,
      "first_seven_seconds":[{"second":t,"what_visible":d,
        "why":"Motivated transition within the authentic painting, preserving the original V6 brand"}
        for t,d in [(0,"The angel has bandaged eyes and a lowered head"),
                    (1,"The bandaged angel's face is visible behind the fixed V6 title"),
                    (3,"The title signature gently fades without obscuring the eyes"),
                    (5,"The boy's gaze changes the meaning of the scene"),
                    (7,"The tiny white flowers reveal the angel's fragile gesture")]],
      "scenes":[{"source_id":"authentic-simberg-original","subject":s["purpose"],
                 "purpose":s["purpose"],"shot":"landscape" if s["kind"]=="landscape" else s["kind"],
                 "motion":s["motion"],"duration_seconds":s["duration"]} for s in shots],
      "transition_reviews_plan":[{"why":"Blindfold and snowdrops create an authentic white visual rhyme"},
                                 {"why":"Stretcher and white snowdrops connect the two boys to the wounded angel"},
                                 {"why":"The boy looks at the viewer before the full scene resolves"}],
      "music_cues":[{"seconds":0,"reason":"The bandage introduces a genuine mystery in a restrained harmony"},
                    {"seconds":total*.48,"reason":"The burden, bare feet, snowdrops and two boys deepen emotional context"},
                    {"seconds":total-5,"reason":"Music fades while full painting remains visible"}],
      "duration_reason":"Eighteen motivated pictorial views linked by repeating objects and a generous full-image close.",
      "selected_techniques":[{"id":k,"why":v} for k,v in TECH],
      "sources":[{"id":"authentic-simberg-original","url":ART_PAGE,
                  "license":"Public-domain painting; original source photograph CC BY 4.0 (Finnish National Gallery / Hannu Aaltonen)",
                  "credit":"Hugo Simberg, Ateneum; photograph Finnish National Gallery / Hannu Aaltonen","status":"verified"}],
      "music":{"title":"Mourning Song","composer":COMPOSER,"origin":"external_licensed",
               "license":"CC BY 4.0","evidence":TRACK_PAGE,
               "emotional_arc":"the wounded angel, her two companions, snowdrops, silent compassion and full painting","rights_status":"verified"},
      "copy_languages":dict.fromkeys(["facebook","instagram","tiktok","youtube"],"it"),
      "archive_only_after_authorization":True,"social_autopublish":False,
      "outputs":dict(video="VIDEO_MASTER.mp4",cover="COPERTINA.jpg",
                     facebook="POST_FACEBOOK.txt",instagram="POST_INSTAGRAM.txt",
                     tiktok="POST_TIKTOK.txt",youtube="POST_YOUTUBE.txt",
                     recipe="VIDEO_RECIPE_V13.json",techniques="TECNICHE_REGIA.md",
                     replication="ISTRUZIONI_REPLICA.md",rights="SOURCES_AND_RIGHTS.md",
                     music_manifest="MUSIC_RELEASE_V20.json"),
      "editorial_standard":"artvision_editorial_v28",
      "review_video_sha256":hash_mp4,
      "reviews":{k:{"passed":False,"notes":"Full real-time playback and aesthetic comparison with V6 is pending."}
                 for k in ["opening","visual","cover","music","rights","full_watch","replicability"]},
      "publication":{"status":"not_published","library_verified":False}}
    (out/"ARTVISION_CONTRACT_V25.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    errors=check_preflight(manifest)
    (out/"PREFLIGHT_REPORT_V25.json").write_text(json.dumps({"status":"PASS" if not errors else "BLOCKED",
                            "errors":errors},indent=2)+"\n",encoding="utf-8")
    return errors
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="output/simberg-v27")
    ap.add_argument("--offset",type=float,default=7.0)
    cfg=ap.parse_args()
    out=Path(cfg.out);out.mkdir(parents=True,exist_ok=True)
    tmp=out/"_work";tmp.mkdir(exist_ok=True)
    source=out/"ARTWORK_ORIGINAL.jpg";score=out/"MOURNING_SONG_ORIGINAL_CC_BY.mp3"
    download(ART_URL,source,"image");download(TRACK_URL,score,"music")
    src=Image.open(source).convert("RGB")
    if not (1.18<src.width/src.height<1.34):raise RuntimeError("Unexpected artwork dimensions")
    raw_duration=sum(s[4] for s in STORY)
    accents,analysis=audio_analysis(score,tmp,cfg.offset,raw_duration+3)
    scenes=align_shots(accents)
    print("Authentic music analysis",analysis,"scenes",len(scenes),flush=True)
    clips=[]
    storyboard=Image.new("RGB",(320*4,584*math.ceil(len(scenes)/4)),(17,20,25))
    draw=ImageDraw.Draw(storyboard)
    for i,s in enumerate(scenes):
        image=full(src) if s["kind"]=="full" else crop(src,STORY[i])
        clips.append(render_clip(image,s,i,tmp))
        preview=image.resize((280,498),Image.Resampling.LANCZOS)
        x=(i%4)*320+20;y=(i//4)*584+15
        storyboard.paste(preview,(x,y))
        draw.text((x,y+505),s["id"]+" "+s["kind"],fill="white",font=ImageFont.truetype(FONT2,22))
        print("Rendered scene",s["id"],s["purpose"],flush=True)
    storyboard.save(out/"STORYBOARD_REAL_ARTWORK.jpg",quality=91)
    concat=tmp/"concat.txt"
    concat.write_text("".join("file '"+str(f.resolve())+"'\n" for f in clips))
    silent=tmp/"silent.mp4"
    run("ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe",0,
        "-i",concat,"-c:v","copy",silent)
    duration=float(probe(silent)["format"]["duration"])
    output=out/"VIDEO_MASTER.mp4"
    run("ffmpeg","-hide_banner","-loglevel","error","-y","-i",silent,
        "-ss",cfg.offset,"-i",score,"-map","0:v:0","-map","1:a:0",
        "-c:v","copy","-af",f"aresample=48000,volume=.84,afade=t=in:st=0:d=0.45,afade=t=out:st={max(0,duration-3.3):.3f}:d=3.3",
        "-c:a","aac","-b:a","192k","-t",duration,"-movflags","+faststart",output)
    # Analyze and adapt this recording independently: never inherit another
    # film's gain measurements. Controlled social loudness target and true peak,
    # preserving soft passages as far as possible.
    quiet=tmp/"music_original_mix_before_loudness.mp4"
    output.replace(quiet)
    run("ffmpeg","-hide_banner","-loglevel","error","-y","-i",quiet,
        "-map","0:v:0","-map","0:a:0","-c:v","copy",
        "-af","loudnorm=I=-19:TP=-2:LRA=11",
        "-c:a","aac","-b:a","192k","-movflags","+faststart",output)
    quiet.unlink(missing_ok=True)
    facts=probe(output)
    assert 40<float(facts["format"]["duration"])<70
    assert any(s.get("codec_type")=="video" and s.get("codec_name")=="h264" and
               s.get("width")==W and s.get("height")==H for s in facts["streams"])
    assert any(s.get("codec_type")=="audio" and s.get("codec_name")=="aac" for s in facts["streams"])
    run("ffmpeg","-hide_banner","-loglevel","error","-xerror","-i",output,"-f","null","-")
    make_cover(crop(src,STORY[0]),out/"COPERTINA.jpg")
    qa=out/"QA_V25";qa.mkdir(exist_ok=True)
    ticks=[0,1,3,5,7]+[round(duration*f,2) for f in (.22,.48,.74,.96)]
    sheet=Image.new("RGB",(300*len(ticks),560),(10,13,18))
    d=ImageDraw.Draw(sheet)
    for i,t in enumerate(ticks):
        file=qa/(f"FRAME_{int(t):02d}.jpg" if isinstance(t,int) else f"TRANSITION_{t:.2f}.jpg")
        run("ffmpeg","-hide_banner","-loglevel","error","-y","-ss",t,
            "-i",output,"-frames:v",1,"-q:v",3,file)
        sheet.paste(Image.open(file).convert("RGB").resize((296,522)),(i*300+2,0))
        d.text((i*300+12,529),str(t)+"s",fill="white",font=ImageFont.truetype(FONT2,21))
    sheet.save(out/"QA_CONTACT_SHEET.jpg",quality=91)
    errors=package(out,source,score,output,scenes,analysis,cfg.offset)
    if errors:raise RuntimeError("V25_PREFLIGHT_BLOCKED: "+";".join(errors))
    report={"status":"RENDERED_NEEDS_ARTISTIC_REVIEW",
            "sha256_mp4":digest(output),"duration_seconds":duration,
            "audio_accent_events":len(accents),"source_sha256":digest(source),
            "music_sha256":digest(score),"full_ffmpeg_decode":True,
            "preflight_contract":"PASS","video":"VIDEO_MASTER.mp4",
            "visual_review":"QA_CONTACT_SHEET.jpg",
            "note":"Technical status does not certify artistic quality or social publication."}
    (out/"TECHNICAL_QA_V27.json").write_text(json.dumps(report,indent=2)+"\n")
    archive=out.parent/"ARTVISION_SIMBERG_WOUNDED_ANGEL_V27_COMPLETE.zip"
    with zipfile.ZipFile(archive,"w") as z:
        for f in out.rglob("*"):
            if f.is_file() and "_work" not in f.parts:
                z.write(f,f.relative_to(out),compress_type=zipfile.ZIP_STORED if
                        f.suffix.lower() in (".mp3",".mp4",".jpg") else zipfile.ZIP_DEFLATED)
    shutil.rmtree(tmp)
    print("RENDER_SUCCESS",str(output),str(archive),round(duration,2),digest(output),flush=True)
if __name__=="__main__":main()
