#!/usr/bin/env python3
"""Bruegel Vienna GG1026 V138: two critic review MP4s from one authentic Gacrux WAV.
Strict preflight; no repeat TTS or substituted voice; never publish or auto-approve.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import wave
import zipfile
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from artvision_babel_museum_v137 import (
    title_plate, full_plate, detail, museum_setup, museum_canvas, museum_frame
)
import gemini_voice

W, H, FPS = 720, 1280, 20
DELAY, TAIL = 4.0, 6.0
ART_SHA = "d8d43ac82b04db798b36d9c7f0ab99dba5fb537fa4d8589674d8cd3d1a78f4cd"
RECIPE = ROOT / "modules/artvision_critico/production_series/bruegel_babel_v138.json"


def sha(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def ff(args):
    p = subprocess.run([str(x) for x in args], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError("FFmpeg failed: " + p.stderr[-1500:])


def load():
    d = json.loads(RECIPE.read_text(encoding="utf8"))
    assert d["work_id"] == "bruegel_tower_babel_1563_khm_gg1026"
    assert d["public_title"] == "The Tower of Babel"
    assert len(d["critico"]["chapters"]) == 9
    script = "\n\n".join(x["text"] for x in d["critico"]["chapters"])
    assert 160 <= len(script.split()) <= 225
    return d, script


def assets(out):
    art = out / "ORIGINAL_ARTWORK.jpg"
    photo = out / "AUTHENTIC_KHM_FRAME_PHOTO_CC_BY3.jpg"
    qa137 = out / "QA_V137.json"
    assert art.is_file() and photo.is_file() and qa137.is_file(), "Reuse existing V136+V137 artifact bytes; no Wikimedia retries"
    assert sha(art) == ART_SHA, "Wrong Commons PD artwork; do not call TTS"
    q = json.loads(qa137.read_text())
    meta = q["authentic_frame_photo"]
    assert meta["sha256"] == sha(photo), "Wrong Hiroki Ogawa licensed photo"
    assert meta["dimensions"] in ([1280, 960], [2400, 1800], [960, 720])
    assert "CC BY 3.0" in meta["credit"]
    assert q["museum_approved"] is False
    with Image.open(art) as im:
        assert tuple(im.size) == (3840, 2866)
    with Image.open(photo) as im:
        assert [im.width, im.height] == meta["dimensions"]
    return art, photo, meta


def narration(out):
    d, text = load()
    assets(out)
    assert gemini_voice.VOICE == "Gacrux" and gemini_voice.MODEL == "gemini-3.8-flash-tts"
    report = {
        "status": "BLOCKED_NO_TTS_CALL", "script_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "single_shared_voice": True, "voice": "Gacrux", "model": gemini_voice.MODEL,
        "cost_approval": "only owner's previously attested second Free/no-billing account",
        "gold_v25": False, "published": False
    }
    (out / "COPIONE_ESATTO_V138.txt").write_text(text, encoding="utf8")
    if os.getenv("ARTVISION_GEMINI_PROJECT_BILLING_TIER") != "Free" or not os.getenv("GEMINI_API_KEY"):
        report["reason"] = "Free/no-billing gate or second-account secret absent"
        (out / "VOICE_RESULT_V138.json").write_text(json.dumps(report, indent=2))
        raise RuntimeError("Free/no-billing account not verified; voice API NOT called")
    try:
        data, timed = gemini_voice.synthesize(text, out)
        wav = out / "VOCE.wav"
        duration = len(data) / gemini_voice.SAMPLE_RATE
        assert wav.is_file() and 65 <= duration <= 160
        alignment = json.loads((out / "ALLINEAMENTO_VOCE.json").read_text())
        assert alignment.get("method") == "asr_with_interpolation" and alignment.get("matched_fraction", 0) >= .85
        report.update(status="ONE_SHARED_WAV_READY", wav_sha256=sha(wav),
                      duration_seconds=duration, asr_matched_fraction=alignment["matched_fraction"])
    except Exception as exc:
        report.update(status="VOICE_ATTEMPT_FAILED_NO_AUTOMATIC_RETRY",
                      reason=type(exc).__name__ + ": " + str(exc)[:230],
                      wav_preserved=(out / "VOCE.wav").is_file())
        (out / "VOICE_RESULT_V138.json").write_text(json.dumps(report, indent=2))
        raise
    (out / "VOICE_RESULT_V138.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


def verify_voice(out, script, chapters):
    wav = out / "VOCE.wav"
    cache = json.loads((out / "VOICE_CACHE_V13.json").read_text())
    align = json.loads((out / "ALLINEAMENTO_VOCE.json").read_text())
    assert wav.exists() and cache["wav_sha256"] == sha(wav)
    assert cache["cache_key"] == gemini_voice.cache_key(script)
    assert cache["profile"]["model"] == "gemini-3.8-flash-tts"
    assert cache["profile"]["voice"] == "Gacrux"
    assert align["method"] == "asr_with_interpolation" and align["matched_fraction"] >= .85
    pcm, rate = sf.read(wav, dtype="float32")
    assert rate == 24000 and pcm.ndim == 1 and np.isfinite(pcm).all()
    duration = len(pcm) / rate
    assert 65 <= duration <= 160
    timed = cache["timed"]
    sentence_counts = [len(gemini_voice.sentences(x["text"])) for x in chapters]
    assert len(timed) == sum(sentence_counts)
    ends = []
    ix = 0
    for n in sentence_counts:
        ix += n
        ends.append(float(timed[ix-1][2]))
    assert 0 < ends[0] < ends[-1] <= duration + .1
    return wav, duration, ends, align


def score(out, duration):
    p = out / "ORIGINAL_AMBIENT_V138.wav"
    sr = 32000
    t = np.arange(round(duration * sr), dtype=np.float64) / sr
    audio = np.zeros_like(t)
    for start, length, freqs in [
        (0, duration*.40, [65.4, 98, 130.8]),
        (duration*.31, duration*.42, [73.4, 110, 146.8]),
        (duration*.65, duration*.37, [58.3, 87.3, 116.5])
    ]:
        delta = t - start
        envelope = np.maximum(0, np.minimum(np.minimum(delta / 3.0, (length - delta) / 4.0), 1))
        for j, hz in enumerate(freqs):
            audio += .037 / (j + 1) * np.sin(2*np.pi*hz*t) * envelope
    fade = np.clip(t/2, 0, 1) * np.clip((duration-t)/3, 0, 1)
    pcm = (np.clip(audio*fade, -.7, .7)*28000).astype("<i2")
    with wave.open(str(p), "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(sr); f.writeframes(pcm.tobytes())
    return p


def render_one(kind, art, museum, whole, plate, beats, ends, duration, out):
    total = round((DELAY + duration + TAIL) * FPS)
    path = out / (kind + "_silent.mp4")
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
           "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "pipe:0", "-an",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
           "-pix_fmt", "yuv420p", str(path)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    from bisect import bisect_right
    try:
        for n in range(total):
            sec = n / FPS
            if sec < DELAY:
                u = sec / DELAY
                if kind == "critico_museum":
                    f = museum_frame(museum, "museum_entry" if u < .50 else "museum_enter",
                                     u*2 if u < .50 else (u-.50)*2)
                else:
                    f = plate if sec < 2 else whole
            elif sec >= DELAY + duration:
                u = (sec - DELAY - duration) / TAIL
                if kind == "critico_museum":
                    f = museum_frame(museum, "museum_return" if u < .5 else "museum_exit",
                                     u*2 if u < .5 else (u-.5)*2)
                else:
                    f = whole if u < .5 else plate
            else:
                spoken = sec - DELAY
                i = min(len(beats)-1, bisect_right(ends, spoken))
                left = 0 if i == 0 else ends[i-1]
                right = max(left + .05, ends[i])
                u = max(0, min(1, (spoken - left)/(right-left)))
                cur = beats[i]
                b = [cur["cx"], cur["cy"], cur["crop_height_px"], .04, .01, -.01]
                if kind == "critico_museum" and i:
                    prev = beats[i-1]
                    t = min(1.0, (spoken-left)/2.5)
                    t = t*t*(3-2*t)
                    b[0] = prev["cx"] + (cur["cx"]-prev["cx"])*t
                    b[1] = prev["cy"] + (cur["cy"]-prev["cy"])*t
                    b[2] = prev["crop_height_px"] + (cur["crop_height_px"]-prev["crop_height_px"])*t
                f = whole if i == 8 else detail(art, b, u)
            proc.stdin.write(np.ascontiguousarray(f, dtype=np.uint8).tobytes())
        proc.stdin.close()
        error = proc.stderr.read().decode("utf8", "replace")
        if proc.wait():
            raise RuntimeError("Video encoding error: " + error[-1300:])
    except Exception:
        proc.kill()
        raise
    return path, total


def render(out):
    d, script = load()
    art_path, photo_path, source = assets(out)
    chapters = d["critico"]["chapters"]
    wav, duration, ends, alignment = verify_voice(out, script, chapters)
    art = cv2.imread(str(art_path))
    photo = cv2.imread(str(photo_path))
    assert art is not None and photo is not None
    room = museum_canvas(museum_setup(photo, art))
    whole = full_plate(Image.open(art_path).convert("RGB"))
    plate = title_plate(Image.open(art_path).convert("RGB"))
    total_duration = (round((DELAY+duration+TAIL)*FPS))/FPS
    music = score(out, total_duration)
    shared = out / "BABEL_CRITICO_SHARED_AUDIO_V138.m4a"
    delay = round(DELAY * 1000)
    ff(["ffmpeg", "-v", "error", "-y", "-i", wav, "-i", music,
        "-filter_complex", f"[0:a]adelay={delay}|{delay},volume=1[v];[1:a]volume=.23[m];[v][m]amix=inputs=2:duration=longest:dropout_transition=0,alimiter=limit=.95[a]",
        "-map", "[a]", "-c:a", "aac", "-b:a", "160k", shared])
    entries = {}
    for kind in ("critico_standard", "critico_museum"):
        silent, frames = render_one(kind, art, room, whole, plate, chapters, ends, duration, out)
        target = out / f"BRUEGEL_THE_TOWER_OF_BABEL_{kind.upper()}_V138_REVIEW.mp4"
        ff(["ffmpeg", "-v", "error", "-y", "-i", silent, "-i", shared,
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy", "-c:a", "copy", "-shortest", "-movflags", "+faststart", target])
        ff(["ffmpeg", "-v", "error", "-xerror", "-i", target, "-f", "null", "-"])
        cap = cv2.VideoCapture(str(target))
        assert cap.isOpened()
        count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        assert (count, width, height) == (frames, W, H) and abs(fps-FPS) < .02
        entries[kind] = {"filename": target.name, "sha256": sha(target), "bytes": target.stat().st_size,
                         "frames": frames, "duration_s": total_duration,
                         "FFmpeg_full_decode": "PASS", "museum_approved": False}
        Image.fromarray(cv2.cvtColor(plate if kind == "critico_standard" else museum_frame(room, "museum_entry", 0), cv2.COLOR_BGR2RGB)).save(out/(kind+"_COVER.jpg"), quality=93)
        silent.unlink()
    (out / "RIGHTS_AND_CREDITS.txt").write_text(
        "The Tower of Babel, Pieter Bruegel the Elder, Vienna GG 1026, 1563, 114.4 x 155.5 cm.\n"
        "Painting: Commons public-domain faithful reproduction, same verified bytes V136.\n"
        "Photograph of actual framed artwork: Hiroki Ogawa, 2015, CC BY 3.0 Unported; "
        "Commons official 1280px derivative (not same hash as original 2400px); adapted for zoom and restored painting area.\n"
        "Frame historical origin NOT asserted. Gallery extended digitally; this is not a real museum-room camera recording.\n"
        "Audio: one natural Google Gacrux WAV from owner's Free/no-billing second account; original synthesized music.\n"
        "Commercial, territorial and human artistic review required; NOT PUBLISHED.\n", encoding="utf8")
    for kind in entries:
        (out/(kind+"_SOCIAL_DRAFT.txt")).write_text(
            "The Tower of Babel · Pieter Bruegel the Elder, 1563.\n"
            "Explore the impossible architecture, tiny workers and unfinished spiral in Bruegel's Vienna masterpiece.\n"
            "Artwork: Commons PD-Art; framed-work photograph Hiroki Ogawa CC BY 3.0; music original.\n"
            "DRAFT — NOT PUBLISHED.\n", encoding="utf8")
    report = {"status": "TWO_REAL_MP4_REVIEW_NOT_GOLD", "artwork": "The Tower of Babel",
              "source_art_sha256": ART_SHA, "frame_photo_sha256": sha(photo_path),
              "frame_derivative_dims": source["dimensions"],
              "source_author": "Hiroki Ogawa CC BY 3.0", "same_WAV_sha256": sha(wav),
              "same_AAC_m4a_sha256": sha(shared), "ASR": alignment,
              "files": entries, "museum_approved": False, "human_watch": "PENDING",
              "Gold_V25": False, "social_published": False, "site_playback_verified": False,
              "new_paid_calls_by_renderer": 0}
    report_path = out / "BABEL_CRITICO_V138_QA.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf8")
    archive = out / "BRUEGEL_BABEL_CRITICO_V138_REVIEW_PACKAGE.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=3) as z:
        for k in entries:
            z.write(out/entries[k]["filename"], entries[k]["filename"])
            for suffix in ("_COVER.jpg", "_SOCIAL_DRAFT.txt"):
                z.write(out/(k+suffix), k+suffix)
        for path in (report_path, out/"RIGHTS_AND_CREDITS.txt", out/"COPIONE_ESATTO_V138.txt",
                     out/"VOICE_RESULT_V138.json", out/"ALLINEAMENTO_VOCE.json"):
            z.write(path, path.name)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
    report["package"] = {"filename": archive.name, "bytes": archive.stat().st_size,
                         "sha256": sha(archive), "CRC": "PASS"}
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--phase", choices=("voice", "render"), required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    if a.phase == "voice":
        narration(a.out)
    else:
        render(a.out)


if __name__ == "__main__":
    main()
