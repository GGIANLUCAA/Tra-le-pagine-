"""Contract tests: unified directorial plan remains conservative and evidence-first."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import studio_regia_supervisor_v1 as regia


def example(fmt="artvision_critico"):
    shots = [
        dict(id="one", start_s=0, end_s=3, asset_id="art", source_verified=True,
             rights_verified=True, visual_subject="Figura centrale", reason="Presenta l'opera",
             composition_group="wide", shot_type="wide", focus_xy=[.5, .5],
             visible_subject_ids=["central"], camera={"move": "locked"}),
        dict(id="two", start_s=3, end_s=6, asset_id="art", source_verified=True,
             rights_verified=True, visual_subject="Volto", reason="Mostra lo sguardo",
             composition_group="detail", shot_type="detail", focus_xy=[.58, .45],
             visible_subject_ids=["face"], camera={"move": "slow_push"}),
    ]
    data = dict(schema=regia.SCHEMA, format=fmt, video_duration_s=6, shots=shots,
                narration=dict(wav_sha256="a"*64, timing_verified=True,
                               segments=[dict(start_s=0, end_s=3, subject_id="central"),
                                         dict(start_s=3, end_s=6, subject_id="face")]))
    return data


class StudioRegiaTests(unittest.TestCase):
    def codes(self, report, kind="blocking"):
        return [x["code"] for x in report[kind]]

    def test_valid_plan_is_not_approval(self):
        result = regia.inspect(example())
        self.assertEqual(result["status"], "plan_needs_real_video_and_artistic_review")
        self.assertEqual(result["blocking"], [])
        self.assertFalse(result["artistic_approved"])
        self.assertFalse(result["can_publish"])
        self.assertFalse(result["rendered"])
        self.assertEqual(result["paid_calls"], 0)

    def test_missing_verified_audio_blocks_narrated(self):
        data = example()
        data["narration"]["timing_verified"] = False
        self.assertIn("SPEECH_TIMECODES_UNVERIFIED", self.codes(regia.inspect(data)))

    def test_subject_not_visible_in_planned_timeline_blocks(self):
        data = example()
        data["shots"][1]["visible_subject_ids"] = ["different"]
        self.assertIn("SUBJECT_MISMATCH", self.codes(regia.inspect(data)))

    def test_subject_late_is_review_and_low_coverage_blocks(self):
        data = example()
        data["shots"][0]["end_s"] = 1.5
        data["shots"].insert(1, dict(data["shots"][0], id="pause", start_s=1.5,
                                     end_s=3, visible_subject_ids=[]))
        result = regia.inspect(data)
        self.assertIn("SUBJECT_MISMATCH", self.codes(result))

    def test_invalid_timeline_blocks(self):
        data = example()
        data["shots"][1]["start_s"] = 2
        self.assertIn("SCENE_OVERLAP", self.codes(regia.inspect(data)))
        data["shots"][1]["start_s"] = 3
        data["shots"][1]["end_s"] = 2
        self.assertIn("INVALID_TIMELINE", self.codes(regia.inspect(data)))

    def test_sources_and_rights_fail_closed(self):
        data = example("storia_rivive")
        data["shots"][0]["rights_verified"] = False
        self.assertIn("SOURCE_NOT_VERIFIED", self.codes(regia.inspect(data)))
        self.assertNotIn("NO_SPEECH_SEGMENTS", self.codes(regia.inspect(data)))

    def test_forbidden_transition_and_camera_block(self):
        data = example()
        data["shots"][1]["transition_in"] = "crossfade"
        data["shots"][1]["camera"] = {"move": "oscillate"}
        result = regia.inspect(data)
        self.assertIn("BAD_TRANSITION", self.codes(result))
        self.assertIn("CAMERA_NOT_DIRECTED", self.codes(result))

    def test_zoom_native_pixels_warning(self):
        data = example()
        data["delivery_resolution_px"] = [1080, 1920]
        data["shots"][1]["source_resolution_px"] = [1200, 1800]
        data["shots"][1]["crop_xyxy"] = [.3, .25, .7, .75]
        self.assertIn("LOW_EFFECTIVE_PIXELS", self.codes(regia.inspect(data), "warnings"))

    def test_repeated_frame_is_not_counted_as_novelty(self):
        data = example("storia_rivive")
        data["narration"] = {}
        data["shots"] = [dict(data["shots"][0], id=str(i), start_s=i*2, end_s=(i+1)*2)
                         for i in range(3)]
        result = regia.inspect(data)
        self.assertIn("REUSED_VISUAL", self.codes(result, "warnings"))

    def test_repeated_move_is_warning_not_hard_style_law(self):
        data = example("artvision_cinema")
        data["shots"] = [dict(data["shots"][1], id=str(i), start_s=i*2, end_s=(i+1)*2)
                         for i in range(3)]
        result = regia.inspect(data)
        self.assertIn("REPEATED_CAMERA_MOVE", self.codes(result, "warnings"))

    def test_uniform_timing_is_a_review_not_a_hard_rule(self):
        data = example("artvision_cinema")
        data["video_duration_s"] = 12
        data["shots"] = [
            dict(data["shots"][0], id=str(i), start_s=i*3, end_s=(i+1)*3,
                 composition_group=str(i)) for i in range(4)
        ]
        result = regia.inspect(data)
        self.assertIn("UNIFORM_TIMING", self.codes(result, "warnings"))
        self.assertEqual(result["blocking"], [])

    def test_long_static_detail_requests_real_review(self):
        data = example("artvision_cinema")
        data["video_duration_s"] = 15
        data["shots"] = [dict(data["shots"][1], start_s=0, end_s=15,
                             camera={"move":"locked"})]
        result = regia.inspect(data)
        self.assertIn("VISUAL_STALL", self.codes(result, "warnings"))
        self.assertEqual(result["blocking"], [])

    def test_invalid_schema_and_boolean_numbers(self):
        self.assertEqual(regia.inspect({})["status"], "blocked_plan")
        data = example()
        data["video_duration_s"] = True
        self.assertIn("INVALID_TIMELINE", self.codes(regia.inspect(data)))

    def test_different_series_do_not_force_narration(self):
        for fmt in ("storia_rivive", "artvision_cinema", "wow_lab", "visual_music"):
            data = example(fmt)
            data["narration"] = {}
            self.assertNotIn("SPEECH_TIMECODES_UNVERIFIED", self.codes(regia.inspect(data)),
                             msg=fmt)


if __name__ == "__main__":
    unittest.main()
