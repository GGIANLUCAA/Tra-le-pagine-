"""No-billing tests for the consumer Vidu GitHub automation."""
import hashlib
import json
import os
import pathlib
import tempfile
import unittest
from unittest.mock import patch

from tools import vidu_consumer_autopilot as bot

PROMPT = ("The wounded traveler grips the brass candleholder with his hand, "
          "moves it slowly, and the warm light reveals the shadowed wall. "
          "Preserve the real gesture, clothing, identity and background.")

class ConsumerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cwd=os.getcwd()
        self.addCleanup(os.chdir,self.cwd)
        os.chdir(self.tmp.name)
        pathlib.Path("episodes/oval/images").mkdir(parents=True)
        self.img=pathlib.Path("episodes/oval/images/scene_07.jpg")
        self.img.write_bytes(b"\xff\xd8\xff"+b"testjpeg"*400)
        self.spec={
            "provider":"vidu_consumer_official_cli",
            "model_version":"3.1",
            "model_name":"Q2 (CLI 3.1)",
            "image_path":str(self.img),
            "image_sha256":bot.sha256(self.img),
            "prompt":PROMPT,
            "spoken_line":"Per leggere meglio, sposto il candelabro con la mano",
            "duration":5,"resolution":"1080p","transition":"pro",
            "schedule_mode":"claw_pass","max_credits":8
        }
        self.manifest=pathlib.Path("episodes/oval/VIDU_I2V_APPROVAL.json")
        self.write()

    def write(self):
        self.manifest.write_text(json.dumps(self.spec,indent=2),encoding="utf8")

    def approve(self, user_text=None):
        self.spec["approval"]={
            "status":"explicit_user_approved",
            "plan_code":bot.fingerprint(self.spec)[:12].upper(),
            "user_text":user_text or "Approvo esplicitamente Vidu Q2 (CLI 3.1), scena ovale, 5 secondi, max 8 crediti",
            "max_generations":1
        }
        self.write()

    def test_preflight_matches_image_and_fingerprint(self):
        p,i,c=bot.validate(self.manifest)
        self.assertEqual(c,bot.fingerprint(self.spec)[:12].upper())
        self.assertEqual(i,self.img.resolve())

    def test_missing_explicit_approval_stops_before_quote(self):
        with self.assertRaises(PermissionError):
            bot.validate(self.manifest,approve=True)

    def test_approved_fingerprint_binds_prompt_exactly(self):
        self.approve()
        bot.validate(self.manifest,approve=True)
        self.spec["prompt"]=PROMPT+" Startle his face."
        self.write()
        with self.assertRaises(PermissionError):
            bot.validate(self.manifest,approve=True)

    def test_q2_pro_fast_approval_cannot_be_used_for_consumer_q2(self):
        self.approve("Approvo SCENA A, Vidu Q2 Pro Fast, 5 secondi, massimo 8 crediti.")
        with self.assertRaises(PermissionError):
            bot.validate(self.manifest,approve=True)

    def test_image_changed_stops(self):
        self.approve()
        self.img.write_bytes(self.img.read_bytes()+b"changed")
        with self.assertRaises(ValueError):
            bot.validate(self.manifest,approve=True)

    def test_wrong_provider_blocked(self):
        self.spec["provider"]="vidu_developer"
        self.write()
        with self.assertRaises(ValueError):
            bot.validate(self.manifest)

    def test_cost_over_approved_amount_blocked(self):
        with patch.dict(os.environ,{"VIDU_TOKEN":"TEST_NOT_REAL","VIDU_BASE_URL":bot.CONSUMER_URL}):
            with patch.object(bot,"cli",side_effect=[
                {"ok":True,"has_pass":True,"remain_seconds":10},
                {"ok":True,"cost_credits":9,"can_submit":True}
            ]):
                with self.assertRaises(RuntimeError):
                    bot.quote(self.spec)

    def test_pass_exhausted_no_fallback(self):
        with patch.dict(os.environ,{"VIDU_TOKEN":"TEST_NOT_REAL","VIDU_BASE_URL":bot.CONSUMER_URL}):
            with patch.object(bot,"cli",return_value={"ok":True,"has_pass":True,"remain_seconds":2}) as called:
                with self.assertRaises(RuntimeError):
                    bot.quote(self.spec)
                called.assert_called_once()

    def test_reservation_failure_prevents_post(self):
        self.approve()
        with patch.object(bot,"quote",return_value=8), patch.object(bot,"reserve_once",side_effect=RuntimeError("ledger unavailable")), patch.object(bot,"cli") as called:
            with self.assertRaises(RuntimeError):
                bot.run_submit(self.spec,self.img,"ABCDE1234567",pathlib.Path("output"))
            called.assert_not_called()

    def test_no_token_no_provider_calls(self):
        with patch.dict(os.environ,{"VIDU_TOKEN":"","VIDU_BASE_URL":bot.CONSUMER_URL}):
            with patch.object(bot,"cli") as called:
                with self.assertRaises(RuntimeError):
                    bot.quote(self.spec)
                called.assert_not_called()

if __name__=="__main__":
    unittest.main()
