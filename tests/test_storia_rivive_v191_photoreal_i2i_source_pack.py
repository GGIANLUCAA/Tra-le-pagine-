"""V191: offline fail-closed checks; separate CI tests on the real V189/V190 bytes."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import storia_rivive_v191_photoreal_i2i_source_pack as v191


def fixtures():
    src=[]
    movie=[]
    for n in range(1,6):
        a={"scene":n,"exact_freeze_file":f"0{n}_scene_last_real_film_frame.png",
           "exact_freeze_sha256":f"{n}"*64,"real_motion_file":f"0{n}_scene_real_film_bw.mp4",
           "real_motion_sha256":f"{n+1}"*64,
           "source_shot_png":f"shot_{n:02}.png",
           "source_crop_native_px":[603,1072],"encoded_raster_px":[720,1280],
           "last_decoded_frame_pixel_identical_to_freeze":True,"source_lock_verified":True}
        src.append(a)
        movie.append({"index":n,"exact_last_decoded_frame_sha256":a["exact_freeze_sha256"],
                     "motion_mp4_sha256":a["real_motion_sha256"]})
    v190={"version":"V190_EXACT_FRAME_I2I_VIDU_HANDOFF",
          "status":"FIVE_REAL_SOURCE_FRAMES_VERIFIED_PROVIDER_BLOCKED",
          "film_sha256":v191.FILM_SHA,"source_frames":src,"photos_generated":0,
          "vidu_clips_generated":0,"provider_requests_sent":0,
          "publication_permitted":False,"rights_italy_verified":False}
    v189={"version":"V189","status":"REAL_BW_MOTION_PROOF_REVIEW_ONLY",
          "source_sha256":v191.FILM_SHA,"scenes":movie,
          "provider_jobs_may_start":False}
    return v190,v189


class V191Tests(unittest.TestCase):
    def test_4_real_sources_one_vidu_and_22_seconds_not_claimed_4k(self):
        a,b=fixtures()
        r=v191.make_plan(a,b)
        self.assertEqual(len(r["photo_i2i_jobs"]),4)
        self.assertEqual(r["vidu_job"]["scene"],5)
        self.assertEqual(r["target_film_duration_s"],22.55)
        self.assertTrue(r["4k_is_only_target_not_original_or_achieved"])
        self.assertEqual(r["source_raster_effective_unscaled_pixels"],[603,1072])
        self.assertFalse(r["publish_permitted"])
        self.assertEqual(r["provider_calls"],0)

    def test_source_film_sha_change_fails(self):
        a,b=fixtures()
        a["film_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"SOURCE_HANDOFF_INVALID"):
            v191.make_plan(a,b)

    def test_fake_photo_or_user_approval_fails_closed(self):
        a,b=fixtures()
        a["photos_generated"]=4
        with self.assertRaisesRegex(ValueError,"UNTRUSTED_STATUS_FLAGS"):
            v191.make_plan(a,b)

    def test_wrong_frame_anchor_digest_refused(self):
        a,b=fixtures()
        b["scenes"][0]["exact_last_decoded_frame_sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"SOURCE_ANCHOR_MISMATCH"):
            v191.make_plan(a,b)

    def test_missing_source_not_five_fails(self):
        a,b=fixtures()
        a["source_frames"]=a["source_frames"][:4]
        with self.assertRaisesRegex(ValueError,"FIVE_EXACT_SOURCE_FRAMES_REQUIRED"):
            v191.make_plan(a,b)

    def test_incorrect_crop_source_px_fails(self):
        a,b=fixtures()
        a["source_frames"][1]["source_crop_native_px"]=[720,1280]
        with self.assertRaisesRegex(ValueError,"SOURCE_ANCHOR_MISMATCH"):
            v191.make_plan(a,b)

    def test_reject_unsafe_archive_paths(self):
        import zipfile
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"bad.zip"
            with zipfile.ZipFile(path,"w") as z:
                z.writestr("../sneak.png",b"bad")
            with self.assertRaisesRegex(ValueError,"UNSAFE_ARCHIVE_MEMBER"):
                with v191.read_archive(path) as z:
                    pass

    def test_reject_duplicate_archive_names(self):
        import zipfile,warnings
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"bad.zip"
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                with zipfile.ZipFile(path,"w") as z:
                    z.writestr("bad.png",b"a")
                    z.writestr("bad.png",b"b")
            with self.assertRaisesRegex(ValueError,"DUPLICATE_ARCHIVE_NAME"):
                with v191.read_archive(path) as z:
                    pass

    def test_real_4k_export_never_asserted_without_real_i2i(self):
        a,b=fixtures()
        r=v191.make_plan(a,b)
        self.assertEqual(r["i2i_generated"],0)
        self.assertEqual(r["vidu_generated"],0)
        self.assertFalse(r["final_mp4_created"])
        self.assertFalse(r["artistic_quality_v98_approved"])
        self.assertTrue(all(x["output_photo"] is None for x in r["photo_i2i_jobs"]))
        self.assertFalse(r["vidu_job"]["scene_authorization"])


if __name__=="__main__":
    unittest.main()
