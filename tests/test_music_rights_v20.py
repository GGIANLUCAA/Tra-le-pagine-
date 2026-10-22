"""V20 guardrail unit tests; stdlib only, no API/no real publication."""
import copy
import json
import unittest
from pathlib import Path
from src.music_rights_v20 import check

TEMPLATE = json.loads(Path("templates/MUSIC_RELEASE_V20.json").read_text(encoding="utf-8"))


def approved():
    x = copy.deepcopy(TEMPLATE)
    x["video"].update({
        "id": "artvision-sample-001", "originality_statement": "Regia e selezione dei quadri originali",
        "visual_rights_evidence": [{"name": "Opera in pubblico dominio", "proof_url": "https://example.org/proof"}]})
    x["music"].update({
        "title": "Demo", "artist": "Compositore", "origin": "external_licensed",
        "source_url": "https://example.org/track", "recording_proof_url": "https://example.org/recording",
        "license_name": "Commercial permission", "license_url": "https://example.org/terms",
        "license_checked_on": "2026-10-21", "allow_commercial": True,
        "permitted_platforms": ["facebook", "instagram", "youtube"],
        "monetization_allowed": True, "ads_allowed": True, "credit_required": True,
        "credit_text": "Music: Demo — Compositore, used with permission",
        "rights_holder_claim_status": "cleared",
        "emotional_direction": "Tensione con quiete", "cue_notes": "Ingresso e climax verificati"})
    x["qa"] = {k: True for k in x["qa"]}
    x["release"].update({"caption_text": "Testo con i crediti", "user_authorized_publication": True})
    return x


class MusicRightsTests(unittest.TestCase):
    def test_blank_template_requires_review(self):
        self.assertEqual(check(TEMPLATE)["status"], "REVIEW_REQUIRED")

    def test_completed_external_ready_for_manual_publication_only(self):
        result = check(approved())
        self.assertEqual(result["status"], "READY_FOR_MANUAL_PUBLICATION")
        self.assertFalse(result["publication_performed"])
        self.assertFalse(result["legal_certification"])

    def test_missing_approval_holds(self):
        x = approved()
        x["release"]["user_authorized_publication"] = False
        self.assertEqual(check(x)["status"], "REVIEW_REQUIRED")

    def test_commercial_prohibited_blocks(self):
        x = approved()
        x["music"]["allow_commercial"] = False
        self.assertEqual(check(x)["status"], "BLOCKED")

    def test_audio_destination_not_licensed_blocks(self):
        x = approved()
        x["distribution"]["targets"] = ["tiktok"]
        self.assertEqual(check(x)["status"], "BLOCKED")

    def test_meta_sound_collection_cannot_claim_youtube_rights(self):
        x = approved()
        x["music"]["origin"] = "meta_sound_collection"
        x["distribution"]["targets"] = ["facebook", "youtube"]
        self.assertEqual(check(x)["status"], "BLOCKED")

    def test_meta_native_embedded_audio_blocks(self):
        x = approved()
        x["music"]["origin"] = "meta_native_library"
        x["music"]["music_embedded"] = True
        self.assertEqual(check(x)["status"], "BLOCKED")

    def test_native_commercial_requires_specific_permission(self):
        x = approved()
        x["music"]["origin"] = "meta_native_library"
        x["music"]["music_embedded"] = False
        x["distribution"]["platform_native_audio_confirmed"] = True
        self.assertEqual(check(x)["status"], "REVIEW_REQUIRED")

    def test_licence_not_same_as_image_clearance(self):
        x = approved()
        x["video"]["visual_rights_evidence"] = []
        self.assertEqual(check(x)["status"], "REVIEW_REQUIRED")

    def test_disputed_claim_blocks(self):
        x = approved()
        x["music"]["rights_holder_claim_status"] = "disputed"
        self.assertEqual(check(x)["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
