# ArtVision Museum Scale S01 / E01 — The Goldfinch (28 October 2026)

**Status: `rendered_needs_review`, NOT Gold Master, NOT social-published.** Latest review candidate: **V50**.

## Actual work, not just a run request
- Subject: **The Goldfinch** (1654), **Carel Fabritius**, Mauritshuis, The Hague, inventory 605.
- Format: **ArtVision Cinema V6** (instrumental, no critic voice), 1080 × 1920, 24 fps, H.264/AAC, **55.00 s**.
- Exact candidate SHA-256: `5b760c609a51acf9c22a5f39aeb90344ea6914b812290c5fc01164376d3c94bd`.
- Candidate: `ArtVision_Goldfinch_Museum_V50_REVIEW.mp4` (24,192,101 bytes), complete ZIP `ArtVision_Goldfinch_Museum_V50_Complete.zip` (45,705,565 bytes), cover `ArtVision_Goldfinch_Museum_V50_Cover.jpg`.
- ChatGPT Library copies confirmed: `/ArtVision/Museum_Scale_S01/ArtVision_Goldfinch_Museum_V50_REVIEW.mp4` and `/ArtVision/Museum_Scale_S01/ArtVision_Goldfinch_Museum_V50_Complete.zip`. Separate cover and contact-sheet Library uploads failed with indexing permission error; both exist in ZIP and local conversation files.
- GitHub Actions **V48** technical source render [run 40614672767](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/40614672767), [artifact 12784144033](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/40614672767#artifacts). V48 passed technical checks but was **artistically rejected as a flat vector gallery**; do not publish or promote V48. V49 replaced the gallery with a more credible photographic-style original reconstruction. V50 further replaced repetitive details with five purposeful views.
- V49 and V50 local scripts archived in `scripts/artvision_goldfinch_museum_v49_local.py` and `scripts/artvision_goldfinch_museum_v50_details_local.py`, and included in ZIP under their original local filenames. They expect original files unpacked into the documented working paths; these are **not** a standalone cloud runner. V48 cloud renderer remains separately preserved for traceability.
- No video-generation paid APIs, no social publishing, no edits to earlier approved masters.

## Queue and three-candidate research
The user-approved `queue/artvision_museum_scale_s01_20261028.json` takes precedence over a new random subject.
1. **Carel Fabritius, The Goldfinch** — selected: an illusion of life and a delicate chain; a genuinely small panel (33.5 × 22.8 cm), strong primary museum documentation and high-res PD-Art source.
2. **J. M. W. Turner, The Fighting Temeraire** — held for S01 E02 Critico; **do not render without real Google Gacrux speech**.
3. **Georges Seurat, A Sunday on La Grande Jatte—1884** — held for S01 E03, monumental 207.6 × 308 cm painting.
No comparable audience analytics were available; no viral-performance claims. No previous Goldfinch release was found in the production register at start.

## Provenance and physical scale
- Official museum [Mauritshuis inv. 605](https://www.mauritshuis.nl/en/our-collection/artworks/605-the-goldfinch): 33.5 × 22.8 cm, oil on panel, Room 14. The museum describes the chained bird, its trained water-drawing behavior, and the scratched wet yellow paint on the wing.
- Actual artwork photo [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Carel_Fabritius_-_The_Goldfinch_-_605_-_Mauritshuis.jpg), faithful photograph of public-domain flat art (PD-Art/PDM; country-specific reuse caveat), 3930 × 6000 pixels. The original image is preserved in ZIP.
- The museum background is **newly generated, illustrative and not a real Mauritshuis interior**. An adult visitor provides the approximate human-scale reference; the panel stays physically small at the opening and only grows as the virtual viewpoint approaches. The fictional visitor and room must not be described as documentary.
- The panel is drawn behind the inner frame lip with contact shadow. No ghosting, double exposures, alpha overlays of paintings, pixel-row stretching or paid i2v.
- Recording: **Water Lily — Kevin MacLeod**, official [track / ISRC USUAN1400035](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1400035), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The actual MP3 is included in ZIP; attribution appears in all four distinct Italian social posts. Territory/platform claims still require publication review.

## Storyboard V50
- 00–05.58 s: museum wide, tiny original-size panel, exact title and artist in approved V6 dark band.
- 05.58–10.67 s: slow visitor approach; photographic-style reconstructed gallery.
- 10.67–16.08 s: physical panel becomes legible in its frame.
- 16.08–21.38 s: authentic painted bird and feeder.
- 21.38–26.46 s: bird's red mask and eye, subtle single push.
- 26.46–31.54 s: scratched yellow wing, subtle single push.
- 31.54–36.75 s: chain and feeding-box, still camera.
- 36.75–42.17 s: original entire panel and signature.
- 42.17–47.25 s: return to framed painting in the same fictional gallery.
- 47.25–55.00 s: retreat to human scale, same room.

## Actual QA and known limits
- MP4 confirmed **H.264, AAC, 1080 × 1920, 24 fps, 1,321 frames, 55.00 s** by ffprobe.
- Complete ffmpeg decode with `-xerror` passed. Audio mean **−19.8 dB**, maximum **−3.2 dB** (volumedetect; not a listening review).
- Cover and first MP4 frame visually inspected: **THE GOLDFINCH** and **CAREL FABRITIUS** present, same serif title, sans artist, dark band, gold rule and placement as the series reference. Mean absolute band difference after encoding ≈ **2.29**. This explicitly prevents the opening-identity defect from **The Temptation of Saint Anthony**.
- Frames at 0, 3, 6, 11, 15.9, 16.1, 21.6, 25, 28, 33, 38, 41.9, 42.2, 47.3, 54.9 s visually inspected; museum and detail crops are opaque and show no visible edge-stretch. The entire film was machine-decoded but **not fully watched/listened to by a human reviewer at normal speed**.
- V50 ZIP CRC `testzip() == None`, includes MP4, JPEG cover, four original V28 posts, original art and original licensed recording, illustrated gallery source, V49/V50 scripts, QA, recipe, storyboard, research and rights.
- Artistic state remains **`rendered_needs_review`**. No false V44 approval or social publication.

## Three issues for next cycle
1. Judge the perceived continuity of the gallery → painted close-up → gallery transitions at normal playback speed.
2. Listen to the complete musical phrase and ensure the five detail holds are neither repetitive nor excessively slow.
3. Compare the photographic-style *illustrative* gallery against the approved Redon Cyclops edge-fixed and Hiroshige physical-scale models; improve contact shadow/frame depth only if it meaningfully helps.

**No new paid model call is authorized.** S01 E02 remains queued, and requires verified natural Google Gacrux narration before any Critico render.
