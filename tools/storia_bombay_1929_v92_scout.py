#!/usr/bin/env python3
"""One-time zero-cost archived footage scout: Bombay January 1929, 13m source.
Output contact sheets and source quality metadata; NO render, NO paid APIs.
"""
import pathlib,json,hashlib,subprocess,urllib.request,cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=pathlib.Path("output/storia_bombay_1929_v92")
ROOT.mkdir(parents=True,exist_ok=True)
SRC=ROOT/"BOMBAY_1929_ORIGINAL.webm"
SOURCE_URL="https://commons.wikimedia.org/wiki/Special:Redirect/file/Street_Scenes_in_Bombay%2C_India_%28real_sound%29%2C_Jan_1929.webm"
def main():
  if not SRC.is_file() or SRC.stat().st_size<100000000:
    request=urllib.request.Request(SOURCE_URL,headers={"User-Agent":"TraLePagine-HistoricalScout/1.0"})
    with urllib.request.urlopen(request,timeout=160) as inp,SRC.open("wb") as f:
      while True:
        data=inp.read(1048576)
        if not data:break
        f.write(data)
        if f.tell()>160000000:raise ValueError("Source bigger than verified 128.82 MB")
  if SRC.stat().st_size < 120000000:raise ValueError("Archival film incomplete")
  cap=cv2.VideoCapture(str(SRC))
  fps=cap.get(cv2.CAP_PROP_FPS);frames=cap.get(cv2.CAP_PROP_FRAME_COUNT)
  dur=frames/fps
  w,h=round(cap.get(3)),round(cap.get(4))
  if w!=1280 or h!=720 or dur<800 or fps<15:raise ValueError("Unexpected original source")
  print("BOMBAY_ARCHIVAL_SOURCE",w,h,dur,fps,SRC.stat().st_size,flush=True)
  seconds=[round(float(x),1) for x in np.linspace(9,802,64)]
  thumb_w,thumb_h=220,360
  font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",18)
  result=[]
  for i,t in enumerate(seconds):
    cap.set(cv2.CAP_PROP_POS_MSEC,t*1000)
    ok,fr=cap.read()
    if not ok:continue
    gr=cv2.cvtColor(fr,cv2.COLOR_BGR2GRAY)
    native_h,native_w=gr.shape
    x=int(native_w/2);crop_w=round(native_h*9/16)
    # optimize centered true pixels; no upscaling before crop
    crop=gr[:,x-crop_w//2:x-crop_w//2+crop_w]
    if crop.size==0:raise ValueError("empty cropped frame")
    scaled=cv2.resize(crop,(thumb_w,thumb_h),interpolation=cv2.INTER_AREA)
    focus=float(cv2.Laplacian(cv2.resize(crop,(160,284)),cv2.CV_64F).var())
    color=Image.fromarray(scaled).convert("RGB")
    result.append((t,focus,color))
  cap.release()
  cols,rows=8,8
  page=Image.new("RGB",(cols*(thumb_w+16),rows*(thumb_h+47)),(12,17,23))
  pen=ImageDraw.Draw(page)
  for i,(t,sharp,thumb) in enumerate(result):
    x=(i%cols)*(thumb_w+16)+8;y=(i//cols)*(thumb_h+47)+6
    page.paste(thumb,(x,y))
    pen.text((x,y+thumb_h+2),f"{i+1:02} · {t:.1f}s",font=font,fill=(238,238,220))
    pen.text((x,y+thumb_h+23),f"focus {sharp:.1f}",font=font,fill=(174,190,204))
  page.save(ROOT/"SCOUT_64_VERT_FRAMES.jpg",quality=88)
  sha=hashlib.sha256()
  with SRC.open("rb") as f:
    for chunk in iter(lambda:f.read(1048576),b""):sha.update(chunk)
  (ROOT/"SCOUT_SOURCE.json").write_text(json.dumps({
    "title":"Bombay, January 1929", "commons_url":"https://commons.wikimedia.org/wiki/File:Street_Scenes_in_Bombay,_India_(real_sound),_Jan_1929.webm",
    "status":"SOURCE_ONLY_NOT_VIDEO_NOT_QA_APPROVED",
    "license_declaration":"PD India + PD US (per Wikimedia page). Italian territorial verification pending",
    "sha256":sha.hexdigest(),"width":w,"height":h,"fps":fps,"duration":dur,
    "total_frames_scanned":len(result),
    "sample_seconds":[{"time_s":t,"focus":round(s,1)} for t,s,_ in result]
  },ensure_ascii=False,indent=2))
  print("ARCHIVE_SCOUT_CONTACT_READY",len(result),str(ROOT/"SCOUT_64_VERT_FRAMES.jpg"),flush=True)
if __name__=="__main__":
  main()
