#!/usr/bin/env python3
"""Read-only site audit, comparing all twelve selected real ArtVision masters with public website.
No uploads/deletions, no tokens/secrets, no publication approvals.
"""
import concurrent.futures, csv, hashlib, json, os, pathlib, re, subprocess, sys, time, urllib.parse
import requests
ROOT="https://video-library-studio.600led.workers.dev"
QUEUE=pathlib.Path("queue/artvision_owner_selected_ten_20261102.json")
OUT=pathlib.Path("output/site_download_audit_v152")
OUT.mkdir(parents=True,exist_ok=True)
AGENT="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36 ArtVisionAuditV152"
PERIOD_S=50
selected=[
 ("bruegel_tower_babel_1563_khm_gg1026","cinema_standard_v136"),
 ("bruegel_tower_babel_1563_khm_gg1026","cinema_museum_v137"),
 ("bruegel_tower_babel_1563_khm_gg1026","critico_standard_v141"),
 ("bruegel_tower_babel_1563_khm_gg1026","critico_museum_v141"),
 ("bruegel_fall_rebel_angels_1562_rmfb_584","new_cinema_standard_v135"),
 ("bruegel_fall_rebel_angels_1562_rmfb_584","critico_standard_v144"),
 ("rembrandt_night_watch_1642_rijks_sk_c_5","new_cinema_standard_v132"),
 ("rembrandt_night_watch_1642_rijks_sk_c_5","critico_standard_v149"),
 ("simberg_garden_death_1896_fng_a_ii_968_16","v134_cinema_candidate"),
 ("simberg_garden_death_1896_fng_a_ii_968_16","critico_standard_v146"),
 ("bruegel_triumph_death_1562_prado_p001393","cinema_standard_v150"),
 ("bruegel_triumph_death_1562_prado_p001393","critico_standard_v151"),
]
# Previous V137 Cinema Museum lives as an exact reviewed MP4; the queue stores SHA
# and the workflow verified bytes, but not the filename/size as direct slot fields.
V137_NAME="BRUEGEL_THE_TOWER_OF_BABEL_CINEMA_MUSEUM_V137_REVIEW.mp4"
V137_BYTES=15646921
def expected():
 q=json.loads(QUEUE.read_text(encoding="utf8"))
 works={x["id"]:x for x in q["works"]}
 assert sum(x["slots_delivered_this_selection"] for x in q["works"])>=12
 result=[]
 for wid,slot in selected:
  x=works[wid][slot]
  filename=x.get("filename") or x.get("mp4_filename")
  if slot=="cinema_museum_v137":filename=V137_NAME
  size=x.get("bytes") or x.get("mp4_bytes")
  if slot=="cinema_museum_v137":size=V137_BYTES
  digest=x.get("sha256") or x.get("mp4_sha256")
  if not (filename and isinstance(size,int) and isinstance(digest,str) and re.fullmatch("[a-f0-9]{64}",digest)):
   raise RuntimeError(f"No exact verified video size and SHA in queue: {wid}/{slot}")
  assert re.fullmatch(r"[\w ().-]{1,190}\.mp4",filename)
  result.append({"work":works[wid]["title_en"],"slot":slot,"name":filename,"bytes":size,"sha256":digest})
 assert len(result)==12 and len({v["name"] for v in result})==12
 return result
def req(path,headers=None,stream=False,timeout=PERIOD_S):
 return requests.get(ROOT+path,headers={"User-Agent":AGENT,**(headers or {})},stream=stream,timeout=(12,timeout),allow_redirects=False)
def json_endpoint(path):
 r=req(path,timeout=75)
 r.raise_for_status()
 return r.json()
def check_range(n,size,route):
 url="/"+route+"/"+urllib.parse.quote(n,safe="")
 r=req(url,headers={"Range":"bytes=0-1023"},timeout=35)
 try:
  data=r.content
  expected=f"bytes 0-1023/{size}"
  h=r.headers
  result={"status":r.status_code,"bytes":len(data),
          "content_type":h.get("Content-Type"),
          "content_range":h.get("Content-Range"),
          "disposition":h.get("Content-Disposition")}
  result["pass"]=(r.status_code==206 and len(data)==1024 and h.get("Content-Range")==expected
                  and h.get("Content-Type","").lower().startswith("video/mp4")
                  and (route!="download" or "attachment" in h.get("Content-Disposition","").lower()))
  return result
 finally:r.close()
def full_download_check(n,size,sha):
 url="/download/"+urllib.parse.quote(n,safe="")
 r=req(url,stream=True,timeout=90)
 h=hashlib.sha256()
 downloaded=0
 try:
  if r.status_code!=200:
   return {"pass":False,"http_status":r.status_code,"error":"full download not 200", "total_bytes":0}
  for b in r.iter_content(1024*1024):
   if not b:continue
   downloaded+=len(b)
   if downloaded>size:
    return {"pass":False,"http_status":r.status_code,"error":"download exceeded expected byte count","total_bytes":downloaded}
   h.update(b)
  return {"pass":downloaded==size and h.hexdigest()==sha,
          "http_status":r.status_code,"total_bytes":downloaded,"sha256":h.hexdigest(),
          "matches_exact_master_sha256":h.hexdigest()==sha}
 finally:r.close()
def video(row,catalog,files):
 n=row["name"]
 output={**row,"in_site_catalog":n in catalog,"catalog_available":(catalog.get(n) or {}).get("available"),
         "in_site_files":n in files,"catalog_reported_size":(files.get(n) or {}).get("size")}
 if n not in files:
  output["result"]="MISSING_FROM_SITE_FILES"
  return output
 if (files[n].get("size") is not None and int(files[n]["size"])!=row["bytes"]):
  output["result"]="WRONG_SIZE_ON_SITE"
  return output
 try:
  output["stream_range"]=check_range(n,row["bytes"],"media")
  output["download_range"]=check_range(n,row["bytes"],"download")
  if not output["stream_range"]["pass"] or not output["download_range"]["pass"]:
   output["result"]="BROKEN_RANGE_OR_DOWNLOAD_RESPONSE"
   return output
  output["complete_download"]=full_download_check(n,row["bytes"],row["sha256"])
  output["result"]="VERIFIED_FULL_DOWNLOAD_SHA256" if output["complete_download"]["pass"] else "BROKEN_FULL_DOWNLOAD_OR_SHA"
 except Exception as e:
  output["result"]="AUDIT_ERROR"
  output["error"]=type(e).__name__+": "+str(e)[:300]
 return output

def main():
 rows=expected()
 info={"status":"AUDIT_STARTED","site":ROOT,"expected_count":len(rows),
       "github_run_id":os.environ.get("GITHUB_RUN_ID","unknown"),"user_agent":AGENT}
 (OUT/"expected.json").write_text(json.dumps(rows,indent=2,ensure_ascii=False))
 try:
  hp=req("/")
  info["homepage_http"]=hp.status_code
  info["homepage_has_title"]="Video Library Studio" in hp.text[:150000]
  rawcat=json_endpoint("/api/catalog")
  rawfiles=json_endpoint("/api/files")
  assert isinstance(rawcat.get("items"),list)
  assert isinstance(rawfiles,list)
  catalog={x.get("key",x.get("name")):x for x in rawcat["items"] if isinstance(x,dict)}
  files={x.get("name",x.get("key")):x for x in rawfiles if isinstance(x,dict)}
  info.update({"catalog_total":len(rawcat["items"]),"actual_files_total":len(rawfiles),
               "site_listed_mp4":sum(bool(n and str(n).lower().endswith(".mp4")) for n in files),
               "catalog_available":sum(x.get("available") is True for x in rawcat["items"] if isinstance(x,dict))})
  print("SITE_CATALOG",json.dumps(info),flush=True)
 except Exception as e:
  info["status"]="SITE_ROOT_OR_CATALOG_FAILURE"
  info["reason"]=type(e).__name__+": "+str(e)[:450]
  (OUT/"site_download_report_v152.json").write_text(json.dumps(info,indent=2))
  print("SITE_AUDIT_FAILED_TO_READ_CATALOG",info,flush=True)
  return
 # Full sha256 of all 12 expected files, max three concurrent HTTP downloads.
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  futures={pool.submit(video,row,catalog,files):row["name"] for row in rows}
  results=[]
  for future in concurrent.futures.as_completed(futures):
   row=future.result()
   print("MASTER",row["result"],row["name"],
         str(row.get("complete_download",{}).get("total_bytes","")),"bytes",flush=True)
   results.append(row)
 results.sort(key=lambda x:x["name"])
 info["expected_result"]={"total":len(results),
                         "verified":sum(x["result"]=="VERIFIED_FULL_DOWNLOAD_SHA256" for x in results),
                         "missing":sum(x["result"]=="MISSING_FROM_SITE_FILES" for x in results),
                         "broken":sum(x["result"] not in ("VERIFIED_FULL_DOWNLOAD_SHA256","MISSING_FROM_SITE_FILES") for x in results)}
 # Site-wide inexpensive Range check for every real *.mp4 served by the site (not ChatGPT-only catalog placeholders).
 candidates=[(n,v) for n,v in files.items() if isinstance(n,str) and re.fullmatch(r"[\w ().-]{1,190}\.mp4",n,re.I) and isinstance(v.get("size"),int) and v["size"]>=1024]
 def one_file(pair):
  n,metadata=pair
  try:
   val=check_range(n,metadata["size"],"download")
   return None if val["pass"] else {"name":n,"error":"DOWNLOAD_RANGE_FAIL","check":val}
  except Exception as exc:
   return {"name":n,"error":type(exc).__name__+": "+str(exc)[:170]}
 bad=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
  for item in pool.map(one_file,candidates):
   if item:bad.append(item)
 info["site_wide_range_check"]={"tested":len(candidates),"passed":len(candidates)-len(bad),"failed":len(bad),
                               "failures":bad[:140]}
 info["masters"]=results
 info["status"]="FULL_PASS" if info["expected_result"]["verified"]==12 and not bad else "INCOMPLETE_SITE_ARCHIVE_OR_DOWNLOADS"
 (OUT/"site_download_report_v152.json").write_text(json.dumps(info,indent=2,ensure_ascii=False))
 with (OUT/"site_master_status_v152.csv").open("w",newline="",encoding="utf8") as f:
  writer=csv.DictWriter(f,fieldnames=["work","slot","name","bytes","result","in_site_catalog","catalog_available","in_site_files"])
  writer.writeheader()
  for row in results:writer.writerow({k:row.get(k,"") for k in writer.fieldnames})
 print("FINAL",json.dumps({k:v for k,v in info.items() if k not in ("masters","site_wide_range_check")}),flush=True)
 print("SITE_WIDE",info["site_wide_range_check"],flush=True)
if __name__=="__main__":main()
