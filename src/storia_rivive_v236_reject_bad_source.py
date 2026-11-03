#!/usr/bin/env python3
"""V236: reject the watermarked Coney Island transfer before AI generation."""
import hashlib
import json
from pathlib import Path

REJECTED_SHA256 = "6360a2073183d610984f5f2743aaaa2d30c2c335ca993917594b0f33f5d56366"

def gate(source_sha256: str, frame_count: int, italy_rights_verified: bool, optical_closeups_verified: bool) -> dict:
    reasons=[]
    if source_sha256 == REJECTED_SHA256:
        reasons.append("FRAMEPOOL_WATERMARKED_TRANSFER_REJECTED_V235")
    if frame_count < 5:
        reasons.append("INSUFFICIENT_DISTINCT_SHOTS")
    if not italy_rights_verified:
        reasons.append("ITALY_RIGHTS_NOT_VERIFIED")
    if not optical_closeups_verified:
        reasons.append("NO_OPTICAL_CLOSEUP_APPROVAL")
    return {"allow_generation":not reasons,"reasons":reasons,
            "credits_allowed":False,"publication_allowed":False}

def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--sha256",required=True)
    p.add_argument("--shots",type=int,default=0)
    p.add_argument("--italy-rights-verified",action="store_true")
    p.add_argument("--optical-closeups-verified",action="store_true")
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    if len(a.sha256)!=64 or any(c not in "0123456789abcdef" for c in a.sha256):
        raise SystemExit("INVALID_SHA256")
    result=gate(a.sha256,a.shots,a.italy_rights_verified,a.optical_closeups_verified)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print("SOURCE_GATE", "PASS" if result["allow_generation"] else "REJECTED",result["reasons"])

if __name__=="__main__":
    main()
