#!/usr/bin/env python3
"""The Barque of Dante: new Cinema private-review candidate with independently verifiable image.
This produces a review file; never Gold, commercially cleared, or published.
"""
import hashlib, json, math, subprocess, urllib.request, urllib.parse, wave
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

OUT=Path("output/artvision-owner-barque-dante-cinema-v1")
OUT.mkdir(parents=True,exist_ok=True)
NAME="Dante et Virgile, dit aussi La barque de Dante - Eugène Delacroix - Musée du Louvre Peintures INV 3820 ; L 3837.jpg"
FILE_PAGE="https://commons.wikimedia.org/wiki/File:Dante_et_Virgile,_dit_aussi_La_barque_de_Dante_-_Eug%C3%A8ne_Delacroix_-_Mus%C3%A9e_du_Louvre_Peintures_INV_3820_%3B_L_3837.jpg"
EXPECTED_SHA1="f400b554befea0d06d8344a3c58c99b0c2e0718a"
EXPECTED_SIZE=20968161
EXPECTED_PIXELS=(9733,7493)
FILENAME=NAME.replace(" ","_")
digest=hashlib.md5(FILENAME.encode("utf8")).hexdigest()
direct=f"https://upload.wikimedia.org/wikipedia/commons/{digest[0]}/{digest[:2]}/{urllib.parse.quote(FILENAME)}"
redirect="https://commons.wikimedia.org/wiki/Special:Redirect/file/"+urllib.parse.quote(FILENAME)
source=OUT/"ORIGINAL_DELACROIX_PD_ART.jpg"
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
 ("THE COMPLETE PAINTING",4.3,None,None),
 ("THE FERRY IN THE STORM",4.5,(.50,.55,.76),(.50,.54,.69)),
 ("DANTE'S RAISED HAND",4.1,(.36,.26,.40),(.36,.30,.34)),
 ("VIRGIL'S DARK CLOAK",4.4,(.66,.38,.45),(.63,.39,.40)),
 ("THE BURNING CITY OF DIS",4.4,(.10,.20,.53),(.13,.23,.47)),
 ("DANTE AND VIRGIL TOGETHER",4.2,(.55,.37,.58),(.55,.39,.52)),
 ("THE RIGHTMOST TORMENTED SOUL",4.2,(.92,.61,.47),(.89,.63,.43)),
 ("THE PALE BODY IN THE WATER",4.5,(.38,.81,.49),(.42,.80,.44)),
 ("THE FACE AT THE LEFT EDGE",4.1,(.08,.63,.44),(.11,.65,.39)),
 ("THE DARK WATER",4.0,(.57,.87,.45),(.55,.85,.39)),
 ("DANTE'S ANXIOUS EXPRESSION",4.3,(.47,.28,.37),(.48,.30,.34)),
 ("VIRGIL'S PROFILE",4.4,(.67,.29,.36),(.65,.30,.32)),
 ("THE BOAT AND ITS PASSENGERS",4.7,(.54,.53,.70),(.53,.55,.62)),
 ("THE STORM CLOUDS",4.2,(.58,.13,.54),(.58,.17,.50)),
 ("THE STRUGGLING ARMS",4.2,(.57,.72,.49),(.58,.73,.43)),
 ("THE LEFT FOREGROUND SOUL",4.4,(.25,.81,.46),(.28,.79,.41)),
 ("THE RIVER AND THE FLAMES",4.7,(.50,.48,.83),(.51,.49,.76)),
 ("THE COMPLETE PAINTING RETURNS",6.2,None,None),
]
DURATION=sum(x[1] for x in SHOTS)
sr=22050
t=np.arange(round((DURATION+.15)*sr),dtype=np.float64)/sr
sound=np.zeros_like(t)
# Original composition, synthesized: no borrowed melody or protected recording.
pitches=[(49,73.42,98),(55,82.41,110),(43.65,65.41,87.31),(58.27,87.31,116.54)]
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
cover=ImageOps.fit(art,(1080,1920),Image.Resampling.LANCZOS,centering=(.5,.5)).filter(ImageFilter.GaussianBlur(40))
cover=Image.blend(cover,Image.new("RGB",(1080,1920),(9,12,20)),.58)
pic=art.copy();pic.thumbnail((1010,1220),Image.Resampling.LANCZOS)
cover.paste(pic,((1080-pic.width)//2,(1920-pic.height)//2))
draw=ImageDraw.Draw(cover)
font1=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",71)
font2=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",30)
draw.text((540,147),"THE BARQUE OF DANTE",fill=(244,228,214),font=font1,anchor="mm")
draw.text((540,1795),"EUGÈNE DELACROIX  ·  1822",fill=(233,222,205),font=font2,anchor="mm")
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
            cv2.putText(frame,"THE BARQUE OF DANTE",(55,113),cv2.FONT_HERSHEY_SIMPLEX,.98,(239,234,213),2,cv2.LINE_AA)
            cv2.putText(frame,"EUGENE DELACROIX  |  1822",(56,154),cv2.FONT_HERSHEY_SIMPLEX,.56,(224,218,198),1,cv2.LINE_AA)
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
 "painting":"The Barque of Dante","artist":"Eugène Delacroix","year":1822,
 "museum":"Musée du Louvre, Paris","accession":"INV 3820 ; L 3837",
 "height_cm":189.0,"width_cm":241.5,
 "object_url":"https://collections.louvre.fr/en/ark:/53355/cl010065871",
 "photo_source_file":FILE_PAGE,"source_used_url":source_url,
 "source_sha1":EXPECTED_SHA1,"source_sha256":sha(source),"source_bytes":source.stat().st_size,
 "pixel_dimensions":list(EXPECTED_PIXELS),
 "photo_author":"Shonagon (2024)",
 "photo_license":"Public Domain Mark 1.0 / PD-Art faithful reproduction on Wikimedia Commons",
 "photo_license_url":"https://creativecommons.org/publicdomain/mark/1.0/",
 "photo_credit":"Eugène Delacroix, The Barque of Dante (1822), Louvre INV 3820. Photograph Shonagon via Wikimedia Commons, PD-Art / Public Domain Mark 1.0.",
 "painting_copyright":"Eugène Delacroix died 1863; underlying artwork public domain in France and Italy",
 "territorial_cultural_heritage_reuse":"PENDING legal review for France/Italy and applicable Louvre/reproduction terms before commercial publishing",
 "distribution_allowed":False,
 "museum_scene":"NONE; Cinema Standard only",
 "music":"New original synthesized atmospheric score, no third-party recordings"
}
(OUT/"SOURCES_RIGHTS.json").write_text(json.dumps(rights,ensure_ascii=False,indent=2),encoding="utf8")
(OUT/"STORYBOARD.json").write_text(json.dumps({"total_duration_s":DURATION,"format":"cinema_standard","shots":timeline,"human_full_speed_QA":"PENDING","visual_semantics":"PENDING","source_identity":"SHA1 verified before render"},ensure_ascii=False,indent=2),encoding="utf8")
posts={"title":"The Barque of Dante — Eugène Delacroix (1822)",
 "facebook":"Un battello attraversa l'Inferno. Dante, avvolto di rosso, si ritrae mentre Virgilio osserva gli spiriti che cercano di aggrapparsi alla barca. Nel 1822 Delacroix dipinse il terrore come una tempesta di corpi, acqua e fuoco. The Barque of Dante, Louvre INV 3820. #ArtHistory #Delacroix",
 "instagram":"Acqua nera, città in fiamme, anime disperate. Un viaggio nell'Inferno secondo Eugène Delacroix, 1822. #TheBarqueOfDante #ArtHistory",
 "tiktok":"Dante attraversa l'Inferno, ma le anime nell'acqua cercano di fermare la barca. Un dipinto che sembra già una scena di cinema. #ArtTok #Delacroix",
 "youtube_shorts":"The Barque of Dante (1822), Eugène Delacroix: an atmospheric visual study of Dante and Virgil crossing the dark river of Hell.",
 "credits":"Eugène Delacroix, The Barque of Dante, 1822, Louvre INV 3820. Photograph: Shonagon via Wikimedia Commons (PD-Art/Public Domain Mark 1.0), photographed 2024. Original synthesized score; final rights and human visual QA pending."}
(OUT/"SOCIAL_DRAFTS.json").write_text(json.dumps(posts,ensure_ascii=False,indent=2),encoding="utf8")
(OUT/"READ_ME_FIRST.md").write_text("PRIVATE REVIEW ONLY. New Cinema candidate for Louvre INV 3820; source verified by original byte count and SHA1 before rendering. Painting is in the public domain and Wikimedia Commons shows PD-Art, but final territorial commercial rights remain pending. Review all moving shots for semantic focus before approval. No Gold, no publication, no paid provider, no changes to existing masters.\n",encoding="utf8")
print("BARQUE_CANDIDATE_MP4_RENDERED",sha(OUT/"VIDEO_REVIEW.mp4"),"duration",DURATION,flush=True)
