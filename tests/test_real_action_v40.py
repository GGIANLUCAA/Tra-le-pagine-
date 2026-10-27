"""V40 tests: live motion, safe assets, no fake action from static video."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from real_action_v40 import inspect_action, produce, validate_spec


def make_source(path, moving=True):
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), 24, (320, 568))
    if not writer.isOpened():
        raise RuntimeError("Cannot create local test MP4")
    yy, xx = np.mgrid[:568, :320]
    bg = np.stack([(xx+yy)%160+35, (xx*2+yy)%170+35,
                   (yy*2+xx)%155+35], axis=-1).astype(np.uint8)
    for k in range(24*6):
        img = bg.copy()
        # Moving textured physical region over a fixed background: action.
        x = 30 + (k // 2)%170 if moving else 30
        y = 220
        cv2.rectangle(img, (x,y), (x+88,y+100), (12, 8, 190), -1)
        cv2.circle(img, (x+44,y+50), 28, (235,235,235), -1)
        cv2.line(img, (x+10,y+20), (x+85,y+90), (8,20,45), 7)
        writer.write(img)
    writer.release()


class RealActionV40(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/"episodes"/"test_episode"
        self.root.mkdir(parents=True)
        self.video = self.root/"moving.mp4"
        self.spec = {
            "provider": "own", "license": "own", "source_url": "",
            "rights_reviewed": True, "visual_reviewed": True,
            "scene_action": "Ingranaggi realmente in movimento",
            "narrative_reason": "Il protagonista avvia il meccanismo",
            "narration_anchor": "Quando aziona la macchina del tempo",
            "seconds": 5,
        }

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),
                         "FFmpeg required")
    def test_real_action_passes_transcode(self):
        make_source(self.video, True)
        result = produce(self.video, self.root/"output.mp4", self.spec, self.root,
                         fps=24, width=320, height=568)
        self.assertEqual(result["status"], "rendered_needs_review")
        self.assertTrue(result["original_footage_has_action"]["median_frame_change"] > 0.20)
        self.assertTrue((self.root/"output.json").is_file())
        self.assertEqual(result["duration"], 5.0)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),
                         "FFmpeg required")
    def test_static_rejected(self):
        make_source(self.video, False)
        with self.assertRaisesRegex(ValueError, "sembra ferma"):
            produce(self.video, self.root/"output.mp4", self.spec, self.root,
                    fps=24, width=320, height=568)

    def test_rights_and_human_review_required(self):
        self.video.write_bytes(b"file")
        for key in ("rights_reviewed", "visual_reviewed"):
            self.spec[key] = False
            with self.assertRaisesRegex(ValueError, "revisionati"):
                validate_spec(self.spec, self.video, self.root)
            self.spec[key] = True

    def test_forbid_external_paths_and_overlong_clip(self):
        self.video.write_bytes(b"file")
        other = Path(self.tmp.name)/"outside.mp4"
        other.write_bytes(b"file")
        with self.assertRaisesRegex(ValueError, "cartella dell'episodio"):
            validate_spec(self.spec, other, self.root)
        self.spec["seconds"] = 11
        with self.assertRaisesRegex(ValueError, "5 a 10"):
            validate_spec(self.spec, self.video, self.root)


if __name__ == "__main__":
    unittest.main()
