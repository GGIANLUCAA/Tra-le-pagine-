"""V10 poster generation: real assets only; legacy episodes untouched."""
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image

SRC=Path(__file__).resolve().parents[1]/"tools"/"build_episode_previews_v10.py"
spec=importlib.util.spec_from_file_location("build_preview",SRC)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class GalleryTests(unittest.TestCase):
    def seed(self,root):
        repo=Path(root)
        ep=repo/"episodes"/"01_prova"
        ep.mkdir(parents=True)
        (repo/"docs").mkdir()
        (ep/"metadata.json").write_text(json.dumps({"title":"Libro originale","author":"Autore"}))
        raw=repo/"raw.jpg"
        Image.effect_noise((900,1200),55).convert("RGB").save(raw,quality=89)
        with zipfile.ZipFile(ep/"scene_premium.zip","w",compression=zipfile.ZIP_DEFLATED) as z:
            z.write(raw,arcname="scena_01.jpg")
            z.writestr("../private/passwords.txt","not-an-image")
        return ep

    def test_real_preview_from_archive(self):
        with tempfile.TemporaryDirectory() as d:
            ep=self.seed(d)
            before=(ep/"scene_premium.zip").read_bytes()
            mod.build(d)
            manifest=json.loads((Path(d)/"docs"/"previews"/"catalog.json").read_text())
            info=manifest["episodes"]["01_prova"]
            self.assertEqual(info["title"],"Libro originale")
            self.assertEqual(info["visual_status"],"real_episode_images")
            self.assertTrue(info["frames"])
            self.assertTrue((Path(d)/"docs"/info["poster"]).is_file())
            self.assertFalse(info["public_video"])
            self.assertEqual(before,(ep/"scene_premium.zip").read_bytes())

    def test_no_images_means_no_fake_poster(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            ep=root/"episodes"/"02_mancante"
            ep.mkdir(parents=True)
            (root/"docs").mkdir()
            (ep/"metadata.json").write_text('{"title":"Solo copione"}')
            mod.build(d)
            info=json.loads((root/"docs"/"previews"/"catalog.json").read_text())["episodes"]["02_mancante"]
            self.assertIsNone(info["poster"])
            self.assertEqual(info["frames"],[])
            self.assertEqual(info["visual_status"],"missing")

    def test_no_automated_mp4_publication(self):
        with tempfile.TemporaryDirectory() as d:
            ep=self.seed(d)
            (ep/"private_video.mp4").write_bytes(b"fake video")
            mod.build(d)
            target=Path(d)/"docs"/"previews"
            self.assertFalse(list(target.rglob("*.mp4")))
            self.assertFalse(json.loads((target/"catalog.json").read_text())["videos_published_automatically"])


if __name__=="__main__":
    unittest.main()
