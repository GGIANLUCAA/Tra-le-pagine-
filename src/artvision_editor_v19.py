#!/usr/bin/env python3
"""ArtVision Editor V19. Piano editoriale non distruttivo; nessun render/pubblicazione."""
import argparse
import json
from collections import Counter
from pathlib import Path

MOVES = {"static","push_in","pull_out","pan_left","pan_right","detail_reveal","match_cut"}
FRAMES = {"detail","portrait","medium","full_artwork","architecture","landscape"}

def check(brief):
    blockers, warnings = [], []
    if not str(brief.get("artist","")).strip():
        blockers.append("Indicare artista")
    if brief.get("format") not in {"artvision_cinema","artvision_meraviglia_breve"}:
        blockers.append("Formato non supportato")
    scenes = brief.get("scenes") or []
    if len(scenes) < 3:
        warnings.append("Meno di tre inquadrature curate")
    prev, run = None, 0
    for i, shot in enumerate(scenes,1):
        move=shot.get("move")
        if move not in MOVES: blockers.append(f"Scena {i}: movimento sconosciuto")
        if shot.get("framing") not in FRAMES: warnings.append(f"Scena {i}: composizione da verificare")
        if not shot.get("artwork"): blockers.append(f"Scena {i}: manca opera")
        if not shot.get("purpose"): warnings.append(f"Scena {i}: manca motivazione")
        run=run+1 if move==prev else 1
        if run==3: warnings.append(f"Scena {i}: tre movimenti {move} consecutivi")
        prev=move
        if shot.get("blurred_background"): warnings.append(f"Scena {i}: sfondo sfocato da valutare")
    if scenes and not scenes[0].get("visual_hook"):
        warnings.append("Apertura priva di gancio VISIVO motivato")
    if brief.get("format")=="artvision_cinema" and any(s.get("on_screen_text") for s in scenes):
        blockers.append("Cinema V6: nessun testo dopo la copertina fissa")
    m=brief.get("music") or {}
    if not all(m.get(x) for x in ("title","composer","source_url","license_url")):
        blockers.append("Musica: titolo, autore, fonte e licenza richiesti")
    sources=brief.get("sources") or []
    if not sources: blockers.append("Registro fonti mancante")
    known={s.get("artwork") for s in sources}
    for i,s in enumerate(sources,1):
        if not all(s.get(x) for x in ("artwork","url","reuse_terms")):
            blockers.append(f"Fonte {i}: compilare opera/URL/riuso")
    for i,s in enumerate(scenes,1):
        if s.get("artwork") not in known:
            warnings.append(f"Scena {i}: opera non presente nel registro fonti")
    e=brief.get("editorial") or {}
    if not e.get("opening") or not e.get("body"):
        warnings.append("Testo editoriale incompleto")
    if len(e.get("hashtags") or [])>5:
        warnings.append("Troppi hashtag (oltre cinque)")
    if not e.get("fact_sources_checked"):
        warnings.append("Fatti del post ancora da verificare")
    if not brief.get("artistic_review_complete"):
        warnings.append("Revisione artistica completa ancora necessaria")
    return blockers, list(dict.fromkeys(warnings))

def outputs(brief):
    blockers,warnings=check(brief)
    m,e=brief.get("music") or {},brief.get("editorial") or {}
    artist=brief.get("artist","Artista")
    chunks=[str(e.get(x,"")).strip() for x in ("opening","body","question") if e.get(x)]
    chunks.append("🎵 Musica: {title} — {composer}\nFonte: {source_url}\nLicenza: {license_url}\nModifiche: {edits}".format(
        title=m.get("title","DA COMPILARE"),composer=m.get("composer","DA COMPILARE"),
        source_url=m.get("source_url","DA COMPILARE"),license_url=m.get("license_url","DA COMPILARE"),
        edits=m.get("edits","Nessuna modifica dichiarata")))
    chunks.append(f"🎨 Opere: {artist}. Elenco fonti e condizioni di riuso nel registro allegato.")
    if e.get("hashtags"): chunks.append(" ".join(e["hashtags"]))
    caption="\n\n".join(chunks)+"\n"
    plan=[f"# Piano di regia V19 — {artist}","","Estensione editoriale: Gold Master V6 invariato.",""]
    for i,s in enumerate(brief.get("scenes") or [],1):
        plan.append(f"{i:02d}. **{s.get('artwork','?')}** — {s.get('framing','?')} / {s.get('move','?')} — {s.get('purpose','motivazione mancante')}")
    plan += ["","## Verifica umana/agente","- Guardare e ascoltare tutto il video, controllare i diritti e la correttezza delle opere.","- Non pubblicare automaticamente; la QA non è certificazione estetica."]
    rights=[f"# Registro fonti — {artist}",""]
    for s in brief.get("sources") or []:
        rights.append(f"- **{s.get('artwork','?')}** — {s.get('url','?')} — {s.get('reuse_terms','?')} — {s.get('attribution','')}")
    rights += ["","Verificare le restrizioni sui beni culturali e l'uso commerciale PRIMA della pubblicazione."]
    report={
      "schema":"artvision-editor-v19","format":brief.get("format"),"artist":artist,
      "blocking_issues":blockers,"warnings":warnings,
      "scene_count":len(brief.get("scenes") or []),
      "moves":dict(Counter(s.get("move") for s in brief.get("scenes") or [])),
      "status":"blocked" if blockers else "editorial_review_required",
      "video_modified":False,"gold_master_modified":False,"automatically_publishable":False
    }
    return report,"\n".join(plan)+"\n",caption,"\n".join(rights)+"\n"

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--brief",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    brief=json.loads(args.brief.read_text(encoding="utf-8"))
    report,plan,caption,rights=outputs(brief)
    args.out.mkdir(parents=True,exist_ok=True)
    files={
      "EDITOR_REPORT_V19.json":json.dumps(report,ensure_ascii=False,indent=2)+"\n",
      "DIRECTION_PLAN_V19.md":plan,
      "SOCIAL_CAPTION_V19.txt":caption,
      "SOURCES_V19.md":rights
    }
    for name,content in files.items(): (args.out/name).write_text(content,encoding="utf-8")
    print(json.dumps({"status":report["status"],"warnings":len(report["warnings"]),"blockers":len(report["blocking_issues"]),"out":str(args.out)},ensure_ascii=False))
    return int(bool(report["blocking_issues"]))

if __name__=="__main__":
    raise SystemExit(main())
