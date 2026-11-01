#!/usr/bin/env python3
"""V173 archival film scanner: look for a *genuinely detailed* close-up source.

Candidate: Prelinger 'Modes of the Moment' (1917), identifier Modesoft1917.
Read-only Internet Archive metadata; optionally inspect video bytes up to 160 MiB.
Never interprets a Public Domain US label as independently cleared Italian rights.
No AI generation, no Vidu, no purchases, no social output. Do not publish media.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

IDENTIFIER = "Modesoft1917"
METADATA_URL = "https://archive.org/metadata/" + IDENTIFIER
SOURCE_PAGE = "https://archive.org/details/" + IDENTIFIER
MAX_BYTES = 160 * 1024 * 1024
FILM_EXTENSIONS = (".mp4", ".m4v", ".mov", ".ogv", ".webm", ".mpg", ".mpeg")
# These are real different shots of the SAME coherent 1917 fashion newsreel,
# not five crops of one still; timestamps are scouting hypotheses, not approvals.
FRAME_PTS = (23.0, 53.5, 68.0, 166.0, 207.0)
MIN_RESEARCH_WIDTH = 960
MIN_RESEARCH_HEIGHT = 720
USER_AGENT = "LaStoriaRivive/1.0 (GGIANLUCAA/Tra-le-pagine-; public historical research)"


def safe_filename(value: object) -> str:
    if not isinstance(value, str) or len(value) > 180:
        raise ValueError("BAD_FILE_NAME")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 ._()+'-]*", value):
        raise ValueError("UNTRUSTED_ARCHIVE_FILE_NAME")
    if ".." in value or value.startswith("."):
        raise ValueError("UNTRUSTED_ARCHIVE_FILE_NAME")
    if not value.lower().endswith(FILM_EXTENSIONS):
        raise ValueError("NOT_VIDEO_EXTENSION")
    return value


def public_domain_label(metadata: dict) -> bool:
    url = str(metadata.get("licenseurl", "")).strip().lower()
    return url in {
        "http://creativecommons.org/licenses/publicdomain/",
        "https://creativecommons.org/licenses/publicdomain/",
        "https://creativecommons.org/publicdomain/mark/1.0/",
        "http://creativecommons.org/publicdomain/mark/1.0/",
        "https://creativecommons.org/publicdomain/zero/1.0/",
        "http://creativecommons.org/publicdomain/zero/1.0/",
    }


def candidate_files(files: list[dict]) -> list[dict]:
    found = []
    for entry in files:
        try:
            name = safe_filename(entry.get("name"))
            size = int(entry.get("size", 0))
        except (ValueError, TypeError):
            continue
        if size <= 0:
            continue
        source = str(entry.get("source", ""))
        fmt = str(entry.get("format", ""))[:100]
        if source == "metadata":
            continue
        found.append({
            "name": name, "size_bytes": size,
            "source": source, "format": fmt,
            "under_160mib_cap": size <= MAX_BYTES,
            "archive_file_url": "https://archive.org/download/" + IDENTIFIER + "/" + quote(name),
            "sha1_expected": entry.get("sha1") if re.fullmatch(r"[a-f0-9]{40}", str(entry.get("sha1", "")).lower()) else None,
        })
    # Native/original video is preferred over the smaller convenience derivative.
    # With no ffprobe, NEVER equate file size or format label with actual resolution.
    found.sort(key=lambda x: (x["source"] == "original", x["size_bytes"]), reverse=True)
    return found


def choose_bounded(candidates: list[dict]) -> dict | None:
    bounded = [c for c in candidates if c["under_160mib_cap"]]
    # Prefer larger bounded candidate to low-bitrate derivatives. No inference of pixels.
    return max(bounded, key=lambda x: (x["source"] == "original", x["size_bytes"])) if bounded else None


def get_metadata() -> dict:
    request = Request(METADATA_URL, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=45) as response:
        result = json.load(response)
    if not isinstance(result, dict) or not isinstance(result.get("metadata"), dict):
        raise ValueError("ARCHIVE_METADATA_MISSING")
    identifier = result.get("metadata", {}).get("identifier")
    if identifier != IDENTIFIER:
        raise ValueError("ARCHIVE_IDENTIFIER_MISMATCH")
    return result


def stream_original(selected: dict, target: Path) -> dict:
    safe_filename(selected["name"])
    expected = int(selected["size_bytes"])
    if expected <= 0 or expected > MAX_BYTES:
        raise ValueError("ORIGINAL_OVER_BYTE_CAP")
    target.parent.mkdir(parents=True, exist_ok=True)
    sha1 = hashlib.sha1()
    sha256 = hashlib.sha256()
    n = 0
    try:
        request = Request(selected["archive_file_url"], headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=90) as source, target.open("wb") as out:
            while True:
                block = source.read(1024 * 1024)
                if not block:
                    break
                n += len(block)
                if n > MAX_BYTES:
                    raise ValueError("ACTUAL_DOWNLOAD_EXCEEDED_BYTE_CAP")
                out.write(block)
                sha1.update(block)
                sha256.update(block)
        if n != expected:
            raise ValueError("ORIGINAL_LENGTH_MISMATCH")
        declared_sha1 = selected.get("sha1_expected")
        if declared_sha1 and sha1.hexdigest() != declared_sha1:
            raise ValueError("ORIGINAL_SHA1_MISMATCH")
        return {"video_source_bytes_sha256": sha256.hexdigest(),
                "video_source_bytes_sha1": sha1.hexdigest(),
                "downloaded_real_bytes": n}
    except Exception:
        target.unlink(missing_ok=True)
        raise


def probe(path: Path) -> dict:
    command = ["ffprobe", "-v", "error", "-show_entries",
               "stream=codec_type,codec_name,width,height,sample_aspect_ratio:format=duration",
               "-of", "json", str(path)]
    run = subprocess.run(command, capture_output=True, text=True, timeout=35, check=True)
    details = json.loads(run.stdout)
    vid = next((s for s in details.get("streams", []) if s.get("codec_type") == "video"), None)
    if not vid:
        raise ValueError("NOT_A_VIDEO_STREAM")
    w, h = int(vid["width"]), int(vid["height"])
    duration = float(details["format"]["duration"])
    if w < 100 or h < 100 or duration < 215:
        raise ValueError("SOURCE_RASTER_OR_DURATION_INVALID")
    return {"width": w, "height": h, "duration_s": duration,
            "video_codec": vid.get("codec_name"),
            "sample_aspect_ratio": vid.get("sample_aspect_ratio"),
            "true_native_720p_or_better": w >= MIN_RESEARCH_WIDTH and h >= MIN_RESEARCH_HEIGHT}


def contact_sheet(source: Path, out: Path) -> dict:
    """Extract five actual nonadjacent historical shots; never alter the original."""
    from PIL import Image, ImageDraw
    out.mkdir(parents=True, exist_ok=True)
    board = Image.new("RGB", (5 * 320, 380), (20, 20, 20))
    draw = ImageDraw.Draw(board)
    written = []
    for i, sec in enumerate(FRAME_PTS, 1):
        target = out / f"REAL_SOURCE_SHOT_{i:02d}.png"
        cmd = ["ffmpeg", "-nostdin", "-y", "-v", "error", "-ss",
               str(sec), "-i", str(source), "-frames:v", "1", str(target)]
        subprocess.run(cmd, capture_output=True, timeout=45, check=True)
        if not target.is_file() or target.stat().st_size < 2000:
            raise RuntimeError("ACTUAL_ARCHIVE_FRAME_MISSING")
        with Image.open(target) as p:
            im = p.convert("RGB")
        im.thumbnail((312, 338))
        board.paste(im, ((i-1)*320 + (320-im.width)//2, 36 + (338-im.height)//2))
        draw.text(((i-1)*320+9, 12), f"REAL FILM at {sec:.1f}s", fill="white")
        written.append({"shot": i, "pts_seconds": sec, "filename": target.name,
                        "source_shot_width": im.width, "source_shot_height": im.height})
    board.save(out/"REAL_FIVE_SHOTS_PRIVATE_REVIEW.jpg", quality=89)
    return {"sampled_original_shots": written, "five_source_frames_really_decoded": True}


def run(out: Path, do_download: bool) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    report = {
        "version": "V173", "candidate": "Modes of the Moment, 1917",
        "archive_id": IDENTIFIER, "source_page": SOURCE_PAGE,
        "licensed_for_italian_publication": False,
        "italian_rights_review": "PENDING_NOT_CLEARED",
        "source_footage_human_art_qa": "PENDING",
        "reference_43055_43056_photo_motion_quality": "UNVERIFIED",
        "real_four_photo_i2i": 0, "real_vidu": 0,
        "paid_calls": 0, "published": False,
        "no_new_video_master_claimed": True,
    }
    try:
        data = get_metadata()
        meta = data["metadata"]
        report["rights_declared_archive_public_domain"] = public_domain_label(meta)
        report["metadata_title"] = str(meta.get("title", ""))[:160]
        report["metadata_date"] = str(meta.get("date", ""))[:100]
        report["listed_video_files"] = candidate_files(data.get("files", []))
        if not public_domain_label(meta):
            report["status"] = "BLOCKED_EXACT_ARCHIVE_PUBLIC_DOMAIN_MARK_MISSING"
            return report
        chosen = choose_bounded(report["listed_video_files"])
        if not chosen:
            report["status"] = "BLOCKED_NO_VIDEO_UNDER_160MIB_NO_DOWNLOAD"
            return report
        report["chosen_candidate"] = chosen
        if not do_download:
            report["status"] = "METADATA_ONLY_REAL_RASTER_UNVERIFIED"
            return report
        source = out/("ORIGINAL_RESEARCH_SOURCE" + Path(chosen["name"]).suffix.lower())
        report.update(stream_original(chosen, source))
        report["actual_ffprobe"] = probe(source)
        report.update(contact_sheet(source, out))
        if not report["actual_ffprobe"]["true_native_720p_or_better"]:
            report["status"] = "REJECT_LOW_NATIVE_RASTER_FOR_PHOTOREAL_MOTION"
        else:
            report["status"] = "REAL_FIVE_FRAME_REVIEW_REQUIRED_NOT_PRODUCTION_CLEARED"
        return report
    except Exception as exc:
        report["status"] = "SCOUT_BLOCKED_NO_PRODUCTION"
        report["error_type"] = type(exc).__name__
        report["error_summary"] = str(exc)[:300]
        return report
    finally:
        # Entire archive stays ephemeral; only PNG/QA are uploaded privately.
        for media in out.glob("ORIGINAL_RESEARCH_SOURCE.*"):
            media.unlink(missing_ok=True)
        (out/"V173_FASHION_SOURCE_QUALITY_AUDIT.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--download", action="store_true")
    args = ap.parse_args()
    result = run(args.out, args.download)
    print(json.dumps({
        "status": result["status"],
        "source_archive": IDENTIFIER,
        "selected_video_file": result.get("chosen_candidate", {}).get("name", ""),
        "true_native_dimensions": result.get("actual_ffprobe", {}).get("width", None),
        "native_height": result.get("actual_ffprobe", {}).get("height", None),
        "paid_calls": 0, "published": False,
    }))


if __name__ == "__main__":
    main()
