#!/usr/bin/env python3
"""Owner one-off Destruction Cinema private review. No publishing, no Gold, no paid APIs."""
import hashlib, json, math, subprocess, urllib.request, wave, zipfile
from pathlib import Path
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont

out=Path("output/owner-cole-destruction-v1")
out.mkdir(parents=True,exist_ok=True)
source=out/"ORIGINAL_ARTWORK.jpg"
page="https://commons.wikimedia.org/wiki/File:Cole_Thomas_The_Course_of_Empire_Destruction_1836.jpg"
original="https://upload.wikimedia.org/wikipedia/commons/6/64/Cole_Thomas_The_Course_of_Empire_Destruction_1836.jpg"
fallback="https://commons.wikimedia.org/wiki/Special:Redirect/file/Cole_Thomas_The_Course_of_Empire_Destruction_1836.jpg"
sha1="b2af9bc527fd6a671ae2e307f8ec8a0a2b4e993a"
source_url=None
for url in (original,fallback):
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"ArtVisionPrivateReview/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-)"})
        with urllib.request.urlopen(req,timeout=95) as res:
            data=res.read(17561413)
        if len(data)!=17561412: raise ValueError(f"wrong original bytes {len(data)}")
        if hashlib.sha1(data).hexdigest()!=sha1: raise ValueError("Commons original SHA1 mismatch")
        source.write_bytes(data)
        with Image.open(source) as img:
            assert img.size==(8917,5532) and img.format=="JPEG"
            img.verify()
        source_url=url
        break
    except Exception as e:
        print("SOURCE_ATTEMPT_FAILED",type(e).__name__,str(e)[:150],flush=True)
if not source_url: raise RuntimeError("Original source unavailable, source gate failed: no render")
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
print("ORIGINAL_VERIFIED",source.stat().st_size,sha(source),flush=True)

# Art-directed, distinct points of interest; all imagery comes from the genuine painting.
shots=[
 ("CRISIS",3.8,(.66,.73,.43),(.61,.71,.37)),
 ("WHOLE",3.6,None,None),
 ("STORM",4.2,(.48,.20,.63),(.52,.21,.57)),
 ("CITY",4.5,(.74,.42,.55),(.70,.40,.49)),
 ("FIRE",4.5,(.84,.28,.45),(.83,.31,.41)),
 ("PEOPLE",4.1,(.42,.65,.52),(.46,.64,.45)),
 ("BRIDGE",4.9,(.45,.72,.54),(.48,.72,.47)),
 ("SHIPS",4.1,(.17,.58,.61),(.20,.59,.55)),
 ("ARCH",4.6,(.41,.81,.47),(.41,.81,.40)),
 ("WATER",4.5,(.60,.87,.37),(.60,.86,.33)),
 ("RUINS",4.5,(.78,.60,.56),(.80,.60,.49)),
 ("SMOKE",4.0,(.87,.21,.42),(.88,.22,.37)),
 ("COLLAPSE",4.5,(.36,.71,.50),(.40,.70,.43)),
 ("HUMANS",4.2,(.63,.82,.37),(.60,.83,.34)),
 ("AFTERMATH",4.4,(.31,.44,.68),(.35,.42,.62)),
 ("WHOLE",5.2,None,None),
]
W,H,FPS=1080,1920,20
duration=sum(s[1] for s in shots)
# Independently composed score: synthesized tones and distant pulses, no copyrighted recording.
sr=22050;n=int((duration+.15)*sr);t=np.arange(n)/sr
audio=np.zeros(n,dtype=np.float64)
chords=[(65.41,98,130.81),(73.42,110,146.83),(55,82.41,110),(61.74,92.5,123.47)]
for idx,start in enumerate(np.arange(0,duration,7.5)):
    end=min(duration+.1,start+8.9)
    a,b=int(start*sr),min(n,int(end*sr));u=t[a:b]-start
    env=np.minimum(1,u/1.35)*np.maximum(0,np.minimum(1,(end-start-u)/1.45))
    for j,freq in enumerate(chords[idx%4]):
        audio[a:b]+=.035/(1+j*.32)*env*(np.sin(2*np.pi*freq*u)+.2*np.sin(4*np.pi*freq*u))
    for off in (0,3.75):
        pos=int((start+off)*sr)
        if pos>=n:continue
        length=min(n-pos,int(.75*sr));z=np.arange(length)/sr
        audio[pos:pos+length]+=.065*np.exp(-5*z)*np.sin(2*np.pi*(52-16*z)*z)
audio+=.013*np.sin(2*np.pi*49*t)
audio*=np.minimum(1,t/1.5)*np.clip((duration-t)/2.4,0,1)
with wave.open(str(out/"SCORE_ORIGINALE.wav"),"wb") as wav:
    wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(sr)
    wav.writeframes((np.tanh(audio*1.5)*32767).astype("<i2").tobytes())

img=cv2.imread(str(source),cv2.IMREAD_COLOR)
assert img is not None
oh,ow=img.shape[:2]
img=cv2.resize(img,(4200,round(oh*4200/ow)),interpolation=cv2.INTER_AREA)
oh,ow=img.shape[:2]
blur=cv2.GaussianBlur(cv2.resize(img,(W,H)),(0,0),42)
whole=cv2.convertScaleAbs(blur,alpha=.4,beta=0)
hh=round(W*oh/ow);yy=(H-hh)//2
whole[yy:yy+hh]=cv2.resize(img,(W,hh),interpolation=cv2.INTER_AREA)
cover=Image.new("RGB",(1080,1920),(12,14,17))
art=Image.open(source).convert("RGB");art.thumbnail((1080,1460),Image.Resampling.LANCZOS)
cover.paste(art,((1080-art.width)//2,(1920-art.height)//2))
d=ImageDraw.Draw(cover)
d.text((540,172),"DESTRUCTION",font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",76),anchor="mm",fill=(237,229,210))
d.text((540,1755),"THOMAS COLE  ·  1836",font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",33),anchor="mm",fill=(237,229,210))
cover.save(out/"COPERTINA.jpg",quality=92)

cmd=["ffmpeg","-y","-hide_banner","-loglevel","error","-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0","-i",str(out/"SCORE_ORIGINALE.wav"),"-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart",str(out/"VIDEO_REVIEW.mp4")]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
contact=[];timeline=[]
for idx,(name,seconds,a,b) in enumerate(shots):
    count=round(seconds*FPS)
    for k in range(count):
        z=k/max(1,count-1);e=z*z*(3-2*z)
        if a is None: frame=whole.copy()
        else:
            cx,cy,height=[a[v]*(1-e)+b[v]*e for v in range(3)]
            ch=min(oh,max(80,round(oh*height)))
            cw=min(ow,max(80,round(ch*W/H)))
            x=max(0,min(ow-cw,round(cx*ow-cw/2)))
            y=max(0,min(oh-ch,round(cy*oh-ch/2)))
            frame=cv2.resize(img[y:y+ch,x:x+cw],(W,H),interpolation=cv2.INTER_AREA)
        if idx==0 and k<int(2.5*FPS):
            a1=min(.68,k/(FPS*.5)*.68)
            dark=np.zeros_like(frame)
            cv2.rectangle(dark,(0,85),(W,270),(17,17,20),-1)
            frame=cv2.addWeighted(frame,1-a1,dark,a1,0)
            cv2.putText(frame,"DESTRUCTION",(62,159),cv2.FONT_HERSHEY_SIMPLEX,1.35,(239,230,215),2,cv2.LINE_AA)
            cv2.putText(frame,"THOMAS COLE  |  1836",(64,209),cv2.FONT_HERSHEY_SIMPLEX,.67,(219,209,192),1,cv2.LINE_AA)
        proc.stdin.write(frame.tobytes())
        if k==count//2: contact.append(cv2.resize(frame,(216,384),interpolation=cv2.INTER_AREA))
    timeline.append({"subject_for_human_review":name,"seconds":seconds,"camera_from":a,"camera_to":b})
proc.stdin.close()
if proc.wait()!=0:raise RuntimeError("FFmpeg rendering failed")
sheet=np.full((4*384,4*216,3),19,dtype=np.uint8)
for idx,frame in enumerate(contact):
    row,col=divmod(idx,4)
    sheet[row*384:(row+1)*384,col*216:(col+1)*216]=frame
cv2.imwrite(str(out/"CONTATTO_REGIA.jpg"),sheet)
rights={"work":"The Course of Empire: Destruction","artist":"Thomas Cole","year":1836,"collection":"New-York Historical","inventory":"1858.4","height_cm":100.3,"width_cm":161.2,"museum_object":"https://emuseum.nyhistory.org/objects/41597/the-course-of-empire-destruction","source_page":page,"source_url":source_url,"original_source_sha1":sha1,"original_source_sha256":sha(source),"original_source_bytes":source.stat().st_size,"source_pixels":[8917,5532],"license_claim":"Wikimedia Commons Public Domain Mark 1.0 / faithful PD-Art image","italian_territorial_commercial_review":"PENDING","publication_allowed":False,"museum_reconstruction":"none","audio":"original locally synthesized score"}
(out/"FONTI_E_DIRITTI.json").write_text(json.dumps(rights,ensure_ascii=False,indent=2),encoding="utf8")
(out/"STORYBOARD_REGIA.json").write_text(json.dumps({"variant":"cinema_standard","total_s":duration,"shots":timeline,"human_visual_review":"PENDING","semantic_crop_review":"PENDING","uses_actual_painting":True},indent=2),encoding="utf8")
posts={"public_title":"Destruction — Thomas Cole (1836)","facebook":"Una città poderosa si disintegra tra tempesta, fuoco e guerra. Thomas Cole dipinge Destruction nel 1836: il quarto capitolo di The Course of Empire. #ArtHistory #ThomasCole","instagram":"Un ponte, la folla in fuga, le fiamme: Destruction (1836), Thomas Cole. Ogni dettaglio racconta il collasso di una civiltà. #Painting #ArtHistory","tiktok":"Questa città non è mai esistita. Ma la sua fine sembra terribilmente reale. Thomas Cole, 1836. #ArtTok #History","youtube_shorts":"Destruction (1836): Thomas Cole mostra un impero immaginario che crolla nella guerra. Scene ricavate dall'opera autentica.","credits":"Thomas Cole, The Course of Empire: Destruction, 1836, New-York Historical 1858.4; faithful Commons reproduction, PDM/PD-Art. Territorial rights check pending. Original synthesized soundtrack."}
(out/"SOCIAL_POSTS.json").write_text(json.dumps(posts,ensure_ascii=False,indent=2),encoding="utf8")
(out/"ISTRUZIONI.md").write_text("Private technical review only. Original painting and original soundtrack. Human artistic/semantic and territorial commercial rights review PENDING. No Gold, no publication, no modification to any master; secondary-30 queue only; this does NOT re-render the legacy five-painting Cole film.\n",encoding="utf8")
print("MP4_RENDERED",sha(out/"VIDEO_REVIEW.mp4"),flush=True)
