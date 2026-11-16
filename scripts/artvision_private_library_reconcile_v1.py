#!/usr/bin/env python3
"""PRIVATE ArtVision Library cross-check against public site; no upload or publishing.

Input: a user-held JSON snapshot of ChatGPT Library metadata exported by an
authorized user. This script cannot automatically access ChatGPT private Library.
It treats filenames and byte sizes as *hints*, not cryptographic identity proofs.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

VIDEO_EXTENSIONS={".mp4",".mov",".m4v"}

def normalized(text):
    s=unicodedata.normalize("NFKD",str(text or ""))
    s="".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+","_",s.lower()).strip("_")

def family_hint(name,path):
    stem=normalized(Path(str(name)).stem)
    # Only heuristic; no merge, deletion or automatic "video already exists".
    stem=re.sub(r"(?:_mobile|_android|_leggero|_light|_hq|_1080p|_720p|_720|_1080|_final|_review|_preview|_diretto)+$","",stem)
    stem=re.sub(r"(?:_v\d+[a-z]?\d*)+$","",stem)
    if stem in {"cinema_standard","cinema_museum","critico_standard","critico_museum","video_master","video"}:
        # Generic MP4 names are meaningful ONLY within their private folder.
        return normalized(str(Path(path).parent))+"__"+stem
    return stem

def load_json(p):
    raw=json.loads(Path(p).read_text(encoding="utf-8"))
    if not isinstance(raw,dict):raise ValueError("Expected JSON object")
    return raw

def secure_destination(out,project_root,manifest_path):
    path=Path(out).expanduser().resolve()
    root=Path(project_root).resolve()
    if path.is_relative_to(root):
        raise ValueError("Private report must be OUTSIDE the GitHub repository")
    if path==Path(manifest_path).resolve():
        raise ValueError("Cannot overwrite source manifest")
    return path

def get_entries(manifest):
    if not isinstance(manifest.get("entries"),list):
        raise ValueError("Manifest must supply entries[]")
    seen=set()
    for x in manifest["entries"]:
        if not isinstance(x,dict):continue
        path=x.get("path")
        if not isinstance(path,str) or not path.startswith("/") or not x.get("name"):
            continue
        if Path(x["name"]).suffix.lower() not in VIDEO_EXTENSIONS:continue
        if path in seen:continue
        seen.add(path)
        yield x

def reconcile(manifest,site,registry=None):
    items=site.get("items",[])
    if not isinstance(items,list):raise ValueError("Public site JSON must supply items[]")
    byname=defaultdict(list)
    for item in items:
        if isinstance(item,dict):
            name=str(item.get("name") or item.get("key") or "").lower()
            if name:byname[name].append(item)
    works=(registry or {}).get("works",[])
    entries=[];families=defaultdict(list)
    for x in get_entries(manifest):
        name=str(x["name"]);size=x.get("size_bytes")
        size=size if isinstance(size,int) and size>=0 else None
        public=byname.get(name.lower(),[])
        equal=bool(public and size is not None and any(y.get("size")==size for y in public))
        if equal:status="same_name_same_size"
        elif public:status="same_name_size_unconfirmed_or_different"
        else:status="no_exact_name_match"
        # Owner's project metadata remains in this PRIVATE output only.
        record={"path":x["path"],"name":name,"bytes":size,
                "created_at":x.get("created_at"),"source":"chatgpt_library_metadata",
                "site_correspondence":status,
                "file_sha256":x.get("sha256") if isinstance(x.get("sha256"),str) and re.fullmatch(r"[a-f0-9]{64}",x["sha256"],re.I) else None,
                "file_sha256_verified":False,
                "possible_public_names":[y.get("name") for y in public],
                "family_hint":family_hint(name,x["path"]),
                "work_candidates":[]}
        txt=normalized(name+" "+x["path"])
        for work in works if isinstance(works,list) else []:
            if not isinstance(work,dict):continue
            surname=normalized(work.get("artist","")).split("_")[-1]
            title_tokens=[t for t in normalized(work.get("title","")).split("_")
                         if len(t)>=4 and t not in {"the","with","from","and","for","over"}]
            # Strong hint only: for ambiguous artists or titles use review.
            if surname and surname in txt.split("_") and title_tokens and all(t in txt.split("_") for t in title_tokens):
                record["work_candidates"].append(work.get("id"))
        families[record["family_hint"]].append(name)
        entries.append(record)
    bystatus=dict(Counter(x["site_correspondence"] for x in entries))
    return {"schema":"artvision-private-library-audit-v1",
        "generated_at":datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_manifest": "owner_provided_private_library_metadata",
        "protection":"PRIVATE_ONLY_NOT_FOR_PUBLIC_GITHUB",
        "summary":{"library_mp4":len(entries),"site_catalog_items":len(items),
                   **bystatus,"possible_revision_families":sum(len(v)>1 for v in families.values()),
                   "possible_work_name_hints":sum(bool(x["work_candidates"]) for x in entries),
                   "byte_hashes_independently_verified":0},
        "entries":entries,
        "revision_families":[{"family":k,"files":v,"meaning":"name-based suspicion only"}
                             for k,v in sorted(families.items()) if len(v)>1]}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest",type=Path,required=True,
                   help="Private JSON exported from ChatGPT Library (outside public repo)")
    p.add_argument("--site",type=Path,default=Path("data/archivio-generale/catalogo_sito.json"))
    p.add_argument("--registry",type=Path,default=Path("data/archivio-generale/opere.json"))
    p.add_argument("--out",type=Path,required=True,help="PRIVATE output JSON; must be outside repo")
    p.add_argument("--repo",type=Path,default=Path(__file__).resolve().parents[1])
    args=p.parse_args()
    try:
        dest=secure_destination(args.out,args.repo,args.manifest)
        report=reconcile(load_json(args.manifest),load_json(args.site),load_json(args.registry))
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        # Print aggregate only; absolutely no private filename/path on public CI logs.
        print(json.dumps({"private_report_generated":True,"summary":report["summary"]},ensure_ascii=False))
    except (OSError,ValueError,TypeError) as e:
        print("PRIVATE_AUDIT_FAILED: "+type(e).__name__,file=sys.stderr)
        return 1
    return 0

if __name__=="__main__":raise SystemExit(main())
