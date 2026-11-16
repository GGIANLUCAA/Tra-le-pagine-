#!/usr/bin/env python3
"""Advisory ArtVision preflight — identify existing work+variant before new render.

Read-only: does not start, stop, approve, publish or delete any video. All file
hashes here are historical claims, never an assertion that bytes are reachable.
"""
from __future__ import annotations
import argparse
import json
import re
import unicodedata
from pathlib import Path

VARIANTS=("critico_standard","critico_museum","cinema_standard","cinema_museum")

def norm(x):
    text=unicodedata.normalize("NFKD",str(x or ""))
    text="".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+"," ",text.lower()).strip()

def find_work(registry,artist,title):
    works=registry.get("works",[])
    exact=[w for w in works if norm(w.get("artist"))==norm(artist) and norm(w.get("title"))==norm(title)]
    if exact:return exact
    # Aliases must be explicitly documented; surname-only or title-only is insufficient.
    return []

def preflight(registry,artist,title,variant,candidate_sha256=None):
    if variant not in VARIANTS:
        raise ValueError("Unknown ArtVision 4x1 variant")
    matches=find_work(registry,artist,title)
    if not matches:
        return {"verdict":"UNKNOWN_NEEDS_RESEARCH","artist":artist,"title":title,
            "variant":variant,"auto_skip_render":False,"reason":"Exact work identity not in registry"}
    if len(matches)>1:
        return {"verdict":"AMBIGUOUS_WORK","candidate_ids":[w.get("id") for w in matches],
            "variant":variant,"auto_skip_render":False,"reason":"Multiple historical objects require human identification"}
    w=matches[0]
    v=w.get("variants",{}).get(variant,{})
    claims=v.get("evidence",[])
    sha_claims={e.get("sha256") for e in claims if isinstance(e,dict) and e.get("sha256")}
    requested=candidate_sha256.lower() if isinstance(candidate_sha256,str) else None
    exact_prior_sha=bool(requested and requested in sha_claims)
    if w.get("excluded"):
        verdict="EXCLUDED_BY_OWNER"
    elif exact_prior_sha:
        verdict="SHA_ALREADY_RECORDED"
    elif v.get("state")=="render_documentato":
        verdict="RENDER_EXISTS_VERIFY_REUSE_OR_REVISION"
    elif v.get("state")=="render_respinto":
        verdict="REJECTED_RENDER_REMAKE_ONLY_WITH_APPROVED_ASSETS"
    elif v.get("state")=="bloccato":
        verdict="BLOCKED_REPAIR_INDEPENDENTLY"
    else:
        verdict="NOT_DOCUMENTED_CHECK_PRIVATE_AND_SITE"
    return {"verdict":verdict,"work_id":w.get("id"),"artist":w.get("artist"),"title":w.get("title"),
            "variant":variant,"variant_state":v.get("state","non_documentato"),
            "render_evidence_count":len(claims),"prior_sha_claim_count":len(sha_claims),
            "same_sha_claim":exact_prior_sha,"site_candidate_count":len(w.get("site_candidates",[])),
            "owner_excluded":bool(w.get("excluded")),"auto_skip_render":False,
            "explanation":"Advisory only: verify real MP4/QA, owner approval and library/site inventory before any rerender."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--artist",required=True);p.add_argument("--title",required=True)
    p.add_argument("--variant",required=True,choices=VARIANTS)
    p.add_argument("--candidate-sha256")
    p.add_argument("--registry",type=Path,default=Path("data/archivio-generale/opere.json"))
    args=p.parse_args()
    r=json.loads(args.registry.read_text(encoding="utf-8"))
    print(json.dumps(preflight(r,args.artist,args.title,args.variant,args.candidate_sha256),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
