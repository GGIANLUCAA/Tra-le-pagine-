#!/usr/bin/env python3
"""V79 — source scout for three different public-domain real moving films with CLOSE FACES.
No retouch/generation yet. Save exact source, license provenance, and contact sheets.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError
import cv2,hashlib,json,subprocess,time
from PIL import Image,ImageDraw,ImageFont

D=Path("output/storia_v79_volti");D.mkdir(parents=True,exist_ok=True)
SOURCES=[
 ("SNEEZE_1894","File:Fred Ott's Sneeze (1894).webm","https://commons.wikimedia.org/wiki/File:Fred_Ott%27s_Sneeze_(1894).webm"),
 ("KISS_1896","File:The Kiss (1896).webm","https://commons.wikimedia.org/wiki/File:The_Kiss_(1896).webm"),
 ("KISS_1900","File:The Kiss (1900).webm","https://commons.wikimedia.org/wiki/File:The_Kiss_(1900).webm")
]
UA="Tra-le-Pagine-Storia-Rivive/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-; historical cinema research)"
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for block in iter(lambda:f.read(1048576),b""):h.update(block)
 return h.hexdigest()
def api(t):
 params=urlencode({"action":"query","format":"json","formatversion":"2","prop":"imageinfo","titles":t,"iiprop":"url|size|mime|extmetadata"})
 url="https://commons.wikimedia.org/w/api.php?"+params
 with urlopen(Request(url,headers={"User-Agent":UA}),timeout=60) as r:return json.load(r)["query"]["pages"][0]["imageinfo"][0]
def download(url,dest,size):
 if dest.exists() and dest.stat().st_size==size:return
 last=""
 for i in range(3):
  try:
   req=Request(url,headers={"User-Agent":UA})
   with urlopen(req,timeout=100) as inp,open(dest,"wb") as out:
    while chunk:=inp.read(1048576):
     out.write(chunk)
     if out.tell()>85_000_000:raise ValueError("Unexpected >85 MB")
   if dest.stat().st_size==size:return
   raise ValueError("Incomplete source")
  except Exception as e:
   last=str(e);time.sleep(i+1)
 raise RuntimeError(last)
def storyboard(p,key,n=10):
 cap=cv2.VideoCapture(str(p));fps=cap.get(cv2.CAP_PROP_FPS)
 dur=cap.get(cv2.CAP_PROP_FRAME_COUNT)/max(1,fps)
 if dur<2:raise RuntimeError("Not a moving film: "+str(p))
 w,h=int(cap.get(3)),int(cap.get(4))
 canvas=Image.new("RGB",(5*290,2*265),(14,16,17));draw=ImageDraw.Draw(canvas)
 frames=[]
 for i in range(n):
  t=(dur-.08)*(i+.5)/n
  cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,fr=cap.read()
  if not ok:raise RuntimeError("Cannot decode source at "+str(t))
  im=Image.fromarray(cv2.cvtColor(fr,cv2.COLOR_BGR2RGB))
  im.thumbnail((280,235))
  x=(i%5)*290+5;y=(i//5)*265+6
  canvas.paste(im,(x+(280-im.width)//2,y))
  draw.text((x+6,y+237),f"{key} {t:.1f}s",fill=(230,228,214))
  frames.append(dict(second=round(t,3),frame_index=round(t*fps)))
 cap.release()
 out=D/(key+"_FOTOGRAMMI.jpg");canvas.save(out,quality=89)
 print("CONTACT",out,w,h,round(dur,2),flush=True)
 return dict(key=key,filename=p.name,width=w,height=h,fps=fps,duration=round(dur,3),sha256=sha(p),frames=frames)
def main():
 records=[]
 for key,name,page in SOURCES:
  print("SCOUT",key,flush=True)
  meta=api(name);md=meta.get("extmetadata",{})
  label=md.get("LicenseShortName",{}).get("value","")
  licenseurl=md.get("LicenseUrl",{}).get("value","")
  if not meta.get("mime","").startswith("video/"):raise RuntimeError("Not archive film")
  if "public domain" not in label.lower() and "pd" not in label.lower() and "publicdomain" not in licenseurl.lower():
   raise RuntimeError("No PD media claim: "+key+" / "+label)
  dest=D/(key+".webm")
  download(meta["url"],dest,meta["size"])
  record=storyboard(dest,key);record.update({"commons_page":page,"direct_source_url":meta["url"],"declared_license":label,"license_url":licenseurl,"bytes":dest.stat().st_size,"rights_italy":"needs separate verification","description":"Original moving film from Wikimedia Commons / Library of Congress"})
  records.append(record)
 (D/"FONTI_VERIFICATE.json").write_text(json.dumps({"sources":records,"actual_moving_source_only":True,"no_vidu":True},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("THREE_SOURCE_SCOUT_DONE",flush=True)
if __name__=="__main__":main()
