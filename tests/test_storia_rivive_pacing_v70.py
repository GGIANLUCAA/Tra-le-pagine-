import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("storia_v70", ROOT / "src/storia_rivive_pacing_v70.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def sample(n=8):
    types = ["face", "action", "wide", "detail", "climax", "action",
             "face", "wide", "detail", "action", "climax", "face",
             "wide", "action", "detail"]
    return {"shots": [{
        "scene_type": types[i],
        "emotional_value": [5,4,3,4,5][i%5],
        "visual_complexity": [3,4,5,3,5][i%5],
        "motion_value": 3, "image_quality": 4,
        "unique_event_id": f"event-{i}",
        "composition_group": types[i],
        "narrative_role": "hook" if i == 0 else "development",
        "visual_evidence": f"At {i*8+5}s frame shows distinct authentic human gesture",
        "source_frame_timecode_s": i*8 + 5.,
        "source_visually_reviewed": True,
        "safe_crop_reviewed": True,
        "source_rights_verified": True,
    } for i in range(n)]}


class TestAdaptiveHistoricalPacingV70(unittest.TestCase):
    def test_different_lengths_without_fixed_25(self):
        totals = []
        for n in (4,5,8,10,12):
            p = mod.plan(sample(n))
            failures, _ = mod.check(p)
            self.assertEqual(failures, [], f"{n} scenes: {failures}")
            t = mod.duration(p["shots"])
            self.assertGreaterEqual(t, 14)
            self.assertLessEqual(t, 35)
            self.assertEqual(p["pacing_v70"]["status"], "TIMING_PLANNED_NOT_VIDEO_QA")
            totals.append(t)
            for shot in p["shots"]:
                self.assertAlmostEqual(shot["start_s"] + (max(1, round(shot["motion_s"] * 30)) - 1) / 30,
                                       shot["source_frame_timecode_s"])
        self.assertGreater(len(set(totals)), 3)

    def test_reject_unreviewed_visual(self):
        p = sample()
        p["shots"][0]["source_visually_reviewed"] = False
        with self.assertRaises(ValueError):
            mod.plan(p)

    def test_reject_duplicate_historical_event(self):
        p = sample()
        p["shots"][1]["unique_event_id"] = p["shots"][0]["unique_event_id"]
        with self.assertRaises(ValueError):
            mod.plan(p)

    def test_prune_three_same_compositions(self):
        p = sample()
        for k in (2,3,4):
            p["shots"][k]["composition_group"] = "same_street"
        result = mod.plan(p)
        self.assertGreaterEqual(len(result["pacing_v70"]["rejected_candidate_event_ids"]),1)
        self.assertFalse(mod.check(result)[0])

    def test_detect_changed_freeze_and_repetitions(self):
        a = mod.plan(sample())
        a["shots"][0]["start_s"] += .5
        self.assertTrue(any("freeze" in e for e in mod.check(a)[0]))
        b = mod.plan(sample())
        b["shots"][1]["composition_group"] = b["shots"][0]["composition_group"]
        b["shots"][2]["composition_group"] = b["shots"][0]["composition_group"]
        self.assertTrue(any("composizioni" in e for e in mod.check(b)[0]))

    def test_dont_pad_three_weak_clips_to_fourteen(self):
        with self.assertRaises(ValueError):
            mod.plan(sample(3))


if __name__ == "__main__":
    unittest.main()
