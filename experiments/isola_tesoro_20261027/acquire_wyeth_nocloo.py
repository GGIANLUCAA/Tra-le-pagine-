from pathlib import Path
from urllib.request import urlopen,Request
from urllib.parse import urljoin
from html.parser import HTMLParser
from PIL import Image
from io import BytesIO
import json,re,time
ROOT=Path("output/isola-wyeth-color")
ROOT.mkdir(parents=True,exist_ok=True)
URL="https://www.nocloo.com/n-c-wyeth-treasure-island-1911/"
class P(HTMLParser):
 def __init__(self):super().__init__();self.results=[]
 def handle_starttag(self,tag,attrs):
  if tag.lower() not in ("img","a"):return
  d=dict(attrs)
  for k in ("data-src","src","href","srcset","data-lazy-src"):
   v=d.get(k,"")
   if re.search(r"wyeth[-_]treasure|treasure\d\d",v,re.I):
    self.results.append((tag,k,urljoin(URL,v.split(",")[0].split(" ")[0])))
records=[]
try:
 with urlopen(Request(URL,headers={"User-Agent":"Mozilla/5.0 (educational illustrated book archive review)"}),timeout=30) as resp:
  html=resp.read(4_000_000).decode('utf8','replace')
 parser=P();parser.feed(html)
 candidates=list(dict.fromkeys(u for tag,k,u in parser.results if 'images' in u or 'wp-content' in u))
 print("PAGE",len(html),"CANDIDATES",len(candidates),candidates[:10],flush=True)
 for n,url in enumerate(candidates[:24]):
  try:
   with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=25) as resp:blob=resp.read(9_000_000)
   with Image.open(BytesIO(blob)) as im:
    w,h=im.size
    if min(w,h)<400:continue
    name=f"{len(records)+1:02d}.jpg"
    im.convert("RGB").save(ROOT/name,quality=92)
   records.append({"name":name,"url":url,"width":w,"height":h})
   print("OK",name,w,h,url,flush=True)
  except Exception as e:
   print("FAIL",str(e)[:130],url,flush=True)
  time.sleep(0.4)
except Exception as e:
 print("PAGE_FAIL",type(e).__name__,str(e)[:200])
(ROOT/"MANIFEST.json").write_text(json.dumps(records,indent=2))
print("COLLECTED",len(records),flush=True)
if len(records)<7: raise SystemExit("Insufficient artworks: no misleading success.")
