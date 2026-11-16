#!/usr/bin/env python3
"""ArtVision | Moreau Oedipus and the Sphinx, 1864 | NEW original Cinema Standard.

Official Met Open Access original (object 437153, accession 21.134.1).
Music from verified 20-recording pool is added by the GitHub workflow.
NO alternate TTS, Gacrux changes, AI-generated painting detail, Museum
simulation, paid APIs, Gold or publication. A single distinct review master.
"""
from __future__ import annotations
import hashlib, json, math, subprocess, urllib.parse, urllib.request, zipfile
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"output/artvision-moreau-oedipus-sphinx-cinema-20261116"
OUT.mkdir(parents=True,exist_ok=True)
OBJECT_ID=437153
OBJECT_PAGE="https://www.metmuseum.org/art/collection/search/437153"
API="https://collectionapi.metmuseum.org/public/collection/v1/objects/437153"
UA="ArtVisionOriginalCinema/1.0 (+https://github.com/GGIANLUCAA/Tra-le-pagine-)"
FPS=20;W=900;H=1600
# Exact painting-relative subjects; their relationship is visible at original
# dimensions. Source only, no hallucinated faces, zooms or digitally invented
# museum. Norm x/y is centre in the actual original image.
SHOTS=[
 ("A face-to-face encounter; reveal artwork",3.5,None,None,"full"),
 ("The entire monumental, narrow painting",4.8,None,None,"full"),
 ("The Sphinx raises her face toward Oedipus",5.0,(.46,.405,.57),(.49,.410,.52),"move"),
 ("Locked eyes; silent challenge",4.7,(.58,.405,.56),(.58,.410,.50),"hold"),
 ("The Sphinx's feathered wings",4.8,(.29,.405,.58),(.28,.425,.54),"move"),
 ("Her lion claws grip Oedipus",4.7,(.53,.59,.56),(.55,.575,.49),"move"),
 ("Oedipus stands firm",4.8,(.72,.425,.68),(.71,.425,.64),"hold"),
 ("His right hand holds the staff",4.5,(.86,.265,.50),(.82,.300,.47),"move"),
 ("The rocky narrow pass",4.0,(.76,.115,.65),(.80,.160,.61),"move"),
 ("Shadows and abandoned traces of victims",5.3,(.37,.825,.59),(.40,.835,.54),"move"),
 ("Fragments near the lower ground",4.4,(.39,.91,.48),(.43,.89,.46),"hold"),
 ("Their gaze again, within the same picture",5.0,(.57,.414,.66),(.57,.41,.61),"move"),
 ("The full artwork and considered ending",6.0,None,None,"full"),
]
N=sum(round(d*FPS) for _,d,*_ in SHOTS)
DURATION=N/FPS
assert 55<DURATION<68 and len(SHOTS)==13

def sha(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""):h.update(b)
 return h.hexdigest()
def get(url,limit=42000000,timeout=140):
 req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json,image/jpeg,*/*"})
 with urllib.request.urlopen(req,timeout=timeout) as r:
  d=r.read(limit+1)
  if len(d)>limit:raise ValueError("Source unexpectedly large")
  return d
def run(args):
 r=subprocess.run([str(a) for a in args],capture_output=True,timeout=220)
 if r.returncode:raise RuntimeError(r.stderr.decode(errors="replace")[-1400:])
 return r.stdout

meta=json.loads(get(API,1000000,45))
assert meta.get("objectID")==OBJECT_ID and meta.get("isPublicDomain") is True
assert meta.get("accessionNumber")=="21.134.1"
assert meta.get("artistDisplayName")=="Gustave Moreau"
assert "Sphinx" in meta.get("title","")
assert meta.get("objectDate")=="1864"
url=meta.get("primaryImage","")
assert isinstance(url,str) and urllib.parse.urlparse(url).hostname=="images.metmuseum.org"
raw=get(url,45000000)
assert raw[:2]==b"\xff\xd8" and len(raw)>200000
orig=OUT/"MET_ORIGINAL_ARTWORK.jpg";orig.write_bytes(raw)
with Image.open(orig) as im:
 im.load()
 assert im.format=="JPEG" and min(im.size)>=1250
 raw_dims=list(im.size)
 print("EXACT_MET_OBJECT_OPEN_ACCESS",OBJECT_ID,"BYTES",len(raw),"PIXELS",raw_dims,"SHA256",sha(orig),flush=True)
 img=im.convert("RGB")
img.thumbnail((4500,6800),Image.Resampling.LANCZOS)
# The painting is unusually tall; do not artificially widen or distort it.
src=np.asarray(img)[:,:,::-1].copy()
ih,iw=src.shape[:2]
assert .45<iw/ih<.60, "Unrecognised Met image shape"
blur=cv2.GaussianBlur(cv2.resize(src,(W,H)),(0,0),49)
blur=cv2.convertScaleAbs(blur,alpha=.19)
fw=min(W-30,round((H-170)*iw/ih))
fh=round(fw*ih/iw)
if fh>H-175:
 fh=H-175;fw=round(fh*iw/ih)
full=blur.copy()
x=(W-fw)//2;y=(H-fh)//2
cv2.rectangle(full,(x-6,y-6),(x+fw+6,y+fh+6),(8,10,11),-1)
full[y:y+fh,x:x+fw]=cv2.resize(src,(fw,fh),interpolation=cv2.INTER_AREA)
cv2.rectangle(full,(x-2,y-2),(x+fw+2,y+fh+2),(130,110,81),2)

def detail(p):
 cx,cy,hi=p
 hh=max(350,min(ih,round(ih*hi)))
 ww=round(hh*W/H)
 if ww>iw:
  ww=iw;hh=round(ww*H/W)
 xx=max(0,min(iw-ww,round(cx*iw-ww/2)))
 yy=max(0,min(ih-hh,round(cy*ih-hh/2)))
 crop=src[yy:yy+hh,xx:xx+ww]
 return cv2.resize(crop,(W,H),interpolation=cv2.INTER_AREA if ww>=W else cv2.INTER_CUBIC)

def smooth(t):
 return t*t*(3-2*t)
def title_overlay(base,seconds):
 if seconds>=3.15:return base
 base=base.copy()
 strength=min(1,seconds/.35,max(0,(3.15-seconds)/.55))
 panel=base.copy()
 cv2.rectangle(panel,(27,58),(W-27,209),(12,16,20),-1)
 base=cv2.addWeighted(panel,.78*strength,base,1-.78*strength,0)
 f="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
 image=Image.fromarray(cv2.cvtColor(base,cv2.COLOR_BGR2RGB))
 d=ImageDraw.Draw(image)
 title="OEDIPUS AND THE SPHINX"
 font=ImageFont.truetype(f,36)
 sub=ImageFont.truetype(f,23)
 d.text((W/2,102),title,font=font,anchor="mm",fill=(240,232,217))
 d.text((W/2,167),"GUSTAVE MOREAU  ·  1864",font=sub,anchor="mm",fill=(202,189,161))
 return cv2.cvtColor(np.asarray(image),cv2.COLOR_RGB2BGR)

# Avoid hard cuts between wildly distant subjects; keep moderate hold duration,
# dissolve only during the first 0.24 seconds (not repetitive "flash" montages).
silent=OUT/"VIDEO_SILENT_HQ_REVIEW.mp4"
cmd=["ffmpeg","-hide_banner","-loglevel","error","-y",
 "-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0",
 "-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",
 "-movflags","+faststart",silent]
proc=subprocess.Popen([str(v) for v in cmd],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
cursor=0.0
timeline=[]
contact=[]
prior_frame=None
try:
 for k,(label,dur,start,end,mode) in enumerate(SHOTS):
  count=round(dur*FPS)
  for i in range(count):
   t=i/max(1,count-1);e=smooth(t)
   if mode=="full":
    f=full.copy()
   else:
    if mode=="hold":
     e=.25+.50*e
    p=tuple(start[j]+(end[j]-start[j])*e for j in range(3))
    f=detail(p)
   # At most 0.3s crossfade when a scene changes, no flashes.
   ramp=min(6,count//4)
   if prior_frame is not None and i<ramp:
    alpha=smooth((i+1)/(ramp+1))
    f=cv2.addWeighted(prior_frame,1-alpha,f,alpha,0)
   if k==0:
    f=title_overlay(f,i/FPS)
   if k==len(SHOTS)-1 and i>=count-round(1.2*FPS):
    alpha=min(.7,max(0,(i-(count-round(1.2*FPS)))/max(1,round(1.2*FPS))))
    f=cv2.convertScaleAbs(f,alpha=1-alpha)
   if i==count//2:contact.append((round(cursor+i/FPS,1),cv2.resize(f,(225,400))))
   proc.stdin.write(np.ascontiguousarray(f).tobytes())
   if i==count-1:prior_frame=f.copy()
  timeline.append({"scene":k+1,"description":label,"start_s":round(cursor,3),"end_s":round(cursor+count/FPS,3),
                   "artwork_only":True,"semantic_position":"from verified original artwork","editorial_review":"PENDING"})
  cursor+=count/FPS
 proc.stdin.close()
 err=proc.stderr.read()
 if proc.wait()!=0:raise RuntimeError(err.decode(errors="replace")[-1800:])
except BaseException:
 proc.kill()
 raise

sheet=np.full((4*427,4*239,3),17,dtype=np.uint8)
for k,(secs,frame) in enumerate(contact):
 xx=k%4*239+6;yy=k//4*427+5
 sheet[yy:yy+400,xx:xx+225]=frame
 cv2.putText(sheet,f"{k+1:02d} / {secs:0.1f}s",(xx+6,yy+418),cv2.FONT_HERSHEY_SIMPLEX,.50,(235,221,198),1,cv2.LINE_AA)
contact_file=OUT/"CONTACT_SHEET.jpg";cv2.imwrite(str(contact_file),sheet)
cover=OUT/"COVER.jpg"
cover_image=Image.fromarray(cv2.cvtColor(title_overlay(full.copy(),.5),cv2.COLOR_BGR2RGB))
cover_image.save(cover,format="JPEG",quality=93)

run(["ffmpeg","-v","error","-xerror","-i",silent,"-map","0:v:0","-f","null","-"])
assert silent.stat().st_size>120000 and abs(cursor-DURATION)<.05, (silent.stat().st_size,cursor,DURATION)
rights={
 "title":"Oedipus and the Sphinx","artist":"Gustave Moreau","date":"1864",
 "institution":"Metropolitan Museum of Art","collection":"European Paintings","met_object_id":OBJECT_ID,
 "accession":"21.134.1","object_url":OBJECT_PAGE,"source_api":API,
 "source_image_url":url,"source_image_sha256":sha(orig),
 "source_original_bytes":len(raw),"source_original_pixels":raw_dims,
 "original_artwork_is_public_domain":True,"exact_api_isPublicDomain":True,
 "image_rights":"Met Open Access public-domain item: official API isPublicDomain true; verify terms for each publishing territory",
 "physical_cm":[206.4,104.8],
 "cinema_only":True,"voice_used":False,"allowed_future_narration":"Only original owner-approved Gemini Gacrux",
 "source_verified_against_official_API":True,"ai_generated_painting_or_frame":False,
 "paid_api_calls":0,"published":False,"gold":False,"human_artistic_review":"PENDING"}
(OUT/"SOURCES_RIGHTS.json").write_text(json.dumps(rights,ensure_ascii=False,indent=2)+"\n","utf8")
(OUT/"STORYBOARD.json").write_text(json.dumps({
 "scene_count":len(SHOTS),"seconds":DURATION,"fps":FPS,"timeline":timeline,
 "no_narrator":True,"music":"Assigned in separate V330 verification step",
 "corresponding_object":"21.134.1",
 "commercial_publish":"NOT YET REVIEWED"},ensure_ascii=False,indent=2)+"\n","utf8")
(OUT/"SOCIAL_COPY_DRAFTS.json").write_text(json.dumps({
 "facebook":"Uno sguardo sospeso sul bordo della vita: Edipo fronteggia la Sfinge. Gustave Moreau, Oedipus and the Sphinx (1864), Metropolitan Museum of Art, 21.134.1. L'enigma resta sospeso nell'aria. #ArtVision #Moreau",
 "instagram":"Non è un abbraccio: è una sfida mortale. La Sfinge aggrappata a Edipo. Oedipus and the Sphinx, Gustave Moreau (1864). The Met. #ArtHistory #Moreau #Mythology",
 "tiktok":"Una domanda, una risposta, la vita in gioco. Guarda gli occhi della Sfinge. Gustave Moreau, 1864.",
 "youtube":"Oedipus and the Sphinx (1864) — Gustave Moreau | ArtVision Cinema Standard. Dipinto originale del Metropolitan Museum of Art, Open Access, inv. 21.134.1.",
 "music_credits":"Add final verified V330 track license+ISRC from MUSIC_V330_PROOF.json",
 "status":"DRAFT_NEVER_AUTO_POST"},ensure_ascii=False,indent=2)+"\n","utf8")
(OUT/"QA_PREMUSIC.json").write_text(json.dumps({
 "title":"Oedipus and the Sphinx","variant":"cinema_standard",
 "duration_seconds":DURATION,"fps":FPS,"scene_count":len(SHOTS),
 "resolution":[W,H],"silent_master_sha256":sha(silent),"original_art_sha256":sha(orig),
 "met_open_access":True,"new_subject_not_existing_checkpoint":True,
 "silent_master_ffmpeg_full_decode":"PASS",
 "human_artistic_review":"PENDING","published":False,"gold":False,
 "voice_not_synthesized":True,"paid_calls":0},indent=2)+"\n","utf8")
print("MOREAU_OEDIPUS_NEW_SILENT_CINEMA_REAL",json.dumps({
 "duration":DURATION,"source_SHA":sha(orig),"mp4_silent_SHA":sha(silent),
 "original_dimensions":raw_dims,"frames":N,"scene_count":len(SHOTS),
 "source_isPublicDomain":True,"rights":"PENDING_FINAL","no_TTS":True}),flush=True)
