#!/usr/bin/env python3
"""ArtVision V31 / 2026-10-25 14:15 — The Sea of Ice, new original museum painting.

An additive wrapper around the previously successful V30 V6-compatible Cinema
renderer. Never alters a historical master. Public-domain original artwork and
CC BY 4.0 sound recording are independently fetched and verified by the engine.
"""
from pathlib import Path
import importlib.util
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "artvision_cinema_duo_v30", ROOT / "scripts/artvision_cinema_duo_v30.py"
)
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
engine.CONFIG = ROOT / "config/artvision_autoproduction_20261025_1415.json"

def full_opaque_museum_matte(art):
    """A single authentic painting on solid dark matte, no blur or ghost image."""
    w, h = 1080, 1920
    bg = Image.new("RGB", (w, h), (6, 9, 15))
    whole = art.copy().convert("RGB")
    whole.thumbnail((1020, 1540), Image.Resampling.LANCZOS)
    x, y = (w - whole.width)//2, (h - whole.height)//2
    draw = ImageDraw.Draw(bg)
    draw.rectangle((x-8, y-8, x+whole.width+7, y+whole.height+7),
                   fill=(19, 22, 29))
    bg.paste(whole, (x, y))
    return bg

engine.cinema.full = full_opaque_museum_matte

if __name__ == "__main__":
    engine.main()
