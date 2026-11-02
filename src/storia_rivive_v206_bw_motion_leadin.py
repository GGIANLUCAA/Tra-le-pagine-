#!/usr/bin/env python3
"""V206: check genuine local B/W motion BEFORE each selected archival freeze.

V204 proves source pixels; V205 detects near-duplicate stills. Neither proves
that a 1.2s moving B/W lead-in exists for each of the five selected frames.
This is a conservative, no-provider research gate, NOT five-shot approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageOps, ImageStat

READY_V204 = "FIVE_FRAMES_REEXTRACTED_FROM_FILM_REVIEW_PENDING"
READY_V205 = "FIVE_VISUALLY_NONREDUNDANT_FRAMES_SHOT_REVIEW_PENDING"
READY_V206 = "FIVE_BW_MOTION_LEADINS_SHOT_REVIEW_PENDING"
FRAME = re.compile(r"frame_(0[1-9]|1[0-2])\.png\Z")
LEAD_SECONDS = 1.2
MAX_FILM_BYTES = 160 * 1024 * 1024


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def metric(first: Path, last: Path) -> dict:
    """Remove global exposure variation; require spatial change as well."""
    with Image.open(first) as a, Image.open(last) as b:
        x = ImageOps.grayscale(a).resize((96, 96))
        y = ImageOps.grayscale(b).resize((96, 96))
    raw = ImageStat.Stat(ImageChops.difference(x, y)).mean[0]
    norm = ImageStat.Stat(ImageChops.difference(
        ImageOps.autocontrast(x), ImageOps.autocontrast(y))).mean[0]
    return {"raw_mad": round(raw, 2), "exposure_normalized_mad": round(norm, 2),
            "moving": raw >= 4.0 and norm >= 3.0}


def sample(film: Path, before: float, folder: Path) -> dict:
    folder.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-nostdin", "-y", "-v", "error", "-ss", f"{before:.4f}",
           "-i", str(film), "-t", str(LEAD_SECONDS),
           "-vf", "fps=3,scale=96:96", "-frames:v", "4",
           str(folder / "motion_%02d.png")]
    subprocess.run(cmd, check=True, capture_output=True, timeout=100)
    frames = sorted(folder.glob("motion_*.png"))
    if len(frames) < 3:
        raise ValueError("Insufficient decoded film motion frames")
    return metric(frames[0], frames[-1])


def inspect(manifest: dict, provenance: dict, novelty: dict,
            scout: dict, cache: Path) -> dict:
    report = {
        "version": "V206_BW_MOTION_LEADIN", "status": "BW_MOTION_BLOCKED",
        "reason": "UNKNOWN", "provider_calls_permitted": False,
        "publish_permitted": False, "five_distinct_shots_approved": False,
        "italian_rights_approved": False, "credits_spent": 0,
    }

    def block(reason):
        report["reason"] = reason
        return report

    if not all(isinstance(v, dict) for v in (manifest, provenance, novelty, scout)):
        return block("INVALID_INPUT")
    if provenance.get("status") != READY_V204 or novelty.get("status") != READY_V205:
        return block("PREVIOUS_SOURCE_GATES_NOT_VERIFIED")
    film_sha = provenance.get("source_film_sha256")
    if not isinstance(film_sha, str) or not re.fullmatch("[0-9a-f]{64}", film_sha):
        return block("INVALID_FILM_SHA")
    if manifest.get("source_video_sha256") != film_sha or scout.get("original_sha256") != film_sha:
        return block("FILM_PROVENANCE_MISMATCH")
    film = cache / "ORIGINAL_ARCHIVE.webm"
    if film.is_symlink() or not film.is_file() or not 0 < film.stat().st_size <= MAX_FILM_BYTES:
        return block("FILM_MISSING_OR_UNSAFE")
    if sha256(film) != film_sha:
        return block("FILM_BYTES_CHANGED_AFTER_V204")
    duration = scout.get("duration_s")
    if isinstance(duration, bool) or not isinstance(duration, (float, int)):
        return block("INVALID_FILM_DURATION")
    duration = float(duration)
    if not math.isfinite(duration) or not 1 <= duration <= 10000:
        return block("INVALID_FILM_DURATION")
    jobs = manifest.get("original_frame_jobs")
    names = provenance.get("selected_frame_names")
    if not isinstance(jobs, list) or len(jobs) != 5 or not isinstance(names, list) or len(names) != 5:
        return block("INVALID_FIVE_FRAME_BINDING")
    period = max(1.0, duration / 12)
    if provenance.get("fps_filter") != "fps=1/" + str(round(period, 4)):
        return block("SCOUT_FPS_MISMATCH")
    evidence = []
    for n, job in enumerate(jobs):
        if not isinstance(job, dict) or not isinstance(job.get("source_file"), str):
            return block("INVALID_SOURCE_JOB")
        name = Path(job["source_file"]).name
        if name != names[n] or not FRAME.fullmatch(name):
            return block("SOURCE_FRAME_BINDING_MISMATCH")
        frame_number = int(name[6:8])
        t = (frame_number - 1) * period
        # A freeze at t=0 cannot have the required preceding real film motion.
        if t < LEAD_SECONDS + 0.1 or t > duration:
            report["blocked_frame"] = name
            return block("NO_PRECEDING_BW_MOTION_WINDOW")
        try:
            with tempfile.TemporaryDirectory(prefix="storia-v206-") as tmp:
                motion = sample(film, t - LEAD_SECONDS, Path(tmp))
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired,
                OSError, ValueError):
            report["blocked_frame"] = name
            return block("MOTION_DECODE_FAILED")
        evidence.append({"source_frame": name, "freeze_time_advisory_s": round(t, 3),
                         "lead_in_start_advisory_s": round(t - LEAD_SECONDS, 3),
                         **motion})
        if not motion["moving"]:
            report["blocked_frame"] = name
            report["motion_evidence"] = evidence
            return block("STATIC_OR_FLICKER_ONLY_BW_LEADIN")
    report.update({
        "status": READY_V206,
        "reason": "FIVE_MOVING_BW_LEADINS; CAMERA_SHOTS_RIGHTS_AND_FREEZE_SYNC_STILL_UNREVIEWED",
        "motion_evidence": evidence, "shot_review_required": True,
        "freeze_timestamps_are_advisory": True,
    })
    return report


def main():
    p = argparse.ArgumentParser()
    for key in ("manifest", "provenance", "novelty", "scout", "cache", "out"):
        p.add_argument("--" + key, required=True)
    a = p.parse_args()
    try:
        result = inspect(*(json.loads(Path(getattr(a, k)).read_text(encoding="utf-8"))
                           for k in ("manifest", "provenance", "novelty", "scout")),
                         Path(a.cache))
    except (OSError, ValueError, TypeError):
        result = {"version": "V206_BW_MOTION_LEADIN", "status": "BW_MOTION_BLOCKED",
                  "reason": "INVALID_OR_MISSING_INPUT", "provider_calls_permitted": False,
                  "publish_permitted": False, "credits_spent": 0}
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(result["status"], result["reason"])
    if result["status"] != READY_V206:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
