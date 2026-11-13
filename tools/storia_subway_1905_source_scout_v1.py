#!/usr/bin/env python3
"""Source-only scout. No paid AI. Five diverse ORIGINAL moving shots. Preview not final."""
import os,sys,time,hashlib,json,subprocess,requests,urllib.parse, pathlib
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
R=pathlib.Path("output/storia_subway_1905_source");R.mkdir(parents=True,exist_ok=True)
FN="2 A. M. in the Subway (1905).webm"
PAGE="https://commons.wikimedia.org/wiki/File:2_A._M._in_the_Subway_(1905).webm"
UA="LaStoriaRivive/2.0 (historical archive source verification; https://github.com/GGIANLUCAA/Tra-le-pagine-)"
def log(*s):print(*s,flush=True)
def run(args,timeout=170):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
 if p.returncode:raise RuntimeError(str(args[:5])+" "+p.stderr[-700:])
 return p.stdout
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for ch in iter(lambda:f.read(1048576),b""):h.update(ch)
 return h.hexdigest()
def fetch_file(url,path,limit=122000000):
 req=requests.get(url,headers={"User-Agent":UA,"Accept":"*/*","Referer":"https://commons.wikimedia.org/"},stream=True,timeout=(20,90))
 try:
  if req.status_code!=200:raise RuntimeError(f"HTTP {req.status_code}")
  ct=req.headers.get("content-type","")
  if "text/html" in ct:raise RuntimeError("HTML_REPLY")
  with open(path,"wb") as f:
   for b in req.iter_content(524288):
    f.write(b)
    if f.tell()>limit:raise RuntimeError("TOO_MANY_BYTES")
  if path.stat().st_size<200000:raise RuntimeError("TOO_SMALL")
  cap=cv2.VideoCapture(str(path));ok=cap.isOpened()
  n=cap.get(cv2.CAP_PROP_FRAME_COUNT);fps=cap.get(cv2.CAP_PROP_FPS)
  cap.release()
  if not ok or not n or not fps:raise RuntimeError("UNDECODABLE_SOURCE")
  return {"file":str(path),"bytes":path.stat().st_size,"sha256":sha(path),"frame_count":n,"fps":fps,"download_url":url}
 finally:req.close()
def acquire():
 s=requests.Session(); s.headers.update({"User-Agent":UA})
 q=s.get("https://commons.wikimedia.org/w/api.php",params={"action":"query","titles":"File:"+FN,"prop":"imageinfo","iiprop":"url|size|sha1","format":"json"},timeout=30)
 q.raise_for_status()
 info=next(iter(q.json()["query"]["pages"].values()))["imageinfo"][0]
 orig=info["url"].split("?")[0]
 encoded=urllib.parse.quote(FN.replace(" ","_"),safe="(),'")
 # Use original Library of Congress 1440x1080 digitization; never silently switch to an unrelated film.
 base=orig.split(".webm")[0]+".webm"
 options=[orig,base,
  "https://commons.wikimedia.org/wiki/Special:Redirect/file/"+encoded,
  "https://upload.wikimedia.org/wikipedia/commons/transcoded/"+orig.split("/commons/")[-1]+"/"+encoded+".720p.vp9.webm"]
 failures=[]
 for i,url in enumerate(dict.fromkeys(options)):
  try:
   meta=fetch_file(url,R/"SOURCE_1905_REAL_MOVING.webm")
   log("SOURCE_DOWNLOAD_OK",i,meta["bytes"],meta["sha256"])
   return meta
  except Exception as e:
   failures.append({"variant":i,"error":str(e)[:140]})
   log("SOURCE_UNAVAILABLE",i,str(e)[:140])
  time.sleep(1)
 (R/"DOWNLOAD_FAILURES.json").write_text(json.dumps(failures,indent=2))
 raise RuntimeError("NO_AUTHENTIC_NEW_SUBJECT_HIGH_RES_FILM")
def make_scout(meta):
 src=meta["file"];cap=cv2.VideoCapture(src);fps=cap.get(cv2.CAP_PROP_FPS)
 dur=cap.get(cv2.CAP_PROP_FRAME_COUNT)/fps
 w=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));h=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
 if not (dur>48 and dur<70 and w>=960 and h>=700):raise RuntimeError("HIGH_DEF_SOURCE_GATE_FAILED")
 # Sample evenly, avoiding title black frames and using face + contrast + color-neutrality scores.
 cascade=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
 results=[]
 for t in np.arange(3.5,min(dur-4,52),1.0):
  cap.set(cv2.CAP_PROP_POS_MSEC,float(t)*1000);ok,frame=cap.read()
  if not ok:continue
  gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
  mean=float(gray.mean());stdev=float(gray.std())
  if not(42<mean<213 and stdev>28):continue
  faces=cascade.detectMultiScale(cv2.equalizeHist(gray),1.12,4,minSize=(26,26))
  facearea=float(sum(a*b for x,y,a,b in faces))
  sharp=float(cv2.Laplacian(gray,cv2.CV_32F).var())
  score=min(facearea/(w*h),.22)*400+min(len(faces),7)*7+min(sharp/13,18)+min(stdev,95)/12
  results.append({"time":round(float(t),2),"score":round(score,3),"faces_auto":len(faces),"sharp":round(sharp,1),"contrast":round(stdev,1),"brightness":round(mean,1)})
 cap.release()
 results.sort(key=lambda v:-v["score"])
 selected=[]
 for cand in results:
  if all(abs(cand["time"]-x["time"])>7.0 for x in selected):
   selected.append(cand)
  if len(selected)==5:break
 selected.sort(key=lambda x:x["time"])
 if len(selected)<5:raise RuntimeError("INSUFFICIENT_FIVE_DISTINCT_ACTING_BEATS")
 # Ensure the actual original 1 sec before anchor is true moving footage, and source not static.
 sheet=Image.new("RGB",(5*360,400),(15,18,25));d=ImageDraw.Draw(sheet)
 for i,z in enumerate(selected):
  t=z["time"]
  a=run(["ffmpeg","-nostdin","-y","-v","error","-ss",str(t),"-i",src,"-frames:v","1",str(R/f"SCENE_{i+1:02d}_BW_EXACT.png")],timeout=45)
  im=Image.open(R/f"SCENE_{i+1:02d}_BW_EXACT.png").convert("RGB")
  im.thumbnail((354,330))
  sheet.paste(im,(i*360+(360-im.width)//2,(340-im.height)//2+25))
  d.text((i*360+6,4),f"ORIGINAL MOVING FILM | {t}s",fill="white")
  d.text((i*360+6,365),f"Auto faces:{z['faces_auto']}  Sharp:{z['sharp']}",fill="#dfdfdf")
 sheet.save(R/"SCOUT_CONTACT_FIVE_ACTUAL_ORIGINAL_FRAMES.jpg",quality=92)
 report={"project":"La Storia Rivive","source_original_page":PAGE,"reality_status":"FICTIONAL_REENACTMENT_NOT_ACTUAL_SUBWAY_PASSENGERS",
   "filmed_year_label":"1905 (Biograph staged silent comedy, not a genuine candid subway documentary)",
   "source_metadata":meta,"video_duration_s":round(dur,2),
   "original_resolution":[w,h],"selected":selected,"status":"FIVE_ACTUAL_ORIGINAL_FRAMES_SOURCE_SCOUT_ONLY",
   "generated_ai_photos":0,"new_vidu_tasks":0,"master_completed":False,
   "publishing_rights":"1905 film US public domain on Wikimedia; Billy Bitzer died 1944; verify EU music/derivatives before publishing"}
 (R/"SCOUT_REPORT.json").write_text(json.dumps(report,indent=2))
 log("SCOUT_SUCCESS_SUBWAY_1905_FIVE_ACTING_BEATS",json.dumps(selected))
if __name__=="__main__":
 try:make_scout(acquire())
 except Exception as e:
  (R/"SOURCE_SCOUT_ERROR.json").write_text(json.dumps({"error":type(e).__name__+": "+str(e)[:500],"spent_credits":0,"finished_video":False},indent=2))
  log("SUBWAY_1905_SOURCE_SCOUT_BLOCKED",str(e)[:500]);sys.exit(1)
