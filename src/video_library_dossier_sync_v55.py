#!/usr/bin/env python3
"""Sync original ArtVision V55 textual dossiers to the PRIVATE site, never MP4s.

The worker accepts GitHub Actions OIDC from video-library-enrich.yml.
Never overwrites owner-curated documents, changes approval, or publishes socials.
"""
import argparse
import hashlib
import json
import os
import re
import time
from pathlib import Path

SCHEMA="artvision-v55-archive-staging-v1"
ENDPOINT="https://video-library-import.600led.workers.dev"
AUDIENCE="vls-gh-import-2026"
PLATFORMS=("facebook","instagram","tiktok","youtube")
FILES=("POST_FACEBOOK.txt","POST_INSTAGRAM.txt","POST_TIKTOK.txt",
       "POST_YOUTUBE.txt","SOURCES_AND_RIGHTS.md",
       "VIDEO_RECIPE_V13.json","DELIVERY_MANIFEST_V55.json")

def digest(data):
    return hashlib.sha256(data).hexdigest()

def prepare(manifest):
    if not isinstance(manifest,dict) or manifest.get("schema")!=SCHEMA:
        raise ValueError("Invalid staging schema")
    video=manifest.get("video_key")
    if not isinstance(video,str) or not re.fullmatch(r"[\w ().-]{1,190}\.mp4",video,re.I) or ".." in video:
        raise ValueError("Unsafe MP4 key")
    expected=manifest.get("video_sha256")
    if not isinstance(expected,str) or not re.fullmatch(r"[a-f0-9]{64}",expected):
        raise ValueError("Exact MP4 SHA256 required")
    size=manifest.get("video_bytes")
    if type(size)!=int or size<100000:
        raise ValueError("Actual MP4 byte count required")
    state=manifest.get("review_state")
    if state not in ("rendered_needs_review","approved_for_final_delivery"):
        raise ValueError("Review status unknown")
    posts=manifest.get("posts")
    if not isinstance(posts,dict) or set(posts)!=set(PLATFORMS):
        raise ValueError("Exactly four posts required")
    seen=set()
    for platform,body in posts.items():
        if not isinstance(body,str) or len(body.strip())<100:
            raise ValueError("Post missing: "+platform)
        normalized=" ".join(body.casefold().split())
        if normalized in seen:
            raise ValueError("Duplicate post")
        seen.add(normalized)
    rights=manifest.get("rights_markdown")
    if not isinstance(rights,str) or len(rights.strip())<150:
        raise ValueError("Rights attribution incomplete")
    recipe=manifest.get("recipe")
    if not isinstance(recipe,dict) or recipe.get("video",{}).get("sha256")!=expected or recipe.get("review_state")!=state:
        raise ValueError("Recipe missing, wrong video hash or wrong review status")
    docs={"POST_"+k.upper()+".txt":v.strip().encode("utf8")+b"\n" for k,v in posts.items()}
    docs["SOURCES_AND_RIGHTS.md"]=rights.strip().encode("utf8")+b"\n"
    docs["VIDEO_RECIPE_V13.json"]=(json.dumps(recipe,ensure_ascii=False,indent=2)+"\n").encode("utf8")
    audit={"schema":SCHEMA,"video_key":video,"local_reference_sha256":expected,
           "review_state":state,"site_cover_verified":False,"site_zip_verified":False,
           "V25_approval":"not_granted_by_this_sync",
           "note":"Private archival attachment sync only; not release approval or social publication"}
    docs["DELIVERY_MANIFEST_V55.json"]=(json.dumps(audit,indent=2)+"\n").encode("utf8")
    if set(docs)!=set(FILES) or any(not 1<len(b)<=250000 for b in docs.values()):
        raise ValueError("Attachment invalid or over 250 KB")
    return video,size,docs

def remote_video_state(remote, expected_bytes):
    """Never attach a dossier to a missing/deleted or wrong-size private MP4."""
    if remote.get("deleted") or not remote.get("exists"):
        return "archive_sync_pending"
    if remote.get("size") != expected_bytes:
        return "size_conflict"
    return "present_size_matched_hash_unverified"

def run(paths,dry_run):
    prepared=[(*prepare(json.loads(p.read_text(encoding="utf8"))),str(p)) for p in paths]
    if len({r[0] for r in prepared})!=len(prepared):
        raise ValueError("Duplicate video keys")
    if dry_run:
        for video,size,docs,origin in prepared:
            print(json.dumps({"status":"DRY_RUN_NO_UPLOAD","video":video,"source":origin,
                              "video_bytes":size,"docs":{k:digest(v) for k,v in docs.items()}},ensure_ascii=False))
        return
    if os.environ.get("GITHUB_REPOSITORY")!="GGIANLUCAA/Tra-le-pagine-":
        raise RuntimeError("Only the authorized GitHub repository can run upload")
    if not os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL") or not os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN"):
        raise RuntimeError("GitHub OIDC not available; no manual token fallback")
    import requests
    s=requests.Session()
    token_cache=("",0)
    def token():
        nonlocal token_cache
        if token_cache[0] and time.time()-token_cache[1]<150:
            return token_cache[0]
        r=s.get(os.environ["ACTIONS_ID_TOKEN_REQUEST_URL"],
                headers={"Authorization":"Bearer "+os.environ["ACTIONS_ID_TOKEN_REQUEST_TOKEN"]},
                params={"audience":AUDIENCE},timeout=20)
        r.raise_for_status()
        token_cache=(r.json()["value"],time.time())
        return token_cache[0]
    def api(method,route,params,body=None):
        r=s.request(method,ENDPOINT+route,params=params,
                    headers={"Authorization":"Bearer "+token()},data=body,timeout=45)
        if r.status_code==409:
            raise RuntimeError("Private archive conflict "+route+": "+r.text[:220])
        r.raise_for_status()
        return r.json()
    for video,size,docs,origin in prepared:
        remote=api("GET","/status",{"key":video})
        remote_state=remote_video_state(remote,size)
        if remote_state=="archive_sync_pending":
            print(json.dumps({"video":video,"status":"ARCHIVE_SYNC_PENDING_VIDEO_NOT_IMPORTED",
                              "video_sha256":"local_reference_only",
                              "note":"No private MP4 yet; no text upload, approval or publication"},ensure_ascii=False))
            continue
        if remote_state=="size_conflict":
            raise RuntimeError("MP4 SIZE CONFLICT in private archive: "+video+" "+repr(remote))
        newly_stored=0
        existing_unverified=0
        for name,data in docs.items():
            params={"video":video,"name":name}
            previous=api("GET","/production-file-status",params)
            if previous.get("exists"):
                existing_unverified+=1
                print(json.dumps({"video":video,"file":name,"result":"EXISTING_UNTOUCHED_HASH_UNVERIFIED"}))
                continue
            value=api("POST","/production-file",{**params,"sha256":digest(data)},body=data)
            check=api("GET","/production-file-status",params)
            if not value.get("ok") or not check.get("exists") or check.get("size")!=len(data):
                raise RuntimeError("Private attachment write not verified: "+video+"/"+name)
            newly_stored+=1
            print(json.dumps({"video":video,"file":name,"result":"PRIVATE_STORED","sha256":digest(data)}))
        print(json.dumps({"video":video,"new_text_files":newly_stored,
                          "existing_text_files_hash_unverified":existing_unverified,
                          "status":"TEXT_ATTACHMENTS_PRESENT_HASH_UNVERIFIED_COVER_ZIP_UNVERIFIED",
                          "video_remote_sha256":"not_available",
                          "artistic_approval":False,"social_publication":False}))

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("manifests",type=Path,nargs="+")
    p.add_argument("--dry-run",action="store_true")
    args=p.parse_args()
    run(args.manifests,args.dry_run)
