# WOW LAB — live evidence, root-cause diagnosis, and one-source preflight · 2026-10-31

Scope: ONLY `wow_lab/` on `experiment/wow-lab-release-queue-hardening-20261030`.
No change to `main`, `.github/workflows/`, ArtVision, Storia Rivive, Vidu, or site.

## Live GitHub check (31 Oct 2026, approx. 01:54 UTC)

- GitHub Releases REST endpoint returned 41 releases, 7 with `wow-lab-*` tags; no new WOW LAB release after `wow-lab-zhu-ling-ink-cat-v4-20261030` (published 2026-10-30 13:05:06 UTC).
- Latest distinct WOW subjects observed: Zhu Ling cat (Met 36075), Sharaku Kabuki hand (37358), Madame X (12127), Hiroshige bluebird (36725), Hokusai (45434). There were seven WOW releases but only five distinct subject IDs.
- WOW LAB runs on `experiment/wow-lab-isolated-v1-20261029`: most recent run 41036823896, success 2026-10-30 09:55 UTC; not an approved master.
- WOW LAB runs on `main`: 41115357751 and 41147022659 both FAILED in the `Generate original-source CC0 2.5D candidate` step, last failure 2026-10-30 23:53 UTC. Publish job skipped.
- Branch `experiment/wow-lab-release-queue-hardening-20261030` had zero Actions runs. No active WOW LAB run was returned in the branch-scoped checks. Unrelated workflows were active; they are not WOW LAB conflicts.

## Exact root cause (not a source-image failure)

Both failed main jobs logged `WOW_LAB_FAIL_CLOSED: invalid literal for int() with base 10: '0T'`.
In `main:wow_lab/engine.py`, `select_artwork()` used `int(stamp[-4:-2])` on an `YYYYMMDDTHH` slot, yielding `'0T'` or `'1T'`. The isolated experimental branch already uses `int(stamp[6:8])` (UTC day), and a regression now covers 36 even-hour slots across three days. This fix has NOT been merged into main.

A separate experimental-branch issue was corrected: package-gate JSON reports were appending the literal two characters backslash+n instead of a newline, making the files invalid JSON. Commit `8c7886a` corrects the serialization.

## Exactly one new candidate for source/mask review (NOT a released video)

- Title: **A Moth**; artist Nicolaas Struyk; Met object **400112**; drawing, 18th century.
- Official record: https://www.metmuseum.org/art/collection/search/400112
- Official API: https://collectionapi.metmuseum.org/public/collection/v1/objects/400112
- Official source: https://images.metmuseum.org/CRDImages/dp/original/DP820071.jpg
- API `isPublicDomain=true`; Met Open Access / CC0.
- Not among the five distinct WOW LAB subjects in the latest seven releases.
- The image was visually inspected via the museum-sourced CC0 Wikimedia copy. It shows one central moth, four wings, very thin antennae, a textured off-white sheet, and a dark rectangular drawn border. **These are extraction risks**: the border must never be included, and the antennae must not be amputated or hallucinated. This source is NOT yet mask-approved and may be rejected.
- Before rendering, run `wow_lab/experiments/preflight_single_met.py --object-id 400112 --out wow_lab/runs/preflight-400112-UNIQUE` in a network-enabled environment. It writes original source, mask, mask overlay, clean-plate audit and a four-panel contact sheet; rejects rather than renders if checks fail.
- Proposed **conditional** 2.5D direction if the full silhouette passes: first 2–3 seconds show the complete historical drawing; then a subtle, slow emergence of the moth above the picture plane, preserving wing and antenna shapes; the offset shadow follows only the moth, not the entire paper; camera parallax stays restrained; hold to appreciate the wing markings; return to the original artwork. Use only an original procedural soundtrack. Do not claim volumetric 3D, real flight, or an authentic physical museum frame.

## Release decision

**NO RELEASE / NOT ARTISTICALLY APPROVED.** The original image pixels could be inspected visually, but a machine-readable original file was not downloadable in this execution environment, so no real mask or full decode could be performed here. GitHub Actions does not trigger on the current experimental branch, and the existing workflow hardcodes a different test source (Met 436535, Van Gogh `Wheat Field with Cypresses`, unsuitable for a clean single-subject extraction). Changing that workflow or `main` is expressly outside the authorized scope.

Required next gate: execute real source-mask audit on the isolated branch in a network-enabled runner, visually inspect the contact sheet, reject incomplete silhouettes, then render and run ffprobe/full decode/still QA. Do not publish a success release based on technical-only evidence. No purchases or social publication.
