"""V177 LOC real film byte probes: exact fixed HTTPS, fail closed, no oversize."""
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("loc177",ROOT/"src/storia_rivive_v177_loc_actual_media_probe.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class V177Tests(unittest.TestCase):
    def test_exact_official_frozen_urls_only(self):
        self.assertEqual(m.ensure_url(m.MP4),m.MP4)
        self.assertEqual(m.ensure_url(m.MOV),m.MOV)
        for url in ("https://evil.com/a.mp4",
                    "http://tile.loc.gov/storage-services/service/mbrs/ntscrm/00047539/00047539.mp4",
                    "https://tile.loc.gov/storage-services/service/mbrs/ntscrm/00047539/other.mp4",
                    "https://tile.loc.gov.evil.com/storage-services/test.mov"):
            with self.subTest(url=url),self.assertRaises(ValueError):
                m.ensure_url(url)

    def test_no_giant_download_without_whole_file_bound(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,"REFUSE_FULL_DOWNLOAD_OVER_BYTE_CAP"):
                m.stream_exact(m.MP4,Path(td)/"source.mp4",m.DOWNLOAD_CAP+1)

    def test_ffprobe_encoded_raster_720p_is_not_reference_quality(self):
        import subprocess,json
        fake={"streams":[{"codec_type":"video","width":720,"height":576,"codec_name":"h264"}],
              "format":{"duration":"850.4"}}
        reply=subprocess.CompletedProcess(args=[],returncode=0,stdout=json.dumps(fake),stderr="")
        with patch.object(m.subprocess,"run",return_value=reply):
            q=m.ffprobe(Path("fake.mp4"))
        self.assertEqual(q["encoded_height"],576)
        self.assertFalse(q["passes_V176_minimum_encoded_pixel_screen"])
        self.assertFalse(q["optical_film_scan_native_hd_verified"])

    def test_ffprobe_1080p_is_not_artistically_approved(self):
        import subprocess,json
        fake={"streams":[{"codec_type":"video","width":1920,"height":1080,"codec_name":"prores"}],
              "format":{"duration":"600"}}
        reply=subprocess.CompletedProcess(args=[],returncode=0,stdout=json.dumps(fake),stderr="")
        with patch.object(m.subprocess,"run",return_value=reply):
            q=m.ffprobe(Path("fake.mov"))
        self.assertTrue(q["passes_V176_minimum_encoded_pixel_screen"])
        self.assertFalse(q["photoreal_human_faces_verified"])
        self.assertFalse(q["optical_film_scan_native_hd_verified"])

    def test_no_video_stream_or_strange_duration_is_rejected(self):
        import subprocess,json
        with patch.object(m.subprocess,"run",return_value=subprocess.CompletedProcess([],
                    0,stdout=json.dumps({"streams":[],"format":{"duration":"20"}}),stderr="")):
            with self.assertRaisesRegex(ValueError,"NO_VIDEO"):
                m.ffprobe(Path("none.mp4"))
        with patch.object(m.subprocess,"run",return_value=subprocess.CompletedProcess([],
                    0,stdout=json.dumps({"streams":[{"codec_type":"video","width":640,"height":480}],
                                          "format":{"duration":"0.5"}}),stderr="")):
            with self.assertRaisesRegex(ValueError,"VIDEO_RASTER_OR_DURATION_INVALID"):
                m.ffprobe(Path("short.mp4"))

    def test_download_length_mismatch_removes_bad_file(self):
        class FakeRead:
            def __init__(self):self.data=io.BytesIO(b"123456789")
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self,n):return self.data.read(n)
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"bad.mp4"
            with patch.object(m,"urlopen",return_value=FakeRead()):
                with self.assertRaisesRegex(ValueError,"VIDEO_BYTE_LENGTH_MISMATCH"):
                    m.stream_exact(m.MP4,out,100)
            self.assertFalse(out.exists())

    def test_probe_is_research_not_video_generation(self):
        with tempfile.TemporaryDirectory() as td:
            with patch.object(m,"probe_remote_headers",side_effect=OSError("test network unavailable")):
                r=m.execute(Path(td))
            self.assertEqual(r["status"],"SCOUT_BLOCKED_LOC_MEDIA_ENDPOINTS")
            self.assertFalse(r["human_artist_quality_approved"])
            self.assertTrue(r["not_final_video"])
            self.assertEqual(r["vidu_credits_spent"],0)
            self.assertTrue((Path(td)/"V177_REAL_LOC_FILM_BYTE_QA.json").exists())


if __name__=="__main__":
    unittest.main()
