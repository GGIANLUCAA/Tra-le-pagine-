#!/usr/bin/env python3
"""V46: integrate a REAL Vidu I2V clip into an existing narrated MP4, no billing.

Requires a Vidu task receipt and a plan with matching exact SHA256.
Output is always rendered_needs_review, never final or pre-approved.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def probe(path: Path) -> dict:
    p = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,width,height:format=duration", "-of", "json", str(path)],
        capture_output=True, text=True, check=True)
    d = json.loads(p.stdout)
    return {
        "duration": float(d["format"]["duration"]),
        "video": next(s for s in d["streams"] if s["codec_type"] == "video"),
        "audio": any(s["codec_type"] == "audio" for s in d["streams"]),
    }


def validate(original: Path, clip: Path, plan_file: Path, record_file: Path,
             start: float, seconds: int):
    for path in (original, clip, plan_file, record_file):
        if not path.is_file() or path.stat().st_size < 100:
            raise ValueError("Input mancante o incompleto: " + str(path))
    plan = json.loads(plan_file.read_text(encoding="utf8"))
    rec = json.loads(record_file.read_text(encoding="utf8"))
    if (rec.get("status") != "success" or not rec.get("task_id") or
            rec.get("fingerprint") != plan.get("fingerprint") or
            rec.get("download_sha256") != digest(clip) or
            plan.get("provider") != "vidu" or
            plan.get("duration") != seconds):
        raise ValueError("Clip senza ricevuta Vidu valida: NON sostituire con motion locale")
    orig = probe(original)
    generated = probe(clip)
    if not orig["audio"]:
        raise ValueError("Il master narrato non ha audio")
    if not 1 <= seconds <= 10 or not .2 <= start < orig["duration"] - seconds - .2:
        raise ValueError("La clip e fuori dalla timeline del master")
    if abs(generated["duration"] - seconds) > .25:
        raise ValueError("Durata I2V differente da quella prevista")
    w, h = orig["video"]["width"], orig["video"]["height"]
    cw, ch = generated["video"]["width"], generated["video"]["height"]
    if abs(w / h - cw / ch) > .045:
        raise ValueError("Aspect ratio diverso: vietato tagliare scene per adattarle")
    return plan, rec, orig, (w, h)


def integrate(original: Path, clip: Path, plan_file: Path, record_file: Path,
              start: float, seconds: int, output: Path) -> dict:
    plan, receipt, original_media, (w, h) = validate(
        original, clip, plan_file, record_file, start, seconds)
    if output.exists() or output.resolve() == original.resolve():
        raise ValueError("Non sovrascrivere file gia esistenti")
    output.parent.mkdir(parents=True, exist_ok=True)
    end = start + seconds
    # Replace ONLY the selected section, no crossfade/ghosting.
    # Keep audio EXACTLY from the original, avoiding a second TTS call.
    filtergraph = (
        f"[0:v]split=2[pre][post];"
        f"[pre]trim=start=0:end={start:.3f},setpts=PTS-STARTPTS,fps=24,format=yuv420p[p];"
        f"[post]trim=start={end:.3f},setpts=PTS-STARTPTS,fps=24,format=yuv420p[q];"
        f"[1:v]scale={w}:{h}:flags=lanczos,setsar=1,"
        f"trim=start=0:duration={seconds},setpts=PTS-STARTPTS,fps=24,format=yuv420p[ai];"
        f"[p][ai][q]concat=n=3:v=1:a=0[v]")
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(original), "-i", str(clip), "-filter_complex", filtergraph,
        "-map", "[v]", "-map", "0:a:0", "-c:v", "libx264",
        "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
        "-c:a", "copy", "-movflags", "+faststart", str(output),
    ]
    subprocess.run(cmd, check=True, timeout=450)
    result_media = probe(output)
    if (not result_media["audio"] or
            abs(result_media["duration"] - original_media["duration"]) > .35):
        output.unlink(missing_ok=True)
        raise RuntimeError("Audio e durata del filmato originale non preservati")
    from animated_video_release_gate_v44 import draft
    report = draft(
        original, output, clip, "generative_i2v",
        "Il viaggiatore attraversa il tempo.",
        "The machine advances while landscapes and centuries move past")
    report["provenance"] = {
        "kind": "provider_i2v", "provider": "vidu",
        "task_id": receipt["task_id"],
        "source_image_sha256": plan["image_sha256"],
        "approval_fingerprint": plan["fingerprint"],
        "billed_credits_verified": False,
    }
    report["scene"]["time_start_seconds"] = start
    report["scene"]["time_end_seconds"] = end
    report["source_task_record"] = str(record_file)
    manifest = output.with_suffix(".REVISIONE_V44.json")
    manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf8")
    return {
        "status": "rendered_needs_review",
        "output": str(output),
        "duration": result_media["duration"],
        "review_manifest": str(manifest),
        "task_id": receipt["task_id"],
        "no_new_vidu_generation": True,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--master", type=Path, required=True)
    ap.add_argument("--vidu-clip", type=Path, required=True)
    ap.add_argument("--plan", type=Path, required=True)
    ap.add_argument("--task-record", type=Path, required=True)
    ap.add_argument("--start", type=float, required=True)
    ap.add_argument("--seconds", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    print(json.dumps(integrate(
        a.master, a.vidu_clip, a.plan, a.task_record,
        a.start, a.seconds, a.out), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
