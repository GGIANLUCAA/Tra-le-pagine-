import unittest
from unittest.mock import patch
from src.storia_rivive_motion_window_v115 import inspect_five_source_windows


class FiveWindows(unittest.TestCase):
    def setUp(self):
        self.windows = [dict(start_pts=0, freeze_pts=45, time_base='1/30') for _ in range(5)]

    def test_rejects_missing_window(self):
        self.assertEqual(inspect_five_source_windows('unused', '0'*64, self.windows[:4])['reason'], 'NEED_FIVE_SOURCE_WINDOWS')

    def test_rejects_bad_metadata(self):
        self.windows[2] = None
        self.assertEqual(inspect_five_source_windows('unused', '0'*64, self.windows)['reason'], 'INVALID_WINDOW_METADATA')

    @patch('src.storia_rivive_motion_window_v115.inspect_source_motion')
    def test_rejects_static_scene(self, inspect):
        inspect.side_effect = [{'motion_verified': True}]*2 + [{'motion_verified': False}]
        result = inspect_five_source_windows('unused', '0'*64, self.windows)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertEqual(len(result['results']), 3)

    @patch('src.storia_rivive_motion_window_v115.inspect_source_motion')
    def test_five_motion_pass_not_approval(self, inspect):
        inspect.return_value = {'motion_verified': True}
        result = inspect_five_source_windows('unused', '0'*64, self.windows)
        self.assertEqual(result['status'], 'FIVE_MOTION_WINDOWS_EVIDENCED_REVIEW_REQUIRED')
        self.assertEqual(len(result['results']), 5)

if __name__ == '__main__':
    unittest.main()
