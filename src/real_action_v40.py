#!/usr/bin/env python3
"""V40: incorporate genuinely MOVING footage into book scenes, no paid API.

This program NEVER generates action from still photographs. It requires source
MP4 footage where objects, people or natural phenomena actually move.
Each clip has source/licensing/narrative metadata and must be reviewed as art.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path

import cv2
import numpy as np

ALLOWED_LICENSES = {"pexels", "pixabay", "cc0", "cc-by-4.0", "own"}
ALLOWED_PROVIDERS = {"pexels", "pixabay", "wikimedia", "own"}
VIDEO_SUFFIXES = {".mp4", ".mov", ".mkv", ".webm"}


def probe(path: Path):
    proc = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                           "format=duration:stream=codec_type,codec_name,width,height",
                           "-of", "json", str(path)], capture_output=True,
                          text=True, check=True)
    result = json.loads(proc.stdout)
    video = next((s for s in result.get("streams", [])
                  if s.get("codec_type") == "video"), None)
    if not video or min(video.get("width", 0), video.get("height", 0)) < 240:
        raise ValueError("Footage privo di video leggibile o dimensioni troppo piccole")
    return float(result["format"]["duration"]), video


def hash_file(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda: f.read(1024*1024), b""):
            h.update(part)
    return h.hexdigest()


def inspect_action(path: Path, start: float, seconds: float):
    """Conservative automatic motion evidence, not semantic/esthetic approval.

    Compare consecutive frames after removing a simple global camera transform:
    camera-only pan/zoom should not be mistaken for moving objects. A moving
    subject may be smaller than the frame, so the measurement is advisory.
    """
    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        raise ValueError("Video sorgente impossibile da aprire")
    diffs, residuals = [], []
    try:
        for offset in np.linspace(0.12, max(0.13, seconds-0.30), num=6):
            for_at = start + float(offset)
            capture.set(cv2.CAP_PROP_POS_MSEC, for_at*1000)
            ok, a = capture.read()
            capture.set(cv2.CAP_PROP_POS_MSEC, (for_at+0.18)*1000)
            ok2, b = capture.read()
            if not ok or not ok2:
                continue
            a = cv2.resize(a, (256, 144), interpolation=cv2.INTER_AREA)
            b = cv2.resize(b, (256, 144), interpolation=cv2.INTER_AREA)
            gray_a, gray_b = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY), cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)
            diffs.append(float(np.mean(cv2.absdiff(gray_a, gray_b))))
            pts = cv2.goodFeaturesToTrack(gray_a, 320, 0.02, 7)
            if pts is None or len(pts) < 10:
                continue
            next_pts, status, _ = cv2.calcOpticalFlowPyrLK(gray_a, gray_b, pts, None)
            if next_pts is None:
                continue
            src, dst = pts[status[:, 0] == 1], next_pts[status[:, 0] == 1]
            if len(src) < 10:
                continue
            affine, _ = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC)
            if affine is None:
                continue
            predicted = cv2.transform(src.reshape(-1, 1, 2), affine).reshape(-1, 2)
            residual = np.linalg.norm(predicted-dst.reshape(-1, 2), axis=1)
            residuals.append(float(np.quantile(residual, 0.75)))
    finally:
        capture.release()
    if len(diffs) < 2:
        raise ValueError("Non riesco a campionare due intervalli di movimento")
    frame_change = float(np.median(diffs))
    object_motion = float(np.median(residuals)) if residuals else 0.0
    if frame_change < 0.65:
        raise ValueError("La fonte sembra ferma: non consegnarla come azione animata")
    return {"median_frame_change": round(frame_change, 3),
            "object_motion_px_256w": round(object_motion, 3),
            "residual_samples": len(residuals),
            "motion_supported": bool(object_motion >= 0.30),
            "manual_action_review_required": True}


def validate_spec(spec: dict, source: Path, root: Path):
    if not isinstance(spec, dict):
        raise ValueError("Specifiche video mancanti")
    path = source.resolve()
    # Work only with user-provided existing footage within the project.
    if not path.is_file() or path.suffix.lower() not in VIDEO_SUFFIXES:
        raise ValueError("Serve un file sorgente video vero esistente")
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Il file video deve essere nella cartella dell'episodio")
    if path.stat().st_size > 650*1024*1024:
        raise ValueError("Sorgente video troppo grande")
    for key in ("provider", "license", "source_url", "rights_reviewed",
                "visual_reviewed", "scene_action", "narrative_reason", "narration_anchor"):
        if key not in spec:
            raise ValueError(f"Campo obbligatorio mancante: {key}")
    if spec["provider"] not in ALLOWED_PROVIDERS:
        raise ValueError("Provider non riconosciuto")
    if str(spec["license"]).lower() not in ALLOWED_LICENSES:
        raise ValueError("Licenza non ammessa; verificare i diritti prima del montaggio")
    if spec["rights_reviewed"] is not True or spec["visual_reviewed"] is not True:
        raise ValueError("I diritti e il contenuto devono essere revisionati prima di montare")
    if spec["provider"] != "own" and not str(spec["source_url"]).startswith("https://"):
        raise ValueError("Fonte originale verificabile richiesta")
    if any(len(str(spec.get(k, "")).strip()) < 12 for k in
           ("scene_action", "narrative_reason", "narration_anchor")):
        raise ValueError("Azione, ragione narrativa e frase devono essere specifiche")
    seconds = spec.get("seconds")
    if type(seconds) is not int or not (5 <= seconds <= 10):
        raise ValueError("Durata clip da 5 a 10 secondi")
    start = spec.get("start", 0.0)
    if not isinstance(start, (int, float)) or start < 0:
        raise ValueError("Inizio footage non valido")
    for name in ("crop_x", "crop_y"):
        value = spec.get(name, 0.5)
        if not isinstance(value, (int, float)) or not 0 <= value <= 1:
            raise ValueError(f"Posizione soggetto {name} deve essere 0..1")
    return float(start), seconds


def produce(source: Path, dest: Path, spec: dict, episode_root: Path,
            fps=24, width=720, height=1280):
    source, dest = Path(source), Path(dest)
    start, seconds = validate_spec(spec, source, Path(episode_root))
    duration, _ = probe(source)
    if start + seconds > duration + 0.03:
        raise ValueError("Durata clip maggiore del footage disponibile")
    if dest.exists() or dest.with_suffix(".json").exists():
        raise ValueError("Non sovrascrivere una clip esistente")
    if fps not in (24, 25, 30) or width % 2 or height % 2:
        raise ValueError("Impostazioni video non compatibili")
    motion = inspect_action(source, start, seconds)
    # Automatic action evidence is not a substitute for an editor examining
    # the actual moving object, but rejects totally static sources.
    x, y = float(spec.get("crop_x", 0.5)), float(spec.get("crop_y", 0.5))
    crop = (f"fps={fps},scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height}:"
            f"x='(in_w-out_w)*{x:.3f}':y='(in_h-out_h)*{y:.3f}',"
            "format=yuv420p")
    dest.parent.mkdir(parents=True, exist_ok=True)
    command = ["ffmpeg", "-nostdin", "-hide_banner", "-v", "error", "-y",
               "-ss", f"{start:.3f}", "-i", str(source), "-t", str(seconds),
               "-vf", crop, "-an", "-frames:v", str(seconds*fps), "-r", str(fps),
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
               "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(dest)]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        output_duration, info = probe(dest)
        if abs(output_duration-seconds) > 0.15 or (
            info["width"], info["height"]) != (width, height):
            raise RuntimeError("Output non conforme")
        manifest = {
            "schema": "real-action-v40",
            "status": "rendered_needs_review",
            "source": str(source),
            "source_sha256": hash_file(source),
            "output_sha256": hash_file(dest),
            "original_footage_has_action": motion,
            "crop_x": x, "crop_y": y, "duration": output_duration,
            "provider": spec["provider"], "license": spec["license"],
            "source_url": spec["source_url"], "scene_action": spec["scene_action"],
            "narrative_reason": spec["narrative_reason"],
            "narration_anchor": spec["narration_anchor"],
            "rights_reviewed_by_operator": True,
            "automatic_approval": False
        }
        dest.with_suffix(".json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
        return manifest
    except Exception:
        dest.unlink(missing_ok=True)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--episode", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    print(json.dumps(produce(args.source, args.output, spec, args.episode),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
