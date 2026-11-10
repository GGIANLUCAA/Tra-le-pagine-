#!/usr/bin/env python3
"""Ulysses and the Sirens: new Cinema private-review candidate with independently verifiable high-resolution art.
This produces a review file; never Gold, commercially cleared, or published.
"""
import hashlib, json, math, subprocess, urllib.request, urllib.parse, wave
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

OUT=Path("output/artvision-owner-ulysses-sirens-cinema-v1")
OUT.mkdir(parents=True,exist_ok=True)
NAME="WATERHOUSE - Ulises y las Sirenas (National Gallery of Victoria, Melbourne, 1891. Óleo sobre lienzo, 100.6 x 202 cm).jpg"
FILE_PAGE="https://commons.wikimedia.org/wiki/File:WATERHOUSE_-_Ulises_y_las_Sirenas_%28National_Gallery_of_Victoria%2C_Melbourne%2C_1891._%C3%93leo_sobre_lienzo%2C_100.6_x_202_cm%29.jpg"
EXPECTED_SHA1="11c5f0c46db3ea0e5572c95f0b230b5395b7ed15"
EXPECTED_SIZE=28945314
EXPECTED_PIXELS=(11001,5386)
FILENAME=NAME.replace(" ","_")
digest=hashlib.md5(FILENAME.encode("utf8")).hexdigest()
direct=f"https://upload.wikimedia.org/wikipedia/commons/{digest[0]}/{digest[:2]}/{urllib.parse.quote(FILENAME)}"
redirect="https://commons.wikimedia.org/wiki/Special:Redirect/file/"+urllib.parse.quote(FILENAME)
source=OUT/"ORIGINAL_WATERHOUSE_PD_ART.jpg"
source_url=None
for url in (direct,redirect):
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"ArtVisionPrivateReview/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-; sourced public domain canvas)"})
        with urllib.request.urlopen(req,timeout=90) as res:
            data=res.read(EXPECTED_SIZE+1)
        if len(data)!=EXPECTED_SIZE: raise ValueError(f"Original byte count mismatch {len(data)}")
        if hashlib.sha1(data).hexdigest()!=EXPECTED_SHA1: raise ValueError("Original SHA1 mismatch")
        source.write_bytes(data)
        with Image.open(source) as im:
            if im.size!=EXPECTED_PIXELS or im.format!="JPEG": raise ValueError(f"Image identification mismatch {im.size}, {im.format}")
            im.verify()
        source_url=url
        print("SOURCE_ORIGINAL_VERIFIED",len(data),EXPECTED_SHA1,url,flush=True)
        break
    except Exception as exc:
        print("SOURCE_ATTEMPT_REJECTED",type(exc).__name__,str(exc)[:220],flush=True)
if source_url is None: raise RuntimeError("BOTH licensed source attempts failed. No fake or unverified video.")
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

FPS=20
W,H=1080,1920
# (caption_for_private_QA, seconds, start(x,y,h), end(x,y,h))
# Coordinates are proposed editorial crops, NOT authenticated semantic bboxes.
# A full-speed review must confirm the depicted details before artistic approval.
SHOTS=[
 ("FULL PAINTING — A SHIP SURROUNDED",5.4,None,None),
 ("THE SAIL AND THE STORM",4.0,(.51,.19,.70),(.52,.24,.65)),
 ("THE SIREN AT THE LEFT",4.2,(.08,.32,.65),(.11,.33,.57)),
 ("THE FLYING SIREN",4.2,(.31,.28,.59),(.33,.30,.55)),
 ("THE CENTRAL BIRD-WOMAN",4.1,(.49,.30,.58),(.51,.31,.52)),
 ("THE HELMSMAN AND DECK",4.4,(.68,.55,.72),(.66,.57,.65)),
 ("THE BOUND ODYSSEUS",4.6,(.74,.58,.57),(.75,.59,.52)),
 ("THE MEN AT THE OARS",4.5,(.49,.75,.62),(.48,.74,.56)),
 ("THE LONG OARS",4.1,(.29,.82,.67),(.31,.81,.59)),
 ("THE SIRENS' DARK WINGS",4.5,(.70,.43,.59),(.68,.42,.52)),
 ("THE ROCKS BEHIND",4.0,(.32,.16,.66),(.34,.17,.61)),
 ("THE PAINTED SAIL",4.3,(.60,.18,.66),(.58,.20,.59)),
 ("THE BOAT'S BLUE HULL",4.4,(.50,.74,.60),(.52,.72,.56)),
 ("SIREN CLOSE VIEW",4.2,(.80,.62,.55),(.82,.62,.49)),
 ("THE SEA AND BOAT",4.3,(.62,.83,.63),(.60,.81,.56)),
 ("THE HUMAN CREW",4.3,(.41,.63,.67),(.43,.63,.62)),
 ("THE CHORUS ABOVE THE SHIP",4.9,(.49,.34,.78),(.52,.36,.72)),
 ("THE FULL PAINTING RETURNS",6.3,None,None),
]
DURATION=sum(x[1] for x in SHOTS)
sr=22050
t=np.arange(round((DURATION+.15)*sr),dtype=np.float64)/sr
sound=np.zeros_like(t)
# Original composition, synthesized: no borrowed melody or protected recording.
pitches=[(65.41,98,130.81),(73.42,110,146.83),(82.41,123.47,164.81),(55,82.41,110)]
for idx,start in enumerate(np.arange(0,DURATION,7.7)):
    end=min(DURATION+.1,start+8.8)
    a,b=round(start*sr),min(len(t),round(end*sr))
    u=t[a:b]-start
    env=np.clip(u/1.45,0,1)*np.clip((end-start-u)/1.55,0,1)
    for j,f in enumerate(pitches[idx%4]):
        ph=2*np.pi*f*u+.05*np.sin(2*np.pi*.14*u)
        sound[a:b]+=env*.025/(1+.36*j)*(np.sin(ph)+.15*np.sin(2*ph))
    for beat in (0,3.85):
        pos=round((start+beat)*sr)
        if pos>=len(t):continue
        num=min(round(1.35*sr),len(t)-pos)
        z=np.arange(num)/sr
        sound[pos:pos+num]+=.034*np.exp(-3.3*z)*np.sin(2*np.pi*55*z)
sound+=.008*np.sin(2*np.pi*48*t)
sound*=np.clip(t/1.6,0,1)*np.clip((DURATION-t)/2.7,0,1)
with wave.open(str(OUT/"ORIGINAL_SCORE.wav"),"wb") as w:
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
    w.writeframes((np.tanh(sound*1.6)*32767).astype("<i2").tobytes())

art=Image.open(source).convert("RGB")
cover=ImageOps.fit(art,(1080,1920),Image.Resampling.LANCZOS,centering=(.48,.50)).filter(ImageFilter.GaussianBlur(39))
cover=Image.blend(cover,Image.new("RGB",(1080,1920),(8,14,20)),.61)
pic=art.copy();pic.thumbnail((1010,1120),Image.Resampling.LANCZOS)
cover.paste(pic,((1080-pic.width)//2,(1920-pic.height)//2))
draw=ImageDraw.Draw(cover)
font1=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",66)
font2=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",29)
draw.text((540,140),"ULYSSES AND THE SIRENS",fill=(240,234,216),font=font1,anchor="mm")
draw.text((540,1795),"JOHN WILLIAM WATERHOUSE  ·  1891",fill=(223,224,214),font=font2,anchor="mm")
cover.save(OUT/"COVER.jpg",quality=93)

arr=cv2.imread(str(source),cv2.IMREAD_COLOR)
if arr is None:raise RuntimeError("Verified JPEG failed OpenCV decoding")
ah,aw=arr.shape[:2]
if ah>3400:
    factor=3400/ah
    arr=cv2.resize(arr,(round(aw*factor),3400),interpolation=cv2.INTER_AREA)
ah,aw=arr.shape[:2]
# Preserve the true entire painting: letterbox based on the file aspect ratio.
bg=cv2.GaussianBlur(cv2.resize(arr,(W,H)),(0,0),34)
whole=cv2.convertScaleAbs(bg,alpha=.31,beta=0)
# Pixel-exact center placement: integer floor and clamping prevent 1081px into a 1080px canvas.
full_h=max(1,min(H,int(W*ah/aw)))
full_w=max(1,min(W,int(full_h*aw/ah)))
y0=(H-full_h)//2
x0=(W-full_w)//2
assert 0<=x0 and 0<=y0 and x0+full_w<=W and y0+full_h<=H
whole[y0:y0+full_h,x0:x0+full_w]=cv2.resize(arr,(full_w,full_h),interpolation=cv2.INTER_AREA)

cmd=["ffmpeg","-y","-hide_banner","-loglevel","error","-f","rawvideo","-pix_fmt","bgr24",
     "-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0","-i",str(OUT/"ORIGINAL_SCORE.wav"),
     "-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k",
     "-shortest","-movflags","+faststart",str(OUT/"VIDEO_REVIEW.mp4")]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
contact=[];timeline=[];offset=0
for idx,(label,seconds,frm,to) in enumerate(SHOTS):
    count=round(seconds*FPS)
    for frame_i in range(count):
        z=frame_i/max(1,count-1)
        e=z*z*(3-2*z)
        if frm is None: frame=whole.copy()
        else:
            cx,cy,height=[frm[j]*(1-e)+to[j]*e for j in range(3)]
            ch=min(ah,max(100,round(ah*height)))
            cw=min(aw,max(100,round(ch*W/H)))
            left=max(0,min(aw-cw,round(cx*aw-cw/2)))
            top=max(0,min(ah-ch,round(cy*ah-ch/2)))
            frame=cv2.resize(arr[top:top+ch,left:left+cw],(W,H),interpolation=cv2.INTER_AREA)
        if idx==0 and frame_i<round(2.7*FPS):
            mask=frame.copy()
            cv2.rectangle(mask,(0,52),(W,200),(19,17,22),-1)
            frame=cv2.addWeighted(frame,.33,mask,.67,0)
            cv2.putText(frame,"ULYSSES AND THE SIRENS",(55,113),cv2.FONT_HERSHEY_SIMPLEX,.94,(239,234,213),2,cv2.LINE_AA)
            cv2.putText(frame,"J. W. WATERHOUSE  |  1891",(56,154),cv2.FONT_HERSHEY_SIMPLEX,.52,(224,218,198),1,cv2.LINE_AA)
        proc.stdin.write(frame.tobytes())
        if frame_i==count//2: contact.append(cv2.resize(frame,(216,384),interpolation=cv2.INTER_AREA))
    timeline.append({"shot":idx+1,"editorial_subject_candidate":label,"start_s":round(offset,2),"duration_s":seconds,"camera_start":frm,"camera_end":to,"subject_semantic_review":"PENDING"})
    offset+=seconds
proc.stdin.close()
if proc.wait()!=0:raise RuntimeError("Encoder FFmpeg failed: no usable MP4")
sheet=np.full((5*384,4*216,3),18,dtype=np.uint8)
for i,frame in enumerate(contact):
    row,col=divmod(i,4)
    sheet[row*384:(row+1)*384,col*216:(col+1)*216]=frame
cv2.imwrite(str(OUT/"CONTACT_SHEET.jpg"),sheet)

rights={
 "painting":"Ulysses and the Sirens","artist":"John William Waterhouse","year":1891,
 "museum":"National Gallery of Victoria, Melbourne","accession":"p.396.3-1",
 "height_cm":100.6,"width_cm":202.0,
 "object_url":"https://www.ngv.vic.gov.au/explore/collection/work/4457/",
 "photo_source_file":FILE_PAGE,"source_used_url":source_url,
 "source_sha1":EXPECTED_SHA1,"source_sha256":sha(source),"source_bytes":source.stat().st_size,
 "pixel_dimensions":list(EXPECTED_PIXELS),
 "photo_author":"Wikimedia Commons faithful PD-Art digital reproduction",
 "photo_license":"Public Domain Mark 1.0 / PD-Art as classified by Wikimedia Commons",
 "photo_license_url":"https://creativecommons.org/publicdomain/mark/1.0/",
 "photo_credit":"John William Waterhouse, Ulysses and the Sirens (1891), oil on canvas, 100.6 x 202.0 cm, National Gallery of Victoria, Melbourne, purchased 1891, © Public Domain; file via Wikimedia Commons.",
 "painting_copyright":"Waterhouse died 1917; public domain in Italy in 2026; museum NGV marks artwork public domain",
 "museum_reproduction_terms":"NGV asks title, artist, dimensions, collection credit; full painting is shown at opening and end; final commercial use rights and download policies pending",
 "territorial_cultural_heritage_reuse":"PENDING FINAL LEGAL REVIEW before commercial publication",
 "distribution_allowed":False,
 "museum_scene":"NONE; Cinema Standard only",
 "music":"New original synthesized atmospheric score, no third-party recordings"
}
(OUT/"SOURCES_RIGHTS.json").write_text(json.dumps(rights,ensure_ascii=False,indent=2),encoding="utf8")
(OUT/"STORYBOARD.json").write_text(json.dumps({"total_duration_s":DURATION,"format":"cinema_standard","shots":timeline,"human_full_speed_QA":"PENDING","visual_semantics":"PENDING","source_identity":"SHA1 verified before render"},ensure_ascii=False,indent=2),encoding="utf8")
posts={"title":"Ulysses and the Sirens — John William Waterhouse (1891)",
 "facebook":"Ulisse vuole ascoltare il canto delle sirene, ma sa che potrebbe condurlo alla morte. Fa tappare le orecchie ai rematori e si fa legare all'albero della nave. Waterhouse dipinge le sirene come donne-uccello, mentre la nave prova a sfuggire. Ulysses and the Sirens, 1891, National Gallery of Victoria. #ArtHistory #Waterhouse",
 "instagram":"Sirene dalle ali scure, rematori decisi, Ulisse legato all'albero. L'Odissea in un dipinto. Ulysses and the Sirens (1891). #ArtHistory #Odyssey",
 "tiktok":"Le sirene di questo quadro non hanno una coda di pesce: hanno ali e volti umani. E Ulisse è legato all'albero della nave. #ArtTok #Waterhouse",
 "youtube_shorts":"Ulysses and the Sirens (1891) — a cinematic visual journey into John William Waterhouse's depiction of the perilous song of the Sirens.",
 "credits":"John William Waterhouse, Ulysses and the Sirens, 1891, oil on canvas, 100.6 × 202 cm, National Gallery of Victoria, Melbourne, purchased 1891, © Public Domain. Wikimedia Commons PD-Art source. Music generated as original score; public reuse subject to final rights/artistic review."}
(OUT/"SOCIAL_DRAFTS.json").write_text(json.dumps(posts,ensure_ascii=False,indent=2),encoding="utf8")
(OUT/"READ_ME_FIRST.md").write_text("PRIVATE REVIEW ONLY. New Cinema candidate of Waterhouse Ulysses and the Sirens, NGV p.396.3-1. Original Commons source must pass SHA1 and bytes checks. NGV requests object attribution and inclusion of full work when showing crops; film shows full image at opening and closing. Human artistic and legal commercial review pending. No Gold, no publication, no paid APIs, no master modifications.\n",encoding="utf8")
print("ULYSSES_CANDIDATE_MP4_RENDERED",sha(OUT/"VIDEO_REVIEW.mp4"),"duration",DURATION,flush=True)
