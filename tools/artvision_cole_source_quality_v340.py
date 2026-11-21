#!/usr/bin/env python3
"""V340 original-source-quality delivery: real UHD 8K portrait from the authentic artwork,
plus a native 4K H.264 mobile version. No upscaling of the old 720p video.
"""
from __future__ import annotations
import argparse,hashlib,json,math,os,subprocess,time,zipfile
from pathlib import Path
import cv2,numpy as np,requests
from PIL import Image,ImageDraw,ImageFont

ap=argparse.ArgumentParser()
ap.add_argument("--mode",choices=["8k","4k"],required=True)
ap.add_argument("--preview-seconds",type=int,default=0)
args=ap.parse_args()

ART="https://upload.wikimedia.org/wikipedia/commons/6/64/Cole_Thomas_The_Course_of_Empire_Destruction_1836.jpg"
ART_SHA256="070c09253e7ff70639817a8790d10ea67b8de0f54f6020625e7b74b1be200cb9"
ART_BYTES=17561412
ART_DIM=(8917,5532)
MUSIC="https://incompetech.com/music/royalty-free/mp3-royaltyfree/The%20Descent.mp3"
MUSIC_SHA256="f097d51700b970efffc62499473ea3a31e09aad4172e787978bc9c2a644d53a2"
ROOT=Path("output/artvision_cole_v340")/args.mode
ASSETS=ROOT/"source";DIST=ROOT/"dist";ROOT.mkdir(parents=True,exist_ok=True);ASSETS.mkdir(exist_ok=True);DIST.mkdir(exist_ok=True)
W,H=(4320,7680) if args.mode=="8k" else (2160,3840)
FPS=30
SEQS=[
("detail",5.4,(.79,.49,1.13),(.74,.51,1.115),0.0,"Start among the ruins"),
("detail",7.1,(.77,.52,1.12),(.52,.65,1.13),.7,"Move toward bridge and fleeing citizens"),
("detail",5.0,(.50,.73,1.28),(.48,.73,1.30),.3,"Pause among the people"),
("detail",2.9,(.24,.66,1.16),(.22,.65,1.15),.65,"Short breath near burning ships"),
("detail",8.2,(.18,.61,1.10),(.55,.62,1.095),.45,"Long harbor traversal"),
("reveal",6.7,(.55,.60,1.095),(.50,.50,None),0.0,"Zoom out revealing full true canvas"),
("whole",7.5,(.50,.50,None),(.50,.50,None),0.0,"Whole painting held"),
("approach",6.6,(.50,.50,None),(.76,.81,1.18),0.0,"Approach citizens again"),
("detail",6.6,(.75,.77,1.18),(.48,.67,1.145),.5,"Move back along bridge"),
("detail",3.2,(.42,.22,1.16),(.41,.23,1.17),.6,"Moment of stillness in the sky"),
("detail",6.6,(.47,.36,1.12),(.83,.37,1.11),.5,"Final architectural movement"),
("reveal",5.8,(.83,.37,1.11),(.50,.50,None),0.0,"Return to original entire canvas"),
("whole",3.4,(.50,.50,None),(.50,.50,None),0.0,"Uninterrupted full painting end"),
]
FULL_DURATION=sum(s[1] for s in SEQS)
assert abs(FULL_DURATION-75)<.001
stop=FULL_DURATION if args.preview_seconds==0 else min(args.preview_seconds,FULL_DURATION)
N_TOTAL=round(stop*FPS)
assert stop>0
UA={"User-Agent":"ArtVisionQualityV340/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-)"}
def fetch(url,name,checksum,minimum_bytes):
    path=ASSETS/name
    if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==checksum:
        return path
    errors=[]
    for attempt in range(3):
        try:
            r=requests.get(url,headers=UA,timeout=90);r.raise_for_status()
            b=r.content
            assert len(b)>=minimum_bytes
            assert hashlib.sha256(b).hexdigest()==checksum,"Source SHA256 mismatch"
            path.write_bytes(b)
            print("VERIFIED_SOURCE",name,len(b),flush=True)
            return path
        except Exception as e:
            errors.append(str(e)[:180]);time.sleep(attempt+1)
    raise RuntimeError("Authentic source unavailable or altered; do not fake an 8K rendering: "+str(errors))
art=fetch(ART,"THOMAS_COLE_ORIGINAL.jpg",ART_SHA256,ART_BYTES)
assert art.stat().st_size==ART_BYTES
score=fetch(MUSIC,"THE_DESCENT_LICENSED_MP3.mp3",MUSIC_SHA256,200000)
src=cv2.imread(str(art),cv2.IMREAD_COLOR)
assert src is not None and (src.shape[1],src.shape[0])==ART_DIM
oh,ow=src.shape[:2]
# Gentle, source-constrained local contrast: sharpen color-luminance only, strength <=5%.
# No hallucinated brushwork, generative upscaling, fake objects or recoloring of the painting.
soft=cv2.GaussianBlur(src,(0,0),.8)
src=cv2.addWeighted(src,1.035,soft,-.035,0)
del soft
# Every frame is spatially re-rendered from the >8,000-pixel original; never from the 720p MP4.
def background():
    ratio=W/H
    crop_w=round(oh*ratio)
    crop=src[:,(ow-crop_w)//2:(ow+crop_w)//2]
    backing=cv2.resize(crop,(W,H),interpolation=cv2.INTER_AREA)
    backing=cv2.GaussianBlur(backing,(0,0),max(24,int(W/48)))
    return np.clip(backing.astype(np.float32)*.48,0,255).astype(np.uint8)
BG=background()
fill=max(W/ow,H/oh)
whole=min(W/ow,H/oh)/fill
SEQS=[(kind,duration,tuple(whole if v is None else v for v in a),
        tuple(whole if v is None else v for v in b),fade,why) for kind,duration,a,b,fade,why in SEQS]
def smooth(p):
    p=min(1.,max(0.,p))
    return p*p*(3-2*p)
def view(v):
    cx,cy,z=v
    scale=fill*z
    sw=ow*scale;sh=oh*scale
    x=W/2-cx*sw
    y=H/2-cy*sh
    if sw>=W:x=min(0,max(W-sw,x))
    else:x=(W-sw)/2
    if sh>=H:y=min(0,max(H-sh,y))
    else:y=(H-sh)/2
    mat=np.asarray([[scale,0,x],[0,scale,y]],np.float32)
    canvas=BG.copy()
    cv2.warpAffine(src,mat,(W,H),dst=canvas,flags=cv2.INTER_CUBIC,
                   borderMode=cv2.BORDER_TRANSPARENT)
    return canvas
# Work in original-resolution coordinates. Pure typography over the authentic painting.
font_dir="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold_dir="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
T_SCALE=W/720
TITLE_F=ImageFont.truetype(bold_dir,round(31*T_SCALE))
SMALL_F=ImageFont.truetype(font_dir,round(23*T_SCALE))
SUB_F=ImageFont.truetype(font_dir,round(18*T_SCALE))
def title(im,seconds):
    if seconds>=3.8:return im
    opacity=min(1,seconds/.75)*min(1,(3.8-seconds)/.95)
    if opacity<=0:return im
    # downsample only the small title area for efficient text rendering, not the painting
    base=Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB))
    overlay=Image.new("RGBA",(W,H),(0,0,0,0))
    d=ImageDraw.Draw(overlay)
    data=[("THE FALL OF AN EMPIRE",TITLE_F,round(990*T_SCALE)),
          ("THOMAS COLE",SMALL_F,round(1058*T_SCALE)),
          ("DESTRUCTION · 1836",SUB_F,round(1110*T_SCALE))]
    for textline,font,y in data:
        box=d.textbbox((0,0),textline,font=font)
        span=box[2]-box[0];x=round((W-span)/2)
        if textline=="THE FALL OF AN EMPIRE":
            d.rounded_rectangle((x-round(24*T_SCALE),y-round(7*T_SCALE),
                x+span+round(24*T_SCALE),y+round(51*T_SCALE)),radius=round(5*T_SCALE),
                fill=(4,10,18,round(190*opacity)))
        d.text((x,y),textline,font=font,fill=(254,251,241,round(246*opacity)))
    base=Image.alpha_composite(base.convert("RGBA"),overlay)
    return cv2.cvtColor(np.asarray(base.convert("RGB")),cv2.COLOR_RGB2BGR)
def blend(a,b,p):
    return cv2.addWeighted(a,1-p,b,p,0)
def interp(a,b,p):
    return tuple(a[k]+(b[k]-a[k])*p for k in range(3))
# Save representative frames without saving thousands of large PNG/JPEG files.
samples=[1.0,7.1,14.0,20.0,29.8,35.3,42.0,48.1,56.0,62.8,69.4,74.1]
previews={}
video=ROOT/("THOMAS_COLE_V340_8K_HEVC.mp4" if args.mode=="8k" else "THOMAS_COLE_V340_4K_ANDROID.mp4")
logfile=ROOT/"encoding.log"
if args.mode=="8k":
    cod=["-c:v","libx265","-preset","ultrafast","-crf","21","-pix_fmt","yuv420p",
         "-tag:v","hvc1","-x265-params","log-level=error"]
else:
    cod=["-c:v","libx264","-preset","veryfast","-crf","17","-pix_fmt","yuv420p",
         "-profile:v","high"]
cmd=["ffmpeg","-hide_banner","-nostdin","-loglevel","warning","-y",
     "-f","rawvideo","-pixel_format","bgr24","-video_size",f"{W}x{H}",
     "-framerate",str(FPS),"-i","pipe:0",
     "-ss","9","-i",str(score),
     "-map","0:v:0","-map","1:a:0",*cod,
     "-c:a","aac","-b:a","192k","-af",
     f"atrim=duration={stop},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=1.2,afade=t=out:st={max(0,stop-3)}:d=3,loudnorm=I=-16:TP=-1.5:LRA=11",
     "-movflags","+faststart","-t",str(stop),str(video)]
start=time.monotonic();n=0;timeline=0.0;last=None
with logfile.open("wb") as logs:
    encoder=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=logs,
                             bufsize=0)
    try:
        for k,(kind,duration,a,b,dissolve,why) in enumerate(SEQS):
            count=round(duration*FPS)
            print("SCENE_START",k+1,len(SEQS),kind,round(timeline,2),duration,flush=True)
            frame_fade=round(dissolve*FPS)
            for i in range(count):
                if n>=N_TOTAL:break
                p=smooth(i/max(1,count-1))
                v=interp(a,b,p)
                frame=view(v)
                if last is not None and frame_fade>0 and i<frame_fade:
                    # Cut-specific restrained visual blending, never blanket dissolves.
                    frame=blend(last,frame,smooth(i/max(1,frame_fade-1)))
                if n/FPS<3.8:frame=title(frame,n/FPS)
                if any(abs(n/FPS-t)<1/FPS/2 for t in samples):
                    previews[round(n/FPS,1)]=cv2.resize(frame,(540,960),interpolation=cv2.INTER_AREA)
                try:encoder.stdin.write(frame.tobytes())
                except BrokenPipeError:raise RuntimeError("Encoder stopped before all frames; see "+str(logfile))
                last=frame if i==count-1 else last
                n+=1
            timeline+=duration
            print("SCENE_DONE",k+1,"FRAMES",n,"ELAPSED",round(time.monotonic()-start,1),flush=True)
            if n>=N_TOTAL:break
        encoder.stdin.close()
        ret=encoder.wait()
        if ret:raise RuntimeError("FFmpeg returned failure "+str(ret)+"; tail: "+logfile.read_text()[-2000:])
    finally:
        if encoder.poll() is None:encoder.kill();encoder.wait()
assert n==N_TOTAL,(n,N_TOTAL)
assert video.exists() and video.stat().st_size>1_000_000
probe=subprocess.run(["ffprobe","-v","error","-show_entries",
 "format=duration,size:stream=codec_name,width,height,pix_fmt,avg_frame_rate",
 "-of","json",str(video)],capture_output=True,text=True,check=True)
parsed=json.loads(probe.stdout)
assert abs(float(parsed["format"]["duration"])-stop)<.3
vstream=next(v for v in parsed["streams"] if v.get("width")==W)
assert vstream["height"]==H
assert any(v["codec_name"]=="aac" for v in parsed["streams"])
# Entire master decode, rather than trusting encoder's success flag.
with (ROOT/"decode.log").open("wb") as fp:
    p=subprocess.run(["ffmpeg","-v","error","-xerror","-i",str(video),"-f","null","-"],
                     stderr=fp,timeout=1200)
assert p.returncode==0,"Full decode failed"
cover=ROOT/("COVER_COLE_8K.jpg" if args.mode=="8k" else "COVER_COLE_4K.jpg")
if previews:
    contact=Image.new("RGB",(4*270,3*480),(12,14,18))
    for i,(t,img) in enumerate(sorted(previews.items())):
        im=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        reduced=Image.fromarray(im).resize((270,480),Image.Resampling.LANCZOS)
        contact.paste(reduced,((i%4)*270,(i//4)*480))
    contact.save(ROOT/"QA_CONTACT_SHEET.jpg",quality=92)
if previews:
    first=Image.fromarray(cv2.cvtColor(next(iter(previews.values())),cv2.COLOR_BGR2RGB))
    first.save(cover,quality=92)
credits=f"""THOMAS COLE — The Course of Empire: Destruction (1836).
Original authentic image {ART}
Origin pixels: {ART_DIM[0]}x{ART_DIM[1]}, original source SHA256 {ART_SHA256}.
VIDEO {W}x{H} pixels {FPS} fps, re-rendered directly from original, NOT upscale of previous 720p MP4.
Important: 8K is the physical output resolution; at tight zooms source detail is lower than 8K.
No generative AI image detail, no invented brushwork. Very subtle source-constrained sharpening.
Audio: The Descent, Kevin MacLeod (incompetech.com), CC BY 4.0:
https://creativecommons.org/licenses/by/4.0/
Exact audio file: {MUSIC}
Audio excerpt 00:09–{stop+9:.1f}, normalized, faded. Not Facebook Sound Collection.
For social uploads, verify actual provider's max resolution and licensing; publication pending owner review.
"""
(ROOT/"README_SOURCES_MUSIC_AND_LIMITS.txt").write_text(credits,encoding="utf-8")
manifest={"status":"RENDERED_QUALITY_CANDIDATE_NOT_PUBLISHED","mode":args.mode,
 "source_origin_px":list(ART_DIM),"output_px":[W,H],"upscaled_from_old_720p":False,
 "real_native_detail_at_all_zooms":False,"source_sha256":ART_SHA256,
 "audio_sha256":MUSIC_SHA256,"duration":stop,"frame_count":n,"fps":FPS,
 "video_sha256":hashlib.sha256(video.read_bytes()).hexdigest(),
 "actual_size_bytes":video.stat().st_size,"full_decode":True,"probe":parsed,
 "timing_unchanged_from_v339":True,"new_ai_image_pixels":False,
 "render_elapsed_seconds":round(time.monotonic()-start,2),
 "pending":{"owner_artistic_approval":True,"commercial_jurisdiction_review":True}}
(ROOT/"QA_MASTER.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
pkg=DIST/("ARTVISION_COLE_V340_8K_SOURCE_MASTER.zip" if args.mode=="8k" else "ARTVISION_COLE_V340_4K_ANDROID.zip")
with zipfile.ZipFile(pkg,"w",zipfile.ZIP_STORED) as z:
    for p in [video,cover,ROOT/"QA_MASTER.json",ROOT/"README_SOURCES_MUSIC_AND_LIMITS.txt",ROOT/"QA_CONTACT_SHEET.jpg"]:
        if p.exists():z.write(p,p.name)
with zipfile.ZipFile(pkg) as z:assert z.testzip() is None
print("MASTER_QUALITY_READY",args.mode,str(video),video.stat().st_size,"frames",n,"elapsed",round(time.monotonic()-start),flush=True)
print("ZIP_READY",pkg,pkg.stat().st_size,flush=True)
