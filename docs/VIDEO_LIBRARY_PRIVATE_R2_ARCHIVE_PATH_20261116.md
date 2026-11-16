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
- Limit to MP4/MOV/M4V up to 30 MiB, reject source/scout/non-final filename markers, verify full SHA256 of uploaded bytes and exact stored byte length, refuse overwrites on collisions.
- Manual-only `.github/workflows/video-library-private-owner-archive.yml`: requires concrete artifact ID, exact internal filename, expected SHA256, expected bytes and explicit private-backup authorization. Checks GitHub artifact metadata, unexpired ZIP, full MP4 hash and FFprobe + FFmpeg decode before private upload.
- Offline CI verifies route isolation, exact SHA, idempotency, collision protection, absence of public writes and compatibility with V55 existing tests.

## Safe deployment gate — not completed by this PR
1. Obtain live Worker source/version and binding backup; compare exact deployed JS to repo before patching. Record rollback version and test the script on an isolated preview before any live write.
2. Add **only** R2 binding `PRIVATE_ARCHIVE → studio-ai-v3-private-archive` while retaining the existing `VIDEOS` binding and all secrets. Never replace the entire Worker blindly or change the public site Worker.
3. Run a test with a synthetic small MP4 in nonproduction preview and a valid GitHub OIDC token; verify 401 without token and no unauthenticated read, SHA and size, no public bucket/catalog changes. Clear only synthetic preview data with recorded permission.
4. After independent approval of rollout, promote this route and run a manual private archival import for ONE unexpired original artifact whose exact SHA and private-backup authority are known. Verify readback metadata in R2 and preserve logs.
5. Only then design an **authenticated owner preview** with explicit login (not `hidden:true` in public catalog), and a separate per-video signed-off public release gate (PR #323). No private video should appear on public Video Library until rights and owner approval are confirmed.

## Limits
This feature does not repair ChatGPT Library connector egress and does not move Library-only MP4s. It is deliberately not a public gallery. A green CI checks code logic, not the deployed route. No extra paid API, no video regeneration, no cron or other ChatGPT automation. Respect #321 and owner instructions.
