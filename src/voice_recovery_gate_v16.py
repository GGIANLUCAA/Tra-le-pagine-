"""Fail-closed check for historical Google voice recovery metadata.

Metadata and hashes describe an old artifact; they do not prove that its bytes are
still available.  This gate only reports a cache as render-ready when the exact
local WAV and every adapter-side manifest/alignment file are present and valid.
It never downloads, synthesizes, or calls a paid provider.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADAPTER_FILES = (
    "VOCE.wav",
    "VOICE_CACHE_V13.json",
    "VOICE_PROFILE_V13.json",
    "ALLINEAMENTO_VOCE.json",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_dir(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise ValueError("target_cache_dir must be a non-empty relative path")
    target = (root / value).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError("target_cache_dir escapes repository")
    return target


def inspect_entry(root: Path, entry: dict) -> dict:
    cache = safe_dir(root, entry.get("target_cache_dir", ""))
    blockers: list[str] = []
    wav = cache / "VOCE.wav"
    if not wav.is_file():
        blockers.append("exact_local_wav_missing")
    else:
        expected = entry.get("wav_sha256")
        if not isinstance(expected, str) or sha256(wav) != expected:
            blockers.append("wav_sha256_mismatch")
        else:
            try:
                with wave.open(str(wav), "rb") as audio:
                    rate = audio.getframerate()
                    channels = audio.getnchannels()
                    duration = audio.getnframes() / rate
                if rate != entry.get("sample_rate"):
                    blockers.append("wav_sample_rate_mismatch")
                if channels != entry.get("channels"):
                    blockers.append("wav_channels_mismatch")
                expected_duration = entry.get("duration_seconds")
                if not isinstance(expected_duration, (int, float)) or abs(duration - expected_duration) > 0.25:
                    blockers.append("wav_duration_mismatch")
            except (OSError, EOFError, wave.Error, ZeroDivisionError):
                blockers.append("wav_unreadable")

    missing = [name for name in ADAPTER_FILES[1:] if not (cache / name).is_file()]
    if missing:
        blockers.append("adapter_cache_files_missing:" + ",".join(missing))
    for name in ADAPTER_FILES[1:]:
        path = cache / name
        if path.is_file():
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(value, dict):
                    raise ValueError
            except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
                blockers.append("invalid_json:" + name)

    return {
        "episode": entry.get("episode"),
        "metadata_status": entry.get("status"),
        "cache_dir": entry.get("target_cache_dir"),
        "render_cache_ready": not blockers,
        "blockers": blockers,
    }


def audit(config: Path, root: Path = ROOT) -> dict:
    data = json.loads(config.read_text(encoding="utf-8"))
    rows = [inspect_entry(root, entry) for entry in data.get("entries", [])]
    return {
        "schema": "voice-recovery-gate-v16",
        "config": str(config),
        "ready": sum(1 for row in rows if row["render_cache_ready"]),
        "blocked": sum(1 for row in rows if not row["render_cache_ready"]),
        "entries": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config/voice_artifact_recovery_v16.json")
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args()
    result = audit(Path(args.config), Path(args.root))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["blocked"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
