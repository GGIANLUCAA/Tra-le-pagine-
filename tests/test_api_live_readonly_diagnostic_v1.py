"""Offline contract tests for bounded read-only API health audit."""
from __future__ import annotations
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
SRC=Path(__file__).resolve().parents[1]/"src"
sys.path.insert(0,str(SRC))
import api_live_readonly_diagnostic_v1 as mod

class HealthContractTests(unittest.TestCase):
    def test_all_public_sources_exactly_once(self):
        self.assertEqual(len(mod.ARCHIVE_PROBES),11)
        self.assertEqual(len(mod.RARE_PROBES),10)
        self.assertEqual(len(mod.PRIVATE_NAMES),8)
    def test_no_key_skips_network(self):
        with patch.object(mod,"_get_json",side_effect=AssertionError("not allowed")):
            with patch.dict(os.environ,{},clear=True):
                for name in mod.PRIVATE_NAMES:
                    self.assertEqual(mod.private_probe(name)["status"],"NO_KEY_IN_GITHUB_ACTIONS")
    def test_403_is_not_success(self):
        ex=HTTPError("https://api.groq.com/openai/v1/models",403,"Forbidden",{},None)
        with patch.object(mod,"_get_json",side_effect=ex):
            with patch.dict(os.environ,{"PROBE_GROQ":"fake-secret"}):
                self.assertEqual(mod.private_probe("groq")["status"],"AUTH_OR_FORBIDDEN")
    def test_429_not_misreported(self):
        ex=HTTPError("https://api.groq.com/openai/v1/models",429,"Rate limit",{},None)
        with patch.object(mod,"_get_json",side_effect=ex):
            with patch.dict(os.environ,{"PROBE_GROQ":"fake-secret"}):
                self.assertEqual(mod.private_probe("groq")["status"],"RATE_LIMITED")
    def test_nvidia_unsupported_get_not_invalid_key(self):
        ex=HTTPError("https://integrate.api.nvidia.com/v1/models",404,"Not Found",{},None)
        with patch.object(mod,"_get_json",side_effect=ex):
            with patch.dict(os.environ,{"PROBE_NVIDIA":"fake-secret"}):
                self.assertEqual(mod.private_probe("nvidia_catalog")["status"],"ENDPOINT_NOT_DOCUMENTED")
    def test_groq_real_response_shape(self):
        with patch.object(mod,"_get_json",return_value={"data":[{"id":"fake-model"}]}) as fake:
            with patch.dict(os.environ,{"PROBE_GROQ":"fake-secret"}):
                self.assertEqual(mod.private_probe("groq")["status"],"PASS")
            self.assertEqual(fake.call_args.args[0],"https://api.groq.com/openai/v1/models")
    def test_pixabay_url_key_is_not_part_of_report(self):
        key="fixture-secret-value"
        with patch.object(mod,"_get_json",return_value={"hits":[]}) as fake:
            with patch.dict(os.environ,{"PROBE_PIXABAY":key}):
                out=mod.private_probe("pixabay")
                self.assertEqual(out["status"],"PASS")
                self.assertNotIn(key,str(out))
                self.assertIn("key=",fake.call_args.args[0])
    def test_public_empty_result_is_reachable_not_licensed(self):
        with patch.object(mod.archives,"search",return_value={"items":[],"api_requests":1}):
            x=mod.public_probe(("archive","met","Socrates"))
            self.assertEqual(x["status"],"PASS")
            self.assertEqual(x["candidates"],0)
            self.assertIn("no media",x["note"])
    def test_no_payment_or_generation(self):
        import inspect
        src=inspect.getsource(mod)
        self.assertNotIn('method="POST"',src)
        self.assertNotIn("generate_draft(",src)
        self.assertNotIn("preview_clip(",src)

if __name__=="__main__":
    unittest.main()
