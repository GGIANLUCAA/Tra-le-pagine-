#!/usr/bin/env python3
"""ArtVision V1 persistent per-slot idempotency claims (ISOLATED PROTOTYPE).

This module NEVER launches rendering or publishes. It does not run as a workflow
step in production. A future authorized worker may call claim_once *only while*
holding the shared GitHub Actions heavy-render concurrency slot. Claim refs
are intentionally never auto-deleted: an ambiguous outcome means quarantine,
NOT automatic retry, and old output remains unchanged.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Protocol

REPO = "GGIANLUCAA/Tra-le-pagine-"
SCHEMA = "artvision-render-claim-v1"
CLAIM_PREFIX = "refs/heads/artvision-idempotency/v1/"
VALID_VARIANTS = frozenset({
    "critico_standard", "critico_museum", "cinema_standard", "cinema_museum",
})
IDENTITY_RE = re.compile(r"[a-z0-9][a-z0-9_-]{2,95}\Z")
REVISION_RE = re.compile(r"v[1-9][0-9]{0,4}\Z")
SHA_RE = re.compile(r"[a-f0-9]{64}\Z")
COMMIT_SHA_RE = re.compile(r"[a-f0-9]{40}\Z")
GUARD_FIELDS = (
    "source_verified", "rights_verified", "storyboard_ready", "qa_plan_ready",
    "owner_selection_verified", "existing_slot_checked", "pilot_lock_checked",
)


class ClaimError(ValueError):
    """Validation failure. No claim may be attempted."""


class ClaimConflict(Exception):
    """The deterministic ref cannot be created because it already exists."""


class ClaimUnknown(Exception):
    """Any ambiguous result (including transport errors). Do not retry."""


@dataclass(frozen=True)
class ClaimPlan:
    ref: str
    identity_digest: str


class ClaimStore(Protocol):
    def create_if_absent(self, ref: str, base_commit_sha: str) -> None: ...


def plan_claim(manifest: dict) -> ClaimPlan:
    """Validate a preflight record; flags are NOT themselves verification evidence."""
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA:
        raise ClaimError("unknown claim schema")
    if manifest.get("repository") != REPO:
        raise ClaimError("wrong repository")
    work_id = manifest.get("work_id")
    revision = manifest.get("revision")
    variant = manifest.get("variant")
    source_sha256 = manifest.get("source_sha256")
    if not isinstance(work_id, str) or not IDENTITY_RE.fullmatch(work_id):
        raise ClaimError("invalid work ID")
    if work_id.startswith("dali_temptation"):
        raise ClaimError("work explicitly excluded by owner")
    if not isinstance(revision, str) or not REVISION_RE.fullmatch(revision):
        raise ClaimError("invalid revision ID")
    if not isinstance(variant, str) or variant not in VALID_VARIANTS:
        raise ClaimError("unknown 4x1 variant")
    if not isinstance(source_sha256, str) or not SHA_RE.fullmatch(source_sha256):
        raise ClaimError("invalid source SHA256")
    if any(manifest.get(key) is not True for key in GUARD_FIELDS):
        raise ClaimError("owner/source/rights/QA/pilot preflight not completely verified")
    if manifest.get("paid_api_calls_authorized") is not False or (
        manifest.get("publication_authorized") is not False
    ):
        raise ClaimError("paid API or publishing prohibited by claim protocol")
    # Only zero-API-cost, explicitly review-only render plans are ever eligible
    # for a first claim. Actual paid providers require a distinct authorization.
    if manifest.get("budget_eur") != 0 or type(manifest.get("budget_eur")) is not int:
        raise ClaimError("zero-budget guard missing")
    identity = {
        "repository": REPO, "work_id": work_id, "variant": variant,
        "revision": revision, "source_sha256": source_sha256,
    }
    canonical = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
    digest = hashlib.sha256(canonical).hexdigest()
    return ClaimPlan(CLAIM_PREFIX + digest, digest)


def claim_once(store: ClaimStore, manifest: dict, base_commit_sha: str) -> dict:
    """One call only. A conflict or any uncertain result forbids another POST.

    GitHub Actions global heavy-render `concurrency` is a separate requirement.
    Neither a successful claim nor its backing ref proves a rendered MP4.
    """
    base = dict(schema=SCHEMA, render_started=False,
                publication_authorized=False, paid_api_calls=0)
    try:
        plan = plan_claim(manifest)
    except ClaimError as exc:
        return dict(base, status="blocked_preflight", reason=str(exc))
    if not isinstance(base_commit_sha, str) or not COMMIT_SHA_RE.fullmatch(base_commit_sha):
        return dict(base, status="blocked_preflight", reason="unverified base commit SHA")
    try:
        store.create_if_absent(plan.ref, base_commit_sha)
    except ClaimConflict:
        return dict(base, status="already_claimed_quarantine", claim_ref=plan.ref,
                    reason="never auto-repeat a candidate already attempted")
    except Exception:
        # Lost responses may happen *after* GitHub accepted a write.
        return dict(base, status="unknown_quarantine", claim_ref=plan.ref,
                    reason="ambiguous claim attempt, never auto-retry")
    return dict(base, status="claim_reserved_only", claim_ref=plan.ref,
                identity_digest=plan.identity_digest,
                reason="claim reserved; separate heavy render guard and QA still required")


def demo_manifest() -> dict:
    """For unit tests and dry-run examples ONLY. Not production evidence."""
    return {
        "schema": SCHEMA, "repository": REPO,
        "work_id": "test_example_never_render", "variant": "cinema_standard",
        "revision": "v1", "source_sha256": "a" * 64,
        **{key: True for key in GUARD_FIELDS},
        "paid_api_calls_authorized": False,
        "publication_authorized": False,
        "budget_eur": 0,
    }


if __name__ == "__main__":
    print(json.dumps({
        "message": "This module does not make GitHub API calls. Use CI simulations.",
        "sample_claim_ref": plan_claim(demo_manifest()).ref,
        "production_enabled": False,
    }, indent=2))
