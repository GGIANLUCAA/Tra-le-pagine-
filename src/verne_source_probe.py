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
