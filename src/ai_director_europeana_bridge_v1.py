#!/usr/bin/env python3
"""Read-only Europeana candidates -> existing AI Director editorial brief.

No media imported, no rights assumed, no video or OpenRouter calls.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_director_v1 import make_brief, audit_scenes, base_report, editorial_prompts, write_reports


def prepare(catalogue, subject):
    if not isinstance(catalogue, dict) or catalogue.get("schema") != "ai-director-europeana-research-v1":
        raise ValueError("Verified Europeana catalogue JSON expected, not arbitrary content")
    if catalogue.get("provider") != "europeana" or catalogue.get("api_requests") != 1:
        raise ValueError("Original public research request evidence missing")
    brief = make_brief("documentario", subject)
    sources = []
    for item in catalogue.get("items", [])[:8]:
        if not isinstance(item, dict):
            continue
        url = item.get("source_url")
        if not isinstance(url, str) or not url.startswith("https://"):
            continue
        title = item.get("title") or item.get("id") or ""
        date = item.get("date") or ""
        claim = item.get("rights_claim") or "Source rights not documented"
        # These are search-result metadata, not verified historical evidence.
        sources.append({
            "url": url, "observation": (str(title)[:170] + " · " + str(date)[:35]),
            "license": "UNVERIFIED (catalogue claim: " + str(claim)[:190] + ")",
            "source_type": "europeana_search_metadata_not_primary_source",
            "rights_review": "pending", "authenticity_review": "pending"
        })
    brief["source_notes"] = sources
    brief["research_candidates_only"] = True
    brief["media_assets_downloaded"] = False
    brief["historical_facts_verified"] = False
    return brief


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--subject", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--report-dir", type=Path, required=True)
    args = p.parse_args(argv)
    if not args.input.is_file() or args.input.stat().st_size > 200_000:
        raise ValueError("Catalogue file missing or too large")
    catalogue = json.loads(args.input.read_text(encoding="utf-8"))
    brief = prepare(catalogue, args.subject)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(brief, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    issues = audit_scenes(brief)
    report = base_report(brief, issues, {"status": "not_checked"})
    report["europeana_candidate_count"] = len(brief["source_notes"])
    report["media_assets_downloaded"] = False
    report["source_notes_are_unverified"] = True
    write_reports(args.report_dir, report, editorial_prompts(brief))
    print("EUROPEANA_TO_DIRECTOR_DRAFT", len(brief["source_notes"]), "no api inference")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
