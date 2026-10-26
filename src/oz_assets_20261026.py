#!/usr/bin/env python3
"""Read the 1900 Denslow illustrations from Gutenberg; fail on missing scenes."""
import hashlib,json,re,time,unicodedata
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request,urlopen
from PIL import Image,ImageOps,ImageFilter,ImageDraw
EP=Path("episodes/oz_dorothy_20261026")
URL="https://www.gutenberg.org/cache/epub/43936/pg43936-images.html"
SPLIT=re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-ÙÈÉ«“])")
class Images(HTMLParser):
 def __init__(self): super().__init__();self.items={}
 def handle_starttag(self,tag,attrs):
  if tag!="img":return
  a=dict(attrs);alt=a.get("alt","");src=a.get("src","")
  if alt and src:self.items.setdefault(key(alt),[]).append((alt,src))
def key(s):
 return re.sub(r"[^a-z0-9]","",''.join(c for c in unicodedata.normalize("NFKD",str(s).lower()) if not unicodedata.combining(c)))
def fetch(url):
 with urlopen(Request(url,headers={"User-Agent":"TraLePagineEditorial/1.0"}),timeout=35) as r:return r.read(14000000)
def frame(im,n):
 im=ImageOps.exif_transpose(im.convert("RGB"))
 bg=ImageOps.fit(im,(960,1707)).filter(ImageFilter.GaussianBlur(42)).convert("RGBA")
 bg=Image.alpha_composite(bg,Image.new("RGBA",bg.size,(13,29,41,170)))
 d=ImageDraw.Draw(bg);d.rounded_rectangle((28,95,932,1612),radius=18,fill=(239,225,203,255),outline=(209,175,116,255),width=5)
 art=ImageOps.contain(im,(820,1425),Image.Resampling.LANCZOS)
 bg.alpha_composite(art.convert("RGBA"),((960-art.width)//2,(1707-art.height)//2))
 return bg.convert("RGB")
def main():
 plan=json.loads((EP/"scene_plan_oz.json").read_text())["scenes"]
 text=(EP/"testo.txt").read_text();pars=[x.strip() for x in text.split("\n\n") if x.strip()]
 assert len(plan)==len(pars) and all(x["narration"]==y for x,y in zip(plan,pars))
 parser=Images();parser.feed(fetch(URL).decode("utf-8","replace"))
 absent=[x["source_alt"] for x in plan if key(x["source_alt"]) not in parser.items]
 if absent:raise RuntimeError("Illustrations unavailable (no generic fallback): "+repr(absent))
 (EP/"images").mkdir(exist_ok=True)
 images=[];cues=[];start=0
 for n,(row,para) in enumerate(zip(plan,pars),1):
  alt,src=parser.items[key(row["source_alt"])][0];link=urljoin(URL,src);raw=fetch(link)
  with Image.open(BytesIO(raw)) as im:
   if min(im.size)<125:raise RuntimeError("Insufficient source image: "+alt)
   result=frame(im,n)
  path=EP/"images"/("scena_%02d.jpg"%n);result.save(path,quality=92,optimize=True)
  if path.stat().st_size<35000:raise RuntimeError("Image too small: "+str(path))
  cues.append({"start_sentence":start,"asset":n,"description":row["intent"],"narration_anchor":SPLIT.split(para)[0]})
  start+=len([x for x in SPLIT.split(para) if x.strip()])
  images.append({"asset":n,"image":str(path),"original_artist":"W. W. Denslow","source_url":link,"source_page":URL,"source_alt":alt,"sha256":hashlib.sha256(raw).hexdigest(),"rights":"Original 1900 public domain per Library of Congress","visual_review":"pending"})
  print(n,alt,flush=True);time.sleep(.1)
 (EP/"scene_cues.json").write_text(json.dumps(cues,ensure_ascii=False,indent=2))
 (EP/"PROVENIENZA_IMMAGINI.json").write_text(json.dumps({"images":images,"source":"https://www.loc.gov/item/03032405/","rights_review":"Original Denslow art public domain; artistic review pending"},ensure_ascii=False,indent=2))
 print("IMAGE PREFLIGHT: SUCCESS",len(images),flush=True)
if __name__=="__main__":main()
