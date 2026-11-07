#!/usr/bin/env python3
"""V292: source-only scout for a genuinely NEW single-episode cinematic candidate.

Gets the original Commons byte stream, checks its SHA1 and native geometry,
and renders side-by-side full-frame/9:16 contact sheets from decoded video.
NO still reconstruction, Vidu POST, approval, social or completed video.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

FILENAME = "Les Cartes vivantes (1904).webm"
FILE_PAGE = "https://commons.wikimedia.org/wiki/File:Les_Cartes_vivantes_(1904).webm"
SHA1 = "9b144141b51ef50bc74fe40a5fd3882cc312f81c"
ORIGINAL_SIZE = 23831680
FILENAME_PARAM = "File:" + FILENAME
ARCHIVE_IDENTIFIER = "silent-les-cartes-vivantes-aka-the-living-playing-cards"


def _request(url: str, timeout: int = 60):
    req = urllib.request.Request(url, headers={
        "User-Agent": "StoriaRiviveResearch/1.0 (public-domain-film-audit; no-billing)",
        "Accept": "*/*",
    })
    for attempt in range(3):
        try:
            return urllib.request.urlopen(req, timeout=timeout)
        except urllib.error.HTTPError as error:
            if error.code not in (429, 503) or attempt == 2:
                raise
            try:
                retry_after = int(error.headers.get("Retry-After", "0"))
            except (ValueError, TypeError):
                retry_after = 0
            # Respect long backoffs by stopping, rather than hammering Wikimedia.
            if retry_after > 120:
                raise RuntimeError("UPSTREAM_RATE_LIMIT_RETRY_LATER") from error
            delay = max(retry_after, 25 * (attempt + 1))
            print(f"UPSTREAM_HTTP_{error.code}_WAIT_{delay}_SECONDS_NO_DUPLICATE_DOWNLOAD", flush=True)
            time.sleep(delay)


def _run(args: list[str], timeout: int = 120) -> str:
    p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       text=True, timeout=timeout)
    if p.returncode:
        raise RuntimeError("MEDIA_TOOL_FAILED " + " ".join(args[:4]) +
                           " STDERR:" + p.stderr[-600:])
    return p.stdout


def _digest(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def source_url() -> str:
    query = urllib.parse.urlencode({
        "action": "query", "format": "json", "titles": FILENAME_PARAM,
        "prop": "imageinfo", "iiprop": "url|size|sha1"})
    api = "https://commons.wikimedia.org/w/api.php?" + query
    with _request(api, 30) as response:
        data = json.load(response)
    pages = data.get("query", {}).get("pages", {})
    infos = [page["imageinfo"][0] for page in pages.values()
             if page.get("imageinfo") and page.get("title") == FILENAME_PARAM]
    if len(infos) != 1:
        raise RuntimeError("COMMONS_EXACT_FILE_METADATA_NOT_FOUND")
    info = infos[0]
    if info.get("size") != ORIGINAL_SIZE:
        raise RuntimeError("COMMONS_FILE_SIZE_CHANGED_REVIEW_REQUIRED")
    url = info.get("url", "")
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != "upload.wikimedia.org":
        raise RuntimeError("COMMONS_SOURCE_URL_UNTRUSTED")
    return url


def download_original(url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with _request(url, 120) as response, target.open("wb") as out:
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            out.write(block)
            if out.tell() > ORIGINAL_SIZE:
                raise RuntimeError("COMMONS_ORIGINAL_OVER_SIZE")
    if target.stat().st_size != ORIGINAL_SIZE:
        raise RuntimeError("COMMONS_ORIGINAL_SIZE_MISMATCH")
    if _digest(target, "sha1") != SHA1:
        raise RuntimeError("COMMONS_ORIGINAL_SHA1_MISMATCH")



def _archive_fallback(folder: Path) -> tuple[Path, str, str, int]:
    """One alternate PD film encode; verify its OWN Archive metadata SHA1.

    This is NOT the Commons-verified SHA1 and must never be represented
    as the same byte-identical source.
    """
    base = "https://archive.org"
    meta_url = base + "/metadata/" + ARCHIVE_IDENTIFIER
    with _request(meta_url, 40) as response:
        metadata = json.load(response)
    if metadata.get("is_dark") or not isinstance(metadata.get("files"), list):
        raise RuntimeError("ARCHIVE_METADATA_UNAVAILABLE")
    choices = []
    for entry in metadata["files"]:
        name = entry.get("name", "")
        size = int(entry.get("size", "0") or 0)
        sha1 = entry.get("sha1", "")
        if (isinstance(name, str)
                and name.lower().endswith((".mp4", ".mpeg", ".mpg", ".ogv", ".webm"))
                and 1000000 <= size <= 130000000
                and isinstance(sha1, str) and len(sha1) == 40
                and all(c in "0123456789abcdef" for c in sha1.lower())):
            choices.append((entry.get("source") == "original", size, name, sha1))
    if not choices:
        raise RuntimeError("ARCHIVE_NO_VETTED_FILM_ENCODE")
    # Single retrieval: original film encode first, best byte-size next.
    choices.sort(reverse=True)
    _, size, filename, sha1 = choices[0]
    url = (base + "/download/" + ARCHIVE_IDENTIFIER + "/" +
           urllib.parse.quote(filename, safe="/"))
    target = folder / ("ARCHIVE_ALTERNATE_FILM" + Path(filename).suffix.lower())
    target.parent.mkdir(parents=True, exist_ok=True)
    with _request(url, 120) as response, target.open("wb") as out:
        for block in iter(lambda: response.read(1024 * 1024), b""):
            out.write(block)
            if out.tell() > size:
                raise RuntimeError("ARCHIVE_ORIGINAL_OVERSIZED")
    if target.stat().st_size != size or _digest(target, "sha1") != sha1:
        raise RuntimeError("ARCHIVE_ORIGINAL_METADATA_SHA1_OR_SIZE_MISMATCH")
    return target, url, sha1, size


def _probe(src: Path) -> dict:
    data = json.loads(_run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                            "-show_entries", "stream=width,height,codec_name,r_frame_rate:format=duration",
                            "-of", "json", str(src)]))
    streams = data.get("streams", [])
    if len(streams) != 1:
        raise RuntimeError("MISSING_OR_MULTIPLE_ARCHIVAL_VIDEO_STREAMS")
    width, height = int(streams[0]["width"]), int(streams[0]["height"])
    if width < 640 or height < 420:
        raise RuntimeError("ORIGINAL_RASTER_TOO_SMALL_FOR_PHOTOREALISM")
    duration = float(data["format"]["duration"])
    if not 150 <= duration <= 190:
        raise RuntimeError("ALTERNATE_ARCHIVE_DURATION_NOT_SAME_FILM_VERIFY")
    return {"original_resolution": [width, height], "duration": round(duration, 3),
            "codec": streams[0].get("codec_name"), "frame_rate": streams[0].get("r_frame_rate")}


def _sheet(images: list[tuple[float, Path]], portrait: bool, destination: Path):
    thumb_size = (154, 272) if portrait else (254, 190)
    ncols = 6
    nrows = (len(images) + ncols - 1) // ncols
    width = ncols * (thumb_size[0] + 12) + 12
    height = nrows * (thumb_size[1] + 30) + 12
    output = Image.new("RGB", (width, height), (23, 25, 28))
    pen = ImageDraw.Draw(output)
    for i, (time, path) in enumerate(images):
        with Image.open(path) as frame:
            frame = frame.convert("RGB")
            if portrait:
                source_width, source_height = frame.size
                crop_width = round(source_height * 9 / 16)
                x1 = (source_width - crop_width) // 2
                frame = frame.crop((x1, 0, x1 + crop_width, source_height))
            view = ImageOps.fit(frame, thumb_size, method=Image.Resampling.LANCZOS)
        x = 12 + (i % ncols) * (thumb_size[0] + 12)
        y = 12 + (i // ncols) * (thumb_size[1] + 30)
        output.paste(view, (x, y))
        pen.text((x, y + thumb_size[1] + 2), f"{time:.1f}s", fill=(245, 245, 245))
    output.save(destination, quality=90, optimize=True)


def main():
    root = Path("output/storia_single_cinema_v292")
    root.mkdir(parents=True, exist_ok=True)
    preview_json = root / "CINEMA_ORIGINAL_SOURCE_PREFLIGHT.json"
    src = root / FILENAME.replace(" ", "_")
    url = source_url()
    origin = "COMMONS_ORIGINAL_SHA1_EXACT"
    original_sha1, original_bytes = SHA1, ORIGINAL_SIZE
    try:
        download_original(url, src)
    except urllib.error.HTTPError as e:
        if e.code != 429:
            raise
        print("COMMONS_HTTP429_ON_FILE_BYTES_FETCH_ARCHIVE_ALTERNATIVE_ONCE")
        src, url, original_sha1, original_bytes = _archive_fallback(root)
        origin = "INTERNET_ARCHIVE_DIFFERENT_ENCODE_SHA1_VALIDATED_NEEDS_ARTISTIC_AND_SOURCE_REVIEW"
    tech = _probe(src)
    samples = []
    with tempfile.TemporaryDirectory(prefix="cinema-source-v292-") as d:
        tmp = Path(d)
        for idx in range(28):
            timestamp = 4.0 + (tech["duration"] - 8.0) * (idx + 0.5) / 28.0
            target = tmp / f"original_{idx:03d}.png"
            _run(["ffmpeg", "-nostdin", "-v", "error", "-ss", str(timestamp),
                  "-i", str(src), "-frames:v", "1", "-y", str(target)], 45)
            with Image.open(target) as im:
                if im.size != tuple(tech["original_resolution"]):
                    raise RuntimeError("SOURCE_DECODED_FRAME_BAD_GEOMETRY")
            samples.append((float(timestamp), target))
        if len(samples) != 28:
            raise RuntimeError("WRONG_SAMPLE_COUNT")
        _sheet(samples, False, root / "ACTUAL_FILM_FRAMES_ORIGINAL_ASPECT.jpg")
        _sheet(samples, True, root / "ACTUAL_FILM_FRAMES_VERTICAL_CROP.jpg")
    report = {
        "version": "V292_NEW_SINGLE_CINEMATIC_FILM_SOURCE_SCOUT",
        "status": "ORIGINAL_FILM_FRAMES_READY_FOR_ARTISTIC_SELECTION_NOT_FINAL",
        "film": "Les Cartes vivantes / The Living Playing Cards",
        "original_year": 1904,
        "creator": "Georges Méliès (died 1938)",
        "source_page": FILE_PAGE,
        "actual_download_url": url,
        "source_material_provenance": origin,
        "is_exact_commons_original_bytes": origin == "COMMONS_ORIGINAL_SHA1_EXACT",
        "original_sha1": original_sha1,
        "original_sha256": _digest(src, "sha256"),
        "original_bytes": original_bytes,
        "native_geometry": tech,
        "source_rights_claim": "Commons marks 1904 film PD; Internet Archive alternate copy not independently cleared; Italy extra transfer rights still require final check",
        "italian_release_rights_final_cleared": False,
        "frames_sampled_on_real_decoded_file": 28,
        "samples_seconds": [t for t, _ in samples],
        "vertical_crop_keeps_full_actor_and_props": "PENDING_VISUAL_REVIEW",
        "one_reconstruction_model_test": "NOT_YET_RUN",
        "new_vidu_task": "NOT_SUBMITTED",
        "new_final_mp4": False,
        "final_kit_zip": False,
        "published": False,
        "prior_sf1906_reused": False,
        "positive_reference_video_files": ["44359.mp4", "43055.mp4", "43056.mp4", "43054.mp4"],
        "negative_reference_video_files": ["44518.mp4"]
    }
    preview_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print("V292_ACTUAL_CINEMATIC_SOURCE_BYTES_SHA1_VERIFIED",
          report["original_sha256"], "frames", len(samples))
    print("V292_NEEDS_SOURCE_CROP_AND_I2I_ARTISTIC_REVIEW_NO_VIDU_NO_FINAL")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        # A failed source download is never silently treated as a finished video.
        root = Path("output/storia_single_cinema_v292")
        root.mkdir(parents=True, exist_ok=True)
        report = {
            "version": "V292_NEW_SINGLE_CINEMATIC_FILM_SOURCE_SCOUT",
            "status": "SOURCE_PREFLIGHT_BLOCKED_NO_FINAL",
            "failure_type": type(error).__name__,
            "failure_summary": str(error)[:400],
            "source_page": FILE_PAGE,
            "real_frames_ready": False,
            "final_mp4": False,
            "final_kit_zip": False,
            "published": False,
        }
        (root / "CINEMA_ORIGINAL_SOURCE_PREFLIGHT.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
        raise
