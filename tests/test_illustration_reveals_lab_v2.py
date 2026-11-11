"""Offline regression for optional V2 illustrated reveals; never touches master files."""
import hashlib
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from illustration_reveals_lab_v2 import recommend, group_masks, animation_maps, frame_at, render

def demo(path):
    im=Image.new("RGB",(180,320),(251,248,241))
    d=ImageDraw.Draw(im)
    d.ellipse((10,32,64,92),fill="#d7ad4a",outline="#333c4c",width=2)
    d.polygon(((85,100),(112,60),(155,100)),fill="#71879e")
    d.rectangle((90,101,145,183),fill="#a1b9be",outline="#333c4c",width=2)
    d.ellipse((24,220,100,285),fill="#b45c75",outline="#333c4c",width=3)
    im.save(path)

class RevealTests(unittest.TestCase):
    def test_director_never_forces_effect(self):
        self.assertEqual(recommend("artvision_cinema","storybook")[0],"none")
        self.assertEqual(recommend("libri","neutral")[0],"none")
        self.assertEqual(recommend("libri","storybook")[0],"director_mix")
        self.assertEqual(recommend("libri","mystery")[0],"stroke_draw")

    def test_island_detection(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"source.png";demo(p)
            src=cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
            fg,groups,paper=group_masks(src)
            self.assertTrue(paper)
            self.assertGreaterEqual(len(groups),3)
            self.assertGreater(int(np.sum(fg>0)),300)
            maps=animation_maps(src,13)
            self.assertEqual(maps[0].shape,(320,180))
            self.assertEqual(frame_at(src,maps,"director_mix",1).shape,src.shape)

    @unittest.skipUnless(shutil.which("ffmpeg"),"FFmpeg unavailable")
    def test_four_effects_do_not_modify_input(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"source.png";demo(p)
            original=hashlib.sha256(p.read_bytes()).hexdigest()
            for mode in ("stroke_draw","object_stagger","pigment_bloom","director_mix"):
                out=Path(td)/(mode+".mp4")
                info=render(p,out,effect=mode,duration=.6,fps=10,width=180,height=320)
                self.assertEqual(info["frames"],6)
                self.assertEqual(info["api_calls"],0)
                self.assertEqual(info["source_sha256"],original)
                self.assertTrue(out.is_file())
                self.assertTrue(out.with_suffix(".json").is_file())
                with self.assertRaises(FileExistsError):
                    render(p,out,effect=mode,duration=.6,fps=10,width=180,height=320)
            self.assertEqual(original,hashlib.sha256(p.read_bytes()).hexdigest())

    def test_full_frame_falls_back_to_none(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"dark.png";Image.new("RGB",(180,320),(24,48,75)).save(p)
            src=cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB)
            self.assertFalse(group_masks(src)[2])
            if shutil.which("ffmpeg"):
                r=render(p,Path(td)/"preview.mp4",effect="director_mix",duration=.6,
                         fps=10,width=180,height=320)
                self.assertEqual(r["selected"],"none")

    def test_cannot_accept_master_mp4_as_image(self):
        with tempfile.TemporaryDirectory() as td:
            mp4=Path(td)/"master.mp4";mp4.write_bytes(b"not-a-real-video")
            with self.assertRaises(ValueError):
                render(mp4,Path(td)/"result.mp4",duration=.6,fps=10,
                       width=180,height=320)
if __name__=="__main__":unittest.main()
