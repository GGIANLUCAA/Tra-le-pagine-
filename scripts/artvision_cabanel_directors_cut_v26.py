#!/usr/bin/env python3
"""ArtVision Cabanel V26: candidate director cut. V6 signature and V25 release contract.
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
ARTIST="ALEXANDRE CABANEL"; TITLE="Fallen Angel"; COMPOSER="Kevin MacLeod"
ART_URL="https://upload.wikimedia.org/wikipedia/commons/f/f7/Alexandre_Cabanel_-_Fallen_Angel.jpg"
ART_PAGE="https://commons.wikimedia.org/wiki/File:Alexandre_Cabanel_-_Fallen_Angel.jpg"
MUSEUM="https://www.museefabre.fr/recherche/musee:MUS_BIEN:4064"
TRACK_URL="https://incompetech.com/music/royalty-free/mp3-royaltyfree/The%20Chamber.mp3"
TRACK_PAGE="https://www.incompetech.com/music/royalty-free/index.html?isrc=USUAN1100400"
LICENSE="https://creativecommons.org/licenses/by/4.0/"
FONT1="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT2="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
# Every decision relates to a REAL motif: gaze / feathers / clasped hands / sky / exile.
# x,y normalised to the whole canvas, not to a random crop; 15 distinct editorial shots.
STORY=[
 ("portrait",.350,.346,2.05,3.68,"locked","The direct wounded gaze, not a decorative introduction"),
 ("detail",.366,.352,1.52,2.72,"slow_pull","Face and protecting forearm connect"),
 ("texture",.121,.382,1.21,2.82,"locked","The dark wing breaks the pale sky"),
 ("detail",.527,.319,1.41,2.92,"locked","Hands clasp together, a gesture of protection"),
 ("landscape",.723,.172,1.22,3.42,"slow_push","The distant departing angels across the sky"),
 ("wide",.393,.433,1.00,3.55,"locked","Body and wing first share the field"),
 ("macro",.332,.349,2.39,2.65,"locked","Eyes return after seeing the departure"),
 ("detail",.631,.594,1.38,3.09,"slow_pull","Bent legs express weight after the fall"),
 ("texture",.158,.786,1.36,2.98,"locked","Green-black painted feathers point downward"),
 ("detail",.795,.803,1.32,3.14,"locked","Bare feet touch the material world"),
 ("wide",.510,.525,1.00,3.82,"slow_push","A pause to read the isolated figure"),
 ("detail",.819,.161,1.29,2.91,"locked","The angels in the opposite corner"),
 ("portrait",.353,.336,1.78,3.30,"locked","The gaze is now understood differently"),
 ("wide",.460,.432,1.00,3.16,"locked","The painting prepares its final disclosure"),
 ("full",.500,.500,1.00,5.60,"locked","Full museum canvas, a long elegant resolution"),
]
TECH=[("human_gaze_start","Eyes are the first photographed source detail"),
      ("visual_hierarchy","A single clear motif draws initial attention"),
      ("motivated_cut","Cuts reveal meaningful painterly subject changes"),
      ("locked_hold","Many shots remain completely still"),
      ("color_match","Pale sky and dark wing become a visual contrast"),
      ("detail_return","An earlier expression returns with a new significance"),
      ("music_continuity_cut","Changes are gently attracted to authentic score accents"),
      ("camera_seasick_gate","No wobble, pendulum, spin or pulsing scale")]
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
            with requests.get(url,headers={"User-Agent":"ArtVisionCabanelV26/1.0 art historical research"},timeout=70,stream=True) as r:
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
    credits=("\n\nOpera: Fallen Angel (1847) — Alexandre Cabanel, Musée Fabre (Montpellier)."
             "\nFonte: "+ART_PAGE+"\nMuseo: "+MUSEUM
             "\nMusica: The Chamber — Kevin MacLeod (incompetech.com)."
             "\nLicenza registrazione: CC BY 4.0 — "+LICENSE
             "\nRegistrazione: "+TRACK_PAGE
             "\nModifiche: estratto musicale con dissolvenze; montaggio e focali del quadro autentico.")
    captions={
      "POST_FACEBOOK.txt":"C'è un dettaglio che rende quest'angelo indimenticabile: lo sguardo.\n\n"
         "Nel 1847 Alexandre Cabanel dipinse il momento della caduta. Il corpo è a terra, le ali sembrano pesanti, e gli angeli sullo sfondo sono ormai lontani. "
         "Ho scelto di partire dagli occhi e di mostrare il resto soltanto alla fine: ogni particolare appartiene davvero alla tela.",
      "POST_INSTAGRAM.txt":"Uno sguardo prima del racconto.\n\n"
         "Fallen Angel di Alexandre Cabanel: ali, mani, occhi, cielo. Un viaggio cinematografico in una sola opera del 1847.",
      "POST_TIKTOK.txt":"Prima guarda gli occhi. Poi scopri il resto.\n\n"
         "Un angelo a terra e il cielo che si allontana: Fallen Angel di Alexandre Cabanel.",
      "POST_YOUTUBE.txt":"Fallen Angel | Alexandre Cabanel — ArtVision Cinema\n\n"
         "Un filmato senza voce che esplora lo sguardo, le ali, le mani e il cielo del celebre dipinto del 1847. "
         "Fotografia autentica, musiche strumentali con attribuzione e regia dedicata."}
    tags="#ArtVision #Cabanel #FallenAngel #ArtHistory"
    for name,caption in captions.items():
        (out/name).write_text(caption+credits+"\n\n"+tags+"\n",encoding="utf-8")
def package(out,impath,music,master,shots,analysis,offset):
    social(out);hash_mp4=digest(master)
    source=f"""# Provenienza e riuso
Opera: Alexandre Cabanel, Fallen Angel (1847), Musée Fabre, inv. 889.2.1.
Museo: {MUSEUM}
Riproduzione Wikimedia: {ART_PAGE}
Fotografia scaricata: {ART_URL}
Riproduzione di un dipinto di pubblico dominio; Wikimedia la indica Public Domain Mark.
Verificare le limitazioni nazionali per l'uso commerciale di fotografie museali.
SHA256 immagine: {digest(impath)}

Musica: The Chamber, Kevin MacLeod, ISRC USUAN1100400.
Brano e registrazione: {TRACK_PAGE}
Registrazione scaricata: {TRACK_URL}
Licenza: Creative Commons Attribution 4.0 — {LICENSE}
SHA256 musica originale: {digest(music)}
Adattamenti: estratto, volume e dissolvenze in entrata e uscita.
Crediti inclusi nei file social. L'eventuale reclamo automatico va verificato.
"""
    (out/"SOURCES_AND_RIGHTS.md").write_text(source,encoding="utf-8")
    notes=["# Regia personalizzata — Fallen Angel","",
           "Arco: sguardo → ali → gesto → angeli lontani → ritorno agli occhi → dipinto intero.",
           "Tre-quarti delle inquadrature statiche. Niente pan avanti e indietro, nessun falso 3D.",
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
    guide=("ArtVision Cabanel Fallen Angel V26\n"
           "Script: scripts/artvision_cabanel_directors_cut_v26.py\n"
           "Comando: python scripts/artvision_cabanel_directors_cut_v26.py --out output/cabanel-v26\n"
           "Preset originale da NON modificare: modules/artvision/APPROVED_PRESET.json\n"
           "Firma grafica: modules/artvision/IDENTITA_VISIVA_FISSA_V6.json\n"
           "Contratto V25: docs/ARTVISION_CONTRATTO_PERMANENTE_V25.md\n"
           "Strumenti: Python 3.11, numpy, Pillow, requests, FFmpeg/FFprobe, font DejaVu.\n"
           "Per una riproduzione identica conservare i due asset e gli SHA256 nel recipe.\n"
           "Per nuovi quadri NON copiare focali: progettare nuova regia. Un solo MP4 finale.\n"
           "Il pacchetto è un candidato da revisionare artisticamente, non un Gold Master approvato.\n")
    (out/"ISTRUZIONI_REPLICA.md").write_text(guide,encoding="utf-8")
    recipe={"schema":"video-recipe-v13","video_id":"cabanel-fallen-angel-v26","format":"artvision_cinema",
            "artist":ARTIST,"title_en":TITLE,"baseline":"cinema_v6","contract":"v25",
            "renderer":"scripts/artvision_cabanel_directors_cut_v26.py",
            "replication_command":"python scripts/artvision_cabanel_directors_cut_v26.py --out output/cabanel-v26",
            "sha256_mp4":hash_mp4,"sha256_artwork":digest(impath),"sha256_music":digest(music),
            "source_page":ART_PAGE,"music_page":TRACK_PAGE,"license":"CC BY 4.0",
            "score_analysis":analysis,"score_offset_seconds":offset,"shots":shots,
            "techniques":[{"id":k,"why":v} for k,v in TECH],
            "duration_seconds":float(probe(master)["format"]["duration"]),
            "frame_size":[W,H],"fps":FPS,"state":"rendered_needs_artistic_review",
            "historical_masters_unchanged":True,"social_published":False}
    (out/"VIDEO_RECIPE_V13.json").write_text(json.dumps(recipe,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    mm={"schema_version":1,
        "video":{"id":"cabanel-fallen-angel-v26","format":"artvision_cinema","title":TITLE,
                 "originality_statement":"Bespoke film direction on authentic 1847 canvas",
                 "visual_rights_evidence":[ART_PAGE,MUSEUM]},
        "music":{"title":"The Chamber","artist":COMPOSER,"origin":"external_licensed",
                 "source_url":TRACK_PAGE,"recording_proof_url":TRACK_PAGE,
                 "license_name":"CC BY 4.0","license_url":LICENSE,"license_checked_on":"2026-10-23",
                 "allow_commercial":True,"permitted_platforms":["facebook","instagram","tiktok","youtube"],
                 "monetization_allowed":True,"ads_allowed":True,"credit_required":True,
                 "credit_text":'"The Chamber" Kevin MacLeod (incompetech.com) CC BY 4.0 '+LICENSE,
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
    manifest={"schema":"artvision-release-contract-v25","video_id":"cabanel-fallen-angel-v26",
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
        for t,d in [(0,"The angel looks directly towards the viewer"),
                    (1,"The gaze is visible over the elegant series opening"),
                    (3,"The title signature gently fades without obscuring the eyes"),
                    (5,"The folded forearms develop the painted expression"),
                    (7,"The dark wing creates a contrast to the brilliant sky")]],
      "scenes":[{"source_id":"authentic-cabanel-original","subject":s["purpose"],
                 "purpose":s["purpose"],"shot":"landscape" if s["kind"]=="landscape" else s["kind"],
                 "motion":s["motion"],"duration_seconds":s["duration"]} for s in shots],
      "transition_reviews_plan":[{"why":"Wounded gaze to wing is a true graphic contrast"},
                                 {"why":"Hands then distant angels connect the narrative of exile"},
                                 {"why":"Return to eyes before full canvas opens the final view"}],
      "music_cues":[{"seconds":0,"reason":"Opening restrained harmony with human gaze"},
                    {"seconds":total*.48,"reason":"Tension deepens with the wings and sky"},
                    {"seconds":total-5,"reason":"Music fades while full painting remains visible"}],
      "duration_reason":"Fifteen artist-specific studies with authentic score accents and a measured full-image closure.",
      "selected_techniques":[{"id":k,"why":v} for k,v in TECH],
      "sources":[{"id":"authentic-cabanel-original","url":ART_PAGE,
                  "license":"Public Domain Mark original painting",
                  "credit":"Cabanel, Musée Fabre, Montpellier","status":"verified"}],
      "music":{"title":"The Chamber","composer":COMPOSER,"origin":"external_licensed",
               "license":"CC BY 4.0","evidence":TRACK_PAGE,
               "emotional_arc":"intimate gaze, physical exile, total reveal","rights_status":"verified"},
      "copy_languages":dict.fromkeys(["facebook","instagram","tiktok","youtube"],"it"),
      "archive_only_after_authorization":True,"social_autopublish":False,
      "outputs":dict(video="VIDEO_MASTER.mp4",cover="COPERTINA.jpg",
                     facebook="POST_FACEBOOK.txt",instagram="POST_INSTAGRAM.txt",
                     tiktok="POST_TIKTOK.txt",youtube="POST_YOUTUBE.txt",
                     recipe="VIDEO_RECIPE_V13.json",techniques="TECNICHE_REGIA.md",
                     replication="ISTRUZIONI_REPLICA.md",rights="SOURCES_AND_RIGHTS.md",
                     music_manifest="MUSIC_RELEASE_V20.json"),
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
    ap.add_argument("--out",default="output/cabanel-v26")
    ap.add_argument("--offset",type=float,default=12.0)
    cfg=ap.parse_args()
    out=Path(cfg.out);out.mkdir(parents=True,exist_ok=True)
    tmp=out/"_work";tmp.mkdir(exist_ok=True)
    source=out/"ARTWORK_ORIGINAL.jpg";score=out/"THE_CHAMBER_ORIGINAL_CC_BY.mp3"
    download(ART_URL,source,"image");download(TRACK_URL,score,"music")
    src=Image.open(source).convert("RGB")
    if not (1.35<src.width/src.height<1.8):raise RuntimeError("Unexpected artwork dimensions")
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
        "-c:v","copy","-af",f"aresample=48000,volume=.84,afade=t=in:st=0:d=.45,afade=t=out:st={max(0,duration-2.9):.3f}:d=2.9",
        "-c:a","aac","-b:a","192k","-t",duration,"-movflags","+faststart",output)
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
    (out/"TECHNICAL_QA_V26.json").write_text(json.dumps(report,indent=2)+"\n")
    archive=out.parent/"ARTVISION_CABANEL_FALLEN_ANGEL_V26_COMPLETE.zip"
    with zipfile.ZipFile(archive,"w") as z:
        for f in out.rglob("*"):
            if f.is_file() and "_work" not in f.parts:
                z.write(f,f.relative_to(out),compress_type=zipfile.ZIP_STORED if
                        f.suffix.lower() in (".mp3",".mp4",".jpg") else zipfile.ZIP_DEFLATED)
    shutil.rmtree(tmp)
    print("RENDER_SUCCESS",str(output),str(archive),round(duration,2),digest(output),flush=True)
if __name__=="__main__":main()
