"""Permanent V33 media routing and provenance preflight.

No network, no API calls, no automatic approvals. Reads the unique editorial policy.
Only new V13 projects with visual assets require per-asset evidence; historical
master projects remain unmodified and must be explicitly migrated if reused.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/"config/editorial_rules.json"
SOURCE_KINDS={
    "approved_library", "authentic_artwork", "verified_archive",
    "openverse_commons", "pixabay_stock", "ai_horde_original",
    "original_illustration", "user_supplied", "other_licensed",
}
AI_KINDS={"ai_horde_original", "original_illustration"}


def policy():
    return json.loads(CONFIG.read_text(encoding="utf-8"))["media_source_priority"]


def proposal(kind, source_needed="narrative_scene"):
    rules=policy()
    formats=rules["format_priority"]
    if kind not in formats:
        raise ValueError("Format sconosciuto")
    return {
        "policy_id":rules["id"],
        "review_status":"pending",
        "subject_specific_need":source_needed,
        "recommended_sequence":list(formats[kind]),
        "decisions":[],
        "note":"Strumenti suggeriti, non chiamati. Diritti e aderenza vanno verificati.",
    }


def check(project, visual_ids):
    """Block declared visual assets without recorded, reviewed sourcing decisions."""
    if not visual_ids:
        return []
    errors=[]
    rules=policy()
    planning=project.get("editorial_plan")
    record=planning.get("media_sourcing") if isinstance(planning,dict) else None
    if not isinstance(record,dict) or record.get("policy_id")!=rules["id"]:
        return ["Priorita media V33: manca il piano fonti con la versione corrente"]
    if record.get("review_status")!="reviewed":
        errors.append("Priorita media V33: revisione fonti non completata")
    decisions=record.get("decisions")
    if not isinstance(decisions,list):
        return errors+["Priorita media V33: elenco decisioni visuali non valido"]
    by_id={}
    for entry in decisions:
        if not isinstance(entry,dict) or not isinstance(entry.get("asset_id"),str):
            errors.append("Priorita media V33: decisione asset non valida")
            continue
        aid=entry["asset_id"]
        if aid in by_id:
            errors.append("Priorita media V33: decisione duplicata per "+aid)
        by_id[aid]=entry
        if aid not in visual_ids:
            errors.append("Priorita media V33: decisione senza asset visivo: "+aid)
        if entry.get("source_kind") not in SOURCE_KINDS:
            errors.append("Priorita media V33: sorgente non riconosciuta: "+aid)
        for key in ("provider", "source_reference", "choice_reason", "scene_match_note"):
            if not isinstance(entry.get(key),str) or not entry[key].strip():
                errors.append(f"Priorita media V33: {aid} manca {key}")
        if entry.get("rights_review")!="reviewed":
            errors.append("Priorita media V33: diritti da verificare per "+aid)
        if entry.get("scene_relevance")!="reviewed":
            errors.append("Priorita media V33: pertinenza da verificare per "+aid)
        if entry.get("visual_review")!="passed":
            errors.append("Priorita media V33: revisione visuale mancante per "+aid)
        source_kind=entry.get("source_kind")
        actual_format=project.get("format")
        if (actual_format in ("artvision_cinema","artvision_critico") and source_kind in AI_KIN
            and entry.get("role_in_video")!="labelled_supporting_reconstruction"):
            errors.append("ArtVision: illustrazione AI non puo sostituire l'opera originale: "+aid)
        if (actual_format=="controluce" and source_kind in AI_KIN
            and entry.get("role_in_video")!="labelled_supporting_reconstruction"):
            errors.append("Controluce: ricostruzione AI non etichettata: "+aid)
    for aid in sorted(set(visual_ids)-set(by_id)):
        errors.append("Priorita media V33: manca provenienza e scelta motivata per "+aid)
    return errors
