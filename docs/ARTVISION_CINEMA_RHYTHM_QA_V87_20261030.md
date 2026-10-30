# ArtVision Cinema Standard V87 — advisory on real MP4 (30/10/2026)

This is a **read-only diagnostic**, not a renderer, approval, publication, or replacement for V25. It never changes a master, queue, pilot lock, or API consumption. Apply to Cinema Standard only; intentional hard cuts are not a Museum V57 violation.

Run: `python src/artvision_cinema_rhythm_guard_v87.py /path/to/real_cinema_standard.mp4`

Dependencies: OpenCV and NumPy; the script decodes every frame, samples a 135×240 grayscale image, and reports hard-cut candidates (MAD >20/255, minimum 0.5s separation), interval regularity, and trailing majority-black composition. Thresholds are **heuristics** and only flag a human review. Dark scenes may be intentional; a PASS does not mean the film is beautiful or V25 approved.

## Reproducible checks performed on actual files

- Wright *An Experiment on a Bird in the Air Pump* Cinema Standard V52B original, **6,690,474 bytes**, SHA256 `ec4525c155334a02696bfa05d745005bea3084f178043c9eaf1dca6d7bfe29e2`, 1339 frames at 24fps: nine candidate cuts at 5.417/10.500/15.792/21.000/26.208/31.500/36.708/41.917/47.208s. Mean internal cut interval **5.224s**, CV **1.26%**. Final **8.583s** majority-black frame composition. **Two artistic advisories raised**. The original master is untouched.
- Separate Fabritius V86A museum-style reference MP4, 880 frames at 20fps: no hard cuts and no trailing majority-black sequence. **No advisory**. This is a sanity check, **not** a Cinema Standard validation or Gold approval.
- Three synthetic regression tests (periodic cuts + dark outro, stable image, missing file): **3/3 PASS locally**.

## Backup boundary checked

Dropbox metadata for the already authorized **Klimt** file `/ARTVISION_KLIMT_4X1_PACCHETTO_COMPLETO.zip`, ID `id:VU6duCyxXTcAAAAAAAAELQ`, returned **65,968,295 bytes** and `is_downloadable=true` (server-modified 2026-10-29 20:33:52Z). A temporary download link could be generated, but this execution's container had no DNS/network route to retrieve the bytes; **no successful roundtrip CRC or SHA** can be claimed. No upload was performed. This does not authorize Bosch, Hokusai, or Wright uploads.

All five user-authorized artworks remain 20 existing slots, 0 automatic Gold V25. The sixth artwork is not authorized. No new voice or video API calls.
