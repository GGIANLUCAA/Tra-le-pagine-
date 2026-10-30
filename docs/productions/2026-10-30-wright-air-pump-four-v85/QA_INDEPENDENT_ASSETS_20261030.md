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
