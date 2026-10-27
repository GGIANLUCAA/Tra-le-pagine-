"""V41 offline tests; never call a paid API."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image

SOURCE=Path(__file__).resolve().parent.parent/"src"/"i2v_budget_v41.py"
spec=importlib.util.spec_from_file_location("i2v_budget_v41",SOURCE)
v41=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v41)


class BudgetV41Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.image=self.root/"image.png"
        Image.effect_noise((400,710), 55).convert("RGB").save(self.image)
        self.out=self.root/"output"
        self.out.mkdir()
        self.prompt="A brass mechanism rotates in the old workshop while the main character pulls a lever."

    def test_720p_off_peak_estimate(self):
        self.assertEqual(v41.estimate(5,True),{"credits":8,"usd":.04})
        self.assertEqual(v41.estimate(5,False),{"credits":16,"usd":.08})
        self.assertEqual(v41.estimate(10,True),{"credits":13,"usd":.065})

    def test_budget_gate_blocks_requests(self):
        with self.assertRaisesRegex(ValueError,"tetto di spesa"):
            v41.plan(self.image,self.prompt,max_cost_usd=.035)
        with self.assertRaisesRegex(ValueError,"Durata"):
            v41.estimate(11)
        with self.assertRaisesRegex(ValueError,"azione"):
            v41.plan(self.image,"pan zoom")

    def test_planned_request_no_network(self):
        with patch.object(v41,"_api",side_effect=AssertionError("API MUST NOT BE CALLED")):
            info=v41.plan(self.image,self.prompt)
            self.assertEqual(info["status"],"planned_not_submitted")
            self.assertTrue(info["off_peak"])
            self.assertFalse(info["audio"])
            self.assertFalse(info["is_rec"])
            self.assertTrue(info["review_required"])

    def test_payload_starts_from_image_and_no_audio(self):
        info=v41.plan(self.image,self.prompt)
        message=v41._payload(info)
        self.assertEqual(message["model"],"viduq2-pro-fast")
        self.assertTrue(message["images"].startswith("data:image/png;base64,"))
        self.assertFalse(message["audio"])
        self.assertTrue(message["off_peak"])

    def test_economy_turbo_low_budget(self):
        self.assertEqual(v41.estimate(3,True,"economy540"),
                         {"credits":5,"usd":.025})
        self.assertEqual(v41.estimate(5,True,"economy540"),
                         {"credits":7,"usd":.035})
        self.assertEqual(v41.estimate(2,True,"economy540"),
                         {"credits":4,"usd":.02})
        with self.assertRaisesRegex(ValueError,"tetto di spesa"):
            v41.plan(self.image,self.prompt,3,True,.02,"economy540")
        info=v41.plan(self.image,self.prompt,3,True,.03,"economy540")
        self.assertEqual(info["model"],"viduq2-turbo")
        self.assertEqual(info["resolution"],"540p")
        request=v41._payload(info)
        self.assertIsInstance(request["images"],list)
        self.assertEqual(len(request["images"]),1)
        self.assertTrue(request["images"][0].startswith("data:image/png;base64,"))
        self.assertFalse(request["audio"])
        self.assertEqual(request["duration"],3)

    def test_no_credits_for_existing_secret_without_explicit_per_scene_consent(self):
        info=v41.plan(self.image,self.prompt)
        self.assertEqual(info["status"],"planned_not_submitted")
        self.assertEqual(len(info["approval_code"]),12)
        with patch.object(v41,"_api",side_effect=AssertionError("NO CREDIT CALL")) as api:
            for value in ("", "AUTORIZZO_10_CENT", "ABC123456789", None):
                with self.assertRaises(PermissionError):
                    v41.submit(info,self.out,"even-if-key-installed",value)
            api.assert_not_called()
        self.assertFalse((self.out/"VIDU_TASK.json").exists())

    def test_exact_plan_code_invalidates_when_any_parameter_changes(self):
        a=v41.plan(self.image,self.prompt,3,True,.1,"economy540")
        variants=[
            v41.plan(self.image,self.prompt+" A bird flies overhead.",3,True,.1,"economy540"),
            v41.plan(self.image,self.prompt,4,True,.1,"economy540"),
            v41.plan(self.image,self.prompt,3,False,.1,"economy540"),
            v41.plan(self.image,self.prompt,3,True,.1,"cinema720"),
        ]
        for variant in variants:
            with self.assertRaises(PermissionError):
                v41.verify_approved_plan(variant,a["approval_code"])
        self.image.write_bytes(self.image.read_bytes()+b"change")
        changed=v41.plan(self.image,self.prompt,3,True,.1,"economy540")
        with self.assertRaises(PermissionError):
            v41.verify_approved_plan(changed,a["approval_code"])

    def test_network_timeout_prevents_unintended_retry(self):
        info=v41.plan(self.image,self.prompt)
        with patch.object(v41,"_api",side_effect=TimeoutError("unconfirmed")):
            with self.assertRaises(TimeoutError):
                v41.submit(info,self.out,"mock-not-real",info["approval_code"])
        record=json.loads((self.out/"VIDU_TASK.json").read_text())
        self.assertEqual(record["status"],"possibly_submitted_check_console")
        with self.assertRaisesRegex(RuntimeError,"già registrata"):
            v41.submit(info,self.out,"mock-not-real",info["approval_code"])


if __name__=="__main__":unittest.main()
