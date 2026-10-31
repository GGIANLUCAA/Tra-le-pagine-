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
    third=lock.get("authorized_third_pilot", {})
    if third.get("enabled") is True and third.get("phase")=="third_pilot_only_no_unbounded_series":
        permitted.add(third.get("allowed_title"))
    fourth=lock.get("authorized_fourth_pilot", {})
    if (fourth.get("enabled") is True and
            fourth.get("phase")=="fourth_pilot_bosch_only" and
            fourth.get("allowed_group_id")=="bosch_garden_earthly_delights_prado_p002823" and
            fourth.get("allowed_title")=="The Garden of Earthly Delights" and
            fourth.get("automatic_fifth_artwork_selection") is False):
        permitted.add(fourth["allowed_title"])
    fifth=lock.get("authorized_fifth_pilot", {})
    if (fifth.get("enabled") is True and
            fifth.get("phase")=="fifth_pilot_wright_only" and
            fifth.get("allowed_group_id")=="wright_air_pump_1768" and
            fifth.get("allowed_title")=="An Experiment on a Bird in the Air Pump" and
            fifth.get("automatic_sixth_artwork_selection") is False):
        permitted.add(fifth["allowed_title"])
    sixth=lock.get("authorized_sixth_pilot", {})
    if (sixth.get("enabled") is True and
            sixth.get("phase")=="sixth_pilot_bocklin_only" and
            sixth.get("allowed_group_id")=="bocklin_isle_of_dead_1883_berlin_ng2_80" and
            sixth.get("allowed_title")=="Isle of the Dead" and
            sixth.get("automatic_seventh_artwork_selection") is False and
            fifth.get("enabled") is True):
        permitted.add(sixth["allowed_title"])
    if project.get("topic") not in permitted:
        raise ValueError("ArtVision PILOT LOCK: artwork outside explicitly authorized pilots")
    variant=project.get("artvision_4x1_variant")
    if variant not in VARIANTS or variant not in lock["variant_ids"]:
        raise ValueError("ArtVision PILOT LOCK: invalid variant")
