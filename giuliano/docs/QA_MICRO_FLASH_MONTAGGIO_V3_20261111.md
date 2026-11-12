# GIULIANO — Regola QA V3: eliminare i micro-flash fra fotografie
Data: 11 novembre 2026 · Effetto rilevato nel documentario *The Walking Giants* (Moai) · Applicare alle future produzioni della serie.

## Il problema dimostrato dal film finito
- MP4 di riferimento fornito dall'utente con vero esperimento di trasporto: durata 209,880 s, 24 fps, 1080×1920.
- Scansione integrale 5.037 fotogrammi, campionamento effettivo 24 fps a 180×320 per differenze percettive.
- 70 salti visivi grandi, **16 coppie di salti ravvicinati** separate da 0,042–0,250 s (2,292 s totali di immagini intermedie involontarie).
- In particolare 77,583; 82,542; 94,500; 121,250; 137,500; 140,958; 143,958; 146,417; 151,583; 155,542; 158,875; 164,375; 170,000; 180,792; 199,333; 202,083 s.
- **Causa:** inserimenti e tagli sovrapposti sulla timeline video permettevano brevi ritorni alla fotografia sottostante o ad altra immagine in corrispondenza dei bordi dell'overlay. Non era un problema della voce o della durata editoriale originaria delle immagini.

## Correzione applicata al file di revisione V3
- Eliminati tutti e 16 i segmenti brevissimi preservando il fotogramma pulito precedente fino al taglio voluto, con filtro FFmpeg `freezeframes` a indici fotogramma precisi.
- Una seconda scansione su tutti i 5.037 fotogrammi del nuovo master ha trovato **0 coppie ravvicinate**, 54 tagli visivi grandi, **nessun intervallo inferiore a 2,5 s** tra tagli rilevati.
- Originale audio Google Gacrux + musica preservato (comparazione hash di audio PCM decodificato), duration 209,880 s.
- Filmato autentico del test inserito tra 106,983 s e 121,290 s, senza alterare il suo contenuto principale.
- Nuovi MP4 Full HD, Android e leggero controllati con decodifica video completa, ZIP con controllo CRC.
- Il file corretto è stato consegnato direttamente nella conversazione; **questa regola nel repository non è un commit del MP4 finale**.

## Regola obbligatoria per ogni futuro MP4
1. Eseguire un detector di cambi visuali sul **master già montato**, non soltanto sulla timeline programmata. Valutare ogni fotogramma a 24/25/30 fps con soglie colorimetrico-percettive calibrate.
2. Se due tagli intenzionali sono separati da meno di 0,5 s in un documentario fotografico, trattare l'intervallo come **errore da revisionare**. Non correggere automaticamente un montaggio di azione/esperimenti reali senza valutazione registica.
3. Le fotografie normali del documentario devono avere tempi leggibili; indicativamente ≥2,5–3 s, con eccezioni motivate. Un flash inferiore a un secondo non deve mai derivare da una sovrapposizione tecnica.
4. Non inserire nuovi spezzoni sopra una timeline preesistente lasciando ai bordi residui da 1–6 fotogrammi. Usare frame/PTS esatti e controllare il primo e l'ultimo secondo di ogni inserto.
5. Conservare la traccia audio approvata mediante copia stream o hash del PCM decodificato quando si corregge soltanto la regia.
6. Il vero filmato di una prova sperimentale ha priorità sulle simulazioni. Distinguerlo dalla grafica e controllarne i diritti prima della pubblicazione.
7. Ripetere il detector sul **risultato esportato**. Non dichiarare «definitivo» prima di avere PASS su MP4, audio, QA flash, ZIP e controllo visuale umano.
8. Se compaiono due cut ravvicinati: fermare la pubblicazione, sostituire il microspezzone con continuità della scena precedente o nuova ripresa pertinente, poi rifare QA.

### Strumenti implementabili
FFmpeg/ffprobe (decoding, frame-accurate `freezeframes`, PCM hash), OpenCV per distanza fra fotogrammi e istogrammi a 24 fps, QA JSON con cut timings e collage prima/dopo. PySceneDetect può essere aggiunto, ma **non sostituisce** il controllo visivo degli stacchi effettivi.

**Importante:** una verifica tecnica elimina errori riproducibili; non può garantire in modo automatico che la regia sia emotivamente convincente. Occorre guardare il film finito per intero.
