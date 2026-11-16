import json
import tempfile
import unittest
from pathlib import Path
from scripts.artvision_master_registry_v1 import build, norm, status, checkpoint_evidence, title_key

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
    def test_legacy_ten_versions_research_and_dossiers(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);self.seed(root)
            queue=root/"queue"
            (queue/"artvision_owner_selected_ten_20261102.json").write_text(json.dumps({
              "works":[{"artist":"Example Old Master","title_en":"The Night Light","year":1902,
                "slots_delivered_this_selection":4,
                "cinema_standard_v155":{"status":"REAL_MP4_VERIFIED","sha256":"1"*64},
                "critico_standard_v156":{"status":"REAL_MP4_VERIFIED","sha256":"2"*64},
                "critico_museum_v164":{"sha256":"3"*64},
                "cinema_museum_v166":{"sha256":"4"*64}},
               {"artist":"Example Other","title_en":"The Old Tower",
                "v134_cinema_candidate":{"mp4_sha256":"5"*64,"mp4_filename":"old.mp4",
                     "status":"real_mp4_artifact_downloaded"}}]}))
            research=root/"research";research.mkdir()
            (research/"artvision_future_works_index_v1_20261107.json").write_text(json.dumps({
              "works":[{"catalog_id":1,"artist":"Future Artist","title":"Future Work",
                "pixel_file_license_status":"unverified"}]}))
            (research/"artvision_owner_selected_30_future_20261109.json").write_text(json.dumps({
              "works":[{"selection_order":1,"artist_as_chosen":"Future Artist",
                "title_as_chosen":"Future Work","current_stage":"pending"}]}))
            target=root/"docs/productions/sample";target.mkdir(parents=True)
            (target/"README.md").write_text("Technical information only")
            (queue/"storia_rivive_v69_film_scouting_candidates.json").write_text(
              '{"items":[{"title":"A Trip Down Main Street","year":1906}]}')
            d=build(root,{"items":[]},"fixture","2026-11-16T10:00:00+00:00")
            night=next(w for w in d["works"] if w["title"]=="The Night Light")
            self.assertEqual(night["render_documented"],4)
            tower=next(w for w in d["works"] if w["title"]=="The Old Tower")
            self.assertEqual(tower["variants"]["cinema_standard"]["state"],"render_documentato")
            self.assertEqual(d["stats"]["research_100"],1)
            self.assertEqual(d["stats"]["selected_future_30"],1)
            self.assertEqual(d["stats"]["production_dossiers"],1)
            self.assertEqual(len(d["history_candidates"]),1)
            self.assertNotIn("Future Work",[w["title"] for w in d["works"]])
    def test_rejected_voice_never_completed(self):
        self.assertEqual(status({"status":"OWNER_REJECTED_WRONG_NARRATION_VOICE__TECHNICAL_ARTIFACT_ONLY",
                                "sha256":"a"*64}),"render_respinto")
    def test_legacy_checkpoint_evidence_schema_variants(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);self.seed(root);q=root/"queue"
            examples=[
                ("golden",{"work":{"artist":"Edward Burne-Jones","title":"The Golden Stairs",
                    "variant":"cinema_standard","state":"RENDERED_TECHNICALLY_VERIFIED"},
                    "qa":{"mp4_sha256":"1"*64,"ffmpeg_full_decode":"PASS_VIDEO_AUDIO"}}),
                ("apparition",{"secondary_work":{"artist":"Gustave Moreau","selected_title":"The Apparition",
                    "variant":"cinema_standard"},"mp4":{"sha256":"2"*64,
                    "ffmpeg_full_audio_decode":"PASS"}}),
                ("fish",{"artist":"Paul Klee","title":"Fish Magic","variant":"cinema_standard",
                    "render":{"hq_720":{"sha256":"3"*64},"h264_aac_full_decode":"PASS"}}),
                ("dead_mother",{"artist":"Edvard Munch","owner_title":"The Dead Mother and Child",
                    "variant":"cinema_standard","video":{"sha256":"4"*64},
                    "technical_qa":{"local_full_ffmpeg_decode":"PASS"}}),
                ("unknown",{"artist":"Unverified Artist","title":"Unverified Claim",
                    "variant":"cinema_standard","status":"NEW_REAL_MP4_REVIEW",
                    "production":{"mp4_hd_sha256":"5"*64},"qa":{"full_ffmpeg_decode":"PENDING"}}),
                ("rejected",{"artist":"Evelyn De Morgan","owner_title":"The Dryad",
                    "variant":"critico_standard","status":"OWNER_REJECTED_WRONG_NARRATION_VOICE",
                    "mp4":{"sha256":"6"*64,"all_streams_ffmpeg_full_decode":"PASS"}})
            ]
            for name,record in examples:
                (q/("owner_"+name+"_checkpoint.json")).write_text(json.dumps(record))
            d=build(root,{"items":[]},"fixture","2026-11-16T10:00:00+00:00")
            for artist,title in [("Edward Burne-Jones","The Golden Stairs"),
                ("Gustave Moreau","The Apparition"),("Paul Klee","Fish Magic"),
                ("Edvard Munch","The Dead Mother and Child")]:
                w=next(w for w in d["works"] if w["artist"]==artist and w["title"]==title)
                self.assertEqual(w["variants"]["cinema_standard"]["state"],"render_documentato",title)
            bad=next(w for w in d["works"] if w["title"]=="Unverified Claim")
            self.assertNotEqual(bad["variants"]["cinema_standard"]["state"],"render_documentato")
            dryad=next(w for w in d["works"] if w["title"]=="The Dryad")
            self.assertEqual(dryad["variants"]["critico_standard"]["state"],"render_respinto")
    def test_declared_hash_needs_qa_evidence(self):
        item={"status":"RENDERED_REAL_MP4","production":{"mp4_hd_sha256":"a"*64},
              "qa":{"ffmpeg_full_decode":"PENDING"}}
        self.assertEqual(checkpoint_evidence(item)["status"],"UNVERIFIED_CHECKPOINT_REQUIRES_MEDIA_PROOF")
        item["qa"]["ffmpeg_full_decode"]="PASS"
        self.assertEqual(checkpoint_evidence(item)["mp4_sha256"],"a"*64)
    def test_normalized_titles(self):
        self.assertEqual(norm("Die Sünde"),"die sunde")
        self.assertEqual(title_key("The Vampire"),title_key("Vampire"))
        self.assertNotEqual(title_key("The Sin"),title_key("The Shipwreck"))
    def test_checkpoint_vampire_matches_owner_selected_article_alias(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);self.seed(root)
            q=root/"queue"
            (q/"artvision_owner_30_fast_quality_lane_20261109.json").write_text(json.dumps({
                "selected_works":[{"artist_as_chosen":"Edvard Munch","title_as_chosen":"The Vampire"}]}))
            (q/"artvision_owner_30_render_checkpoint_vampire.json").write_text(json.dumps({
                "artist":"Edvard Munch","work":"Vampire","variant":"cinema_standard",
                "mp4":{"sha256":"a"*64},"qa":{"local_ffmpeg_all_streams":"PASS"}}))
            d=build(root,{"items":[]},"fixture","2026-11-16T10:00:00+00:00")
            w=[x for x in d["works"] if x["artist"]=="Edvard Munch"]
            self.assertEqual(len(w),1)
            self.assertEqual(w[0]["variants"]["cinema_standard"]["state"],"render_documentato")

if __name__ == "__main__":
    unittest.main()
