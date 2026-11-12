#!/usr/bin/env python3
"""Fail-closed evidence gate for photorealistic freeze-frame restoration.

Checks *evidence and provenance*, not subjective visual quality. No provider calls,
no credentials, no cost. Artistic approval is always separate.
"""
import argparse
import hashlib
import json
from pathlib import Path

def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def evaluate(manifest, root):
    errors=[]
    scenes=manifest.get("scenes")
    if not isinstance(scenes,list) or not scenes:
        errors.append("NO_SCENES")
        scenes=[]
    for index,scene in enumerate(scenes,1):
        prefix=f"SCENE_{index}_"
        if not isinstance(scene,dict):
            errors.append(prefix+"INVALID")
            continue
        if scene.get("reconstruction_method")!="generative_image_to_image":
            errors.append(prefix+"NOT_GENERATIVE_I2I")
        if not scene.get("provider") or not scene.get("model"):
            errors.append(prefix+"MODEL_PROVENANCE_MISSING")
        if not isinstance(scene.get("original_timecode_s"),(int,float)) or scene["original_timecode_s"]<0:
            errors.append(prefix+"TIMECODE_MISSING")
        for field in ("original_frame","generated_photo"):
            name=scene.get(field)
            if not isinstance(name,str) or not name or Path(name).is_absolute() or ".." in Path(name).parts:
                errors.append(prefix+field.upper()+"_PATH_INVALID")
                continue
            path=(root/name).resolve()
            if not path.is_relative_to(root.resolve()) or not path.is_file() or path.stat().st_size<1000:
                errors.append(prefix+field.upper()+"_MISSING")
                continue
            expected=scene.get(field+"_sha256")
            if not isinstance(expected,str) or expected.lower()!=sha256(path):
                errors.append(prefix+field.upper()+"_SHA_MISMATCH")
        if scene.get("human_scene_fidelity_review") is not True:
            errors.append(prefix+"FIDELITY_REVIEW_PENDING")
        if scene.get("human_benchmark_visual_review") is not True:
            errors.append(prefix+"BENCHMARK_VISUAL_REVIEW_PENDING")
    return {"status":"FINAL_APPROVAL_EVIDENCE_PASS" if not errors else "BLOCKED_PHOTO_RECONSTRUCTION_OR_REVIEW",
            "evidence_gate_only":True,"artistic_quality_guaranteed":False,
            "scene_count":len(scenes),"errors":errors}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--manifest",required=True,type=Path)
    parser.add_argument("--root",required=True,type=Path)
    parser.add_argument("--report",required=True,type=Path)
    args=parser.parse_args()
    result=evaluate(json.loads(args.manifest.read_text()),args.root)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result))
    return 0 if not result["errors"] else 2

if __name__=="__main__":
    raise SystemExit(main())
