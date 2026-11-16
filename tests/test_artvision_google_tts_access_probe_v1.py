import unittest
import urllib.error
from scripts.artvision_google_tts_access_probe_v1 import check_model,scan,ENDPOINTS

class Response:
    status=200
    def __enter__(self): return self
    def __exit__(self,*args):return False

class GoogleTtsProbeTests(unittest.TestCase):
    def test_no_key_never_calls_web(self):
        def forbid(*args,**kwargs):raise AssertionError("No call allowed")
        d=scan("",opener=forbid)
        self.assertEqual(len(d["results"]),len(ENDPOINTS))
        self.assertTrue(all(r["status"]=="NO_KEY" for r in d["results"]))
    def test_get_metadata_only_with_secret_header(self):
        def fake(request,timeout):
            self.assertEqual(request.get_method(),"GET")
            self.assertEqual(request.get_header("X-goog-api-key"),"SECRET_IN_TEST_ONLY")
            self.assertNotIn("SECRET_IN_TEST_ONLY",request.full_url)
            return Response()
        x=check_model("v1beta","gemini-3.8-flash-tts","SECRET_IN_TEST_ONLY",fake)
        self.assertEqual(x["status"],"VISIBLE")
        self.assertNotIn("SECRET_IN_TEST_ONLY",str(x))
    def test_api_404_is_reported_not_retried_or_renamed(self):
        def no_model(req,timeout):raise urllib.error.HTTPError(req.full_url,404,"Not found",{},None)
        x=check_model("v1","gemini-3.8-flash-tts","a",no_model)
        self.assertEqual(x["status"],"HTTP_404")
    def test_both_api_versions_and_no_hidden_generation(self):
        names=set(ENDPOINTS)
        self.assertIn(("v1","gemini-3.8-flash-tts"),names)
        self.assertIn(("v1beta","gemini-3.8-flash-tts"),names)
        self.assertIn(("v1beta","gemini-2.5-flash-preview-tts"),names)
if __name__=="__main__":unittest.main()
