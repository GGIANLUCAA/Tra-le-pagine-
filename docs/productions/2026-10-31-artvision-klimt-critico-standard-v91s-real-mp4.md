# ArtVision V91S — Klimt *The Kiss*, Critico Standard: revisione reale e backup (31 ottobre 2026)

## Risultato verificato
L'utente ha apprezzato esplicitamente **Socrate Critico Museum V90R3** ("Bello mi piace molto") e ha chiesto di proseguire. Questo resta un benchmark qualitativo editoriale, **non un'approvazione Gold V25**. Partendo dai byte veri del pacchetto Klimt V90 su Dropbox, è stata prodotta **una revisione non distruttiva del solo slot Critico Standard**. Il master V72, il Museum V73/V91 e tutte le altre varianti sono rimasti intatti.

**MP4 reale:** `Klimt_Critico_Standard_V91S_FOCUS_NARRATIVO_REVIEW.mp4`
- **44.612.006 byte; SHA-256 `0e4c540d90cdead1e8a3129b0f4b6b03f70341d803ca1b84216df132facbe0b4`**.
- H.264 720×1280 / 20 fps / **4.150 frame**, durata **207,500 s** (video originale 3:27.5).
- **FFmpeg full-decode audio/video PASS**. AAC estratto in ADTS: SHA-256 `7e33f4a696f77033afddfad2f18562295b605c39cfd50a999bf94843907a53fe`, **identico bit per bit** a Critico Standard V72, Critico Museum V73 e Museum V91. Riutilizzata l'unica voce Google Gacrux già esistente; **nessuna nuova chiamata TTS e nessuna spesa API**.
- Quadro originale PD, stesso JPEG 4096×4188 SHA-256 `43e998b7b9dc6f935918dbd55ff1a3f34052b932d563e74e5d2d5dceb2660b24`.
- **27 inquadrature** semanticamente impostate su timecode del vero cache ASR: hook volti/mani 0–4,5s; quadro intero con piccolo titolo 4,5–12s; volti/bacio 24,6–48s; mani 48–70,8s; rettangoli maschili/cerchi femminili 70,8–96,2s; oro 96,2–115,8s; fiori, bordo prato e margine 115,8–140,5s; gambe inginocchiate 140,5–161,1s; volti/pelle e contrasto dipinto 161,1–181,8s; prospettiva complessiva 181,8–191,2s; volti e quadro intero nel finale 191,2–207,5s. Micro-pan/zoom dal **vero dipinto**, con transizioni brevi e senza ripetere l'originale zoom monotono.
- **Regia Standard autonoma**: nessuna sala/cornice museale ricostruita all'interno, nessuna aggiunta di figure AI. La variante Museum V91 resta un video distinto, con la stessa traccia audio.

## Archivio e readback, fisici
- MP4 su Libreria privata: `/ArtVision/Klimt/V91S_CRITICO_STANDARD_FOCUS/Klimt_Critico_Standard_V91S_FOCUS_NARRATIVO_REVIEW.mp4`.
- ZIP su Libreria privata: `/ArtVision/Klimt/V91S_CRITICO_STANDARD_FOCUS/KLIMT_CRITICO_STANDARD_V91S_REVIEW_ANDROID.zip`, **45.451.179 byte**, SHA-256 `ee172e4b5b1ed27421a210bc3a9a3f09b6f9131ca7cd867d847f387be27488b5`.
- **Entrambi caricati e riscaricati realmente**, SHA-256 del readback uguale al file di origine. ZIP **13 membri**, CRC PASS e SHA-256 dell'MP4 estratto uguale a quello del video singolo.
- Contenuto ZIP: vero MP4, copertina, confronto immagini **originale V72 vs V91S** tratte dai due MP4, 4 bozze di post, copione integrale, allineamento Gacrux, fonte/licenze, QA JSON e renderer di riproduzione. Le bozze NON sono state pubblicate.
- Il pacchetto storico Klimt 4×1 su Dropbox **non è stato sovrascritto**, né duplicato in Dropbox senza un consenso al nuovo percorso.

## QA artistica e limiti, senza inventare
Decodifica integrale e campionamento visivo **non equivalgono all'ascolto/visione umani integrali**. La voce originale ha 476 parole, durata lunga 207,5s: non accorciare arbitrariamente senza un WAV nuovo e compatibile, di costo verificato. Verificare ritmo (specialmente 12–30s), transizioni, centratura dei dettagli nel playback completo e fine video. **Gold V25 resta PENDING / 0**. **Il player su sito/Android e import R2 della V91S NON sono stati verificati.**

## Obblighi successivi
1. Confronto artistico reale dell'utente sulle due varianti Klimt (Critico Standard V91S e Critico Museum V91) rispetto al benchmark Socrate V90R3, senza presumere Gold.
2. Solo se necessario, correzioni minime non distruttive con nuovi MP4 verificati e copie readback; evitare rifacimenti dei quattro originali.
3. Ripristinare nel sito il precedente **Socrate Cinema Museum V61** già staged in Libreria e verificare playback autentico (non basta object list R2). Se lo strumento richiede selezione di file `fileParams`, non dichiarare l'import riuscito.
4. Nessuna sesta opera, nessun social autopublish, nessuna spesa API, nessuna nuova automazione o perdita di master. I 4 video per opera restano 4 slot: le revisioni non li incrementano.
