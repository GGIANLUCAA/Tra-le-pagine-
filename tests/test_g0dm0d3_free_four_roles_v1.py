#!/usr/bin/env python3
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import g0dm0d3_free_four_roles_v1 as p

CATALOGUE={"data":[
    {"id":p.MODELS[0],"pricing":{"prompt":"0","completion":"0","request":"0"}},
    {"id":p.MODELS[1],"pricing":{"prompt":"0.000000","completion":"0","request":0}},
]}


class FreeOnlyFourRoles(unittest.TestCase):
    def test_dry_run_never_sends_request(self):
        with mock.patch.object(p,"_get_json",side_effect=AssertionError("NO NETWORK")):
            r=p.experiment("giuliano","Anticitera un computer antico",key="",execute=False)
        self.assertEqual(r["status"],"dry_run_no_inference")
        self.assertEqual(r["model_calls"],0)
        self.assertFalse(r["video_rendered"])

    def test_no_key_fails_without_catalogue_or_model_calls(self):
        with mock.patch.object(p,"_get_json",side_effect=AssertionError("NO NETWORK")):
            r=p.experiment("giuliano","Anticitera meccanismo in bronzo",key="",execute=True)
        self.assertEqual(r["status"],"blocked_missing_openrouter_key")
        self.assertEqual(r["model_calls"],0)

    def test_live_zero_price_only(self):
        self.assertEqual(p.attest_live_free_models(CATALOGUE)["max_prompts"],4)
        for price in ("0.0001","3","-0.002","unknown"):
            bad=json.loads(json.dumps(CATALOGUE))
            bad["data"][0]["pricing"]["completion"]=price
            with self.subTest(price=price),self.assertRaises(p.FreeOnlyError):
                p.attest_live_free_models(bad)
        with self.assertRaises(p.FreeOnlyError):
            p.attest_live_free_models({"data":[CATALOGUE["data"][0]]})

    def test_four_roles_two_distinct_pinned_free_models_exactly_four_attempts(self):
        prompts=[]
        def fake_ask(model,text,key):
            prompts.append((model,text))
            return {"text":"Analisi specifica sul reperto, timpi e regia "+str(len(prompts)),
                    "model":model,"reported_cost_usd":0,"human_approved":False}
        with mock.patch.object(p,"_get_json",side_effect=AssertionError("NO NETWORK")):
            r=p.experiment("giuliano","Anticitera meccanismo in bronzo",key="safe-placeholder",
                           catalogue=CATALOGUE,execute=True,ask=fake_ask)
        self.assertEqual(r["status"],"four_roles_returned_unapproved")
        self.assertEqual(r["model_calls"],4)
        self.assertEqual([x[0] for x in prompts],list(p.MODEL_FOR_ROLE))
        self.assertTrue(all(":free" in x[0] for x in prompts))
        self.assertEqual([x["role"] for x in r["responses"]],list(p.ROLES))
        self.assertIn("Analisi specifica",prompts[3][1])
        self.assertFalse(r["human_artistic_approval"])
        self.assertFalse(r["publication_authorized"])
        self.assertFalse(r["video_rendered"])
        with tempfile.TemporaryDirectory() as tmp:
            p.save(r,tmp)
            self.assertTrue((Path(tmp)/"ANDROID_REPORT.html").exists())
            self.assertTrue((Path(tmp)/"REPORT.json").exists())

    def test_stop_on_first_error_no_retry(self):
        calls=[]
        def broken(model,prompt,key):
            calls.append(model)
            raise p.FreeOnlyError("quota exhausted")
        r=p.experiment("giuliano","Anticitera meccanismo in bronzo",key="safe-placeholder",
                       catalogue=CATALOGUE,execute=True,ask=broken)
        self.assertEqual(r["status"],"incomplete_no_retry")
        self.assertEqual(r["model_calls"],1)
        self.assertEqual(len(calls),1)

    def test_no_explicit_payment_or_auto_router(self):
        for model in ("openrouter/free","google/gemma-4-31b-it","openai/gpt-4.1",
                      "nvidia/nemotron-3-super-120b-a12b:free"):
            with self.assertRaises(p.FreeOnlyError):
                p._request_free(model,"Anticitera nel mare antico, scena e narrazione"*5,"none",
                                transport=lambda req: self.fail("POST forbidden"))
        with self.assertRaises(p.FreeOnlyError):
            p._request_free(p.MODELS[0],"A"*120,"key",transport=lambda req:{
                "model":"openai/gpt-4.1",
                "choices":[{"message":{"content":"Valid text"*7}}],
                "usage":{"cost":0}})
        with self.assertRaises(p.FreeOnlyError):
            p._request_free(p.MODELS[0],"A"*120,"key",transport=lambda req:{
                "model":p.MODELS[0],
                "choices":[{"message":{"content":"Valid text"*7}}],
                "usage":{"cost":0.001}})

    def test_request_has_exact_free_model_no_fallback_and_zero_max_price(self):
        request_seen=[]
        def transport(req):
            raw=json.loads(req.data)
            request_seen.append(raw)
            return {"model":p.MODELS[0],"choices":[{"message":{"content":"Specific response "*5}}],
                    "usage":{"cost":0}}
        p._request_free(p.MODELS[0],"Film documentario su Anticitera " * 4,
                        "not-a-real-key",transport=transport)
        body=request_seen[0]
        self.assertEqual(body["model"],p.MODELS[0])
        self.assertFalse(body["provider"]["allow_fallbacks"])
        self.assertEqual(body["provider"]["max_price"],{"prompt":0,"completion":0})
        self.assertLessEqual(body["max_tokens"],1200)
        self.assertEqual(body["reasoning"],{"enabled":False})
        self.assertNotIn("models",body)

    def test_liquid_does_not_inherit_nvidia_reasoning_override(self):
        seen=[]
        def transport(req):
            obj=json.loads(req.data);seen.append(obj)
            return {"model":p.MODELS[1],
                    "choices":[{"message":{"content":"Questa e una risposta specifica sul reperto e sulle ricostruzioni."}}],
                    "usage":{"cost":0}}
        result=p._request_free(p.MODELS[1],"Narrativa di Anticitera e ingranaggi "*4,
                               "fake",transport=transport)
        self.assertNotIn("reasoning",seen[0])
        self.assertEqual(result["reported_cost_usd"],0)

    def test_real_antikythera_scene_map_is_shared_with_all_roles(self):
        saved=[]
        def responder(model,text,key):
            saved.append(text)
            return {"text":"Una proposta verificabile con tempi fotografici corretti "+str(len(saved)),
                    "model":model,"reported_cost_usd":0,"human_approved":False}
        result=p.experiment("giuliano","Anticitera: migliori movimenti e regia in 20 scene",
                            key="fake",catalogue=CATALOGUE,execute=True,ask=responder)
        self.assertEqual(result["status"],"four_roles_returned_unapproved")
        self.assertEqual(len(saved),4)
        self.assertTrue(all("126,12 s" in text for text in saved))
        self.assertTrue(all("le foto NON sono scansioni X" in text for text in saved))
        self.assertTrue(all("75,21-96 s" in text for text in saved))
        self.assertTrue(all(len(text) <= 6500 for text in saved))

    def test_escape_untrusted_model_text_in_android(self):
        with tempfile.TemporaryDirectory() as tmp:
            r={"status":"four_roles_returned_unapproved",
               "model_calls":1,"responses":[{"role":"critico","model":p.MODELS[0],
                                            "text":"<script>alert('x')</script>"}]}
            p.save(r,tmp)
            s=(Path(tmp)/"ANDROID_REPORT.html").read_text()
            self.assertNotIn("<script>",s)
            self.assertIn("&lt;script&gt;",s)

if __name__ == "__main__":
    unittest.main()
