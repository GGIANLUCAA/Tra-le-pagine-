#!/usr/bin/env python3
"""V153 negative visual QA on REAL one-shot photographic files.

Checks exact bytes of a model-produced candidate against a versioned known-bad
SHA registry. A high numerical grayscale correlation does NOT mean
people/animal identity is preserved. Never marks an unknown image as
artistically approved; no network, models, credits or publishing.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image
from src.storia_rivive_v149_authentic_bw_proxy import sha256_file

REGISTRY_VERSION="V153_KNOWN_I2I_ARTISTIC_REJECTS_V1"
REJECT="V153_VISUAL_IDENTITY_QA_REJECT_KNOWN_HALLUCINATION_RISK"
REVIEW="V153_UNSEEN_AI_IMAGE_HUMAN_REVIEW_REQUIRED"


def audit(folder, registry):
    root=Path(folder)
    record=json.loads((root/"V153_EXPERIMENT_REPORT.json").read_text(encoding="utf-8"))
    negatives=json.loads(Path(registry).read_text(encoding="utf-8"))
    if (negatives.get("version")!=REGISTRY_VERSION
            or negatives.get("not_a_user_approval") is not True
            or negatives.get("production_rights_italy_verified") is not False):
        raise ValueError("V153_KNOWN_BAD_REGISTRY_NOT_AUTHENTIC")
    if (record.get("version")!="V153" or record.get("scene")!=2
            or record.get("source_id")!="girl_cat_1900"
            or record.get("source_frame_sha256")!="37da59961c75fddea7609ab2d29302f0171dd2c45f9e823ebc8059b7ab810534"
            or record.get("source_crop_sha256")!="209320b0bcf9b734e28f5160542c6d99a4043dedf09d0ed36e84833d4a367b25"
            or record.get("real_i2i_generated") is not True
            or record.get("technical_candidate_pass") is not True
            or record.get("free_provider_requests_sent")!=1
            or record.get("paid_calls")!=0 or record.get("vidu_calls")!=0
            or record.get("finished_video") is not False
            or record.get("rights_italy_verified") is not False
            or record.get("artistically_approved") is not False):
        raise ValueError("V153_PREVIOUS_TECHNICAL_ARTIFACT_INVALID_FOR_VISUAL_QA")
    photo=root/"SCENE02_FREE_I2I_CANDIDATE.png"
    preview=root/"SCENE02_BW_FREEZE_REAL_I2I_REVIEW_ONLY.mp4"
    for path,key in [(photo,"i2i_candidate_sha256"),
                     (preview,"technical_video_preview_sha256")]:
        if not path.is_file() or path.is_symlink() or sha256_file(path)!=record.get(key):
            raise ValueError("V153_REAL_PHOTO_OR_MP4_BYTES_SHA_NOT_MATCHING_QA")
    with Image.open(photo) as image:
        image.verify()
    with Image.open(photo) as image:
        if image.size!=(720,1280) or image.format!="PNG":
            raise ValueError("V153_MODEL_OUTPUT_NOT_REAL_CORRECT_FORMAT_PHOTO")
    p=subprocess.run(["ffprobe","-v","error","-show_entries",
        "stream=codec_name,codec_type,width,height:format=duration",
        "-of","json",str(preview)],capture_output=True,text=True,check=True,timeout=35)
    info=json.loads(p.stdout)
    video=[x for x in info.get("streams",[]) if x.get("codec_type")=="video"]
    if (len(video)!=1 or video[0].get("codec_name")!="h264"
            or video[0].get("width")!=720 or video[0].get("height")!=1280
            or not 4.2 <= float(info["format"]["duration"]) <= 4.9):
        raise ValueError("V153_4SEC_BW_TO_I2I_VIDEO_CORRUPT")
    # Do NOT infer new identity for unknown image. Exact SHA can disqualify one
    # already-observed bad result; any other file is still human-QA pending.
    known=[]
    for entry in negatives.get("entries",[]):
        if (entry.get("scene")==2
                and entry.get("source_id")==record["source_id"]
                and entry.get("source_frame_sha256")==record["source_frame_sha256"]
                and entry.get("source_crop_sha256")==record["source_crop_sha256"]
                and entry.get("ai_photo_sha256")==record["i2i_candidate_sha256"]
                and entry.get("inspection")=="ASSISTANT_VISUAL_REVIEW_REJECT_NOT_HUMAN_APPROVAL"
                and entry.get("pilot_reuse_permitted") is False
                and entry.get("serial_production_permitted") is False
                and entry.get("social_or_site_publication_permitted") is False):
            known.append(entry)
    if len(known)>1:
        raise ValueError("V153_DUPLICATE_NEGATIVE_REVIEW_SHA")
    report={
        "version":"V153_ARTISTIC_ANTI_REGRESSION",
        "status": REJECT if known else REVIEW,
        "source_frame_sha256":record["source_frame_sha256"],
        "actual_i2i_photo_sha256":sha256_file(photo),
        "actual_mp4_sha256":sha256_file(preview),
        "technical_metric_pass_does_not_equal_artistic_pass":True,
        "visual_inspection_kind":"ASSISTANT_VISUAL_REVIEW_NOT_HUMAN_APPROVAL" if known else "PENDING",
        "visual_inspection_reasons":known[0]["reasons"] if known else [],
        "master_eligible":False,
        "candidate_allowed_as_reused_i2i":False,
        "v98_level_claimed":False,
        "five_film_editorial_coherence_verified":False,
        "rights_italy_verified":False,
        "human_artistic_approval":False,
        "social_or_site_publication_permitted":False,
        "provider_requests_made_during_this_QA":0,
        "credits_spent_during_this_QA":0
    }
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--artifact-dir",required=True)
    p.add_argument("--registry",default="config/storia_rivive_v153_rejected_i2i_samples.json")
    p.add_argument("--out",required=True)
    args=p.parse_args()
    result=audit(args.artifact_dir,args.registry)
    path=Path(args.out)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("V153_ARTISTIC_REVIEW_RESULT",result["status"],"no_approval",True,"paid",0)
