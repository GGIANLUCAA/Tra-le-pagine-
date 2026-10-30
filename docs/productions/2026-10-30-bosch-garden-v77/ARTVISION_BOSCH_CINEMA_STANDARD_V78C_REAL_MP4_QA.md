# ArtVision Bosch — Cinema Standard V78C, real MP4 and scoped QA (30/10/2026)

**Actual fourth painting, one of four slots:** Bosch, *The Garden of Earthly Delights*, Museo del Prado inventory **P002823**. Only **Cinema Standard** is now physically rendered. The other **three Bosch slots remain unrendered**, 0/4 V25 Gold Master, 0 site imports verified. This report is a hash ledger, **NOT the video bytes**.

## Actual original MP4 — session-scoped, not in GitHub

- File: `BOSCH_CINEMA_STANDARD_V78C_REVIEW.mp4`
- **SHA256:** `3eb4a29c00b5d937f9385fef583a39dcccb754073328258db9f8b3b940acb2ba`
- **Bytes:** 17,461,112; **duration:** 41.65 s; H264/AAC 720×1280, 20 fps, vertical 9:16.
- ffprobe and **ffmpeg full decode PASS**; OpenCV 833 actual frames decoded; consecutive grayscale frame MAD at 90×160: peak **13.0025/255**, **0 frames above 35** (technical jump check only).
- Actual first frames 0.1/1/3/5/7 s extracted and visually checked; opening title and artist are legible. Full-speed human listening/creative approval **PENDING**.
- Music `Water Lily` original Kevin MacLeod MP3: SHA256 `b8c4f3b03a50af34c01a3f3b986a3d411f56a6c0c9a5b00807ccb5d83c74e8c6`; [official track CC BY 4.0](https://remote.incompetech.com/music/royalty-free/index.html?Search=Search&isrc=USUAN1400035). Music excerpt and fade; measured final audio mean **−21.8 dB**, max **−5.7 dB**. Exact attribution in each social post.
- Painting source: [Wikimedia Commons BoschFXD PD-Art](https://commons.wikimedia.org/wiki/File:The_Garden_of_Earthly_Delights_by_BoschFXD.jpg), **color-adjusted derivative**, 6800×3871, 12,130,063 bytes, SHA256 `830978840378c93991b16ed9219e1a78343c633aa8b62035fa65bf9f9ff26cd9`. Source acquired by [GitHub Actions run 41024818174](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41024818174), artifact **12963745760** (temporary, not persistent archive).
- 12 source-based views, no generative additions or fake Museum room, no video AI spend. Last frame is editorial slate, not a historical frame.

## Real packages, all ZIP CRC passed

| Artifact | Bytes | SHA256 | Content |
|---|---:|---|---|
| `BOSCH_CINEMA_STANDARD_V78C_ANDROID.zip` | 17,461,284 | `8b29958fc9a5b74a5f7f1e3e033d8217c8942c6153c4054fb5f8263c5d30914d` | MP4 only, internal MP4 SHA checked |
| `BOSCH_CINEMA_STANDARD_V78C_COMPLETO.zip` | 36,455,560 | `2fa9904fd758e22fad22b614a883cef3b9d5c6af6ccec02b32569064ae80e86d` | 24 members: MP4, cover, 4 original posts, 9 QA frames, contact sheet, source PD JPEG, original licensed music, rights/QA manifests, source renderer and audio revision command |

**Revisions are NOT fifth videos.** V78 (SHA `9ac4163d51a3c92fbd287d04fe415c71835ff3ce0fba634b8f343a5926360a03`) rejected for empty outro; V78B (SHA `3f44a3f60bf76004ab9b2a3a0735b263c6c31b1d8779cdf2274c7e5918b59374`) had music too quiet (−31.8 dB mean). V78C changes only the audio by +10 dB using FFmpeg stream-copy of V78B video, **identical H264 elementary stream SHA `09fb5b8c623e270219560f6a26e58f2ea5ca3a191aa907ba9ab35b8ed31e4bcd`**.

## Gates still blocking other three variants

1. Critico Standard and Critico Museum: **new exact shared Gacrux WAV and script** with cost/quota permission and ASR; old Bosch V22 is a visual/narration reference, NOT a new 4×1 slot. Do not synthesize or charge without consent.
2. Both Museum: Prado sources give incompatible dimension conventions (185.8×172.5 cm central panel + 76.5 cm wings vs 205.5×384.9 cm total), and **no work-specific authentic frame** has passed V80. A declared reconstruction is possible only within V80 and user-approved alternative. No false original frame or gallery claim.
3. Private Video Library/Dropbox import not verified; ChatGPT sandbox links expire. Do not infer permanent storage from this ledger.

**No social autopublishing, no V25 approval, no new automation, no other artwork or format touched.**
