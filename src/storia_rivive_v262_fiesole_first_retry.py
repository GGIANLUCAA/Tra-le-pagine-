#!/usr/bin/env python3
"""V262: one bounded, no-cost CPU retry for authentic Fiesole shot 01.

Keeps the diffusion model's built-in safety checker enabled. A filtered or
missing result is NOT a photo, cannot be counted, and never becomes a video.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import storia_rivive_v261_fiesole_first_source_i2i as first

# Short affirmative prompt avoids CLIP's 77-token truncation observed in V261.
PROMPT = (
    "Apply subtle realistic color to this original black and white archival photograph. "
    "Preserve all existing objects, contours, and camera geometry exactly. "
    "Natural daylight and restrained wood, metal, and straw colors."
)
SEED = 262
VERSION = "V262_FIRST_SOURCE_SAFETY_RESPECTING_RETRY_NOT_FINAL"
QA_NAME = "V257_SOURCE_LOCKED_I2I_QA.json"


def stamp_report(out: Path) -> None:
    """Keep a truthful audit trail even if model inference was rejected."""
    path = out / QA_NAME
    if not path.is_file():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    data.update(
        version=VERSION,
        seed=SEED,
        prompt_sha256=hashlib.sha256(PROMPT.encode("utf-8")).hexdigest(),
        prior_trial="V261_MODEL_OUTPUT_FILTERED_BY_SAFETY_CHECKER",
        safety_checker_disabled=False,
        new_final_episodes_delivered=0,
        artistic_approval=False,
        italian_rights_verified=False,
        publish_allowed=False,
        paid_credits_spent=0,
    )
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    argv = sys.argv[1:]
    if "--out" not in argv or argv.index("--out") + 1 >= len(argv):
        raise ValueError("V262_OUTPUT_PATH_REQUIRED")
    out = Path(argv[argv.index("--out") + 1])
    first.PROMPT = PROMPT
    first.SEED = SEED
    try:
        first.main()  # source SHA and five-scene uniqueness validated by V261
    finally:
        stamp_report(out)


if __name__ == "__main__":
    main()
