# ARTVISION · Bruegel, The Fall of the Rebel Angels · Critico Museum V214 (7 novembre 2026)

## Scopo
Correggere V213, che era stato **respinto artisticamente** dopo la revisione campionata del 07/11 perché nel capitolo 1 (16.26–29.06s) e nell'ultimo capitolo (98.04–109.40s) non si vedeva l'intero quadro quando il narratore lo descriveva. V214 è una **revisione della stessa variante**; non crea un nuovo slot, non modifica i master già verificati, non è Gold, non è pubblicata.

## Consegnato: vero MP4 nuovo per revisione
- File: `BRUEGEL_REBEL_ANGELS_CRITICO_MUSEUM_V214_REVIEW.mp4`
- MP4 SHA-256: `ae43dd4d34b1d38e3f7de6d97d734a2523d0b5c7237a50a8b4c12a2ff8da5e57`
- Dimensione: **39,741,023 byte**; 115.80s, 2316 frame, 20fps, 720x1280, H.264/AAC.
- ZIP: `BRUEGEL_REBEL_CRITICO_MUSEUM_V214_PACKAGE.zip`
- ZIP SHA-256: `9368d6122badbbeb3f2211fa9531a6c697df8ef333b8261fc90d67f8dfc7fbbe`
- ZIP dimensione: **45,529,608 byte**.
- V214 `QA.json`, preview, contact sheet, credits, WAV Gacrux sono nello ZIP; l'originale script completo `artvision_v214_renderer.py` va preservato separatamente come artifact di lavorazione.
- **Full FFmpeg decoding** di tutti gli stream PASS **due volte**, prima della copia e dopo readback dalla Libreria; SHA MP4/ZIP identici; ZIP CRC e MP4 embedded SHA PASS.

## QA regia e montaggio
- **Corretti difetti A/B V213:** quadro 100% nell'inquadratura per i segmenti testati di entrambi i capitoli panoramici: campioni e coverage automatico continuo del capitolo 1 16.5–27.2s e capitolo 8 98.2–108.5s, ognuno **1.0** (non semplici foto ferme invece del video).
- I capitoli di dettaglio 2–7 mantengono la stessa immagine autentica, la camera unica e il focus narrativo dell'originale V144. Il campionamento dei fotogrammi mostra Michele, cielo, creature, fauci e farfalla alle rispettive frasi.
- L'ingresso e il ritorno sono nella fotografia originale del museo; durante la narrazione resta in campo **solo il dipinto**, senza cornice. Per mostrare un dipinto orizzontale intero in verticale, si usa un **fondale neutro morbido ricavato dai colori dell'opera**, senza fingere che sia una sala fisica o un'installazione storica. Cambia solo quando il piano pittorico riempie già tutto il quadro.
- Automatic pixel-cut check: massimo delta frame consecutivi **31.583** sui frame raw ridotti (limite 35); verifica indipendente del MP4 decodificato **33.312**. Il raccordo verso il dettaglio centrale intorno a **29.9s** resta relativamente rapido ed è punto di attenzione in full-speed QA.
- L'integrità tecnica e il sampled visual check **NON sostituiscono** la revisione artistica completa in riproduzione normale. **Artistico finale: PENDING**, **Gold: false**, **published: false**, **queue approved slot increment: 0**.

## Fonti, audio, diritti
- Pieter Bruegel il Vecchio, *The Fall of the Rebel Angels* (1562), Royal Museums of Fine Arts of Belgium inv 584, dimensioni **162 × 117 cm**. Artwork: `09f675e7861da808ede4bc1f85573e97884fdbcc6c1d6cb482e3e449d58aace5`.
- Fotografia **realmente effettuata davanti a questo dipinto in sala** FrDr CC BY 4.0, originale SHA `9992ac6ee8121af95c785fbdb1450dddbf56fbc24bef7eebef61c4440e51cfce`, fonte https://commons.wikimedia.org/wiki/File:Koninklijke_Musea_voor_Schone_Kunsten_van_Belgi%C3%AB_44.jpg. NON prova che l'allestimento sia quello attuale nel 2026 o che la cornice risalga al 1562.
- Critico Standard V144 originale SHA MP4 `83aad1da82a091de42aa19ca6bd532a0e2a2b21c27f4c4c34eac5e53c8799f39`. Voce Gacrux WAV originale `e50f97bf6bf272bdda3a1b8577acf492f974d5c88d2b336d35cf976c5a814ade`, **stesso AAC esatto del V144**; nessun TTS nuovo, nessuna spesa.
- Diritti territoriali e clearance per rilascio commerciale **PENDING**. Niente Gold automatico, pubblicazione, modifica di file verificati né chiamate a servizi a pagamento.

## Archive persistente verificato, non link di download pubblici
- MP4 Library: `/ArtVision/BRUEGEL_REBEL_ANGELS_CRITICO_MUSEUM_V214_REVIEW.mp4`; `libfile_89ccb27485408191878788b69df8db69`.
- ZIP Library: `/ArtVision/BRUEGEL_REBEL_CRITICO_MUSEUM_V214_PACKAGE.zip`; `libfile_0a568ca4803481918468365c9ae024cd`.
- Report QA Library: `libfile_cdb1ccabdcd4819198017baf657045e4`. Contact sheet Library: `libfile_29974ebe0b8c8191b70db8b88a3307ac`.
- Script V214 riproducibile nella Libreria privata: `/ArtVision/artvision_v214_renderer.py`, id `libfile_b6e3a9dc9a7481918695e85e90ea9f52`, SHA256 `cc491a48512ee06a17c58ac7935ff5bb96955b279bdc39b3777cb8921d9af39f`; richiede gli artifact originali, SHA locked e percorso di lavoro locale; **non** è un renderer pronto all'uso su qualsiasi runner senza ripristinare quelle sorgenti.
- **Readback indipendente:** materializzati MP4 e ZIP dalla Libreria nel container, entrambi SHA-256 coincidevano; ZIP CRC e FFmpeg full decode nuovamente PASS. I link `sandbox:/mnt/data` sono limitati a questa conversazione e non vanno documentati come URL pubblici permanenti.

## Coda e prossimi passi
- Coda owner ancora **26/40**. Le varianti V212 Cinema Museum e V214 Critico Museum sono vere produzioni tecniche distinte ma artisticamente non finali; V214 sostituisce il precedente **V213 non approvato** come provino Critico Museum.
- Per finalizzare: controllo full-speed su schermo verticale e controllo mirato del raccordo intorno a 29.9 s, verifica autorizzazioni di riuso commerciale e attribuzione foto; solo allora Gold/approvazione owner come previsto.
- Nel ciclo successivo NON rifare V212/V214 come nuovi slot. Passare a Simberg, Magic Circle o Blake indipendenti, con regola anti-blocco due tentativi e selezione dalla queue corrente. Dalí rimane sospeso.
