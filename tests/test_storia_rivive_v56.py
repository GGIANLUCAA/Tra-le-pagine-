import copy
import importlib.util
import json
import hashlib
import tempfile
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
        p["rights"]["source_rights_clear_for_noncommercial_publication"] = True
        self.assertTrue(mod.evaluate(p, "source")["ok"])

    def test_v59_rejects_non_pd_footage_even_when_nonmonetized(self):
        p = copy.deepcopy(self.pilot)
        p["rights"].update(reviewed_by_human=True,
                           source_rights_clear_for_noncommercial_publication=True)
        for license_name in ("CC BY", "CC BY-NC", "CC BY-NC-SA", "All rights reserved"):
            p["rights"]["license"] = license_name
            self.assertFalse(mod.evaluate(p, "source")["ok"])
        p["rights"]["license"] = "CC0"
        self.assertTrue(mod.evaluate(p, "source")["ok"])

    def test_v59_public_domain_requires_jurisdiction_review(self):
        p = copy.deepcopy(self.pilot)
        p["rights"].update(license="PDM", reviewed_by_human=True,
                           source_rights_clear_for_noncommercial_publication=True,
                           jurisdiction_reviewed=False)
        self.assertFalse(mod.evaluate(p, "source")["ok"])
        p["rights"]["jurisdiction_reviewed"] = True
        self.assertTrue(mod.evaluate(p, "source")["ok"])

    def test_paid_key_is_not_approval(self):
        p = copy.deepcopy(self.pilot)
        p["rights"]["reviewed_by_human"] = True
        p["rights"]["source_rights_clear_for_noncommercial_publication"] = True
        p["cost"]["vidu_calls_planned"] = 1
        self.assertFalse(mod.evaluate(p, "source")["ok"])

    def test_sepia_not_ai(self):
        p = copy.deepcopy(self.pilot)
        p["rights"]["reviewed_by_human"] = True
        p["rights"]["source_rights_clear_for_noncommercial_publication"] = True
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        original = Path(temp.name) / "original.webm"
        original.write_bytes(b"mock-original-test-content")
        p["source"].update(start_sec=1, end_sec=14,
                           original_file_path=str(original),
                           original_sha256=hashlib.sha256(original.read_bytes()).hexdigest())
        p["editorial"].update(opening_0_3="Mani di persone in un'azione reale",
                              reveal_3_7="Dettaglio storico in progressione", framing_reason="Letterbox per salvare volti",
                              no_faces_cut_reviewed=True,first_frame_location_year_verified=True)
        p["colorization"]["mode"] = "sepia_tint"
        p["colorization"]["described_as_ai_colorized"] = True
        self.assertFalse(mod.evaluate(p, "pre-render")["ok"])
        p["colorization"]["described_as_ai_colorized"] = False
        self.assertTrue(mod.evaluate(p, "pre-render")["ok"])

    def test_multicolor_required_for_final_delivery(self):
        p = copy.deepcopy(self.pilot)
        p["colorization"]["mode"] = "sepia_tint"
        out = mod.evaluate(p, "delivery")
        self.assertTrue(any("V56.1" in x and "colorizzazione" in x for x in out["errors"]))
        p["colorization"]["mode"] = "ai_colorized"
        out = mod.evaluate(p, "delivery")
        self.assertTrue(any("V56.1" in x and "multicolore" in x for x in out["errors"]))
        p["colorization"]["natural_multicolor_reviewed"] = True
        p["colorization"]["reference_style_match_reviewed"] = True
        out = mod.evaluate(p, "delivery")
        self.assertFalse(any("V56.1" in x for x in out["errors"]))

    def test_no_false_full_delivery(self):
        p = copy.deepcopy(self.pilot)
        self.assertFalse(mod.evaluate(p, "delivery")["ok"])

if __name__ == "__main__":
    unittest.main()
