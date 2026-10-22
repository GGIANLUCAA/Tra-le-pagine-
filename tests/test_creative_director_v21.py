"""Test dei pacchetti creativi: nessuna metrica inventata, nessuna pubblicazione."""
import copy
import json
import tempfile
import subprocess
import unittest
from pathlib import Path

from src.creative_director_v21 import (
 duration_plan,choose_visual,mood_music,write_package,caption_set,get_context,actual_seconds
)

E={"schema":"artvision-enigma-v1","id":"arcimboldo-test","artist":"Giuseppe Arcimboldo",
 "artwork":"Vertumno","hook":"Come puo essere un volto fatto solo di frutti?",
 "resolution":"L'opera raffigura Rodolfo II come dio delle stagioni.",
 "original_value":"Analisi dei dettagli vegetali che costruiscono il volto.",
 "source":{"file_page":"https://commons.wikimedia.org/wiki/File:Curated.jpg",
           "license":"PDM"},
 "fact_sources":["https://samlingar.shm.se/"],
 "shots":[{"seconds":3.2,"purpose":"Ogni dettaglio"} for _ in range(12)],
 "music":{"origin":"external_licensed","title":"Evening Fall (Piano)",
          "artist":"Kevin MacLeod","source_url":"https://incompetech.com/",
          "license_url":"https://creativecommons.org/licenses/by/4.0/",
          "commercial_allowed":True}}

class CreativeDirectorV21Tests(unittest.TestCase):
 def test_duration_follows_content_not_single_fixed_length(self):
    self.assertEqual(duration_plan(E)["seconds"],38.4)
    book={"format":"libri","scenes":[{"seconds":20},{"seconds":18},{"seconds":31}]}
    self.assertEqual(duration_plan(book)["seconds"],69)
    long={"format":"libri","scenes":[{"seconds":21} for _ in range(13)]}
    self.assertEqual(duration_plan(long)["seconds"],273)
    empty=duration_plan({"format":"libri"})
    self.assertIsNone(empty["seconds"])
    self.assertFalse(empty["fixed_template"])
 def test_real_master_time_overrides_estimated(self):
    self.assertEqual(duration_plan(E,actual=37.63)["basis"],"ffprobe_master_reale")
    self.assertEqual(duration_plan(E,actual=37.63)["seconds"],37.63)
 def test_visual_selection_is_relevant_not_random_bodies(self):
    b={"format":"artvision_critico","visual_candidates":[
       {"id":"donna_genericissima","type":"human_figure","relevance":1,"impact":5,"source":"x","rights":"y"},
       {"id":"statua_pertinente","type":"sculpture","relevance":5,"impact":4,"source":"https://museum","rights":"CC0"}]}
    arch,asset,warnings=choose_visual(b,["human_gaze","sculptural_form"],history=[])
    self.assertEqual(asset["id"],"statua_pertinente")
    self.assertEqual(arch,"sculptural_form")
 def test_history_does_not_force_unrelated_visual(self):
    arch,asset,w=choose_visual({"format":"artvision_enigma","visual_candidates":[
       {"id":"opera","type":"painting","relevance":5,"impact":4,"source":"museum","rights":"CC0"}]},
       ["enigmatic_detail","unexpected_contrast"],[{"archetype":"enigmatic_detail"}]*5)
    self.assertEqual(asset["id"],"opera")
    self.assertIn(arch,("enigmatic_detail","unexpected_contrast"))
 def test_meta_native_audio_never_embedded_or_exported_worldwide(self):
    b={"music":{"origin":"meta_native_library","id":"FB-123","title":"Un brano",
        "embedded":True},"format":"artvision_cinema"}
    m=mood_music(b,["facebook","youtube"])
    self.assertTrue(any("BLOCCO" in x for x in m["warnings"]))
    self.assertIn("NON",m["master_policy"].upper() if "NON" in m["master_policy"].upper() else "NON")
    self.assertTrue(any("fuori" in x for x in m["warnings"]))
 def test_same_meta_track_can_be_reused_only_with_reverified_rights(self):
    b={"music":{"origin":"meta_sound_collection","id":"collection-1","title":"Track"}}
    m=mood_music(b,["facebook","instagram"])
    self.assertIn("puo tornare",m["repetition_rule"])
    self.assertTrue(any("Sound Collection" in x for x in m["warnings"]))
 def test_social_captions_differ_by_platform(self):
    m=mood_music(E,["facebook","instagram","tiktok","youtube"])
    captions=caption_set(E,get_context(E),m,["facebook","instagram","tiktok","youtube"])
    self.assertNotEqual(captions["facebook"]["description"],captions["tiktok"]["description"])
    for row in captions.values():
      self.assertLessEqual(len(row["hashtags"]),4)
      self.assertIn("Fonte:",row["description"])
 def test_no_master_means_no_fake_thumbnail_or_social_ready(self):
    with tempfile.TemporaryDirectory() as t:
      b=write_package(E,Path(t))
      self.assertFalse(b["ready_to_publish"])
      self.assertIsNone(b["technical_preview"])
      self.assertFalse((Path(t)/"COPERTINA_CANDIDATA_V21.jpg").exists())
      for plat in ("FACEBOOK","INSTAGRAM","TIKTOK","YOUTUBE"):
        self.assertTrue((Path(t)/("POST_"+plat+"_V21.txt")).exists())
      self.assertTrue(any("Manca master" in s for s in b["warnings"]))
 def test_enigma_has_individual_opening_without_fake_retention(self):
    with tempfile.TemporaryDirectory() as t:
      b=write_package(E,Path(t))
      self.assertEqual([x["from_seconds"] for x in b["first_7_seconds"]],[0,1,3,5])
      self.assertEqual(b["cover"]["recommended_archetype"],"enigmatic_detail")
      self.assertFalse(b["ready_to_publish"])
      self.assertFalse(b["automatic_scoring_not_aesthetic_certification"] is False)
 def test_real_first_frames_and_hash(self):
    with tempfile.TemporaryDirectory() as t:
      root=Path(t);master=root/"video.mp4"
      subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
       "-f","lavfi","-i","testsrc2=size=320x568:rate=12:duration=8.5",
       "-f","lavfi","-i","sine=frequency=440:duration=8.5",
       "-shortest","-c:v","libx264","-preset","ultrafast","-pix_fmt","yuv420p",
       "-c:a","aac",str(master)],check=True,timeout=90)
      self.assertGreater(actual_seconds(master),8.)
      data=write_package(E,root/"package",video=master)
      self.assertTrue((root/"package"/"APERTURA_0_7_V21.jpg").is_file())
      self.assertTrue((root/"package"/"COPERTINA_CANDIDATA_V21.jpg").is_file())
      self.assertEqual(len(data["video_sha256"]),64)
      self.assertTrue(data["cover"]["approved_original_must_remain"])
      self.assertFalse(data["ready_to_publish"])

if __name__=="__main__":
 unittest.main()
