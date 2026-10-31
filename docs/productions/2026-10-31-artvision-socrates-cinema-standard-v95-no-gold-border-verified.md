# ArtVision Socrate V95 — rimozione vera cornice residua nel finale (31/10/2026)

## Difetto osservato sul file reale V94
Nel fotogramma **32,5s** di `Socrate_Cinema_Standard_V94_PLATONE_FINALE_FULL_REVIEW.mp4`, il dipinto completo mostrava ancora **sottili linee dorate verticali** ai bordi sinistro e destro, residue della cornice digitale Museum della fonte V61. In Cinema Standard non deve esserci una cornice museale fittizia. Verifica sulla sorgente pittorica V94 (832×538): i tre pixel di colonna più esterni a destra sono classificati dorati nell'**88,9%** del campione, confermando il residuo. È un difetto nuovo concreto non risolto da V94.

## Correzione fisica V95 (revisione stesso slot, non quinto video)
- Nuovo file: **`Socrate_Cinema_Standard_V95_NO_MUSEUM_BORDER_REVIEW.mp4`**.
- **25.056.665 byte, SHA256 `95a6e75e92f8a25fd8ebbb4cdc31c0f7ea551343fe40b1c861ef908aea11b601`**.
- 35,041667 s, 720×1280, 24 fps, **841 frame H264**, audio AAC.
- **FFmpeg `-xerror` FULL DECODE PASS** su MP4 creato e **sul download di ritorno dalla Libreria**.
- **AAC bit-identico** a V94 e al master V59: demux ADTS SHA256 `80ff682ac731b0dd78fc4fa52413d2cb27747d49a3bc1fd64ab4850077145bc0`, 804.352 byte.
- Fonte visiva: ritaglio autentico del dipinto derivato da V61 e già conservato in V94. Tolti 6 px a sinistra, 8 a destra, 3 sopra e 5 sotto, per escludere la cornice e gli artefatti JPEG. La quota di pixel dorati nelle ultime 3 colonne della nuova sorgente scende a **16,4%** (residuo di colori propri dell'opera, non banda verticale).
- Ricomposta **solo la regia dei 30,00–35,04 s**, senza cambiare il movimento narrativo precedente, con sfondo sfocato ricavato dal medesimo dipinto e leggero zoom finale.
- **Proporzioni reali** dell'opera da Met 436105, dimensioni 129,5 × 196,2 cm: https://collectionapi.metmuseum.org/public/collection/v1/objects/436105 (`isPublicDomain:true`). Non è stato possibile scaricare il JPG originale ad alta risoluzione per indisponibilità rete del container: **la fonte V95 resta la JPEG compressa dal video V61**, non un nuovo master Met ad alta risoluzione.
- Il resto del video viene ricodificato tecnicamente H264 senza modifica di scene/copione/musica. SSIM su 8 frame campionati a t=0..29,5 s tra V94 e V95: **0,988–0,995**, coerente con stessa regia e lieve ricompressione; non è identità bit-per-bit video.
- Nessuna AI, TTS, Vidu, acquisto o spesa API.

## Archivio vero e QA
- Libreria privata: **`/ArtVision/Socrate/V95_CINEMA_STANDARD_BORDER_FIX/Socrate_Cinema_Standard_V95_NO_MUSEUM_BORDER_REVIEW.mp4`**.
- **Upload riuscito e DOWNLOAD DI RITORNO REALE**, 25.056.665 byte, **SHA256 identico**; FFmpeg full decode sul file riscaricato **PASS**.
- Salvati anche `SOCRATE_V95_QA.json`, `LEGGIMI_V95.md`, `revise_v95.py` nella stessa cartella. Confronto JPG disponibile nel container `/mnt/data/ARTVISION_QA_20261031/CONFRONTO_SOCRATE_V94_V95_FINALE.jpg`; upload Libreria di JPG/PNG ha risposto **403 trusted producer** e NON è verificato in Libreria. Non inventare file caricato.
- MP4 V94 originale, ZIP V94, ZIP Socrate 4×1 V93 e ZIP Klimt V92 **non sovrascritti**. V95 è **candidata** per lo stesso slot Cinema Standard, NON Gold V25.
- QA visiva campionata e decode macchina non equivalgono a visione integrale umana.

## Stato player / prossimo passo
- Nuovo controllo R2 `video-library-studio`: HTTP200, **0 oggetti** con prefix esatto V61, Socrate V94 e Klimt Cinema V92; stato plugin aggregato **409 MP4 / 250 import ChatGPT** non prova queste versioni. V95 non importato, **playback Android non verificato**.
- Import plugin `Video Library Studio Import` richiede fileParams realmente scelto dall'utente. Non inventarlo; nessuna pubblicazione o modifica Worker. Prima importare V61 già staged, poi revisioni selezionate; verificare R2 e playback veri.
- Non rifare pacchetti 4×1, non aprire sesta opera, non creare task aggiuntivi, non consumare API. La sola automazione ArtVision esistente può continuare con QA su difetti nuovi.
