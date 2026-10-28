#!/usr/bin/env python3
"""V67 source ingestion and visual editor scouting of Vienna Austria market/rural 1920 CC0 film."""
import hashlib, json, os, urllib.parse, urllib.request
from pathlib import Path
import cv2
from PIL import Image, ImageDraw, ImageFont
TITLE="File:Marché couvert et scènes rurales - AI140423.webm"
PAGE="https://commons.wikimedia.org/wiki/File:March%C3%A9_couvert_et_sc%C3%A8nes_rurales_-_AI140423.webm"
OUT=Path("output/storia_rivive_v67_vienna_1920");OUT.mkdir(parents=True,exist_ok=True)
SOURCE=OUT/"VIENNA_1920_ARCHIVIO_CC0.webm"
UA="TraLePagineStoriaRivive/0.7 (https://github.com/GGIANLUCAA/Tra-le-pagine-; educational, nonmonetized)"
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(2**20),b""):h.update(b)
 return h.hexdigest()
def original():
 q=urllib.parse.urlencode({"action":"query","format":"json","formatversion":2,"prop":"imageinfo",
  "titles":TITLE,"iiprop":"url|size|mime|extmetadata","iiextmetadatafilter":"LicenseShortName|LicenseUrl|Artist"})
 req=urllib.request.Request("https://commons.wikimedia.org/w/api.php?"+q,headers={"User-Agent":UA})
 with urllib.request.urlopen(req,timeout=45) as r:j=json.load(r)
 info=j["query"]["pages"][0]["imageinfo"][0]
 lic=info.get("extmetadata",{}).get("LicenseShortName",{}).get("value","")
 url=info.get("extmetadata",{}).get("LicenseUrl",{}).get("value","")
 if "cc0" not in lic.lower().replace(" ","") and "publicdomain/zero" not in url:
  raise ValueError("Non-CC0 movie source: "+lic+" "+url)
 if not info["mime"].startswith("video/") or info["size"]>45_000_000:
  raise ValueError("Wrong mime/file size")
 if not SOURCE.is_file() or SOURCE.stat().st_size!=info["size"]:
  req=urllib.request.Request(info["url"],headers={"User-Agent":UA})
  with urllib.request.urlopen(req,timeout=120) as fp,open(SOURCE,"wb") as dst:
   for b in iter(lambda:fp.read(2**20),b""):dst.write(b)
 if SOURCE.stat().st_size!=info["size"]:raise ValueError("Truncated download")
 info2={"archival_source":"Musée départemental Albert-Kahn","artist":"Lucien Le Saint",
        "original_file_page":PAGE,"title":TITLE,"license_claim":lic,"license_url":url,
        "source_file_sha256":sha(SOURCE),"source_size":SOURCE.stat().st_size,
        "rights_status":"CC0 stated on exact Commons file. Independent legal/privacy rights still reviewed prior public release.",
        "date_note":"Vienna Austria, March 1920: covered food market and rural firewood/forest scenes; do not claim they occur at one location/time."}
 (OUT/"SOURCE_PROVENANCE.json").write_text(json.dumps(info2,ensure_ascii=False,indent=2)+"\n")
 return SOURCE,info2

def sheets():
 cap=cv2.VideoCapture(str(SOURCE));fps=cap.get(cv2.CAP_PROP_FPS);num=cap.get(cv2.CAP_PROP_FRAME_COUNT)
 if fps<=0 or num<=0:raise ValueError("Invalid video")
 dur=num/fps
 print("FILM_METADATA",{"fps":fps,"frames":num,"duration":dur},flush=True)
 times=list(range(2,int(dur)-1,5))
 try:font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",18)
 except:font=ImageFont.load_default()
 frame_log=[]
 for sheet_idx in range(0,len(times),24):
  subset=times[sheet_idx:sheet_idx+24]
  sheet=Image.new("RGB",(6*235,4*190),(24,26,32));d=ImageDraw.Draw(sheet)
  for i,t in enumerate(subset):
   cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,frame=cap.read()
   if not ok:continue
   frame_log.append({"seconds":t,"n":len(frame_log)})
   preview=cv2.cvtColor(cv2.resize(frame,(220,165)),cv2.COLOR_BGR2RGB)
   x=(i%6)*235+7;y=(i//6)*190+6
   sheet.paste(Image.fromarray(preview),(x,y))
   d.rectangle((x,y+134,x+89,y+165),fill=(15,15,18))
   d.text((x+6,y+141),f"{t:03d}s",font=font,fill=(245,242,225))
  name=OUT/f"CONTACT_{sheet_idx//24+1:02d}.jpg"
  sheet.save(name,quality=88);print("CONTACT_COMPLETE",str(name),flush=True)
 cap.release()
 (OUT/"FRAME_INDEX.json").write_text(json.dumps({"source_fps":fps,"source_duration":dur,"samples":frame_log},indent=2))
if __name__=="__main__":
 original();sheets()
