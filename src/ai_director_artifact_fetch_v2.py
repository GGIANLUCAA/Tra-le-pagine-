#!/usr/bin/env python3
"""Download ONE bounded GitHub Actions artifact for read-only local AI Director V2 QA.

No paid API, no execution of downloaded code, no publication or modification
of original archives. Authenticates only with the ephemeral GitHub Actions token.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import os
import re
import shutil
import stat
import tempfile
import urllib.error
import urllib.request
import urllib.parse
import zipfile
from pathlib import Path

REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
MAX_ARCHIVE_BYTES = 450_000_000
MAX_EXTRACTED_BYTES = 750_000_000
MAX_ENTRIES = 200
KEEP = {".json", ".mp4"}
PREFER = ("MP4", "REVIEW", "CINEMATIC", "VIDEO", "ANDROID", "RESEARCH")


def _get(url, key):
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + key, "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "TraLePagine-OfflineDirectorV2"})
    with urllib.request.urlopen(req, timeout=45) as res:
        return json.load(res)


class _SafeArtifactRedirect(urllib.request.HTTPRedirectHandler):
    """Never leak GitHub Authorization to the signed artifact storage domain."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        redirect = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirect is not None:
            old_host = urllib.parse.urlsplit(req.full_url).hostname
            new_host = urllib.parse.urlsplit(newurl).hostname
            if new_host != old_host:
                redirect.remove_header("Authorization")
                redirect.remove_unredirected_header("Authorization")
        return redirect


def _archive(url, key, target):
    # GitHub artifact endpoint redirects to a short-lived signed ZIP URL.
    # urllib ordinarily forwards Authorization on redirect: signed Azure
    # storage rejects this with HTTP 401, so strip it across origins.
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + key, "Accept": "application/vnd.github+json",
        "User-Agent": "TraLePagine-OfflineDirectorV2"})
    opener = urllib.request.build_opener(_SafeArtifactRedirect)
    count = 0
    with opener.open(req, timeout=120) as res, target.open("wb") as out:
        while True:
            chunk = res.read(1024 * 1024)
            if not chunk:
                break
            count += len(chunk)
            if count > MAX_ARCHIVE_BYTES:
                raise ValueError("Archive exceeds safety download cap")
            out.write(chunk)
    return count


def _unpack(path, out):
    extracted = []
    total = 0
    seen = set()
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        if len(members) > MAX_ENTRIES:
            raise ValueError("Too many archive members")
        for item in members:
            src = item.filename.replace("\\", "/")
            parts = src.split("/")
            if (item.is_dir() or not src or src.startswith("/") or
                any(x in ("", ".", "..") for x in parts) or
                ((item.external_attr >> 16) & stat.S_IFMT(0o777777)) == stat.S_IFLNK):
                continue
            name = Path(src).name
            if Path(name).suffix.lower() not in KEEP or name in seen:
                continue
            if item.file_size > MAX_EXTRACTED_BYTES or total + item.file_size > MAX_EXTRACTED_BYTES:
                continue
            if item.file_size < 2:
                continue
            target = out / name
            with archive.open(item) as inf, target.open("wb") as outf:
                copied = 0
                while True:
                    part = inf.read(1024 * 1024)
                    if not part:
                        break
                    copied += len(part)
                    if copied > item.file_size or copied > MAX_EXTRACTED_BYTES:
                        raise ValueError("Invalid expanded member size")
                    outf.write(part)
            if copied != item.file_size:
                target.unlink(missing_ok=True)
                raise ValueError("Incomplete archive member")
            total += copied
            seen.add(name)
            extracted.append({"name": name, "bytes": copied,
                              "sha256": hashlib.sha256(target.read_bytes()).hexdigest()
                              if copied < 5_000_000 else None})
    return extracted


def acquire(repo, run_id, artifact_name, outdir, token, *, get=_get, download=_archive):
    if not REPO_RE.fullmatch(repo):
        raise ValueError("Untrusted repository name")
    if not isinstance(run_id, int) or run_id <= 0:
        raise ValueError("Invalid run id")
    if not token:
        raise ValueError("Missing GitHub Actions token")
    if artifact_name and (len(artifact_name) > 160 or
                          not re.fullmatch(r"[A-Za-z0-9_.-]+", artifact_name)):
        raise ValueError("Unsafe artifact name")
    base = "https://api.github.com/repos/" + repo
    run = get(base + "/actions/runs/" + str(run_id), token)
    owning = (run.get("head_repository") or {}).get("full_name")
    if run.get("repository", {}).get("full_name") != repo or owning != repo:
        raise ValueError("Run belongs to another repository")
    if run.get("status") != "completed" or run.get("conclusion") != "success":
        return {"status": "producer_not_successful", "run_id": run_id,
                "files": [], "artistic_approval": False}
    payload = get(base + "/actions/runs/" + str(run_id) + "/artifacts?per_page=100", token)
    artifacts = [a for a in payload.get("artifacts", []) if not a.get("expired") and
                 0 < a.get("size_in_bytes", 0) < MAX_ARCHIVE_BYTES]
    if artifact_name:
        artifacts = [a for a in artifacts if a.get("name") == artifact_name]
    else:
        artifacts = [a for a in artifacts if any(s in a.get("name", "").upper() for s in PREFER)]
        artifacts.sort(key=lambda a: (
            min((i for i, mark in enumerate(PREFER) if mark in a.get("name", "").upper()), default=9),
            a.get("size_in_bytes", 0)))
    if not artifacts:
        return {"status": "no_eligible_artifact", "run_id": run_id,
                "files": [], "artistic_approval": False}
    selected = artifacts[0]
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = Path(tmp) / "delivery.zip"
        download(selected["archive_download_url"], token, zip_path)
        files = _unpack(zip_path, outdir)
    return {"status": "extracted_for_readonly_review", "run_id": run_id,
            "artifact": selected["name"], "files": files,
            "artistic_approval": False, "publication": False}


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--run-id", type=int, default=0)
    p.add_argument("--artifact", default="")
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    if args.run_id == 0:
        report = {"status": "no_run_id_provided", "files": [],
                  "artistic_approval": False}
    else:
        report = acquire(os.environ.get("GITHUB_REPOSITORY", ""),
                         args.run_id, args.artifact, args.out,
                         os.environ.get("GH_TOKEN", ""))
    (args.out / "ARTIFACT_INPUT.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("AI_DIRECTOR_ARTIFACT_FETCH", report["status"], "files", len(report["files"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
