#!/usr/bin/env python3
"""V217 four-film source-byte qualification. Research only, never FINAL or paid."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import re
import subprocess
from pathlib import Path

from PIL import Image, ImageChops, ImageOps, ImageStat

MANIFEST_VERSION = "V217_FOUR_PILOTS_SOURCE_SHORTLIST"
SCOUT_READY = "REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW"
SELECTION_READY = "FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW"
EPISODE_RE = re.compile(r"[a-z0-9_]{8,64}\Z")


def read_manifest(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("version") != MANIFEST_VERSION:
        raise ValueError("INVALID_V217_MANIFEST")
    if any(value.get(flag) is not False for flag in
           ("credit_spend_allowed", "publish_allowed", "italian_rights_approved")):
        raise ValueError("V217_MANIFEST_UNSAFE_PERMISSIONS")
    items = value.get("episodes")
    if not isinstance(items, list) or len(items) != 4:
        raise ValueError("EXACTLY_FOUR_EPISODES_REQUIRED")
    ids, pages = set(), set()
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("INVALID_EPISODE")
        identifier, page = item.get("id"), item.get("source_page")
        if not isinstance(identifier, str) or not EPISODE_RE.fullmatch(identifier):
            raise ValueError("INVALID_EPISODE_ID")
        if (not isinstance(page, str) or not page.startswith(
                "https://commons.wikimedia.org/wiki/File:") or
                any(c in page for c in ("\n", "\r", "#", "?"))):
            raise ValueError("UNSAFE_ARCHIVE_SOURCE")
        if identifier in ids or page in pages:
            raise ValueError("DUPLICATED_EPISODE_OR_ARCHIVE_SOURCE")
        ids.add(identifier)
        pages.add(page)
        if item.get("rights_status", "").endswith("ITALIAN_RIGHTS_NOT_REVIEWED") is False:
            raise ValueError("RIGHTS_STATUS_CANNOT_BE_PREAPPROVED")
    return value


def episode(manifest: dict, episode_id: str) -> dict:
    for item in manifest["episodes"]:
        if item["id"] == episode_id:
            return item
    raise ValueError("UNKNOWN_EPISODE")


def prepare(manifest: dict, episode_id: str, out: Path) -> dict:
    item = episode(manifest, episode_id)
    out.mkdir(parents=True, exist_ok=True)
    order = {
        "contract": "LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT",
        "cycle_id": "v217_four_unique_source_research",
        "episode_id": episode_id,
        "source_page": item["source_page"],
        "paid_api_call_permitted": False,
        "publish_permitted": False,
        "italian_rights_verified": False,
    }
    (out / "WORK_ORDER.json").write_text(
        json.dumps(order, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return order


def safe_read(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, UnicodeError, ValueError):
        return {}


def endpoint_alignment(clip: Path, reference: Path) -> dict:
    """Compare the DECODED preview endpoint with the actual selected archival PNG.

    A candidate timecode is only advisory: a cut or seek error can leave a
    title card in the preview while its chosen PNG depicts a different shot.
    Ignore the preview's top text overlay, never infer source lock from names.
    """
    if reference.is_symlink() or not reference.is_file() or not re.fullmatch(
            r"frame_(0[1-9]|1[0-2])\.png", reference.name):
        raise ValueError("INVALID_SOURCE_REFERENCE_FRAME")
    with Image.open(reference) as original:
        if original.format != "PNG":
            raise ValueError("INVALID_SOURCE_REFERENCE_FORMAT")
        source = ImageOps.fit(original.convert("L"), (144, 256)).crop((0, 32, 144, 256))
    decoded = subprocess.run(
        ["ffmpeg", "-nostdin", "-hide_banner", "-v", "error",
         "-i", str(clip), "-an", "-vf", "reverse",
         "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "pipe:1"],
        check=True, capture_output=True, timeout=35)
    with Image.open(io.BytesIO(decoded.stdout)) as image:
        actual = image.convert("L").resize((144, 256)).crop((0, 32, 144, 256))
    raw = ImageStat.Stat(ImageChops.difference(source, actual)).mean[0]
    normalized = ImageStat.Stat(ImageChops.difference(
        ImageOps.autocontrast(source), ImageOps.autocontrast(actual))).mean[0]
    # Conservative pixelwise preflight, NOT exact-frame or artistic approval.
    return {"source_frame": reference.name,
            "source_frame_sha256": hashlib.sha256(reference.read_bytes()).hexdigest(),
            "luma_mae": round(raw, 2),
            "contrast_mae": round(normalized, 2),
            "endpoint_visually_aligned": raw <= 24 and normalized <= 38}


def render_source_only_preview(
        film: Path, timestamps: list[float], out: Path,
        reference_frames: list[Path]) -> dict:
    """Actual source motion, rejected if its endpoint mismatches source PNG."""
    if (film.is_symlink() or not film.is_file() or len(timestamps) != 5
            or len(reference_frames) != 5):
        raise ValueError("INVALID_SOURCE_PREVIEW_INPUT")
    out.mkdir(exist_ok=True, parents=True)
    clips = []
    alignment = []
    for idx, timestamp in enumerate(timestamps):
        if (isinstance(timestamp, bool) or not isinstance(timestamp, (float, int))
                or not math.isfinite(timestamp) or timestamp < 1.3):
            raise ValueError("INVALID_REVIEW_TIMESTAMP")
        clip = out / ("SOURCE_SHOT_%02d.mp4" % (idx + 1))
        cmd = [
            "ffmpeg", "-nostdin", "-hide_banner", "-v", "error", "-y",
            "-ss", "%.3f" % (timestamp - 1.2), "-i", str(film),
            "-t", "1.2", "-an", "-vf",
            "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,"
            "scale=720:1280:flags=lanczos,setsar=1,"
            "format=gray,drawtext=text='SOURCE REVIEW - NOT FINAL':"
            "fontcolor=white:fontsize=24:x=(w-text_w)/2:y=40,"
            "format=yuv420p,fps=24",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "24",
            "-movflags", "+faststart", str(clip)]
        subprocess.run(cmd, check=True, capture_output=True, timeout=90)
        clips.append(clip)
        match = endpoint_alignment(clip, reference_frames[idx])
        match["selected_timecode_s"] = round(float(timestamp), 3)
        alignment.append(match)
    (out / "SOURCE_ENDPOINT_ALIGNMENT_V223.json").write_text(
        json.dumps({"version": "V223_SOURCE_PREVIEW_ENDPOINT_EVIDENCE",
                    "alignment_is_not_exact_frame_certification": True,
                    "checks": alignment}, indent=2) + "\n", encoding="utf-8")
    if not all(item["endpoint_visually_aligned"] for item in alignment):
        raise ValueError("SOURCE_PREVIEW_FRAME_MISMATCH")
    paths = out / "concat.txt"
    # All clips live in the same controlled working directory; no user paths.
    paths.write_text("".join("file '%s'\n" % p.name for p in clips), encoding="utf-8")
    preview = out / "SOURCE_REVIEW_ONLY_NOT_FINAL.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-v", "error", "-y",
                    "-f", "concat", "-safe", "0", "-i", str(paths.resolve()),
                    "-c:v", "copy", "-movflags", "+faststart", str(preview.resolve())],
                   check=True, capture_output=True, timeout=50, cwd=out)
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=width,height,codec_name:format=duration", "-of",
         "json", str(preview.resolve())],
        check=True, capture_output=True, text=True, timeout=30)
    data = json.loads(probe.stdout)
    video = next((s for s in data.get("streams", []) if s.get("codec_name") == "h264"), {})
    duration = float(data.get("format", {}).get("duration", 0))
    if video.get("width") != 720 or video.get("height") != 1280 or not 5 <= duration <= 7.5:
        raise ValueError("REVIEW_VIDEO_FAILED_REAL_MEDIA_QA")
    return {"review_preview": preview.name, "duration_s": round(duration, 3),
            "width": 720, "height": 1280, "source_shots": 5, "real_source_motion": True,
            "has_i2i_photos": False, "has_vidu_clip": False, "final_video": False,
            "source_endpoint_alignment_evidence": "SOURCE_ENDPOINT_ALIGNMENT_V223.json",
            "source_endpoint_match_is_not_exact_frame_certification": True}


def finish(manifest: dict, episode_id: str, cache: Path, output: Path) -> dict:
    item = episode(manifest, episode_id)
    scout = safe_read(cache / "SCOUT_REPORT.json")
    selection = safe_read(output / "SHOT_AWARE_SELECTION_V210.json")
    result = {
        "version": MANIFEST_VERSION, "episode_id": episode_id,
        "source_page": item["source_page"],
        "status": "SOURCE_REJECTED",
        "reason": "SOURCE_NOT_READY",
        "italian_rights_verified": False,
        "four_real_i2i_photos": 0, "vidu_animated_clips": 0,
        "finished_mp4": False, "finished_zip": False,
        "credits_spent": 0, "publish_permitted": False,
        "reviewed_by_human": False,
        "artifact_is_only_source_evidence": True
    }
    if scout.get("status") != SCOUT_READY:
        result["reason"] = scout.get("status", "SOURCE_SCOUT_FAILED")
    elif selection.get("status") != SELECTION_READY:
        result["reason"] = selection.get("reason", "SHOT_SELECTION_FAILED")
    else:
        times = selection.get("candidate_segment_times_s", [])
        chosen = selection.get("preselected", [])
        film = cache / "ORIGINAL_ARCHIVE.webm"
        try:
            if (not isinstance(chosen, list) or len(chosen) != 5
                    or any(not isinstance(x, dict) or not isinstance(x.get("filename"), str)
                           or not re.fullmatch(r"frame_(0[1-9]|1[0-2])\.png", x["filename"])
                           for x in chosen)):
                raise ValueError("SOURCE_PREVIEW_INVALID_SELECTED_FRAMES")
            expected = scout.get("original_sha256")
            if (not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected)
                    or film.is_symlink() or not film.is_file()
                    or hashlib.sha256(film.read_bytes()).hexdigest() != expected):
                raise ValueError("SOURCE_PREVIEW_FILM_HASH_MISMATCH")
            references = [cache / "original_frames" / x["filename"] for x in chosen]
            preview = render_source_only_preview(film, times, output, references)
        except ValueError as exc:
            result["reason"] = str(exc) if str(exc).startswith("SOURCE_") else "SOURCE_PREVIEW_INVALID_INPUT"
        except (OSError, subprocess.SubprocessError) as exc:
            result["reason"] = "SOURCE_PREVIEW_RENDER_FAILED_" + type(exc).__name__
        else:
            result.update(preview)
            result["status"] = "FIVE_SOURCE_SHOTS_REVIEW_PENDING"
            result["reason"] = "ARCHIVAL_PREVIEW_ONLY_NOT_I2I_OR_VIDU"
    output.mkdir(exist_ok=True, parents=True)
    (output / "V217_RESEARCH_REPORT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(result["episode_id"], result["status"], result["reason"])
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--episode", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--cache")
    parser.add_argument("--finish", action="store_true")
    args = parser.parse_args()
    manifest = read_manifest(Path(args.manifest))
    out = Path(args.out)
    if args.finish:
        if not args.cache:
            raise ValueError("CACHE_REQUIRED_FOR_FINISH")
        finish(manifest, args.episode, Path(args.cache), out)
    else:
        prepare(manifest, args.episode, out)


if __name__ == "__main__":
    main()
