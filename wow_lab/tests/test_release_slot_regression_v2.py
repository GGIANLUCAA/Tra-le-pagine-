"""Fail-closed regressions: one slot must never be reused even for V2 edits."""
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import engine

class SlotAndQueueHardening(unittest.TestCase):
    def test_duplicate_subject_different_release_slots_are_all_reserved(self):
        releases = [
            {"tag_name": "wow-lab-v1-20261030T12",
             "body": '<!-- WOWLAB_META {"object_id":400112,"slot":"20261030T12"} -->',
             "published_at": "2026-10-30T12:10:00Z"},
            {"tag_name": "wow-lab-v1-20261030T10",
             "body": '<!-- WOWLAB_META {"object_id":400112,"slot":"20261030T10"} -->',
             "published_at": "2026-10-30T10:10:00Z"},
        ]
        history = engine.parse_wow_release_history(releases)
        self.assertEqual(len(history), 1)
        self.assertEqual(set(history[0]["slots_utc"]), {"20261030T10", "20261030T12"})
        for stamp in ("20261030T10", "20261030T12"):
            with self.assertRaisesRegex(RuntimeError, "WOW_LAB_SLOT_ALREADY_RELEASED"):
                engine.ensure_slot_available(stamp, history)

    def test_naive_and_timezone_aware_release_dates_sort_without_crash(self):
        releases = [
            {"tag_name":"wow-lab-v1-20261030T08",
             "body":'<!-- WOWLAB_META {"object_id":400112,"slot":"20261030T08"} -->',
             "published_at":"2026-10-30T08:01:00"},
            {"tag_name":"wow-lab-v1-20261030T10",
             "body":'<!-- WOWLAB_META {"object_id":400113,"slot":"20261030T10"} -->',
             "published_at":"2026-10-30T10:01:00Z"},
        ]
        history = engine.parse_wow_release_history(releases)
        self.assertEqual([x["object_id"] for x in history], [400113,400112])

    def test_no_false_slot_block_for_other_hour(self):
        history = [{"object_id":400112,"tag":"wow-lab-v1-20261030T10",
                    "slot_utc":"20261030T10","slots_utc":["20261030T10"]}]
        engine.ensure_slot_available("20261030T14", history)

    def test_github_actions_queue_missing_token_fails_closed(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN":""}):
            with self.assertRaisesRegex(RuntimeError,"WOW_LAB_QUEUE_UNVERIFIED"):
                engine.get_json("https://api.github.com/repos/GGIANLUCAA/Tra-le-pagine-/actions/runs?status=queued")

    def test_museum_request_does_not_use_github_token(self):
        with patch.object(engine, "get_bytes", return_value=b'{"isPublicDomain":true}') as read:
            with patch.dict(os.environ, {"GITHUB_TOKEN":"test-secret"}):
                self.assertTrue(engine.get_json("https://collectionapi.metmuseum.org/public/collection/v1/objects/400112")["isPublicDomain"])
            read.assert_called_once()

if __name__=="__main__":
    unittest.main()
