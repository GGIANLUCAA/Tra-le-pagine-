# ArtVision V117 — completare 8 Critico finora bloccati (4 opere storiche, mantenere Cinema)

## Autorizzazione / significato «video mancanti»
Il 1 novembre 2026 utente: «Sì mi soddisfa per adesso procedi con i video mancanti» a seguito della consegna dei 16 MP4 V116 (4 opere x4). Il feedback **approva provvisoriamente V116**, NON è Gold V25 formale. Indagine su `queue/artvision_four_variants_s01_20261028.json`: tutte le ultime 16 produzioni V116 sono realmente complete. Mancavano invece le coppie Critico (blocked) in quattro gruppi STORICI:
- Carel Fabritius — *The Goldfinch*, Mauritshuis 605
- Georges Seurat — *A Sunday on La Grande Jatte — 1884*, Art Institute of Chicago 1926.224
- J. M. W. Turner — *The Fighting Temeraire*, National Gallery NG524
- Winslow Homer — *The Gulf Stream*, Met 11122 / 06.1234

Per ognuno i due Cinema sono già renderizzati; **non ricrearli, non sovrascriverli, non spendere crediti video AI**.

### Workflow e codice
One shot GitHub Actions: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41351647619
- Workflow `.github/workflows/artvision-missing-critico-v117.yml`
- Source `src/artvision_missing_critico_v117.py`
- Ricette `modules/artvision_critico/production_series/2026_11_01_missing_critico_v117/*.json`
- Richiesta trigger `requests/artvision/missing-eight-critico-v117-20261101.json`
- Serializzazione `max-parallel:1`, 4 jobs x 2 new real MP4 (solo Critico Standard + Critico Museum), one Gacrux WAV per painting, same AAC bit-identical across pair. Google key via GitHub secret `GEMINI_API_KEY2` owner-attested Free/no billing, actual billing not verified independently. Never retry voice call if prior result uncertain.

### Consegna completa verificata Fabritius — 2/8
Run job first succeeded. GitHub artifact **13101194533**: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41351647619/artifacts/13101194533
- MP4 Standard: `FABRITIUS_GOLDFINCH_CRITICO_STANDARD_V117_REVIEW.mp4`, **11,856,857 bytes**, 99.52 sec, SHA256 `d1bb19d660975f06df33e9c9e44a3991c7eb0817b81573ba2cfcbb9d74e7fcde`.
- MP4 Museum: `FABRITIUS_GOLDFINCH_CRITICO_MUSEUM_V117_REVIEW.mp4`, **12,865,992 bytes**, 99.52 sec, SHA256 `b0402f864e3f5439072aaab588d4a62328faf9db302d26fc0ef9142ef7182512`.
- Source authentic Fabritius Mauritshuis 605 Commons 3930×6000, SHA `b3c68e063addcb1cb4b49fb58b240750084b74cfb5957d91afa4db688f55830c`.
- ONE shared Gacrux WAV SHA `f94cf545615c204fb5c3ba813c9189386073cac3d140b65c05df0ca82b833d79`, same AAC ADTS SHA `7a5630505b3d6da889fb1addf01213067411c794c42684704ea381dc7506c80f`.
- Real artifact physically downloaded and extracted in the current conversation's container; both MP4 SHA exactly matched QA, **full FFmpeg -xerror decode PASS**, `FABRITIUS_GOLDFINCH_2_CRITICO_ANDROID_V117.zip` CRC PASS, 3 members.
- Verified user-facing sandbox path current session `/mnt/data/ARTVISION_V117_FABRITIUS_2_CRITICO/FABRITIUS_GOLDFINCH_2_CRITICO_ANDROID_V117.zip`; make sure container path exists before ever reusing a sandbox link in another session. Contact sheet of 9 actual museum frames inspected. Digital gallery != real Mauritshuis.
- Updated GitHub queue: both Fabritius Critico = `rendered_needs_review`, preserve Cinema. Gold V25 = no.

### Remaining jobs state at writing this report (not promises)
**Seurat**: job in progress at “Single natural Italian Gacrux voice, identical AAC in BOTH actual MP4”; source/PD and cards preflight passed; no MP4 artifact yet available, so cannot honestly claim completed.
**Turner**: queued
**Homer**: queued

The remote GitHub workflow may continue independently of this chat. Do not claim delivery until downloadable artifact, SHA/ZIP CRC/full FFmpeg readback PASS. If a voice attempt is uncertain, do not rerun paid/voice request; first inspect GitHub logs/artifacts to recover WAV. Do not start a duplicate ArtVision V117 workflow while this one is active. Original V114 16 and V116 16 MP4 untouched. Old queue groups not overwritten. No social autopublishing. Existing ChatGPT Library was full in V113; no permanent Library backup claimed. GH artifact retention 30 days only.

Important: user asked video, never offer a generated still image as a substitute. Before next action inspect job/run status from latest real GitHub API.
