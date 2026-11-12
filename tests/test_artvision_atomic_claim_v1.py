import io
import json
import threading
import unittest
import urllib.error
from concurrent.futures import ThreadPoolExecutor

from src.artvision_atomic_claim_v1 import (
    CLAIM_PREFIX, REPO, ClaimConflict, ClaimUnknown,
    claim_once, demo_manifest, plan_claim,
)
from src.artvision_atomic_github_store_v1 import GithubClaimStore


class AtomicMemoryStore:
    """Imitates GitHub POST create-ref conflict with an atomic critical section."""

    def __init__(self):
        self.refs = {}
        self.mu = threading.Lock()
        self.attempts = 0

    def create_if_absent(self, ref, sha):
        with self.mu:
            self.attempts += 1
            if ref in self.refs:
                raise ClaimConflict("already exists")
            self.refs[ref] = sha


class UncertainStore:
    def __init__(self):
        self.attempts = 0

    def create_if_absent(self, ref, sha):
        self.attempts += 1
        raise ClaimUnknown("connection dropped after possibly committing")


class FakeHttpResponse(io.BytesIO):
    def __init__(self, status, payload=None):
        super().__init__(json.dumps(payload or {}).encode())
        self.status = status


def http_error(code):
    return urllib.error.HTTPError(
        "https://api.github.com/...", code, "mock", {}, io.BytesIO(b"{}"))


class ClaimTests(unittest.TestCase):
    BASE_SHA = "d" * 40

    def test_stable_claim_id(self):
        m = demo_manifest()
        a = plan_claim(m)
        b = plan_claim(dict(reversed(list(m.items()))))
        self.assertEqual(a.ref, b.ref)
        self.assertTrue(a.ref.startswith(CLAIM_PREFIX))
        self.assertEqual(len(a.identity_digest), 64)

    def test_distinct_variants_have_distinct_claims(self):
        vals = []
        for variant in ("critico_standard", "critico_museum", "cinema_standard", "cinema_museum"):
            m = demo_manifest()
            m["variant"] = variant
            vals.append(plan_claim(m).ref)
        self.assertEqual(len(vals), len(set(vals)))

    def test_revision_or_source_change_new_claim(self):
        original = demo_manifest()
        changed_revision = {**original, "revision": "v2"}
        changed_source = {**original, "source_sha256": "b" * 64}
        self.assertEqual(3, len({
            plan_claim(original).ref, plan_claim(changed_revision).ref,
            plan_claim(changed_source).ref,
        }))

    def test_40_parallel_contenders_one_claim(self):
        store = AtomicMemoryStore()
        with ThreadPoolExecutor(max_workers=16) as executor:
            results = list(executor.map(
                lambda _: claim_once(store, demo_manifest(), self.BASE_SHA), range(40)))
        self.assertEqual(sum(r["status"] == "claim_reserved_only" for r in results), 1)
        self.assertEqual(sum(r["status"] == "already_claimed_quarantine" for r in results), 39)
        self.assertEqual(len(store.refs), 1)
        self.assertTrue(all(not r["render_started"] for r in results))

    def test_second_attempt_never_success(self):
        s = AtomicMemoryStore()
        self.assertEqual(claim_once(s, demo_manifest(), self.BASE_SHA)["status"],
                         "claim_reserved_only")
        self.assertEqual(claim_once(s, demo_manifest(), self.BASE_SHA)["status"],
                         "already_claimed_quarantine")

    def test_uncertain_write_is_not_retried(self):
        s = UncertainStore()
        r = claim_once(s, demo_manifest(), self.BASE_SHA)
        self.assertEqual(r["status"], "unknown_quarantine")
        self.assertEqual(s.attempts, 1)

    def test_bad_base_commit_sha_makes_no_write(self):
        s = AtomicMemoryStore()
        r = claim_once(s, demo_manifest(), "0" * 64)
        self.assertEqual(r["status"], "blocked_preflight")
        self.assertEqual(s.attempts, 0)

    def test_missing_evidence_fails_closed(self):
        for key in ("source_verified", "rights_verified", "storyboard_ready", "qa_plan_ready",
                    "owner_selection_verified", "existing_slot_checked", "pilot_lock_checked"):
            with self.subTest(key=key):
                m = demo_manifest()
                m[key] = None
                s = AtomicMemoryStore()
                self.assertEqual(claim_once(s, m, self.BASE_SHA)["status"], "blocked_preflight")
                self.assertEqual(s.attempts, 0)

    def test_false_publication_gate_rejects_even_zero_budget(self):
        m = demo_manifest()
        m["publication_authorized"] = True
        self.assertEqual(claim_once(AtomicMemoryStore(), m, self.BASE_SHA)["status"],
                         "blocked_preflight")

    def test_paid_cost_or_paid_flag_rejected(self):
        for patch in ({"budget_eur": 1},
                      {"budget_eur": 0.0},
                      {"paid_api_calls_authorized": True}):
            with self.subTest(patch=patch):
                m = {**demo_manifest(), **patch}
                self.assertEqual(claim_once(AtomicMemoryStore(), m, self.BASE_SHA)["status"],
                                 "blocked_preflight")

    def test_unknown_variant_rejected(self):
        m = {**demo_manifest(), "variant": "cinema_museum_extra"}
        self.assertEqual(claim_once(AtomicMemoryStore(), m, self.BASE_SHA)["status"],
                         "blocked_preflight")

    def test_unhashable_variant_rejected_safely(self):
        m = {**demo_manifest(), "variant": ["cinema_standard"]}
        self.assertEqual(claim_once(AtomicMemoryStore(), m, self.BASE_SHA)["status"],
                         "blocked_preflight")

    def test_wrong_repo_rejected(self):
        m = {**demo_manifest(), "repository": "someone/else"}
        self.assertEqual(claim_once(AtomicMemoryStore(), m, self.BASE_SHA)["status"],
                         "blocked_preflight")

    def test_dali_excluded(self):
        m = {**demo_manifest(), "work_id": "dali_temptation_st_anthony"}
        self.assertEqual(claim_once(AtomicMemoryStore(), m, self.BASE_SHA)["status"],
                         "blocked_preflight")

    def test_failed_claim_cannot_be_mistaken_for_render(self):
        s = AtomicMemoryStore()
        r = claim_once(s, demo_manifest(), self.BASE_SHA)
        self.assertTrue(r["claim_ref"].startswith(CLAIM_PREFIX))
        self.assertFalse(r["render_started"])
        self.assertFalse(r["publication_authorized"])


class GithubAdapterTests(unittest.TestCase):
    BASE_SHA = "d" * 40

    def test_post_once_success(self):
        requests = []
        def transport(request, timeout):
            requests.append(request)
            return FakeHttpResponse(201)
        store = GithubClaimStore("fake-test-token", transport=transport)
        store.create_if_absent(plan_claim(demo_manifest()).ref, self.BASE_SHA)
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].get_method(), "POST")
        self.assertIn('"sha": "' + self.BASE_SHA + '"', requests[0].data.decode())
        self.assertIn(REPO, requests[0].full_url)

    def test_422_get_existing_conflict_no_retry_post(self):
        requests = []
        ref = plan_claim(demo_manifest()).ref
        def transport(request, timeout):
            requests.append(request.get_method())
            if request.get_method() == "POST":
                raise http_error(422)
            return FakeHttpResponse(200, {"ref": ref})
        s = GithubClaimStore("fake-test-token", transport=transport)
        with self.assertRaises(ClaimConflict):
            s.create_if_absent(ref, self.BASE_SHA)
        self.assertEqual(requests, ["POST", "GET"])

    def test_422_without_existing_ref_unknown_no_retry(self):
        requests = []
        ref = plan_claim(demo_manifest()).ref
        def transport(request, timeout):
            requests.append(request.get_method())
            if request.get_method() == "POST":
                raise http_error(422)
            raise http_error(404)
        with self.assertRaises(ClaimUnknown):
            GithubClaimStore("test", transport=transport).create_if_absent(ref, self.BASE_SHA)
        self.assertEqual(requests, ["POST", "GET"])

    def test_http_500_does_not_retry(self):
        calls = []
        def transport(request, timeout):
            calls.append(request.get_method())
            raise http_error(500)
        with self.assertRaises(ClaimUnknown):
            GithubClaimStore("test", transport=transport).create_if_absent(
                plan_claim(demo_manifest()).ref, self.BASE_SHA)
        self.assertEqual(calls, ["POST"])

    def test_connection_drop_does_not_retry(self):
        calls = []
        def transport(request, timeout):
            calls.append(request.get_method())
            raise OSError("connection reset after write")
        with self.assertRaises(ClaimUnknown):
            GithubClaimStore("test", transport=transport).create_if_absent(
                plan_claim(demo_manifest()).ref, self.BASE_SHA)
        self.assertEqual(calls, ["POST"])

    def test_invalid_ref_never_hits_network(self):
        calls = []
        def transport(request, timeout):
            calls.append(request.get_method())
            return FakeHttpResponse(201)
        with self.assertRaises(ClaimUnknown):
            GithubClaimStore("test", transport=transport).create_if_absent(
                "refs/heads/evil-other-ref", self.BASE_SHA)
        self.assertEqual(calls, [])

    def test_invalid_suffix_never_hits_network(self):
        calls = []
        def transport(request, timeout):
            calls.append(request.get_method())
            return FakeHttpResponse(201)
        with self.assertRaises(ClaimUnknown):
            GithubClaimStore("test", transport=transport).create_if_absent(
                CLAIM_PREFIX + ("z" * 64), self.BASE_SHA)
        self.assertEqual(calls, [])

    def test_invalid_commit_never_hits_network(self):
        calls = []
        def transport(request, timeout):
            calls.append(request.get_method())
            return FakeHttpResponse(201)
        with self.assertRaises(ClaimUnknown):
            GithubClaimStore("test", transport=transport).create_if_absent(
                plan_claim(demo_manifest()).ref, "0" * 64)
        self.assertEqual(calls, [])

    def test_empty_token_rejected(self):
        with self.assertRaises(ValueError):
            GithubClaimStore("")


if __name__ == "__main__":
    unittest.main()
