#!/usr/bin/env python3
"""V66: source-geometry gate for archival B/W -> generative color photo.
Not an identity detector; high sharpness alone never proves historical fidelity.
An actual human review and origin/rights checks are mandatory for approval.
"""
import argparse, hashlib, json
from pathlib import Path
import cv2
import numpy as np

REQUIRED = ["source_faces_poses_approved","original_people_count_preserved",
            "same_objects_and_layout_approved","photo_quality_reference_approved",
            "ai_reconstruction_disclosure_confirmed","rights_verified"]

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as fp:
        for part in iter(lambda:fp.read(1024*1024),b""): h.update(part)
    return h.hexdigest()

def compare(source_path,candidate_path,human_review=None):
    source=cv2.imread(str(source_path)); candidate=cv2.imread(str(candidate_path))
    if source is None or candidate is None: raise ValueError("Missing/undecodable images")
    def geometry_map(image):
        gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        low=cv2.resize(gray,(64,112),interpolation=cv2.INTER_AREA)
        return cv2.GaussianBlur(low,(11,11),0).astype(np.float32)
    a=geometry_map(source);b=geometry_map(candidate)
    corr=float(np.corrcoef(a.ravel(),b.ravel())[0,1])
    if not np.isfinite(corr):corr=0.
    chroma=float(cv2.cvtColor(candidate,cv2.COLOR_BGR2HSV)[:,:,1].mean())
    sharpness=float(cv2.Laplacian(cv2.cvtColor(candidate,cv2.COLOR_BGR2GRAY),cv2.CV_32F).var())
    manual=human_review or {}
    geometry_ok=corr>=.56
    human_ok=all(manual.get(k) is True for k in REQUIRED)
    status=("ART_DIRECTOR_APPROVED" if geometry_ok and human_ok
            else "REJECT_NOT_SOURCE_FAITHFUL" if not geometry_ok
            else "PENDING_HUMAN_FIDELITY_AND_IMAGE_QUALITY_REVIEW")
    return {
        "v":"V66","source_sha256":sha256(source_path),
        "candidate_sha256":sha256(candidate_path),
        "source_dimensions":list(source.shape[1::-1]),
        "candidate_dimensions":list(candidate.shape[1::-1]),
        "source_geometry_correlation":round(corr,4),
        "geometry_compatible":geometry_ok,
        "mean_color_saturation":round(chroma,2),
        "laplacian_variance_descriptive_NOT_quality_grade":round(sharpness,2),
        "manual_review":{k:manual.get(k,None) for k in REQUIRED},
        "status":status,
        "caveat":"No algorithm can recover a true face that the source did not record. Do not claim identity accuracy from this score."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("source");p.add_argument("candidate")
    p.add_argument("--human-json");p.add_argument("--report",required=True)
    args=p.parse_args()
    manual=json.loads(Path(args.human_json).read_text()) if args.human_json else None
    result=compare(args.source,args.candidate,manual)
    Path(args.report).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(result["status"],result["source_geometry_correlation"])
    return 0 if result["status"]=="ART_DIRECTOR_APPROVED" else 2
if __name__=="__main__":raise SystemExit(main())
