"""Opt-in V39 microclip integration for the established book narrator V4.

No TTS/API calls. The clip replaces the first seconds of an existing visual
cue, keeps all voice/scene boundaries, and freezes its end frame if needed.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from microcinema_v39 import EFFECTS, render


def config_for_cue(config_path, cue: int):
    if not config_path or not Path(config_path).is_file():
        return None
    obj = json.loads(Path(config_path).read_text(encoding="utf-8"))
    scene = next((s for s in obj.get("scenes", []) if s.get("cue") == cue), None)
    if not scene or "microcinema" not in scene:
        return None
    cfg = scene["microcinema"]
    if not isinstance(cfg, dict) or set(cfg) - {"effect", "seconds", "reason"}:
        raise ValueError(f"MicroCinema scene {cue}: unknown fields")
    if cfg.get("effect") not in EFFECTS or cfg.get("effect") == "depth_layers":
        raise ValueError("MicroCinema automatico: depth_layers richiede due asset con validazione separata")
    if type(cfg.get("seconds")) is not int or cfg["seconds"] not in range(5, 11):
        raise ValueError("MicroCinema: secondi interi da 5 a 10")
    if len(str(cfg.get("reason", "")).strip()) < 15:
        raise ValueError("MicroCinema: serve una motivazione narrativa specifica")
    if scene.get("effect") in {"sketch_paint", "brush_reveal"} or scene.get("postfx") not in (None, "off"):
        raise ValueError("MicroCinema non puo essere sovrapposto a reveal forti o postfx frei0r")
    return cfg


def make_insert(picture, cue: int, count: int, fps: int, width: int, height: int,
                temp: Path, config_path):
    cfg = config_for_cue(config_path, cue)
    if cfg is None:
        return None
    if count < cfg["seconds"] * fps:
        raise ValueError(
            f"Scena {cue}: voce {count/fps:.2f}s, insufficiente per microclip {cfg['seconds']}s"
        )
    temp = Path(temp)
    clip = temp / f"microcinema_{cue:02d}_source.mp4"
    report = render(Path(picture), clip, cfg["effect"], "libri", cfg["seconds"],
                    width, height, fps)
    if count == cfg["seconds"] * fps:
        out = clip
    else:
        out = temp / f"microcinema_{cue:02d}_frozen_tail.mp4"
        hold = (count - cfg["seconds"] * fps) / fps
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(clip),
            "-vf", f"tpad=stop_mode=clone:stop_duration={hold:.6f}",
            "-frames:v", str(count), "-r", str(fps), "-an",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-pix_fmt", "yuv420p", str(out)
        ], check=True)
    return out, {
        "cue": cue,
        "effect": cfg["effect"],
        "narrative_reason": cfg["reason"],
        "micro_seconds": cfg["seconds"],
        "scene_seconds": round(count / fps, 3),
        "hold_last_frame_seconds": round(max(0, count / fps - cfg["seconds"]), 3),
        "render_status": report["status"],
        "source_sha256": report["source_sha256"],
        "review_required": True,
    }
