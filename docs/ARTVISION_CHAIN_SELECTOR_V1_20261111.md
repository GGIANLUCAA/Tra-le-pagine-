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
