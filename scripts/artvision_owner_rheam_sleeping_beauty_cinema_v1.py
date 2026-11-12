#!/usr/bin/env python3
"""Rheam The Sleeping Beauty: one new source-locked Cinema Standard private review.
No paid providers, no fictional museum, no new voice and no publishing.
"""
from pathlib import Path
import hashlib, io, json, math, subprocess, urllib.parse, urllib.request, wave, zipfile
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
OUT=Path("output/artvision-owner-rheam-sleeping-beauty-v1"); OUT.mkdir(parents=True,exist_ok=True)
FILENAME="Henry meynell rheam the sleeping beauty2024 CKS 22681 0006 000(120158).jpg"
PAGE="https://commons.wikimedia.org/wiki/File:Henry_meynell_rheam_the_sleeping_beauty2024_CKS_22681_0006_000%28120158%29.jpg"
URL="https://upload.wikimedia.org/wikipedia/commons/8/8d/Henry_meynell_rheam_the_sleeping_beauty2024_CKS_22681_0006_000%28120158%29.jpg"
OBJECT="https://www.christies.com/lot/lot-6486205"
EXPECTED_PIXELS=(3200,1987)
USER_AGENT="ArtVisionPrivateReview/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-; exact source provenance research)"
def fetch(url,limit):
    req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT})
    with urllib.request.urlopen(req,timeout=90) as r:return r.read(limit)
def digest(raw):return hashlib.sha256(raw).hexdigest()
def check(command):
    p=subprocess.run([str(x) for x in command],capture_output=True)
    if p.returncode:raise RuntimeError(p.stderr.decode(errors="replace")[-2200:])
    return p.stdout
# Independently compare the received original bytes with Commons's exact-file metadata.
api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|sha1|size|mime|extmetadata","titles":"File:"+FILENAME})
evidence={}
try:
    d=json.loads(fetch(api,3_000_000))
    info=next(iter(d["query"]["pages"].values()))["imageinfo"][0]
    assert info["mime"]=="image/jpeg"
    assert (info["width"],info["height"])==EXPECTED_PIXELS
    assert info["size"]>1000000 and info["size"]<5000000
    assert "Public Domain" in json.dumps(info["extmetadata"]) or "PD-Art" in json.dumps(info["extmetadata"])
    evidence={"sha1":info["sha1"].lower(),"size":info["size"],"source":"Commons imageinfo exact file","mime":info["mime"]}
except Exception as exc:
    # Never manufacture official provenance. A known canonical original URL is
    # separately acceptable for an unpublished trial, but blocks final release.
    print("COMMONS_API_UNAVAILABLE_PRIVATE_TRIAL_ONLY",repr(exc)[:220],flush=True)
    evidence={"sha1":None,"size":None,"source":"canonical Commons path + downloaded bytes; API not independently corroborated"}
raw=None
for u in (URL,"https://commons.wikimedia.org/wiki/Special:Redirect/file/"+urllib.parse.quote(FILENAME.replace(" ","_"),safe="-_.()")):
    try:
        b=fetch(u,6_000_000)
        if len(b)<1000000 or len(b)>5000000:raise ValueError("Unexpected source file size")
        with Image.open(io.BytesIO(b)) as im:
            if im.format!="JPEG" or im.size!=EXPECTED_PIXELS:raise ValueError("Wrong picture identity/pixels")
            im.verify()
        if evidence["sha1"] and hashlib.sha1(b).hexdigest()!=evidence["sha1"]:raise ValueError("Commons SHA1 mismatch")
        if evidence["size"] and len(b)!=evidence["size"]:raise ValueError("Commons byte count mismatch")
        raw=b; evidence["url_used"]=u
        break
    except Exception as e:print("SOURCE_ATTEMPT_FAILED",type(e).__name__,str(e)[:130],flush=True)
if raw is None:raise RuntimeError("EXACT_HIGH_RES_SOURCE_FAILED_DO_NOT_RENDER")
(OUT/"SOURCE_ORIGINAL.jpg").write_bytes(raw)
evidence.update({"download_sha256":digest(raw),"download_sha1":hashlib.sha1(raw).hexdigest(),"bytes":len(raw),"pixels":EXPECTED_PIXELS})
print("EXACT_ORIGINAL_VERIFIED",json.dumps(evidence),flush=True)

# Different focal ideas, held long enough for a human eye to read, not AI-transformed imagery.
SHOTS=[
 ("WHOLE WORK — THE SLEEPING BEAUTY",4.5,None,None),
 ("THE WATCHFUL YOUNG MAN",4.1,(.31,.22,.31),(.34,.23,.29)),
 ("THE SLEEPING WOMAN",4.8,(.32,.43,.32),(.33,.45,.30)),
 ("AN OUTSTRETCHED HAND",4.1,(.15,.31,.31),(.17,.34,.29)),
 ("CARVED WOODEN BED",4.2,(.14,.65,.32),(.15,.63,.30)),
 ("BLUE AND GREEN FABRICS",4.3,(.56,.66,.32),(.55,.70,.29)),
 ("THE ROSES AND VINES",4.8,(.83,.31,.32),(.81,.37,.30)),
 ("THE SLEEPING WOMAN'S HAND",4.3,(.43,.51,.31),(.43,.54,.29)),
 ("PETALS ON THE FLOOR",4.1,(.36,.87,.33),(.36,.85,.30)),
 ("WIDE RETURN — NOTHING MOVES",6.4,None,None),
]
FPS=20;W,H=720,1280
counts=[round(d*FPS) for _,d,_,_ in SHOTS];N=sum(counts);D=N/FPS
assert 43<=D<=50 and N==sum(counts)
# Self-composed quiet score from raw waveforms, no licensed recording, no melody imitation.
SR=22050;num=round((D+.2)*SR)
ts=np.arange(num)/SR;music=np.zeros((num,2),np.float64)
triads=[(146.83,174.61,220),(130.81,164.81,196),(123.47,146.83,185),(130.81,164.81,220)]
for j,start in enumerate(np.arange(0,D,6.8)):
    begin=int(start*SR);end=min(num,int((start+8.2)*SR))
    if end<=begin:continue
    local=ts[begin:end]-start
    env=np.clip(local/1.2,0,1)*np.clip(((end-begin)/SR-local)/2.4,0,1)
    for k,f in enumerate(triads[j%len(triads)]):
        tone=(np.sin(2*np.pi*f*local)+.12*np.sin(2*np.pi*f*2.002*local))*.016/(1+.35*k)*env
        music[begin:end,0]+=tone
        music[begin:end,1]+=tone*(.87+.02*k)
    music[begin:end]+=((np.sin(2*np.pi*55*local)*np.exp(-2.6*local)*.01)[:,None])
music*=np.clip(ts/1.4,0,1)[:,None]*np.clip((D-ts)/3.0,0,1)[:,None]
with wave.open(str(OUT/"ORIGINAL_SCORE.wav"),"wb") as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
    w.writeframes((np.tanh(music*1.45)*32767).astype("<i2").tobytes())

art=cv2.imdecode(np.frombuffer(raw,dtype=np.uint8),cv2.IMREAD_COLOR)
assert art is not None and art.shape[:2]==(1987,3200)
AH,AW=art.shape[:2]
blur=cv2.GaussianBlur(cv2.resize(art,(W,H)),(0,0),39)
whole=cv2.convertScaleAbs(blur,alpha=.27)
iw=W-38;ih=int(iw*AH/AW);left=(W-iw)//2;top=(H-ih)//2
whole[top:top+ih,left:left+iw]=cv2.resize(art,(iw,ih),interpolation=cv2.INTER_AREA)
def subject(coords):
    x,y,z=coords
    # The portrait crop cannot exceed painting height; moves the camera, not the art.
    cw=min(AW,max(320,round(AW*z)))
    ch=min(AH,round(cw*H/W))
    cw=min(AW,round(ch*W/H))
    xx=max(0,min(AW-cw,round(x*AW-cw/2)))
    yy=max(0,min(AH-ch,round(y*AH-ch/2)))
    return cv2.resize(art[yy:yy+ch,xx:xx+cw],(W,H),interpolation=cv2.INTER_AREA)

cover=whole.copy()
cv2.rectangle(cover,(0,95),(W,210),(15,20,22),-1)
cv2.putText(cover,"THE SLEEPING BEAUTY",(34,162),cv2.FONT_HERSHEY_SIMPLEX,.75,(231,227,216),2,cv2.LINE_AA)
cv2.imwrite(str(OUT/"COVER.jpg"),cover,[cv2.IMWRITE_JPEG_QUALITY,91])
proc=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0","-i",str(OUT/"ORIGINAL_SCORE.wav"),"-map","0:v:0","-map","1:a:0","-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p","-c:a","aac","-b:a","128k","-shortest","-movflags","+faststart",str(OUT/"VIDEO_ANDROID.mp4")],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
contact=[];story=[];current=0
try:
    for idx,((name,dur,a,b),count) in enumerate(zip(SHOTS,counts)):
        for i in range(count):
            q=i/max(1,count-1);ease=q*q*(3-2*q)
            if a is None:frame=whole.copy()
            else:frame=subject(tuple(a[k]+(b[k]-a[k])*ease for k in range(3)))
            if idx==0 and i<40:
                # small calm title, disappears quickly; no permanent watermark.
                alpha=.66*max(0,min(1,i/8,(40-i)/9))
                overlay=frame.copy()
                cv2.rectangle(overlay,(0,95),(W,205),(14,19,22),-1)
                frame=cv2.addWeighted(frame,1-alpha,overlay,alpha,0)
                cv2.putText(frame,"THE SLEEPING BEAUTY",(35,162),cv2.FONT_HERSHEY_SIMPLEX,.75,(232,224,210),2,cv2.LINE_AA)
            if i==count//2:contact.append(cv2.resize(frame,(180,320)))
            proc.stdin.write(np.ascontiguousarray(frame).tobytes())
        story.append({"shot":idx+1,"description":name,"start_s":round(current,2),"duration_s":count/FPS,"human_visual_review":"PENDING"})
        current+=count/FPS
    proc.stdin.close();error=proc.stderr.read()
    if proc.wait():raise RuntimeError(error.decode(errors="replace")[-1500:])
except Exception:
    proc.kill();raise
sheet=np.full((3*335,4*188,3),19,np.uint8)
for idx,frame in enumerate(contact):
    x=idx%4*188+4;y=idx//4*335+4
    sheet[y:y+320,x:x+180]=frame
cv2.imwrite(str(OUT/"CONTACT_SHEET.jpg"),sheet)
video=OUT/"VIDEO_ANDROID.mp4"
check(["ffmpeg","-v","error","-xerror","-i",video,"-map","0","-f","null","-"])
probe=json.loads(check(["ffprobe","-v","error","-show_format","-show_streams","-of","json",video]))
v=[s for s in probe["streams"] if s.get("codec_type")=="video"]
a=[s for s in probe["streams"] if s.get("codec_type")=="audio"]
assert len(v)==1 and v[0]["codec_name"]=="h264" and v[0]["width"]==W and v[0]["height"]==H
assert len(a)==1 and a[0]["codec_name"]=="aac"
assert abs(float(probe["format"]["duration"])-D)<.4
(OUT/"FFPROBE.json").write_text(json.dumps(probe,indent=2))
rights={"title":"The Sleeping Beauty","artist":"Henry Meynell Rheam","year":1899,
 "object":"Christie's London, June 2024 lot 6486205; 75.6 x 121.9cm; photographed work not presented as gallery",
 "source_page":PAGE,"object_page":OBJECT,"source_provenance":evidence,
 "image_rights":"Wikimedia Commons PD-Art/PDM statement; Christie photograph and territorial commercial distribution require separate review",
 "review_only":True,"commercial_rights_final":"PENDING","publication_authorized":False,
 "music":"original synthesized score, not sampled or borrowed", "artwork_is_not_ai_reconstructed":True}
(OUT/"SOURCES_RIGHTS.json").write_text(json.dumps(rights,indent=2,ensure_ascii=False))
(OUT/"STORYBOARD.json").write_text(json.dumps({"duration_s":D,"scenes":story,"human_full_speed_review":"PENDING"},indent=2))
posts={"title":"The Sleeping Beauty — Henry Meynell Rheam (1899)","facebook":"A prince reaches towards a sleeping girl, surrounded by carved wood and flowering roses. Henry Meynell Rheam, The Sleeping Beauty, 1899. A dreamlike watercolor with extraordinary blue fabric.","instagram":"The roses have grown around her. The blue fabric seems almost alive. The Sleeping Beauty, 1899. #ArtHistory","tiktok":"A fairytale frozen in blue, flowers, and silence. The Sleeping Beauty (1899). #ArtTok","youtube":"The Sleeping Beauty — Henry Meynell Rheam. An original visual journey inside the 1899 watercolor. Credits and image reuse terms in the archive.","status":"DRAFT_ONLY_NOT_PUBLISHED"}
(OUT/"SOCIAL_DRAFTS.json").write_text(json.dumps(posts,indent=2,ensure_ascii=False))
qa={"status":"ONE_REAL_NEW_PRIVATE_CINEMA_MP4_NEEDS_ARTISTIC_AND_RIGHTS_REVIEW","painting":"The Sleeping Beauty","artist":"Henry Meynell Rheam",
 "variant":"cinema_standard","source_sha256":evidence["download_sha256"],"source_sha1":evidence["download_sha1"],
 "source_image_pixels":list(EXPECTED_PIXELS),"video_sha256":digest(video.read_bytes()),"video_bytes":video.stat().st_size,
 "duration_s":D,"frame_count":N,"fps":FPS,"resolution":[W,H],"shots":len(SHOTS),
 "ffmpeg_full_decode":"PASS","gold":False,"published":False,"paid_calls":0,"territorial_rights":"PENDING","human_artistic_review":"PENDING",
 "original_ten_queue_slots_added":0,"future_thirty_new_cinema_slot":1}
(OUT/"QA_TECHNICAL.json").write_text(json.dumps(qa,indent=2))
zip_file=OUT/"ANDROID_REVIEW_PACKAGE.zip"
with zipfile.ZipFile(zip_file,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=3) as z:
    for name in ("VIDEO_ANDROID.mp4","COVER.jpg","CONTACT_SHEET.jpg","FFPROBE.json","QA_TECHNICAL.json","SOURCES_RIGHTS.json","STORYBOARD.json","SOCIAL_DRAFTS.json"):
        z.write(OUT/name,arcname=name)
with zipfile.ZipFile(zip_file) as z:
    assert z.testzip() is None
    assert digest(z.read("VIDEO_ANDROID.mp4"))==qa["video_sha256"]
print("PRODUCED",json.dumps({"video_sha256":qa["video_sha256"],"zip_sha256":digest(zip_file.read_bytes()),"frames":N,"duration":D,"full_decode":"PASS","crc":"PASS","gold":False}),flush=True)
