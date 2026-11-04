#!/usr/bin/env python3
"""V291: inspect the exact last 1.5s of each 4.8s source shot (the intended B/W edit).

Long V243 archival roughcuts can contain historical intertitles outside the
1.5s motion window that a V98-style 4+1 episode would actually display.
This creates a REAL edited source-only video and checks all decoded frames.
No I2I/Vidu calls, rights clearance or artistic approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageOps, ImageStat
from storia_rivive_v210_shot_aware_selection import likely_intertitle

FPS = 24
SHOT_FRAMES = 115
MOTION_FRAMES = 36
SHOT_COUNT = 5


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _run(*args: str, timeout: int = 90) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True, check=True, timeout=timeout)


def _frame_count(path: Path) -> int:
    data = json.loads(_run("ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
                           "-show_entries", "stream=width,height,r_frame_rate,nb_read_frames",
                           "-of", "json", str(path), timeout=30).stdout)
    streams = data.get("streams", [])
    if len(streams) != 1 or streams[0].get("width") != 720 or streams[0].get("height") != 1280 \
            or streams[0].get("r_frame_rate") != "24/1":
        raise ValueError("INVALID_DECODED_SOURCE_GEOMETRY_OR_FPS")
    return int(streams[0].get("nb_read_frames") or 0)


def check(video: Path, manifest: Path, output: Path, edited_video: Path) -> dict:
    if video.is_symlink() or not video.is_file() or manifest.is_symlink() or not manifest.is_file():
        raise ValueError("SOURCE_ROUGHCUT_OR_MANIFEST_MISSING")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    shots = data.get("shots")
    if data.get("version") != "V243_ARCHIVAL_FREEZE_ENDPOINT_REVIEW" or not isinstance(shots, list) \
            or len(shots) != SHOT_COUNT or any(not isinstance(x, dict) or not x.get("sha256") for x in shots):
        raise ValueError("INVALID_SOURCE_REVIEW_MANIFEST")
    if _frame_count(video) != SHOT_COUNT * SHOT_FRAMES:
        raise ValueError("SOURCE_REVIEW_FRAMECOUNT_MISMATCH")
    source_sha = _sha(video)
    windows = [(i * SHOT_FRAMES + SHOT_FRAMES - MOTION_FRAMES,
                (i + 1) * SHOT_FRAMES - 1) for i in range(SHOT_COUNT)]
    expression = "+".join(f"between(n\\,{lo}\\,{hi})" for lo, hi in windows)
    edited_video.parent.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="storia-v291-") as tmp:
        folder = Path(tmp)
        candidate = folder / "all_180_source_motion_frames.mp4"
        _run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(video),
             "-vf", f"select={expression},setpts=N/(24*TB)", "-an", "-frames:v", "180",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p",
             str(candidate), timeout=120)
        if _frame_count(candidate) != SHOT_COUNT * MOTION_FRAMES:
            raise ValueError("SHORT_EDIT_VIDEO_FRAMECOUNT_MISMATCH")
        _run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(candidate),
             "-vsync", "0", str(folder / "frame_%03d.png"), timeout=120)
        images = sorted(folder.glob("frame_*.png"))
        if len(images) != SHOT_COUNT * MOTION_FRAMES:
            raise ValueError("SHORT_EDIT_DECODE_INCOMPLETE")
        trim_frames = []
        per_shot = []
        for i, (start, end) in enumerate(windows):
            flagged = []
            for j, path in enumerate(images[i * MOTION_FRAMES: (i + 1) * MOTION_FRAMES]):
                with Image.open(path) as im:
                    if im.format != "PNG" or im.size != (720, 1280):
                        raise ValueError("SHORT_EDIT_DECODE_INVALID_FRAME")
                if likely_intertitle(path):
                    flagged.append(j)
            # Trim at most six early frames (0.25s), preserving >=1.25s
            # of genuine motion. A title at the middle/end rejects the scene.
            trim = flagged[-1] + 1 if flagged else 0
            trim = trim if trim <= 6 and all(x < trim for x in flagged) else MOTION_FRAMES
            trim_frames.append(trim)
            per_shot.append({"shot": i + 1, "source_frame": shots[i].get("source_frame"),
                             "source_frame_sha256": shots[i]["sha256"],
                             "original_decoded_frame_range": [start + trim, end],
                             "motion_seconds": round((MOTION_FRAMES-trim) / FPS, 3),
                             "inspected_candidate_frames": MOTION_FRAMES,
                             "excluded_early_intertitle_frames": flagged,
                             "trimmed_leading_frames": trim})
        chosen_ranges = [(i * MOTION_FRAMES + trim, (i + 1) * MOTION_FRAMES - 1)
                         for i, trim in enumerate(trim_frames) if trim < MOTION_FRAMES]
        if len(chosen_ranges) == SHOT_COUNT:
            expr = "+".join(f"between(n\\,{lo}\\,{hi})" for lo, hi in chosen_ranges)
            _run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(candidate),
                 "-vf", f"select={expr},setpts=N/(24*TB)", "-r", "24", "-fps_mode", "cfr", "-an",
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p",
                 str(edited_video), timeout=120)
            expected = sum(MOTION_FRAMES - trim for trim in trim_frames)
            if _frame_count(edited_video) != expected:
                raise ValueError("SHORT_EDIT_TRIMMED_VIDEO_FRAMECOUNT_MISMATCH")
            frames = folder / "validated"
            frames.mkdir()
            _run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(edited_video),
                 "-vsync", "0", str(frames / "frame_%03d.png"), timeout=120)
            validated = sorted(frames.glob("frame_*.png"))
            if len(validated) != expected:
                raise ValueError("TRIMMED_SOURCE_FRAME_DECODE_FAILED")
            offset = 0
            for i, entry in enumerate(per_shot):
                length = MOTION_FRAMES - trim_frames[i]
                chosen = validated[offset:offset + length]
                offset += length
                flags = [j for j, path in enumerate(chosen) if likely_intertitle(path)]
                with Image.open(chosen[0]) as im:
                    first = ImageOps.grayscale(im).resize((160, 90))
                with Image.open(chosen[-1]) as im:
                    last = ImageOps.grayscale(im).resize((160, 90))
                movement = round(ImageStat.Stat(ImageChops.difference(first, last)).mean[0], 3)
                entry.update({"decoded_final_frames_inspected": length,
                              "remaining_title_frames": flags,
                              "first_last_motion_luma_mae": movement,
                              "motion_candidate": movement >= 0.5 and not flags})
        else:
            for entry in per_shot:
                entry.update({"decoded_final_frames_inspected": 0, "remaining_title_frames": [],
                              "first_last_motion_luma_mae": 0, "motion_candidate": False})
    passed = len(chosen_ranges) == SHOT_COUNT and all(x["motion_candidate"] for x in per_shot)
    report = {"version": "V291_REAL_LAST_MOTION_EDIT_WINDOW_PREFLIGHT",
              "status": "FIVE_REAL_1P5S_EDIT_WINDOWS_PASS_NOT_ARTISTIC_APPROVAL" if passed
                        else "REJECT_SHORT_EDIT_WINDOW_ARTISTIC_REVIEW_REQUIRED",
              "source_roughcut_sha256": source_sha,
              "edited_motion_preview_sha256": _sha(edited_video) if edited_video.is_file() else None,
              "edited_motion_preview": edited_video.name,
              "frames_total_decoded": 180,
              "frames_in_final_short_preview": sum(MOTION_FRAMES - t for t in trim_frames if t < MOTION_FRAMES),
              "source_shot_frame_count": SHOT_FRAMES, "frames_per_short_shot": MOTION_FRAMES,
              "shots": per_shot, "must_use_these_exact_short_windows_in_final_render": True,
              "i2i_photos_generated": False, "vidu_clip_generated": False,
              "italian_rights_verified": False, "artistic_approved": False,
              "finished_mp4": False, "finished_zip": False, "publish_permitted": False,
              "new_final_videos_delivered": 0}
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(report["status"], "motion_mae", [x["first_last_motion_luma_mae"] for x in per_shot],
          "trimmed_early_frames", [x["trimmed_leading_frames"] for x in per_shot])
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("video", "manifest", "out", "preview"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    check(args.video, args.manifest, args.out, args.preview)
