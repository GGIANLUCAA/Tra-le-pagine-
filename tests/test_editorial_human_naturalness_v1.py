"""Human tone rule: never claim AI detection or block genuine artistic endings."""
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from editorial_human_naturalness_v1 import review

OLD_BRUEGEL = """A prima vista è un vortice senza fine. Angeli e creature mostruose.
Vicino al centro compare l'arcangelo Michele.

La lotta tra bene e male sembra infinita. E il quadro ci lascia una domanda:
il mostruoso appartiene davvero a un altro mondo, oppure nasce già dentro il nostro?"""

NEW_BRUEGEL = """Bruegel dipinge Michele al centro, con la spada in alto.
Attorno si affollano figure, pesci, artigli e armature.

Michele è ancora lì, in mezzo alla mischia. E accanto alla sua spada
c'è un volto minuscolo che a una prima occhiata quasi sfugge."""


class HumanToneEditorialTests(unittest.TestCase):
    def test_reject_specific_stock_final_from_actual_work(self):
        r=review(OLD_BRUEGEL,format_name="artvision_critico")
        self.assertEqual(r["status"],"revision_required")
        self.assertIn("STOCK_FINAL_QUESTION",[x["code"] for x in r["blocking"]])
        self.assertFalse(r["human_approved"])
        self.assertFalse(r["ai_authorship_detected"])

    def test_new_specific_observation_not_automatically_approved(self):
        r=review(NEW_BRUEGEL,format_name="artvision_critico")
        self.assertEqual(r["blocking"],[])
        self.assertEqual(r["status"],"no_stock_phrases_found_not_approved")
        self.assertFalse(r["human_approved"])

    def test_genuine_research_question_is_not_forbidden(self):
        script="Nel dipinto manca una data certa.\n\nQuale fonte documenta la commissione?"
        r=review(script)
        self.assertEqual(r["blocking"],[])
        self.assertIn("FINAL_QUESTION_NEEDS_PURPOSE",[x["code"] for x in r["warnings"]])

    def test_stock_invitation_blocks_only_finale(self):
        good="Il quadro ci invita a riflettere, scrive il catalogo. Poi il pittore cambiò composizione.\n\nSulla tela resta la spada di Michele."
        self.assertEqual(review(good)["blocking"],[])
        bad="La scena mostra molti animali.\n\nL'opera ci invita a riflettere."
        self.assertIn("STOCK_FINAL_INVITATION",[i["code"] for i in review(bad)["blocking"]])

    def test_normal_documentary_ending_is_allowed(self):
        s="Il restauro è stato terminato nel 1997.\n\nOggi si vedono ancora le parti in legno rimaste scoperte."
        self.assertEqual(review(s,format_name="documentario")["blocking"],[])

    def test_soft_formula_warns_without_making_artificial_determinations(self):
        r=review("Non è soltanto una figura, ma anche un simbolo.\n\nLa mano è dipinta in alto.")
        self.assertIn("FORMULA_NOT_JUST_BUT",[x["code"] for x in r["warnings"]])
        self.assertEqual(r["blocking"],[])
        self.assertFalse(r["ai_authorship_detected"])

    def test_silent_video_caption_and_social_copy_are_supported(self):
        for context in ("on_screen","social_copy"):
            r=review("Paris · 1898",format_name="storia_rivive",context=context)
            self.assertEqual(r["blocking"],[])
            self.assertEqual(r["context"],context)

    def test_malformed_and_empty_are_safe(self):
        with self.assertRaises(TypeError):review(None)
        with self.assertRaises(ValueError):review("valid",context="unknown")
        self.assertEqual(review("  ")["status"],"revision_required")

    def test_does_not_rewrite_user_content_or_generate_voice(self):
        r=review(OLD_BRUEGEL)
        self.assertFalse(r["rewrote_script"])
        self.assertEqual(r["new_tts_calls"],0)


if __name__=="__main__":
    unittest.main()
