#!/usr/bin/env python3
"""V102: prepare immutable source-locked image-to-image jobs from REAL native film frames.

No provider calls, no AI image output claims, no publication. The result can be
consumed by a future free/approved image-to-image worker.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from PIL import Image

PROMPT=(
    "Restore THIS EXACT archival film frame into a realistic, high-detail modern "
    "documentary photograph. Preserve all existing people, facial identity only "
    "as supported by original pixels, pose, clothes, architecture, vehicles, "
    "objects, framing and perspective. Period-appropriate natural colors. "
    "Never invent eyes, faces, limbs, signs, people or objects. "
    "This is an interpretive color reconstruction, not an original color photograph."
)
NEGATIVE=(
    "face swap, invented identity, extra people, extra limbs, changing objects, "
    "modern cars, plastic skin, cartoon, AI painting, hallucinated text, "
    "wrong era, inaccurate architecture, cropped faces, excessive saturation"
)
def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def build(order,selection,source_dir):
    if order.get("contract")!="LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT":
        raise ValueError("Not an authenticated V101 work-order schema")
    if order.get("paid_api_call_permitted") is not False or order.get("publish_permitted") is not False:
        raise ValueError("Unsafe work-order permissions")
    if selection.get("status")!="FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW":
        raise ValueError("No five candidate source frames")
    chosen=selection.get("preselected",[])
    if len(chosen)!=5:raise ValueError("Need five genuine distinct frame positions")
    names=[r["filename"] for r in chosen]
    if len(set(names))!=5:raise ValueError("Duplicate frames")
    jobs=[]
    for n,row in enumerate(chosen):
        name=row["filename"]
        if not re.fullmatch(r"frame_\d{2}\.png",name):raise ValueError("Unsafe source filename")
        path=source_dir/"original_frames"/name
        if not path.is_file():raise ValueError("Missing original source frame")
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            width,height=image.size
        if width<320 or height<240:raise ValueError("Original source too small")
        jobs.append({
          "job_id":f"{order['cycle_id']}_photo_{n+1:02d}",
          "source_file":str(path),"source_sha256":sha(path),
          "source_raster_px":[width,height],
          "target_raster_px":[720,1280],
          "target_kind":"REAL_SOURCE_LOCKED_I2I_PHOTOGRAPH",
          "role":"VIDU_SOURCE_ANCHOR_NOT_RENDERED" if n==4 else "STATIC_COLOR_REVEAL",
          "prompt":PROMPT,"negative_prompt":NEGATIVE,
          "allow_source_reframing":False,"allow_invented_people":False,
          "provider":"NOT_SELECTED_NO_CALL","request_sent":False,
          "result_file":None,"restored_photo_approved":False,
          "human_face_fidelity":"PENDING","source_geometry_gate":"PENDING",
          "scene_distinctness_gate":"PENDING","rights_gate":"PENDING"
        })
    return {"version":"V102_SOURCE_LOCKED_I2I_JOBS",
      "cycle_id":order["cycle_id"],"episode_id":order["episode_id"],
      "source_video_sha256":sha(source_dir/"ORIGINAL_ARCHIVE.webm"),
      "original_frame_jobs":jobs,"photos_requested":5,
      "photos_generated":0,"photos_approved":0,
      "provider_requests_sent":0,"paid_api_calls":0,
      "vidu_calls":0,"publication_permitted":False,
      "status":"I2I_INPUTS_PREPARED_NO_AI_GENERATION",
      "warning":"These are five source frames, not five verified distinct camera shots."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--order",required=True);p.add_argument("--selection",required=True)
    p.add_argument("--source-dir",required=True);p.add_argument("--out",required=True)
    a=p.parse_args()
    output=Path(a.out);output.parent.mkdir(parents=True,exist_ok=True)
    try:
        data=build(json.loads(Path(a.order).read_text()),
                   json.loads(Path(a.selection).read_text()),Path(a.source_dir))
    except Exception as e:
        data={"version":"V102_SOURCE_LOCKED_I2I_JOBS","status":"I2I_INPUTS_BLOCKED",
              "reason":type(e).__name__+": "+str(e)[:220],
              "photos_generated":0,"provider_requests_sent":0,"paid_api_calls":0,
              "vidu_calls":0,"publication_permitted":False}
    output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("V102_I2I_PREP",data["status"],"provider_requests",data["provider_requests_sent"])
if __name__=="__main__":main()
