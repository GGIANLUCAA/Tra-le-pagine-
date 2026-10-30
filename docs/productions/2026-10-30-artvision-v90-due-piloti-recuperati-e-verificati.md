# ArtVision V90 — Due pacchetti 4×1 recuperati, QA dei byte dal backup (30 ottobre 2026)

## Scopo e risultato
Controllo realizzato in questa sessione usando `files.list` e `files.materialize` per recuperare VERI MP4/ZIP da Libreria privata e dalla cartella Dropbox collegata. Le vecchie sessioni `/mnt/data` non sono state trattate come persistenti. Non sono stati consumati crediti API/Vidu, rigenerati audio/video né avviate nuove opere.

**Risultato:** recuperati e decodificati i **quattro originali Socrate** e le **quattro varianti Klimt**: 8 MP4 distinti; verificati due ZIP con CRC PASS, ffprobe + ffmpeg FULL-DECODE PASS per tutti gli otto file e pari AAC dei due critici per ogni opera. Un nono MP4, revisione separata Socrate Museum V89R1, è stato anch'esso recuperato, verificato e decodificato. Non equivalgono ad approvazione artistica V25 o test player Android/sito.

## Socrate — backup privato Libreria
- Path Libreria: `/ArtVision/Socrate/V89_recupero_originali/ARTVISION_SOCRATES_4X1_COMPLETO_PILOTA_V67_BACKUP.zip`
- Dimensione **117.280.478 B**; SHA256 **`bd075b4f39600eea64712970e812a2ca967128326f27674a79d3cc7da40ed462`** verificato nella presente sessione (coincide con la precedente lettura di ritorno V89); test ZIP CRC OK.
- Critico Standard V67: `f68592a8d65d5d774494f49892a4b8be8f9bbe7842ab19631f85046f0adf19c3`, 168.166667s, 1080×1920, AAC/H264, FULL DECODE PASS.
- Critico Museum V67: `c3be9d91b2967df4e484918b6d678b141111130eea991b63493d15b843c090a9`, 168.166667s, 1080×1920, AAC/H264, FULL DECODE PASS.
- Cinema Standard V59: `0f946f74397c780c9357f545d0a9712926bf02eb3f43ba4866eba7cda8828540`, 35.041667s, 720×1280, FULL DECODE PASS.
- Cinema Museum V61: `6ae8a2cb1ad3709bea4bab801ddefdaf8e7a00b3f3f65f50ddd81af8e4414afc`, 38.0s, 1080×1920, FULL DECODE PASS.
- Critico AAC demux ADTS: **stesso SHA256 per entrambi** `3f1374c08615822bd8c2fd41597d98dbcc2335ca3235543e5e978d9feee44669`.
- ZIP include quattro copertine, 16 post per le quattro piattaforme, ricette/fonti/QA. Voce Gacrux originale conservata separatamente in Libreria.
- Derivato separato V89R1 `Socrate_Critico_Museum_V89R1_REVIEW_FINALE.mp4`: **29.208.931 B**, SHA256 `e6cce47dd7adcf7d54262e9deab9ec450888e25462e739740dd6f39edc0416d3`, 720×1280, 168.166667s, AAC uguale, FULL DECODE PASS. Originale 1080p intatto. Il difetto cornice a 108–111s è attenuato/eliminato nei fotogrammi QA; durate zoom e volto Platone restano da rifinire.

## Klimt — recupero nuovo del 30/10
- Dropbox path: `/ARTVISION_KLIMT_4X1_PACCHETTO_COMPLETO.zip`, file `id:VU6duCyxXTcAAAAAAAAELQ`.
- File vero materializzato dal percorso Libreria collegato `/Dropbox/ARTVISION_KLIMT_4X1_PACCHETTO_COMPLETO.zip`, **65.968.295 B**, SHA256 `3a274ffe739599122f1b0f04bf3ee13837c8d706c25f03c7fdaf61cbb6d49f75`.
- **Dropbox `content_hash` verificato:** `ca71c10eb9b1aaef28204288d91893111e30190c7f6511d8cf29f42117eb6b9c`, ricalcolato a blocchi SHA256 da 4 MiB secondo il formato Dropbox e confrontato al valore fornito dal connettore. Non soltanto metadata.
- ZIP CRC **PASS**; 4 veri MP4, 4 copertine e 16 testi social; presente sorgente voce `SORGENTI/VOCE_GACRUX_UNICA.wav` e musica/foto/ricette.
- Critico Standard: `01_Klimt_Critico_Standard_Gacrux.mp4`, 17.136.945 B, SHA256 `d8bf725675e45be210383a4ca3b2113a06807bb9af540e21b3adb7fa2b4e5eb8`, durata **207.5s**, 720×1280 20fps, H264/AAC, **FULL DECODE PASS**.
- Critico Museum: `02_Klimt_Critico_Museum_Gacrux.mp4`, 13.583.486 B, SHA256 `814e52f6d4281df14d3064bce6f1295ab6cdc059a5d5c80acf7db0a095cbf1ab`, durata **207.5s**, stesso codec/frame rate, **FULL DECODE PASS**.
- Cinema Standard: `03_Klimt_Cinema_Standard.mp4`, 3.774.837 B, SHA256 `5651ec851055d007dba9ed86762840decd51a9008a9ebdfcba470618e31200a6`, durata **47s**, **FULL DECODE PASS**.
- Cinema Museum: `04_Klimt_Cinema_Museum.mp4`, 4.343.198 B, SHA256 `9dc3cf7abcebc3e8b16d105e9e9934cde8775cec1ac6b684519fe0df1875e746`, durata **52s**, **FULL DECODE PASS**.
- Critico AAC demux ADTS identico byte-per-byte: `7e33f4a696f77033afddfad2f18562295b605c39cfd50a999bf94843907a53fe` su entrambi.
- Revisione visiva preliminare con contatto 8 frame per ciascuno dei quattro MP4 (non sostituisce visione integrale): Critico di **3:27** superiore alla durata editoriale preferita dall'utente; ripetizione di inquadrature e presenza di elementi di cornice/matte nel Museum durante tratti di spiegazione da valutare frame-by-frame. **La sala e la cornice scura Klimt sono ricostruzioni dichiarate, NON fotografie della cornice autentica di Belvedere.** Necessaria decisione estetica, non falsificare fonte.

## Stato e prossimi passi
1. **Backup reali dei due 4×1 verificati**: Socrate Libreria privata con impronta SHA; Klimt Dropbox con content_hash reale verificato. Il blocco precedente di materializzazione Klimt è risolto usando la copia `/Dropbox` della Libreria.
2. **Non ancora V25 Gold**: 0 approvazioni proprietario; QA umano completo e refinements regia ancora richiesti. Correzioni come nuove revisioni dello stesso slot, senza perdere master e senza tagli audio arbitrari.
3. **Player sul sito / Android e import R2 singolo video**: NON verificati da questo controllo. La sola disponibilità dell'archivio e il conteggio aggregato della videoteca non prova la presenza o riproduzione di questi 8 MP4.
4. Restare sui due piloti, nessuna sesta opera, nessun social pubblicato, nessuna spesa API non autorizzata. Arte e accuratezza delle inquadrature precedono cadenza e volume.
