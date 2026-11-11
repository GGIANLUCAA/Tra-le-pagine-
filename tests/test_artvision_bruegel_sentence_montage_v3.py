"""V3 speech-to-camera tests: actual timecodes, authentic artwork anchors, no aesthetic approval."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from artvision_bruegel_sentence_montage_v3 import BEATS,sentence_plan,sentence_index


class NarrativeBeatsTests(unittest.TestCase):
    def setUp(self):
        self.chapters=[{"cx":.5,"cy":.5,"crop_height_px":1200,
                        "focus":f"source anchor {i}"} for i in range(9)]
        self.timed=[(f"Frase {i}",float(i)*4,float(i)*4+3.) for i in range(18)]

    def make(self,**kw):
        return sentence_plan(kw.get("timed",self.timed),
                             kw.get("chapters",self.chapters),
                             3.5,"a"*64,"b"*64)

    def test_all_beats_from_real_asr(self):
        x=self.make()
        self.assertEqual(len(x["shots"]),18)
        self.assertEqual(x["shots"][7]["camera_area"],"wide")
        self.assertEqual(x["shots"][7]["reason"],
                         "Show sky-to-lower-dark contrast in the entire authentic work")
        self.assertEqual(x["shots"][7]["video_start_s"],31.5)
        self.assertFalse(x["artistic_approved"])
        self.assertTrue(x["no_new_voice_calls"])

    def test_sentence_switch_uses_actual_end_and_pause(self):
        self.assertEqual(sentence_index(self.timed,2.4),0)
        self.assertEqual(sentence_index(self.timed,3.2),0)
        self.assertEqual(sentence_index(self.timed,3.8),0)
        self.assertEqual(sentence_index(self.timed,3.9),1)
        self.assertEqual(sentence_index(self.timed,4.4),1)
        self.assertEqual(sentence_index(self.timed,7.5),1)
        self.assertEqual(sentence_index(self.timed,7.88),2)
        self.assertEqual(sentence_index(self.timed,71.),17)

    def test_backward_asr_fails_closed(self):
        b=list(self.timed)
        b[7]=("invalid",3,4)
        with self.assertRaises(ValueError):self.make(timed=b)

    def test_unknown_source_camera_anchor_blocked(self):
        b=list(self.chapters)
        b[4]={"focus":"unverified"}
        with self.assertRaises(ValueError):self.make(chapters=b)

    def test_wrong_count_does_not_guess_timestamps(self):
        with self.assertRaises(ValueError):self.make(timed=self.timed[:-1])


if __name__=="__main__":unittest.main()
