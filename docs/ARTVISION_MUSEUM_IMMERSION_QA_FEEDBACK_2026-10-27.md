# ArtVision Museum Immersion — feedback e QA dei raccordi (27 ottobre 2026)

## Stato
Feedback positivo dell'utente su *The Ninth Wave* di Ivan Aivazovsky: l'effetto museo è promettente, ma **non è un Gold Master**. Il feedback identifica tre difetti concreti: (1) opera leggermente decentrata o fuori dal bordo interno della cornice; (2) stacco percettibile tra avvicinamento nel museo e primo dettaglio del film; (3) stesso stacco tra ultimo dettaglio e ritorno alla sala.

La V2 approvata come **direzione di qualità**, non come master definitivo, va preservata intatta. È stata esportata separatamente una prova correttiva V3 (nessuna sovrascrittura dell'originale).

## Correzione sperimentale V3 eseguita
- Quadro confinato esclusivamente al **rettangolo interno** della cornice mediante maschera geometrica opaca; niente sbordature.
- La stessa fotografia verificata del dipinto (5815 × 3648) viene usata anche durante l'avvicinamento: non sostituire il quadro sul confine del museo con un'altra immagine/crop senza match.
- L'ultimo fotogramma dell'ingresso è stato registrato geometricamente sui pixel del primo fotogramma del montaggio centrale esistente (matching SIFT/RANSAC). La transizione è un movimento continuo all'interno dell'**unica opera**, senza crossfade tra quadri.
- Per l'uscita, il film centrale finisce prima del taglio verso un cielo diverso; il movimento inverso comincia sulla stessa immagine dell'ultima scena conservata e riporta alla stessa sala e punto camera del primo fotogramma.
- Centro del film e musica già utilizzata mantenuti, senza riscrivere regia o audio del contenuto.
- V3: MP4 verticale 1080 × 1920, H.264/AAC, 24 fps, durata circa 63,96 s. Controlli completati: ffprobe, decodifica integrale senza errori, controllo visivo dei fotogrammi ai due punti di giunzione e dei fotogrammi iniziale/finale.

## Principi operativi riutilizzabili
1. **No cornice che taglia/contamina il dipinto**: definire il perimetro interno dell'opera e verificare una cornice di sicurezza anti-sbordo sui fotogrammi di ingresso e ritorno.
2. **Niente salto tra sala e dettagli**: il raccordo deve terminare sullo stesso ritaglio, scala, posizione e grading della prima inquadratura interna. Controllare fotogrammi adiacenti al taglio, non solo gli still di copertina.
3. **Niente salto al ritorno**: iniziare l'uscita su un dettaglio esattamente coerente con l'ultima scena precedente, ricomporre il dipinto e soltanto dopo rivelare la cornice e la sala.
4. Una sola opera **opaca** per fotogramma; mai ghosting, blend o dissolvenze incrociate tra dipinti. Allineare i pixel, non mascherare il taglio con trasparenza.
5. La V3 è ancora una ricostruzione di sala/cornice non autentiche e un'animazione 2D, **non una ripresa museale documentaria, né un video 8K**. Ricercare geometria 3D e frame storico solo se fonti disponibili.
6. L'effetto Museum Immersion resta **una tecnica opzionale**, da scegliere secondo il soggetto; non un'apertura obbligatoria per tutti i video.

## Ulteriori QA artistici consigliati
Controllo 0–3 s; controllo di prospettiva fisica e consistenza della cornice su tutta la traiettoria; confronto fotogramma prima/dopo *entrambe* le giunzioni a grandezza nativa; conferma di leggibilità esatta titolo/artista; realismo dei materiali del museo; ascolto audio; fonti e diritti separati della foto e della registrazione. Nessun automatismo deve proclamare «Gold Master» solo perché ffmpeg è passato.

Questo documento è un addendum non distruttivo per apprendere dal feedback; il sistema di regole attive e il preset Cinema V6 conservano la precedenza.