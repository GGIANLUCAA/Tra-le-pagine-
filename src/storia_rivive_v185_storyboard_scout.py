#!/usr/bin/env python3
"""V185: extract five candidate camera shots from SHA-locked local film.

Only original source frames are saved. Scene cuts are algorithmic hints,
not proof of five different shots, rights, exact freeze PTS or approval.
No network, provider calls, credits, or publishing.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

from storia_rivive_v184_source_intake import inspect_local

PTS_RE = re.compile(r"\bpts_time:([0-9]+(?:\.[0-9]+)?)")
MIN_CUT_SPACING = 2.0
SCENE_THRESHOLD = 0.10


def _run(args, timeout):
    return subprocess.run(args, check=True, capture_output=True, text=True, timeout=timeout)


def detect_scene_cuts(source, duration, threshold=SCENE_THRESHOLD):
    """Decode the film; detect possible cuts at 320 px, never upscale output."""
    if not (0.01 <= threshold <= 0.90):
        raise ValueError("INVALID_SCENE_THRESHOLD")
    filtergraph = f"scale=320:-2,select='gt(scene,{threshold:.3f})',showinfo"
    proc = _run([
        "ffmpeg", "-hide_banner", "-nostdin", "-nostats", "-loglevel", "info",
        "-i", str(source), "-map", "0:v:0", "-an", "-vf", filtergraph,
        "-f", "null", "-",
    ], timeout=max(120, min(2400, int(duration * 4 + 120))))
    cuts = []
    for line in proc.stderr.splitlines():
        if "Parsed_showinfo" not in line:
            continue
        match = PTS_RE.search(line)
        if match:
            t = float(match.group(1))
            if 0.1 < t < duration - 0.5 and (not cuts or t - cuts[-1] >= MIN_CUT_SPACING):
                cuts.append(round(t, 3))
    return cuts


def extract_frame(source, t, destination):
    """Sample a native-resolution PNG; exact final freeze PTS remains unverified."""
    _run([
        "ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "error", "-y",
        "-ss", f"{t:.3f}", "-i", str(source), "-map", "0:v:0",
        "-frames:v", "1", "-vsync", "0", str(destination),
    ], timeout=120)
    if not destination.is_file() or destination.stat().st_size == 0:
        raise ValueError("FRAME_EXTRACTION_FAILED")
    return hashlib.sha256(destination.read_bytes()).hexdigest()


def scout_local(source, expected_sha256, output_dir, threshold=SCENE_THRESHOLD):
    source, output_dir = Path(source), Path(output_dir)
    report = {
        "version": "V185", "source_path": str(source),
        "scene_threshold": threshold, "source_sha256": None,
        "status": "SCOUT_BLOCKED", "blocking_issues": [], "candidates": [],
        "rights_italy_verified": False, "five_distinct_shots_verified": False,
        "freeze_pts_verified": False, "human_visual_qa_approved": False,
        "provider_jobs_may_start": False, "publish_permitted": False,
    }
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256 or ""):
        report["blocking_issues"].append("VALID_SOURCE_SHA256_REQUIRED")
        return report
    if any(p.is_symlink() for p in (source, *source.parents)):
        report["blocking_issues"].append("SYMLINK_SOURCE_REJECTED")
        return report
    intake = inspect_local(source, expected_sha256)
    report["source_sha256"] = intake.get("source_sha256")
    if intake["status"] != "ASSETS_PENDING" or intake["source_sha256"] != expected_sha256:
        report["blocking_issues"].append("V184_SOURCE_INTAKE_NOT_READY")
        report["blocking_issues"].extend(intake["blocking_issues"])
        return report
    duration = intake["media"]["duration_seconds"]
    report["source_media"] = intake["media"]
    try:
        cuts = detect_scene_cuts(source, duration, threshold)
    except (OSError, ValueError, subprocess.SubprocessError):
        report["blocking_issues"].append("SCENE_DETECTION_FAILED")
        return report
    report["detected_cut_pts_seconds"] = cuts
    times = [0.5]
    for cut in cuts:
        sample = round(cut + 0.5, 3)
        if sample < duration - 0.25 and sample - times[-1] >= MIN_CUT_SPACING:
            times.append(sample)
        if len(times) == 5:
            break
    if len(times) != 5:
        report["blocking_issues"].append("FEWER_THAN_FIVE_SCENE_CANDIDATES")
        return report
    if output_dir.exists():
        report["blocking_issues"].append("OUTPUT_DIR_ALREADY_EXISTS")
        return report
    output_dir.mkdir(parents=True)
    try:
        for i, t in enumerate(times, 1):
            dest = output_dir / f"candidate_{i:02d}.png"
            sha = extract_frame(source, t, dest)
            report["candidates"].append({
                "index": i, "sample_requested_seconds": t,
                "png_filename": dest.name, "png_sha256": sha,
                "source_sha256": expected_sha256,
                "camera_shot_human_verified": False,
                "freeze_pts_verified": False,
            })
    except (OSError, ValueError, subprocess.SubprocessError):
        report["blocking_issues"].append("FRAME_EXTRACTION_FAILED")
        return report
    if len({c["png_sha256"] for c in report["candidates"]}) != 5:
        report["blocking_issues"].append("DUPLICATE_EXTRACTED_FRAME_BYTES")
        return report
    report["status"] = "FIVE_CANDIDATES_NEED_VISUAL_REVIEW"
    report["blocking_issues"] = [
        "FIVE_TRUE_CAMERA_SHOTS_NOT_HUMAN_VERIFIED",
        "EXACT_FREEZE_PTS_NOT_YET_VERIFIED",
        "ITALIAN_TERRITORIAL_RIGHTS_REVIEW_PENDING",
        "I2I_AND_VIDU_NOT_GENERATED",
    ]
    (output_dir / "V185_STORYBOARD.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--threshold", type=float, default=SCENE_THRESHOLD)
    parser.add_argument("--report", help="Optional JSON report path, including blocked results")
    args = parser.parse_args()
    report = scout_local(args.file, args.expected_sha256, args.out_dir, args.threshold)
    if args.report:
        target = Path(args.report)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"], "issues": report["blocking_issues"],
        "candidate_count": len(report["candidates"]),
    }, ensure_ascii=False))
    return 0 if report["status"] == "FIVE_CANDIDATES_NEED_VISUAL_REVIEW" else 2


if __name__ == "__main__":
    raise SystemExit(main())
