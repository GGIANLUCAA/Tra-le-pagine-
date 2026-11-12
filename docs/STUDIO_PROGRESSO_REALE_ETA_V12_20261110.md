# Centro di controllo V12 — Avanzamento reale e tempo residuo prudente
**10 novembre 2026 · Anteprima / PR bozza** · Nessuna modifica al sito live o ai video.

## Perché questa versione non mostra una barra inventata
I video non hanno un tempo noto: render, Vidu, TTS, upload, QA, download e diritti richiedono durate variabili. Il semplice fatto che una automazione ChatGPT sia stata eseguita NON rende il suo lavoro osservabile tramite una pagina pubblica. Usare percentuali di tempo passate o timelapse simulati renderebbe il sito meno affidabile.

## Cosa si vede adesso
Nella Home del Centro di controllo, in **Salute produzioni** e in **Ripara GPT** compare **Avanzamento dei lavori**, solo per run GitHub del ramo `main` identificate nel campione pubblico per un progetto video.
- Barra: percentuale **dei passaggi GitHub osservati e terminati**, NON percentuale di montaggio, MP4 o QA. Quando GitHub non espone step, compare una barra tratteggiata senza percentuale.
- Fase: nome del job/step realmente in esecuzione oppure dicitura che la fase non è esposta.
- Stato: GitHub in coda/in corso/completato tecnicamente; se fallito, **da riparare**. Una fase oltre 30 minuti senza nuovi step è **da verificare**, non automaticamente bloccata.
- Tempo residuo: **solo della run GitHub**, non del video, calcolato come intervallo prudente dal 20° all'80° percentile di almeno **5 run riuscite** dello stesso `workflow_id`, `main`, con evento `schedule`/`workflow_dispatch` e durata storica valida (1 min–6 h). In assenza di dati, orari incompleti o durata oltre l'intervallo, **stima non disponibile**.
- Output video: **non certificato**. Anche se un workflow completa, occorrono MP4 vero, decode, SHA, ZIP, diritti e revisione.
- Pulsante **Ripara / verifica GPT** apre la diagnosi con run e job, non modifica il workflow.

## Aggiornamento in tempo quasi reale
La pagina aggiorna il campione delle run GitHub circa ogni **105 secondi**, quando è visibile, e la fase del massimo di 3 run selezionate. Il Worker usa cache per ridurre chiamate a GitHub, controlla gli ID contro un campione di run reali main e accetta solo GET. Non effettua operazioni di scrittura né richieste a pagamento.

## Limite fondamentale e successiva fase possibile
Questa è una **telemetria tecnica GitHub**, non ancora un **cronometro dei singoli filmati generati dalle automazioni ChatGPT**. Per una barra per ciascun video con ETA verificabile occorrerà che ogni produttore autorizzato emetta un checkpoint con:
1. `project`, `work_id`, `slot_id`/episodio e `video_key` corrispondenti alla coda;
2. identificativo `run_id`, fase effettiva e marcature temporali di inizio/fine;
3. heartbeat datato e motivo di blocco verificato da log;
4. storico durate per fase/format, con campione sufficiente e intervalli di confidenza;
5. prova separata di MP4/ZIP e QA, prima dello stato «finito».

L'aggiunta dei checkpoint va fatta nei produttori reali, uno per volta, **senza aggiungere cron o workflow duplicati**. Fino ad allora il pannello dichiara esplicitamente che le automazioni ChatGPT non sono visibili e il termine di consegna MP4 non è stimabile.

## Implementazione e verifiche
- `site/control-center-progress-backend.fragment.js` incorporato in `site/control-center-preview.worker.js`: endpoint GET `/api/progress?run=ID`, job/step GitHub reali, ETA limitata e fail-closed.
- `site/control-center-progress-frontend.fragment.js` incorporato in `site/control-center-preview.html`: card e barra responsive Android.
- `tests/control-center-production-progress.test.mjs`: source match, sicurezza, parsing, ETA, progress, segnale vecchio, URL pubblico validato, cache e nessun POST.
- `tests/control-center-action-hub-dom.test.cjs`: UI Android simulata con status reali, percentuale step, fase ed ETA indisponibile.
- `.github/workflows/artvision-control-center-preview-ci.yml`: compilazione senza deploy.
- Sito pubblico e catalogo: **non modificati** in questa PR.

## Monitoraggio temporaneo richiesto dal proprietario
È stata configurata separatamente una automazione ChatGPT (3 giorni, ogni 2 ore, fino a 36 occorrenze) per controllare salute del sito, CI, anteprime, file e anomalie. La sua attività **non** dimostra la telemetria dal produttore; le correzioni in GitHub, se possibili, restano in rami/PR separati con test. Il monitor non può consumare Vidu/API, pubblicare, cancellare né fare merge automaticamente. Notifiche solo per problemi importanti.
