#!/usr/bin/env python3
"""ArtVision V31 / 25 October 02:15: Circe Invidiosa by John William Waterhouse.
Additive bespoke 14-shot curatorial short using proven V30 renderer and immutable V6 signature.
Full artwork on a fully opaque charcoal museum matte; no cross-scene alpha or ghosting.
"""
from pathlib import Path
import importlib.util
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("artvision_cinema_duo_v30",ROOT/"scripts/artvision_cinema_duo_v30.py")
engine=importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
engine.CONFIG=ROOT/"config/artvision_autoproduction_20261025_0215.json"

def full_canvas_museum_matte(src):
    W,H=1080,1920
    base=Image.new("RGB",(W,H),(10,13,17))
    full=src.copy()
    full.thumbnail((1010,1770),Image.Resampling.LANCZOS)
    x=(W-full.width)//2
    y=(H-full.height)//2
    d=ImageDraw.Draw(base)
    d.rectangle((x-9,y-9,x+full.width+8,y+full.height+8),fill=(22,23,27))
    d.rectangle((x-2,y-2,x+full.width+1,y+full.height+1),outline=(184,157,117),width=2)
    base.paste(full,(x,y))
    return base

engine.cinema.full=full_canvas_museum_matte

if __name__=="__main__":
    engine.main()
