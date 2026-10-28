import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("v58", ROOT/"src/storia_rivive_montage_v58.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class StoryMontageV58(unittest.TestCase):
    def make_plan(self, folder):
        clip = folder / "test.mp4"
        subprocess.run(["ffmpeg","-nostdin","-loglevel","error","-y","-f","lavfi",
                        "-i","testsrc2=size=160x120:rate=24","-t","2.7",
                        "-c:v","libx264","-pix_fmt","yuv420p",str(clip)],
                       check=True, capture_output=True, timeout=90)
        source = {"source_page":"https://commons.wikimedia.org/wiki/File:Sample",
                  "source_id":"test_fixture","rights_checked":True,
                  "source_license":"CC0","nonmonetized_publication_rights_checked":True,
                  "framing_reviewed":True}
        reveal = {**source, "kind":"reveal", "bw_file":str(clip), "color_file":str(clip),
                  "start":0, "duration":1.25,"reveal_at":.4,"reveal_seconds":.4,
                  "same_source_and_frames_verified":True,"semantic_color_reviewed":True}
        outro = {**source, "kind":"archive_bw","file":str(clip),"start":1.25,"duration":1.25}
        return {"title":"TEST ONLY — not AI-colorized","test_only":True,
                "width":360,"height":640,"scenes":[reveal,outro],"audio":{}}

    def test_v59_rejects_copyrighted_archival_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan = self.make_plan(Path(tmp))
            plan["scenes"][0]["source_license"] = "CC BY-NC"
            errors, _ = mod.check(plan)
            self.assertTrue(any("V59" in e for e in errors))

    def test_no_paid_api_and_no_autopublish(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan = self.make_plan(Path(tmp))
            plan["allow_paid_calls"] = True
            plan["autopublish"] = True
            errors, _ = mod.check(plan)
            self.assertGreaterEqual(len(errors),2)

    def test_no_sepia_as_final(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan = self.make_plan(Path(tmp))
            plan["test_only"] = False
            plan["width"],plan["height"] = 720,1280
            errors,_=mod.check(plan)
            self.assertTrue(any("rapporto V57" in x for x in errors))

    def test_ai_insert_disclosure_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan = self.make_plan(Path(tmp))
            plan["scenes"].append({"kind":"ai_reconstruction","file":plan["scenes"][0]["bw_file"],
                "start":0,"duration":1.1,"framing_reviewed":True,"paid_generation_used":True})
            errors,_=mod.check(plan)
            self.assertTrue(any("Vidu" in x for x in errors))
            self.assertTrue(any("ricostruzione" in x for x in errors))

    def test_real_ffmpeg_montage_of_test_fixture_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp); plan=self.make_plan(folder)
            errors,duration=mod.check(plan)
            self.assertEqual(errors,[])
            self.assertEqual(duration,2.5)
            outfile=folder/"TEST_ONLY_MONTAGE.mp4"
            result=mod.render(plan,outfile)
            self.assertTrue(outfile.exists())
            self.assertEqual(result["status"],"rendered_needs_review_and_V55_delivery")
            ff=subprocess.run(["ffmpeg","-nostdin","-v","error","-xerror",
                                "-i",str(outfile),"-f","null","-"],capture_output=True)
            self.assertEqual(ff.returncode,0,ff.stderr.decode()[:800])
            self.assertEqual(len(result["video_sha256"]),64)


if __name__=="__main__":
    unittest.main()
