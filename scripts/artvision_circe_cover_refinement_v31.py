#!/usr/bin/env python3
"""Cover-only refinement V31 for Circe Invidiosa, preserving the approved V6 movie.
One elegant V6-family band: artwork title + artist, no duplicated music/title.
"""
from pathlib import Path
import argparse
from PIL import Image,ImageDraw,ImageFont
W,H=1080,1920

def create(source,out):
    src=Image.open(source).convert('RGB')
    iw,ih=src.size;zoom=1.15
    vw=min(iw,ih*W/H)/zoom;vh=vw*H/W
    cx,cy=.52,.34
    x=min(max(0,cx*iw-vw/2),iw-vw)
    y=min(max(0,cy*ih-vh/2),ih-vh)
    base=src.crop((round(x),round(y),round(x+vw),round(y+vh))).resize((W,H),Image.Resampling.LANCZOS).convert('RGBA')
    layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
    d.rounded_rectangle((56,1340,1024,1590),radius=10,fill=(5,8,13,205))
    d.line((130,1495,950,1495),fill=(218,198,168,186),width=2)
    serif='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
    sans='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    def center(text,top,maxw,size,font,color):
        while size>16:
            f=ImageFont.truetype(font,size)
            b=d.textbbox((0,0),text,font=f);width=b[2]-b[0]
            if width<=maxw:break
            size-=1
        d.text(((W-width)/2,top),text,font=f,fill=color)
    center('CIRCE INVIDIOSA',1387,880,68,serif,(255,251,243,255))
    center('JOHN WILLIAM WATERHOUSE',1521,870,31,sans,(218,208,192,255))
    Path(out).parent.mkdir(parents=True,exist_ok=True)
    Image.alpha_composite(base,layer).convert('RGB').save(out,quality=95,subsampling=0)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--source',required=True)
    p.add_argument('--out',required=True)
    a=p.parse_args()
    create(a.source,a.out)
