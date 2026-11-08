# ArtVision 4×1 · The Triumph of Death · Cinema Museum V217 · Private technical review (2026-11-08)

Owner task: 6adca191603c8191a90d5190901cd034. Branch `main`. This checkpoint does **not** assert that a new 4×1 Museum slot has been accepted.

## New physical edit this cycle
- Work ID: `bruegel_triumph_death_1562_prado_p001393`; variant `cinema_museum`.
- **V217** 48.00s, 720×1280, 20fps, H264/AAC, 960 real frames.
- Actual local working-container output: `/mnt/data/triumph_v217/THE_TRIUMPH_OF_DEATH_CINEMA_MUSEUM_V217_ANDROID_REVIEW.mp4`
- MP4 bytes **14,851,833**, SHA256 **edc724783729262ded63e8c1a6ea55f97d0d01665bb025f19f5a9dcd3bc373cf**.
- ZIP: `THE_TRIUMPH_OF_DEATH_V217_ANDROID_REVIEW_PACKAGE.zip`, **16,068,597 bytes**, SHA256 **31599af6b25b07ad33b4a4aa39ac563f4f4f0394db6d4476db9b9fd579f0b5b9**. Includes MP4, cover, contact sheet, QA JSON, storyboard and source rights.
- Full FFmpeg H264/AAC decode PASS, 960-frame probe PASS, original V150 AAC bit-identical PASS, ZIP CRC and embedded MP4 hash PASS.
- These bytes are in the **ChatGPT working-container conversation attachment**, not assumed to exist in GitHub Releases, on the website, or in permanent private Library. An attempted private Library upload returned `container_session_unavailable` — do not claim permanent byte backup.

## Real sources
- Original painting *The Triumph of Death*, c.1562–1563, Prado P001393, **117 cm height × 162 cm width**.
- Authentic **2013 photograph of the exact framed painting**: Priscila Costa / Ministério da Cultura, **CC BY 2.0**, [source](https://commons.wikimedia.org/wiki/File:Pieter_Bruegel_der_Aeltere_-_Der_Triumph_des_Todes_-_mit_Rahmen.jpg); SHA256 `c7b99abad654ca86c1df05f51b14013cd877eb11b079fde71799636987a73517`. It proves the photographed frame and partial wall in 2013, **not** a historical-original frame nor a complete 2026 Prado room.
- Faithful PD source original painting: [Wikimedia](https://commons.wikimedia.org/wiki/File:Thetriumphofdeath.jpg); SHA256 `2cbaefc3961b999fc5a916db06dd96b3b95789789a795da83cc1d7947f3e1fbb`.
- Original Cinema Standard V150 SHA256 `c460fe7fa72ac29425de67eec40f986add502c42ec9e4166050c7ce107804138`, unchanged. Same original AAC soundtrack (ADTS SHA `ee095d8747f3e9aba2769817ec2abedb94f9748427ae96a9c334f58ddc23b2d5`). No TTS or paid APIs.

## Real newly directed shot / QA
- Full portrait opening using actual photographed frame; shot enters original clean artwork. Middle retains original V150 source-matched documentary painting cuts.
- Last segment **39.60–48.00 s** redesigned instead of previous faulty V215/V216 44s jump. Original frame 791 is the final banquet painting detail; V217 begins from homography-registered matching crop at frame 792 and performs **one uninterrupted 168-frame camera retreat** to photographed framed painting. No frame compositing falsely claimed to be original historical Prado installation.
- Original 2013 photographed wall is extended for social portrait display with a **neutrally composited wall**, metadata classification **`ricostruzione scenografica/non allestimento reale`**. This is NOT a real complete museum room; V118/V119 gallery approval not passed.
- Automatic seam MAD (8-bit) 791→792 **35.936**; later moving-camera steps (pixel MAD) may be higher due to source-image geometric zoom, so **human full-speed artistic review remains PENDING**. Intro 79→80 **1.284**. Source image-to-photo registration: 2,133 SIFT inliers; not equivalent to human artistic approval.
- Earlier V198, V215 and V216 are superseded review attempts and MUST NOT be counted as additional slots.

## Queue and restrictions
- Queue source `queue/artvision_owner_selected_ten_20261102.json`, reviewed on current `main`: **26/40 technical slots**; **0 newly approved slots**. V217 = one new physical review MP4, not a new approved Museum delivery. Dalí remains suspended.
- Human full-speed artistic sign-off: **PENDING**; commercial/territorial rights and frame/museum final clearance: **PENDING**; Gold `false`, published `false`.
- No website/social publishing, no GitHub Release, no paid API, no modification of any old master, no concurrent render dispatch, no new automation.
- Next executable step: full-speed review of V217 39.55s–48s and artistic suitability of the photographed/extended wall; if rejected, mark this candidate and move to another incomplete Museum slot without duplicating V217. For final slot count, first clear V118/V119 plus territorial rights. Separate backup of exact bytes is still needed.

## 2026-11-08 — Addendum: private Library backup RESOLVED
The initial container-path upload failed because the connector could not access the container session. A retry using the immutable exported-file references **succeeded**. Permanent private Library paths:
- MP4 `/ArtVision/Triumph_Death_V217/THE_TRIUMPH_OF_DEATH_CINEMA_MUSEUM_V217_ANDROID_REVIEW.mp4` — ID `libfile_125521293edc8191951b714231d5bb50`.
- ZIP `/ArtVision/Triumph_Death_V217/THE_TRIUMPH_OF_DEATH_V217_ANDROID_REVIEW_PACKAGE.zip` — ID `libfile_238380fc17d0819193847986c5969ba9`.
The **independently re-materialized private Library bytes** were verified again: MP4 SHA256 `edc724783729262ded63e8c1a6ea55f97d0d01665bb025f19f5a9dcd3bc373cf`, ZIP SHA256 `31599af6b25b07ad33b4a4aa39ac563f4f4f0394db6d4476db9b9fd579f0b5b9`; all-stream FFmpeg full decode, ZIP CRC and embedded MP4 SHA PASS. The storage issue is resolved; **Android playback in the user's own device is not independently tested**. This is still a private *review*, not an artistic/museum approved Gold or published film, and no slot increment has been recorded.
