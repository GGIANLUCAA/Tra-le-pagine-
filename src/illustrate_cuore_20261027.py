#!/usr/bin/env python3
"""16 original gothic ink-and-light illustrations for Poe's The Tell-Tale Heart.
No stock, API, image model, copyrighted photos, or externally sourced media.
Each frame has its own scene composition; not a cropped collage.
"""
from pathlib import Path
import argparse
import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
W,H=720,1280
GOLD=(231,188,113)
CYAN=(121,191,207)
RED=(194,67,64)

def poly(d, pts, fill, outline=None, width=1):
    d.polygon(pts,fill=fill)
    if outline:d.line(pts+[pts[0]],fill=outline,width=width,joint="curve")

def glow(im, x,y,rad,col,alpha=100):
    layer=Image.new("RGBA",(W,H))
    d=ImageDraw.Draw(layer)
    d.ellipse((x-rad,y-rad,x+rad,y+rad),fill=(*col,alpha))
    layer=layer.filter(ImageFilter.GaussianBlur(rad//2))
    im.alpha_composite(layer)

def canvas(seed,top=(10,19,31),bottom=(43,48,55)):
    rng=random.Random(seed)
    im=Image.new("RGB",(W,H))
    pix=im.load()
    # textured midnight gradient; distinct flecks, not smooth placeholder blocks
    for y in range(H):
        t=y/H
        for x in range(W):
            grain=rng.gauss(0,4.3)+2.2*math.sin(x*.021+y*.014)
            shade=.83+.17*math.cos((x-W*.5)/W*math.pi)
            pix[x,y]=tuple(max(0,min(255,int((top[i]*(1-t)+bottom[i]*t)*shade+grain))) for i in range(3))
    return im.convert("RGBA")

def room(d,vanish=(350,385),floor=815,angle=0):
    vx,vy=vanish
    poly(d,[(0,0),(W,0),(W,H),(0,H)],(13,20,29,85))
    poly(d,[(0,0),(vx,vy),(vx,floor),(0,H)],(16,24,34,220),GOLD+(42,),2)
    poly(d,[(W,0),(vx,vy),(vx,floor),(W,H)],(33,35,42,225),GOLD+(45,),2)
    poly(d,[(0,H),(vx,floor),(W,H)],(55,43,43,230),GOLD+(70,),3)
    for n in range(-5,8):
        x=vx+n*94
        d.line((vx,floor,x,H),fill=(215,156,105,95),width=3)
    for yy in (900,995,1095,1205):
        d.line((0,yy,W,yy),fill=(210,147,105,75),width=3)

def door(d,x=175,y=255,w=365,h=720,ajar=False):
    d.rectangle((x,y,x+w,y+h),fill=(8,16,24,255),outline=(198,146,91,220),width=10)
    poly(d,[(x+23,y+25),(x+w-20,y+25),(x+w-20,y+h-26),(x+23,y+h-26)],(44,37,39,255),(148,108,73,170),3)
    for yy in (y+100,y+380):
        d.rectangle((x+48,yy,x+w-52,yy+210),outline=(134,103,83,160),width=6)
    if ajar:
        poly(d,[(x+w-30,y+20),(x+w+90,y+125),(x+w+90,y+h+30),(x+w-30,y+h-20)],(12,20,29,250),GOLD+(160,),4)
    d.ellipse((x+w-75,y+h*.58,x+w-58,y+h*.58+17),fill=GOLD+(230,))

def figure(d,x,y,scale=1,old=False,turn=0,arms=True,shade=None):
    col=shade or ((38,39,47,255) if old else (9,16,27,255))
    rw=48*scale
    # shoulders, legs and head are entirely within frame
    poly(d,[(x-80*scale,y+160*scale),(x-44*scale,y+72*scale),(x+42*scale,y+72*scale),(x+90*scale,y+170*scale),(x+64*scale,y+385*scale),(x-65*scale,y+385*scale)],col,(161,121,86,145),max(1,int(2*scale)))
    d.ellipse((x-rw,y-42*scale,x+rw,y+90*scale),fill=(181,154,132,255) if old else (24,30,38,255),outline=(215,171,113,190),width=max(1,int(3*scale)))
    if old:
        d.arc((x-rw-4*scale,y-52*scale,x+rw+4*scale,y+35*scale),175,355,fill=(219,220,205,230),width=max(2,int(11*scale)))
        d.line((x-12*scale,y+46*scale,x+16*scale,y+45*scale),fill=(65,70,76,240),width=max(1,int(2*scale)))
    if arms:
        d.line((x-62*scale,y+150*scale,x-105*scale,y+305*scale),fill=col,width=max(8,int(28*scale)))
        d.line((x+58*scale,y+150*scale,x+95*scale,y+295*scale),fill=col,width=max(8,int(28*scale)))

def eye(d,x,y,scale=1,open_=True):
    w=185*scale;h=86*scale
    d.ellipse((x-w,y-h,x+w,y+h),fill=(226,219,194,250),outline=(67,50,50,255),width=max(3,int(9*scale)))
    if open_:
        d.ellipse((x-66*scale,y-69*scale,x+66*scale,y+69*scale),fill=(100,155,178,255),outline=(45,70,86,255),width=max(2,int(7*scale)))
        d.ellipse((x-30*scale,y-35*scale,x+30*scale,y+35*scale),fill=(24,39,51,255))
        d.ellipse((x-42*scale,y-55*scale,x-12*scale,y-23*scale),fill=(255,255,245,230))
        d.arc((x-w+8,y-h+5,x+w-8,y+h-3),190,344,fill=(255,255,250,180),width=max(2,int(4*scale)))
    else:
        d.line((x-w,y,x+w,y),fill=(50,42,45,255),width=max(2,int(8*scale)))

def lantern(d,x,y,angle=0):
    d.line((x,y-135,x,y-25),fill=(207,166,104,230),width=9)
    poly(d,[(x-48,y-26),(x+48,y-26),(x+36,y+105),(x-36,y+105)],(219,171,99,85),GOLD+(240,),6)
    d.ellipse((x-18,y+5,x+18,y+40),fill=(249,211,140,255))
    d.arc((x-55,y-60,x+55,y+15),175,355,fill=GOLD+(220,),width=8)

def bed(d,x=75,y=740,w=575,h=290):
    poly(d,[(x,y+75),(x+w,y+42),(x+w,y+h),(x,y+h+40)],(71,63,63,255),GOLD+(160,),5)
    poly(d,[(x+15,y+42),(x+w-18,y+16),(x+w-22,y+155),(x+15,y+195)],(194,185,163,235),(239,216,172,170),4)
    d.ellipse((x+42,y+5,x+210,y+125),fill=(206,194,176,255),outline=(235,210,163,220),width=3)
    d.line((x,y+75,x,y+h+85),fill=(112,76,65,255),width=13)
    d.line((x+w,y+42,x+w,y+h+35),fill=(112,76,65,255),width=13)

def clock(d,x,y,r=170):
    d.ellipse((x-r-15,y-r-15,x+r+15,y+r+15),fill=(22,30,38,255),outline=GOLD+(230,),width=13)
    d.ellipse((x-r+18,y-r+18,x+r-18,y+r-18),outline=(197,174,139,190),width=4)
    for j in range(12):
        a=math.pi*2*j/12
        xx=x+math.sin(a)*(r-38); yy=y-math.cos(a)*(r-38)
        d.ellipse((xx-4,yy-4,xx+4,yy+4),fill=(238,211,156,240))
    d.line((x,y,x+67,y-77),fill=GOLD+(245,),width=10)
    d.line((x,y,x-30,y-108),fill=GOLD+(245,),width=8)
    d.ellipse((x-12,y-12,x+12,y+12),fill=(255,220,154,255))

def heartbeat(d,x,y,scale=1):
    pts=[]
    for i in range(121):
        px=x+(i-60)*5*scale
        v=0
        if 32<i<38:v=-(i-32)*17
        elif 38<=i<42:v=-102+(i-38)*63
        elif 42<=i<48:v=150-(i-42)*25
        elif 70<=i<78:v=-22*math.sin((i-70)/8*math.pi)
        pts.append((px,y+v*scale))
    d.line(pts,fill=RED+(235,),width=max(3,int(6*scale)),joint="curve")

def chair(d,x,y):
    d.line((x-110,y-195,x-110,y+170),fill=(109,77,59,255),width=18)
    d.line((x+85,y-195,x+85,y+170),fill=(109,77,59,255),width=18)
    poly(d,[(x-110,y-192),(x+85,y-192),(x+78,y-18),(x-105,y-18)],(55,48,47,255),GOLD+(140,),4)
    poly(d,[(x-135,y+10),(x+120,y-5),(x+100,y+58),(x-115,y+65)],(84,57,49,255),GOLD+(140,),4)
    d.line((x-107,y+60,x-120,y+260),fill=(96,65,54,255),width=14)
    d.line((x+90,y+60,x+110,y+260),fill=(96,65,54,255),width=14)

def scene(n,out):
    rng=random.Random(20261027+n*31)
    top=(8,17,29) if n not in (3,8,13) else (29,16,26)
    im=canvas(n+17,top=top,bottom=(48,42,44))
    d=ImageDraw.Draw(im,"RGBA")
    if n in (0,1,2,4,5,6,9,10,11,12,14,15):
        room(d,vanish=(350,390 if n!=9 else 340),floor=835)
    if n==0:
        for k in range(8):
            d.line((0,820+k*57,W,810+k*61),fill=(206,137,91,150),width=5)
        heartbeat(d,350,615,1.05)
        d.ellipse((135,180,585,640),outline=RED+(45,),width=12)
    elif n==1:
        glow(im,370,520,300,GOLD,70);d=ImageDraw.Draw(im,"RGBA")
        figure(d,330,480,1.45,False)
        d.arc((140,230,560,880),190,345,fill=GOLD+(90,),width=6)
    elif n==2:
        d.rectangle((430,210,610,710),fill=(55,83,94,130),outline=GOLD+(160,),width=7)
        figure(d,300,505,1.13,True)
        d.ellipse((280,565,310,584),fill=CYAN+(245,))
    elif n==3:
        for k in range(13):
            d.arc((55-k*3,280-k*4,670+k*3,960+k*4),165,345,fill=(171,112,95,40),width=3)
        eye(d,355,630,1.38,True)
    elif n==4:
        for k in range(7):
            x=45+k*96
            poly(d,[(x,400),(x+72,400),(x+72,895),(x,895)],(6,15,24,160),GOLD+(40,),2)
        door(d,198,335,322,620,True)
        d.polygon([(460,480),(720,180),(720,1080),(460,870)],fill=(220,183,112,32))
    elif n==5:
        bed(d,75,710,580,265)
        figure(d,350,635,.56,True,arms=False)
        d.arc((240,420,540,690),180,350,fill=(198,175,123,120),width=5)
    elif n==6:
        clock(d,370,380,170)
        door(d,185,695,360,450,True)
        d.line((480,700,640,1040),fill=(235,190,117,100),width=7)
    elif n==7:
        d.polygon([(0,900),(720,530),(720,950)],fill=(235,191,113,80))
        eye(d,425,655,.90,True)
        lantern(d,130,700)
        d.line((230,630,350,625),fill=GOLD+(170,),width=6)
    elif n==8:
        for k in range(9):
            r=55+k*54
            d.ellipse((355-r,640-r,355+r,640+r),outline=RED+(max(20,140-k*13),),width=7)
        heartbeat(d,355,635,.9)
    elif n==9:
        bed(d,75,730,560,280)
        poly(d,[(250,570),(450,570),(520,980),(185,980)],(7,11,20,225),GOLD+(65,),3)
        d.ellipse((285,450,417,592),fill=(7,11,20,245))
    elif n==10:
        for k in range(9):
            yy=510+k*75
            d.line((0,yy,W,yy+28),fill=(221,164,109,190),width=7)
        d.polygon([(180,880),(580,900),(560,1120),(170,1090)],fill=(14,21,28,245),outline=GOLD+(160,))
        d.line((330,470,440,770),fill=(120,93,72,240),width=17)
    elif n==11:
        door(d,95,190,530,875,False)
        for k,x in enumerate((250,375,495)):
            figure(d,x,625,.57,False,arms=False,shade=(20,26,35,255))
        d.ellipse((125,310,590,760),outline=GOLD+(70,),width=4)
    elif n==12:
        chair(d,340,830)
        for x in (170,360,545):
            figure(d,x,350,.64,False,arms=False,shade=(27,33,43,255))
        d.line((30,740,700,735),fill=GOLD+(95,),width=7)
    elif n==13:
        chair(d,340,680)
        heartbeat(d,350,990,.92)
        for k in range(5):
            d.arc((130-k*20,320-k*40,590+k*20,860+k*40),180,340,fill=RED+(70-k*10,),width=5)
    elif n==14:
        for x in (120,330,565):
            figure(d,x,480,.75,False,arms=False,shade=(27,31,38,255))
        heartbeat(d,345,1020,.73)
        d.line((0,845,720,845),fill=GOLD+(130,),width=4)
    elif n==15:
        for k in range(9):
            d.line((0,800+k*55,W,815+k*55),fill=GOLD+(95,),width=4)
        d.polygon([(290,410),(330,350),(355,670),(380,990),(335,1010)],fill=(177,140,105,240))
        d.ellipse((292,310,367,420),fill=(181,145,109,245))
        heartbeat(d,360,1040,.6)
    # floating ink scratches and paper grain, all confined to a single opaque scene
    d=ImageDraw.Draw(im,"RGBA")
    for _ in range(360):
        x=rng.randrange(W);y=rng.randrange(H)
        dx=rng.randrange(1,19)
        d.line((x,y,x+dx,y+rng.randrange(-3,4)),fill=(234,205,164,rng.randrange(4,19)),width=1)
    rgb=im.convert("RGB")
    rgb=ImageEnhance.Contrast(rgb).enhance(1.11)
    # deterministic texture makes file nontrivial, never a debug placeholder
    rgb.save(out,quality=91,subsampling=0,optimize=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    for i in range(16):
        path=a.out/f"scena_{i+1:02}.jpg"
        scene(i,path)
        if path.stat().st_size<35000:raise RuntimeError("Illustration unexpectedly small: "+str(path))
        print(path.name,path.stat().st_size,flush=True)
if __name__=="__main__":
    main()
