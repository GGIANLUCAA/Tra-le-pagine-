#!/usr/bin/env python3
"""John William Waterhouse The Lady of Shalott 1888 Cinema review: verified PD artwork, original synthesized soundtrack, no paid API."""
import argparse, hashlib, json, os, subprocess, urllib.request, wave, zipfile
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
URL="https://upload.wikimedia.org/wikipedia/commons/1/1e/John_William_Waterhouse_-_The_Lady_of_Shalott_-_Google_Art_Project.jpg"
SOURCE_PAGE="https://commons.wikimedia.org/wiki/File:John_William_Waterhouse_-_The_Lady_of_Shalott_-_Google_Art_Project.jpg"
RIGHTS_PAGE="https://www.tate.org.uk/art/artworks/waterhouse-the-lady-of-shalott-n01543"
W,H,FPS=720,1280,20
BEATS=[
 ("cover",2.8,None),
 ("her_face_and_expression",4.6,(.423,.355,1650,.060,-.011,.006)),
 ("hand_loosens_the_chain",4.6,(.267,.515,1450,.055,.014,.006)),
 ("boat_and_tapestry",4.6,(.498,.715,1650,.055,.012,-.008)),
 ("three_candles_and_crucifix",4.6,(.690,.444,1450,.055,-.012,.008)),
 ("carved_prow",4.6,(.884,.388,1450,.055,-.012,.005)),
 ("water_and_reflections",4.6,(.792,.789,1800,.060,-.016,.008)),
 ("riverbank_reeds",4.6,(.115,.775,1650,.055,.013,-.008)),
 ("forest_and_camelot_shadows",4.6,(.545,.178,2450,.055,-.014,.006)),
 ("entire_painting",4.6,None),
 ("cover",3.8,None)
]
assert abs(sum(x[1] for x in BEATS)-48)<1e-5

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
 if not p.exists():
  req=urllib.request.Request(URL,headers={"User-Agent":"ArtVision-SourceVerification/1.0 (Wikimedia Commons artwork attribution)"})
  with urllib.request.urlopen(req,timeout=90) as resp:
   if "image/jpeg" not in resp.headers.get("Content-Type",""):raise ValueError("Unexpected source MIME")
   data=resp.read(15_000_001)
   if len(data)>15_000_000:raise ValueError("Unexpected source size")
   p.write_bytes(data)
 with Image.open(p) as im:
  if im.size!=(4180,3208) or im.format!="JPEG":raise ValueError(f"Wrong art image/version: {im.size} {im.format}")
 if not 4_000_000<=p.stat().st_size<=10_000_000:
  raise ValueError("Unexpected Google Art Project source byte size; no render")
 return {"source":URL,"source_page":SOURCE_PAGE,"sha256":digest(p),"bytes":p.stat().st_size,"pixels":[4180,3208],"rights":"Wikimedia Commons PD-Art/PDM faithful reproduction; Tate N01543 and UK photographic claims noted, territorial rights review pending"}

def title_plate(img):
 fontfile=next((x for x in ["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf","/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf"] if Path(x).exists()),None)
 if not fontfile:raise FileNotFoundError("Serif font missing")
 fontsmall=next((x for x in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",fontfile] if Path(x).exists()),None)
 bg=Image.new("RGB",(W,H),(13,15,17))
 d=ImageDraw.Draw(bg)
 for s,y,size,face,color in [
  ("THE LADY OF SHALOTT",73,34,fontfile,(232,228,217)),
  ("JOHN WILLIAM WATERHOUSE · 1888",155,18,fontsmall,(183,179,163)),
  ("TATE BRITAIN · LONDON",205,15,fontsmall,(170,165,148))]:
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

def original_score(p):
 # Original 48 s gentle ambient soundtrack, written here; no licensed third-party track.
 rate=32000;dur=48;t=np.arange(int(rate*dur))/rate
 # Dark but tender, slowly shifting minor ninth pad with irregular overtones.
 audio=np.zeros(t.shape,dtype=np.float64)
 chords=[(0,[110.0,164.81,220.0,293.66]),(12,[98.0,146.83,196.0,261.63]),
         (24,[87.31,130.81,174.61,246.94]),(36,[110.0,164.81,220.0,329.63])]
 for start,tones in chords:
  local=t-start;gate=(local>=0)&(local<13)
  fade=np.clip(local/2.5,0,1)*np.clip((13-local)/3.5,0,1)
  for j,hz in enumerate(tones):
   vibr=np.sin(2*np.pi*hz*t+.6*np.sin(2*np.pi*(.07+j*.021)*t))
   audio += (.043/(1+j*.22))*vibr*fade*gate
 for hit,fr in [(5.0,440),(10.4,392),(16.7,349.23),(23.9,329.63),(30.2,392),(37.5,440),(42.4,329.63)]:
  local=t-hit
  envelope=np.where(local>=0,np.exp(-np.maximum(local,0)*.95),0.0)
  audio+=.12*envelope*np.sin(2*np.pi*fr*local)*(local>=0)
 globalfade=np.clip(t/1.5,0,1)*np.clip((dur-t)/3.5,0,1)
 audio=np.clip(np.tanh(audio*1.6)*globalfade,-.9,.9)
 pcm=np.asarray(audio*30000,dtype="<i2")
 with wave.open(str(p),"wb") as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(pcm.tobytes())

def main():
 pa=argparse.ArgumentParser();pa.add_argument("--output",type=Path,required=True);pa.add_argument("--source",type=Path)
 a=pa.parse_args();out=a.output;out.mkdir(parents=True,exist_ok=True)
 art=a.source or out/"ORIGINAL_ARTWORK.jpg"
 source=get_art(art)
 orig=Image.open(art).convert("RGB");cv= cv2.imread(str(art))
 assert cv is not None
 plate=title_plate(orig);whole=full_plate(orig)
 mp4=out/"WATERHOUSE_THE_LADY_OF_SHALOTT_CINEMA_V155_REVIEW.mp4"
 sound=out/"ORIGINAL_AMBIENT_SCORE_V155.wav";original_score(sound)
 cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo","-vcodec","rawvideo","-s",f"{W}x{H}","-pix_fmt","bgr24","-r",str(FPS),"-i","pipe:0",
      "-i",str(sound),"-map","0:v","-map","1:a","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-movflags","+faststart","-shortest",str(mp4)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 frames=0;mid=[];beats=[]
 try:
  for sid,sec,b in BEATS:
   n=round(sec*FPS);beats.append({"shot":sid,"from_s":round(frames/FPS,2),"to_s":round((frames+n)/FPS,2)})
   for j in range(n):
    frame=plate if sid=="cover" else whole if b is None else detail(cv,b,j/max(1,n-1))
    if j==n//2:mid.append((sid,cv2.resize(frame,(180,320))))
    proc.stdin.write(frame.tobytes());frames+=1
  proc.stdin.close();err=proc.stderr.read();rc=proc.wait()
  if rc:raise RuntimeError(err.decode("utf-8","replace")[-2000:])
 except Exception:
  proc.kill();raise
 if frames!=960:raise ValueError(f"Unexpected frames {frames}")
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
 cv2.imwrite(str(out/"CONTACT_SHEET_V155.jpg"),img_sheet)
 Image.fromarray(cv2.cvtColor(plate,cv2.COLOR_BGR2RGB)).save(out/"COVER.jpg",quality=94)
 (out/"RIGHTS_AND_CREDITS.txt").write_text(
  "John William Waterhouse, The Lady of Shalott, 1888; Tate Britain inventory N01543, oil on canvas, 153 x 200 cm.\n"+
  "Actual source: Wikimedia Commons 4180x3208 Google Art Project faithful reproduction, Public Domain Mark/PD-Art: "+SOURCE_PAGE+"\n"+
  "Tate official object: "+RIGHTS_PAGE+"\n"+
  "Source JPEG verified size/format and measured SHA256: "+source["sha256"]+"\n"+
  "Tate Britain claims rights to certain reproductions in the UK; commercial territorial rights and final release require independent review. This is a PRIVATE REVIEW ONLY, no social publication.\n"+
  "Original procedurally synthesized ambient music; no externally licensed audio, Vidu, paid image or API calls.\n"+
  "No Museum frames or 3D environment represented; only historical artwork details and full image. Museum variants require separate authentic frame verification.\n",
  encoding="utf8")
 (out/"SOCIAL_DRAFT_UNPUBLISHED.txt").write_text(
  "The Lady of Shalott · John William Waterhouse, 1888.\n\n"
  "The final voyage begins. Look closely at the chain, the candles, the tapestry and the mysterious river beyond the boat.\n\n"
  "Tate Britain N01543. Artwork image from Wikimedia Commons Google Art Project faithful public-domain reproduction, subject to territorial rights review. Original sound.\n"
  "DRAFT ONLY — NOT PUBLISHED.\n",encoding="utf8")
 qa={"work":"The Lady of Shalott","artist":"John William Waterhouse","year":1888,"museum":"Tate Britain","accession":"N01543","work_dimensions_cm":[153,200],"source":source,"audio":"original synthesized ambient","source_audio_sha256":digest(sound),"mp4":{"filename":mp4.name,"bytes":mp4.stat().st_size,"sha256":digest(mp4),"duration_seconds":48,"frames":frames,"full_ffmpeg_decode":"PASS"},"ffprobe":ffprobe,"beats":beats,"cinema_standard_review":True,"cinema_museum":False,"critico_standard":False,"critico_museum":False,"museum_approved":False,"gold_v25":False,"social_published":False,"site_playback_verified":False,"human_artistic_review":"PENDING","zero_paid_api_calls":True,"public_title_in_frame":"THE LADY OF SHALOTT"}
 (out/"QA_V155.json").write_text(json.dumps(qa,indent=2,ensure_ascii=False))
 archive=out/"WATERHOUSE_LADY_SHALOTT_CINEMA_V155_REVIEW_PACKAGE.zip"
 with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=4) as z:
  for fn in [mp4,"COVER.jpg","CONTACT_SHEET_V155.jpg","QA_V155.json","RIGHTS_AND_CREDITS.txt","SOCIAL_DRAFT_UNPUBLISHED.txt","ORIGINAL_ARTWORK.jpg","ORIGINAL_AMBIENT_SCORE_V155.wav"]:
   f=fn if isinstance(fn,Path) else out/fn
   z.write(f,arcname=f.name)
 with zipfile.ZipFile(archive) as z:
  if z.testzip() is not None:raise ValueError("Bad ZIP CRC")
 qa["package"]={"filename":archive.name,"bytes":archive.stat().st_size,"sha256":digest(archive),"crc":"PASS"}
 (out/"QA_V155.json").write_text(json.dumps(qa,indent=2,ensure_ascii=False))
 print(json.dumps({"render":"SUCCESS","mp4":qa["mp4"],"package":qa["package"],"public_title":"The Lady of Shalott"},indent=2))

if __name__=="__main__":main()
