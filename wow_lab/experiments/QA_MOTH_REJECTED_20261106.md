# WOW LAB — candidate gate / rejected · 2026-11-06

## Checked, not inferred
- Scope: experimental branch only; no `main`, no studio, no social publication, no paid API.
- Current release list at preflight: 7 `wow-lab-*` releases, 5 distinct Met object IDs: 36075, 37358, 36725, 12127, 45434. No active concurrent WOW render at gate.
- GitHub Actions run: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/42269374236
- 87/87 isolated regression tests passed, FFmpeg installed and tested.
- `LIVE_GITHUB_PREFLIGHT_PASS`: slot `20261106T18`, distinct_previous `[36075,37358,36725,12127,45434]`.
- Actual source: Nicolaas Struyk, *A Moth*, Met object 400112, official https://www.metmuseum.org/art/collection/search/400112, CC0 `isPublicDomain=true`.
- Original actual JPEG acquired by GitHub runner, 1317×1492 pixels, SHA-256 `a3005f12b96555fc441534d60c341bdec79c370dbd1ed929eaf4f56406c4292d`.
- Mask gate report: `technical_pass=false`, `proposal.reasons=["nonuniform_background"]`, `border_lab_p90=75.98`, `geometry.reasons=["no_candidate_mask"]`.
- Direct visual inspection of the authentic original: historical rectangular ink frame plus variable tan paper background; four wings and extremely thin antennae and legs. Automated foreground extraction would risk amputating or fusing these details, contrary to fidelity and Bluebird V3 feedback.
- Review artifact (real source + audit + contact sheet): https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/42269374236/artifacts/13528303217

## Release decision
**REJECTED: no valid subject mask.** No candidate video, no approved master, no ZIP and no release. Do NOT bypass the mask gate or claim that the real original is easy to segment.

## Correction / next experiment
Try a different authentic CC0 image with a dominant broad outline and a localized clean backdrop. The next *mask-only* source study is Miyagi Gengyo's `Picture of a Balloon` (Met object 55534), 1860, official https://www.metmuseum.org/art/collection/search/55534. This artwork is not among the five known released subjects. Its balloon is isolated visually against a sky, but strings and basket need strict real-size inspection before any 2.5D render. Do not assume numerical segmentation proves semantic completeness. Never use any of the two humans in the foreground as an extracted duplicate.
