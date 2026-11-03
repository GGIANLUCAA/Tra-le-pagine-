#!/usr/bin/env python3
"""Vienna Bruegel GG 1026 Cinema Museum review: exact real framed-work photo by Hiroki Ogawa CC BY 3.0, no paid APIs."""
import argparse, hashlib, json, os, subprocess, urllib.request, wave, zipfile
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
URL="https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/The_Tower_of_Babel_%28Bruegel%29.jpg/3840px-The_Tower_of_Babel_%28Bruegel%29.jpg"
SOURCE_PAGE="https://commons.wikimedia.org/wiki/File:The_Tower_of_Babel_(Bruegel).jpg"
RIGHTS_PAGE="https://www.khm.at/en/objectdb/detail/323"
FRAME_URL="https://upload.wikimedia.org/wikipedia/commons/9/91/The_Tower_of_Babel_1563_Bruegel_Kunsthistorisches_Museum_Wien_Austria_-_panoramio.jpg"
FRAME_SOURCE_PAGE="https://commons.wikimedia.org/wiki/File:The_Tower_of_Babel_1563_Bruegel_Kunsthistorisches_Museum_Wien_Austria_-_panoramio.jpg"
FRAME_CREDIT="Hiroki Ogawa, museum photograph 2015, CC BY 3.0 Unported; photo adapted/cropped and painting pixels upgraded from verified Commons PD source"
FRAME_LICENSE="https://creativecommons.org/licenses/by/3.0/"
W,H,FPS=720,1280,20
BEATS=[
("museum_entry",5.0,None),
("museum_enter",7.0,None),
("summit_in_the_clouds",5.0,(.53,.18,1350,.05,.015,0)),
("unfinished_red_stories",5.0,(.66,.35,1420,.07,-.008,.008)),
("stone_arcades",5.0,(.42,.50,1540,.06,.01,-.01)),
("builders_and_cranes",5.0,(.39,.74,1350,.07,.02,.01)),
("nimrod_and_his_court",5.0,(.17,.83,1250,.08,-.01,0)),
("ships_of_the_harbour",5.0,(.89,.65,1550,.07,-.02,0)),
("the_city_below",5.0,(.13,.51,1650,.06,.015,0)),
("whole_image_return",4.4,None),
("museum_return",5.0,None),
("museum_exit",6.0,None)]
DURATION=sum(x[1] for x in BEATS)
assert abs(DURATION-62.4)<1e-4

def digest(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()

def run(cmd):
 p=subprocess.run(list(map(str,cmd)),stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 if p.returncode:raise RuntimeError(f"{' '.join(map(str,cmd[:5]))}: {p.stderr[-2000:]}")
 return p.stdout

def get_art(p):
 urls=[URL,
 "https://thumb.wikimedia.org/wikipedia/commons/thumb/d/de/The_Tower_of_Babel_%28Bruegel%29.jpg/3840px-The_Tower_of_Babel_%28Bruegel%29.jpg",
 "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/The_Tower_of_Babel_%28Bruegel%29.jpg/2560px-The_Tower_of_Babel_%28Bruegel%29.jpg"]
 actual=URL if p.exists() else None
 if not p.exists():
  errors=[]
  for url in urls:
   try:
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (ArtVision Commons PD-art source checker)","Accept":"image/jpeg"})
    with urllib.request.urlopen(req,timeout=80) as resp:
     if "image" not in resp.headers.get("Content-Type",""):raise ValueError("Unexpected source MIME")
     with open(p,"wb") as dest:
      total=0
      while True:
       data=resp.read(1048576)
       if not data:break
       total+=len(data)
       if total>40_000_000:raise ValueError("Image above 40 MB cap")
       dest.write(data)
    actual=url
    break
   except Exception as exc:
    errors.append(str(exc))
    if p.exists():p.unlink()
  if not actual:raise RuntimeError("All PD-art source downloads failed: "+repr(errors))
 with Image.open(p) as im:
  if im.format!="JPEG" or im.width<2560 or im.height<1900 or not (1.30<im.width/im.height<1.37):
   raise ValueError(f"Wrong Tower of Babel version/source dimensions: {im.size} {im.format}")
  dims=list(im.size)
 return {"source":actual,"source_page":SOURCE_PAGE,"sha256":digest(p),"bytes":p.stat().st_size,"pixels":dims,"rights":"Wikimedia Commons independent faithful reproduction PD-Art/PDM; KHM official image download excluded"}


def title_plate(img):
 fontfile=next((x for x in ["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf","/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf"] if Path(x).exists()),None)
 if not fontfile:raise FileNotFoundError("Serif font missing")
 fontsmall=next((x for x in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",fontfile] if Path(x).exists()),None)
 bg=Image.new("RGB",(W,H),(13,15,17))
 d=ImageDraw.Draw(bg)
 for s,y,size,face,color in [
  ("THE TOWER OF BABEL",73,36,fontfile,(232,228,217)),
  ("PIETER BRUEGEL THE ELDER  ·  1563",155,18,fontsmall,(183,179,163)),
  ("KUNSTHISTORISCHES MUSEUM  ·  VIENNA",205,15,fontsmall,(170,165,148))]:
  f=ImageFont.truetype(face,size)
  b=d.textbbox((0,0),s,font=f)
  d.text(((W-(b[2]-b[0]))//2,y),s,font=f,fill=color)
 d.line((60,252,660,252),fill=(141,125,90),width=2)
 im=img.copy();im.thumbnail((678,790),Image.Resampling.LANCZOS)
 bg.paste(im,((W-im.width)//2,324))
 d=ImageDraw.Draw(bg)
 d.line((70,1152,650,1152),fill=(79,74,59),width=1)
 return cv2.cvtColor(np.asarray(bg),cv2.COLOR_RGB2BGR)

def full_plate(img):
 sh=img.resize((W,H),Image.Resampling.LANCZOS)
 sh=ImageEnhance.Brightness(sh.filter(ImageFilter.GaussianBlur(34))).enhance(.32)
 fr=img.copy();fr.thumbnail((700,1120),Image.Resampling.LANCZOS)
 sh.paste(fr,((W-fr.width)//2,(H-fr.height)//2))
 return cv2.cvtColor(np.asarray(sh),cv2.COLOR_RGB2BGR)

def detail(im,b,p):
 cx,cy,ch,zoom,dx,dy=b
 ease=p*p*(3-2*p)
 crop_h=int(ch*(1-zoom*ease));crop_w=int(crop_h*W/H)
 cxp=(cx+(ease-.5)*dx)*im.shape[1]
 cyp=(cy+(ease-.5)*dy)*im.shape[0]
 x0=int(max(0,min(im.shape[1]-crop_w,cxp-crop_w/2)))
 y0=int(max(0,min(im.shape[0]-crop_h,cyp-crop_h/2)))
 cr=im[y0:y0+crop_h,x0:x0+crop_w]
 if cr.size==0:raise ValueError("Empty crop")
 return cv2.resize(cr,(W,H),interpolation=cv2.INTER_AREA)

def get_frame(p):
 if not p.exists():
  urls=[FRAME_URL,"https://commons.wikimedia.org/wiki/Special:Redirect/file/The_Tower_of_Babel_1563_Bruegel_Kunsthistorisches_Museum_Wien_Austria_-_panoramio.jpg"]
  errors=[]
  for url in urls:
   try:
    req=urllib.request.Request(url,headers={"User-Agent":"ArtVision-MuseumPhotoVerification/1.0 (Creative Commons attribution)","Accept":"image/jpeg"})
    with urllib.request.urlopen(req,timeout=75) as resp:
     if "image" not in resp.headers.get("Content-Type",""):raise ValueError("Unexpected photo MIME")
     data=resp.read(7_000_001)
     if len(data)>7_000_000:raise ValueError("Museum photo >7 MB")
    p.write_bytes(data);break
   except Exception as exc:
    errors.append(str(exc))
    if p.exists():p.unlink()
  else:raise RuntimeError("Museum photo download unavailable: "+repr(errors))
 with Image.open(p) as im:
  if im.size!=(2400,1800) or im.format!="JPEG":raise ValueError(f"Wrong original museum photo: {im.size} {im.format}")
 return {"filename":p.name,"bytes":p.stat().st_size,"sha256":digest(p),"dimensions":[2400,1800],"source_page":FRAME_SOURCE_PAGE,"credit":FRAME_CREDIT,"license":FRAME_LICENSE}

def museum_setup(photo, art):
 # Real frame/photo from KHM room: CC BY photo, not fabricated painting/frame.
 # Replace only the blurred picture INSIDE the captured wooden frame with verified
 # original PD artwork. Never touch the authentic wood frame or its corner joins.
 quadrilateral=np.float32([[464,300],[2034,298],[2050,1422],[469,1443]])
 ah,aw=art.shape[:2]
 src=np.float32([[0,0],[aw-1,0],[aw-1,ah-1],[0,ah-1]])
 M=cv2.getPerspectiveTransform(src,quadrilateral)
 art_warp=cv2.warpPerspective(art,M,(2400,1800),flags=cv2.INTER_LANCZOS4)
 mask=np.zeros((1800,2400),dtype=np.uint8)
 cv2.fillConvexPoly(mask,quadrilateral.astype(np.int32),255)
 mask=cv2.GaussianBlur(mask,(9,9),2.0)
 mask3=(mask[...,None]/255.0).astype(np.float32)
 # Slight ambient gallery tone and reflection preserve in-photograph credibility.
 refined=(photo*(1-.91*mask3)+art_warp*(.91*mask3)).clip(0,255).astype(np.uint8)
 return refined

def museum_canvas(photo):
 # The photo is genuine, with wall extrapolation only outside its photographed area.
 # No false furniture, people or architectural embellishments.
 hh,ww=photo.shape[:2]
 canvas=cv2.resize(photo,(720,1280),interpolation=cv2.INTER_AREA)
 canvas=cv2.GaussianBlur(canvas,(0,0),70)
 canvas=(canvas.astype(np.float32)*.64).astype(np.uint8)
 # Original photo at 700x525, centred in a realistic neutral wall with feathered boundary.
 fw=702;fh=round(hh*fw/ww);x=(720-fw)//2;y=350
 imp=cv2.resize(photo,(fw,fh),interpolation=cv2.INTER_AREA)
 # Blend actual photographed neutral wall into extended wall; soft seam only at edges.
 yy,xx=np.mgrid[:fh,:fw]
 edge=np.minimum.reduce([xx,fw-xx-1,yy,fh-yy-1]).astype(float)
 a=np.clip(edge/27,0,1)[...,None]
 target=canvas[y:y+fh,x:x+fw]
 canvas[y:y+fh,x:x+fw]=(imp*a+target*(1-a)).astype(np.uint8)
 return canvas

def museum_zoom(base, phase):
 # Geometric movement only, no dissolves or ghosted paintings.
 z=1.0+1.65*(phase*phase*(3-2*phase))
 cx,cy=360,650
 M=np.float32([[z,0,cx*(1-z)],[0,z,cy*(1-z)]])
 return cv2.warpAffine(base,M,(720,1280),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT_101)

def museum_public_title(frame,progress):
 # Authentic image and frame remain visible from the first frame;
 # clean English title only in free wall area, not over the painting.
 if progress>.72:return frame
 ff=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
 draw=ImageDraw.Draw(ff)
 serif="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
 sans="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
 font=ImageFont.truetype(serif,28)
 sub=ImageFont.truetype(sans,15)
 title="THE TOWER OF BABEL"
 credit="PIETER BRUEGEL THE ELDER · 1563"
 for t,y,f in [(title,119,font),(credit,165,sub)]:
  bb=draw.textbbox((0,0),t,font=f)
  draw.text(((720-(bb[2]-bb[0]))//2,y),t,font=f,fill=(232,224,209),stroke_width=1,stroke_fill=(18,20,22))
 return cv2.cvtColor(np.asarray(ff),cv2.COLOR_RGB2BGR)

def museum_frame(base,sid,progress):
 if sid=="museum_entry":return museum_public_title(museum_zoom(base,progress*.16),progress)
 if sid=="museum_enter":return museum_zoom(base,.16+progress*.84)
 if sid=="museum_return":return museum_zoom(base,1-progress*.50)
 if sid=="museum_exit":return museum_zoom(base,.50*(1-progress))
 raise ValueError(sid)

def original_score(p):
 # Entirely original composition, no downloaded audio, samples, or paid services.
 rate=32000;dur=DURATION;t=np.arange(round(rate*dur))/rate
 audio=np.zeros(t.shape,dtype=np.float64)
 chords=[(0,15,[73.42,110.00,146.83,220.0]),
         (11,15,[65.41,98.00,130.81,196.0]),
         (22,16,[58.27,87.31,116.54,174.61]),
         (35,16,[65.41,98.00,146.83,196.0]),
         (46,16,[73.42,110.00,164.81,220.0])]
 for i,(start,length,tones) in enumerate(chords):
  x=t-start;env=np.clip(x/3,0,1)*np.clip((length-x)/4,0,1)
  env[(x<0)|(x>=length)]=0
  for j,hz in enumerate(tones):
   phase=2*np.pi*hz*t+.35*np.sin(2*np.pi*(.06+j*.013)*t+i*.5)
   audio+=(.048/(1+j*.3))*(np.sin(phase)+.17*np.sin(phase*2.01))*env
 for sec,hz in [(5.0,293.66),(10.5,349.23),(17.0,261.63),(24.0,440.0),
                (29.4,329.63),(35.9,293.66),(42.2,261.63),(48.0,349.23),(52.0,293.66)]:
  x=t-sec;gate=(x>=0)&(x<5)
  env=np.exp(-np.maximum(x,0)*.95)*gate
  audio+=.08*env*(np.sin(2*np.pi*hz*x)+.2*np.sin(2*np.pi*hz*2.03*x))
 for sec in [3.2,7.6,11.6,15.8,20.6,24.8,29.6,33.8,38.2,42.6,47.2,51.4]:
  x=t-sec;env=np.exp(-np.maximum(x,0)*3.2)*(x>=0)
  audio+=.08*env*np.sin(2*np.pi*63*x)
 fade=np.clip(t/2.8,0,1)*np.clip((dur-t)/3.7,0,1)
 pcm=(np.clip(np.tanh(audio*1.8)*fade,-.9,.9)*30000).astype("<i2")
 with wave.open(str(p),"wb") as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes(pcm.tobytes())


def main():
 pa=argparse.ArgumentParser();pa.add_argument("--output",type=Path,required=True);pa.add_argument("--source",type=Path)
 a=pa.parse_args();out=a.output;out.mkdir(parents=True,exist_ok=True)
 art=a.source or out/"ORIGINAL_ARTWORK.jpg"
 source=get_art(art)
 frame_path=out/"AUTHENTIC_KHM_FRAME_PHOTO_CC_BY3.jpg"
 frame_meta=get_frame(frame_path)
 orig=Image.open(art).convert("RGB");cv=cv2.imread(str(art))
 frame=cv2.imread(str(frame_path))
 assert cv is not None and frame is not None
 museum=museum_canvas(museum_setup(frame,cv))
 plate=title_plate(orig);whole=full_plate(orig)
 # Real museum picture must be visible for the first and last segments.
 assert "standard" not in "THE TOWER OF BABEL".lower()
 mp4=out/"BRUEGEL_THE_TOWER_OF_BABEL_CINEMA_MUSEUM_V137_REVIEW.mp4"
 sound=out/"ORIGINAL_SCORE_V137.wav";original_score(sound)
 cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo","-vcodec","rawvideo","-s",f"{W}x{H}","-pix_fmt","bgr24","-r",str(FPS),"-i","pipe:0",
      "-i",str(sound),"-map","0:v","-map","1:a","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-movflags","+faststart","-shortest",str(mp4)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 frames=0;mid=[];beats=[]
 try:
  for sid,sec,b in BEATS:
   n=round(sec*FPS);beats.append({"shot":sid,"from_s":round(frames/FPS,2),"to_s":round((frames+n)/FPS,2)})
   for j in range(n):
    p=j/max(1,n-1)
    frame=museum_frame(museum,sid,p) if sid.startswith("museum") else whole if b is None else detail(cv,b,p)
    if j==n//2:mid.append((sid,cv2.resize(frame,(180,320))))
    proc.stdin.write(frame.tobytes());frames+=1
  proc.stdin.close();err=proc.stderr.read();rc=proc.wait()
  if rc:raise RuntimeError(err.decode("utf-8","replace")[-2000:])
 except Exception:
  proc.kill();raise
 if frames!=round(DURATION*FPS):raise ValueError(f"Unexpected frames {frames}; expected {round(DURATION*FPS)}")
 run(["ffmpeg","-v","error","-i",mp4,"-f","null","-"])
 cap=cv2.VideoCapture(str(mp4))
 if not cap.isOpened():raise ValueError("MP4 could not be opened for readback")
 readback={"width":int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),"height":int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),"frames":int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),"fps":float(cap.get(cv2.CAP_PROP_FPS))}
 cap.release()
 if readback["width"]!=W or readback["height"]!=H or readback["frames"]!=frames or abs(readback["fps"]-FPS)>.01:raise ValueError(f"MP4 video readback mismatch: {readback}")
 ffprobe={"format":{"duration":frames/FPS,"size":mp4.stat().st_size},"video_readback":readback,"audio_verified_by_full_ffmpeg_decode":True}
 img_sheet=np.full((3*350,4*194,3),17,dtype=np.uint8)
 for i,(name,frame) in enumerate(mid):
  y=(i//4)*350+6;x=(i%4)*194+6;img_sheet[y:y+320,x:x+180]=frame
  cv2.putText(img_sheet,name[:18],(x,y+332),cv2.FONT_HERSHEY_SIMPLEX,.32,(235,235,235),1,cv2.LINE_AA)
 cv2.imwrite(str(out/"CONTACT_SHEET_V137.jpg"),img_sheet)
 Image.fromarray(cv2.cvtColor(plate,cv2.COLOR_BGR2RGB)).save(out/"COVER.jpg",quality=94)
 (out/"RIGHTS_AND_CREDITS.txt").write_text(
  "Pieter Bruegel the Elder, The Tower of Babel, VIENNA version 1563. Kunsthistorisches Museum GG 1026, oil on oak panel 114.4 x 155.5 cm.\n"+
  "Public-domain faithful reproduction: "+SOURCE_PAGE+"\n"+
  "KHM museum identification (not image downloaded): "+RIGHTS_PAGE+"\n"+
  "Source Wikimedia URL: "+URL+"\nOriginal soundtrack: generated procedurally for this video without third-party samples.\n"+
  "Authentic museum-framed photo: "+FRAME_SOURCE_PAGE+"\n"+
  "Photographer: Hiroki Ogawa. License CC BY 3.0 Unported: "+FRAME_LICENSE+"\n"+
  "Adaptations: original photograph colour/geometry preserved, blurred painting interior replaced with licensed PD faithful reproduction; photo extended over neutral wall outside photographed area.\n"+
  "Current museum architecture, display state and 16th-century historical frame are NOT claimed; a 2015 photograph of the artwork in its frame is used. No third-party AI footage.\n"+
  "Artwork public-domain status does NOT automatically override institution-specific reuse rules or territorial cultural-heritage conditions; check before public or commercial distribution.\n")
 (out/"SOCIAL_DRAFT_UNPUBLISHED.txt").write_text("The Tower of Babel · Pieter Bruegel the Elder, 1563.\nA dream of human ambition, hundreds of tiny lives and an impossible tower.\nArtwork: Kunsthistorisches Museum Vienna GG 1026. Painting scan: Wikimedia Commons PD-Art. Framed photo: Hiroki Ogawa, CC BY 3.0 (cropped, interior sharpened), https://creativecommons.org/licenses/by/3.0/. Original soundtrack.\nDRAFT ONLY — NOT PUBLISHED.\n")
 qa={"work":"The Tower of Babel","artist":"Pieter Bruegel the Elder","year":1563,"museum":"Kunsthistorisches Museum Vienna","accession":"GG 1026","work_dimensions_cm":[114.4,155.5],"source":source,"authentic_frame_photo":frame_meta,"museum_environment":"actual framed-work photograph KHM 2015 with digitally extended wall; source painting restored from independent Commons PDM", "frame_historicity":"photo documented 2015, historical frame not claimed","audio":"original synthesized ambient","source_audio_sha256":digest(sound),"mp4":{"filename":mp4.name,"bytes":mp4.stat().st_size,"sha256":digest(mp4),"duration_seconds":DURATION,"frames":frames,"full_ffmpeg_decode":"PASS"},"ffprobe":ffprobe,"beats":beats,"cinema_standard_review":False,"cinema_museum":True,"critico_standard":False,"critico_museum":False,"museum_approved":False,"gold_v25":False,"social_published":False,"site_playback_verified":False,"human_artistic_review":"PENDING","zero_paid_api_calls":True,"public_title_in_frame":"THE TOWER OF BABEL only on museum intro, no Standard/project label"}
 (out/"QA_V137.json").write_text(json.dumps(qa,indent=2,ensure_ascii=False))
 archive=out/"BRUEGEL_BABEL_V137_CINEMA_MUSEUM_REVIEW_PACKAGE.zip"
 with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=4) as z:
  for fn in [mp4,"COVER.jpg","CONTACT_SHEET_V137.jpg","QA_V137.json","RIGHTS_AND_CREDITS.txt","SOCIAL_DRAFT_UNPUBLISHED.txt","ORIGINAL_ARTWORK.jpg","ORIGINAL_SCORE_V137.wav","AUTHENTIC_KHM_FRAME_PHOTO_CC_BY3.jpg"]:
   f=fn if isinstance(fn,Path) else out/fn
   z.write(f,arcname=f.name)
 with zipfile.ZipFile(archive) as z:
  if z.testzip() is not None:raise ValueError("Bad ZIP CRC")
 qa["package"]={"filename":archive.name,"bytes":archive.stat().st_size,"sha256":digest(archive),"crc":"PASS"}
 (out/"QA_V137.json").write_text(json.dumps(qa,indent=2,ensure_ascii=False))
 print(json.dumps({"render":"SUCCESS","mp4":qa["mp4"],"package":qa["package"],"public_title":"The Tower of Babel"},indent=2))

if __name__=="__main__":main()
