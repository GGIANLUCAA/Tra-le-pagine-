"""Fail-open queue selection for independent ArtVision jobs; no rendering or billing."""
from __future__ import annotations
from typing import Iterable, Mapping

BLOCKED = {"BLOCKED", "BLOCKED_VOICE_GACRUX", "PENDING_APPROVED_GACRUX_VOICE", "BLOCKED_ASSETS", "BLOCKED_RIGHTS", "BLOCKED_QA"}
DONE = {"DONE", "COMPLETED", "APPROVED", "GOLD"}
READY = {"READY", "QUEUED", "PENDING"}

def select_next(jobs: Iterable[Mapping], attempted: set[str] | None = None):
    """Return next eligible independent job, or None. Never alter source jobs.

    Jobs require id, status and optional dependencies. A blocked job does not
    block unrelated jobs. A dependency must be explicitly DONE in this snapshot.
    """
    jobs = list(jobs)
    attempted = attempted or set()
    by_id = {str(j["id"]): j for j in jobs}
    if len(by_id) != len(jobs):
        raise ValueError("Duplicate job IDs")
    for job in jobs:
        jid = str(job["id"])
        if jid in attempted or job.get("status") not in READY:
            continue
        deps = job.get("dependencies", [])
        if all(str(dep) in by_id and by_id[str(dep)].get("status") in DONE for dep in deps):
            return job
    return None

def record_block(job: Mapping, reason: str):
    """Produce a new checkpoint record without touching the original job."""
    if not reason:
        raise ValueError("A block reason is required")
    return {**job, "status": "BLOCKED", "block_reason": reason}
