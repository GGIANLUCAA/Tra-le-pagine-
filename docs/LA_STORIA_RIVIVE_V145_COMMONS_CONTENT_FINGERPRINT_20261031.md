# La Storia Rivive V145 — original Commons content fingerprints (31/10/2026)

## Defect and correction

V141 compared only `width × height` of the published Commons original. A different original upload at the **same page URL and same raster** would be silently classified as unchanged. V145 now requests the public `imageinfo.sha1` (40 hex characters) in the same metadata call. It records `live_original_sha1` for each of the seven known SD originals and compares against `commons_original_sha1` **only when an independently captured baseline is present**. A changed SHA1 becomes `ORIGINAL_CONTENT_CHANGED_REQUIRES_NEW_SOURCE_REVIEW`; a missing/malformed live fingerprint against a known baseline becomes `LIVE_FINGERPRINT_UNAVAILABLE` (fail-closed).

**Current limitation:** the V140 snapshot has dimensions but **no original SHA1 baseline**. V145 therefore reports `BASELINE_NOT_RECORDED`, `same_raster_original_bytes_verified=false`, and does not claim that identical dimensions mean identical bytes. The PR-scoped free live Commons job creates an artifact with the actual fingerprints for a later reviewed baseline. A metadata SHA1 is not the SHA-256 of the downloaded film, not a source authenticity guarantee, and never proves five camera shots, Italian rights, face quality or publishing permission.

The scheduled V101 workflow now retains the live JSON in its research artifact, so later review is possible. No I2I, Vidu POST, purchase, or publication is performed. ArtVision/WOW LAB/V98 unchanged.

## Verification

`python -m unittest discover -s tests -p 'test_storia_rivive_v141_live_sd_recheck.py' -v`

`python -m unittest discover -s tests -p 'test_storia_rivive_v121.py' -v`

The V109 PR workflow also runs the real metadata smoke check for a V145 PR. Observe its logs/artifact before recording any SHA1 baseline. Do not add fingerprints from memory or from thumbnails.
