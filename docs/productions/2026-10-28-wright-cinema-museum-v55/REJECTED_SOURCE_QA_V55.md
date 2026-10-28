# ArtVision Wright Cinema Museum V55 — independent visual rejection (28/10/2026)

**REJECTED_SOURCE_NOT_MUSEUM — do not release or count as a completed Cinema Museum variant.**

- GitHub Actions run [40779342914](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/40779342914) succeeded technically and produced H.264/AAC 1080×1920 53.1 s, MP4 SHA256 `21a8112cd95d2326221654cb49a2d22518f72aa69dd3abbb3677403518050800`. ffprobe, full decode and ZIP CRC passed.
- **Actual independent source inspection in ChatGPT:** extracted `ORIGINAL_REAL_GALLERY_PHOTO_AD_MESKENS_CC_BY_SA_4.jpg` from the complete source ZIP and visually examined it. The Commons 2019 Ad Meskens image is a **tight detail of the painted lecturer, cockatoo and adjacent faces**. It does **NOT** show the full painting, gilded frame, gallery wall or room.
- The generated 5–7 s and closing Museum scenes are a small rectangular *painting detail* floating in a dark matte. They do not meet the promised physical museum frame, room or scale. Technical gates did not detect this semantic failure. This is exactly why V44/V55 require separate artistic inspection.
- Therefore the first rendered video is a **rejected technical study**, not `rendered_needs_review` as a candidate Cinema Museum master, not an approved work, not imported, not published. **Do not use its package for site import or claim four variants.**
- Source claim correction: the 2019 photo by Ad Meskens is genuinely CC BY-SA 4.0 but it is a cropped detail. The workflow/source comments claiming the photo depicts a gilded frame were incorrect and must not be reused.
- Action: started a separate zero-credit photo source probe `.github/workflows/artvision-wright-museum-photo-probe-v55.yml` comparing full-frame photo candidates with clear Wikimedia Commons license evidence. A corrected new render may proceed only after a **real frame and gallery image is visually confirmed**, with rights and posts corrected for the actual author/source. Do not merely relabel the rejected MP4.
- Existing Wright V52B Cinema Standard SHA256 `ec4525c155334a02696bfa05d745005bea3084f178043c9eaf1dca6d7bfe29e2` remains untouched. Wright Cinema Museum remains `planned` in the queue. Critico variants remain blocked pending genuine Gacrux.
- No paid video APIs, social publication or private archive import.

## Observed defects (based on real images, not invented full-speed review)
1. **5–7 s:** supposed museum reveal shows a cropped lecturer rather than the authentic frame or painting at physical scale. Cause: source file name and metadata were trusted without inspecting pixels. Fix: image-level visual preflight before render.
2. **~50 s:** supposed museum exit returns to the same isolated crop in a dark matte. Cause: frame photo was never acquired. Fix: only use a source showing the whole original painting and its real frame.
3. **Gallery shot composition:** dark empty matte dominates screen while the painting detail occupies a small rectangle. Fix: recompose based on a real full framed photo and compare at smartphone size, preserving historical scale.

No `OPENING_REVIEW`, learning-loop success, or Gold Master claimed for this rejected hash.
