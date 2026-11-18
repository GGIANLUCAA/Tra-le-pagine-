# ArtVision · controllo anti-duplicati — 18 novembre 2026, 18:35 CET

Stato: **AUDIT PARZIALE; NESSUN NUOVO RENDER AVVIATO**. Questo file non certifica un video finito.

## Evidenze lette su main
- `data/archivio-generale/opere.json` generato 2026-11-18 14:47:59 UTC: 95 opere, 153 slot documentati, 127 non documentati, 542 elementi sito, 11 non disponibili. Un censimento non prova che i singoli MP4 siano scaricabili.
- `queue/artvision_owner_30_render_checkpoint_20261117_dadd_cinema_museum.json`: Dadd, *The Fairy Feller's Master-Stroke*, Cinema Museum già realizzato, SHA256 HD `20ea9f88a3dc0e0cfa0fd2fb0eca77bf1d5cafc4297b4aa71a5dc8820f45b412`; review e diritti pendenti; non rigenerare.
- `queue/artvision_owner_30_render_checkpoint_20261117_sadko_cinema_museum.json`: Repin, *Sadko*, Cinema Museum già realizzato, SHA256 HD `c099bae3800db7c2cc07f1a5d6b5932996d4450b4742a36c16e81675cf26ccca`; review e diritti pendenti; non rigenerare.
- `research/artvision_rare_cc0_video_candidates_20261115.json`: Bierstadt *The Last of the Buffalo* già documentato come candidato; checkpoint successivo lo registra già prodotto, quindi non è uno slot nuovo.
- GitHub Actions ultimi run visibili: 44357309077 WOW LAB failure (2026-11-18 17:19 UTC); 44357441122 Video Library Automatic Import skipped; 44328348077 Archivio Generale success. Non attribuire questi run a produzione Cinema completata.

## Gate e handoff
Non è stato identificato in questa verifica uno slot non duplicato con asset originale in bytes/pixel/SHA, licenza commerciale specifica e musica verificata simultaneamente. Non dispatchare alla cieca: rischio doppioni e licenze. La verifica di tutti i 114 file queue e di tutti gli artifact non è stata completata. Non sono stati eseguiti download binari, FFmpeg, test Android o readback Library in questo ciclo.

**Risultato:** 0 nuovi MP4, 0 ZIP, 0 pubblicazioni, 0 spese. Stato: RESEARCH_ONLY / NOT_READY. Prossima azione: esaminare checkpoint rimanenti e selezionare uno slot distinto prima di avviare il renderer esistente, senza cambiare workflow o schedule.
