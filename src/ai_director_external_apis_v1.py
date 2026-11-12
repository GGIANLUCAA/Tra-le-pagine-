#!/usr/bin/env python3
"""Opt-in API adapters for ArtVision AI Director.

Public catalogue search lives in ai_director_keyless_archives_v1.py.
Gemini: optional still-image editorial review (not full MP4 artistic QA).
Groq: optional STT with segment timestamps (not voice-scene verification).

No network by default. Paid/uncertain provider operations fail closed under a
separate explicitly reviewed policy. Nothing can publish, render, or spend
automatically. Do not run against private media in public repository artifacts.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import html
import json
import mimetypes
import os
from pathlib import Path
import re
import sys
from urllib import error, parse, request

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config/ai_director_external_api_v1.json"
GROQ_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
GEMINI_API = "https://generativelanguage.googleapis.com/v1beta/models/"
MAX_RESPONSE = 750_000
MAX_FRAME = 1_500_000
MAX_AUDIO = 10_000_000


class ExternalAPIError(ValueError):
    pass


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ExternalAPIError("Unexpected redirect; credentials kept on allowlisted host")


def _credential(key):
    if not isinstance(key, str) or not key or len(key) > 1000 or re.search(r"\s", key):
        raise ExternalAPIError("Missing or invalid API key")
    return key


def _send(req, *, transport=None):
    """Send exactly one request, never follow redirects, do not expose secrets on errors."""
    try:
        with (transport or request.build_opener(NoRedirect()).open)(req, timeout=22) as response:
            if int(response.headers.get("Content-Length") or "0") > MAX_RESPONSE:
                raise ExternalAPIError("Provider response exceeds limit")
            raw = response.read(MAX_RESPONSE + 1)
        if len(raw) > MAX_RESPONSE:
            raise ExternalAPIError("Provider response exceeds limit")
        obj = json.loads(raw)
        if not isinstance(obj, dict):
            raise ExternalAPIError("Unexpected provider JSON shape")
        return obj
    except error.HTTPError as exc:
        raise ExternalAPIError("Provider returned HTTP " + str(exc.code)) from None
    except (error.URLError, TimeoutError, OSError, ValueError) as exc:
        if isinstance(exc, ExternalAPIError):
            raise
        raise ExternalAPIError("Provider unreachable or invalid response") from None


def _display(value, limit=200):
    if isinstance(value, list):
        value = next((x for x in value if isinstance(x, str) and x.strip()), "")
    if not isinstance(value, (str, int, float)):
        return ""
    value = re.sub(r"<[^>]*>", "", str(value))
    return html.unescape(value).strip()[:limit]


def _safe_link(value):
    if isinstance(value, list):
        value = next((s for s in value if isinstance(s, str)), "")
    if not isinstance(value, str) or len(value) > 1600:
        return ""
    p = parse.urlsplit(value)
    if p.scheme != "https" or not p.hostname or p.username or p.password or p.port:
        return ""
    if p.hostname in {"localhost", "127.0.0.1", "::1"}:
        return ""
    return value


def load_policy(path=POLICY):
    p = Path(path)
    if not p.is_file() or p.stat().st_size > 25_000:
        raise ExternalAPIError("External API policy missing or oversized")
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != "ai-director-external-api-policy-v1" or data.get("default_deny") is not True:
        raise ExternalAPIError("External API policy is not fail-closed")
    return data


def _admit_live(service, model, policy, *, today=None):
    """Evidence-based, manual opt-in; no paid/unknown plans through this adapter."""
    if service not in {"gemini_image", "groq_transcription"}:
        raise ExternalAPIError("Service not supported for AI live review")
    routes = policy.get("routes")
    if not isinstance(routes, list):
        raise ExternalAPIError("Policy routes must be a list")
    matching = [r for r in routes if isinstance(r, dict) and r.get("service") == service and r.get("model") == model]
    if len(matching) != 1:
        raise ExternalAPIError("Model not explicitly approved under this API policy")
    route = matching[0]
    required = ("enabled", "no_charge_verified", "commercial_terms_checked",
                "commercial_use_permitted", "billing_disabled_verified",
                "no_paid_fallback_verified", "account_limit_checked")
    if any(route.get(k) is not True for k in required):
        raise ExternalAPIError("Provider cost, account or legal attestations incomplete")
    if any(type(route.get(k)) not in (int, float) or route[k] != 0
           for k in ("input_usd_per_million", "output_usd_per_million", "cost_per_audio_hour_usd")):
        raise ExternalAPIError("Provider price is not attested as exactly zero")
    source = _safe_link(route.get("official_evidence_url", ""))
    if not source:
        raise ExternalAPIError("Official HTTPS policy evidence required")
    try:
        verified = dt.date.fromisoformat(route["verified_on"])
    except (KeyError, TypeError, ValueError):
        raise ExternalAPIError("Official verification date missing") from None
    now = today or dt.datetime.now(dt.timezone.utc).date()
    if not dt.timedelta(0) <= now - verified <= dt.timedelta(days=7):
        raise ExternalAPIError("Pricing attestation stale or in the future")
    if os.environ.get("AI_DIRECTOR_EXTERNAL_LIVE") != "1":
        raise ExternalAPIError("External AI calls disabled; explicit opt-in needed")
    return route


def _frame_bytes(frame):
    p = Path(frame)
    if not p.is_file() or p.stat().st_size > MAX_FRAME or p.stat().st_size < 100:
        raise ExternalAPIError("Image must be 100B..1.5MB")
    raw = p.read_bytes()
    if raw[:3] == b"\xff\xd8\xff":
        mime = "image/jpeg"
    elif raw[:8] == b"\x89PNG\r\n\x1a\n":
        mime = "image/png"
    else:
        raise ExternalAPIError("Only genuine JPEG or PNG stills; extract frames separately")
    return mime, raw


def gemini_frame_review(frame, *, model, key, prompt, policy=None, transport=None):
    """Optional ONE source-derived frame review; never says it watched full MP4."""
    if not isinstance(model, str) or not re.fullmatch(r"gemini-[a-z0-9.-]{3,70}", model):
        raise ExternalAPIError("Explicit Gemini model ID required")
    _admit_live("gemini_image", model, policy or load_policy())
    key = _credential(key)
    if not isinstance(prompt, str) or not 10 <= len(prompt.strip()) <= 800:
        raise ExternalAPIError("Image inspection question must be 10..800 characters")
    mime, frame_bytes = _frame_bytes(frame)
    body = {"contents": [{"parts": [
        {"text": "Assess only the supplied single frame. Do not claim to have seen the full video, heard audio, verified rights or approved the movie. Label uncertainty. " + prompt},
        {"inline_data": {"mime_type": mime, "data": base64.b64encode(frame_bytes).decode("ascii")}}
    ]}], "generationConfig": {"maxOutputTokens": 400, "temperature": 0.2}}
    req = request.Request(GEMINI_API + model + ":generateContent",
                          data=json.dumps(body).encode("utf-8"), method="POST",
                          headers={"Content-Type": "application/json", "x-goog-api-key": key})
    answer = _send(req, transport=transport)
    try:
        text = answer["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        raise ExternalAPIError("Gemini returned no usable text") from None
    if not isinstance(text, str) or not text.strip():
        raise ExternalAPIError("Gemini response empty")
    return {"provider": "gemini", "model": model, "text": text[:6000],
            "mode": "one_frame_editorial_draft", "full_video_watched": False,
            "sources_verified": False, "human_approved": False, "auto_publish": False}


def groq_transcription(audio, *, model, key, policy=None, transport=None):
    """Optional ONE uploaded audio file, returns segments; NEVER text/visual sync proof."""
    if model not in {"whisper-large-v3", "whisper-large-v3-turbo"}:
        raise ExternalAPIError("Only explicitly supported Whisper transcription models")
    _admit_live("groq_transcription", model, policy or load_policy())
    key = _credential(key)
    p = Path(audio)
    if not p.is_file() or p.stat().st_size > MAX_AUDIO or p.stat().st_size < 100:
        raise ExternalAPIError("Audio file must be 100B..10MB")
    allowed = {".wav":"audio/wav", ".mp3":"audio/mpeg", ".flac":"audio/flac", ".m4a":"audio/mp4"}
    mime = allowed.get(p.suffix.lower())
    if not mime:
        raise ExternalAPIError("Supported audio: WAV, MP3, FLAC, M4A")
    raw = p.read_bytes()
    boundary = "aidir-boundary-6ad3298d"  # Delimiter, never reused for security-sensitive signing
    parts = [
        "--" + boundary + "\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\n" + model + "\r\n",
        "--" + boundary + "\r\nContent-Disposition: form-data; name=\"response_format\"\r\n\r\nverbose_json\r\n",
        "--" + boundary + "\r\nContent-Disposition: form-data; name=\"timestamp_granularities[]\"\r\n\r\nsegment\r\n",
        "--" + boundary + "\r\nContent-Disposition: form-data; name=\"file\"; filename=\"source" + p.suffix.lower() +
        "\"\r\nContent-Type: " + mime + "\r\n\r\n"
    ]
    body = "".join(parts).encode("ascii") + raw + ("\r\n--" + boundary + "--\r\n").encode("ascii")
    req = request.Request(GROQ_URL, method="POST", data=body,
                          headers={"Authorization": "Bearer " + key,
                                   "Content-Type": "multipart/form-data; boundary=" + boundary})
    data = _send(req, transport=transport)
    transcript = data.get("text")
    segments = data.get("segments")
    if not isinstance(transcript, str) or not isinstance(segments, list):
        raise ExternalAPIError("Timestamped Groq response missing text or segments")
    clean = []
    for s in segments[:500]:
        if not isinstance(s, dict):
            continue
        start, end = s.get("start"), s.get("end")
        if (type(start) not in (int, float) or type(end) not in (int, float) or
            not 0 <= start < end <= 86400):
            continue
        clean.append({"start_s": start, "end_s": end, "text": _display(s.get("text"), 700)})
    return {"provider": "groq", "model": model, "status": "transcribed_unverified",
            "text": transcript[:18000], "segments": clean, "audio_track_listened_by_human": False,
            "visual_alignment_verified": False, "publication_authorized": False}


def main():
    parser = argparse.ArgumentParser(description="External APIs for AI Director, fail closed")
    parser.add_argument("--mode", choices=("inventory",), required=True)
    parser.add_argument("--output", default="output/ai_director_apis/report.json")
    args = parser.parse_args()
    report = {
        "schema": "ai-director-external-api-status-v1", "network_requests": 0,
        "status": "disabled", "auto_render": False, "publication_authorized": False,
        "gemini_frame_review": "disabled_until_account_zero_cost_proof",
        "groq_transcription": "disabled_until_account_zero_cost_proof",
        "cloudflare_vision": "not_active_requires_account_plan_and_meta_license_check",
        "openrouter": "existing_ai_director_model_guard_only",
    }
    if args.mode == "inventory":
        report["status"] = "safe_offline_inventory"
        report["credentials_present"] = {
            k: bool(os.environ.get(k)) for k in (
                "GEMINI_API_KEY", "GROQ_API_KEY",
                "OPENROUTER_API_KEY", "CLOUDFLARE_API_TOKEN", "CLOUDFLARE_ACCOUNT_ID")
        }
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    # Output path managed by workflow. No secret/key appears in the report.
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("AI_DIRECTOR_APIS", report.get("status"), "requests=", report.get("api_requests", 0))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ExternalAPIError, OSError, ValueError) as exc:
        raise SystemExit("AI_DIRECTOR_EXTERNAL_FAIL_CLOSED: " + str(exc))
