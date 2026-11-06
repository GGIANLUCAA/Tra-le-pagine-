# WOW LAB — real source and mask gate: Picture of a Balloon — 2026-11-06

Status: **REJECTED — NO MP4, NO APPROVED MASTER, NO RELEASE**.

## Verified source and automation
- Met Open Access / CC0, verified through live Met API in GitHub runner: `Picture of a Balloon`, by Miyagi Gengyo, 1860, object ID `55534`; museum source: https://www.metmuseum.org/art/collection/search/55534
- Original fetched by the isolated GitHub Actions mask-only workflow, SHA256 `99b94eda560233c6c020cc63b66659fad086e1602b5eb5edcd87cc8087ae0202`, 2768 × 4000 pixels. The full image is preserved in the action artifact, not modified in the source.
- Run: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/42270043933
- Actual source/QA artifact: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/42270043933/artifacts/13527679442
- GitHub Actions tests: 87 passed, including FFmpeg/ffprobe regression tests. Live release/queue/slot checks passed with 7 WOW releases and 5 distinct prior subjects: 36075, 37358, 36725, 12127, 45434.
- Generic mask-first preflight failed correctly, reason `subject_near_border,no_candidate_mask`: the decorative border and two full-length onlookers mean the global-color segmentation cannot isolate the balloon.

## Visual investigation of source pixels (outside the approved pipeline)
- The only conceivable single moving subject is the hot-air balloon on the upper left. Its rounded envelope has good contrast against blue sky, but very fine original rigging connects the envelope to the basket and red/white flags.
- Locally tested three tentative region-guided masks (envelope color threshold, basket/flags inclusion, lighter dark rope lines) on the genuine source, plus image-level line-segment detection. These were *diagnostic tests only*, not approved artistic segmentation or published output.
- Enlarged examination showed imperfect/missing ropes, partial connectors and jagged details around the hanging basket and flags. Moving only the envelope would visibly separate a balloon from its own lines or duplicate a stationary balloon. These are hard artistic failures, not minor codec issues.
- No 2.5D/3D label or status of success is justified. Do not hide the defect with synthetic paper or extra flags.

## Decision and iterative correction
- **Reject this image for unattended full-image masking** with the current conservative extractor.
- Preserve the original source, SHA256 and rejection artifact; never put this candidate into an automatic release as a success.
- Improve subject selection toward one contiguous, broad-edged silhouette against a genuinely uniform background and little or no slender attachments, or adopt a guided segmentation pipeline that first proves whole-object completeness at native image resolution; any new mask still requires independent visual review.
- Existing experimental config still has old single-candidate `400112` and is *not* validated for mass production; do not auto-enable owner task or treat `production_ready=false` as publishable.
- During these checks no social post, paid API, core code, or `main` edit occurred. The experimental workflow is a mask-only diagnostic, never publishes releases.
