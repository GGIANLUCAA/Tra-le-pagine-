#!/usr/bin/env python3
"""ArtVision Eleven v4 one-call museum-authentic critic PILOT.

Standalone review pipeline. Requires owner-selected Eleven voice and one explicit
manual generation. Does NOT change the approved production narrator, or publish.
The final image source must match a pinned SHA before any credit-consuming request.
"""
from __future__ import annotations

import argparse
import base64
from difflib import SequenceMatcher
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RECIPE = ROOT / "modules/artvision_critico/production_series/bruegel_rebel_angels_v144.json"
MODEL = "eleven_v4"
PREVIEW_CHAPTERS = 4
MAX_INPUT_CHARACTERS = 720
MAX_PREVIEW_CREDITS_ESTIMATE = 720
API = "https://api.elevenlabs.io"
UA = "ArtVision-Private-Preflight/1.0 (read-only-public-artwork)"
W, H, FPS = 720, 1280, 12
INTRO, OUTRO = 1.5, 2.5


def sha(data_or_path):
    h = hashlib.sha256()
    if isinstance(data_or_path, (str, Path)):
        with Path(data_or_path).open("rb") as f:
            for p in iter(lambda: f.read(1024 * 1024), b""):
                h.update(p)
    else:
        h.update(data_or_path)
    return h.hexdigest()


def recipe_and_text():
    q = json.loads(RECIPE.read_text(encoding="utf8"))
    assert q["work_id"] == "bruegel_fall_rebel_angels_1562_rmfb_584"
    assert q["source_art_sha256"] == "09f675e7861da808ede4bc1f85573e97884fdbcc6c1d6cb482e3e449d58aace5"
    chapters = q["chapters"][:PREVIEW_CHAPTERS]
    assert len(chapters) == PREVIEW_CHAPTERS
    spoken = "\n\n".join(ch["text"].strip() for ch in chapters)
    if not 150 <= len(spoken) <= MAX_INPUT_CHARACTERS:
        raise ValueError("Unexpected pilot script length")
    return q, chapters, spoken


def json_write(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".part")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    tmp.replace(path)


def artwork_file(q, out, provided=None):
    """No AI art, no unpinned Commons image: verify exact original bytes."""
    from PIL import Image
    out.mkdir(parents=True, exist_ok=True)
    art = out / "ORIGINAL_ARTWORK.jpg"
    if provided:
        data = Path(provided).read_bytes()
        if sha(data) != q["source_art_sha256"]:
            raise ValueError("Provided artwork SHA mismatch; no synthesis")
        art.write_bytes(data)
    elif not art.is_file() or sha(art) != q["source_art_sha256"]:
        name = urllib.parse.unquote(q["source_page"].split("File:", 1)[-1])
        url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(name)
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=80) as response:
                data = response.read(35_000_000)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            raise RuntimeError("Authentic source download unavailable; no Eleven call") from None
        if sha(data) != q["source_art_sha256"]:
            raise RuntimeError("Authentic source differs from pinned SHA; no Eleven call")
        art.write_bytes(data)
    if sha(art) != q["source_art_sha256"]:
        raise RuntimeError("Artwork SHA mismatch")
    with Image.open(art) as img:
        if img.size != tuple(q["source_art_dimensions"]) or img.format != "JPEG":
            raise ValueError("Artwork dimensions/format unexpected")
    return art


def plan(out, artwork=None):
    q, chapters, text = recipe_and_text()
    art = artwork_file(q, out, artwork)
    script_path = out / "COPIONE_ESATTO.txt"
    script_path.write_text(text + "\n", encoding="utf8")
    result = {
        "schema": "artvision-eleven-v4-preview-v1",
        "state": "READY_FOR_MANUAL_VOICE_DECISION",
        "work_id": q["work_id"],
        "title": q["public_title"],
        "model": MODEL,
        "script_sha256": sha(text.encode("utf8")),
        "source_sha256": sha(art),
        "chapters": [{"title": c["title"], "focus": c["focus"], "text": c["text"]}
                     for c in chapters],
        "script_characters": len(text),
        "estimated_credits_at_1_per_character": len(text),
        "allowed_preview_characters": MAX_INPUT_CHARACTERS,
        "voice_calls_allowed_by_default": 0,
        "gallery_or_social_publishing": False,
        "human_voice_review": "pending",
    }
    json_write(out / "PREFLIGHT.json", result)
    return result


def api_get(path, key):
    req = urllib.request.Request(
        API + path,
        headers={"xi-api-key": key, "Accept": "application/json"},
        method="GET"
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError("ElevenLabs read-only preflight HTTP " + str(exc.code)) from None
    except urllib.error.URLError:
        raise RuntimeError("ElevenLabs preflight temporarily unavailable") from None


def account_read_only(key, voice_id, script_chars):
    if not key or not voice_id:
        raise RuntimeError("Missing ELEVENLABS_API_KEY or ELEVENLABS_VOICE_ID")
    if not re.fullmatch(r"[A-Za-z0-9_-]{8,128}", voice_id):
        raise ValueError("Invalid Eleven voice ID")
    subscription = api_get("/v1/user/subscription", key)
    used = subscription.get("character_count")
    limit = subscription.get("character_limit")
    if type(used) is not int or type(limit) is not int or limit < 0:
        raise RuntimeError("Could not verify workspace credits; stop before generation")
    remaining = max(0, limit - used)
    if remaining < 2 * script_chars:
        raise RuntimeError("Insufficient verified credits for conservative preview buffer")
    models = api_get("/v1/models", key)
    matching = [m for m in models if m.get("model_id") == MODEL]
    if not matching or matching[0].get("can_do_text_to_speech") is not True:
        raise RuntimeError("Eleven v4 not available for this API key")
    voice = api_get("/v1/voices/" + urllib.parse.quote(voice_id), key)
    if voice.get("voice_id") != voice_id:
        raise RuntimeError("Voice not owned/accessible by current API key")
    return {
        "verified_model": MODEL,
        "verified_voice_name": voice.get("name"),
        "verified_voice_category": voice.get("category"),
        "workspace_tier": subscription.get("tier"),
        "workspace_remaining_before": remaining,
        "script_characters": script_chars,
        "estimated_credits_at_1_per_character": script_chars,
        "credits_hard_cap_guaranteed": False,
        "note": "Credits are estimated, not reserved. No auto top-up, no retries."
    }


def download_one_voice(text, key, voice_id, out):
    # One HTTP POST only; no retry after timeout, because the provider may have billed.
    # Character-timing endpoint returns audio and alignment in a single billable call.
    body = json.dumps({
        "text": text,
        "model_id": MODEL,
        "language_code": "it"
    }, ensure_ascii=False).encode("utf8")
    url = API + "/v1/text-to-speech/" + urllib.parse.quote(voice_id) + "/with-timestamps?output_format=mp3_44100_128"
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"xi-api-key": key, "Content-Type": "application/json",
                 "Accept": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=175) as r:
            payload = json.load(r)
    except urllib.error.HTTPError as exc:
        raise RuntimeError("Single Eleven synthesis HTTP " + str(exc.code) + ". DO NOT AUTO-RETRY") from None
    except Exception:
        raise RuntimeError("Eleven synthesis uncertain; DO NOT RETRY automatically") from None
    if not isinstance(payload, dict) or not payload.get("audio_base64"):
        raise RuntimeError("Synthesis response missing audio; DO NOT AUTO-RETRY")
    try:
        audio = base64.b64decode(payload["audio_base64"], validate=True)
    except Exception:
        raise RuntimeError("Synthesis audio decode failed; DO NOT AUTO-RETRY") from None
    if len(audio) < 1024 or not audio.startswith((b"ID3", b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")):
        raise RuntimeError("Synthesis MP3 invalid; DO NOT AUTO-RETRY")
    audio_path = out / "VOCE_ELEVEN_V4.mp3"
    audio_path.write_bytes(audio)  # Persist before alignment so a failed render cannot burn credits again.
    alignment = payload.get("normalized_alignment") or payload.get("alignment")
    json_write(out / "ELEVEN_TIMESTAMPS.json", alignment or {"error": "missing"})
    return audio_path, alignment


def chapter_ranges(text, chapters, alignment, duration):
    """Use verified character-level timestamps; do not guess picture timing."""
    if not isinstance(alignment, dict):
        raise ValueError("Missing precise ElevenLabs timestamps; preserve audio")
    chars = alignment.get("characters")
    starts = alignment.get("character_start_times_seconds")
    ends = alignment.get("character_end_times_seconds")
    if not isinstance(chars, list) or not isinstance(starts, list) or not isinstance(ends, list):
        raise ValueError("Invalid Eleven alignment structure")
    if not chars or len(chars) != len(starts) or len(chars) != len(ends):
        raise ValueError("Eleven alignment lengths inconsistent")
    heard = "".join(chars)
    matching = SequenceMatcher(None, text.casefold(), heard.casefold(), autojunk=False)
    blocks = matching.get_matching_blocks()
    if sum(b.size for b in blocks) / max(len(text), len(heard)) < .87:
        raise ValueError("Text/timestamp mismatch; do not fake synchronization")
    indices = {}
    for b in blocks:
        for k in range(b.size):
            indices[b.a + k] = b.b + k
    results = []
    offset = 0
    for i, ch in enumerate(chapters):
        part = ch["text"].strip()
        left, right = offset, offset + len(part) - 1
        hits = [indices[k] for k in range(left, right + 1) if k in indices]
        if len(hits) < .82 * len(part):
            raise ValueError("Unreliable per-scene alignment; preserve voice")
        a = float(starts[hits[0]])
        b = float(ends[hits[-1]])
        if not (0 <= a < b <= duration + .4):
            raise ValueError("Timeline is not finite/monotonic or longer than voice")
        results.append({"chapter": i, "title": ch["title"], "focus": ch["focus"],
                        "voice_start": round(a, 3), "voice_end": round(b, 3),
                        "video_start": round(INTRO + a, 3),
                        "video_end": round(INTRO + b, 3)})
        offset += len(part) + (2 if i < len(chapters) - 1 else 0)
    for before, after in zip(results, results[1:]):
        if after["voice_start"] < before["voice_end"] - .1:
            raise ValueError("Overlapping scene timings")
    return results


def audio_duration(path):
    info = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path)
    ], text=True)
    return float(info)


def render(out, art, q, chapters, timing, audio, duration):
    from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
    from bisect import bisect_right
    import numpy as np
    source = Image.open(art).convert("RGB")
    base = source.resize((W, H)).filter(ImageFilter.GaussianBlur(35))
    base = ImageEnhance.Brightness(base).enhance(.32)
    whole = source.copy()
    whole.thumbnail((W - 24, H - 160), Image.Resampling.LANCZOS)
    whole_plate = base.copy()
    whole_plate.paste(whole, ((W - whole.width) // 2, (H - whole.height) // 2))
    cover = whole_plate.copy()
    drawer = ImageDraw.Draw(cover)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
    title_font = ImageFont.truetype(font_path, 35) if Path(font_path).exists() else ImageFont.load_default()
    drawer.text((28, 45), "THE FALL OF THE REBEL ANGELS", font=title_font, fill=(237, 231, 220),
                stroke_width=1, stroke_fill=(12, 12, 12))
    cover.save(out / "COVER.jpg", quality=94)
    total = INTRO + duration + OUTRO
    silent = out / "SILENT_PILOT.mp4"
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "pipe:0", "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "22", "-pix_fmt", "yuv420p", str(silent)
    ]
    ends = [t["voice_end"] for t in timing]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    snapshots = []
    try:
        for n in range(round(total * FPS)):
            sec = n / FPS
            spoken = sec - INTRO
            if sec < INTRO * .75 or spoken >= duration:
                frame = cover if sec < INTRO * .75 or sec > total - OUTRO / 2 else whole_plate
            elif sec < INTRO:
                frame = whole_plate
            else:
                j = min(len(chapters) - 1, bisect_right(ends, spoken))
                item = chapters[j]
                a = 0 if j == 0 else timing[j-1]["voice_end"]
                b = timing[j]["voice_end"]
                u = max(0., min(1., (spoken - a) / max(.1, b - a)))
                if j in (0, 1):
                    frame = whole_plate
                else:
                    scale = 1.0 - .045 * u  # subtle camera movement, not forced pacing
                    ch = int(item["crop_height_px"] * scale)
                    cw = round(ch * W / H)
                    cx = int(source.width * item["cx"])
                    cy = int(source.height * item["cy"])
                    x0 = max(0, min(source.width-cw, cx-cw//2))
                    y0 = max(0, min(source.height-ch, cy-ch//2))
                    frame = source.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.Resampling.LANCZOS)
            if n in (1, round(total * FPS * .3), round(total * FPS * .65)):
                snapshots.append(frame.copy().resize((180, 320)))
            proc.stdin.write(np.asarray(frame, dtype=np.uint8).tobytes())
        proc.stdin.close()
        stderr = proc.stderr.read()
        if proc.wait():
            raise RuntimeError("FFmpeg visual render failed: " + stderr.decode("utf8", "replace")[-400:])
    except Exception:
        proc.kill()
        raise
    review = out / "BRUEGEL_ELEVEN_V4_CRITICO_REVIEW.mp4"
    # Real spoken audio starts after a short visual introduction; no AI-generated music.
    subprocess.run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(silent), "-i", str(audio),
        "-filter_complex", f"[1:a]adelay={round(INTRO*1000)}|{round(INTRO*1000)}[narration]",
        "-map", "0:v", "-map", "[narration]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
        "-movflags", "+faststart", str(review)
    ], check=True)
    # Decode both streams, not just check file existence.
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-xerror", "-i", str(review), "-f", "null", "-"], check=True)
    if snapshots:
        sheet = Image.new("RGB", (180 * len(snapshots), 320), (20, 20, 20))
        for i, snap in enumerate(snapshots):
            sheet.paste(snap, (i * 180, 0))
        sheet.save(out / "CONTACT_SHEET.jpg", quality=91)
    silent.unlink(missing_ok=True)
    return review


def package(out, q, plan_data, voice_path, review, timing):
    json_write(out / "TIMELINE.json", timing)
    (out / "SOURCES_AND_RIGHTS.txt").write_text(
        "Pieter Bruegel the Elder, The Fall of the Rebel Angels (1562).\n"
        + "Real artwork photo source: " + q["source_page"] + "\n"
        + "Source SHA256: " + q["source_art_sha256"] + "\n"
        + "Voice: owner-selected ElevenLabs eleven_v4 pilot; requires rights review.\n"
        + "No gallery/social publication. No museum or historical frame simulated.\n"
        + "No music in this VOICE-only comparison pilot.\n", encoding="utf8")
    qa = {
        "state": "TECHNICAL_REVIEW_READY_ARTISTIC_REVIEW_PENDING",
        "voice": "ElevenLabs eleven_v4",
        "voice_sha256": sha(voice_path),
        "mp4_sha256": sha(review),
        "source_sha256": q["source_art_sha256"],
        "scene_count": len(timing),
        "speech_synchronized_from": "ElevenLabs character timings, same voice request",
        "credit_calls_this_run": 1,
        "estimated_credits_at_1_per_character": plan_data["script_characters"],
        "human_listening": "pending",
        "voice_vs_gacrux_comparison": "pending",
        "published": False,
        "gold": False
    }
    json_write(out / "QA_ELEVEN_V4.json", qa)
    files = [review, voice_path, out / "COPIONE_ESATTO.txt", out / "TIMELINE.json",
             out / "QA_ELEVEN_V4.json", out / "SOURCES_AND_RIGHTS.txt",
             out / "COVER.jpg", out / "CONTACT_SHEET.jpg"]
    bundle = out / "ARTVISION_BRUEGEL_ELEVEN_V4_REVIEW.zip"
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for f in files:
            if f.exists():
                z.write(f, f.name)
    with zipfile.ZipFile(bundle) as z:
        if z.testzip() is not None:
            raise RuntimeError("ZIP failed CRC test")
    return qa


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--stage", choices=("preflight", "account", "generate"), default="preflight")
    p.add_argument("--out", type=Path, default=Path("output/eleven_v4_bruegel_preview"))
    p.add_argument("--artwork", type=Path)
    args = p.parse_args()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    try:
        q, chapters, script = recipe_and_text()
        info = plan(out, args.artwork)
        if args.stage == "preflight":
            print(json.dumps(info, ensure_ascii=False, indent=2))
            return 0
        key = os.environ.get("ELEVENLABS_API_KEY", "")
        voice = os.environ.get("ELEVENLABS_VOICE_ID", "")
        account = account_read_only(key, voice, len(script))
        json_write(out / "ELEVEN_ACCOUNT_PREFLIGHT.json", account)
        if args.stage == "account":
            print(json.dumps(account, ensure_ascii=False, indent=2))
            return 0
        if os.environ.get("ARTVISION_ELEVEN_ALLOW_ONE_CALL") != "ONE_PREVIEW_ONLY":
            raise RuntimeError("Single-use credit confirmation missing: 0 TTS calls")
        if (out / "VOCE_ELEVEN_V4.mp3").exists():
            raise RuntimeError("Audio already exists: reuse; do NOT regenerate")
        audio, alignment = download_one_voice(script, key, voice, out)
        duration = audio_duration(audio)
        if not 8 <= duration <= 120:
            raise RuntimeError("Voice duration outside pilot limits; preserve original MP3")
        scenes = chapter_ranges(script, chapters, alignment, duration)
        mp4 = render(out, out / "ORIGINAL_ARTWORK.jpg", q, chapters, scenes, audio, duration)
        qa = package(out, q, info, audio, mp4, scenes)
        print(json.dumps(qa, ensure_ascii=False, indent=2))
        return 0
    except Exception as e:
        print("ARTVISION_ELEVEN_PILOT_BLOCKED:", type(e).__name__, str(e)[:330], file=sys.stderr)
        print("No automatic regeneration. Preserve any previously synthesized MP3.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
