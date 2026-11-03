#!/usr/bin/env python3
"""V248 Fiesole 1912: repair real archival motion windows before any I2I/Vidu.

Review only. Six SHA-bound historical camera-view candidates are sampled on
the ORIGINAL film for title cards, then exact-source endpoint checks are run.
Five clean shots may produce a 24s SOURCE-ONLY MP4, never a final episode.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import tempfile
from pathlib import Path
from PIL import Image

from storia_rivive_v210_shot_aware_selection import likely_intertitle
from storia_rivive_v243_freeze_endpoint_roughcut import load_plan, build
from storia_rivive_v244_real_endpoint_pixel_qa import endpoint_error, inspect
from storia_rivive_v247_motion_intertitle_qa import check

FILM_SHA = "f87ca5d51a1ba4b60ffb0e5db6162f3b0afadcd3bf3b94393dcf66337a7af7fe"
SOURCE_PAGE = "https://commons.wikimedia.org/wiki/File:Manufacture_de_chapeaux_de_paille_%C3%A0_Fiesole_(1912).webm"
EPISODE = "fiesole_straw_hats_1912_v220"
# Editorial review of the V247 flagged windows: avoid frame 02/05/08
# as first-choice endpoints. Alternatives: machinery, hands, hat shaping.
CANDIDATES = [
    ("frame_03.png", "3ebabe8a57ce3cf386681255ad4d896ab540d31005bfbfd1087474f62af714cb"),
    ("frame_04.png", "f8e5cdfcf9047fb69e0ae95587752202267c14926885729346ccd281d1085088"),
    ("frame_06.png", "e2bdfc9ece63e4f66e4ddf62c438551e4cbf72badd013e1b774ed5be4a9bb8ee"),
    ("frame_07.png", "1d77c757e3193bc9c046f2ae10baebb49a3b71fe379ed359b18e761956f4afb0"),
    ("frame_10.png", "53e1c602b0c11dacf35eb19ab356283acb58a9825df28ae9a30e171a64f62f62"),
    ("frame_11.png", "ecbf51237c78e76e51f1c0ff3898f49538f520ef4a4da53a5b38e241c2328be6"),
]
SEGMENT_SECONDS = 4.8

def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def verified_input(film: Path, scout_path: Path, frames: Path) -> float:
    if film.is_symlink() or not film.is_file() or sha(film) != FILM_SHA:
        raise ValueError("V248_ORIGINAL_FILM_SHA_MISMATCH")
    scout = json.loads(scout_path.read_text(encoding="utf-8"))
    if (scout.get("status") != "REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW"
            or scout.get("source_page") != SOURCE_PAGE
            or scout.get("original_sha256") != FILM_SHA
            or scout.get("source_frames_extracted") != 12):
        raise ValueError("V248_SCOUT_SOURCE_PROVENANCE_MISMATCH")
    period = scout.get("sampling_period_s")
    if (isinstance(period, bool) or not isinstance(period, (float, int))
            or not math.isfinite(period) or not 8 < period < 11):
        raise ValueError("V248_INVALID_SOURCE_SAMPLING_PERIOD")
    for name, expected in CANDIDATES:
        path = frames / name
        if path.is_symlink() or not path.is_file() or sha(path) != expected:
            raise ValueError("V248_SOURCE_FRAME_SHA_MISMATCH_" + name)
        with Image.open(path) as image:
            if image.format != "PNG" or image.size != (1920, 1080):
                raise ValueError("V248_NATIVE_FRAME_GEOMETRY_CHANGED")
            image.verify()
    return float(period)

def extract_photo(film: Path, time_s: float, target: Path) -> None:
    subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
        "-ss", f"{time_s:.3f}", "-i", str(film), "-an",
        "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,format=gray",
        "-frames:v", "1", str(target)], check=True, timeout=60)
    if not target.is_file() or target.stat().st_size < 1000:
        raise ValueError("V248_MOTION_SAMPLE_NOT_DECODED")

def choose(rows: list[dict]) -> list[dict]:
    """No false approval if fewer than five authentic, clean moving views."""
    eligible = [r for r in rows if not any(r["title_flags"]) and r["endpoint_mae"] <= 24]
    eligible.sort(key=lambda r: r["timestamp_s"])
    if len(eligible) < 5:
        raise ValueError("V248_FEWER_THAN_FIVE_CLEAN_SOURCE_WINDOWS")
    result = eligible[:5]
    if len({r["frame"] for r in result}) != 5:
        raise ValueError("V248_DUPLICATED_SOURCE_FRAMES")
    return result

def run(film: Path, scout: Path, frames: Path, folder: Path) -> dict:
    period = verified_input(film, scout, frames)
    folder.mkdir(parents=True, exist_ok=True)
    rows = []
    report_path = folder / "V248_FIESOLE_EDITORIAL_WINDOWS.json"
    report = {"version": "V248_FIESOLE_CLEAN_MOTION_REVIEW",
              "episode": EPISODE, "source_sha256": FILM_SHA,
              "status": "EVALUATING_REAL_SOURCE", "candidate_count": len(CANDIDATES),
              "selected_five": [], "candidate_evidence": rows,
              "real_i2i_generated": 0, "vidu_generated": 0,
              "human_approved": False, "italian_rights_verified": False,
              "final_mp4": False, "final_zip": False,
              "new_final_episodes_delivered": 0, "publish_allowed": False}
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    try:
        with tempfile.TemporaryDirectory(prefix="storia-v248-") as directory:
            work = Path(directory)
            for name, digest in CANDIDATES:
                index = int(name[6:8])
                time_s = round((index - 0.5) * period, 3)
                if time_s < SEGMENT_SECONDS + .1:
                    raise ValueError("V248_SOURCE_MOTION_TOO_SHORT")
                flags = []
                # Four actual moving frames over the entire 4.8s window.
                for j, offset in enumerate((0.25, 1.55, 3.1, 4.55)):
                    sample = work / f"{index:02d}_sample_{j}.png"
                    extract_photo(film, time_s - SEGMENT_SECONDS + offset, sample)
                    flags.append(bool(likely_intertitle(sample)))
                endpoint = work / f"{index:02d}_endpoint.png"
                extract_photo(film, time_s - 1/24, endpoint)
                error = endpoint_error(frames / name, endpoint)
                rows.append({"frame": name, "original_sha256": digest,
                             "timestamp_s": time_s, "title_flags": flags,
                             "endpoint_mae": error,
                             "source_window_clean_candidate": not any(flags) and error <= 24})
                report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        chosen = choose(rows)
        selection = {"version": "V210_SHOT_AWARE_PRESELECTION",
                     "status": "FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW",
                     "reason": "V248_SHA_LOCKED_EDITORIAL_RESELECT_MOTION_CHECKED_NOT_APPROVED",
                     "preselected": [{"filename": r["frame"]} for r in chosen],
                     "candidate_segment_times_s": [r["timestamp_s"] for r in chosen],
                     "five_distinct_shots_approved": False, "provider_calls_permitted": False,
                     "publish_permitted": False}
        alignment = {"checks": [
            {"source_frame": r["frame"], "source_frame_sha256": r["original_sha256"],
             "selected_timecode_s": r["timestamp_s"],
             "endpoint_visually_aligned": True, "endpoint_mae": r["endpoint_mae"]}
            for r in chosen]}
        selection_path = folder / "SHOT_AWARE_SELECTION_V248_NOT_APPROVED.json"
        alignment_path = folder / "SOURCE_ENDPOINT_ALIGNMENT_V248.json"
        selection_path.write_text(json.dumps(selection, indent=2) + "\n", encoding="utf-8")
        alignment_path.write_text(json.dumps(alignment, indent=2) + "\n", encoding="utf-8")
        plan = load_plan(selection_path, alignment_path, frames)
        video_path = folder / "FIESOLE_V248_CLEAN_MOTION_SOURCE_ONLY_NOT_FINAL.mp4"
        rendered = build(film, plan, video_path)
        endpoint_qa = inspect(video_path, video_path.with_suffix(".json"), frames,
                              folder / "V248_ENDPOINT_QA.json")
        motion_qa = check(video_path, video_path.with_suffix(".json"),
                          folder / "V248_MOTION_INTERTITLE_QA.json")
        report["selected_five"] = [r["frame"] for r in chosen]
        report["endpoint_result"] = endpoint_qa["status"]
        report["motion_result"] = motion_qa["status"]
        report["duration_s"] = rendered["duration_s"]
        if (endpoint_qa["status"] != "REVIEW_ENDPOINTS_PASS"
                or motion_qa["flagged_shots"]):
            raise ValueError("V248_REAL_MP4_QA_REJECTED")
        report["status"] = "FIVE_CLEAN_MOTION_WINDOWS_SOURCE_ROUGHCUT_NOT_FINAL"
    except Exception as exc:
        report["status"] = "REJECTED_NEEDS_OTHER_SOURCE_WINDOWS"
        report["error_type"] = type(exc).__name__
        report["reason"] = str(exc)[:150]
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        raise
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report

def main() -> None:
    parser = argparse.ArgumentParser()
    for arg in ("film", "scout", "frames", "out"):
        parser.add_argument("--" + arg, required=True, type=Path)
    args = parser.parse_args()
    print("V248", run(args.film, args.scout, args.frames, args.out)["status"])

if __name__ == "__main__":
    main()
