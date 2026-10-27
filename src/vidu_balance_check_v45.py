#!/usr/bin/env python3
"""Read-only Vidu API credit probe. NEVER makes a billable generation request.

No API keys, balances, or account package details are written to disk/logs.
Only boolean 'can afford first planned clip' statuses are reported.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


ENDPOINT = "https://api.vidu.com/ent/v2/credits"


def available_credits(data: dict) -> int:
    """Return *conservative* credits without double-counting package summaries."""
    entries = data.get("remains")
    if entries is None:
        entries = data.get("remaining_credits")
    if not isinstance(entries, list):
        return 0
    # Multiple active package TYPES may coexist; the endpoint aggregates by type.
    values = []
    for item in entries:
        if not isinstance(item, dict):
            continue
        n = item.get("credit_remain")
        if type(n) in (int, float) and n >= 0:
            values.append(int(n))
    return sum(values)


def safe_summary(data: dict) -> dict:
    n = available_credits(data)
    return {
        "kind": "vidu_api_balance_check_no_spend",
        "api_key_recognized": True,
        "credits_for_5s_720p_offpeak": n >= 8,
        "credits_for_5s_720p_normal": n >= 16,
        "spent_credits_by_this_test": 0,
        "new_video_generated": False,
    }


def main() -> None:
    key = os.environ.get("VIDU_API_KEY", "")
    if not key:
        print(json.dumps({"api_key_recognized": False, "reason": "VIDU_API_KEY_missing",
                          "spent_credits_by_this_test": 0}))
        return
    req = urllib.request.Request(
        ENDPOINT, method="GET",
        headers={"Authorization": "Token " + key, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read(500_000))
        summary = safe_summary(data)
    except urllib.error.HTTPError as exc:
        # Never print response body or arbitrary server text, which might include PII.
        summary = {"api_key_recognized": False, "status": "HTTP_" + str(exc.code),
                   "spent_credits_by_this_test": 0}
    except (OSError, ValueError):
        summary = {"api_key_recognized": False, "status": "network_or_parse_error",
                   "spent_credits_by_this_test": 0}
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
