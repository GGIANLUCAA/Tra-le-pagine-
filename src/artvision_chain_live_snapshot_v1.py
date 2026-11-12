#!/usr/bin/env python3
"""Read-only GitHub Actions inventory for ArtVision. NOT a lock or a dispatcher.

This provides evidence for a human/CI review. Multiple GitHub API reads are not
atomic; they can NEVER authorize a render launch by themselves.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ACTIVE_STATUSES = (
    "queued", "in_progress", "waiting", "pending", "requested", "action_required",
)
MAX_PAGES_PER_STATUS = 5
PAGE_SIZE = 100
REPO = "GGIANLUCAA/Tra-le-pagine-"

# Actual owner source research is independent and does not hold a heavy render.
RESEARCH_ONLY_PATHS = frozenset({
    ".github/workflows/artvision-owner-source-research-v4.yml",
})


class SnapshotError(Exception):
    pass


def _path(run):
    raw = run.get("path", "")
    if not isinstance(raw, str):
        raise SnapshotError("run path is malformed")
    return raw.split("@", 1)[0]


def _is_possible_heavy(run):
    path = _path(run)
    name = run.get("name")
    if not isinstance(name, str):
        raise SnapshotError("run name is malformed")
    if path in RESEARCH_ONLY_PATHS:
        return False
    if path.startswith(".github/workflows/artvision-owner-"):
        return True
    # Conservative flag for parallel ArtVision render workflows outside the
    # single owner namespace. False positives cost time, not credits.
    return bool(name.casefold().startswith("artvision") and
                re.search(r"(render|cinema|museum|critico|production|produzione|4x1|4×1)",
                          name, re.IGNORECASE))


def collect_active_runs(fetch_page):
    """Validate a complete six-status inventory; abort on partial coverage."""
    all_runs = {}
    for requested_status in ACTIVE_STATUSES:
        expected_total = None
        collected = 0
        for page in range(1, MAX_PAGES_PER_STATUS + 1):
            response = fetch_page(requested_status, page)
            if not isinstance(response, dict):
                raise SnapshotError("malformed API payload")
            total = response.get("total_count")
            runs = response.get("workflow_runs")
            if type(total) is not int or total < 0 or not isinstance(runs, list):
                raise SnapshotError("API missing total_count or workflow_runs")
            if expected_total is None:
                expected_total = total
            # If the server's total changes while paging, fail closed.
            if total != expected_total:
                raise SnapshotError("live run inventory changed during pagination")
            if collected + len(runs) > expected_total:
                raise SnapshotError("API returned more runs than total_count")
            if not runs and collected != expected_total:
                raise SnapshotError("incomplete live run inventory")
            for run in runs:
                if not isinstance(run, dict) or type(run.get("id")) is not int:
                    raise SnapshotError("malformed workflow run ID")
                status = run.get("status")
                if status not in ACTIVE_STATUSES and status != "completed":
                    raise SnapshotError("unknown live run status")
                # Seen IDs are deduplicated across status transitions.
                all_runs[run["id"]] = run
            collected += len(runs)
            if collected == expected_total:
                break
        else:
            raise SnapshotError("live run inventory exceeds safe pagination cap")
    return list(all_runs.values())


def build_snapshot(fetch_page):
    runs = collect_active_runs(fetch_page)
    heavy = []
    for run in runs:
        if run["status"] not in ACTIVE_STATUSES:
            continue
        if _is_possible_heavy(run):
            heavy.append({
                "id": run["id"],
                "name": run["name"],
                "path": _path(run),
                "status": run["status"],
                "url": run.get("html_url", ""),
                "head_branch": run.get("head_branch", ""),
            })
    heavy.sort(key=lambda x: x["id"])
    return {
        "schema": "artvision-chain-live-snapshot-v1",
        "repo": REPO,
        "inventory_status": "complete_read_only_non_atomic",
        "active_run_statuses_checked": list(ACTIVE_STATUSES),
        "active_runs_observed": len(runs),
        "possible_heavy_runs": heavy,
        # May be used ONLY for a dry-run selector preview.
        "active_heavy_render": bool(heavy),
        "dispatch_authorized": False,
        "publication_authorized": False,
        "paid_api_calls": 0,
        "limitations": [
            "GitHub run enumeration is not an atomic lock",
            "Does not certify completed video/artifact, credits or human QA",
            "Cannot detect external renderers or unlisted workflow names",
            "Never start a render based only on this snapshot",
        ],
    }


def github_fetch_page(token, status, page, repo=REPO):
    if repo != REPO or status not in ACTIVE_STATUSES or not (1 <= page <= MAX_PAGES_PER_STATUS):
        raise SnapshotError("invalid GitHub inventory scope")
    url = ("https://api.github.com/repos/" + REPO +
           "/actions/runs?" + urllib.parse.urlencode({
               "status": status, "per_page": PAGE_SIZE, "page": page,
           }))
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "artvision-chain-readonly-v1",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            if res.status != 200:
                raise SnapshotError("GitHub returned non-200 response")
            return json.load(res)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        # No token or raw HTTP contents in reports/logs.
        raise SnapshotError("GitHub live inventory unavailable: " +
                            type(exc).__name__) from None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    token = os.environ.get("GITHUB_TOKEN", "")
    observed_repo = os.environ.get("GITHUB_REPOSITORY", "")
    try:
        if not token or observed_repo != REPO:
            raise SnapshotError("authenticated target repository not verified")
        report = build_snapshot(lambda status, page: github_fetch_page(token, status, page))
    except (SnapshotError, ValueError, KeyError, TypeError) as exc:
        report = {
            "schema": "artvision-chain-live-snapshot-v1",
            "repo": REPO,
            "inventory_status": "unknown_fail_closed",
            "active_heavy_render": None,
            "dispatch_authorized": False,
            "publication_authorized": False,
            "error": str(exc),
        }
        success = False
    else:
        success = True
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Live ArtVision inventory:", report["inventory_status"],
          "| possible heavy runs:", len(report.get("possible_heavy_runs", [])))
    if not success:
        sys.exit(2)


if __name__ == "__main__":
    main()
