# ArtVision 4×1 — Bruegel *The Fall of the Rebel Angels* — V212 e V213 (7 novembre 2026)

## Esito materiale, NON approvazione artistica
Sono stati prodotti **due MP4 realmente nuovi**, distinti dai precedenti V200/V202/V204/V205. Sono **provini Cinema Museum e Critico Museum** con una vera fotografia della sala 68 in cui appare esattamente l'opera incorniciata. Non sono master Gold, non sono pubblicati, non costituiscono **nuovi slot approvati**: la coda resta **26/40 tecnicamente registrati**, con giudizio artistico e diritti territoriali ancora pendenti.

### Cinema Museum V212 — reale, archivio privato con readback
- MP4: \`BRUEGEL_REBEL_ANGELS_CINEMA_MUSEUM_V212_REVIEW.mp4\`, 48.00 s H264/AAC 720×1280 20fps, **34,356,196 byte**, SHA256 \`14a75721e28183745b5d4bd93d048d89d3dbd7bbb9d5c55a7ef2d1e98045795d\`.
- ZIP: \`BRUEGEL_REBEL_V212_PACKAGE.zip\`, **42,667,268 byte**, SHA256 \`2b1fc7704ed92e883ac130f54a157a2544c9d0a2186125a52042a6a3707e3422\`.
- Esecuzione renderer CI: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/42412660940 . Job \`render\` PASS, upload artifact ID \`13589966914\` (ZIP caricabile da GitHub dopo accesso). Il job readback interno ha una regressione di nome chiave: interroga \`new_slots_counted\` mentre metadata usa \`new_completed_approved_slots\`; **il FAIL di questo job non corrisponde a MP4 corrotto**.
- Readback INDIPENDENTE, senza nuovo render, PASS: https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/42412831862 , rapporto artifact ID \`13590690438\`; SHA/size/MP4 decode video+audio/ZIP CRC/MP4 inside ZIP tutti PASS.
- Camera continua su fotografia reale e tela registrata con SIFT, **253 inliers, errore mediano 0.89 px**; massimo scarto medio tra frame adiacenti 23.194 (soglia automatic gate 32), ogni dettaglio dentro il piano pittorico, nessun taglio montato, **originale AAC Cinema Standard V153 bit-identico**.
- Libreria privato \`/ArtVision/BRUEGEL_REBEL_ANGELS_CINEMA_MUSEUM_V212_REVIEW.mp4\` id \`libfile_0dfe661d9de48191aefd65e37cfaba6f\`; ZIP id \`libfile_ee1a86cefc088191a75d85e4ca099dee\`.

### Critico Museum V213 — reale, archivio privato con readback
- MP4: \`BRUEGEL_REBEL_ANGELS_CRITICO_MUSEUM_V213_REVIEW.mp4\`, **115.80 s** H264/AAC 720×1280 20fps, **53,458,838 byte**, SHA256 \`05c1e0a15f7207a881b625230047e934e4e4261693189fc6b96c3aa240e6e23c\`.
- ZIP: \`BRUEGEL_REBEL_CRITICO_MUSEUM_V213_PACKAGE.zip\`, **65,963,928 byte**, SHA256 \`a0d2a48568f764c4f5432aae0a46631a5aaeee5e96deb8479ea4e3683078e3a1\`.
- Render locale diretto; asset: originale dipinto da V153 artifact \`13343701748\`, fotografia sala da V212, originale Critico Standard V144 artifact \`13309290632\`. Gli hash di art, stanza, Critico Standard e Gacrux WAV sono stati bloccati/controllati prima del render.
- **Voce Gacrux originale RIUTILIZZATA** WAV SHA256 \`e50f97bf6bf272bdda3a1b8577acf492f974d5c88d2b336d35cf976c5a814ade\`, AAC MP4 bit-identico al Critico Standard V144; nessuna nuova chiamata TTS.
- 18 frasi da cache ASR V144, 9 capitoli con soggetto ripreso come nella ricetta originale; camera continua nel vero quadro della vera sala, cornice fuori dai dettagli centrali, stesso luogo in apertura e ritorno.
- **AutoQA**: primo tentativo respinto a scarto 35.962; corretto in maniera reversibile anticipando i movimenti tra capitoli, secondo tentativo max 30.577 (limite 35), PASS. FFmpeg full decode video+audio, hash, WAV/AAC SHA e ZIP CRC PASS.
- Libreria privata \`/ArtVision/BRUEGEL_REBEL_ANGELS_CRITICO_MUSEUM_V213_REVIEW.mp4\` id \`libfile_320b7d93592481918a644cf02e246231\`; ZIP id \`libfile_a320f56247e48191b4d3779b5fb9363a\`.

### Provenienza e salvaguardie
- Opera originale: Pieter Bruegel il Vecchio, 1562, Royal Museums of Fine Arts of Belgium inv. 584, dimensioni **162 × 117 cm**. ART JPEG SHA256 \`09f675e7861da808ede4bc1f85573e97884fdbcc6c1d6cb482e3e449d58aace5\`.
- **Fotografia autentica dell'opera incorniciata e della sala**: FrDr, CC BY 4.0, https://commons.wikimedia.org/wiki/File:Koninklijke_Musea_voor_Schone_Kunsten_van_Belgi%C3%AB_44.jpg , SHA256 \`9992ac6ee8121af95c785fbdb1450dddbf56fbc24bef7eebef61c4440e51cfce\`. Non attesta che la sala sia rimasta identica nel 2026 o che la cornice risalga al 1562.
- Entrambi MP4 e ZIP sono stati caricati nella Libreria **e materializzati nuovamente nel container**, byte verificati singolarmente con SHA256, entrambi ZIP CRC PASS. Sono inoltre scaricabili come allegati nell'attuale conversazione ChatGPT; questi link sono di sessione e non vanno riportati come permanenti su GitHub.
- Controllo tavole di contatto effettuato; la **revisione artistica completa in riproduzione a velocità naturale, prova Android da utente e liberatoria territoriale commerciale restano PENDING**. Non affermare Gold o pubblicazione in loro assenza.
- Zero nuove API a pagamento, zero pubblicazione automatica, zero modifiche ai master verificati, Dalí sospeso. Non incrementare \`slots_delivered_this_selection\` per questi provini senza review V80/V118/V119 e decisione ufficiale.

### Prossimo ciclo
Non rigenerare V212/V213, che esistono realmente e sono archiviati. Prima QA artistico umano e diritti; nel frattempo continuare gli altri slot Museum indipendenti ancora vuoti: priorità nuova prova sorgenti esatte Simberg / *The Magic Circle* (PH02 porta centrale = limite geometrico) / Blake, nel rispetto della direttiva due tentativi e passa oltre. Non conteggiare preparazione o recupero come nuova produzione.
