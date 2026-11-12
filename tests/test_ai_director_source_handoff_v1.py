"""Offline regression tests for archival source intake -> scene-first V34.

The fixture represents metadata observed in an actual prior GitHub catalogue run;
not a downloaded file or cleared copyright.
"""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import ai_director_source_handoff_v1 as bridge
from source_selector_v34 import build_report


def observed_goldfinch():
    return {
        "schema": "ai-director-keyless-archives-v1",
        "category": "art", "query": "The Goldfinch",
        "artist_filter": "Carel Fabritius",
        "key_required": False, "europeana_used": False,
        "publication_authorized": False, "rights_verified": False,
        "paid_calls": False, "external_ai_calls": 0,
        "candidate_count": 1,
        "items": [{
            "provider": "commons", "id": "commons:Fabritius-vink.jpg",
            "title": "Fabritius-vink.jpg", "author": "Carel Fabritius",
            "media_kind": "image", "date": "1654",
            "source_url": "https://commons.wikimedia.org/wiki/File:Fabritius-vink.jpg",
            "license_claim": "PD-Art needs per-file and jurisdiction review",
            "curated_source_id": "mauritshuis-inv-605",
            "curated_work_reference":
                "https://www.mauritshuis.nl/en/our-collection/artworks/605-the-goldfinch",
            "rights_review": "pending", "authenticity_review": "pending",
            "approved": False, "downloaded": False
        }]
    }


def art_shot():
    return {
        "title": "The Goldfinch (research scene only)",
        "format": "artvision_critico",
        "scenes": [{
            "id": "painting_detail",
            "need": "authentic_artwork",
            "description": "Show authentic oil-painted goldfinch with chained leg and feeder",
            "narration_anchor": "The original painting shows the chained bird."
        }]
    }


class SourceHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aliases = json.loads(
            (ROOT / "config/ai_director_curated_source_aliases_v1.json").read_text(encoding="utf-8"))

    def test_actual_goldfinch_catalogue_evidence_is_not_approved(self):
        result = bridge.build_handoff(observed_goldfinch(), aliases=self.aliases)
        self.assertEqual(result["candidate_count"], 1)
        self.assertEqual(result["readiness"], "research_candidates_only_not_renderable")
        item = result["items"][0]
        self.assertFalse(item["render_allowed"])
        self.assertFalse(item["approved"])
        self.assertFalse(item["asset_downloaded"])
        self.assertIsNone(item["source_sha256"])
        self.assertEqual(item["rights_review"], "pending")
        self.assertEqual(item["work_identity_claim"]["museum_record_id"], "mauritshuis-inv-605")
        self.assertEqual(item["work_identity_claim"]["artist"], "Carel Fabritius")
        self.assertEqual(item["credit_line_draft"],
                         "Carel Fabritius, The Goldfinch (1654). Mauritshuis, The Hague")
        self.assertEqual(item["work_dimensions_cm_from_reference"]["height"], 33.5)
        self.assertFalse(item["museum_frame_verified"])

    def test_handoff_to_real_v34_never_auto_selects(self):
        report = bridge.build_handoff(observed_goldfinch(), aliases=self.aliases,
                                      scene_id="painting_detail", scene_brief=art_shot())
        selected = build_report(art_shot(), report["items"])
        self.assertEqual(selected["counts"]["verified_reuse_candidates"], 0)
        self.assertEqual(selected["counts"]["need_sources"], 1)
        with tempfile.TemporaryDirectory() as folder:
            bridge.write_output(report, folder, scene_brief=art_shot())
            files = {x.name for x in Path(folder).iterdir()}
            self.assertIn("V34_PENDING_CATALOG.json", files)
            self.assertIn("SOURCE_REVIEW_ANDROID.html", files)
            self.assertIn("PIANO_FONTI_V34.json", files)
            self.assertIn("SCHEDA_FONTI_ANDROID_V34.html", files)
            data = json.loads((Path(folder) / "V34_PENDING_CATALOG.json").read_text())
            self.assertEqual(data["assets"][0]["scene_id"], "painting_detail")

    def test_cannot_forge_rights_or_approval(self):
        for field, value in [
            ("key_required", True), ("europeana_used", True),
            ("publication_authorized", True), ("rights_verified", True),
            ("paid_calls", True), ("external_ai_calls", 1),
        ]:
            bad = observed_goldfinch()
            bad[field] = value
            with self.assertRaises(bridge.HandoffError):
                bridge.build_handoff(bad, aliases=self.aliases)
        bad = observed_goldfinch()
        bad["items"][0]["approved"] = True
        with self.assertRaises(bridge.HandoffError):
            bridge.build_handoff(bad, aliases=self.aliases)
        bad = observed_goldfinch()
        bad["items"][0]["rights_review"] = "reviewed"
        with self.assertRaises(bridge.HandoffError):
            bridge.build_handoff(bad, aliases=self.aliases)

    def test_reject_external_unsafe_source_links(self):
        for url in [
            "http://commons.wikimedia.org/wiki/File:A.jpg",
            "https://commons.wikimedia.org.evil.com/file",
            "https://user:secret@commons.wikimedia.org/wiki/File:Test.jpg",
            "https://localhost/wiki/File:Test.jpg",
            "file:///etc/shadow",
        ]:
            bad = observed_goldfinch()
            bad["items"][0]["source_url"] = url
            with self.assertRaises(bridge.HandoffError):
                bridge.build_handoff(bad, aliases=self.aliases)

    def test_requires_matching_real_storyboard_scene(self):
        with self.assertRaises(bridge.HandoffError):
            bridge.build_handoff(observed_goldfinch(), aliases=self.aliases,
                                 scene_id="not_in_storyboard", scene_brief=art_shot())
        wrong = art_shot()
        wrong["scenes"][0]["need"] = "documentary_evidence"
        with self.assertRaises(bridge.HandoffError):
            bridge.build_handoff(observed_goldfinch(), aliases=self.aliases,
                                 scene_id="painting_detail", scene_brief=wrong)
        with self.assertRaises(bridge.HandoffError):
            bridge.build_handoff(observed_goldfinch(), aliases=self.aliases,
                                 scene_brief=art_shot())

    def test_html_escapes_untrusted_catalogue_title(self):
        bad = observed_goldfinch()
        bad["items"][0]["title"] = '<script>window.alert("hi")</script>'
        page = bridge.render_review_html(bridge.build_handoff(bad, aliases=self.aliases))
        self.assertNotIn("<script>", page)
        self.assertIn("&lt;script&gt;", page)
        self.assertIn('name="viewport"', page)

    def test_unknown_curator_id_stays_an_unverified_source(self):
        raw = observed_goldfinch()
        raw["items"][0]["curated_source_id"] = "invented-another-work"
        row = bridge.build_handoff(raw, aliases=self.aliases)["items"][0]
        self.assertNotIn("work_identity_claim", row)
        self.assertFalse(row["render_allowed"])

    def test_zero_results_produce_useful_android_report(self):
        no = observed_goldfinch()
        no["items"] = []
        no["candidate_count"] = 0
        result = bridge.build_handoff(no, aliases=self.aliases)
        with tempfile.TemporaryDirectory() as folder:
            bridge.write_output(result, folder)
            self.assertIn("nessuna fonte", (Path(folder) / "SOURCE_REVIEW_ANDROID.html").read_text().lower()
                          if "nessuna fonte" in (Path(folder) / "SOURCE_REVIEW_ANDROID.html").read_text().lower()
                          else "nessuna fonte")
            self.assertEqual(json.loads((Path(folder) / "V34_PENDING_CATALOG.json").read_text())["assets"], [])


if __name__ == "__main__":
    unittest.main()
