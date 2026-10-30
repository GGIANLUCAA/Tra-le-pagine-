# WOW LAB · Release/queue hardening + verified pop-out gate · 2026-10-30

Scope: **only wow_lab/**, isolated experiment branch; no main, no core workflows, no paid APIs, no social publishing.

## Fixed failure modes

1. The last-six-subject list still deduplicates V1/V2 re-edits, but each re-edit now reserves its own historical UTC slot. Previously the duplicate subject was discarded with its slot, allowing a second production in a used slot.
2. Every release returned by the first GitHub API page is audited (no early cutoff at 25 unique subjects). If the page reaches 100 entries, the job fails closed rather than assuming older release slots are absent.
3. GitHub Actions queue reads now use GITHUB_TOKEN, scoped strictly to the repository's Actions API endpoint. Missing token, truncated queue or failed API request must stop the job. Pending/waiting jobs are checked in addition to queued/in_progress.
4. Naive and timezone-aware release timestamps are normalized to UTC before sorting.
5. The extracted silhouette must actually cross the projected frame boundary before soundtrack or MP4 rendering. POPOUT_GEOMETRY_PREFLIGHT.json records opening/reveal outside-frame ratios and explicit rejection reasons. Mere camera zoom cannot pass. This is 2.5D, not volumetric 3D.
6. The reveal starts at normalized progress 0.22 rather than 0.13, corresponding to approximately 2–3 seconds for the existing 9–12s candidates.

## Validation status

- New regression files: tests/test_release_slot_regression_v2.py and tests/test_popout_geometry_gate.py.
- Synthetic numerical projection was checked locally; the partial-escape fixture gave ~0.43 outside-frame ratio and a lower subject gave 0.00.
- **Full GitHub Actions run and complete unit suite on this branch have not been executed.**
- **Live GitHub releases/queue cannot be exhaustively enumerated from the available connector read actions in this execution.** Do not claim the current slot is free; do not render or publish a new candidate until the live preflight is available.
- **No real-source mask or new MP4 has been validated** in this execution. Artistic approval remains false.
- Known earlier workflow run 41060273020: build_candidate failed, publish_namespaced_prerelease skipped. It is not proof of the latest workflow state.

## Next required gate

Run the isolated test suite, obtain the actual current release/queue state, select a genuinely new rights-verified subject, inspect real mask/stills, run FFprobe and full FFmpeg decode, and only then decide whether a release is justified. Do not enable automatic release publication of unapproved work.
