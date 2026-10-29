#!/usr/bin/env python3
"""V83: NEW YORK 1911 — authentic moving film + source-locked colored freeze frames."""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode,quote
import importlib.util,json,hashlib,html,zipfile
import cv2,numpy as np

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("base",ROOT/"src/storia_v80_new_york_venice.py")
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
base.OUT=Path("output/storia_v83_new_york_1911")
META={"city":"NEW YORK","year":"1911",
 "commons":"File:New York 1911.webm",
 "page":"https://commons.wikimedia.org/wiki/File:New_York_1911.webm",
 "description":"Genuine 1911 New York city moving street life. Svenska Biografteatern.",
 "shots":[
  {"t":56.0,"center":635,"length":2.20,"tag":"early New York streets and transport"},
  {"t":150.0,"center":640,"length":2.20,"tag":"New York 1911 daily city life"},
  {"t":258.0,"center":640,"length":2.30,"tag":"historic moving street scene in New York"},
  {"t":415.0,"center":640,"length":2.20,"tag":"historic Manhattan activity captured on film"}
 ]}
def get_archive(d):
 api="https://commons.wikimedia.org/w/api.php?"+urlencode({"action":"query","format":"json","formatversion":"2","prop":"imageinfo","titles":META["commons"],"iiprop":"url|size|mime|extmetadata"})
 with urlopen(Request(api,headers={"User-Agent":base.UA,"Accept":"application/json"}),timeout=60) as r:
  data=json.load(r)
 it=data["query"]["pages"][0]["imageinfo"][0]
 assert it["mime"]=="video/webm", "Not a moving film"
 master=it["url"]; filename=master.rsplit("/",1)[-1]
 # Prefer verified 720p Wikimedia transcode: within free CI constraints, no billable services.
 link=master.rsplit("/",1)[0].replace("/commons/","/commons/transcoded/")+"/"+filename+"/"+filename+".720p.vp9.webm"
 dest=d/"AUTHENTIC_1911_FILM_720p.webm"
 if not dest.exists() or dest.stat().st_size<15_000_000:
  req=Request(link,headers={"User-Agent":base.UA})
  with urlopen(req,timeout=120) as resp,open(dest,"wb") as out:
   while True:
    chunk=resp.read(1024*1024)
    if not chunk:break
    out.write(chunk)
    if out.tell()>230_000_000:raise RuntimeError("Unexpectedly large transcode")
 cap=cv2.VideoCapture(str(dest))
 w,h=cap.get(3),cap.get(4);fps=cap.get(5);duration=cap.get(7)/max(fps,1);cap.release()
 if w<1100 or h<700 or duration<425 or fps<14:raise RuntimeError("SOURCE_QUALITY_FAILED "+str((w,h,fps,duration)))
 lic={k:html.unescape(v.get("value","")) for k,v in it.get("extmetadata",{}).items() if k in ("LicenseShortName","Copyrighted","LicenseUrl","Artist")}
 detail={"page":META["page"],"creator":"Svenska Biografteatern","source":link,"sha256":base.sha(dest),"source_resolution":[w,h],"source_duration":duration,"source_fps":fps,"commons_licensing":lic,"rights_for_italy":"PENDING_HUMAN_REVIEW","note":"Color is an interpretation; audio is new; no fabricated source frames."}
 (d/"SOURCE_QA.json").write_text(json.dumps(detail,indent=2,ensure_ascii=False))
 print("REAL_FILM_ACQUIRED",w,h,duration,dest.stat().st_size,flush=True)
 return dest,detail

def main():
 d=base.OUT;d.mkdir(parents=True,exist_ok=True)
 source,info=get_archive(d)
 stills=base.grab_stills(source,META,d)
 dd,session,model=base.load_dd()
 photos=[]
 for rec in stills:
  src=d/rec["source_frame"]
  # Restore scene without remodelling people or objects. Neural chroma
  # prediction plus conservative local clarity preserves original geometry.
  img=base.natural_color(dd,session,src)
  lab=cv2.cvtColor(img,cv2.COLOR_BGR2LAB)
  clahe=cv2.createCLAHE(clipLimit=1.5,tileGridSize=(12,12))
  l=lab[:,:,0];lab[:,:,0]=cv2.addWeighted(l,.82,clahe.apply(l),.18,0)
  img=cv2.cvtColor(lab,cv2.COLOR_LAB2BGR)
  soft=cv2.GaussianBlur(img,(0,0),0.8)
  img=cv2.addWeighted(img,1.25,soft,-.25,0)
  target=d/("PHOTO_AI_%02d.png"%rec["scene"]);cv2.imwrite(str(target),img)
  geom=base.similarity(cv2.imread(str(src)),img)
  sat=float(cv2.cvtColor(img,cv2.COLOR_BGR2HSV)[:,:,1].mean())
  if geom<0.86 or sat<9:raise RuntimeError("PHOTO_QA_REJECT geometry="+str(geom)+" saturation="+str(sat))
  photos.append({**rec,"photo_file":target.name,"photo_sha256":base.sha(target),"geom_corr":round(geom,3),"sat":round(sat,1),"model":"DDColor color restoration without generative replacement","human_qa":"PENDING"})
  print("COLOR_PHOTO_READY",rec["scene"],geom,sat,flush=True)
 (d/"PHOTO_QA.json").write_text(json.dumps(photos,ensure_ascii=False,indent=2))
 base.render(META,source,photos,d,info)
 old=d/"LA_STORIA_RIVIVE_NEW_YORK_1911_V80.mp4"
 new=d/"LA_STORIA_RIVIVE_NEW_YORK_1911_V83.mp4"
 old.rename(new)
 qa_path=d/"QA.json";qa=json.loads(qa_path.read_text())
 qa.update({"version":"V83","video":new.name,"sha256":base.sha(new),"colorization_note":"Neural plausible color; not a new AI-created face or invented history","semantic_qa":"PENDING_HUMAN","publication":"REVIEW_ONLY"})
 qa_path.write_text(json.dumps(qa,indent=2,ensure_ascii=False))
 kit=d/"LA_STORIA_RIVIVE_NEW_YORK_1911_KIT.zip"
 with zipfile.ZipFile(kit,"w",compression=zipfile.ZIP_DEFLATED) as z:
  for x in [new,d/"COVER.jpg",d/"BEFORE_AFTER_ACTUAL_GENERATED.jpg",qa_path,d/"SOURCE_QA.json",d/"PHOTO_QA.json",*d.glob("POST_*.txt")]:z.write(x,x.name)
 with zipfile.ZipFile(kit) as z:assert z.testzip() is None
 print("V83_NEW_YORK_1911_VIDEO_READY",new,new.stat().st_size,"ZIP",kit,kit.stat().st_size,flush=True)
if __name__=="__main__":main()
