"""Optional Qwen3-TTS 0.6B Oracle ARM preview client; never replaces approved Gacrux.

The engine must be behind an authenticated HTTPS reverse proxy. Its native
HTTP server does not authenticate callers. Only loopback HTTP is permitted.
No cloud resource is provisioned, and no paid API is called by this module.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request
import wave
from pathlib import Path

MAX_WAV_BYTES = 60 * 1024 * 1024
DEFAULT_TEXT = (
    "Nel dipinto, la luce non si limita a illuminare la scena. "
    "Ci conduce verso il particolare che l'artista ha scelto di lasciare in ombra."
)
WAV_NAME = "VOCE_QWEN_PROVINO.wav"
MP3_NAME = "VOCE_QWEN_PROVINO.mp3"
MANIFEST_NAME = "QWEN_VOICE_PREVIEW_V1.json"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_endpoint(base_url: str, token: str | None) -> str:
    parsed = urllib.parse.urlsplit(base_url.strip())
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("URL TTS non valida: credenziali/query non consentite")
    if parsed.path not in ("", "/") or not parsed.hostname:
        raise ValueError("Indicare l'URL base HTTPS del server, senza percorso")
    local = parsed.hostname.lower() in ("localhost", "127.0.0.1", "::1")
    if parsed.scheme != "https" and not (parsed.scheme == "http" and local):
        raise ValueError("Server remoto: HTTPS obbligatorio")
    if not local and not token:
        raise ValueError("ARTVISION_QWEN_TTS_TOKEN richiesto per server remoto")
    return base_url.rstrip("/")


def _wav_duration(data: bytes) -> float:
    if len(data) > MAX_WAV_BYTES or len(data) < 44:
        raise ValueError("Risposta audio vuota o troppo grande")
    try:
        with wave.open(io.BytesIO(data), "rb") as wav:
            if (wav.getnchannels(), wav.getsampwidth(), wav.getframerate()) != (1, 2, 24000):
                raise ValueError("Atteso WAV PCM mono 16-bit 24000 Hz")
            if wav.getcomptype() != "NONE" or wav.getnframes() < 2400:
                raise ValueError("WAV non PCM oppure troppo breve")
            expected = wav.getnframes() * 2
            if len(data) < wav._data_chunk.offset + expected:
                raise ValueError("WAV incompleto")
            return wav.getnframes() / 24000
    except (EOFError, wave.Error, AttributeError) as exc:
        raise ValueError("Risposta del server non è WAV PCM valido") from exc


def _fetch(endpoint: str, token: str | None, path: str, body: dict | None = None,
           timeout: int = 900) -> bytes:
    headers = {"Accept": "audio/wav" if body is not None else "application/json"}
    payload = None
    if token:
        headers["Authorization"] = "Bearer " + token
    if body is not None:
        headers["Content-Type"] = "application/json"
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(endpoint + path, data=payload, headers=headers,
                                     method="POST" if body is not None else "GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            result = response.read(MAX_WAV_BYTES + 1)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Server Qwen: HTTP {exc.code}") from None
    except urllib.error.URLError:
        raise RuntimeError("Server Qwen irraggiungibile: controllare URL e proxy TLS") from None
    if len(result) > MAX_WAV_BYTES:
        raise ValueError("Risposta oltre limite audio 60 MB")
    return result


def generate_preview(text: str, output_dir: str | Path,
                     *, base_url: str | None = None, token: str | None = None,
                     speaker: str = "ryan", force: bool = False) -> dict:
    """Create an isolated, unapproved voice audition. Never touches VOCE.wav."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Copione vuoto")
    if len(text) > 16000:
        raise ValueError("Copione troppo lungo per un singolo provino")
    if speaker not in {"ryan", "vivian", "serena", "aiden", "eric",
                       "dylan", "uncle_fu", "ono_anna", "sohee"}:
        raise ValueError("Speaker Qwen non riconosciuto")
    raw_url = base_url if base_url is not None else os.getenv("ARTVISION_QWEN_TTS_URL", "")
    secret = token if token is not None else os.getenv("ARTVISION_QWEN_TTS_TOKEN", "")
    endpoint = _safe_endpoint(raw_url, secret)
    body = {"text": text.strip(), "speaker": speaker, "language": "Italian"}
    fingerprint = _sha(json.dumps({
        "endpoint": endpoint, "body": body, "adapter": "qwen-oracle-preview-v1"
    }, sort_keys=True, ensure_ascii=False).encode("utf-8"))
    output = Path(output_dir)
    wav_path, manifest_path = output / WAV_NAME, output / MANIFEST_NAME
    if not force and manifest_path.is_file() and wav_path.is_file():
        try:
            existing = json.loads(manifest_path.read_text(encoding="utf-8"))
            wav_bytes = wav_path.read_bytes()
            if (existing["request_sha256"] == fingerprint and
                    existing["wav_sha256"] == _sha(wav_bytes)):
                _wav_duration(wav_bytes)
                return {**existing, "cached": True}
        except (OSError, KeyError, ValueError, TypeError, json.JSONDecodeError):
            pass
    status = json.loads(_fetch(endpoint, secret, "/v1/health", timeout=30))
    if status.get("status") != "ok":
        raise RuntimeError("Server Qwen non pronto")
    result = _fetch(endpoint, secret, "/v1/tts", body=body)
    duration = _wav_duration(result)
    output.mkdir(parents=True, exist_ok=True)
    temp = output / (WAV_NAME + ".tmp")
    temp.write_bytes(result)
    temp.replace(wav_path)
    mp3_path = output / MP3_NAME
    if shutil.which("ffmpeg"):
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                        "-i", str(wav_path), "-codec:a", "libmp3lame", "-b:a", "160k",
                        str(mp3_path)], check=True)
    info = {
        "schema": "qwen-oracle-voice-preview-v1",
        "provider": "Qwen3-TTS self-hosted (Oracle optional)",
        "speaker": speaker, "language": "Italian",
        "request_sha256": fingerprint, "wav_sha256": _sha(result),
        "sample_rate": 24000, "duration_seconds": round(duration, 3),
        "wav_file": WAV_NAME, "mp3_file": MP3_NAME if mp3_path.is_file() else None,
        "approved_for_critico": False,
        "replaces_gacrux": False,
        "artistic_review_required": True,
        "cached": False,
    }
    manifest_path.write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8")
    return info
