#!/usr/bin/env python3
"""Zero-network tests for ArtVision fixed 20 music selection and reuse safety."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import artvision_music_selector_v330 as music

class FixedMusicPaletteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog=music.load_catalog()

    def pick(self,title,moods=None,artist="",history=None,pin=None,duration=None):
        return music.select_music(title=title,artist=artist,moods=moods,
            history=history,pinned_track_id=pin,duration=duration,catalog=self.catalog)

    def test_exactly_twenty_unique_real_recordings_metadata(self):
        data=self.catalog
        self.assertEqual(data["fixed_slots"],20)
        self.assertEqual(len(data["tracks"]),20)
        self.assertEqual(len({t["id"] for t in data["tracks"]}),20)
        self.assertEqual(len({t["isrc"] for t in data["tracks"]}),20)
        self.assertTrue(all(t["download_url"].startswith(music.OFFICIAL_DOMAIN) for t in data["tracks"]))
        self.assertTrue(all(t["recording_verified"] is False for t in data["tracks"]))
        self.assertTrue(all(t["license"]=="CC BY 4.0" for t in data["tracks"]))

    def test_mood_selection_matches_tragedy(self):
        r=self.pick("Death and the Child",["grief","somber"],"Edvard Munch")
        track=next(t for t in self.catalog["tracks"] if t["id"]==r["selected"]["track_id"])
        self.assertTrue(set(track["editorial_moods"])&{"grief","somber"})
        self.assertNotEqual(track["id"],"call_to_adventure")

    def test_mystical_mermaid_is_not_battle_audio(self):
        r=self.pick("A Mermaid",["magical","dreamlike"],"Waterhouse")
        track=next(t for t in self.catalog["tracks"] if t["id"]==r["selected"]["track_id"])
        self.assertTrue(set(track["editorial_moods"])&{"magical","dreamlike"})
        self.assertNotEqual(track["id"],"the_descent")

    def test_heroic_wild_hunt_not_lullaby(self):
        r=self.pick("The Wild Hunt of Odin",["epic","heroic"],"Peter Nicolai Arbo")
        track=next(t for t in self.catalog["tracks"] if t["id"]==r["selected"]["track_id"])
        self.assertTrue(set(track["editorial_moods"])&{"epic","heroic"})
        self.assertNotEqual(track["id"],"calmant")

    def test_four_variants_pinned_same_track(self):
        first=self.pick("The Wild Hunt of Odin",["epic","heroic"],"Arbo")
        track=first["selected"]["track_id"]
        hist=[{"work_id":"unrelated","track_id":track}]*3
        museum=self.pick("The Wild Hunt of Odin",["somber"],"Arbo",history=hist,pin=track)
        self.assertEqual(track,museum["selected"]["track_id"])
        self.assertTrue(museum["shared_four_variants"])

    def test_avoid_latest_three_different_works(self):
        first=self.pick("A Mermaid",["magical","dreamlike"],"John William Waterhouse")
        tid=first["selected"]["track_id"]
        recent=[{"work_id":f"painting-{i}","track_id":tid} for i in range(3)]
        second=self.pick("Sleeping Beauty",["magical","dreamlike"],"Rheam",history=recent)
        self.assertNotEqual(second["selected"]["track_id"],tid)

    def test_not_count_four_variants_as_different_works(self):
        hist=[
            {"work_id":"odin-arbo","track_id":"magistar"},
            {"work_id":"odin-arbo","track_id":"magistar"},
            {"work_id":"odin-arbo","track_id":"magistar"},
            {"work_id":"mermaid-waterhouse","track_id":"immersed"},
        ]
        self.assertEqual(music._history_recent(hist,"another"),
                         ["immersed","magistar"])

    def test_no_mood_knowledge_is_flagged(self):
        r=self.pick("Untitled strange collection",artist="Anonymous")
        self.assertEqual(r["mood_source"],"unknown_manual_review_required")
        self.assertEqual(r["human_listening_review"],"PENDING")

    def test_unknown_mood_fails(self):
        with self.assertRaises(ValueError):
            self.pick("Garden",["infinite-viral-viewers"])

    def test_source_duration_gate_and_source_proof(self):
        with self.assertRaises(ValueError):
            self.pick("A Mermaid",pin="ghost_processional",duration=120)
        t=self.catalog["tracks"][0]
        self.assertIn(t["isrc"],t["source_url"])
        self.assertIn("Kevin MacLeod",music.credit({"title":t["title"]}))
        self.assertIn("creativecommons.org/licenses/by/4.0",music.credit(t))

    def test_no_overwrite_master(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"master.mp4"
            p.write_bytes(b"not actually a video")
            with self.assertRaisesRegex(ValueError,"Never overwrite"):
                music.private_remix(source_video=p,out_video=p,
                                    recording=p,track={"title":"Calmant","track_id":"calmant"})

    def test_reject_nonofficial_audio_source(self):
        bogus={"isrc":"X1","title":"Bogus","track_id":"bogus",
               "source_duration_seconds":200,"download_url":"https://example.com/fake.mp3"}
        with tempfile.TemporaryDirectory() as cache:
            with self.assertRaisesRegex(ValueError,"non-official"):
                music.acquire_recording(bogus,Path(cache))

if __name__=="__main__":unittest.main()
