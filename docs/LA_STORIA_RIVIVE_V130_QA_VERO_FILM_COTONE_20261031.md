# La Storia Rivive V130 — collaudo GitHub e revisione visiva sul film reale

Data: 31 ottobre 2026. Formato: **solo restauro storico**, issue #144 / mandato V108. Questa nota documenta risultati effettivamente letti; NON approva il film per nuovi 4+1, I2I, Vidu, Italia o pubblicazione.

## Prova tecnica realmente conclusa

- [GitHub Actions V109 #41164272102](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41164272102): **SUCCESS**, 86/86 test su 10 suite, fra cui V128 8/8, V129 6/6, V127 9/9. Esecuzione **sul branch PR #148**, senza API a pagamento.
- [GitHub Actions V121 #41164275161](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41164275161): **SUCCESS**, passo reale sul film *Filature et Tissage du coton* presente in Wikimedia Commons (titolo catalografico «1920» da verificare).
- [Artifact ZIP reale 13028139469](https://github.com/GGIANLUCAA/Tra-le-pagine-/actions/runs/41164275161/artifacts/13028139469): scaricato, aperto e letto effettivamente. Contiene `REAL_FILM_AUDIT_V121.json`, `FIVE_MOVING_REVIEW_V126.json`, `BALANCED_VISUAL_REVIEW_V128.json`, `BALANCED_CONTACT_SHEET_V128.jpg`, `PREFREEZE_MOTION_STRIPS_V129.json` e `PREFREEZE_MOTION_STRIPS_V129.jpg`. Sono **diagnostiche JPG e JSON**, non MP4 finale.
- Pellicola originale acquisita nel runner, SHA-256 `e3022cb130442f7695d411724ae619fc8c184696ddae30293958c1c75ec8ffd9`, raster decodificato 1920×1080 (non prova di scansione cinematografica HD nativa); 48 PNG supplementari, 21 candidati fotografici, 8 con prova di movimento spaziale B/N.
- La V125 è correttamente `V125_MOTION_SOURCE_SELECTION_BLOCKED` (copertura solo nelle ultime 3/5 regioni). V126 alternativa da revisione: **5 segmenti differenti** `frame_21,23,34,42,48`, gap almeno 12 s e 3 regioni. V126b rimane `V126_SOURCE_FRAME_AUDIT_BLOCKED` per mancata copertura 5/5, *non* è un crash. V128 dà `V128_FIVE_BALANCED_FRAMES_VISUAL_REVIEW_REQUIRED`, senza coppie near-duplicate segnalate; V129 dà `V129_FIVE_SOURCE_LOCKED_MOTION_STRIPS_REVIEW_ONLY`.
- I 5 proxy B/N reali V129 hanno prodotto ciascuno **5 campioni decodificati a 4 fps**, di cui 3 visualizzati nella tavola (non gli exact frame PTS del freeze). Nessun controllo proxy equivale all'approvazione dei cinque cambi di camera.

## Revisione visiva effettiva sulle immagini dell'artifact

Sono state **aperte e osservate entrambe le tavole JPG originali** dell'artifact (non solo inferenza dai JSON):

| Frame autentico | Freeze nella pellicola | Osservazione sul soggetto e sull'impatto |
|---|---:|---|
| `frame_21` | 210,16 s | Macchinario con bobine sospese: movimento presente, soggetto ripetitivo e resa cromatica da valutare |
| `frame_23` | 232,36 s | Tessitura con molti fili/macchine: composizione visivamente distinta da 21, però sempre tema meccanico |
| `frame_34` | 357,36 s | Altro macchinario, **ampie alte luci sovraesposte**: scarso margine per un restauro fotografico credibile e fedele nei dettagli perduti |
| `frame_42` | 452,88 s | Operaia che lavora al telaio, soggetto umano e gesto interessante; mani/viso ancora da verificare su frame originali a piena risoluzione |
| `frame_48` | 509,88 s | Panoramica di reparto con molte persone/macchine, **volti minuscoli**, rischio di inventare persone/identità nel restauro I2I |

Le cinque composizioni **sembrano diverse nella tavola** e mostrano differenze fra i proxy B/N, ma non sono stati visionati per intero i cinque estratti in movimento in forma originale. Il numero di tagli calcolato da FFmpeg non certifica automaticamente cinque riprese cinematografiche autenticamente distinte.

### Decisione tecnica prudente

**`ASSETS_PENDING / SOURCE_ARTISTIC_REVIEW_HOLD`** per questo soggetto; non avanzare a quattro I2I/una Vidu a pagamento su questa cinquina. Il compromesso «due macchinari, uno sovraesposto, una persona, una panoramica con volti piccoli» non è ancora dimostrato pari al minimo qualitativo **San Francisco V98**. Non sostituire dettagli storici perduti con volti/macchine immaginari. È ammissibile proporre altri frame/scatti documentati o cambiare film; non bollare in modo definitivo l'intero archivio come inutilizzabile senza esaminarlo.

**Blocco esterno distinto**: titolarità/autore e anno attribuiti, nonché diritti residui applicabili all'Italia, **non verificati**. Non usare il marchio Public Domain della sola scheda Commons come certificazione territoriale.

## Costi, sicurezza e prossima azione

0 nuovi restauri fotografici I2I; 0 nuovi MP4 Vidu; 0 nuovi master/ZIP Android; 0 crediti API spesi e 0 social pubblicati. I trigger V130 su branch sono esclusivamente di collaudo gratuito e devono essere rimossi prima di integrare le PR #145/#147/#148 nel ramo principale.

**Prossima azione:** rendere questa valutazione visiva un blocco editoriale ripetibile prima di collegare le API, selezionare fonte alternativa con più azione umana/volti leggibili e diritti italiani verificabili. Poi quattro veri I2I fedeli, una clip Vidu dall'esatto frame con saldo/authorization gate corrente, video 4+1, controlli V91/V94/V96/V99 e tre piloti. Nessuna autorizzazione di spesa o pubblicazione è implicita.
