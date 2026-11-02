#!/usr/bin/env python3
"""V122: experimental single-photo room plane reprojection. NOT a museum master.

Usage:
 python src/artvision_bocklin_v122_photo_room_3d_proxy.py \
  --photo GAL02_PHOTOGRAPH.jpg --museum-video 02_Critico_Museum_V106_CANDIDATO.mp4 \
  --output BOECKLIN_PHOTO_ROOM_3D_PROXY_V122_8S_REVIEW.mp4

Photo: Daniel Naber, Museum Barberini, CC BY 4.0 (NOT Alte Nationalgalerie).
Frame source: modern Sailko photograph CC BY 3.0 in genuine V106 MP4.
Dimensions and camera intrinsics are approximate; NOT metrologically validated.
No API, TTS, AI, credits, new artwork, or social publishing.
"""
import argparse
import hashlib
import json
import math
import os
import subprocess

import cv2
import numpy as np

PHOTO_SHA = "ea95335ef66afa225351e1dd423c49d5e84aeb15574e97b965fa25c1d5b91db2"
VIDEO_SHA = "c1c54dba4f0198df3a8f82e11513378bccf2831647dca01741163250c857a263"
WIDTH, HEIGHT, FPS, FRAMES = 720, 1280, 20, 160
F0, C0X, C0Y = 2533.3333, 1824.0, 1241.3333
ROOM_X, ROOM_Z, ROOM_H = 4.05, 13.5, 3.5
PAINT_X, PAINT_Y, PAINT_W, PAINT_H, PAINT_Z = -2.05, 1.85, 1.70, 0.98, 13.465


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def prepare(photo, video):
    if sha256(photo) != PHOTO_SHA:
        raise ValueError("Wrong photographic source SHA; do not substitute an unknown gallery.")
    if sha256(video) != VIDEO_SHA:
        raise ValueError("Wrong V106 MP4 SHA; protect the source and its frame.")
    source = cv2.imread(photo)
    if source is None or source.shape[:2] != (2736, 3648):
        raise ValueError("Photo dimensions mismatch")
    cap = cv2.VideoCapture(video)
    ok, frame = cap.read()
    cap.release()
    if not ok or frame.shape[:2] != (1280, 720):
        raise ValueError("Cannot decode original museum frame")
    framed_painting = frame[445:834, 30:690].copy()
    return source, framed_painting


def make_frame(s, source, framed_painting, rays):
    d0x, d0y, d0z = rays
    approach = (1 - math.cos(2 * math.pi * s)) / 2
    camx = -0.15 - 0.30 * approach
    camy = 1.60
    camz = 1.80 + 4.0 * approach
    yaw = math.atan2(PAINT_X - camx, PAINT_Z - camz)
    co, si = math.cos(yaw), math.sin(yaw)
    dx = co * d0x + si * d0z
    dy = d0y
    dz = -si * d0x + co * d0z
    near = np.full((HEIGHT, WIDTH), np.inf, np.float32)
    xx = np.zeros_like(near)
    yy = np.zeros_like(near)
    zz = np.zeros_like(near)

    for plane in ("back", "right", "left", "floor", "ceiling"):
        if plane == "back":
            t = (ROOM_Z - camz) / np.where(np.abs(dz) > 1e-6, dz, 1e-6)
        elif plane == "right":
            t = (ROOM_X - camx) / np.where(np.abs(dx) > 1e-6, dx, 1e-6)
        elif plane == "left":
            t = (-ROOM_X - camx) / np.where(np.abs(dx) > 1e-6, dx, 1e-6)
        elif plane == "floor":
            t = (0 - camy) / np.where(np.abs(dy) > 1e-6, dy, 1e-6)
        else:
            t = (ROOM_H - camy) / np.where(np.abs(dy) > 1e-6, dy, 1e-6)
        x = camx + t * dx
        y = camy + t * dy
        z = camz + t * dz
        valid = (
            (t > 0) & (t < near)
            & (x >= -ROOM_X - 0.0001) & (x <= ROOM_X + 0.0001)
            & (y >= -0.0001) & (y <= ROOM_H + 0.0001)
            & (z >= -0.0001) & (z <= ROOM_Z + 0.0001)
        )
        near = np.where(valid, t, near)
        xx = np.where(valid, x, xx)
        yy = np.where(valid, y, yy)
        zz = np.where(valid, z, zz)

    zsafe = np.maximum(zz, 0.0001)
    mx = (C0X + F0 * xx / zsafe).astype(np.float32)
    my = (C0Y - F0 * (yy - 1.6) / zsafe).astype(np.float32)
    background = cv2.remap(
        source, mx, my, cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT, borderValue=(40, 39, 36)
    )

    t = (PAINT_Z - camz) / np.where(np.abs(dz) > 1e-6, dz, 1e-6)
    px = camx + t * dx
    py = camy + t * dy
    inside = (
        (np.abs(px - PAINT_X) <= PAINT_W / 2)
        & (np.abs(py - PAINT_Y) <= PAINT_H / 2)
        & (t > 0) & (t < near + 0.2)
    )
    wall_t = (ROOM_Z - camz) / np.where(np.abs(dz) > 1e-6, dz, 1e-6)
    bx = camx + wall_t * dx
    by = camy + wall_t * dy
    shadow = (
        (np.abs(bx - PAINT_X) < PAINT_W / 2 + 0.035)
        & (np.abs(by - (PAINT_Y - 0.018)) < PAINT_H / 2 + 0.035)
        & (wall_t > 0) & ~inside
    )
    background[shadow] = (background[shadow] * 0.78).astype(np.uint8)
    tx = ((px - (PAINT_X - PAINT_W / 2)) / PAINT_W
          * (framed_painting.shape[1] - 1)).astype(np.float32)
    ty = (((PAINT_Y + PAINT_H / 2) - py) / PAINT_H
          * (framed_painting.shape[0] - 1)).astype(np.float32)
    overlay = cv2.remap(
        framed_painting, tx, ty, cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT
    )
    background[inside] = overlay[inside]
    return background


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--photo", required=True)
    parser.add_argument("--museum-video", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if os.path.exists(args.output):
        parser.error("Output exists: refusing to overwrite")
    source, painting = prepare(args.photo, args.museum_video)
    ys, xs = np.mgrid[0:HEIGHT, 0:WIDTH].astype(np.float32)
    rays = ((xs - WIDTH / 2) / 1450.0, (HEIGHT / 2 - ys) / 1450.0,
            np.ones_like(xs))
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "rawvideo", "-pixel_format", "bgr24",
        "-video_size", f"{WIDTH}x{HEIGHT}", "-framerate", str(FPS),
        "-i", "pipe:0", "-an", "-c:v", "libx264", "-preset", "fast",
        "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        args.output
    ]
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for index in range(FRAMES):
            frame = make_frame(index / (FRAMES - 1), source, painting, rays)
            process.stdin.write(frame.tobytes())
        process.stdin.close()
        error = process.stderr.read()
        process.wait()
        if process.returncode:
            raise RuntimeError(error.decode("utf-8", "replace"))
    except Exception:
        process.kill()
        raise
    print(json.dumps({
        "status": "LOCAL_ONLY_STUDY_NOT_APPROVED",
        "path": args.output, "bytes": os.path.getsize(args.output),
        "sha256": sha256(args.output), "fps": FPS, "frames": FRAMES,
        "duration_seconds": FRAMES / FPS, "audio": False,
        "physical_scale_calibrated": False,
        "actual_Berlin_room": False, "V25_Gold": False
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
