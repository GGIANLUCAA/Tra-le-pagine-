#!/usr/bin/env python3
"""V72: inspect LOC primary source media, not a social rip. Conservative scout, no paid API."""
import json,urllib.request,urllib.parse,time,hashlib,os,subprocess
from pathlib import Path
O=Path("output/storia_v72_coney");O.mkdir(parents=True,exist_ok=True)
ITEM="https://www.loc.gov/item/00563608/"
def grab(url,timeout=45):
 req=urllib.request.Request(url,headers={"User-Agent":"Tra-le-Pagine-ArtVision/1.0 (research; public domain archival verification)","Accept":"application/json, */*"})
 with urllib.request.urlopen(req,timeout=timeout) as r:
  return r.read()
raw=None;err=[]
for u in [ITEM+"?fo=json",ITEM+"?fo=json&at=resources",ITEM+"?fo=json&at=item,resources"]:
 try:
  body=grab(u)
  obj=json.loads(body)
  if "resources" in obj or "item" in obj:
   raw=obj;print("LOC_JSON_OK",u,sorted(obj.keys())[:50],flush=True);break
 except Exception as e:
  err.append({"url":u,"error":str(e)[:280]})
if raw is None:
 (O/"SOURCE_DISCOVERY.json").write_text(json.dumps({"errors":err,"status":"API_BLOCKED"},indent=2))
 raise SystemExit("LOC_API_NOT_ACCESSIBLE; no invented file")
videos=[];unknown=[]
def walk(node,path="",depth=0):
 if depth>12:return
 if isinstance(node,dict):
  for k,v in node.items():
   if k in ("url","href","download","download_url","streaming_url") and isinstance(v,str):
    lo=v.lower().split("?")[0]
    if any(x in lo for x in [".mp4",".mov",".webm",".m4v",".m3u8",".avi",".ogv"]):
     videos.append({"url":v,"where":path+"."+k,"mimetype":node.get("mimetype"),"size":node.get("size"),"label":node.get("label")})
    elif "video" in str(node.get("mimetype","")).lower() or "prores" in str(node).lower()[:240]:
     unknown.append({"url":v,"where":path+"."+k,"meta":str(node)[:200]})
   walk(v,path+"."+k,depth+1)
 elif isinstance(node,list):
  for i,v in enumerate(node):walk(v,path+"["+str(i)+"]",depth+1)
walk(raw)
seen=set();videos=[v for v in videos if not (v["url"] in seen or seen.add(v["url"]))]
data={"source":ITEM,"title":"Shooting the Chutes, Luna Park, Coney Island","date":"1903-07-03","source_api_keys":sorted(raw.keys()),"video_sources":videos,"other_possible_sources":unknown[:15],"source_rights_note":"LOC general reuse notice US; territorial checks for Italy pending","previous_errors":err}
(O/"SOURCE_DISCOVERY.json").write_text(json.dumps(data,indent=2,ensure_ascii=False))
print("FOUND_VIDEO_URLS",len(videos),flush=True)
for v in videos:print("VIDEO",json.dumps(v),flush=True)
if not videos:raise SystemExit("No direct film URL in LOC JSON")
# Prefer actual HD/ProRes if available; avoid playlists and YouTube reuploads
ordered=sorted(videos,key=lambda x:(int(".mov" in x["url"].lower()),int(".mp4" in x["url"].lower()),int("prores" in str(x).lower())),reverse=True)
for ix,v in enumerate(ordered):
 if ".m3u8" in v["url"]:continue
 try:
  u=v["url"];print("TRY_MASTER",u[:200],flush=True)
  suffix=Path(urllib.parse.urlparse(u).path).suffix.lower() or ".mp4"
  if suffix not in [".mov",".mp4",".webm",".m4v",".avi",".ogv"]:suffix=".mp4"
  dest=O/("SOURCE_ORIGINAL"+suffix)
  req=urllib.request.Request(u,headers={"User-Agent":"Tra-le-Pagine-ArtVision/1.0"})
  with urllib.request.urlopen(req,timeout=80) as resp,open(dest,"wb") as f:
   while b:=resp.read(1<<20):
    f.write(b)
    if f.tell()>600_000_000:raise RuntimeError("Source >600 MB scout cap")
  if dest.stat().st_size<100000:raise RuntimeError("Short file")
  p=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration,size:stream=codec_name,width,height,r_frame_rate","-of","json",str(dest)],capture_output=True,text=True,timeout=25)
  if p.returncode:raise RuntimeError(p.stderr[-450:])
  probe=json.loads(p.stdout)
  (O/"ACQUIRED_SOURCE.json").write_text(json.dumps({"file":dest.name,"url":u,"sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),"probe":probe},indent=2))
  print("VIDEO_ACQUIRED",dest.name,dest.stat().st_size,json.dumps(probe),flush=True)
  break
 except Exception as e:
  print("MASTER_UNAVAILABLE",str(e)[:250],flush=True)
  if dest.exists():dest.unlink()
else:raise SystemExit("All master URLs failed")
