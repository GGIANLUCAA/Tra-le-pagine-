#!/usr/bin/env python3
"""One-shot, read-only source inventory for Alice Rackham 1907, no paid APIs."""
from pathlib import Path
from urllib.parse import urljoin
from io import BytesIO
import json, requests
from bs4 import BeautifulSoup
from PIL import Image, ImageOps, ImageDraw
URL="https://www.gutenberg.org/cache/epub/28885/pg28885-images.html"
OUT=Path("output/alice_wonderland_20261028")
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 s=requests.Session();s.headers.update({"User-Agent":"TraLePagineStudio/1.0 (one public-domain illustrated ebook; editorial source review)"})
 r=s.get(URL,timeout=55);r.raise_for_status()
 print("GUTENBERG_HTML",r.status_code,len(r.content),flush=True)
 soup=BeautifulSoup(r.content,"html.parser")
 rows=[]
 for i,tag in enumerate(soup.find_all("img")):
  src=tag.get("src","");alt=tag.get("alt","");title=tag.get("title","")
  parent=tag.parent
  near=" ".join(parent.stripped_strings)[:170] if parent else ""
  prev=tag.find_previous(string=True)
  prev=str(prev).strip()[:130] if prev else ""
  rows.append({"index":i,"src":src,"alt":alt,"title":title,"near":near,"prev":prev,"url":urljoin(URL,src)})
  print("IMAGE",i,repr(src),repr(alt[:110]),repr(near[:100]),flush=True)
 (OUT/"SOURCE_INVENTORY.json").write_text(json.dumps({"url":URL,"count":len(rows),"images":rows},ensure_ascii=False,indent=2))
 if len(rows)<15:raise RuntimeError("Too few illustrated source images, no TTS")
 previews=[]
 for row in rows:
  if not row["src"]:continue
  try:
   u=row["url"];resp=s.get(u,timeout=30);resp.raise_for_status()
   with Image.open(BytesIO(resp.content)) as im:
    im.load();w,h=im.size
    if min(w,h)<150:continue
    img=ImageOps.contain(im.convert("RGB"),(225,270))
    previews.append((row["index"],row["alt"],img,(w,h)))
  except Exception as e:print("PREVIEW_FAIL",row["index"],type(e).__name__,str(e)[:100],flush=True)
  if len(previews)>=80:break
 if len(previews)<12:raise RuntimeError("Source image downloads insufficient, no TTS")
 cols=5;cw,ch=270,350;rows_n=(len(previews)+cols-1)//cols
 board=Image.new("RGB",(cols*cw,rows_n*ch),(242,236,223));d=ImageDraw.Draw(board)
 for j,(idx,alt,im,size) in enumerate(previews):
  x=(j%cols)*cw;y=(j//cols)*ch
  board.paste(im,(x+(cw-im.width)//2,y+10))
  d.text((x+8,y+282),f"{idx}: {size[0]}x{size[1]}",fill=(20,30,35))
  d.text((x+8,y+301),alt[:33],fill=(20,30,35))
 board.save(OUT/"CONTACT_SHEET.jpg",quality=87)
 print("SOURCE_INVENTORY_READY",len(rows),"preview",len(previews),flush=True)
if __name__=="__main__":main()
