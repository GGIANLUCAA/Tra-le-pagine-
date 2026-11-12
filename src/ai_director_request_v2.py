#!/usr/bin/env python3
"""Parse a single GitHub-committed, explicitly free AI Director V2 review request.

No GitHub API dispatch, no shell execution, no media generation.
A push event can only select the exact JSON added/changed in that commit.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import subprocess
from pathlib import Path

FORMATS = {"giuliano", "artvision_4x1", "storia_rivive", "wow_lab", "documentario"}
PATH = re.compile(r"requests/ai_director_v2/[a-z0-9][a-z0-9_-]{0,69}\.json\Z")
ARTIFACT = re.compile(r"[A-Za-z0-9_.-]{1,160}\Z")


def validate_request(obj):
    if not isinstance(obj, dict) or set(obj) != {
            "schema", "producer_run_id", "video_format", "artifact_name",
            "publish", "external_paid_calls"}:
        raise ValueError("Invalid request fields")
    if obj["schema"] != "ai-director-review-request-v1":
        raise ValueError("Wrong schema")
    if type(obj["producer_run_id"]) is not int or not 1 <= obj["producer_run_id"] <= 999999999999:
        raise ValueError("Invalid producer run id")
    if obj["video_format"] not in FORMATS:
        raise ValueError("Unknown review format")
    if not isinstance(obj["artifact_name"], str) or not ARTIFACT.fullmatch(obj["artifact_name"]):
        raise ValueError("Exact artifact name required for requested replay")
    if obj["publish"] is not False or obj["external_paid_calls"] is not False:
        raise ValueError("Publication and paid calls forbidden")
    return obj


def changed_request(root, head="HEAD", *, git=subprocess.run):
    root = Path(root).resolve()
    result = git(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", head,
                  "--", "requests/ai_director_v2"],
                 cwd=root, capture_output=True, text=True, timeout=15, check=True)
    changed = result.stdout.splitlines()
    if len(changed) != 1 or not PATH.fullmatch(changed[0]):
        raise ValueError("Exactly one safe changed AI Director review request required")
    path = (root / changed[0]).resolve()
    if not path.is_relative_to(root) or not path.is_file() or path.stat().st_size > 4096:
        raise ValueError("Request missing/unsafe")
    data = json.loads(path.read_text(encoding="utf-8"))
    return validate_request(data)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, default=Path("."))
    p.add_argument("--env-output", type=Path, required=True)
    o = p.parse_args(argv)
    r = changed_request(o.repo)
    with o.env_output.open("a", encoding="utf-8") as out:
        out.write("SAFE_RUN_ID=" + str(r["producer_run_id"]) + "\n")
        out.write("DIRECTOR_FORMAT=" + r["video_format"] + "\n")
        out.write("SAFE_ARTIFACT_NAME=" + r["artifact_name"] + "\n")
    print("AI_DIRECTOR_EXPLICIT_SAFE_REQUEST", r["producer_run_id"], r["video_format"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
