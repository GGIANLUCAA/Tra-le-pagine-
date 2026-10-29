#!/usr/bin/env python3
"""V85 ELLIS ISLAND 1903. Real archival footage; four independently restored SAME-FRAME portraits.
Produces no generated people, substitutions, invented motion or paid API calls."""
from pathlib import Path
import cv2,numpy as np,json,zipfile,importlib.util
ROOT=Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location("base",ROOT/"src/storia_v80_new_york_venice.py")
base=importlib.util.module_from_spec(sp);sp.loader.exec_module(base)
base.OUT=Path("output/storia_v85_ellis_1903")
meta={"city":"ELLIS ISLAND","year":"1903",
 "commons":"File:Emigrants (i.e. immigrants) landing at Ellis Island -.webm",
 "page":"https://commons.wikimedia.org/wiki/File:Emigrants_(i.e._immigrants)_landing_at_Ellis_Island_-.webm",
 "description":"Genuine Alfred C. Abadie, Edison film July 24 1903; arrivals disembark from the William Myers at Ellis Island",
 "shots":[
  {"t":91.5,"center":1030,"length":2.00,"tag":"people disembarking in period coats carrying luggage"},
  {"t":103.2,"center":720,"length":2.20,"tag":"real female arrivals and family walking past early camera"},
  {"t":115.8,"center":590,"length":2.10,"tag":"immigrant arrivals walking on dock with bags and hats"},
  {"t":141.0,"center":835,"length":2.10,"tag":"passengers disembarking close to the original camera"}
 ]}
def relight_and_restore(bgr):
    # DDColor models trained to predict plausible ab channels. Improve visible material clarity
    # without fabricating bodies, wheels, garments, faces, buildings or expressions.
    lab=cv2.cvtColor(bgr,cv2.COLOR_BGR2LAB)
    l,a,b=cv2.split(lab)
    l=cv2.addWeighted(l,.60,cv2.createCLAHE(clipLimit=2.1,tileGridSize=(10,10)).apply(l),.40,0)
    img=cv2.cvtColor(cv2.merge((l,a,b)),cv2.COLOR_LAB2BGR)
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV).astype("float32")
    original_sat=float(np.mean(hsv[:,:,1]))
    amplification=min(6.0,max(1.45,60.0/max(5.,original_sat)))
    # Rich, not neon, and genuine luminance protected.
    hsv[:,:,1]=np.minimum(170,hsv[:,:,1]*amplification+5.0)
    hsv[:,:,2]=np.minimum(252,hsv[:,:,2]*1.035+3.)
    img=cv2.cvtColor(hsv.astype("uint8"),cv2.COLOR_HSV2BGR)
    smooth=cv2.bilateralFilter(img,7,22,3)
    img=cv2.addWeighted(img,1.20,smooth,-.20,0)
    return img
def main():
 d=base.OUT;d.mkdir(parents=True,exist_ok=True)
 src,info=base.acquire(meta,d)
 recs=base.grab_stills(src,meta,d)
 dd,ss,model=base.load_dd()
 photos=[]
 for r in recs:
    old=cv2.imread(str(d/r["source_frame"]))
    color=base.natural_color(dd,ss,d/r["source_frame"])
    photo=relight_and_restore(color)
    # ENHANCE structural detail only with source matching image. Not face synthesis.
    gray_old=cv2.cvtColor(old,cv2.COLOR_BGR2GRAY)
    sharp=cv2.detailEnhance(photo,sigma_s=6,sigma_r=.16)
    photo=cv2.addWeighted(photo,.67,sharp,.33,0)
    hs=cv2.cvtColor(photo,cv2.COLOR_BGR2HSV)
    sat=float(hs[:,:,1].mean())
    geom=base.similarity(old,photo)
    fn=d/("PHOTO_AI_%02d.png"%r["scene"])
    cv2.imwrite(str(fn),photo,[cv2.IMWRITE_PNG_COMPRESSION,2])
    if geom<.83 or sat<24:raise RuntimeError("PHOTOGRAPHIC_COLOR_REJECTED: %d saturation %.1f source-fit %.3f"%(r["scene"],sat,geom))
    photos.append({**r,"photo_file":fn.name,"photo_sha256":base.sha(fn),
      "geom_corr":round(geom,3),"sat":round(sat,1),"method":"DDColor with source-locked photometric and local detail processing",
      "faces":"original faces and original contours; no invented pixels claimed as archival truth",
      "strong_face_reconstruction":"NOT_AVAILABLE_WITH_CURRENT_MODEL"})
    print("COLOR_PHOTO",r["scene"],"sat",round(sat,1),"geometry",round(geom,3),flush=True)
 (d/"PHOTO_QA.json").write_text(json.dumps(photos,indent=2,ensure_ascii=False))
 try:
    base.render(meta,src,photos,d,info)
 except Exception as e:
    print("STRICT_QA_OR_RENDER_FAILED",str(e)[:600],flush=True)
    # Preserve review output if base.render created it; do not declare approved.
    if not list(d.glob("LA_STORIA_RIVIVE*.mp4")):raise
 old=d/"LA_STORIA_RIVIVE_ELLIS ISLAND_1903_V80.mp4"
 if not old.exists():raise RuntimeError("NO_RENDERED_MP4")
 new=d/"ELLIS_ISLAND_1903_V85.mp4"
 old.rename(new)
 qa_path=d/"QA.json"
 if qa_path.exists():
    qa=json.loads(qa_path.read_text())
 else:
    qa={"version":"V85","strict_gate":"FAILED_OR_UNFINISHED"}
 qa.update({"version":"V85","asset":new.name,"source_page":meta["page"],"ai_restoration":"color and source-locked detail, not generative facial replacement",
  "human_visual_approval":"PENDING","publication":"REVIEW_ONLY","spent_Vidu_credits":0})
 qa_path.write_text(json.dumps(qa,ensure_ascii=False,indent=2))
 # Create authentic after-check contact, regardless of the V74 structural algorithm.
 from PIL import Image,ImageDraw
 im=Image.new("RGB",(4*240,2*450),(15,18,23));dr=ImageDraw.Draw(im)
 for j,p in enumerate(photos):
    a=Image.open(d/p["source_frame"]).convert("RGB").resize((232,413))
    b=Image.open(d/p["photo_file"]).convert("RGB").resize((232,413))
    im.paste(a,(j*240+3,24));im.paste(b,(j*240+3,474))
    dr.text((j*240+6,4),f"ORIGINAL {j+1}",fill="white")
    dr.text((j*240+6,454),f"RESTORED {j+1}",fill="white")
 im.save(d/"CONFRONTO_PRIMA_DOPO.jpg",quality=93)
 if not (d/"COVER.jpg").exists():Image.open(d/photos[0]["photo_file"]).convert("RGB").save(d/"COVER.jpg")
 (d/"FONTI.txt").write_text("ELLIS ISLAND 1903 - Alfred C. Abadie (Edison); Library of Congress 00694367\nOriginal: "+meta["page"]+"\nPublic domain per Commons (creator died 1950, US publication 1903). Digital color is conjectural.\nMusical soundtrack composed procedurally; no external licensed music. Human artistic approval pending.\n")
 (d/"POST_FACEBOOK.txt").write_text("ELLIS ISLAND · 1903\nA century ago, these people stepped off a boat and into a new life. Watch authentic footage from 1903 become a color portrait — a digital interpretation of one real instant.\nOriginal film: Library of Congress / Alfred C. Abadie. #EllisIsland #1903 #RestoredHistory\n")
 kit=d/"ELLIS_ISLAND_1903_KIT_V85.zip"
 with zipfile.ZipFile(kit,"w",zipfile.ZIP_DEFLATED) as z:
    for p in [new,d/"COVER.jpg",d/"CONFRONTO_PRIMA_DOPO.jpg",d/"QA.json",d/"SOURCE_QA.json",d/"PHOTO_QA.json",d/"FONTI.txt",d/"POST_FACEBOOK.txt"]:
        z.write(p,p.name)
 with zipfile.ZipFile(kit) as z:assert z.testzip() is None
 print("VIDEO_ARTIFACT_READY",new,new.stat().st_size,"KIT",kit.stat().st_size,flush=True)
if __name__=="__main__":main()
