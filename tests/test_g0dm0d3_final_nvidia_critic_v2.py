#!/usr/bin/env python3
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import g0dm0d3_free_four_roles_v1 as board
import g0dm0d3_final_nvidia_critic_v2 as final

CAT={"data":[{"id":m,"pricing":{"prompt":"0","completion":"0","request":"0"}}
             for m in board.MODELS]}


def prior():
    return {
        "schema":"g0dm0d3-four-role-resume-critic-v1",
        "status":"critic_only_incomplete_no_retry",
        "source_run_id":final.PREVIOUS_ORIGINAL_RUN,
        "source_report_sha256":final.PREVIOUS_ORIGINAL_SHA256,
        "model_calls":5,"resumed_attempts":1,
        "failure_reason":"No displayable text: finish_reason=length",
        "format":"giuliano","subject":"Anticitera 20 scene e ingranaggi",
        "models":list(board.MODELS),"publication_authorized":False,
        "video_rendered":False,
        "responses":[{"role":role,"model":model,
                      "text":"Fatti e dettagli basati sul bronzo del film verificato. "*4,
                      "reported_cost_usd":0}
                     for role,model in zip(board.ROLES[:3],board.MODEL_FOR_ROLE[:3])]
    }


class NvidiaFinalCritic(unittest.TestCase):
    def source(self,tmp,data=None):
        path=Path(tmp)/"REPORT.json"
        path.write_text(json.dumps(data or prior(),ensure_ascii=False),encoding="utf-8")
        return path,hashlib.sha256(path.read_bytes()).hexdigest()

    def test_one_real_critic_not_three_replays(self):
        with tempfile.TemporaryDirectory() as tmp:
            p,sha=self.source(tmp)
            asked=[]
            def ask(model,prompt,key):
                asked.append((model,prompt))
                return {"model":model,
                        "text":"Rilievi: la prima scena dice 1900; le radiografie non ci sono. "*3,
                        "reported_cost_usd":0}
            with patch.object(final,"PREVIOUS_REPORT_SHA256",sha):
                r=final.complete(p,"fake",catalogue=CAT,ask=ask)
            self.assertEqual(r["status"],"four_real_roles_two_free_models_unapproved")
            self.assertEqual(len(r["responses"]),4)
            self.assertEqual(r["model_calls"],6)
            self.assertEqual(r["new_actual_model_attempts"],1)
            self.assertEqual(len(asked),1)
            self.assertEqual(asked[0][0],board.MODELS[0])
            self.assertIn("1900 vs 1901",asked[0][1])
            self.assertTrue(r["critic_uses_same_model_as_screenwriter_and_director"])
            self.assertFalse(r["publication_authorized"])

    def test_sha_mismatch_blocks_without_contacting_provider(self):
        with tempfile.TemporaryDirectory() as tmp:
            p,_=self.source(tmp)
            with patch.object(board,"_get_json",side_effect=AssertionError("network")):
                with self.assertRaises(board.FreeOnlyError):
                    final.complete(p,"fake")

    def test_price_must_be_zero_before_one_post(self):
        with tempfile.TemporaryDirectory() as tmp:
            p,sha=self.source(tmp)
            cat=json.loads(json.dumps(CAT))
            cat["data"][0]["pricing"]["prompt"]="0.01"
            with patch.object(final,"PREVIOUS_REPORT_SHA256",sha):
                r=final.complete(p,"fake",catalogue=cat,ask=lambda *x:self.fail())
            self.assertEqual(r["status"],"blocked_zero_price_unverified")
            self.assertEqual(r["new_actual_model_attempts"],0)

    def test_no_double_call_if_critic_unavailable(self):
        with tempfile.TemporaryDirectory() as tmp:
            p,sha=self.source(tmp)
            calls=[]
            def fail(model,prompt,key):
                calls.append(1)
                raise board.FreeOnlyError("free provider not responding")
            with patch.object(final,"PREVIOUS_REPORT_SHA256",sha):
                r=final.complete(p,"fake",catalogue=CAT,ask=fail)
            self.assertEqual(len(calls),1)
            self.assertEqual(r["status"],"final_critic_failed_no_retry")
            self.assertEqual(len(r["responses"]),3)

    def test_paid_prior_text_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad=prior();bad["responses"][0]["reported_cost_usd"]=0.0002
            p,sha=self.source(tmp,bad)
            with patch.object(final,"PREVIOUS_REPORT_SHA256",sha):
                with self.assertRaisesRegex(board.FreeOnlyError,"Prior model"):
                    final.complete(p,"fake",catalogue=CAT,ask=lambda *x:self.fail())


if __name__=="__main__":
    unittest.main()
