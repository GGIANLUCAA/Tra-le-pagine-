"""V152: prevent mixed historical footage from becoming paid 4+1 jobs."""
import copy
import json
import unittest
from pathlib import Path

from src.storia_rivive_v152_editorial_preflight import STATUS, V151_STATUS, audit

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "config/storia_rivive_v149_five_original_motion_preview.json").read_text(encoding="utf-8"))


def handoff_for(m):
    rows = []
    for source in m["sources"]:
        rows.append({
            "scene": source["scene"],
            "role": "I2I_PHOTO_CANDIDATE_NOT_GENERATED" if source["scene"] <= 4 else "VIDU_ANCHOR_NOT_SUBMITTED",
            "source_id": source["id"], "source_page": source["source_page"],
            "source_film_sha256": source["original_sha256"],
            "native_original_frame_sha256": source["frame_sha256"],
            "native_original_frame_pts": source["freeze_pts"],
            "native_time_base": source["time_base"],
            "image_to_image_sent": False, "vidu_request_sent": False,
            "source_subject_artistically_reviewed": False,
            "face_and_object_fidelity_verified": False,
            "rights_italy_verified": False, "provider_credit_budget_approved": False,
        })
    return {
        "status": V151_STATUS, "real_source_frames_sha_verified": 5,
        "candidate_i2i_jobs": 4, "vidu_frame_anchors": 1,
        "real_restored_photos_generated": 0, "real_vidu_clips_generated": 0,
        "provider_requests_sent": 0, "paid_api_calls": 0,
        "source_subjects_are_a_coherent_single_episode_verified": False,
        "five_different_camera_shots_artistically_verified": False,
        "rights_italy_verified": False, "artistic_approved": False,
        "gateway_scene_permission_granted": False, "publish_permitted": False,
        "freeze_frames": rows,
    }


class EditorialPreflightV152(unittest.TestCase):
    def test_real_manifest_is_mixed_and_not_a_coherent_episode(self):
        result = audit(MANIFEST, handoff_for(MANIFEST))
        self.assertEqual(result["status"], STATUS)
        self.assertEqual(result["source_years"], [1896, 1897, 1898, 1900])
        self.assertEqual(result["scenes_without_documented_place"], [2, 3, 5])
        self.assertEqual(result["same_place_year_candidate_groups"], [
            {"place": "LYON", "year": 1896, "scenes": [1, 4], "count": 2}
        ])
        self.assertIn("MIXED_HISTORICAL_YEARS", result["blocking_reasons"])
        self.assertFalse(result["provider_jobs_may_start"])
        self.assertEqual(result["paid_api_calls"], 0)

    def test_even_same_city_and_year_does_not_approve_rights_or_paid_jobs(self):
        m = copy.deepcopy(MANIFEST)
        for s in m["sources"]:
            s["year"] = 1896
            s["place_label"] = "LYON · 1896"
        result = audit(m, handoff_for(m))
        self.assertEqual(result["scenes_without_documented_place"], [])
        self.assertEqual(result["source_years"], [1896])
        self.assertNotIn("MIXED_HISTORICAL_YEARS", result["blocking_reasons"])
        self.assertFalse(result["provider_jobs_may_start"])
        self.assertFalse(result["coherent_single_episode_verified"])
        self.assertFalse(result["rights_italy_verified"])

    def test_tampered_source_frame_sha_is_rejected(self):
        h = handoff_for(MANIFEST)
        h["freeze_frames"][4]["native_original_frame_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "V152_HANDOFF_SCENE_SHA_ROLE_OR_PERMISSION_MISMATCH"):
            audit(MANIFEST, h)

    def test_tampered_vidu_role_or_source_is_rejected(self):
        h = handoff_for(MANIFEST)
        h["freeze_frames"][4]["role"] = "I2I_PHOTO_CANDIDATE_NOT_GENERATED"
        with self.assertRaisesRegex(ValueError, "V152_HANDOFF_SCENE_SHA_ROLE_OR_PERMISSION_MISMATCH"):
            audit(MANIFEST, h)

    def test_forged_approval_is_rejected(self):
        h = handoff_for(MANIFEST)
        h["gateway_scene_permission_granted"] = True
        with self.assertRaisesRegex(ValueError, "V152_UNVERIFIED_OR_PREAPPROVED_HANDOFF"):
            audit(MANIFEST, h)

    def test_forged_row_permission_is_rejected(self):
        h = handoff_for(MANIFEST)
        h["freeze_frames"][0]["rights_italy_verified"] = True
        with self.assertRaisesRegex(ValueError, "V152_HANDOFF_SCENE_SHA_ROLE_OR_PERMISSION_MISMATCH"):
            audit(MANIFEST, h)

    def test_place_year_contradiction_is_rejected(self):
        m = copy.deepcopy(MANIFEST)
        m["sources"][0]["place_label"] = "LYON · 1897"
        with self.assertRaisesRegex(ValueError, "V152_PLACE_LABEL_YEAR_CONTRADICTS_SOURCE"):
            audit(m, handoff_for(m))

    def test_missing_fifth_scene_is_rejected(self):
        h = handoff_for(MANIFEST)
        h["freeze_frames"].pop()
        with self.assertRaisesRegex(ValueError, "V152_EXACT_FIVE_SOURCE_HANDOFF_ROWS_REQUIRED"):
            audit(MANIFEST, h)


if __name__ == "__main__":
    unittest.main()
