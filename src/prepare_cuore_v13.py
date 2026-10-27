#!/usr/bin/env python3
"""Build an honest V13 dossier for the Poe episode; no TTS, no publishing."""
from pathlib import Path
import argparse, json, shutil, hashlib, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from video_director_v13 import brief, check, write_json

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--episode",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--visual-reviewed",action="store_true",
                    help="Only after actually inspecting the generated contact sheet")
    a=ap.parse_args()
    ep=a.episode; out=a.out
    assert not out.exists() or not any(out.iterdir()),"Refuse to overwrite an existing dossier"
    project=brief("libri","Il cuore rivelatore — Edgar Allan Poe",out)
    (out/"assets").mkdir(exist_ok=True)
    script=ep/"testo.txt"
    shutil.copy2(script,out/"COPIONE.txt")
    cues=json.loads((ep/"scene_cues.json").read_text())
    paras=[x.strip() for x in script.read_text(encoding="utf-8").split("\n\n") if x.strip()]
    assert len(paras)==len(cues)==16
    project["script"]="COPIONE.txt"
    project["bibliography"]={
        "author":"Edgar Allan Poe","publication_year":1843,
        "edition_reference":"The Pioneer, January 1843; Edgar Allan Poe Society comparative transcription",
        "rights_notes":"Original English text public domain (Poe died 1849); Italian narration newly written, not a modern translation."
    }
    project["editorial_metadata"]={"series":"Tra le Pagine — Classici che parlano ancora",
        "themes":"obsession, guilt, unreliable narrator","genre":"gothic short story",
        "narration_style":"intimate restrained Italian storytelling"}
    project["business"]={"audience":"Lettori italiani di classici e racconti psicologici",
        "viewer_promise":"Il delitto perfetto crolla per un rumore forse immaginato",
        "original_contribution":"Adattamento italiano originale e 16 illustrazioni d'inchiostro e luce",
        "primary_platform":"Facebook","goal":"racconto completo e riconoscibilità della serie",
        "cta":"Nessuna domanda artificiale", "experiment":"apertura con il battito, non con il nome autore",
        "time_budget_minutes":55,"cash_budget_eur":0}
    plan=project["editorial_plan"]
    plan.update({
        "subject_insight":"Poe usa un narratore inattendibile: ciò che sente può essere colpa, non un cuore soprannaturale.",
        "sources":[
            {"reference":"https://www.eapoe.org/works/cmprs/pt043c00.htm",
             "finding":"Testo comparativo della prima pubblicazione 1843 e versioni successive; occhio velato, sette notti, ottava notte, polizia e confessione.",
             "verification_notes":"Consultato il testo e la storia delle edizioni il 27 ottobre 2026; adattamento originale senza copiare traduzioni.","status":"reviewed"},
            {"reference":"https://economie.fgov.be/en/themes/intellectual-property/intellectual-property-rights/copyright-and-related-rights/copyright/copyright-protection-works/copyright-duration",
             "finding":"Durata ordinaria di copyright 70 anni dopo la morte nell'UE.",
             "verification_notes":"Fonte istituzionale; Poe morto 1849, originale pubblicato 1843. Non copiare traduzioni moderne.","status":"reviewed"}],
        "opening_promise":"Un battito sotto le assi rivelerà un segreto nascosto.",
        "payoff":"La confessione è provocata da un battito che gli altri non sembrano sentire.",
        "cover_reason":"L'occhio velato e il legno scuro riassumono l'ossessione senza spoilerare l'epilogo.",
        "duration_seconds":175,
        "duration_reason":"339 parole, 16 svolte autonome; durata reale ricalcolata dopo Gacrux, non un template.",
        "techniques":[
            {"id":"static_tableau","reason":"La tensione richiede attese leggibili e pause visive.","status":"trial"},
            {"id":"micro_push","reason":"Avvicinamento lento all'occhio e alla confessione, senza tagli di volti.","status":"trial"},
            {"id":"motivated_cut","reason":"Un taglio per ogni cambio di fatto narrato, nessuna dissolvenza fantasma.","status":"trial"},
            {"id":"negative_space","reason":"Il vuoto della stanza amplifica il sospetto.","status":"trial"}],
        "mix_reason":"Inchiostro, controluce e legno; camera contenuta, tagli puliti e battito come motivo visivo.",
        "social_languages":{"facebook":"it","instagram":"it","tiktok":"it","youtube":"it"},
        "comparison_reference":"V38: La macchina del tempo è un riferimento positivo per varietà, non un template.",
        "voice_image_sync_review":"pending_until_real_audio",
        "artistic_review":"pending_until_full_video",
    })
    plan["narrative_design"]={
        "story_beats":[c["description"] for c in cues],
        "distinct_visual_needs":[{"beat":i+1,"need":c["description"]} for i,c in enumerate(cues)],
        "image_count_reason":"16 scene per 16 cambi effettivi di situazione e prospettiva, non per quota fissa.",
        "pace_reason":"Alternare attese statiche e crescendo verso la confessione; timing da voce effettiva.",
        "reference_id":"time_machine_20261026",
        "portable_lessons":["visuals match spoken actions","distinct scenes","no ghosting"],
        "do_not_copy_reference_parameters":True
    }
    assets=[];decisions=[];scenes=[]
    for i,cue in enumerate(cues):
        source=ep/"images"/f"scena_{i+1:02}.jpg"
        assert source.is_file(),source
        target=out/"assets"/source.name
        shutil.copy2(source,target)
        aid=f"v{i+1:02}"
        assets.append({"id":aid,"role":"visual","file":f"assets/{source.name}",
                       "sha256":sha(target),"source":"original scripted illustration by Tra le Pagine",
                       "rights":"original code, no external media; review final composition"})
        decisions.append({
            "asset_id":aid,"source_kind":"original_illustration",
            "provider":"Tra le Pagine original procedural illustration",
            "source_reference":"src/illustrate_cuore_20261027.py",
            "choice_reason":"This precise fictional action cannot be truthfully sourced as generic stock.",
            "scene_match_note":cue["description"],
            "rights_review":"reviewed","scene_relevance":"reviewed",
            "visual_review":"passed" if a.visual_reviewed else "pending"})
        scenes.append({"asset_id":aid,"description":cue["description"],
                       "reason":"Rappresenta l'evento del paragrafo "+str(i+1),
                       "narration_anchor":paras[i][:min(45,len(paras[i]))]})
    project["assets"]=assets;project["scenes"]=scenes
    plan["media_sourcing"]={"policy_id":plan["media_sourcing"]["policy_id"],
        "review_status":"reviewed" if a.visual_reviewed else "pending",
        "decisions":decisions,
        "note":"Original local render; rights from own code. Visual inspection not automatically certified."}
    project["reviews"]={
        "story":{"status":"passed","notes":"Compared against Poe Society 1843 text, 16 narrative beats."},
        "visuals":{"status":"passed" if a.visual_reviewed else "pending",
                   "notes":"Contact sheet checked for completeness and composition" if a.visual_reviewed else "Awaiting visual inspection"},
        "rights":{"status":"passed","notes":"Original public-domain literary source and original programmatic images; no stock."}}
    write_json(out/"PROJECT_V13.json",project)
    result=check(out/"PROJECT_V13.json")
    write_json(out/"PREFLIGHT_V13.json",result)
    print(json.dumps({"ready":result["ready"],"blockers":result["blockers"],
                      "warnings":result["warnings"]},ensure_ascii=False,indent=2))
    if a.visual_reviewed and not result["ready"]:
        raise SystemExit("V13 blocked")
if __name__=="__main__":
    main()
