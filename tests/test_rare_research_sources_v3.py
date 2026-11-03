"""Ten no-key primary research sources; all tests run offline with fake HTTP."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit,parse_qs

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import rare_research_sources_v3 as src
import source_selector_v34 as selector

UUID_M="c88b3df0-de91-4f5b-a9ef-7b2b9a6d8abb"
UUID_P="09539ab1-416d-3870-810b-8a6b3b604368"

class RareV3Tests(unittest.TestCase):
    def test_ten_unique_providers(self):
        self.assertEqual(len(src.PROVIDERS),10)
    def test_validation_prevents_outbound_request(self):
        for provider,q,limit in [
            ("bad","landscape",1),("finna","a",1),("rijks","fine\nart",1),
            ("crossref","historical art",6),("getty_museum","Van Gogh",1),
        ]:
            with self.assertRaises(src.ResearchError):
                src.search(provider,q,limit,lambda u:self.fail("HTTP"))
    def test_rijks_returns_only_identifiers(self):
        def fake(u):
            p=parse_qs(urlsplit(u).query)
            self.assertEqual(p["title"],["Night Watch"])
            self.assertEqual(p["imageAvailable"],["true"])
            return {"orderedItems":[{"id":"https://id.rijksmuseum.nl/200100988"},
                                    {"id":"http://localhost/injection"}]}
        r=src.search("rijks","Night Watch",2,fake)
        self.assertEqual(len(r["items"]),1)
        self.assertEqual(r["items"][0]["media_kind"],"image_candidate")
        self.assertEqual(r["items"][0]["rights_review"],"pending")
    def test_finna_requested_small_field_set(self):
        def fake(u):
            p=parse_qs(urlsplit(u).query)
            self.assertEqual(p["lookfor"],["Simberg"])
            self.assertIn("title",p["field[]"])
            return {"records":[{"id":"museo.123","title":"Garden of Death",
                                 "year":"1896"}]}
        r=src.search("finna","Simberg",1,fake)
        self.assertEqual(len(r["items"]),1)
        self.assertIn("finna.fi/Record/museo.123",r["items"][0]["source_url"])
    def test_getty_exact_uuid_museum_and_provenance(self):
        for provider,ident in [("getty_museum",UUID_M),("getty_provenance",UUID_P)]:
            def fake(u):
                self.assertIn(ident,u)
                return {"id":u,"identified_by":[{"type":"Name","content":"Historic portrait"}]}
            with self.subTest(provider=provider):
                r=src.search(provider,ident,1,fake)
                self.assertEqual(r["items"][0]["title"],"Historic portrait")
                self.assertEqual(r["items"][0]["media_kind"],"metadata")
                self.assertEqual(r["items"][0]["rights_review"],"pending")
    def test_wikidata_entity_not_automatic_evidence(self):
        r=src.search("wikidata","Rembrandt",1,lambda u:{"search":[{
            "id":"Q5598","label":"Rembrandt","description":"Dutch painter"},
            {"id":"BAD","label":"bad"}]})
        self.assertEqual(len(r["items"]),1)
        self.assertFalse(r["items"][0]["approved"])
    def test_openverse_audio_metadata_not_audio_file(self):
        r=src.search("openverse_audio","train station",1,lambda u:{"results":[{
            "id":"abc-def","title":"Train","creator":"Anon","license":"by",
            "foreign_landing_url":"https://freesound.org/people/x/sounds/123"}]})
        self.assertEqual(len(r["items"]),1)
        self.assertEqual(r["items"][0]["media_kind"],"audio")
        self.assertFalse(r["items"][0]["downloaded"])
    def test_librivox_books_are_not_voice_clones(self):
        def fake(u):
            self.assertEqual(parse_qs(urlsplit(u).query)["limit"],["2"])
            return {"books":[{"id":"42","title":"The Novel",
                              "url_librivox":"https://librivox.org/the-novel",
                              "authors":[{"first_name":"Jules","last_name":"Verne"}]}]}
        r=src.search("librivox","Jules Verne",2,fake)
        self.assertEqual(r["items"][0]["media_kind"],"audio_reference")
        self.assertIn("Jules Verne",r["items"][0]["author"])
    def test_librivox_author_prefix_routes_author_param(self):
        def fake(u):
            p=parse_qs(urlsplit(u).query)
            self.assertEqual(p["author"],["Verne"])
            self.assertNotIn("title",p)
            return {"books":[]}
        result=src.search("librivox","author:Verne",1,fake)
        self.assertEqual(result["items"],[])
        self.assertEqual(result["api_requests"],1)

    def test_openlibrary_key_validated(self):
        r=src.search("openlibrary","Alice Wonderland",1,lambda u:{"docs":[{
            "key":"/works/OL12345W","title":"Alice","first_publish_year":1865,
            "author_name":["Lewis Carroll"]}]})
        self.assertEqual(len(r["items"]),1)
        self.assertEqual(r["items"][0]["date"],"1865")
    def test_gutendex_book_country_rights_pending(self):
        r=src.search("gutendex","Verne",1,lambda u:{"results":[{
            "id":42,"title":"A Book","authors":[{"name":"Verne, Jules"}]}]})
        self.assertEqual(r["items"][0]["media_kind"],"book")
        self.assertEqual(r["items"][0]["rights_review"],"pending")
    def test_crossref_bibliographic_evidence(self):
        r=src.search("crossref","Rembrandt provenance",1,lambda u:{"message":{"items":[{
            "DOI":"10.1234/art.1","title":["An art history paper"],
            "published":{"date-parts":[[2020,1,1]]},
            "author":[{"given":"Jane","family":"Doe"}]}]}})
        self.assertIn("doi.org/10.1234/art.1",r["items"][0]["source_url"])
        self.assertEqual(r["items"][0]["date"],"2020")
    def test_all_never_auto_publish_or_approve(self):
        for provider in src.PROVIDERS:
            if provider=="getty_museum":q=UUID_M
            elif provider=="getty_provenance":q=UUID_P
            else:q="historic art"
            with patch.object(src,"request_json",return_value={}):
                r=src.search(provider,q,1)
            self.assertFalse(r["automatic_publish"])
            self.assertFalse(r["auto_approved"])
            self.assertFalse(r["automatic_selection"])
            self.assertEqual(r["downloaded_files"],0)
            self.assertFalse(r["paid_calls"])

    def test_v34_rijks_finna_scene_integration_stays_pending(self):
        for provider,need,fmt in [
            ("rijks","authentic_artwork","artvision_critico"),
            ("finna","authentic_artwork","artvision_critico"),
            ("finna","documentary_evidence","controluce")]:
            brief={"format":fmt,"title":"Source research","scenes":[{
                "id":"s1","need":need,"description":"Authentic original historical object with documentation",
                "narration_anchor":"Historical explanation"}]}
            payload={"items":[{"provider":provider,"id":provider+":sample",
                 "source_url":"https://example.org/record",
                 "media_kind":"image_candidate"}],"api_requests":1}
            with self.subTest(provider=provider,need=need),patch.object(src,"search",return_value=payload):
                report,detail=selector.discover_single(brief,[],"s1",provider,"The Night Watch",1)
                self.assertEqual(report["counts"]["need_sources"],1)
                self.assertEqual(detail["results"][0]["rights_review"],"pending")
                self.assertEqual(detail["downloaded_files"],0)
                self.assertFalse(detail["automatic_selection"])

if __name__=="__main__":
    unittest.main()
