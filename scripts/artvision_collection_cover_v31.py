#!/usr/bin/env python3
"""Additive cover refinement for V31 Symbolist collection; leaves Cinema V6 master untouched."""
from pathlib import Path
import argparse
from PIL import Image,ImageDraw,ImageFont
W,H=1080,1920
def create(source,output):
    im=Image.open(source).convert("RGB")
    iw,ih=im.size;cx,cy,zoom=.36,.26,1.27
    vw=min(iw,ih*W/H)/zoom;vh=vw*H/W
    x=min(max(0,cx*iw-vw/2),iw-vw);y=min(max(0,cy*ih-vh/2),ih-vh)
    frame=im.crop((round(x),round(y),round(x+vw),round(y+vh))).resize((W,H),Image.Resampling.LANCZOS)
    base=frame.convert("RGBA");layer=Image.new("RGBA",(W,H));d=ImageDraw.Draw(layer)
    d.rounded_rectangle((56,1340,1024,1590),radius=10,fill=(5,8,13,203))
    serif="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
    sans="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    def centered(text,top,max_width,point,font,color):
        n=point
        while n>14:
            f=ImageFont.truetype(font,n)
            bbox=d.textbbox((0,0),text,font=f)
            width=bbox[2]-bbox[0]
            if width<=max_width:break
            n-=1
        d.text(((W-width)/2,top),text,font=f,fill=color)
    centered("VISIONS OF SYMBOLISM",1378,890,57,serif,(255,251,243,255))
    d.line((130,1495,950,1495),fill=(218,198,168,186),width=2)
    centered("MOREAU  ·  REDON  ·  BÖCKLIN",1521,880,29,sans,(218,208,192,255))
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Image.alpha_composite(base,layer).convert("RGB").save(output,quality=95,subsampling=0)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,help="ORIGINAL_REDON.jpg")
    p.add_argument("--out",required=True,help="COPERTINA.jpg")
    a=p.parse_args()
    create(a.source,a.out)
