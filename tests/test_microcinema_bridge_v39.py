"""Extra V39 integration tests: opt-in semantics and real scene duration."""
import json
import tempfile
import unittest
from pathlib import Path
import sys

import cv2
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from microcinema_book_bridge_v39 import config_for_cue, make_insert


class MicrocinemaBridgeV39Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        yy, xx = np.mgrid[0:360, 0:202]
        im = np.stack([xx*255//202, yy*255//360, (xx+yy)%255], axis=-1).astype(np.uint8)
        self.source = self.dir / "source.jpg"
        cv2.imwrite(str(self.source), im)
        self.plan = self.dir / "effetti_v4.json"

    def set_plan(self, effect="slow_push", seconds=5, effect_v4="cinematic_pan", postfx=None):
        self.plan.write_text(json.dumps({"scenes": [
            {"cue":1, "effect":effect_v4, "postfx":postfx, "microcinema":{
                "effect":effect, "seconds":seconds,
                "reason":"La porta al centro della storia viene lentamente rivelata."}}
        ]}), encoding="utf-8")

    def test_absent_is_noop(self):
        self.assertIsNone(config_for_cue(self.dir/"absent.json", 1))
        self.set_plan()
        self.assertIsNone(config_for_cue(self.plan, 0))

    def test_real_mp4_preserves_scene_length(self):
        self.set_plan()
        output, manifest = make_insert(self.source, 1, 7*12, 12, 320, 568, self.dir, self.plan)
        self.assertTrue(output.is_file())
        self.assertEqual(manifest["micro_seconds"],5)
        self.assertEqual(manifest["hold_last_frame_seconds"],2)
        cap = cv2.VideoCapture(str(output))
        self.assertEqual(round(cap.get(cv2.CAP_PROP_FRAME_COUNT)),84)
        cap.release()
        self.assertTrue(manifest["review_required"])

    def test_fail_if_voice_shot_shorter_than_clip(self):
        self.set_plan(seconds=9)
        with self.assertRaisesRegex(ValueError,"insufficiente"):
            make_insert(self.source,1,6*12,12,320,568,self.dir,self.plan)

    def test_no_unreviewed_depth_or_stacking(self):
        self.set_plan(effect="depth_layers")
        with self.assertRaisesRegex(ValueError,"depth_layers"):
            config_for_cue(self.plan,1)
        self.set_plan(effect_v4="sketch_paint")
        with self.assertRaisesRegex(ValueError,"sovrapposto"):
            config_for_cue(self.plan,1)
        self.set_plan(postfx="vintage_grain")
        with self.assertRaisesRegex(ValueError,"sovrapposto"):
            config_for_cue(self.plan,1)


if __name__ == "__main__":
    unittest.main()
