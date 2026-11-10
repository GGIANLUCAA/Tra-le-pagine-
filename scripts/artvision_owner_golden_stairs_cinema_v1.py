#!/usr/bin/env python3
"""Golden Stairs: owner-authorized private Cinema candidate, exact licensed source.
This produces a review file; never Gold, commercially cleared, or published.
"""
import hashlib, json, math, subprocess, urllib.request, urllib.parse, wave
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT=Path("output/artvision-owner-golden-stairs-cinema-v1")
OUT.mkdir(parents=True,exist_ok=True)
NAME="Edward coley burne-jones, the golden stairs, 1880.jpg"
FILE_PAGE="https://commons.wikimedia.org/wiki/File:Edward_coley_burne-jones,_the_golden_stairs,_1880.jpg"
EXPECTED_SHA1="228c89451aba3687e19e1fc87c22cb435cced2d1"
EXPECTED_SIZE=8259955
EXPECTED_PIXELS=(2658,4986)
FILENAME=NAME.replace(" ","_")
digest=hashlib.md5(FILENAME.encode("utf8")).hexdigest()
direct=f"https://upload.wikimedia.org/wikipedia/commons/{digest[0]}/{digest[:2]}/{urllib.parse.quote(FILENAME)}"
redirect="https://commons.wikimedia.org/wiki/Special:Redirect/file/"+urllib.parse.quote(FILENAME)
source=OUT/"ORIGINAL_SAILKO_CC_BY3.jpg"
source_url=None
for url in (direct,redirect):
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"ArtVisionPrivateReview/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-; CC BY attribution)"})
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
 ("THE PROCESSION",3.5,(.51,.45,.52),(.51,.45,.49)),
 ("THE ENTIRE PAINTING",4.3,None,None),
 ("UPPER LANDING",3.8,(.49,.16,.42),(.54,.18,.37)),
 ("THE FIRST DESCENT",4.2,(.60,.30,.45),(.57,.32,.39)),
 ("CRESCENT OF THE STAIR",4.5,(.57,.43,.42),(.59,.44,.35)),
 ("THE FIGURES",4.1,(.50,.55,.44),(.47,.56,.39)),
 ("DAPPLED LIGHT",4.0,(.37,.35,.42),(.40,.37,.37)),
 ("THE CURVE",4.5,(.58,.59,.47),(.56,.59,.41)),
 ("THE MIDDLE LANDING",4.1,(.39,.49,.48),(.44,.51,.40)),
 ("THE WHITE DRESSES",4.3,(.51,.68,.46),(.53,.68,.39)),
 ("A MUSICAL DETAIL",4.5,(.56,.33,.35),(.57,.36,.32)),
 ("THE LAST STEPS",4.0,(.46,.83,.43),(.47,.80,.38)),
 ("THE PALETTE",4.2,(.46,.44,.60),(.50,.44,.52)),
 ("THE PROCESSION RETURNS",4.2,(.52,.56,.58),(.50,.54,.53)),
 ("THE ARCHITECTURE",4.0,(.49,.24,.57),(.50,.25,.50)),
 ("THE DESCENT",4.3,(.50,.69,.54),(.52,.66,.49)),
 ("THE FULL STORY",5.8,None,None),
]
DURATION=sum(x[1] for x in SHOTS)
sr=22050
t=np.arange(round((DURATION+.15)*sr),dtype=np.float64)/sr
sound=np.zeros_like(t)
# Original composition, synthesized: no borrowed melody or protected recording.
pitches=[(87.31,130.81,174.61),(73.42,110,146.83),(98,146.83,196),(82.41,123.47,164.81)]
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
cover=Image.new("RGB",(1080,1920),(16,15,18))
pic=art.copy();pic.thumbnail((930,1590),Image.Resampling.LANCZOS)
cover.paste(pic,((1080-pic.width)//2,(1920-pic.height)//2))
draw=ImageDraw.Draw(cover)
font1=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",65)
font2=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",28)
draw.text((540,85),"THE GOLDEN STAIRS",fill=(237,227,205),font=font1,anchor="mm")
draw.text((540,1828),"EDWARD BURNE-JONES · 1880",fill=(221,212,195),font=font2,anchor="mm")
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
            cv2.putText(frame,"THE GOLDEN STAIRS",(55,113),cv2.FONT_HERSHEY_SIMPLEX,1.05,(239,234,213),2,cv2.LINE_AA)
            cv2.putText(frame,"EDWARD BURNE-JONES  |  1880",(56,154),cv2.FONT_HERSHEY_SIMPLEX,.50,(224,218,198),1,cv2.LINE_AA)
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
 "painting":"The Golden Stairs","artist":"Edward Burne-Jones","year":1880,
 "museum":"Tate Britain","accession":"N04005",
 "height_cm":269.2,"width_cm":116.8,
 "object_url":"https://www.tate.org.uk/art/artworks/burne-jones-the-golden-stairs-n04005",
 "photo_source_file":FILE_PAGE,"source_used_url":source_url,
 "source_sha1":EXPECTED_SHA1,"source_sha256":sha(source),"source_bytes":source.stat().st_size,
 "pixel_dimensions":list(EXPECTED_PIXELS),
 "photo_author":"Sailko",
 "photo_license":"Creative Commons Attribution 3.0 Unported",
 "photo_license_url":"https://creativecommons.org/licenses/by/3.0/",
 "photo_credit":"Photograph © Sailko, licensed CC BY 3.0 (crop and moving edit for private ArtVision review)",
 "painting_copyright":"Author died 1898; underlying artwork public-domain claim",
 "territorial_cultural_heritage_reuse":"PENDING LEGAL REVIEW (including any Tate/museum-specific terms)",
 "distribution_allowed":False,
 "museum_scene":"NONE; Cinema Standard only",
 "music":"new original synthesized score, no third-party recordings"}
(OUT/"SOURCES_RIGHTS.json").write_text(json.dumps(rights,ensure_ascii=False,indent=2),encoding="utf8")
(OUT/"STORYBOARD.json").write_text(json.dumps({"total_duration_s":DURATION,"format":"cinema_standard","shots":timeline,"human_full_speed_QA":"PENDING","visual_semantics":"PENDING","source_identity":"SHA1 verified before render"},ensure_ascii=False,indent=2),encoding="utf8")
posts={"title":"The Golden Stairs — Edward Burne-Jones (1880)",
 "facebook":"Una scala di figure in abiti chiari scende senza che sia evidente una destinazione. Nel 1880 Burne-Jones trasformò una processione in ritmo, luce e mistero. The Golden Stairs, Tate Britain. #ArtHistory #PreRaphaelite",
 "instagram":"Una scala infinita, tessuti chiari e figure quasi sospese. The Golden Stairs (1880), Edward Burne-Jones. #ArtHistory #TheGoldenStairs",
 "tiktok":"Sono tutte in movimento, ma il quadro sembra fermare il tempo. The Golden Stairs, 1880. #ArtTok #ArtHistory",
 "youtube_shorts":"The Golden Stairs (1880): a close study of Burne-Jones's unusual descending procession, painted detail by detail.",
 "credits":"Edward Burne-Jones, The Golden Stairs, 1880, Tate Britain N04005. Photo © Sailko CC BY 3.0 https://commons.wikimedia.org/wiki/File:Edward_coley_burne-jones,_the_golden_stairs,_1880.jpg; photograph cropped/animated. Original synthesized music."}
(OUT/"SOCIAL_DRAFTS.json").write_text(json.dumps(posts,ensure_ascii=False,indent=2),encoding="utf8")
(OUT/"READ_ME_FIRST.md").write_text("PRIVATE REVIEW ONLY. Technically rendered Cinema candidate, not an approved finished Gold video. Original photo credit Sailko CC BY 3.0. Review the moving MP4 visually at full speed and confirm subject crops/rights before any commercial publication. No fictitious museum. Does not change primary queue 26/36. No new paid APIs or publisher actions.\n",encoding="utf8")
print("CANDIDATE_MP4_RENDERED",sha(OUT/"VIDEO_REVIEW.mp4"),"duration",DURATION,flush=True)
