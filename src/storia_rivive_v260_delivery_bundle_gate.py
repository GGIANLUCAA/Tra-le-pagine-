#!/usr/bin/env python3
"""V260: verify bytes of the delivery ZIP instead of trusting manifest flags.
Checks posts, JPEG, source dossier and exact final MP4; not artistic/legal approval.
"""
from __future__ import annotations
import hashlib
import json
import re
from difflib import SequenceMatcher
from pathlib import Path, PurePosixPath
import zipfile

REQUIRED_POSTS = ("POST_FACEBOOK.txt", "POST_INSTAGRAM.txt",
                  "POST_TIKTOK.txt", "POST_YOUTUBE.txt")
SOURCE_DOSSIERS = ("SOURCES_AND_RIGHTS.md", "FONTI_E_DIRITTI.md", "FONTI_E_DIRITTI.txt")
REJECT_TEXT = ("todo", "lorem ipsum", "placeholder", "inserire qui",
               "da completare", "testo esempio")

def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def _sha256_member(archive: zipfile.ZipFile, member: str) -> str:
    digest = hashlib.sha256()
    with archive.open(member, "r") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def _read_text(archive: zipfile.ZipFile, member: str) -> str:
    if archive.getinfo(member).file_size > 300_000:
        raise ValueError("text file too large")
    return archive.read(member).decode("utf-8-sig").strip()

def inspect(video_path: Path, delivery_zip: Path | None = None) -> dict:
    """Fail closed on missing, corrupt or incomplete package and wrong MP4 bytes."""
    video_path = Path(video_path)
    errors: list[str] = []
    result: dict = {"status": "BLOCKED", "checks": {}, "errors": errors}
    if not video_path.is_file() or video_path.stat().st_size < 1024:
        errors.append("FINAL_VIDEO_MISSING_OR_EMPTY")
        return result
    if delivery_zip is None:
        candidates = sorted(video_path.parent.glob("*.zip"))
        if len(candidates) != 1:
            errors.append("DELIVERY_ZIP_MISSING_OR_AMBIGUOUS")
            return result
        delivery_zip = candidates[0]
    delivery_zip = Path(delivery_zip)
    if not delivery_zip.is_file() or delivery_zip.stat().st_size < 100:
        errors.append("DELIVERY_ZIP_MISSING_OR_EMPTY")
        return result
    result["checks"]["delivery_zip"] = delivery_zip.name
    result["checks"]["video_sha256"] = _sha256(video_path)
    try:
        with zipfile.ZipFile(delivery_zip) as archive:
            infos = [i for i in archive.infolist() if not i.is_dir()]
            names = [i.filename for i in infos]
            if len(set(names)) != len(names):
                errors.append("DUPLICATE_ARCHIVE_ENTRY")
                return result
            if any(PurePosixPath(n).is_absolute() or ".." in PurePosixPath(n).parts
                   or "\\" in n for n in names):
                errors.append("UNSAFE_ARCHIVE_PATH")
                return result
            bad = archive.testzip()
            if bad is not None:
                errors.append("CORRUPT_ZIP_MEMBER:" + bad)
                return result
            by_base: dict[str, list[str]] = {}
            for name in names:
                by_base.setdefault(PurePosixPath(name).name.upper(), []).append(name)
            unique_post_texts: dict[str, str] = {}
            for post in REQUIRED_POSTS:
                matches = by_base.get(post.upper(), [])
                if len(matches) != 1:
                    errors.append("POST_MISSING_OR_DUPLICATED:" + post)
                    continue
                try:
                    content = _read_text(archive, matches[0])
                except (UnicodeError, ValueError):
                    errors.append("POST_INVALID_TEXT:" + post)
                    continue
                if (len(content) < 100 or len(content.split()) < 16
                        or any(re.search(r"(?<!\w)" + re.escape(bad) + r"(?!\w)", content.casefold()) for bad in REJECT_TEXT)):
                    errors.append("POST_EMPTY_OR_PLACEHOLDER:" + post)
                else:
                    # A different filename alone does not make four platform
                    # posts different. Detect exact and near-copied captions.
                    normalized = " ".join(content.casefold().split())
                    if any(normalized == prior or
                           SequenceMatcher(None, normalized, prior).ratio() >= 0.92
                           for prior in unique_post_texts.values()):
                        errors.append("POST_DUPLICATED_OR_NEAR_DUPLICATE:" + post)
                    else:
                        unique_post_texts[post] = normalized
                        result["checks"][post] = "DISTINCT_CONTENT_PRESENT"
            dossier = [n for key in SOURCE_DOSSIERS
                       for n in by_base.get(key.upper(), [])]
            if len(dossier) != 1:
                errors.append("SOURCE_RIGHTS_DOSSIER_MISSING_OR_DUPLICATED")
            else:
                try:
                    rights_text = _read_text(archive, dossier[0])
                    if (len(rights_text) < 60 or "http" not in rights_text.lower()
                            or any(re.search(r"(?<!\w)" + re.escape(t) + r"(?!\w)", rights_text.casefold()) for t in REJECT_TEXT)):
                        errors.append("SOURCE_RIGHTS_DOSSIER_INCOMPLETE")
                except (UnicodeError, ValueError):
                    errors.append("SOURCE_RIGHTS_DOSSIER_INVALID_TEXT")
            covers = [n for n in names if PurePosixPath(n).suffix.lower()
                      in (".jpg", ".jpeg")]
            valid_covers = [n for n in covers if archive.getinfo(n).file_size > 1024
                            and archive.open(n).read(3) == b"\xff\xd8\xff"]
            if not valid_covers:
                errors.append("REAL_JPEG_COVER_MISSING")
            else:
                result["checks"]["cover"] = [PurePosixPath(n).name for n in valid_covers]
            videos = [n for n in names if PurePosixPath(n).suffix.lower() == ".mp4"]
            if not videos:
                errors.append("FINAL_MP4_NOT_IN_DELIVERY_ZIP")
            elif not any(_sha256_member(archive, n) ==
                         result["checks"]["video_sha256"] for n in videos):
                errors.append("FINAL_MP4_ZIP_BYTES_MISMATCH")
            else:
                result["checks"]["identical_final_mp4_inside_zip"] = True
    except (OSError, zipfile.BadZipFile, RuntimeError, EOFError, ValueError) as exc:
        errors.append("DELIVERY_ZIP_UNREADABLE:" + type(exc).__name__)
    if not errors:
        result["status"] = "DELIVERY_BYTES_VALID_ARTISTIC_AND_RIGHTS_REVIEW_STILL_REQUIRED"
    return result

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--delivery-zip")
    args = parser.parse_args()
    report = inspect(Path(args.video),
                     Path(args.delivery_zip) if args.delivery_zip else None)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not report["errors"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
