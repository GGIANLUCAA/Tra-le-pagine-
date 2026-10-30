"""Release provenance, chronology and duplicate-slot regression tests."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import engine

class ReleaseHistoryGuardTests(unittest.TestCase):
    def releases(self):
        # Deliberately out of order, as returned by some GitHub release queries.
        return [
            {"tag_name":"wow-lab-madame-x-silhouette-v2-20261030",
             "body":"Metropolitan Museum of Art CC0, object 12127.",
             "published_at":"2026-10-30T05:54:51Z"},
            {"tag_name":"wow-lab-zhu-ling-ink-cat-v4-20261030",
             "body":"Separate Met CC0 art V4 (object ID 36075).",
             "published_at":"2026-10-30T13:05:06Z"},
            {"tag_name":"wow-lab-hiroshige-bluebird-multilayer-v3-20261030",
             "body":"Original verified Met Open Access CC0 print 36725.",
             "published_at":"2026-10-30T12:14:13Z"},
            {"tag_name":"wow-lab-sharaku-kabuki-hand-v4-20261030",
             "body":"authentic CC0 Met 37358.",
             "published_at":"2026-10-30T12:50:17Z"},
            {"tag_name":"wow-lab-madame-x-silhouette-v1-20261030",
             "body":"Metropolitan Museum of Art CC0, object 12127.",
             "published_at":"2026-10-30T05:48:51Z"},
            {"tag_name":"wow-lab-hiroshige-bluebird-36725-v1-20261030",
             "body":"The Metropolitan Museum of Art 36725 Open Access CC0.",
             "published_at":"2026-10-30T10:12:16Z"},
            {"tag_name":"wow-lab-hokusai-45434-android-20261029",
             "body":"Metropolitan Museum of Art CC0 Hokusai print 45434.",
             "published_at":"2026-10-29T22:43:34Z"},
        ]

    def test_real_legacy_release_formats_are_recognized(self):
        history=engine.parse_wow_release_history(self.releases())
        self.assertEqual([x["object_id"] for x in history],
                         [36075,37358,36725,12127,45434])

    def test_utc_publication_is_rounded_to_two_hour_slot(self):
        history=engine.parse_wow_release_history(self.releases())
        self.assertEqual([x["slot_utc"] for x in history[:3]],
                         ["20261030T12","20261030T12","20261030T12"])

    def test_duplicate_slot_is_blocked(self):
        history=engine.parse_wow_release_history(self.releases())
        with self.assertRaisesRegex(RuntimeError,"WOW_LAB_SLOT_ALREADY_RELEASED"):
            engine.ensure_slot_available("20261030T12",history)
        engine.ensure_slot_available("20261030T14",history)

    def test_unknown_object_provenance_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError,"WOW_LAB_HISTORY_UNVERIFIED"):
            engine.parse_wow_release_history([
                {"tag_name":"wow-lab-no-source-v4","body":"Just a pretty video"}])

    def test_conflicting_object_provenance_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError,"WOW_LAB_HISTORY_UNVERIFIED"):
            engine.parse_wow_release_history([
                {"tag_name":"wow-lab-conflict","body":"object ID 36075; Met 37358"}])

    def test_metadata_slot_takes_precedence_over_release_timestamp(self):
        rel=[{"tag_name":"wow-lab-v1-20261030T08",
              "body":'<!-- WOWLAB_META {"object_id":436535,"slot":"20261030T08"} -->',
              "published_at":"2026-10-30T09:10:00Z"}]
        self.assertEqual(engine.parse_wow_release_history(rel)[0]["slot_utc"],
                         "20261030T08")

if __name__=="__main__":
    unittest.main()
