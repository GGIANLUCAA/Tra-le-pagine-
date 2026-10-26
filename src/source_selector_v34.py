#!/usr/bin/env python3
"""V34 source selector: scene-first, policy V33, approved reuse before new requests.

Plan is offline/deterministic. 'discover' explicitly makes ONE API search for ONE
scene, with no downloading, generation, approval or publication. No secrets in logs.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys

try:
    from .media_source_priority_v33 import policy as media_policy
except ImportError:
    from media_source_priority_v33 import policy as media_policy

ROOT = Path(__file__).resolve().parents[1]
MAX_SCENES = 80
MAX_CANDIDATES = 300
KINDS = {"fictional_action", "establishing", "authentic_artwork",
         "documentary_evidence", "documentary_broll", "music_visual"}
FORMAT_DEFAULT = {
    "libri": "fictional_action", "artvision_cinema": "authentic_artwork",
    "artvision_critico": "authentic_artwork", "controluce": "documentary_evidence",
    "visual_music": "music_visual", "hyperlumen": "music_visual",
}
MATERIALS = {"approved_library", "authentic_artwork", "verified_archive",
             "openverse_commons", "pixabay_stock", "ai_horde_original",
             "original_illustration", "user_supplied", "other_licensed"}
AI = {"ai_horde_original", "original_illustration"}
ARCHIVE = {"authentic_artwork", "verified_archive", "openverse_commons"}
STOCK = {"pixabay_stock", "openverse_commons"}
SAFE_ID = re.compile(r"[A-Za-z0-9_-]{1,70}\Z")


class SelectionError(ValueError):
    pass


def require(cond, message):
    if not cond:
        raise SelectionError(message)


def read_json(path):
    p = Path(path)
    require(p.is_file() and p.stat().st_size < 4_000_000, "File JSON assente o troppo grande")
    return json.loads(p.read_text(encoding="utf-8"))


def scene_kind(fmt, scene):
    k = scene.get("need", FORMAT_DEFAULT[fmt])
    require(k in KINDS, "Tipo di scena sconosciuto")
    if fmt in ("artvision_cinema", "artvision_critico"):
        require(k in ("authentic_artwork", "establishing"),
                "ArtVision richiede opere autentiche; non forzare una ricostruzione")
    if fmt in ("visual_music", "hyperlumen"):
        require(k == "music_visual", "Visual Music richiede dati/asset sincronizzati")
    return k


def get_scenes(brief):
    fmt = brief.get("format")
    require(fmt in FORMAT_DEFAULT, "Format non supportato dal V34")
    raw = brief.get("scenes")
    require(isinstance(raw, list) and 1 <= len(raw) <= MAX_SCENES, "Servono da 1 a 80 scene")
    scenes, ids = [], set()
    for i, s in enumerate(raw, 1):
        require(isinstance(s, dict), f"Scena {i}: struttura non valida")
        ident = str(s.get("id") or f"scene_{i:03d}")
        require(bool(SAFE_ID.fullmatch(ident)) and ident not in ids, "ID scena duplicato/non valido")
        ids.add(ident)
        desc = s.get("description")
        require(isinstance(desc, str) and 8 <= len(desc.strip()) <= 1800,
                "Scena senza descrizione precisa")
        kind = scene_kind(fmt, s)
        anchor = s.get("narration_anchor", "")
        require(isinstance(anchor, str), "Ancora della narrazione non valida")
        scenes.append({"id": ident, "description": desc.strip(), "need": kind,
                       "narration_anchor": anchor[:400],
                       "query": s.get("search_query", "")})
    return fmt, scenes


def catalog_assets(data):
    if isinstance(data, list):
        raw = data
    elif isinstance(data, dict):
        raw = data.get("assets", data.get("items", data.get("results", [])))
    else:
        raise SelectionError("Catalogo non valido")
    require(isinstance(raw, list) and len(raw) <= MAX_CANDIDATES, "Catalogo eccessivo/non valido")
    out = []
    for a in raw:
        if not isinstance(a, dict):
            continue
        row = dict(a)
        provider = str(row.get("provider") or "")
        row["provider"] = provider
        if "source_kind" not in row:
            row["source_kind"] = {"pixabay": "pixabay_stock", "openverse": "openverse_commons"}.get(
                provider, "other_licensed")
        # Normalize the existing source adapters without claiming reviews took place.
        row["source_reference"] = str(row.get("source_reference") or row.get("source_url") or "")[:1200]
        sid = row.get("scene_id", "")
        row["scene_id"] = str(sid) if sid is not None else ""
        out.append(row)
    return out


def review_ok(a):
    return (a.get("rights_review") == "reviewed"
            and a.get("visual_review") == "passed"
            and a.get("scene_relevance") == "reviewed"
            and a.get("source_reference"))


def fit(fmt, scene, a):
    """Only explicitly matched and reviewed assets can be reused automatically."""
    kind = a.get("source_kind")
    if kind not in MATERIALS or str(a.get("scene_id")) != scene["id"]:
        return False
    if a.get("media_kind", "image") not in ("image", "video"):
        return False
    if not review_ok(a):
        return False
    # Critical distinction: documented as authentic, not merely claiming to be.
    if scene["need"] == "authentic_artwork":
        return (kind in ARCHIVE and a.get("authenticity_review") == "reviewed"
                and a.get("media_kind", "image") == "image")
    if scene["need"] == "documentary_evidence":
        return kind in ARCHIVE and a.get("authenticity_review") == "reviewed"
    if scene["need"] == "documentary_broll":
        return kind not in AI
    if scene["need"] == "fictional_action":
        return kind in ("approved_library", "ai_horde_original", "original_illustration",
                        "user_supplied", "other_licensed")
    if scene["need"] == "music_visual":
        return kind in ("approved_library", "original_illustration", "user_supplied",
                        "other_licensed") and a.get("sync_review") == "passed"
    return kind not in AI or fmt == "libri"


def fallback_for(fmt, scene):
    need = scene["need"]
    if need == "authentic_artwork":
        return ["approved_authentic_artwork", "museum_open_access_catalogue", "openverse_v7",
                "STOP_if_no_authentic_rights_verified_asset"]
    if need == "documentary_evidence":
        return ["approved_documentary_evidence", "primary_source_archive", "openverse_v7",
                "STOP_and_label_reconstruction_if_no_evidence"]
    if need == "documentary_broll":
        return ["approved_archive", "openverse_v7", "pixabay_single_search",
                "STOP_if_stock_is_not_relevant"]
    if need == "establishing":
        return ["approved_library", "openverse_v7", "pixabay_single_search",
                "manual_original_illustration_trial"]
    if need == "music_visual":
        return ["approved_synchronized_assets", "original_geometry_renderer",
                "STOP_if_not_synchronized"]
    return ["approved_scene_illustration", "ai_horde_manual_three_scene_trial",
            "other_model_gpu_not_integrated", "STOP_if_character_consistency_fails"]


def rank_reviewed(scene, items, fmt):
    candidates = [a for a in items if fit(fmt, scene, a)]
    # Prefer an approved existing exact scene file; otherwise authenticity dominates.
    category = {
        "approved_library": 100, "user_supplied": 90, "authentic_artwork": 86,
        "verified_archive": 81, "openverse_commons": 75,
        "original_illustration": 74, "ai_horde_original": 70,
        "other_licensed": 65, "pixabay_stock": 48
    }
    if scene["need"] in ("authentic_artwork", "documentary_evidence"):
        category.update({"authentic_artwork": 115, "verified_archive": 100,
                         "openverse_commons": 90})
    candidates.sort(key=lambda x: (-category.get(x["source_kind"], 0),
                                   str(x.get("id") or ""), x["source_reference"]))
    # Protect against duplicate files and duplicate source links.
    seen, result = set(), []
    for a in candidates:
        key = a.get("sha256") or a["source_reference"]
        if key in seen:
            continue
        seen.add(key)
        result.append(a)
    return result


def build_report(brief, assets=None):
    fmt, scenes = get_scenes(brief)
    configured = media_policy()
    require(configured["id"] == "media-priority-v33",
            "Regole centrali diverse, aggiornare il selettore")
    items = catalog_assets(assets or [])
    all_scenes = []
    for s in scenes:
        reviewed = rank_reviewed(s, items, fmt)
        selected = reviewed[0] if reviewed else None
        all_scenes.append({
            "scene_id": s["id"], "narration_anchor": s["narration_anchor"],
            "description": s["description"], "need": s["need"],
            "status": "reviewed_asset_available" if selected else "source_needed",
            "recommended_source": (selected.get("source_kind") if selected
                                   else fallback_for(fmt, s)[0]),
            "approved_candidate": ({
                "id": selected.get("id"), "source_reference": selected["source_reference"],
                "source_kind": selected["source_kind"], "provider": selected["provider"],
                "sha256": selected.get("sha256"),
            } if selected else None),
            "reviewed_candidates": len(reviewed),
            "recommended_path": fallback_for(fmt, s),
            "search_query_suggested": s["query"] if isinstance(s["query"], str) else "",
            "automatic_generation": False,
            "needs_editorial_confirmation": True,
        })
    return {
        "schema": "source-selector-v34", "format": fmt,
        "title": brief.get("title", brief.get("topic", "")),
        "policy": configured["id"], "scenes": all_scenes,
        "counts": {
            "scenes": len(all_scenes),
            "verified_reuse_candidates": sum(x["status"] == "reviewed_asset_available" for x in all_scenes),
            "need_sources": sum(x["status"] == "source_needed" for x in all_scenes),
        },
        "no_api_calls_by_default": True,
        "no_paid_services": True, "no_auto_download": True,
        "no_auto_render": True, "no_auto_publish": True,
        "provider_verification": "Existing catalogue credentials only; service availability not guaranteed.",
        "note": "Scene routing and exact reviewed reuse, not AI verification of narrative accuracy.",
    }


def discover_single(brief, catalog, scene_id, provider, query, limit, environ=None):
    fmt, scenes = get_scenes(brief)
    scene = next((s for s in scenes if s["id"] == scene_id), None)
    require(scene is not None, "Scena richiesta inesistente")
    require(provider in ("pixabay", "openverse"), "Solo provider effettivamente integrati")
    require(scene["need"] in ("establishing", "documentary_broll"),
            "Ricerca stock non adatta a scene letterarie precise o opere autentiche")
    require(provider != "openverse" or scene["need"] != "music_visual", "Non compatibile")
    # Uses only ONE existing adapter call, never both APIs or loops over all scenes.
    try:
        from .free_sources_bridge_v1 import produce
    except ImportError:
        from free_sources_bridge_v1 import produce
    search = produce(provider, query, "image", limit, environ)
    candidates = catalog_assets(catalog or [])
    added = []
    for item in search["items"]:
        row = dict(item)
        row["scene_id"] = scene["id"]
        row["media_kind"] = "image"
        row["rights_review"] = "pending"
        row["visual_review"] = "pending"
        row["scene_relevance"] = "pending"
        row["authenticity_review"] = "pending"
        added.append(row)
    report = build_report(brief, candidates + added)
    return report, {"schema": "source-discovery-v34",
                    "scene_id": scene["id"], "provider": provider, "query": query,
                    "results": added, "rights_revised": False, "automatic_selection": False,
                    "new_api_calls": 1, "downloaded_files": 0}


def main():
    p = argparse.ArgumentParser(description="V34 source routing, safe from Android.")
    p.add_argument("--brief", default="config/image_pipeline_v1_demo.json")
    p.add_argument("--catalog", default="")
    p.add_argument("--mode", choices=("plan", "discover"), default="plan")
    p.add_argument("--scene", default="")
    p.add_argument("--provider", choices=("pixabay", "openverse"), default="openverse")
    p.add_argument("--query", default="")
    p.add_argument("--limit", type=int, default=3)
    p.add_argument("--out", default="output/media_v34")
    args = p.parse_args()
    try:
        brief = read_json(args.brief)
        catalog = read_json(args.catalog) if args.catalog else []
        output = Path(args.out)
        output.mkdir(parents=True, exist_ok=True)
        if args.mode == "plan":
            report = build_report(brief, catalog)
            detail = None
        else:
            require(bool(args.scene and args.query), "La ricerca richiede una scena e query esplicite")
            report, detail = discover_single(brief, catalog, args.scene, args.provider,
                                             args.query, args.limit)
        (output / "PIANO_FONTI_V34.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if detail:
            (output / "CANDIDATI_DA_APPROVARE_V34.json").write_text(
                json.dumps(detail, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": "ok", "mode": args.mode, "scenes": report["counts"]["scenes"],
                          "reusable": report["counts"]["verified_reuse_candidates"],
                          "missing": report["counts"]["need_sources"]}))
    except (SelectionError, ValueError, KeyError) as exc:
        raise SystemExit("Selettore V34: " + str(exc)) from None


if __name__ == "__main__":
    main()
