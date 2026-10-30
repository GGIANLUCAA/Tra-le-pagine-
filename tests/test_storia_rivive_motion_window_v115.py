import unittest
from src.storia_rivive_motion_window_v115 import check_source_window


class MotionWindowTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(check_source_window(0, 45, '1/30')[0], True)

    def test_short(self):
        self.assertEqual(check_source_window(0, 12, '1/30')[1], 'PRE_FREEZE_WINDOW_TOO_SHORT')

    def test_long(self):
        self.assertEqual(check_source_window(0, 120, '1/30')[1], 'PRE_FREEZE_WINDOW_TOO_LONG')

    def test_clock(self):
        self.assertEqual(check_source_window(0, 45, '1/0')[1], 'INVALID_TIME_BASE')

    def test_bool_pts(self):
        self.assertEqual(check_source_window(True, 45, '1/30')[1], 'INVALID_PTS_TYPE')

    def test_reverse(self):
        self.assertEqual(check_source_window(45, 30, '1/30')[1], 'NO_PRE_FREEZE_SOURCE_WINDOW')


if __name__ == '__main__':
    unittest.main()
