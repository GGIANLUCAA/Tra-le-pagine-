#!/usr/bin/env python3
"""ArtVision Fish Audio cloud TTS prototype: ALWAYS the s2.1-pro-free model.

Hosted on GitHub Actions, manageable from Android. No Google, no local computer,
no paid-model fallback, no voice substitution or social publishing.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL = "https://api.fish.audio/v1/tts"
MODEL = "s2.1-pro-free"
MAX_REVIEW_CHARS = 450
MAX_PRODUCTION_CHARS = 12_000
ALLOWED_FORMATS = {"critico_standard", "critico_museum"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_script(relative_path: str) -> str:
    if not isinstance(relative_path, str) or not relative_path:
        raise ValueError("Missing copione path")
    target = (ROOT / relative_path).resolve()
    if not target.is_relative_to(ROOT) or not target.is_file() or target.suffix not in {".txt", ".md"}:
        raise ValueError("The copione must be a .txt or .md in this repository")
    text = target.read_text(encoding="utf-8").strip()
    if len(text.split()) < 10:
        raise ValueError("Copione too short")
    return text


def validate_request(job: dict, reference_id: str, approved: bool) -> dict:
    work = job.get("work_id")
    if not isinstance(work, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{1,79}", work):
        raise ValueError("Invalid work_id")
    if job.get("format") not in ALLOWED_FORMATS:
        raise ValueError("Only Critico format supported")
    if job.get("allow_paid_api") is not False or job.get("auto_publish") is not False:
        raise ValueError("No paid API calls or automatic publishing are permitted")
    if job.get("provider") != "fish_audio_free":
        raise ValueError("Provider must be fish_audio_free")
    if reference_id and not re.fullmatch(r"[A-Za-z0-9_-]{8,128}", reference_id):
        raise ValueError("Invalid Fish private voice reference ID")
    is_review = job.get("review_only") is True
    if not is_review and not approved:
        raise RuntimeError("Chosen voice not approved; only a short review is permitted")
    state = ("AWAITING_VOICE_REFERENCE_ID" if not reference_id else
             "READY_REVIEW" if is_review else "READY_APPROVED_VOICE")
    return {
        "work_id": work, "format": job["format"], "provider": "fish_audio_free",
        "model": MODEL, "state": state, "review_only": is_review,
        "shared_variants": sorted(ALLOWED_FORMATS), "paid_calls": 0,
        "publish_enabled": False
    }


def request_audio(text: str, reference_id: str, key: str) -> bytes:
    # The 'model' header MUST be present: Fish defaults to paid s2.1-pro.
    if not reference_id or not key:
        raise RuntimeError("Missing API key or private voice ID: no request sent")
    payload = {
        "text": text,
        "reference_id": reference_id,
        "format": "mp3",
        "mp3_bitrate": 192,
        "language": "it",
        "latency": "normal",
        "normalize": True,
        "condition_on_previous_chunks": True
    }
    req = urllib.request.Request(
        URL, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers={"Authorization": "Bearer " + key,
                 "Content-Type": "application/json",
                 "model": MODEL}
    )
    try:
        with urllib.request.urlopen(req, timeout=150) as response:
            if response.status != 200:
                raise RuntimeError("Unexpected HTTP status")
            mime = (response.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            if mime not in ("audio/mpeg", "audio/mp3", "application/octet-stream"):
                raise RuntimeError("Unexpected Fish response type (not audio)")
            audio = response.read(45_000_000)
    except urllib.error.HTTPError as err:
        # Do not echo API response contents: they may carry user details.
        raise RuntimeError(f"Fish free API returned HTTP {err.code}; no paid fallback") from None
    except urllib.error.URLError:
        raise RuntimeError("Fish free API unavailable; no paid fallback") from None
    if len(audio) < 1_024 or not audio.startswith((b"ID3", b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")):
        raise RuntimeError("Fish did not return a valid MP3 file")
    return audio


def run(job_path: Path, outdir: Path, *, plan_only=False) -> dict:
    job = json.loads(job_path.read_text(encoding="utf-8"))
    reference_id = os.environ.get("FISH_VOICE_ID", "").strip()
    approved = os.environ.get("ARTVISION_FISH_VOICE_APPROVED", "").strip().lower() == "true"
    info = validate_request(job, reference_id, approved)
    text = read_script(job["script_path"])
    max_chars = MAX_REVIEW_CHARS if info["review_only"] else MAX_PRODUCTION_CHARS
    if len(text) > max_chars:
        raise ValueError(f"Copione too long for this job (maximum {max_chars} characters)")
    if plan_only:
        return info
    if info["state"] == "AWAITING_VOICE_REFERENCE_ID":
        raise RuntimeError("Save the selected Fish Audio private voice ID in GitHub Actions secret FISH_VOICE_ID")
    key = os.environ.get("FISH_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Save the Fish API key in GitHub Actions secret FISH_API_KEY")
    destination = outdir / info["work_id"]
    destination.mkdir(parents=True, exist_ok=True)
    fingerprint = hashlib.sha256(json.dumps({
        "text": text, "voice_id": reference_id, "model": MODEL,
        "review_only": info["review_only"]
    }, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    master = destination / "VOCE.mp3"
    manifest = destination / "VOICE_MANIFEST.json"
    if master.exists() and manifest.exists():
        prior = json.loads(manifest.read_text(encoding="utf-8"))
        if prior.get("fingerprint") == fingerprint and prior.get("sha256_mp3") == digest(master):
            return dict(prior, state="REUSED_VERIFIED_CACHE")
    output = request_audio(text, reference_id, key)
    tmp = destination / "VOCE.partial.mp3"
    try:
        tmp.write_bytes(output)
        # Validate a genuine decodable audio file before declaring success.
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-xerror",
                        "-i", str(tmp), "-f", "null", "-"], check=True,
                       capture_output=True, timeout=180)
        tmp.replace(master)
        (destination / "COPIONE.txt").write_text(text + "\n", encoding="utf-8")
        data = {**info, "state": "AUDIO_GENERATED_REVIEW_PENDING",
                "fingerprint": fingerprint, "sha256_mp3": digest(master),
                "listening_review": "pending", "renderer_handoff": "not_connected",
                "source_voice_id_sha256": hashlib.sha256(reference_id.encode()).hexdigest()}
        manifest.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return data
    finally:
        tmp.unlink(missing_ok=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True, type=Path)
    ap.add_argument("--out-root", default="output/voice_fish", type=Path)
    ap.add_argument("--plan", action="store_true")
    args = ap.parse_args()
    try:
        print(json.dumps(run(args.job, args.out_root, plan_only=args.plan),
                         ensure_ascii=False, indent=2))
        return 0
    except (ValueError, RuntimeError, OSError, KeyError, subprocess.CalledProcessError,
            subprocess.TimeoutExpired) as exc:
        print(f"FISH_FREE_VOICE_BLOCKED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
