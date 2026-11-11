import unittest
from director_qa import audit

class DirectorTests(unittest.TestCase):
    def test_real_hook_and_semantic_checks(self):
        scenes=[]
        for i in range(4):
            scenes.append({"visual_start_sec":float(i*4),"visual_end_sec":float((i+1)*4),
                           "subject":"excavation" if i<3 else "portrait",
                           "sentence":"Baffi, capelli e volti" if i==3 else "Lo scavo"})
        result=audit({"scene_to_sentence_alignment":scenes})
        self.assertEqual(result["critical_count"],1)
        self.assertTrue(any(x["code"]=="HOOK_NO_ARMY_WIDE" for x in result["issues"]))
    def test_true_formation_hook(self):
        scenes=[{"visual_start_sec":0,"visual_end_sec":3,"subject":"formation","sentence":"Esercito"},
                {"visual_start_sec":3,"visual_end_sec":7,"subject":"weapons","sentence":"Le frecce"}]
        result=audit({"scene_to_sentence_alignment":scenes})
        self.assertEqual(result["critical_count"],0)
        self.assertEqual(result["review_count"],0)
    def test_detail_claim_not_proven_by_generic_detail(self):
        scenes=[{"visual_start_sec":0,"visual_end_sec":2,"subject":"formation","sentence":"Esercito"},
                {"visual_start_sec":2,"visual_end_sec":7.8,"subject":"detail","sentence":"Le scarpe"}]
        result=audit({"scene_to_sentence_alignment":scenes})
        self.assertTrue(any(x["code"]=="SEMANTIC_REVIEW" for x in result["issues"]))
        self.assertTrue(any(x["code"]=="LONG_HOLD" for x in result["issues"]))

if __name__=="__main__":unittest.main()
