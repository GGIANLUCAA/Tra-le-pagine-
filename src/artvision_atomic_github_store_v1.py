#!/usr/bin/env python3
"""Unwired GitHub ref adapter for ArtVision claim protocol.

NO code in this module runs on import. Never used by current CI/workflows.
Future integration must hold shared heavy-render concurrency, verify V58 and
all license/QA evidence, and explicitly authorize *one* write.
"""
import json
import urllib.error
import urllib.request
from src.artvision_atomic_claim_v1 import (
    REPO, CLAIM_PREFIX, COMMIT_SHA_RE, SHA_RE, ClaimConflict, ClaimUnknown,
)

GITHUB_API = "https://api.github.com/repos/" + REPO
DEFAULT_TIMEOUT_S = 12


class GithubClaimStore:
    def __init__(self, token: str, *, transport=None):
        if not isinstance(token, str) or not token:
            raise ValueError("a GitHub Actions contents:write token is required")
        self._token = token
        # Injectable to test without real network/write.
        self._transport = transport or urllib.request.urlopen

    def _request(self, method, path, body=None):
        data = None if body is None else json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            GITHUB_API + path,
            data=data,
            method=method,
            headers={
                "Authorization": "Bearer " + self._token,
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "artvision-atomic-claim-v1",
            },
        )
        return self._transport(req, timeout=DEFAULT_TIMEOUT_S)

    def create_if_absent(self, ref: str, base_commit_sha: str) -> None:
        if not isinstance(ref, str) or not ref.startswith(CLAIM_PREFIX) or (
            SHA_RE.fullmatch(ref[len(CLAIM_PREFIX):]) is None
        ):
            raise ClaimUnknown("invalid claim ref")
        if not isinstance(base_commit_sha, str) or not COMMIT_SHA_RE.fullmatch(base_commit_sha):
            raise ClaimUnknown("invalid base commit SHA")

        # Exactly one POST. NEVER retry it, even on timeout or HTTP 5xx:
        # GitHub may have created the ref before the connection failed.
        try:
            with self._request("POST", "/git/refs", {
                "ref": ref, "sha": base_commit_sha,
            }) as response:
                if response.status != 201:
                    raise ClaimUnknown("unexpected create-ref HTTP status")
                return
        except urllib.error.HTTPError as exc:
            if exc.code != 422:
                raise ClaimUnknown("create-ref rejected or ambiguous") from None
            # 422 may mean duplicate OR validation error. A GET can classify
            # existing without sending another write. GET errors stay unknown.
            suffix = ref[len("refs/"):]
            try:
                with self._request("GET", "/git/ref/" + suffix) as response:
                    if response.status != 200:
                        raise ClaimUnknown("post-conflict GET uncertain")
                    body = json.load(response)
            except Exception:
                raise ClaimUnknown("post-conflict lookup uncertain") from None
            if isinstance(body, dict) and body.get("ref") == ref:
                raise ClaimConflict("immutable claim already exists")
            raise ClaimUnknown("GitHub ref state ambiguous")
        except ClaimUnknown:
            raise
        except Exception:
            raise ClaimUnknown("create-ref response ambiguous") from None
