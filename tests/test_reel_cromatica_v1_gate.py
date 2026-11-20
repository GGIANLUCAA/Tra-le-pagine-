"""Regressione del gate `reel_cromatica_v1`: profilo, packaging e standard V28.

Copre i controlli che V19 non legge (i quattro post pubblici distinti) e i
blocchi strutturali del piano di regia.
"""
import copy
import json
import unittest
from pathlib import Path

from src.reel_cromatica_v1_gate import check

EXAMPLE = json.loads(Path("templates/REEL_CROMATICA_V1_CANDIDATE.json").read_text(encoding="utf-8"))
PROFILE = json.loads(Path("config/reel_cromatica_v1.json").read_text(encoding="utf-8"))


class TestReelCromaticaV1Gate(unittest.TestCase):
    def test_candidate_brief_has_no_blocker(self):
        blockers, warnings, facts = check(copy.deepcopy(EXAMPLE), PROFILE)
        self.assertEqual(blockers, [])
        self.assertEqual(facts["shots"], 10)
        self.assertEqual(facts["distinct_works"], 8)
        self.assertEqual(facts["packaging_system"], "chip")
        self.assertTrue(warnings)

    def test_missing_social_posts_is_blocker(self):
        case = copy.deepcopy(EXAMPLE)
        case.pop("social_posts")
        blockers, _, _ = check(case, PROFILE)
        self.assertTrue(any("quattro post" in item for item in blockers))

    def test_empty_post_is_blocker(self):
        case = copy.deepcopy(EXAMPLE)
        case["social_posts"]["tiktok"] = "   "
        blockers, _, _ = check(case, PROFILE)
        self.assertTrue(any("Post tiktok" in item for item in blockers))

    def test_duplicated_posts_are_blocker(self):
        case = copy.deepcopy(EXAMPLE)
        case["social_posts"]["tiktok"] = case["social_posts"]["instagram"]
        blockers, _, _ = check(case, PROFILE)
        self.assertTrue(any("quasi identici" in item for item in blockers))

    def test_forbidden_word_in_post_is_blocker(self):
        case = copy.deepcopy(EXAMPLE)
        case["social_posts"]["facebook"] += "\n\nUn trabajo de regia con zoom."
        blockers, _, _ = check(case, PROFILE)
        self.assertTrue(any("parola vietata" in item for item in blockers))

    def test_forbidden_cliche_in_post_is_blocker(self):
        case = copy.deepcopy(EXAMPLE)
        case["social_posts"]["youtube"] += "\n\nLasciati trasportare."
        blockers, _, _ = check(case, PROFILE)
        self.assertTrue(any("cliché" in item for item in blockers))

    def test_call_to_action_in_post_is_blocker(self):
        case = copy.deepcopy(EXAMPLE)
        case["social_posts"]["instagram"] += "\n\nComenta abajo."
        blockers, _, _ = check(case, PROFILE)
        self.assertTrue(any("richiesta di interazione" in item for item in blockers))

    def test_internal_workflow_term_in_post_is_blocker(self):
        case = copy.deepcopy(EXAMPLE)
        case["social_posts"]["tiktok"] += "\n\nStoryboard y shot list del reel."
        blockers, _, _ = check(case, PROFILE)
        self.assertTrue(any("termine interno" in item for item in blockers))

    def test_post_without_subject_is_blocker(self):
        case = copy.deepcopy(EXAMPLE)
        case["social_posts"]["facebook"] = "Un cuadro muy bonito de un pintor desconocido."
        blockers, _, _ = check(case, PROFILE)
        self.assertTrue(any("non cita l'artista" in item for item in blockers))

    def test_hashtag_count_out_of_range_is_warning(self):
        case = copy.deepcopy(EXAMPLE)
        case["social_posts"]["tiktok"] = case["social_posts"]["tiktok"] + " #Extra #Ancora #Quinto"
        blockers, warnings, _ = check(case, PROFILE)
        self.assertEqual(blockers, [])
        self.assertTrue(any("hashtag" in item and "tiktok" in item for item in warnings))

    def test_duration_equal_to_reference_is_blocker(self):
        case = copy.deepcopy(EXAMPLE)
        shift = PROFILE["reference"]["reference_sample_measured"]["duration_seconds"] - case["episode"]["target_duration_seconds"]
        for shot in case["scenes"]:
            shot["start"] = round(shot["start"] + shift, 3)
            shot["end"] = round(shot["end"] + shift, 3)
        blockers, _, _ = check(case, PROFILE)
        self.assertTrue(any("troppo vicina al campione" in item for item in blockers))

    def test_subtitles_are_blocker(self):
        case = copy.deepcopy(EXAMPLE)
        case["subtitles"] = True
        blockers, _, _ = check(case, PROFILE)
        self.assertTrue(any("Sottotitoli vietati" in item for item in blockers))

    def test_unknown_work_in_sources_is_blocker(self):
        case = copy.deepcopy(EXAMPLE)
        case["scenes"][0]["artwork"] = "Opera Inesistente"
        blockers, _, _ = check(case, PROFILE)
        self.assertTrue(any("non registrata nel registro fonti" in item for item in blockers))

    def test_chip_requires_three_rows(self):
        case = copy.deepcopy(EXAMPLE)
        case["scenes"][0]["on_screen_text"]["rows"] = case["scenes"][0]["on_screen_text"]["rows"][:2]
        blockers, _, _ = check(case, PROFILE)
        self.assertTrue(any("tre righe" in item for item in blockers))

    def test_text_in_final_seconds_is_blocker(self):
        case = copy.deepcopy(EXAMPLE)
        case["scenes"][8]["on_screen_text"] = copy.deepcopy(case["scenes"][0]["on_screen_text"])
        blockers, _, _ = check(case, PROFILE)
        self.assertTrue(any("ultimi" in item for item in blockers))

    def test_auto_zoom_is_blocker(self):
        case = copy.deepcopy(EXAMPLE)
        case["scenes"][0]["camera_reason"] = "auto_zoom"
        blockers, _, _ = check(case, PROFILE)
        self.assertTrue(any("auto_zoom" in item for item in blockers))

    def test_missing_audience_research_is_blocker(self):
        case = copy.deepcopy(EXAMPLE)
        case.pop("audience_research")
        blockers, _, _ = check(case, PROFILE)
        self.assertTrue(any("V32" in item for item in blockers))

    def test_fewer_than_three_candidates_is_blocker(self):
        case = copy.deepcopy(EXAMPLE)
        case["audience_research"]["candidates"] = case["audience_research"]["candidates"][:2]
        blockers, _, _ = check(case, PROFILE)
        self.assertTrue(any("almeno 3" in item for item in blockers))

    def test_duplicate_candidate_is_blocker(self):
        case = copy.deepcopy(EXAMPLE)
        candidates = case["audience_research"]["candidates"]
        candidates[1]["work"] = candidates[0]["work"]
        candidates[1]["artist"] = candidates[0]["artist"]
        blockers, _, _ = check(case, PROFILE)
        self.assertTrue(any("duplicato" in item for item in blockers))

    def test_candidate_without_signal_is_blocker(self):
        case = copy.deepcopy(EXAMPLE)
        case["audience_research"]["candidates"][0].pop("audience_signal")
        blockers, _, _ = check(case, PROFILE)
        self.assertTrue(any("senza segnale dichiarato" in item for item in blockers))

    def test_unavailable_signal_without_reason_is_blocker(self):
        case = copy.deepcopy(EXAMPLE)
        case["audience_research"]["candidates"][0]["audience_signal"] = {"status": "unavailable"}
        blockers, _, _ = check(case, PROFILE)
        self.assertTrue(any("indisponibilità" in item for item in blockers))

    def test_selected_work_must_be_one_of_the_candidates(self):
        case = copy.deepcopy(EXAMPLE)
        case["audience_research"]["selected_work"] = "Opera Non Confrontata"
        blockers, _, _ = check(case, PROFILE)
        self.assertTrue(any("scegliere esplicitamente" in item for item in blockers))


if __name__ == "__main__":
    unittest.main()
