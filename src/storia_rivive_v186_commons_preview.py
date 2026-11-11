#!/usr/bin/env python3
"""V186: bounded real Wikimedia HD derivative scouting; never a master or native scan.

Read-only download of a public Wikimedia *transcode* for five original-film
frame PREVIEWS. SHA locks the downloaded derivative only, not the 1.64GB
original scan. I2I, Vidu, territorial rights and approval stay blocked.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from storia_rivive_v184_source_intake import inspect_local

FILE_TITLE = "File:A Corner in Wheat (1909).webm"
PAGE = "https://commons.wikimedia.org/wiki/File:A_Corner_in_Wheat_(1909).webm"
API = "https://commons.wikimedia.org/w/api.php"
MAX_BYTES = 420 * 1024 * 1024
MAX_SECONDS = 420
USER_AGENT = "LaStoriaRivive-V186/1.0 (source scouting; github.com/GGIANLUCAA/Tra-le-pagine-)"
FRACTIONS = (0.10, 0.25, 0.42, 0.60, 0.80)


def _trusted_media_url(url):
    parsed = urlparse(url)
    return (parsed.scheme == "https" and parsed.hostname == "upload.wikimedia.org"
            and not parsed.username and not parsed.password and parsed.port in (None, 443))


def select_1080_derivative(derivatives):
    """Reject original/SD and pick the official high-resolution transcode."""
    eligible = []
    for d in derivatives:
        url = d.get("src", "")
        if not _trusted_media_url(url):
            continue
        if not urlparse(url).path.lower().endswith(".webm"):
            continue
        try:
            width, height = int(d.get("width", 0)), int(d.get("height", 0))
        except (ValueError, TypeError):
            continue
        if width >= 1280 and height >= 900 and height <= 1080:
            eligible.append((height, width, url))
    if not eligible:
        raise ValueError("NO_TRUSTED_HD_TRANSCODE")
    eligible.sort(reverse=True)
    h, w, u = eligible[0]
    return {"url": u, "declared_width": w, "declared_height": h,
            "kind": "WIKIMEDIA_COMPRESSED_DERIVATIVE_NOT_ORIGINAL_SCAN"}


def discover_derivative(opener=urlopen):
    query = urlencode({"action": "query", "titles": FILE_TITLE,
                       "prop": "videoinfo", "viprop": "derivatives|url|size",
                       "format": "json"})
    req = Request(API + "?" + query, headers={"User-Agent": USER_AGENT})
    with opener(req, timeout=30) as response:
        obj = json.load(response)
    pages = obj.get("query", {}).get("pages", {})
    if len(pages) != 1:
        raise ValueError("UNEXPECTED_COMMONS_FILE_RESPONSE")
    info = next(iter(pages.values())).get("videoinfo") or []
    if len(info) != 1:
        raise ValueError("COMMONS_VIDEOINFO_MISSING")
    return select_1080_derivative(info[0].get("derivatives") or [])


def bounded_download(url, target, opener=urlopen, max_bytes=MAX_BYTES,
                     max_seconds=MAX_SECONDS):
    if not _trusted_media_url(url):
        raise ValueError("UNTRUSTED_MEDIA_URL")
    target = Path(target)
    if target.exists():
        raise ValueError("DESTINATION_EXISTS")
    partial = target.with_name(target.name + ".part")
    if partial.exists():
        raise ValueError("PARTIAL_FILE_ALREADY_EXISTS")
    request = Request(url, headers={"User-Agent": USER_AGENT})
    started = time.monotonic()
    digest = hashlib.sha256()
    count = 0
    try:
        with opener(request, timeout=45) as response:
            if not _trusted_media_url(response.geturl()):
                raise ValueError("UNTRUSTED_MEDIA_REDIRECT")
            header = response.headers.get("Content-Length")
            if header is not None and int(header) > max_bytes:
                raise ValueError("MEDIA_EXCEEDS_DOWNLOAD_LIMIT")
            with partial.open("xb") as dest:
                while True:
                    if time.monotonic() - started > max_seconds:
                        raise ValueError("DOWNLOAD_TIME_BUDGET_EXCEEDED")
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    count += len(chunk)
                    if count > max_bytes:
                        raise ValueError("MEDIA_EXCEEDS_DOWNLOAD_LIMIT")
                    digest.update(chunk)
                    dest.write(chunk)
        if count == 0:
            raise ValueError("EMPTY_DOWNLOAD")
        partial.replace(target)
        return {"bytes": count, "sha256": digest.hexdigest()}
    finally:
        if partial.exists():
            partial.unlink()


def sample_five(local_media, sha256, out_dir):
    """Extract five real film frames at spaced times, NOT verified distinct shots."""
    intake = inspect_local(local_media, sha256)
    if intake["status"] != "ASSETS_PENDING":
        raise ValueError("V184_INTAKE_FAILED:" + ",".join(intake["blocking_issues"]))
    duration = intake["media"]["duration_seconds"]
    if duration < 30:
        raise ValueError("FILM_TOO_SHORT")
    out_dir = Path(out_dir)
    if out_dir.exists():
        raise ValueError("OUTPUT_DIR_EXISTS")
    out_dir.mkdir()
    previews = []
    for n, frac in enumerate(FRACTIONS, 1):
        second = round(duration * frac, 3)
        output = out_dir / f"preview_{n:02}.png"
        subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
                        "-ss", f"{second:.3f}", "-i", str(local_media),
                        "-map", "0:v:0", "-frames:v", "1", "-y", str(output)],
                       check=True, timeout=110, capture_output=True)
        if not output.is_file() or not output.stat().st_size:
            raise ValueError("MISSING_EXTRACTED_FRAME")
        previews.append({"filename": output.name, "requested_second": second,
                         "sha256": hashlib.sha256(output.read_bytes()).hexdigest()})
    if len({x["sha256"] for x in previews}) != 5:
        raise ValueError("REPEATED_PREVIEW_FRAME_BYTES")
    return {"media": intake["media"], "previews": previews}


def run(out_root, opener=urlopen):
    out_root = Path(out_root)
    out_root.mkdir(parents=True, exist_ok=True)
    film = out_root / "commons_1080_derivative.webm"
    report = {"version": "V186", "source_page": PAGE,
              "status": "SOURCE_PREVIEW_BLOCKED", "blocking_issues": [],
              "provider_jobs_may_start": False, "publish_permitted": False,
              "rights_italy_verified": False, "five_distinct_shots_verified": False,
              "native_scan_verified": False, "freeze_pts_verified": False,
              "four_i2i_completed": False, "vidu_clip_completed": False}
    try:
        selection = discover_derivative(opener)
        report["derivative"] = {k: v for k, v in selection.items() if k != "url"}
        report["derivative_url"] = selection["url"]
        result = bounded_download(selection["url"], film, opener=opener)
        report["derivative_download"] = result
        details = sample_five(film, result["sha256"], out_root / "five_previews")
        report.update(details)
        report["status"] = "FIVE_REAL_FILM_PREVIEWS_NEED_REVIEW"
        report["blocking_issues"] = [
            "DERIVATIVE_NOT_ORIGINAL_MASTER", "FIVE_CAMERA_SHOTS_UNVERIFIED",
            "ITALIAN_RIGHTS_UNVERIFIED", "FOUR_REAL_I2I_MISSING",
            "EXACT_SOURCE_LOCK_AND_VIDU_MISSING", "ARTISTIC_QA_PENDING"]
    except (OSError, ValueError, KeyError, TimeoutError, subprocess.SubprocessError) as exc:
        report["blocking_issues"].append(type(exc).__name__ + ":" + str(exc)[:160])
    finally:
        if film.exists():
            film.unlink()  # save only small previews and SHA metadata, not huge transcode
        (out_root / "V186_SOURCE_PREVIEW_REPORT.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    report = run(args.out)
    print(json.dumps({"status": report["status"],
                      "issues": report["blocking_issues"]}, ensure_ascii=False))
    return 0 if report["status"] == "FIVE_REAL_FILM_PREVIEWS_NEED_REVIEW" else 2


if __name__ == "__main__":
    raise SystemExit(main())
