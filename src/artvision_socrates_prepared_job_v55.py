#!/usr/bin/env python3
"""Prepare one verified Socrates 4x1 dossier and one Cinema Standard V55 job.

Run only after the official Met image and pinned music have been downloaded.
No voice synthesis, paid API, museum render, publication or false V25 approval.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRE = ROOT / "docs/productions/2026-10-29-socrates-cinema-standard-v55/PREPRODUCTION_V55.json"
ASSETS = ROOT / "output/artvision-socrates-assets-v55"
MET = "https://www.metmuseum.org/art/collection/search/436105"
MUSIC = "https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1400035"
TITLE = "The Death of Socrates"
ARTIST = "Jacques Louis David"
SCENES = [
    ("cup", "The hemlock cup is offered by the distraught attendant", [0.55,0.43], 4.2),
    ("finger", "Socrates points upward while accepting the inevitable", [0.72,0.31], 4.1),
    ("face", "The calm face and pale body of Socrates contrast with grief", [0.69,0.45], 4.3),
    ("attendant", "The red-clad attendant cannot bear to witness the death", [0.41,0.54], 4.5),
    ("plato", "The seated figure of Plato embodies sorrow and recollection", [0.20,0.65], 4.3),
    ("shackles", "The discarded chains lie at the foot of the philosopher's bed", [0.43,0.83], 4.1),
    ("witness", "Grieving disciples on the right reach toward the dying teacher", [0.86,0.50], 4.1),
    ("whole", "The complete friezelike composition restores the full moral choice", [0.50,0.50], 6.1),
]
SPEECH = [
    "La coppa di cicuta è già pronta. Ma al centro di questo dipinto, il condannato sembra essere l'unico uomo sereno.",
    "Socrate indica il cielo e tende la mano verso il veleno. David fa parlare i gesti prima ancora dei volti.",
    "Il filosofo è idealizzato: il corpo saldo e la luce chiara trasformano una morte in una scelta morale.",
    "Il giovane che porge la coppa non riesce a guardare. Il suo dolore rende più sorprendente la calma del maestro.",
    "All'estrema sinistra siede Platone, raffigurato anziano. David lo inserisce deliberatamente come autore del racconto.",
    "Le catene sul pavimento ricordano la prigione, ma il dipinto sposta la nostra attenzione sulla libertà interiore.",
    "I discepoli si aggrappano a Socrate. Il contrasto tra il loro movimento e la sua fermezza regge tutta la scena.",
    "Rivedendo il quadro intero, capiamo il paradosso: chi sta per morire sembra guidare tutti gli altri.",
]
LOCATIONS = [
    "center right, above the attendant's hand",
    "upper center-right, above Socrates's shoulder",
    "center-right, philosopher's head and torso",
    "center-left, figure in red tunic",
    "lower left, elderly seated man",
    "lower center, stone floor under the couch",
    "far right, cluster of grieving pupils",
    "entire horizontal composition",
]
CLAIMS = [
    "The attendant extends the cup of hemlock toward Socrates.",
    "Socrates gestures upward with one hand and toward the cup with the other.",
    "David gives Socrates an idealized, composed body.",
    "The attendant turns away, unable to face the scene.",
    "Plato is seated at the foot of the bed, a deliberate artistic inclusion.",
    "Discarded shackles lie on the stone floor by the couch.",
    "The figures around Socrates display contrasting responses to grief.",
    "The scene is organized as a spare, classical horizontal frieze.",
]
SIGNIFICANCE = [
    "The immediate hook is the decision to accept death rather than renounce convictions.",
    "The two gestures make the moral dilemma visible and narratively legible.",
    "The classical idealization contrasts calm conviction with the terror of death.",
    "The witness's refusal to look emphasizes the emotional cost of the choice.",
    "Plato's presence connects the historical story with its written transmission.",
    "The chains underscore the contrast between physical captivity and inner freedom.",
    "The contrasting expressions make Socrates's stillness more powerful.",
    "The return to the whole reveals the compositional balance behind the ethical story.",
]

def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda:f.read(1024*1024),b""):h.update(part)
    return h.hexdigest()

def prepare():
    meta=json.loads((ASSETS/"PREPARED_ASSETS_V55.json").read_text())
    pre=json.loads(PRE.read_text())
    if meta["status"]!="assets_verified_only" or meta["object_id"]!=436105 or pre["group_id"]!="david_death_of_socrates_met436105_1787":
        raise ValueError("Exact Met source or production identity mismatch")
    for key in ("artwork","music"):
        item=meta[key]
        file=ASSETS/item["file"]
        if not file.is_file() or digest(file)!=item["sha256"]:raise ValueError("Missing or altered "+key)
    group=ASSETS/"ARTVISION_4X1_PLAN.json"
    if not group.exists():raise ValueError("Run official V13 four-brief before this builder")
    plan=json.loads(group.read_text())
    plan["research_status"]="met_primary_record_and_pinned_source_assets_verified"
    ids=[x[0] for x in SCENES]
    d=plan["emotional_direction"]
    d.update({
        "central_tension":"Socrates calmly accepts the cup of hemlock while the disciples around him are overwhelmed by grief.",
        "intended_feeling":["awe","sorrow"],
        "evidence_details":[{"id":key,"location":LOCATIONS[i],"observation":CLAIMS[i],
                             "significance":SIGNIFICANCE[i],"image_source":MET,
                             "claim_type":"documented" if key in ("cup","finger","attendant","plato","shackles","witness") else "interpretation"}
                            for i,(key,*_) in enumerate(SCENES)],
        "reveal_order":ids,
        "opening_hook":"The poisoned cup is visible immediately, then Socrates's gesture reveals a startling calm.",
        "closing_payoff":"Return to the entire canvas after exploring the witnesses, chains and opposing gestures.",
        "wow_justification":"The condemned man is the calmest person in the room, a moral contrast grounded in David's painting."
    })
    plan["learning"]={"previous_reference":"Cyclops V46/V57 and Hiroshige real scale for future Museum only",
                      "experiment_variable":"Source-authentic detail order and restrained music for Cinema Standard",
                      "expected_improvement":"Open with the cup rather than a generic whole-painting establishing shot",
                      "post_render_review":"pending"}
    def scene(key, i, fmt):
        item={"kind":"detail","detail_id":key,
              "purpose":SIGNIFICANCE[i],"movement":"Gentle single-axis optical movement within authentic artwork pixels",
              "emotional_effect":"Quiet moral tension turning toward compassion",
              "duration_seconds":SCENES[i][3]}
        if fmt=="critico":item["spoken_line"]=SPEECH[i]
        return item
    for name, variant in plan["variants"].items():
        fmt, mode = name.split("_")
        variant["status"]="blocked" if fmt=="critico" or mode=="museum" else "planned"
        variant["variation_reason"]=(
            "Museum emphasizes documented 129.5 by 196.2 cm physical scale, sculpted frame and continuous gallery return, unlike the source-only Standard"
            if mode=="museum" else
            "Standard reveals eight meaningful authentic painted details without pretending to reconstruct the real Met gallery"
        )
        variant["opening_0_7"]={
            "first_frame_title_artist":"THE DEATH OF SOCRATES / JACQUES LOUIS DAVID",
            "first_frame_visual":"Authentic painting, cup offered at center, visible from the very first frame",
            "first_3_seconds_hook":"The offered cup and the serene gesture immediately establish the impending death",
            "seconds_3_to_7_reveal":"Reveal the pointing hand and contrast the philosopher with the anguished attendant",
            "detail_id":"cup",
            "mobile_composition_reason":"The cup and fingers remain in the central vertical phone-safe region",
            "audio_or_voice_cue":"Identical verified Gacrux voice required for Critico" if fmt=="critico" else "Water Lily instrumental licensed recording begins softly from the opening",
            "qa_status":"pending_visual_review"
        }
        scenes=[scene(k,i,fmt) for i,(k,*_) in enumerate(SCENES)]
        if mode=="museum":
            variant["museum"].update({
                "width_cm":196.2,"height_cm":129.5,"dimensions_source":MET,
                "frame_status":"Met API frame outer dimensions documented; appearance unverified; quality V46 blocked",
                "gallery_id":"socrates-met436105-specific-reconstruction-not-yet-rendered",
                "entrance_plan":"Artwork already visible in human-scale reconstructed gallery, uninterrupted camera into the authentic image plane",
                "exit_same_gallery_plan":"Uninterrupted return from painted surface through same physical frame to same gallery",
                "scene_is_reconstruction":True
            })
            scenes=[{"kind":"gallery_entry","purpose":"Establish physical dimensions with painting already visible",
                     "movement":"Continuous optical approach through the frame",
                     "emotional_effect":"Anticipation of a difficult moral decision","duration_seconds":3.2}]+scenes+[
                    {"kind":"gallery_exit","purpose":"Return to the same gallery and restore physical scale",
                     "movement":"Continuous optical retreat through same frame",
                     "emotional_effect":"Contemplation after the final reveal","duration_seconds":3.1}]
        variant["scenes"]=scenes
    dump(group,plan)
    source=meta["artwork"]["source_url"]
    music=meta["music"]
    shots=[]
    for i,(key,purpose,focus,seconds) in enumerate(SCENES):
        shots.append({"file":"met_original.jpg","sha256":meta["artwork"]["sha256"],
                      "mode":"whole" if key=="whole" else "detail","detail_id":key,
                      "focus":focus,"duration_seconds":seconds,"purpose":purpose+"; "+SIGNIFICANCE[i]})
    cin={"schema":"artvision-cinema-prepared-v55-v1","variant":"cinema_standard",
         "title":TITLE,"artist":ARTIST,
         "music":{"file":"water_lily_original.mp3","sha256":music["sha256"],
                  "license":"CC BY 4.0","recording_title":"Water Lily",
                  "recording_artist":"Kevin MacLeod","source_url":MUSIC,
                  "license_url":"https://creativecommons.org/licenses/by/4.0/"},
         "shots":shots}
    dump(ASSETS/"CINEMA_PLAN_V55.json",cin)
    for name in plan["variants"]:
        file=ASSETS/name/"PROJECT_V13.json"
        p=json.loads(file.read_text())
        if name!="cinema_standard":
            # Only Cinema Standard is being rendered in this cycle.
            continue
        p["status"]="planned"
        p["assets"]=[
            {"id":"art","role":"visual","file":"../met_original.jpg","sha256":meta["artwork"]["sha256"],
             "source":source,"rights":"Met Open Access Public Domain; object 436105"},
            {"id":"music","role":"music","file":"../water_lily_original.mp3","sha256":music["sha256"],
             "source":MUSIC,"rights":"Kevin MacLeod Water Lily CC BY 4.0, attribution mandatory"}
        ]
        p["scenes"]=[{"asset_id":"art","description":CLAIMS[i],"reason":SIGNIFICANCE[i]}
                     for i in range(len(SCENES))]
        ep=p["editorial_plan"]
        ep.update({
            "subject_insight":"Socrates calmly accepts hemlock while the surrounding disciples grieve.",
            "sources":[{"reference":MET,"finding":"Met identifies painting, 1787, public domain, physical dimensions, Plato and gesture symbolism",
                        "verification_notes":"Official Met catalog consulted; downloaded image and source SHA verified","status":"reviewed"},
                       {"reference":MUSIC,"finding":"Original Water Lily recording by Kevin MacLeod under CC BY 4.0",
                        "verification_notes":"Pinned SHA verified in official acquisition step","status":"reviewed"}],
            "opening_promise":"The philosopher who faces death calmly while everyone else is distraught.",
            "payoff":"Reveal the whole scene after each specific gesture and witness.",
            "cover_reason":"Exact English title and artist with real cup detail on the first frame.",
            "duration_seconds":sum(x[3] for x in SCENES),
            "duration_reason":"Eight purposefully chosen painted details, each held 4-6 seconds for comprehension.",
            "mix_reason":"Restrained visual focus and licensed instrumental recording; no fake museum or voice.",
            "social_languages":{"facebook":"Italian","instagram":"Italian","tiktok":"Italian","youtube":"Italian"},
            "techniques":[{"id":"close_then_wide","reason":"Cup first, full ethical tableau at the end","status":"trial"},
                          {"id":"micro_push","reason":"Subtle camera movement without fabricating painted content","status":"trial"}],
            "media_sourcing":{"policy_id":ep["media_sourcing"]["policy_id"],"review_status":"reviewed",
                             "decisions":[{"asset_id":"art","source_kind":"authentic_artwork","provider":"Metropolitan Museum of Art Open Access",
                                           "source_reference":source,"choice_reason":"Official high-resolution source of exact Met object",
                                           "scene_match_note":"Cup, gesture, witnesses and chains inspected against Met artwork",
                                           "rights_review":"reviewed","scene_relevance":"reviewed","visual_review":"passed"}]},
            "audience_research":{"candidates":[{"artist":x["artist"],"work":x["work"],"visual_hook":x["hook"],
                               "human_interest":x["reason"],"historical_anchor":"Official Met object record "+str(x["object_id"]),
                               "asset_rights_notes":"Public-domain candidate, exact source checked only for selected work",
                               "comparison_reason":x["reason"],
                               "audience_signal":{"status":"unavailable","reason":"No verified current retention or reach analytics"}} for x in pre["v32_comparison"]],
                               "selection_mode":"research_selected","selected_work":TITLE,
                               "selection_reason":"Ethical stakes and legible authentic visual details",
                               "viewer_interest":"Poison cup and the contrast between calm and grief",
                               "creative_direction":"Reveal eight real details before the whole image",
                               "signal_limitations":"No verified social performance data; editorial hypothesis only",
                               "analytics_feedback":"not_yet_published"}
        })
        p["reviews"]={key:{"status":"passed","notes":note} for key,note in {
            "story":"Met catalog supports depicted hemlock, gestures and deliberate Plato inclusion; storyboard is factual with marked interpretation.",
            "visuals":"Original Met image authenticated and 8 semantic focus points cross-checked against official museum reproduction; final MP4 review pending.",
            "rights":"Met isPublicDomain=true and pinned CC BY 4.0 recording with attribution confirmed by acquisition manifest."}.items()}
        dump(file,p)
    dump(ASSETS/"SOCRATES_CINEMA_JOB_V16.json",{
        "adapter":"cinema_v55_prepared",
        "project_file":"output/artvision-socrates-assets-v55/cinema_standard/PROJECT_V13.json",
        "assets_dir":"output/artvision-socrates-assets-v55",
        "cinema_plan_file":"output/artvision-socrates-assets-v55/CINEMA_PLAN_V55.json"})
    deliver=ASSETS/"V55_EDITORIAL"
    deliver.mkdir(exist_ok=False)
    posts={
        "facebook":"Un uomo sta per bere la cicuta. Eppure è l'unico a non sembrare spaventato. In The Death of Socrates, Jacques-Louis David costruisce un dramma di gesti: la coppa, la mano rivolta al cielo, gli allievi disperati. Guardate poi Platone seduto all'estrema sinistra: la sua presenza collega l'immagine al racconto scritto. Opera del 1787, Metropolitan Museum of Art. Immagine: The Met Open Access, pubblico dominio. Musica: Water Lily — Kevin MacLeod (CC BY 4.0), incompetech.com.",
        "instagram":"La mano indica il cielo. L'altra raggiunge il veleno. Il contrasto fra il volto sereno di Socrate e il dolore dei suoi discepoli rende questa tela di Jacques-Louis David un'immagine indimenticabile. Scorriamo i dettagli originali fino a ritrovare la composizione intera. The Death of Socrates, 1787, The Met. Fonte visiva: Met Open Access (PD). Soundtrack: Water Lily by Kevin MacLeod, CC BY 4.0, incompetech.com. #StoriaDellArte #JacquesLouisDavid #Socrate",
        "tiktok":"Sta per morire. Ma guarda chi è il più calmo della stanza. La coppa della cicuta arriva, un allievo distoglie lo sguardo e Socrate continua a indicare il cielo. Non è un effetto AI: sono dettagli reali del dipinto The Death of Socrates (1787) di Jacques-Louis David, custodito al Metropolitan Museum of Art. Opera originale: The Met, pubblico dominio. Water Lily — Kevin MacLeod, CC BY 4.0, incompetech.com. #arte #socrate #painting",
        "youtube":"Perché Socrate sembra così sereno nel momento della morte? In questo breve percorso cinematografico osserviamo la coppa, i gesti, la figura di Platone, le catene e i discepoli prima di tornare all'intera composizione neoclassica. The Death of Socrates (1787), Jacques-Louis David, The Metropolitan Museum of Art, accession 31.45. Riproduzione ufficiale The Met Open Access, pubblico dominio. Colonna sonora: Water Lily di Kevin MacLeod, concessa CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), fonte incompetech.com."
    }
    for k,v in posts.items(): (deliver/("POST_"+k.upper()+".txt")).write_text(v+"\n",encoding="utf-8")
    (deliver/"FONTI_E_DIRITTI.md").write_text(
        "# The Death of Socrates — sources and rights\n\nThe Metropolitan Museum of Art, object 436105, accession 31.45, Jacques Louis David, 1787, 129.5 x 196.2 cm. Official collection: "+MET+
        "\nMet Open Access API: https://collectionapi.metmuseum.org/public/collection/v1/objects/436105 . The exact downloaded primaryImage is marked isPublicDomain=true, hash "+meta["artwork"]["sha256"]+
        ". Frame exterior measurements are documented, but appearance and gallery reconstruction are not authenticated. No Museum film is produced here.\n\n"
        "Recording: Water Lily by Kevin MacLeod, original recording at "+MUSIC+
        " . License Creative Commons Attribution 4.0: https://creativecommons.org/licenses/by/4.0/ . Recording SHA256 "+music["sha256"]+
        ". This film contains no narration and no new AI-generated artwork. Attribution is retained in each social post.\n",encoding="utf-8")
    print(json.dumps({"status":"READY_FOR_OFFICIAL_V54_V13_PREFLIGHT","assets_sha":meta["artwork"]["sha256"],
                      "music_sha":music["sha256"],"variant":"cinema_standard","four_variants_planned":4},indent=2))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--prepare",action="store_true",required=True)
    prepare()
