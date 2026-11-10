#!/usr/bin/env python3
"""The Duel After the Masquerade: one-off owner-authorized private Cinema candidate.
This produces a review file; never Gold, commercially cleared, or published.
"""
import hashlib, json, math, subprocess, urllib.request, urllib.parse, wave
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

OUT=Path("output/artvision-owner-duel-masquerade-cinema-v1")
OUT.mkdir(parents=True,exist_ok=True)
NAME="Jean-Léon Gérôme - The Duel After the Masquerade - Google Art Project.jpg"
FILE_PAGE="https://commons.wikimedia.org/wiki/File:Jean-L%C3%A9on_G%C3%A9r%C3%B4me_-_The_Duel_After_the_Masquerade_-_Google_Art_Project.jpg"
EXPECTED_SHA1="71995210db9c17889e156ce2870e3211974fa4f8"
EXPECTED_SIZE=11659708
EXPECTED_PIXELS=(8401,5760)
FILENAME=NAME.replace(" ","_")
digest=hashlib.md5(FILENAME.encode("utf8")).hexdigest()
direct=f"https://upload.wikimedia.org/wikipedia/commons/{digest[0]}/{digest[:2]}/{urllib.parse.quote(FILENAME)}"
redirect="https://commons.wikimedia.org/wiki/Special:Redirect/file/"+urllib.parse.quote(FILENAME)
source=OUT/"ORIGINAL_WALTERS_PD_ART.jpg"
source_url=None
for url in (direct,redirect):
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"ArtVisionPrivateReview/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-; PD artwork verification)"})
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
 ("THE WOUNDED DUELIST",3.8,(.29,.68,.52),(.31,.70,.45)),
 ("THE ENTIRE PAINTING",4.2,None,None),
 ("THE FROZEN MORNING",4.2,(.49,.16,.67),(.51,.19,.61)),
 ("THE CARRIAGES",3.9,(.70,.49,.48),(.72,.48,.43)),
 ("PIERROT IN WHITE",4.4,(.29,.75,.45),(.32,.73,.39)),
 ("THE COMPANION IN BLACK",4.1,(.18,.61,.48),(.19,.61,.43)),
 ("THE RED COSTUME",4.0,(.43,.73,.50),(.44,.75,.43)),
 ("THE SWORD",4.3,(.12,.84,.40),(.15,.85,.34)),
 ("THE DESPAIR",4.1,(.34,.55,.43),(.36,.58,.38)),
 ("THE SILENT FOREST",3.9,(.41,.28,.63),(.45,.31,.56)),
 ("THE VICTORS WALK AWAY",4.5,(.78,.60,.59),(.77,.61,.52)),
 ("THE HARLEQUIN",4.2,(.89,.64,.39),(.87,.65,.34)),
 ("THE COSTUME OF THE VICTOR",4.5,(.70,.61,.43),(.69,.61,.39)),
 ("THE WOUNDED HAND",4.3,(.38,.82,.32),(.39,.80,.29)),
 ("THE DARK CLOAK",4.2,(.19,.58,.35),(.21,.56,.30)),
 ("THE DISTANCE",4.3,(.69,.39,.62),(.71,.40,.57)),
 ("THE AFTERMATH",4.3,(.40,.69,.61),(.38,.70,.55)),
 ("THE ENTIRE PAINTING",6.0,None,None),
]
DURATION=sum(x[1] for x in SHOTS)
sr=22050
t=np.arange(round((DURATION+.15)*sr),dtype=np.float64)/sr
sound=np.zeros_like(t)
# Original composition, synthesized: no borrowed melody or protected recording.
pitches=[(55,82.41,110),(61.74,92.5,123.47),(65.41,98,130.81),(49,73.42,98)]
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
cover=ImageOps.fit(art,(1080,1920),Image.Resampling.LANCZOS,centering=(.42,.53)).filter(ImageFilter.GaussianBlur(35))
cover=Image.blend(cover,Image.new("RGB",(1080,1920),(10,13,18)),.53)
pic=art.copy();pic.thumbnail((1010,1120),Image.Resampling.LANCZOS)
cover.paste(pic,((1080-pic.width)//2,(1920-pic.height)//2))
draw=ImageDraw.Draw(cover)
font1=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",85)
font2=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",31)
draw.text((540,165),"THE DUEL",fill=(244,225,208),font=font1,anchor="mm")
draw.text((540,235),"AFTER THE MASQUERADE",fill=(238,228,216),font=font2,anchor="mm")
draw.text((540,1795),"JEAN-LÉON GÉRÔME  ·  1857–1859",fill=(234,223,207),font=font2,anchor="mm")
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
full_h=min(H,round(W*ah/aw))
full_w=round(full_h*aw/ah)
whole[(H-full_h)//2:(H+full_h)//2,(W-full_w)//2:(W+full_w)//2]=cv2.resize(arr,(full_w,full_h),interpolation=cv2.INTER_AREA)

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
            cv2.putText(frame,"THE DUEL",(55,113),cv2.FONT_HERSHEY_SIMPLEX,1.45,(239,234,213),2,cv2.LINE_AA)
            cv2.putText(frame,"AFTER THE MASQUERADE  |  GEROME 1857-1859",(56,154),cv2.FONT_HERSHEY_SIMPLEX,.47,(224,218,198),1,cv2.LINE_AA)
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
 "painting":"The Duel After the Masquerade","artist":"Jean-Léon Gérôme","year":"1857–1859",
 "museum":"Walters Art Museum, Baltimore","accession":"37.51",
 "height_cm":39.1,"width_cm":56.3,
 "object_url":"https://art.thewalters.org/object/37.51/",
 "photo_source_file":FILE_PAGE,"source_used_url":source_url,
 "source_sha1":EXPECTED_SHA1,"source_sha256":sha(source),"source_bytes":source.stat().st_size,
 "pixel_dimensions":list(EXPECTED_PIXELS),
 "photo_author":"Walters Art Museum / Google Art Project original",
 "photo_license":"Public Domain Mark (PD-Art faithful reproduction of 2-D artwork)",
 "photo_license_url":"https://creativecommons.org/publicdomain/mark/1.0/",
 "photo_credit":"Jean-Léon Gérôme, The Duel After the Masquerade, Walters Art Museum 37.51, original via Wikimedia Commons (PDM/PD-Art)",
 "painting_copyright":"Jean-Léon Gérôme died 1904; underlying artwork public domain",
 "museum_release":"Walters Art Museum Commons collection releases its 2-D paintings and photographs to the public domain worldwide",
 "commercial_territorial_review":"PENDING FINAL REVIEW PRIOR TO PUBLICATION",
 "distribution_allowed":False,
 "museum_scene":"NONE; Cinema Standard only",
 "music":"new original synthesized score, no third-party recordings"}
(OUT/"SOURCES_RIGHTS.json").write_text(json.dumps(rights,ensure_ascii=False,indent=2),encoding="utf8")
(OUT/"STORYBOARD.json").write_text(json.dumps({"total_duration_s":DURATION,"format":"cinema_standard","shots":timeline,"human_full_speed_QA":"PENDING","visual_semantics":"PENDING","source_identity":"SHA1 verified before render"},ensure_ascii=False,indent=2),encoding="utf8")
posts={"title":"The Duel After the Masquerade — Jean-Léon Gérôme (1857–1859)",
 "facebook":"Una festa in maschera finisce in tragedia. In un bosco gelato di Parigi, Pierrot giace ferito mentre gli avversari si allontanano. Jean-Léon Gérôme trasforma il momento successivo al duello in una scena di silenzio e disperazione. #ArtHistory #Gerome",
 "instagram":"Un duello finito. Una figura in bianco ferita, il gelo e gli avversari che si allontanano. The Duel After the Masquerade, Gérôme. #ArtHistory #Painting",
 "tiktok":"Sembrano usciti da una festa in maschera. Ma quello che è successo nella neve è terribile. The Duel After the Masquerade. #ArtTok",
 "youtube_shorts":"The Duel After the Masquerade: Jean-Léon Gérôme's wintry aftermath of a costumed duel (1857–1859), in 18 carefully framed visual shots.",
 "credits":"Jean-Léon Gérôme, The Duel After the Masquerade, 1857–1859, Walters Art Museum 37.51. Public-domain faithful reproduction via Wikimedia Commons / Google Art Project. Synthesized original score. Public posting requires separate artistic and rights approval."}
(OUT/"SOCIAL_DRAFTS.json").write_text(json.dumps(posts,ensure_ascii=False,indent=2),encoding="utf8")
(OUT/"READ_ME_FIRST.md").write_text("PRIVATE REVIEW ONLY. New Cinema candidate for the exact Walters Museum painting 37.51, not the Chantilly or Hermitage versions. Source verified by original byte count and SHA1. Artistic crop review and final publication rights clearance pending. No Gold, no publishing, no paid provider or modifications to existing masters.\n",encoding="utf8")
print("DUEL_CANDIDATE_MP4_RENDERED",sha(OUT/"VIDEO_REVIEW.mp4"),"duration",DURATION,flush=True)
