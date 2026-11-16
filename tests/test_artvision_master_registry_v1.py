import json
import tempfile
import unittest
from pathlib import Path
from scripts.artvision_master_registry_v1 import build, norm, status

class MasterRegistryTests(unittest.TestCase):
    def seed(self,root):
        queue=root/"queue"
        queue.mkdir(parents=True)
        (queue/"artvision_four_variants_s01_20261028.json").write_text(json.dumps({
          "groups":[{"artist":"Example Artist","artwork":"The Winter Garden","year":1901,
            "variants":{"cinema_standard":{"status":"rendered_needs_review",
                 "video_sha256":"a"*64},
                 "critico_standard":{"status":"blocked_voice"}}}]}))
        (queue/"artvision_owner_selected_ten_20261102.json").write_text('{"works":[]}')
        (queue/"artvision_owner_30_fast_quality_lane_20261109.json").write_text('{"selected_works":[]}')
        (queue/"artvision_new_series_20261114.json").write_text(json.dumps({
          "works":[{"title":"The Winter Garden","artist":"Example Artist","year":1901},
                   {"title":"The Sin","artist":"Franz von Stuck","year":1893},
                   {"title":"The Sin","artist":"Franz von Stuck","year":1912}]}))
        (queue/"artvision_autoproduction_v31_state.json").write_text('{"cycle_log":[]}')
        (queue/"extra_checkpoint_20261115_bierstadt.json").write_text(json.dumps({
          "artist":"Albert Bierstadt","title":"The Last of the Buffalo",
          "variant_matrix":{"cinema_standard":{"status":"RENDERED_TECH_QA_ART_REVIEW_PENDING",
             "preferred_v2_mp4_sha256":"b"*64}}}))
    def test_works_versions_site_and_distinct_years(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);self.seed(root)
            catalog={"items":[
                {"name":"EXAMPLE_ARTIST_THE_WINTER_GARDEN_CINEMA_STANDARD.mp4",
                 "key":"EXAMPLE_ARTIST_THE_WINTER_GARDEN_CINEMA_STANDARD.mp4",
                 "source":"cloudflare","available":True,"category":"Artisti e pittura"},
                {"name":"MYSTERY_GENERIC_123.mp4","available":False,"category":"Altri progetti"}]}
            r=build(root,catalog,"fixture","2026-11-16T10:00:00+00:00")
            self.assertEqual(r["stats"]["works"],4)
            self.assertEqual(r["stats"]["site_items"],2)
            self.assertEqual(r["stats"]["site_unavailable"],1)
            winter=next(w for w in r["works"] if w["title"]=="The Winter Garden")
            self.assertEqual(winter["variants"]["cinema_standard"]["state"],"render_documentato")
            self.assertEqual(winter["variants"]["critico_standard"]["state"],"bloccato")
            self.assertEqual(len(winter["site_candidates"]),1)
            buffalo=next(w for w in r["works"] if w["artist"]=="Albert Bierstadt")
            self.assertEqual(buffalo["variants"]["cinema_standard"]["state"],"render_documentato")
            mystery=next(x for x in r["site_items"] if "MYSTERY" in x["name"])
            self.assertEqual(mystery["artist"],"da_verificare")
    def test_no_invented_completion(self):
        self.assertEqual(status({"status":"not_started"}),"da_produrre")
        self.assertEqual(status({"status":"pending_rights"}),"in_coda_o_preflight")
        self.assertEqual(status({"status":"rendered_needs_review"}),"render_documentato")
        self.assertEqual(status({"status":"failed_upload"}),"bloccato")
    def test_normalized_titles(self):
        self.assertEqual(norm("Die Sünde"),"die sunde")

if __name__ == "__main__":
    unittest.main()
