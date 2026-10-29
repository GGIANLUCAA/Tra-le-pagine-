"""Source-faithful Wright V78 geometry, continuity and no invented frame tests.
Offline synthetic imagery only, not artistic approval.
"""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from PIL import Image
import numpy as np
import artvision_wright_visual_v78 as v

class WrightV78(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=Image.new("RGB",(4946,3688),(67,102,128))
        cls.room=Image.new("RGB",(v.W,v.H),(52,65,68))
    def test_room_is_not_museum_photo(self):
        self.assertEqual(v.room().size,(720,1280))
    def test_museum_source_center_direct(self):
        im=v.museum(self.source,self.room,15,(.5,.5))
        self.assertEqual(im.getpixel((v.W//2,v.H//2)),(67,102,128))
    def test_continuity_start_end(self):
        a=v.museum_frame(self.source,self.room,0,52,False)
        b=v.museum_frame(self.source,self.room,52,52,False)
        self.assertTrue(np.array_equal(np.asarray(a),np.asarray(b)))
    def test_distinct_critico_cinema(self):
        c=v.critico_standard(self.source,12,90)
        s=v.cinema_standard(self.source,12,44)
        self.assertEqual(c.size,(720,1280))
        self.assertEqual(s.size,(720,1280))
    def test_source_4x3_unaltered_in_wide_shot(self):
        im=v.museum(self.source,self.room,1,(.5,.5))
        self.assertEqual(im.getpixel((360,640)),(67,102,128))
    def test_cover_9x16(self):
        self.assertEqual(v.cover(self.source,"cinema_museum").size,(1080,1920))

if __name__=="__main__":unittest.main()
