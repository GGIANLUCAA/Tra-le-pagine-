# WOW LAB · verified source / queue preflight · 2026-10-31 02:24 UTC

Scope: isolated `wow_lab/` branch `experiment/wow-lab-release-queue-hardening-20261030`. No main/core/workflow/social changes.

## Live GitHub evidence
- GitHub Releases REST (per_page=100): 41 releases total; **7** tags prefixed `wow-lab-`; newest `wow-lab-zhu-ling-ink-cat-v4-20261030`, published **2026-10-30 13:05:06 UTC**. No newer WOW release.
- The seven releases represent five distinct Met object IDs: **36075, 37358, 12127, 36725, 45434**. Object **400112** is new relative to those.
- Actions REST: no WOW LAB run among 12 in-progress and none among queued/waiting runs at inspection time; unrelated Storia Rivive/site workflows are active and were not touched.
- Branch-scoped Actions query for `experiment/wow-lab-release-queue-hardening-20261030`: **0 runs**.
- Latest observed main WOW run `41147022659` failed on 2026-10-30 (known slot parser error); no approved new candidate.
- The existing `.github/workflows/wow-lab-isolated-v1.yml` triggers pushes only to `experiment/wow-lab-isolated-v1-20261029`, plus scheduled/main dispatch. It does **not** execute the current experimental branch. Editing workflows or main is forbidden by owner instruction, so no workflow was changed or dispatched.

## Authentic artwork inspected
- Nicolaas Struyk, **A Moth**, Met object **400112**, accession **2008.440.1**. Official museum record: https://www.metmuseum.org/art/collection/search/400112 (Public Domain).
- Official artwork-page image link verified: https://collectionapi.metmuseum.org/api/collection/v1/iiif/400112/770372/main-image
- Browser inspection: one central moth, generally pale paper, distinct dark hand-drawn rectangular border at edges, **very thin antennae/legs**. Technical segmentation may mistake the frame for foreground or amputate antennae. **No mask was downloaded or generated during this execution. Do not treat the source as mask-approved.**
- A different Met record, **400116**, also titled `A Moth`, has a different image and accession **2008.440.5**. The two must never be conflated. The engine now requires the requested object ID to match the API record.

## Actual changes this run
- `engine.save_original()` now checks the public-domain rights gate and tries the **exact verified official Met IIIF image for 400112** only if the normal original/thumbnail image fails. No guessed URLs for other artworks. Regression test: `tests/test_met_iiif_fallback.py`.
- Fixed obsolete test expectations for the atomic no-overwrite run-directory guard in `tests/test_live_preflight_safety.py`.
- `experiments/preflight_single_met.py` now writes `PREFLIGHT_RESULT.json` with `source_acquisition_blocked` if the official image cannot be downloaded; it does not falsely claim a mask or MP4. Regression test added in `tests/test_single_met_preflight.py`.
- GitHub compare `main...experiment/wow-lab-release-queue-hardening-20261030` lists **33 changed files, all under `wow_lab/`** at inspection.

## Blocking gate and decision
- The execution environment cannot resolve Met image hosts via direct HTTP, even though the official image is visible through the browser search tool. No authentic source bytes are available for local OpenCV extraction.
- The experimental branch has no GitHub Actions run/trigger; the owner explicitly forbids modifying `main` or the workflow. Thus tests and real mask extraction could not be executed on a GitHub runner here.
- **NO VIDEO, NO RELEASE, NO APPROVAL.** Do not invent downloadable MP4/ZIP links or substitute a different artwork's image. Next authorized step is a real network-enabled mask preflight for object 400112, visual inspection of the original/mask overlay/clean plate, and rejection if the frame or fine antennae fail. Only then consider a distinctive 2.5D storyboard and video decode QA.

All changes remain isolated. No Vidu, paid APIs, social publishing or core workflow changes.
