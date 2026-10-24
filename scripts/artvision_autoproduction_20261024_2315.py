#!/usr/bin/env python3
"""ArtVision V31 scheduled 23:15: Hugo Simberg, The Wounded Angel (1903).
Additive entrypoint for V30 Cinema, preserving approved V6 opening/cover and V25/V28 gates.
Full-canvas shots use an OPAQUE charcoal museum matte, not blurred duplicate painting.
This implements the latest no-ghosting/one-opaque-artwork rule without modifying historical masters.
"""
from pathlib import Path
import importlib.util
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("artvision_cinema_duo_v30",ROOT/"scripts/artvision_cinema_duo_v30.py")
engine=importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
engine.CONFIG=ROOT/"config/artvision_autoproduction_20261024_2315.json"

def full_canvas_opaque_museum_matte(src):
    """One sharp, opaque, unaltered painting on a neutral matte; never a ghosted backdrop."""
    W,H=1080,1920
    bg=Image.new("RGB",(W,H),(9,12,17))
    whole=src.copy()
    whole.thumbnail((1020,1600),Image.Resampling.LANCZOS)
    x=(W-whole.width)//2
    y=(H-whole.height)//2
    d=ImageDraw.Draw(bg)
    d.rectangle((x-8,y-8,x+whole.width+7,y+whole.height+7),fill=(20,23,27))
    d.rectangle((x-2,y-2,x+whole.width+1,y+whole.height+1),outline=(172,151,118),width=2)
    bg.paste(whole,(x,y))
    return bg

engine.cinema.full=full_canvas_opaque_museum_matte
if __name__=="__main__":
    engine.main()
