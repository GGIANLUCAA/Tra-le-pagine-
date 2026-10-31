# La Storia Rivive · V124 — 48 originali HD reali, selezione temporale a 5 regioni

Data: 31 ottobre 2026. Ambito **esclusivamente Restauro storico**. La V124 non produce video finiti, non richiede foto AI, non invia Vidu e non pubblica nulla.

## Film autentico su byte effettivi

Sorgente: [Filature et Tissage du coton (1920), Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Filature_et_Tissage_du_coton_(1920).webm).

- Film scaricato su GitHub Actions: 66.553.161 byte, SHA-256 immutato `e3022cb130442f7695d411724ae619fc8c184696ddae30293958c1c75ec8ffd9`, FFprobe 1920×1080, circa 524,96 s.
- Analisi precedente V121/V123 sui 12 PNG: solo **3** candidati fotografici; intertitoli, logo e schemi rifiutati. Esecuzione [41156930678](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41156930678).
- Nuovo modulo `src/storia_rivive_adaptive_sampling_v124.py`: a partire dallo **stesso film SHA-bound e dai 144 timestamp di tagli candidati V113**, seleziona al massimo 48 *segmenti sufficientemente lunghi*, distribuiti lungo la durata del film, e decodifica **una volta il vero video** con FFmpeg `select` + `showinfo` senza normalizzare il frame rate o riscrivere artificialmente i PTS. Ogni PNG possiede SHA-256 e `source_pts`, tempo e timebase reali.
- [Run 41157549529](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41157549529) SUCCESS, artifact `STORIA_V121_ONE_REAL_ARCHIVE_AUDIT_41157549529`, contiene `ADAPTIVE_RANK_V124.json`, `SCOUT_REPORT.json`, `ADAPTIVE_CONTACT_SHEET_V124.jpg`. Ho scaricato e letto realmente questi risultati: **48/48 PNG source-locked**, **21/48 candidati fotografici** (pixel filter conservativo), **48/48 finestre PTS temporalmente valide**. La presenza del video 1080p nominale **non certifica** una scansione originale 1080p né volti di qualità V98.
- Primo ranking *solo per punteggio*: `frame_25`, `frame_37`, `frame_42`, `frame_43`, `frame_48`. Troppo concentrato nella seconda parte del film, anche con immagini somiglianti (es. 42 e 43).
- Correzione di regia `spread_review_shortlist`: sceglie il miglior frame fotografico per ciascuno dei **cinque quinti temporali** della pellicola, senza duplicare il segmento V113; blocca la shortlist se una regione è priva di candidati. La regola è SOLO per questa ricerca supplementare, non un'approvazione di nuove scene.

## Cinque frame originali ora proposti per revisione artistica

La **seconda verifica reale** [Actions run 41157888552](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41157888552), artifact `STORIA_V121_ONE_REAL_ARCHIVE_AUDIT_41157888552`, è terminata SUCCESS. Ho scaricato e letto i rapporti effettivi: `V124_FIVE_TIME_SPREAD_SOURCE_CANDIDATES_REVIEW_ONLY`.

| Scena (proposta, non approvata) | Timecode film originale (s) | Segmento V113 candidato | Che cosa resta da controllare |
|---|---:|---:|---|
| `frame_10.png` | 98,16 | 28 | persona/macchinario e dettaglio leggibile, crop 9:16 |
| `frame_20.png` | 199,68 | 58 | funzione delle macchine e contrasto originale |
| `frame_25.png` | 260,68 | 73 | bobine/telaio, distinguerlo dalla seconda scena |
| `frame_37.png` | 390,52 | 111 | effettivo movimento e varietà di soggetto |
| `frame_42.png` | 452,88 | 128 | operatrice al telaio, mani e volto realmente leggibili |

**Attenzione:** i segmenti FFmpeg V113 e cinque regioni temporali distinte NON sono prova che siano cinque **vere riprese di camera**. Un PASS PTS non prova che i macchinari si muovano semanticamente in ogni finestra B/N. I 21 candidati sono da visionare; le immagini non sono automaticamente fotografie I2I né lavori pronti.

## Test ripetibili e salvaguardie

- `tests/test_storia_rivive_v124.py` verifica PTS/SHA su un MP4 effettivamente codificato in modo sintetico, provenienza non falsificata, 5 campioni in segmenti diversi, stop su fonte SHA falsa, soglie, e ora riproduce **i 21 punteggi/timestamp autentici** dal rapporto del 1920 per controllare la diversificazione temporale. Non include i 48 PNG storici nel repository.
- [CI V109 run 41157888434](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41157888434): **49/49 test PASS**. [CI V116 run 41157888568](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41157888568): **72/72 test PASS** (incluse suite V115–V124 e cache). Una prima esecuzione V124 aveva un caso sintetico mal configurato, corretto senza cambiare le regole di sicurezza.
- Questa capacità è nella PR bozza #147, dipendente dalla PR #145, e non ancora su `main`. Il workflow V121 di audit è isolato dalla produzione autonoma V101 a tre ore; non ci sono nuove chiamate API fatturabili o modifiche a ArtVision/WOW LAB/V98.

## Prossimi blocchi concreti

1. Verificare con FFmpeg su **byte originali** il movimento B/N nelle cinque finestre specifiche, e visionare il film e i cinque crop per distinguere vere camera shots, non soltanto segmenti V113.
2. Accertare fonte/autore/licenza e **diritti italiani** (la scheda Commons Public domain non costituisce da sola autorizzazione territoriale certificata).
3. Solo con fonte idonea, quattro reali I2I fotografiche fedeli e una vera clip Vidu dalla quinta fonte con gate/consumo crediti prepagati verificato, poi montaggio V98, QA V91/V94/V96/V99 e tre piloti.
4. Nulla va dichiarato finale, approvato o pubblicato ora. **0 nuovi MP4/ZIP, 0 nuovi I2I, 0 nuove clip Vidu, 0 crediti usati** in questa versione.
