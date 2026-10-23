"""Regression tests for ArtVision V28: no fake AI/production social captions."""
import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from artvision_editorial_post_v28 import config,validate_entry,write_posts,validate_folder,editorial_body,FILES

class EditorialV28Tests(unittest.TestCase):
    def test_curated_cabanel_simberg_entries_are_complete(self):
        for k,e in config()["entries"].items():
            with self.subTest(episode=k):
                self.assertEqual([],validate_entry(k,e))

    def test_caption_is_story_not_a_montage_instruction(self):
        for k,e in config()["entries"].items():
            b=e["captions"]["facebook"].lower()
            for forbidden in ("zoom","ho scelto di", "regia","montaggio","camera","in questo video","algoritmo"):
                self.assertNotIn(forbidden,b,k)

    def test_generate_and_validate_all_four_posts(self):
        for key in config()["entries"]:
            with tempfile.TemporaryDirectory() as td:
                write_posts(key,td,overwrite=False)
                self.assertEqual([],validate_folder(td))
                for _,name in FILES.items():
                    self.assertTrue((Path(td)/name).is_file())
                self.assertTrue((Path(td)/"POST_EDITORIAL_RESEARCH.json").is_file())

    def test_do_not_overwrite_edits(self):
        with tempfile.TemporaryDirectory() as td:
            write_posts("cabanel_v26",td,overwrite=False)
            txt=Path(td)/"POST_FACEBOOK.txt"
            txt.write_text("Testo utente: non sovrascrivere",encoding="utf-8")
            with self.assertRaises(FileExistsError):
                write_posts("cabanel_v26",td,overwrite=False)
            self.assertIn("Testo utente",txt.read_text(encoding="utf-8"))

    def test_reject_production_talk(self):
        with tempfile.TemporaryDirectory() as td:
            write_posts("simberg_v27",td,overwrite=False)
            f=Path(td)/"POST_FACEBOOK.txt"
            s=f.read_text(encoding="utf-8")
            s=s.replace("Due ragazzi trasportano", "Ho scelto di partire dallo zoom. Due ragazzi trasportano")
            f.write_text(s,encoding="utf-8")
            self.assertTrue(any("forbidden process/AI" in x for x in validate_folder(td)))

    def test_reject_made_up_unresearched_topic(self):
        import copy
        x=copy.deepcopy(config()["entries"]["cabanel_v26"])
        x["primary_sources"]=[]
        self.assertTrue(validate_entry("made-up-work",x))

    def test_generalizes_to_future_english_titles(self):
        text="Fatto reale narrato in modo umano.\n\nMy Future Painting (1847) — Artist.\nMusica: track."
        self.assertEqual("Fatto reale narrato in modo umano.",
            editorial_body(text,"My Future Painting"))

if __name__=="__main__":
    unittest.main()
