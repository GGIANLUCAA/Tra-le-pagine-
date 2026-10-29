"""Fail-closed four-variant pilot lock; no render or paid requests."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
VARIANTS={"critico_standard","critico_museum","cinema_standard","cinema_museum"}

def enforce_pilot_project(project, root=ROOT):
    if project.get("serial_mode")!="artvision_4x1":
        return
    policy=Path(root)/"config/artvision_pilot_lock_v58.json"
    if not policy.exists():
        return  # Legacy branches have no lock; active branch must keep its config.
    lock=json.loads(policy.read_text(encoding="utf-8"))
    if lock.get("schema")!="artvision-pilot-lock-v58":
        raise ValueError("ArtVision pilot lock schema invalid")
    if lock.get("active") is not True:
        return
    if lock.get("automatic_new_artwork_selection") is not False:
        raise ValueError("ArtVision pilot lock policy invalid")
    permitted={lock.get("allowed_title")}
    second=lock.get("authorized_second_pilot", {})
    if second.get("enabled") is True and second.get("phase")=="second_pilot_only_not_automatic_series":
        permitted.add(second.get("allowed_title"))
    if project.get("topic") not in permitted:
        raise ValueError("ArtVision PILOT LOCK: artwork outside explicitly authorized pilots")
    variant=project.get("artvision_4x1_variant")
    if variant not in VARIANTS or variant not in lock["variant_ids"]:
        raise ValueError("ArtVision PILOT LOCK: invalid variant")
