import unittest
from src.artvision_four_variants_gate import validate

class FourVariantsGateTests(unittest.TestCase):
    def test_empty_fails(self):
        self.assertTrue(validate({}))
    def test_missing_emotional_details_fails(self):
        self.assertTrue(any("details" in x for x in validate({"emotional_direction":{"central_tension":"A","intended_feeling":["wonder"]},"variants":{}})))
    def test_no_fabricated_approval(self):
        self.assertTrue(any("critico_standard" in x for x in validate({"emotional_direction":{"central_tension":"A","intended_feeling":["wonder"],"evidence_details":[],"reveal_order":[],"wow_justification":"B"},"variants":{}})))
if __name__ == "__main__": unittest.main()
