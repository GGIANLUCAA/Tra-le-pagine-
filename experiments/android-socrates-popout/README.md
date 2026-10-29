# ArtVision 3D Studio — Android Pop-Out Socrates (isolated experiment)

**State:** executable, self-contained browser prototype; **not** a verified 3D reconstruction, production renderer, Android-tested MP4, or published site feature.

**Branch:** `experiment/android-socrates-popout-standard-20261029`
**Entry point:** `experiments/android-socrates-popout/index.html`
**Artwork:** *The Death of Socrates*, Jacques-Louis David (1787), Met object 436105. Official reference: https://www.metmuseum.org/art/collection/search/436105 — The Met marks the work Public Domain, painting 129.5 × 196.2 cm. Get source JPG from the Met and upload it directly from Android.

## What is implemented now

- Standalone mobile-first Italian HTML page, no npm/build/external libraries.
- Android file input for genuine painting and optional externally cleaned/inpainted painting.
- Touch polygon selection of Socrates. An **indicative polygon** button is only an editable guess, not AI segmentation.
- Front-facing 2.5D cutout: illustrated frame, clipped original artwork texture, displacement + scaling with easing and contact shadow; landscape art placed in portrait 720×1280.
- 7-second preview rendered in HTML Canvas and user-triggered PNG export.
- Optional user-triggered `MediaRecorder` download when browser supports video canvas capture, format WebM in common browsers (or MP4 only if the browser itself supports it).
- Images processed in memory in the browser. No uploads, paid APIs, secrets, Vidu calls or network requests in application code.

## Honest boundaries

- **Not real 3D**: the cutout remains a flat textured plane; it cannot reveal unknown sides of the body, fabric or face. This is a visual feasibility lab, not a mesh generator.
- No automatic SAM/AI segmentation, no Hunyuan/TRELLIS backend, no GPU.
- If the user does **not** load a clean background, the original Socrates remains partially underneath a blurred approximation; this can cause ghosting and is not acceptable as a final master.
- The on-screen frame is scenic reconstruction, **not** Met's documented frame; museum scale/reconstruction rules V46/V69 apply to any actual production.
- Export depends on Android browser support; WebM is **not MP4/H.264**. No verified Android device playback or end-to-end export test has been performed. For final MP4, add a separate tested FFmpeg CPU conversion workflow after review.
- No audio, QA dossier, cover, social texts, archive upload or SHA/ZIP packaging. The experiment is not a delivered ArtVision V55 film.

## Android manual trial

1. From an Android browser download the HTML file, then open it in a browser supporting local HTML files (or serve through a separate static preview host). Browser file restrictions vary.
2. Download the authentic Met image; select **Carica il dipinto**.
3. Trace Socrates' whole silhouette carefully with the finger, including raised arm and clothing. Use **Ricomincia** if needed; the indicative mask is not a finished mask.
4. Optionally supply a retouched **background without the subject** to prevent a double figure.
5. Tap **Anteprima 7 s**. If available, tap **Registra WebM** or **Salva fotogramma PNG**. Check the resulting file on the device before claiming success.

## Production-safe integration plan (NOT implemented)

```
Android controller → source CC0/rights preflight
                   → SAM 2/other foreground segmentation on authorized free remote compute
                   → image clean plate / manual verification
                   → 3D image-to-mesh (candidate, GPU/license availability check)
                   → camera projection / texture preservation / genuine occlusion
                   → Blender/FFmpeg compositing
                   → QA preview to Android → optional V55 dossier + private archive
```

- Prototype first with exact subject, silhouette and clean plate; then compare 2.5D vs one real 3D mesh from a compatible remotely run model.
- Use a separate workflow activated **only manually** for this experiment, never `schedule`, `push`, `workflow_dispatch` from production orchestration or `repository_dispatch` that triggers four-variant production.
- Explicit user authorization **before any paid GPU or video API call**, and fail-closed on unavailable free compute.
- Preserve ArtVision V58/V68 pilot locks, unique owner, four existing video slots and V25 approvals; this experiment is not an extra ArtVision 4×1 slot. Never auto-publish or auto-merge.
- To deploy on a public site, create explicit **static** preview hosting separately, avoiding changes to existing site build and worker until reviewed.

## Verification carried out on 29 Oct 2026

- Repo `GGIANLUCAA/Tra-le-pagine-` inspected; default branch `main`, existing `src/`, `docs/`, `.github/workflows/` and V58/V68 rules confirmed.
- HTML and JavaScript syntax checked using Node.js `--check`; validated no network fetching or external dependencies in client source.
- Container browser navigation was blocked by execution-environment policy. **Not** tested successfully on real Android. No source image or end-user rendering result was produced.

**Gate to next step:** user reviews Android 2.5D trial; correct segmentation/clean plate and output. Only then pilot actual image-to-3D model on verified free remote resource.

## Review correction after real source test (29 October 2026)

A separate GitHub Actions workflow `experiment-android-socrates-popout.yml` was exercised on the genuine Met image. Run 40926187730 generated a real 5s MP4 and comparison but **its automatic GrabCut mask accidentally included part of the red-clothed disciple**. Therefore its output/artifact 12920302226 is **REJECTED ARTISTICALLY**. File-level tests alone did not catch this mistake. Do not claim that run as the final before/after.

The corrected manual-mask test was generated separately within the ChatGPT working environment, from the same genuine Met image (4000×2663), using only the contours of Socrates. The reviewer inspected the new side-by-side picture and frames 0,1,2,3,4,5; a 6-second vertical H.264/AAC MP4, stills, and an offline Android HTML slider were exported and verified with FFmpeg. Source image and original soundtrack are zero-paid-API. This **remains a 2.5D painted cutout**, not a true 3D mesh, and the backdrop/frame are scenic reconstructions. The corrected sandbox attachment is NOT automatically persisted to GitHub or the private Video Library; the cloud workflow needs the hand-traced silhouette and art-QA gate before it can replace this experiment. The four ArtVision V68 videos, master records, live site, and production owner were not changed.
