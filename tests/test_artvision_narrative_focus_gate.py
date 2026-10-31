"""Offline regression tests for ArtVision speech/visible-subject QA."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from artvision_narrative_focus_gate import analyze


def fixture():
    h = "a" * 64
    segments = [
        {"id": "face", "start_s": 0, "end_s": 4,
         "speech": "Il volto mostra una lieve tensione.",
         "subject_id": "main_face", "subject_bbox_xyxy": [.10, .10, .30, .30]},
        {"id": "hand", "start_s": 4, "end_s": 8,
         "speech": "La mano indica il cielo.",
         "subject_id": "raised_hand", "subject_bbox_xyxy": [.55, .30, .70, .50]},
    ]
    shots = [
        {"segment_id": "face", "start_s": .8, "end_s": 5.2,
         "camera_crop_xyxy": [.05, .05, .45, .45]},
        {"segment_id": "hand", "start_s": 4.8, "end_s": 9.2,
         "camera_crop_xyxy": [.48, .25, .80, .60]},
    ]
    return {
        "schema": "artvision-narrative-focus-v1",
        "artwork_id": "example-not-a-production",
        "shared_voice": {"wav_sha256": h, "duration_s": 8,
                         "timing_method": "verified_asr"},
        "segments": segments,
        "variants": {
            k: {"wav_sha256": h, "voice_offset_s": 1, "video_duration_s": 10,
                "shots": copy.deepcopy(shots)}
            for k in ("critico_standard", "critico_museum")
        }
    }


class NarrativeFocusTests(unittest.TestCase):
    def test_valid_plan_not_artistically_approved(self):
        report = analyze(fixture())
        self.assertEqual(report["status"], "plan_checks_passed")
        self.assertFalse(report["certifies_visual_semantics"])
        self.assertFalse(report["v25_approved"])

    def test_incorrect_subject_is_cropped(self):
        data = fixture()
        data["variants"]["critico_museum"]["shots"][1]["camera_crop_xyxy"] = [.1, .1, .3, .3]
        codes = [x["code"] for x in analyze(data)["errors"]]
        self.assertIn("SPOKEN_SUBJECT_CROPPED", codes)

    def test_bad_timing_creates_repair_proposal_without_mutating_input(self):
        data = fixture()
        shot = data["variants"]["critico_standard"]["shots"][0]
        shot["start_s"] = 3
        before = copy.deepcopy(data)
        report = analyze(data)
        self.assertEqual(report["status"], "blocked")
        self.assertIn("PHRASE_NOT_VISIBLE_FOR_FULL_MEANING",
                      [x["code"] for x in report["errors"]])
        self.assertTrue(report["repair_proposals"])
        self.assertEqual(data, before)

    def test_museum_and_standard_need_exact_same_wav(self):
        data = fixture()
        data["variants"]["critico_museum"]["wav_sha256"] = "b" * 64
        self.assertIn("CRITICO_WAV_MISMATCH",
                      [x["code"] for x in analyze(data)["errors"]])

    def test_plausible_but_unverified_timing_is_not_accepted(self):
        data = fixture()
        data["shared_voice"]["timing_method"] = "estimated_by_length"
        self.assertIn("VOICE_TIMING_UNVERIFIED",
                      [x["code"] for x in analyze(data)["errors"]])

    def test_final_cannot_pass_without_real_rendered_mp4(self):
        report = analyze(fixture(), phase="final")
        self.assertEqual(report["status"], "blocked")
        self.assertIn("MISSING_RENDERED_MP4_PATH",
                      [x["code"] for x in report["errors"]])
        self.assertFalse(report["v25_approved"])


if __name__ == "__main__":
    unittest.main()
