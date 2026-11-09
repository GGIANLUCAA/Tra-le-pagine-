# WOW LAB | visual QA | 2026-11-09

## Subject and provenance
Metropolitan Museum of Art CC0, Albrecht Dürer, **The Rhinoceros** (1515), object ID **388482**. Official record: https://www.metmuseum.org/art/collection/search/388482. This subject is distinct from the previous six unique WOW LAB release artworks.

## Reproducible experimental output
Isolated GitHub Actions run **42584555936**, experimental branch **experiment/wow-lab-isolated-v1-20261029**. The job produced a 10.0 s 540x960 20 fps H.264/AAC MP4 with independently synthesized audio and a downloadable GitHub Actions ZIP artifact. ffprobe verified both streams, full ffmpeg decode exited successfully; source SHA-256 `9a402eea7639299e8778db4a2c2b3922d449f604733cf64e548a9c4daa180732`.

**Artistic decision: NON APPROVATO (technical preview only).** The camera merely orbits a framed engraving. No subject separation, real pop-out, or compelling surprise occurs; do not call the preview a successful WOW master.

## Rejected segmentation preflight
High-resolution source 3682x2942 used for independent manual + GrabCut mask candidate. On actual visual inspection, the mask cuts inaccurately around ears and horn, carries an obvious pale paper triangle beneath the chin, includes original floor and hatch marks near hooves, and has rough dorsal edge traces. **Mask QA FAIL; no pop-out rendering is authorized from this mask.**

## Root causes and next step
1. Default `gallery_orbit` recipe is too generic. Do not publish as approved.
2. Original etching uses similarly textured pale material for the rhino and background; color-based segmentation is insufficient.
3. Choose ONE new CC0 artwork with a truly bold, isolated silhouette against a distinct backdrop, and inspect high-resolution edge, thin elements, background fill and cast shadows before any pop-out render.
4. Respect duplicate guards: do not re-use this Dürer subject in the next six episodes; do not retry rejected Moth 400112/Balloon 55534; do not extract fragile Bluebird flowers.
5. Verify H264/AAC, full decode, frames, downloadable MP4/ZIP and cost=0. No social publication.

## Safety
No paid APIs or Vidu; `no_paid_services=true`, `no_vidu=true`, `production_ready=false` remain unchanged. No modification to main, ArtVision, La Storia Rivive, Cinema Reale, website or official automations. No social publication.