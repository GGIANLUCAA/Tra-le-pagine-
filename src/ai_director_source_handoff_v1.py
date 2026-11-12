#!/usr/bin/env python3
"""AI Director: keyless archive discovery -> unapproved source intake for V34.

Purely offline. Does not download, generate or license content, inspect a video,
or auto-select a source for a final film. Real source use still requires evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from source_selector_v34 import build_report, get_scenes, render_html

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "ai-director-keyless-archives-v1"
OUT_SCHEMA = "ai-director-source-intake-v1"
MAX_BYTES = 200_000
MAX_CANDIDATES = 9
HOSTS = {
    "artic": {"www.artic.edu"},
    "met": {"www.metmuseum.org"},
    "cleveland": {"clevelandart.org", "www.clevelandart.org"},
    "commons": {"commons.wikimedia.org"},
    "loc": {"www.loc.gov"},
    "archive": {"archive.org"},
    "wellcome": {"wellcomecollection.org", "wellcome.org"},
}
KIND_TO_MATERIAL = {
    "art": "authentic_artwork",
    "historical_video": "verified_archive",
    "historical_photo": "verified_archive",
    "general": "verified_archive",
}
SCENE_KIND = {
    "art": "authentic_artwork",
    "historical_video": "documentary_evidence",
    "historical_photo": "documentary_evidence",
    "general": "documentary_evidence",
}

class HandoffError(ValueError):
    pass


def read_json(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise HandoffError("Missing/oversized input JSON")
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise HandoffError("Input must be a JSON object")
    return obj


def safe_source_url(url, provider):
    if not isinstance(url, str) or len(url) > 1400:
        return False
    try:
        p = urlsplit(url)
    except ValueError:
        return False
    return (p.scheme == "https" and p.hostname in HOSTS.get(provider, set())
            and not p.username and not p.password and p.port is None)


def _str(value, maximum=300):
    if not isinstance(value, str):
        return ""
    return value.strip()[:maximum]


def _known_work(item, aliases):
    """Evidence notes, NOT an automatic rights clearance or image identity proof."""
    work_id = item.get("curated_source_id")
    if not isinstance(work_id, str) or not isinstance(aliases, dict):
        return {}
    for work in aliases.get("entries", []):
        if not isinstance(work, dict) or work.get("id") != work_id:
            continue
        if work.get("publication_authorized") is not False:
            continue
        if work.get("fallback_provider") != item.get("provider"):
            continue
        if work.get("example_record") != item.get("source_url"):
            continue
        return {
            "work_identity_claim": {"artist": _str(work.get("artist")),
                                    "title": _str(work.get("canonical_title")),
                                    "museum_reference": _str(work.get("reference_url"), 1200),
                                    "museum_record_id": work_id},
            "publisher_terms_url": _str(work.get("usage_terms_url"), 1200),
            "credit_line_draft": _str(work.get("credit_line_draft"), 300),
            "work_dimensions_cm_from_reference": work.get("dimensions_cm"),
            "museum_frame_verified": False, "museum_room_verified": False,
            "high_resolution_file_verified": False,
        }
    return {}


def build_handoff(research, *, aliases=None, scene_id="", scene_brief=None):
    if research.get("schema") != SCHEMA:
        raise HandoffError("Expected real keyless research JSON")
    if research.get("key_required") is not False or research.get("europeana_used") is not False:
        raise HandoffError("Research must be keyless and Europeana-free")
    if research.get("publication_authorized") is not False or research.get("rights_verified") is not False:
        raise HandoffError("Discovery cannot claim automatic approval")
    if research.get("paid_calls") is not False or research.get("external_ai_calls") != 0:
        raise HandoffError("Discovery with unknown spend or AI calls not acceptable")
    category = research.get("category")
    if category not in KIND_TO_MATERIAL:
        raise HandoffError("Unrecognized source category")
    source_items = research.get("items")
    if not isinstance(source_items, list) or len(source_items) > MAX_CANDIDATES:
        raise HandoffError("Archive candidates missing or excessive")
    if research.get("candidate_count") != len(source_items):
        raise HandoffError("Candidate count does not match input")
    if scene_id:
        if not isinstance(scene_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,70}", scene_id):
            raise HandoffError("Invalid scene ID")
        if not isinstance(scene_brief, dict):
            raise HandoffError("Real V34 scene brief required for scene routing")
        fmt, scenes = get_scenes(scene_brief)
        shot = next((s for s in scenes if s["id"] == scene_id), None)
        if not shot or shot["need"] != SCENE_KIND[category]:
            raise HandoffError("Source category does not match this real storyboard scene")
    elif scene_brief is not None:
        raise HandoffError("scene_id required when scene_brief is supplied")
    intake = []
    seen = set()
    for raw in source_items:
        if not isinstance(raw, dict) or raw.get("approved") is not False:
            raise HandoffError("All discovery sources must be explicitly unapproved")
        provider, kind = raw.get("provider"), raw.get("media_kind")
        url = raw.get("source_url")
        if provider not in HOSTS or not safe_source_url(url, provider):
            raise HandoffError("Source record has unknown origin or unsafe URL")
        expected = {"historical_video": {"video"}, "historical_photo": {"image"},
                    "art": {"image"}, "general": {"image", "video"}}[category]
        if kind not in expected:
            raise HandoffError("Media kind mismatch in source research")
        if raw.get("rights_review") != "pending":
            raise HandoffError("Unexpected rights status on discovered source")
        if url in seen:
            continue
        seen.add(url)
        ident = hashlib.sha256(url.encode("utf-8")).hexdigest()[:20]
        row = {
            "id": "archive_" + ident, "scene_id": scene_id,
            "provider": provider, "media_kind": kind,
            "source_kind": KIND_TO_MATERIAL[category],
            "source_reference": url, "source_url": url,
            "source_title": _str(raw.get("title")),
            "source_creator_claim": _str(raw.get("author")),
            "source_date_claim": _str(raw.get("date"), 80),
            "license_claim_unverified": _str(raw.get("license_claim"), 400),
            "rights_review": "pending", "visual_review": "pending",
            "scene_relevance": "pending", "authenticity_review": "pending",
            "source_sha256": None, "local_file": None,
            "actual_pixel_dimensions": None,
            "attribution_verified": False,
            "asset_downloaded": False, "render_allowed": False,
            "approved": False, "publication_authorized": False,
            "required_review": [
                "Inspect original provider record and uploader provenance",
                "Verify Italy/commercial reuse rights and mandatory credits",
                "Visually compare actual file with correct painting/era/scene",
                "Inspect downloaded ORIGINAL bytes, dimensions, SHA256 and video motion",
                "Confirm source-to-scene mapping and existing series quality gates",
            ],
        }
        row.update(_known_work(raw, aliases))
        intake.append(row)
    return {
        "schema": OUT_SCHEMA,
        "category": category, "query": _str(research.get("query")),
        "artist_filter": _str(research.get("artist_filter")),
        "source_run": "read_only_catalogue_results",
        "items": intake, "candidate_count": len(intake),
        "scene_id": scene_id, "scene_assignment_verified": False,
        "rights_verified": False, "assets_verified": False,
        "readiness": "research_candidates_only_not_renderable",
        "v34_reuse_allowed": False,
        "europeana_used": False, "paid_calls": False,
        "no_download": True, "no_render": True, "no_publish": True,
    }


def render_review_html(result):
    esc = lambda x: html.escape(str(x or ""), quote=True)
    parts = []
    for item in result["items"]:
        reference = item.get("work_identity_claim") or {}
        curator = (f'<p>Riferimento opera: {esc(reference.get("title"))} — '
                   f'{esc(reference.get("artist"))} · '
                   f'{esc(reference.get("museum_reference"))}</p>') if reference else ""
        credit = (f'<p>Credito suggerito (non verificato): '
                  f'{esc(item.get("credit_line_draft"))}</p>') if item.get("credit_line_draft") else ""
        checks = "".join("<li>" + esc(v) + "</li>" for v in item["required_review"])
        parts.append('<section><h2>' + esc(item["source_title"]) +
                     '</h2><p>Archivio: ' + esc(item["provider"]) + ' · ' +
                     esc(item["media_kind"]) + '</p><p>Fonte: <a href="' +
                     esc(item["source_reference"]) + '">' + esc(item["source_reference"]) +
                     '</a></p>' + curator + credit +
                     '<p>Diritti, identificazione e file originale: NON VERIFICATI</p>'
                     '<ul>' + checks + '</ul></section>')
    no_results = '<section><p>Nessuna fonte candidata da assegnare; continuare la ricerca senza inventare asset.</p></section>' if not parts else ""
    return ('<!doctype html><html lang="it"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>AI Director · Fonti da verificare</title><style>'
            'body{background:#111822;color:#edf0f6;font:16px system-ui;max-width:820px;'
            'margin:0 auto;padding:20px;line-height:1.5}section{background:#202b38;'
            'padding:18px;border-radius:12px;margin:14px 0}a{color:#a8d5ff;'
            'overflow-wrap:anywhere}h2{font-size:18px}</style>'
            '<h1>Archivio → Regia: schede sorgenti</h1>'
            '<p>Solo ricerca: nessuna fonte è autorizzata al rendering o alla pubblicazione.</p>'
            + "".join(parts) + no_results + '</html>')


def write_output(result, out, *, scene_brief=None):
    dest = Path(out)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "V34_PENDING_CATALOG.json").write_text(
        json.dumps({"assets": result["items"], "reviewed": False}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    (dest / "SOURCE_INTAKE.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (dest / "SOURCE_REVIEW_ANDROID.html").write_text(render_review_html(result), encoding="utf-8")
    if scene_brief is not None:
        # Authoritative V34 selector must report source_needed for every pending candidate.
        report = build_report(scene_brief, result["items"])
        if report["counts"]["verified_reuse_candidates"] != 0:
            raise HandoffError("Unexpected V34 auto-approval of an unreviewed source")
        (dest / "PIANO_FONTI_V34.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (dest / "SCHEDA_FONTI_ANDROID_V34.html").write_text(render_html(report), encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--research", required=True)
    ap.add_argument("--aliases", default=str(ROOT / "config/ai_director_curated_source_aliases_v1.json"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--scene-brief", default="")
    ap.add_argument("--scene-id", default="")
    args = ap.parse_args(argv)
    source = read_json(args.research)
    aliases = read_json(args.aliases)
    scenes = read_json(args.scene_brief) if args.scene_brief else None
    result = build_handoff(source, aliases=aliases, scene_id=args.scene_id, scene_brief=scenes)
    write_output(result, args.out, scene_brief=scenes)
    print(json.dumps({"intake": result["candidate_count"], "render_allowed": False,
                      "rights_verified": False, "v34_reuse_allowed": False}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (HandoffError, ValueError, OSError, KeyError) as exc:
        raise SystemExit("SOURCE_HANDOFF_FAIL_CLOSED: " + str(exc)) from None
