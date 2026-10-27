# ArtVision Cinema — The Cyclops (27/10/2026, 20:15)

## Stato effettivo
**rendered_needs_review — NON Gold Master.** Nuovo montaggio autonomo di 51,333 s (1080×1920, 24 fps, H.264/AAC), generato e controllato localmente con Pillow/FFmpeg, **senza API video IA a pagamento** e senza pubblicazione social.

**IMPORTANTE — duplicati:** l'opera *The Cyclops* (Odilon Redon, ca. 1914) era già stata mostrata nelle Collection *Visions of Symbolism* e *The Other Side of Beauty*. Questo MP4 è un **nuovo film singolo con una regia distinta**, ma **non una nuova opera nel catalogo**. Non conteggiarla come quadro mai trattato. La scelta è stata un fallback a costo zero per indisponibilità locale del nuovo asset Bruegel/Turner; nel prossimo ciclo privilegiare una vera opera inedita con diritti e file acquisiti.

## Consegne reali (Google Drive personale, non social)
- [MP4 verificato](https://drive.google.com/file/d/1Aq9n8IV4qdfJ9Oto8vrgTEU2b4rz27pr/view)
- [Copertina JPEG](https://drive.google.com/file/d/1RtrdpY0hHkNMgZGSpzICl9W2zdfWj7og/view)
- [ZIP completo verificato](https://drive.google.com/file/d/1t6LIT8d4ZeRyvnFaYCxVpqI43rMIR-nm/view)

ZIP: 53.355.001 byte, 41 file; include MP4, copertina, fonte originale, registrazione MP3 originale, 4 post IT distinti e scritti, ricerca, licenze, ricetta, storyboard, script, QA e fotogrammi.

SHA256 MP4: `860922e2ffac18bfd6859a291f26b58e53dfbe639cb3eb2d50b5efedd17acda0`.
SHA256 ZIP: `7d0ac3092aaefb60b9aff810e020a8fdd1c2b0fcc40c84f17385d909fef9c0ce`.

QA: ffprobe H264 1080×1920 24 fps + AAC stereo 44,1 kHz; decodifica integrale ffmpeg **PASS**; ZIP CRC e contenuto **PASS**; copertina e primo frame controllati visivamente, **THE CYCLOPS + ODILON REDON** entrambi presenti con template tipografico V6-family. Il difetto di titolazione della produzione *The Temptation of Saint Anthony* non è stato ripetuto. Audio tecnico: mean -21,8 dBFS, peak -6,8 dBFS; ascolto soggettivo integrale e approvazione artistica umana **pendenti**. Nessuna affermazione di pubblicabilità automatica.

## Ricerca editoriale
Tre candidati: *The Fall of the Rebel Angels* (Pieter Bruegel the Elder, 1562), *The Fighting Temeraire* (J. M. W. Turner, 1839), *The Cyclops* (Odilon Redon, ca. 1914). Segnali social pubblici comparabili non verificati, nessuna statistica inventata. Bruegel e Turner non acquisiti localmente; Redon già in archivio con hash verificabile.

Fonte primaria: https://www.krollermuller.nl/en/collection/odilon-redon-the-cyclops-km-103-098 (Polifemo, Galatea, Aci, ca. 1914).
Riproduzione: https://commons.wikimedia.org/wiki/File:Odilon_Redon_-_The_Cyclops,_c._1914.jpg (Public Domain Mark; SHA256 `1b89371abacf105f1f28ef91a79567080c49bc6de894084db35910ac2493223f`).
Registrazione: *Echoes of Time* — Kevin MacLeod, ISRC USUAN1300029, CC BY 4.0 https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1300029 (MP3 SHA256 `be9740a15e0395d4e763d8ea5f8691ee2422924f44a03b12c329ecc4a59cc2a8`).

## Regia e feedback precedente
L'utente ha respinto la V3 di *The Ninth Wave* perché il quadro sembrava una foto sovrapposta alla cornice. **Non ripetere quella falsa sala**. In questo episodio è stata scelta una regia classica di dettaglio e rivelazione, senza cornice né finto museo, con tagli opachi e movimenti minimi. Non significa che il problema della cornice sia risolto: l'effetto museo rimane sospeso fino a prova convincente di profondità, occlusione e contatto reale.

## 3 limiti autocritici per il ciclo successivo
1. Opera già presente in due raccolte: serve davvero un nuovo quadro, non solo un nuovo edit.
2. Occhio del gigante mostrato due volte: richiamo motivato, ma da verificare se il pubblico lo trova ripetitivo.
3. La tela non è 9:16 e il totale usa matte scuro: è preferibile a distorsione/crop falso, ma meno immersivo.

Il ZIP include `build_cyclops.py`, `render_cyclops.py` e tutte le fonti necessarie per replicare il film. Nessuna modifica ai Gold Master e nessuna spesa Vidu/Kling/Runware/Wan/Seedance.
