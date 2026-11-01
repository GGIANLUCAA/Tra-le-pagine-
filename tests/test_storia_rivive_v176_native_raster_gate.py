#!/usr/bin/env python3
"""V176: offline regression tests for fail-closed encoded raster gate.

Real decoded film pixels are required; 720p/480p previews are not promoted to
source material just because an AI upscaler can produce a 4K output.
"""
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE=Path(__file__).resolve().parents[1]/"src"/"storia_rivive_scout_v101.py"
spec=importlib.util.spec_from_file_location("storia_v176",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def probe(w=None,h=None,codec="h264"):
    stream={"codec_type":"video","codec_name":codec}
    if w is not None:stream["width"]=w
    if h is not None:stream["height"]=h
    return {"streams":[stream],"format":{"duration":"28.0"}}


class V176RasterGate(unittest.TestCase):
    def test_1917_original_352x240_is_rejected(self):
        q=m.v176_source_raster_gate(probe(352,240,codec="mpeg1video"))
        self.assertEqual(q["status"],"REJECT_LOW_SOURCE_PIXELS_FOR_REFERENCE_LEVEL_MOTION")
        self.assertEqual(q["native_central_portrait_crop_px"],[135,240])
        self.assertFalse(q["minimum_reference_43055_43056_met"])

    def test_480p_and_720p_are_rejected(self):
        for w,h in ((720,480),(720,576),(1280,720),(640,480),(1920,800)):
            with self.subTest(raster=(w,h)):
                q=m.v176_source_raster_gate(probe(w,h))
                self.assertEqual(q["status"],"REJECT_LOW_SOURCE_PIXELS_FOR_REFERENCE_LEVEL_MOTION")

    def test_1080p_or_4k_is_only_eligible_for_visual_review(self):
        for w,h in ((1920,1080),(3840,2160),(1080,1920)):
            with self.subTest(raster=(w,h)):
                q=m.v176_source_raster_gate(probe(w,h))
                self.assertEqual(q["status"],"SOURCE_ENCODED_RASTER_ELIGIBLE_FOR_VISUAL_REVIEW")
                self.assertTrue(q["encoded_pixel_geometry_verified"])
                self.assertFalse(q["native_scan_quality_or_face_detail_verified"])
                self.assertFalse(q["italian_rights_verified"])
                self.assertFalse(q["minimum_reference_43055_43056_met"])
                self.assertFalse(q["four_photo_i2i_verified"])
                self.assertFalse(q["vidu_motion_verified"])

    def test_missing_or_invalid_stream_fail_closed(self):
        for p in ({"streams":[]}, {"streams":[{"codec_type":"audio"}]},
                  probe(None,1080),probe(1920,None),probe(-1,1080),probe(20000,1080)):
            with self.subTest(p=p):
                q=m.v176_source_raster_gate(p)
                self.assertNotEqual(q["status"],"SOURCE_ENCODED_RASTER_ELIGIBLE_FOR_VISUAL_REVIEW")

    def test_reject_before_expensive_frame_extraction(self):
        # No remote calls; the same original bytes/ffprobe JSON flow as inspect().
        class FakeResponse:
            def __init__(self,payload):self.payload=payload;self.done=False
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self,n):
                if self.done:return b""
                self.done=True
                return self.payload
        sample=b"real-file-bytes-mocked-for-offline-test"
        metadata={"source_page":"https://commons.wikimedia.org/wiki/File:Example.webm",
                  "download_url":"https://upload.wikimedia.org/Example.webm",
                  "size_bytes":len(sample),"historical_rights_italy_approved":False}
        result=subprocess.CompletedProcess(args=[],returncode=0,stdout=json.dumps(probe(352,240)),stderr="")
        with tempfile.TemporaryDirectory() as d:
            with patch.object(m,"metadata",return_value=metadata), \
                 patch.object(m,"urlopen",return_value=FakeResponse(sample)), \
                 patch.object(m.subprocess,"run",return_value=result) as run:
                output=m.inspect(metadata["source_page"],Path(d))
            self.assertEqual(output["status"],"REJECT_LOW_SOURCE_PIXELS_FOR_REFERENCE_LEVEL_MOTION")
            self.assertEqual(output["source_frames_extracted"],0)
            self.assertFalse(output["finished_mp4"])
            self.assertFalse((Path(d)/"original_frames").exists())
            self.assertEqual(run.call_count,1)
            self.assertEqual((Path(d)/"ORIGINAL_ARCHIVE.webm").read_bytes(),sample)

    def test_no_fake_hd_from_a_filename(self):
        q=m.v176_source_raster_gate(probe(352,240))
        self.assertEqual(q["status"],"REJECT_LOW_SOURCE_PIXELS_FOR_REFERENCE_LEVEL_MOTION")
        self.assertFalse(q["minimum_reference_43055_43056_met"])


if __name__=="__main__":unittest.main()
