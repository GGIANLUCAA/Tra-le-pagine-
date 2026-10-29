# ArtVision · Vermeer Pop-Out V2 — Experimental Android CPU Pipeline

**Status 29 October 2026:** separate test module, source-faithful 2.5D geometry. **Not a full 3D sculpture or an approved ArtVision master.**

## User feedback and correction
The first Vermeer video was rejected: it was essentially a magnification, with insufficient perceived depth compared to the Socrates proof. The replacement must have a visibly different camera/foreground geometry, an object crossing a frame edge, absence of duplicate silhouettes, and identity of face and materials grounded in the actual painting. Do not substitute a newly generated AI portrait image for a technical proof.

## Implementation and files
- Renderer: `artvision_popout_v2_standalone.py` in this experiment directory.
- Runner: `.github/workflows/experiment-vermeer-popout-v2.yml`, scoped **only** to this test branch and its own files. No schedule, no Vidu, no secret, no paid API, no publishing.
- Primary source: *Girl with a Pearl Earring*, Johannes Vermeer, Mauritshuis 670. Main work: https://www.mauritshuis.nl/en/our-collection/artworks/670-girl-with-a-pearl-earring .
- Source image (public-domain photographic reproduction offered at Wikimedia Commons): https://commons.wikimedia.org/wiki/File:Johannes_Vermeer_-_Girl_with_a_Pearl_Earring_-_670_-_Mauritshuis.jpg ; check source rights for commercial use separately.
- Runtime: GitHub-hosted Ubuntu CPU; Python 3.11, OpenCV, NumPy, Pillow, FFmpeg. Compatible with supervision from Android browser—no PC or local GPU.
- Script may also accept `--source path` and `--mask path` to reproduce or manually refine output.
- Output: `01_ORIGINALE.jpg`, `02_MOMENTO_USCITA.jpg`, `03_POP_OUT_PARALLASSE_3D.jpg`, `04_PRIMA_DOPO.jpg`, `05_VERMEER_POP_OUT_V2_CAMERA_3D.mp4`, source/mask/manifest, uploaded to an isolated GitHub Actions artifact if the workflow finishes.

## Mechanism
1. Automatically download the documented, non-generative painting source or accept an authorized upload.
2. GrabCut human-guided source mask isolates only the original painted person; it is not an AI-generated figure.
3. Create a dark clean plate using source-region texture, with an expanded/feathered silhouette hole (prevents the duplicate/ghost in V1).
4. Assign a **curved but explicitly hypothetical** depth field to head, scarf, shoulder and earring and project its texture; differential movement under horizontal camera orbit.
5. Project the painting+scenic frame as a separate physical plane (perspective transform). The head and torso project forward and cross left/top frame edges, with a restrained shadow.
6. Export H.264 + AAC in 720×1280 at 24 fps for 8 seconds; original ambient music synthesized locally, no third-party audio.
7. Verify full decode, 0–7-second sample frames, direct file and ZIP before sending to user.

## Truthful boundary
The renderer does **not** infer the unseen sides of the face, the rear of the costume, real anatomy or a watertight character mesh. The 3D-related geometry is a **2.5D depth surface over pixels from the historical painting**, and the gallery and frame are artistic reconstructions. A dramatic look does not validate historical or dimensional authenticity. Artists must visually inspect hairline, eyes, hands, figure edges, frame occlusion, and contact shadows; automated checks are insufficient.

## Safe project integration
- This is **not** another 4x1 slot and does not alter Socrates/Klimt pilots, official V58 lock, V68 presets, official workflows, site or archives.
- Only after the owner visually accepts the effect, plan a reusable adapter with user-selectable subject, per-artwork mask/depth, optional verified free 3D backend, and V55 packing.
- No GPU purchase, Vidu credits, API spending, or social publishing without explicit user approval.
- For each artwork, first research the museum's actual painting scale and present/verified frame; do not mislabel the scenic frame as real.

## Local QA snapshot
- Test source: visually faithful original picture from Mauritshuis with provenance verified.
- Test local MP4: 8.000 s, 720×1280, 24 fps, H.264/AAC, complete decode **PASS**.
- Local video SHA-256: `b774dda5480bb3d8907a8704e6bd9c98a9fb39eb26005d8b11b59cc4095cbf13`.
- Frames at 0,1,2,3,4,5,6,7 s inspected as contact sheet; **artistically experimental**. V1 zoom failure recorded, real-world phone playback of V2 **not verified**.
- This local hash is NOT automatically the hash of any GitHub Actions rerender using a potentially different Commons JPEG. Each cloud run must be checked separately.
