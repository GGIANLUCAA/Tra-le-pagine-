#!/usr/bin/env python3
"""Read-only free-provider discovery from Free LLM API Hub.

Never creates accounts, accesses provider APIs, configures billing, or enables
FreeLLMAPI routes. Upstream is an advisory catalog, not an authorization source.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from urllib import request, error
from urllib.parse import urlsplit

SOURCE = "https://raw.githubusercontent.com/pacocartones/free-llm-api-hub/main/data/providers.json"
MAX_BYTES = 4_000_000
MAX_AGE_DAYS = 45
TARGETS = {
    "groq": "rapid_inference_and_whisper",
    "openrouter": "rotating_free_language_models",
    "cloudflare-workers-ai": "serverless_free_daily_allowance",
    "z-ai": "glm_free_text_and_vision",
    "google-gemini": "editorial_language_and_vision_check_terms_for_EEA",
}


class CatalogError(ValueError):
    pass


def date_from_iso(value: object) -> dt.date:
    if not isinstance(value, str):
        raise CatalogError("Expected YYYY-MM-DD date")
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise CatalogError("Invalid verification date") from exc


def is_fresh(value: object, now: dt.date, max_age_days: int = MAX_AGE_DAYS) -> bool:
    try:
        age = (now - date_from_iso(value)).days
        return 0 <= age <= max_age_days
    except CatalogError:
        return False


def review_snapshot(data: dict, today: dt.date | None = None) -> dict:
    now = today or dt.datetime.now(dt.timezone.utc).date()
    if not isinstance(data, dict) or not isinstance(data.get("providers"), list):
        raise CatalogError("Malformed Hub dataset")
    if len(data["providers"]) > 1000:
        raise CatalogError("Unexpectedly large provider collection")
    if not is_fresh(data.get("generated"), now):
        raise CatalogError("Hub dataset build is missing, future-dated or stale")
    identified = {}
    for item in data["providers"]:
        if not isinstance(item, dict):
            continue
        slug = item.get("slug")
        if slug in TARGETS:
            if slug in identified:
                raise CatalogError("Duplicate provider slug: " + slug)
            identified[slug] = item
    candidates = []
    for slug, goal in TARGETS.items():
        p = identified.get(slug)
        if p is None:
            candidates.append({
                "provider": slug, "goal": goal, "status": "unavailable_in_catalog",
                "may_call_api": False,
            })
            continue
        docs = p.get("docs_url")
        parsed = urlsplit(docs) if isinstance(docs, str) else None
        linked = (bool(parsed and parsed.scheme == "https" and parsed.hostname
                       and parsed.hostname not in {"localhost", "127.0.0.1"}))
        checked = (
            p.get("verified") is True
            and is_fresh(p.get("last_verified"), now)
            and p.get("category") == "ongoing"
            and p.get("free_type") in ("perpetual", "renewing-quota")
            and p.get("card_required") is False
            and p.get("commercial_ok") is True
            and p.get("is_text_llm") is True
            and linked
        )
        candidates.append({
            "provider": slug,
            "goal": goal,
            "status": "candidate_manual_review" if checked else "hold_reverification_needed",
            "may_call_api": False,
            "needs_account_configuration": True,
            "requires_phone": p.get("phone_required"),
            "source_verified": p.get("verified") is True,
            "last_verified": p.get("last_verified"),
            "official_documentation": docs if linked else None,
            "free_type": p.get("free_type"),
            "modality_hints": [m for m in (p.get("modalities") or []) if m in
                              {"text", "vision", "audio", "image", "embeddings"}],
            "sample_models_unverified": [
                m for m in (p.get("models_free") or [])[:5] if isinstance(m, str)
            ],
            "notes": str(p.get("notes") or "")[:420],
        })
    return {
        "schema": "studio-ai-free-discovery-v2",
        "status": "read_only_no_providers_enabled",
        "dataset_version": str(data.get("version") or "unknown"),
        "dataset_generated": data.get("generated"),
        "snapshot_reviewed_on": now.isoformat(),
        "candidates": candidates,
        "local_options": [
            {"engine": x, "status": "requires_own_hardware",
             "monetary_api_cost": "none_for_local_inference_only",
             "note": "Hardware, electricity, model licenses and downloads still apply."}
            for x in ("Ollama", "llama.cpp", "LocalAI")
        ],
        "router_decision": "FreeLLMAPI_only; avoid duplicate LiteLLM/Portkey/ZeroSpend routers",
        "automatic_provider_activation": False,
        "commercial_terms_approved": False,
        "billing_state_verified": False,
        "provider_calls_performed": 0,
    }


def fetch_catalog(*, opener=None) -> dict:
    transport = opener or request.urlopen
    req = request.Request(SOURCE, headers={"User-Agent": "StudioFreeAIAudit/2.0"})
    try:
        with transport(req, timeout=20) as response:
            raw = response.read(MAX_BYTES + 1)
    except (OSError, error.URLError, TimeoutError) as exc:
        raise CatalogError("Could not retrieve public Hub data") from exc
    if len(raw) > MAX_BYTES:
        raise CatalogError("Hub response exceeds size limit")
    try:
        return json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise CatalogError("Hub response is not valid JSON") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, help="Offline JSON snapshot; no network")
    parser.add_argument("--refresh", action="store_true",
                        help="Read only the public Hub dataset from GitHub")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if bool(args.snapshot) == bool(args.refresh):
        parser.error("Select exactly one of --snapshot or --refresh")
    data = json.loads(args.snapshot.read_text(encoding="utf-8")) if args.snapshot else fetch_catalog()
    result = review_snapshot(data)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print("READ_ONLY_DISCOVERY", len(result["candidates"]),
          "providers; enabled 0; provider API calls 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
