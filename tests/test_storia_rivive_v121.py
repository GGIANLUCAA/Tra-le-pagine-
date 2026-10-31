"""V121: source resolution from real Commons imageinfo, never thumbnail or upscale."""
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.storia_rivive_scout_v101 import native_raster_preflight, inspect, metadata, verify_decoded_original_raster

COMMONS="https://commons.wikimedia.org/wiki/File:Example.webm"

class _FakeApiResponse(io.BytesIO):
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.close()

class V121SourceRasterTests(unittest.TestCase):
    def test_commons_576p_is_rejected(self):
        status=native_raster_preflight({"original_width_px":768,"original_height_px":576})
        self.assertEqual(status["status"],"SOURCE_NATIVE_DETAIL_INSUFFICIENT_SKIP_DOWNLOAD")
        self.assertEqual(status["native_portrait_crop_width_px"],324)

    def test_commons_480p_is_rejected(self):
        status=native_raster_preflight({"original_width_px":720,"original_height_px":480})
        self.assertFalse(status["native_raster_eligible"])
        self.assertEqual(status["native_portrait_crop_width_px"],270)

    def test_720p_native_is_only_preflight_not_approval(self):
        status=native_raster_preflight({"original_width_px":1280,"original_height_px":720})
        self.assertTrue(status["native_raster_eligible"])
        self.assertIn("REQUIRES_DECODE_AND_RIGHTS",status["status"])

    def test_unknown_and_boolean_rasters_fail_closed(self):
        for width,height in ((None,576),(768,None),(True,720),(768,True),("1920",1080),(0,1080)):
            with self.subTest(width=width,height=height):
                status=native_raster_preflight({"original_width_px":width,"original_height_px":height})
                self.assertEqual(status["status"],"SOURCE_RASTER_METADATA_MISSING_SKIP_DOWNLOAD")

    def test_scan_metadata_exposes_real_original_dimensions(self):
        response={"query":{"pages":[{"imageinfo":[{"url":"https://upload.wikimedia.org/wikipedia/commons/0/00/Example.webm",
                    "size":3200000,"width":768,"height":576,
                    "extmetadata":{"LicenseShortName":{"value":"CC0"}}}]}]}}
        with patch("src.storia_rivive_scout_v101.urlopen",return_value=_FakeApiResponse(json.dumps(response).encode())):
            m=metadata(COMMONS)
        self.assertEqual((m["original_width_px"],m["original_height_px"]),(768,576))
        self.assertFalse(m["historical_rights_italy_approved"])
        self.assertFalse(m["social_publish_permitted"])

    def test_low_resolution_never_downloads_original_video(self):
        source={"source_page":COMMONS,"download_url":"https://upload.wikimedia.org/wikipedia/commons/0/00/Example.webm",
                "size_bytes":3000000,"original_width_px":768,"original_height_px":576,
                "license_metadata":"CC0","historical_rights_italy_approved":False}
        with tempfile.TemporaryDirectory() as temp:
            with patch("src.storia_rivive_scout_v101.metadata",return_value=source):
                with patch("src.storia_rivive_scout_v101.urlopen",side_effect=AssertionError("Media download attempted")):
                    result=inspect(COMMONS,Path(temp))
            self.assertEqual(result["status"],"SOURCE_NATIVE_DETAIL_INSUFFICIENT_SKIP_DOWNLOAD")
            self.assertFalse(result["original_media_downloaded"])
            self.assertFalse((Path(temp)/"ORIGINAL_ARCHIVE.webm").exists())

    def test_ffprobe_video_stream_missing_or_wrong_fails(self):
        original={"original_width_px":1280,"original_height_px":720}
        with self.assertRaisesRegex(ValueError,"SOURCE_DECODED_RASTER_DIFFERS"):
            verify_decoded_original_raster({"streams":[{"codec_type":"audio"}]},original)
        with self.assertRaisesRegex(ValueError,"SOURCE_DECODED_RASTER_DIFFERS"):
            verify_decoded_original_raster({"streams":[{"codec_type":"video","width":640,"height":480}]},original)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"),"FFmpeg required")
    def test_ffprobe_confirms_real_decoded_video_raster(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"raster_fixture.mp4"
            subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-nostdin","-y",
                            "-f","lavfi","-i","testsrc2=size=1280x720:rate=1:duration=1",
                            "-frames:v","1","-c:v","mpeg4",str(p)],check=True,timeout=30)
            result=subprocess.run(["ffprobe","-v","error","-show_entries",
                "stream=codec_type,width,height","-of","json",str(p)],
                capture_output=True,text=True,check=True,timeout=20)
            info=json.loads(result.stdout)
            self.assertTrue(verify_decoded_original_raster(info,{
                "original_width_px":1280,"original_height_px":720}))
            with self.assertRaisesRegex(ValueError,"SOURCE_DECODED_RASTER_DIFFERS"):
                verify_decoded_original_raster(info,{
                    "original_width_px":1920,"original_height_px":1080})

    def test_missing_dimensions_never_downloads(self):
        source={"source_page":COMMONS,"download_url":"https://upload.wikimedia.org/wikipedia/commons/0/00/Example.webm",
                "size_bytes":3000000,"original_width_px":None,"original_height_px":None}
        with tempfile.TemporaryDirectory() as temp:
            with patch("src.storia_rivive_scout_v101.metadata",return_value=source):
                with patch("src.storia_rivive_scout_v101.urlopen",side_effect=AssertionError("Media download attempted")):
                    result=inspect(COMMONS,Path(temp))
            self.assertEqual(result["status"],"SOURCE_RASTER_METADATA_MISSING_SKIP_DOWNLOAD")
            self.assertFalse((Path(temp)/"ORIGINAL_ARCHIVE.webm").exists())

if __name__=="__main__":
    unittest.main()
