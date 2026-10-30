import sys,unittest
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import artvision_martin_critico_visual_v82 as v

class CriticoDirectorV82(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.art=Image.new("RGB",(1000,640),(100,30,20))
    cls.frame=Image.new("RGB",(1024,717),(217,177,59)) # synthetic frame color
    cls.room=Image.new("RGB",(720,1280),(57,62,67))
  def test_script_beats_nine(self):
    self.assertEqual(len(v.SCENE_EDIT),9)
    self.assertEqual(len(v.MUSEUM_ROUTE),9)
    self.assertGreaterEqual(sum(len(a) for a in v.SCENE_EDIT),13)
  def test_closeups_in_full_color_and_vertical(self):
    for t in [0,7,20,35,51,72]:
      im=v.critico_standard(self.art,t,94)
      self.assertEqual(im.size,(720,1280))
  def test_real_frame_only_intro_exit(self):
    # a completely gold synthetic "framed photograph" is strongly detectable
    duration=96.
    for t in [9,16,23,35,44,58,72,84]:
      im=v.museum_frame(self.art,self.frame,self.room,t,duration,True)
      a=np.asarray(im)
      self.assertFalse(np.any(np.all(a==[217,177,59],axis=2)),f"frame contaminated story at {t}s")
    for t in [0,duration]:
      im=v.museum_frame(self.art,self.frame,self.room,t,duration,True)
      self.assertTrue(np.any(np.all(np.asarray(im)==[217,177,59],axis=2)))
  def test_one_storyboard_per_paragraph(self):
    bounds=[float(x) for x in range(0,100,10)]
    self.assertEqual(len(bounds),10)
    v.assign_narrative_timing(bounds)
    for i in range(9):
      beat,u,a,b=v.beat_at(i*10+5,91.5)
      self.assertEqual(beat,i)
  def test_exit_same_frame_room(self):
    a=v.museum_frame(self.art,self.frame,self.room,0,96,True)
    b=v.museum_frame(self.art,self.frame,self.room,96,96,True)
    self.assertTrue(np.array_equal(np.asarray(a),np.asarray(b)))
if __name__=="__main__":unittest.main()
