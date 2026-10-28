import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("v56", ROOT / "src/storia_rivive_preflight_v56.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class HistoricalRulesV56(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pilot = json.loads((ROOT / "templates/STORIA_RIVIVE_V56_EPISODE.json").read_text(encoding="utf-8"))

    def test_pilot_remains_blocked(self):
        report = mod.evaluate(self.pilot, "source")
        self.assertFalse(report["ok"])
        self.assertTrue(any("diritti" in x.lower() for x in report["errors"]))

    def test_source_gate(self):
        p = copy.deepcopy(self.pilot)
        p["rights"]["reviewed_by_human"] = True
        p["rights"]["source_rights_clear_for_commercial_reuse"] = True
        self.assertTrue(mod.evaluate(p, "source")["ok"])

    def test_paid_key_is_not_approval(self):
        p = copy.deepcopy(self.pilot)
        p["rights"]["reviewed_by_human"] = True
        p["rights"]["source_rights_clear_for_commercial_reuse"] = True
        p["cost"]["vidu_calls_planned"] = 1
        self.assertFalse(mod.evaluate(p, "source")["ok"])

    def test_sepia_not_ai(self):
        p = copy.deepcopy(self.pilot)
        p["rights"]["reviewed_by_human"] = True
        p["rights"]["source_rights_clear_for_commercial_reuse"] = True
        p["source"].update(start_sec=1, end_sec=14)
        p["editorial"].update(opening_0_3="Mani di persone in un'azione reale",
                              reveal_3_7="Dettaglio storico in progressione", framing_reason="Letterbox per salvare volti",
                              no_faces_cut_reviewed=True,first_frame_location_year_verified=True)
        p["colorization"]["mode"] = "sepia_tint"
        p["colorization"]["described_as_ai_colorized"] = True
        self.assertFalse(mod.evaluate(p, "pre-render")["ok"])
        p["colorization"]["described_as_ai_colorized"] = False
        self.assertTrue(mod.evaluate(p, "pre-render")["ok"])

    def test_no_false_full_delivery(self):
        p = copy.deepcopy(self.pilot)
        self.assertFalse(mod.evaluate(p, "delivery")["ok"])

if __name__ == "__main__":
    unittest.main()
