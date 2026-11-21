#!/usr/bin/env python3
"""ArtVision Qwen cloud voice pilot: GitHub-hosted runner + HF ZeroGPU.
No PC, Google calls, billable fallback, automatic publishing, or unapproved narrator.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/artvision_voice_profiles_v1.json"
FORMATS = ("critico_standard", "critico_museum")


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def script_path(relative: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise ValueError("Missing script path")
    p = (ROOT / relative).resolve()
    if not p.is_relative_to(ROOT) or not p.is_file() or p.suffix not in (".txt", ".md"):
        raise ValueError("Copione must be .txt/.md inside repo")
    return p


def segments(text: str, limit: int = 300) -> list[str]:
    """Keep sentences whole where possible. No assistant-added words."""
    sentences = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text).strip())
    out, buf = [], ""
    for sentence in sentences:
        for part in ([sentence] if len(sentence) <= limit else
                     re.findall(r".{1,%d}(?:\s|$)|\S+" % (limit - 20), sentence)):
            part = part.strip()
            if not part:
                continue
            if len(buf) + len(part) + 1 > limit and buf:
                out.append(buf)
                buf = ""
            buf = (buf + " " + part).strip()
    if buf:
        out.append(buf)
    return out


def plan(job: dict, cfg: dict) -> dict:
    work = job.get("work_id")
    if not isinstance(work, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{1,79}", work):
        raise ValueError("Invalid work_id")
    fmt = job.get("format")
    if fmt not in FORMATS:
        raise ValueError("Only critico formats supported")
    if job.get("allow_paid_api") is not False or job.get("auto_publish") is not False:
        raise ValueError("Paid API and autopublishing must be false")
    profile_id = job.get("voice_profile", cfg["default_by_format"][fmt])
    profile = cfg["profiles"].get(profile_id)
    if not profile or profile.get("engine") != "hf_zerogpu":
        raise ValueError("Use a Qwen ZeroGPU cloud profile only: no Google or PC")
    state = ("READY_CLOUD" if profile.get("approved") is True else
             "REVIEW_ONLY" if job.get("review_only") is True and profile.get("review_samples_allowed") is True else
             "WAITING_OWNER_APPROVAL")
    return dict(work_id=work, format=fmt, voice_profile=profile_id,
                state=state, model=profile["model"], engine="hf_zerogpu",
                shared_variants=list(FORMATS), paid_api_calls=0,
                auto_publish=False)


def get_private_reference(token: str) -> tuple[Path, str]:
    """Owner stores sample and exact transcript in a private HF dataset, never GitHub."""
    from huggingface_hub import hf_hub_download
    repo = os.environ.get("ARTVISION_HF_VOICE_DATASET", "").strip()
    if not repo or repo.count("/") != 1:
        raise RuntimeError("ARTVISION_HF_VOICE_DATASET must be owner/private-dataset")
    audio = Path(hf_hub_download(repo_id=repo, repo_type="dataset",
                                 filename="voice_reference.wav", token=token))
    txt = Path(hf_hub_download(repo_id=repo, repo_type="dataset",
                               filename="voice_reference.txt", token=token))
    transcript = txt.read_text(encoding="utf-8").strip()
    if len(transcript.split()) < 8:
        raise RuntimeError("Voice reference transcript missing/too short")
    return audio, transcript


def free_hf_account(token: str) -> None:
    from huggingface_hub import HfApi
    who = HfApi(token=token).whoami()
    if who.get("isPro") is True:
        raise RuntimeError("PRO account rejected: this adapter allows only Free tier")
    if not who.get("name"):
        raise RuntimeError("Hugging Face authentication not verified")


def synthesize(job_path: Path, outroot: Path, plan_only: bool) -> dict:
    job = json.loads(job_path.read_text(encoding="utf8"))
    cfg = json.loads(CONFIG.read_text(encoding="utf8"))
    result = plan(job, cfg)
    text = script_path(job["script_path"]).read_text(encoding="utf8").strip()
    if len(text.split()) < 15:
        raise ValueError("Copione too short")
    if plan_only:
        return result
    if result["state"] == "WAITING_OWNER_APPROVAL":
        raise RuntimeError("Candidate voice not approved: no third-party calls")
    if result["state"] == "REVIEW_ONLY":
        if len(text) > 350:
            raise RuntimeError("First voice review is limited to 350 characters")
    portions = segments(text, limit=300)
    if not portions or len(portions) > 4:
        raise RuntimeError("Max four chunks per job while testing limited free GPU quota")

    token = os.environ.get("HF_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Missing GitHub secret HF_TOKEN")
    free_hf_account(token)
    audio, transcript = get_private_reference(token)

    fingerprint = hashlib.sha256(json.dumps({
        "text": text, "profile": result["voice_profile"], "model": result["model"],
        "audio_sha256": sha256(audio), "transcript": transcript,
    }, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    out = (outroot / result["work_id"]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    wav = out / "VOCE.wav"
    metadata = out / "VOICE_MANIFEST.json"
    if metadata.exists() and wav.exists():
        prior = json.loads(metadata.read_text(encoding="utf8"))
        if prior.get("fingerprint") == fingerprint and prior.get("wav_sha256") == sha256(wav):
            return dict(prior, state="VERIFIED_CACHED_AUDIO")

    from gradio_client import Client, handle_file
    import numpy as np
    import soundfile as sf

    client = Client("Qwen/Qwen3-TTS", token=token, verbose=False)
    samples, rate = [], None
    for index, portion in enumerate(portions):
        # The official UI currently exposes "Auto" rather than "Italian".
        # Always test Italian speech quality before approval.
        response = client.predict(handle_file(str(audio)), transcript, portion,
                                  "Auto", False, "1.7B",
                                  api_name="/generate_voice_clone")
        raw = response[0] if isinstance(response, (tuple, list)) else response
        if isinstance(raw, dict):
            raw = raw.get("path")
        if not isinstance(raw, (str, Path)) or not Path(raw).is_file():
            raise RuntimeError("Remote Qwen did not return a readable audio file")
        data, sr = sf.read(str(raw), dtype="float32", always_2d=True)
        data = data.mean(axis=1)
        if data.size < 1000 or not np.isfinite(data).all():
            raise RuntimeError("Invalid remote audio")
        if rate is not None and sr != rate:
            raise RuntimeError("Inconsistent Qwen sample rates")
        rate = sr
        samples.append(data)
        if index < len(portions) - 1:
            samples.append(np.zeros(int(sr * 0.18), dtype="float32"))
    joined = np.concatenate(samples)
    sf.write(str(wav), np.clip(joined, -0.98, 0.98), rate, subtype="PCM_16")
    subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
                    "-y", "-i", str(wav), "-c:a", "libmp3lame", "-b:a", "160k",
                    str(out / "VOCE.mp3")], check=True)
    (out / "COPIONE.txt").write_text(text + "\n", encoding="utf8")
    result.update(state="CLOUD_VOICE_REVIEW_PENDING", fingerprint=fingerprint,
                  wav_sha256=sha256(wav), sample_rate=rate,
                  duration_seconds=round(len(joined) / rate, 2),
                  human_listening_review="pending",
                  renderer_handoff="not_yet_connected",
                  remote_engine="Qwen/Qwen3-TTS public ZeroGPU Space")
    metadata.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf8")
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", type=Path, required=True)
    ap.add_argument("--out-root", type=Path, default=Path("output/voice_cloud"))
    ap.add_argument("--plan", action="store_true")
    args = ap.parse_args()
    try:
        print(json.dumps(synthesize(args.job, args.out_root, args.plan),
                         indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f"VOICE_CLOUD_BLOCKED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
