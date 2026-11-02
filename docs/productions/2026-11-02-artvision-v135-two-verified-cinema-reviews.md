# ArtVision V135 — two real reviewed MP4 files, no Gold or publishing (2026-11-02)

## Hugo Simberg — The Garden of Death (1896), Ateneum A II 968:16

- V134 first Cinema slot, 48.000 s, H.264/AAC 720×1280 20fps.
- **Actual MP4** `SIMBERG_THE_GARDEN_OF_DEATH_CINEMA_V134_REVIEW.mp4`: **5,123,709 bytes**, SHA256 `2ec7e57ac37c521c2d8e224ed026d651f44a201790ae55f02e902c771d891152`.
- Actual GitHub Actions run **41535956792** SUCCESS; actual artifact **13183352784**, 17,189,823-byte outer archive, downloaded to current execution environment. Run URL: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41535956792
- Artifact ZIP CRC PASS, actual MP4 SHA readback matches manifest, **local full FFmpeg decode PASS**; source JPG **4001×3609**, SHA256 `514bf455d7cdc3543e3ee8ff49f206370ef34121c72e49e04353e3e902f530a5`.
- Full inner ZIP **11,546,669 bytes**, SHA256 `e9d380129488d9edff95e901291a87d95db4d1e00d3ca8fdb7d9adde610acf32`, ZIP CRC PASS; includes MP4, cover, contact sheet, QA, rights, unpublished social draft, original source JPG and original synthesized score WAV.
- Public-facing cover verified visually: title, author, year and museum only; no project name, no technical variant label. Original ambient soundtrack generated without third-party samples or paid API calls.
- Source: https://commons.wikimedia.org/wiki/File:Hugo_Simberg_-_The_Garden_of_Death_-_Google_Art_Project.jpg — Commons PD-Art/PDM; institution collection rights independently referenced. Publication territory-specific clearance not certified.
- **Remaining three slots**: Critico Standard, Critico Museum (same verified voice) and Cinema Museum. No unverified TTS, no fabricated museum. **NOT GOLD, NOT PUBLISHED, NOT SITE PLAYBACK-VERIFIED.** GitHub artifact retention currently expires 2026-12-02.

## Pieter Bruegel the Elder — The Fall of the Rebel Angels (1562), inventory 584

- **Proven new defect in previous V133**: both public title-card intervals and the JPEG cover showed forbidden footer **ARTVISION · CINEMA STANDARD**, despite the owner's explicit no-project/no-Standard rule. Verified by inspecting the actual V133 MP4 and JPEG, not inferred.
- **V135 is a non-destructive revision of the SAME Cinema slot**: title-card footer corrected only at video frames 0–49 (0–2.45 s) and 890–959 (44.5–47.95 s), 20fps; other image frames unchanged in editorial composition, no new AI or API.
- Actual corrected MP4 `BRUEGEL_FALL_REBEL_ANGELS_CINEMA_STANDARD_V135_CLEAN_PUBLIC_TITLE_REVIEW.mp4`: **19,883,963 bytes**, SHA256 `346c361919da8cfa652a8f451d2a9879a384f870cdbf2d0a936f290f996e92f5`; H.264/AAC 720×1280, 48.000 s, **full FFmpeg decode PASS**.
- Original V133 MP4 SHA `744ba3e924df222cde88558d42a1c454e743f3b9f673c6addb7213f497653078` retained unchanged; **AAC demux ADTS SHA bit-identical** V133/V135 `672f0cccfc59ce8dda31c8e2602d62553d20b95405dab856158d044bc89cd936`.
- Corrected cover JPG SHA `49366ee1570e762d1c3e3c45c2d23daadcd8c6934e6a778c48e33f708255301c`. Public social draft removed project hashtag and technical headings; unpublished.
- V135 review ZIP **37,172,085 bytes**, SHA256 `de5bce5a684945898eb8ffdfd61f825ce5156445d9bcb8b536a1e4af14e700a2`, 10 members, CRC PASS, with MP4, cover, source artwork, original licensed music, credits, social draft, QA and source-code reference.
- Music `Evening of Chaos` Kevin MacLeod CC BY 4.0, attribution required. Image Commons PD-Art/PDM; museum/territorial rights review pending. **Not Gold, not published, not site playback verified.** This V135 copy exists in current conversation sandbox; no durable private Library upload was claimed because prior quota error remains.

## Production controls

- The prior V134 GitHub run **41523878356** FAILED before rendering because `ffprobe` was unavailable on the runner. No paid calls or MP4 were made in that failed run. The renderer and workflow were corrected; one retry succeeded.
- Exactly one new verified Simberg Cinema slot, one corrected Bruegel Cinema slot (no slot increment), no duplicate owner automations, no parallel ArtVision renders, no Vidu/Gacrux calls or expenses, no social posting.
- 4×1 completion for these works **still pending**. Automated QA does not replace human artistic review. Museum rooms and frames require separately verified provenance and physical scale. No claim that site/Android playback works.
