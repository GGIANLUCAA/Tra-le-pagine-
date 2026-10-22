#!/usr/bin/env python3
"""Recover allowlisted Google voice artifacts with exact hashes; never calls TTS."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "config/voice_artifact_recovery_v16.json"
DEFAULT_QUEUE = ROOT / "queue/production_v15.json"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def safe_extract(archive, target):
    target = Path(target).resolve()
    with zipfile.ZipFile(archive) as zf:
        for info in zf.infolist():
            output = (target / info.filename).resolve()
            if not output.is_relative_to(target):
                raise ValueError("Percorso non sicuro nell'artefatto")
        zf.extractall(target)


def download(entry, destination, local_artifacts=None):
    local = Path(local_artifacts) / f"artifact-{entry['artifact_id']}.zip" if local_artifacts else None
    if local and local.is_file():
        shutil.copy2(local, destination)
        return
    repo = os.environ.get("GITHUB_REPOSITORY")
    if repo != "GGIANLUCAA/Tra-le-pagine-":
        raise RuntimeError("Recupero consentito soltanto nel repository previsto")
    route = f"repos/{repo}/actions/artifacts/{entry['artifact_id']}/zip"
    with Path(destination).open("wb") as stream:
        subprocess.run(["gh", "api", route], stdout=stream, check=True)


def requested_episodes(queue_path):
    queue = load(queue_path)
    return {
        item.get("episode")
        for item in queue.get("items", [])
        if item.get("status") == "prepared" and item.get("adapter") == "books_gemini_cache"
    }


def recover(entry, local_artifacts=None):
    if entry.get("status") != "recoverable_verified_voice_and_timing" or not entry.get("timing_file"):
        return {"episode": entry.get("episode"), "status": "blocked", "reason": entry.get("blocker", "Allineamento verificato assente")}
    with tempfile.TemporaryDirectory(prefix="voice-recovery-v16-") as tmp_name:
        tmp = Path(tmp_name)
        archive = tmp / "artifact.zip"
        download(entry, archive, local_artifacts)
        safe_extract(archive, tmp / "files")
        source = tmp / "files"
        artifact_script = source / entry["artifact_script_file"]
        wav = source / entry["wav_file"]
        timing = source / entry["timing_file"]
        repo_script = ROOT / entry["script_file"]
        if artifact_script.read_text(encoding="utf-8").strip() != repo_script.read_text(encoding="utf-8").strip():
            raise ValueError("Copione dell'artefatto diverso dal repository")
        if sha256(wav) != entry["wav_sha256"]:
            raise ValueError("Hash WAV diverso dal manifest")

        import sys
        sys.path.insert(0, str(ROOT / "src"))
        from gemini_voice import SAMPLE_RATE, _sha, cache_key, sentences, voice_profile
        import soundfile as sf

        data, sample_rate = sf.read(wav, dtype="float32")
        if sample_rate != entry["sample_rate"] or sample_rate != SAMPLE_RATE or data.ndim != 1:
            raise ValueError("Formato WAV diverso dal manifest")
        rows = load(timing)
        phrases = sentences(repo_script.read_text(encoding="utf-8"))
        timed = [[row["text"], float(row["start"]), float(row["end"])] for row in rows]
        if [row[0] for row in timed] != phrases:
            raise ValueError("Timing frase non corrispondente al copione")
        duration = len(data) / sample_rate
        if abs(duration - float(entry["duration_seconds"])) > 0.05 or any(not 0 <= a < b <= duration + 0.1 for _, a, b in timed):
            raise ValueError("Durata o limiti del timing non validi")
        profile = voice_profile()
        if profile["provider"] != entry["voice_provider"] or profile["model"] != entry["voice_model"] or profile["voice"] != entry["voice_profile"]:
            raise ValueError("Profilo voce del codice diverso dal manifest")

        target = ROOT / entry["target_cache_dir"]
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(wav, target / "VOCE.wav")
        alignment = {
            "schema": "voice-alignment-v13",
            "method": "recovered_artifact_sentence_timing",
            "sentence_count": len(timed),
            "duration_seconds": duration,
            "requires_sync_review": True,
            "source_workflow_run_id": entry["workflow_run_id"],
            "note": "Tempi recuperati dall'artefatto storico; la revisione integrale audio/video resta obbligatoria."
        }
        write_json(target / "ALLINEAMENTO_VOCE.json", alignment)
        write_json(target / "VOICE_PROFILE_V13.json", profile)
        write_json(target / "VOICE_CACHE_V13.json", {
            "cache_key": cache_key(repo_script.read_text(encoding="utf-8")),
            "wav_sha256": _sha(target / "VOCE.wav"),
            "profile": profile,
            "timed": timed,
            "alignment": alignment,
            "recovered_from": {
                "workflow_run_id": entry["workflow_run_id"],
                "artifact_id": entry["artifact_id"],
                "artifact_digest": entry["artifact_digest"]
            }
        })
        return {"episode": entry["episode"], "status": "recovered", "cache_dir": entry["target_cache_dir"], "wav_sha256": entry["wav_sha256"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--queue", default=str(DEFAULT_QUEUE))
    parser.add_argument("--episode", action="append")
    parser.add_argument("--local-artifacts", help="Cartella di ZIP artifact-ID per collaudo offline")
    parser.add_argument("--out", default="output/production-v16/VOICE_RECOVERY_REPORT_V16.json")
    args = parser.parse_args()
    manifest = load(args.manifest)
    wanted = set(args.episode or requested_episodes(args.queue))
    results = []
    for entry in manifest.get("entries", []):
        if entry.get("episode") in wanted:
            results.append(recover(entry, args.local_artifacts))
    report = {"schema": "voice-recovery-report-v16", "requested": sorted(wanted), "results": results, "paid_calls": 0}
    write_json(ROOT / args.out, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
