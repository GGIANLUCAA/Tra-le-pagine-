#!/usr/bin/env python3
"""ArtVision V31 · Mikhail Vrubel / The Demon Seated (1890).
New source-specific direction; no changes to V6 Gold Master.
Uses the proven V30 rendering/rights pipeline and the 24 October no-ghosting rule.
"""
from pathlib import Path
import importlib.util
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("artvision_cinema_duo_v30",ROOT/"scripts/artvision_cinema_duo_v30.py")
engine=importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
engine.CONFIG=ROOT/"config/artvision_autoproduction_20261025_0515.json"

def full_canvas_opaque_museum_matte(src):
    """Display exactly ONE sharp unaltered artwork on opaque charcoal, no ghosting."""
    W,H=1080,1920
    bg=Image.new("RGB",(W,H),(8,11,16))
    painting=src.copy()
    painting.thumbnail((1030,1550),Image.Resampling.LANCZOS)
    x=(W-painting.width)//2
    y=(H-painting.height)//2
    pen=ImageDraw.Draw(bg)
    pen.rectangle((x-11,y-11,x+painting.width+10,y+painting.height+10),fill=(21,24,29))
    pen.rectangle((x-3,y-3,x+painting.width+2,y+painting.height+2),outline=(174,151,116),width=3)
    bg.paste(painting,(x,y))
    return bg

def cover_one_band(image,path):
    """V6 family: same palette, typeface, one discreet band, artwork title and artist."""
    W,H=1080,1920
    bg=image.convert("RGB").copy()
    draw=ImageDraw.Draw(bg,"RGBA")
    draw.rounded_rectangle((56,1340,1024,1590),radius=10,fill=(5,8,13,190))
    draw.line((130,1495,950,1495),fill=(218,198,168,186),width=2)
    serif="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
    sans="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    title="THE DEMON SEATED"
    artist="MIKHAIL VRUBEL"
    tf=ImageFont.truetype(serif,60)
    af=ImageFont.truetype(sans,30)
    def center(s,font,y,fill):
        box=draw.textbbox((0,0),s,font=font)
        draw.text(((W-(box[2]-box[0]))/2,y),s,font=font,fill=fill)
    center(title,tf,1390,(255,251,243,255))
    center(artist,af,1525,(218,208,192,255))
    bg.save(path,quality=95,subsampling=0)

engine.cinema.full=full_canvas_opaque_museum_matte
engine.cinema.make_cover=cover_one_band
if __name__=="__main__":
    engine.main()
