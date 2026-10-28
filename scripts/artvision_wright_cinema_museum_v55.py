#!/usr/bin/env python3
"""Wright Cinema Museum V55: genuine 2019 framed photograph, real 1768 painting, no paid APIs.

Distinct from Wright V52B Cinema Standard. The historical photo is not represented
as the current 2026 location of the painting. Output is review-only, not V25 approved.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
import requests
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
spec = importlib.util.spec_from_file_location("wright_v52b_base", ROOT / "scripts/artvision_wright_air_pump_20261028.py")
wright = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wright)
engine, cinema = wright.engine, wright.cinema
engine.CONFIG = ROOT / "config/artvision_wright_cinema_museum_v55.json"
engine.editorial.CATALOG = ROOT / "config/artvision_wright_cinema_museum_v55_editorial.json"

W, H, FPS = 1080, 1920, 24
CW, CH = 2160, 3840
SLUG = "wright_air_pump_cinema_museum_v55"
OUT = ROOT / "output/artvision-wright-cinema-museum-v55"
PHOTO_PAGE = "https://commons.wikimedia.org/wiki/File:London_National_Gallery_Wright_of_Derby_Experiment_on_a_Bird_in_an_Air_Pump.jpg"
PHOTO_URLS = (
    "https://upload.wikimedia.org/wikipedia/commons/3/3f/London_National_Gallery_Wright_of_Derby_Experiment_on_a_Bird_in_an_Air_Pump.jpg",
    "https://commons.wikimedia.org/wiki/Special:Redirect/file/London_National_Gallery_Wright_of_Derby_Experiment_on_a_Bird_in_an_Air_Pump.jpg",
)
PHOTO = None
PHOTO_BASE = None
original_crop = cinema.crop
original_render_clip = cinema.render_clip


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_photo(path):
    errors = []
    for url in PHOTO_URLS:
        try:
            with requests.get(url, timeout=75, stream=True,
                              headers={"User-Agent": "ArtVisionV55/1.0 (attributed gallery photo research)"}) as response:
                response.raise_for_status()
                if "image/" not in response.headers.get("Content-Type", "").lower():
                    raise ValueError("gallery response is not an image")
                with path.open("wb") as out:
                    for block in response.iter_content(524288):
                        if block:
                            out.write(block)
            if path.stat().st_size < 1500000:
                raise ValueError("gallery photo too small")
            with Image.open(path) as im:
                im.verify()
            with Image.open(path) as im:
                if im.width < 4000 or im.height < 3000:
                    raise ValueError("gallery photo insufficient resolution")
            return url
        except Exception as exc:
            errors.append(type(exc).__name__ + ": " + str(exc)[:200])
            path.unlink(missing_ok=True)
    raise RuntimeError("AUTHENTIC_GALLERY_PHOTO_UNAVAILABLE: " + " | ".join(errors))


def gallery_base():
    global PHOTO_BASE
    if PHOTO_BASE is not None:
        return PHOTO_BASE
    if PHOTO is None:
        raise RuntimeError("Authentic museum photo not loaded")
    # The genuine landscape photograph is kept uncropped across its full width.
    # Neutral matte is outside the photograph, never stretched painting pixels.
    im = PHOTO.copy()
    im.thumbnail((CW - 80, 1920), Image.Resampling.LANCZOS)
    base = Image.new("RGB", (CW, CH), (13, 17, 21))
    x = (CW - im.width) // 2
    y = 860
    base.paste(im, (x, y))
    # Thin restrained photo edge, not a fabricated painting frame.
    d = ImageDraw.Draw(base)
    d.rectangle((x - 3, y - 3, x + im.width + 3, y + im.height + 3),
                outline=(70, 66, 60), width=5)
    PHOTO_BASE = base
    return base


def gallery_frame(zoom):
    src = gallery_base()
    z = max(1.0, min(1.5, float(zoom)))
    ww, hh = CW / z, CH / z
    x0 = max(0, min(CW - ww, CW / 2 - ww / 2))
    y0 = max(0, min(CH - hh, 1660 - hh / 2))
    return src.crop((round(x0), round(y0), round(x0 + ww), round(y0 + hh))).resize(
        (W, H), Image.Resampling.LANCZOS)


def crop(art, shot):
    if str(shot[-1]).startswith("MUSEUM:"):
        return gallery_frame(1.0)
    return original_crop(art, shot)


def full(art):
    return gallery_frame(1.0)


def render_clip(image, scene, index, work):
    if index not in (1, 9):
        return original_render_clip(image, scene, index, work)
    a, b = ((1.0, 1.36) if index == 1 else (1.36, 1.0))
    frame_dir = work / ("museum_frames_%02d" % index)
    frame_dir.mkdir(exist_ok=False)
    count = round(float(scene["duration"]) * FPS)
    for n in range(count):
        t = n / max(1, count - 1)
        smooth = t * t * (3 - 2 * t)
        z = a + (b - a) * smooth
        gallery_frame(z).save(frame_dir / ("f%04d.jpg" % n), quality=91, subsampling=0)
    clip = work / ("clip_%02d.mp4" % index)
    cinema.run("ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
               "-framerate", FPS, "-i", frame_dir / "f%04d.jpg",
               "-r", FPS, "-c:v", "libx264", "-preset", "veryfast", "-crf", 19,
               "-pix_fmt", "yuv420p", clip)
    shutil.rmtree(frame_dir)
    return clip


cinema.crop = crop
cinema.full = full
cinema.render_clip = render_clip
cinema.signature = wright.brand


def main():
    global PHOTO
    from artvision_delivery_v55 import pack, filehash
    folder = OUT / SLUG
    if (folder / "VIDEO_MASTER.mp4").exists():
        raise RuntimeError("Wright Cinema Museum already exists: no overwrite or duplicate")
    folder.mkdir(parents=True, exist_ok=True)
    photo_file = folder / "ORIGINAL_REAL_GALLERY_PHOTO_AD_MESKENS_CC_BY_SA_4.jpg"
    used_url = fetch_photo(photo_file)
    # V55 visual-source incident: the Ad Meskens 2019 file is a tight painting DETAIL,
    # not a photographed gilded frame. Block its known SHA before any rendering.
    if sha(photo_file) == "b82ea9c5ca81ab220a4d34f908293e920293b15a2b7eaa0215ac14a92c0dd523":
        raise RuntimeError("V55_SOURCE_FRAME_NOT_VISIBLE: this 2019 photo is only a cropped lecturer/bird detail; cannot be a Cinema Museum entry/exit. Acquire and inspect a real full-frame photo first.")
    with Image.open(photo_file) as im:
        PHOTO = im.convert("RGB").copy()
    engine.render_one("air_pump", OUT)
    film, cover = folder / "VIDEO_MASTER.mp4", folder / "COPERTINA.jpg"
    first = folder / "QA_FIRST_FRAME_V55.jpg"
    subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(film), "-frames:v", "1", str(first)], check=True)
    with Image.open(cover) as a, Image.open(first) as b:
        if a.size != b.size or a.size != (W, H):
            raise RuntimeError("V55 cover and first-frame sizes differ")
        aa = np.asarray(a.convert("RGB"), dtype=np.int16)
        bb = np.asarray(b.convert("RGB"), dtype=np.int16)
        mad = float(np.abs(aa[1340:1590] - bb[1340:1590]).mean())
        if mad >= 17:
            raise RuntimeError("V55 first-frame branding differs from cover: %.3f" % mad)
        for y0, y1 in ((1355, 1407), (1410, 1475), (1516, 1568)):
            if np.sum(np.all(aa[y0:y1, 150:930] > 210, axis=2)) <= 120:
                raise RuntimeError("Title/artist missing in V55 cover: %d" % y0)
    rights = folder / "SOURCES_AND_RIGHTS.md"
    with rights.open("a", encoding="utf8") as f:
        f.write("\n## Authentic historical museum photograph (separate from painting)\n")
        f.write("Photographer: Ad Meskens. Photo taken 22 September 2019, National Gallery London.\n")
        f.write("Photo page: " + PHOTO_PAGE + "\n")
        f.write("Actual source URL: " + used_url + "\n")
        f.write("CC BY-SA 4.0: https://creativecommons.org/licenses/by-sa/4.0/\n")
        f.write("Credit: © Ad Meskens / Wikimedia Commons; adapted with crop and restrained camera movement.\n")
        f.write("Photo SHA256: " + sha(photo_file) + "\n")
        f.write("Historical photograph, NOT proof of current location. National Gallery lists the painting on loan to Derby Museums until 1 Nov 2026.\n")
        f.write("Canvas: 183 × 244 cm, National Gallery NG725; frame is a genuine 19th-century English gilded frame, actual outer dimensions not documented.\n")
        f.write("The film includes an adaptation of a CC BY-SA 4.0 photograph. Share-alike obligations and territorial rights need human review before release.\n")
        f.write("The painting reproduction is public domain / PD-Art; the actual recording The Descent by Kevin MacLeod is separately CC BY 4.0.\n")
        f.write("No fabricated visitor, no fake museum corridor, no claim of physical metres-per-pixel precision.\n")
    recipe_path = folder / "VIDEO_RECIPE_V13.json"
    recipe = json.loads(recipe_path.read_text(encoding="utf8"))
    recipe.update({
        "variant": "cinema_museum", "renderer": "scripts/artvision_wright_cinema_museum_v55.py",
        "replication_command": "python scripts/artvision_wright_cinema_museum_v55.py",
        "museum_photo": PHOTO_PAGE, "museum_photo_sha256": sha(photo_file),
        "museum_photo_license": "CC BY-SA 4.0, © Ad Meskens",
        "museum_photo_year": 2019, "museum_scene": "real historical photograph, not reconstruction",
        "painting_dimensions_cm": {"height": 183, "width": 244},
        "real_frame": "19th-century English gilded, National Gallery catalogue",
        "frame_outer_dimensions": "unknown",
        "gallery_entry_scene": 1, "gallery_exit_scene": 9,
        "v55_opening_review": "pending actual normal-speed audiovisual watch",
        "artistic_status": "rendered_needs_review", "human_approval": False
    })
    recipe_path.write_text(json.dumps(recipe, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    packdir = OUT / "V55_DELIVERY"
    manifest = pack(film, cover, {k: folder / ("POST_" + k.upper() + ".txt")
                                  for k in ("facebook", "instagram", "tiktok", "youtube")},
                    rights, recipe_path, packdir)
    android = packdir / "ARTVISION_WRIGHT_CINEMA_MUSEUM_V55_SOLO_VIDEO_ANDROID.zip"
    with zipfile.ZipFile(android, "w", allowZip64=True) as z:
        z.write(film, film.name, compress_type=zipfile.ZIP_STORED)
    with zipfile.ZipFile(android) as z:
        if z.testzip() is not None:
            raise RuntimeError("Android ZIP CRC failed")
    originals = OUT / "ARTVISION_WRIGHT_CINEMA_MUSEUM_V55_ORIGINALS.zip"
    with zipfile.ZipFile(originals, "w", allowZip64=True) as z:
        for p in sorted(folder.rglob("*")):
            if p.is_file() and "_working" not in p.parts:
                z.write(p, p.relative_to(folder),
                        compress_type=zipfile.ZIP_STORED if p.suffix.lower() in
                        (".mp4", ".jpg", ".mp3") else zipfile.ZIP_DEFLATED)
        for name in ("scripts/artvision_wright_cinema_museum_v55.py",
                     "config/artvision_wright_cinema_museum_v55.json",
                     "config/artvision_wright_cinema_museum_v55_editorial.json",
                     "docs/productions/2026-10-28-wright-cinema-museum-v55/ARTVISION_4X1_PLAN.json"):
            z.write(ROOT / name, name)
    with zipfile.ZipFile(originals) as z:
        if z.testzip() is not None:
            raise RuntimeError("Original source ZIP CRC failed")
    (OUT / "RELEASE_STATE_V55.json").write_text(json.dumps({
        "state": "rendered_needs_review", "video_sha256": filehash(film),
        "photo_sha256": sha(photo_file), "technical_pack": "passed",
        "human_full_speed_watch": False, "V25_approved": False,
        "photo_rights_human_review": "pending", "archive": "archive_sync_pending",
        "social_published": False, "paid_video_credits": 0,
        "v55_manifest": manifest
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print("WRIGHT_CINEMA_MUSEUM_V55_RENDERED_NEEDS_REVIEW", filehash(film),
          "photo", sha(photo_file), "cover_mad", round(mad, 3), flush=True)


if __name__ == "__main__":
    main()
