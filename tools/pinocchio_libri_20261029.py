#!/usr/bin/env python3
"""Pinocchio 1902 Chiostri, public-domain source. Real media; fail closed on Gacrux quota.
No paid image/video generation, no substitute voice, no social publication.
"""
from __future__ import annotations
import argparse,hashlib,json,math,os,subprocess,zipfile
from pathlib import Path
from io import BytesIO
import requests,numpy as np,soundfile as sf
from PIL import Image,ImageDraw,ImageFilter,ImageFont,ImageOps

OUT=Path("output/pinocchio_20261029")
CAT=Path("reports/pinocchio_image_catalog_20261029.json")
SOURCE="https://www.gutenberg.org/cache/epub/52484/pg52484-images.html"
TITLE="PINOCCHIO"
AUTHOR="CARLO COLLODI"
ILLUSTRATOR="CARLO CHIOSTRI"
# One flashforward then an emotional chronological journey. Each index is a DIFFERENT original engraving.
BEATS=[
(78,"Nello stomaco di un mostro marino, Pinocchio intravide una luce. Non era un tesoro: era suo padre, che credeva perduto.","Il ritrovamento di Geppetto nel Pesce-cane; flashforward iniziale"),
(1,"Ma tutto era cominciato con un semplice pezzo di legno. Un falegname lo colpì, e dal legno uscì una voce.","Il legno vivo nella bottega di maestro Ciliegia"),
(4,"Geppetto lo portò a casa e iniziò a scolpire un burattino. Gli occhi si mossero prima ancora che finisse il volto.","La nascita del burattino e il naso che cresce"),
(6,"Appena ebbe le mani, Pinocchio rubò la parrucca al suo creatore. Era vivo, ma non sapeva ancora amare.","Il primo dispetto a Geppetto"),
(7,"Quando imparò a camminare, fuggì per strada. Geppetto lo rincorse, mentre tutti ridevano di quel padre disperato.","La fuga e l'inseguimento"),
(11,"Geppetto non aveva denaro. Vendette la sua vecchia casacca per comprargli un libro di scuola. Pinocchio promise di studiare.","Il sacrificio di Geppetto per l'Abbecedario"),
(14,"Ma lungo la strada sentì la musica di un teatro. Vendette il libro, dimenticando il sacrificio del padre.","La deviazione verso il teatro dei burattini"),
(18,"Il terribile Mangiafoco lo minacciò, poi si commosse. Gli donò cinque monete d'oro perché tornasse da Geppetto.","Mangiafoco e il dono delle monete"),
(20,"Sulla via del ritorno incontrò un Gatto e una Volpe. Gli promisero ricchezze facili, e Pinocchio volle crederci.","L'incontro con il Gatto e la Volpe"),
(24,"Di notte, due figure mascherate lo inseguirono nel bosco. Il sogno del denaro diventò paura.","L'agguato notturno degli assassini"),
(27,"Una Fata dai capelli turchini lo soccorse. Per la prima volta qualcuno gli chiese di guardare in faccia i propri errori.","La Fata salva il burattino"),
(30,"Pinocchio mentì, e il suo naso si allungò fino a impedirgli di muoversi. Ogni bugia lo intrappolava di più.","Il naso lunghissimo dopo le bugie"),
(31,"Non imparò subito. Tornò dalla Volpe e dal Gatto e sotterrò le monete in un campo, aspettando un albero d'oro.","L'inganno del Campo dei miracoli"),
(47,"La Fata gli offrì un'altra possibilità: studiare, lavorare, diventare un ragazzo vero. Per un po', Pinocchio cambiò.","La promessa di diventare un bravo ragazzo"),
(61,"Poi arrivò Lucignolo e lo convinse a partire per il Paese dei balocchi, dove non esistevano né scuola né doveri.","La tentazione del Paese dei balocchi"),
(67,"Dopo mesi di divertimenti, Pinocchio si svegliò con due orecchie d'asino. La libertà senza responsabilità era diventata una gabbia.","La metamorfosi in asino"),
(75,"Venduto e gettato in mare, tornò burattino. Ma tra le onde comparve l'enorme bocca del Pesce-cane.","Il mare e l'incontro con il mostro"),
(79,"Nel buio del mostro ritrovò Geppetto. Stavolta non fuggì: lo aiutò a uscire, caricandolo sulle spalle.","Il coraggio di salvare il padre"),
(81,"Sulla terraferma Pinocchio lavorò per nutrire Geppetto, rinunciando ai facili guadagni. Non cercava più una scorciatoia.","Il lavoro e la cura di Geppetto"),
(84,"Una mattina si svegliò bambino. Non era stata la magia a cambiarlo: erano state le sue scelte, finalmente diventate amore.","La trasformazione finale in bambino"),
]
NAVY=(19,31,42);GOLD=(193,158,105);IVORY=(236,226,207)
def h(b):return hashlib.sha256(b).hexdigest()
def fnt(size,bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if bold else "")+".ttf",size)
def write(name,obj):
    (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
def frame(im):
    im=ImageOps.exif_transpose(im.convert("RGB"))
    # Preserve original composition and faces: NO cover crop of historical artwork.
    bg=ImageOps.fit(im,(720,1280),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(38))
    bg=Image.blend(bg,Image.new("RGB",(720,1280),NAVY),.88)
    art=ImageOps.contain(im,(656,1120),Image.Resampling.LANCZOS)
    paper=Image.new("RGB",(art.width+20,art.height+20),IVORY)
    paper.paste(art,(10,10))
    bg.paste(paper,((720-paper.width)//2,(1280-paper.height)//2))
    return bg
def cover(im):
    c=im.copy()
    d=ImageDraw.Draw(c)
    d.rectangle((0,0,720,300),fill=NAVY)
    d.text((360,54),"TRA LE PAGINE",font=fnt(29,True),fill=GOLD,anchor="ma")
    d.text((360,122),"PINOCCHIO",font=fnt(65,True),fill=IVORY,anchor="ma")
    d.text((360,205),"CARLO COLLODI",font=fnt(27),fill=IVORY,anchor="ma")
    d.rectangle((0,1160,720,1280),fill=NAVY)
    d.text((360,1213),"ILLUSTRAZIONI · CARLO CHIOSTRI · 1902",font=fnt(18),fill=GOLD,anchor="ma")
    c.save(OUT/"COPERTINA.jpg",quality=94)
    return c
def music(seconds):
    sr=24000;n=int(seconds*sr);y=np.zeros(n,dtype=np.float32)
    # Original subdued minor-mode leitmotif: not an existing musical recording.
    pattern=[(50,0.0),(53,1.4),(57,2.8),(55,4.2),(48,5.6),(52,7.0),(50,8.4),(45,9.8)]
    for k in range(math.ceil(seconds/11.2)):
        for note,offset in pattern:
            pos=k*11.2+offset
            if pos>=seconds:continue
            length=min(int(sr*2.6),n-int(pos*sr))
            t=np.arange(length,dtype=np.float32)/sr
            hz=440*2**((note-69)/12)
            env=np.minimum(1,t/.07)*np.exp(-t/1.2)
            y[int(pos*sr):int(pos*sr)+length]+(.022*np.sin(2*np.pi*hz*t)+.006*np.sin(4*np.pi*hz*t))*env
    t=np.arange(n,dtype=np.float32)/sr
    y*=np.minimum(1,t/1.0)*np.minimum(1,np.maximum(0,seconds-t)/2)
    sf.write(OUT/"MUSICA_ORIGINALE.wav",np.clip(y,-.3,.3),sr)
def command(*args):
    subprocess.run([str(a) for a in args],check=True)
def encode(frames,seconds,outfile,voice=None):
    durations=seconds if isinstance(seconds,list) else [seconds/len(frames)]*len(frames)
    assert len(durations)==len(frames)
    playlist=OUT/"concat.txt"
    with playlist.open("w",encoding="utf8") as p:
        for im,d in zip(frames,durations):
            p.write("file '"+str(im.resolve())+"'\nduration "+str(max(.1,d))+"\n")
        p.write("file '"+str(frames[-1].resolve())+"'\n")
    total=sum(durations)
    music(total)
    args=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",playlist]
    if voice:
        args+=["-i",voice,"-i",OUT/"MUSICA_ORIGINALE.wav",
               "-filter_complex","[1:a]volume=1.0[v];[2:a]volume=0.24[m];[v][m]amix=inputs=2:duration=first:dropout_transition=0[a]",
               "-map","0:v:0","-map","[a]"]
    else:
        args+=["-i",OUT/"MUSICA_ORIGINALE.wav","-map","0:v:0","-map","1:a:0"]
    args+=["-vf","fps=24,format=yuv420p","-t",str(total),"-sn","-c:v","libx264","-preset","veryfast","-crf","24",
           "-c:a","aac","-b:a","128k","-movflags","+faststart",outfile]
    command(*args)
    command("ffmpeg","-hide_banner","-loglevel","error","-xerror","-i",outfile,"-f","null","-")
    probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_format","-show_streams","-of","json",str(outfile)],text=True))
    v=next(x for x in probe["streams"] if x["codec_type"]=="video")
    a=next(x for x in probe["streams"] if x["codec_type"]=="audio")
    assert (v["width"],v["height"],v["codec_name"],a["codec_name"])==(720,1280,"h264","aac")
    assert not any(x.get("codec_type")=="subtitle" for x in probe["streams"])
    return {"file":outfile.name,"sha256":h(outfile.read_bytes()),"bytes":outfile.stat().st_size,
            "seconds":float(probe["format"]["duration"]),"video":"H264 720x1280","audio":"AAC",
            "full_decode":True,"no_subtitle_track":True}
def package(path,files):
    with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED,compresslevel=2) as z:
        for p in files:
            if p.is_file():z.write(p,p.relative_to(OUT))
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
def prepare():
    OUT.mkdir(parents=True,exist_ok=True)
    source=json.loads(CAT.read_text(encoding="utf8"))
    assert source["count"]>=80
    items=source["items"]
    assert len(BEATS)==20 and len(set(x[0] for x in BEATS))==20
    session=requests.Session()
    session.headers["User-Agent"]="TraLePagineStudio/1.0 (public domain illustration project)"
    frames=[];provenance=[];cards=[]
    (OUT/"SCENE").mkdir(exist_ok=True)
    for k,(index,words,meaning) in enumerate(BEATS,1):
        row=items[index]
        url=row["url"]
        response=session.get(url,timeout=55);response.raise_for_status()
        if len(response.content)>12000000:raise RuntimeError("Oversize image")
        with Image.open(BytesIO(response.content)) as raw:
            raw.load()
            if min(raw.size)<180:raise RuntimeError("Historical image too small "+url)
            dim=raw.size
            original=raw.convert("RGB")
        target=OUT/"SCENE"/("SCENA_%02d.jpg"%k)
        frame(original).save(target,quality=92,optimize=True)
        frames.append(target)
        prov={"scene":k,"plate_index":index,"chapter":row["chapter"],"source_url":url,
              "source_page":SOURCE,"original_dimensions":dim,"original_sha256":h(response.content),
              "frame_sha256":h(target.read_bytes()),
              "rights":"Collodi died 1890, Chiostri died 1939; original 1902 historical engraving; public domain Italy life+70",
              "visual_intent":meaning,"narration":words,"human_visual_review":"pending"}
        provenance.append(prov)
        cards.append({"scene":k,"source_reference":url,"visual_intent":meaning,
                      "narration_anchor":words,"visual_review":"pending actual image review",
                      "rights_review":"historical source and author terms documented; individual asset review pending"})
        print("REAL_IMAGE",k,index,dim,url,flush=True)
    opening=cover(Image.open(frames[0]).convert("RGB"))
    opening_path=OUT/"OPENING.jpg";opening.save(opening_path,quality=93)
    preview_frames=[opening_path]+frames[1:]
    sheet=Image.new("RGB",(720,5*225),NAVY);draw=ImageDraw.Draw(sheet)
    for i,p in enumerate(frames):
        im=Image.open(p).resize((144,205),Image.Resampling.LANCZOS)
        x=(i%5)*144;y=(i//5)*225
        sheet.paste(im,(x,y));draw.text((x+8,y+206),str(i+1),font=fnt(13,True),fill=IVORY)
    sheet.save(OUT/"STORYBOARD.jpg",quality=91)
    script="\n\n".join(b[1] for b in BEATS)
    (OUT/"COPIONE.txt").write_text(script+"\n",encoding="utf8")
    write("SCHEDE_VISUALI_V35.json",{"schema":"schede-visuali-v35-draft","episode":"pinocchio_20261029",
        "format":"9:16 720x1280","cards":cards,"artistic_review":"pending"})
    write("PROJECT_V13.json",{"schema":"project-v13-draft","format":"libri","title":"Pinocchio","author":"Carlo Collodi",
        "status":"assets_acquired_voice_free_quota_unconfirmed",
        "editorial_contract":{"voice":"Google Gemini Gacrux ONLY with confirmed free quota",
                              "paid_video_api_calls_allowed":False,"social_publish":False},
        "bibliography":{"publication_year":1883,"edition_reference":SOURCE,"illustrator":"Carlo Chiostri","illustration_year":1902},
        "editorial_plan":{"hook":BEATS[0][1],"ending":BEATS[-1][1],
          "scene_count":20,"mix_reason":"Twenty genuinely different engravings; flashforward, regret, temptation, reunion and transformation; no simulated physical animation.",
          "sources":[{"reference":SOURCE,"verification":"edition inspected"}],
          "media_sourcing":{"decisions":provenance}},
        "release":"rendered_needs_review_or_preview_only"})
    write("PROVENIENZA_IMMAGINI.json",provenance)
    (OUT/"FONTI_E_DIRITTI.md").write_text(
        "# Fonti e diritti\n\nTesto originale: Carlo Collodi, *Le avventure di Pinocchio* (1883), morto nel 1890.\n"
        "Illustrazioni: Carlo Chiostri, edizione Bemporad 1902, morto nel 1939.\n"
        "Fonte scansioni: "+SOURCE+"\n"
        "Profilo illustratore: https://www.archiginnasio.it/objects/profile-carlo-chiostri\n"
        "Italia: scadenza del termine ordinario vita+70 per testo e incisioni; verificare separatamente ogni riproduzione e i termini del sito sorgente prima della pubblicazione.\n"
        "Ogni asset ha URL e SHA256 in PROVENIENZA_IMMAGINI.json. Nessuna immagine AI e nessun video AI.\n",
        encoding="utf8")
    (OUT/"MUSICA_CREDITI.txt").write_text("Tema originale 'Il legno e il mare': sintesi musicale autonoma Tra le Pagine, nessun sample o registrazione di terzi.\n",encoding="utf8")
    posts={
        "FACEBOOK":"Un padre che vende la propria giacca per comprare un libro. Un figlio che lo vende per inseguire un sogno. In *Pinocchio* il cuore della storia non è il naso che si allunga: è il momento in cui il burattino smette di fuggire e torna a prendersi cura di Geppetto. Rivisitiamo il capolavoro di Carlo Collodi attraverso venti incisioni storiche di Carlo Chiostri, dall'edizione Bemporad del 1902. Un racconto di errori, seconde possibilità e amore che cambia le persone. Fonte: Project Gutenberg #52484. #Pinocchio #CarloCollodi #LetteraturaItaliana #TraLePagine",
        "INSTAGRAM":"«Non era stata la magia a cambiarlo.» 🌙 Pinocchio ci porta dalla bottega di Geppetto alle profondità del mare, attraverso venti tavole storiche di Carlo Chiostri. Una storia su quanto costa crescere e su chi continua ad aspettarci. Testo: Carlo Collodi (1883). Illustrazioni: Carlo Chiostri, edizione 1902, fonte Project Gutenberg #52484. #Pinocchio #LibriDaRiscoprire #StorieCheRestano #TraLePagine",
        "TIKTOK":"E se il momento più importante di Pinocchio NON fosse il naso che cresce? Il vero cambiamento arriva quando ritrova Geppetto nel ventre del Pesce-cane. Racconto originale di Carlo Collodi, reinterpretato con 20 incisioni autentiche di Carlo Chiostri (1902). Fonte: Project Gutenberg #52484. #Pinocchio #Storytelling #Libri #TraLePagine",
        "YOUTUBE":"PINOCCHIO | Il momento in cui un burattino diventa figlio — Carlo Collodi\n\nUna lettura condensata e originale di *Le avventure di Pinocchio* (1883): il sacrificio di Geppetto, la fuga, il Gatto e la Volpe, la Fata, il Paese dei balocchi, il Pesce-cane e la scelta finale di prendersi cura del padre. Regia costruita su 20 illustrazioni autentiche e distinte dell'edizione Bemporad 1902, realizzate da Carlo Chiostri.\n\nFonti: Project Gutenberg eBook #52484, https://www.gutenberg.org/ebooks/52484. Carlo Collodi (1826–1890); Carlo Chiostri (1863–1939). Musica originale Tra le Pagine.\n\n#Pinocchio #CarloCollodi #Audiolibro #Racconti #TraLePagine"
    }
    for k,v in posts.items():(OUT/("POST_"+k+".txt")).write_text(v+"\n",encoding="utf8")
    (OUT/"STORYBOARD.txt").write_text("\n".join(str(i)+". "+b[2]+" | "+b[1] for i,b in enumerate(BEATS,1)),encoding="utf8")
    duration=40.0
    result=encode(preview_frames,duration,OUT/"PINOCCHIO_ANTEPRIMA_VISIVA_40S_NON_NARRATA.mp4")
    state={"episode":"pinocchio_20261029","status":"visual_preview_only_not_final","preview":result,
           "distinct_original_images":len(frames),"source_catalog_count":source["count"],
           "gacrux_voice_generated":False,"free_quota_attested":False,"narrated_master_exists":False,
           "artistic_review":"pending","V13":"draft","V35":"pending",
           "archive_imported":False,"social_published":False,"paid_video_api_calls":0}
    write("QA_STATO_REALE.json",state)
    package(OUT/"PINOCCHIO_ANTEPRIMA_SOLO_VIDEO.zip",[OUT/result["file"]])
    package(OUT/"PINOCCHIO_DOSSIER_VISIVO_NON_FINALE.zip",
            [p for p in OUT.rglob("*") if p.is_file() and not p.name.endswith(".zip")])
    print("PREVIEW_COMPLETE",json.dumps(state,ensure_ascii=False),flush=True)
def render():
    state=json.loads((OUT/"QA_STATO_REALE.json").read_text(encoding="utf8"))
    if os.getenv("GEMINI_TTS_FREE_QUOTA_CONFIRMED")!="true" or not os.getenv("GEMINI_API_KEY"):
        print("NO_GACRUX_FREE_QUOTA_ATTESTATION; no synthesis and no replacement")
        return
    import sys
    sys.path.insert(0,"src")
    from gemini_voice import synthesize,sentences
    text=(OUT/"COPIONE.txt").read_text(encoding="utf8")
    samples,timed=synthesize(text,OUT/"GACRUX")
    seconds=len(samples)/24000
    if not 110<=seconds<=220:raise RuntimeError("Narration duration needs editorial review")
    # ASR-derived sentence endpoints, not fabricated equal-time narration.
    paragraphs=[p.strip() for p in text.split("\n\n") if p.strip()]
    assert len(paragraphs)==20
    ends=[];i=0
    for p in paragraphs:
        i+=len(sentences(p))
        if i>len(timed):raise RuntimeError("Speech timing mismatch")
        ends.append(float(timed[i-1][2]))
    if i!=len(timed):raise RuntimeError("Unaccounted speech sentences")
    durations=[max(.1,b-a) for a,b in zip([0]+ends[:-1],ends)]
    if min(durations)<2.0:raise RuntimeError("Too short a scene for legible image")
    frames=[OUT/"OPENING.jpg"]+[OUT/"SCENE"/("SCENA_%02d.jpg"%i) for i in range(2,21)]
    result=encode(frames,durations,OUT/"PINOCCHIO_MASTER_GACRUX_DA_REVISIONARE.mp4",voice=OUT/"GACRUX"/"VOCE.wav")
    package(OUT/"PINOCCHIO_MASTER_SOLO_VIDEO_V36.zip",[OUT/result["file"]])
    state.update({"status":"rendered_needs_review","gacrux_voice_generated":True,
                  "free_quota_attested":True,"narrated_master_exists":True,"narrated_master":result,
                  "audio_alignment":"ASR timing; artistic sync review pending","artistic_review":"pending"})
    write("QA_STATO_REALE.json",state)
    package(OUT/"PINOCCHIO_PACCHETTO_COMPLETO_DA_REVISIONARE.zip",
            [p for p in OUT.rglob("*") if p.is_file() and not p.name.endswith(".zip")])
    print("GACRUX_MASTER_RENDERED_NEEDS_REVIEW",json.dumps(state,ensure_ascii=False),flush=True)
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--mode",choices=["prepare","render"],required=True)
    a=ap.parse_args()
    if a.mode=="prepare":prepare()
    else:render()
