#!/usr/bin/env python3
"""Off-line tests: no online assets, no false aesthetic / rights certification."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("artvision_contract_gate_v25", ROOT/"src"/"artvision_contract_gate_v25.py")
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def sample():
    artist="TEST ARTIST"; composer="TEST COMPOSER"; title="THE TEST PAINTING"
    return dict(
        schema="artvision-release-contract-v25",
        video_id="artvision-test-episode-00001",format="artvision_cinema",approved_baseline="cinema_v6",
        artwork={"artist":artist,"title_en":title,"title_language":"en",
                 "identity_source":"https://example.org/test-museum-artwork"},
        opening={"identity_preset":"modules/artvision/IDENTITA_VISIVA_FISSA_V6.json",
                 "artist_text":artist,"composer":composer,
                 "music_credit_text":"MUSIC BY "+composer},
        cover={"identity_family":"cinema_v6","title_en":title,"artist":artist,
               "language":"en","existing_design_unchanged":True},
        on_screen_text=[{"role":"opening_artist","text":artist},
                        {"role":"opening_music","text":"MUSIC BY "+composer}],
        voice=False, subtitles=False,
        first_seven_seconds=[{"second":s,"what_visible":"A visible real painting detail",
                              "why":"This detail establishes authentic visual tension"}
                              for s in (0,1,3,5,7)],
        duration_reason="Music and emotional sequence determines runtime without filler.",
        scenes=[{"source_id":"authentic-art-source","subject":"Legible true artwork detail",
                 "purpose":"Reveal another subject in this genuine artwork",
                 "shot":typ, "motion":"locked","duration_seconds":6}
                for typ in ("wide","detail","macro","portrait","medium","texture","full","detail")],
        transition_reviews_plan=[{"why":"Visual relationship and real musical phrase motivate this cut"}
                                  for _ in range(3)],
        music_cues=[{"reason":"Musical structure dictates the camera and pause"} for _ in range(3)],
        selected_techniques=[
            {"id":"visual_hierarchy","why":"Keep main painted figure in focus"},
            {"id":"motivated_cut","why":"Move to thematically related subject"},
            {"id":"rhythmic_rest","why":"Pause before musical resolution"}
        ],
        sources=[{"id":"authentic-art-source","url":"https://example.org/art",
                  "license":"Public domain work, rights checked","credit":"Example Museum source","status":"verified"}],
        music={"title":"Original test score","composer":composer,"origin":"original",
               "license":"Owned original test recording","evidence":"local source project",
               "emotional_arc":"Intro, tension and gentle closing", "rights_status":"verified"},
        copy_languages={"facebook":"it"},archive_only_after_authorization=True,
        social_autopublish=False,outputs={key:name for key,name in gate.FIELDS.items()},
        review_video_sha256="REPLACE_SHA256_AFTER_RENDER",
        reviews={key:{"passed":False,"notes":"Await actual human inspection at original playback speed."}
                 for key in gate.REVIEW_KEYS},
        publication={"status":"not_published"}
    )


class ContractTests(unittest.TestCase):
    def test_valid_structural_preflight(self):
        self.assertEqual(gate.check_preflight(sample()),[])

    def test_v21_cinema_package_includes_v25_contract(self):
        from src.creative_director_v21 import write_package
        brief={
            "format":"artvision_cinema",
            "project_id":"artvision-munch-test-episode",
            "artist":"Edvard Munch",
            "artwork_title_en":"The Scream",
            "topic":"The Scream",
            "original_value":"Creative art direction with verified real composition",
            "hook":"The expressive painted figure starts the scene.",
            "resolution":"The artwork is revealed fully at the last phrase.",
            "shots":[{"seconds":5,"purpose":"Visual story beat"} for _ in range(9)]
        }
        with tempfile.TemporaryDirectory() as td:
            result=write_package(brief,Path(td))
            manifest=Path(td)/"ARTVISION_CONTRACT_V25.json"
            self.assertTrue(manifest.is_file())
            payload=json.loads(manifest.read_text(encoding="utf8"))
            self.assertEqual(payload["artwork"]["title_en"],"The Scream")
            self.assertEqual(payload["artwork"]["artist"],"EDVARD MUNCH")
            self.assertTrue(gate.check_preflight(payload))
            self.assertFalse(result["ready_to_publish"])

    def test_scaffold_from_brief_never_approves(self):
        with tempfile.TemporaryDirectory() as td:
            manifest = gate.scaffold_from_brief(
                {"project_id":"artvision-test-2468","artist":"Edvard Munch",
                 "artwork_title_en":"The Scream"}, Path(td))
            parsed=json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(parsed["artwork"]["artist"],"EDVARD MUNCH")
            self.assertEqual(parsed["artwork"]["title_en"],"The Scream")
            self.assertEqual(parsed["artwork"]["title_language"],"en")
            self.assertTrue(gate.check_preflight(parsed),
                "Brief scaffold must remain incomplete until the agent verifies rights, music and scenes.")
            manifest.write_text('{"custom":"do not overwrite"}',encoding="utf-8")
            gate.scaffold_from_brief({"artist":"Other artist"},Path(td))
            self.assertEqual(json.loads(manifest.read_text(encoding="utf-8"))["custom"],
                             "do not overwrite")

    def test_template_is_draft_not_approval(self):
        draft=json.loads((ROOT/"templates"/"ARTVISION_CONTRACT_V25.json").read_text(encoding="utf-8"))
        self.assertTrue(gate.check_preflight(draft))
        self.assertTrue(all(not x["passed"] for x in draft["reviews"].values()))

    def test_foreign_language_or_wrong_opening_blocked(self):
        obj=sample()
        obj["artwork"]["title_language"]="it"
        obj["on_screen_text"].append({"role":"subtitle","text":"Guarda questo dipinto!"})
        error="\n".join(gate.check_preflight(obj))
        self.assertIn("en obbligatorio",error)
        self.assertIn("Nel film Cinema soltanto",error)

    def test_no_weak_unmotivated_slideshow(self):
        obj=sample()
        obj["scenes"]=obj["scenes"][:4]
        obj["transition_reviews_plan"]=[]
        error="\n".join(gate.check_preflight(obj))
        self.assertIn("Almeno 8 scelte",error)
        self.assertIn("almeno tre transizioni",error)

    def test_identity_is_immutable(self):
        obj=sample()
        obj["opening"]["identity_preset"]="new-random-font"
        obj["cover"]["existing_design_unchanged"]=False
        error="\n".join(gate.check_preflight(obj))
        self.assertIn("identita V6",error)
        self.assertIn("Gold Master storico invariato",error)

    def test_rights_and_caption_are_mandatory(self):
        obj=sample()
        obj["sources"][0]["status"]="unknown"
        obj["music"]["rights_status"]="unchecked"
        obj["copy_languages"]["facebook"]="en"
        error="\n".join(gate.check_preflight(obj))
        self.assertIn("Fonte visiva",error)
        self.assertIn("Musica:",error)
        self.assertIn("Facebook italiana",error)

    def test_techniques_and_motion_must_be_real(self):
        obj=sample()
        obj["selected_techniques"][0]["id"]="made_up_effect"
        obj["scenes"][0]["motion"]="oscillate"
        error="\n".join(gate.check_preflight(obj))
        self.assertIn("inesistente",error)
        self.assertIn("moto macchina non permesso",error)

    def test_delivery_zip_contains_every_required_file_and_no_overwrite(self):
        import zipfile
        data=sample()
        data["video_id"]="example-batch-999"
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)
            manifest=base/"ARTVISION_CONTRACT_V25.json"
            manifest.write_text(json.dumps(data),encoding="utf-8")
            for filename in gate.FIELDS.values():
                (base/filename).write_bytes(b"synthetic test bytes for packaging only")
            frames=base/"QA_V25"
            frames.mkdir()
            for second in gate.REVIEW_SECONDS:
                (frames/f"FRAME_{second:02d}.jpg").write_bytes(b"synthetic frame test only")
            data_info={"video_sha256":"1"*64}
            archive=gate.pack_delivery(manifest,data,data_info)
            self.assertTrue(archive.is_file())
            with zipfile.ZipFile(archive) as z:
                names=set(z.namelist())
            self.assertIn("VIDEO_MASTER.mp4",names)
            self.assertIn("COPERTINA.jpg",names)
            self.assertIn("POST_FACEBOOK.txt",names)
            self.assertIn("VIDEO_RECIPE_V13.json",names)
            self.assertIn("ISTRUZIONI_REPLICA.md",names)
            self.assertIn("ARTVISION_CONTRACT_V25.json",names)
            self.assertIn("QA_V25/FRAME_07.jpg",names)
            before=archive.stat().st_mtime_ns
            again=gate.pack_delivery(manifest,data,data_info)
            self.assertEqual(archive,again)
            self.assertEqual(before,archive.stat().st_mtime_ns)

    def test_final_rejects_missing_media_and_posts(self):
        obj=sample()
        with tempfile.TemporaryDirectory() as td:
            errors, facts=gate.check_final(obj,Path(td))
        self.assertIn("VIDEO_MASTER.mp4","\n".join(errors))
        self.assertIn("COPERTINA.jpg","\n".join(errors))
        self.assertIsNone(facts["video_sha256"])

    def test_final_rejects_deceptive_review_without_files(self):
        obj=sample()
        obj["reviews"]={key:{"passed":True,"notes":"I viewed and verified the scene, color, sound and actual image."}
                        for key in gate.REVIEW_KEYS}
        with tempfile.TemporaryDirectory() as td:
            errors,_=gate.check_final(obj,Path(td))
        self.assertTrue(any("VIDEO_MASTER.mp4" in x for x in errors))

    def test_no_duplicate_technique(self):
        obj=sample()
        obj["selected_techniques"].append(obj["selected_techniques"][0].copy())
        self.assertTrue(any("duplicate" in x.lower() for x in gate.check_preflight(obj)))


if __name__=="__main__":
    unittest.main()
