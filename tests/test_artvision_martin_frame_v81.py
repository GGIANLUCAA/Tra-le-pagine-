"""V81 museum frame is a PHOTO, never a generated border. Continuous camera in/out.
Synthetic image tests do not certify painting-specific artistic quality.
"""
import sys,unittest
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import artvision_martin_visual_v81 as v

class MartinPhotoFrameV81(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.art=Image.new('RGB',(1000,640),(100,35,18))
        # Bright gold rectangle stands for PHOTO pixels in these synthetic tests.
        cls.frame=Image.new('RGB',(1024,717),(216,176,58))
        cls.room=Image.new('RGB',(720,1280),(57,61,65))
    def test_actual_frame_not_drawn(self):
        # First inspect the photo aperture compositor: pixels outside the aperture stay unchanged.
        out=v.original_photo_mounted(self.art,self.frame)
        self.assertEqual(out.getpixel((4,4)),(216,176,58))
        self.assertEqual(out.getpixel((512,352)),(100,35,18))
    def test_frame_visible_exterior(self):
        im=v.museum_frame(self.art,self.frame,self.room,0,51)
        arr=np.asarray(im)
        self.assertTrue(np.any(np.all(arr==[216,176,58],axis=2)))
    def test_gold_frame_absent_during_inside(self):
        for t in [11,15,22,29,38]:
            im=v.museum_frame(self.art,self.frame,self.room,t,51)
            arr=np.asarray(im)
            self.assertFalse(np.any(np.all(arr==[216,176,58],axis=2)),f'frame still visible at {t}s')
    def test_identical_frame_return(self):
        initial=v.museum_frame(self.art,self.frame,self.room,0,51)
        final=v.museum_frame(self.art,self.frame,self.room,51,51)
        self.assertTrue(np.array_equal(np.asarray(initial),np.asarray(final)))
    def test_critic_same_museum_source(self):
        self.assertEqual(v.museum_frame(self.art,self.frame,self.room,10,117,True).size,(720,1280))
        self.assertEqual(v.critico_standard(self.art,10,117).size,(720,1280))
    def test_cover(self):
        self.assertEqual(v.cover(self.art,'critico_museum').size,(1080,1920))
if __name__=="__main__":unittest.main()
