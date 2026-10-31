# La Storia Rivive V145 — original Commons content fingerprints (31/10/2026)

## Defect and correction

V141 compared only `width × height` of the published Commons original. A different original upload at the **same page URL and same raster** would be silently classified as unchanged. V145 now requests the public `imageinfo.sha1` (40 hex characters) in the same metadata call. It records `live_original_sha1` for each of the seven known SD originals and compares against `commons_original_sha1` **only when an independently captured baseline is present**. A changed SHA1 becomes `ORIGINAL_CONTENT_CHANGED_REQUIRES_NEW_SOURCE_REVIEW`; a missing/malformed live fingerprint against a known baseline becomes `LIVE_FINGERPRINT_UNAVAILABLE` (fail-closed).

**Baseline captured from real Commons API:** [V145 live job #41219020616](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41219020616), [actual JSON artifact #13048549180](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41219020616/artifacts/13048549180). All seven Commons originals returned valid, distinct 40-hex SHA1 values and unchanged SD dimensions on 31/10/2026. The registry now records each original SHA1 with the run/artifact evidence URL. Subsequent runs compare live SHA1 to this **dated snapshot**, detect same-raster replacements, and fail closed on missing live fingerprint. A matching SHA1 proves only that the Commons-published original has the same content fingerprint as the captured snapshot, **not** that its underlying film is sharp, legally cleared, or suitable for 4+1. A metadata SHA1 is not the SHA-256 of the downloaded film, not a source authenticity guarantee, and never proves five camera shots, Italian rights, face quality or publishing permission.

The scheduled V101 workflow now retains the live JSON in its research artifact, so later review is possible. No I2I, Vidu POST, purchase, or publication is performed. ArtVision/WOW LAB/V98 unchanged.

## Verification

`python -m unittest discover -s tests -p 'test_storia_rivive_v141_live_sd_recheck.py' -v`

`python -m unittest discover -s tests -p 'test_storia_rivive_v121.py' -v`

The V109 PR workflow also runs the real metadata smoke check for a V145 PR. Compare the new live SHA1 values against the seven recorded originals and inspect the actual artifact. Never infer hashes from thumbnails or file names.
