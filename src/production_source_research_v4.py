#!/usr/bin/env python3
"""V4 scheduled source research companion for the existing ArtVision/Story owners.

Never changes a production queue, supplies approved assets, downloads media,
renders video, spends paid credits, or publishes. One bounded source query
per real scheduled research cycle, with full provenance and honest failure.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re

import public_archive_sources_v2 as archive
import rare_research_sources_v3 as rare

ALLOWED = {
    "artvision": (archive.ART | {"commons", "rijks", "finna"}),
    "storia": (archive.ARCHIVE | {"finna"}),
}
STATUS_PENDING = ("rights_review", "authenticity_review", "visual_review", "scene_relevance")

class CycleResearchError(ValueError):
    pass

def utc_slot(value: str) -> dt.datetime:
    try:
        x = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        raise CycleResearchError("Invalid cycle timestamp") from None
    if x.tzinfo is None:
        raise CycleResearchError("Timezone required")
    x = x.astimezone(dt.timezone.utc)
    return x.replace(hour=(x.hour // 3) * 3, minute=0, second=0, microsecond=0)

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def config_checked(conf):
    if conf.get("schema") != "source-cycle-companion-v4":
        raise CycleResearchError("Unknown research contract")
    if conf.get("paid_calls_allowed") is not False or conf.get("auto_publish") is not False:
        raise CycleResearchError("Unexpected spending/publication permission")
    if conf.get("max_results_per_cycle") != 1 or conf.get("max_api_calls_per_cycle") != 2:
        raise CycleResearchError("Cycle request budget must remain bounded")
    for project in ("artvision", "storia"):
        entries = conf.get(project)
        if not isinstance(entries, dict) or not entries:
            raise CycleResearchError("Missing source research entries for " + project)
        for ident, entry in entries.items():
            if not re.fullmatch(r"[a-z0-9_]{6,100}", ident):
                raise CycleResearchError("Invalid editorial ID")
            provider = entry.get("provider")
            query = entry.get("query")
            if provider not in ALLOWED[project]:
                raise CycleResearchError("Provider is not permitted for project " + project)
            if not isinstance(query, str) or not 3 <= len(query.strip()) <= 120 or re.search(r"[\x00-\x1f\x7f]", query):
                raise CycleResearchError("Unsafe research query for " + ident)
    return conf

def artvision_target(queue, conf, slot):
    if queue.get("schema") != "artvision-owner-selected-ten-v128":
        raise CycleResearchError("Unknown ArtVision owner queue")
    if queue.get("owner_automation_id") != "6adca191603c8191a90d5190901cd034":
        raise CycleResearchError("ArtVision owner task mismatch")
    works = queue.get("works")
    if not isinstance(works, list) or len(works) != 10:
        raise CycleResearchError("ArtVision owner queue should contain 10 works")
    ids = [x.get("id") for x in works if isinstance(x, dict)]
    if len(set(ids)) != 10:
        raise CycleResearchError("Duplicate or invalid ArtVision work IDs")
    eligible = [w for w in works if w.get("preflight_status") != "rights_blocked_no_render_no_distribution"]
    if set(x["id"] for x in eligible) != set(conf["artvision"]):
        raise CycleResearchError("ArtVision research mapping needs owner queue review")
    if not eligible:
        raise CycleResearchError("No eligible ArtVision sources")
    work = eligible[(int(slot.timestamp()) // 10800) % len(eligible)]
    return {
        "item_id": work["id"],
        "subject": work.get("title_en"),
        "artist": work.get("artist"),
        "official_source_page": work.get("official_object_url"),
        "source_unchanged": True,
        "ownership": "ARTVISION_OWNER_SELECTED_TEN_V128",
    }

def storia_target(order, conf, slot):
    if order.get("contract") != "LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT":
        raise CycleResearchError("V101 work order required")
    ident = order.get("episode_id")
    if not isinstance(ident, str) or ident not in conf["storia"]:
        raise CycleResearchError("Unknown Story candidate: do not fall back to other episode")
    cycle = order.get("cycle_id")
    if cycle != "storia-" + slot.strftime("%Y%m%d-%H%M"):
        raise CycleResearchError("Story research order cycle does not match current slot")
    return {
        "item_id": ident,
        "subject": order.get("subject"),
        "artist": None,
        "official_source_page": order.get("source_page"),
        "source_unchanged": True,
        "ownership": "STORIA_RIVIVE_V101_SOURCE_ORDER",
    }

def plan(project, now, conf, queue=None, order=None):
    conf = config_checked(conf)
    if project not in ALLOWED:
        raise CycleResearchError("Project not supported")
    slot = utc_slot(now)
    if project == "artvision":
        if not isinstance(queue, dict):
            raise CycleResearchError("ArtVision selected-ten queue required")
        target = artvision_target(queue, conf, slot)
    else:
        if not isinstance(order, dict):
            raise CycleResearchError("Real V101 work order required")
        target = storia_target(order, conf, slot)
    spec = conf[project][target["item_id"]]
    provider, query = spec["provider"], spec["query"]
    signature = "\n".join([project, slot.isoformat(), target["item_id"], provider, query])
    return {
        "schema": "source-cycle-companion-v4",
        "project": project,
        "cycle_utc": slot.isoformat(),
        "cycle_id": slot.strftime("%Y%m%dT%H%MZ"),
        "request_sha256": hashlib.sha256(signature.encode("utf-8")).hexdigest(),
        "provider": provider,
        "query": query,
        "item_id": target["item_id"],
        "subject": target["subject"],
        "artist": target["artist"],
        "official_source_page": target["official_source_page"],
        "owner": target["ownership"],
        "source_unchanged": True,
        "request_budget": {"searches": 1, "max_results": 1, "max_provider_requests": 2},
        "rights_checked": False,
        "auto_download": False, "auto_render": False, "auto_publish": False,
        "approved_assets": 0, "paid_api_calls": 0,
        "status": "PLANNED_NOT_QUERIED",
        "candidates": [],
    }

def execute(plan_data, fetchers=None):
    out = dict(plan_data)
    if out.get("schema") != "source-cycle-companion-v4":
        raise CycleResearchError("Unknown plan")
    if out.get("status") != "PLANNED_NOT_QUERIED":
        raise CycleResearchError("Plan already consumed")
    provider = out["provider"]
    if provider not in ALLOWED[out["project"]]:
        raise CycleResearchError("Forbidden provider")
    fetchers = fetchers or {}
    out["status"] = "API_FAILED_NO_RETRY"
    out["api_requests"] = 0
    out["candidates"] = []
    try:
        if provider in rare.PROVIDERS:
            result = rare.search(provider, out["query"], 1, fetchers.get(provider))
        else:
            result = archive.search(provider, out["query"], 1, fetchers.get(provider))
        if result.get("api_requests", 0) > out["request_budget"]["max_provider_requests"]:
            raise CycleResearchError("API request budget exceeded")
        records = result.get("items") or []
        if len(records) > 1:
            raise CycleResearchError("More candidates than permitted")
        normalized = []
        for item in records:
            if not isinstance(item, dict) or not item.get("source_reference"):
                continue
            row = dict(item)
            for field in STATUS_PENDING:
                row[field] = "pending"
            row["selected"] = False
            row["approved"] = False
            row["review_required"] = True
            normalized.append(row)
        out["candidates"] = normalized
        out["api_requests"] = result["api_requests"]
        out["status"] = "RESEARCH_CANDIDATES_PENDING_REVIEW" if normalized else "NO_MATCH"
    except (archive.old.ResearchError, rare.ResearchError, CycleResearchError,
            OSError, ValueError) as exc:
        out["error_type"] = type(exc).__name__
        out["error_note"] = str(exc)[:160]
    return out

def save_report(path, report):
    dst = Path(path)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def main():
    p = argparse.ArgumentParser(description="Production-adjacent source research, no media or spending")
    p.add_argument("--project", required=True, choices=sorted(ALLOWED))
    p.add_argument("--now", required=True)
    p.add_argument("--config", default="config/source_cycle_companion_v4.json")
    p.add_argument("--artvision-queue", default="queue/artvision_owner_selected_ten_20261102.json")
    p.add_argument("--storia-order", default="output/storia_v101/WORK_ORDER.json")
    p.add_argument("--out", required=True)
    a = p.parse_args()
    conf = load_json(a.config)
    queue = load_json(a.artvision_queue) if a.project == "artvision" else None
    order = load_json(a.storia_order) if a.project == "storia" else None
    report = execute(plan(a.project, a.now, conf, queue, order))
    save_report(a.out, report)
    print(json.dumps({
        "cycle": report["cycle_id"], "project": report["project"],
        "provider": report["provider"], "status": report["status"],
        "candidates": len(report["candidates"]), "paid_api_calls": 0,
        "rendered": False, "published": False,
    }))

if __name__ == "__main__":
    main()
