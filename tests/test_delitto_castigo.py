"""Tests: book episode source and archival image treatment, no API requests."""
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image,ImageOps

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from assets_delitto_castigo import SEARCHES, quality_photo, grade_photo, SCENE_COUNT

REPO=Path(__file__).resolve().parents[1]
EP=REPO/"episodes"/"08_delitto_e_castigo"


class CrimeAndPunishmentTests(unittest.TestCase):
    def test_12_diverse_scene_topics(self):
        self.assertEqual(len(SEARCHES),SCENE_COUNT)
        self.assertEqual(sorted(SEARCHES),list(range(1,13)))
        self.assertTrue(all(1<=len(terms)<=4 for terms in SEARCHES.values()))

    def test_narration_and_metadata(self):
        txt=(EP/"testo.txt").read_text(encoding="utf-8")
        meta=json.loads((EP/"metadata.json").read_text(encoding="utf-8"))
        self.assertTrue(300<=len(txt.split())<=480)
        self.assertEqual(meta["episode"],"08")
        self.assertIn("Dostoevskij",meta["author"])
        self.assertEqual(meta["voice"],"gemini")
        for key in ("Raskol'nikov","Sonja","Porfirij","Siberia"):
            self.assertIn(key,txt)

    def test_monotone_scene_cues(self):
        txt=(EP/"testo.txt").read_text(encoding="utf-8")
        phrases=[x.strip() for x in re.split(
            r'(?<=[.!?])\s+(?=[A-ZÀ-ÙÈÉ«“])',
            re.sub(r'\s+',' ',txt)) if x.strip()]
        cues=json.loads((EP/"scene_cues.json").read_text())
        starts=[x["start_sentence"] for x in cues]
        self.assertEqual([x["asset"] for x in cues],list(range(1,13)))
        self.assertEqual(starts[0],0)
        self.assertTrue(all(a<b for a,b in zip(starts,starts[1:])))
        self.assertTrue(all(i<len(phrases) for i in starts))

    def test_poster_size_and_quality(self):
        im=Image.effect_noise((1250,850),55).convert("RGB")
        out=io.BytesIO();im.save(out,format="JPEG",quality=88)
        photo=quality_photo(out.getvalue())
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/"scena_01.jpg"
            info=grade_photo(photo,target,"cool")
            self.assertEqual(info["width"],1080)
            self.assertEqual(info["height"],1920)
            self.assertGreater(info["bytes"],35_000)
            with Image.open(target) as rendered:
                self.assertEqual(rendered.size,(1080,1920))

    def test_no_low_quality_input(self):
        im=Image.new("RGB",(70,90),"blue")
        out=io.BytesIO();im.save(out,format="JPEG")
        with self.assertRaises(ValueError):
            quality_photo(out.getvalue())

    def test_no_unapproved_v4_effect_overuse(self):
        cfg=json.loads((EP/"effetti_v4.json").read_text(encoding="utf-8"))
        strong=[s for s in cfg["scenes"] if s["effect"] in {"brush_reveal","sketch_paint"}]
        self.assertEqual(len(strong),1)

    def test_render_gate_and_no_autopublish(self):
        req=json.loads((EP/"PRODUCI.json").read_text(encoding="utf-8"))
        self.assertEqual(req["voice"],"Google Gemini")
        self.assertTrue(req["approved"])
        flow=(REPO/".github/workflows/delitto-castigo-video.yml").read_text()
        self.assertIn("if: github.event_name == 'push'",flow)
        self.assertIn("DELITTO_E_CASTIGO_VIDEO_MP4",flow)
        self.assertNotIn("gh release create",flow)


if __name__=="__main__":
    unittest.main()
