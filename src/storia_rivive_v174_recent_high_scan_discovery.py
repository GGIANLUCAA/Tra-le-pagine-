#!/usr/bin/env python3
"""V174 free archival search for post-2023 high-definition *candidates*.

Searches ONLY Internet Archive official metadata for recent Prelinger uploads
with original historical dates and explicitly public-domain-marked item rights.
Important: upload year is NOT film year, bitrate NOT source native resolution,
and a US PD label is NOT automatically Italian film-publication clearance.
No video download or generated AI. No paid API. No social publication.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen, Request

USER_AGENT = "LaStoriaRiviveResearch/1.0 (GH GGIANLUCAA/Tra-le-pagine-)"
SEARCH_ENDPOINT = "https://archive.org/advancedsearch.php"
API_METADATA_PREFIX = "https://archive.org/metadata/"
ALLOWED_IDENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_\-.]{1,99}$")
START_UPLOADED = "2023-01-01T00:00:00Z"
MAX_SEARCH_ROWS = 80
MAX_ITEM_FETCHES = 24
SOURCE_YEAR_MIN = 1895
SOURCE_YEAR_MAX = 1935
QUERY_VARIANTS = (
    # A query whose metadata may include the year but not the date.
    "collection:prelinger AND mediatype:movies AND year:[1895 TO 1935] AND publicdate:[2023-01-01T00:00:00Z TO *]",
    # Alternative often needed for ephemeral films with date only.
    "collection:prelinger AND mediatype:movies AND date:[1895 TO 1935] AND publicdate:[2023-01-01T00:00:00Z TO *]",
)


def parse_historical_year(metadata: dict) -> int | None:
    candidates = [metadata.get("year", ""), metadata.get("date", "")]
    # Never derive the film's historic year from the archive upload timestamp.
    for value in candidates:
        match = re.search(r"(?<!\d)(18\d{2}|19[0-3]\d)(?!\d)", str(value))
        if match:
            year = int(match.group(0))
            if SOURCE_YEAR_MIN <= year <= SOURCE_YEAR_MAX:
                return year
    return None


def public_domain_exact(metadata: dict) -> bool:
    label = str(metadata.get("licenseurl", "")).strip().lower()
    return label in {
        "http://creativecommons.org/licenses/publicdomain/",
        "https://creativecommons.org/licenses/publicdomain/",
        "https://creativecommons.org/publicdomain/mark/1.0/",
        "http://creativecommons.org/publicdomain/mark/1.0/",
        "https://creativecommons.org/publicdomain/zero/1.0/",
        "http://creativecommons.org/publicdomain/zero/1.0/",
    }


def safe_id(value: object) -> str:
    if not isinstance(value, str) or not ALLOWED_IDENT.fullmatch(value):
        raise ValueError("UNSAFE_ARCHIVE_IDENTIFIER")
    return value


def metadata_get(url: str) -> dict:
    # Hosts are constructed by this module, not read from remote results.
    with urlopen(Request(url, headers={"User-Agent": USER_AGENT}), timeout=30) as response:
        data=json.load(response)
    if not isinstance(data, dict):
        raise ValueError("ARCHIVE_RETURNED_NON_OBJECT")
    return data


def search_ids() -> list[dict]:
    merged: dict[str, dict] = {}
    for query in QUERY_VARIANTS:
        params = urlencode({
            "q": query, "fl[]": "identifier,title,year,date,publicdate,licenseurl",
            "sort[]": "publicdate desc", "rows": str(MAX_SEARCH_ROWS),
            "page": "1", "output": "json",
        })
        data = metadata_get(SEARCH_ENDPOINT+"?"+params)
        docs = data.get("response",{}).get("docs",[])
        if not isinstance(docs, list):
            raise ValueError("INVALID_ARCHIVE_SEARCH_DATA")
        for doc in docs:
            if not isinstance(doc, dict):
                continue
            try:
                identifier=safe_id(doc.get("identifier"))
            except ValueError:
                continue
            merged.setdefault(identifier, doc)
    return list(merged.values())[:MAX_SEARCH_ROWS]


def video_files(media: list[dict]) -> list[dict]:
    out = []
    for f in media:
        name=f.get("name")
        if not isinstance(name,str) or len(name)>180 or "/" in name or "\\" in name or ".." in name:
            continue
        if not name.lower().endswith((".mp4",".mov",".mpg",".mpeg",".ogv",".webm")):
            continue
        try:
            length=int(f.get("size",0))
        except (ValueError,TypeError):
            continue
        if length<1000000:
            continue
        out.append({
            "filename":name,
            "size_mib":round(length/(1024*1024),2),
            "source":str(f.get("source",""))[:30],
            "format":str(f.get("format",""))[:90],
        })
    out.sort(key=lambda x:x["size_mib"],reverse=True)
    return out[:8]


def discover() -> dict:
    report = {
        "version":"V174","origin":"Internet Archive Prelinger metadata",
        "official_research_archive":"https://archive.org/details/prelinger",
        "requires_independent_italian_rights_review":True,
        "native_resolution_verified_by_ffprobe":False,
        "paid_calls":0,"videos_downloaded":0,"image_generation_requests":0,
        "vidu_requests":0,"published":False,
        "candidates":[],
    }
    try:
        matches=search_ids()
        report["search_matching_identifiers"]=len(matches)
        report["search_preview"]=[{
            "identifier": str(d.get("identifier",""))[:100],
            "title": str(d.get("title",""))[:100],
            "date": str(d.get("date",""))[:40],
            "year": str(d.get("year",""))[:40],
            "publicdate": str(d.get("publicdate",""))[:40],
            "search_license_declared": str(d.get("licenseurl",""))[:180],
        } for d in matches[:25]]
        report["item_metadata_examined"]=0
        report["exclusion_counts"]={"no_film_year":0,"no_exact_public_domain_item_mark":0,"no_video_file":0}
        for doc in matches[:MAX_ITEM_FETCHES]:
            identifier = safe_id(doc["identifier"])
            try:
                data=metadata_get(API_METADATA_PREFIX+identifier)
                report["item_metadata_examined"]+=1
                metadata=data.get("metadata",{})
                if not isinstance(metadata,dict) or metadata.get("identifier") != identifier:
                    raise ValueError("ITEM_METADATA_ID_MISMATCH")
                year=parse_historical_year(metadata)
                if year is None:
                    report["exclusion_counts"]["no_film_year"]+=1
                    continue
                if not public_domain_exact(metadata):
                    report["exclusion_counts"]["no_exact_public_domain_item_mark"]+=1
                    continue
                files=video_files(data.get("files",[]))
                if not files:
                    report["exclusion_counts"]["no_video_file"]+=1
                    continue
                report["candidates"].append({
                    "identifier":identifier,
                    "title":str(metadata.get("title",""))[:160],
                    "year_filmed_from_item_metadata":year,
                    "upload_date_archive":str(doc.get("publicdate",""))[:60],
                    "license_url_declared":str(metadata.get("licenseurl","")),
                    "source_page":"https://archive.org/details/"+identifier,
                    "candidate_video_files":files,
                    "has_file_over_100mib":any(f["size_mib"]>100 for f in files),
                    "native_high_res_confirmed":False,
                    "reason_to_inspect":"Recent archive uploads may have newer scans, but verify actual pixel raster on bytes before any production.",
                })
            except Exception as exc:
                report.setdefault("failed_metadata_ids",[]).append({
                    "identifier":identifier,"error_type":type(exc).__name__})
        report["status"]="CANDIDATES_REQUIRE_NATIVE_VIDEO_FFPROBE_AND_ARTISTIC_REVIEW" if report["candidates"] else "NO_QUALIFIED_CANDIDATES_FROM_BOUNDED_SEARCH"
    except Exception as exc:
        report["status"]="RESEARCH_NETWORK_OR_SEARCH_BLOCKED_NO_PRODUCTION"
        report["error_type"]=type(exc).__name__
        report["error_summary"]=str(exc)[:240]
    return report


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    data=discover()
    (args.out/"V174_RECENT_PRELINGER_METADATA_CANDIDATES.json").write_text(
        json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":data["status"],
        "records_considered":data.get("search_matching_identifiers",0),
        "candidate_film_ids":[i["identifier"] for i in data["candidates"]],
        "native_hd_verified":False,"spent":0,"published":False,
    }))


if __name__=="__main__":main()
