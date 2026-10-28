"""Offline user-path tests. No API calls or publishing."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from video_director_v13 import brief, check, capture, digest, get_format, read_json, write_json


class VideoDirectorTests(unittest.TestCase):
    def ready_project(self, folder):
        folder = Path(folder)
        p = brief("libri", "Un racconto", folder)
        from test_editorial_rules import completed_plan
        p["editorial_plan"] = completed_plan()
        p["editorial_plan"]["techniques"][0]["id"] = "book_v12_scene"
        (folder / "story.txt").write_text("Anna apre la porta. Poi torna al mare.", encoding="utf-8")
        from PIL import Image
        Image.new("RGB", (100, 100), "blue").save(folder / "scene.jpg")
        p["script"] = "story.txt"
        p["editorial_plan"]["media_sourcing"] = {
            "policy_id": "media-priority-v33", "review_status": "reviewed",
            "decisions": [{"asset_id": "one", "source_kind": "user_supplied",
                           "provider": "test_fixture", "source_reference": "local-test-file-scene.jpg",
                           "choice_reason": "Original test image matching the test scene",
                           "scene_match_note": "Fixture: Anna on the threshold",
                           "rights_review": "reviewed", "scene_relevance": "reviewed",
                           "visual_review": "passed"}]
        }
        p["assets"] = [{"id": "one", "file": "scene.jpg", "role": "visual", "source": "Originale di prova",
                        "rights": "Proprio", "sha256": digest(folder / "scene.jpg")}]
        p["scenes"] = [{"asset_id": "one", "description": "Anna sulla soglia", "reason": "Apertura della vicenda",
                        "narration_anchor": "Anna apre la porta."}]
        p["reviews"] = {key: {"status": "passed", "notes": "Revisione simulata per test"}
                        for key in ("story", "visuals", "rights")}
        write_json(folder / "PROJECT_V13.json", p)
        return p

    def test_brief_routes_to_approved_cinema_not_legacy(self):
        with tempfile.TemporaryDirectory() as d:
            p = brief("artvision_cinema", "Caravaggio", d)
            self.assertEqual(p["preset"], "cinema_v6")
            self.assertEqual(p["status"], "planned")
            self.assertFalse(check(Path(d) / "PROJECT_V13.json")["ready"])
            self.assertIn("Van Gogh", (Path(d) / "BRIEF_GPT.md").read_text())
            with self.assertRaises(ValueError):
                brief("libri", "Do not replace", d)

    def test_registry_paths_exist_and_critico_uses_new_cover(self):
        for fmt in read_json(ROOT / "config/video_formats_v13.json")["formats"].values():
            for name in fmt["guides"] + fmt["entrypoints"]:
                self.assertTrue((ROOT / name).is_file(), name)
        self.assertEqual(get_format("artvision_critico")["preset"], "critico-series-v2")

    def test_missing_generators_are_not_claimed_ready(self):
        for kind in ("controluce", "visual_music", "hyperlumen"):
            with tempfile.TemporaryDirectory() as d:
                brief(kind, "Nuovo video", d)
                result = check(Path(d) / "PROJECT_V13.json")
                self.assertFalse(result["ready"])
                self.assertTrue(any("Sorgenti da recuperare" in x for x in result["blockers"]))

    def test_valid_project_then_modified_asset_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            self.ready_project(d)
            file = Path(d) / "PROJECT_V13.json"
            self.assertTrue(check(file)["ready"])
            self.assertFalse(check(file)["semantic_accuracy_certified"])
            (Path(d) / "scene.jpg").write_bytes(b"different content")
            self.assertFalse(check(file)["ready"])

    def test_v38_creative_review_detects_cloned_scenes_without_scene_quota(self):
        with tempfile.TemporaryDirectory() as d:
            p = self.ready_project(d)
            p["editorial_plan"]["narrative_design"].update(
                story_beats=["Opening", "Return"],
                distinct_visual_needs=["The door", "The consequence"],
                image_count_reason="Two distinct narrative moments",
                pace_reason="Contrast between the opening and the outcome")
            p["scenes"].append({
                "asset_id": "one", "description": "Anna sulla soglia",
                "reason": "Apertura della vicenda",
                "narration_anchor": "Poi torna al mare."
            })
            write_json(Path(d) / "PROJECT_V13.json", p)
            result = check(Path(d) / "PROJECT_V13.json")
            self.assertTrue(result["ready"], "V38 is advice, not another render blocker")
            self.assertTrue(result["creative_review"]["needs_creative_review"])
            self.assertTrue(any("DUPLICATE_SHOT_WITHOUT_REASON" in x for x in result["warnings"]))
            # Creative correction is an explicit motivation, not a fabricated new image.
            p["scenes"][1]["reuse_reason"] = "Returning to a remembered visual motif is intentional"
            write_json(Path(d) / "PROJECT_V13.json", p)
            checked = check(Path(d) / "PROJECT_V13.json")
            self.assertFalse(checked["creative_review"]["needs_creative_review"])

    def test_outside_paths_and_wrong_anchor_are_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            p = self.ready_project(d)
            p["assets"][0]["file"] = "../external.jpg"
            p["scenes"][0]["narration_anchor"] = "Una frase inventata."
            write_json(Path(d) / "PROJECT_V13.json", p)
            result = check(Path(d) / "PROJECT_V13.json")
            self.assertTrue(any("fuori" in b for b in result["blockers"]))
            self.assertTrue(any("frase" in b for b in result["blockers"]))

    def test_subtitle_change_and_unreviewed_story_block(self):
        with tempfile.TemporaryDirectory() as d:
            p = self.ready_project(d)
            p["subtitles"] = True
            p["reviews"]["story"] = {"status": "passed", "notes": ""}
            write_json(Path(d) / "PROJECT_V13.json", p)
            result = check(Path(d) / "PROJECT_V13.json")
            self.assertTrue(any("sottotitoli" in b for b in result["blockers"]))
            self.assertTrue(any("story" in b for b in result["blockers"]))

    def test_real_video_capture_has_hashes_sources_and_measured_resolution(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            video, cover = root / "film.mp4", root / "cover.jpg"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=blue:s=180x320:r=12:d=1",
                            "-f", "lavfi", "-i", "sine=frequency=440:duration=1", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-shortest", str(video)], check=True)
            Image.new("RGB", (180, 320), "blue").save(cover)
            source = root / "script.txt"; source.write_text("Copione originale")
            out = root / "delivery"
            result = capture("libri", "Test", video, cover, out, [source])
            self.assertEqual(result["technical"]["width"], 180)
            self.assertEqual(result["video"]["sha256"], digest(video))
            self.assertEqual(result["status"], "rendered_needs_review")
            for item in [result["video"], result["cover"]] + result["sources"]:
                self.assertEqual(digest(out / item["file"]), item["sha256"])
            b = brief("libri", "Next", root / "next", [out / "VIDEO_RECIPE_V13.json"])
            self.assertEqual(len(b["references"]), 1)
            self.assertFalse((root / "next" / "VOCE.wav").exists())

    def test_four_brief_cli_requires_real_emotional_plan_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "ARTVISION_4X1_PLAN.json"
            args = [sys.executable, str(ROOT / "src/video_director_v13.py"),
                    "four-brief", "--topic", "The Goldfinch", "--artist",
                    "Carel Fabritius", "--out", str(target)]
            self.assertEqual(subprocess.run(args, capture_output=True).returncode, 0)
            plan = read_json(target)
            self.assertEqual(len(plan["variants"]), 4)
            self.assertFalse(plan["approval"]["user_approval"])
            check_args = [sys.executable, str(ROOT / "src/video_director_v13.py"),
                          "four-check", "--plan", str(target)]
            self.assertEqual(subprocess.run(check_args, capture_output=True).returncode, 2)
            self.assertNotEqual(subprocess.run(args, capture_output=True).returncode, 0)

    def test_serial_artvision_project_blocks_unchecked_group(self):
        with tempfile.TemporaryDirectory() as d:
            from artvision_four_variants_gate import new_plan
            folder = Path(d) / "art"
            p = brief("artvision_cinema", "The Goldfinch", folder)
            p["serial_mode"] = "artvision_4x1"
            p["artvision_4x1_plan"] = "ARTVISION_4X1_PLAN.json"
            write_json(folder / "ARTVISION_4X1_PLAN.json",
                       new_plan("The Goldfinch", "Carel Fabritius"))
            write_json(folder / "PROJECT_V13.json", p)
            result = check(folder / "PROJECT_V13.json")
            self.assertFalse(result["ready"])
            self.assertTrue(any("4x1:" in x for x in result["blockers"]))

    def test_audio_only_cannot_be_registered_as_finished_video(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "voice.wav"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=duration=0.2", str(f)], check=True)
            with self.assertRaisesRegex(ValueError, "audio/video"):
                capture("libri", "Test", f, "unused.jpg", Path(d) / "out")


if __name__ == "__main__":
    unittest.main()
