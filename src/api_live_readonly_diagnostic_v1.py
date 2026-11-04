#!/usr/bin/env python3
"""One-shot live READ-ONLY endpoint audit, zero generative requests or paid calls.

Runs only on trusted GitHub Actions main push/explicit manual launch. Never
logs keys, account balances, identities or raw provider responses. Checks
reachability/auth only, not inference/video, license or free account balance.
"""
from __future__ import annotations

import concurrent.futures
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import public_archive_sources_v2 as archives
import rare_research_sources_v3 as rare

ARCHIVE_PROBES={
    "met":"Socrates","artic":"Seurat","cleveland":"landscape",
    "loc":"Market Street 1906","archive":"historic film","commons":"Venice 1896",
    "vam":"Turner","smk":"Eckersberg","wellcome":"Victorian portrait",
    "nasa":"Apollo 11","gallica":"Paris 1900",
}
RARE_PROBES={
    "rijks":"Night Watch","finna":"Hugo Simberg",
    "getty_museum":"c88b3df0-de91-4f5b-a9ef-7b2b9a6d8abb",
    "getty_provenance":"09539ab1-416d-3870-810b-8a6b3b604368",
    "wikidata":"Rembrandt","openverse_audio":"train station",
    "librivox":"author:Verne","openlibrary":"The Lady of Shalott",
    "gutendex":"Verne","crossref":"Rembrandt art history",
}
PRIVATE_NAMES=("groq","nvidia_catalog","gemini_models","hugging_face",
               "openrouter","pixabay","ai_horde","vidu_balance")

def _http_status(exc):
    # Source adapters sanitize most errors to "HTTP NNN".
    if isinstance(exc,urllib.error.HTTPError):
        return exc.code
    m=re.search(r"HTTP[\s_]+([1-5]\d\d)",str(exc))
    return int(m.group(1)) if m else None

def _error_status(exc):
    code=_http_status(exc)
    if code in (401,403):
        return "AUTH_OR_FORBIDDEN"
    if code==429:
        return "RATE_LIMITED"
    if code==404:
        return "NOT_FOUND_OR_INCOMPATIBLE"
    if code is not None:
        return "HTTP_ERROR_"+str(code)
    return "NETWORK_OR_PARSE_ERROR"

def public_probe(item):
    family,provider,query=item
    try:
        data=(archives if family=="archive" else rare).search(provider,query,1)
        if not isinstance(data,dict) or not isinstance(data.get("items"),list) or data.get("api_requests",0)<1:
            return {"status":"INVALID_RESPONSE"}
        return {"status":"PASS","candidates":len(data["items"]),
                "note":"endpoint responded, no media or rights clearance"}
    except Exception as exc:
        return {"status":_error_status(exc)}

def _get_json(url,headers,timeout=12):
    req=urllib.request.Request(url,headers=headers,method="GET")
    with urllib.request.urlopen(req,timeout=timeout) as response:
        raw=response.read(700_001)
        if len(raw)>700_000:
            raise ValueError("Response exceeds cap")
    obj=json.loads(raw)
    if not isinstance(obj,dict):
        raise ValueError("JSON object required")
    return obj

def _env(name):
    key=os.environ.get("PROBE_"+name,"")
    if not key or any(ch.isspace() for ch in key):
        return None
    return key

def private_probe(name):
    envname={
        "groq":"GROQ","nvidia_catalog":"NVIDIA",
        "gemini_models":"GEMINI","hugging_face":"HF",
        "openrouter":"OPENROUTER","pixabay":"PIXABAY",
        "ai_horde":"AIHORDE","vidu_balance":"VIDU",
    }[name]
    key=_env(envname)
    if not key:
        return {"status":"NO_KEY_IN_GITHUB_ACTIONS"}
    bearer={"Authorization":"Bearer "+key,"Accept":"application/json",
            "User-Agent":"TraLePagine-ReadOnlyAudit/1.0"}
    try:
        if name=="groq":
            obj=_get_json("https://api.groq.com/openai/v1/models",bearer)
            ok=isinstance(obj.get("data"),list)
        elif name=="nvidia_catalog":
            # NVIDIA documents POST /v1/chat/completions; model list is not
            # guaranteed: a 404 here means 'unverifiable', not bad credentials.
            obj=_get_json("https://integrate.api.nvidia.com/v1/models",bearer)
            ok=isinstance(obj.get("data"),list)
        elif name=="gemini_models":
            obj=_get_json("https://generativelanguage.googleapis.com/v1beta/models",{
                "x-goog-api-key":key,"Accept":"application/json",
                "User-Agent":"TraLePagine-ReadOnlyAudit/1.0"})
            ok=isinstance(obj.get("models"),list)
        elif name=="hugging_face":
            obj=_get_json("https://huggingface.co/api/whoami-v2",bearer)
            ok=bool(obj.get("name") or obj.get("type") or obj.get("id"))
        elif name=="openrouter":
            obj=_get_json("https://openrouter.ai/api/v1/key",bearer)
            ok=isinstance(obj.get("data"),dict)
        elif name=="pixabay":
            params=urllib.parse.urlencode({"key":key,"q":"historic city","per_page":3,"image_type":"photo"})
            obj=_get_json("https://pixabay.com/api/?"+params,{
                "Accept":"application/json","User-Agent":"TraLePagine-ReadOnlyAudit/1.0"})
            ok=isinstance(obj.get("hits"),list)
        elif name=="ai_horde":
            obj=_get_json("https://aihorde.net/api/v2/find_user",{
                "apikey":key,"Accept":"application/json",
                "User-Agent":"TraLePagine-ReadOnlyAudit/1.0"})
            ok=bool(obj.get("id") or obj.get("username"))
        elif name=="vidu_balance":
            obj=_get_json("https://api.vidu.com/ent/v2/credits?show_detail=true",{
                "Authorization":"Token "+key,"Accept":"application/json",
                "User-Agent":"TraLePagine-ReadOnlyAudit/1.0"})
            ok=isinstance(obj.get("remains") or obj.get("remaining_credits"),list)
        else:
            return {"status":"UNSUPPORTED"}
        return {"status":"PASS" if ok else "INVALID_RESPONSE",
                "note":"read-only authentication/metadata; no generative inference"}
    except Exception as exc:
        code=_http_status(exc)
        if name=="nvidia_catalog" and code in (404,405):
            return {"status":"ENDPOINT_NOT_DOCUMENTED",
                    "note":"NVIDIA key presence known; cannot assert inference works"}
        return {"status":_error_status(exc)}

def main():
    items=([("archive",n,q) for n,q in ARCHIVE_PROBES.items()]+
           [("rare",n,q) for n,q in RARE_PROBES.items()])
    report={"schema":"api-read-only-live-test-v1",
            "date_utc":datetime.now(timezone.utc).isoformat(),
            "test_type":"LIVE_GET_ONLY_PUBLIC_SEARCH_AND_CREDENTIAL_METADATA",
            "zero_generations":True,"zero_paid_inference":True,
            "media_downloaded":False,"credentials_disclosed":False,
            "public":{},"credentials":{}}
    tasks=[("public",i[1],i) for i in items]+[("private",name,name) for name in PRIVATE_NAMES]
    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as pool:
        futures={pool.submit(public_probe,t[2]) if t[0]=="public"
                 else pool.submit(private_probe,t[2]):(t[0],t[1]) for t in tasks}
        for future in concurrent.futures.as_completed(futures):
            kind,name=futures[future]
            try: result=future.result()
            except Exception: result={"status":"INTERNAL_CHECK_ERROR"}
            report["public" if kind=="public" else "credentials"][name]=result
    for group in ("public","credentials"):
        for name,result in sorted(report[group].items()):
            print(group.upper(),name,result["status"],
                  "candidates="+str(result["candidates"]) if "candidates" in result else "")
    report["summary"]={
        group:{state:sum(x["status"]==state for x in report[group].values())
               for state in sorted(set(x["status"] for x in report[group].values()))}
        for group in ("public","credentials")
    }
    out=Path(os.environ.get("API_LIVE_REPORT","output/api_live_check_v1/RESULTS.json"))
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("NO_CHARGED_INFERENCE_NO_VIDEO_GENERATION_KEYS_NOT_LOGGED")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
