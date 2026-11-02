#!/usr/bin/env python3
"""V215 one-source archival pilot: fetch real HD film and select source frames.

This is research-only: produces a private contact sheet and candidate-shot
report. No image generation, Vidu, social publishing or fictional approvals.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from storia_rivive_scout_v101 import inspect
from storia_rivive_frame_rank_v101 import rank
from storia_rivive_v210_shot_aware_selection import select

SOURCE_PAGE = "https://commons.wikimedia.org/wiki/File:Filature_et_Tissage_du_coton_(1920).webm"


def run(out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    cache = out / "source-cache"
    report = {"version": "V215_REAL_HD_SOURCE_TRIAL",
              "subject": "Filature et Tissage du coton (1920)",
              "source_page": SOURCE_PAGE, "status": "SOURCE_SCOUT_BLOCKED",
              "source_downloaded": False, "source_frames_extracted": 0,
              "five_distinct_shots_approved": False,
              "italian_rights_approved": False,
              "photo_i2i_generated": 0, "vidu_clips_generated": 0,
              "finished_mp4": False, "published": False,
              "provider_calls_permitted": False, "credits_spent": 0}
    try:
        scout = inspect(SOURCE_PAGE, cache)
        (out / "SCOUT_REPORT.json").write_text(
            json.dumps(scout, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if scout.get("status") != "REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW":
            report["reason"] = scout.get("status", "SCOUT_NOT_READY")
            return report
        report["source_downloaded"] = True
        report["source_frames_extracted"] = scout["source_frames_extracted"]
        report["original_sha256"] = scout["original_sha256"]
        report["sampling_period_s"] = scout.get("sampling_period_s")
        report["sampling_window_s"] = scout.get("sampling_window_s")
        ranking = rank(cache / "original_frames")
        (out / "FRAME_RANKING.json").write_text(
            json.dumps(ranking, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if ranking.get("status") != "FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW":
            report["status"] = "SOURCE_RANKING_BLOCKED"
            report["reason"] = ranking.get("status")
            return report
        selection = select(ranking, scout, cache)
        (out / "SHOT_AWARE_SELECTION_V210.json").write_text(
            json.dumps(selection, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        report["status"] = selection["status"]
        report["reason"] = selection["reason"]
        report["candidate_frame_names"] = [r["filename"] for r in selection["preselected"]]
        report["candidate_times_advisory_s"] = selection.get("candidate_segment_times_s", [])
        report["manual_source_and_rights_review_required"] = True
        return report
    except Exception as exc:
        # Network, decoding and detector failures remain an honest blocked
        # source, never a false production success.
        report["status"] = "SOURCE_SCOUT_BLOCKED"
        report["reason"] = type(exc).__name__ + ": " + str(exc)[:220]
        return report
    finally:
        (out / "REAL_SOURCE_TRIAL_V215.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    args = p.parse_args()
    report = run(Path(args.out))
    print("V215_REAL_HD_SOURCE_TRIAL", report["status"], report.get("reason", ""))
    print("PROVIDER_CALLS=0 PUBLISHED=false FINISHED_MP4=false")


if __name__ == "__main__":
    main()
