import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from artvision_recipe_v68 import (
    VARIANTS,build_recipe,change_creative,inspect,load_preset,write_new
)

class ArtVisionReusableFourVariantsV68Tests(unittest.TestCase):
    def setUp(self):
        self.new=build_recipe("test-work-123","Painting ABC","Artist XYZ",
                              "https://example.org/artwork")
        self.preset=load_preset()

    def test_four_original_slots_and_real_voice_invariants(self):
        self.assertEqual(tuple(self.new["variants"]),VARIANTS)
        inv=self.new["invariants"]
        self.assertTrue(inv["shared_critico_script_and_exact_wav_sha256"])
        self.assertTrue(inv["museum_entry_exit_continuous_camera"])
        self.assertTrue(inv["no_cropped_foreground_people"])
        self.assertTrue(inv["no_voice_in_cinema"])
        self.assertTrue(inv["zero_paid_video_ai_without_per_scene_consent"])
        self.assertFalse(self.new["production"]["render_eligible"])
        self.assertEqual(inspect(self.new),[])

    def test_per_work_customization_keeps_original_preset_and_unrelated_recipe(self):
        unmodified=copy.deepcopy(self.new)
        updated=change_creative(self.new,"slots.cinema_museum.target_seconds",
                                "62","Please make this museum cinema longer")
        self.assertEqual(updated["creative"]["slots"]["cinema_museum"]["target_seconds"],62)
        self.assertEqual(self.new,unmodified)
        self.assertEqual(self.preset["defaults"]["slots"]["cinema_museum"]["target_seconds"],40)
        self.assertEqual(updated["change_log"][0]["requested_scope"],"THIS_ARTWORK_ONLY")
        self.assertEqual(inspect(updated),[])

    def test_more_centered_and_critic_script_length_controls(self):
        b=change_creative(self.new,"slots.critico_standard.camera_center_x",
                          "0.55","Keep Socrates closer to center of the view")
        c=change_creative(b,"critico_pair.target_words",
                          "540","Give a more detailed critical analysis")
        self.assertAlmostEqual(c["creative"]["slots"]["critico_standard"]["camera_center_x"],.55)
        self.assertEqual(c["creative"]["critico_pair"]["target_words"],540)
        self.assertEqual(c["creative"]["critico_pair"]["narration_duration_policy"],
                         "from_verified_WAV_not_fixed")
        self.assertEqual(inspect(c),[])

    def test_alternate_frame_must_be_openly_labeled_creative(self):
        with self.assertRaisesRegex(ValueError,"declared_creative_alternative"):
            change_creative(self.new,"museum.frame_finish","dark_wood",
                            "Use a deliberately darker frame instead")
        b=change_creative(self.new,"museum.frame_mode",
                          "declared_creative_alternative",
                          "I want an alternate artistic frame not a museum replica")
        c=change_creative(b,"museum.frame_finish","dark_wood",
                          "Use darker wood only as a declared creative recreation")
        self.assertEqual(inspect(c),[])
        self.assertTrue(c["creative"]["museum"]["room_reconstruction_disclosure_required"])

    def test_immutable_safety_rules_and_unknown_fields_are_rejected(self):
        with self.assertRaisesRegex(ValueError,"Immutable or unknown"):
            change_creative(self.new,"invariants.critico_voice","Other",
                            "Try a different voice for some reason")
        with self.assertRaisesRegex(ValueError,"Value outside safe range"):
            change_creative(self.new,"museum.safe_margin_percent","2",
                            "Tighter frame with unsafe person cropping")
        with self.assertRaisesRegex(ValueError,"Expected integer"):
            change_creative(self.new,"slots.cinema_standard.target_seconds","forty",
                            "Make it shorter or longer as requested")

    def test_duplicate_mp4_across_slots_rejected(self):
        a=self.new["variants"]["cinema_standard"]
        b=self.new["variants"]["cinema_museum"]
        for x in (a,b):
            x.update(status="rendered_needs_review",mp4_sha256="a"*64,mp4_bytes=5000000)
        self.assertTrue(any("SAME MP4 hash" in e for e in inspect(self.new)))

    def test_two_critico_have_to_reuse_exact_verified_voice(self):
        for v in ("critico_standard","critico_museum"):
            self.new["variants"][v].update(status="rendered_needs_review",
                   mp4_sha256=("b" if v=="critico_standard" else "c")*64,
                   mp4_bytes=3000000,
                   voice_script_sha256="d"*64,
                   source_voice_sha256=("e" if v=="critico_standard" else "f")*64)
        self.assertTrue(any("same verified voice" in e for e in inspect(self.new)))
        self.new["variants"]["critico_museum"]["source_voice_sha256"]="e"*64
        self.assertEqual(inspect(self.new),[])

    def test_no_false_human_approval(self):
        self.new["variants"]["cinema_standard"]["V25_approved"]=True
        self.assertTrue(any("full-speed QA" in e for e in inspect(self.new)))

    def test_existing_pilot_lock_blocks_new_artworks_for_render(self):
        warnings=inspect(self.new,root=ROOT,require_render=True)
        self.assertTrue(any("PILOT LOCK" in s for s in warnings))
        self.assertTrue(any("Missing verified" in s for s in warnings))

    def test_immutable_output_file_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"recipe.json"
            write_new(p,self.new)
            self.assertTrue(p.is_file())
            with self.assertRaises(FileExistsError):
                write_new(p,self.new)

if __name__=="__main__":
    unittest.main()
