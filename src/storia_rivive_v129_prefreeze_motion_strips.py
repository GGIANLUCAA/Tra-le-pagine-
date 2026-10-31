#!/usr/bin/env python3
"""V129: five SHA-bound *moving* pre-freeze film strips, for human review only.

Diagnostic 4-fps proxies are deliberately NOT frame-accurate freeze evidence,
proof of camera-shot differences, Italian rights, or permission to generate.
The full film and moving excerpts are never uploaded as artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path

from PIL import Image, ImageDraw

try:
    from src.storia_rivive_v128_balanced_frame_review import sha256_file, verified_source_rows
    from src.storia_rivive_motion_window_v115 import check_source_window
except ModuleNotFoundError:
    from storia_rivive_v128_balanced_frame_review import sha256_file, verified_source_rows
    from storia_rivive_motion_window_v115 import check_source_window

WIDTH, HEIGHT, CHANNELS = 240, 135, 3
FRAME_BYTES = WIDTH * HEIGHT * CHANNELS
MAX_PROXY_FRAMES = 10


def decode_proxy(video, start_pts, freeze_pts, time_base, *, ffmpeg="ffmpeg"):
    """Decode a few scaled *approximate* time samples; never reuse for freeze."""
    ok, reason = check_source_window(start_pts, freeze_pts, time_base)
    if not ok:
        raise ValueError("V129_INVALID_PRE_FREEZE_WINDOW_" + reason)
    if not shutil.which(ffmpeg):
        raise ValueError("V129_FFMPEG_MISSING")
    n, d = map(int, time_base.split("/"))
    start = float(Fraction(start_pts * n, d))
    duration = float(Fraction((freeze_pts-start_pts)*n, d))
    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin",
           "-ss", f"{start:.9f}", "-i", str(video), "-t", f"{duration:.9f}",
           "-an", "-sn", "-dn", "-vf",
           f"fps=4,scale={WIDTH}:{HEIGHT}:flags=area,format=rgb24",
           "-frames:v", str(MAX_PROXY_FRAMES), "-f", "rawvideo",
           "-pix_fmt", "rgb24", "pipe:1"]
    try:
        completed = subprocess.run(cmd, capture_output=True, timeout=40, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError("V129_PRE_FREEZE_DECODE_ERROR") from exc
    data = completed.stdout
    if (completed.returncode != 0 or len(data) % FRAME_BYTES != 0
            or len(data) < 3*FRAME_BYTES or len(data) > MAX_PROXY_FRAMES*FRAME_BYTES):
        raise ValueError("V129_PRE_FREEZE_PROXY_FRAMES_INSUFFICIENT_OR_INVALID")
    count = len(data)//FRAME_BYTES
    positions = (0, (count-1)//2, count-1)
    pictures = [Image.frombytes("RGB", (WIDTH, HEIGHT),
                                data[k*FRAME_BYTES:(k+1)*FRAME_BYTES]) for k in positions]
    if len({hashlib.sha256(im.tobytes()).digest() for im in pictures}) < 2:
        raise ValueError("V129_PRE_FREEZE_PROXY_STATIC_OR_TOO_SPARSE")
    return pictures, count, hashlib.sha256(data).hexdigest()


def run(film_path, balanced_path, motion_path, scout_path, frames_path, report_path,
        sheet_path, *, decoder=decode_proxy):
    """Validate all five source windows and film hash BEFORE any FFmpeg work."""
    balanced = json.loads(Path(balanced_path).read_text(encoding="utf-8"))
    motion = json.loads(Path(motion_path).read_text(encoding="utf-8"))
    scout = json.loads(Path(scout_path).read_text(encoding="utf-8"))
    rows = verified_source_rows(balanced, motion, scout, frames_path)
    if len(rows) != 5:
        raise ValueError("V129_NEED_FIVE_SOURCE_LOCKED_WINDOWS")
    source_sha = rows[0]["source_film_sha256"]
    if (any(row["source_film_sha256"] != source_sha for row in rows)
            or sha256_file(film_path) != source_sha):
        raise ValueError("V129_ORIGINAL_FILM_SHA_MISMATCH")
    selected = {x["filename"]: x for x in balanced["five_review_candidates"]}
    windows = []
    for row in rows:
        entry = selected[row["filename"]]
        window = entry["pre_freeze_window_pts"]
        start, freeze, clock = window["start_pts"], window["freeze_pts"], window["time_base"]
        valid, reason = check_source_window(start, freeze, clock)
        if (not valid or freeze != entry["source_pts"]
                or clock != entry["source_time_base"]):
            raise ValueError("V129_SOURCE_PTS_WINDOW_MISMATCH_" + reason)
        windows.append((row, start, freeze, clock))
    # Only after all metadata and original film bytes pass do we invoke FFmpeg.
    pictures, metadata = [], []
    for row, start, freeze, clock in windows:
        previews, count, proxy_sha = decoder(film_path, start, freeze, clock)
        if len(previews) != 3 or any(im.size != (WIDTH, HEIGHT) for im in previews):
            raise ValueError("V129_INVALID_PREVIEW_TRIPTYCH")
        pictures.append(previews)
        metadata.append({"source_frame":row["filename"],
                         "freeze_source_pts_time_s":row["source_pts_time_s"],
                         "pre_freeze_start_pts":start,"freeze_pts":freeze,
                         "source_time_base":clock,"proxy_decoded_frame_count":count,
                         "proxy_rgb_sha256":proxy_sha})
    sheet = Image.new("RGB", (WIDTH*3, 172*5), (17, 17, 17))
    pen = ImageDraw.Draw(sheet)
    for i, (row, preview) in enumerate(zip(rows, pictures)):
        y = i*172
        pen.text((5, y+5),
                 f"{row['filename']} | original freeze {row['source_pts_time_s']:.2f}s | 4fps diagnostic, NOT exact PTS",
                 fill=(245,245,245))
        for j, image in enumerate(preview):
            sheet.paste(image, (j*WIDTH,y+27))
    report = {"version":"V129_REAL_PREFREEZE_MOTION_STRIPS_UNAPPROVED",
              "status":"V129_FIVE_SOURCE_LOCKED_MOTION_STRIPS_REVIEW_ONLY",
              "original_film_sha256":source_sha,
              "five_prefreeze_proxy_strips":metadata,
              "proxy_sampling_is_not_exact_freeze_pts":True,
              "five_genuine_camera_shots_verified":False,
              "historical_year_verified":False,
              "italian_rights_verified":False,
              "human_artistic_approved":False,
              "four_i2i_approved":False,"vidu_clip_approved":False,
              "paid_api_calls":0,"video_finished":False,"published":False,
              "note":"Three frames per window are approximate FFmpeg diagnostic proxies; compare real shots manually. No film or moving excerpt distributed."}
    report_file, sheet_file = Path(report_path), Path(sheet_path)
    report_file.parent.mkdir(parents=True,exist_ok=True)
    sheet_file.parent.mkdir(parents=True,exist_ok=True)
    sheet.save(sheet_file,format="JPEG",quality=88)
    report_file.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("film","balanced","motion","scout","frames","out","sheet"):
        p.add_argument("--"+name,required=True)
    args=p.parse_args()
    output,sheet=Path(args.out),Path(args.sheet)
    # A previous output cannot be mistaken for this run's successful review.
    if sheet.exists():
        sheet.unlink()
    try:
        result=run(args.film,args.balanced,args.motion,args.scout,args.frames,
                   output,sheet)
    except (OSError,ValueError,KeyError,TypeError,IndexError,subprocess.SubprocessError) as exc:
        if sheet.exists():
            sheet.unlink()
        result={"version":"V129_REAL_PREFREEZE_MOTION_STRIPS_UNAPPROVED",
                "status":"V129_SOURCE_MOTION_STRIPS_BLOCKED","reason":str(exc)[:220],
                "five_prefreeze_proxy_strips":[],"five_genuine_camera_shots_verified":False,
                "italian_rights_verified":False,"human_artistic_approved":False,
                "paid_api_calls":0,"video_finished":False,"published":False}
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("V129_PREFREEZE_MOTION",result["status"])


if __name__=="__main__":
    main()
