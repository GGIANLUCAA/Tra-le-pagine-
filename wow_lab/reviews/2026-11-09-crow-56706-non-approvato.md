# WOW LAB 2026-11-09 · Crow Resting on Wood Trunk · NON APPROVATO

Isolated evaluation only. The MP4 preview was rendered locally with free CPU software and kept **out of all social channels and GitHub releases** because artistic QA failed. The associated source-code and artifacts are included in the local review kit, not committed to the project or merged into main.

## Provenance and rights
- Work: *Crow Resting on Wood Trunk*, Kawanabe Kyōsai; The Metropolitan Museum of Art, object **56706**
- Source: https://www.metmuseum.org/art/collection/search/56706
- Original source: https://images.metmuseum.org/CRDImages/as/original/DP124566.jpg
- Met API public-domain flag: true. Licence: Met Open Access CC0.
- Source SHA-256: `46b1602520d5e7adc2f74de2a9f2cba8b2bd084bd829a8f4d9ed97aa6d96177e`
- No external generation API, Vidu, credits, subscriptions, GPU bills, or social publication.

## Preflight and quality review
- Checked public WOW-LAB releases: 7 previously known prereleases; current new subject 56706 absent.
- Latest previous `wow_lab` MP4 was a Dürer rhinoceros **technical preview**, not an approved release.
- GitHub Actions in-progress check: none when this work began.
- Original high-resolution mask inspected at 2785 × 3882 pixels, including beak, eye, head, wing outline, both feet, and tail.
- Original paper was reconstructed separately; no fabricated animal anatomy or wing-flapping imposed.
- Vertical preview: 720 × 1280, 24 fps, duration 12.5 seconds, H.264 with AAC original synthetic soundtrack.
- Independent FFprobe and full FFmpeg decode: technical pass. Android-ready video bytes: 733163.
- MP4 SHA-256: `09d121db41ed3c70ffff1b947db274a57e74a6c955ece9733ef007bd6371c1b3`.
- ZIP CRC validated with 16 files; includes source, mask, clean-plate audit, cover, decoded frames, original audio, rights and draft social copy.

## Artistic verdict: NOT APPROVED
The subject separates from the source print and moves on an independent layer with cast shadow, focus variation and original audio, **but still appears too much like a flat cutout**. The feet appear to float when separated from the paper and the reconstructed fill behind the crow is smoother than the authentic surrounding pigment. This is not convincingly volumetric or photorealistic. It must **not** be labelled a finished WOW effect, used as a master, or published as a social video.

## Root causes and next corrective direction
1. **Root cause:** body translation/scaling without articulated depth. **Correction:** choose a single subject permitting trustworthy multi-plane decomposition and independent pose motion; reject static flat actor-only zoom.
2. **Root cause:** full-body removal exposes missing historical paper and branch marks. **Correction:** choose simpler clean backgrounds or construct a physically plausible clean plate and inspect at output size and full resolution.
3. **Root cause:** light/shadows do not replace true depth. **Correction:** require visible occlusion and credible foreground/background separation, not just a dark duplicate shadow.
4. **Quality gate:** inspect opening/intermediate/climax/end frames, paper holes, eye, beak, feet and tail at 100% output resolution before approval. No fragile multi-flower extractions.
5. **Delivery gate:** a public `wow-lab-*` release with verified Android MP4 and ZIP links is allowed only after artistic approval. A local test download alone is insufficient.

## Isolation and costs
Branch `experiment/wow-lab-crow-56706-qareview-20261109`, file `wow_lab/reviews/2026-11-09-crow-56706-non-approvato.md` only. Do not merge into `main`. Existing guards `no_paid_services=true`, `no_vidu=true`, `no_social_publish=true`, `production_ready=false` remain unchanged. Do not alter other series, official rules, tasks, core archives or site.
