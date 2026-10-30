"""WOW LAB: pre-render proof of actual frame crossing (not camera zoom)."""
import sys
import unittest
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from subject_popout import audit_popout_projection

class PopoutGeometryGate(unittest.TestCase):
    def sample(self, top):
        layer=np.zeros((200,200,4),dtype=np.uint8)
        layer[top:top+36,70:130,:3]=(35,80,180)
        layer[top:top+36,70:130,3]=255
        quad=np.float32([[170,240],[370,240],[370,440],[170,440]])
        return layer,quad

    def test_top_subject_visibly_crosses_frame(self):
        layer,quad=self.sample(3)
        result=audit_popout_projection(layer,quad,width=540,height=960)
        self.assertTrue(result["pass"],result)
        self.assertGreater(result["reveal_outside_ratio"],.012)
        self.assertFalse(result["artistic_approval"])

    def test_subject_staying_inside_frame_is_rejected(self):
        layer,quad=self.sample(148)
        result=audit_popout_projection(layer,quad,width=540,height=960)
        self.assertFalse(result["pass"],result)
        self.assertIn("no_visible_subject_frame_crossing",result["reasons"])

    def test_empty_subject_is_rejected(self):
        layer,quad=self.sample(3)
        layer[:]=0
        self.assertIn("empty_projected_subject",
                      audit_popout_projection(layer,quad)["reasons"])

    def test_gate_precedes_audio_and_video(self):
        code=(ROOT/"engine.py").read_text(encoding="utf-8")
        stage=code[code.index("def run(args):"):]
        self.assertLess(stage.index("crossing=audit_popout_projection"),
                        stage.index("original_sound("))
        self.assertLess(stage.index("crossing=audit_popout_projection"),
                        stage.index("subprocess.Popen(cmd"))

if __name__=="__main__":
    unittest.main()
