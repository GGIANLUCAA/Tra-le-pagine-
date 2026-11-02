import json
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from storia_rivive_v236_lusitania_editorial_recut import EPISODE,FILM_SHA,SHOTS,prepare

class V236RealArchiveReframeTests(unittest.TestCase):
    def test_four_real_i2i_inputs_and_one_real_vidu_anchor(self):
        self.assertEqual(len(SHOTS),5)
        self.assertEqual([x[-1] for x in SHOTS].count('I2I'),4)
        self.assertEqual([x[-1] for x in SHOTS].count('VIDU_SOURCE_ANCHOR_NO_I2I'),1)
        self.assertEqual(len({x[0] for x in SHOTS}),5)
        self.assertEqual(len({x[1] for x in SHOTS}),5)
        self.assertEqual(len(FILM_SHA),64)
        self.assertTrue(EPISODE.startswith('lusitania_'))

    def test_refuses_unverified_original_film(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache=Path(tmp)/'cache';cache.mkdir()
            (cache/'SCOUT_REPORT.json').write_text(json.dumps({
                'status':'REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW',
                'source_page':'https://commons.wikimedia.org/wiki/File:Passengers_arriving_for_the_RMS_Lusitania,_NYC,_May_1,_1915.webm',
                'original_sha256':FILM_SHA,'source_frames_extracted':12,'sampling_period_s':26.406}))
            with self.assertRaisesRegex(ValueError,'V236_ORIGINAL_FILM_BYTES_CHANGED'):
                prepare(cache,Path(tmp)/'out')

    def test_refuses_frame_without_sha_even_when_metadata_looks_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache=Path(tmp)/'cache';(cache/'original_frames').mkdir(parents=True)
            (cache/'SCOUT_REPORT.json').write_text(json.dumps({
                'status':'REAL_BW_FILM_FRAMES_READY_FOR_PHOTO_SOURCE_REVIEW',
                'source_page':'https://commons.wikimedia.org/wiki/File:Passengers_arriving_for_the_RMS_Lusitania,_NYC,_May_1,_1915.webm',
                'original_sha256':FILM_SHA,'source_frames_extracted':12,'sampling_period_s':26.406}))
            Image.new('RGB',(1920,1080),(0,0,0)).save(cache/'original_frames'/'frame_02.png')
            with self.assertRaisesRegex(ValueError,'V236_SOURCE_FRAME_SHA_MISMATCH'):
                prepare(cache,Path(tmp)/'out',require_film=False)
if __name__=='__main__':unittest.main()
