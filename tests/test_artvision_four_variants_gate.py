"""No paid APIs, no renderer. Verify 4x1 planning and critique contracts."""
import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from src.artvision_four_variants_gate import new_plan, validate
from src.artvision_learning_loop_v1 import (
    SCHEMA as REVIEW_SCHEMA, record, next_lesson, validate_review,
)


def ready_plan():
    plan = new_plan("The Goldfinch", "Carel Fabritius")
    d = plan["emotional_direction"]
    d.update({
        "central_tension": "Un uccellino vivo contrasta con la catena che limita la sua libertà.",
        "intended_feeling": ["tenerezza", "malinconia"],
        "opening_hook": "La piccola creatura sembra libera, ma il dettaglio svela la catena.",
        "closing_payoff": "La sua immobilità diventa il centro della nostra comprensione.",
        "wow_justification": "La catena minuscola cambia come interpretiamo la quiete dell'opera.",
        "evidence_details": [
            {
                "id": f"d{i}",
                "location": f"Area specifica numero {i} in primo piano",
                "observation": f"Particolare visibile e verificabile numero {i}.",
                "significance": f"Il particolare numero {i} sviluppa il significato emotivo.",
                "image_source": "https://example.org/museum-image",
                "claim_type": "documented",
            }
            for i in range(1, 4)
        ],
        "reveal_order": ["d1", "d2", "d3"],
    })
    lines = ["La luce illumina la figura principale.",
             "Un particolare cambia il significato della scena.",
             "L'immagine finale conserva una malinconia sottile."]
    for name, variant in plan["variants"].items():
        variant["variation_reason"] = f"Scelta visiva specifica per {name}, senza duplicare effetti."
        if variant["mode"] == "museum":
            variant["museum"].update({
                "width_cm": 22.8, "height_cm": 33.5,
                "dimensions_source": "Museum official collection object page",
                "frame_status": "documented_current_frame",
                "gallery_id": "gallery-1",
                "entrance_plan": "Avvicinamento credibile alla parete e quadro.",
                "exit_same_gallery_plan": "Ritorno alla stessa parete e posizione.",
            })
            variant["scenes"].append({
                "kind": "gallery_entry",
                "purpose": "Stabilire la scala reale prima di entrare.",
                "movement": "Avvicinamento controllato",
                "emotional_effect": "Curiosità iniziale",
                "duration_seconds": 2.5,
            })
        for i, line in enumerate(lines, 1):
            scene = {
                "kind": "detail",
                "detail_id": f"d{i}",
                "purpose": f"Rivelare un dettaglio significativo {i} e rafforzare il racconto.",
                "movement": "Camera ferma e avvicinamento dolce",
                "emotional_effect": "Il contrasto diventa più intimo",
                "duration_seconds": 7.0,
            }
            if variant["format"] == "critico":
                scene["spoken_line"] = line
            variant["scenes"].append(scene)
        if variant["mode"] == "museum":
            variant["scenes"].append({
                "kind": "gallery_exit",
                "purpose": "Rivedere la scala fisica dopo la scoperta.",
                "movement": "Ritorno graduale e stabile",
                "emotional_effect": "Riflessione e memoria",
                "duration_seconds": 2.5,
            })
    return plan


def review_for_bytes(data):
    return {
        "schema": REVIEW_SCHEMA, "painting_id": "goldfinch",
        "variant": "cinema_museum",
        "video_sha256": hashlib.sha256(data).hexdigest(),
        "inspection": {"watched_full_video": True, "listened_audio": True, "reviewer": "agent"},
        "findings": [
            {"severity": "major", "problem": "Transizione troppo rapida all'inizio.",
             "specific_evidence": "Fotogramma al secondo 2 con salto netto.",
             "likely_cause": "Raccordo non abbastanza preciso.",
             "next_change": "Allungare il passaggio di mezzo secondo.",
             "verification": "Confrontare la scena a velocità normale.",
             "at_second": 0.2},
            {"severity": "minor", "problem": "Chiusura musicale troppo brusca.",
             "specific_evidence": "Il brano si interrompe al secondo 20.",
             "likely_cause": "Fade di uscita non sufficientemente lungo.",
             "next_change": "Estendere di poco il finale musicale.",
             "verification": "Riascoltare gli ultimi cinque secondi.",
             "at_second": 0.7},
        ],
        "next_experiment": {
            "one_variable": "Durata del passaggio di entrata",
            "hypothesis": "Un ingresso più lento migliora la leggibilità.",
            "verification": "Confronto prima e dopo sugli stessi frame.",
        },
        "claims_gold_master": False, "user_approved": False,
    }


class FourVariantsGateTests(unittest.TestCase):
    def test_empty_fails(self):
        self.assertTrue(validate({}))

    def test_blank_scaffold_not_approved(self):
        draft = new_plan("The Goldfinch", "Carel Fabritius")
        self.assertEqual(len(draft["variants"]), 4)
        self.assertTrue(validate(draft))

    def test_complete_plan_passes_structural_review(self):
        self.assertEqual(validate(ready_plan()), [])

    def test_museum_missing_scale_blocks(self):
        p = ready_plan()
        p["variants"]["cinema_museum"]["museum"]["width_cm"] = None
        self.assertTrue(any("width_cm" in s for s in validate(p)))

    def test_critico_must_share_exact_narration(self):
        p = ready_plan()
        p["variants"]["critico_museum"]["scenes"][2]["spoken_line"] = "Un altro racconto."
        self.assertTrue(any("stesso identico" in s for s in validate(p)))

    def test_cinema_cannot_have_narration(self):
        p = ready_plan()
        p["variants"]["cinema_standard"]["scenes"][0]["spoken_line"] = "Sorpresa!"
        self.assertTrue(any("senza voce" in s for s in validate(p)))

    def test_duplicate_detail_identifiers_rejected(self):
        p = ready_plan()
        p["emotional_direction"]["evidence_details"][1]["id"] = "d1"
        self.assertTrue(any("duplicato" in s for s in validate(p)))

    def test_bad_field_types_never_crash(self):
        p = ready_plan()
        p["emotional_direction"]["reveal_order"] = [["bad"], {"bad": True}, 5]
        p["emotional_direction"]["evidence_details"][0]["id"] = ["unhashable"]
        self.assertTrue(validate(p))

    def test_cannot_self_approve_final_mp4(self):
        p = ready_plan()
        p["variants"]["cinema_standard"]["status"] = "approved_for_final_delivery"
        self.assertTrue(any("revisione umana" in s for s in validate(p)))


class SelfCritiqueLedgerTests(unittest.TestCase):
    def test_no_file_no_factual_review(self):
        review = review_for_bytes(b"sample-video-for-tests")
        self.assertTrue(any("--video" in s for s in validate_review(review)))

    def test_wrong_sha_refused_and_correct_sha_recorded(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            vid = root / "example.mp4"
            subprocess.run([
                "ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                "-i", "color=c=black:s=144x256:r=10:d=1",
                "-f", "lavfi", "-i", "sine=duration=1",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-shortest", str(vid)],
                check=True, capture_output=True)
            review = review_for_bytes(vid.read_bytes())
            ledger = root / "learning.jsonl"
            self.assertFalse(record({**review, "video_sha256": "0" * 64}, vid, ledger)["saved"])
            self.assertTrue(record(review, vid, ledger)["saved"])
            self.assertFalse(record(review, vid, ledger)["saved"])
            suggestion = next_lesson(ledger)
            self.assertEqual(suggestion["status"], "proposed_not_proven")
            self.assertEqual(suggestion["based_on_video_sha256"], review["video_sha256"])

    def test_corrupted_bytes_cannot_pass_video_probe(self):
        with tempfile.TemporaryDirectory() as folder:
            vid = Path(folder) / "fake.mp4"
            vid.write_bytes(b"not a real video")
            review = review_for_bytes(vid.read_bytes())
            self.assertTrue(any("ffprobe" in x or "MP4" in x
                                for x in validate_review(review, vid)))

    def test_review_never_certifies_gold_master(self):
        r = review_for_bytes(b"sample")
        r["claims_gold_master"] = True
        r["user_approved"] = True
        self.assertTrue(any("Gold Master" in s for s in validate_review(r)))


if __name__ == "__main__":
    unittest.main()
