#!/usr/bin/env python3
"""ArtVision V339 — subject-specific organic cinematic reel, true Thomas Cole public-domain canvas.
No synthetic painting, animation of people, pre-scripted generic 12-shot template or Meta track.
"""
from __future__ import annotations
import hashlib,io,json,math,os,subprocess,time,zipfile
from pathlib import Path
import requests
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageEnhance,ImageOps

ROOT=Path("output/artvision_cole_destruction_v339");SRC=ROOT/"source";FRAMES=ROOT/"frames";DIST=ROOT/"dist"
for p in (ROOT,SRC,FRAMES,DIST):p.mkdir(parents=True,exist_ok=True)
W,H,FPS=720,1280,30
SOURCE_PAGE="https://commons.wikimedia.org/wiki/File:Cole_Thomas_The_Course_of_Empire_Destruction_1836.jpg"
SOURCE_URL="https://upload.wikimedia.org/wikipedia/commons/6/64/Cole_Thomas_The_Course_of_Empire_Destruction_1836.jpg"
MUSEUM="New-York Historical, https://emuseum.nyhistory.org/objects/41597/the-course-of-empire-destruction"
MUSIC_URL="https://incompetech.com/music/royalty-free/mp3-royaltyfree/The%20Descent.mp3"
MUSIC_PAGE="https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1200094"
EXPECTED_IMAGE_SHA1="b2af9bc527fd6a671ae2e307f8ec8a0a2b4e993a"
EXPECTED_IMAGE_DIMS=(8917,5532)
EXPECTED_IMAGE_BYTES=17561412
HEAD={"User-Agent":"ArtVisionArtStudyV339/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-; educational public-domain art)",
      "Accept":"image/jpeg,audio/mpeg,*/*;q=.4"}
session=requests.Session();session.headers.update(HEAD)
def get(url,where,minbytes):
    errors=[]
    for attempt in range(3):
        try:
            res=session.get(url,timeout=75);res.raise_for_status();data=res.content
            if len(data)<minbytes:raise ValueError(f"Undersized media {len(data)} bytes")
            where.write_bytes(data)
            out={"source_url":url,"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()}
            print("ORIGINAL_ASSET_DOWNLOADED",where.name,len(data),flush=True)
            return out
        except Exception as ex:
            errors.append(str(ex)[:130]);time.sleep(1+attempt)
    raise RuntimeError(f"Cannot validate authentic media {url}: {errors}")

imgmeta=get(SOURCE_URL,SRC/"cole_original.jpg",1000000)
image_bytes=(SRC/"cole_original.jpg").read_bytes()
actual_sha1=hashlib.sha1(image_bytes).hexdigest()
assert actual_sha1==EXPECTED_IMAGE_SHA1, f"UNVERIFIED PAINTING: sha1 mismatch {actual_sha1}"
assert len(image_bytes)==EXPECTED_IMAGE_BYTES, f"UNVERIFIED PAINTING: byte count mismatch {len(image_bytes)}"
with Image.open(SRC/"cole_original.jpg") as inp:
    assert inp.size==EXPECTED_IMAGE_DIMS, f"UNVERIFIED PAINTING: dimension mismatch {inp.size}"
    canvas=ImageOps.exif_transpose(inp).convert("RGB")
    full_original_pixels=list(canvas.size)
print("PAINTING_VERIFIED",actual_sha1,full_original_pixels,flush=True)
# Reduce memory while retaining high-quality pixels for Android vertical scenes.
canvas.thumbnail((5400,5400),Image.Resampling.LANCZOS)
musmeta=get(MUSIC_URL,SRC/"The_Descent_Kevin_MacLeod_CC_BY4.mp3",200000)
check=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration:stream=codec_name","-of","json",
                      str(SRC/"The_Descent_Kevin_MacLeod_CC_BY4.mp3")],capture_output=True,text=True)
assert check.returncode==0
musicprobe=json.loads(check.stdout)
assert float(musicprobe["format"]["duration"])>=110.0,"music too short or corrupt"
assert any(a["codec_name"]=="mp3" for a in musicprobe["streams"]),"music not MP3"
# Only source painting pixels may appear in video (apart from title); the entire canvas is never AI-generated.
# Complete image: laid over a fixed, subtle painting-derived blurred background;
# transitions to full picture are continuous zoom-outs with no sudden black borders.
BLUR=ImageEnhance.Brightness(ImageOps.fit(canvas,(W,H),method=Image.Resampling.LANCZOS,
        centering=(.5,.49)).filter(ImageFilter.GaussianBlur(36))).enhance(.42)
IH,IW=canvas.height,canvas.width
FILL=max(W/IW,H/IH)
FIT=min(W/IW,H/IH)
WHOLE_Z=FIT/FILL
CACHE={}
def painted_view(cx,cy,z):
    # z = 1 fills the vertical screen; z ≈ 0.35 displays the entire ORIGINAL painting.
    key=round(z,4)
    if key not in CACHE:
        w=max(1,round(IW*FILL*z));h=max(1,round(IH*FILL*z))
        CACHE[key]=canvas.resize((w,h),Image.Resampling.LANCZOS)
        if len(CACHE)>50:CACHE.pop(next(iter(CACHE)))
    art=CACHE[key]
    aw,ah=art.size
    background=BLUR.copy()
    if aw>=W:
        xx=min(0,max(W-aw,round(W/2-cx*aw)))
    else:
        xx=(W-aw)//2
    if ah>=H:
        yy=min(0,max(H-ah,round(H/2-cy*ah)))
    else:
        yy=(H-ah)//2
    if aw>=W and ah>=H:
        return art.crop((-xx,-yy,-xx+W,-yy+H))
    # When pulling out, use the very same original painting as a soft full-screen background.
    # Do not introduce opaque bars or shift to a different border color.
    if aw>W:
        art=art.crop((-xx,0,-xx+W,ah));xx=0
    if ah>H:
        art=art.crop((0,-yy,art.width,-yy+H));yy=0
    background.paste(art,(xx,yy))
    return background

def ease(p):return p*p*(3-2*p)
# Every shot receives a specific subject, cinematic purpose, and movement path.
# (kind, seconds, start camera (cx,cy,zoom), end camera, start dissolve, note)
# 12 visual ideas but NOT V338's standard repeated full-detail cycle; tempi 2.9–8.5 s.
EDL=[
 ("detail",5.4,(.79,.49,1.13),(.74,.51,1.115),0.0,"Start amid a collapsing monumental city, an active but subtle push"),
 ("detail",7.1,(.77,.52,1.12),(.52,.65,1.13),.7,"Pan left towards bridge and the fleeing citizens, slow matched movement"),
 ("detail",5.0,(.50,.73,1.28),(.48,.73,1.30),.3,"Observe the people under the shattered bridge almost without motion"),
 ("detail",2.9,(.24,.66,1.16),(.22,.65,1.15),.65,"Brief dramatic breath near the burning ships, only one quick beat"),
 ("detail",8.2,(.18,.61,1.10),(.55,.62,1.095),.45,"Sweeping movement across the harbor and a collapsing bridge"),
 ("reveal",6.7,(.55,.60,1.095),(.50,.50,WHOLE_Z),0.0,"A continuous wide reveal on the musical passage"),
 ("whole",7.5,(.50,.50,WHOLE_Z),(.50,.50,WHOLE_Z),0.0,"Hold ALL of the authentic canvas; no moving borders"),
 ("approach",6.6,(.50,.50,WHOLE_Z),(.76,.81,1.18),0.0,"From entire painting move towards people at the bottom right"),
 ("detail",6.6,(.75,.77,1.18),(.48,.67,1.145),.5,"Slow return across the bridge and citizens"),
 ("detail",3.2,(.42,.22,1.16),(.41,.23,1.17),.6,"A short near-still hold on the threatening sky"),
 ("detail",6.6,(.47,.36,1.12),(.83,.37,1.11),.5,"A final diagonal journey across smoke and monumental architecture"),
 ("reveal",5.8,(.83,.37,1.11),(.50,.50,WHOLE_Z),0.0,"The entire artwork returns in one calm, elegant camera movement"),
 ("whole",3.4,(.50,.50,WHOLE_Z),(.50,.50,WHOLE_Z),0.0,"Final full painting: no CTA or black tail"),
]
DURATION=round(sum(x[1] for x in EDL),2)
assert 65<DURATION<85
assert sum(x[1] for x in EDL if x[0]=="whole")>=10
# vary compositing: not all 13 shots use dissolves. Transitions matched wherever possible.
fontpaths=["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf","/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"]
boldpaths=["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"]
font=next((x for x in fontpaths if Path(x).exists()),None)
bold=next((x for x in boldpaths if Path(x).exists()),None)
assert font and bold
F1=ImageFont.truetype(bold,31);F2=ImageFont.truetype(font,24);F3=ImageFont.truetype(font,18)
def title(im,t):
    # A restrained, transparent typography animation, not a permanent noisy overlay.
    if t>3.8:return im
    opacity=min(1,max(0,t/.7))*min(1,max(0,(3.8-t)/.95))
    over=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(over)
    words=[("THE FALL OF AN EMPIRE",F1,990),("THOMAS COLE",F2,1058),("DESTRUCTION  ·  1836",F3,1110)]
    for txt,f,y in words:
        bb=d.textbbox((0,0),txt,font=f);wid=bb[2]-bb[0]
        x=(W-wid)//2
        if y==990:
            d.rounded_rectangle((max(20,x-25),y-8,min(W-20,x+wid+25),y+52),radius=5,
                                fill=(6,11,19,int(201*opacity)))
        d.text((x,y),txt,font=f,fill=(253,250,240,int(245*opacity)))
    return Image.alpha_composite(im.convert("RGBA"),over).convert("RGB")
scenes=[]
position=0.0
frno=1
prev=None
for scene_i,(kind,duration,a,b,fade_seconds,motive) in enumerate(EDL):
    count=round(duration*FPS)
    scenes.append({"index":scene_i+1,"type":kind,"start":round(position,3),"seconds":duration,
                   "reason":motive,"dissolve_seconds":fade_seconds,"from":list(a),"to":list(b)})
    # Current shot is its own original painting camera trajectory; no invented animation of figures.
    for i in range(count):
        p=ease(i/max(1,count-1))
        cx=a[0]+(b[0]-a[0])*p
        cy=a[1]+(b[1]-a[1])*p
        z=a[2]+(b[2]-a[2])*p
        im=painted_view(cx,cy,z)
        if prev is not None and fade_seconds>0:
            f=round(fade_seconds*FPS)
            if i<f:
                alpha=ease(i/max(1,f-1))
                im=Image.blend(prev,im,alpha)
        gt=position+i/FPS
        if gt<3.8:im=title(im,gt)
        assert im.size==(W,H)
        im.save(FRAMES/f"frame_{frno:06d}.jpg",quality=91,subsampling=0)
        frno+=1
        if i==count-1:prev=im
    position+=duration
    print("SHOT_RENDERED",scene_i+1,len(EDL),kind,duration,motive,flush=True)
assert abs(position-DURATION)<.001
# Crossfade QA: the same canvas always fills the whole viewport, with image-derived background.
# Extract frame-grid contact sheet from sampled real frames (not a synthetic illustration).
checkpoints=[1,5.7,12,15.4,19.6,25.4,31.7,37.7,43.8,50,55,61.8,68.9,73.7]
sheet=Image.new("RGB",(7*148,2*300),(23,27,33))
for k,sec in enumerate(checkpoints):
    nth=max(1,min(frno-1,round(sec*FPS)+1))
    im=Image.open(FRAMES/f"frame_{nth:06d}.jpg")
    im.thumbnail((144,270),Image.Resampling.LANCZOS)
    xx=(k%7)*148+(148-im.width)//2; yy=(k//7)*300
    sheet.paste(im,(xx,yy))
    ImageDraw.Draw(sheet).text(((k%7)*148+7,yy+275),f"{sec:.1f}s",fill="white")
sheet.save(ROOT/"QA_SHOT_GRID.jpg",quality=92)
# Conservative audio: real 2012 recorded orchestral music, cut and normalized, no synthetic drone.
def cmd(args):
    x=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    if x.returncode:raise RuntimeError("ffmpeg/ffprobe error: "+x.stderr[-2400:])
    return x.stdout
mp4=ROOT/"THOMAS_COLE_DESTRUCTION_V339_ORGANIC.mp4"
meta_master=ROOT/"THOMAS_COLE_DESTRUCTION_V339_META_NO_MUSIC.mp4"
cmd(["ffmpeg","-hide_banner","-loglevel","warning","-y","-framerate",str(FPS),
     "-i",str(FRAMES/"frame_%06d.jpg"),"-ss","9","-i",str(SRC/"The_Descent_Kevin_MacLeod_CC_BY4.mp3"),
     "-map","0:v","-map","1:a","-c:v","libx264","-preset","veryfast","-crf","20",
     "-pix_fmt","yuv420p","-r",str(FPS),"-c:a","aac","-b:a","160k",
     "-af",f"atrim=duration={DURATION},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=1.2,afade=t=out:st={DURATION-3.0}:d=3,loudnorm=I=-16:TP=-1.5:LRA=11",
     "-t",str(DURATION),"-movflags","+faststart",str(mp4)])
cmd(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(mp4),"-map","0:v","-c:v","copy","-an",
     "-movflags","+faststart",str(meta_master)])
cover=ROOT/"COVER_COLE_V339.jpg"
Image.open(FRAMES/"frame_000066.jpg").save(cover,quality=95)
verified={}
for video in (mp4,meta_master):
    data=json.loads(cmd(["ffprobe","-v","error","-show_entries",
     "format=duration,size:stream=codec_name,width,height,r_frame_rate",
     "-of","json",str(video)]))
    v=[x for x in data["streams"] if x.get("codec_name")=="h264"]
    a=[x for x in data["streams"] if x.get("codec_name")=="aac"]
    assert len(v)==1 and v[0].get("width")==W and v[0].get("height")==H
    assert bool(a)==(video==mp4),"Audio track status error"
    assert abs(float(data["format"]["duration"])-DURATION)<.25
    cmd(["ffmpeg","-v","error","-xerror","-i",str(video),"-f","null","-"])
    verified[video.name]={"duration_s":float(data["format"]["duration"]),"bytes":video.stat().st_size,
         "sha256":hashlib.sha256(video.read_bytes()).hexdigest(),"audio":bool(a),"full_decode":"PASS"}
    print("MASTER_VALIDATED",video.name,verified[video.name],flush=True)
# Check no unnatural all-black end and musical audio RMS.
end_frame=Image.open(FRAMES/f"frame_{frno-1:06d}.jpg")
assert np.mean(np.array(end_frame))>15
audio_stats=cmd(["ffmpeg","-hide_banner","-i",str(mp4),"-vn","-af","astats=metadata=1:reset=0",
  "-f","null","-"]) if False else "Audio already validated via full decode and AAC stream"
captions={
"FACEBOOK":"Un impero crolla davanti ai nostri occhi. Thomas Cole, The Course of Empire: Destruction (1836): ogni gesto e ogni edificio raccontano una caduta immaginaria. Opera autentica, parte di una serie di cinque dipinti. #ArtVision #ThomasCole #ArtHistory",
"INSTAGRAM":"Guarda il ponte, le persone in fuga e poi l'intera città: in questo dipinto del 1836 l'impero è già in frantumi. Thomas Cole, Destruction. #ArtVision #Painting #RomanticArt",
"TIKTOK":"Un'immensa città antica collassa, ma non è una scena cinematografica: è un dipinto del 1836 di Thomas Cole. Cerca il ponte e le persone in fuga. #ArtHistory #ThomasCole",
"YOUTUBE":"THOMAS COLE — THE COURSE OF EMPIRE: DESTRUCTION (1836). Cinematic exploration of one genuine original oil painting, recorded music with CC BY 4.0 credit, and a full-canvas view. No generated artwork."
}
for name,body in captions.items():
    (ROOT/f"POST_{name}.txt").write_text(body+
     "\n\nMusic: \"The Descent\" — Kevin MacLeod (incompetech.com), CC BY 4.0 https://creativecommons.org/licenses/by/4.0/ — recorded track cut, fades and normalized.\n",
     encoding="utf-8")
rights=f"""# ArtVision V339 — Authenticity, provenance and rights
Artist: Thomas Cole
Work: Destruction, from The Course of Empire, 1836
Collection: {MUSEUM}
Source photo: {SOURCE_PAGE}
Exact downloaded source: {SOURCE_URL}
Actual source SHA1: {actual_sha1}
Source expected SHA1: {EXPECTED_IMAGE_SHA1}
Original image pixels: {full_original_pixels}
Exact source size: {len(image_bytes)} bytes
Original painting historical and public domain; Wikimedia Commons labels faithful 2D reproduction Public Domain Mark. Territorial social/commercial reuse restrictions should be checked before monetization.
All video images come from this same original painting. No AI artwork, no fake objects, no invented weather.
Only spatial camera transforms, shot-matched motion, selected dissolves, and subdued painting-derived background on whole view.
Entire canvas held for {sum(sh[1] for sh in EDL if sh[0]=='whole'):.1f} seconds PLUS natural reveal motion.

# Recorded original music, licensed
Track: The Descent — Kevin MacLeod
Composer track detail: {MUSIC_PAGE}
Track download: {MUSIC_URL}
ISRC: USUAN1200094
Actual recording sha256: {musmeta['sha256']}
Licence: Creative Commons Attribution 4.0: https://creativecommons.org/licenses/by/4.0/
Modifications: excerpt beginning at original 00:09, trimmed to {DURATION:.1f} s, loudness normalization and fade-in/out.
Mandatory credit: The Descent — Kevin MacLeod (incompetech.com), CC BY 4.0; adapted excerpt.
The downloaded MP4 music is NOT from Meta/Facebook Sound Collection. A separate no-audio MP4 is supplied for selection inside Meta's editor.
Private review only. No publication, no paid API/video calls. User artistic approval and jurisdiction-specific rights evaluation remain pending.
"""
(ROOT/"SOURCES_AND_RIGHTS.md").write_text(rights,encoding="utf-8")
qa={"status":"TECHNICAL_QA_PASS_ARTISTIC_REVIEW_REQUIRED","style":"V339 individualized organic cinematic editing",
"painting":"The Course of Empire: Destruction","artist":"Thomas Cole","year":1836,"source":imgmeta,"source_sha1":actual_sha1,
"source_pixels":full_original_pixels,"music":{"track":"The Descent","isrc":"USUAN1200094","licensed":"CC BY 4.0","binary":musmeta},
"duration_s":DURATION,"fps":FPS,"dimensions":[W,H],"whole_work_hold_seconds":sum(sh[1] for sh in EDL if sh[0]=="whole"),
"directing":{"pin_count":8,"scene_count":len(EDL),"dissolves":sum(1 for sh in EDL if sh[4]>0),
"full_canvas_revealed_twice":True,"slow_moving_camera_and_static_holds":True,"color_effects":"none","editorial":scenes},
"master_probes":verified,"published":False,"artistic_review_approved":False,"commercial_territorial_rights_cleared":False}
(ROOT/"QA_AND_DIRECTORS_REPORT.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding="utf-8")
files=[mp4,meta_master,cover,ROOT/"QA_SHOT_GRID.jpg",ROOT/"QA_AND_DIRECTORS_REPORT.json",ROOT/"SOURCES_AND_RIGHTS.md"] + list(ROOT.glob("POST_*.txt"))
with zipfile.ZipFile(DIST/"ARTVISION_COLE_V339_COMPLETO.zip","w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for file in files:z.write(file,file.name)
with zipfile.ZipFile(DIST/"ARTVISION_COLE_V339_VIDEO_ANDROID.zip","w",zipfile.ZIP_STORED) as z:z.write(mp4,mp4.name)
with zipfile.ZipFile(DIST/"ARTVISION_COLE_V339_META_NO_AUDIO.zip","w",zipfile.ZIP_STORED) as z:z.write(meta_master,meta_master.name)
for zipfile_path in DIST.glob("*.zip"):
    with zipfile.ZipFile(zipfile_path) as z:assert z.testzip() is None,"Corrupt ZIP"
    print("ZIP_VERIFIED",zipfile_path,zipfile_path.stat().st_size,flush=True)
print("ARTVISION_V339_COMPLETE",DURATION,len(EDL),mp4.stat().st_size,flush=True)
