# The Tower of Babel — V136 evidence (2026-11-03)

Exact work: Pieter Bruegel the Elder, **The Tower of Babel** (Vienna large version, 1563), Kunsthistorisches Museum **GG 1026**, painting 114.4 × 155.5 cm. Public visible title: **The Tower of Babel**; no project name or variant label. Only one candidate for internal cinema_standard slot.

## Evidence verified in GitHub Actions

- One run: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41549505091 (success, completed 2026-11-02 23:59:49 UTC); job 125633288051 success, no rerun.
- Renderer ran and performed full FFmpeg decode, video readback via OpenCV and SHA256 on runner; the separate workflow step independently re-read and hashed the physical MP4 and checked frame count.
- MP4: BRUEGEL_THE_TOWER_OF_BABEL_CINEMA_V136_REVIEW.mp4; **18,165,533 bytes**, SHA256 **ad401e87ac181d6627bed80b5072a466fa2cc930143857838896b4d1bfe7a6a4**, 59.4 s, 1,188 frames, 720 × 1280 at 20 fps; full FFmpeg decode PASS **on GitHub runner**.
- Inner ZIP: BRUEGEL_BABEL_V136_CINEMA_REVIEW_PACKAGE.zip; **25,313,745 bytes**, SHA256 **f1db3a60e17766c6988383f75bf9460d978787f5d10eac73f40441c5b1c4c416**, CRC PASS on runner. Note renderer writes QA_V136.json once more after packaging, so the QA file inside inner ZIP is earlier snapshot; video and package SHA are printed in logs.
- GitHub Actions artifact: ID **13190316891**, **44,058,851 bytes**, SHA256 **857efc85a1f8ba13894d8e7b4308aa27683ed0a2ca65a3e209e8c5019ac2fcc9**, 5 uploaded files. Link https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41549505091/artifacts/13190316891 (retention through 2026-12-02 23:59:45 UTC).
- GitHub connector **download_workflow_artifact** completed and materialized the outer ZIP as `/mnt/data/babel_v136_actions_artifact.zip` in this conversation. The container runtime returned Redis/connection errors on attempts to open/hash/decode the downloaded ZIP; independent local SHA/CRC/full decode readback is **not** claimed.

## Source and rights

- Image source is the independent Wikimedia Commons PD-Art/PDM file https://commons.wikimedia.org/wiki/File:The_Tower_of_Babel_(Bruegel).jpg (Commons offers a 3840px thumbnail of the exact Vienna composition). **Not** a KHM official private-use download. The code validates JPEG, minimum 2560 × 1900 pixels and aspect ratio 1.30–1.37, but source SHA and actual downloaded dimensions must be read from QA_V136.json before final approval. Rights for commercial distribution and relevant national heritage rules require a separate final review.
- Audio was procedurally synthesized in the local renderer; no third-party music samples, TTS, Vidu or paid API calls. Museum room and frame were not invented in this cinema candidate.

## Release gate

**Keep slots_delivered_this_selection at 0** until independently re-reading the downloaded artifact and validating outer ZIP digest, MP4 SHA and full FFmpeg decode. The CI-produced MP4 exists, but is **not** claimed as delivered, Gold, published, archived permanently or playable on the site. No duplicate V136 request or rerun. After passing readback, change this same slot to 1; then consider next variant one at a time, after rights/quality gates. Preserve all master versions.
