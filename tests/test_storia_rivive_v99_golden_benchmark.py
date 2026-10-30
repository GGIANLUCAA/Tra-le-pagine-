"""V99 regression tests — no paid API calls; tests read actual V98 only when supplied."""
import copy, os, pathlib, sys, tempfile, unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"src"))
import storia_rivive_v99_golden_benchmark as g

def good_manifest():
    shots=[];start=0.0
    for i in range(4):
        bw=1.3;reveal=.36;hold=1.65;d=bw+reveal+hold
        shots.append({"kind":"classic_photo","start_s":start,"duration_s":d,"bw_motion_s":bw,
          "reveal_s":reveal,"color_photo_hold_s":hold,"restoration_model":"Finegrain+DDColor",
          "source_film_sha256":"a"*64,"source_timecode_s":55.0+30*i})
        start+=d
    shots.append({"kind":"vidu_motion","start_s":start,"duration_s":6.08,"bw_motion_s":1.08,
      "source_film_sha256":"a"*64,"source_timecode_s":300.0})
    return {"format":"storia_rivive","project_format":"4classic_1vidu","scenes":shots}

class TestGoldenV99(unittest.TestCase):
    def test_00_real_accepted_v98_video_scanned_from_release(self):
        p=os.environ.get("V99_GOLDEN_VIDEO","")
        if not p:self.skipTest("Set V99_GOLDEN_VIDEO to actual MP4 from the user-accepted GitHub release")
        a=g.approved_reference(p)
        self.assertEqual(a["reference_sha256"],g.GOLDEN_SHA)
        self.assertEqual(len(a["per_scene"]),5)
        self.assertTrue(all(x["color_gain"]>2 for x in a["per_scene"][:4]))
        self.assertGreater(a["per_scene"][4]["moving_intervals"],2)

    def test_01_reference_is_immutable_sha_not_filename(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/"LA_STORIA_RIVIVE_SF1906_V98_FOUR_REAL_I2I_ONE_REAL_VIDU.mp4"
            p.write_bytes(b"fake MP4 with misleading filename")
            with self.assertRaisesRegex(RuntimeError,"HASH_MISMATCH"):
                g.approved_reference(p)

    def test_02_good_five_scene_order(self):
        self.assertEqual(g.structural_checks(good_manifest()),[])

    def test_03_reject_sixth_fake_filler(self):
        m=good_manifest()
        m["scenes"].append(copy.deepcopy(m["scenes"][0]))
        self.assertIn("FIVE_REAL_SCENES_NOT_PRESENT",g.structural_checks(m))

    def test_04_reject_vidu_in_wrong_scene(self):
        m=good_manifest();m["scenes"][1]["kind"]="vidu_motion"
        self.assertIn("FOUR_PHOTOGRAPHS_PLUS_ONE_VIDU_WRONG_ORDER",g.structural_checks(m))

    def test_05_ddcolor_is_not_finegrain_restoration(self):
        m=good_manifest();m["scenes"][2]["restoration_model"]="DDColor-only"
        self.assertIn("SCENE_3_DDCOLOR_ONLY_IS_NOT_A_REAL_PHOTO_RESTORATION",g.structural_checks(m))

    def test_06_overlong_photo_hold_not_approved(self):
        m=good_manifest();m["scenes"][3]["color_photo_hold_s"]=3.9
        self.assertIn("SCENE_4_PHOTO_DURATION_OR_REVEAL_WRONG",g.structural_checks(m))

    def test_07_reused_same_source_not_a_different_shot(self):
        m=good_manifest();m["scenes"][1]["source_timecode_s"]=m["scenes"][0]["source_timecode_s"]
        self.assertIn("SCENE_2_ORIGINAL_SOURCE_REPEATED",g.structural_checks(m))

    def test_08_reject_video_missing_five_seconds_of_vidu(self):
        m=good_manifest();m["scenes"][4]["duration_s"]=2.0
        self.assertIn("SCENE_5_VIDU_NOT_FIVE_SECONDS",g.structural_checks(m))

    def test_09_reject_wrong_source_sha_and_zero_film_evidence(self):
        m=good_manifest();m["scenes"][0]["source_film_sha256"]="unknown"
        self.assertIn("SCENE_1_SOURCE_FILM_HASH_NOT_VERIFIED",g.structural_checks(m))

    def test_10_missing_actual_photo_is_not_a_successful_qa(self):
        errors=[]
        with tempfile.TemporaryDirectory() as tmp:
            p=g.file(tmp,{"restored_photo_file":"never_existed.png",
                          "restored_photo_sha256":"c"*64},"restored_photo_file",
                "restored_photo_sha256",errors,"SCENE_2_I2I")
        self.assertIsNone(p)
        self.assertIn("SCENE_2_I2I_MISSING_FILE",errors)

    def test_11_no_overstated_human_approval_in_baseline(self):
        p=os.environ.get("V99_GOLDEN_VIDEO","")
        if not p:self.skipTest("Reference MP4 unavailable locally")
        report=g.approved_reference(p)
        self.assertNotIn("human_artistic_approval",report)
        self.assertEqual(report["reference_release"],g.GOLDEN_TAG)

    def test_12_real_V98_vs_video_visual_comparison_sheet(self):
        p=os.environ.get("V99_GOLDEN_VIDEO","")
        if not p:self.skipTest("Reference MP4 not on runner")
        reference=g.golden_timeline()
        # This test exercises the visual tool, not semantic approval of new faces.
        with tempfile.TemporaryDirectory() as d:
            out=pathlib.Path(d)/"ab-qa.jpg"
            result=g.visual_reference_contact_sheet(p,p,{"scenes":reference},out)
            self.assertEqual(result,str(out))
            self.assertGreater(out.stat().st_size,60_000)

if __name__=="__main__": unittest.main()
