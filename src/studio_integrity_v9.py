#!/usr/bin/env python3
"""Bounded, read-only integrity checks for one existing ArtVision MP4 or local V55 ZIP.

This tool NEVER renders, uploads, publishes, approves, changes queue state, or
uses a paid API. A successful byte-level check is NOT an artistic Gold review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

SCHEMA = "studio-integrity-v9"
SITE = "https://video-library-studio.600led.workers.dev"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) Chrome/130.0.0.0 ArtVisionIntegrityV9"
FILE_RE = re.compile(r"^[\w ().-]{1,190}\.mp4$", re.I)
SHA_RE = re.compile(r"^[a-f0-9]{64}$")
MAX_MEDIA_BYTES = 250 * 1024 * 1024
MAX_ZIP_EXPANDED = 750 * 1024 * 1024
MAX_ZIP_FILES = 150
CHUNK_BYTES = 1024 * 1024


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Do not send a download request to a different host."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def default_opener():
    return urllib.request.build_opener(NoRedirect)


def sha_file(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as src:
        for block in iter(lambda: src.read(CHUNK_BYTES), b""):
            sha.update(block)
    return sha.hexdigest()


def valid_master(row: dict) -> dict:
    if not isinstance(row, dict):
        raise ValueError("Master metadata must be an object")
    name, size, digest = row.get("name"), row.get("bytes"), row.get("sha256")
    if (not isinstance(name, str) or not FILE_RE.fullmatch(name)
            or type(size) is not int or not 1024 <= size <= MAX_MEDIA_BYTES
            or not isinstance(digest, str) or not SHA_RE.fullmatch(digest)):
        raise ValueError("Missing or unsafe expected filename/size/SHA256")
    return {"name": name, "bytes": size, "sha256": digest,
            "work": str(row.get("work", ""))[:120], "slot": str(row.get("slot", ""))[:90]}


def known_master(slot_index: int) -> dict:
    """Reuse the V161 pinned set. No custom URL or untrusted SHA input."""
    if type(slot_index) is not int or not 1 <= slot_index <= 17:
        raise ValueError("Target index must be 1..17")
    from video_library_site_download_audit_v161 import expected
    masters = expected()
    if len(masters) != 17:
        raise ValueError("Pinned source master count changed")
    return valid_master(masters[slot_index - 1])


def request_for(name: str, range_header: str | None = None):
    url = SITE + "/download/" + urllib.parse.quote(name, safe="")
    headers = {"User-Agent": USER_AGENT, "Accept": "video/mp4",
               "Accept-Encoding": "identity"}
    if range_header is not None:
        headers["Range"] = range_header
    return urllib.request.Request(url, headers=headers, method="GET")


def audit_master(row: dict, opener=None) -> dict:
    row = valid_master(row)
    opener = opener or default_opener()
    report = {"schema": SCHEMA, "kind": "mp4", "name": row["name"],
              "work": row["work"], "slot": row["slot"],
              "expected_bytes": row["bytes"], "expected_sha256": row["sha256"],
              "range_verified": False, "bytes_verified": False,
              "sha256_verified": False, "mp4_full_download_verified": False,
              "actual_bytes": 0, "actual_sha256": None,
              "failure": None, "owner_approved": False,
              "publish_authorized": False, "zip_verified": False}
    try:
        with opener.open(request_for(row["name"], "bytes=0-1023"), timeout=35) as src:
            if (src.status != 206 or
                    src.headers.get("Content-Range") != f"bytes 0-1023/{row['bytes']}" or
                    src.headers.get("Content-Length") != "1024" or
                    not src.headers.get("Content-Type", "").lower().startswith("video/mp4") or
                    "attachment" not in src.headers.get("Content-Disposition", "").lower()):
                raise ValueError("RANGE_RESPONSE_UNEXPECTED")
            block = src.read(1025)
            if len(block) != 1024:
                raise ValueError("RANGE_BYTE_COUNT_WRONG")
        report["range_verified"] = True
        with opener.open(request_for(row["name"]), timeout=90) as src:
            if src.status != 200:
                raise ValueError("DOWNLOAD_HTTP_NOT_200")
            if not src.headers.get("Content-Type", "").lower().startswith("video/mp4"):
                raise ValueError("DOWNLOAD_MIME_WRONG")
            if "attachment" not in src.headers.get("Content-Disposition", "").lower():
                raise ValueError("DOWNLOAD_NOT_ATTACHMENT")
            advertised = src.headers.get("Content-Length")
            if advertised and (not advertised.isdecimal() or int(advertised) != row["bytes"]):
                raise ValueError("DOWNLOAD_CONTENT_LENGTH_MISMATCH")
            sha, size = hashlib.sha256(), 0
            while True:
                part = src.read(CHUNK_BYTES)
                if not part:
                    break
                size += len(part)
                if size > row["bytes"]:
                    raise ValueError("DOWNLOAD_EXCEEDS_EXPECTED_BYTES")
                sha.update(part)
            report["actual_bytes"] = size
            report["actual_sha256"] = sha.hexdigest()
            report["bytes_verified"] = size == row["bytes"]
            report["sha256_verified"] = report["actual_sha256"] == row["sha256"]
            report["mp4_full_download_verified"] = bool(
                report["range_verified"] and report["bytes_verified"] and
                report["sha256_verified"])
            if not report["mp4_full_download_verified"]:
                report["failure"] = "INCOMPLETE_OR_DIFFERENT_MASTER"
    except (urllib.error.URLError, OSError, ValueError) as exc:
        # Never copy origin errors, arbitrary response bodies or credentials.
        if isinstance(exc, ValueError) and re.fullmatch(r"[A-Z_]+", str(exc)):
            report["failure"] = str(exc)
        else:
            report["failure"] = "NETWORK_OR_IO_ERROR"
    return report


def verify_zip(path: Path, expected_sha: str) -> dict:
    """CRC readback of an existing V55 package; no extraction or uploads."""
    if not isinstance(expected_sha, str) or not SHA_RE.fullmatch(expected_sha):
        raise ValueError("Exact ZIP SHA256 is required")
    path = Path(path).resolve()
    report = {"schema": SCHEMA, "kind": "zip", "name": path.name,
              "expected_sha256": expected_sha, "actual_sha256": None,
              "zip_full_read_verified": False, "zip_crc_verified": False,
              "zip_contents_complete": False, "failure": None,
              "owner_approved": False, "publish_authorized": False}
    if not path.is_file() or path.stat().st_size > MAX_MEDIA_BYTES or path.stat().st_size == 0:
        report["failure"] = "ZIP_FILE_MISSING_OR_TOO_LARGE"
        return report
    digest = sha_file(path)
    report["actual_sha256"] = digest
    if digest != expected_sha:
        report["failure"] = "ZIP_SHA256_MISMATCH"
        return report
    try:
        with zipfile.ZipFile(path) as archive:
            members = [m for m in archive.infolist() if not m.is_dir()]
            if not members or len(members) > MAX_ZIP_FILES:
                raise ValueError("ZIP_MEMBER_COUNT_INVALID")
            if sum(m.file_size for m in members) > MAX_ZIP_EXPANDED:
                raise ValueError("ZIP_EXPANDED_SIZE_EXCEEDED")
            names = set()
            for m in members:
                name = m.filename
                pure = PurePosixPath(name)
                if (not name or "\\" in name or "\x00" in name or pure.is_absolute()
                        or any(part in (".", "..") for part in pure.parts)
                        or stat.S_ISLNK((m.external_attr >> 16) & 0xffff)):
                    raise ValueError("ZIP_UNSAFE_MEMBER")
                names.add(name)
            # V55 delivery structure: one actual MP4, cover, all four post files
            # and a source/rights document. Names are anchored to this layout.
            prefixes = [
                "PACCHETTO/01_VIDEO/", "PACCHETTO/02_COPERTINA/",
                "PACCHETTO/04_FONTI_E_RICETTA/"
            ]
            posts = [f"PACCHETTO/03_POST_SOCIAL/POST_{site}.txt"
                     for site in ("FACEBOOK", "INSTAGRAM", "TIKTOK", "YOUTUBE")]
            complete = (
                any(n.startswith(prefixes[0]) and n.lower().endswith(".mp4") for n in names)
                and any(n.startswith(prefixes[1]) and n.lower().endswith(".jpg") for n in names)
                and any(n.startswith(prefixes[2]) for n in names)
                and all(n in names for n in posts))
            if not complete:
                raise ValueError("ZIP_V55_DELIVERY_MISSING_COMPONENTS")
            bad = archive.testzip()  # bounded size, CRC for every member
            if bad:
                raise ValueError("ZIP_CRC_FAILED")
            report["zip_contents_complete"] = True
            report["zip_crc_verified"] = True
            report["zip_full_read_verified"] = True
    except (ValueError, OSError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
        if isinstance(exc, ValueError) and re.fullmatch(r"[A-Z_]+", str(exc)):
            report["failure"] = str(exc)
        else:
            report["failure"] = "ZIP_READ_ERROR"
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--slot-index", type=int, help="1..17, from V161 pinned master list")
    mode.add_argument("--zip-path", type=Path, help="Existing local V55 ZIP; no download")
    parser.add_argument("--expected-zip-sha256", help="Required for --zip-path")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.slot_index is not None:
        if args.expected_zip_sha256:
            parser.error("ZIP SHA cannot be supplied with --slot-index")
        result = audit_master(known_master(args.slot_index))
    else:
        if not args.expected_zip_sha256:
            parser.error("--expected-zip-sha256 required with --zip-path")
        result = verify_zip(args.zip_path, args.expected_zip_sha256)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    success = (result["mp4_full_download_verified"] if result["kind"] == "mp4"
               else result["zip_full_read_verified"])
    print("VERIFIED" if success else "NOT_VERIFIED",
          result["kind"], result["name"], result.get("failure") or "")
    return 0 if success else 2


if __name__ == "__main__":
    raise SystemExit(main())
