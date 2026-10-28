# ArtVision V55 — Independent QA and queue gate (2026-10-28, 17:13 Europe/Rome)

## What was actually checked

Re-opened the two previously delivered local candidate MP4s and their complete ZIPs. This run did **not** create a new MP4, claim artistic approval, or modify existing masters. Source paths were present in the active ChatGPT working container; these checks do not establish successful Android downloads.

| Variant | Exact SHA256 | ffprobe | Full FFmpeg -xerror decode | ZIP CRC and embedded MP4 hash |
| --- | --- | --- | --- | --- |
| Fabritius / The Goldfinch / Cinema Standard V55 | `537d7f8683bbac8791a8e629916ee206c845d41673eebd3a8dec1bee7575b1f2` | H264/AAC 1080×1920, 24fps, 43.6667s | PASS | PASS |
| Seurat / A Sunday on La Grande Jatte—1884 / Cinema Standard V55 | `fec7ec7d2c64460d3737f92eeca99fd0d521c775ab2dfda39502293dfa683789` | H264/AAC 1080×1920, 24fps, 51.917s | PASS | PASS |

The four social posts in each complete ZIP exist and are byte-distinct. This check does **not** certify their literary quality or the live site's persistence. Verified exact title and artist in sampled first frames of both MP4s. Examined frames extracted at 0.1, 1, 3, 5, 7, 12, 18, 24, 30, 38 and 45 seconds (45 is beyond the Goldfinch runtime); reviewed a contact sheet against the genuine source reproduction. This is **sampled visual inspection**, not normal-speed full audiovisual review. No `OPENING_REVIEW` or V54 learning-ledger record was fabricated.

## Concrete observed visual issues (not invented A/B improvements)

1. **Seurat, ~3–7s and ~24s:** a narrow, strongly colored band is visible at the bottom of the cropped frames. Comparison with the authentic source JPEG shows that this is Seurat's **real painted border**, not a repeated-pixel edge-stretch defect. Nevertheless it resembles the rejected striping effect on a phone. Next test: crop only the affected detail scenes within the inner painted area while preserving the monkey, foreground couple and pointillist texture. Do not strip the border from the intentionally dedicated border scene (~38–42s), which is legitimate.
2. **Seurat, ~45–52s:** whole painting is presented at small size inside black vertical background, potentially reducing impact on mobile. Compare a wider full-painting hold preserving the entire authentic composition, without stretching. Hypothesis only.
3. **Goldfinch, ~3–7s:** the full-bird composition remains nearly unchanged across sampled frames at 3/5/7s; may feel too static after the initial closeup. Next test: only adjust the timing of the existing genuine bird/chain reveal, avoiding invented motion or repetitive crops. Hypothesis only.

Do **not** start an unplanned corrective render until the official V13 four-brief/four-check preflight, one-variable experiment and source/rights gate are satisfied. Do not overwrite either original candidate. Current artistic state remains `rendered_needs_review`.

## Queue, next production and site

Compared V54 `queue/artvision_four_variants_s01_20261028.json` against V53 legacy `queue/artvision_dual_format_s01_20261028.json` and existing V55 reports. Wright Cinema Standard V52B, Goldfinch Cinema Standard V55, Seurat Cinema Standard V55, Goldfinch Museum V50 and Seurat Museum V51 are already registered; avoid duplicating. The Wright/Goldfinch/Seurat Critico variants still require a genuinely verified natural Google Gacrux voice; do not downgrade to Cinema. The next non-duplicative Cinema candidate in this queue is Turner's *The Fighting Temeraire* Standard, which needs a real locally obtained source image and a complete V13 preflight before rendering. National Gallery catalogue documents the oil painting as 90.7×121.6cm (NG524): https://www.nationalgallery.org.uk/paintings/catalogues/egerton-2000/the-fighting-temeraire . Commons provides a PD-Art reproduction: https://commons.wikimedia.org/wiki/File:Turner_-_The_Fighting_Temeraire.jpg . The image could be inspected online but could **not** be downloaded to the isolated local runtime in this cycle, so no legitimate new Turner render was started. Reference comparisons also included Fabritius and Seurat, which are already represented in the queue.

Video Library Studio connector returned only aggregate `videoCount=370` and `chatgptImports=211`, **not proof** that either exact SHA was imported. The importer requires an owner-selected ChatGPT file parameter, unavailable non-interactively here. No V25 release approval or live catalog/player/cover/4-post/ZIP verification was obtained. Both `archive_sync_pending`; no social publishing and no paid video API calls. The official `src/video_director_v13.py four-check` and `src/artvision_delivery_v55.py pack` were **not** re-executed in this cycle (the earlier complete ZIPs were independently revalidated). Do not claim otherwise.

**Status:** technical revalidation completed; artistic and archive gates pending. Next safe action: obtain the exact Turner source and execute the repository's official preflight before new rendering; separately seek actual audiovisual review and V25 release for existing candidates.
