# Video Library Studio · private owner archive for existing GitHub Artifacts

Status: **PR-only, NOT LIVE**. No new MP4 imported, no Cloudflare deployment, no site/social publication.

## Proven gap (16 Nov 2026)
- Public R2 bucket `video-library-studio`: 6,232 objects, 727 MP4; latest MP4 upload 13 Nov 2026.
- Separate private R2 bucket `studio-ai-v3-private-archive`: exists, **0 objects**.
- Current `video-library-import` Worker binding: `VIDEOS → video-library-studio` only.
- ChatGPT Library has newer, private MP4s. Their egress is **BLOCKED_FILE_EGRESS** by issue #321; never substitute file_id, materialized paths, or public URLs.
- At least one original GitHub artifact exists for Bierstadt V1 (run 43702160089 / artifact 14156323297), but the preferred V2 MP4 is only in Library and has `publication:false`. Do not claim the V1 is the approved V2.

## This PR adds, but does not deploy
- New routes `POST /private-single` and `GET /private-status`, authenticated by a **specific dedicated GitHub Actions OIDC workflow ref on main**, not the existing public uploader.
- Require `PRIVATE_ARCHIVE` R2 binding; if absent, return 503. Store only to `gh-artifacts/<artifact_id>/<filename>` in the separate private bucket. **No video-byte retrieval route**; no client/public gallery, catalog or social publication.
- Accept MP4/MOV/M4V up to 30 MiB through the in-Worker verified SHA256 single-upload route; larger finished MP4s up to 512 MiB through authenticated known-Content-Length streaming. GitHub Actions verifies complete source SHA256 and FFmpeg decode before streaming, R2 readback verifies size and source SHA metadata. **For streaming, the Worker does not independently recompute a full post-upload SHA256 from R2**; do not misreport this as a verified readback digest. Reject source/scout/non-final filename markers and refuse overwrite collisions.
- The existing `.github/workflows/video-library-private-owner-archive.yml` now has two disjoint jobs in the **same workflow**: explicit manual import (artifact ID + exact file + SHA + bytes + private-backup authorization), and scheduled reconciliation **every four hours once merged into main**. No new ChatGPT automation was created. The scheduled job examines at most three recent GH artifacts per cycle, verifies MP4/FFprobe/full FFmpeg decode, deduplicates by artifact ID and immutable private checkpoint, and stores a JSON-only report. It performs **PRIVATE_ARCHIVE writes exclusively**, not public catalog writes. Proven rejected/intermediate/source file names are excluded. Backup is not approval for public publication.
- Offline CI checks Worker syntax, route isolation, exact SHA for small files, streaming with known length, immutable archive checkpoint, idempotency, collision protection, absence of public writes, reconciler selection, and V55 backward compatibility. GitHub Actions CI PASS: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/43859378284 ; this is NOT a live upload test.

## Safe deployment gate — not completed by this PR
1. Obtain live Worker source/version and binding backup; compare exact deployed JS to repo before patching. Record rollback version and test the script on an isolated preview before any live write.
2. Add **only** R2 binding `PRIVATE_ARCHIVE → studio-ai-v3-private-archive` while retaining the existing `VIDEOS` binding and all secrets. Never replace the entire Worker blindly or change the public site Worker.
3. Run a test with a synthetic small MP4 in nonproduction preview and a valid GitHub OIDC token; verify 401 without token and no unauthenticated read, SHA and size, no public bucket/catalog changes. Clear only synthetic preview data with recorded permission.
4. After independent approval of rollout, promote this route and run a manual private archival import for ONE unexpired original artifact whose exact SHA and private-backup authority are known. Verify readback metadata in R2 and preserve logs.
5. Only then design an **authenticated owner preview** with explicit login (not `hidden:true` in public catalog), and a separate per-video signed-off public release gate (PR #323). No private video should appear on public Video Library until rights and owner approval are confirmed.

## Limits
This feature does not repair ChatGPT Library connector egress and does not move Library-only MP4s. It is deliberately not a public gallery. A green CI checks code logic, not the deployed route. No extra paid API, no video regeneration, no cron or other ChatGPT automation. Respect #321 and owner instructions.

## Backfill for Library-only videos (unresolved platform permission)
Existing files produced outside GitHub Actions (for example 15–16 Nov Goya Witches Flight Cinema Museum, Turner Shipwreck Cinema Museum, Franz von Stuck The Sin, Thomas Cole Manhood preferred version) are **not** transformed into GitHub artifacts by changing a workflow. Their Library objects cannot be exported by inventing fileParams or using Library IDs. The authorized OpenAI Library download feature is a user-initiated download. Consequently, this PR must not claim all latest files synced; a one-time sanctioned file-transfer workflow (owner-only local import or restored official file selection) is required for the gaps. New GH-first render jobs will be eligible for automatic private backup once the code, Worker binding and tests are deployed correctly.

## Rollout order
- Run PR offline tests first (current state: pass), review Worker OIDC route-ref allowlist on exact main commit, and backup **existing Worker version + bindings**.
- Preview new Worker version with both `VIDEOS` preserved and `PRIVATE_ARCHIVE → studio-ai-v3-private-archive` added. Test no-token 401, no binding 503, source-only/invalid name 400, hash mismatch 400, private upload/readback, and that public catalog doesn't change. Do not paste any secrets or replace full Worker outside a controlled diff.
- Deploy only with rollback/version evidence. Then merge or enable the private workflow on main after code-deployment compatibility is verified. A green artifact-reconciliation run means **PRIVATE_R2 only**, not SITE_PUBLIC.
- Use a different, explicit per-file site release authorization/rights gate (PR #323) and test public player Range 0–1023 before marking SITE_VISIBLE. Do not auto-promote pending review.
