#!/usr/bin/env python3
"""V175: real Library of Congress per-item media discovery for quality-first sources.

Only the LOC official JSON API, exact per-item records and media host allowlist.
Does not download media, create videos, buy credits, or infer Italian rights.
Listings of ProRes/MOV never count as verified native-HD raster: only byte FFprobe
on an actual downloaded file can confirm a raster, plus human QA for detail.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

UA = "LaStoriaRiviveSourceResearch/1.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-)"
API_ORIGIN = "https://www.loc.gov"
# Fiction actors have closer faces/temporal texture; 00694408 is the existing
# V98 golden reference, included only as known-good control, NEVER a new subject.
ITEMS = {
    "2012600307": {"expected":"A corner in wheat", "year":1909, "role":"candidate"},
    "00694365": {"expected":"Sky scrapers of New York City", "year":1903, "role":"negative_control_panoramic"},
    "00694408": {"expected":"A trip down Market Street", "year":1906, "role":"existing_V98_do_not_reproduce"},
}
MAX_ITEM_RESPONSE = 6_000_000
ACCEPTED_LOC_HOSTS = (
    "www.loc.gov",
    "loc.gov",
    "tile.loc.gov",
    "cdn.loc.gov",
    "media.loc.gov",
    "stream-media.loc.gov",
    "download.loc.gov",
    "hdl.loc.gov",
)
MEDIA_SUFFIXES = (".mov",".mp4",".m4v",".webm",".ogv",".mxf",".mpg",".mpeg")
DATE_RE = re.compile(r"(18\d\d|19[0-3]\d)")


def safe_item_id(value: str) -> str:
    if not isinstance(value,str) or not re.fullmatch(r"[0-9]{8,12}", value):
        raise ValueError("UNSAFE_LOC_ITEM_ID")
    return value


def is_loc_url(value: object) -> bool:
    if not isinstance(value,str):return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and parsed.hostname in ACCEPTED_LOC_HOSTS and not parsed.username and not parsed.password and parsed.port in (None,443)


def is_media_url(value: object) -> bool:
    if not is_loc_url(value):return False
    parsed=urlparse(value)
    return parsed.path.lower().endswith(MEDIA_SUFFIXES)


def get_json(item_id: str) -> dict:
    safe_item_id(item_id)
    link = API_ORIGIN + "/item/" + item_id + "/?fo=json"
    req=Request(link,headers={"User-Agent":UA,"Accept":"application/json"})
    with urlopen(req, timeout=45) as fh:
        if fh.status != 200:
            raise ValueError("LOC_HTTP_NOT_OK")
        payload=fh.read(MAX_ITEM_RESPONSE+1)
    if len(payload)>MAX_ITEM_RESPONSE:
        raise ValueError("LOC_RESPONSE_TOO_LARGE")
    data=json.loads(payload)
    if not isinstance(data,dict):
        raise ValueError("LOC_METADATA_NOT_OBJECT")
    return data


def collect_media_urls(value: object, max_items: int=12000) -> list[dict]:
    """Never follow arbitrary locations. Only collect https://LOC/*.mp4, *.mov, etc."""
    media = {}
    pending=[(value,"root")]
    visited=0
    while pending and visited<max_items:
        curr,path=pending.pop()
        visited+=1
        if isinstance(curr,dict):
            for key,val in list(curr.items())[:500]:
                pending.append((val,(path+"/"+str(key))[-180:]))
        elif isinstance(curr,list):
            for i,val in enumerate(curr[:2000]):
                pending.append((val,(path+"/"+str(i))[-180:]))
        elif isinstance(curr,str) and is_media_url(curr):
            media.setdefault(curr,{"url":curr,"json_path":path,
              "format_hint":"ProRes-or-MOV (not proven)" if urlparse(curr).path.lower().endswith(".mov") else "MP4-or-other (not proven)",
              "native_raster_verified":False,"actual_source_quality_approved":False})
    return list(media.values())[:120]


def inspect_one(item_id: str, info: dict) -> dict:
    result={
        "id":item_id,
        "url":"https://www.loc.gov/item/"+item_id+"/",
        "expected_subject":info["expected"],"historical_year_expected":info["year"],
        "role":info["role"],"italian_rights_verified":False,
        "film_original_or_high_res_verified":False,
        "source_eligible_for_final":False,
        "real_i2i_count":0,"real_vidu_count":0,"credits_spent":0,
    }
    try:
        doc=get_json(item_id)
        item=doc.get("item",{})
        if not isinstance(item,dict): item={}
        result["response_top_keys"]=sorted(doc.keys())[:40]
        result["record_title"]=str(item.get("title",doc.get("title","")))[:200]
        result["record_date"]=str(item.get("date",doc.get("date","")))[:140]
        result["rights_item_note"]=str(item.get("rights_and_access",item.get("rights","")))[:800]
        result["media_links"]=collect_media_urls(doc)
        result["media_downloads_found"]=len(result["media_links"])
        result["status"]="MEDIA_METADATA_FOUND_UNVERIFIED_NATIVE_AND_RIGHTS" if result["media_links"] else "LOC_ITEM_HAS_NO_DOWNLOADABLE_MEDIA_LINK_IN_JSON"
    except Exception as exc:
        result["status"]="LOC_API_ACCESS_OR_METADATA_BLOCKED"
        result["error_type"]=type(exc).__name__
        result["error_summary"]=str(exc)[:220]
    return result


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    records=[inspect_one(i,info) for i,info in ITEMS.items()]
    result={"version":"V175","research_scope":"LOC National Screening Room source quality",
       "records":records, "no_media_download":True, "italian_rights_review":"PENDING",
       "no_purchased_or_consumed_credits":True, "no_video_master_created":True,
       "benchmark_43055_43056_preserved":True, "social_publish":False}
    (args.out/"V175_LOC_SOURCE_METADATA.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"candidate_records":[{"id":x["id"],"status":x["status"],
      "media_links":x.get("media_downloads_found",0),"role":x["role"]} for x in records],
      "paid_calls":0,"final_video":False}))


if __name__=="__main__":main()
