#!/usr/bin/env python3
"""ArtVision voice autopilot pilot: safe, queue-driven local voice cloning.

Creates one reusable narration per work, for Critico Standard + Museum.
Never replaces the existing Gacrux contract unless the owner approves a profile.
No paid API calls, no public audio/reference uploads, no automatic publishing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/artvision_voice_profiles_v1.json"
FORMATS = {"critico_standard", "critico_museum"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_repo_file(relative_path: str) -> Path:
    if not isinstance(relative_path, str) or not relative_path.strip():
        raise ValueError("Missing script_path")
    p = (ROOT / relative_path).resolve()
    if not p.is_relative_to(ROOT) or not p.is_file():
        raise ValueError("Script must be an existing file inside the repository")
    if p.suffix.lower() not in {".txt", ".md"}:
        raise ValueError("Script file must be plain text (.txt or .md)")
    return p


def chunks(text: str, limit: int = 290) -> list[str]:
    """Keep sentences intact wherever possible; never rewrite the narration."""
    parts = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text.strip()))
    out, current = [], ""
    for part in parts:
        if len(current) + len(part) + 1 > limit and current:
            out.append(current)
            current = ""
        if len(part) > limit:
            words = part.split()
            for word in words:
                if current and len(current) + len(word) + 1 > limit:
                    out.append(current)
                    current = ""
                current = (current + " " + word).strip()
        else:
            current = (current + " " + part).strip()
    if current:
        out.append(current)
    return out


def plan_job(job: dict, settings: dict) -> dict:
    work_id = job.get("work_id")
    if not isinstance(work_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{1,79}", work_id):
        raise ValueError("Invalid work_id")
    fmt = job.get("format")
    if fmt not in FORMATS:
        raise ValueError("Only Critico Standard/Museum supported in pilot")
    if job.get("allow_paid_api") is not False or job.get("auto_publish") is not False:
        raise ValueError("allow_paid_api=false and auto_publish=false are mandatory")
    defaults = settings["default_by_format"]
    profile_id = job.get("voice_profile", defaults[fmt])
    profile = settings["profiles"].get(profile_id)
    if not profile:
        raise ValueError("Unknown voice profile")
    engine = profile.get("engine")
    state = ("EXISTING_GACRUX_PIPELINE_UNCHANGED" if engine == "existing_gemini"
             else "READY_LOCAL" if engine == "qwen_local" and profile.get("approved") is True
             else "PENDING_OWNER_VOICE_APPROVAL")
    # Both versions use the same work_id output folder and hash; never a double TTS call.
    return {"work_id": work_id, "format": fmt, "voice_profile": profile_id,
            "engine": engine, "model": profile.get("model"),
            "state": state, "shared_variants": ["critico_standard", "critico_museum"],
            "paid_api_calls": 0, "auto_publish": False}


def qwen_generate(text: str, audio: Path, reference_text: str, model_id: str, out: Path) -> tuple[int, float]:
    import numpy as np
    import soundfile as sf
    import torch
    from qwen_tts import Qwen3TTSModel

    cuda = torch.cuda.is_available()
    model = Qwen3TTSModel.from_pretrained(
        model_id, device_map="cuda:0" if cuda else "cpu",
        dtype=torch.bfloat16 if cuda else torch.float32)
    prompt = model.create_voice_clone_prompt(
        ref_audio=str(audio), ref_text=reference_text, x_vector_only_mode=False)
    samples, sample_rate = [], None
    for section in chunks(text):
        wavs, sr = model.generate_voice_clone(
            text=section, language="Italian", voice_clone_prompt=prompt)
        if not wavs:
            raise RuntimeError("Qwen returned no audio")
        data = np.asarray(wavs[0], dtype=np.float32).reshape(-1)
        if not data.size or not np.isfinite(data).all():
            raise RuntimeError("Qwen returned empty/invalid audio")
        if sample_rate is not None and sr != sample_rate:
            raise RuntimeError("Inconsistent sample rate")
        sample_rate = sr
        samples.append(data)
        samples.append(np.zeros(int(sr * 0.18), dtype=np.float32))
    if not samples:
        raise RuntimeError("No voice segments generated")
    joined = np.concatenate(samples)
    if len(joined) / sample_rate < 5:
        raise RuntimeError("Voice too short")
    sf.write(str(out), np.clip(joined, -0.98, 0.98), sample_rate, subtype="PCM_16")
    return int(sample_rate), round(len(joined) / sample_rate, 3)


def run_job(job_path: Path, out_root: Path, plan_only: bool = False) -> dict:
    job = json.loads(job_path.read_text(encoding="utf8"))
    settings = json.loads(CONFIG.read_text(encoding="utf8"))
    plan = plan_job(job, settings)
    text = safe_repo_file(job["script_path"]).read_text(encoding="utf8").strip()
    if len(text.split()) < 15:
        raise ValueError("Script too short")
    if plan_only:
        return plan
    if plan["state"] != "READY_LOCAL":
        raise RuntimeError(plan["state"] + ": no new audio generated")
    reference = Path(os.environ.get("ARTVISION_VOICE_REFERENCE_WAV", "")).expanduser()
    ref_txt_file = Path(os.environ.get("ARTVISION_VOICE_REFERENCE_TEXT_FILE", "")).expanduser()
    if not reference.is_file() or not ref_txt_file.is_file():
        raise RuntimeError("Local reference WAV and reference transcript are required on the runner")
    if reference.suffix.lower() != ".wav":
        raise RuntimeError("Reference file must be WAV")
    reference_text = ref_txt_file.read_text(encoding="utf8").strip()
    if len(reference_text.split()) < 8:
        raise RuntimeError("Reference transcript is too short")
    out = (out_root / plan["work_id"]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    wav = out / "VOCE.wav"
    meta = out / "VOICE_MANIFEST.json"
    fingerprint = hashlib.sha256(json.dumps({
        "script": text, "voice_profile": plan["voice_profile"],
        "model": plan["model"], "reference_sha": sha256(reference),
        "reference_text_sha": hashlib.sha256(reference_text.encode()).hexdigest()
    }, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    if wav.is_file() and meta.is_file():
        previous = json.loads(meta.read_text(encoding="utf8"))
        if previous.get("fingerprint") == fingerprint and previous.get("wav_sha256") == sha256(wav):
            previous["status"] = "REUSED_VERIFIED_CACHE"
            return previous
    temp = out / "VOCE.partial.wav"
    try:
        sr, duration = qwen_generate(text, reference, reference_text, plan["model"], temp)
        temp.replace(wav)
        if not shutil.which("ffmpeg"):
            raise RuntimeError("ffmpeg needed to produce MP3")
        subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
                        "-y", "-i", str(wav), "-c:a", "libmp3lame", "-b:a", "160k",
                        str(out / "VOCE.mp3")], check=True)
        (out / "COPIONE.txt").write_text(text + "\n", encoding="utf8")
        result = dict(plan, status="GENERATED_REVIEW_ONLY", fingerprint=fingerprint,
                      wav_sha256=sha256(wav), sample_rate=sr,
                      duration_seconds=duration, human_listening_review="pending",
                      renderer_consumption="not_yet_wired")
        meta.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf8")
        return result
    finally:
        temp.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True, type=Path)
    parser.add_argument("--out-root", type=Path, default=Path("output/voice_autopilot"))
    parser.add_argument("--plan", action="store_true")
    args = parser.parse_args()
    try:
        data = run_job(args.job, args.out_root, plan_only=args.plan)
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.CalledProcessError) as exc:
        print("ARTVISION_VOICE_BLOCKED:", type(exc).__name__, str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
