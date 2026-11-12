# ArtVision · claims atomici V1 — prototipo isolato, 12 novembre 2026

## Scopo e stato

Questa è la **seconda protezione** della futura catena ArtVision. È distinta dal selettore in PR #258 (ancora read-only) e dalla progettazione in PR #255. Nessun job corrente viene modificato, nessuna coda owner viene consumata, nessun MP4 viene generato o pubblicato. Il test su PR è offline e dispone di `contents: read`, non di `contents: write`.

Un solo slot ArtVision è identificato da:
`repo + work_id + variante 4x1 + revisione`.
Il SHA256 della fonte è richiesto come prova, **ma NON fa parte della chiave di deduplica**: sostituire una foto non autorizza a produrre nuovamente lo stesso slot. Il digest SHA256 di questa identità compone un ref immutabile
`refs/heads/artvision-idempotency/v1/<digest>`.

### Prenotazione proposta (NON ancora collegata al render)

- Chi effettuerà la produzione in futuro dovrà prima detenere lo **stesso gruppo GitHub Actions `artvision-owner-single-heavy-render`** dei workflow heavy esistenti. `cancel-in-progress: false` protegge un rendering già avviato; per una coda vera andrà valutato `queue: max`, disponibile in GitHub Actions nel 2026, evitando la sostituzione dei pending. La coda deve comunque essere deduplicata dal nostro orchestratore.
- Rileggere lo stato GitHub in modo attendibile, i documenti owner, il blocco pilota V58, il source SHA effettivo, le licenze, il QA plan, gli slot consegnati, i costi e le approvazioni. I booleani di un JSON non costituiscono prove indipendenti.
- Nel punto in cui il worker detiene l'esclusività, provare **una sola volta** il `POST /git/refs` di GitHub con un ref deterministico, se e solo se il lavoro è nuovo e autorizzato. Il server decide l'esistenza in modo condiviso per tutti i worker.
- Risultato 201: soltanto `claim_reserved_only`. **Non** è un render, non è QA, non è approvazione o rilascio.
- Risultato 422: eseguire al massimo un GET di verifica. Se il ref esiste, `already_claimed_quarantine`; altrimenti `unknown_quarantine`.
- Timeout, 5xx, JSON/HTTP ignoto: `unknown_quarantine`; **mai ripetere automaticamente** un POST perché il ref potrebbe essere già stato creato.
- I ref di claim non sono cancellati automaticamente. Un tentativo interrotto viene registrato per revisione del proprietario; altri lavori indipendenti possono continuare dopo che il gruppo heavy è libero. Un vero rifacimento richiede nuova revisione e documentazione tecnica esplicita, non una modifica invisibile della fonte.
- La struttura conserva quattro varianti distinte per opera. Nessuna pubblicazione, nessun addebito API: questo prototipo accetta soltanto `budget_eur: 0` e `paid_api_calls_authorized: false`.

## File reali

- `src/artvision_atomic_claim_v1.py`: validazione identità e protocollo `claim_once`; store iniettato; demo sola lettura.
- `src/artvision_atomic_github_store_v1.py`: adapter REST presente nel codice ma **non chiamato da workflow, trigger o script di produzione**. Nessun token configurato.
- `tests/test_artvision_atomic_claim_v1.py`: simulazione di 40 contender, 1 solo claim consentito, collisione, timeout post-write, HTTP 422/500, fonte cambiata, diritti, blocco pilota e divieti pubblicazione.
- `.github/workflows/artvision-atomic-claim-protocol-ci.yml`: test CI read-only, senza effetti collaterali.

## Limitazioni cruciali / passaggio successivo

1. Simulare un server atomico in memoria e testare un adapter HTTP mock **non dimostra ancora** un claim creato su GitHub in situazione reale. Nessun ref `artvision-idempotency/` viene scritto in questa PR.
2. La concurrency GitHub è una protezione a livello workflow e non include i processi esterni: **non è ancora un lock globale universale**. Il gruppo attuale copre soltanto i workflow che lo dichiarano, quindi occorre auditare tutti i renderer in uso prima di attivare il bridge.
3. I workflow vecchi di molte opere sono attivati soltanto al push di specifici YAML, non via `workflow_dispatch`. Non è corretto dichiarare operativa l'automazione finché non esiste un orchestratore approvato con un trigger controllato, un'unica riserva per slot e test end-to-end.
4. Il blocco pilota V58 è ancora un vincolo da verificare realmente; il flag `pilot_lock_checked` del manifesto è solo un'interfaccia futura e non può sbloccarlo.
5. Quando sarà prevista la prima prova reale, effettuare un **canary isolato senza spesa e senza video** su ref di test dedicato, con piano di cleanup e analisi degli effetti dei trigger push. Poi canary su un solo candidato realmente autorizzato, QA video completo e consegna Android controllata.
6. Proteggere i video originali, V80/V82/V94/V96/V99/V118/V119/V320/V322, nessun Gold automatico e zero pubblicazione social/sito senza controllo.

Questo lavoro è un **protocollo e un prototipo testato**, non l'attivazione della produzione continua.
