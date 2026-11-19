#!/usr/bin/env python3
"""ArtVision | NEW The Love Song — Sir Edward Burne-Jones (1868–77), Met 435826.

Original Met Open Access image only. Private Cinema Standard review, 13
hand-choreographed real-painting shots, no alternative voice/TTS, no API spend.
Music from fixed-20 catalogue inserted by CI only after binary/license check.
"""
from __future__ import annotations
import hashlib,json,subprocess,urllib.parse,urllib.request,zipfile
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"output/artvision-burnejones-love-song-cinema-20261119"
OUT.mkdir(parents=True,exist_ok=True)
OBJECT=435826
API="https://collectionapi.metmuseum.org/public/collection/v1/objects/435826"
PAGE="https://www.metmuseum.org/art/collection/search/435826"
UA="ArtVision-Cinema/1.0 (GGIANLUCAA Tra-le-pagine-; Met OpenAccess CC0)"
W,H,FPS=900,1600,18
# Label, seconds, start (x,y, height_fraction), end, visual mode.
# Coordinates refer to the exact Met painting, left knight, central musician,
# right Cupid at the bellows, organ pipes, flowers and old city in background.
SHOTS=[
 ("The love song — three figures",3.5,None,None,"whole"),
 ("One painting: longing, music, love",4.9,None,None,"whole"),
 ("The woman at the organ",4.8,(.425,.43,.64),(.435,.41,.57),"move"),
 ("Her hands at the keys",4.6,(.56,.51,.45),(.565,.50,.42),"move"),
 ("Cupid beside the organ",4.6,(.825,.53,.66),(.83,.54,.61),"move"),
 ("Cupid pumps the bellows",4.5,(.80,.72,.46),(.79,.69,.45),"move"),
 ("A knight waits at left",5.0,(.14,.55,.68),(.15,.54,.62),"move"),
 ("Armor and a hand",4.2,(.18,.76,.46),(.19,.73,.43),"move"),
 ("The distant medieval town",4.3,(.35,.18,.51),(.38,.18,.48),"move"),
 ("Stillness of the green meadow",4.4,(.245,.50,.49),(.29,.49,.46),"move"),
 ("Flowers under the stone terrace",4.4,(.52,.92,.44),(.57,.91,.40),"move"),
 ("Organ pipes divide two worlds",5.3,(.66,.43,.66),(.66,.43,.62),"move"),
 ("Return to the entire artwork",6.4,None,None,"whole"),
]
FRAMES=[round(s[1]*FPS) for s in SHOTS]
DURATION=sum(FRAMES)/FPS
assert 59<DURATION<67 and len(SHOTS)==13

def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for chunk in iter(lambda:f.read(1<<20),b""): h.update(chunk)
 return h.hexdigest()
def run(args,timeout=180):
 p=subprocess.run([str(x) for x in args],capture_output=True,timeout=timeout)
 if p.returncode: raise RuntimeError(p.stderr.decode(errors="replace")[-1800:])
 return p.stdout
def download(url,limit,timeout):
 if not url.startswith("https://"): raise RuntimeError("HTTPS required")
 req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json,image/jpeg,*/*"})
 with urllib.request.urlopen(req,timeout=timeout) as resp:
  data=resp.read(limit+1)
  if not data or len(data)>limit:raise RuntimeError("Unexpected download bytes")
  return data

meta=json.loads(download(API,1_000_000,50))
assert meta.get("objectID")==OBJECT, "Wrong Met object"
assert meta.get("isPublicDomain") is True, "Not actually Met public domain"
assert meta.get("accessionNumber")=="47.26", "Accession does not match the 1868–77 painting"
assert "Burne-Jones" in meta.get("artistDisplayName","")
assert meta.get("title")=="The Love Song", "Wrong titled work or study"
assert "1868" in meta.get("objectDate",""), "Unexpected date"
image_url=meta.get("primaryImage")
assert isinstance(image_url,str) and urllib.parse.urlparse(image_url).hostname=="images.metmuseum.org"
raw=download(image_url,65_000_000,160)
assert len(raw)>300_000 and raw.startswith(b"\xff\xd8")
original=OUT/"ORIGINAL_MET_PAINTING.jpg"
original.write_bytes(raw)
with Image.open(original) as im:
 im.load()
 assert im.format=="JPEG" and min(im.size)>=1400
 imsize=im.size
 painting=im.convert("RGB")
print("LOVE_SONG_OFFICIAL_MET",OBJECT,imsize,len(raw),sha(original),flush=True)
painting.thumbnail((6000,6000),Image.Resampling.LANCZOS)
base=np.asarray(painting)[:,:,::-1].copy()
IH,IW=base.shape[:2]
assert 1.24<IW/IH<1.48, "Original is not the wide painting"
background=cv2.GaussianBlur(cv2.resize(base,(W,H)),(0,0),57)
background=cv2.convertScaleAbs(background,alpha=.23)
wide=background.copy()
fw=min(W-22,round((H-220)*IW/IH))
fh=round(fw*IH/IW)
x=(W-fw)//2;y=(H-fh)//2
cv2.rectangle(wide,(x-8,y-8),(x+fw+8,y+fh+8),(9,11,13),-1)
wide[y:y+fh,x:x+fw]=cv2.resize(base,(fw,fh),interpolation=cv2.INTER_AREA)
cv2.rectangle(wide,(x-3,y-3),(x+fw+3,y+fh+3),(117,98,68),2)

def detail(p):
 cx,cy,fraction=p
 hh=min(IH,max(400,round(IH*fraction)))
 ww=round(hh*W/H)
 if ww>IW:
  ww=IW;hh=round(ww*H/W)
 xx=max(0,min(IW-ww,round(cx*IW-ww/2)))
 yy=max(0,min(IH-hh,round(cy*IH-hh/2)))
 return cv2.resize(base[yy:yy+hh,xx:xx+ww],(W,H),interpolation=cv2.INTER_AREA if ww>W else cv2.INTER_CUBIC)
def smooth(t):return t*t*(3-2*t)
def title_overlay(frame):
 image=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
 drawer=ImageDraw.Draw(image)
 drawer.rounded_rectangle((28,90,W-28,251),radius=13,fill=(11,15,17))
 font="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
 drawer.text((W//2,143),"THE LOVE SONG",font=ImageFont.truetype(font,51),anchor="mm",fill=(239,227,200))
 drawer.text((W//2,218),"EDWARD BURNE-JONES   ·   1868–77",
             font=ImageFont.truetype(font,22),anchor="mm",fill=(205,193,165))
 return cv2.cvtColor(np.asarray(image),cv2.COLOR_RGB2BGR)

video=OUT/"SILENT_MASTER_REVIEW.mp4"
proc=subprocess.Popen(["ffmpeg","-hide_banner","-loglevel","error","-y",
 "-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0",
 "-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",
 "-movflags","+faststart",str(video)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
story=[];contact=[];elapsed=0.0;prior=None
try:
 for seq,(label,seconds,start,end,mode) in enumerate(SHOTS):
  count=FRAMES[seq]
  for j in range(count):
   t=j/max(1,count-1)
   f=wide.copy() if mode=="whole" else detail(tuple(start[z]+(end[z]-start[z])*smooth(t) for z in range(3)))
   if prior is not None and j<5:
    # A short soft bridge, not a 1-second random still.
    f=cv2.addWeighted(prior,1-smooth((j+1)/6),f,smooth((j+1)/6),0)
   if seq==0 and j<round(2.9*FPS):f=title_overlay(f)
   if seq==len(SHOTS)-1 and j>=count-round(1.2*FPS):
    fade=(j-(count-round(1.2*FPS)))/max(1,round(1.2*FPS))
    f=cv2.convertScaleAbs(f,alpha=1-.7*fade)
   if j==count//2:contact.append((elapsed+j/FPS,cv2.resize(f,(225,400))))
   proc.stdin.write(np.ascontiguousarray(f).tobytes())
   if j==count-1:prior=f.copy()
  story.append({"shot":seq+1,"subject":label,"start_s":round(elapsed,3),
                "end_s":round(elapsed+count/FPS,3),
                "source":"Actual Met 435826 picture, not generated",
                "human_creative_review":"PENDING"})
  elapsed+=count/FPS
 proc.stdin.close()
 errors=proc.stderr.read()
 if proc.wait()!=0:raise RuntimeError(errors.decode(errors="replace")[-1800:])
except BaseException:
 proc.kill()
 raise
assert video.is_file() and video.stat().st_size>250000
assert abs(elapsed-DURATION)<.06
run(["ffmpeg","-v","error","-xerror","-i",video,"-map","0:v:0","-f","null","-"])
contact_sheet=np.full((4*417,4*235,3),17,np.uint8)
for i,(t,frame) in enumerate(contact):
 xx=i%4*235+5;yy=i//4*417+4
 contact_sheet[yy:yy+400,xx:xx+225]=frame
 cv2.putText(contact_sheet,f"{i+1:02d} / {t:.1f}s",(xx+8,yy+412),cv2.FONT_HERSHEY_SIMPLEX,.50,(238,232,216),1,cv2.LINE_AA)
cv2.imwrite(str(OUT/"CONTACT_SHEET.jpg"),contact_sheet)
cover=title_overlay(wide.copy())
cv2.imwrite(str(OUT/"COVER.jpg"),cover)
rights={"artist":"Sir Edward Burne-Jones","title":"The Love Song","date":"1868–1877",
 "museum":"Metropolitan Museum of Art","met_object_id":435826,"accession":"47.26",
 "object_page":PAGE,"official_api":API,"source_url":image_url,
 "original_sha256":sha(original),"original_bytes":len(raw),"original_pixels":list(imsize),
 "met_api_isPublicDomain":True,"painting_rights":"Met Open Access, public domain",
 "source_image_territory_review":"PENDING before commercial distribution",
 "scenography":"None: authentic painting, Cinema Standard",
 "voice":"NONE (Cinema, not Critico)","Gacrux_voice_changed":False,
 "paid_calls":0,"published":False,"gold":False,"human_artistic_review":"PENDING"}
(OUT/"SOURCE_RIGHTS.json").write_text(json.dumps(rights,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
(OUT/"STORYBOARD.json").write_text(json.dumps({
 "duration_s":DURATION,"scene_count":len(story),"shots":story,
 "global_video_format":"Cinema Standard","human_speed_QA":"PENDING",
 "music":"Actual recording inserted by V330 Music20 step; not in silent source"
},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
(OUT/"SOCIAL_DRAFTS.json").write_text(json.dumps({
 "facebook":"Un cavaliere in armatura ascolta una melodia che sembra fermare il tempo. Davanti a lui una donna suona l'organo, mentre Cupido aziona il mantice. The Love Song (1868–77), Edward Burne-Jones. The Met. #ArtVision",
 "instagram":"Tre personaggi, una musica impossibile da ascoltare. Burne-Jones: The Love Song (1868–77). #ArtHistory #PreRaphaelite",
 "tiktok":"Un cavaliere, Cupido e una melodia capace di incantare. The Love Song — Edward Burne-Jones.",
 "youtube":"The Love Song | Edward Burne-Jones (1868–77) | ArtVision Cinema Standard. Original Metropolitan Museum of Art artwork, Open Access.",
 "music_credits":"PENDING_V330_REAL_TRACK_SELECTION",
 "published":False},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
(OUT/"PRE_MUSIC_QA.json").write_text(json.dumps({
 "status":"REAL_NEW_CINEMA_SILENT_MASTER_SOURCE_VERIFIED",
 "source_art_sha256":sha(original),"source_met_isPublicDomain":True,
 "silent_sha256":sha(video),"silent_duration_s":DURATION,
 "silent_full_ffmpeg_decode":"PASS","fps":FPS,"resolution":[W,H],
 "scene_count":len(SHOTS),"no_TTS":True,"no_billed_API":True,
 "human_review":"PENDING","published":False,"gold":False},indent=2)+"\n",encoding="utf8")
print("BURNE_JONES_LOVE_SONG_REAL_NEW_CINEMA_SILENT_SUCCESS",json.dumps({
 "met_object":OBJECT,"sha":sha(original),"video_sha":sha(video),
 "duration_s":DURATION,"scenes":len(SHOTS),"human_review":"PENDING"}),flush=True)
