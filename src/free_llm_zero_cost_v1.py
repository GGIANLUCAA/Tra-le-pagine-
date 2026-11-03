#!/usr/bin/env python3
"""Fail-closed zero-cost admission check for optional FreeLLMAPI editorial calls.

This verifies configured evidence BEFORE a request. It cannot verify an upstream
provider's actual billing state; users must keep upstream paid models disabled.
Never treat router-side fallback or a free model name as a billing guarantee.
"""
from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

SCHEMA = "free-llm-zero-cost-v1"
DEFAULT_POLICY = Path(__file__).resolve().parents[1] / "config/free_llm_zero_cost_v1.json"
MODEL_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._:/+-]{1,140}$")


class ZeroCostPolicyError(ValueError):
    pass


def load_policy(path: str | Path = DEFAULT_POLICY) -> dict:
    p = Path(path)
    if p.stat().st_size > 262_144:
        raise ZeroCostPolicyError("Cost policy exceeds safe size")
    value = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ZeroCostPolicyError("Cost policy must be an object")
    return value


def admit(model: str, policy: dict, today: dt.date | None = None) -> dict:
    """Return one verified candidate; reject unknown costs, missing ToS, stale proof."""
    now = today or dt.datetime.now(dt.timezone.utc).date()
    if not isinstance(policy, dict) or policy.get("schema") != SCHEMA:
        raise ZeroCostPolicyError("Missing supported cost-policy schema")
    if policy.get("default_deny") is not True:
        raise ZeroCostPolicyError("default_deny must be true")
    days = policy.get("max_evidence_age_days")
    if type(days) is not int or not 1 <= days <= 14:
        raise ZeroCostPolicyError("Evidence maximum age must be 1..14 days")
    routes = policy.get("routes")
    if not isinstance(routes, list):
        raise ZeroCostPolicyError("Cost policy routes must be an array")
    if not isinstance(model, str) or not MODEL_RE.fullmatch(model):
        raise ZeroCostPolicyError("Invalid model identifier")
    if model.lower() in {"auto", "fusion"} or model.lower().startswith("auto:"):
        raise ZeroCostPolicyError("Implicit model selection/fusion is forbidden by zero-cost policy")

    matches = [r for r in routes if isinstance(r, dict) and r.get("model") == model]
    if len(matches) != 1:
        raise ZeroCostPolicyError("Model not explicitly approved as zero-cost")
    r = matches[0]
    if r.get("enabled") is not True:
        raise ZeroCostPolicyError("Model disabled")
    if any(r.get(field) is not True for field in (
        "free_plan_verified", "commercial_use_terms_checked",
        "commercial_use_permitted", "billing_disabled_verified",
        "free_only_fallback_verified", "no_promo_credit_dependency",
    )):
        raise ZeroCostPolicyError("Free/terms/billing/fallback attestations missing")
    for name in ("input_usd_per_million", "output_usd_per_million"):
        value = r.get(name)
        if type(value) not in (int, float) or value != 0:
            raise ZeroCostPolicyError("Cost not exactly zero: " + name)
    provider = r.get("provider")
    if not isinstance(provider, str) or not re.fullmatch("[a-z][a-z0-9_-]{1,48}", provider):
        raise ZeroCostPolicyError("Provider identifier missing")
    doc = r.get("official_evidence_url", "")
    parsed = urlsplit(doc) if isinstance(doc, str) else None
    if not parsed or parsed.scheme != "https" or not parsed.hostname or not parsed.path:
        raise ZeroCostPolicyError("Official HTTPS pricing/ToS evidence URL required")
    try:
        verified = dt.date.fromisoformat(r["verified_on"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ZeroCostPolicyError("Fresh verification date required") from exc
    if not (dt.timedelta(0) <= now - verified <= dt.timedelta(days=days)):
        raise ZeroCostPolicyError("Verification missing, stale or future-dated")
    # No automatic credential creation, uploads or billing operations.
    return r


def route_matches_actual(route: dict, routed_via: str, fallback_attempts: str | None) -> bool:
    """A POST-CALL alarm; routing headers cannot stop earlier upstream billing."""
    if not routed_via or routed_via == "unknown":
        return False
    # Header is documented as platform/model (model portion may include slash).
    expected = route["provider"] + "/" + route["model"]
    if routed_via != expected:
        return False
    try:
        attempts = int(fallback_attempts or "0")
    except (TypeError, ValueError):
        return False
    return attempts == 0


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", default=str(DEFAULT_POLICY))
    parser.add_argument("--model", default="auto")
    opts = parser.parse_args()
    admit(opts.model, load_policy(opts.policy))
    print("ZERO_COST_POLICY_ADMITTED (attestation only, not provider billing guarantee)")


if __name__ == "__main__":
    main()
