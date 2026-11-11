"""Opt-in cinematographic camera tests: geometry and ASR rather than aesthetics."""
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from artvision_critico_directed_camera_v2 import (
    crop_camera, smooth_progress, chapter_plan, BRUEGEL_MODES
)

CH = {"cx":.55, "cy":.56, "crop_height_px":1150, "focus":"angeli al centro"}


class DirectedCameraTests(unittest.TestCase):
    def test_hold_has_zero_motion_at_beginning_and_end(self):
        self.assertEqual(smooth_progress(0), 0)
        self.assertEqual(smooth_progress(.2), 0)
        self.assertEqual(smooth_progress(.8), 1)
        self.assertEqual(smooth_progress(1), 1)
        self.assertAlmostEqual(smooth_progress((.24+.77)/2), .5)

    def test_locked_crop_is_bitwise_identical(self):
        seq=[crop_camera(CH, u, 3840,2772,720,1280,"locked")
             for u in (0,.15,.5,.8,1)]
        self.assertEqual(len(set(seq)),1)

    def test_push_monotonic_and_has_easing_holds(self):
        seq=[crop_camera(CH,u,3840,2772,720,1280,"hold_push")
             for u in (0,.1,.24,.5,.77,.9,1)]
        self.assertEqual(seq[0],seq[1])
        self.assertEqual(seq[-1],seq[-2])
        heights=[r[3]-r[1] for r in seq]
        self.assertEqual(heights,sorted(heights,reverse=True))
        self.assertLess(heights[-1],heights[0])

    def test_pan_slow_and_bounded(self):
        seq=[crop_camera(CH,u,3840,2772,720,1280,"hold_pan_right")
             for u in (0,.2,.5,.8,1)]
        self.assertLess(seq[0][0],seq[-1][0])
        self.assertLess(seq[-1][0]-seq[0][0],.02*3840)
        self.assertEqual(seq[0],seq[1])
        self.assertEqual(seq[-1],seq[-2])

    def test_never_shows_out_of_bounds_crop(self):
        ch={"cx":.99,"cy":.02,"crop_height_px":950,"focus":"bordi"}
        for mode in BRUEGEL_MODES.values():
            for u in (0,.25,.5,.75,1):
                x0,y0,x1,y1=crop_camera(ch,u,3840,2772,720,1280,mode)
                self.assertTrue(0<=x0<x1<=3840)
                self.assertTrue(0<=y0<y1<=2772)
                self.assertAlmostEqual((x1-x0)/(y1-y0),720/1280,delta=.002)

    def test_fails_closed_on_insufficient_image_source(self):
        with self.assertRaises(ValueError):
            crop_camera(CH,.4,600,400,720,1280,"hold_push")

    def test_real_asr_plan_uses_actual_timecodes_no_voice_change(self):
        chapters=[{"focus":"cielo"},{"focus":"terra"}]
        plan=chapter_plan(chapters,[4.5,10.2],voice_offset_s=3.5,
                          wav_sha256="a"*64,source_sha256="b"*64,
                          modes={0:"locked",1:"hold_push"})
        self.assertEqual(plan["chapters"][1]["start_s"],8.0)
        self.assertEqual(plan["chapters"][1]["end_s"],13.7)
        self.assertFalse(plan["changes_narration"])
        self.assertFalse(plan["can_publish"])
        self.assertFalse(plan["artistic_approved"])

    def test_invalid_timestamps_are_rejected(self):
        with self.assertRaises(ValueError):
            chapter_plan([{"focus":"real"},{"focus":"real"}],[7,6],
                         voice_offset_s=2,wav_sha256="a"*64,
                         source_sha256="b"*64,modes={0:"locked",1:"hold_push"})

    def test_bool_and_unapproved_modes_invalid(self):
        for mode in ("sinusoidal", "bouncy", "dolly_zoom", "", None):
            with self.assertRaises(ValueError):
                crop_camera(CH,.4,3840,2772,720,1280,mode)
        with self.assertRaises(ValueError):
            crop_camera(CH, True,3840,2772,720,1280,"locked")


if __name__=="__main__":
    unittest.main()
