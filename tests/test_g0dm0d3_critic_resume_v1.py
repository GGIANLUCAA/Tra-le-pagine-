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
import g0dm0d3_critic_resume_v1 as resume


def prior():
    return {
        "schema": "g0dm0d3-free-four-role-pilot-v1",
        "format": "giuliano",
        "subject": "Anticitera: correggi 20 scene del documentario",
        "models": list(board.MODELS),
        "status": "incomplete_no_retry",
        "failure_reason": "No displayable text: finish_reason=length",
        "model_calls": 4,
        "video_rendered": False, "publication_authorized": False,
        "responses": [
            {"role": role, "model": model,
             "text": "Valutazione concreta della regia e del documento storico. "*5,
             "reported_cost_usd": 0}
            for role,model in zip(board.ROLES[:3],board.MODEL_FOR_ROLE[:3])]
    }


CAT={"data":[{"id":id_,"pricing":{"prompt":"0","completion":"0","request":"0"}}
             for id_ in board.MODELS]}


class CriticOnlyResumeTests(unittest.TestCase):
    def make_source(self,root,obj=None):
        path=root/"prior_report.json"
        path.write_text(json.dumps(obj or prior(),ensure_ascii=False))
        sha=hashlib.sha256(path.read_bytes()).hexdigest()
        return path,sha

    def test_exact_sha_locked_original_and_one_real_call_only(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            path,sha=self.make_source(root)
            asked=[]
            def fake(model,prompt,key):
                asked.append((model,prompt))
                return {"model":model,"text":"Critica: ripetizioni dei frammenti e tempi sbagliati. "*5,
                        "reported_cost_usd":0}
            with patch.object(resume,"SOURCE_SHA256",sha):
                result=resume.resume(path,"test-only",catalogue=CAT,ask=fake)
            self.assertEqual(len(asked),1)
            self.assertEqual(asked[0][0],board.MODELS[1])
            self.assertIn("la prima scena dice 1900",asked[0][1])
            self.assertIn("50,26–63,32",asked[0][1])
            self.assertEqual(result["status"],"four_roles_returned_unapproved")
            self.assertEqual([x["role"] for x in result["responses"]],
                             ["sceneggiatore","storico","regista","critico"])
            self.assertEqual(result["model_calls"],5)
            self.assertEqual(result["resumed_attempts"],1)
            self.assertFalse(result["video_rendered"])
            self.assertFalse(result["publication_authorized"])

    def test_changed_original_hash_blocks_network_call(self):
        with tempfile.TemporaryDirectory() as t:
            path,_=self.make_source(Path(t))
            with patch.object(board,"_get_json",side_effect=AssertionError("network not allowed")):
                with self.assertRaisesRegex(board.FreeOnlyError,"SHA"):
                    resume.resume(path,"test-only")

    def test_unapproved_paid_previous_output_is_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            obj=prior()
            obj["responses"][1]["reported_cost_usd"]=0.01
            path,sha=self.make_source(Path(t),obj)
            with patch.object(resume,"SOURCE_SHA256",sha):
                with self.assertRaisesRegex(board.FreeOnlyError,"zero-price"):
                    resume.resume(path,"test-only",catalogue=CAT,ask=lambda *x: self.fail())

    def test_critic_error_stops_after_one(self):
        with tempfile.TemporaryDirectory() as t:
            path,sha=self.make_source(Path(t))
            called=[]
            def broken(model,prompt,key):
                called.append(1)
                raise board.FreeOnlyError("free model overloaded")
            with patch.object(resume,"SOURCE_SHA256",sha):
                result=resume.resume(path,"test-only",catalogue=CAT,ask=broken)
            self.assertEqual(result["status"],"critic_only_incomplete_no_retry")
            self.assertEqual(len(result["responses"]),3)
            self.assertEqual(len(called),1)

    def test_zero_price_gate_before_any_post(self):
        with tempfile.TemporaryDirectory() as t:
            path,sha=self.make_source(Path(t))
            bad=json.loads(json.dumps(CAT))
            bad["data"][1]["pricing"]["completion"]="0.0001"
            with patch.object(resume,"SOURCE_SHA256",sha):
                result=resume.resume(path,"test-only",catalogue=bad,ask=lambda *x:self.fail())
            self.assertEqual(result["status"],"blocked_live_zero_price_unverified")
            self.assertEqual(result["resumed_attempts"],0)

    def test_2500_tokens_only_in_explicit_critic_call(self):
        requests=[]
        def transport(req):
            obj=json.loads(req.data);requests.append(obj)
            return {"model":board.MODELS[1],
                    "choices":[{"message":{"content":"Una critica storica approfondita. "*10}}],
                    "usage":{"cost":0}}
        board._request_free(board.MODELS[1],"Tesi sui bronzi greci "*5,
                            "dummy",transport=transport,max_output_tokens=2500)
        self.assertEqual(requests[0]["max_tokens"],2500)
        self.assertEqual(requests[0]["provider"]["max_price"],
                         {"prompt":0,"completion":0})
        self.assertFalse(requests[0]["provider"]["allow_fallbacks"])
        with self.assertRaises(board.FreeOnlyError):
            board._request_free(board.MODELS[1],"Tesi sui bronzi greci "*5,
                                "dummy",transport=lambda *args:self.fail(),
                                max_output_tokens=50000)


if __name__=="__main__":
    unittest.main()
