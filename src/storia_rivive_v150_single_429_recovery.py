#!/usr/bin/env python3
"""V150: retry only the ONE Commons source hit by HTTP429 in V149 (scene 3).

Preserve all four already-verified 1.35s H264 previews from run 41223340544
without requesting their full original video again. Maximum TWO attempts,
one gentle 12s pause on explicit HTTP429, never API payments or publishing.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

try:
    from src.storia_rivive_v149_authentic_bw_proxy import validate,process_one
except ModuleNotFoundError:
    from storia_rivive_v149_authentic_bw_proxy import validate,process_one

PRIOR_RUN=41223340544
PRIOR_ARTIFACT_A=13050324762
PRIOR_ARTIFACT_B=13050802833


def recover(manifest,outdir,*,processor=process_one,delay=time.sleep):
    m=json.loads(Path(manifest).read_text(encoding="utf-8"))
    films=validate(m)
    item=films[2]
    if item["scene"]!=3 or item["id"]!="workers_sidewalk_1898":
        raise ValueError("V150_MUST_RECOVER_ONLY_WORKERS_1898")
    root=Path(outdir);root.mkdir(parents=True,exist_ok=True)
    result=None
    for attempt in (1,2):
        result=processor(item,root)
        if result.get("status")=="V149_TRUE_SOURCE_BW_MOVING_MP4_REVIEW_ONLY":
            break
        if attempt==2 or "429" not in result.get("reason",""):
            break
        print("V150_COMMONS_HTTP429_ONE_SLOW_RETRY_AFTER_COOLDOWN",flush=True)
        delay(12)
    record={"version":"V150_ONE_MISSING_REAL_FILM_RECOVERY",
            "status":("V150_WORKERS_REAL_BW_SOURCE_MP4_RECOVERED" if
                       result.get("status")=="V149_TRUE_SOURCE_BW_MOVING_MP4_REVIEW_ONLY"
                       else "V150_COMMONS_SOURCE_STILL_BLOCKED_NO_RESTORATION"),
            "prior_run":PRIOR_RUN,"prior_original_artifacts":[PRIOR_ARTIFACT_A,PRIOR_ARTIFACT_B],
            "original_source_reused_not_redownloaded_count":4,
            "retried_source_id":item["id"],"attempts_max":2,
            "clip":result,
            "paid_calls":0,"i2i_generated":0,"vidu_generated":0,
            "human_artistic_approval":False,"rights_italy_verified":False,
            "publish_permitted":False,"video_finished":False}
    (root/"V150_WORKERS_RECOVERY_REPORT.json").write_text(
        json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("V150_ONLY_MISSING_ORIGINAL_SOURCE",record["status"],
          "file",item["id"],"paid",0,flush=True)
    return record


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",default="config/storia_rivive_v149_five_original_motion_preview.json")
    p.add_argument("--out",required=True)
    a=p.parse_args()
    recover(a.manifest,a.out)
