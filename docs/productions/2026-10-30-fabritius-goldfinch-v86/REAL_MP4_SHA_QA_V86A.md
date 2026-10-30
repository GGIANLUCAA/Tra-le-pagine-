# Fabritius sixth pilot — real video V86/V86A, 30 October 2026

## Actual successful rendering (not a simulated dossier)
- GitHub Actions **run 41045497074 SUCCESS**, original physical artifact **12972163106**.
- V86 MP4 SHA256 `a20e589ba267df66041d525539732a5cee06ae07e969993a9cb0b05f7d9eb0e8`, 6,794,807 bytes, **44.000 s H264/AAC 720×1280 20fps**.
- 880 frames, continuous in/out of an **actual photographic frame of this exact painting**, V57 max grayscale frame MAD 4.30125/255, no frames over 35; whole MP4 decode PASS; independent ZIP CRC and byte-identical embedded MP4 PASS.
- Real photographic source 2017 **Sailko**, original Commons CC BY 3.0, SHA256 `f66b36f7a80e83d6ec378e97cf4d5126c288750ba2e584c29f304f59f421597b`; painting Mauritshuis accession **605**, panel **33.5×22.8 cm**. Background is an explicitly **digitally treated extension of the SAME photograph**, not a documentary Mauritshuis room.
- Kevin MacLeod **Water Lily**, licensed recording CC BY 4.0, SHA256 `b8c4f3b03a50af34c01a3f3b986a3d411f56a6c0c9a5b00807ccb5d83c74e8c6`. Four platform posts attribute both authors.
- Actions V86 original ZIP Android SHA `4135fb4d1540791a46ba2088e35aaf49e2f931b74f7280a1483018eb97964003`, full ZIP SHA `7358f66d1563ee5395700cbad7dbf791849fa2b2745f53adf103076f97fd080e`.

## Measured audio correction V86A — same Museum slot, NOT another film
- Original V86 measured via ffmpeg volumedetect: **mean −29.6 dB, peak −13.4 dB**; low for Android.
- In ChatGPT runtime, corrected AAC with volume ×2.2, `-c:v copy`, same original H264 stream SHA `4e68c121743e764c71075c6c6c7355c9bb133200d78f9fde8772c5d368108912` (bit-identical before and after).
- Corrected V86A physical MP4 SHA256 **`bc28663de3cd764eee0e8875697d8b596d80ffe5f4462aa39ad50c68326829db`**, **6,969,978 bytes**; ffmpeg complete decode PASS; corrected audio mean **−22.8 dB**, peak **−6.6 dB** without clipping.
- V86A ChatGPT-only Android ZIP: 6,972,962 bytes SHA `fd48a000255ea03aa2cd77ccafc519cd787cc12cd37aa331a23586720afbda2f`, full ZIP 17,485,971 bytes SHA `9b40c1686d31c32f420c8be6f894603038068f8832b5bf7e200d0f0c7f68c7b2`; both CRC+embedded video identity PASS.
- **Persistence:** V86 raw artifact is stored on GitHub Actions for its retention window. V86A remux MP4 and ZIP reside in this ChatGPT conversation runtime only; **do not claim V86A uploaded to GitHub or private site**.
- Script in this PR now incorporates the measured ×2.2 relative volume adjustment for **future reproducibility**; it has not been rerun after the change to avoid needless visual rendering.

## Authorization, preservation, honest status
- User explicitly requested a new ArtVision video and authorized proceeding: scoped sixth pilot `fabritius_goldfinch_1654`; all prior five 4×1 masters unchanged. An original Fabritius Cinema Standard V55 and original Cinema Museum V50 remain as historical variants; V86/V86A are revisions of the **same Cinema Museum slot**, **not fifth slot**.
- Two new Critico MP4s **not created**: one true shared Google Gacrux WAV/cost verification remains blocked. No TTS call, no paid AI video, no social auto-post or private archive upload.
- **0 V25 approvals**; sampled frames manually viewed for V86/V86A video only, no full human-speed independent review.
- Queue on main is intentionally unchanged until reliable delivery/approval; PR is **DRAFT**.
