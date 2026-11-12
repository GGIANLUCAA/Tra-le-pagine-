#!/usr/bin/env python3
"""ArtVision: Flavitsky Princess Tarakanova, 1863/64 TRETYAKOV full painting.
PRIVATE Cinema Standard only: no fake museum, no new TTS, no paid API, no publishing.
Never substitute the 1862 Yekaterinburg version or the Russian Museum head study.
"""
import argparse, hashlib, io, json, math, os, subprocess, urllib.request, wave, zipfile
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"output/artvision-owner-flavitsky-tarakanova-cinema-v1"
ORIGINAL_URL="https://upload.wikimedia.org/wikipedia/commons/7/7b/Tarakanova.jpg"
FALLBACK_URL="https://commons.wikimedia.org/wiki/Special:Redirect/file/Tarakanova.jpg"
SOURCE_PAGE="https://commons.wikimedia.org/wiki/File:Tarakanova.jpg"
MUSEUM_PAGE="https://my.tretyakov.ru/app/masterpiece/8412"
WORK_ID="flavitsky_princess_tarakanova_tretyakov_inv347_1863_1864"
WIDTH,HEIGHT,FPS=720,1280,20
SOURCE_DIMS=(1400,1845)
SOURCE_SHA256="749e30f146b61886c5d342c7da8f204afdadc73e5a3fe953221ba4dbdbe5f948"
SOURCE_SHA1="4e96a98a1d6a4568119f54c348ca329ad6fc2521"
SOURCE_BYTES=463191
# Deliberately gentle, distinguishable focuses. All subject locations refer to
# the exact Tretyakov composition, not any study/earlier edition.
SCENES=[
 ("The entire flooded room — dramatic opening",6.0,.50,.50,1.00),
 ("The prisoner's face and lost gaze",5.6,.29,.24,.63),
 ("Light breaking through the barred window",5.5,.86,.21,.66),
 ("The red and white gown",5.0,.32,.59,.70),
 ("The table and humble possessions",4.8,.88,.75,.65),
 ("The soaked bed beside the window",5.1,.72,.72,.75),
 ("Rising water across the floor",5.0,.58,.90,.68),
 ("The entire painting — final hold",6.5,.50,.50,1.00)

def sha(x):return hashlib.sha256(Path(x).read_bytes()).hexdigest()
def save(x,obj):Path(x).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def short_preflight():
 q=json.loads((ROOT/"research/artvision_owner_selected_30_future_20261109.json").read_text())
 m=[x for x in q["works"] if x.get("title_as_chosen")=="Princess Tarakanova" and x.get("artist_as_chosen")=="Konstantin Flavitsky"]
 assert len(m)==1 and m[0]["selection_order"]==4
 assert not list((ROOT/"queue").glob("artvision_owner_30_render_checkpoint_*tarakanova*.json")), "Duplicate owner slot"
 assert not list((ROOT/"queue").glob("artvision_owner_30_render_checkpoint_*flavitsky*.json")), "Duplicate owner slot"
 assert len(SCENES)==10 and 40<sum(x[1] for x in SCENES)<60
 # The known wrong high-resolution first version is explicitly excluded.
 assert "1862" not in ORIGINAL_URL and "Tarakanova.jpg" in ORIGINAL_URL
 return {"work":WORK_ID,"owner_order":4,"exact_artwork":"Tretyakov inventory 347, 245x187.5cm, 1863/64, NOT Yekaterinburg 1862","source_page":SOURCE_PAGE,"museum":MUSEUM_PAGE,"data_rights":"private source evaluation; commercial rights PENDING"}
def source_readback():
 p=OUT/"ORIGINAL_TRETYAKOV.jpg"
 for u in (ORIGINAL_URL,FALLBACK_URL):
  try:
   request=urllib.request.Request(u,headers={"User-Agent":"ArtVision/1.0 (private art source verification; bot-compliant)"})
   with urllib.request.urlopen(request,timeout=65) as resp:
    b=resp.read(1000000)
   assert b and len(b)==SOURCE_BYTES and hashlib.sha1(b).hexdigest()==SOURCE_SHA1 and hashlib.sha256(b).hexdigest()==SOURCE_SHA256, "Commons source version bytes/SHA mismatch"
   with Image.open(io.BytesIO(b)) as im:
    assert im.format=="JPEG" and im.size==SOURCE_DIMS,("Wrong edition or image dimensions",im.format,im.size)
    im.verify()
   p.write_bytes(b)
   record={"source_filename":"Tarakanova.jpg","source_url":u,"source_page":SOURCE_PAGE,"museum_page":MUSEUM_PAGE,"source_bytes":len(b),"source_sha1":hashlib.sha1(b).hexdigest(),"source_sha256":sha(p),"pixels":SOURCE_DIMS,"rights":"PD-Art/PDM per Wikimedia Commons; photographer unknown; territorial/commercial clearance PENDING","original_exact_artwork":"Tretyakov, 1863/64, 245x187.5 cm, inventory 347; NOT first version from Yekaterinburg"}
   save(OUT/"SOURCE_READBACK.json",record)
   print("TRETYAKOV_EXACT_SOURCE_VERIFIED",json.dumps({k:record[k] for k in ("source_bytes","source_sha1","source_sha256","pixels")}),flush=True)
   return p
  except Exception as e:
   print("SOURCE_ATTEMPT_FAILED",type(e).__name__,str(e)[:160],flush=True)
 raise RuntimeError("NO_VERIFIED_EXACT_TRETYAKOV_SOURCE_NO_VIDEO")
def whole(img,background):
 ih,iw=img.shape[:2]
 # Full art is always shown without changing subject proportions.
 h=HEIGHT-80;w=round(h*iw/ih)
 if w>WIDTH-20:w=WIDTH-20;h=round(w*ih/iw)
 small=cv2.resize(img,(w,h),interpolation=cv2.INTER_AREA)
 f=background.copy()
 y=(HEIGHT-h)//2;x=(WIDTH-w)//2
 f[y:y+h,x:x+w]=small
 return f
def focus(img,x,y,f,drift):
 ih,iw=img.shape[:2]
 basewidth=min(iw,ih*WIDTH/HEIGHT)
 cw=basewidth*f;ch=cw*HEIGHT/WIDTH
 px=(x+.006*drift)*iw
 py=(y+.004*drift)*ih
 px=max(cw/2,min(iw-cw/2,px))
 py=max(ch/2,min(ih-ch/2,py))
 ratio=cw/WIDTH
 M=np.array([[ratio,0,px-ratio*WIDTH/2],[0,ratio,py-ratio*HEIGHT/2]],dtype=np.float32)
 return cv2.warpAffine(img,M,(WIDTH,HEIGHT),flags=cv2.INTER_LINEAR|cv2.WARP_INVERSE_MAP,borderMode=cv2.BORDER_REPLICATE)
def soundtrack(seconds):
 sr=24000;n=int(seconds*sr);t=np.arange(n,dtype=np.float64)/sr;out=np.zeros(n)
 # Original, quiet score. Avoid transcribing any protected melody.
 harmonies=[(130.81,164.81,196.00),(116.54,146.83,174.61),(110.0,130.81,164.81),(98.0,123.47,146.83)]
 for i,ch in enumerate(harmonies):
  start=i*seconds/4;end=(i+1)*seconds/4
  mask=(t>=start-1)&(t<end+1);tx=t[mask]
  env=np.clip((tx-(start-1))/2,0,1)*np.clip((end+1-tx)/2,0,1)
  for f in ch:
   out[mask]+=.011*env*(np.sin(2*np.pi*f*tx)+.12*np.sin(4*np.pi*f*tx))
  out[mask]+=.004*env*np.sin(2*np.pi*ch[0]*.5*tx)
 # Subtle drifting wind/water atmosphere, wholly synthesized.
 out+=.0025*np.sin(2*np.pi*52*t)*(0.5+0.5*np.sin(2*np.pi*.115*t))
 out*=np.clip(t/1.3,0,1)*np.clip((seconds-t)/2.2,0,1)
 audio=np.int16(np.clip(out,-.85,.85)*32767)
 with wave.open(str(OUT/"ORIGINAL_SCORE.wav"),"wb") as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(audio.tobytes())
def produce(source):
 with Image.open(source) as im:rgb=np.asarray(im.convert("RGB"))
 # full image remains unchanged; only background is soft image-derived matte.
 bg=cv2.resize(rgb,(WIDTH,HEIGHT),interpolation=cv2.INTER_LINEAR)
 bg=cv2.GaussianBlur(bg,(0,0),36)
 bg=cv2.convertScaleAbs(bg,alpha=.27,beta=0)
 stream=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{WIDTH}x{HEIGHT}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","23","-pix_fmt","yuv420p",str(OUT/"VIDEO_SILENT.mp4")],stdin=subprocess.PIPE)
 contact=[];frames=0
 try:
  for (label,seconds,x,y,f) in SCENES:
   n=round(seconds*FPS)
   for k in range(n):
    d=(k/max(1,n-1)*2-1)
    a=whole(rgb,bg) if f==1.0 else focus(rgb,x,y,f,d)
    if k==n//2:contact.append(cv2.resize(a,(180,320),interpolation=cv2.INTER_AREA))
    stream.stdin.write(a.tobytes());frames+=1
 finally:
  stream.stdin.close()
 if stream.wait()!=0:raise RuntimeError("FFMPEG_SILENT_RENDER_FAILED")
 contact_sheet=Image.new("RGB",(180*4,320*2))
 for i,a in enumerate(contact):contact_sheet.paste(Image.fromarray(a),((i%4)*180,(i//4)*320))
 contact_sheet.save(OUT/"CONTACT_SHEET.jpg",quality=83)
 cover=Image.fromarray(focus(rgb,.38,.39,.88,0))
 dr=ImageDraw.Draw(cover,"RGBA");dr.rectangle((0,82,WIDTH,300),fill=(0,0,0,175))
 ft=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",42)
 sub=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",25)
 dr.text((20,117),"PRINCESS TARAKANOVA",font=ft,fill="white")
 dr.text((23,208),"KONSTANTIN FLAVITSKY",font=sub,fill="white")
 cover.save(OUT/"COVER.jpg",quality=90)
 soundtrack(frames/FPS)
 p=OUT/"VIDEO_ANDROID_REVIEW.mp4"
 subprocess.run(["ffmpeg","-v","error","-y","-i",str(OUT/"VIDEO_SILENT.mp4"),"-i",str(OUT/"ORIGINAL_SCORE.wav"),"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","112k","-shortest","-movflags","+faststart",str(p)],check=True)
 subprocess.run(["ffmpeg","-v","error","-xerror","-i",str(p),"-map","0","-f","null","-"],check=True)
 return p,frames
def main():
 pa=argparse.ArgumentParser();pa.add_argument("--preflight-only",action="store_true");a=pa.parse_args()
 OUT.mkdir(parents=True,exist_ok=True)
 p=short_preflight()
 source=source_readback()
 save(OUT/"PREFLIGHT.json",p)
 if a.preflight_only:
  print("PUBLIC_DOMAIN_SOURCE_PREFLIGHT_PASS_TRETYAKOV_NOT_YEKATERINBURG",flush=True)
  return
 mp4,frames=produce(source)
 s=json.loads((OUT/"SOURCE_READBACK.json").read_text())
 qa={"work":"Princess Tarakanova","artist":"Konstantin Flavitsky","edition":"State Tretyakov Gallery, inventory 347, painted 1863/exhibited 1864","source_sha256":s["source_sha256"],"source_bytes":s["source_bytes"],"video_sha256":sha(mp4),"video_bytes":mp4.stat().st_size,"duration_s":frames/FPS,"frame_count":frames,"resolution":[WIDTH,HEIGHT],"fps":FPS,"scenes":len(SCENES),"revision":2,"audio":"AAC original synthesized score","ffmpeg_full_decode":"PASS","publication_rights_and_territory":"PENDING","human_full_speed_qa":"PENDING","gold":False,"published":False,"extra_paid_calls":0}
 save(OUT/"QA_TECHNICAL.json",qa)
 save(OUT/"STORYBOARD.json",{"exact_object":"Tretyakov (not Ekaterinburg first version)","narrative_type":"visual-only no voice","shots":[{"detail":l,"seconds":sec,"x":x,"y":y,"fraction":f} for l,sec,x,y,f in SCENES],"editorial_check":"Director corrective V2: fewer repeated bed/dress closeups and shorter overall runtime; full-speed human QA still required"})
 save(OUT/"SOCIAL_DRAFTS.json",{"title":"Princess Tarakanova — Konstantin Flavitsky","facebook":"La prigioniera e l'acqua. Flavitsky dipinse nel 1863/64 una leggenda drammatica, non un fatto storico: la vera Tarakanova morì prima dell'alluvione del 1777.","instagram":"Un volto, una stanza, l'acqua che sale. Princess Tarakanova, Konstantin Flavitsky. #ArtHistory #Painting","tiktok":"Questa donna sembra destinata a morire nell'alluvione. Ma l'episodio è una leggenda. Princess Tarakanova.","youtube_shorts":"Princess Tarakanova — 19th-century Russian painting with a tragic historical myth. Original source, cinematic detail.","publication":"NOT APPROVED — RIGHTS AND ARTISTIC QA PENDING"})
 with zipfile.ZipFile(OUT/"ANDROID_REVIEW_PACKAGE.zip","w",compression=zipfile.ZIP_DEFLATED,compresslevel=2) as z:
  for name in ("VIDEO_ANDROID_REVIEW.mp4","COVER.jpg","CONTACT_SHEET.jpg","QA_TECHNICAL.json","STORYBOARD.json","SOCIAL_DRAFTS.json","SOURCE_READBACK.json"):
   z.write(OUT/name,arcname=name)
 with zipfile.ZipFile(OUT/"ANDROID_REVIEW_PACKAGE.zip") as z:
  assert z.testzip() is None
  assert hashlib.sha256(z.read("VIDEO_ANDROID_REVIEW.mp4")).hexdigest()==qa["video_sha256"]
 print("REAL_NEW_TARAKANOVA_CINEMA_REVIEW",qa["video_sha256"],qa["duration_s"],flush=True)
if __name__=="__main__":main()
