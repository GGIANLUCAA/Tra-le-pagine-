# La Storia Rivive · verifica produzione e consegna 06/11/2026 — V299

## Risultato concreto
- Recuperato da GitHub Actions run [42134457336](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/42134457336), artifact ID **13464593986**, il master di revisione `BOMBAY_V298_VISUAL_REMASTER_REVIEW.mp4`.
- MP4 verificato H.264 + AAC, **720 × 1280, 30 fps, 19.133 secondi**, 6.917.805 byte. Video SHA256 `838dabf86de379d8d4d00a961563a10b9eac5a017ad35d2a300b274943b38718`. Decodifica completa FFmpeg superata.
- Le prime quattro sequenze provengono dal lavoro preesistente V98.1, migliorate in V298 con **una** fotografia rigenerata tramite vero image-to-image Finegrain della stessa inquadratura; l'ultima sequenza conserva **una clip Vidu reale preesistente**. Nessuna nuova richiesta Vidu e nessun nuovo consumo di crediti.
- Gate di geometria della nuova fotografia: correlazione struttura 0.98994 e colore presente, confronto visivo originale-restauro salvato. **Il gate automatico NON certifica identità, anatomia o perfezione fotografica**.
- Misura del movimento nella parte finale della vera clip già integrata (15–18,8 secondi): differenza media di luminanza campionata ~22,3/255 tra letture ogni 0,25s; movimento visibile. La misura non prova che tutte le persone o gli oggetti siano perfettamente stabili.
- Preparato nuovo ZIP Android con MP4, copertina reale, storyboard, prima/dopo, quattro bozze social, log QA e controllo CRC ZIP. Percorsi sandbox ChatGPT **non permanenti**: non riportarli come URI pubblici nel repo.
- Questo è **un miglioramento di un soggetto precedente, non un nuovo soggetto**, e NON un video editorialmente approvato o pubblicato.

## Nuovo contenuto in prova — cinema del 1903
- GitHub run [42145684681](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/42145684681), artifact ID 13470720244: `CINEMA_1903_THE_GREAT_TRAIN_ROBBERY.mp4` in H.264/AAC 720×1280, 24 fps, 16.25s, SHA `7e09ead59addfa16ebb79ee761bd33a1006ce26aca2e6f07bee96c864a38f307`.
- Il video è riproducibile ma contiene **un'unica ripresa principale con interventi cromatici poco naturali** e non contiene Vidu: NON soddisfa il format internazionale approvato 4 foto I2I + 1 Vidu. Trattare come provino, non promuovere in serie o al sito. La selezione di nuovi fotogrammi forti e varie scene originali è da correggere.

## Priorità tecnica prima del successivo video NUOVO
1. Rafforzare la selezione delle **vere differenti inquadrature** d'archivio a risoluzione utile e senza burn-in; evitare clip lunghe monocromatiche con finti colori.
2. Generare foto image-to-image *dopo* aver bloccato timecode e geometria, conservando gli SHA delle fonti e il controllo visivo comparato ai benchmark 43055/43056.
3. Quattro ricostruzioni fotografiche verificabili + una clip **Vidu realmente generata dalla stessa scena**, con ricevuta task, bilancio crediti e autorizzazione per singola richiesta. Nessun surrogato video e nessuna spesa o richiesta pagata senza condizioni del gateway.
4. Solo se V91/V94/V96/V99 e giudizio artistico sono superati, pubblicare/consegnare come master; diritti territoriali e utilizzo archivi da confermare.
5. Per ogni file consegnato, controllare prima l'esistenza e l'integrità del file, MP4 H264/AAC, traccia audio, riproduzione integrale, ZIP CRC, e percorso/download reale accessibile anche da Android.

## Stato autenticazione consumer Vidu
- Workflow del 06/11/2026 [42178178921](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/42178178921) riporta `VIDU_TOKEN` consumer assente; il raccoglitore non ha scaricato nuove clip. È distinto da `VIDU_API_KEY` del gateway, quindi non dedurre che il provider sia totalmente assente o che possano essere spesi crediti della sottoscrizione web senza verifica.
