# ArtVision source/production checkpoint — 2026-11-21 06:33 Europe/Rome

## Verified live against GitHub main
- Read current `data/archivio-generale/opere.json`: generated 2026-11-20T23:11:40Z; 96 works, 153 documented variants, 548 site entries, 11 unavailable. This is registry metadata, not proof of MP4 playback or current concurrent lock state.
- Read `queue/artvision_owner_selected_ten_20261102.json`, owner-selected 30, Caravaggio source dossier, V338 rules, prior 01:40 checkpoint, Shab-i Barat candidate dossier.
- The owner-selected 30 explicitly remain future research, not blanket render clearance. Older research-only restrictions are superseded by the owner's later 17 November conditional EXTRA production authorization, but source, rights, soundtrack, duplicate and lock gates remain mandatory.
- Shab-i Barat, Met accession 30.95.174.21, remains NOT READY: no exact photo bytes/pixel/hash, music recording or concurrency verification.
- New diagnostic: independent HTTPS attempts from this execution container to api.artic.edu, collectionapi.metmuseum.org and www.nga.gov all failed DNS resolution. This demonstrates a general outbound DNS limitation in this runtime, not evidence that the Met alone is down. Do not keep retrying the same failed source.
- V338 requires individual editorial pacing rather than the previous fixed twelve-shot pattern.

## Decision and truthful accounting
No new MP4 dispatched or completed; 0 new works. No TECH PASS, ART REVIEW PASS, downloadable artifact, verified Library readback or publication claim. No changes to queue, masters, schedules, workflows or existing automations; no expense.

## Distinct next viable strategy
Use an existing authorized GitHub Action runner or already-preserved GitHub artifact with provenance and verified image/music bytes, not this DNS-blocked container. Before any dispatch inspect latest run, queue, object identity, locks and existing output. If no safe slot, switch to a different object with already accessible CC0 image bytes and licensed V330 soundtrack; do not label it READY on metadata alone. For any new production preserve MP4, Android ZIP, cover, socials, full FFmpeg decode, SHA/CRC, license proof and private artifact readback. No automatic publication.
