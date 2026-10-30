#!/usr/bin/env python3
"""V101: scheduled research preflight. No paid API calls or publication."""
from __future__ import annotations
import argparse, datetime as dt, json, re
from pathlib import Path
from urllib.parse import urlparse

def slot_at(value):
    t=dt.datetime.fromisoformat(value.replace("Z","+00:00"))
    if t.tzinfo is None: raise ValueError("timezone required")
    t=t.astimezone(dt.timezone.utc)
    return t.replace(hour=(t.hour//3)*3,minute=0,second=0,microsecond=0)

def candidate_issues(c):
    issues=[]
    u=urlparse(c.get("source_page",""))
    if u.scheme!="https" or u.netloc not in ("commons.wikimedia.org","www.loc.gov","loc.gov"):
        issues.append("SOURCE_PAGE_NOT_ALLOWLISTED")
    if c.get("license") not in ("CC0_as_declared","CC0","PUBLIC_DOMAIN","PDM"):
        issues.append("SOURCE_LICENSE_NEEDS_REVIEW")
    if c.get("rights_italy_verified") is not True:
        issues.append("ITALY_AND_RESIDUAL_RIGHTS_NEED_REVIEW")
    if c.get("historical_attribution_verified") is not True:
        issues.append("HISTORICAL_PLACE_DATE_NEED_REVIEW")
    if c.get("original_film_sha256_verified") is not True:
        issues.append("SOURCE_VIDEO_SHA_NOT_VERIFIED")
    if c.get("source_native_visual_review") is not True:
        issues.append("NATIVE_VIDEO_FACE_AND_CROP_REVIEW_PENDING")
    return issues

def build_work_order(bank,now,profile):
    slot=slot_at(now)
    entries=bank.get("candidates",[])
    if not isinstance(entries,list) or not entries: raise ValueError("No candidates")
    if profile.get("format")!="storia_rivive" or profile.get("schedule_hours")!=3: raise ValueError("Unsafe schedule")
    if profile.get("paid_calls_allowed") is not False or profile.get("social_autopublish") is not False:
        raise ValueError("Unsafe permissions")
    ids=[c.get("id") for c in entries]
    if any(not isinstance(i,str) or not re.fullmatch("[a-z0-9_]{6,64}",i) for i in ids):
        raise ValueError("Invalid candidates")
    if len(set(ids))!=len(ids): raise ValueError("Duplicate candidate")
    c=entries[(int(slot.timestamp())//10800)%len(entries)]
    issues=candidate_issues(c)
    flag=profile.get("historical_flags",{}).get(c["id"])
    title={"place":None,"year":c.get("year"),"flag":None,"flag_status":"OMITTED_UNTIL_VERIFIED"}
    if isinstance(flag,dict) and flag.get("historical_reviewed") is True and flag.get("supported_by_renderer") is True:
        title.update({"flag":flag["country_code"],"place":flag["place_label"],"flag_status":"PREVIEW_ONLY_UNTIL_HISTORICAL_SOURCE_REVIEW"})
    return {"contract":"LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT",
      "cycle_utc":slot.isoformat(),"cycle_id":"storia-"+slot.strftime("%Y%m%d-%H%M"),
      "episode_id":c["id"],"subject":c.get("title"),"source_page":c.get("source_page"),
      "source_license_claim":c.get("license"),"title":title,
      "requested_scenes":{"classic_real_i2i_photos":4,"source_locked_vidu":1},
      "future_vidu_max_after_gate_update":2,"duration_range_seconds":[14,35],
      "photo_status":"PENDING_REAL_I2I","vidu_status":"PENDING_SOURCE_LOCKED_ACTUAL_MP4",
      "paid_api_call_permitted":False,"credits_spent":0,"publish_permitted":False,
      "golden_reference":"SF1906 V98 SHA256 b20726893e067bbae493859ae1c51379c4abab8c2c8768d5c6f2d4ab324b47a8",
      "required_quality_gates":["V91","V94","V96","V99"],"blocking_issues":issues,
      "status":"SOURCE_PREFLIGHT_REVIEW_REQUIRED" if issues else "READY_FOR_ASSET_ACQUISITION_NOT_RENDER",
      "video_completed":False,"human_approved":False,
      "note":"Repeated queue item is a research candidate, never automatically a distinct finished episode."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--bank",default="queue/storia_rivive_candidates_v58.json")
    p.add_argument("--profile",default="config/storia_rivive_autopilot_v101.json")
    p.add_argument("--now",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    data=build_work_order(json.loads(Path(a.bank).read_text(encoding="utf-8")),a.now,
                          json.loads(Path(a.profile).read_text(encoding="utf-8")))
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"cycle":data["cycle_id"],"candidate":data["episode_id"],
                      "status":data["status"],"paid_calls":0,"publication":False}))
if __name__=="__main__":main()
