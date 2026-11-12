#!/usr/bin/env python3
"""Reuse source-verified Commons bytes from earlier Actions. No Wikimedia GET.

Source run 43296332537 downloaded 34 photographs and authentic OGV aerial
footage with original byte hashes. Four photos lack author metadata; reject.
Never publish or claim a final MP4 here.
"""
import hashlib,json,shutil
from pathlib import Path
SOURCE=Path("input-nazca")
OUT=Path("output/giuliano-nazca-licensed")
OUT.mkdir(parents=True,exist_ok=True)
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""):h.update(b)
 return h.hexdigest()
def main():
 old=json.loads((SOURCE/"SOURCE_SCOUT.json").read_text())
 assert old["schema"]=="nazca-source-scout-v1"
 assert len(old["photos"])>=30 and old["real_video"] is not None
 seen=set(); keep=[]; rejects=[]
 for item in old["photos"]:
  path=SOURCE/item["filename"]
  assert path.is_file() and path.stat().st_size==item["bytes"]
  assert sha(path)==item["sha256"],"photo bytes mismatch"
  if not item.get("author") or not item.get("license_url") or not item.get("license"):
   rejects.append({"title":item["title"],"reason":"missing_attribution"});continue
  assert "commons.wikimedia.org/wiki/File:" in item["page"]
  assert "creativecommons.org" in item["license_url"] or "publicdomain" in item["license_url"].lower()
  assert item["source_url"] and item["title"] not in seen
  seen.add(item["title"]);keep.append(item)
  shutil.copy2(path,OUT/item["filename"])
 assert len(keep)>=26, len(keep)
 mov=old["real_video"]
 assert mov["filename"]=="NAZCA_REAL_AERIAL_SOURCE.ogv"
 assert mov["author"] and mov["license"] and mov["license_url"]
 assert mov["duration_s"]>=40 and mov["duration_s"]<=50
 p=SOURCE/mov["filename"]
 assert p.is_file() and p.stat().st_size==mov["bytes"] and sha(p)==mov["sha256"]
 shutil.copy2(p,OUT/mov["filename"])
 shutil.copy2(SOURCE/"CONTACT_SHEET.jpg",OUT/"CONTACT_SHEET_ORIGINAL_ALL_SOURCES.jpg")
 x={"schema":"nazca-curated-existing-media-v1","status":"REAL_MEDIA_SHA_LICENSE_PASS",
   "original_action_run":43296332537,"original_artifact":"GIULIANO_NAZCA_REAL_MEDIA_SCOUT_43296332537",
   "photos":keep,"real_video":mov,"excluded_uncredited":rejects,
   "image_count":len(keep),"source_media_created_with_ai":False,
   "review_required_before_social_publication":True,
   "rights_note":"Various CC BY and CC BY-SA terms; attribution and derivative licensing must be respected in credits/social; not public domain claim",
   "synthetic_video_calls":0,"voice_calls":0}
 (OUT/"SOURCE_CURATED.json").write_text(json.dumps(x,indent=2,ensure_ascii=False)+"\n")
 (OUT/"AUTHORS_CREDITS.txt").write_text(
  "GIULIANO 04 NAZCA | SOURCES - owner review only\n"
  "Wikimedia Commons original photos, resized to fit frame; no AI-redrawn glyphs.\n"
  "Each source URL, author, license, and original SHA256 in SOURCE_CURATED.json.\n"+
  "\n".join(f"{p['title']} | {p['author']} | {p['license']} | {p['license_url']} | {p['page']}" for p in keep)+
  f"\nAERIAL FOOTAGE | {mov['title']} | {mov['author']} | {mov['license']} | {mov['license_url']} | {mov['page']}\n",
  encoding="utf-8")
 print("NAZCA_CURATED_REAL_PHOTOS",len(keep),"REJECTED_NO_AUTHOR",len(rejects),flush=True)
 print("NAZCA_REAL_AERIAL_VIDEO_REUSED_SHA",mov["sha256"],mov["duration_s"],flush=True)
if __name__=="__main__":main()
