#!/usr/bin/env python3
"""Creative Director V21: packaging social, hook, durata e musica per TUTTE le serie.
Solo piano + analisi del master: NON modifica MP4, preset, voci o copertine approvate.
Dati mancanti rimangono mancanti; non produce metriche o contenuti fattuali inventati.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
POLICY=ROOT/"config"/"creative_director_v21.json"
FORMATS={
 "libri","artvision_cinema","artvision_enigma","artvision_critico",
 "controluce","visual_music","hyperlumen","other"
}
PLATFORMS={"facebook","instagram","tiktok","youtube"}
NATIVE={"meta_native_library","meta_sound_collection"}
CREDITS_REQUIRED={"CC BY 4.0","CC BY 3.0"}
ARCHETYPES={
 "enigmatic_detail":"un dettaglio indecifrabile diventa una rivelazione",
 "human_gaze":"uno sguardo umano porta alla storia",
 "dramatic_event":"un gesto decisivo apre una domanda reale",
 "sculptural_form":"materia, ombra e struttura tridimensionale",
 "beautiful_motion":"una forma visiva memorabile diventa movimento",
 "quiet_tension":"silenzio e attesa prima di un cambiamento",
 "musical_pulse":"un evento sonoro reale guida la prima trasformazione",
 "unexpected_contrast":"due elementi coerenti mostrano un contrasto sorprendente",
}
ASSETS={"painting","portrait","sculpture","architecture","nature","manuscript",
        "human_figure","dramatic_art","abstract","photography","other"}
SERIES_RULES={
 "artvision_cinema":"Firma e copertina Cinema V6 approvata: NON sovrascrivere; niente testo aggiuntivo",
 "artvision_critico":"Copertina Critico V2: titolo opera + artista; niente titoli italiani impressi nel video",
 "libri":"Identita Tra le Pagine; voce Google e immagini aderenti alle scene; nessun sottotitolo",
 "artvision_enigma":"Rivelazione veritiera, copertina leggibile e primo dettaglio subito riconoscibile",
 "visual_music":"Primo effetto ancorato alla musica misurata; niente forme casuali",
 "hyperlumen":"Geometrie leggibili e primo evento musicale reale",
 "controluce":"Apertura verificata, senza immagini di ricostruzione presentate come reali",
 "other":"Continuita dello stile della serie, regia specifica del soggetto",
}
PREFERENCES={
 "artvision_enigma":["enigmatic_detail","unexpected_contrast","quiet_tension"],
 "artvision_critico":["enigmatic_detail","human_gaze","unexpected_contrast","sculptural_form"],
 "artvision_cinema":["beautiful_motion","human_gaze","quiet_tension","sculptural_form"],
 "libri":["dramatic_event","human_gaze","quiet_tension"],
 "controluce":["dramatic_event","quiet_tension","human_gaze"],
 "visual_music":["musical_pulse","beautiful_motion","unexpected_contrast"],
 "hyperlumen":["musical_pulse","beautiful_motion","quiet_tension"],
 "other":["enigmatic_detail","human_gaze","dramatic_event","sculptural_form"]
}
VISUAL_COMPAT={
 "enigmatic_detail":{"painting","sculpture","architecture","dramatic_art","abstract","manuscript"},
 "human_gaze":{"portrait","human_figure","painting","photography"},
 "dramatic_event":{"dramatic_art","human_figure","painting","photography","manuscript"},
 "sculptural_form":{"sculpture","architecture","abstract","painting"},
 "beautiful_motion":{"nature","abstract","painting","sculpture","architecture"},
 "quiet_tension":{"portrait","dramatic_art","architecture","nature","human_figure"},
 "musical_pulse":{"abstract","sculpture","painting","nature"},
 "unexpected_contrast":{"painting","sculpture","portrait","dramatic_art","nature","abstract"},
}
HASHTAGS={"artvision_cinema":["ArtVision","Arte"],"artvision_enigma":["ArtVision","Arte"],
"artvision_critico":["Arte","StoriaDellArte"],"libri":["Libri","Letteratura"],
"controluce":["Storia","Documentario"],"hyperlumen":["VisualMusic","ArteDigitale"],
"visual_music":["Musica","VisualMusic"],"other":["Creativita"]}

def clean(x):return " ".join(str(x or "").split())
def safe_tag(s):
    s=re.sub(r"[^A-Za-zÀ-ÿ0-9]","",str(s or ""))
    return s[:32]
def as_positive_number(x):
    if isinstance(x,bool):return None
    try:
        value=float(x)
        return value if math.isfinite(value) and value>0 else None
    except (TypeError,ValueError):return None
def validate_origin(origin):
    if origin not in ("external_licensed","meta_sound_collection","meta_native_library","original","not_chosen"):
        raise ValueError("Origine musica sconosciuta")
def fmt_from(brief):
    if brief.get("schema")=="artvision-enigma-v1":return "artvision_enigma"
    f=brief.get("format") or "other"
    return f if f in FORMATS else "other"
def read_policy(path=POLICY):
    policy=json.loads(Path(path).read_text(encoding="utf8"))
    if policy.get("schema")!="creative-director-v21":raise ValueError("Policy V21 invalida")
    return policy

def actual_seconds(video):
    if not video:return None
    p=Path(video)
    if not p.is_file():raise FileNotFoundError(str(p))
    data=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries",
        "format=duration","-of","json",str(p)],text=True,timeout=20))
    seconds=as_positive_number(data.get("format",{}).get("duration"))
    if not seconds:raise ValueError("Durata master non verificabile")
    return round(seconds,3)

def duration_plan(brief,actual=None,history=None):
    """NON impone 30/60/180s: misura oppure suggerisce una finestra revisibile."""
    kind=fmt_from(brief)
    if actual:
        return {"seconds":actual,"basis":"ffprobe_master_reale","fixed_template":False,
                "advice":"Non allungare o accorciare automaticamente: esaminare retention per questa durata."}
    if brief.get("schema")=="artvision-enigma-v1":
        shots=brief.get("shots") or []
        val=sum(as_positive_number(s.get("seconds")) or 0 for s in shots if isinstance(s,dict))
        if val>0:return {"seconds":round(val,2),"basis":"shot_timing_curato_da_validare","fixed_template":False}
    spoken=as_positive_number(brief.get("voice_duration_seconds") or brief.get("narration_seconds"))
    if spoken:return {"seconds":round(spoken,2),"basis":"timing_voce_dichiarato_da_verificare","fixed_template":False}
    scenes=brief.get("scenes") or []
    secs=sum(as_positive_number(s.get("seconds") or s.get("duration")) or 0 for s in scenes if isinstance(s,dict))
    if secs>0 and all(as_positive_number(s.get("seconds") or s.get("duration")) for s in scenes if isinstance(s,dict)):
        return {"seconds":round(secs,2),"basis":"somma_scene_dichiarate","fixed_template":False}
    # Finestra creativa, NON previsione "l'algoritmo preferisce X secondi".
    complexity=len(scenes) if isinstance(scenes,list) else 0
    if kind in ("artvision_enigma",):
        band=[25,80] if complexity>=9 else [15,65]
    elif kind in ("artvision_cinema","visual_music","hyperlumen"):
        band=[45,220] if complexity>=9 else [18,150]
    elif kind in ("libri","artvision_critico","controluce"):
        band=[120,420] if complexity>=8 else [40,240]
    else:band=[20,220]
    comparable=[]
    for h in history or []:
        if not isinstance(h,dict) or h.get("format")!=kind or not h.get("verified"):continue
        dur=as_positive_number(h.get("duration_seconds"))
        hold=as_positive_number(h.get("average_watch_seconds"))
        if dur and hold and hold<=dur*2:comparable.append((dur,hold/dur))
    advice="Durata da scegliere in regia, in base a contenuto, numero di rivelazioni e ritmo."
    if len(comparable)>=5:
        ordered=sorted(comparable,key=lambda t:t[1],reverse=True)
        strong=ordered[:max(2,len(ordered)//3)]
        values=sorted(d for d,_ in strong)
        advice+=f" Dati storici verificati: i filmati con maggiore watch ratio durano {values[0]:.0f}–{values[-1]:.0f}s; correlazione NON causale."
    return {"seconds":None,"creative_window_seconds":band,"basis":"ipotesi_editoriale_da_misurare",
            "fixed_template":False,"advice":advice}

def candidates_from(brief):
    explicit=brief.get("visual_candidates")
    if isinstance(explicit,list) and explicit:return explicit
    candidates=[]
    for asset in brief.get("assets") or []:
        if isinstance(asset,dict) and asset.get("role")=="visual":
            candidates.append({"id":asset.get("id"),"type":asset.get("visual_type","other"),
                "relevance":asset.get("relevance"),"impact":asset.get("impact"),
                "source":asset.get("source"),"rights":asset.get("rights"),
                "visual_description":asset.get("description","")})
    if brief.get("schema")=="artvision-enigma-v1":
        src=brief.get("source") or {}
        return [{"id":clean(brief.get("artwork")),"type":"painting","relevance":5,"impact":4,
                 "source":src.get("file_page"),"rights":src.get("license"),
                 "visual_description":clean(brief.get("hook"))}]
    return candidates

def choose_visual(brief,archetypes,history):
    candidates=candidates_from(brief)
    valid=[];warnings=[]
    for c in candidates:
        if not isinstance(c,dict):continue
        typ=c.get("type") or "other"
        if typ not in ASSETS:
            warnings.append("Tipo immagine sconosciuto: verificare "+clean(c.get("id")))
            continue
        relevance=as_positive_number(c.get("relevance"))
        if not relevance or relevance<3:
            warnings.append("Materiale non certificato come pertinente: "+clean(c.get("id")))
            continue
        if not c.get("source") or not c.get("rights"):
            warnings.append("Origine/diritti immagine incompleti: "+clean(c.get("id")))
            continue
        valid.append(c)
    if not valid:
        warnings.append("Copertina: nessun asset visivo pertinente e con provenienza documentata")
        return None,None,warnings
    past=Counter(x.get("archetype") for x in (history or [])[-8:] if isinstance(x,dict))
    choices=[]
    for i,a in enumerate(archetypes):
        for v in valid:
            if v["type"] not in VISUAL_COMPAT[a]:continue
            score=10*min(5,float(v.get("relevance") or 0))+2*min(5,float(v.get("impact") or 0))
            score+=max(0,5-i)-min(past[a]*3,9)
            choices.append((score,a,v))
    if not choices:
        warnings.append("Nessuna combinazione coerente tra apertura e immagini disponibili")
        return None,None,warnings
    choices.sort(key=lambda r:(-r[0],r[1],str(r[2].get("id"))))
    _,arch,asset=choices[0]
    if not asset.get("visual_description"):
        warnings.append("Manca descrizione semantica della copertina per valutazione umana")
    return arch,asset,warnings

def mood_music(brief,targets):
    m=brief.get("music") or {}
    if isinstance(m,str):m={}
    origin=m.get("origin") or ("external_licensed" if m.get("license") or m.get("license_url") else "not_chosen")
    validate_origin(origin)
    title=clean(m.get("title"))
    artist=clean(m.get("artist") or m.get("composer"))
    track_id=clean(m.get("track_id") or m.get("id"))
    warnings=[]
    if origin=="not_chosen":
        warnings.append("Musica non selezionata: ascoltare almeno tre candidate compatibili quando disponibili")
    if origin in NATIVE:
        if not track_id:
            warnings.append("Manca identificativo esatto del brano nella libreria Meta")
        if any(p not in ("facebook","instagram") for p in targets):
            warnings.append("Traccia Meta non autorizzata automaticamente fuori Facebook/Instagram")
        if origin=="meta_native_library":
            warnings.append("Aggiungere il brano nell'app Meta al momento della pubblicazione; non estrarlo e non incorporarlo nel master universale")
            if m.get("embedded") is True: warnings.append("BLOCCO: audio da libreria nativa incorporato nel master")
            if m.get("commercial_allowed") is not True: warnings.append("Uso commerciale o monetizzazione di questo brano non dimostrati")
        else:
            warnings.append("Sound Collection: verificare termini, brano e territorio; NON estendere la licenza ad altri social")
    elif origin=="external_licensed":
        if not all(m.get(k) for k in ("title","source_url","license_url")):
            warnings.append("Titolo, fonte o licenza registrazione esterna incompleti")
        if m.get("commercial_allowed") is not True:
            warnings.append("Uso commerciale della registrazione da verificare")
    elif origin=="original":
        if not m.get("recording_proof"):
            warnings.append("Prova titolarita della registrazione e degli eventuali campioni mancante")
    if m.get("credit_required") is True and not m.get("credit_text"):
        warnings.append("Crediti obbligatori ancora da redigere")
    return {"origin":origin,"track_id":track_id or None,"title":title or None,"artist":artist or None,
        "candidate_strategy":"tre brani motivati per mood, sincronizzazione reale, mix voce e diritti; nessuna scelta casuale",
        "repetition_rule":"Lo stesso brano puo tornare piu volte quando l'effetto e giustificato: alternare emozione/ritmo e controllare stanchezza sonora.",
        "master_policy":("video pulito con voce/dialoghi originali; aggiungere musica SOLO nell'app Meta"
            if origin=="meta_native_library" else
            "creare un master specifico Meta; per altri social usare una registrazione con licenza separata"
            if origin=="meta_sound_collection" else
            "traccia originale/licenziata verificata, master riutilizzabile soltanto nei territori e social autorizzati"),
        "platform_instructions":{
            p:("Aggiungere la traccia scelta nell'editor Facebook/Instagram; controllare prima autorizzazioni per lo specifico uso"
               if p in ("facebook","instagram") and origin in NATIVE else
               "Usare audio proprio o registrazione indipendentemente autorizzata per questa piattaforma")
            for p in targets},"warnings":warnings}

def get_context(brief):
    if brief.get("schema")=="artvision-enigma-v1":
        return {"title":clean(brief.get("artwork")),"artist":clean(brief.get("artist")),
                "topic":clean(brief.get("artwork")),"opening":clean(brief.get("hook")),
                "resolution":clean(brief.get("resolution")),"original":clean(brief.get("original_value"))}
    business=brief.get("business") or {}
    return {"title":clean(brief.get("title") or brief.get("topic") or brief.get("artist")),
        "artist":clean(brief.get("artist")),
        "topic":clean(brief.get("topic") or brief.get("artist")),
        "opening":clean(brief.get("opening") or brief.get("hook") or business.get("viewer_promise")),
        "resolution":clean(brief.get("resolution") or brief.get("original_angle")),
        "original":clean(business.get("original_contribution") or brief.get("original_value"))}
def caption_set(brief,context,music,targets):
    """Non inventa fatti storici: usa SOLO materiali che il brief contiene."""
    topic=context["title"] or context["topic"] or "Il nuovo episodio"
    opening=context["opening"] or topic
    resolution=context["resolution"]
    original=context["original"]
    intro=opening.rstrip(" .!?" )+("?" if opening.endswith("?") else ".")
    facts=resolution.rstrip(".")+"." if resolution else ""
    value=original.rstrip(".")+"." if original and original.casefold()!=facts.casefold() else ""
    body=" ".join(x for x in [intro,facts,value] if x).strip()
    tags=[safe_tag(k) for k in HASHTAGS[fmt_from(brief)]]
    artist=safe_tag(context["artist"])
    if artist and artist.lower() not in [t.lower() for t in tags]:tags.append(artist)
    tags=[t for t in tags if t][:4]
    credits=clean(brief.get("credits"))
    if music["origin"]=="external_licensed" and music["title"]:
        m=brief.get("music") or {}
        if m.get("credit_text"):credits=(credits+"\n"+clean(m["credit_text"])).strip()
        elif m.get("license_url"):credits=(credits+"\nMusica: "+music["title"]+" — "+(music["artist"] or "autore da verificare")+
            "\nFonte: "+clean(m.get("source_url"))+"\nLicenza: "+clean(m.get("license_url"))+
            "\nModifiche: estratto, mix e dissolvenze se applicati.").strip()
    outputs={}
    hashstr=" ".join("#"+x for x in tags)
    for p in targets:
        if p=="facebook":
            text=body+("\n\nChe dettaglio hai notato per primo?" if brief.get("question_supported") is True else "")
            text+="\n\n"+hashstr
        elif p=="instagram":
            text=(intro+" "+facts).strip()+"\n\n"+hashstr
        elif p=="tiktok":
            text=opening[:180]+("\n"+hashstr if hashstr else "")
        else:
            text=body+"\n\n"+hashstr
        if credits:text+="\n\n"+credits
        outputs[p]={"title":topic[:85],"description":text.strip(),"hashtags":tags,
            "publication_steps":{
              "facebook":"Reel: copertina riconoscibile e primo fotogramma forte; controlla autoplay, licenze, eventuale audio Meta in-app prima di pubblicare",
              "instagram":"Reel 9:16: verifica griglia profilo e copertina; controlla audio e margini UI; non aggiungere hashtag casuali",
              "tiktok":"Rivedi i primi 1/3/5/7 secondi con audio e senza; scegli copertina in editor, tag pertinenti, audio consentito",
              "youtube":"Per Shorts scegli un fotogramma direttamente dall'app quando previsto; per video lunghi carica thumbnail dedicata; titolo fedele al contenuto"}[p]}
    return outputs

def first_seconds_plan(brief,context,arch,asset,seconds):
    visual=clean((asset or {}).get("visual_description") or context["opening"])
    if not visual:visual="Inquadrare un soggetto verificato e davvero coerente con la promessa"
    item=[]
    segments=[(0,1,"Primo fotogramma: impatto immediato e leggibilita su schermo piccolo"),
              (1,3,"Introdurre la promessa con immagine/voce o evento sonoro autentico"),
              (3,5,"Aggiungere una informazione o cambio visivo motivato"),
              (5,7,"Rafforzare attesa e direzione; NON ripetere la stessa immagine")]
    for start,end,role in segments:
        if seconds is not None and start>=seconds:break
        item.append({"from_seconds":start,"to_seconds":min(end,seconds) if seconds else end,
            "purpose":role,"archetype":arch,"visual_anchor":visual,
            "verified_visual":bool(asset),"proposed_only":True})
    return item

def probe_preview(video,folder):
    """5 fotogrammi reali (0, 1, 3, 5, 7s) + miniatura candidata; zero redesign."""
    from PIL import Image,ImageOps,ImageDraw,ImageStat
    duration=actual_seconds(video)
    stamps=[x for x in (.08,1.,3.,5.,7.) if x < max(.1,duration-.12)]
    for extra in (duration*.24,duration*.55):
        if extra>.08 and all(abs(extra-x)>1 for x in stamps):stamps.append(extra)
    stamps.sort()
    found=[]
    for i,t in enumerate(stamps):
        p=folder/("FIRST_FRAME_%02d.jpg"%i)
        cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-ss",str(t),"-i",str(video),
            "-frames:v","1","-vf","scale=320:-2",str(p)]
        subprocess.run(cmd,check=True,timeout=35)
        with Image.open(p) as img:
            gray=ImageOps.grayscale(img).resize((64,64))
            stat=ImageStat.Stat(gray)
            mid=stat.mean[0]; contrast=stat.stddev[0]
            # Heuristica TECNICA, non giudizio estetico. Evita quasi nero/sovraesposto.
            score=contrast - abs(mid-125)*.19 + (1.5 if t<=7 else 0)
            im=img.convert("RGB").copy()
        found.append({"time":round(t,2),"file":p.name,"score":round(score,2),"thumb":im})
    if not found:raise ValueError("Video troppo corto per estrarre il primo fotogramma")
    valid=sorted(found,key=lambda x:(-x["score"],x["time"]))
    pick=valid[0]
    # estrai la vera immagine dal master alla risoluzione originale, NON cambia il video
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-ss",str(pick["time"]),
        "-i",str(video),"-frames:v","1","-q:v","2",str(folder/"COPERTINA_CANDIDATA_V21.jpg")],check=True,timeout=50)
    tilew,tileh=200,388
    sheet=Image.new("RGB",(tilew*len(found),tileh),(14,24,35))
    d=ImageDraw.Draw(sheet)
    for i,row in enumerate(found):
        photo=row["thumb"]
        photo.thumbnail((tilew-12,tileh-38))
        sheet.paste(photo,(tilew*i+(tilew-photo.width)//2,5))
        d.text((tilew*i+10,tileh-28),f'{row["time"]}s',fill="white")
    sheet.save(folder/"APERTURA_0_7_V21.jpg",quality=88)
    return {"sampled_seconds":[x["time"] for x in found],
        "selected_candidate_second":pick["time"],"selected_by":"contrasto tecnico: DA VALIDARE artisticamente",
        "visual_semantics_automated":False,"cover_overwrites_existing":False,
        "contact_sheet":"APERTURA_0_7_V21.jpg","candidate":"COPERTINA_CANDIDATA_V21.jpg"}

def write_package(brief,output,*,video=None,history=None,targets=None,policy_path=POLICY):
    policy=read_policy(policy_path)
    if not isinstance(brief,dict):raise ValueError("Richiesta creativa JSON obbligatoria")
    kind=fmt_from(brief)
    targets=targets or policy["platforms"]
    if not isinstance(targets,list) or not targets or len(targets)!=len(set(targets)) or any(p not in PLATFORMS for p in targets):
        raise ValueError("Piattaforme non valide")
    history=history or []
    context=get_context(brief)
    archetypes=PREFERENCES[kind]
    arch,asset,vis_warnings=choose_visual(brief,archetypes,history)
    duration=duration_plan(brief,actual_seconds(video) if video else None,history=history)
    music=mood_music(brief,targets)
    openings=first_seconds_plan(brief,context,arch,asset,duration.get("seconds"))
    social=caption_set(brief,context,music,targets)
    warnings=list(vis_warnings)+list(music["warnings"])
    if not context["original"]:warnings.append("Contributo originale non documentato")
    if not context["opening"]:warnings.append("Primo hook non ancora scritto")
    if not context["resolution"]:warnings.append("Rivelazione finale o informazione promessa da verificare")
    if not brief.get("source_verified") and not brief.get("fact_sources_checked"):
        warnings.append("Fatti, opere e diritti delle immagini ancora da verificare editorialmente")
    if video is None:warnings.append("Manca master effettivo: primo fotogramma e copertina non ancora verificabili")
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    preview=None
    if video:preview=probe_preview(video,output)
    record={"schema":"creative-director-v21","project_id":clean(brief.get("project_id") or brief.get("id")),
        "format":kind,"topic":context["topic"],"series_identity":SERIES_RULES[kind],
        "cover":{"approved_original_must_remain":True,"recommended_archetype":arch,
                 "source_asset_id":str(asset.get("id")) if asset else None,
                 "selection_rationale":"priorita ad attinenza e diritti; storico formati evita ripetizione, non aggiunge immagini a caso",
                 "small_screen_review_required":True,"notes":"Una scultura, figura, volto, paesaggio o opera solo se PERTINENTE, originale e con diritti verificati"},
        "first_7_seconds":openings,"duration":duration,"music":music,
        "social":social,"technical_preview":preview,
        "review_status":"review_required","ready_to_publish":False,
        "published":False,"warnings":list(dict.fromkeys(warnings)),
        "editorial_checks":["Copertina leggibile in griglia telefono",
              "Primo fotogramma interessante SENZA obbligo di titolo/overlay",
              "Hook 0–3s, sviluppo 3–5s, promessa onesta 5–7s",
              "Originalita specifica per il soggetto; niente varieta casuale e nessuna immagine fuorviante",
              "Durata giustificata dalla storia e confrontata con retention reale se esiste",
              "Mix musicale coerente, licenza commerciale verificata per ogni destinazione",
              "Credit fotografici/musicali completi, descrizioni diverse per social",
              "Master integrale visto/ascoltato: regia e audio effettivi, no sottotitoli",
              "Nessuna pubblicazione senza autorizzazione umana"],
        "video_sha256":hashlib.sha256(Path(video).read_bytes()).hexdigest() if video else None,
        "automatic_scoring_not_aesthetic_certification":True}
    (output/"CREATIVE_PACKAGE_V21.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    for platform,data in social.items():
        text=data["title"]+"\n\n"+data["description"]+"\n\nISTRUZIONI\n"+data["publication_steps"]+"\n"+
            music["platform_instructions"][platform]+"\n"
        (output/("POST_"+platform.upper()+"_V21.txt")).write_text(text,encoding="utf8")
    parts=["# Creative Director V21 — "+(context["title"] or kind),"",
        "### Prima impressione",f"Archetipo proposto: {arch or 'da definire'}",
        f"Identita di serie: {SERIES_RULES[kind]}","",
        "### Durata",json.dumps(duration,ensure_ascii=False),"",
        "### Apertura 0–7 secondi"]
    for s in openings:parts.append(f"- {s['from_seconds']}–{s['to_seconds']} s: {s['purpose']}")
    parts+=["","### Musica",music["master_policy"],"","### Revisione necessaria"]
    parts+=["- "+x for x in record["editorial_checks"]]
    parts+=["","### Segnalazioni"]+["- "+w for w in record["warnings"]]
    parts+=["","I numeri di retention e viralita NON sono predetti. La copertina candidata non sostituisce quella approvata."]
    (output/"ISTRUZIONI_PUBBLICAZIONE_V21.md").write_text("\n".join(parts)+"\n",encoding="utf8")
    return record

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--brief",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--video",type=Path)
    p.add_argument("--history",type=Path)
    p.add_argument("--targets",nargs="+",choices=sorted(PLATFORMS))
    a=p.parse_args()
    brief=json.loads(a.brief.read_text(encoding="utf8"))
    history=json.loads(a.history.read_text(encoding="utf8")) if a.history else []
    if isinstance(history,dict):history=history.get("published",[])
    record=write_package(brief,a.out,video=a.video,history=history,targets=a.targets)
    print(json.dumps({"status":record["review_status"],"format":record["format"],
        "duration":record["duration"],"warning_count":len(record["warnings"]),
        "preview":bool(record["technical_preview"]),"published":False},ensure_ascii=False))
if __name__=="__main__":main()
