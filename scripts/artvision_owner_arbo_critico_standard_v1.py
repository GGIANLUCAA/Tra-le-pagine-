#!/usr/bin/env python3
"""Private real Critico Standard for Arbo NG.M.00258. No museum illusion, publication or paid TTS."""
import hashlib,io,json,math,os,re,subprocess,sys,urllib.request,urllib.parse,zipfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"output/artvision-owner-arbo-critico-v1"
SOURCE="Peter Nicolai Arbo - The wild Hunt of Odin - NG.M.00258 - National Museum of Art, Architecture and Design.jpg"
SOURCE_SHA256="510a60bb9797eedefab0ed1ca393d6ff5013bf2f689704dbd394808b88532b44"
SOURCE_SHA1="ecb86ffd7042eaedaa334fedce39ff795029960f"
MUSEUM_URL="https://www.nasjonalmuseet.no/en/collection/object/NG.M.00258"
SOURCE_PAGE="https://commons.wikimedia.org/wiki/File:Peter_Nicolai_Arbo_-_The_wild_Hunt_of_Odin_-_NG.M.00258_-_National_Museum_of_Art,_Architecture_and_Design.jpg"
BEATS=[
("Una notte d'inverno. All'improvviso, il cielo si riempie di cavalli. Secondo le leggende norvegesi, incontrare questa cavalcata poteva portare sventura.",.45,.35,.43,"cavalcata"),
("Peter Nicolai Arbo dipinse La caccia selvaggia di Odino nel 1872. La grande tela, larga oltre due metri, è oggi conservata al Museo Nazionale di Oslo.",.5,.5,1.,"tutta opera"),
("Guarda i cavalieri. Non galoppano sulla terra: sembrano correre sopra le nuvole, tutti trascinati dalla stessa raffica di vento.",.52,.38,.47,"cavalieri"),
("Mantelli e criniere si gonfiano. Le zampe dei cavalli si intrecciano. Arbo trasforma una folla confusa in una sensazione precisa: velocità.",.36,.48,.4,"cavalli"),
("Nella tradizione citata dal museo, il corteo è guidato da Sigurd, l'uccisore del drago. A chiuderlo compare la strega Gyro Ryssetova.",.46,.43,.57,"schiera"),
("In cielo passano anche i corvi di Odino. E più avanti, Thor solleva il martello mentre il suo carro è trainato da due capre.",.38,.61,.42,"corvi e Thor"),
("Sotto questa folla, la terra rimane silenziosa. Si distinguono il paesaggio e una luce pallida, lontanissima dai cavalieri.",.53,.81,.49,"paesaggio"),
("Dietro la corsa appare un bagliore rossastro. Il museo suggerisce che possa evocare Helheim, il regno dei morti. Ma è una possibilità, non una certezza.",.80,.33,.38,"bagliore"),
("Arbo si ispirò anche a una poesia del 1844 di Johan Sebastian Welhaven. In quei versi, cavalli neri attraversavano l'aria notturna.",.57,.44,.58,"cavalcata e cielo"),
("Qui non c'è una battaglia da vincere. C'è soltanto una cavalcata che attraversa il cielo, mentre chi resta sulla terra può soltanto guardarla passare.",.5,.5,1.,"opera intera")]
def text():return "\n\n".join(x[0] for x in BEATS)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def check_queue():
 j=json.loads((ROOT/"research/artvision_owner_selected_30_future_20261109.json").read_text())
 w=[x for x in j["works"] if x.get("title_as_chosen")=="The Wild Hunt of Odin" and x.get("artist_as_chosen")=="Peter Nicolai Arbo"]
 assert len(w)==1 and w[0]["selection_order"]==1
 assert 170<=len(text().split())<=245
 assert not list((ROOT/"queue").glob("artvision_owner_30_render_checkpoint_*arbo*critico*.json"))
 assert not list((ROOT/"queue").glob("artvision_owner_30_render_checkpoint_*critico*arbo*.json"))
 return {"words":len(text().split()),"beats":len(BEATS),"script_sha256":hashlib.sha256(text().encode()).hexdigest()}
def get_source():
 p=OUT/"SOURCE_ORIGINAL.jpg"
 if p.exists() and digest(p)==SOURCE_SHA256:return p
 import hashlib
 key=SOURCE.replace(" ","_");m=hashlib.md5(key.encode()).hexdigest()
 urls=["https://upload.wikimedia.org/wikipedia/commons/"+m[0]+"/"+m[:2]+"/"+urllib.parse.quote(key,safe="._-"),"https://commons.wikimedia.org/wiki/Special:Redirect/file/"+urllib.parse.quote(key,safe="._-")]
 for u in urls:
  try:
   with urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"ArtVision-research/1.0"}),timeout=110) as r:b=r.read(7151029)
   assert len(b)==7151028 and hashlib.sha1(b).hexdigest()==SOURCE_SHA1
   with Image.open(io.BytesIO(b)) as im:assert im.size==(10291,7074) and im.format=="JPEG"
   p.write_bytes(b);assert digest(p)==SOURCE_SHA256
   return p
  except Exception as e:print("SOURCE_FALLBACK",type(e).__name__,str(e)[:120],flush=True)
 raise RuntimeError("BLOCKED_EXACT_ORIGINAL_IMAGE")
def get_voice():
 # Caller also gates all three conditions in workflow. A key alone does NOT authorize billing.
 if not (os.getenv("GEMINI_TTS_FREE_QUOTA_CONFIRMED","").lower()=="true" and os.getenv("GEMINI_TTS_PROJECT_BILLING_DISABLED_CONFIRMED","").lower()=="true" and os.getenv("GEMINI_API_KEY")):
  raise RuntimeError("BLOCKED_FREE_VOICE_COST_GATE")
 sys.path.insert(0,str(ROOT/"src"))
 import gemini_voice
 assert gemini_voice.VOICE=="Gacrux"
 voice,timed=gemini_voice.synthesize(text(),OUT)
 # Sentence timing is ASR or explicitly estimated, not an invented perfect alignment.
 sentence_counts=[len(gemini_voice.sentences(b[0])) for b in BEATS]
 if sum(sentence_counts)!=len(timed):raise RuntimeError("VOICE_TIMING_COUNT_MISMATCH")
 spans=[];k=0
 for n in sentence_counts:
  subset=timed[k:k+n];spans.append((float(subset[0][1]),float(subset[-1][2])));k+=n
 import soundfile as sf
 a,sr=sf.read(OUT/"VOCE.wav")
 return spans,len(a)/sr
def frame(im,x,y,fraction):
 W,H=720,1280
 if fraction>=.99:
  # Preserve entire real artwork: vignette background comes from the same photograph only.
  bg=im.resize((W,H),Image.Resampling.BILINEAR).filter(__import__("PIL.ImageFilter",fromlist=["GaussianBlur"]).GaussianBlur(38)).convert("RGB")
  bg=Image.blend(bg,Image.new("RGB",(W,H),"black"),.55)
  ww=W-20;hh=round(ww*im.height/im.width)
  bg.paste(im.resize((ww,hh),Image.Resampling.LANCZOS),(10,(H-hh)//2))
  return bg
 # Crop portrait region with actual pixel proportions, no AI-generated details.
 cw=max(1,int(im.width*fraction));ch=round(cw*H/W)
 if ch>im.height:ch=im.height;cw=round(ch*W/H)
 l=int(max(0,min(im.width-cw,x*im.width-cw/2)));t=int(max(0,min(im.height-ch,y*im.height-ch/2)))
 return im.crop((l,t,l+cw,t+ch)).resize((W,H),Image.Resampling.BILINEAR)
def render(spans,duration,source):
 fps=16;W,H=720,1280
 ff=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s","720x1280","-r",str(fps),"-i","-","-an","-c:v","libx264","-preset","veryfast","-crf","24","-pix_fmt","yuv420p","-movflags","+faststart",str(OUT/"VIDEO_ONLY.mp4")],stdin=subprocess.PIPE)
 with Image.open(source) as im:
  img=im.convert("RGB")
  try:
   for n in range(math.ceil(duration*fps)):
    sec=n/fps
    index=next((k for k,(a,b) in enumerate(spans) if a<=sec<b),len(BEATS)-1)
    _,x,y,z,_=BEATS[index];a,b=spans[index]
    prog=max(0,min(1,(sec-a)/max(.001,b-a)))
    # Gentle drift only, no flash cuts or excessive digital zoom.
    pic=frame(img,x+.006*(prog-.5),y+.008*(prog-.5),z)
    ff.stdin.write(pic.tobytes())
  finally:
   ff.stdin.close()
  if ff.wait():raise RuntimeError("FAILED_VIDEO_RENDER")
  cover=frame(img,.45,.38,.48)
  dr=ImageDraw.Draw(cover,"RGBA");dr.rectangle((0,0,720,225),fill=(0,0,0,175))
  ft=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",45)
  dr.text((30,42),"THE WILD HUNT",font=ft,fill="white");dr.text((30,105),"OF ODIN",font=ft,fill="white")
  cover.save(OUT/"COPERTINA.jpg",quality=89)
 return fps
def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument("--preflight-only",action="store_true");arg=p.parse_args()
 OUT.mkdir(parents=True,exist_ok=True)
 gate=check_queue();(OUT/"COPIONE_IT.txt").write_text(text(),encoding="utf-8")
 save(OUT/"STORYBOARD.json",{"work":"The Wild Hunt of Odin","artist":"Peter Nicolai Arbo","source":MUSEUM_URL,"beats":[{"index":i+1,"speech":v[0],"source_detail":v[4],"crop_center":[v[1],v[2]],"fraction":v[3]} for i,v in enumerate(BEATS)],"semantic_precision":"Needs full-speed artistic review"})
 save(OUT/"PREFLIGHT.json",gate)
 if arg.preflight_only:print("PASS_PREFLIGHT",gate);return
 source=get_source();spans,dur=get_voice()
 save(OUT/"TIMING.json",{"beats":spans,"voice_seconds":dur,"asr_report":json.loads((OUT/"ALLINEAMENTO_VOCE.json").read_text())})
 render(spans,dur,source)
 dest=OUT/"CRITICO_STANDARD_ANDROID_REVIEW.mp4"
 subprocess.run(["ffmpeg","-v","error","-y","-i",str(OUT/"VIDEO_ONLY.mp4"),"-i",str(OUT/"VOCE.wav"),"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","128k","-shortest","-movflags","+faststart",str(dest)],check=True)
 subprocess.run(["ffmpeg","-v","error","-xerror","-i",str(dest),"-map","0","-f","null","-"],check=True)
 qa={"status":"PRIVATE_CRITICO_REVIEW_NOT_GOLD","mp4_sha256":digest(dest),"mp4_bytes":dest.stat().st_size,"duration_seconds":dur,"source_sha256":digest(source),"voice_sha256":digest(OUT/"VOCE.wav"),"full_decode":"PASS","commercial_territorial_release":"PENDING","artistic_full_speed":"PENDING","word_image_semantics":"PENDING","published":False,"gold":False,"old_cinema_modified":False,"new_paid_calls":0}
 save(OUT/"QA_TECHNICAL.json",qa)
 with zipfile.ZipFile(OUT/"CONSEGNA_CRITICO_ANDROID.zip","w",compression=zipfile.ZIP_DEFLATED,compresslevel=2) as z:
  for name in ["CRITICO_STANDARD_ANDROID_REVIEW.mp4","COPERTINA.jpg","COPIONE_IT.txt","STORYBOARD.json","TIMING.json","QA_TECHNICAL.json"]:z.write(OUT/name,arcname=name)
 with zipfile.ZipFile(OUT/"CONSEGNA_CRITICO_ANDROID.zip") as z:assert z.testzip() is None
 print("ACTUAL_CRITICO_MP4_SHA256",qa["mp4_sha256"],"NO_GOLD")
if __name__=="__main__":main()
