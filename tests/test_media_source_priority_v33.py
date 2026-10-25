"""Offline tests: V33 per-format priority and mandatory provenance gate."""
import json
import unittest
from pathlib import Path

from src.media_source_priority_v33 import policy, proposal, check
from src.editorial_rules import new_plan


def project(kind, decisions):
    p = new_plan()
    p["media_sourcing"] = {"policy_id": policy()["id"], "review_status": "reviewed",
                          "decisions": decisions}
    return {"format": kind, "editorial_plan": p}


def asset(aid="scene01", src="ai_horde_original", role=None):
    d = {"asset_id": aid, "source_kind": src, "provider": "test-provider",
         "source_reference": "https://example.invalid/item/license-reviewed",
         "choice_reason": "Better matches narrated action than generic stock",
         "scene_match_note": "Exactly depicts the required moment without extra objects",
         "rights_review": "reviewed", "scene_relevance": "reviewed",
         "visual_review": "passed"}
    if role:
        d["role_in_video"] = role
    return d


class MediaV33Tests(unittest.TestCase):
    def test_01_policy_is_shared_with_editorial_config(self):
        p = policy()
        self.assertEqual(p["id"], "media-priority-v33")
        self.assertEqual(p["provider_registry"]["pixabay"]["credential"], "PIXABAY")
        self.assertEqual(p["provider_registry"]["pixabay"]["official_name"], "Pixabay")
        self.assertEqual(p["provider_registry"]["ai_horde"]["status"], "prototype_three_images_manual_only")
        self.assertFalse(p["provider_registry"]["ai_horde"]["secondary_key_active"])
        self.assertTrue(p["no_premium_default"])
        self.assertEqual(p["default_cash_budget_eur"], 0)

    def test_02_choice_depends_on_format(self):
        book = proposal("libri")
        cinema = proposal("artvision_cinema")
        self.assertEqual(book["recommended_sequence"][1], "original_ai_illustrations_for_specific_actions")
        self.assertEqual(cinema["recommended_sequence"][0], "authentic_verified_original_artworks")
        self.assertNotEqual(book["recommended_sequence"], cinema["recommended_sequence"])

    def test_03_new_plan_pending_not_falsely_approved(self):
        p = new_plan()["media_sourcing"]
        self.assertEqual(p["policy_id"], "media-priority-v33")
        self.assertEqual(p["review_status"], "pending")
        self.assertEqual(p["decisions"], [])

    def test_04_no_images_requires_no_decisions_yet(self):
        self.assertEqual(check(project("libri", []), set()), [])

    def test_05_provenance_required_for_every_visual(self):
        errors = check(project("libri", [asset("scene01")]), {"scene01", "scene02"})
        self.assertTrue(any("scene02" in e for e in errors))

    def test_06_no_auto_approval(self):
        p = project("libri", [asset()])
        p["editorial_plan"]["media_sourcing"]["review_status"] = "pending"
        self.assertTrue(any("revisione fonti" in e for e in check(p, {"scene01"})))

    def test_07_rights_and_visual_reviews_required(self):
        d = asset()
        d["rights_review"] = "pending"
        d["visual_review"] = "pending"
        errs = check(project("libri", [d]), {"scene01"})
        self.assertTrue(any("diritti" in x for x in errs))
        self.assertTrue(any("revisione visuale" in x for x in errs))

    def test_08_duplicate_decision_cannot_be_used(self):
        errs = check(project("libri", [asset(), asset()]), {"scene01"})
        self.assertTrue(any("duplicata" in x for x in errs))

    def test_09_books_allow_original_illustrations_when_reviewed(self):
        self.assertEqual(check(project("libri", [asset()]), {"scene01"}), [])

    def test_10_artvision_refuses_fake_ai_as_authentic_art(self):
        errs = check(project("artvision_cinema", [asset()]), {"scene01"})
        self.assertTrue(any("opera originale" in x for x in errs))
        self.assertEqual(check(project("artvision_cinema", [asset(src="authentic_artwork")]),
                               {"scene01"}), [])

    def test_11_documentary_requires_labelled_reconstruction(self):
        errs = check(project("controluce", [asset()]), {"scene01"})
        self.assertTrue(any("non etichettata" in x for x in errs))
        self.assertEqual(check(project("controluce", [asset(role="labelled_supporting_reconstruction")]),
                               {"scene01"}), [])

    def test_12_missing_reference_blocks(self):
        d=asset()
        d["source_reference"]=""
        self.assertTrue(any("source_reference" in x for x in
                            check(project("libri", [d]), {"scene01"})))

if __name__ == "__main__":
    unittest.main()
