"""Test offline, senza feed esterni, chiavi AI o immagini generate."""
from datetime import date
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from controluce import parse_feed, collect, validate_episode, sentence_count

PILOT = Path(__file__).resolve().parents[1]/"formats/controluce/episodes/2026-10-18_trasporti_sud"
RSS = b'''<?xml version="1.0"?><rss version="2.0"><channel><title>News</title>
<item><title>Un evento &amp; un commento</title><link>https://example.org/a</link><description>Testo &lt;b&gt;illustrativo&lt;/b&gt;</description><pubDate>Sun, 18 Oct 2026 10:07:00 +0200</pubDate></item></channel></rss>'''

class ControluceTests(unittest.TestCase):
    def test_rss_is_only_a_candidate(self):
        rows=parse_feed(RSS,{"id":"prova","name":"Test","kind":"independent"})
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["published_date_rome"],"2026-10-18")
        self.assertIsNone(rows[0]["event_date"])
        self.assertEqual(rows[0]["status"],"da_verificare")
        self.assertEqual(rows[0]["summary"],"Testo illustrativo")
    def test_collect_is_not_a_verified_news_story(self):
        with tempfile.TemporaryDirectory() as tmp:
            inp=Path(tmp)/"sources.json"
            inp.write_text(json.dumps({"sources":[{"id":"prova","name":"Test","kind":"independent","rss":"https://example.org/feed"}]}))
            result=collect(inp,date(2026,10,18),Path(tmp)/"out.json",fetcher=lambda url:RSS)
            self.assertEqual(len(result["candidates"]),1)
            self.assertFalse(result["approved_for_render"])
            self.assertIsNone(result["selected_story"])
    def test_pilot_is_blocked_before_any_paid_render(self):
        with self.assertRaisesRegex(ValueError,"Approvazione"):
            validate_episode(PILOT,require_images=False)
    def test_approved_structure_can_be_checked_without_images(self):
        with tempfile.TemporaryDirectory() as tmp:
            ep=Path(tmp)
            for original in PILOT.iterdir():
                if original.is_file(): shutil.copy2(original,ep/original.name)
            for name,key in [("metadata.json","approved_for_render"),("research.json","approved_by_editor")]:
                data=json.loads((ep/name).read_text(encoding="utf-8"));data[key]=True
                (ep/name).write_text(json.dumps(data,ensure_ascii=False))
            details=validate_episode(ep,require_images=False)
            self.assertEqual(details["event_date"],"2026-10-18")
            self.assertGreaterEqual(details["verified_source_domains"],2)
            self.assertEqual(details["scenes"],11)
            with self.assertRaisesRegex(ValueError,"Immagini premium mancanti"):
                validate_episode(ep,require_images=True)
    def test_unverified_claim_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            ep=Path(tmp)
            for f in PILOT.iterdir():
                if f.is_file():shutil.copy2(f,ep/f.name)
            data=json.loads((ep/"metadata.json").read_text());data["approved_for_render"]=True
            (ep/"metadata.json").write_text(json.dumps(data))
            research=json.loads((ep/"research.json").read_text());research["approved_by_editor"]=True
            research["claims"][0]["source_ids"]=[]
            (ep/"research.json").write_text(json.dumps(research))
            with self.assertRaisesRegex(ValueError,"Fatto senza fonte"):
                validate_episode(ep,require_images=False)
    def test_script_has_expected_sentence_structure(self):
        self.assertEqual(sentence_count((PILOT/"testo.txt").read_text()),22)

if __name__=="__main__": unittest.main()
