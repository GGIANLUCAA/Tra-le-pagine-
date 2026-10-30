# WOW LAB — autonomous preflight, isolated branch, 2026-10-30

Scope: only `wow_lab/`. No core changes, social posts, Vidu, paid APIs, or production release.

## Repository checks

- GitHub WOW releases inspected: latest distinct Met objects **36075, 37358, 36725, 12127, 45434**; V1/V2/V3 repetitions counted once. The release history includes multiple items in the same **20261030T12 UTC** window; do not render another candidate for that window.
- Queried public GitHub Actions `status=in_progress` and `status=queued`; both returned **0** at inspection time. This is a point-in-time observation, not a distributed lock.
- The protected main scheduler has not been updated; these experimental changes are not yet active there.

## Source proposal (NOT a video)

**Nicolaas Struyk, A Moth**, Metropolitan Museum of Art, official object **400112**, early/mid 18th century. Official collection page labels the drawing **Public Domain**:
https://www.metmuseum.org/art/collection/search/400112

This object is absent from the last five distinct WOW subjects. Its possible advantage is a relatively isolated moth on paper; **not verified from source pixels**. Fine antennae and watercolor transparency are major extraction risks. The previously proposed object number 400116 was not confirmed; 400112 is the official page returned for this work.

## New isolated pre-render proposal

- `wow_lab/subject_extractor.py`: conservative CPU OpenCV mask proposal for single dark/colored subject on uniform background. Background statistics from image perimeter; rejects busy borders, missing subjects, multiple objects, edge-touching subjects, weak seeds, background-like pixels; GrabCut refinement.
- Calls `wow_lab/mask_audit.py` after segmentation. Writes `candidate_mask.png`, `mask_before_render.jpg`, `subject_preflight.json` **before any render**.
- Fails closed (exit 2) on rejection. Technical mask success does not imply semantic completeness or artistic approval.
- Five offline synthetic regression tests added under `wow_lab/tests/`. These passed in a local CPU reproduction; GitHub Actions on this new branch have **not** been executed.

## Regia proposed, conditional on actual mask review

Moth on paper; within 2–4 seconds the drawing subtly comes alive. If the entire moth, wing tips, and antennae can be segmented without paper leakage, animate a restrained wing lift over the virtual frame, a shadow cast onto the surrounding wall, slight foreground parallax, and return to the original drawing. Original synthesized audio only. This is a **2.5D cut-out illusion**, not a reconstructed volumetric 3D moth. Reject if antennae, body, or wing edges are lost.

## Honest block

The official high-resolution image was not acquired in this run; no real-source mask preview exists. Thus there is **no approved mask, no verified pop-out video, no FFmpeg QA, no MP4/ZIP, and no release**. The new module is not yet wired into the existing `engine.py` renderer; enabling unattended production would be premature. The next safe step is real-source acquisition and inspection of the generated mask, then integration and full video QA on this branch.
