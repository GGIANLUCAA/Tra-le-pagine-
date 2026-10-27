"""V44 regression tests: no paid API, no files uploaded, fail closed."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SRC = Path(__file__).resolve().parents[1] / "src" / "animated_video_release_gate_v44.py"
spec = importlib.util.spec_from_file_location("release_v44", SRC)
v44 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v44)


class AnimatedVideoReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.o = root / "original.mp4"
        self.c = root / "candidate.mp4"
        self.clip = root / "motion.mp4"
        self.o.write_bytes(b"ORIGINAL" * 60)
        self.c.write_bytes(b"DIFFERENT CANDIDATE" * 60)
        self.clip.write_bytes(b"ANIMATED BY LOCAL WARP" * 60)
        self.d = v44.draft(self.o, self.c, self.clip,
                           "generative_i2v", "L'uomo tira una leva.",
                           "The man physically pulls the lever and the machine starts")

    def reviews_passed_but_generated_from_local_warp(self):
        self.d["status"] = "approved_for_final_delivery"
        self.d["scene"]["time_start_seconds"] = 10.9
        self.d["scene"]["time_end_seconds"] = 13.9
        for key in v44.CHECKS:
            self.d["reviews"][key] = {
                "passed": True, "evidence": "Observed test evidence of real-time review for " + key
            }
        self.d["reviewer"] = {
            "kind": "human_editor", "name": "Example QA", "decision": "approved",
            "reason": "Reviewed full candidate against original with synchronized spoken words.",
            "reviewed_video_sha256": self.d["candidate"]["sha256"],
        }

    def test_draft_is_unapproved_even_if_mp4_exists(self):
        errors = v44.check(self.d, self.o, self.c, self.clip)
        self.assertTrue(any("non e approvato" in e for e in errors))
        self.assertTrue(any("Revisione artistica" in e for e in errors))
        self.assertTrue(any("generazione I2V reale" in e for e in errors))

    def test_local_motion_never_qualifies_as_real_i2v(self):
        self.reviews_passed_but_generated_from_local_warp()
        self.d["provenance"] = {
            "kind": "local_motion", "provider": "opencv",
            "task_id": "", "source_image_sha256": "", "approval_fingerprint": "",
        }
        errors = v44.check(self.d, self.o, self.c, self.clip, "generative_i2v")
        self.assertTrue(any("NON e generazione I2V reale" in e for e in errors))

    def test_changing_final_video_invalidates_previous_review(self):
        self.reviews_passed_but_generated_from_local_warp()
        self.d["provenance"] = {
            "kind": "provider_i2v", "provider": "vidu",
            "task_id": "V42-task", "source_image_sha256": "aa" * 32,
            "approval_fingerprint": "bb" * 32,
        }
        self.assertEqual(v44.check(self.d, self.o, self.c, self.clip), [])
        self.c.write_bytes(b"REPLACED NOT REVIEWED" * 50)
        errors = v44.check(self.d, self.o, self.c, self.clip)
        self.assertTrue(any("SHA-256 diverso" in e for e in errors))

    def test_machine_deformation_without_action_must_be_rejected(self):
        self.reviews_passed_but_generated_from_local_warp()
        self.d["provenance"] = {
            "kind": "provider_i2v", "provider": "vidu",
            "task_id": "123", "source_image_sha256": "aa" * 32,
            "approval_fingerprint": "bb" * 32,
        }
        self.d["reviews"]["requested_action_actually_visible"] = {
            "passed": False,
            "evidence": "Observed that the actor's arm and lever stay static in this test.",
        }
        errors = v44.check(self.d, self.o, self.c, self.clip)
        self.assertTrue(any("requested_action_actually_visible" in e for e in errors))

    def test_empty_generic_self_review_never_qualifies(self):
        self.reviews_passed_but_generated_from_local_warp()
        self.d["provenance"] = {
            "kind": "provider_i2v", "provider": "vidu", "task_id": "123",
            "source_image_sha256": "aa" * 32, "approval_fingerprint": "bb" * 32,
        }
        self.d["reviews"]["no_warped_gears_or_artifacts"]["evidence"] = "ok"
        self.d["reviewer"]["kind"] = "automated"
        errors = v44.check(self.d, self.o, self.c, self.clip)
        self.assertTrue(any("no_warped_gears_or_artifacts" in e for e in errors))
        self.assertTrue(any("revisore reale" in e for e in errors))

    def test_original_and_candidate_identical_is_blocked(self):
        self.reviews_passed_but_generated_from_local_warp()
        self.d["provenance"] = {
            "kind": "provider_i2v", "provider": "vidu", "task_id": "123",
            "source_image_sha256": "aa" * 32, "approval_fingerprint": "bb" * 32,
        }
        self.c.write_bytes(self.o.read_bytes())
        self.d["candidate"]["sha256"] = v44.sha256(self.c)
        self.d["reviewer"]["reviewed_video_sha256"] = self.d["candidate"]["sha256"]
        errors = v44.check(self.d, self.o, self.c, self.clip)
        self.assertTrue(any("Filmato invariato" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
