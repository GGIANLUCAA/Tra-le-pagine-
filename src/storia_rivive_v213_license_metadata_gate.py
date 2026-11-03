#!/usr/bin/env python3
"""V213: compare V101 candidate license claims with actual Commons file metadata.

A matching Commons short license label is NOT a legal opinion, territorial
clearance, verification of the film's authors, or permission to use AI/Vidu.
This is a no-network, no-cost, fail-closed research gate before I2I planning.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

STATUS_OK = "SOURCE_LICENSE_CLAIM_MATCHED_RIGHTS_REVIEW_PENDING"
STATUS_BLOCKED = "SOURCE_LICENSE_METADATA_BLOCKED"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
CC0_LABELS = {"CC0", "CC0 1.0", "CC0 1.0 Universal"}
PUBLIC_DOMAIN_LABELS = {"Public domain", "Public Domain", "PDM", "Public Domain Mark 1.0"}


def inspect(order: dict, scout: dict, verified_cache: dict) -> dict:
    report = {
        "version": "V213_SOURCE_LICENSE_METADATA_GATE",
        "status": STATUS_BLOCKED,
        "reason": "UNKNOWN",
        "claim_consistent_with_current_commons_metadata": False,
        "research_ready": False,
        "italian_rights_approved": False,
        "underlying_film_rights_verified": False,
        "human_legal_review_completed": False,
        "provider_calls_permitted": False,
        "publish_permitted": False,
        "credits_spent": 0,
    }

    def block(reason: str) -> dict:
        report["reason"] = reason
        return report

    if not all(isinstance(x, dict) for x in (order, scout, verified_cache)):
        return block("INVALID_INPUT_SCHEMA")
    if (order.get("contract") != "LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT"
            or order.get("paid_api_call_permitted") is not False
            or order.get("publish_permitted") is not False):
        return block("INVALID_OR_UNSAFE_WORK_ORDER")
    if (verified_cache.get("ready") is not True
            or verified_cache.get("status") != "REAL_BW_FILM_FRAMES_VERIFIED_FOR_RESEARCH_ONLY"):
        return block("V196_SOURCE_BYTES_NOT_VERIFIED")
    source_page = order.get("source_page")
    if not isinstance(source_page, str) or not source_page:
        return block("INVALID_SOURCE_PAGE")
    url = urlparse(source_page)
    if (url.scheme != "https" or url.netloc != "commons.wikimedia.org"
            or not url.path.startswith("/wiki/File:")):
        return block("SOURCE_NOT_COMMONS_FILE_PAGE")
    if scout.get("source_page") != source_page:
        return block("SCOUT_SOURCE_PAGE_MISMATCH")
    expected_sha = verified_cache.get("original_film_sha256")
    if (not isinstance(expected_sha, str) or not SHA256.fullmatch(expected_sha)
            or scout.get("original_sha256") != expected_sha):
        return block("SOURCE_FILM_SHA_BINDING_MISMATCH")
    if (scout.get("historical_rights_italy_approved") is not False
            or scout.get("social_publish_permitted") is not False):
        return block("SCOUT_CLAIMS_UNSUPPORTED_RIGHTS_OR_PUBLICATION")
    claim = order.get("source_license_claim")
    actual = scout.get("license_metadata")
    if not isinstance(actual, str) or not 1 <= len(actual) <= 100:
        return block("MISSING_OR_INVALID_COMMONS_LICENSE_METADATA")
    if not isinstance(claim, str):
        return block("INVALID_SOURCE_LICENSE_CLAIM")
    if claim in ("CC0", "CC0_as_declared"):
        matched = actual.strip() in CC0_LABELS
    elif claim in ("PUBLIC_DOMAIN", "PDM"):
        matched = actual.strip() in PUBLIC_DOMAIN_LABELS
    else:
        return block("UNSUPPORTED_SOURCE_LICENSE_CLAIM")
    if not matched:
        # Do not print the raw Commons label (it can be arbitrary HTML/text).
        return block("CANDIDATE_LICENSE_CLAIM_DIFFERS_FROM_COMMONS")
    report.update({
        "status": STATUS_OK,
        "reason": "COMMONS_LABEL_MATCH_ONLY; ITALIAN_RIGHTS_AND_UNDERLYING_FILM_REVIEW_REQUIRED",
        "claim_consistent_with_current_commons_metadata": True,
        "research_ready": True,
        "source_film_sha256": expected_sha,
        "source_page": source_page,
        "license_claim": claim,
        "license_label_checked": actual.strip(),
    })
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    for field in ("order", "scout", "v196", "out"):
        parser.add_argument("--" + field, required=True)
    args = parser.parse_args()
    try:
        data = inspect(json.loads(Path(args.order).read_text(encoding="utf-8")),
                       json.loads(Path(args.scout).read_text(encoding="utf-8")),
                       json.loads(Path(args.v196).read_text(encoding="utf-8")))
    except (OSError, UnicodeError, ValueError, TypeError):
        data = {"version": "V213_SOURCE_LICENSE_METADATA_GATE",
                "status": STATUS_BLOCKED, "reason": "MISSING_OR_INVALID_INPUT",
                "research_ready": False, "italian_rights_approved": False,
                "provider_calls_permitted": False, "publish_permitted": False,
                "credits_spent": 0}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(data["status"], data["reason"])


if __name__ == "__main__":
    main()
