"""V176 offline regression of V101 source pixel gate; 43055/43056 target."""

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("v101_scout",ROOT/"src/storia_rivive_scout_v101.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def film(w,h):
    return {"streams":[{"codec_type":"video","width":w,"height":h,
                        "codec_name":"h264"}]}


class V176SourceQualityTests(unittest.TestCase):
    def test_paris_1918_sd_is_rejected_before_i2i(self):
        q=m.v176_source_raster_gate(film(720,576))
        self.assertEqual(q["status"],"REJECT_LOW_SOURCE_PIXELS_FOR_REFERENCE_LEVEL_MOTION")
        self.assertLess(q["source_to_720x1280_portrait_pixel_area_ratio"],.25)
        self.assertFalse(q["minimum_reference_43055_43056_met"])

    def test_1917_fashion_sd_is_rejected(self):
        q=m.v176_source_raster_gate(film(352,240))
        self.assertEqual(q["status"],"REJECT_LOW_SOURCE_PIXELS_FOR_REFERENCE_LEVEL_MOTION")

    def test_720p_even_if_labelled_hd_is_rejected_for_portrait(self):
        q=m.v176_source_raster_gate(film(1280,720))
        self.assertEqual(q["status"],"REJECT_LOW_SOURCE_PIXELS_FOR_REFERENCE_LEVEL_MOTION")
        self.assertEqual(q["native_central_portrait_crop_px"],[405,720])

    def test_1080p_is_only_eligible_for_human_source_review(self):
        q=m.v176_source_raster_gate(film(1920,1080))
        self.assertEqual(q["status"],"SOURCE_ENCODED_RASTER_ELIGIBLE_FOR_VISUAL_REVIEW")
        self.assertEqual(q["native_central_portrait_crop_px"],[608,1080])
        for claim in ("minimum_reference_43055_43056_met","native_scan_quality_or_face_detail_verified",
                      "italian_rights_verified","subject_large_and_legible_verified",
                      "four_photo_i2i_verified","vidu_motion_verified"):
            self.assertFalse(q[claim])

    def test_4k_is_not_automatically_approved_for_artistic_quality(self):
        q=m.v176_source_raster_gate(film(3840,2160))
        self.assertEqual(q["status"],"SOURCE_ENCODED_RASTER_ELIGIBLE_FOR_VISUAL_REVIEW")
        self.assertFalse(q["native_scan_quality_or_face_detail_verified"])

    def test_invalid_or_missing_dimensions_fail_closed(self):
        self.assertEqual(m.v176_source_raster_gate({"streams":[]})["status"],"SOURCE_NO_VIDEO_STREAM")
        self.assertEqual(m.v176_source_raster_gate({"streams":[{"codec_type":"video"}]})["status"],
                         "SOURCE_MISSING_ENCODED_RASTER")
        self.assertEqual(m.v176_source_raster_gate(film("garbage",360))["status"],
                         "SOURCE_MISSING_ENCODED_RASTER")
        self.assertEqual(m.v176_source_raster_gate(film(1,1))["status"],
                         "SOURCE_INVALID_ENCODED_RASTER")

    def test_sar_ambiguity_does_not_claim_optical_scan(self):
        q=m.v176_source_raster_gate({"streams":[{"codec_type":"video",
                     "width":1920,"height":1080,"sample_aspect_ratio":"4:3"}]})
        self.assertEqual(q["status"],"SOURCE_ENCODED_RASTER_ELIGIBLE_FOR_VISUAL_REVIEW")
        self.assertFalse(q["native_scan_quality_or_face_detail_verified"])

    def test_rejected_film_never_extracts_fake_frames(self):
        from unittest.mock import MagicMock
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)
            orig_meta=m.metadata
            try:
                m.metadata=lambda page: {
                     "source_page":page, "size_bytes":4,
                     "download_url":"https://upload.wikimedia.org/test.webm",
                     "license_metadata":"CC0", "social_publish_permitted":False}
                class FilmData:
                    def __enter__(self):return self
                    def __exit__(self,*args):return False
                    def read(self,n=-1):return b"abcd" if not getattr(self,"done",False) else b""
                film_data=FilmData()
                def get(n):out=film_data.read(n);film_data.done=True;return out
                film_data.read=get
            finally:
                m.metadata=orig_meta

    def test_quality_thresholds_were_not_replaced_with_technical_mux_pass(self):
        self.assertGreaterEqual(m.MIN_ENCODED_SOURCE_HEIGHT,1000)
        self.assertGreaterEqual(m.MIN_NATIVE_PORTRAIT_PIXEL_RATIO,.60)


if __name__=="__main__":
    unittest.main()
