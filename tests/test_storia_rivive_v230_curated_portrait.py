"""V230: source SHA/geometry/consent preflight; all offline and no paid calls."""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import storia_rivive_v230_curated_portrait as m
ROOT = Path(__file__).resolve().parents[1]


class SourceLockedPortraitTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / "config/storia_rivive_v230_source_crops.json").read_text())

    def test_curated_five_crops_are_non_authorizing_and_unique(self):
        cfg=self.config
        self.assertFalse(cfg["credit_spend_allowed"])
        self.assertFalse(cfg["publish_allowed"])
        self.assertFalse(cfg["italian_rights_approved"])
        entry=cfg["sources"][0]
        self.assertEqual(entry["episode_id"], "early_cinema_sorrows_1910_v225")
        self.assertEqual([x["filename"] for x in entry["frames"]],
                         ["frame_%02d.png" % i for i in range(8,13)])
        self.assertEqual(len({x["left_px"] for x in entry["frames"]}), 5)

    def fixture(self, root):
        cfg=copy.deepcopy(self.config)
        film=root / "ORIGINAL_ARCHIVE.webm"
        film.write_bytes(b"synthetic mock film for SHA tests only")
        frames=root / "original_frames"
        frames.mkdir()
        for i, row in enumerate(cfg["sources"][0]["frames"]):
            path=frames / row["filename"]
            Image.new("RGB", (1280,720), (20*i,60+i,100)).save(path)
            row["source_frame_sha256"]=m.digest(path)
        cfg["sources"][0]["original_sha256"]=m.digest(film)
        scout={"status":"REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW",
               "original_sha256":m.digest(film),"duration_s":500}
        sel={"status":m.READY,
             "preselected":[{"filename":x["filename"]} for x in cfg["sources"][0]["frames"]],
             "candidate_segment_times_s":[262.5,297.5,332.5,367.5,402.5]}
        return cfg,sel,scout

    def test_source_file_changes_or_unapproved_flags_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            cfg,sel,scout=self.fixture(root)
            self.assertEqual(m.validate(cfg,sel,scout,root,"early_cinema_sorrows_1910_v225")["episode_id"],
                             "early_cinema_sorrows_1910_v225")
            self.assertIsNone(m.validate(cfg,sel,scout,root,"other_episode"))
            altered=copy.deepcopy(cfg)
            altered["sources"][0]["frames"][0]["left_px"]=1200
            with self.assertRaisesRegex(ValueError,"BOUNDS"):
                m.validate(altered,sel,scout,root,"early_cinema_sorrows_1910_v225")
            altered=copy.deepcopy(cfg)
            altered["sources"][0]["frames"][2]["source_frame_sha256"]="0"*64
            with self.assertRaisesRegex(ValueError,"SHA_CHANGED"):
                m.validate(altered,sel,scout,root,"early_cinema_sorrows_1910_v225")
            altered=copy.deepcopy(cfg)
            altered["credit_spend_allowed"]=True
            with self.assertRaisesRegex(ValueError,"UNSAFE"):
                m.validate(altered,sel,scout,root,"early_cinema_sorrows_1910_v225")
            (root / "ORIGINAL_ARCHIVE.webm").write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError,"FILM_HASH_MISMATCH"):
                m.validate(cfg,sel,scout,root,"early_cinema_sorrows_1910_v225")


if __name__ == "__main__":
    unittest.main()
