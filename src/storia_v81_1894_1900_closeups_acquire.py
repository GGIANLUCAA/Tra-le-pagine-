#!/usr/bin/env python3
"""V81: acquire exact original close-up films for modern-face-restoration series.
All three from primary Wikimedia Commons pages with archive SHA verified.
"""
from pathlib import Path
from urllib.request import urlopen,Request
import hashlib,subprocess,json
OUT=Path("output/storia_v81_archive_closeups");OUT.mkdir(parents=True,exist_ok=True)
SOURCES=[
 ("SNEEZE_1894.webm","https://upload.wikimedia.org/wikipedia/commons/3/35/Fred_Ott%27s_Sneeze_%281894%29.webm","a310a9e466490de4c32b39f25411790023dbc198e04902a2276f1fdfec2cd690"),
 ("KISS_1896.webm","https://upload.wikimedia.org/wikipedia/commons/d/dd/The_Kiss_%281896%29.webm","862317cd5f159788638384845f7dc7624ca01c528e15465dc1ed71336e5d53f3"),
 # 1900 lower-resolution 480p clip excluded: faces not trustworthy as modern photography
]
def digest(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for x in iter(lambda:f.read(1048576),b""):h.update(x)
 return h.hexdigest()
docs=[]
for fname,url,expected in SOURCES:
 p=OUT/fname
 if not p.exists() or digest(p)!=expected:
  req=Request(url,headers={"User-Agent":"TraLePagine-Historical-Restoration/1.0 (educational research)"})
  with urlopen(req,timeout=140) as res,p.open("wb") as f:
   while buf:=res.read(1048576):f.write(buf)
 h=digest(p)
 if h!=expected:raise RuntimeError("Actual source mismatch "+fname+":"+h)
 probe=subprocess.run(["ffprobe","-v","error","-show_entries","stream=codec_name,width,height,r_frame_rate:format=duration,size","-of","json",str(p)],capture_output=True,text=True,check=True)
 inf=json.loads(probe.stdout)
 docs.append({"file":fname,"url":url,"sha256":h,"ffprobe":inf,"right":"Commons file record marked public domain; additional territorial legal checks before publication"})
 print("REAL_SOURCE_ACQUIRED",fname,p.stat().st_size,flush=True)
(OUT/"SOURCE_MANIFEST.json").write_text(json.dumps({"sources":docs,"note":"Original historic films only; never use as moving 4K when original source is smaller"},indent=2))
