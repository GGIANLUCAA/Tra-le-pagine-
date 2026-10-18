#!/usr/bin/env python3
"""Opt-in cinematic frei0r plugin filters for Tra le Pagine.

Project: https://github.com/dyne/frei0r (free software).
Eight underlying frei0r plugins were tested on the Ubuntu GitHub Actions
runner in https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/39168733579

All plugin names come from this fixed allowlist, never from user-supplied
shell commands. A softened blend preserves important facial detail.
No paid API calls, GPU, or hidden downloads.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

# preset -> (installed frei0r filter, fraction of treatment over original)
PRESETS = {
    "soft_bloom": ("softglow", 0.24),
    "golden_glow": ("glow", 0.19),
    "edge_luminosity": ("edgeglow", 0.15),
    "ink_graphic": ("cartoon", 0.31),
    "cinema_vignette": ("vignette", 0.28),
    "poster_art": ("posterize", 0.29),
    "halftone_pages": ("colorhalftone", 0.19),
    "vintage_grain": ("rgbnoise", 0.09),
}
# Effects are STATIC grades; emotional timing is handled by scene cues.
# All presets preserve the original picture through alpha-like blending.


def apply_postfx(source: Path, dest: Path, preset: str, frame_count: int, fps: int) -> Path:
    if preset not in PRESETS:
        raise ValueError(f"Unknown frei0r preset: {preset!r}")
    if frame_count < 1 or fps < 1:
        raise ValueError("Invalid frame count or rate")
    plugin, fraction = PRESETS[preset]
    source = Path(source)
    dest = Path(dest)
    if not source.is_file():
        raise FileNotFoundError(source)
    fraction = f"{fraction:.3f}"
    graph = (
        "[0:v]split=2[original][tofx];"
        f"[tofx]format=rgba,frei0r=filter_name={plugin},format=yuv420p[treated];"
        "[original]format=yuv420p[base];"
        f"[base][treated]blend=all_mode=normal:all_opacity={fraction},format=yuv420p[video]"
    )
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
        "-filter_complex", graph, "-map", "[video]",
        "-frames:v", str(int(frame_count)), "-an", "-r", str(int(fps)),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-pix_fmt", "yuv420p", str(dest)
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(
            f"Frei0r preset '{preset}' failed; check apt install frei0r-plugins "
            "and ffmpeg --enable-frei0r. " + completed.stderr[-1200:]
        )
    if not dest.is_file() or dest.stat().st_size < 1000:
        raise RuntimeError(f"Frei0r preset '{preset}' produced no valid video")
    return dest
