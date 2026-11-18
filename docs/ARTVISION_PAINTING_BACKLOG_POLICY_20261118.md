# ArtVision — catalogo quadri espandibile (18 novembre 2026)

## Fonti di selezione esistenti
- `queue/artvision_owner_selected_ten_20261102.json`: coda precedente; non duplicare varianti già concluse, escluso Dalí secondo istruzioni owner.
- `research/artvision_owner_selected_30_future_20261109.json` e `queue/artvision_owner_30_fast_quality_lane_20261109.json`: 30 selezioni dell'owner, mantenere tutte anche quando una fonte è bloccata.
- `queue/artvision_new_series_20261114.json`: nuove opere, checkpoint e stati per variante.
- `queue/production_v15.json`: coda di pacchetti render V16 attualmente vuota; le liste di quadri NON sono pacchetti V16.

## Regole di espansione senza perdita dati
1. Conservare le liste ricevute dall'owner come sorgenti immutabili; ogni nuova lista è un lotto aggiuntivo, non sostituisce quelli esistenti.
2. Deduplicare per artista, opera, esemplare museale e variante 4×1, confrontando checkpoint, MP4 verificati, Gallery e Releases; non confondere studi/versioni diverse.
3. Mantenere almeno tre stati distinti: `candidate` (da verificare), `source_rights_ready` (immagine esatta, licenza, SHA, metadati), `render_prepared` (asset, progetto, audio dove necessario e QA preflight compatibili con il renderer).
4. Se una variante è bloccata, selezionare la prossima variante o opera indipendente; un blocco Gacrux riguarda solo Critico, non Cinema.
5. Non inserire automaticamente un candidato nella coda V16 finché non esiste un pacchetto preparato e verificato; la quantità della lista non equivale alla quantità di video pronti.
6. Consentire aggiunte future dell'owner senza cancellare priorità, stati, diritti, checksum e checkpoint precedenti. Proposte automatiche in un lotto separato e identificato.
7. Quando le opere pronte finiscono, avviare nuova ricerca di opere con immagini e diritti verificabili, senza inventare readiness o chiamate a pagamento.

## Prossima implementazione
Realizzare un adapter con test che legge i lotti, produce un indice unificato deduplicato e genera un report di candidati/preparati/bloccati; solo un secondo passo validato può alimentare `queue/production_v15.json`.
