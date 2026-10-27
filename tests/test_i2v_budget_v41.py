"""V41 offline tests; never call a paid API."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

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
        self.image.write_bytes(b"sample non-sensitive placeholder bytes"*100)
        self.out=self.root/"output"
        self.out.mkdir()
        self.prompt="A brass mechanism rotates in the old workshop while the main character pulls a lever."

    def test_720p_off_peak_estimate(self):
        self.assertEqual(v41.estimate(5,True),{"credits":9,"usd":.045})
        self.assertEqual(v41.estimate(5,False),{"credits":18,"usd":.09})
        self.assertEqual(v41.estimate(10,True),{"credits":14,"usd":.07})

    def test_budget_gate_blocks_requests(self):
        with self.assertRaisesRegex(ValueError,"tetto di spesa"):
            v41.plan(self.image,self.prompt,max_cost_usd=.04)
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
        self.assertTrue(message["images"][0].startswith("data:image/png;base64,"))
        self.assertFalse(message["audio"])
        self.assertTrue(message["off_peak"])

    def test_network_timeout_prevents_unintended_retry(self):
        info=v41.plan(self.image,self.prompt)
        with patch.object(v41,"_api",side_effect=TimeoutError("unconfirmed")):
            with self.assertRaises(TimeoutError):
                v41.submit(info,self.out,"mock-not-real")
        record=json.loads((self.out/"VIDU_TASK.json").read_text())
        self.assertEqual(record["status"],"possibly_submitted_check_console")
        with self.assertRaisesRegex(RuntimeError,"già registrata"):
            v41.submit(info,self.out,"mock-not-real")


if __name__=="__main__":unittest.main()
