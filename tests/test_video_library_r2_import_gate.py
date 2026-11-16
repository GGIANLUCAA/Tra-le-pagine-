"""Regression checks for the public R2 importer; no network, uploads or secrets."""
import ast
import hashlib
import io
import json
import pathlib
import unittest
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/video-library-r2-import.yml"
REVIEW_KEYS = ("opening", "visual", "cover", "music", "rights", "full_watch", "replicability")


def script_source():
    text = WORKFLOW.read_text(encoding="utf-8")
    start_marker = "          python3 - <<'PY'\n"
    end_marker = "\n          PY"
    assert text.count(start_marker) == 1, "Expected one importer inline script"
    start = text.index(start_marker) + len(start_marker)
    end = text.index(end_marker, start)
    lines = text[start:end].splitlines()
    assert all(not line or line.startswith("          ") for line in lines)
    return "\n".join(line[10:] if line else "" for line in lines) + "\n"


def gates():
    source = script_source()
    tree = ast.parse(source)
    names = {"publication_gate", "site_release_gate"}
    fns = [node for node in tree.body
           if isinstance(node, ast.FunctionDef) and node.name in names]
    assert {fn.name for fn in fns} == names
    namespace = {"hashlib": hashlib}

    def contract_manifests(zf):
        manifests = []
        for member in zf.namelist():
            if pathlib.PurePosixPath(member).name == "ARTVISION_CONTRACT_V25.json":
                manifests.append((member, json.loads(zf.read(member))))
        return manifests

    namespace["contract_manifests"] = contract_manifests
    module = ast.fix_missing_locations(ast.Module(body=fns, type_ignores=[]))
    exec(compile(module, str(WORKFLOW), "exec"), namespace)
    return namespace["site_release_gate"]


def bundle(video=b"real-hash-test-not-a-published-video", status="not_published",
           site_ok=False, owner_ok=False, reviews=True, hash_ok=True):
    digest = hashlib.sha256(video).hexdigest() if hash_ok else "0" * 64
    contract = {
        "review_video_sha256": digest,
        "reviews": {key: {"passed": reviews} for key in REVIEW_KEYS},
        "publication": {
            "status": status,
            "site_publication_authorized": site_ok,
            "owner_approved": owner_ok,
        },
    }
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as z:
        z.writestr("VIDEO_MASTER.mp4", video)
        z.writestr("ARTVISION_CONTRACT_V25.json", json.dumps(contract))
    out.seek(0)
    return zipfile.ZipFile(out)


class PublicR2ImportGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gate = staticmethod(gates())

    def test_script_compiles(self):
        compile(script_source(), str(WORKFLOW), "exec")

    def test_recent_artifacts_no_longer_bypass_gate(self):
        source = script_source()
        self.assertNotIn("DIRECT SITE IMPORT (ART REVIEW NOT REQUIRED)", source)
        self.assertIn("allowed,reason=site_release_gate(z,videos)", source)
        self.assertIn("PRIVATE_BLOCKED (no public R2 upload)", source)

    def test_v25_approval_alone_cannot_publish(self):
        with bundle(reviews=True) as z:
            self.assertFalse(self.gate(z, ["VIDEO_MASTER.mp4"])[0])

    def test_explicit_owner_approval_and_exact_hash_pass(self):
        with bundle(status="approved_for_site", site_ok=True, owner_ok=True) as z:
            self.assertTrue(self.gate(z, ["VIDEO_MASTER.mp4"])[0])

    def test_each_authorization_is_required(self):
        for status, site_ok, owner_ok in [
            ("not_published", True, True),
            ("approved_for_site", False, True),
            ("approved_for_site", True, False),
        ]:
            with self.subTest(status=status, site_ok=site_ok, owner_ok=owner_ok):
                with bundle(status=status, site_ok=site_ok, owner_ok=owner_ok) as z:
                    self.assertFalse(self.gate(z, ["VIDEO_MASTER.mp4"])[0])

    def test_wrong_hash_or_incomplete_review_blocks(self):
        for passed, matched in [(False, True), (True, False)]:
            with self.subTest(passed=passed, matched=matched):
                with bundle(status="approved_for_site", site_ok=True,
                            owner_ok=True, reviews=passed, hash_ok=matched) as z:
                    self.assertFalse(self.gate(z, ["VIDEO_MASTER.mp4"])[0])


if __name__ == "__main__":
    unittest.main()
