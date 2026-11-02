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
    if not isinstance(chosen,list) or any(not isinstance(row,dict) for row in chosen):
        raise ValueError("Invalid frame selection structure")
    if len(chosen)!=5:raise ValueError("Need five genuine distinct frame positions")
    names=[r.get("filename") for r in chosen]
    if any(not isinstance(name,str) for name in names):
        raise ValueError("Invalid source frame filename")
    if len(set(names))!=5:raise ValueError("Duplicate frames")
    jobs=[]
    pixel_hashes=set()
    native_geometry=None
    for n,row in enumerate(chosen):
        name=row["filename"]
        if not re.fullmatch(r"frame_\d{2}\.png",name):raise ValueError("Unsafe source filename")
        path=source_dir/"original_frames"/name
        if path.is_symlink():raise ValueError("Symlink source frame forbidden")
        if not path.is_file():raise ValueError("Missing original source frame")
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            rgb=image.convert("RGB")
            width,height=rgb.size
            pixel_sha256=hashlib.sha256(rgb.tobytes()).hexdigest()
        if width<320 or height<240:raise ValueError("Original source too small")
        if pixel_sha256 in pixel_hashes:raise ValueError("Duplicate decoded source pixels")
        pixel_hashes.add(pixel_sha256)
        if native_geometry is None:native_geometry=(width,height)
        if (width,height)!=native_geometry:raise ValueError("Mixed original frame geometry")
        is_photo=n<4
        jobs.append({
          "job_id":f"{order['cycle_id']}_photo_{n+1:02d}",
          "source_file":str(path),"source_sha256":sha(path),
          "source_pixel_sha256":pixel_sha256,
          "source_raster_px":[width,height],
          "target_raster_px":[720,1280] if is_photo else None,
          "target_kind":"REAL_SOURCE_LOCKED_I2I_PHOTOGRAPH" if is_photo else "VIDU_SOURCE_ANCHOR_NO_I2I",
          "role":"STATIC_COLOR_REVEAL" if is_photo else "VIDU_SOURCE_ANCHOR_NOT_RENDERED",
          "prompt":PROMPT if is_photo else None,
          "negative_prompt":NEGATIVE if is_photo else None,
          "allow_source_reframing":False,"allow_invented_people":False,
          "provider":"NOT_SELECTED_NO_CALL" if is_photo else "NOT_APPLICABLE_NO_I2I",
          "request_sent":False,
          "result_file":None,"restored_photo_approved":False,
          "human_face_fidelity":"PENDING","source_geometry_gate":"PENDING",
          "scene_distinctness_gate":"PENDING","rights_gate":"PENDING"
        })
    archive=source_dir/"ORIGINAL_ARCHIVE.webm"
    if archive.is_symlink() or not archive.is_file():
        raise ValueError("Missing or symlinked original archive")
    return {"version":"V102_SOURCE_LOCKED_I2I_JOBS",
      "cycle_id":order["cycle_id"],"episode_id":order["episode_id"],
      "source_video_sha256":sha(source_dir/"ORIGINAL_ARCHIVE.webm"),
      "original_frame_jobs":jobs,"source_frames_prepared":5,
      "photos_requested":4,"photo_jobs_prepared":4,
      "vidu_source_anchor":{"source_file":jobs[4]["source_file"],
          "source_sha256":jobs[4]["source_sha256"],
          "source_pixel_sha256":jobs[4]["source_pixel_sha256"],
          "approved":False,"vidu_request_sent":False},
      "photos_generated":0,"photos_approved":0,
      "provider_requests_sent":0,"paid_api_calls":0,
      "vidu_calls":0,"publication_permitted":False,
      "status":"I2I_INPUTS_PREPARED_NO_AI_GENERATION",
      "warning":"Four unsubmitted photo I2I jobs and one unsubmitted Vidu source anchor. Five distinct decoded frames are NOT proof of five different camera shots."}

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
