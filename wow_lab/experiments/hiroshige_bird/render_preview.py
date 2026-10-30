#!/usr/bin/env python3
"""WOW LAB isolated CC0 print experiment — Hiroshige bluebird 36725.
Real MP4 + synth audio. Portrait-specific conservative silhouette.
Only writes inside wow_lab/experiments/hiroshige_bird/output/.
"""
import json, hashlib, math, subprocess, zipfile, wave
from pathlib import Path
import cv2, numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parent
AS=ROOT/"sources";O=ROOT/"output";O.mkdir(exist_ok=True)
PROV=AS/"SOURCE_PROVENANCE.json";SRC=AS/"HIROSHIGE_36725_WORK.png";RAW=AS/"HIROSHIGE_36725_ORIGINAL.jpg"
W,H,FPS,DUR=720,1280,24,11.5
PW,PH,PX,PY=440,585,140,290
OUTLINE=[(496,148),(515,141),(525,170),(530,220),(541,286),(550,337),(565,381),(583,407),(607,430),(626,484),(631,537),(639,581),(671,590),(692,604),(708,629),(712,662),(704,693),(675,718),(641,728),(610,724),(584,711),(557,703),(525,701),(497,687),(472,666),(452,645),(440,628),(415,613),(403,598),(410,576),(424,555),(439,527),(458,497),(478,464),(493,452),(498,435),(497,398),(492,344),(483,267),(485,188)]
CLEAN_OUTLINE=[(487,122),(519,122),(547,266),(574,252),(608,292),(626,366),(645,404),(666,463),(675,534),(709,566),(738,626),(739,709),(706,751),(537,748),(482,716),(419,660),(390,618),(395,556),(425,487),(463,438),(484,386),(474,277)]
FT="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FN="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def font(size,serif=True):return ImageFont.truetype(FT if serif else FN,size)
def ease(v):v=min(1.,max(0.,v));return v*v*(3-2*v)
def pval(t):
    if t<1.4:return 0.
    if t<3.55:return ease((t-1.4)/2.15)
    if t<7.:return 1.
    if t<9.5:return 1-ease((t-7.)/2.5)
    return 0.
def extract(im):
    raw=np.asarray(im.convert("RGB"));h,w=raw.shape[:2]
    assert (w,h)==(1203,1600),(w,h)
    rr=raw[:,:,0].astype("int16");gg=raw[:,:,1].astype("int16");bb=raw[:,:,2].astype("int16")
    area=np.zeros((h,w),np.uint8);cv2.fillPoly(area,[np.array(OUTLINE,np.int32)],255)
    blue=(bb-rr>7)&(bb-gg>-7)&(rr<150)&(gg<158)
    head=np.zeros_like(area);cv2.ellipse(head,(647,660),(72,72),0,0,360,255,-1)
    dark=(rr<125)&(gg<139)&(bb<145)&(bb-rr>-7)&(gg-rr>-13)&(head>0)
    ca=np.zeros_like(area);cv2.ellipse(ca,(577,654),(30,59),0,0,360,255,-1)
    cheek=(rr<200)&(rr>75)&(gg<142)&(bb<126)&(ca>0)
    m=np.uint8((blue|dark|cheek)&(area>0))*255
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))
    n,labels,stats,_=cv2.connectedComponentsWithStats(m,8);keep=np.zeros_like(m)
    for k in range(1,n):
        if stats[k,cv2.CC_STAT_AREA]>70:
            x,y,_,_,_=stats[k]
            if 375<x<730 and y<735:keep[labels==k]=255
    m=cv2.dilate(keep,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    m=cv2.GaussianBlur(m,(5,5),.8)
    ratio=float(np.mean(m>127))
    assert .020<ratio<.036, f"Mask failed ratio {ratio:.4f}"
    x,y,bw,bh=cv2.boundingRect(np.uint8(m>128))
    assert x>=440 and y>=130 and x+bw<730 and y+bh<740,"Mask leakage"
    assert np.count_nonzero(m[:,:385]>20)==0 and np.count_nonzero(m[:,760:]>20)==0
    alpha=np.dstack([raw,m])
    audit=raw.astype(np.float32);a=m/255.
    audit[:,:,0]=np.clip(audit[:,:,0]*(1-a*.2)+a*245*.2,0,255)
    audit[:,:,1]=audit[:,:,1]*(1-a*.5)
    audit[:,:,2]=audit[:,:,2]*(1-a*.2)
    Image.fromarray(audit.astype("uint8")).resize((480,638)).save(O/"MASK_AUDIT.jpg",quality=90)
    pad=6;lx=x-pad;ly=y-pad;rx=x+bw+pad;by=y+bh+pad
    Image.fromarray(m).save(O/"BIRD_MASK.png")
    return Image.fromarray(alpha[ly:by,lx:rx],"RGBA"),m,(lx,ly),ratio

def background(im,mask):
    a=np.asarray(im.convert("RGB"));h,w=a.shape[:2]
    hole=np.zeros((h,w),np.uint8);cv2.fillPoly(hole,[np.array(CLEAN_OUTLINE,np.int32)],255)
    hole=cv2.dilate(hole,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(11,11)))
    donor=a[820:1540,385:750].copy()
    if donor.shape[:2]!=(720,365):raise ValueError("Missing clean print texture")
    paper=np.tile(donor,(math.ceil(h/720),math.ceil(w/365),1))[:h,:w,:]
    paper=cv2.GaussianBlur(paper,(0,0),1.0)
    amt=cv2.GaussianBlur(hole.astype("float32")/255.,(0,0),4.5)
    cleaned=np.uint8(np.clip(a*(1-amt[:,:,None])+paper*amt[:,:,None],0,255))
    # These two woodcut strokes replace segments hidden underneath the bird.
    branch=[(430,686),(444,646),(465,601),(490,562),(524,525),(560,480),(603,432),(644,390)]
    stem=[(701,278),(704,380),(704,477),(706,577),(709,710),(708,830)]
    cv2.polylines(cleaned,[np.array(branch,np.int32)],False,(103,79,72),8,cv2.LINE_AA)
    cv2.polylines(cleaned,[np.array(branch,np.int32)],False,(141,111,93),2,cv2.LINE_AA)
    cv2.polylines(cleaned,[np.array(stem,np.int32)],False,(172,83,69),5,cv2.LINE_AA)
    cv2.polylines(cleaned,[np.array(stem,np.int32)],False,(205,124,98),2,cv2.LINE_AA)
    return Image.fromarray(cleaned)

def scene(im,clean,sprite,xy):
    origsize=im.size
    src=im.resize((PW,PH),Image.Resampling.LANCZOS)
    clean=clean.resize((PW,PH),Image.Resampling.LANCZOS)
    sc=PW/origsize[0]
    sprite=sprite.resize((int(sprite.width*sc),int(sprite.height*sc)),Image.Resampling.LANCZOS)
    sx=PX+int(xy[0]*sc);sy=PY+int(xy[1]*PH/origsize[1])
    yy,xx=np.mgrid[:H,:W];illum=np.exp(-((xx-W*.47)/(W*.69))**2-((yy-H*.35)/(H*.75))**2)
    grain=cv2.GaussianBlur(np.random.default_rng(36725).normal(0,1.8,(H,W)).astype("float32"),(0,0),.55)
    wall=np.zeros((H,W,3),np.uint8)
    for c,(base,peak) in enumerate([(16,18),(21,21),(26,25)]):
        wall[:,:,c]=np.clip(base+peak*illum+grain,0,255)
    return src,clean,sprite,sx,sy,Image.fromarray(wall,"RGB").convert("RGBA")

def frame(t,scene):
    orig,clean,sprite,sx,sy,wall=scene;p=pval(t)
    image=wall.copy();d=ImageDraw.Draw(image,"RGBA")
    d.text((W//2,74),"ARTVISION  ·  WOW LAB",font=font(24,False),anchor="mm",fill=(196,176,145,255))
    d.text((W//2,130),"THE BLUEBIRD",font=font(45),anchor="mm",fill=(243,236,222,255))
    d.text((W//2,173),"A PRINT COMES ALIVE",font=font(21,False),anchor="mm",fill=(176,186,194,255))
    shade=Image.new("RGBA",(W,H));sd=ImageDraw.Draw(shade,"RGBA")
    sd.rectangle((PX-22,PY-23,PX+PW+24,PY+PH+28),fill=(0,0,0,170))
    image=Image.alpha_composite(image,shade.filter(ImageFilter.GaussianBlur(19)))
    d=ImageDraw.Draw(image,"RGBA")
    for off,col,th in [(15,(64,49,37),4),(10,(153,117,73),4),(6,(219,196,149),3),(2,(98,81,61),2)]:
        d.rectangle((PX-off,PY-off,PX+PW+off,PY+PH+off),outline=(*col,255),width=th)
    image.paste(Image.blend(orig,clean,p),(PX,PY))
    if p>.001:
        q=1+1.5*p
        sw=max(1,int(sprite.width*q));sh=max(1,int(sprite.height*q))
        fg=sprite.resize((sw,sh),Image.Resampling.BICUBIC)
        ox=sx+int(165*p-7*math.sin(t*1.6)*p-10*(q-1))
        oy=sy-int(105*p+9*math.sin(t*.9)*p)-int(35*(q-1))
        dark=Image.new("RGBA",(sw,sh),(2,5,9,0))
        dark.putalpha(fg.getchannel("A").point(lambda v:int(v*.48*p)))
        shadow=Image.new("RGBA",(W,H));shadow.paste(dark,(ox+int(19*p),oy+int(24*p)))
        image=Image.alpha_composite(image,shadow.filter(ImageFilter.GaussianBlur(17)))
        image.alpha_composite(fg,(ox,oy))
    d=ImageDraw.Draw(image)
    d.text((W//2,1033),"ONE LITTLE BIRD. ONE IMPOSSIBLE MOMENT.",font=font(20),fill=(234,220,195),anchor="mm")
    d.text((W//2,1087),"HIROSHIGE  ·  ca. 1838",font=font(20,False),fill=(187,174,155),anchor="mm")
    d.text((W//2,1134),"THE MET   /   CC0 ORIGINAL   /   2.5D",font=font(17,False),fill=(145,164,179),anchor="mm")
    return image.convert("RGB")

def audio(path):
    sr=24000;t=np.arange(int(DUR*sr),dtype=np.float64)/sr
    rng=np.random.default_rng(36725);noise=rng.normal(0,1,len(t))
    air=np.convolve(noise,np.ones(15)/15.,mode="same")
    swell=.10+.8*np.exp(-((t-3.75)/1.5)**2)+.33*np.exp(-((t-7.3)/1.8)**2)
    track=.16*air*swell
    chirp=(np.sin(2*np.pi*(1010*t-12*t*t))*.006+np.sin(2*np.pi*(1360*t-14*t*t))*.005)
    track+=chirp*np.exp(-((t-5.1)/1.3)**2)
    track+=np.sin(2*np.pi*440*t)*.023*np.exp(-np.maximum(t-2.35,0)*.9)*(t>2.35)
    track+=np.sin(2*np.pi*659.25*t)*.013*np.exp(-np.maximum(t-2.39,0)*1.4)*(t>2.39)
    track=np.clip(track,-.8,.8)*np.minimum(1,np.minimum(t/.5,(DUR-t)/.65))
    with wave.open(str(path),"wb") as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr)
        f.writeframes((track*32767).astype("int16").tobytes())
def main():
    meta=json.loads(PROV.read_text())
    assert meta["artwork_id"]==36725 and meta["isPublicDomain"] and meta["license"]=="Met Open Access CC0"
    assert hashlib.sha256(RAW.read_bytes()).hexdigest()==meta["original_sha256"]
    im=Image.open(SRC).convert("RGB")
    fg,mask,xy,ratio=extract(im)
    scn=scene(im,background(im,mask),fg,xy)
    before=frame(.5,scn);peak=frame(5,scn);after=frame(10.3,scn)
    for im0,name in [(before,"BEFORE.jpg"),(peak,"WOW_MOMENT.jpg"),(after,"AFTER.jpg")]:
        im0.save(O/name,quality=92)
    pair=Image.new("RGB",(2*W,H))
    pair.paste(before,(0,0));pair.paste(peak,(W,0))
    pair.save(O/"BEFORE_AFTER.jpg",quality=91)
    snd=O/"SYNTH_AUDIO.wav";audio(snd)
    mp4=O/"HIROSHIGE_BLUEBIRD_WOW_ANDROID.mp4"
    cmd=["ffmpeg","-y","-nostdin","-hide_banner","-loglevel","error",
         "-f","rawvideo","-pixel_format","rgb24","-video_size",f"{W}x{H}",
         "-framerate",str(FPS),"-i","pipe:0","-i",str(snd),
         "-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","96k","-movflags","+faststart","-t",str(DUR),str(mp4)]
    process=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for i in range(int(FPS*DUR)):
            process.stdin.write(np.asarray(frame(i/FPS,scn)).tobytes())
        process.stdin.close()
        err=process.stderr.read().decode(errors="replace")
        if process.wait():raise RuntimeError(err[-600:])
    except BaseException:
        process.kill();raise
    test=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",str(mp4),"-f","null","-"],capture_output=True,text=True,timeout=110)
    if test.returncode:raise RuntimeError(test.stderr[-900:])
    probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries","stream=codec_name,width,height:format=duration","-of","json",str(mp4)],text=True))
    assert any(s.get("codec_name")=="h264" for s in probe["streams"])
    assert any(s.get("codec_name")=="aac" for s in probe["streams"])
    assert float(probe["format"]["duration"])>11.4 and mp4.stat().st_size>100000
    qa={"status":"needs_artistic_review","object_id":36725,"artist":meta["artist"],
        "artwork":meta["title"],"source_url":meta["object_url"],
        "source_sha256":meta["original_sha256"],"license":"Met Open Access CC0",
        "mask_ratio":ratio,"resolution":[W,H],"fps":FPS,"duration":DUR,
        "full_decode_ok":True,"h264":True,"aac":True,"is_real_3d":False,
        "effect":"2.5D bird-specific silhouette + paper background fill",
        "frame":"invented gallery presentation, not historical frame",
        "paid_api_spend":0,"auto_social_publish":False,"video_bytes":mp4.stat().st_size}
    (O/"QA.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2))
    (O/"SOCIAL_DRAFTS.txt").write_text("A bluebird leaps out of an 1838 Japanese print. Hiroshige, Weeping Cherry and Bluebird. Original CC0 print: Metropolitan Museum of Art. A 2.5D experiment; gallery setting is illustrative. #ArtVision #Hiroshige #WowLab\n")
    kit=O/"HIROSHIGE_BLUEBIRD_ANDROID_KIT.zip"
    with zipfile.ZipFile(kit,"w",zipfile.ZIP_DEFLATED) as z:
        for n in ["HIROSHIGE_BLUEBIRD_WOW_ANDROID.mp4","BEFORE.jpg","WOW_MOMENT.jpg",
                  "AFTER.jpg","BEFORE_AFTER.jpg","MASK_AUDIT.jpg","QA.json","SOCIAL_DRAFTS.txt"]:
            z.write(O/n,n)
    with zipfile.ZipFile(kit) as z:assert z.testzip() is None
    print(json.dumps({"video":str(mp4),"kit":str(kit),**qa}))
if __name__=="__main__":main()
