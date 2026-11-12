#!/usr/bin/env python3
"""New source-locked 1900 Waterhouse A Mermaid Cinema Standard PRIVATE review.

Never substitute an 1892 sketch, an AI remake, or the Royal Academy's
copyrighted photograph of the physical frame. No TTS, paid calls, Museum claims,
site publication or Gold approval.
"""
from __future__ import annotations
import hashlib,io,json,math,subprocess,urllib.request,wave,zipfile
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"output/artvision-owner-waterhouse-mermaid-cinema-v1"
SOURCE_URL="https://upload.wikimedia.org/wikipedia/commons/1/12/John_William_Waterhouse_-_Mermaid.JPG"
SOURCE_PAGE="https://commons.wikimedia.org/wiki/File:John_William_Waterhouse_-_Mermaid.JPG"
SOURCE_SHA1="e288cc3ad87653593f4a634256bcd595495c08fe"
SOURCE_BYTES=578091
SOURCE_SIZE=(1852,2693)
OFFICIAL_RA="https://www.royalacademy.org.uk/art-artists/work-of-art/a-mermaid"
FRAME_RA="https://www.royalacademy.org.uk/art-artists/work-of-art/frame-for-john-william-waterhouse-ra-a-mermaid"
USER_AGENT="ArtVisionPrivateReview/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-; exact PD-Art file)"

def sha(path:Path)->str:
 h=hashlib.sha256()
 with path.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def cmd(argv):
 p=subprocess.run([str(v) for v in argv],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 if p.returncode:raise RuntimeError(p.stderr.decode(errors="replace")[-2200:])
 return p.stdout

def original():
 req=urllib.request.Request(SOURCE_URL,headers={"User-Agent":USER_AGENT})
 with urllib.request.urlopen(req,timeout=80) as response:
  raw=response.read(SOURCE_BYTES+1)
 if len(raw)!=SOURCE_BYTES:raise ValueError("Original Commons file byte size mismatch")
 if hashlib.sha1(raw).hexdigest()!=SOURCE_SHA1:raise ValueError("Original Commons SHA1 mismatch")
 with Image.open(io.BytesIO(raw)) as pic:
  assert pic.format=="JPEG", "Unexpected media format"
  assert pic.size==SOURCE_SIZE,"Original pixels mismatch; no substitute"
  pic.verify()
 p=OUT/"ORIGINAL_WATERHOUSE_1900.jpg"
 p.write_bytes(raw)
 return p

# Visual dramaturgy follows actual documented canvas; hand, hair, pearls, tail, sea,
# cliffs. Coordinates are candidate crops; full-speed semantic QA remains required.
SCENES=[
 ("HOOK — pearls beside the tail",2.7,(.26,.84,.45),(.27,.82,.41)),
 ("1900 painting — entire composition",4.5,None,None),
 ("gaze toward the surf",4.2,(.59,.32,.47),(.58,.35,.43)),
 ("the hand combing copper hair",4.1,(.25,.45,.49),(.23,.47,.44)),
 ("pearl shell on the pebbles",4.4,(.19,.81,.43),(.19,.80,.38)),
 ("silver scales and the curve of the tail",4.5,(.54,.86,.46),(.55,.86,.40)),
 ("waves brushing the rocks",4.2,(.32,.68,.48),(.30,.67,.42)),
 ("high cliffs and black opening",4.1,(.79,.19,.48),(.76,.20,.45)),
 ("red hair, wind and fingers",4.2,(.32,.52,.47),(.34,.55,.42)),
 ("the distant water under the cliffs",4.1,(.81,.46,.48),(.82,.45,.43)),
 ("reveal the whole shore",4.8,None,None),
 ("return to the silent figure",6.0,None,None)
]
FPS=20
W,H=720,1280
COUNTS=[round(n*FPS) for _,n,_,_ in SCENES]
FRAMES=sum(COUNTS)
DUR=FRAMES/FPS
assert 51<DUR<56 and len(SCENES)==12
OUT.mkdir(parents=True,exist_ok=True)
src=original()
raw=cv2.imread(str(src),cv2.IMREAD_COLOR)
assert raw is not None
ih,iw=raw.shape[:2]
assert (iw,ih)==SOURCE_SIZE
source_hash=sha(src)
print("SOURCE_VERIFIED",SOURCE_BYTES,SOURCE_SHA1,source_hash,flush=True)

def original_music():
 sr=24000
 tt=np.arange(round((DUR+.18)*sr),dtype=np.float64)/sr
 a=np.zeros((len(tt),2),dtype=np.float64)
 # Music is original: nonperiodic wave textures, slowly voiced harmonics and distant
 # soft impacts, no sampled audio, copyrighted composition or synthesized speech.
 progression=[
  (73.416,110.0,146.832),
  (65.406,98.0,130.813),
  (82.407,123.471,164.814),
  (73.416,110.0,164.814),
  (65.406,98.0,146.832),
  (73.416,110.0,146.832)
 ]
 for k,start in enumerate(np.arange(0,DUR,9.5)):
  s=round(start*sr);e=min(len(tt),round((start+10.9)*sr))
  z=tt[s:e]-start
  env=np.minimum(1,z/1.9)*np.minimum(1,np.maximum(0,(e-s)/sr-z)/2.8)
  for j,p in enumerate(progression[k%len(progression)]):
   osc=(np.sin(2*np.pi*p*z+.13*np.sin(2*np.pi*.075*z))+
    .17*np.sin(2*np.pi*(p*2.002)*z+0.4))
   a[s:e,0]+=(.020/(j+1)**.4)*env*osc
   a[s:e,1]+=(.019/(j+1)**.4)*env*np.sin(2*np.pi*p*z+.18+.10*np.sin(2*np.pi*.082*z))
  # subdued, brief low throb at 0 and 4.8 of each phrase
  for beat in (0.,4.8):
   pos=round((start+beat)*sr)
   if pos>=len(tt):continue
   count=min(round(1.4*sr),len(tt)-pos)
   u=np.arange(count)/sr
   throb=.018*np.exp(-5*u)*np.sin(2*np.pi*(62-11*u)*u)
   a[pos:pos+count,:]+=throb[:,None]
 # Very low sea-like wash, deterministic.
 a[:,0]+=.0031*np.sin(2*np.pi*37.2*tt+.32*np.sin(2*np.pi*.3*tt))
 a[:,1]+=.0031*np.sin(2*np.pi*37.4*tt+.44*np.sin(2*np.pi*.28*tt))
 a*=np.minimum(1,tt/1.5)[:,None]*np.minimum(1,np.maximum(0,DUR-tt)/2.6)[:,None]
 a=np.tanh(a*1.2)*.85
 p=OUT/"ORIGINAL_SCORE.wav"
 with wave.open(str(p),"wb") as ww:
  ww.setnchannels(2);ww.setsampwidth(2);ww.setframerate(sr)
  ww.writeframes((a*32767).astype("<i2").tobytes())
 return p

score=original_music()
soft=cv2.GaussianBlur(cv2.resize(raw,(W,H),interpolation=cv2.INTER_AREA),(0,0),45)
wide=cv2.convertScaleAbs(soft,alpha=.30)
f_w=W-24;f_h=round(f_w*ih/iw)
assert f_h<=H-90
ix=(W-f_w)//2;iy=(H-f_h)//2
wide[iy:iy+f_h,ix:ix+f_w]=cv2.resize(raw,(f_w,f_h),interpolation=cv2.INTER_AREA)

def crop(x,y,frac):
 # frac means fraction of original height: the camera moves, not the painting.
 ch=max(550,min(ih,round(ih*frac)))
 cw=min(iw,max(310,round(ch*W/H)))
 xx=max(0,min(iw-cw,round(x*iw-cw/2)))
 yy=max(0,min(ih-ch,round(y*ih-ch/2)))
 return cv2.resize(raw[yy:yy+ch,xx:xx+cw],(W,H),interpolation=cv2.INTER_AREA)

# Editorial cover, no fake museum gallery or AI reimagining.
cover=wide.copy()
cv2.rectangle(cover,(0,58),(W,230),(16,20,24),-1)
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",57)
subfont=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",22)
rgb=Image.fromarray(cv2.cvtColor(cover,cv2.COLOR_BGR2RGB))
draw=ImageDraw.Draw(rgb)
draw.text((W//2,121),"A MERMAID",font=font,fill=(239,230,211),anchor="mm")
draw.text((W//2,188),"JOHN WILLIAM WATERHOUSE  ·  1900",font=subfont,fill=(218,209,191),anchor="mm")
rgb.save(OUT/"COVER.jpg",quality=92)

video=OUT/"VIDEO_ANDROID_REVIEW.mp4"
pipe=subprocess.Popen(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0","-i",str(score),"-map","0:v:0","-map","1:a:0","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","-c:a","aac","-b:a","144k","-shortest","-movflags","+faststart",str(video)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
contact=[];timing=[];elapsed=0.0
try:
 for k,((label,seconds,point_a,point_b),count) in enumerate(zip(SCENES,COUNTS)):
  for j in range(count):
   t=j/max(1,count-1)
   ease=t*t*(3-2*t)
   if point_a is None:frame=wide.copy()
   else:
    pose=[point_a[i]+(point_b[i]-point_a[i])*ease for i in range(3)]
    frame=crop(*pose)
   if k==0 and j>=4 and j<37:
    # Title appears over the pearls, fades out before second scene.
    over=frame.copy()
    alpha=min(.55, .55*(j-4)/12,.55*(37-j)/10)
    cv2.rectangle(over,(0,74),(W,173),(21,20,26),-1)
    frame=cv2.addWeighted(over,max(0,alpha),frame,1-max(0,alpha),0)
    if alpha>.2: cv2.putText(frame,"A MERMAID",(28,137),cv2.FONT_HERSHEY_SIMPLEX,.92,(231,225,211),2,cv2.LINE_AA)
   pipe.stdin.write(np.ascontiguousarray(frame).tobytes())
   if j==count//2:contact.append(cv2.resize(frame,(180,320),interpolation=cv2.INTER_AREA))
  timing.append({"number":k+1,"semantic_candidate":label,"start_s":round(elapsed,2),"duration_s":count/FPS,"visual_review":"PENDING"})
  elapsed+=count/FPS
 pipe.stdin.close();err=pipe.stderr.read()
 if pipe.wait()!=0:raise RuntimeError("ffmpeg encode failed: "+err.decode(errors="replace")[-1100:])
except Exception:
 pipe.kill()
 raise

sheet=np.full((3*336,4*190,3),20,np.uint8)
for i,frm in enumerate(contact):
 x=(i%4)*190+5;y=(i//4)*336+5
 sheet[y:y+320,x:x+180]=frm
cv2.imwrite(str(OUT/"CONTACT_SHEET.jpg"),sheet)
cmd(["ffmpeg","-v","error","-xerror","-i",video,"-map","0","-f","null","-"])
probe=json.loads(cmd(["ffprobe","-v","error","-show_format","-show_streams","-of","json",video]))
v=[s for s in probe["streams"] if s.get("codec_type")=="video"]
a=[s for s in probe["streams"] if s.get("codec_type")=="audio"]
assert len(v)==1 and v[0]["codec_name"]=="h264" and (v[0]["width"],v[0]["height"])==(W,H)
assert len(a)==1 and a[0]["codec_name"]=="aac"
assert abs(float(probe["format"]["duration"])-DUR)<.4
assert int(v[0].get("nb_frames",FRAMES))==FRAMES
(OUT/"FFPROBE.json").write_text(json.dumps(probe,indent=2))
rights={
 "title":"A Mermaid","owner_title":"The Mermaid","artist":"John William Waterhouse","year":1900,
 "museum":"Royal Academy of Arts, London","accession":"03/805","height_cm":96.5,"width_cm":66.6,
 "source_file":SOURCE_PAGE,"image_url":SOURCE_URL,
 "image_sha1":SOURCE_SHA1,"image_sha256":source_hash,"image_bytes":SOURCE_BYTES,"image_pixels":SOURCE_SIZE,
 "photo_terms":"Wikimedia Commons PD-Art/PDM for this original digital file; source photograph secondary territorial terms may apply",
 "artist_died":1917,"commercial_use_review":"PENDING; no site/social publication",
 "frame_reference":FRAME_RA,
 "frame_provenance":"Royal Academy object 04/1571, carved pine, late 17th century modified 19th century, 119.2x89.6x9 cm",
 "frame_photo_license":"ROYAL ACADEMY REQUIRES SEPARATE COMMERCIAL LICENSE; NOT USED IN THIS VIDEO",
 "frame_scene_in_movie":False,"gallery_scene_in_movie":False,"underlying_original_artwork_unchanged":True,
 "music":"new original self-synthesized soundtrack; no borrowed recordings"
}
(OUT/"SOURCE_AND_RIGHTS.json").write_text(json.dumps(rights,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
(OUT/"STORYBOARD.json").write_text(json.dumps({"duration_s":DUR,"fps":FPS,"shots":timing,"human_full_speed_review":"PENDING","source_pixel_identity":"verified SHA1, bytes, dimensions","no_AI_repainting":True},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
posts={
 "title":"A Mermaid — John William Waterhouse (1900)",
 "facebook":"Una figura solitaria, uno specchio d'acqua inquieto e un guscio pieno di perle. In A Mermaid (1900), Waterhouse racconta il mito senza mostrare marinai o navi. Royal Academy of Arts, Londra. #ArtHistory #Waterhouse",
 "instagram":"I capelli ramati, le perle e un mare scuro. Un dettaglio alla volta, dentro A Mermaid di Waterhouse (1900). #ArtHistory #Painting",
 "tiktok":"Guarda le perle ai piedi della sirena. Poi il mare, i capelli e le scogliere. È A Mermaid (1900), John William Waterhouse. #ArtTok",
 "youtube_shorts":"A Mermaid — John William Waterhouse, 1900. A cinematic journey across the authentic painting, set to an original score.",
 "status":"EDITORIAL_DRAFT_ONLY_NOT_POSTED"
}
(OUT/"SOCIAL_DRAFTS.json").write_text(json.dumps(posts,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
qa={"schema":"artvision-owner-waterhouse-mermaid-cinema-v1","one_new_video":True,"variant":"cinema_standard",
 "work":"A Mermaid","artist":"John William Waterhouse",
 "original_file_sha1":SOURCE_SHA1,"original_file_sha256":source_hash,
 "mp4_name":video.name,"mp4_sha256":sha(video),"mp4_bytes":video.stat().st_size,
 "fps":FPS,"frames":FRAMES,"duration_s":DUR,"resolution":[W,H],"shots":len(SCENES),
 "full_ffmpeg_decode":"PASS","territorial_license_final":"PENDING",
 "human_artistic_full_speed_review":"PENDING","real_museum_claim":False,
 "gold":False,"published":False,"paid_api_calls":0,"original_ten_slots_added":0,
 "second_30_cinema_slot_candidates_added":1}
(OUT/"QA_TECHNICAL.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n")
parts=[
 "VIDEO_ANDROID_REVIEW.mp4","COVER.jpg","CONTACT_SHEET.jpg","SOURCE_AND_RIGHTS.json",
 "STORYBOARD.json","SOCIAL_DRAFTS.json","QA_TECHNICAL.json","FFPROBE.json"
]
zfile=OUT/"ANDROID_REVIEW_PACKAGE.zip"
with zipfile.ZipFile(zfile,"w",zipfile.ZIP_DEFLATED,compresslevel=3) as z:
 for name in parts:z.write(OUT/name,arcname=name)
with zipfile.ZipFile(zfile) as z:
 assert z.testzip() is None
 assert hashlib.sha256(z.read(video.name)).hexdigest()==qa["mp4_sha256"]
print("WATERHOUSE_MERMAID_NEW_CINEMA_REVIEW",json.dumps({"video_sha256":qa["mp4_sha256"],"zip_sha256":sha(zfile),"duration_s":DUR,"bytes":qa["mp4_bytes"],"ffmpeg":"PASS","crc":"PASS","gold":False}),flush=True)
