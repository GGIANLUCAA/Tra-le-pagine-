#!/usr/bin/env python3
"""Turner Cinema Museum V55: genuine CC BY-SA 4.0 gallery photograph, real painting, review only.

Not a synthetic museum, a different film from Cinema Standard. No paid APIs.
The 2023 photo's authorship metadata is inconsistent: final rights review remains pending.
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
spec = importlib.util.spec_from_file_location(
    "turner_standard_v55_base", ROOT / "scripts/artvision_turner_cinema_standard_v55.py"
)
std = importlib.util.module_from_spec(spec)
spec.loader.exec_module(std)
engine = std.engine
cinema = std.cinema
engine.CONFIG = ROOT / "config/artvision_turner_cinema_museum_v55.json"
engine.editorial.CATALOG = ROOT / "config/artvision_turner_cinema_museum_v55_editorial.json"
W, H, FPS = 1080, 1920, 24
CW, CH = 2160, 3840
SLUG = "turner_fighting_temeraire_cinema_museum_v55"
OUT = ROOT / "output/artvision-turner-cinema-museum-v55"
PHOTO_PAGE = "https://commons.wikimedia.org/wiki/File:JMW_Turner%27s_The_Fighting_Temeraire.jpg"
PHOTO_URLS = (
    "https://upload.wikimedia.org/wikipedia/commons/7/7b/JMW_Turner%27s_The_Fighting_Temeraire.jpg",
    "https://commons.wikimedia.org/wiki/Special:Redirect/file/JMW_Turner%27s_The_Fighting_Temeraire.jpg",
)
PHOTO = None
BASE = None
original_crop = cinema.crop
original_render_clip = cinema.render_clip

def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for data in iter(lambda: stream.read(1048576), b""):
            h.update(data)
    return h.hexdigest()

def download_gallery_photo(path):
    """Fail closed unless the genuine large Commons photograph can be decoded."""
    if path.exists():
        with Image.open(path) as im:
            im.verify()
        return
    problems = []
    for url in PHOTO_URLS:
        try:
            with requests.get(url, timeout=75, stream=True,
                              headers={"User-Agent": "ArtVisionMuseumV55/1.0 (licensed-asset-research)"}) as response:
                response.raise_for_status()
                if "image" not in response.headers.get("Content-Type", "").lower():
                    raise ValueError("not image content")
                with path.open("wb") as dest:
                    for part in response.iter_content(524288):
                        if part:
                            dest.write(part)
            if path.stat().st_size < 1000000:
                raise ValueError("unexpectedly small gallery photograph")
            with Image.open(path) as im:
                im.verify()
            with Image.open(path) as im:
                if im.width < 2000 or im.height < 3000:
                    raise ValueError("gallery photo lacks source resolution")
            return
        except Exception as exc:
            path.unlink(missing_ok=True)
            problems.append(str(exc)[:200])
    raise RuntimeError("AUTHENTIC_GALLERY_PHOTO_UNAVAILABLE: " + " | ".join(problems))

def gallery_base():
    """Real photographed wall and frame, with a dark editorial matte BELOW the photograph.
    Never synthesize architecture, stretch painted edges, or mislabel as a room reconstruction.
    """
    global BASE
    if BASE is not None:
        return BASE
    if PHOTO is None:
        raise RuntimeError("gallery photograph not loaded")
    image = PHOTO.resize((CW, 2880), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (CW, CH), (12, 17, 21))
    canvas.paste(image, (0, -280))
    # A photographic fade into a neutral matte; no pixel-row replication.
    for y in range(2150, 2600):
        blend = (y - 2150) / 450.0
        strip = canvas.crop((0, y, CW, y + 1))
        canvas.paste(Image.blend(strip, Image.new("RGB", (CW, 1), (12, 17, 21)), blend), (0, y))
    BASE = canvas
    return BASE

def gallery_frame(zoom):
    base = gallery_base()
    z = max(1.0, min(2.2, float(zoom)))
    ww, hh = CW / z, CH / z
    # Camera centres on the actual painting, not a fabricated visitor or corridor.
    x0 = max(0, min(CW - ww, 1080 - ww / 2))
    y0 = max(0, min(CH - hh, 1270 - hh / 2))
    return base.crop((round(x0), round(y0), round(x0 + ww), round(y0 + hh))).resize(
        (W, H), Image.Resampling.LANCZOS
    )

def crop(src, shot):
    if str(shot[-1]).startswith("MUSEUM:"):
        return gallery_frame(1.0)
    return original_crop(src, shot)

def full(src):
    return gallery_frame(1.0)

def cover(src, path):
    std.brand(gallery_frame(1.0), 1).save(path, quality=95, subsampling=0)

def render_clip(img, scene, i, work):
    ranges = {0: (1.0, 1.32), 1: (1.32, 2.12), 8: (2.12, 1.32), 9: (1.32, 1.0)}
    if i not in ranges:
        return original_render_clip(img, scene, i, work)
    a, b = ranges[i]
    frame_dir = work / ("real_gallery_frames_%02d" % i)
    frame_dir.mkdir(exist_ok=False)
    frames = round(float(scene["duration"]) * FPS)
    for n in range(frames):
        t = n / max(1, frames - 1)
        smooth = t * t * (3 - 2 * t)
        z = a + (b - a) * smooth
        frame = gallery_frame(z)
        if i == 0:
            sec = n / FPS
            alpha = 1.0 if sec < 3.0 else max(0.0, 1.0 - (sec - 3.0) / .65)
            if alpha:
                frame = std.brand(frame, alpha)
        frame.save(frame_dir / ("f%04d.jpg" % n), quality=92, subsampling=0)
    output = work / ("clip_%02d.mp4" % i)
    cinema.run("ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
               "-framerate", FPS, "-i", frame_dir / "f%04d.jpg",
               "-r", FPS, "-c:v", "libx264", "-preset", "veryfast", "-crf", 19,
               "-pix_fmt", "yuv420p", output)
    shutil.rmtree(frame_dir)
    return output

cinema.crop = crop
cinema.full = full
cinema.make_cover = cover
cinema.render_clip = render_clip
cinema.signature = std.brand

def main():
    global PHOTO
    from artvision_delivery_v55 import pack, filehash
    folder = OUT / SLUG
    if (folder / "VIDEO_MASTER.mp4").exists():
        raise RuntimeError("Turner Cinema Museum already rendered: do not overwrite")
    folder.mkdir(parents=True, exist_ok=True)
    photo_file = folder / "ORIGINAL_REAL_GALLERY_PHOTO_CC_BY_SA_4_0.jpg"
    download_gallery_photo(photo_file)
    with Image.open(photo_file) as im:
        PHOTO = im.convert("RGB").copy()
    # Engine uses its own authentic painting, music, four V28 posts and V25 preflight.
    engine.render_one("temeraire", OUT)
    video = folder / "VIDEO_MASTER.mp4"
    coverfile = folder / "COPERTINA.jpg"
    first = folder / "QA_FIRST_FRAME_V55.jpg"
    subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
                    "-y", "-i", str(video), "-frames:v", "1", str(first)], check=True)
    with Image.open(coverfile) as cover_im, Image.open(first) as first_im:
        if cover_im.size != first_im.size or cover_im.size != (W, H):
            raise RuntimeError("First-frame and cover dimensions differ")
        a = np.asarray(cover_im.convert("RGB"), dtype=np.int16)
        b = np.asarray(first_im.convert("RGB"), dtype=np.int16)
        mad = float(np.abs(a[1340:1590] - b[1340:1590]).mean())
        if mad >= 17:
            raise RuntimeError("V55 branded first-frame/cover mismatch %.3f" % mad)
        for y0, y1 in ((1355, 1407), (1410, 1475), (1516, 1568)):
            if np.sum(np.all(a[y0:y1, 150:930] > 210, axis=2)) <= 120:
                raise RuntimeError("V55 title or artist not visible in cover: %d" % y0)
    rights = folder / "SOURCES_AND_RIGHTS.md"
    with rights.open("a", encoding="utf8") as f:
        f.write("\n## Additional genuine museum photograph\n")
        f.write("Photo of the painting and its real gilded frame, photographed 3 July 2023.\n")
        f.write("Commons source: " + PHOTO_PAGE + "\n")
        f.write("Original file: " + PHOTO_URLS[0] + "\n")
        f.write("Commons license: CC BY-SA 4.0 https://creativecommons.org/licenses/by-sa/4.0/\n")
        f.write("Uploader: Ellie pellegrino. Commons author field confusingly lists the painter;\n")
        f.write("the photographer's legal attribution is NOT independently confirmed. Human review required.\n")
        f.write("Photo SHA256: " + digest(photo_file) + "\n")
        f.write("Adaptation: crop, photographic zoom, dark matte; no invented gallery or new frame.\n")
        f.write("Photo-derived film is offered under CC BY-SA 4.0 subject to human rights review;\n")
        f.write("Kevin MacLeod's original recording remains separately CC BY 4.0.\n")
        f.write("Painting dimensions (not including frame): 90.7 x 121.6 cm, National Gallery NG524.\n")
        f.write("No claim of exact metre-per-pixel measurement from a single museum photograph.\n")
    recipe_path = folder / "VIDEO_RECIPE_V13.json"
    recipe = json.loads(recipe_path.read_text(encoding="utf8"))
    recipe.update({
        "variant": "cinema_museum", "renderer": "scripts/artvision_turner_cinema_museum_v55.py",
        "replication_command": "python scripts/artvision_turner_cinema_museum_v55.py",
        "real_museum_photo": PHOTO_PAGE, "real_museum_photo_sha256": digest(photo_file),
        "photo_license": "CC BY-SA 4.0; photographer attribution pending review",
        "artwork_dimensions_cm": {"height": 90.7, "width": 121.6},
        "actual_frame": "Visible in genuine 2023 National Gallery photograph",
        "gallery_scene": "real photograph, no synthesized architecture",
        "entry_exit": "same photo; 0-7 sec physical frame then painting, final return",
        "camera_zoom_ranges": {"0": [1.0, 1.32], "1": [1.32, 2.12],
                               "8": [2.12, 1.32], "9": [1.32, 1.0]},
        "opening_review": "pending actual full-speed video and audio watch",
        "artistic_status": "rendered_needs_review", "human_approval": False
    })
    recipe_path.write_text(json.dumps(recipe, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    packdir = OUT / "V55_DELIVERY"
    manifest = pack(video, coverfile,
                    {k: folder / ("POST_" + k.upper() + ".txt")
                     for k in ("facebook", "instagram", "tiktok", "youtube")},
                    rights, recipe_path, packdir)
    android = packdir / "ARTVISION_TURNER_CINEMA_MUSEUM_V55_SOLO_VIDEO_ANDROID.zip"
    with zipfile.ZipFile(android, "w", allowZip64=True) as z:
        z.write(video, video.name, compress_type=zipfile.ZIP_STORED)
    with zipfile.ZipFile(android) as z:
        assert z.testzip() is None and z.getinfo(video.name).file_size == video.stat().st_size
    # Source-inclusive dossier; not the website's dynamically generated ZIP.
    original_zip = OUT / "ARTVISION_TURNER_CINEMA_MUSEUM_V55_ORIGINALS.zip"
    with zipfile.ZipFile(original_zip, "w", allowZip64=True) as z:
        for p in folder.rglob("*"):
            if p.is_file() and "_working" not in p.parts:
                z.write(p, p.relative_to(folder),
                        compress_type=zipfile.ZIP_STORED if p.suffix.lower() in
                        (".mp4", ".jpg", ".mp3") else zipfile.ZIP_DEFLATED)
        for name in ("scripts/artvision_turner_cinema_museum_v55.py",
                     "config/artvision_turner_cinema_museum_v55.json",
                     "config/artvision_turner_cinema_museum_v55_editorial.json"):
            z.write(ROOT / name, name)
    with zipfile.ZipFile(original_zip) as z:
        assert z.testzip() is None
    release = {
        "state": "rendered_needs_review", "video_sha256": filehash(video),
        "photo_sha256": digest(photo_file), "technical_pack": "passed",
        "human_full_speed_watch": False, "V25_approved": False,
        "photo_rights_human_review": "pending", "archive": "archive_sync_pending",
        "social_published": False, "paid_video_credits": 0,
        "v55_manifest": manifest
    }
    (OUT / "RELEASE_STATE_V55.json").write_text(
        json.dumps(release, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print("TURNER_CINEMA_MUSEUM_V55_RENDERED_NEEDS_REVIEW", filehash(video),
          "photo", digest(photo_file), "cover_mad", round(mad, 3), flush=True)

if __name__ == "__main__":
    main()
