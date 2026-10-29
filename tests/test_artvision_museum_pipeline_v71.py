import copy
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from artvision_museum_pipeline_v71 import build, load_json, PlanningBlocked, BASELINE, LOCK
from artvision_museum_camera_v64 import camera_at

DOSSIER=ROOT/"docs/productions/2026-10-29-socrates-pilot-v68/MUSEUM_DIRECTOR_DOSSIER_V71.json"

class MuseumPipelineTests(unittest.TestCase):
    def setUp(self):
        self.d=load_json(DOSSIER)
    def test_real_socrates_dossier_passes_without_render(self):
        p=build(self.d)
        self.assertEqual(p["schema"],"artvision-museum-integration-plan-v71")
        self.assertFalse(p["controls"]["render_authorized"])
        self.assertTrue(p["controls"]["pilot_lock_active"])
    def test_real_dimensions_and_frame_are_not_replaced_by_guess(self):
        p=build(self.d)
        self.assertEqual(p["physical_stage"]["artwork"]["width_cm"],196.2)
        self.assertEqual(p["physical_stage"]["artwork"]["height_cm"],129.5)
        self.assertEqual(p["physical_stage"]["frame"]["dimensions_kind"],"supplied_documented_or_estimated")
        self.assertAlmostEqual(p["physical_stage"]["frame"]["width_cm"],233.68,places=2)
        self.assertEqual(p["evidence"]["frame_status"],"historic_documented")
    def test_not_actual_museum_filming(self):
        p=build(self.d)
        self.assertEqual(p["evidence"]["gallery_status"],"declared_contemporary_reconstruction")
        self.assertFalse(p["evidence"]["real_gallery_claim"])
        self.assertIn("NOT actual",p["evidence"]["gallery_disclosure"])
    def test_four_existing_unique_outputs_preserved(self):
        p=build(self.d)
        self.assertEqual(len(p["four_slots"]),4)
        self.assertEqual(len(set(v["existing_sha256"] for v in p["four_slots"].values())),4)
        self.assertFalse(any(v["has_new_render"] for v in p["four_slots"].values()))
        self.assertEqual(sum(bool(v["museum_plan"]) for v in p["four_slots"].values()),2)
    def test_critic_wav_reused_without_synthesis(self):
        p=build(self.d)
        self.assertEqual(len(p["voice"]["critico_exact_shared_wav_sha256"]),64)
        self.assertFalse(p["voice"]["re_synthesis_authorized"])
    def test_camera_returns_and_continuous_across_return(self):
        p=build(self.d)
        for variant in ("critico_museum","cinema_museum"):
            seq=p["museum_camera"][variant]
            seconds=seq["duration_seconds"]
            starts=seq["beat_starts_seconds"]
            poses=seq["poses"]
            first=camera_at(0,seconds,starts,poses)
            last=camera_at(seconds,seconds,starts,poses)
            self.assertTrue(all(abs(a-b)<1e-6 for a,b in zip(first,last)))
            t=starts[-2]
            before=camera_at(t-.001,seconds,starts,poses)
            after=camera_at(t+.001,seconds,starts,poses)
            self.assertLess(max(abs(x-y) for x,y in zip(before,after)),.05)
    def test_missing_frame_provenance_blocks(self):
        d=copy.deepcopy(self.d)
        d["frame"]["photo_source"]=""
        with self.assertRaises(PlanningBlocked):build(d)
    def test_unknown_image_digest_blocks(self):
        d=copy.deepcopy(self.d)
        d["artwork"]["image_sha256"]="not-sha"
        with self.assertRaises(PlanningBlocked):build(d)
    def test_wrong_painting_blocked(self):
        d=copy.deepcopy(self.d)
        d["artwork_id"]="new_non_pilot_artwork"
        with self.assertRaisesRegex(PlanningBlocked,"PILOT LOCK"):build(d)
    def test_existing_media_and_lock_unchanged(self):
        before=copy.deepcopy(self.d)
        b=load_json(BASELINE)
        lock=load_json(LOCK)
        p=build(self.d)
        self.assertEqual(self.d,before)
        self.assertEqual(p["controls"]["owner_automation_id"],lock["owner_automation_id"])
        self.assertEqual(p["four_slots"]["critico_museum"]["existing_sha256"],
                         b["four_slots"]["critico_museum"]["sha256"])

if __name__=="__main__":
    unittest.main()
