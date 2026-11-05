"""V167 pure pixel regression: optimized Museum intro must match unoptimized V164 exactly.

Run: python -m unittest tests.test_artvision_museum_static_cache_v167 -v
Synthetic photo only, no API, no TTS, no render, no change to historical masters.
"""
import importlib.util
import pathlib
import tempfile
import unittest
from unittest import mock

try:
 import cv2
 import numpy as np
 from PIL import Image, ImageDraw, ImageFont
 READY = True
except ImportError:
 READY = False

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "artvision_lady_shalott_critico_museum_v164.py"


def legacy_frame(photo,t):
 """Original V164 staged() math preserved as reference for pixel equality."""
 mat=cv2.imread(str(photo))
 ph,pw=mat.shape[:2]
 scale=min(670/pw,895/ph)
 sw,sh=int(scale*pw),int(scale*ph)
 img=cv2.resize(mat,(sw,sh),interpolation=cv2.INTER_AREA)
 im=np.full((1280,720,3),(24,24,25),np.uint8)
 for y in range(1280):
  v=int(16+13*(1-abs(y-1280/2)/(1280/2)))
  im[y,:]=(v+7,v+6,v+4)
 zoom=.93+.085*max(0,min(1,t))
 iw,ih=int(sw*zoom),int(sh*zoom)
 sub=cv2.resize(img,(iw,ih),interpolation=cv2.INTER_CUBIC)
 px=(720-iw)//2;py=(1280-ih)//2+95
 x1,y1,x2,y2=max(0,px),max(0,py),min(720,px+iw),min(1280,py+ih)
 if x1<x2 and y1<y2:im[y1:y2,x1:x2]=sub[y1-py:y2-py,x1-px:x2-px]
 pil=Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB))
 d=ImageDraw.Draw(pil)
 serif=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',30)
 sans=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
 for title,y,font,col in [('THE LADY OF SHALOTT',85,serif,(235,225,207)),
                           ('JOHN WILLIAM WATERHOUSE · 1888',143,sans,(194,185,165))]:
  b=d.textbbox((0,0),title,font=font)
  d.text(((720-b[2]+b[0])/2,y),title,font=font,fill=col)
 return cv2.cvtColor(np.asarray(pil),cv2.COLOR_RGB2BGR)


@unittest.skipUnless(READY, "cv2/numpy/Pillow are needed for pixel regression")
class CacheDoesNotChangeVideoPixels(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  spec=importlib.util.spec_from_file_location("artvision_museum_v164_fast",SRC)
  cls.renderer=importlib.util.module_from_spec(spec)
  spec.loader.exec_module(cls.renderer)

 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.addCleanup(self.tmp.cleanup)
  self.img=pathlib.Path(self.tmp.name)/"photograph.jpg"
  # Reproducible photo with varied high-frequency detail and colors.
  rng=np.random.default_rng(20261105)
  arr=rng.integers(0,256,size=(600,800,3),dtype=np.uint8)
  self.assertTrue(cv2.imwrite(str(self.img),arr,[cv2.IMWRITE_JPEG_QUALITY,93]))
  self.renderer._museum_static_assets.cache_clear()

 def test_eight_keyframes_pixel_identical(self):
  for t in [0.,.05,.13,.20,.40,.65,.80,1.]:
   with self.subTest(t=t):
    expected=legacy_frame(self.img,t)
    actual=self.renderer.staged(self.img,t)
    self.assertEqual(actual.shape,expected.shape)
    self.assertTrue(np.array_equal(actual,expected),
                    "Any pixel mismatch is a quality regression")

 def test_one_source_decode_and_font_load_for_multiple_frames(self):
  imread=self.renderer.cv2.imread
  load_font=self.renderer.ImageFont.truetype
  with mock.patch.object(self.renderer.cv2,'imread',wraps=imread) as read,\
       mock.patch.object(self.renderer.ImageFont,'truetype',wraps=load_font) as font:
   for i in range(12):
    self.renderer.staged(self.img,i/11)
   self.assertEqual(read.call_count,1)
   self.assertEqual(font.call_count,2)
  self.assertEqual(self.renderer._museum_static_assets.cache_info().misses,1)
  self.assertEqual(self.renderer._museum_static_assets.cache_info().hits,11)

 def test_distinct_photo_files_not_confused(self):
  second=pathlib.Path(self.tmp.name)/"other.jpg"
  im=np.zeros((480,640,3),np.uint8)
  im[:]=(10,50,200)
  cv2.imwrite(str(second),im)
  a=self.renderer.staged(self.img,.4)
  b=self.renderer.staged(second,.4)
  self.assertFalse(np.array_equal(a,b))
  self.assertEqual(self.renderer._museum_static_assets.cache_info().misses,2)

if __name__=="__main__":
 unittest.main()
