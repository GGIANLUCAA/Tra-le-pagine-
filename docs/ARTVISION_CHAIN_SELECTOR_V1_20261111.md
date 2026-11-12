# ArtVision event-driven chain — selector V1 (11 Nov 2026)
This is a **dry-run-only**, fail-closed first executable component of PR #255's plan. It selects one eligible *new* candidate from an explicit manifest; it does **not** trigger GitHub Actions, render video, edit masters, buy credits or publish.
Run: `python -m unittest discover -s tests -p 'test_artvision_chain_selector_v1.py'`
Then: `python src/artvision_chain_selector_v1.py /path/to/manifest.json`.
Manifest example:
```json
{"active_heavy_render": false, "completed_ids": [], "running_ids": [],
 "candidates": [{"id":"unique-artwork-variant", "status":"ready",
 "source_verified":true, "rights_verified":true, "storyboard_ready":true,
 "qa_plan_ready":true, "workflow_path":".github/workflows/approved.yml"}]}
```
IMPORTANT: active_heavy_render=false must be independently verified against live runs; never assume it. The manifest is not proof of rights or artifact status. Before wiring dispatch, verify approved workflow allowlist, authenticated live run enumeration, atomic concurrency/idempotency, artifact SHA/FFmpeg/ZIP checks, QA artistic review, no auto-publish, no extra spending. Maintain four variants separately. For future titles: large original artwork title, prominent artist, documented year, Android readability; no changes to existing masters.

## V1 hardening (12 Nov 2026, PR #258)
- A candidate with `status: blocked` or `status: quarantined`, or whose ID appears in `quarantined_ids`, is skipped **without blocking unrelated works**. Recovery of the original candidate needs new independent source/QA evidence.
- A malformed candidate entry is ignored, but malformed candidate lists or completed/running/quarantined ID snapshots return `preparing` (fail closed). Unknown/bogus active-render values remain busy.
- Workflow file paths are restricted to ordinary YAML filenames directly inside `.github/workflows/` (no traversal, nested paths, or arbitrary user-supplied scripts).
- `quarantined_ids` defaults to an empty list for compatibility; production must not assume the manifest is authoritative for live GitHub Actions.
- Expanded unit coverage from 9 to 17 test cases. Run `python -m unittest discover -s tests -p 'test_artvision_chain_selector_v1.py'`.
- This is still read-only selection, **not** a live lock, dispatch, owner workflow integration, automated restart, video completion or publishing. A safe live chain additionally needs authenticated GitHub run enumeration, atomic idempotency, temporal lock, workflow allowlist and independently verified QA.

## V1.1 live read-only GitHub integration (12 Nov 2026, PR #258)
- Added `src/artvision_chain_live_snapshot_v1.py`: uses only the Actions **read** permission with the GitHub Actions token of this repo. Queries `queued`, `in_progress`, `waiting`, `pending`, `requested`, and `action_required` across all branches, with pagination, deduplication and strict fail-closed response validation.
- Existing owner Cinema workflows (e.g. Arbo, Sadko, Pompeii) already declare `concurrency.group: artvision-owner-single-heavy-render` and `cancel-in-progress: false`. The scanner conservatively counts owner render workflows as possible heavy work, while treating the known source-research V4 workflow as non-render research.
- The workflow `.github/workflows/artvision-chain-selector-ci.yml` runs both offline test suites, then executes a real, authenticated, **read-only** GitHub run inventory and saves a short-lived JSON report artifact. It cannot download media, dispatch, spend credits, publish, or change masters.
- If GitHub denies Actions read, a status page is missing/inconsistent, a run is malformed, the repo identity is unexpected, or the token is unavailable: output is `inventory_status: unknown_fail_closed` with `active_heavy_render: null`; CI fails rather than treating the repository as idle.
- An apparently idle live snapshot is **not** an atomic lock. Status transitions can race with the scan, and `active_heavy_render: false` is not authorization to launch. Dispatch remains prohibited by design. Complete owner-state and idempotency checks, allowlisted on-demand workflows, commit/ref lease or stronger atomic control, positive QA, and single-item canary validation are still missing. Existing push-only render workflows must not be falsely treated as workflow_dispatch-compatible.
- A candidate manifest with unverified source/rights/QA is still NOT eligible for production. Queue checkpoints are historical snapshots, not runtime confirmation. No automatic merge into `main`.

## V1.2 read-only handoff, not a producer
`src/artvision_chain_live_preview_v1.py` joins only a complete live GitHub inventory with an explicit versioned `artvision-chain-candidates-v1` review manifest and a named `reviewed_workflow_paths` allowlist. The live inventory (not the queue) overrides any `active_heavy_render` flag. Invalid repo, missing statuses, malformed allowlist, unknown schema, and candidate workflows outside the allowlist all fail closed. Even a valid fully prepared candidate receives only `candidate_manual_review_only`; `dispatch_authorized` and `render_started` are always false. The GitHub CI tests the real status handoff against a clearly synthetic, non-production-ready item and stores `NEXT_ACTION_PREVIEW.json` beside the live inventory report. This does not establish a production-grade idempotency ledger, certified remaining-slot count, atomic lock, executable on-demand producer workflow, media QA, or continuous delivery.
