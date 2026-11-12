# ArtVision owner — event-driven production chain, safe design (11 Nov 2026)

Status: **DESIGN ONLY, NOT ENABLED**. This proposal does not schedule, dispatch or render anything. Existing ChatGPT hourly automation remains the watchdog.

## Verified existing behavior
- One-shot workflows such as `.github/workflows/artvision-owner-forest-fire-cinema-v1.yml` and `artvision-owner-shipwreck-cinema-v1.yml` run on `push` to their own workflow path.
- Both use `concurrency.group: artvision-owner-single-heavy-render` and `cancel-in-progress: false`.
- Both verify media with full FFmpeg decode, independent artifact readback, hashes and ZIP CRC. These gates must remain.
- The current owner selection consists of the primary queue (Dalí excluded) and the separate 30-work shortlist. Existing checkpoints may contain stale status; actual run/artifact SHA wins.

## Proposed minimal implementation, split into reviewable PRs
1. **Read-only selector + tests**: derive candidates from the two queues, verified run/artifact evidence and existing checkpoints; use identity key `queue/work_id/variant/source_sha256/script_sha256`. Unknown source/license, duplicate, pending running job and unclear rights are NOT READY. Never interpret a candidate image as cleared rights.
2. **Preparation-only lane**: while one heavy render runs, source research and shot/storyboard validation may run separately. No new paid API or rendering. Persist a provenance dossier with exact object ID, source URL, license, SHA, resolution, attribution and owner-authorized variant.
3. **One render worker**: choose exactly one READY candidate after rechecking latest main and in-progress runs. Keep global heavy-render concurrency lock. Acquire a persistent lease/idempotency record for candidate key before dispatch. A queued GitHub concurrency job is not proof of exclusivity for different trigger races: check again inside the worker.
4. **Completion event**: only a verified successful terminal render and independent readback should request selection of the next READY work. A failed job records BLOCKED and proceeds to a *different* eligible work after at most two safe attempts. Avoid triggering from documentation commits, research-only workflows, pull requests, or the handoff JSON.
5. **Loop protection**: require unique run ID + candidate key + artifact SHA; reject repeated completion events, previously processed keys, and identical input. Cap consecutive transitions and cumulative runtime per chain, with explicit backoff on 429, source/license errors, Actions limits and empty queue. Preserve the hourly watchdog as recovery, not a competing dispatcher.
6. **Output**: new MP4 only after full audio/video decode, source SHA, ZIP CRC, independent artifact byte readback and media QA. Artistic review, commercial-rights clearance, Gold and publication remain separate; no automatic approval or publication.

## Required validation before enabling
- Unit tests: empty queue, all blocked, duplicate candidate, running candidate, stale checkpoint, Dalí excluded, bad license, mismatched SHA, simultaneous completion events, replayed event, failed readback, 429, retry limit.
- Integration dry run using fixture inputs and no render/dispatch.
- One supervised real candidate, with proof of one and only one heavy render and its QA artifact; then a second distinct candidate.
- Review GitHub Actions permission scope, event triggers and GitHub Actions billing/usage limits before enabling.
- Never modify previously verified masters or deploy website/social changes.

## Immediate safe optimization
Keep one-shot existing workflows unchanged until the above checks pass. Parallelize only *preparation* (research, legal preflight, narration and storyboard) with a single heavy render. Cache free Python dependencies in a separate reviewed change only if its benefit is measured and reproducible.

## Current blockers
No confirmed generic dispatcher or selector currently enabled; no production claims follow from this design document. This PR is intentionally a non-executing proposal so that a mistaken push cannot launch a duplicate expensive render.
