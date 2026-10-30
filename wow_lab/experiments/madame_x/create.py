#!/usr/bin/env python3
"""WOW LAB / Madame X / Met CC0. Independent portrait silhouette pop-out.

No changes to ArtVision presets, queues, archives or social publishing.
The portrait and object record must both pass source verification.
Technical tests do not equal approval of artistic quality.
"""
from __future__ import annotations
import hashlib,io,json,math,random,subprocess,sys,urllib.request,zipfile
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageOps,ImageDraw,ImageFont,ImageFilter
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from engine import original_sound
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"output";OUT.mkdir(exist_ok=True)
ID=12127;W,H=540,960;FPS=20;DUR=10
def req(url,max_bytes=16000000):
    if not url.startswith("https://"):raise ValueError("HTTPS only")
    request=urllib.request.Request(url,headers={"User-Agent":"ArtVision-WOWLAB-isolated/2.0","Accept":"*/*"})
    with urllib.request.urlopen(request,timeout=40) as f:b=f.read(max_bytes+1)
    if not b or len(b)>max_bytes:raise RuntimeError("Empty or oversize source")
    return b
def font(s):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if Path(p).is_file():return ImageFont.truetype(p,s)
    return ImageFont.load_default()
def ease(p):
    p=np.clip(p,0,1);return float(p*p*(3-2*p))
def time_envelope(t):
    if t<.45:return 0
    if t<2.65:return ease((t-.45)/2.2)
    if t<6.1:return 1.0
    if t<8.55:return 1-ease((t-6.1)/2.45)
    return 0
def get_source():
    url=f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{ID}"
    rec=json.loads(req(url,2000000))
    if rec.get("objectID")!=ID or not rec.get("isPublicDomain"):
        raise ValueError("Museum object or CC0 license unverified")
    if "Sargent" not in rec.get("artistDisplayName",""):
        raise ValueError("Wrong painter returned")
    if "Madame X" not in rec.get("title",""):
        raise ValueError("Wrong portrait returned")
    for u in [rec.get("primaryImage"),rec.get("primaryImageSmall")]:
        if not u or not u.startswith("https://"):continue
        try:
            raw=req(u,26000000)
            image=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
            if min(image.size)<700:continue
            image.thumbnail((1200,1600),Image.Resampling.LANCZOS)
            (OUT/"SOURCE_AUTHENTIC.jpg").write_bytes(raw)
            return image,rec,hashlib.sha256(raw).hexdigest(),u
        except Exception as e:
            print("Authentic source candidate unavailable: ",str(e)[:120])
    raise RuntimeError("No verified high-resolution museum image")
def segment(image):
    """Conservative portrait-specific region mask: body in center, dark background outside.
    GrabCut fails closed when the subject cannot be cleanly distinguished."""
    img=np.asarray(image)
    h,w=img.shape[:2]
    sw,sh=600,int(600*h/w)
    small=cv2.resize(img,(sw,sh),interpolation=cv2.INTER_AREA)
    # Portrait centered. High-confidence foreground = face, upper torso, illuminated arm.
    gc=np.full((sh,sw),cv2.GC_PR_BGD,np.uint8)
    cv2.rectangle(gc,(int(sw*.13),int(sh*.08)),(int(sw*.92),int(sh*.93)),cv2.GC_PR_FGD,-1)
    # outer 10% definitely museum background, not part of the sitter
    gc[:int(sh*.07),:]=cv2.GC_BGD
    gc[int(sh*.95):,:]=cv2.GC_BGD
    gc[:,:int(sw*.08)]=cv2.GC_BGD
    gc[:,int(sw*.95):]=cv2.GC_BGD
    # known body placements drawn from visible work structure, not blind pixel brightness
    seeds=np.zeros((sh,sw),np.uint8)
    for xx,yy,rx,ry in [(.51,.28,.09,.105),(.53,.42,.16,.10),(.60,.61,.22,.10),(.46,.70,.20,.14)]:
        cv2.ellipse(seeds,(int(sw*xx),int(sh*yy)),(int(sw*rx),int(sh*ry)),0,0,360,255,-1)
    gc[seeds>0]=cv2.GC_FGD
    bg=np.zeros((1,65),np.float64);fg=np.zeros((1,65),np.float64)
    cv2.grabCut(cv2.cvtColor(small,cv2.COLOR_RGB2BGR),gc,None,bg,fg,5,cv2.GC_INIT_WITH_MASK)
    m=np.uint8(np.isin(gc,[cv2.GC_FGD,cv2.GC_PR_FGD]))*255
    # Keep only component connected to face and torso seed.
    labels_count,labels,stats,centers=cv2.connectedComponentsWithStats(m,8)
    good=[]
    for i in range(1,labels_count):
        if stats[i,cv2.CC_STAT_AREA] > m.size*.002:
            good.append(i)
    if not good:raise RuntimeError("SEGMENTATION_REJECT: no foreground found")
    priority=max(good,key=lambda k:stats[k,cv2.CC_STAT_AREA])
    m=np.where(labels==priority,255,0).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))
    m=cv2.resize(m,(w,h),interpolation=cv2.INTER_LINEAR)
    m=cv2.GaussianBlur(m,(5,5),1.0)
    ratio=float((m>128).mean())
    if not .09<ratio<.68:raise RuntimeError(f"SEGMENTATION_REJECT: ratio {ratio:.2f}")
    x,y,bw,bh=cv2.boundingRect((m>120).astype(np.uint8))
    if bw<w*.18 or bh<h*.22:raise RuntimeError("SEGMENTATION_REJECT: no full portrait profile")
    rgba=np.dstack([img,m])
    comparison=Image.fromarray(img,"RGB")
    marks=np.array(comparison)
    marks[:,:,0]=np.uint8(np.clip(marks[:,:,0].astype(float)*.7+m*.27,0,255))
    marks[:,:,1]=np.uint8(marks[:,:,1].astype(float)*(.9-.35*m/255))
    Image.fromarray(marks).resize((500,int(500*h/w))).save(OUT/"MASK_AUDIT.jpg",quality=90)
    return Image.fromarray(rgba,"RGBA"),m,ratio
def paint_clean(im,m):
    """Neutral, conservative gallery fill under subject. Not claimed museum authenticity."""
    a=np.asarray(im).copy()
    h,w=a.shape[:2]
    mask=cv2.dilate((m>10).astype(np.uint8)*255,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(19,19)))
    # Inpainting black/neutral gallery field behind moving portrait.
    cleaned=cv2.inpaint(cv2.cvtColor(a,cv2.COLOR_RGB2BGR),mask,5,cv2.INPAINT_TELEA)
    cleaned=cv2.cvtColor(cleaned,cv2.COLOR_BGR2RGB)
    return Image.fromarray(cleaned)
def stage_canvas():
    y,x=np.mgrid[:H,:W]
    diffuse=np.exp(-((x-W*.47)/(W*.70))**2-((y-H*.35)/(H*.82))**2)
    wall=np.zeros((H,W,3),np.uint8)
    noise=np.random.default_rng(88).normal(0,.6,(H,W))
    for i,(b,p) in enumerate([(18,23),(18,23),(20,26)]):
        wall[:,:,i]=np.clip(b+p*diffuse+noise,0,255)
    return Image.fromarray(wall,"RGB").convert("RGBA")
def frame_at(t,art,clean,sprite,wall,ratio):
    p=time_envelope(t)
    stage=wall.copy()
    d=ImageDraw.Draw(stage)
    d.text((W//2,60),"ARTVISION  /  WOW LAB",font=font(16),fill=(213,183,132),anchor="mm")
    d.text((W//2,97),"MADAME X",font=font(39),fill=(245,231,213),anchor="mm")
    d.text((W//2,130),"JOHN SINGER SARGENT",font=font(17),fill=(193,185,168),anchor="mm")
    aw,ah=art.size
    targetw=350;targeth=int(targetw*ah/aw)
    if targeth>610:
        targeth=610;targetw=int(targeth*aw/ah)
    x=(W-targetw)//2; y=180
    bbox=(x,y,x+targetw,y+targeth)
    # Canvas shadow, neutral understated frame. Not an asserted historical museum frame.
    shadow=Image.new("RGBA",(W,H))
    sd=ImageDraw.Draw(shadow)
    sd.rectangle((x-18,y-18,x+targetw+25,y+targeth+27),fill=(0,0,0,150))
    stage=Image.alpha_composite(stage,shadow.filter(ImageFilter.GaussianBlur(17)))
    d=ImageDraw.Draw(stage)
    for off,col in [(15,(59,41,31)),(11,(142,105,69)),(7,(205,166,105)),(3,(92,70,47))]:
        d.rectangle((x-off,y-off,x+targetw+off,y+targeth+off),outline=col,width=3)
    src=Image.blend(art.resize((targetw,targeth),Image.Resampling.LANCZOS),
                    clean.resize((targetw,targeth),Image.Resampling.LANCZOS),p*.95)
    stage.paste(src,(x,y))
    if p>.001:
        # Separate figure, parallax and controlled tilt, not mere whole-painting zoom.
        s=1+.31*p
        w2=int(targetw*s);h2=int(targeth*s)
        figure=sprite.resize((w2,h2),Image.Resampling.BICUBIC)
        cx=x+targetw*.51;cy=y+targeth*.52
        ox=int(cx+(x-cx)*s-19*p+5*math.sin(t*.65)*p)
        oy=int(cy+(y-cy)*s-59*p)
        a=figure.getchannel("A")
        dark=Image.new("RGBA",figure.size,(0,0,0,0))
        dark.putalpha(a.point(lambda v:int(v*.65*p)))
        shade=Image.new("RGBA",(W,H))
        shade.paste(dark,(ox+int(23*p),oy+int(27*p)))
        stage=Image.alpha_composite(stage,shade.filter(ImageFilter.GaussianBlur(16)))
        stage.alpha_composite(figure,(ox,oy))
    d=ImageDraw.Draw(stage)
    d.text((W//2,875),"THE PORTRAIT CROSSES THE FRAME",font=font(16),
           fill=(222,212,193),anchor="mm")
    d.text((W//2,905),"MET · CC0 ORIGINAL · 2.5D TEST",font=font(12),
           fill=(171,163,148),anchor="mm")
    return stage.convert("RGB")
def main():
    im,rec,sha,url=get_source()
    foreground,m,ratio=segment(im)
    clean=paint_clean(im,m)
    wall=stage_canvas()
    audio=OUT/"ORIGINAL_AUDIO.wav"
    original_sound(audio,DUR,ID)
    dest=OUT/"MADAME_X_POP_OUT_WOW_LAB.mp4"
    cmd=["ffmpeg","-y","-nostdin","-hide_banner","-loglevel","error",
        "-f","rawvideo","-pixel_format","rgb24","-video_size",f"{W}x{H}",
        "-framerate",str(FPS),"-i","pipe:0","-i",str(audio),
        "-c:v","libx264","-preset","veryfast","-crf","23","-pix_fmt","yuv420p",
        "-c:a","aac","-b:a","96k","-movflags","+faststart","-t",str(DUR),str(dest)]
    process=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    stills=[]
    try:
        for i in range(FPS*DUR):
            fr=frame_at(i/FPS,im,clean,foreground,wall,ratio)
            if i in (0,4*FPS,9*FPS):stills.append(fr.copy())
            process.stdin.write(np.asarray(fr).tobytes())
        process.stdin.close()
        err=process.stderr.read().decode(errors="replace")
        if process.wait():raise RuntimeError(err[-1800:])
    except:
        process.kill();raise
    stills[0].save(OUT/"BEFORE.jpg",quality=92)
    stills[1].save(OUT/"PEAK.jpg",quality=92)
    beforeafter=Image.new("RGB",(W*2,H))
    beforeafter.paste(stills[0],(0,0));beforeafter.paste(stills[1],(W,0))
    beforeafter.save(OUT/"BEFORE_AFTER.jpg",quality=91)
    check=subprocess.run(["ffmpeg","-hide_banner","-loglevel","error",
       "-i",str(dest),"-f","null","-"],capture_output=True,text=True,timeout=130)
    if check.returncode:raise RuntimeError("Full video decode failed: "+check.stderr[-1000:])
    probe=json.loads(subprocess.check_output(["ffprobe","-v","error",
         "-show_entries","stream=codec_name,width,height:format=duration","-of","json",str(dest)],text=True))
    assert any(s.get("codec_name")=="h264" for s in probe["streams"])
    assert any(s.get("codec_name")=="aac" for s in probe["streams"])
    assert float(probe["format"]["duration"])>=9.9
    assert dest.stat().st_size>90000
    qa={"status":"needs_human_review","technical_ok":True,
        "original_artist":rec["artistDisplayName"],"original_title":rec["title"],
        "objectID":ID,"source_url":rec.get("objectURL"),"image_url":url,
        "source_sha256":sha,"license":"Met Open Access CC0",
        "foreground_ratio":ratio,"video_bytes":dest.stat().st_size,
        "duration_seconds":DUR,"resolution":[W,H],"fps":FPS,
        "effect":"2.5D silhouette pop-out, not true 3D",
        "frame":"fictional unverified gallery frame; not reproducing artwork's real frame",
        "paid_api_spend":0,"auto_social_publication":False}
    (OUT/"QA.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2))
    (OUT/"SOCIAL_DRAFT.txt").write_text(
        "Una presenza attraversa la cornice. Madame X, John Singer Sargent. "
        "Opera autentica The Metropolitan Museum of Art, Open Access/CC0. "
        "Esperimento WOW LAB 2.5D: la galleria e la cornice sono ricostruzioni illustrative. "
        "#ArtVision #MadameX #ArtHistory\n")
    zipname=OUT/"MADAME_X_ANDROID_KIT.zip"
    with zipfile.ZipFile(zipname,"w",zipfile.ZIP_DEFLATED) as z:
        for f in ["MADAME_X_POP_OUT_WOW_LAB.mp4","BEFORE.jpg","PEAK.jpg",
                  "BEFORE_AFTER.jpg","MASK_AUDIT.jpg","QA.json","SOCIAL_DRAFT.txt"]:
            z.write(OUT/f,f)
    with zipfile.ZipFile(zipname) as z:assert z.testzip() is None
    print(json.dumps({"result":"OK","mp4":str(dest),"zip":str(zipname),**qa},ensure_ascii=False))
if __name__=="__main__":
    main()
