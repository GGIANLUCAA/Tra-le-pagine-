"""V38: creativity checks are evidence and warnings, not scene-count templates."""
import unittest

from src.narrative_variation_v38 import inspect
from src.editorial_rules import new_plan


def scene(asset, desc, reason, camera=None, **kwargs):
    value = {"asset_id": asset, "description": desc, "reason": reason}
    if camera is not None:
        value["camera"] = camera
    value.update(kwargs)
    return value


class NarrativeVariationV38Tests(unittest.TestCase):

    def project(self, scenes):
        plan = new_plan()
        plan["narrative_design"].update(
            story_beats=["opening", "action", "outcome"],
            distinct_visual_needs=["location", "action", "gesture"],
            image_count_reason="Three distinct narrative needs",
            pace_reason="Speech and emotional changes",
        )
        return {"editorial_contract": {"requested_format": "libri"},
                "format": "libri", "editorial_plan": plan, "scenes": scenes}

    def test_quiet_episode_with_one_image_is_not_rejected(self):
        p = self.project([scene("single", "Quiet landscape", "A meaningful pause", "still")])
        result = inspect(p)
        self.assertFalse(result["needs_creative_review"])
        self.assertEqual(result["distinct_visual_asset_ids_observed"], 1)
        self.assertFalse(result["automatic_artistic_approval"])

    def test_adventure_episode_can_use_many_distinct_visuals(self):
        shots = [scene("a"+str(i), "Event "+str(i), "Shows distinct action "+str(i),
                       "camera "+str(i)) for i in range(27)]
        result = inspect(self.project(shots))
        self.assertEqual(result["scene_count_observed"], 27)
        self.assertFalse(result["needs_creative_review"])
        self.assertFalse(result["hardcoded_target_duration_or_image_count"])

    def test_clone_shots_raised_as_review_not_blocker(self):
        shots = [scene("same", "Door", "Reveal the door"),
                 scene("same", "Door", "Reveal the door")]
        result = inspect(self.project(shots))
        self.assertTrue(result["needs_creative_review"])
        self.assertEqual(result["finding_counts"]["DUPLICATE_SHOT_WITHOUT_REASON"], 1)
        self.assertEqual(result["findings"][0]["scenes"], [1, 2])
        self.assertTrue(all(f["level"] == "review" for f in result["findings"]))

    def test_intentional_return_to_same_visual_is_allowed(self):
        shots = [scene("a", "Door", "Reveal the door"),
                 scene("a", "Door", "Reveal the door",
                       reuse_reason="Return to the same door after the character decides")]
        result = inspect(self.project(shots))
        self.assertNotIn("DUPLICATE_SHOT_WITHOUT_REASON", result["finding_counts"])

    def test_same_camera_three_times_warns_only_when_unexplained(self):
        p = self.project([scene("a", "Opening", "First beat", "slow_zoom"),
                          scene("b", "The journey", "Second beat", "slow_zoom"),
                          scene("c", "The revelation", "Final beat", "slow_zoom")])
        self.assertIn("REPEATED_CAMERA_UNEXPLAINED", inspect(p)["finding_counts"])
        for x in p["scenes"]:
            x["camera_reason"] = "Motivated steady visual language"
        self.assertNotIn("REPEATED_CAMERA_UNEXPLAINED", inspect(p)["finding_counts"])

    def test_v38_motivation_is_checked_without_number_target(self):
        p = self.project([scene("a", "First", "Story one"),
                          scene("b", "Second", "Story two")])
        p["editorial_plan"]["narrative_design"].update(
            image_count_reason="", pace_reason="")
        result = inspect(p)
        self.assertIn("VISUAL_COUNT_NOT_MOTIVATED", result["finding_counts"])
        self.assertIn("RHYTHM_NOT_MOTIVATED", result["finding_counts"])
        self.assertFalse(result["hardcoded_target_duration_or_image_count"])

    def test_legacy_recipe_does_not_become_automatically_blocked(self):
        result = inspect({"format": "libri", "scenes": [
            scene("old", "Archive illustration", "Historical scene")]})
        self.assertFalse(result["needs_creative_review"])

    def test_malformed_editorial_plan_never_crashes_a_creative_review(self):
        p = {"editorial_contract": {"requested_format": "libri"},
             "editorial_plan": "invalid legacy data",
             "scenes": [scene("a", "Still life", "Atmosphere")]}
        result = inspect(p)
        self.assertIn("V38_PLAN_MISSING", result["finding_counts"])

    def test_reference_is_not_master_approval(self):
        p = self.project([scene("x", "Scene", "Reason")])
        p["editorial_plan"]["narrative_design"].update(
            reference_id="time_machine_20261026",
            do_not_copy_reference_parameters=False)
        self.assertIn("REFERENCE_TEMPLATE_RISK", inspect(p)["finding_counts"])


if __name__ == "__main__":
    unittest.main()
