#!/usr/bin/env python3
"""V39 experimental cinematic inserts, 5–10 seconds. CPU/FFmpeg; no APIs.

No AI motion synthesis. Layered depth requires a clean plate and an aligned
transparent foreground from the SAME narrative illustration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path

import cv2
import numpy as np

EFFECTS = ("slow_push", "focus_reveal", "light_travel", "depth_layers")
FORMATS = ("libri", "artvision_cinema", "artvision_critico", "controluce")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_image(path: Path, alpha: bool = False) -> np.ndarray:
    if not path.is_file():
        raise ValueError(f"Immagine non trovata: {path}")
    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"Impossibile leggere: {path}")
    if alpha:
        if img.ndim != 3 or img.shape[2] != 4 or not np.any(img[:, :, 3] < 255):
            raise ValueError("Primo piano richiesto: PNG RGBA realmente trasparente")
    elif img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    elif img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    if img.dtype != np.uint8:
        raise ValueError("Usare immagini 8-bit RGB/RGBA")
    return img


def ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def cover(img: np.ndarray, width: int, height: int, scale: float = 1.18) -> np.ndarray:
    """Crop with overscan so small camera moves never reveal black borders."""
    h, w = img.shape[:2]
    if min(w, h) < 1:
        raise ValueError("Immagine vuota")
    tw, th = math.ceil(width * scale), math.ceil(height * scale)
    factor = max(tw / w, th / h)
    scaled = cv2.resize(img, (math.ceil(w * factor), math.ceil(h * factor)),
                        interpolation=cv2.INTER_CUBIC if factor > 1 else cv2.INTER_AREA)
    sh, sw = scaled.shape[:2]
    left, top = (sw - tw) // 2, (sh - th) // 2
    return scaled[top:top + th, left:left + tw].copy()


def camera_crop(img: np.ndarray, width: int, height: int, p: float,
                travel: float = 0.05, offset: float = 0.0) -> np.ndarray:
    h, w = img.shape[:2]
    amount = ease(p)
    dx = int(round((w - width) * (0.5 + (amount - 0.5) * travel * 4 + offset)))
    dy = int(round((h - height) * (0.5 - (amount - 0.5) * travel * 1.6)))
    dx = min(max(dx, 0), w - width)
    dy = min(max(dy, 0), h - height)
    return img[dy:dy + height, dx:dx + width]


def make_frame(base: np.ndarray, width: int, height: int, p: float,
               effect: str, fg: np.ndarray | None = None) -> np.ndarray:
    if effect == "depth_layers":
        bg = camera_crop(base, width, height, p, 0.10, -0.02)
        subject = camera_crop(fg, width, height, p, -0.12, 0.02)
        a = subject[:, :, 3:4].astype(np.float32) / 255.0
        frame = np.clip(bg.astype(np.float32) * (1.0 - a) +
                        subject[:, :, :3].astype(np.float32) * a, 0, 255).astype(np.uint8)
    else:
        frame = camera_crop(base, width, height, p,
                            0.025 if effect == "slow_push" else 0.06)
    if effect == "focus_reveal":
        amount = 1.0 - ease(min(1.0, p / 0.26))
        if amount > 0.001:
            blur = cv2.GaussianBlur(frame, (0, 0), sigmaX=5.0 * amount + 0.5)
            frame = cv2.addWeighted(frame, 1 - amount, blur, amount, 0)
    elif effect == "light_travel":
        yy, xx = np.ogrid[:height, :width]
        cx, cy = width * (0.18 + 0.64 * ease(p)), height * 0.42
        field = np.exp(-((xx - cx) / (width * 0.38)) ** 2 -
                       ((yy - cy) / (height * 0.52)) ** 2).astype(np.float32)
        frame = np.clip(frame.astype(np.float32) *
                        (1.0 + 0.11 * field[:, :, None]), 0, 255).astype(np.uint8)
    return frame


def inspect(path: Path, width: int, height: int, seconds: int) -> dict:
    check = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                            "format=duration:stream=codec_name,width,height",
                            "-of", "json", str(path)],
                           check=True, capture_output=True, text=True)
    obj = json.loads(check.stdout)
    video = next((s for s in obj.get("streams", []) if s.get("width")), None)
    duration = float(obj.get("format", {}).get("duration", 0))
    if not video or video.get("codec_name") != "h264" or (video["width"], video["height"]) != (width, height):
        raise RuntimeError("MP4 non supera controllo codec/risoluzione")
    if abs(duration - seconds) > 0.15:
        raise RuntimeError(f"Durata errata: {duration}")
    return {"codec": "h264", "width": width, "height": height, "duration_seconds": duration}


def render(image: Path, output: Path, effect: str, kind: str,
           seconds: int, width: int, height: int, fps: int,
           foreground_file: Path | None = None) -> dict:
    if effect not in EFFECTS or kind not in FORMATS:
        raise ValueError("Formato o effetto sconosciuto")
    if seconds not in range(5, 11):
        raise ValueError("Durata consentita: 5–10 secondi")
    if min(width, height) < 144 or max(width, height) > 1920 or width % 2 or height % 2:
        raise ValueError("Dimensioni pari, da 144 a 1920")
    if fps not in (12, 24, 25, 30):
        raise ValueError("FPS consentiti: 12, 24, 25, 30")
    if effect == "depth_layers" and kind != "libri":
        raise ValueError("Profondita a livelli solo per libri (arte/cronaca non ricostruite)")
    if effect == "depth_layers" and foreground_file is None:
        raise ValueError("depth_layers richiede --foreground")
    if effect != "depth_layers" and foreground_file is not None:
        raise ValueError("--foreground solo per depth_layers")
    if kind.startswith("artvision") and effect not in ("slow_push", "focus_reveal"):
        raise ValueError("ArtVision: solo movimenti neutrali")
    if output.exists() or output.with_suffix(".json").exists():
        raise ValueError("Output gia presente: non sovrascrivere")
    raw = read_image(image)
    foreground = read_image(foreground_file, alpha=True) if foreground_file else None
    if foreground is not None and foreground.shape[:2] != raw.shape[:2]:
        raise ValueError("Background e foreground devono avere dimensioni originali uguali")
    base = cover(raw, width, height)
    fg = cover(foreground, width, height) if foreground is not None else None
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo",
           "-pix_fmt", "bgr24", "-s", f"{width}x{height}", "-r", str(fps),
           "-i", "pipe:0", "-an", "-c:v", "libx264", "-preset", "veryfast",
           "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output)]
    frames = seconds * fps
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for i in range(frames):
            frame = make_frame(base, width, height, i / max(1, frames - 1), effect, fg)
            proc.stdin.write(frame.tobytes())
        proc.stdin.close()
        stderr = proc.stderr.read().decode("utf-8", "replace")
        if proc.wait():
            raise RuntimeError("FFmpeg: " + stderr[-1500:])
        technical = inspect(output, width, height, seconds)
        result = {
            "schema": "microcinema-v39-trial",
            "status": "rendered_needs_review",
            "effect": effect, "format": kind, "source": str(image),
            "source_sha256": sha256(image),
            "foreground": str(foreground_file) if foreground_file else None,
            "foreground_sha256": sha256(foreground_file) if foreground_file else None,
            "fps": fps, "technical": technical,
            "notes": "No API/GPU/AI video. Richiede controllo umano, fonti/diritti, sincronizzazione e revisione estetica."
        }
        output.with_suffix(".json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return result
    except Exception:
        if proc.poll() is None:
            proc.kill()
            proc.wait()
        if output.exists():
            output.unlink()
        raise
    finally:
        if proc.stderr:
            proc.stderr.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--image", required=True, type=Path)
    ap.add_argument("--foreground", type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--effect", choices=EFFECTS, default="slow_push")
    ap.add_argument("--format", dest="kind", choices=FORMATS, default="libri")
    ap.add_argument("--seconds", type=int, default=7)
    ap.add_argument("--width", type=int, default=720)
    ap.add_argument("--height", type=int, default=1280)
    ap.add_argument("--fps", type=int, default=24)
    args = ap.parse_args()
    print(json.dumps(render(args.image, args.out, args.effect, args.kind, args.seconds,
                            args.width, args.height, args.fps, args.foreground),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
