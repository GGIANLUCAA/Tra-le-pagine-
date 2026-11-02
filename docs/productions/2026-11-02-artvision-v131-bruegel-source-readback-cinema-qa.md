# ArtVision V131 — Bruegel inv. 584: source fisiche + revisione reale del Cinema legacy

**Data:** 2026-11-02. **Owner:** `6adca191603c8191a90d5190901cd034`. **Opera selezionata #1:** Pieter Bruegel the Elder, *The Fall of the Rebel Angels* (1562), Musées royaux des Beaux-Arts de Belgique, **inv. 584**, olio su quercia **117 × 162 cm**.

**RISULTATO NON È UN NUOVO MP4:** recupero di byte autentici già prodotti, controllo completo dei checksum, controllo visivo di 11 fotogrammi del Cinema legacy e specifica di correzione. Non modificati master, lock, slot 4×1, stato Gold, archivio privato o pubblicazioni. Nessun TTS/Vidu/costo.

## Prova fisica della fonte e della musica

- GitHub Actions **artifact 12775741359** scaricato di nuovo come ZIP reale (16 MB circa); **SHA256 ZIP** `3265e5f24b9078b312779b0b9c44d0dcc9d96fc39271a217fe399cfc2b35b143`, test CRC **PASS**.
- `ORIGINAL_ARTWORK.jpg` estratto e verificato: **3840×2772 RGB**, SHA256 `09f675e7861da808ede4bc1f85573e97884fdbcc6c1d6cb482e3e449d58aace5`; identico al `SHA256SUMS.txt` dell'artifact. Fonte Commons/Google Art Project [file esatto](https://commons.wikimedia.org/wiki/File:Pieter_Bruegel_the_Elder_-_The_Fall_of_the_Rebel_Angels_-_Google_Art_Project.jpg), indicato PDM/PD-Art per riproduzione fedele di opera bidimensionale in pubblico dominio; il file è una versione ridotta dell'originale 30.000×21.654 px, non una fotografia della cornice.
- `ORIGINAL_LICENSED_MUSIC.mp3` estratto e verificato: **282,096 s**, SHA256 `00a2fee94641761f37e74973eaaa654e1a8a628269f585707d46987558d07573`; `SHA256SUMS.txt` corrisponde. Identificazione nell'artifact: *Evening of Chaos* di Kevin MacLeod, ISRC **USUAN1300041**. [Scheda ufficiale Incompetech](https://remote.incompetech.com/music/royalty-free/index.html?Search=Search&isrc=USUAN1300041) pubblica **CC BY 4.0** e il credito obbligatorio; [testo della licenza](https://creativecommons.org/licenses/by/4.0/). Uso in un derivato richiede attribuzione e indicazione delle modifiche, non spese di licenza aggiuntive. L'identificazione del file audio si basa sul manifest/provenienza già conservato; non è stata eseguita comparazione fingerprint con il server del compositore.
- La [scheda istituzionale del dipinto](https://fine-arts-museum.be/fr/la-collection/pieter-i-bruegel-la-chute-des-anges-rebelles) conferma 1562, inv. 584, 117×162 cm. La **foto istituzionale** reca un diverso credito fotografico (Grafisch Buro Lefevre) e **NON** è stata assimilata automaticamente alla fonte Commons PDM.

## Controllo del Cinema già esistente (non è un nuovo slot 4×1)

- `FALL_OF_REBEL_ANGELS_CINEMA_LEGACY_REVIEW.mp4`: **19.376.181 B**, SHA256 `0bd2fb6e0aadd02ae1eab56fa804f5fcb914c15330121765e28ba5878531f12a`, **55,25 s**, H264/AAC **1080×1920 24 fps**, **FFmpeg full decode PASS**.
- Fotogrammi reali estratti a **0,5; 2; 5; 8; 12; 18; 25; 33; 41; 48; 54 s**; contatto visivo composto localmente (JPEG 1296×838, SHA256 `43f1b44cdbcbffccda48bf4b8d3a7e8fc04e1e18d0d84ec6b48fbf3adccc324c`). Questa tavola è solo evidenza QA locale: **NON** caricata in GitHub/Library né consegnata come video.
- **Difetto artistico concreto:** le inquadrature **5 e 8 s** sono quasi lo stesso soggetto con variazione minima (RGB MAE campionato **7,2/255**); 0,5 e 2 s sono identiche nel campione (RGB MAE **0**). Alcuni dettagli sono rivisitati in seguito (es. 12/33 s). Non è sufficiente per certificare montaggio vario, né sostituisce visione integrale a velocità normale.
- La copertina **mostra già il titolo inglese** e l'artista: non applicare inutilmente la correzione V129 di *Triumph*/*Magic Circle*. Il finale a 54 s mostra il dipinto completo orizzontale con ampie fasce nere nel verticale: scelta grafica da valutare, non bug codec.
- **Proposta non renderizzata:** per un eventuale Cinema Standard 4×1 usare sequenze semantiche distinte (arcangelo centrale, angeli bianchi, ibridi pesce/insetto, discesa e quadro integrale), camera misurata, durata motivata e nessuna ripetizione gratuita; preservare il vecchio V6 come master storico.

## Gate ancora NON superati

1. **Cornice Bruegel:** foto indipendente [Sailko 2016 CC BY 3.0](https://commons.wikimedia.org/wiki/File:Pieter_bruegel_il_vecchio,_Caduta_degli_angeli_ribelli,_1562,_37.JPG) identificata, ma file non acquisito con SHA256 locale e cornice dell'esemplare non validata visivamente; non chiamarla originale/storica.
2. **Sala V119:** nessuno dei cinque preset è asset 3D/fotografico approvato; non sostituire con galleria raster. Nessun provino Museum autentico V118/V119 realizzato.
3. **Critico:** manca WAV originale condivisa con costo/Free Tier effettivamente verificato. Nessuna nuova TTS consentita per inferenza.
4. **Diritti/territorio:** Commons PDM è evidenza utile ma non una licenza universale per tutte le giurisdizioni e i diritti su fotografie museali terze; verifica del file esatto e condizioni di distribuzione finale ancora distinta.
5. **Consegna:** Library segnalata piena da V129; nessun nuovo backup/download readback persistente, quattro MP4 non esistono per la selezione #1.

**Decisione:** nessun rendering della nuova serie, nessun Gold/pubblicazione, **0/4 nuovi slot**. Proseguire con vera fonte cornice/sala e autorizzazioni economiche prima di renderizzare; il vecchio Cinema rimane integro e candidato a riuso solo dopo review.
