# WOW LAB · Clean-plate + post-render quality gates · 2026-10-31

**Isolation:** all edits on `experiment/wow-lab-release-queue-hardening-20261030`, strictly under `wow_lab/`. Compared against `main`: zero changed files outside `wow_lab/`. No changes to `main`, core workflows, ArtVision, La Storia Rivive, Vidu, site, or parent automations.

## New protections

1. `subject_popout.audit_clean_plate()` rejects inpainting over non-uniform scenery before the first audio/video frame. It examines the LAB variation of the actual source's ring around the extracted silhouette and the reconstructed patch. Limits: ring p90 <= 18, reconstructed region p90 <= 28. Every candidate writes `CLEAN_PLATE_AUDIT.json`; failed candidates raise `PreflightRejected`. This cannot certify semantic correctness or a convincing artistic effect.
2. `review_video.review()` performs a second independent `ffprobe` / `ffmpeg -xerror` full-decode check, samples eight frames, writes `VIDEO_CONTACT_SHEET.jpg` and `VIDEO_REVIEW.json`, and rejects static videos (fewer than three inter-sample differences above 1.2 mean RGB units). It explicitly keeps `artistic_approval=false` and `publishable_master=false`.
3. `engine.run()` now invokes this second video review **before** generating social drafts, manifest, and ZIP. Technical rejection writes `REJECTED_REPORT.json` and stops; the contact sheet and report are included in a successful technical candidate's ZIP.
4. Added `tests/test_clean_plate_gate.py` and `tests/test_video_review_gate.py` (8 cases total) for uniform/patterned backgrounds, invalid inpainting, moving/static AAC MP4, path restrictions, and QA ordering.

## Actual validation

- Four synthetic clean-plate numerical checks were run in the local Python/OpenCV environment: uniform background accepted technically; checkerboard background, incorrect inpaint color, and mismatched dimensions rejected.
- Two synthetic H.264/AAC clips were generated and inspected locally with OpenCV: moving test pattern yielded 7/7 active frame transitions; static gray video yielded 0/7. These validate the threshold logic, **not a real artwork**.
- The committed full GitHub test suite was **not run**. There is no live end-to-end verified WOW LAB render.
- Current GitHub releases and Actions queue were **not verified**: public GitHub API was inaccessible from the available web/container environment; the connected GitHub actions expose file reads and known-run reads but not complete release/queue listing. Hence no new slot or subject is claimed as free, and no new MP4/release was started.
- No authentic CC0 source image or real mask was acquired or artistically reviewed in this run. No preview/master/ZIP or download link has been claimed.

## Release decision

**FAIL CLOSED / NO RELEASE.** Resume candidate production only in a verified GitHub runtime with a complete live release/queue preflight, real CC0 source and inspected silhouette, accepted clean plate, genuine frame crossing, full decode, contact sheet, and artistic review. Do not label geometric success as true 3D or an approved master.
