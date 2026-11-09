import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from studio_cycle_handoff_v1 import SCHEMA, handoff, load, research_summary


def research(project="artvision", state="RESEARCH_CANDIDATES_PENDING_REVIEW"):
    is_candidate = state == "RESEARCH_CANDIDATES_PENDING_REVIEW"
    return {
        "schema": "source-cycle-companion-v4",
        "project": project,
        "cycle_utc": "2026-11-10T03:00:00+00:00",
        "cycle_id": "20261110T0300Z",
        "item_id": "the_magic_circle" if project == "artvision" else "historic_venice",
        "owner": "ARTVISION_OWNER_SELECTED_TEN_V128" if project == "artvision" else "STORIA_V101",
        "rights_checked": False, "auto_download": False,
        "auto_render": False, "auto_publish": False,
        "paid_api_calls": 0, "approved_assets": 0,
        "status": state,
        "candidates": ([{
            "rights_review": "pending", "approved": False,
            "review_required": True,
            "source_reference": "https://example.org/archival-candidate"
        }] if is_candidate else []),
    }


def order():
    return {
        "contract": "LA_STORIA_RIVIVE_V101_SAFE_AUTOPILOT",
        "episode_id": "historic_venice",
        "cycle_id": "storia-20261110-0300",
        "cycle_utc": "2026-11-10T03:00:00+00:00",
        "blocking_issues": ["SOURCE_VIDEO_SHA_NOT_VERIFIED"],
        "video_completed": False,
        "publish_permitted": False, "paid_api_call_permitted": False,
    }


def cycle():
    return {
        "cycle_id": "storia-20261110-0300",
        "candidate": "historic_venice",
        "source_research_v4_status": "RESEARCH_CANDIDATES_PENDING_REVIEW",
        "finished_mp4": False, "published": False,
        "charged_api_requests": 0,
    }


class StudioCycleHandoffTests(unittest.TestCase):
    def test_artvision_candidates_are_not_video_or_approved_assets(self):
        d = handoff("artvision", research(), run_id="42717357437")
        self.assertEqual(d["schema"], SCHEMA)
        self.assertEqual(d["state"], "SOURCE_CANDIDATE_NEEDS_REVIEW")
        self.assertEqual(d["candidate_count"], 1)
        self.assertEqual(d["item_id"], "the_magic_circle")
        self.assertTrue(d["evidence"]["research_report"])
        self.assertEqual(d["new_finished_mp4"], 0)
        for k in ("auto_render_started", "auto_publish_authorized",
                  "owner_artistic_approved", "paid_api_calls_authorized",
                  "master_mp4_verified_by_handoff",
                  "source_rights_verified_by_handoff"):
            self.assertFalse(d[k], k)
        self.assertIn("actions/runs/42717357437", d["run_url"])

    def test_artvision_no_match_goes_to_next_source_not_fictitious_success(self):
        d = handoff("artvision", research(state="NO_MATCH"))
        self.assertEqual(d["state"], "NO_SOURCE_MATCH")
        self.assertEqual(d["next_action"], "try_next_independent_source")
        self.assertEqual(d["candidate_count"], 0)

    def test_artvision_api_failed_has_no_automatic_retry(self):
        d = handoff("artvision", research(state="API_FAILED_NO_RETRY"))
        self.assertEqual(d["state"], "RESEARCH_NOT_READY")
        self.assertFalse(d["automatic_retry_started"])

    def test_unknown_or_missing_research_is_safe(self):
        self.assertEqual(handoff("artvision", None)["state"], "EVIDENCE_INCOMPLETE")
        wrong = research()
        wrong["project"] = "storia"
        self.assertFalse(handoff("artvision", wrong)["evidence"]["research_report"])
        wrong = research()
        wrong["auto_publish"] = True
        self.assertFalse(handoff("artvision", wrong)["evidence"]["research_report"])
        wrong = research()
        wrong["paid_api_calls"] = 1
        self.assertFalse(handoff("artvision", wrong)["evidence"]["research_report"])

    def test_storia_preflight_is_not_a_new_video(self):
        d = handoff("storia", research("storia"), order(), cycle())
        self.assertEqual(d["state"], "SOURCE_CANDIDATE_NEEDS_REVIEW")
        self.assertTrue(all(d["evidence"].values()))
        self.assertIn("SOURCE_VIDEO_SHA_NOT_VERIFIED", d["reported_blocker_codes"])
        self.assertFalse(d["auto_render_started"])
        self.assertEqual(d["new_finished_mp4"], 0)

    def test_storia_works_without_optional_source_lookup_but_not_ready(self):
        d = handoff("storia", None, order(), cycle())
        self.assertEqual(d["state"], "PREPARATION_ONLY_NO_VERIFIED_RESEARCH")
        self.assertFalse(d["evidence"]["research_report"])
        self.assertTrue(d["evidence"]["cycle_status"])

    def test_mismatched_cycle_never_promotes_stale_research(self):
        stale = research("storia")
        stale["cycle_utc"] = "2026-11-09T21:00:00+00:00"
        d = handoff("storia", stale, order(), cycle())
        self.assertEqual(d["state"], "PREPARATION_ONLY_NO_VERIFIED_RESEARCH")
        self.assertEqual(d["new_finished_mp4"], 0)
        bad_cycle = cycle()
        bad_cycle["candidate"] = "some_other_film"
        d = handoff("storia", research("storia"), order(), bad_cycle)
        self.assertEqual(d["state"], "EVIDENCE_INCOMPLETE")

    def test_unverified_artistic_approval_or_charges_are_rejected(self):
        r = research("artvision")
        r["candidates"][0]["approved"] = True
        self.assertEqual(research_summary(r, "artvision")["state"], "MISSING_OR_INVALID")
        r = research("artvision")
        r["candidates"][0]["rights_review"] = "approved"
        self.assertEqual(research_summary(r, "artvision")["state"], "MISSING_OR_INVALID")
        c = cycle()
        c["charged_api_requests"] = 1
        self.assertEqual(handoff("storia", research("storia"), order(), c)["state"],
                         "EVIDENCE_INCOMPLETE")

    def test_url_is_from_valid_run_id_only(self):
        d = handoff("artvision", research(), run_id="https://evil.example")
        self.assertIsNone(d["run_url"])
        self.assertNotIn("evil", json.dumps(d))

    def test_bad_json_is_not_an_empty_approval(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "RESEARCH_REPORT.json"
            self.assertIsNone(load(p))
            p.write_text("not json", encoding="utf-8")
            self.assertIsNone(load(p))
            p.write_text(json.dumps(research()), encoding="utf-8")
            self.assertEqual(load(p)["schema"], "source-cycle-companion-v4")


if __name__ == "__main__":
    unittest.main()
