#!/usr/bin/env python3
"""Experimental source-faithful 2.5D foreground pull from Met 436105.
Not a real 3D mesh. No network APIs beyond downloading CC0 artwork.
No paid services, no ArtVision production or publishing integration.
"""
import argparse
import hashlib
import io
import json
import math
import subprocess
from pathlib import Path
from urllib.request import Request, urlopen

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

MET_URL = "https://images.metmuseum.org/CRDImages/ep/original/DP-13139-001.jpg"
FALLBACK = "https://commons.wikimedia.org/wiki/Special:FilePath/The_Death_of_Socrates_MET_DP-13139-001.jpg?width=2400"
W, H = 720, 1280


def download():
    errors = []
    for url in [MET_URL, FALLBACK]:
        try:
            req = Request(url, headers={"User-Agent": "ArtVision-3DStudio-test/1.0 (public domain art experiment)"})
            with urlopen(req, timeout=45) as r:
                data = r.read(18_000_000)
            im = Image.open(io.BytesIO(data)).convert("RGB")
            if min(im.size) < 800:
                raise ValueError("low resolution")
            return im, data, url
        except Exception as exc:
            errors.append(str(exc)[:200])
    raise RuntimeError("Unable to fetch genuine artwork: " + "; ".join(errors))


def font(size):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
              "/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf"]:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def masks(image):
    w, h = image.size
    # A broad, manually inferred trimap for the central figure, to be visually audited.
    # No fictitious AI segmentation claim. Retains foreground only if GrabCut agrees.
    poly = [(0.31,.46),(.38,.43),(.46,.42),(.48,.36),(.49,.31),
            (.51,.29),(.54,.32),(.56,.41),(.60,.40),(.60,.30),
            (.60,.21),(.63,.17),(.66,.22),(.67,.40),(.65,.49),
            (.64,.61),(.62,.73),(.57,.86),(.49,.87),(.46,.71),
            (.43,.60),(.38,.55),(.31,.53)]
    pts = np.array([[(int(x*w),int(y*h)) for x,y in poly]], np.int32)
    zone = np.zeros((h,w), np.uint8)
    cv2.fillPoly(zone, pts, 255)
    # Hard foreground seeds from eroded silhouette, probable foreground nearer its edge.
    interior = cv2.erode(zone, np.ones((25,25),np.uint8), iterations=1)
    exterior = cv2.dilate(zone, np.ones((23,23),np.uint8), iterations=1)
    gc = np.full((h,w),cv2.GC_BGD, dtype=np.uint8)
    gc[exterior>0] = cv2.GC_PR_BGD
    gc[zone>0] = cv2.GC_PR_FGD
    gc[interior>0] = cv2.GC_FGD
    gc[:4,:] = cv2.GC_BGD
    bg = np.zeros((1,65),np.float64)
    fg = np.zeros((1,65),np.float64)
    bgr = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
    cv2.grabCut(bgr,gc,None,bg,fg,4,cv2.GC_INIT_WITH_MASK)
    result = np.uint8(np.where((gc==cv2.GC_FGD)|(gc==cv2.GC_PR_FGD),255,0))
    # Exclude distant isolated blobs. Use only the largest 3 connected foreground components.
    n, labels, stats, centers = cv2.connectedComponentsWithStats(result, 8)
    if n>1:
        order = sorted(range(1,n),key=lambda i: stats[i,cv2.CC_STAT_AREA],reverse=True)
        selected = [i for i in order[:4] if stats[i,cv2.CC_STAT_AREA] > 120]
        result = np.where(np.isin(labels,selected),255,0).astype(np.uint8)
    result = cv2.morphologyEx(result,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    result = cv2.GaussianBlur(result,(5,5),1.2)
    if int((result>100).sum()) < 1800:
        raise ValueError("foreground mask collapsed")
    return result


def plate(image,mask):
    src = cv2.cvtColor(np.asarray(image),cv2.COLOR_RGB2BGR)
    holes = cv2.dilate((mask>90).astype(np.uint8)*255, np.ones((13,13),np.uint8),iterations=1)
    bg = cv2.inpaint(src,holes,17,cv2.INPAINT_TELEA)
    # soften inpainted part; this remains a visible approximation, not faithful restored source.
    return Image.fromarray(cv2.cvtColor(bg,cv2.COLOR_BGR2RGB))


def background():
    y,x=np.mgrid[0:H,0:W]
    cx,cy=W*.47,H*.35
    light=np.exp(-(((x-cx)/520)**2+((y-cy)/820)**2))
    grain=np.random.default_rng(42).normal(0,1.4,(H,W))
    arr=np.zeros((H,W,3),np.uint8)
    for c,(base,add) in enumerate([(16,28),(19,29),(25,30)]):
        arr[:,:,c]=np.clip(base+light*add+grain,0,255)
    return Image.fromarray(arr,"RGB")


def stage(img,clean,fg,mask,p=0):
    sc=background()
    d=ImageDraw.Draw(sc,"RGB")
    d.rectangle((0,1000,W,H),fill=(25,25,30))
    for j in range(120):
        pos=1000+j
        d.line((0,pos,W,pos),fill=(26+int(j*.07),26+int(j*.06),29+int(j*.05)))
    d.text((W//2,96),"ARTVISION   /   3D STUDIO",fill=(218,190,141),font=font(25),anchor="mm")
    d.text((W//2,158),"THE DEATH OF SOCRATES",fill=(242,236,219),font=font(33),anchor="mm")
    d.text((W//2,202),"JACQUES-LOUIS DAVID  ·  1787",fill=(178,171,156),font=font(20),anchor="mm")
    pw,ph=620,int(620*img.height/img.width)
    px,py=(W-pw)//2,445
    # Museum frame is a creative approximation, not authenticated actual frame.
    shadow=Image.new("RGBA",(W,H))
    sh=ImageDraw.Draw(shadow)
    sh.rounded_rectangle((px-32,py-29,px+pw+39,py+ph+43),radius=8,fill=(0,0,0,180))
    shadow=shadow.filter(ImageFilter.GaussianBlur(23))
    sc=Image.alpha_composite(sc.convert("RGBA"),shadow)
    d=ImageDraw.Draw(sc)
    for depth,color in [(24,(49,30,18)),(19,(130,86,41)),(15,(211,164,81)),(11,(88,56,30)),(7,(223,181,104)),(2,(57,39,22))]:
        d.rectangle((px-depth,py-depth,px+pw+depth,py+ph+depth),outline=color,width=3)
    painting=img.resize((pw,ph),Image.Resampling.LANCZOS)
    sc.paste(clean.resize((pw,ph),Image.Resampling.LANCZOS) if p>0.01 else painting,(px,py))
    if p>0.01:
        # Shift/scale of the original painted figure; 2.5D plane with contact shadow.
        rgba=fg.resize((pw,ph),Image.Resampling.LANCZOS)
        alpha=mask.resize((pw,ph),Image.Resampling.BICUBIC)
        rgba.putalpha(alpha)
        cx=px+int(pw*.52);cy=py+int(ph*.51)
        scale=1+0.43*p
        sw,shh=int(pw*scale),int(ph*scale)
        subject=rgba.resize((sw,shh),Image.Resampling.BICUBIC)
        x=int(cx+(px-cx)*scale+14*p)
        y=int(cy+(py-cy)*scale-66*p)
        contact=Image.new("RGBA",(W,H),(0,0,0,0))
        dark=Image.new("RGBA", subject.size,(0,0,0,0))
        dark.putalpha(subject.getchannel("A").point(lambda v:int(v*.48*p)))
        contact.paste(dark,(x+int(28*p),y+int(34*p)))
        sc=Image.alpha_composite(sc,contact.filter(ImageFilter.GaussianBlur(20)))
        # Dark edge makes flat sprite appear separated from the canvas.
        sc.alpha_composite(subject,(x,y))
        # Subtle directional rim highlight on the mask boundary.
        if p>.65:
            a=np.asarray(subject.getchannel("A"))
            edges=cv2.Canny(a,25,140)
            glow=np.zeros((shh,sw,4),np.uint8)
            glow[:,:,:3]=[219,178,108];glow[:,:,3]=(edges*.14*p).astype(np.uint8)
            sc.alpha_composite(Image.fromarray(glow,"RGBA"),(x,y))
    d=ImageDraw.Draw(sc)
    d.text((W//2,1048), "DIPINTO ORIGINALE" if p<.01 else "SOCRATE OLTRE LA CORNICE",
           font=font(25),fill=(232,220,196),anchor="mm")
    d.text((W//2,1089),"MET · 436105 · PUBLIC DOMAIN",font=font(17),fill=(151,151,150),anchor="mm")
    d.text((W//2,1131),"PROVA TECNICA 2.5D · NON 3D REALE",font=font(18),fill=(204,163,98),anchor="mm")
    return sc.convert("RGB")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="output/artvision-3d-socrates-test")
    args=ap.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    im,raw,url=download()
    (out/"Socrate_MET_originale.jpg").write_bytes(raw)
    im.thumbnail((960,960),Image.Resampling.LANCZOS)
    mask_arr=masks(im)
    mask=Image.fromarray(mask_arr)
    fg=im.copy()
    clean=plate(im,mask_arr)
    mask.save(out/"socrates_mask_review.png")
    before=stage(im,clean,fg,mask,0)
    after=stage(im,clean,fg,mask,1)
    before.save(out/"01_PRIMA_originale.jpg",quality=91)
    after.save(out/"02_DOPO_popout_2_5D.jpg",quality=93)
    # Single comparison, each half derives directly from the genuine Met photograph.
    comp=Image.new("RGB",(W*2,H),(0,0,0))
    comp.paste(before,(0,0));comp.paste(after,(W,0))
    comp.save(out/"03_PRIMA_DOPO_confronto.jpg",quality=92)
    cmd=["ffmpeg","-y","-f","rawvideo","-pixel_format","rgb24","-video_size",f"{W}x{H}",
         "-framerate","15","-i","-","-an","-c:v","libx264","-preset","veryfast",
         "-pix_fmt","yuv420p","-crf","23","-movflags","+faststart",str(out/"04_POP_OUT_demo_5s.mp4")]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    try:
        for i in range(75):
            t=i/15
            prog=max(0,min(1,(t-.45)/3.35))
            prog=prog*prog*(3-2*prog)
            frame=stage(im,clean,fg,mask,prog)
            proc.stdin.write(frame.tobytes())
        proc.stdin.close()
        errs=proc.stderr.read().decode(errors="replace")
        rc=proc.wait()
        if rc:raise RuntimeError("ffmpeg failed "+errs[-800:])
    except Exception:
        proc.kill()
        raise
    manifest={"source":url,"met_object_id":436105,"source_sha256":hashlib.sha256(raw).hexdigest(),
              "image_size_original":Image.open(io.BytesIO(raw)).size,
              "reconstruction":"2.5D planar extract using mask / GrabCut + illustration; NOT true 3D",
              "frame":"scenic approximation NOT authenticated", "audio":False,"paid_api_calls":0,
              "qa":"automated file-level only, visual and Android review still required",
              "files":{p.name:{"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
                       for p in out.iterdir() if p.is_file()}}
    (out/"MANIFEST.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1",str(out/"04_POP_OUT_demo_5s.mp4")],check=True)
    print(json.dumps({k:v for k,v in manifest.items() if k!="files"},indent=2))


if __name__=="__main__":
    main()
