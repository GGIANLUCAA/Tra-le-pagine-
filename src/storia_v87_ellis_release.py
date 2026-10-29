#!/usr/bin/env python3
"""V87 downloadable review cut from independently verified V85 film. No extra people, paid calls or invented motion."""
import cv2,numpy as np,subprocess,zipfile,json,hashlib
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
D=Path("output_v87");D.mkdir(exist_ok=True)
I=Path("input")
old=I/"ELLIS_ISLAND_1903_V85.mp4"
mute=D/"SILENT.mp4";new=D/"ELLIS_ISLAND_1903_V87_PREVIEW.mp4"
cap=cv2.VideoCapture(str(old));fps=cap.get(5);w=int(cap.get(3));h=int(cap.get(4))
p=subprocess.Popen(["ffmpeg","-nostdin","-y","-v","error","-f","rawvideo","-pix_fmt","bgr24","-s",f"{w}x{h}","-r",str(fps),"-i","-","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",str(mute)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
cache={};n=0
while True:
 ok,fr=cap.read()
 if not ok:break
 small=cv2.resize(fr,(90,160));sat=float(cv2.cvtColor(small,cv2.COLOR_BGR2HSV)[:,:,1].mean())
 if sat>14:
  code=hashlib.md5(cv2.resize(fr,(32,54)).tobytes()).hexdigest()
  if code in cache:fr=cache[code].copy()
  else:
   hsv=cv2.cvtColor(fr,cv2.COLOR_BGR2HSV);hsv[:,:,1]=np.minimum(255,hsv[:,:,1].astype("float32")*.55).astype("uint8")
   fr=cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
   avg=np.mean(fr.reshape(-1,3),axis=0)
   gain=np.clip((np.mean(avg)/np.maximum(avg,1))**.46,.84,1.26)
   fr=np.minimum(255,fr.astype("float32")*gain).astype("uint8")
   l=cv2.cvtColor(fr,cv2.COLOR_BGR2GRAY);sh=((255-l).astype("float32")/255)**1.7
   fr[:,:,0]=np.minimum(255,fr[:,:,0].astype("float32")+8*sh).astype("uint8")
   fr[:,:,2]=np.maximum(0,fr[:,:,2].astype("float32")-5*sh).astype("uint8")
   if len(cache)<130:cache[code]=fr.copy()
 p.stdin.write(fr.tobytes());n+=1
p.stdin.close();err=p.stderr.read();assert p.wait()==0,err[-500:];cap.release()
subprocess.run(["ffmpeg","-nostdin","-y","-v","error","-i",str(mute),"-i",str(old),"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","copy","-movflags","+faststart",str(new)],check=True)
subprocess.run(["ffmpeg","-v","error","-xerror","-i",str(new),"-f","null","-"],check=True)
c=cv2.VideoCapture(str(new));c.set(cv2.CAP_PROP_POS_MSEC,3800);ok,frame=c.read();c.release();assert ok
picture=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)).convert("RGBA")
overlay=Image.new("RGBA",(w,h));d=ImageDraw.Draw(overlay)
for y in range(440):d.line((0,y,w,y),fill=(8,12,20,int(155*max(0,1-y/440))))
picture=Image.alpha_composite(picture,overlay);d=ImageDraw.Draw(picture)
font="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
for txt,y,size in [("ELLIS ISLAND",130,52),("1903",208,82),("THE ARRIVAL",324,24)]:
 f=ImageFont.truetype(font,size);box=d.textbbox((0,0),txt,font=f)
 d.text(((w-(box[2]-box[0]))/2,y),txt,font=f,fill=(252,250,243,255))
d.line((170,112,w-170,112),fill=(218,197,159,255),width=2)
picture.convert("RGB").save(D/"COVER.jpg",quality=93)
(D/"READ_ME.txt").write_text("ELLIS ISLAND 1903 — REVIEW PREVIEW; not artistically approved.\nFilm: Alfred C. Abadie, 1903, Library of Congress; https://commons.wikimedia.org/wiki/File:Emigrants_(i.e._immigrants)_landing_at_Ellis_Island_-.webm\nSame-frame neural colorization; no new generative faces. Colors are conjectural. The face enhancement still falls below the user's supplied references. Spent Vidu credits: 0.\n")
(D/"POST_FACEBOOK.txt").write_text("ELLIS ISLAND · 1903. A real historical film showing immigrants landing in New York. Watch authentic black-and-white motion become an interpreted color photograph. Source: Library of Congress / Alfred C. Abadie. #History #EllisIsland\n")
(D/"QA.json").write_text(json.dumps({"status":"REVIEW_ONLY","real_archival_film":True,"duration":n/fps,"full_decoding":"PASS","voice":"none; instrumental soundtrack","generative_face_reconstruction":False,"vidu_credits_spent":0,"not_published_to_social":True},indent=2))
kit=D/"ELLIS_ISLAND_1903_KIT_V87_PREVIEW.zip"
with zipfile.ZipFile(kit,"w",zipfile.ZIP_DEFLATED) as z:
 for f in [new,D/"COVER.jpg",D/"READ_ME.txt",D/"POST_FACEBOOK.txt",D/"QA.json",I/"CONFRONTO_PRIMA_DOPO.jpg"]:z.write(f,f.name)
with zipfile.ZipFile(kit) as z:assert z.testzip() is None
print("PREVIEW_FULLY_DECODED_AND_KIT_TESTED",new,new.stat().st_size,kit,kit.stat().st_size,flush=True)
