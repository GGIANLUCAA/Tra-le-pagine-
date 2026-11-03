#!/usr/bin/env python3
"""V209: independent FFmpeg cut evidence for five authentic archival selections.

The V204–207 gates validate original pixels, novelty and motion; they cannot
establish different camera shots. This conservative review gate uses an FFmpeg
scene-change heuristic over source film bytes and maps the five freeze times
to candidate segments. A positive result is NEVER shot approval, Italian
rights approval or permission to call generative providers.
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path

READY_MOTION = "FIVE_BW_MOTION_LEADINS_SHOT_REVIEW_PENDING"
READY_PROVENANCE = "FIVE_FRAMES_REEXTRACTED_FROM_FILM_REVIEW_PENDING"
REVIEW_PENDING = "FIVE_SHOT_BOUNDARY_CANDIDATES_REVIEW_PENDING"
MAX_BYTES = 160 * 1024 * 1024
MAX_SECONDS = 420
LEAD_SECONDS = 1.2
PTS = re.compile(r"\bpts_time:\s*([0-9]+(?:\.[0-9]+)?)")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def detect_boundaries(film: Path, seconds: float) -> list[float]:
    """Low-rate analysis to limit CI cost; not an authoritative cut detector."""
    cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-v", "info", "-i", str(film),
           "-t", f"{seconds:.3f}", "-an",
           "-vf", r"fps=3,select=gt(scene\,0.22),showinfo", "-f", "null", "-"]
    completed = subprocess.run(cmd, capture_output=True, text=True,
                               timeout=180, check=True)
    candidates = []
    for line in completed.stderr.splitlines():
        if "showinfo" not in line or "pts_time:" not in line:
            continue
        match = PTS.search(line)
        if match:
            value = float(match.group(1))
            if math.isfinite(value) and value > 0 and (not candidates or value - candidates[-1] > 0.20):
                candidates.append(round(value, 3))
    return candidates


def inspect(manifest: dict, provenance: dict, motion: dict, scout: dict,
            cache: Path) -> dict:
    report = {"version": "V209_CUT_CANDIDATE_REVIEW",
              "status": "SHOT_BOUNDARY_REVIEW_BLOCKED", "reason": "UNKNOWN",
              "shot_distinctness_reviewed_by_human": False,
              "five_distinct_shots_approved": False,
              "italian_rights_approved": False,
              "provider_calls_permitted": False,
              "publish_permitted": False, "credits_spent": 0}

    def block(reason: str) -> dict:
        report["reason"] = reason
        return report

    if not all(isinstance(x, dict) for x in (manifest, provenance, motion, scout)):
        return block("INVALID_INPUT_SCHEMA")
    if provenance.get("status") != READY_PROVENANCE or motion.get("status") != READY_MOTION:
        return block("PREVIOUS_FILM_GATES_NOT_VERIFIED")
    expected = provenance.get("source_film_sha256")
    if not isinstance(expected, str) or not re.fullmatch(r"[a-f0-9]{64}", expected):
        return block("INVALID_SOURCE_HASH")
    if manifest.get("source_video_sha256") != expected or scout.get("original_sha256") != expected:
        return block("SOURCE_HASH_BINDING_MISMATCH")
    film = cache / "ORIGINAL_ARCHIVE.webm"
    if film.is_symlink() or not film.is_file() or not 0 < film.stat().st_size <= MAX_BYTES:
        return block("SOURCE_FILE_MISSING_OR_UNSAFE")
    if sha256(film) != expected:
        return block("SOURCE_FILM_BYTES_CHANGED")
    duration = scout.get("duration_s")
    if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not math.isfinite(duration):
        return block("INVALID_FILM_DURATION")
    if not 1.0 <= duration <= 10000:
        return block("INVALID_FILM_DURATION")
    evidence = motion.get("motion_evidence")
    jobs = manifest.get("original_frame_jobs")
    if not isinstance(evidence, list) or len(evidence) != 5 or not isinstance(jobs, list) or len(jobs) != 5:
        return block("INVALID_FIVE_SHOT_EVIDENCE")
    times = []
    for i, item in enumerate(evidence):
        if not isinstance(item, dict) or not isinstance(jobs[i], dict):
            return block("INVALID_SHOT_EVIDENCE_ROW")
        timestamp = item.get("freeze_time_advisory_s")
        original_name = item.get("source_frame")
        if (not isinstance(original_name, str) or original_name != Path(str(jobs[i].get("source_file", ""))).name
                or isinstance(timestamp, bool) or not isinstance(timestamp, (float, int))
                or not math.isfinite(timestamp) or timestamp < LEAD_SECONDS or timestamp >= duration):
            return block("INVALID_FREEZE_TIMESTAMP_OR_BINDING")
        times.append(float(timestamp))
    if times != sorted(times) or len(set(times)) != 5:
        return block("INVALID_FREEZE_SEQUENCE")
    scan_seconds = min(float(duration), times[-1] + 0.4)
    if scan_seconds > MAX_SECONDS:
        return block("SOURCE_TOO_LONG_FOR_BOUNDED_CUT_REVIEW")
    try:
        boundaries = detect_boundaries(film, scan_seconds)
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, OSError, ValueError):
        return block("CUT_DETECTION_FAILED")
    report["candidate_cut_times_s"] = boundaries
    report["detector"] = "FFmpeg fps=3 select=gt(scene,0.22) heuristic"
    report["manual_recheck_required"] = True
    shot_indices = [bisect.bisect_right(boundaries, t) for t in times]
    lead_indices = [bisect.bisect_right(boundaries, t - LEAD_SECONDS) for t in times]
    report["candidate_segments"] = [
        {"frame": evidence[i]["source_frame"],
         "freeze_time_advisory_s": times[i], "segment_index": shot_indices[i],
         "lead_in_same_candidate_segment": lead_indices[i] == shot_indices[i]}
        for i in range(5)]
    if any(a != b for a, b in zip(shot_indices, lead_indices)):
        return block("MOVING_LEADIN_CROSSES_CANDIDATE_SHOT_CUT")
    if len(set(shot_indices)) != 5:
        return block("FIVE_SEPARATE_CUT_SEGMENTS_NOT_DETECTED")
    report["status"] = REVIEW_PENDING
    report["reason"] = "FIVE_CANDIDATE_SEGMENTS_FOUND_NOT_HUMAN_APPROVED"
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    for name in ("manifest", "provenance", "motion", "scout", "cache", "out"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    try:
        data = inspect(*(json.loads(Path(getattr(args, k)).read_text(encoding="utf-8"))
                         for k in ("manifest", "provenance", "motion", "scout")),
                       Path(args.cache))
    except (OSError, ValueError, TypeError):
        data = {"version": "V209_CUT_CANDIDATE_REVIEW",
                "status": "SHOT_BOUNDARY_REVIEW_BLOCKED",
                "reason": "INVALID_OR_MISSING_INPUT",
                "five_distinct_shots_approved": False,
                "provider_calls_permitted": False, "publish_permitted": False,
                "credits_spent": 0}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(data["status"], data["reason"])
    if data["status"] != REVIEW_PENDING:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
