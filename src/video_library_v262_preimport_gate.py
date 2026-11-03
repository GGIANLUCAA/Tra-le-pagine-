#!/usr/bin/env python3
"""V262: fail-closed actual-archive pre-import for Video Library Studio.

Verifies the SAME bytes the VLS importer will consume before ANY R2 POST.
This supplements (never replaces) the V25 exact-hash artistic approval gate.
Nested ZIP contents are intentionally not counted: the importer does not upload
them as editorial attachments. No network, secrets, publication or AI calls.
"""
from __future__ import annotations

import json
import re
import shutil
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

from storia_rivive_v260_delivery_bundle_gate import inspect as inspect_delivery_bytes

ACCEPTED_VIDEO_EXTENSION = ".mp4"
MAX_VIDEO_SIZE = 2 * 1024 * 1024 * 1024  # refuse unsafe unpacking, not a quality criterion

def inspect(artifact_zip: Path) -> dict:
    """Return audit only; caller must separately verify human V25 approval."""
    path = Path(artifact_zip)
    blocked = {"status": "BLOCKED", "passed": False,
               "reason": "UNINSPECTED_ARCHIVE", "actual_video_member": None,
               "separate_artistic_approval": "REQUIRED",
               "website_upload_authorization": "NOT_INFERRED"}
    if not path.is_file() or path.is_symlink():
        return {**blocked, "reason": "ARCHIVE_MISSING_OR_SYMLINK"}
    try:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            if len(names) != len(set(names)):
                return {**blocked, "reason": "DUPLICATE_ARCHIVE_MEMBERS"}
            if any(PurePosixPath(n).is_absolute() or ".." in PurePosixPath(n).parts
                   or "\\" in n for n in names):
                return {**blocked, "reason": "UNSAFE_ARCHIVE_MEMBERS"}
            # The importer sees only top-level members of the outer Actions
            # ZIP, never files hidden INSIDE an embedded delivery ZIP.
            masters = [i for i in z.infolist() if not i.is_dir()
                       and PurePosixPath(i.filename).suffix.lower() == ACCEPTED_VIDEO_EXTENSION]
            other_videos = [i.filename for i in z.infolist() if not i.is_dir()
                            and PurePosixPath(i.filename).suffix.lower() in (".mov", ".m4v")]
            if len(masters) != 1 or other_videos:
                return {**blocked, "reason": "EXACTLY_ONE_OUTER_MP4_REQUIRED"}
            master = masters[0]
            if master.file_size < 1024 or master.file_size > MAX_VIDEO_SIZE:
                return {**blocked, "reason": "OUTER_MP4_SIZE_NOT_ALLOWED"}
            # Never accept an archive with a V25 review but no real social
            # package: V260 validates posts, cover, dossier, CRC and identical
            # master hash without trusting filename/manifest booleans.
            with tempfile.TemporaryDirectory(prefix="vls-v262-") as folder:
                original = Path(folder) / "VERIFIED_IMPORT_MASTER.mp4"
                with z.open(master) as inp, original.open("wb") as out:
                    shutil.copyfileobj(inp, out, length=1 << 20)
                report = inspect_delivery_bytes(original, path)
            if report["errors"]:
                return {**blocked, "reason": "DELIVERY_BYTES_INCOMPLETE",
                        "delivery_errors": report["errors"][:16]}
            return {"status": "COMPLETE_SOURCE_ARCHIVE_BYTES_UNDER_REVIEW",
                    "passed": True,
                    "reason": "ONE_MP4_PLUS_DISTINCT_POSTS_COVER_RIGHTS_AND_CRC",
                    "actual_video_member": master.filename,
                    "master_sha256": report["checks"]["video_sha256"],
                    "separate_artistic_approval": "REQUIRED",
                    "website_upload_authorization": "NOT_INFERRED"}
    except (OSError, EOFError, ValueError, RuntimeError, zipfile.BadZipFile) as exc:
        return {**blocked, "reason": "ARCHIVE_UNREADABLE_" + type(exc).__name__}

def main() -> int:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--artifact", type=Path, required=True)
    opts = p.parse_args()
    report = inspect(opts.artifact)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
