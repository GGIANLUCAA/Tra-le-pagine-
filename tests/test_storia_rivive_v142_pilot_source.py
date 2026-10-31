"""V142: strict free research contract for rare Constantinople 1916 Ogg/Theora film.

Unit tests do NOT grant rights, artistic approval, Vidu cost or an MP4 master.
The PR-only GitHub Action downloads one authentic Commons file and reports
SHA-256, decoded raster, original motion and five-shot candidates.
"""
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.storia_rivive_autopilot_v101 import build_work_order
from src.storia_rivive_scout_v101 import metadata, native_raster_preflight, verify_decoded_original_raster

ROOT=Path(__file__).resolve().parents[1]
WORKFLOW=ROOT/".github/workflows/storia-v142-constantinople-source-audit.yml"
BANK=ROOT/"queue/storia_rivive_candidates_v58.json"
PROFILE=ROOT/"config/storia_rivive_autopilot_v101.json"
ID="constantinople_messter_1916"
PAGE="https://commons.wikimedia.org/wiki/File:Messter_Woche_Mackensen_in_Constantinople_1916_filmed_by_Nelson_Edwards.ogg"

class _Response(io.BytesIO):
    def __enter__(self):return self
    def __exit__(self,*args):self.close()

class TestV142PilotSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow=WORKFLOW.read_text(encoding="utf-8")
        cls.bank=json.loads(BANK.read_text(encoding="utf-8"))
        cls.profile=json.loads(PROFILE.read_text(encoding="utf-8"))

    def test_precise_archival_page_and_editorial_not_approval(self):
        rows=[c for c in self.bank["candidates"] if c["id"]==ID]
        self.assertEqual(len(rows),1)
        src=rows[0]
        self.assertEqual(src["source_page"],PAGE)
        self.assertEqual(src["year"],1916)
        self.assertEqual(src["commons_original_raster_claim_px"],[1920,1080])
        self.assertLess(src["commons_original_file_size_mb_approx"],160)
        self.assertFalse(src["rights_italy_verified"])
        self.assertFalse(src["historical_attribution_verified"])
        self.assertFalse(src["source_native_visual_review"])
        self.assertFalse(src["original_film_sha256_verified"])
        self.assertIn("Bundesarchiv",src["license_origin_country_claim"])
        self.assertIn("UNVERIFIED",src["source_archive_verification"])

    def test_work_order_blocks_real_generation_and_publication(self):
        src=next(c for c in self.bank["candidates"] if c["id"]==ID)
        order=build_work_order({"candidates":[src]},"2026-10-31T14:00:00Z",self.profile)
        self.assertEqual(order["episode_id"],ID)
        self.assertEqual(order["source_page"],PAGE)
        self.assertEqual(order["requested_scenes"],{"classic_real_i2i_photos":4,"source_locked_vidu":1})
        for k in ("paid_api_call_permitted","publish_permitted","human_approved","video_completed"):
            self.assertFalse(order[k])
        self.assertEqual(order["credits_spent"],0)
        self.assertIn("ITALY_AND_RESIDUAL_RIGHTS_NEED_REVIEW",order["blocking_issues"])
        self.assertIn("HISTORICAL_PLACE_DATE_NEED_REVIEW",order["blocking_issues"])

    def test_ogg_video_url_is_accepted_only_on_official_commons_host(self):
        payload={"query":{"pages":[{"imageinfo":[{
            "url":"https://upload.wikimedia.org/wikipedia/commons/7/7a/Messter_Woche_Mackensen.ogg",
            "width":1920,"height":1080,"size":104800000,
            "extmetadata":{"LicenseShortName":{"value":"Public domain"}}}]}]}}
        with patch("src.storia_rivive_scout_v101.urlopen",
                   return_value=_Response(json.dumps(payload).encode("utf-8"))):
            info=metadata(PAGE)
        self.assertEqual(info["size_bytes"],104800000)
        self.assertTrue(info["download_url"].endswith(".ogg"))
        self.assertTrue(native_raster_preflight(info)["native_raster_eligible"])
        self.assertFalse(info["historical_rights_italy_approved"])
        self.assertFalse(info["social_publish_permitted"])

    def test_ogg_media_audio_only_or_wrong_raster_is_rejected(self):
        src={"original_width_px":1920,"original_height_px":1080}
        with self.assertRaisesRegex(ValueError,"SOURCE_DECODED_RASTER_DIFFERS"):
            verify_decoded_original_raster(
                {"streams":[{"codec_type":"audio"}]},src)
        with self.assertRaisesRegex(ValueError,"SOURCE_DECODED_RASTER_DIFFERS"):
            verify_decoded_original_raster(
                {"streams":[{"codec_type":"video","width":640,"height":360}]},src)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),"FFmpeg test fixture required")
    def test_actual_theora_ogg_bytes_decode_even_under_legacy_webm_cache_filename(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"ORIGINAL_ARCHIVE.webm"
            # Encode actual Ogg/Theora bytes. The staging extension is legacy;
            # FFprobe must decode the video stream from bytes, not pretend WebM.
            subprocess.run(["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
                "-f","lavfi","-i","testsrc2=size=1280x720:rate=2:duration=1",
                "-frames:v","2","-an","-c:v","libtheora","-q:v","3",
                "-f","ogg",str(p)],check=True,timeout=45)
            probe=subprocess.run(["ffprobe","-v","error","-show_entries",
                "stream=codec_type,codec_name,width,height","-of","json",str(p)],
                capture_output=True,text=True,check=True,timeout=20)
            data=json.loads(probe.stdout)
            streams=[x for x in data["streams"] if x["codec_type"]=="video"]
            self.assertEqual(len(streams),1)
            self.assertEqual(streams[0]["codec_name"],"theora")
            self.assertTrue(verify_decoded_original_raster(data,{
                "original_width_px":1280,"original_height_px":720}))

    def test_workflow_one_free_pr_scoped_actual_film_audit(self):
        s=self.workflow
        self.assertIn("  pull_request:",s)
        self.assertIn("  workflow_dispatch:",s)
        self.assertNotIn("  schedule:",s)
        self.assertIn("  contents: read",s)
        self.assertIn("if: github.run_attempt == 1",s)
        self.assertIn('c["id"]=="'+ID+'"',s)
        self.assertIn(PAGE,s)
        self.assertNotIn("versailles_treaty_1919",s)
        self.assertNotIn("white_house_1917_1921",s)
        self.assertNotIn("secrets.",s)
        self.assertNotIn("VIDU_API_KEY",s)
        self.assertNotIn("gh release create",s)
        self.assertIn('if order["paid_api_call_permitted"] or order["publish_permitted"]:',s)
        for prog in ("storia_rivive_scout_v101.py","storia_rivive_v134_cache_readiness.py",
                     "storia_rivive_adaptive_sampling_v124.py","storia_rivive_v125_real_motion_audit.py",
                     "storia_rivive_v126_balanced_motion_review.py","storia_rivive_v126_frame_diversity.py",
                     "storia_rivive_v128_balanced_frame_review.py","storia_rivive_v129_prefreeze_motion_strips.py"):
            self.assertIn(prog,s)

    def test_artifact_contains_only_review_evidence_not_historical_footage(self):
        s=self.workflow
        self.assertIn('"rights_italy_verified":False',s)
        self.assertIn('"exact_commons_file_matches_bundesarchiv_reel":False',s)
        self.assertIn('"modern_derivative_reuse_cleared":False',s)
        self.assertIn('"publication_permitted":False',s)
        artifact=s.split("      - name: Save only source metadata",1)[-1]
        self.assertIn("STORIA_V142_CONSTANTINOPLE_SOURCE_AUDIT_",artifact)
        self.assertIn("REAL_SOURCE_AUDIT_V142.json",artifact)
        self.assertIn("PREFREEZE_MOTION_STRIPS_V129.jpg",artifact)
        self.assertNotIn("ORIGINAL_ARCHIVE.webm",artifact)
        self.assertNotIn("original_frames/",artifact)
        self.assertNotIn("*.mp4",artifact)
        self.assertNotIn("secrets.",artifact)


if __name__=="__main__":
    unittest.main()
