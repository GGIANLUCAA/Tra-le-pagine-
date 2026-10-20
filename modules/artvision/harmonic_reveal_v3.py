#!/usr/bin/env python3
"""ArtVision V3: authored details -> whole, restrained camera, REAL CC BY piano recording."""
from __future__ import annotations
import argparse, hashlib, json, math, shutil, subprocess, time
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import urlopen,Request
import cv2
import numpy as np
from PIL import Image,ImageOps,ImageDraw,ImageFont
from artvision import collect,download_pictures

MUSIC={
"title":"Calmant","artist":"Kevin MacLeod",
"source":"https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100859",
"license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
"urls":["https://incompetech.com/music/royalty-free/mp3-royaltyfree/Calmant.mp3",
"https://commons.wikimedia.org/wiki/Special:Redirect/file/Kevin_MacLeod_-_Calmant.ogg"],
"credit":'"Calmant" Kevin MacLeod (incompetech.com) - Creative Commons BY 4.0 - https://creativecommons.org/licenses/by/4.0/ - excerpt and fades for ArtVision.'
}
# Hand-authored attention points, not randomly sampled image locations.
# (catalogue title fragment, normalized x/y focal target, storytelling reason, opening zoom, timing weight)
CURATED=[
("irises",(.56,.56),"petals and irises brushwork",1.65,1.12),
("sunflowers",(.53,.45),"sunflower heads and pigment texture",1.60,1.12),
("two poplars",(.57,.39),"vertical rhythm of trees and sky",1.54,1.04),
("flowering orchard",(.54,.44),"branches and flowering trees",1.52,.98),
("bouquet of flowers",(.51,.49),"flower forms and contrasting color",1.55,1.06),
("large plane trees",(.51,.48),"tree trunks and road perspective",1.50,1.03),
("wheat field",(.55,.52),"grain pattern and horizon",1.46,1.09),
("street in saintes",(.52,.44),"street and southern architecture",1.45,.97),
("landscape with wheelbarrow",(.50,.51),"wheelbarrow in landscape",1.43,.96),
("nursery on schenkweg",(.56,.50),"figures in the deep street",1.48,1.01),
("first steps",(.49,.52),"child reaching toward parents",1.51,1.19),
("the zouave",(.53,.29),"eyes and face of portrait",1.54,1.19),
("adeline ravoux",(.53,.31),"expression and eyes of Adeline",1.53,1.20),
("arlésienne",(.52,.31),"sitter's face and hands",1.53,1.10),
("dr. gachet",(.54,.34),"hands, cheek and expression",1.53,1.22),
("corridor in the asylum",(.50,.48),"vanishing-point in asylum corridor",1.48,1.18)]
def cmd(args):
 p=subprocess.run(args,capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stderr[-3500:] or str(args))
 return p.stdout
def smooth(t):
 t=max(0.,min(1.,float(t)))
 return t*t*(3.-2.*t)
def music_file(folder,min_length):
 errors=[]
 for url in MUSIC["urls"]:
  ext=".mp3" if url.endswith(".mp3") else ".ogg"
  path=folder/("licensed_music"+ext)
  try:
   with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0 ArtVision cultural montage"}),timeout=45) as response: data=response.read(14_000_000)
   if len(data)<80_000:raise ValueError("empty audio download")
   path.write_bytes(data)
   meta=json.loads(cmd(["ffprobe","-v","error","-show_entries","format=duration","-of","json",str(path)]))
   if float(meta["format"]["duration"])<min_length:raise ValueError("audio shorter than film")
   return path,url,hashlib.sha256(data).hexdigest()
  except Exception as e:errors.append(str(e)[:260]);path.unlink(missing_ok=True)
 raise RuntimeError("Real CC-licensed recording unavailable: "+"; ".join(errors))
def arrange(works,artist,duration):
 if "van gogh" not in artist.lower():raise RuntimeError("V3 requires artist-specific human-curated focal map. Do not guess details for another artist.")
 ranked=[]
 for index,item in enumerate(works):
  title=item["title"].lower()
  for order,(key,xy,reason,zoom,weight) in enumerate(CURATED):
   if key in title:
    ranked.append((order,index,xy,reason,zoom,weight));break
 ranked.sort(key=lambda a:a[0])
 if len(ranked)<6:raise RuntimeError("Insufficient works with intentional directorial focus")
 weights=np.array([r[5] for r in ranked],dtype=float)
 spans=weights/weights.sum()*duration
 scenes=[];pos=0
 for n,(rank,index,xy,reason,zoom,weight) in enumerate(ranked):
  seconds=float(spans[n]);detail=seconds*.39;reveal=seconds*.31;whole=seconds-detail-reveal
  if detail<2.2 or whole<1.6:raise RuntimeError("Timing insufficient for deliberate viewing")
  scenes.append({"scene":n+1,"art_index":index,"title":works[index]["title"],"start":round(pos,3),
   "end":round(pos+seconds,3),"detail_seconds":round(detail,4),
   "reveal_seconds":round(reveal,4),"whole_seconds":round(whole,4),
   "focus":xy,"zoom":zoom,"curatorial_reason":reason,
   "direction":"near-still detail -> smooth pull-back -> whole artwork held",
   "editorial_focus":"hand-curated","split_screen":False})
  pos+=seconds
 return scenes
def render_frame(img,w,h,xy,z):
 ih,iw=img.shape[:2]
 # maintain original painting aspect ratio exactly; no recoloring or generation
 scale=min((w-32)/iw,(h-128)/ih)*z
 nw=max(1,round(iw*scale));nh=max(1,round(ih*scale))
 layer=cv2.resize(img,(nw,nh),interpolation=cv2.INTER_AREA if scale<1 else cv2.INTER_CUBIC)
 align=smooth((z-1)/.55)
 x=(w-nw)*.5*(1-align)+(w*.5-xy[0]*nw)*align
 y=(h-nh)*.5*(1-align)+(h*.5-xy[1]*nh)*align
 x=int(round(x));y=int(round(y))
 bg=np.full((h,w,3),(13,12,11),dtype=np.uint8)
 ox=max(x,0);oy=max(y,0);ex=min(w,x+nw);ey=min(h,y+nh)
 if ex>ox and ey>oy:bg[oy:ey,ox:ex]=layer[oy-y:ey-y,ox-x:ex-x]
 return bg
def title(frame,artist,opacity):
 h,w=frame.shape[:2]
 canvas=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)).convert("RGBA")
 glass=Image.new("RGBA",(w,h),(0,0,0,0));d=ImageDraw.Draw(glass)
 font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",33)
 a=max(0,min(255,int(255*opacity)))
 d.rounded_rectangle((27,55,w-27,150),radius=5,fill=(9,11,15,int(a*.67)))
 d.text((50,83),artist.upper(),font=font,fill=(244,237,218,a))
 return cv2.cvtColor(np.asarray(Image.alpha_composite(canvas,glass).convert("RGB")),cv2.COLOR_RGB2BGR)
def render_video(works,story,duration,out,artist,music):
 fps=24;w,h=720,1280
 temp=out/"_render_v3";temp.mkdir(exist_ok=True)
 raw=temp/"video_silent.mp4"
 writer=cv2.VideoWriter(str(raw),cv2.VideoWriter_fourcc(*"mp4v"),fps,(w,h))
 if not writer.isOpened():raise RuntimeError("Video encoder not started")
 used={s["art_index"] for s in story};photos={}
 for i in used:
  with Image.open(works[i]["file"]) as p:
   im=ImageOps.exif_transpose(p).convert("RGB")
   if max(im.size)>2300:im.thumbnail((2300,2300),Image.Resampling.LANCZOS)
   photos[i]=cv2.cvtColor(np.array(im),cv2.COLOR_RGB2BGR)
 target=int(duration*fps);written=0
 try:
  for idx,scene in enumerate(story):
   span=scene["end"]-scene["start"];count=(target-written) if idx==len(story)-1 else round(span*fps)
   detail=scene["detail_seconds"];reveal=scene["reveal_seconds"]
   for k in range(count):
    t=k/fps
    if t<detail:z=scene["zoom"]*(1-.005*smooth(t/max(detail,.01)))
    elif t<detail+reveal:z=1+(scene["zoom"]-1)* (1-smooth((t-detail)/reveal))
    else:z=1
    fr=render_frame(photos[scene["art_index"]],w,h,scene["focus"],z)
    if idx==0 and t<3.3:fr=title(fr,artist,min(1.,t/.6,(3.3-t)/.75))
    if idx==len(story)-1 and t>span-2:fr=cv2.convertScaleAbs(fr,alpha=max(0,(span-t)/2))
    writer.write(fr);written+=1
   print(f"V3 art-directed {idx+1}/{len(story)} {scene['title']}",flush=True)
 finally:writer.release()
 if written!=target:raise RuntimeError("Frame count mismatch")
 final=out/"ARTVISION_VIDEO.mp4"
 cmd(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(raw),"-i",str(music),
      "-t",str(duration),"-map","0:v:0","-map","1:a:0",
      "-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",
      "-c:a","aac","-b:a","160k","-af",f"volume=0.9,afade=t=in:st=0:d=1.0,afade=t=out:st={duration-3}:d=3",
      "-movflags","+faststart",str(final)])
 cmd(["ffmpeg","-hide_banner","-loglevel","error","-y","-ss","1.2","-i",str(final),"-frames:v","1",str(out/"COPERTINA.jpg")])
 q=json.loads(cmd(["ffprobe","-v","error","-show_entries","format=duration,size:stream=codec_type,width,height","-of","json",str(final)]))
 if abs(float(q["format"]["duration"])-duration)>1.5 or {x["codec_type"] for x in q["streams"]}!={"video","audio"}:raise RuntimeError("Failed media validation")
 shutil.rmtree(temp,ignore_errors=True)
 return q
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--artist",default="Vincent van Gogh")
 parser.add_argument("--duration",type=int,default=150)
 parser.add_argument("--max-works",type=int,default=16)
 parser.add_argument("--out",default="output/artvision")
 args=parser.parse_args()
 if not 120<=args.duration<=180:parser.error("duration range 120-180")
 if not 8<=args.max_works<=24:parser.error("max-works range 8-24")
 start=time.monotonic();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
 catalog,errors=collect(args.artist)
 if len(catalog)<6:raise RuntimeError(f"Insufficient artworks: {errors}")
 works,failures=download_pictures(catalog,out/"source_images",args.max_works)
 story=arrange(works,args.artist,args.duration)
 choice={s["art_index"] for s in story}
 (out/"STORYBOARD_REGIA.json").write_text(json.dumps(story,ensure_ascii=False,indent=2),encoding="utf8")
 (out/"OPERE_FONTI_E_DIRITTI.json").write_text(json.dumps({"artist":args.artist,"style":"harmonic_reveal_v3",
  "works":[works[i] for i in sorted(choice)],"errors":errors,"image_download_failures":failures,
  "publish":False,"legal_note":"Verify local museum image rights before commercial publication"},ensure_ascii=False,indent=2),encoding="utf8")
 music,url,checksum=music_file(out,args.duration+.5)
 proof={k:v for k,v in MUSIC.items() if k!="urls"}
 proof.update({"downloaded_from":url,"sha256":checksum,"edits":"Excerpt and fades"})
 (out/"MUSICA_LICENZA_E_CREDITI.json").write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding="utf8")
 workscredits="\n".join(f"{works[i]['title']} - {works[i]['source']} - {works[i]['license']} - {works[i]['url']}" for i in sorted(choice))
 (out/"CREDITI_E_FONTI.txt").write_text(workscredits+"\n\n"+MUSIC["credit"]+"\n",encoding="utf8")
 (out/"DESCRIZIONE_SOCIAL.txt").write_text(f"Vincent van Gogh - dettagli che diventano opere intere.\n\n{MUSIC['credit']}\n\nFonti delle opere: file CREDITI_E_FONTI.txt.\n#Arte #VanGogh #ArtVision\n",encoding="utf8")
 report=render_video(works,story,args.duration,out,args.artist,music)
 metrics={"style":"harmonic_reveal_v3","duration":float(report["format"]["duration"]),"artist":args.artist,
 "works":len(choice),"scenes":len(story),"bytes":int(report["format"]["size"]),
 "elapsed_seconds":round(time.monotonic()-start,1),"music_real_recording":True,
 "music":MUSIC["title"],"music_license":MUSIC["license"],"voice":"off",
 "paid_api_used":0,"publish":False,"split_screen":False}
 (out/"REPORT_PRODUZIONE.json").write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding="utf8")
 music.unlink(missing_ok=True)
 shutil.rmtree(out/"source_images",ignore_errors=True)
 print("ARTVISION HARMONIC REVEAL V3 SUCCESS",json.dumps(metrics,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
