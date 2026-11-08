#!/usr/bin/env python3
"""Real-MP4 sentence evidence for ArtVision Critico. No AI, TTS, editing or approval.

The existing renderer calls capture() after it has physically rendered and decoded
its MP4. Real video-frame thumbnails, real Gacrux WAV hashes, real cached ASR
timestamps and renderer-emitted camera crops are recorded. This NEVER guesses
which painted subject is being discussed, and never approves publication.
"""
from __future__ import annotations

import bisect
import hashlib
import json
import math
import re
import subprocess
import wave
from pathlib import Path

SCHEMA = "artvision-critico-real-mp4-focus-v1"
VALID_VARIANTS = {"critico_standard", "critico_museum"}


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for part in iter(lambda: stream.read(1 << 20), b""):
            h.update(part)
    return h.hexdigest()


def wav_seconds(path):
    with wave.open(str(path), "rb") as stream:
        if stream.getframerate() <= 0 or stream.getnframes() <= 0:
            raise ValueError("Empty or unreadable WAV")
        return stream.getnframes() / stream.getframerate()


def _verified_cache(cache, wav, offset, duration):
    if not isinstance(cache, dict):
        raise ValueError("Invalid voice cache")
    if cache.get("wav_sha256") != digest(wav):
        raise ValueError("WAV not identical to verified ASR cache")
    alignment = cache.get("alignment") or {}
    if alignment.get("method") != "asr_with_interpolation" or (
            alignment.get("matched_fraction") or 0) < .85:
        raise ValueError("Real ASR verification required, not estimated timing")
    timed = cache.get("timed")
    if not isinstance(timed, list) or not timed:
        raise ValueError("No verified ASR sentences")
    previous_start = -1.0
    verified = []
    for index, item in enumerate(timed):
        if not isinstance(item, list) or len(item) != 3:
            raise ValueError("Invalid ASR sentence record")
        speech, first, last = item
        if (not isinstance(speech, str) or not speech.strip()
                or any(isinstance(t, bool) or not isinstance(t, (int, float))
                       or not math.isfinite(t) for t in (first, last))
                or not 0 <= first < last <= duration + .1
                or first < previous_start):
            raise ValueError(f"Unverified sentence timing {index + 1}")
        if offset + last > duration + offset + .1:
            raise ValueError("ASR sentence outside WAV")
        previous_start = first
        verified.append((speech, float(first), float(last)))
    return verified, alignment


def _validate_camera_trace(trace, video_duration):
    if not isinstance(trace, list) or not trace:
        return []
    last = -1.0
    for row in trace:
        if not isinstance(row, dict):
            raise ValueError("Invalid camera trace row")
        t = row.get("time_s")
        if (isinstance(t, bool) or not isinstance(t, (float, int))
                or not math.isfinite(t) or not 0 <= t <= video_duration
                or t <= last):
            raise ValueError("Camera trace must be real ordered frame times")
        last = t
        if row.get("kind") not in ("whole_plate", "detail"):
            raise ValueError("Unknown scene type")
        crop = row.get("camera_crop_xyxy")
        if row["kind"] == "detail" and (
                not isinstance(crop, list) or len(crop) != 4
                or any(not isinstance(v, (float, int)) or isinstance(v, bool)
                       or not math.isfinite(v) for v in crop)
                or not (0 <= crop[0] < crop[2] <= 1
                        and 0 <= crop[1] < crop[3] <= 1)):
            raise ValueError("Real detail camera must have valid source crop")
    return trace


def capture(*, video, wav, voice_cache, output_dir, variant,
            voice_offset_s, video_duration_s, camera_trace,
            expected_video_sha256=None):
    """Build inspectable evidence; accepts no subject boxes or human approval claims."""
    if variant not in VALID_VARIANTS:
        raise ValueError("Not an ArtVision Critico variant")
    video, wav, voice_cache = map(Path, (video, wav, voice_cache))
    if not video.is_file() or video.stat().st_size <= 0 or not wav.is_file():
        raise ValueError("Real MP4 and WAV required")
    if (isinstance(voice_offset_s, bool) or not isinstance(voice_offset_s, (float, int))
            or not math.isfinite(voice_offset_s) or voice_offset_s < 0
            or isinstance(video_duration_s, bool)
            or not isinstance(video_duration_s, (float, int))
            or not math.isfinite(video_duration_s) or video_duration_s <= 0):
        raise ValueError("Invalid actual voice offset or MP4 duration")
    video_hash = digest(video)
    if expected_video_sha256 is not None and video_hash != expected_video_sha256:
        raise ValueError("Physical MP4 SHA mismatch")
    cache = json.loads(voice_cache.read_text(encoding="utf-8"))
    duration = wav_seconds(wav)
    if voice_offset_s + duration > video_duration_s + .15:
        raise ValueError("MP4 cuts off narrated WAV")
    timed, alignment = _verified_cache(cache, wav, voice_offset_s, duration)
    trace = _validate_camera_trace(camera_trace, video_duration_s)
    trace_times = [row["time_s"] for row in trace]
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    frames = output / "REAL_MP4_FRAMES"
    frames.mkdir(exist_ok=True)
    sentences = []
    for idx, (speech, start, end) in enumerate(timed, 1):
        video_start, video_end = voice_offset_s + start, voice_offset_s + end
        if video_end > video_duration_s + .10:
            raise ValueError("Sentence leaves rendered MP4")
        times = {
            "start": min((video_start + video_end) / 2, video_start + .12),
            "middle": (video_start + video_end) / 2,
            "end": max((video_start + video_end) / 2, video_end - .12),
        }
        samples = []
        for kind, at in times.items():
            if not 0 <= at < video_duration_s:
                raise ValueError("Invalid MP4 sample time")
            filename = f"sentence_{idx:02d}_{kind}.jpg"
            path = frames / filename
            subprocess.run([
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
                "-ss", f"{at:.4f}", "-i", str(video),
                "-frames:v", "1", "-q:v", "4", str(path),
            ], check=True, timeout=45)
            if not path.is_file() or not path.stat().st_size:
                raise ValueError("Real-MP4 frame extraction failed")
            # Nearest measured crop, not an invented crop or semantic subject box.
            closest = None
            if trace:
                place = bisect.bisect_left(trace_times, at)
                candidates = [trace[min(place, len(trace)-1)],
                              trace[max(0, place-1)]]
                closest = min(candidates, key=lambda row: abs(row["time_s"] - at))
                if abs(closest["time_s"] - at) > .51:
                    closest = None
            samples.append({
                "type": kind, "time_s": round(at, 4),
                "actual_mp4_frame": "REAL_MP4_FRAMES/" + filename,
                "frame_sha256": digest(path),
                "camera_measurement": closest,
                "subject_matches_spoken_text": "UNREVIEWED",
                "visual_review": "PENDING",
            })
        sentences.append({
            "id": f"s{idx:02d}", "spoken_text": speech,
            "audio_start_s": start, "audio_end_s": end,
            "video_start_s": round(video_start, 4),
            "video_end_s": round(video_end, 4),
            "samples": samples,
        })
    report = {
        "schema": SCHEMA, "variant": variant,
        "media_sha256": video_hash, "wav_sha256": digest(wav),
        "asr_cache_sha256": digest(voice_cache),
        "asr_method": alignment["method"],
        "asr_matched_fraction": alignment["matched_fraction"],
        "voice_offset_s": voice_offset_s,
        "video_duration_s": video_duration_s,
        "sentence_count": len(sentences),
        "real_frames_extracted": len(sentences) * 3,
        "camera_measurements_from_renderer": bool(trace),
        "semantic_subject_bboxes_verified": False,
        "status": "needs_visual_and_semantic_review",
        "reviewer_approval": False,
        "v25_gold": False, "website_published": False,
        "new_audio_video_api_calls": 0,
        "does_not_change_original_mp4": True,
        "sentences": sentences,
    }
    target = output / "ARTVISION_CRITICO_REAL_MP4_FOCUS_QA.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
