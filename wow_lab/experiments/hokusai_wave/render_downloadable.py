#!/usr/bin/env python3
"""Hokusai CC0 cinematic pop-out export for independent Android download.

No Vidu, no AI image synthesis, no changes outside WOW LAB. Artistically
experimental 2.5D; nothing here constitutes a real 3D mesh or historical frame.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import cv2, numpy as np, math, wave, json, subprocess, hashlib, zipfile

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/"assets"
OUT=ROOT/"output"
OUT.mkdir(exist_ok=True)
W,H=720,1280
FPS=24
DUR=11
PW,PH=540,363
PX,PY=90,470
def ease(t):
    t=np.clip(t,0,1)
    return float(t*t*(3-2*t))
def reveal(t):
    if t<.5:return 0.0
    if t<2.7:return ease((t-.5)/2.2)
    if t<5.9:return 1.0
    if t<8.25:return 1-ease((t-5.9)/2.35)
    return 0.0
def font(size):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf","/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf"):
        if Path(p).is_file():return ImageFont.truetype(p,size)
    return ImageFont.load_default()

def cutout(source):
    a=np.asarray(source,dtype=np.uint8)
    hh,ww=a.shape[:2]
    b,g,r=cv2.split(a[:,:,::-1])
    b=b.astype("int16");g=g.astype("int16");r=r.astype("int16")
    blue=(b-r>16)&(b-g>5)&(b>g*.99)&(r<210)
    poly=np.array([[0,325],[130,325],[235,240],[285,190],[345,146],[450,99],[575,80],[665,81],
                   [745,116],[850,188],[920,265],[935,415],[875,461],[825,450],[775,510],[755,705],
                   [640,760],[560,710],[500,660],[410,650],[300,710],[200,745],[60,730],[0,720]],np.int32)
    poly[:,0]=poly[:,0]*ww//1600;poly[:,1]=poly[:,1]*hh//1076
    area=np.zeros((hh,ww),np.uint8)
    cv2.fillPoly(area,[poly],255)
    mask=blue.astype("uint8")*255
    mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(13,13)))
    mask=cv2.dilate(mask,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,15)))
    mask=cv2.bitwise_and(mask,area)
    mask[:int(345*hh/1076),:int(140*ww/1600)]=0
    mask=cv2.GaussianBlur(mask,(7,7),1.7)
    ratio=float(np.mean(mask>125))
    if not (.11<ratio<.32):raise RuntimeError(f"Unexpected wave foreground ratio {ratio:.3f}")
    return mask

def clean_plate(source,mask):
    """Conservative scenic background, preserving print beneath other objects."""
    rgb=np.asarray(source).astype("float32")
    h,w=mask.shape
    outer=cv2.dilate((mask>10).astype(np.uint8)*255,
                     cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(29,29)))
    num,labels,stats,_=cv2.connectedComponentsWithStats(outer,8)
    keep=np.zeros_like(outer)
    for idx in range(1,num):
        if stats[idx,cv2.CC_STAT_AREA]>280:
            keep[labels==idx]=255
    strength=cv2.GaussianBlur(keep,(0,0),11).astype("float32")/255
    ys=np.linspace(0,1,h,dtype=np.float32)
    blend=np.clip((ys-.48)/.26,0,1)
    blend=blend*blend*(3-2*blend)
    pale=np.array([235,221,188],np.float32)
    ocean=np.array([164,192,199],np.float32)
    fill=pale[None,None,:]*(1-blend[:,None,None])+ocean[None,None,:]*blend[:,None,None]
    fill=np.broadcast_to(fill,(h,w,3)).copy()
    # retain paper's original scan-like granularity
    rng=np.random.default_rng(45434)
    noise=cv2.GaussianBlur(rng.normal(0,1,(h,w)).astype("float32"),(0,0),.6)
    fill=np.clip(fill+noise[:,:,None]*2.3,0,255)
    combined=rgb*(1-strength[:,:,None])+fill*strength[:,:,None]
    return Image.fromarray(np.uint8(np.clip(combined,0,255)))

def ambient(path):
    sr=24000
    t=np.arange(DUR*sr)/sr
    rng=np.random.default_rng(45434)
    noise=rng.normal(0,1,len(t))
    # ambient slow surf, not a borrowed recording or a composition
    low=np.convolve(noise,np.ones(83)/83,"same")
    mid=np.convolve(noise,np.ones(11)/11,"same")
    swell=np.exp(-((t-2.7)/1.3)**2)*.48+np.exp(-((t-5.2)/1.7)**2)*.28
    score=(.17+.75*swell)*(low*.58+mid*.22)
    score+=.035*np.sin(2*np.pi*73.4*t)*np.exp(-((t-3)/1.7)**2)
    score+=.014*np.sin(2*np.pi*220*t)
    fade=np.minimum(1,np.minimum(t/.4,(DUR-t)/.85))
    audio=np.int16(np.clip(score*fade*2.2,-.8,.8)*32767)
    with wave.open(str(path),"wb") as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(sr)
        wav.writeframes(audio.tobytes())

def scene_at(t,original,plate,sprite,wall):
    p=reveal(t)
    frame=wall.copy()
    draw=ImageDraw.Draw(frame,"RGBA")
    draw.text((W//2,91),"ARTVISION · WOW LAB",font=font(28),fill=(216,187,141),anchor="mm")
    draw.text((W//2,149),"THE GREAT WAVE",font=font(40),fill=(239,233,214),anchor="mm")
    draw.text((W//2,196),"KATSUSHIKA HOKUSAI · c.1830",font=font(18),fill=(164,162,155),anchor="mm")
    # Painting is rendered initially exactly from source art, without fake content.
    # At p>0 the cutout leaves a reconstructed background within the print.
    paint=Image.blend(original,plate,p)
    draw.rounded_rectangle((PX-26,PY-22,PX+PW+32,PY+PH+35),radius=5,fill=(3,3,4,105))
    for offset,color,weight in [(22,(62,45,28),4),(17,(161,112,58),5),(11,(210,161,87),4),
                                (7,(93,65,39),3),(3,(221,185,116),3)]:
        draw.rectangle((PX-offset,PY-offset,PX+PW+offset,PY+PH+offset),
                       outline=(*color,255),width=weight)
    frame.paste(paint,(PX,PY))
    if p>.001:
        # The wave expands out of the print, crossing its top frame into the wall.
        # The triangular visual extraction is mask-based, not a true sculptural surface.
        mul=1+.27*p
        ow=int(PW*mul);oh=int(PH*mul)
        layer=sprite.resize((ow,oh),Image.Resampling.BICUBIC)
        anchorx=PX+PW*.47
        anchory=PY+PH*.75
        ox=int(anchorx+(PX-anchorx)*mul-26*p)
        oy=int(anchory+(PY-anchory)*mul-113*p)
        # cast strong contact shadow where wave physically overlaps frame/wall
        a=layer.getchannel("A")
        shadow=Image.new("RGBA",(W,H))
        dark=Image.new("RGBA",layer.size)
        dark.putalpha(a.point(lambda v:int(v*.56*p)))
        shadow.paste(dark,(ox+int(20*p),oy+int(27*p)))
        shadow=shadow.filter(__import__("PIL.ImageFilter",fromlist=["GaussianBlur"]).GaussianBlur(18))
        frame=Image.alpha_composite(frame,shadow)
        frame.alpha_composite(layer,(ox,oy))
    d=ImageDraw.Draw(frame)
    d.text((W//2,1032),"AN IMAGE BECOMES SPACE",font=font(24),
           fill=(232,220,201),anchor="mm")
    d.text((W//2,1093),"THE MET · JP1847 · PUBLIC DOMAIN",font=font(17),
           fill=(171,171,168),anchor="mm")
    d.text((W//2,1148),"CINEMATIC 2.5D  ·  ORIGINAL ARTWORK",font=font(16),
           fill=(202,172,121),anchor="mm")
    return frame.convert("RGB")

def main():
    manifest=json.loads((ASSETS/"SOURCE_MANIFEST.json").read_text())
    assert manifest["object_id"]==45434 and manifest["isPublicDomain"] is True
    original_bytes=(ASSETS/"HOKUSAI_MET_45434_ORIGINAL.jpg").read_bytes()
    assert hashlib.sha256(original_bytes).hexdigest()==manifest["sha256_original"]
    im=Image.open(ASSETS/"HOKUSAI_MET_45434_WORKING.png").convert("RGB")
    # Normalize to exact composition calibration used for wave outline.
    im=im.resize((1600,1076),Image.Resampling.LANCZOS)
    mask=cutout(im)
    background=clean_plate(im,mask)
    rgba=im.resize((PW,PH),Image.Resampling.LANCZOS).convert("RGBA")
    alpha=Image.fromarray(mask).resize((PW,PH),Image.Resampling.BICUBIC)
    rgba.putalpha(alpha)
    original=im.resize((PW,PH),Image.Resampling.LANCZOS)
    plate=background.resize((PW,PH),Image.Resampling.LANCZOS)
    yy,xx=np.mgrid[:H,:W]
    rg=np.random.default_rng(104)
    grain=rg.normal(0,1.0,(H,W))
    light=np.exp(-((xx-W*.48)/(W*.75))**2-((yy-H*.28)/(H*.8))**2)
    rgb=np.zeros((H,W,3),np.uint8)
    for c,(base,peak) in enumerate(((18,23),(20,25),(26,27))):
        rgb[:,:,c]=np.uint8(np.clip(base+peak*light+grain,0,255))
    wall=Image.fromarray(rgb,"RGB").convert("RGBA")
    amb=OUT/"ORIGINAL_SURF.wav"
    ambient(amb)
    video=OUT/"HOKUSAI_WOW_POP_OUT_ANDROID.mp4"
    cmd=["ffmpeg","-y","-nostdin","-loglevel","error",
         "-f","rawvideo","-pixel_format","rgb24","-video_size",f"{W}x{H}",
         "-framerate",str(FPS),"-i","pipe:0",
         "-i",str(amb),"-c:v","libx264","-preset","veryfast","-crf","22",
         "-pix_fmt","yuv420p","-c:a","aac","-b:a","96k",
         "-movflags","+faststart","-t",str(DUR),str(video)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        first=mid=None
        for idx in range(int(FPS*DUR)):
            t=idx/FPS
            frame=scene_at(t,original,plate,rgba,wall)
            if idx==0:first=frame.copy()
            if idx==int(FPS*3.5):mid=frame.copy()
            proc.stdin.write(np.asarray(frame).tobytes())
        proc.stdin.close()
        errors=proc.stderr.read().decode(errors="replace")
        if proc.wait()!=0:raise RuntimeError(errors[-1000:])
    except Exception:
        proc.kill();raise
    assert first is not None and mid is not None
    first.save(OUT/"01_BEFORE.jpg",quality=92)
    mid.save(OUT/"02_AFTER.jpg",quality=93)
    comparison=Image.new("RGB",(2*W,H))
    comparison.paste(first,(0,0));comparison.paste(mid,(W,0))
    comparison.save(OUT/"03_COMPARISON.jpg",quality=92)
    test=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error",
                         "-i",str(video),"-f","null","-"],
                         capture_output=True,text=True,timeout=110)
    if test.returncode:raise RuntimeError(test.stderr)
    details=json.loads(subprocess.check_output(["ffprobe","-v","error",
                        "-show_entries","stream=codec_name,width,height:format=duration",
                        "-of","json",str(video)],text=True))
    assert float(details["format"]["duration"])>=10.95
    assert any(s.get("codec_name")=="h264" for s in details["streams"])
    assert any(s.get("codec_name")=="aac" for s in details["streams"])
    report={"status":"needs_human_review","source":manifest["objectURL"],
            "license":"Met Open Access CC0","commercial_use":True,
            "object_id":45434,"render":"isolated 2.5D pop-out not true 3D",
            "is_auto_published_to_social":False,"paid_api_eur":0,
            "video_bytes":video.stat().st_size,"full_ffmpeg_decode":True,
            "size":[W,H],"duration":11,"frame_rate":FPS}
    (OUT/"QA.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    kit=OUT/"HOKUSAI_WOW_ANDROID_KIT.zip"
    with zipfile.ZipFile(kit,"w",zipfile.ZIP_DEFLATED) as z:
        for name in ["HOKUSAI_WOW_POP_OUT_ANDROID.mp4","01_BEFORE.jpg","02_AFTER.jpg","03_COMPARISON.jpg","QA.json"]:
            z.write(OUT/name,name)
    with zipfile.ZipFile(kit) as z:assert z.testzip() is None
    print(json.dumps({"mp4":str(video),"zip":str(kit),**report},ensure_ascii=False))

if __name__=="__main__":
    main()
