#!/usr/bin/env python3
"""One EPUB download to visually review all Kate Greenaway illustrations; no generation."""
import hashlib,json,re,zipfile
from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from PIL import Image,ImageDraw,ImageFont,ImageOps
OUT=Path("output/pifferaio_hamelin_source_review")
HTML="https://www.gutenberg.org/cache/epub/18343/pg18343-images.html"
EPUB="https://www.gutenberg.org/ebooks/18343.epub3.images"
def font(n):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",n)
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 s=requests.Session();s.headers.update({"User-Agent":"TraLePagine-Editorial/1.0 (single book source review)"})
 h=s.get(HTML,timeout=45);h.raise_for_status()
 b=s.get(EPUB,timeout=55);b.raise_for_status()
 if not 100000<len(b.content)<25000000:raise RuntimeError("EPUB unexpected size")
 soup=BeautifulSoup(h.content,"html.parser")
 items=[]
 for tag in soup.find_all("img"):
  src=tag.get("src","")
  if not re.search(r"\.(?:jpe?g|png|gif)$",src,re.I):continue
  mark=tag.find_previous(class_=re.compile("pagenum",re.I))
  m=re.search(r"(?:Pg|Page)?\s*(\d{1,3})",mark.get_text(" ",strip=True),re.I) if mark else None
  items.append({"src":src,"page":int(m.group(1)) if m else None,"alt":tag.get("alt","")})
 with zipfile.ZipFile(BytesIO(b.content)) as z:
  files={Path(n).name:n for n in z.namelist() if re.search(r"\.(?:jpe?g|png|gif)$",n,re.I)}
  seen=set();data=[]
  for item in items:
   name=Path(item["src"]).name
   if name in seen or name not in files:continue
   seen.add(name)
   raw=z.read(files[name])
   try:
    with Image.open(BytesIO(raw)) as im:
     im.load()
     if im.width<200 or im.height<200:continue
     pic=im.convert("RGB")
   except OSError:continue
   p=OUT/("ORIGINAL_%02d_"%len(data)+name)
   pic.save(p,quality=92)
   data.append({**item,"filename":p.name,"sha256":hashlib.sha256(raw).hexdigest(),
      "size":[pic.width,pic.height],"source_page":HTML,"epub_url":EPUB})
 if len(data)<16:raise RuntimeError("Not enough original illustrations in EPUB: "+str(len(data)))
 cols=5;w=255;h=335;rows=(len(data)+cols-1)//cols
 board=Image.new("RGB",(cols*w,rows*h+105),(242,237,228))
 d=ImageDraw.Draw(board);d.rectangle((0,0,board.width,95),fill=(21,44,56))
 d.text((25,28),"GREENAWAY | ORIGINALI DA VERIFICARE",font=font(29),fill="white")
 for i,row in enumerate(data):
  x=i%cols*w;y=95+i//cols*h
  pic=Image.open(OUT/row["filename"])
  thumb=ImageOps.contain(pic,(w-16,h-80))
  board.paste(thumb,(x+(w-thumb.width)//2,y+8))
  d.text((x+9,y+h-58),"#%02d  pagina %s"%(i+1,row["page"]),font=font(16),fill=(21,44,56))
  d.text((x+9,y+h-33),Path(row["src"]).name[:28],font=font(13),fill=(21,44,56))
 board.save(OUT/"TUTTE_LE_TAVOLE_GREENAWAY.jpg",quality=90)
 (OUT/"CATALOGO_ORIGINALI.json").write_text(json.dumps({"images":data,"source":HTML,
  "visual_review":"pending manual scene match","note":"Not all images depict the scene named by nearest page number."},
  ensure_ascii=False,indent=2)+"\n")
 print("EPUB_SINGLE_REQUEST",len(b.content),"IMAGES",len(data),flush=True)
if __name__=="__main__":main()
