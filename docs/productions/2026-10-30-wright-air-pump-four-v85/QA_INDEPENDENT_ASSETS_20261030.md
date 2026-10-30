# Wright V85 — verifica indipendente di due asset originali (30/10/2026)

**Ambito:** QA tecnico effettuato in questa esecuzione su byte effettivamente recuperati da GitHub Actions, NON una nuova produzione, NON revisione V25, NON prova di archiviazione privata o pubblicazione. Nessuna nuova chiamata Google TTS/video AI.

## Cinema Standard V52B — originale storico, stesso slot V85

- Fonte GitHub Actions: run `40649283319`, artifact `12798647211`, nome `ARTVISION_V52B_WRIGHT_AIR_PUMP_RENDERED_NEEDS_REVIEW`. Artifact recuperato con successo il 30/10/2026, ZIP esterno CRC PASS, quattro membri (incluso ZIP completo).
- `wright_air_pump_20261028_0915/VIDEO_MASTER.mp4` estratto davvero: **6.690.474 byte**, SHA256 **`ec4525c155334a02696bfa05d745005bea3084f178043c9eaf1dca6d7bfe29e2`**, esattamente uguale alla scheda V85. Non ricodificato e non modificato.
- `ffprobe`: **55,900 s**, **1080×1920**, **24 fps**, **H.264 + AAC**. `ffmpeg -xerror` decodifica completa video **PASS**, audio **PASS**.
- Traccia audio non silenziosa, `volumedetect` media **−20,5 dB**, massimo **−4,4 dB**; questo NON certifica l'ascolto umano o la licenza musicale.
- Campionamento visivo su 12 istanti reali: **0,1 / 2 / 5 / 8 / 12 / 18 / 24 / 30 / 38 / 45 / 53 / 55 s**. Il dipinto originale resta riconoscibile, dettagli differenziati, ritorno a vista d'insieme a ~53 s. **Punto da sottoporre a V25:** il cartiglio scuro di titolo rimane in primo piano ai campioni 0,1–5 s e copre parte del dipinto durante il gancio iniziale. Valutare se ridurlo/anticiparne la rimozione in una futura revisione dello STESSO slot; nessun rerender autorizzato da questo rapporto. Le inquadrature ravvicinate tagliano parti laterali dei personaggi, perlopiù per il focus sui dettagli; il solo campionamento non certifica assenza di tagli indesiderati nell'intero video.
- **Esito:** integrità e decodifica dell'originale V52B confermate indipendentemente; **status invariato `rendered_needs_review`**.

## Gacrux V85 — WAV originale e copione esatto

- Fonte GitHub Actions: run `41030305113`, artifact `12966285611`, `ARTVISION_WRIGHT_ONE_REAL_GACRUX_V85`; scaricato e aperto, ZIP CRC PASS, otto file.
- `VOCE.wav`: **10.320.044 byte**, SHA256 **`d31a0bb8ea3a53af4c45d88db3e7d3e3e9a478115618fb73c8ad99e5268885ef`** (corrisponde alla ricetta V85); **215,000 s**, PCM signed 16-bit, mono, 24 kHz.
- `COPIONE_ESATTO_V85.txt`: SHA256 **`133de71cf67a6cf280fd2bfc41ab32e7038269d9d0f6a32fa5e3659f0e5350f9`**, coincide con dossier.
- `volumedetect` WAV: media **−20,6 dB**, picco **−0,8 dB**. Nessun errore ZIP/lettura. Non è stato effettuato nuovo TTS; **non** è stato verificato che ogni parola del WAV sia pronunciata correttamente, né l'identità AAC nei due Critico in questa esecuzione.
- **Esito:** cache vocale originale riproducibile da artifact esistente, hash verificato; non significa archivio perpetuo.

## Limitazioni e prossimo gate

I quattro MP4 V85 e gli ZIP risultano elencati nella Libreria ChatGPT, ma il tentativo di materializzare `WRIGHT_4_VIDEO_ANDROID_V85.zip` per verificarne i byte ha restituito **`This Project file does not have an authorized raw-byte materialization path`**. Non affermare dunque un backup stabile in sito/Dropbox, né che i quattro master siano stati tutti riesaminati qui. Richiedono V25 umano, confronto reale sincronizzazione audio–dettaglio e verifica download/playback dall'archivio autorizzato. Nessuna modifica alla coda, nessuna sesta opera, nessuna pubblicazione.

Link fonti interne: [dossier Wright V85](FOUR_REAL_MP4S_QA_AND_DELIVERY.md), [coda 4×1](../../../queue/artvision_four_variants_s01_20261028.json).

## Verifica registica quantitativa aggiuntiva — Cinema Standard V52B (30/10/2026)

**Prova nuova su MP4 originale**, non sul manifest: `/mnt/data/WRIGHT_CINEMA_STANDARD_V52B_VERIFIED.mp4`, 6.690.474 byte, SHA256 `ec4525c155334a02696bfa05d745005bea3084f178043c9eaf1dca6d7bfe29e2`. Lettura frame-per-frame con OpenCV: **1.339 frame video decodificati a 24 fps** (durata immagini 55,792 s; contenitore ffprobe 55,900 s). Grayscale a 135×240 per rilevare discontinuità; non sostituisce visione V25.

- **Nove stacchi netti rilevati** (mean absolute pixel difference tra frame consecutivi >20/255): a circa **5,417 / 10,500 / 15,792 / 21,000 / 26,208 / 31,500 / 36,708 / 41,917 / 47,208 s**. Gli otto intervalli interni sono **5,224 s medi**, deviazione standard **0,070 s**, coefficiente di variazione **1,35%**. Ritmo quasi perfettamente periodico: **rischio concreto di montaggio a stampino**, contrario alla regia dinamica motivata dall'opera. Non sono salti di camera Museum V57; sono tagli nel Cinema Standard, quindi non applicare indiscriminatamente la soglia V57.
- **Ultimo stacco a 47,208 s**: per circa **8,58 s**, cioè **15,4% della durata video effettiva**, l'opera completa rimane piccola al centro di un grande campo nero. A campioni 47,5–55,5 s circa **60,4% dei pixel** ha luminanza <12/255 (campionamento 135×240), rispetto a ~0–3% nei precedenti campioni; la composizione riduce fortemente l'impatto visivo nel finale. Questo è un **difetto registicamente prioritario da valutare**, non un errore di decodifica.
- **Apertura**: cartiglio nero con titolo ancora presente ai campioni 0,5 / 2,5 / 4,5 s; scompare al taglio ~5,417 s. Insieme al finale statico, il primo/ultimo segmento consumano almeno ~14 s (circa 25%) senza il miglior potenziale di immersione nel quadro.
- **Rimedio candidato, NON applicato al master**: copertina/titolo molto più breve e meno coprente, alternanza di hold e movimenti motivati dai soggetti invece di stacchi fissi ogni 5,2 s, ritorno finale all'intera tela in una composizione che occupi più spazio utile, outro sensibilmente più corto. Verificare con V25 umano e preservare originale V52B immutato. **Nessun nuovo MP4, nessuna nuova approvazione, nessuna API a pagamento**.

Questa verifica approfondisce il QA precedente con **due difetti registicamente misurati** e non modifica il conteggio dei quattro slot Wright né la coda.
