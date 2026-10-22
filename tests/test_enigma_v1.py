"""Test non distruttivi per ArtVision Enigma V1 (nessun network, nessun TTS)."""
import copy
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from PIL import Image,ImageDraw

from modules.artvision_enigma.enigma_v1 import validate,boundaries,frame,whole_art,render
import cv2
import numpy as np

EXAMPLE=json.loads(Path("modules/artvision_enigma/episodes/arcimboldo_vertumnus.json").read_text(encoding="utf8"))

class TestEnigma(unittest.TestCase):
    def test_valid_curated_story(self):
        self.assertAlmostEqual(validate(EXAMPLE),40.0)

    def test_blocks_false_or_empty_sources(self):
        case=copy.deepcopy(EXAMPLE);case["source"]["license"]="all rights reserved"
        with self.assertRaises(ValueError): validate(case)
        case=copy.deepcopy(EXAMPLE);case["fact_sources"]=[]
        with self.assertRaises(ValueError): validate(case)

    def test_reveal_cannot_be_first_or_repeated(self):
        case=copy.deepcopy(EXAMPLE);case["shots"][0]["kind"]="full_artwork"
        with self.assertRaises(ValueError): validate(case)
        case=copy.deepcopy(EXAMPLE);case["shots"][1]["kind"]="iris_reveal";case["shots"][2]["kind"]="iris_reveal"
        with self.assertRaises(ValueError): validate(case)

    def test_sync_only_on_real_close_onset(self):
        shots=[{"seconds":3},{"seconds":4},{"seconds":5}]
        edges=boundaries(shots,[3.09,10.5],12)
        self.assertAlmostEqual(edges[1],3.09)
        self.assertAlmostEqual(edges[2],7.0)
        self.assertEqual(edges[-1],12.)

    def test_frame_preserves_shape(self):
        im=np.zeros((900,750,3),dtype=np.uint8)
        im[:,:,0]=70;im[:,:,1]=150
        end=whole_art(im,320,568)
        f=frame(im,EXAMPLE["shots"][5],.6,320,568,end)
        self.assertEqual(f.shape,(568,320,3))
        self.assertGreater(float(f.mean()),8)

    @unittest.skipUnless(os.environ.get("ENIGMA_SMOKE")=="1","Render reale solo in CI smoke con ffmpeg/librosa")
    def test_real_video_with_synthetic_assets(self):
        # Sintetico SOLO test tecnico, mai presentato come contenuto reale/pubblicabile.
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            p=root/"test-art.jpg"
            im=Image.new("RGB",(720,960),(42,35,29))
            d=ImageDraw.Draw(im)
            d.ellipse((200,180,500,470),fill=(209,121,31))
            d.rectangle((190,630,580,850),fill=(67,120,80))
            im.save(p)
            m=root/"test-audio.wav"
            subprocess.run(["ffmpeg","-loglevel","error","-y","-f","lavfi","-i",
                "sine=frequency=440:duration=30","-c:a","pcm_s16le",str(m)],
                check=True)
            data=copy.deepcopy(EXAMPLE)
            # 25.2 sec; 12 FPS @320x568 to keep CI cheap
            for shot in data["shots"]:shot["seconds"]=2.8
            result=render(data,p,m,root/"video",width=320,height=568,fps=12)
            self.assertTrue(result.is_file())
            from modules.artvision_enigma.enigma_v1 import ffprobe
            info=ffprobe(result)
            self.assertIn("video",{x["codec_type"] for x in info["streams"]})
            self.assertIn("audio",{x["codec_type"] for x in info["streams"]})
            report=json.loads((root/"video"/"REPORT_QA.json").read_text())
            self.assertTrue(report["technical_pass"])
            self.assertTrue(report["artistic_review_required"])
            self.assertFalse(report["published"])
            self.assertTrue((root/"video"/"COPERTINA.jpg").is_file())
            self.assertTrue((root/"video"/"ANTEPRIMA_SCENE.jpg").is_file())
            self.assertTrue((root/"video"/"EDITOR_REPORT_V19.json").is_file())

if __name__=="__main__":unittest.main()
