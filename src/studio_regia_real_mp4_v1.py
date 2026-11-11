#!/usr/bin/env python3
"""Read-only, time-bounded visual rhythm audit on REAL MP4 bytes.

This extracts low-resolution samples from a real local video, with FFmpeg, and
reports possible visual stalls, dark intervals and major visual changes.
It cannot infer image meaning, historical truth, rights, beauty or approval.
No network, paid AI, altered masters or publication.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageOps, ImageStat

MAX_SAMPLES = 160
MAX_DURATION_S = 600
MAX_VIDEO_BYTES = 300 * 1024 * 1024


def digest(path):
    sha = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            sha.update(chunk)
    return sha.hexdigest()


def probe(path):
    cmd = ["ffprobe", "-v", "error", "-show_entries",
           "format=duration:stream=codec_type,codec_name,width,height",
           "-of", "json", str(path)]
    info = json.loads(subprocess.check_output(cmd, text=True, timeout=30))
    dur = float(info.get("format", {}).get("duration", 0))
    streams = info.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if not math.isfinite(dur) or dur <= 0 or video is None:
        raise ValueError("MP4 has no valid video stream/duration")
    if dur > MAX_DURATION_S:
        raise ValueError("Audit duration limit: use an explicitly scoped episode <= 600s")
    return dur, video, audio


def dhash(gray):
    small = gray.resize((9, 8), Image.Resampling.BILINEAR)
    pixels = list(small.getdata())
    return sum((1 << (row * 8 + col)) for row in range(8) for col in range(8)
               if pixels[row * 9 + col] > pixels[row * 9 + col + 1])


def _diff(a, b):
    return ImageStat.Stat(ImageChops.difference(a, b)).mean[0]


def _sheet(frames, picks, times, dest):
    tw, th, cols = 200, 242, 6
    selected = sorted(set(picks))
    rows = math.ceil(len(selected) / cols)
    image = Image.new("RGB", (cols * tw, rows * th), (21, 24, 32))
    draw = ImageDraw.Draw(image)
    for index, frame_index in enumerate(selected):
        with Image.open(frames[frame_index]) as img:
            shot = ImageOps.contain(img.convert("RGB"), (tw - 10, th - 29))
        x, y = (index % cols) * tw, (index // cols) * th
        image.paste(shot, (x + (tw - shot.width) // 2, y + (th - 29 - shot.height) // 2))
        draw.text((x + 10, y + th - 25), "t≈%.1fs" % times[frame_index], fill=(233, 233, 233))
    image.save(dest, quality=88)


def analyze(video, out, *, sample_cap=MAX_SAMPLES):
    source = Path(video)
    if not source.is_file() or not 0 < source.stat().st_size <= MAX_VIDEO_BYTES:
        raise ValueError("Real local MP4 required, non-empty and <=300 MB")
    if type(sample_cap) is not int or not 12 <= sample_cap <= MAX_SAMPLES:
        raise ValueError("sample_cap must be an integer in 12..160")
    duration, vstream, astream = probe(source)
    result_dir = Path(out)
    result_dir.mkdir(parents=True, exist_ok=True)
    # The sampling interval covers the whole video rather than its first part.
    step = max(.5, duration / (sample_cap - 1))
    with tempfile.TemporaryDirectory(prefix="regia-real-frame-") as temp:
        pattern = str(Path(temp) / "frame_%05d.jpg")
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin",
            "-i", str(source), "-vf", f"fps=1/{step:.5f},scale=240:-2",
            "-frames:v", str(sample_cap), "-q:v", "5", "-y", pattern,
        ], check=True, timeout=180, capture_output=True, text=True)
        frames = sorted(Path(temp).glob("frame_*.jpg"))
        if not frames:
            raise ValueError("No actual frames extracted from MP4")
        times = [round(min(duration, (i + .5) * step), 3) for i in range(len(frames))]
        stats, changes, dark, still = [], [], [], []
        previous = None
        previous_hash = None
        for i, path in enumerate(frames):
            with Image.open(path) as img:
                rgb = img.convert("RGB")
                gray = ImageOps.grayscale(rgb)
                values = list(gray.resize((48, 48)).getdata())
                darkness = sum(v < 10 for v in values) / len(values)
                mean = ImageStat.Stat(gray).mean[0]
                hsv = rgb.convert("HSV")
                saturation = ImageStat.Stat(hsv).mean[1] / 255
                hashed = dhash(gray)
                change = None if previous is None else _diff(gray, previous)
                bit_changes = None if previous_hash is None else (hashed ^ previous_hash).bit_count()
                is_dark = darkness > .95 and mean < 12
                is_still = change is not None and change < 1.6 and bit_changes <= 2
                is_jump = change is not None and change > 24 and bit_changes >= 12
                if is_dark:
                    dark.append(i)
                if is_still:
                    still.append(i)
                if is_jump:
                    changes.append(i)
                stats.append({
                    "sample_index": i, "approx_time_s": times[i],
                    "mean_luma": round(mean, 1),
                    "mean_saturation": round(saturation, 3),
                    "mean_abs_change": None if change is None else round(change, 2),
                    "dhash_distance": bit_changes,
                    "nearly_black": is_dark,
                    "nearly_unchanged": is_still,
                    "large_visual_jump": is_jump,
                })
                previous = gray.copy()
                previous_hash = hashed
        # Long contiguous intervals of negligible change, not aesthetic failures.
        spans = []
        start = None
        for idx in range(1, len(stats) + 1):
            active = idx < len(stats) and stats[idx]["nearly_unchanged"]
            if active and start is None:
                start = idx - 1
            if start is not None and not active:
                end = idx - 1
                seconds = max(0, (end - start) * step)
                if seconds >= 3.5:
                    spans.append({
                        "approx_start_s": times[start],
                        "approx_end_s": times[end],
                        "sampled_span_s": round(seconds, 2),
                        "severity": "review_only",
                    })
                start = None
        prolonged_dark = []
        if dark:
            first = last = dark[0]
            for index in dark[1:] + [len(frames) + 3]:
                if index == last + 1:
                    last = index
                    continue
                if (last - first + 1) * step >= 1.8:
                    prolonged_dark.append({"approx_start_s": times[first],
                                           "approx_end_s": times[last]})
                first = last = index
        warnings = []
        for span in spans:
            warnings.append({"code": "POSSIBLE_VISUAL_STALL",
                             "at_s": span["approx_start_s"],
                             "detail": "Frame quasi invariati: verificare se la pausa e intenzionale"})
        for interval in prolonged_dark:
            warnings.append({"code": "LONG_DARK_SECTION", "at_s": interval["approx_start_s"],
                             "detail": "Controllare se il nero prolungato e voluto"})
        if duration >= 20 and not changes:
            warnings.append({"code": "LOW_DETECTED_VISUAL_VARIATION", "at_s": 0,
                             "detail": "Nessun salto netto fra i campioni: camera continua o poca varieta; verificare a velocita normale"})
        # Contact sheet includes opening, ending, evenly-spaced coverage and some jumps.
        picks = [min(len(frames)-1, int(round((len(frames)-1)*i/19))) for i in range(20)]
        picks += [0, min(1, len(frames)-1), min(3, len(frames)-1)]
        picks += changes[:4]
        sheet = result_dir / "REGIA_REAL_MP4_CONTACT_SHEET.jpg"
        _sheet(frames, picks, times, sheet)
    report = {
        "schema": "studio-regia-real-mp4-v1",
        "source": {"file_name": source.name, "sha256": digest(source),
                   "size_bytes": source.stat().st_size,
                   "duration_s": round(duration, 3),
                   "width": vstream.get("width"), "height": vstream.get("height"),
                   "video_codec": vstream.get("codec_name"),
                   "audio_codec": astream.get("codec_name") if astream else None},
        "sampling": {"method": "ffmpeg full-video fixed time-grid, scaled image comparison",
                     "approx_step_s": round(step, 3),
                     "frames_checked": len(stats),
                     "limitations": "Sampling misses rapid cuts, exact PTS and subtle motion; change metrics are not scene/semantic recognition."},
        "potential_cuts_approx_s": [times[i] for i in changes][:40],
        "potential_still_intervals": spans,
        "potential_dark_intervals": prolonged_dark,
        "warnings": warnings,
        "contact_sheet": sheet.name,
        "frame_stats": stats,
        "status": "needs_actual_visual_and_audio_review",
        "original_mp4_unchanged": True,
        "artistically_approved": False,
        "final_master": False,
        "published": False,
        "paid_calls": 0,
    }
    (result_dir / "REGIA_REAL_MP4_V1.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--video", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    report = analyze(args.video, args.out)
    print(json.dumps({"status": report["status"],
                      "sha256": report["source"]["sha256"],
                      "duration_s": report["source"]["duration_s"],
                      "potential_cuts_approx_s": report["potential_cuts_approx_s"],
                      "potential_still_intervals": report["potential_still_intervals"],
                      "warnings": report["warnings"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
