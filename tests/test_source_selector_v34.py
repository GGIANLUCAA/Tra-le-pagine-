"""V34 tests do not call external services or expose GitHub Secrets."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
import source_selector_v34 as sel


def sample(fmt="libri", kind="fictional_action", ident="001"):
    return {"title":"Test", "format":fmt, "scenes":[
        {"id":ident,"need":kind,"description":"The same heroine opens a small golden door",
         "narration_anchor":"La protagonista apre la porta."}
    ]}


def approved(**updates):
    x={"id":"asset-saved", "scene_id":"001", "source_kind":"approved_library",
       "provider":"studio_library", "source_reference":"approved/scene_001.jpg",
       "rights_review":"reviewed", "visual_review":"passed",
       "scene_relevance":"reviewed", "media_kind":"image",
       "sha256":"aaaa"*16}
    x.update(updates)
    return x


class SelectorV34Tests(unittest.TestCase):
    def test_offline_plan_no_api_and_correct_format(self):
        with patch.object(sel, "discover_single", side_effect=AssertionError("network unexpectedly called")):
            r=sel.build_report(sample(), [])
        self.assertEqual(r["counts"]["need_sources"],1)
        self.assertTrue(r["no_auto_publish"])
        self.assertTrue(r["no_api_calls_by_default"])
        self.assertIn("ai_horde_manual_three_scene_trial",r["scenes"][0]["recommended_path"])
        self.assertFalse(r["scenes"][0]["automatic_generation"])

    def test_exact_reviewed_asset_reused(self):
        r=sel.build_report(sample(),[approved()])
        self.assertEqual(r["counts"]["verified_reuse_candidates"],1)
        self.assertEqual(r["scenes"][0]["approved_candidate"]["source_kind"],"approved_library")

    def test_generic_approved_asset_not_used_for_different_scene(self):
        r=sel.build_report(sample(),[approved(scene_id="something_else")])
        self.assertEqual(r["counts"]["need_sources"],1)

    def test_no_unreviewed_reuse(self):
        for bad in [{"rights_review":"pending"},{"visual_review":"pending"},
                    {"scene_relevance":"pending"},{"source_reference":""}]:
            r=sel.build_report(sample(),[approved(**bad)])
            self.assertEqual(r["counts"]["need_sources"],1)

    def test_stock_not_falsely_matching_specific_fictional_action(self):
        item=approved(source_kind="pixabay_stock",provider="pixabay",
                      source_reference="https://pixabay.com/photos/garden-42/")
        r=sel.build_report(sample(),[item])
        self.assertEqual(r["counts"]["need_sources"],1)

    def test_artwork_only_authentic_verified(self):
        p=sample("artvision_critico","authentic_artwork")
        for item in [approved(source_kind="ai_horde_original"),
                     approved(source_kind="authentic_artwork",authenticity_review="pending"),
                     approved(source_kind="pixabay_stock",authenticity_review="reviewed")]:
            self.assertEqual(sel.build_report(p,[item])["counts"]["need_sources"],1)
        art=approved(source_kind="authentic_artwork",authenticity_review="reviewed")
        self.assertEqual(sel.build_report(p,[art])["counts"]["verified_reuse_candidates"],1)

    def test_documentary_evidence_no_stock_no_ai(self):
        p=sample("controluce","documentary_evidence")
        for kind in ("pixabay_stock","ai_horde_original","original_illustration"):
            self.assertEqual(sel.build_report(p,[approved(source_kind=kind)])["counts"]["need_sources"],1)
        genuine=approved(source_kind="verified_archive",authenticity_review="reviewed")
        self.assertEqual(sel.build_report(p,[genuine])["counts"]["verified_reuse_candidates"],1)

    def test_establishing_uses_stock_when_verified(self):
        p=sample("libri","establishing")
        item=approved(source_kind="pixabay_stock",provider="pixabay",
                      source_reference="https://pixabay.com/photos/landscape-123/")
        self.assertEqual(sel.build_report(p,[item])["counts"]["verified_reuse_candidates"],1)

    def test_music_needs_sync_review(self):
        p=sample("visual_music","music_visual")
        self.assertEqual(sel.build_report(p,[approved()])["counts"]["need_sources"],1)
        self.assertEqual(sel.build_report(p,[approved(sync_review="passed")])["counts"]["need_sources"],0)

    def test_duplicate_files_deduplicated(self):
        p=sample()
        r=sel.build_report(p,[approved(id="a"),approved(id="b")])
        self.assertEqual(r["scenes"][0]["reviewed_candidates"],1)

    def test_provider_not_called_for_specific_book_scene(self):
        p=sample()
        with patch("free_sources_bridge_v1.produce", side_effect=AssertionError("Unexpected service")):
            with self.assertRaisesRegex(sel.SelectionError, "non adatta"):
                sel.discover_single(p,[],"001","pixabay","garden",3)

    def test_explicit_single_search_sanitized_and_not_approved(self):
        p=sample("libri","establishing")
        candidates=[{"id":123,"provider":"pixabay","source_url":"https://pixabay.com/photos/city-123/",
                     "kind":"image","title":"Foggy landscape"}]
        with patch("free_sources_bridge_v1.produce",return_value={"items":candidates}) as called:
            report, details=sel.discover_single(p,[],"001","pixabay","old town",3,{"PIXABAY":"secret-value"})
        called.assert_called_once()
        self.assertEqual(details["new_api_calls"],1)
        self.assertEqual(details["results"][0]["rights_review"],"pending")
        self.assertEqual(report["counts"]["need_sources"],1)
        self.assertNotIn("secret-value",str(details))

    def test_reject_unknown_format_or_duplicate_scene(self):
        bad=sample()
        bad["scenes"].append(dict(bad["scenes"][0]))
        with self.assertRaises(sel.SelectionError):
            sel.build_report(bad,[])
        with self.assertRaises(sel.SelectionError):
            sel.build_report(sample("mystery"),[])

    def test_html_is_mobile_and_escapes_input(self):
        p=sample()
        p["scenes"][0]["description"]="Character <script> does not appear in the scene"
        h=sel.render_html(sel.build_report(p,[]))
        self.assertIn('name="viewport"',h)
        self.assertNotIn("<script>",h)
        self.assertIn("&lt;script&gt;",h)

    def test_case_specific_status_from_demo(self):
        demo=sel.read_json(ROOT/"config/source_selector_v34_demo.json")
        r=sel.build_report(demo,[])
        self.assertEqual(r["counts"]["scenes"],2)
        self.assertEqual(r["scenes"][0]["need"],"documentary_evidence")
        self.assertEqual(r["scenes"][1]["recommended_path"][2],"pixabay_single_search")


if __name__=="__main__":
    unittest.main()
