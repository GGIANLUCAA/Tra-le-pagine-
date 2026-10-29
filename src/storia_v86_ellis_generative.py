#!/usr/bin/env python3
"""V86. Reject inadequate DDColor fallback, require generative photo restoration on source frame."""
from pathlib import Path
import importlib.util,sys,json,cv2,zipfile
ROOT=Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location("base",ROOT/"src/storia_v80_new_york_venice.py")
base=importlib.util.module_from_spec(sp);sp.loader.exec_module(base)
sp2=importlib.util.spec_from_file_location("v85",ROOT/"src/storia_v85_ellis_island_1903.py")
v85=importlib.util.module_from_spec(sp2);sp2.loader.exec_module(v85)
meta=v85.meta
base.OUT=Path("output/storia_v86_ellis_1903")
def main():
 d=base.OUT;d.mkdir(parents=True,exist_ok=True)
 src,info=base.acquire(meta,d)
 recs=base.grab_stills(src,meta,d)
 dd,ss,model=base.load_dd()
 # base method FAILS if free image model is down: no fake high quality or paid API.
 photos=base.enhanced_ai_images(meta,recs,d,dd,ss)
 base.render(meta,src,photos,d,info)
 old=d/"LA_STORIA_RIVIVE_ELLIS ISLAND_1903_V80.mp4";new=d/"ELLIS_ISLAND_1903_V86.mp4";old.rename(new)
 from PIL import Image,ImageDraw
 board=Image.new("RGB",(4*240,2*445),(18,20,24));draw=ImageDraw.Draw(board)
 for j,p in enumerate(photos[:4]):
  a=Image.open(d/p["source_frame"]).convert("RGB").resize((230,408))
  b=Image.open(d/p["photo_file"]).convert("RGB").resize((230,408))
  board.paste(a,(j*240+5,26));board.paste(b,(j*240+5,470))
  draw.text((j*240+8,4),"SOURCE "+str(j+1),fill="white")
  draw.text((j*240+8,449),"PHOTO AI "+str(j+1),fill="white")
 board.save(d/"AI_RESTORATION_REVIEW.jpg",quality=92)
 q=json.loads((d/"QA.json").read_text());q.update({"version":"V86","video":new.name,
    "generative_restoration":"Finegrain free image enhancer applied to actual colorized frame",
    "manual_verification":"PENDING","social_publication":False,"credits_vidu_used":0})
 (d/"QA.json").write_text(json.dumps(q,indent=2,ensure_ascii=False))
 k=d/"ELLIS_ISLAND_1903_KIT_V86.zip"
 with zipfile.ZipFile(k,"w",zipfile.ZIP_DEFLATED) as z:
  for f in [new,d/"COVER.jpg",d/"AI_RESTORATION_REVIEW.jpg",d/"QA.json",d/"SOURCE_QA.json",d/"PHOTO_QA.json",*d.glob("POST_*.txt")]:z.write(f,f.name)
 assert zipfile.ZipFile(k).testzip() is None
 print("V86_REAL_GENERATIVE_FILM",new,new.stat().st_size,flush=True)
if __name__=="__main__":main()
