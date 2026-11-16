#!/usr/bin/env python3
"""Private-only GitHub Artifact -> R2 reconciliation. No public catalog write.

The GitHub Actions workflow has an OIDC identity accepted ONLY on /private-*
Worker routes. It never uploads to public VIDEOS, publishes socials, or alters
existing masters. ChatGPT Library-only files are beyond this integration.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import io
import json
import os
from pathlib import PurePosixPath
import re
import subprocess
import sys
import tempfile
import time
import zipfile

import requests

API = "https://api.github.com/repos/"
AUDIENCE = "vls-gh-import-2026"
VIDEO_EXTS = (".mp4", ".m4v", ".mov")
MAX_ZIP = 1024 * 1024 * 1024
MAX_VIDEO = 512 * 1024 * 1024
SINGLE_LIMIT = 30 * 1024 * 1024
# Hard owner/private archive boundaries: never count these as finished owner films.
BAD_MARKERS = re.compile(
    r"(^|[_ .-])(SOURCE|SCOUT|CONTACT|FRAMES|ASSETS|PROBE|RAW|"
    r"NOT_FINAL|NON_FINALE|REJECTED|RESPINTO|INTERMEDIATE|"
    r"BENCHMARK|QA_ONLY)([_ .-]|$)", re.I)
BAD_PREFIXES = ("AUDIO_POLISHED_REVIEW", "TRUE_BW_MOTION", "SOURCE_SHOT_")
ARTIFACT_FAMILIES = ("ARTVISION", "GIULIANO", "STORIA", "TRA_LE_PAGINE",
                     "VIDEO_PAPA", "WOW_LAB", "REGIA_UMANA")


def candidate_video(name: str, artifact_name: str) -> bool:
    file = PurePosixPath(name).name
    if not re.fullmatch(r"[A-Za-z0-9_(). -]{1,180}\.(mp4|m4v|mov)", file, re.I):
        return False
    if BAD_MARKERS.search(file) or BAD_MARKERS.search(artifact_name):
        return False
    if file.upper().startswith(BAD_PREFIXES):
        return False
    if "THE_DRYAD_CRITICO" in file.upper():  # explicitly rejected Gacrux substitute
        return False
    return True


def candidate_artifact(a: dict, since: str) -> bool:
    name = str(a.get("name") or "").upper()
    return bool(not a.get("expired") and
                (a.get("created_at") or "") >= since and
                name.startswith(ARTIFACT_FAMILIES) and
                not BAD_MARKERS.search(name))


def audit_complete_mp4(path: str) -> None:
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,codec_name", "-of", "json", path],
        capture_output=True, text=True, check=True, timeout=45)
    doc = json.loads(probe.stdout)
    if not any(s.get("codec_type") == "video" for s in doc.get("streams", [])):
        raise ValueError("No video stream")
    decoded = subprocess.run(
        ["ffmpeg", "-v", "error", "-xerror", "-i", path, "-map", "0:v:0",
         "-f", "null", "-"], capture_output=True, text=True, timeout=240)
    if decoded.returncode:
        raise ValueError("Full decode failed: " + decoded.stderr[:180])


class Bridge:
    def __init__(self, session: requests.Session, repo: str, endpoint: str, gh_token: str):
        self.s, self.repo, self.root = session, repo, endpoint.rstrip("/")
        self.head = {"Authorization": "Bearer " + gh_token,
                     "Accept": "application/vnd.github+json",
                     "X-GitHub-Api-Version": "2022-11-28"}
        self._cached = ("", 0.0)

    def oidc(self) -> str:
        if self._cached[0] and time.time() - self._cached[1] < 180:
            return self._cached[0]
        r = self.s.get(os.environ["ACTIONS_ID_TOKEN_REQUEST_URL"],
                       headers={"Authorization": "Bearer " +
                                os.environ["ACTIONS_ID_TOKEN_REQUEST_TOKEN"]},
                       params={"audience": AUDIENCE}, timeout=30)
        r.raise_for_status()
        self._cached = (r.json()["value"], time.time())
        return self._cached[0]

    def private(self, method: str, path: str, *, params=None, **kwargs) -> dict:
        r = self.s.request(method, self.root + path, params=params,
                           headers={"Authorization": "Bearer " + self.oidc(),
                                    "Content-Type": "video/mp4"},
                           timeout=240, **kwargs)
        r.raise_for_status()
        result = r.json()
        if result.get("private") is not True:
            raise ValueError("PRIVATE_ONLY invariant not confirmed for " + path)
        return result

    def artifact_rows(self, since: str) -> list[dict]:
        found = []
        for page in range(1, 7):
            r = self.s.get(API + self.repo + "/actions/artifacts",
                           headers=self.head,
                           params={"per_page": 100, "page": page},
                           timeout=45)
            r.raise_for_status()
            chunk = r.json().get("artifacts", [])
            found.extend(a for a in chunk if candidate_artifact(a, since))
            if len(chunk) < 100:
                break
        found.sort(key=lambda a: (a.get("created_at") or "", a.get("id") or 0),
                   reverse=True)
        return found

    def archive_zip(self, artifact_id: int, out: str) -> None:
        with self.s.get(API + self.repo + "/actions/artifacts/" +
                        str(artifact_id) + "/zip", headers=self.head,
                        stream=True, timeout=200) as r:
            r.raise_for_status()
            total = 0
            with open(out, "wb") as fd:
                for block in r.iter_content(1024 * 1024):
                    total += len(block)
                    if total > MAX_ZIP:
                        raise ValueError("ZIP above safety limit")
                    fd.write(block)

    def stage_video(self, aid: int, member: str, zf: zipfile.ZipFile) -> dict:
        name = PurePosixPath(member).name
        info = zf.getinfo(member)
        if not 1024 <= info.file_size <= MAX_VIDEO:
            raise ValueError("Video size outside limit")
        with tempfile.TemporaryDirectory() as tmp:
            target = os.path.join(tmp, name)
            sha = hashlib.sha256()
            count = 0
            with zf.open(member) as rd, open(target, "wb") as wr:
                while chunk := rd.read(1024 * 1024):
                    count += len(chunk)
                    if count > MAX_VIDEO:
                        raise ValueError("Over-size MP4")
                    sha.update(chunk)
                    wr.write(chunk)
            if count != info.file_size:
                raise ValueError("Truncated archive member")
            digest = sha.hexdigest()
            params = {"artifact": str(aid), "key": name}
            existing = self.private("GET", "/private-status", params=params)
            if existing.get("exists"):
                if existing.get("size") != count or existing.get("sha256") != digest:
                    raise ValueError("Existing private object conflict: " + name)
                return {"name": name, "bytes": count, "sha256": digest}
            audit_complete_mp4(target)
            params["sha256"] = digest
            large = count > SINGLE_LIMIT
            if large:
                params["bytes"] = count
            with open(target, "rb") as rd:
                content = rd.read()
            result = self.private("POST",
                                  "/private-stream" if large else "/private-single",
                                  params=params, data=content)
            if (result.get("size") != count or result.get("sha256") != digest or
                    not (result.get("stored") or result.get("already_exists"))):
                raise ValueError("Private R2 upload/readback check failed")
            return {"name": name, "bytes": count, "sha256": digest}

    def run(self, max_artifacts: int, since: str) -> dict:
        readiness = self.private("GET", "/private-ready")
        if not readiness.get("ready"):
            raise RuntimeError("PRIVATE_ARCHIVE binding not yet active")
        rows = self.artifact_rows(since)
        details = []
        imported = skipped = failed = 0
        for artifact in rows:
            if imported >= max_artifacts:
                break
            aid = int(artifact["id"])
            done = self.private("GET", "/private-artifact-done",
                                params={"artifact": str(aid)})
            if done.get("done"):
                skipped += 1
                continue
            with tempfile.TemporaryDirectory() as tmp:
                archive_path = os.path.join(tmp, "artifact.zip")
                try:
                    self.archive_zip(aid, archive_path)
                    with zipfile.ZipFile(archive_path) as zf:
                        members = [n for n in zf.namelist() if
                                   not n.endswith("/") and
                                   candidate_video(n, artifact["name"])]
                        if not members:
                            details.append({"artifact": aid, "state": "NO_FINISHED_MP4"})
                            continue
                        # No confusion between distinct names: exact per-artifact key.
                        unique = {PurePosixPath(n).name for n in members}
                        if len(unique) != len(members):
                            raise ValueError("Ambiguous identical MP4 basenames")
                        verified = [self.stage_video(aid, member, zf)
                                    for member in members[:20]]
                        if len(members) > 20:
                            raise ValueError("Excess video count in one artifact")
                    marked = self.private("POST", "/private-artifact-done",
                                          params={"artifact": str(aid)},
                                          json={"files": verified})
                    if not marked.get("done"):
                        raise ValueError("Archive checkpoint not confirmed")
                    imported += 1
                    details.append({"artifact": aid, "state": "PRIVATE_ARCHIVED",
                                    "videos": verified})
                except Exception as exc:
                    failed += 1
                    details.append({"artifact": aid, "state": "BLOCKED",
                                    "reason": str(exc)[:300]})
        return {"schema": "vls-private-auto-reconcile-v1",
                "private_only": True, "site_publication_count": 0,
                "artifact_candidates": len(rows), "new_artifacts_archived": imported,
                "already_archived": skipped, "blocked_artifacts": failed,
                "details": details}


def main() -> None:
    today = dt.datetime.now(dt.timezone.utc)
    start = max(dt.datetime(2026, 11, 12, tzinfo=dt.timezone.utc),
                today - dt.timedelta(days=14))
    since = start.isoformat(timespec="seconds").replace("+00:00", "Z")
    with requests.Session() as session:
        service = Bridge(session, os.environ["GITHUB_REPOSITORY"],
                         os.getenv("PRIVATE_INGEST", "https://video-library-import.600led.workers.dev"),
                         os.environ["GH_TOKEN"])
        result = service.run(int(os.getenv("MAX_ARTIFACTS_PER_CYCLE", "3")), since)
    os.makedirs("reports", exist_ok=True)
    with open("reports/video_library_private_reconcile_last.json", "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    # Partial blocked artifacts must be visible as failed, not 'zero errors success'.
    if result["blocked_artifacts"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
