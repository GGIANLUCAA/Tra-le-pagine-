# La Storia Rivive V56 — Pilot Beirut 1919 (prima prova reale, 28/10/2026)

## Sorgente reale
- [Scènes de rue — AI13347](https://commons.wikimedia.org/wiki/File:Sc%C3%A8nes_de_rue_-_AI13347.webm) — Musée Albert-Kahn, Lucien Le Saint, Beirut, 1919 (titolo e dati archivistici da verificare prima della pubblicazione).
- Licenza riportata da Commons: CC0; completare il controllo di diritti residuali e metadati nell'iter V56.
- Master Wikimedia recuperato realmente nel [workflow Actions 40701782146](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/40701782146). Esecuzione **success**: test V56, download e tavola provini.
- Origine scaricata: WebM (VP9/Opus) 720×576, durata 187,784 secondi (caratteristiche del file digitale, non specifiche della pellicola originale); SHA256 `53de3231f50cb7da1d5f909efe387c71f38467f1cba986beb6ed634f1d1728a1`.
- Frammento scelto dopo analisi fotogrammi originali: ~137–150 s. Passanti e cammelli in strada. Il taglio centrale 9:16 conserva il principale soggetto, ma a certe riprese nasconde lati dell'originale; ricontrollare il moto a schermo intero.

## Risultato reale prodotto in ChatGPT
- Provino locale: `STORIA_RIVIVE_BEIRUT_1919_PROVINO.mp4`, **12,917 s**, 720×1280, H264/AAC.
- Fonte esclusiva: i fotogrammi del medesimo filmato Wikimedia; nessuna ripresa sintetica.
- Effetto B/N→**viraggio caldo monocromatico**, NON colorizzazione AI autentica e non colori dell'epoca. Transizione a circa 4–6,5 secondi.
- Accompagnamento originale sintetizzato localmente, non suono d'archivio né canzone storica protetta.
- Copertina ricavata da un fotogramma del video, 4 testi social originali, `FONTI_DIRITTI.json`, `RICETTA.json`, `QA.json`, `APERTURA_E_SCENE.jpg`, ZIP con CRC testato.
- MP4 controllato con ffprobe + **decodifica integrale** nel container. Tavola real-frame 0.1, 1, 3, 5, 7, 10, 12.2 s controllata visivamente. Questo non equivale a vera approvazione artistica con visione e ascolto realtime su Android.
- File ChatGPT: creati e forniti tramite link `sandbox:/mnt/data/LA_STORIA_RIVIVE_BEIRUT_1919/...` verificati nel runtime; **non** archiviati in GitHub o su sito privato e non si presume che siano accessibili in una chat diversa.

## Stato e blocchi senza scorciatoie
- **PROVINO**, non Gold Master, non pubblicato. Colorizzazione AI coerente fra fotogrammi ancora non disponibile/integrata.
- Nessun credito Vidu e nessuna API a pagamento.
- Consegnato MP4 locale, JPEG e ZIP completo. Download effettivo su Android dell'utente non ancora confermato.
- Video Library Studio: `archive_sync_pending`. Non importato, non certificati playback/cover/social/ZIP sul sito.
- Non far partire serie ricorrenti fino a un video a colori vero verificato, V55 completato, diritto e sito verificati. Non riutilizzare il timing di questo pilot come stampino.

## Lezioni per il prossimo ciclo
1. Per B/N→colore vero serve modello di colorizzazione, interpolazione temporale/flicker QA e **stessa ripresa**.
2. Velocizzare render: la pipeline attuale decodifica la fonte due volte per B/N e viraggio, con rischio di stop del job; decodificare una volta e diramare i filtri, esportazione più efficiente.
3. Migliorare il 9:16 selezionando clip dove persone e azione stanno al centro; evitare tagli a volti, corpi e cammelli.
4. Sostituire musica provvisoria con traccia originale di qualità verificata, senza copiare registrazioni d'epoca.
5. Verificare il sito privato con import autorizzato e una scheda completa di quattro post distinti. Non chiamare `delivery_ready` una prova incompleta.

Fonte regole: [V56](LA_STORIA_RIVIVE_CONTRATTO_V56.md) e [V55](REGOLE_ATTIVE.md).