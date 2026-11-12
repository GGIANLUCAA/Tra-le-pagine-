#!/usr/bin/env python3
"""Keyless primary-source search for AI Director; never Europeana, no API keys.

Reuses the museum/archive adapters already present in Tra le Pagine, with
per-provider caps, no retry, evidence-only candidate status, and Android reports.
Not a downloader, license clearance, film renderer, AI model, or publisher.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import re

from ai_director_v1 import audit_scenes, base_report, editorial_prompts, make_brief, write_reports
from public_archive_sources_v2 import search as search_public

ROOT = Path(__file__).resolve().parents[1]
POLICY = {
    "art": ("artic", "met", "cleveland"),
    "historical_video": ("loc", "archive", "commons"),
    "historical_photo": ("loc", "commons", "wellcome"),
    "general": ("loc", "artic", "commons"),
}
ALLOWED = frozenset(p for group in POLICY.values() for p in group)
MAX_TOTAL_CANDIDATES = 9
MAX_REQUESTS = 12


class KeylessResearchError(ValueError):
    pass


def _valid_query(query):
    if not isinstance(query, str) or not 3 <= len(query.strip()) <= 100:
        raise KeylessResearchError("Query length must be 3 to 100 characters")
    if re.search(r"[\x00-\x1f\x7f]", query):
        raise KeylessResearchError("Search query contains forbidden control characters")
    return query.strip()


def _safe_field(v, length=240):
    return v[:length] if isinstance(v, str) else ""


def select_providers(category="general", selected=None):
    if category not in POLICY:
        raise KeylessResearchError("Unsupported research category")
    if selected:
        if selected not in ALLOWED:
            raise KeylessResearchError("Provider must be an approved keyless source")
        return (selected,)
    return POLICY[category]


def research(query, *, category="general", selected=None, per_provider=2, fetcher=None):
    """User-initiated, maximum three keyless sources. No media is retrieved."""
    query = _valid_query(query)
    if type(per_provider) is not int or not 1 <= per_provider <= 3:
        raise KeylessResearchError("Per-provider limit must be 1..3")
    chosen = select_providers(category, selected)
    items, provider_reports, seen = [], [], set()
    total_calls = 0
    for provider in chosen:
        # Existing v1/v2 adapters: Met may issue 1 metadata query + up to N object fetches.
        planned_max = 1 + per_provider if provider == "met" else 1
        if total_calls + planned_max > MAX_REQUESTS:
            provider_reports.append({"provider": provider, "status": "skipped_budget"})
            continue
        try:
            response = search_public(provider, query, limit=per_provider, fetcher=fetcher)
            calls = response.get("api_requests")
            if type(calls) is not int or not 1 <= calls <= planned_max:
                raise KeylessResearchError("Source adapter returned invalid request count")
            total_calls += calls
            source_items = response.get("items")
            if not isinstance(source_items, list):
                raise KeylessResearchError("Source adapter returned invalid candidates")
            inserted = 0
            excluded_by_media_kind = 0
            wanted_media = {
                "historical_video": {"video"},
                "historical_photo": {"image"},
                "art": {"image"},
            }.get(category)
            for candidate in source_items[:per_provider]:
                if not isinstance(candidate, dict):
                    continue
                # A museum painting tagged with the searched city is not historic film.
                # Filter *before* selection; never claim metadata proves visual relevance.
                if wanted_media is not None and candidate.get("media_kind") not in wanted_media:
                    excluded_by_media_kind += 1
                    continue
                url = candidate.get("source_url")
                if not isinstance(url, str) or not url.startswith("https://") or url in seen:
                    continue
                seen.add(url)
                items.append({
                    "provider": provider, "id": _safe_field(candidate.get("id")),
                    "title": _safe_field(candidate.get("title")),
                    "author": _safe_field(candidate.get("author")),
                    "date": _safe_field(candidate.get("date"), 80),
                    "media_kind": _safe_field(candidate.get("media_kind"), 60),
                    "source_url": url[:1200],
                    "preview": _safe_field(candidate.get("preview"), 1200),
                    "license_claim": _safe_field(candidate.get("license_claim"), 320),
                    "rights_review": "pending", "authenticity_review": "pending",
                    "scene_relevance": "pending", "source_verified": False,
                    "approved": False, "downloaded": False
                })
                inserted += 1
                if len(items) >= MAX_TOTAL_CANDIDATES:
                    break
            provider_reports.append({"provider": provider, "status": "response_received",
                                     "added_candidates": inserted,
                                     "excluded_by_media_kind": excluded_by_media_kind,
                                     "api_requests": calls})
        except (ValueError, TypeError, KeyError, OSError) as exc:
            # Never reflect source response, user credentials or URL into logs.
            provider_reports.append({"provider": provider, "status": "provider_unavailable_or_invalid"})
            total_calls += planned_max  # conservative estimate when an exception hides partial requests
    status = "candidates_need_review" if items else "no_candidates_or_sources_unavailable"
    return {
        "schema": "ai-director-keyless-archives-v1", "category": category,
        "query": query, "status": status, "providers": provider_reports,
        "api_requests_upper_bound": total_calls,
        "items": items, "candidate_count": len(items),
        "key_required": False, "europeana_used": False,
        "external_ai_calls": 0, "paid_calls": False,
        "rights_verified": False, "media_downloaded": False,
        "human_approved": False, "publication_authorized": False,
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat()
    }


def director_from_candidates(result, subject, fmt="documentario"):
    if not isinstance(result, dict) or result.get("schema") != "ai-director-keyless-archives-v1":
        raise KeylessResearchError("Expected keyless archive result")
    if result.get("europeana_used") is not False or result.get("key_required") is not False:
        raise KeylessResearchError("Keyless provenance fields missing")
    if fmt not in {"documentario", "artvision_4x1", "storia_rivive", "giuliano", "wow_lab"}:
        raise KeylessResearchError("Unrecognized AI Director format")
    brief = make_brief(fmt, subject)
    notes = []
    for candidate in result.get("items", [])[:MAX_TOTAL_CANDIDATES]:
        if not isinstance(candidate, dict) or candidate.get("approved") is not False:
            continue
        url = candidate.get("source_url")
        if not isinstance(url, str) or not url.startswith("https://"):
            continue
        summary = (_safe_field(candidate.get("title"), 160) + " / " +
                   _safe_field(candidate.get("date"), 50)).strip(" /")
        notes.append({
            "url": url,
            "observation": "Catalog record (not fact-checked): " + summary,
            "license": "NOT VERIFIED — " + _safe_field(candidate.get("license_claim"), 200),
            "record_provider": candidate.get("provider"),
            "rights_review": "pending", "authenticity_review": "pending"
        })
    brief["source_notes"] = notes
    brief["research_candidates_only"] = True
    brief["rights_verified"] = False
    brief["assets_downloaded"] = False
    brief["research_source"] = "keyless_museum_archive_catalogues"
    return brief


def export_result(result, subject, fmt, output):
    target = Path(output)
    target.mkdir(parents=True, exist_ok=True)
    (target / "CANDIDATES.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    brief = director_from_candidates(result, subject, fmt=fmt)
    (target / "DIRECTOR_BRIEF.json").write_text(json.dumps(brief, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    problems = audit_scenes(brief)
    report = base_report(brief, problems, {"status": "not_checked"})
    report["archive_research"] = {
        "providers": result["providers"], "candidate_count": result["candidate_count"],
        "request_count_upper_bound": result["api_requests_upper_bound"],
        "key_required": False, "europeana_used": False
    }
    report["sources_verified"] = False
    report["rights_verified"] = False
    write_reports(target / "director", report, editorial_prompts(brief))
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description="AI Director keyless public archive scout")
    ap.add_argument("--category", choices=sorted(POLICY), default="general")
    ap.add_argument("--provider", choices=sorted(ALLOWED))
    ap.add_argument("--query", default="Venice 1896")
    ap.add_argument("--format", choices=("documentario", "artvision_4x1", "storia_rivive", "giuliano", "wow_lab"), default="storia_rivive")
    ap.add_argument("--per-provider", type=int, choices=(1, 2, 3), default=2)
    ap.add_argument("--execute", action="store_true", help="Only explicit manual usage sends keyless GET requests")
    ap.add_argument("--output", default="output/ai_director_archives_v1")
    args = ap.parse_args(argv)
    if args.execute:
        result = research(args.query, category=args.category, selected=args.provider,
                          per_provider=args.per_provider)
    else:
        result = {
            "schema": "ai-director-keyless-archives-v1", "category": args.category,
            "query": _valid_query(args.query), "status": "dry_run_no_api_calls",
            "providers": [], "api_requests_upper_bound": 0, "items": [],
            "candidate_count": 0, "key_required": False, "europeana_used": False,
            "external_ai_calls": 0, "paid_calls": False,
            "rights_verified": False, "media_downloaded": False,
            "human_approved": False, "publication_authorized": False
        }
    export_result(result, args.query, args.format, args.output)
    print(json.dumps({"status": result["status"], "candidate_count": result["candidate_count"],
                      "requests_upper_bound": result["api_requests_upper_bound"],
                      "europeana_used": False, "key_required": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
