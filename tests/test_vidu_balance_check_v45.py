"""Free Vidu balance check tests. No network, no API key."""
import importlib.util
from pathlib import Path
import unittest

src = Path(__file__).resolve().parents[1] / "src" / "vidu_balance_check_v45.py"
spec = importlib.util.spec_from_file_location("balance_v45", src)
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class BalanceProbeTests(unittest.TestCase):
    def test_remains_supports_credit_totals(self):
        d = {"remains": [
            {"type": "test", "credit_remain": 6},
            {"type": "metered", "credit_remain": 11},
        ]}
        self.assertEqual(v.available_credits(d), 17)
        self.assertTrue(v.safe_summary(d)["credits_for_5s_720p_normal"])

    def test_older_remaining_credits_response(self):
        d = {"remaining_credits": [{"type": "metered", "credit_remain": 9}]}
        self.assertTrue(v.safe_summary(d)["credits_for_5s_720p_offpeak"])
        self.assertFalse(v.safe_summary(d)["credits_for_5s_720p_normal"])

    def test_zero_not_confused_with_subscriptions(self):
        d = {"remains": [{"credit_remain": 0}], "packages": [
            {"credit_remain": 1000}
        ]}
        self.assertEqual(v.available_credits(d), 0)
        self.assertFalse(v.safe_summary(d)["credits_for_5s_720p_offpeak"])

    def test_absent_or_incorrect_response_fail_closed(self):
        self.assertEqual(v.available_credits({}), 0)
        self.assertEqual(v.available_credits({"remains": "100"}), 0)
        self.assertEqual(v.available_credits({"remains": [{"credit_remain": True}]}), 0)

    def test_no_balance_or_secret_exposed(self):
        summary = v.safe_summary({"remains": [{"type": "metered", "credit_remain": 573}]})
        encoded = str(summary)
        self.assertNotIn("573", encoded)
        self.assertNotIn("metered", encoded)
        self.assertEqual(summary["spent_credits_by_this_test"], 0)
        self.assertFalse(summary["new_video_generated"])


if __name__ == "__main__":
    unittest.main()
