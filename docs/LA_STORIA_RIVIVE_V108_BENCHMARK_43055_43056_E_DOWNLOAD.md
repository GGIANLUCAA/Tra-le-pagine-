# La Storia Rivive · V108 — Benchmark visivi 43055/43056 e consegne Android

**Decisione editoriale del 31/10/2026.** L'utente ha nuovamente inviato i filmati personali `43055.mp4` e `43056.mp4` come riferimento di qualità della ricostruzione. Non usare il loro materiale come sorgente storica da ripubblicare.

## Audit oggettivo dei due benchmark
- `43055.mp4`: 20,233 s, H.264/AAC, 720×1280, 30 fps. Scene rivelate B/N→fotografie interpretative AI a colori, con volti, tessuti, accessori e sfondi di forte leggibilità e nitidezza percepita. Nella parte finale presenta schermate promozionali nere che **non fanno parte dello stile richiesto**.
- `43056.mp4`: 20,967 s, H.264/AAC, 720×1280, 30 fps. Stessa estetica, varie scene con restauro generativo forte, identità e profondità fotografiche, colori ricchi ma non necessariamente storicamente accertati. Anche qui NON replicare la coda promozionale.
- Entrambi sono **720×1280 e NON video 4K nativi**. L'effetto "sembra 4K" deriva da una ricostruzione fotografica generativa percepita come dettagliata, non dal semplice numero di pixel o da un passaggio di upscale.

## Audit vero CHINA c. 1928 V107
- MP4 V107 originale reperito in ChatGPT, 20,9s, H264/AAC 1080×1920 e 30fps, riproduzione e decodifica completa verificate. Un file esiste ma il precedente link Library appariva non disponibile all'utente.
- La ricostruzione delle quattro immagini è **DDColor + RealESRGAN (colore semantico + super-risoluzione appresa), non un restauro fotografico generativo equivalente ai due riferimenti**. I dettagli dei volti/oggetti NON sono ricostruiti al livello qualitativo dei benchmark. NON spacciare 1080×1920 per qualità superiore rispetto ai riferimenti 720×1280.
- La quinta scena è movimento d'archivio colorizzato, **non Vidu**. Manca l'approvazione finale V94/V96/V99; la licenza territoriale italiana della fonte non è verificata. Non pubblicare né identificare il lavoro come master finale.
- Il MP4 per Android è stato ricodificato da originale, nuovo file `720×1280` con codec H.264/AAC + `faststart`, durata 20,905s, dimensione circa 3,4MB e decode completo FFmpeg superato; consegnato come nuovo allegato ChatGPT e ZIP verificato CRC.
- File ChatGPT temporanei non vanno citati nel repository come link permanenti. Per i prossimi video servono asset realmente reperibili: sito privato/Release verificata e almeno un download utente provato, conservando file MP4, copertina, ZIP.

## Blocco di qualità vincolante per le produzioni future
1. Se il risultato mostra solo colori aggiunti a volti ancora molli, V94 `visual_photo_reconstruction_pass=false`. Un filtro DDColor, l'upscale e il semplice sharpen non soddisfano lo stile dei due riferimenti.
2. Prima di spendere crediti Vidu: ottenere quattro fotografie ricostruite realmente con un modello image-to-image, con composizione, sagome e oggetti originali source-locked, e confronto umano con riferimenti `43055.mp4` e `43056.mp4`. Il modello non deve inventare un'altra inquadratura e non deve creare identità arbitrarie spacciate per storiche.
3. Fonte storica sufficiente: soggetti grandi a video, volti leggibili, scansione pulita; se una fonte ha solo pochi pixel nel crop 9:16, **scegliere un'altra fonte** senza ostinarsi con filtri sfocanti. L'obiettivo è la percezione fotografica, NON una falsa promessa di 4K.
4. Regia: vero movimento B/N → freeze esatto del frame realmente filmato → morph/transizione breve → fotografia I2I fotorealistica con tempo per apprezzarla, 4 scene; quinta con video Vidu vero animato dalla stessa foto restaurata e con scene/volti coerenti. Niente foto generiche, montaggio di scene sbagliate, promo nera o coda di filler.
5. Se manca Vidu o manca la ricostruzione generativa, il MP4 può essere consegnato solo come **provino tecnico**, anche se FFmpeg, durata e audio sono tutti perfetti. Non chiedere nuovamente regole di stile già note.
6. File non disponibile significa **blocco di consegna**: verificare path reale nel runtime corrente, codec e decode, nuovo nome copiato/creato in questa conversazione, ZIP CRC, e link verificato. Non inventare percorsi `sandbox:`; se resta non accessibile, dare link esterno reale già verificato.
