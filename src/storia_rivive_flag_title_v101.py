#!/usr/bin/env python3
"""V101: draw a small historical flag and title in transparent vertical overlay.
Does not imply verified visual clearance for people in the scene.
"""
import argparse
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

FLAGS={"FR":("#002395","#FFFFFF","#ED2939")}
def produce(metadata,destination):
    code=metadata.get("flag");place=metadata.get("place");year=metadata.get("year")
    if code not in FLAGS or not isinstance(place,str) or not place.isupper() or not isinstance(year,int) or not 1800<=year<=2026:
        raise ValueError("Unsupported or unreviewed flag/place/year")
    im=Image.new("RGBA",(720,1280),(0,0,0,0))
    draw=ImageDraw.Draw(im);x=44;y=54;w=39;h=26
    for i,color in enumerate(FLAGS[code]):
        draw.rectangle((x+i*w//3,y,x+(i+1)*w//3-1,y+h-1),fill=color)
    draw.rectangle((x,y,x+w-1,y+h-1),outline=(240,230,210,190),width=1)
    try: font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",32)
    except OSError:font=ImageFont.load_default()
    caption=place+" · "+str(year)
    draw.text((99,45),caption,font=font,fill=(246,232,206,255),stroke_width=1,stroke_fill=(20,23,28,175))
    bbox=draw.textbbox((99,45),caption,font=font)
    if bbox[2]>684 or bbox[3]>102:raise ValueError("Title exceeds safe area")
    path=Path(destination);path.parent.mkdir(parents=True,exist_ok=True);im.save(path)
    return {"overlay":str(path),"format":"720x1280 RGBA","flag":code,
            "safe_zone_geometry_pass":True,"subject_occlusion_check":"PENDING_ON_ACTUAL_VIDEO"}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--place",required=True);p.add_argument("--year",type=int,required=True)
    p.add_argument("--flag",required=True);p.add_argument("--output",required=True)
    a=p.parse_args()
    print(produce({"place":a.place,"year":a.year,"flag":a.flag},a.output))
