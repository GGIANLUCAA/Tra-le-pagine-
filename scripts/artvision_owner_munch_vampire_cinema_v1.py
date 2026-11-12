#!/usr/bin/env python3
"""Private ArtVision Cinema Standard of the 1893 GKM 0640 Göteborg version of Munch's Vampire."""
from pathlib import Path
import os,sys,hashlib,urllib.request,urllib.parse,json,subprocess,math,wave,zipfile
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"output/artvision-owner-munch-vampire-cinema-v1"
NAME="Edvard Munch Vampire.jpg"
URL="https://upload.wikimedia.org/wikipedia/commons/4/4d/Edvard_Munch_Vampire.jpg"
ALTERNATE="https://commons.wikimedia.org/wiki/Special:Redirect/file/Edvard_Munch_Vampire.jpg"
PAGE="https://commons.wikimedia.org/wiki/File:Edvard_Munch_Vampire.jpg"
MUSEUM="https://www.munch.no/en/object/PE.M.00332"
SOURCE_SHA1="c58f63c1f88719f1cb64a7feb35f0cc272e8ec31"
SOURCE_BYTES=4236527
PIXELS=(2865,2308)
FPS=18
WIDTH,HEIGHT=1080,1920
# Shot subject centers are measured relative to the actual 2865x2308 photograph.
SHOTS=[
("The embrace — initial striking focus",4.0,.51,.44,0.81),
("Face hidden beneath copper hair",4.4,.46,.42,0.72),
("The woman's red hair",4.5,.54,.37,0.72),
("The man's dark head",4.6,.46,.57,0.70),
("The pale embrace",4.9,.39,.71,0.74),
("The hand",4.0,.54,.74,0.68),
("Dark colors and painterly textures",4.6,.26,.37,0.77),
("Hair folding across the shoulder",4.3,.67,.49,0.72),
("The two bodies, opposing colors",4.2,.51,.51,0.93),
("Return to whole unaltered canvas",5.0,.50,.50,1.00)
]
DURATION=sum(x[1] for x in SHOTS)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def preflight():
 q=json.loads((ROOT/"research/artvision_owner_selected_30_future_20261109.json").read_text())
 works=[x for x in q["works"] if x.get("title_as_chosen")=="The Vampire" or (x.get("title_as_chosen")=="The Vampire" and x.get("artist_as_chosen")=="Edvard Munch") or (x.get("title_as_chosen")=="Vampire" and x.get("artist_as_chosen")=="Edvard Munch")]
 assert len(works)==1, "Owner shortlist must have exactly one Munch Vampire"
 assert not list((ROOT/"queue").glob("artvision_owner_30_render_checkpoint_*vampire*.json")), "Slot already completed: do not render duplicate"
 assert FPS>=18 and DURATION>=37 and len(SHOTS)>=8
 return {"selected_order":works[0]["selection_order"],"painting":"Vampire","artist":"Edvard Munch","museum_object":"GKM 0640 / Woll 334","source_expected_sha1":SOURCE_SHA1,"duration":DURATION,"shots":len(SHOTS),"variant":"cinema_standard","status":"PRIVATE_TEST_ONLY"}
def get_source():
 p=OUT/"SOURCE_ORIGINAL.jpg"
 for url in (URL,ALTERNATE):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"ArtVision/OwnerPrivateCinema (Wikimedia Commons educational source verification)"}),timeout=100) as r:data=r.read(SOURCE_BYTES+1)
   assert len(data)==SOURCE_BYTES and hashlib.sha1(data).hexdigest()==SOURCE_SHA1, "Original bytes do not match Commons"
   p.write_bytes(data)
   with Image.open(p) as im:assert im.size==PIXELS and im.format=="JPEG", "Wrong museum variant/image"
   return p,url
  except Exception as e:print("IMAGE_ATTEMPT_FAILED",type(e).__name__,str(e)[:130],flush=True)
 raise RuntimeError("NO_EXACT_IMAGE: reject source, no video produced")
def ease(t):return t*t*(3-2*t)
def make_bg(rgb):
 b=cv2.resize(rgb,(WIDTH,HEIGHT),interpolation=cv2.INTER_LINEAR)
 b=cv2.GaussianBlur(b,(0,0),38)
 return cv2.convertScaleAbs(b,alpha=.40,beta=0)
def whole_frame(rgb,bg):
 x=WIDTH-18;h=int(rgb.shape[0]*x/rgb.shape[1])
 h=min(h,HEIGHT-140);w=int(rgb.shape[1]*h/rgb.shape[0])
 frame=bg.copy()
 scaled=cv2.resize(rgb,(w,h),interpolation=cv2.INTER_AREA)
 left=(WIDTH-w)//2;top=(HEIGHT-h)//2
 frame[top:top+h,left:left+w]=scaled
 return frame
def crop_frame(rgb,cx,cy,fraction,drift):
 ih,iw=rgb.shape[:2]
 # fraction of the maximum crop width compatible with portrait 9:16 aspect.
 max_width=min(iw,ih*WIDTH/HEIGHT)
 crop_width=max_width*fraction
 scale=crop_width/WIDTH
 xx=(cx+.005*drift)*iw
 yy=(cy+.007*drift)*ih
 # Keep all source pixels inside canvas where possible.
 xx=max(crop_width/2,min(iw-crop_width/2,xx))
 crop_height=scale*HEIGHT
 yy=max(crop_height/2,min(ih-crop_height/2,yy))
 M=np.float32([[scale,0,xx-scale*WIDTH/2],[0,scale,yy-scale*HEIGHT/2]])
 return cv2.warpAffine(rgb,M,(WIDTH,HEIGHT),flags=cv2.INTER_LINEAR|cv2.WARP_INVERSE_MAP,borderMode=cv2.BORDER_REPLICATE)
def synth_score(duration):
 sr=24000;count=int(sr*duration);t=np.arange(count,dtype=np.float64)/sr
 y=np.zeros(count,dtype=np.float64)
 sequence=[(130.81,155.56,196.0),(116.54,155.56,174.61),(103.83,130.81,155.56),(98.0,146.83,196.0)]
 for ix,ch in enumerate(sequence):
  start=ix*duration/len(sequence);end=(ix+1)*duration/len(sequence)
  m=(t>=start-1)&(t<end+1);tt=t[m]
  envelope=np.clip((tt-(start-1))/2,0,1)*np.clip(((end+1)-tt)/2,0,1)
  for hz in ch:
   y[m]+=0.010*envelope*(np.sin(2*np.pi*hz*tt)+.22*np.sin(2*np.pi*2*hz*tt))
  y[m]+=.005*envelope*np.sin(2*np.pi*ch[0]*.5*tt)
 # Gentle glimmer and dark pulse (fully synthetic original composition).
 y+=.0025*np.sin(2*np.pi*392*t)*(0.5+0.5*np.sin(2*np.pi*.083*t))
 y+=.003*np.sin(2*np.pi*65.41*t)*(0.5+0.5*np.sin(2*np.pi*.23*t))
 y*=np.minimum(1,np.minimum(t/1.6,(duration-t)/2.0)).clip(0,1)
 out=np.int16(np.clip(y,-.8,.8)*32767)
 with wave.open(str(OUT/"ORIGINAL_SCORE.wav"),"wb") as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(out.tobytes())
def render(src):
 im=cv2.imread(str(src),cv2.IMREAD_COLOR)
 assert im is not None and im.shape[1]==PIXELS[0] and im.shape[0]==PIXELS[1]
 rgb=cv2.cvtColor(im,cv2.COLOR_BGR2RGB)
 rgb=rgb[22:-12,12:-12]  # trim camera-captured black canvas border, never alter figures
 bg=make_bg(rgb)
 p=OUT/"VIDEO_ONLY.mp4"
 ff=subprocess.Popen(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{WIDTH}x{HEIGHT}","-r",str(FPS),"-i","pipe:0","-an","-c:v","libx264","-preset","veryfast","-crf","23","-pix_fmt","yuv420p",str(p)],stdin=subprocess.PIPE)
 frames_for_qa=[];frame_count=0;cursor=0
 try:
  for idx,(label,dur,x,y,f) in enumerate(SHOTS):
   n=round(dur*FPS)
   for k in range(n):
    prog=k/max(1,n-1);move=ease(prog)*2-1
    if f>=.999:
     frame=whole_frame(rgb,bg)
    else:
     frame=crop_frame(rgb,x,y,f,move)
    if k==n//2:frames_for_qa.append((label,cv2.resize(frame,(270,480),interpolation=cv2.INTER_AREA)))
    ff.stdin.write(frame.tobytes());frame_count+=1
   cursor+=dur
 finally:
  if ff.stdin:ff.stdin.close()
 if ff.wait()!=0:raise RuntimeError("FFMPEG_RENDER_FAILED")
 from PIL import ImageOps
 covers=Image.new("RGB",(270*5,480*2))
 for i,(label,image) in enumerate(frames_for_qa):
  covers.paste(Image.fromarray(image),((i%5)*270,(i//5)*480))
 covers.save(OUT/"CONTACT_SHEET.jpg",quality=83)
 cover=Image.fromarray(crop_frame(rgb,.50,.48,.90,0))
 dr=ImageDraw.Draw(cover,"RGBA")
 dr.rectangle((0,85,1080,395),fill=(0,0,0,170))
 ft=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",105)
 sub=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",43)
 dr.text((64,130),"VAMPIRE",font=ft,fill=(255,255,255,255))
 dr.text((68,290),"EDVARD MUNCH · 1893",font=sub,fill=(255,255,255,245))
 cover.save(OUT/"COVER.jpg",quality=88)
 return frame_count
def main():
 import argparse
 pa=argparse.ArgumentParser();pa.add_argument("--preflight-only",action="store_true");args=pa.parse_args()
 OUT.mkdir(parents=True,exist_ok=True)
 gate=preflight();dump(OUT/"PREFLIGHT.json",gate)
 if args.preflight_only:print("SAFE_PREFLIGHT_PASS",gate);return
 src,url=get_source()
 frame_count=render(src)
 synth_score(frame_count/FPS)
 p=OUT/"VIDEO_ANDROID.mp4"
 subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(OUT/"VIDEO_ONLY.mp4"),"-i",str(OUT/"ORIGINAL_SCORE.wav"),"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","128k","-movflags","+faststart","-shortest",str(p)],check=True)
 subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-xerror","-i",str(p),"-map","0","-f","null","-"],check=True)
 qa={"title":"Vampire","artist":"Edvard Munch","year":1893,"edition":"Gothenburg Museum of Art GKM 0640, Woll 334","status":"ONE_REAL_NEW_PRIVATE_CINEMA_NEEDS_HUMAN_ARTISTIC_AND_TERRITORIAL_RIGHTS_REVIEW","variant":"cinema_standard","video_sha256":sha(p),"video_bytes":p.stat().st_size,"source_sha256":sha(src),"source_sha1":SOURCE_SHA1,"source_bytes":src.stat().st_size,"resolution":[WIDTH,HEIGHT],"fps":FPS,"frames":frame_count,"duration_s":frame_count/FPS,"shots":len(SHOTS),"soundtrack":"original synthesis only","FFMPEG_full_audio_video_decode":"PASS","publisher_rights_territorial":"PENDING","human_fullspeed_QA":"PENDING","gold":False,"published":False,"new_paid_api_calls":0}
 dump(OUT/"QA_TECHNICAL.json",qa)
 dump(OUT/"SOURCES_RIGHTS.json",{"museum_object":"GKM 0640 / Woll 334, 1893","museum_record":MUSEUM,"source_licensing_page":PAGE,"used_url":url,"source_sha1":SOURCE_SHA1,"source_sha256":sha(src),"credit":"Edvard Munch, Vampire (1893), Göteborgs konstmuseum GKM 0640; faithful photograph by Andrzej Otrębski via Wikimedia Commons, PD-Art/PDM description.","statement":"Original painting is public domain in Europe due to 1944 death. Photograph rights and venue-specific commercial/territorial reuse require human review; PRIVATE ONLY.","museum_scene":False})
 dump(OUT/"STORYBOARD.json",{"note":"10 distinct semantic camera shots on authentic photographic reproduction, no AI-created painting details; human artistic review pending","shots":[{"label":l,"duration":d,"approx_center":[x,y],"crop_fraction":f} for l,d,x,y,f in SHOTS]})
 dump(OUT/"SOCIAL_POSTS.json",{"title_en":"Vampire — Edvard Munch","facebook":"Un abbraccio o una minaccia? In Vampire (1893), Munch trasforma un gesto intimo in un'immagine inquietante.","instagram":"Vampire — Edvard Munch, 1893. Due figure, un abbraccio, un dubbio. #ArtHistory #Munch","tiktok":"Non c'è sangue. Perché allora lo chiamiamo Vampire? Edvard Munch, 1893. #ArtTok","youtube_shorts":"Vampire (1893) — An unsettling embrace by Edvard Munch. Visual study, original score.","publication":"DRAFT_ONLY_RIGHTS_REVIEW_PENDING"})
 with zipfile.ZipFile(OUT/"ANDROID_REVIEW_PACKAGE.zip","w",compression=zipfile.ZIP_DEFLATED,compresslevel=2) as z:
  for fname in ("VIDEO_ANDROID.mp4","COVER.jpg","CONTACT_SHEET.jpg","QA_TECHNICAL.json","SOURCES_RIGHTS.json","STORYBOARD.json","SOCIAL_POSTS.json"):
   z.write(OUT/fname,arcname=fname)
 with zipfile.ZipFile(OUT/"ANDROID_REVIEW_PACKAGE.zip") as z:
  assert z.testzip() is None
  assert hashlib.sha256(z.read("VIDEO_ANDROID.mp4")).hexdigest()==qa["video_sha256"]
 print("PRODUCED_NEW_MUNCH_CINEMA_PRIVATE",qa["video_sha256"],qa["duration_s"],flush=True)
if __name__=="__main__":main()
