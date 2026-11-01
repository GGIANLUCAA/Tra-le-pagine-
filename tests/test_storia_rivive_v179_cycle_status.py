"""V179: V101 must record source rejection instead of failing on missing frames."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("storia_v179", ROOT / "src/storia_rivive_v179_cycle_status.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
ORDER = {"contract": "LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT",
         "cycle_id": "storia-20261101-1200", "episode_id": "fashion_1917",
         "paid_api_call_permitted": False, "publish_permitted": False}


class V179CycleTests(unittest.TestCase):
    def test_sd_film_rejected_with_no_false_assets(self):
        r = module.build_status(ORDER, {"status": "REJECT_LOW_SOURCE_PIXELS_FOR_REFERENCE_LEVEL_MOTION",
                                        "source_raster_quality_gate_v176": {"encoded_raster_px": [352, 240]}})
        self.assertEqual(r["status"], "SOURCE_REJECTED")
        self.assertEqual(r["source_raster_quality_gate_v176"]["encoded_raster_px"], [352, 240])
        self.assertEqual(r["source_frames_preselected_not_shots_verified"], 0)
        self.assertEqual(r["source_locked_i2i_jobs_prepared_not_generated"], 0)
        self.assertFalse(r["finished_mp4"])

    def test_oversize_or_invalid_video_rejected(self):
        for status in ("MANUAL_ACQUISITION_REQUIRED_SIZE_LIMIT", "SOURCE_NO_VIDEO_STREAM",
                       "SOURCE_INVALID_ENCODED_RASTER"):
            with self.subTest(status=status):
                self.assertEqual(module.build_status(ORDER, {"status": status})["status"], "SOURCE_REJECTED")

    def test_network_failure_is_pending_not_success_or_permanent_reject(self):
        r = module.build_status(ORDER, {"status": "SOURCE_SCOUT_BLOCKED_NO_PRODUCTION",
                                        "error_type": "HTTPError"})
        self.assertEqual(r["status"], "ASSETS_PENDING")
        self.assertIn("retry", r["next_required"].lower())
        self.assertEqual(r["charged_api_requests"], 0)

    def test_source_ready_does_not_approve_shots_i2i_or_video(self):
        r = module.build_status(ORDER, {"status": module.READY},
            {"status": "FIVE_BW_FRAME_CANDIDATES_FOR_REAL_ARTISTIC_SOURCE_REVIEW"},
            {"status": "I2I_INPUTS_PREPARED_NO_AI_GENERATION"})
        self.assertEqual(r["status"], "ASSETS_PENDING")
        self.assertEqual(r["source_frames_preselected_not_shots_verified"], 5)
        self.assertEqual(r["source_locked_i2i_jobs_prepared_not_generated"], 5)
        for key in ("five_distinct_moving_shots_verified", "italian_rights_verified",
                    "finished_mp4", "human_approved", "published"):
            self.assertFalse(r[key])
        self.assertEqual(r["restored_i2i_photos_approved"], 0)
        self.assertEqual(r["real_vidu_clips_approved"], 0)

    def test_duplicate_source_frames_reject_cycle_without_i2i(self):
        r = module.build_status(
            ORDER, {"status": module.READY},
            {"status": "SOURCE_TOO_FEW_VISUALLY_DIVERSE_CANDIDATE_FRAMES",
             "preselected": []}, {})
        self.assertEqual(r["status"], "SOURCE_REJECTED")
        self.assertEqual(r["frame_preselection_status"],
                         "SOURCE_TOO_FEW_VISUALLY_DIVERSE_CANDIDATE_FRAMES")
        self.assertEqual(r["source_frames_preselected_not_shots_verified"], 0)
        self.assertEqual(r["source_locked_i2i_jobs_prepared_not_generated"], 0)
        self.assertEqual(r["charged_api_requests"], 0)
        self.assertFalse(r["human_approved"])

    def test_missing_scout_report_never_claims_success(self):
        r = module.build_status(ORDER, {}, {}, {})
        self.assertEqual(r["source_scout"], "SOURCE_SCOUT_NOT_AVAILABLE")
        self.assertEqual(r["status"], "ASSETS_PENDING")

    def test_unsafe_order_is_rejected(self):
        for bad in ({"paid_api_call_permitted": True}, {"publish_permitted": True},
                    {"contract": "INVALID"}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                module.build_status({**ORDER, **bad}, {})

    def test_workflow_skips_rank_and_i2i_on_rejected_source(self):
        w = (ROOT / ".github/workflows/storia-rivive-v101-auto-3h.yml").read_text()
        for step in ("Rank actual native-resolution source frames",):
            start = w.index("      - name: " + step)
            end = w.find("      - name:", start + 1)
            section = w[start:end if end >= 0 else None]
            self.assertIn("if: steps.scout_status.outputs.ready == 'true'", section)
        self.assertIn("python src/storia_rivive_v179_cycle_status.py", w)
        self.assertIn("output/storia_v101/CYCLE_STATUS.json", w)
        self.assertIn("if: always()", w)
        rank_start = w.index("      - name: Rank actual native-resolution source frames")
        rank_end = w.index("      - name: Prepare five source-SHA-locked I2I requests",rank_start)
        self.assertIn("id: frame_rank",w[rank_start:rank_end])
        self.assertIn("V180_FRAME_DIVERSITY_PREFLIGHT",w[rank_start:rank_end])
        prep_start = rank_end
        prep_end = w.index("      - name:",prep_start+1)
        self.assertIn("if: steps.frame_rank.outputs.ready == 'true'",
                      w[prep_start:prep_end])


if __name__ == "__main__":
    unittest.main()
