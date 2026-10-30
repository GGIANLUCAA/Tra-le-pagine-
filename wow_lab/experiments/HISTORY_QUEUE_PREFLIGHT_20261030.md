# WOW LAB · Run gate / history repair · 2026-10-30

Scope: isolated branch `experiment/wow-lab-history-guard-20261030`, files exclusively in `wow_lab/`. No production merge, no paid APIs, no social or archive changes.

## Real observed failures
- GitHub Actions main workflow run 41060273020 failed at source selection with `invalid literal for int() with base 10: '0T'`. Main still uses the old engine.
- Independent WOW LAB releases already exist for Zhu Ling (Met 36075) and Sharaku (Met 37358), both within the same 20261030T12 UTC two-hour window; generating another for this slot would duplicate production.
- Existing release history parser did not recognize V4 notes of the form `Met 37358` and assumed API release listing order was chronological; that could fail closed or incorrectly identify the last six distinct subjects.

## Changes, branch only
1. Parse V1-V4 verified Met IDs, reject missing/conflicting provenance.
2. Sort by publication timestamp before deduplicating versions of one artwork.
3. Map release timestamps and explicit manifest slots to UTC two-hour windows.
4. Reject a slot already represented by a WOW LAB release.
5. Check public GitHub Actions in-progress and queued runs, ignoring the caller and unrelated projects. Fail closed if the queue cannot be verified.
6. Add offline unit tests for actual legacy notes, ordering, slots, conflict handling, parallel jobs and truncated queue listings.

## Still blocked
- The scheduler reads `main`; no changes were made to `main` or protected workflows. Branch fixes are not deployed.
- Tests were committed but not executed by GitHub Actions for this branch. No passing test claim.
- The current renderer still moves the entire artwork panel; it does not require a pre-render silhouette mask or create a verified true pop-out subject. Therefore it is not artistically production-ready.
- No new MP4 or release was generated on this run. Existing V4 videos are experimental 2.5D with artistic review pending.
- GitHub releases and runs may change concurrently; preflight reduces but cannot eliminate races between unrelated workflows. The existing workflow only protects its own release tag at publication.

## Next required quality gate
Only after the independent mask-extraction and subject-layer compositing pipeline has been connected and visually audited should a fresh distinct subject/slot be rendered. Keep technical preview distinct from artistic approval.
