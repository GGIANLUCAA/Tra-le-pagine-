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
