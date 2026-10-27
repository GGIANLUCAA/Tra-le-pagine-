"""One-request inspection of the 1871 Riou/de Neuville Gutenberg image index."""
from html.parser import HTMLParser
from urllib.request import Request,urlopen
from urllib.parse import urljoin
import json
URL="https://www.gutenberg.org/cache/epub/54873/pg54873-images.html"
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.images=[]
 def handle_starttag(self,tag,attrs):
  if tag=="img":
   a=dict(attrs);self.images.append({"src":urljoin(URL,a.get("src","")),"alt":a.get("alt",""),"title":a.get("title",""),"class":a.get("class",""),"id":a.get("id","")})
with urlopen(Request(URL,headers={"User-Agent":"TraLePagineEditorial/1.0"}),timeout=40) as x:
 html=x.read(9000000).decode("utf-8","replace")
p=Parser();p.feed(html)
print("SOURCE",URL,"HTML_BYTES",len(html),"IMAGE_COUNT",len(p.images),flush=True)
for i,v in enumerate(p.images):print(f"IMAGE_{i:03d}: {json.dumps(v,ensure_ascii=False)}",flush=True)

print("CAPTION_CONTEXT_SNIPPETS",flush=True)
for number in (4,9,15,23,31,40,49,55,64,72,78,85,96,107):
 marker=f"im{number:03}.jpg"
 pos=html.find(marker)
 if pos>=0:
  print("CONTEXT",number,json.dumps(html[max(0,pos-120):pos+650],ensure_ascii=False),flush=True)

import re
from html import unescape
captions=[]
for m in re.finditer(r'<img\b[^>]*src="images/(im\d+)\.jpg"[^>]*>\s*<p class="caption"[^>]*>(.*?)</p>',html,re.S|re.I):
 clean=unescape(re.sub(r"<[^>]+>"," ",m.group(2)))
 clean=" ".join(clean.split())
 captions.append((m.group(1),clean))
print("CAPTIONS_FOUND",len(captions),flush=True)
for num,caption in captions:print("CAPTION",num,json.dumps(caption,ensure_ascii=False),flush=True)
