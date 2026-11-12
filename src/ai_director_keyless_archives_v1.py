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
import unicodedata

from ai_director_v1 import audit_scenes, base_report, editorial_prompts, make_brief, write_reports
from public_archive_sources_v2 import search as search_public

ROOT = Path(__file__).resolve().parents[1]
POLICY = {
    "art": ("artic", "met", "cleveland", "commons"),
    "historical_video": ("loc", "archive", "commons"),
    "historical_photo": ("loc", "commons", "wellcome"),
    "general": ("loc", "artic", "commons"),
}
ALLOWED = frozenset(p for group in POLICY.values() for p in group)
MAX_TOTAL_CANDIDATES = 9
MAX_REQUESTS = 12
STOPWORDS = frozenset({
    "the", "a", "an", "and", "or", "of", "in", "at", "for", "from", "by",
    "with", "to", "on", "la", "il", "lo", "gli", "le", "di", "del",
    "della", "da", "una", "un", "e", "artwork", "painting",
    "historical", "historic", "movie", "film", "footage", "video",
    "photograph", "photo", "image"
})


def _keywords(value):
    if not isinstance(value, str):
        return []
    folded = "".join(c for c in unicodedata.normalize("NFKD", value.casefold())
                     if not unicodedata.combining(c))
    return [t for t in re.findall(r"[a-z0-9]+", folded)
            if (len(t) >= 3 or t.isdecimal()) and t not in STOPWORDS]


def _source_relevance(query, candidate, *, category, artist=""):
    """Strict catalogue text match, not an authenticity or artistic judgement."""
    words = list(dict.fromkeys(_keywords(query)))
    if not words:
        raise KeylessResearchError("No meaningful terms in the search query")
    title = _keywords(candidate.get("title", ""))
    author = _keywords(candidate.get("author", ""))
    date = _keywords(candidate.get("date", ""))
    artist_words = list(dict.fromkeys(_keywords(artist)))
    if artist_words and category != "art":
        raise KeylessResearchError("Artist filter is only supported for artwork")
    if artist_words and not all(t in author for t in artist_words):
        return False, "artist_name_not_matched", []
    title_terms = [t for t in words if t not in artist_words]
    actual = set(title + author + date)
    found = [term for term in title_terms if term in actual]
    if title_terms and len(found) != len(title_terms):
        return False, "query_terms_not_matched", found
    return True, "metadata_text_match_unverified", found




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


def _curated_alias(query, artist):
    """Exact title+creator match only: no fuzzy guesses, no scraped claims."""
    cfg = ROOT / "config/ai_director_curated_source_aliases_v1.json"
    if not cfg.is_file() or cfg.stat().st_size > 20_000:
        raise KeylessResearchError("Curated aliases config missing/oversized")
    try:
        data = json.loads(cfg.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        raise KeylessResearchError("Curated aliases invalid") from None
    if data.get("schema") != "ai-director-curated-source-aliases-v1" or not isinstance(data.get("entries"), list):
        raise KeylessResearchError("Curated aliases format invalid")
    query_words = _keywords(query)
    artist_words = _keywords(artist)
    for entry in data["entries"][:30]:
        if not isinstance(entry, dict) or not artist_words:
            continue
        if _keywords(entry.get("canonical_title")) != query_words:
            continue
        if _keywords(entry.get("artist")) != artist_words:
            continue
        # Only previously reviewed primary-museum provenance, no API keys.
        if entry.get("fallback_provider") != "commons":
            continue
        if not str(entry.get("reference_url", "")).startswith("https://www.mauritshuis.nl/"):
            continue
        if entry.get("publication_authorized") is not False:
            continue
        alias = _valid_query(entry.get("fallback_search"))
        if not _keywords(alias):
            continue
        return entry, alias
    return None


def research(query, *, category="general", selected=None, per_provider=2, artist="", fetcher=None):
    """User-initiated, up to four keyless sources. No media is retrieved."""
    query = _valid_query(query)
    if type(per_provider) is not int or not 1 <= per_provider <= 3:
        raise KeylessResearchError("Per-provider limit must be 1..3")
    if artist and (category != "art" or not _keywords(artist)):
        raise KeylessResearchError("Artist name filter applies only to art and needs real terms")
    if not _keywords(query):
        raise KeylessResearchError("Search query has no meaningful terms")
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
            excluded_by_relevance = 0
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
                matched, explanation, matched_terms = _source_relevance(
                    query, candidate, category=category, artist=artist)
                if not matched:
                    excluded_by_relevance += 1
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
                    "approved": False, "downloaded": False,
                    "text_relevance": explanation, "matched_query_terms": matched_terms,
                    "artist_filter_requested": bool(artist)
                })
                inserted += 1
                if len(items) >= MAX_TOTAL_CANDIDATES:
                    break
            provider_reports.append({"provider": provider, "status": "response_received",
                                     "added_candidates": inserted,
                                     "excluded_by_media_kind": excluded_by_media_kind,
                                     "excluded_by_relevance": excluded_by_relevance,
                                     "api_requests": calls})
        except (ValueError, TypeError, KeyError, OSError) as exc:
            # Never reflect source response, user credentials or URL into logs.
            provider_reports.append({"provider": provider, "status": "provider_unavailable_or_invalid"})
            total_calls += planned_max  # conservative estimate when an exception hides partial requests
    # One documented translation/filename recovery, only if exact artwork AND
    # creator were specified and the ordinary source scout has no candidates.
    # Do not expand arbitrary historical queries or retry providers on HTTP errors.
    if category == "art" and artist and not selected and not items and total_calls + 1 <= MAX_REQUESTS:
        fallback = _curated_alias(query, artist)
        if fallback:
            entry, alias_query = fallback
            provider = entry["fallback_provider"]
            try:
                response = search_public(provider, alias_query, limit=3, fetcher=fetcher)
                calls = response.get("api_requests")
                if type(calls) is not int or calls != 1:
                    raise KeylessResearchError("Unexpected alias query request count")
                total_calls += calls
                candidates = response.get("items")
                if not isinstance(candidates, list):
                    raise KeylessResearchError("Invalid alias response")
                chosen = 0
                for candidate in candidates[:3]:
                    if not isinstance(candidate, dict) or candidate.get("media_kind") != "image":
                        continue
                    passed, reason, words = _source_relevance(
                        alias_query, candidate, category="art", artist=artist)
                    url = candidate.get("source_url")
                    if not passed or not isinstance(url, str) or not url.startswith("https://") or url in seen:
                        continue
                    seen.add(url)
                    items.append({
                        "provider": provider,
                        "id": _safe_field(candidate.get("id")),
                        "title": _safe_field(candidate.get("title")),
                        "author": _safe_field(candidate.get("author")),
                        "date": _safe_field(candidate.get("date"), 80),
                        "media_kind": "image", "source_url": url[:1200],
                        "preview": _safe_field(candidate.get("preview"), 1200),
                        "license_claim": _safe_field(candidate.get("license_claim"), 320),
                        "rights_review": "pending", "authenticity_review": "pending",
                        "scene_relevance": "pending", "source_verified": False,
                        "approved": False, "downloaded": False,
                        "text_relevance": "curated_filename_alias_match_unverified",
                        "matched_query_terms": words,
                        "artist_filter_requested": True,
                        "curated_work_reference": entry["reference_url"],
                        "curated_source_id": entry["id"],
                        "alias_used": alias_query,
                        "canonical_title_requested": query
                    })
                    chosen += 1
                provider_reports.append({"provider": provider,
                                         "status": "curated_alias_response",
                                         "added_candidates": chosen,
                                         "api_requests": calls,
                                         "alias_source_id": entry["id"]})
            except (ValueError, TypeError, KeyError, OSError):
                total_calls += 1  # pessimistic bound after a failed single request
                provider_reports.append({"provider": provider, "status": "curated_alias_unavailable",
                                         "alias_source_id": entry["id"]})
    status = "candidates_need_review" if items else "no_candidates_or_sources_unavailable"
    return {
        "schema": "ai-director-keyless-archives-v1", "category": category,
        "query": query, "artist_filter": artist, "status": status, "providers": provider_reports,
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
    ap.add_argument("--artist", default="", help="Optional exact-creator metadata filter for art")
    ap.add_argument("--execute", action="store_true", help="Only explicit manual usage sends keyless GET requests")
    ap.add_argument("--output", default="output/ai_director_archives_v1")
    args = ap.parse_args(argv)
    if args.execute:
        result = research(args.query, category=args.category, selected=args.provider,
                          per_provider=args.per_provider, artist=args.artist)
    else:
        if args.artist and args.category != "art":
            raise KeylessResearchError("Artist requires art category")
        result = {
            "schema": "ai-director-keyless-archives-v1", "category": args.category,
            "query": _valid_query(args.query), "artist_filter": args.artist,
            "status": "dry_run_no_api_calls",
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
