# WOW LAB — mask gate V2 preflight, 2026-10-30

Status: **technical guard improved; NO NEW MP4; NO RELEASE**.

## Isolation / duplicate check
- Scope: only `wow_lab/` on `experiment/wow-lab-mask-gate-20261030`. No changes to main, protected rules, other workflows, archive, Vidu, or social platforms.
- Existing distinct released Met objects: 12127 (Madame X V1/V2), 36725 (Hiroshige Bluebird), 45434 (Hokusai). V1/V2 Madame X count as one subject.
- Recent WOW LAB GitHub mirror runs 41049208836 and 41049068007 both completed successfully; no WOW LAB render in progress among the inspected recent workflow runs.
- No new slot release created here.

## New candidate, NOT rendered
- Nicolaas Struyk, *A Moth*, Metropolitan Museum of Art object **400116**, accession 2008.440.5.
- Official source: https://www.metmuseum.org/art/collection/search/400116
- Public Domain according to official Met object page; separate full-size image URL observed: https://images.metmuseum.org/CRDImages/dp/original/DP820075.jpg
- One centered moth on pale paper with relatively opaque wings; unlike the previous bird and wave tests, the subject is an insect. Thin antennae and brushy outer edges remain a **significant silhouette risk**.
- The source image could not be materialized into the working runtime this run; therefore no authentic image mask could be generated or verified. Do not call this candidate production-ready or count it as a completed release.

## Mask gate V2 — local regression
- Added inner/outer CIELAB boundary contrast check to catch cut-out regions that merely contain the original background.
- Added interior-hole count to detect missing subject patches; still checks area, components, border contact, and contour complexity.
- Every technical PASS explicitly reports `semantic_completeness_verified=false` and `requires_visual_review=true`.
- Seven synthetic offline unit tests passed locally.
- Existing authentic Hiroshige Bluebird work image + old mask: **REJECTED**, `internal_holes_subject_missing_patches` (6 internal holes), despite a boundary contrast of 23.34 LAB. This matches the user's criticism of the previous extraction.
- Existing authentic Hokusai wave mask: **REJECTED**, with border contact (225 pixels), 22 internal holes, and weak boundary contrast (0.40 LAB). It is not a suitable silhouette master.
- Audit images were inspected; previous Bluebird silhouette includes unmasked patches within the bird. No artistic approval granted.

## Next safe step
1. Acquire official full-resolution image and verify image/source hash and CC0.
2. Produce candidate mask for moth, audit against the authentic source and inspect antennae/wing edges at native resolution.
3. If mask fails, reject before render; do not substitute zoom or whole-canvas perspective.
4. Only after a verified mask, create isolated MP4+AAC and full QA, then consider a namespaced Android release.

No paid API, no new social post, no new video link, no GitHub main modification.
