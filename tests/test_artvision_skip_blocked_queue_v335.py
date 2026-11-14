import unittest
from src.artvision_skip_blocked_queue_v335 import select_next, record_block

class SkipBlockedTests(unittest.TestCase):
    def test_blocked_voice_does_not_stop_cinema(self):
        jobs=[{"id":"critico","status":"BLOCKED_VOICE_GACRUX"},{"id":"cinema","status":"READY"}]
        self.assertEqual(select_next(jobs)["id"],"cinema")
    def test_blocked_museum_does_not_stop_independent_job(self):
        jobs=[{"id":"museum","status":"BLOCKED_ASSETS"},{"id":"rivive","status":"QUEUED"}]
        self.assertEqual(select_next(jobs)["id"],"rivive")
    def test_dependency_is_not_bypassed(self):
        jobs=[{"id":"voice","status":"BLOCKED"},{"id":"critico","status":"READY","dependencies":["voice"]},{"id":"cinema","status":"READY"}]
        self.assertEqual(select_next(jobs)["id"],"cinema")
    def test_no_duplicates_within_cycle(self):
        jobs=[{"id":"a","status":"READY"},{"id":"b","status":"READY"}]
        self.assertEqual(select_next(jobs,{"a"})["id"],"b")
    def test_no_work_returns_none(self):
        self.assertIsNone(select_next([{"id":"a","status":"BLOCKED"}]))
    def test_record_block_does_not_mutate(self):
        original={"id":"a","status":"READY"}
        blocked=record_block(original,"missing assets")
        self.assertEqual(original["status"],"READY")
        self.assertEqual(blocked["block_reason"],"missing assets")
    def test_duplicate_ids_rejected(self):
        with self.assertRaises(ValueError):
            select_next([{"id":"a","status":"READY"},{"id":"a","status":"READY"}])
if __name__ == "__main__":
    unittest.main()
