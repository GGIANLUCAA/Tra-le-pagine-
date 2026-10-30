#!/usr/bin/env python3
"""Fail-closed ArtVision 4x1 scheduler bridge. No rendering, downloads or paid calls.

Use before invoking production_adapter_v16.py. Diagnoses eligible work only.
It never emits a job or bypasses V13 material/rights preflight.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "queue/artvision_four_variants_s01_20261028.json"
PRODUCTION = ROOT / "queue/production_v15.json"
VARIANTS = ("cinema_standard", "cinema_museum", "critico_standard", "critico_museum")


def choose(root=ROOT):
    queue = json.loads((root / "queue/artvision_four_variants_s01_20261028.json").read_text())
    production = json.loads((root / "queue/production_v15.json").read_text())
    # One ArtVision renderer at a time: never select work while a job exists.
    if production.get("items"):
        return {"status":"existing_jobs_take_priority", "count":len(production["items"]),
                "new_artwork_required":False}
    from artvision_pilot_guard_v58 import enforce_pilot_project
    lock_path = root / "config/artvision_pilot_lock_v58.json"
    if lock_path.is_file():
        lock = json.loads(lock_path.read_text())
        if lock.get("active") is True:
            group = next((g for g in queue["groups"] if g.get("group_id") == lock["allowed_group_id"]), None)
            if group is None:
                return {"status": "pilot_missing_from_queue", "new_artwork_required": False}
            for variant in VARIANTS:
                enforce_pilot_project({"serial_mode":"artvision_4x1","topic":group["artwork"],"artvision_4x1_variant":variant},root)
            states={v:group["variants"][v]["status"] for v in VARIANTS}
            if all(s in ("rendered_needs_review","approved_for_final_delivery") for s in states.values()):
                second=lock.get("authorized_second_pilot",{})
                if second.get("enabled") is True and second.get("phase")=="second_pilot_only_not_automatic_series":
                    next_group=next((g for g in queue["groups"] if g.get("group_id")==second.get("allowed_group_id")),None)
                    if next_group is None or next_group.get("artwork")!=second.get("allowed_title"):
                        return {"status":"authorized_second_pilot_missing","rendering_allowed":False,
                                "new_artwork_required":False}
                    for variant in VARIANTS:
                        enforce_pilot_project({"serial_mode":"artvision_4x1",
                            "topic":next_group["artwork"],"artvision_4x1_variant":variant},root)
                    second_states={v:next_group["variants"][v]["status"] for v in VARIANTS}
                    count=sum(s in ("rendered_needs_review","approved_for_final_delivery") for s in second_states.values())
                    third=lock.get("authorized_third_pilot",{})
                    if count==4 and third.get("enabled") is True and third.get("phase")=="third_pilot_only_no_unbounded_series":
                        wave=next((g for g in queue["groups"] if g.get("group_id")==third.get("allowed_group_id")),None)
                        if wave is None or wave.get("artwork")!=third.get("allowed_title"):
                            return {"status":"third_pilot_missing","new_artwork_required":False,"rendering_allowed":False}
                        for variant in VARIANTS:
                            enforce_pilot_project({"serial_mode":"artvision_4x1",
                               "topic":wave["artwork"],"artvision_4x1_variant":variant},root)
                        wstates={v:wave["variants"][v]["status"] for v in VARIANTS}
                        rendered=sum(s in ("rendered_needs_review","approved_for_final_delivery") for s in wstates.values())
                        # V76: exact fourth pilot, never a generic queue release.
                        fourth=lock.get("authorized_fourth_pilot",{})
                        if (rendered==4 and fourth.get("enabled") is True and
                            fourth.get("phase")=="fourth_pilot_bosch_only" and
                            fourth.get("allowed_group_id")=="bosch_garden_earthly_delights_prado_p002823" and
                            fourth.get("automatic_fifth_artwork_selection") is False):
                            bosch=next((g for g in queue["groups"] if
                                g.get("group_id")==fourth.get("allowed_group_id") and
                                g.get("artwork")==fourth.get("allowed_title")),None)
                            if bosch is None:
                                return {"status":"fourth_pilot_missing","rendering_allowed":False,
                                        "new_artwork_required":False}
                            for v in VARIANTS:
                                enforce_pilot_project({"serial_mode":"artvision_4x1",
                                    "topic":bosch["artwork"],"artvision_4x1_variant":v},root)
                            bstates={v:bosch["variants"][v]["status"] for v in VARIANTS}
                            bcount=sum(s in ("rendered_needs_review","approved_for_final_delivery")
                                       for s in bstates.values())
                            fifth=lock.get("authorized_fifth_pilot",{})
                            if (bcount==4 and fifth.get("enabled") is True and
                                fifth.get("phase")=="fifth_pilot_wright_only" and
                                fifth.get("allowed_group_id")=="wright_air_pump_1768" and
                                fifth.get("automatic_sixth_artwork_selection") is False):
                                wright=next((g for g in queue["groups"] if
                                    g.get("group_id")==fifth.get("allowed_group_id") and
                                    g.get("artwork")==fifth.get("allowed_title")),None)
                                if wright is None:
                                    return {"status":"fifth_pilot_missing","rendering_allowed":False,
                                            "new_artwork_required":False}
                                for v in VARIANTS:
                                    enforce_pilot_project({"serial_mode":"artvision_4x1",
                                        "topic":wright["artwork"],"artvision_4x1_variant":v},root)
                                fifth_states={v:wright["variants"][v]["status"] for v in VARIANTS}
                                fifth_count=sum(s in ("rendered_needs_review","approved_for_final_delivery")
                                                for s in fifth_states.values())
                                return {"status":"fifth_pilot_four_rendered_review_pending" if fifth_count==4 else "fifth_pilot_in_progress",
                                        "work":wright["group_id"],"artwork":wright["artwork"],
                                        "rendered_count":fifth_count,
                                        "approved_count":sum(s=="approved_for_final_delivery" for s in fifth_states.values()),
                                        "variants":fifth_states,
                                        "rendering_allowed":fifth_count!=4,
                                        "new_artwork_required":False,"new_sixth_artwork_allowed":False,
                                        "next_action":"Wright five-work pilot has four genuine MP4s, one same Gacrux WAV and documented real frame. No automatic sixth work; V25 review, archivability, access only."}
                            return {"status":"fourth_pilot_four_rendered_review_pending" if bcount==4
                                      else "fourth_pilot_in_progress",
                                    "work":bosch["group_id"],"artwork":bosch["artwork"],
                                    "rendered_count":bcount,"variants":bstates,
                                    "new_artwork_required":False,"new_fifth_artwork_allowed":False,
                                    "rendering_allowed":bcount<4,
                                    "next_action":"Only Bosch scoped slots after asset/rights/voice/frame gates; "
                                      "Cinema Standard first. No fifth work or paid AI calls."}
                        return {"status":"third_pilot_four_rendered_review_pending" if rendered==4 else "third_pilot_in_progress",
                                "work":wave["group_id"],"artwork":wave["artwork"],
                                "rendered_count":rendered,"variants":wstates,
                                "new_artwork_required":False,"new_fourth_artwork_allowed":False,
                                "next_action":"Complete the exact 2 missing Hokusai Critico slots with same Google Gacrux WAV; preserve 2 existing Cinema MP4s, no auto 4th work."}
                    return {"status":"second_pilot_preproduction" if count==0 else
                             ("second_pilot_four_rendered_review_pending" if count==4 else "second_pilot_in_progress"),
                             "work":next_group["group_id"],"artwork":next_group["artwork"],
                             "new_artwork_required":False,"new_third_artwork_allowed":False,
                             "rendered_count":count,"approved_count":sum(
                                s=="approved_for_final_delivery" for s in second_states.values()),
                             "variants":second_states,
                             "next_action":"Advance The Kiss only after artwork-specific source, rights, Gacrux and V13/V46 gates. Never count dossier/preview as MP4; preserve Socrates."}
                completed=sum(s=="approved_for_final_delivery" for s in states.values())
                return {"status":"pilot_four_rendered_review_pending" if completed<4 else "pilot_awaiting_explicit_second_pilot",
                        "work":group["group_id"],
                        "new_artwork_required":False,
                        "rendering_allowed":False,
                        "rendered_count":4,"approved_count":completed,
                        "variants":states,
                        "next_action":"Use ArtVision V68 reusable recipe to preserve feedback, run real visual/audio QA and verify private archive; do NOT auto-produce more works or repeat renders. Explicit user approval is required for second pilot."}
            return {"status":"pilot_in_progress","work":group["group_id"],
                    "new_artwork_required":False,
                    "variants":states,
                    "next_action":"Complete the missing Socrates 4x1 slots; do not select new artwork."}

    if production.get("items"):
        return {"status": "existing_jobs_take_priority", "count": len(production["items"])}
    blocked = []
    missing_standard = 0
    for group in queue["groups"]:
        for variant in VARIANTS:
            state = group["variants"][variant]["status"]
            if state in ("rendered_needs_review", "approved_for_final_delivery"):
                continue
            if variant.startswith("critico"):
                blocked.append({"work": group["group_id"], "variant": variant,
                                "reason": "verified_gacrux_cache_required"})
                continue
            if variant == "cinema_museum":
                blocked.append({"work": group["group_id"], "variant": variant,
                                "reason": "no_verified_generic_museum_renderer"})
                continue
            missing_standard += 1
            blocked.append({"work": group["group_id"], "variant": variant,
                            "reason": "prepared_v13_project_and_rights_review_required"})
    # A planned Museum without a compatible real renderer is not an executable
    # video job. Do not let it monopolize the only ArtVision rendering owner;
    # instead prepare a new authentic Standard subject, preserving Museum block.
    return {"status": "new_artwork_preparation_required" if not missing_standard else "missing_standard_preparation",
            "blockers": blocked,
            "new_artwork_required": missing_standard == 0,
            "next_action": "Select a new V32-reviewed artwork and prepare authentic local assets, music rights, four-variant dossier and V13 project; do not enqueue a fake render."
               if missing_standard == 0 else "Prepare the listed missing Cinema Standard with source/rights-reviewed V13 project; do not manufacture a V15 job."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = choose()
    print(json.dumps(result, ensure_ascii=False, indent=2))
