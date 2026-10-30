# La Storia Rivive · CHINA c. 1928 — audit V103 (30/10/2026)

## Esito REALE, non una falsa consegna
Fonte: Wikimedia Commons `China and the Chinese, 1920s - Travelfilmarchive.webm`.
Archivio fonte: 720×480 px, 488.84s; SHA-256 verificato in GitHub Actions
`fbdf513bd01171c51c431d79510f93a92b44ccdf44bdfdf03d28f6357c1d43d5`.
Riprese reali selezionate a t≈72,182,222,317,437s (5 periodi distinti, NON ancora cinque inquadrature verificate da revisore). Selezione tecnica e film B/N riusciti.

La fonte è **troppo poco dettagliata per volti garantiti** dopo crop verticale, e include il timecode `TFA` sovraimpresso. Il V103 ha dovuto introdurre un taglio top/bottom della sorgente originale, senza cancellare o inventare pixel. NON chiamare il file originale 4K o HD nativo.

## Verifica image-to-image
Test 1: Finegrain libero su input monocromatico ha restituito immagini con saturazione troppo bassa (circa 5–9 di media), dunque non qualificabili come autentiche fotografie a colori; dopo tre prove è stato raggiunto il limite ZeroGPU anonimo. Test 2: generazione alimentata da DDColor semantico + token HF_TOKEN (non esposto nei log) ha incontrato l'ulteriore limite quota ZeroGPU Free già al primo invio. **Non ripetere la chiamata a ritmo automatico, non ricaricare, non richiedere upgrade PRO automaticamente.**

Nessuna fotografia image-to-image finale approvata, nessuna nuova clip Vidu. Il progetto resta sotto V91/V94/V96/V99; San Francisco V98 resta il benchmark minimo accettabile. La pubblicazione social/sito non è autorizzata.

## Output provino interno (solo in ChatGPT, NON final master)
Montaggio tecnico B/N di cinque scene autentiche e partitura originale; 14,2s verticale 540×960 H264/AAC, taglio del timecode per controllo regia. **Non soddisfa il requisito delle 4 foto I2I e della 1 clip Vidu, non va promosso a Gold Master o video concluso.** Evidenza QA locale disponibile in chat; non inventare un link GitHub Release.

## Correzioni operative prima di nuove spese
1. Gate fonte: misurare raster nativo utilizzabile *dopo* il crop, presenza watermark/timecode, dimensione reale dei volti; cambiare fonte se la parte utile è debole. Non usare source score alto se l'oggetto storico è poco leggibile.
2. In uscita: provare un solo I2I da base AI DDColor e bloccare in caso di quota/saturazione/identità errata. Non effettuare cinque richieste destinate a fallire.
3. Carico API e spese: controllare quota residua e licenza prima di lanciare batch, senza upgrade né tentativi indiscriminati.
4. Reel finali: solo quattro I2I genuini e una Vidu dallo stesso frame di fonte; verifica visiva reale su persone, architettura e oggetti; V99 e diritti territoriali Italia prima della pubblicazione.
5. Scegliere in futuro fonti d'epoca con scansioni più nitide, possibilmente senza scritte archivistiche impresse, invece di ripetere l'ottimizzazione cosmetica di sorgenti 480p.

## Rights
Wikimedia Commons contrassegna la fonte come pubblico dominio negli USA e in Cina; il relativo status e gli eventuali diritti residuali in Italia non sono stati approvati. Nessuna pubblicazione pubblica derivata dal film è stata effettuata da questo flusso.
