#!/usr/bin/env python3
"""Resilient source-only cinematic scout: bounded requests, no Vidu or paid APIs.

Uses a SHORT excerpt of an actual archival film instead of downloading 1.36 GB.
The source item can be replaced only by an explicitly named alternative
of the SAME film. After failures, consults existing archive discovery adapters
for a separate, unapproved next candidate. Never substitutes fabricated media.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import cv2
import imageio_ffmpeg
import requests
from PIL import Image, ImageDraw

OUTPUT = Path("output/storia_zorro_1920_hd")
API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "LaStoriaRiviveResearch/1.1 (historical research, bounded queries)"}
TITLES = [
    ("zorro_1920_1080", "File:The Mark of Zorro 1920.webm", 1620, 1080),
    ("zorro_1920_720", "File:The Mark of Zorro (1920).webm", 928, 720),
]
OFFSET_SECONDS = 1200
SEGMENT_SECONDS = 26
MAX_SEGMENT_BYTES = 160 * 1024 * 1024


def record(name, obj):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def source_metadata(title):
    for attempt in range(2):
        try:
            response = requests.get(
                API, params={"action": "query", "titles": title, "prop": "imageinfo",
                             "iiprop": "url|size|sha1|extmetadata", "format": "json"},
                headers=HEADERS, timeout=22)
            if response.status_code in (429, 503) and attempt == 0:
                retry = response.headers.get("Retry-After", "")
                try:
                    pause = min(12, max(4, int(retry)))
                except (TypeError, ValueError):
                    pause = 6
                print("ARCHIVE_RATE_LIMIT_METADATA", response.status_code,
                      "bounded_pause_seconds", pause, flush=True)
                time.sleep(pause)
                continue
            response.raise_for_status()
            page = next(iter(response.json()["query"]["pages"].values()))
            info = page["imageinfo"][0]
            p = urlsplit(info["url"])
            if p.scheme != "https" or p.hostname != "upload.wikimedia.org":
                raise ValueError("UNTRUSTED_MEDIA_HOST")
            clean_url = urlunsplit((p.scheme, p.netloc, p.path, "", ""))
            return info, clean_url
        except (requests.RequestException, KeyError, StopIteration, ValueError) as error:
            if attempt == 1:
                raise RuntimeError("COMMONS_METADATA_UNAVAILABLE_" +
                                   type(error).__name__) from None
    raise RuntimeError("COMMONS_METADATA_UNAVAILABLE")


def excerpt(url):
    dest = OUTPUT / "SOURCE.mp4"
    dest.unlink(missing_ok=True)
    args = [imageio_ffmpeg.get_ffmpeg_exe(), "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
            "-ss", str(OFFSET_SECONDS), "-user_agent", HEADERS["User-Agent"],
            "-rw_timeout", "20000000", "-i", url, "-t", str(SEGMENT_SECONDS),
            "-an", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(dest)]
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=165)
        if proc.returncode:
            raise RuntimeError("EXCERPT_FFMPEG_REMOTE_UNAVAILABLE_" +
                               ("HTTP_429" if "429" in proc.stderr else "NETWORK_OR_DECODE"))
        if not dest.exists() or not 100000 < dest.stat().st_size < MAX_SEGMENT_BYTES:
            raise RuntimeError("EXCERPT_MISSING_OR_TOO_LARGE")
        cap = cv2.VideoCapture(str(dest))
        if not cap.isOpened():
            raise RuntimeError("EXCERPT_CANNOT_BE_DECODED")
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        if width < 900 or height < 680:
            raise RuntimeError("NOT_HIGH_ENOUGH_NATIVE_GEOMETRY")
        if fps <= 0 or frames / fps < 16:
            raise RuntimeError("EXCERPT_TOO_SHORT_OR_FPS_UNKNOWN")
        report = {"format": {"duration": str(frames / fps), "size": dest.stat().st_size},
                  "streams": [{"width": width, "height": height, "fps": fps}]}
        return report
    except Exception:
        dest.unlink(missing_ok=True)
        raise


def discover_elsewhere():
    """Independent catalogues are leads only, never automatic rights clearance."""
    sys.path.insert(0, str(Path("src").resolve()))
    from public_archive_sources_v1 import search
    found = []
    for provider in ("archive", "loc"):
        try:
            result = search(provider, "The Mark of Zorro 1920", 4)
            found.append({"provider": provider, "items": result["items"],
                          "status": "DISCOVERY_ONLY_RIGHTS_AND_BYTES_UNVERIFIED"})
        except Exception as error:
            found.append({"provider": provider, "error_type": type(error).__name__})
    record("INDEPENDENT_ARCHIVE_FALLBACK_CANDIDATES.json", found)
    return found


def make_scout(info, item, probe, failures):
    p = OUTPUT
    source = p / "SOURCE.mp4"
    cap = cv2.VideoCapture(str(source))
    if not cap.isOpened():
        raise RuntimeError("EXCERPT_DECODE_FAILED")
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if fps <= 0 or count < 50:
        raise RuntimeError("BAD_EXCERPT_FPS")
    duration = count / fps
    detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    board = Image.new("RGB", (1600, 1060), (18, 20, 22))
    pen = ImageDraw.Draw(board)
    samples = []
    for i in range(20):
        t = min(duration - 0.5, (i + 0.5) * duration / 20)
        frame_idx = round(t * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ok, frame = cap.read()
        if not ok:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(cv2.equalizeHist(gray),
                                          minNeighbors=5, minSize=(48, 48))
        h, w = frame.shape[:2]
        sharpness = float(cv2.Laplacian(gray, cv2.CV_32F).var())
        relative_faces = sum(min(float(bw * bh) / (w * h), .15)
                             for x, y, bw, bh in faces)
        score = relative_faces + .000004 * sharpness
        samples.append({"relative_time_s": round(t, 3),
                        "original_time_s": round(OFFSET_SECONDS + t, 3),
                        "frame": frame_idx, "face_count_auto_not_validated": len(faces),
                        "relative_face_area": round(relative_faces, 5),
                        "sharpness": round(sharpness, 1), "rank_score": score})
        for x, y, bw, bh in faces:
            cv2.rectangle(frame, (x, y), (x + bw, y + bh), (0, 225, 255), 2)
        thumb = Image.fromarray(cv2.cvtColor(cv2.resize(frame, (312, 234)),
                                            cv2.COLOR_BGR2RGB))
        xx = (i % 5) * 320
        yy = (i // 5) * 265
        board.paste(thumb, (xx + 4, yy + 26))
        pen.text((xx + 4, yy + 3), f"t={OFFSET_SECONDS+t:.1f}s faces={len(faces)}",
                 fill="white")
    cap.release()
    if len(samples) < 12:
        raise RuntimeError("INSUFFICIENT_SAMPLED_FRAMES")
    board.save(p / "ACTUAL_FILM_CONTACT_SHEET.jpg", quality=90)
    best = max(samples, key=lambda row: row["rank_score"])
    cap = cv2.VideoCapture(str(source))
    cap.set(cv2.CAP_PROP_POS_FRAMES, best["frame"])
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError("ANCHOR_FRAME_DECODE_FAILURE")
    cv2.imwrite(str(p / "EXACT_ORIGINAL_ANCHOR.png"), frame)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    report = {
        "status": "TRUE_SHORT_SOURCE_EXCERPT_AND_FACE_SCOUT_ONLY_NOT_FINAL",
        "film": "The Mark of Zorro (1920)",
        "source_variant": item[0], "source_title": item[1],
        "source_original_file_sha1_from_commons": info.get("sha1"),
        "source_original_reported_bytes": info.get("size"),
        "source_original_reported_width": info.get("width"),
        "source_original_reported_height": info.get("height"),
        "excerpt_sha256": digest, "excerpt_original_offset_s": OFFSET_SECONDS,
        "excerpt_duration_s": duration, "excerpt_resolution": [
            int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or frame.shape[1],
            int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or frame.shape[0]],
        "selected_relative_s": best["relative_time_s"],
        "selected_original_timecode_s": best["original_time_s"],
        "selected_excerpt_frame_index": best["frame"],
        "samples": samples, "failed_prior_candidates": failures,
        "rights_italy": "PENDING_REVIEW_FOR_FILM_AND_DIGITAL_COPY",
        "human_face_fidelity": "PENDING_VISUAL_REVIEW",
        "reconstructed_i2i_images": 0, "vidu_paid_calls": 0,
        "new_final_mp4": False, "published": False}
    record("SOURCE_LOCK_QA.json", report)
    print("TRUE_ARCHIVAL_EXCERPT_AND_CONTACT_SHEET_READY",
          item[0], "selected_original_seconds", best["original_time_s"],
          "NO_I2I_NO_VIDU_NO_FINAL", flush=True)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    failures = []
    for item in TITLES:
        key, title, expected_w, expected_h = item
        try:
            info, url = source_metadata(title)
            if int(info.get("width", 0)) < expected_w or int(info.get("height", 0)) < expected_h:
                raise RuntimeError("ARCHIVE_COPY_RESOLUTION_CHANGED")
            # The 1080p original is 1.36 GB; NEVER download the whole film.
            print("TRY_BOUNDED_REMOTE_EXCERPT", key, "source_bytes", info.get("size"),
                  "excerpt_s", SEGMENT_SECONDS, flush=True)
            probe = excerpt(url)
            record("COMMONS_SOURCE_METADATA.json", {
                "title": title, "width": info.get("width"),
                "height": info.get("height"), "size": info.get("size"),
                "sha1": info.get("sha1"),
                "rights_pending": True})
            make_scout(info, item, probe, failures)
            return
        except Exception as error:
            failures.append({"candidate": key, "failure_type": type(error).__name__,
                             "reason": str(error)[:180]})
            print("ARCHIVE_CANDIDATE_FAILED_MOVE_TO_NEXT", key,
                  type(error).__name__, flush=True)
    discovered = discover_elsewhere()
    record("SOURCE_LOCK_QA.json", {
        "status": "INDEPENDENT_ARCHIVE_FALLBACK_DISCOVERED_NO_VERIFIED_VIDEO",
        "film": "The Mark of Zorro (1920)",
        "failed_candidates": failures, "alternative_catalogues_checked": [
            row["provider"] for row in discovered],
        "next_step": "Evaluate different verified HD film or same-film independent scan",
        "no_fake_film": True, "new_final_mp4": False, "new_vidu_paid_calls": 0,
        "rights_italy": "PENDING", "published": False})
    print("ZORRO_NOT_YET_VERIFIED_INDEPENDENT_DISCOVERY_RECORDED", flush=True)


if __name__ == "__main__":
    main()
